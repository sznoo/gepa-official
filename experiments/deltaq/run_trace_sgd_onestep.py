import argparse
import hashlib
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

import dspy

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from examples.hotpotqa.program import HotpotMultiHop

try:
    from examples.hotpotqa.metric import answer_match_fn
except Exception:
    answer_match_fn = None

try:
    from tqdm.auto import tqdm
except Exception:
    def tqdm(x, **kwargs):
        return x


_tls = threading.local()


# -------------------------
# Basic utilities
# -------------------------

def read_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_json(path):
    return json.load(open(path))


def truncate(x, n):
    x = "" if x is None else str(x)
    return x if len(x) <= n else x[:n] + "\n...[truncated]"


def as_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, tuple):
        return list(x)
    if isinstance(x, set):
        return list(x)
    return [x]


def title_from_doc(doc):
    return str(doc).split(" | ", 1)[0].strip()


def get_first(d, keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return default


def _flatten_answer_values(x):
    vals = []
    if x is None:
        return vals
    if isinstance(x, str):
        if x.strip():
            vals.append(x.strip())
        return vals
    if isinstance(x, (int, float)):
        vals.append(str(x))
        return vals
    if isinstance(x, dict):
        for k in ["answer", "text", "value", "label"]:
            vals.extend(_flatten_answer_values(x.get(k)))
        return vals
    if isinstance(x, (list, tuple, set)):
        for y in x:
            vals.extend(_flatten_answer_values(y))
        return vals
    vals.append(str(x))
    return vals


def gold_answers_of(row):
    vals = []
    for k in ["gold_answer", "gold_answers", "answer", "answers", "target_answer", "target_answers"]:
        if isinstance(row, dict) and k in row:
            vals.extend(_flatten_answer_values(row.get(k)))

    out = []
    seen = set()
    for v in vals:
        key = v.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(v.strip())
    return out


def gold_answer_of(row):
    vals = gold_answers_of(row)
    return vals[0] if vals else ""


def gold_support_titles_of(row):
    return get_first(row, ["gold_support_titles", "support_titles", "supporting_titles"], [])


def missing_titles_of(row):
    return get_first(row, ["missing_titles_after_hop1", "base_missing", "missing_support_titles"], [])


def normalize_answer(s):
    s = str(s or "").lower()
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def answer_score(pred_answer, gold_answer):
    golds = _flatten_answer_values(gold_answer)
    if not golds:
        return 0.0
    npred = normalize_answer(pred_answer)
    return float(any(npred == normalize_answer(g) for g in golds))


def make_lm(args):
    kwargs = {
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_base:
        kwargs["api_base"] = args.api_base
    if args.api_key:
        kwargs["api_key"] = args.api_key
    return dspy.LM(args.model, **kwargs)


def get_lm(args):
    if not hasattr(_tls, "lm"):
        _tls.lm = make_lm(args)
    return _tls.lm


def clean_lm_text(x):
    if isinstance(x, list):
        x = x[0] if x else ""
    x = str(x).strip()
    x = re.sub(r"^```(?:json)?", "", x, flags=re.I).strip()
    x = re.sub(r"```$", "", x).strip()
    if x.lower().startswith("json"):
        x = x[4:].strip()
    return x


def extract_json_obj(text):
    text = clean_lm_text(text)
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return None
    return None


def lm_json_call(args, prompt):
    lm = get_lm(args)
    last_error = None
    for i in range(args.retries):
        try:
            out = lm(prompt)
            raw = clean_lm_text(out)
            obj = extract_json_obj(raw)
            if isinstance(obj, dict):
                return obj, raw, None
            last_error = f"JSON parse failed: {raw[:500]}"
        except Exception as e:
            last_error = str(e)
        if i + 1 < args.retries:
            time.sleep(2.0 * (i + 1))
    return {}, "", last_error


# -------------------------
# DSPy prompt utilities
# -------------------------

def set_predictor_instructions(predictor, instructions):
    sig = predictor.signature
    if hasattr(sig, "with_instructions"):
        predictor.signature = sig.with_instructions(instructions)
        return

    try:
        sig.instructions = instructions
        return
    except Exception:
        pass

    # Last resort for newer/older DSPy variants.
    try:
        predictor.signature = sig.__class__.with_instructions(sig, instructions)
        return
    except Exception as e:
        raise RuntimeError(f"Could not set instructions on predictor: {e}")


def apply_prompts(program, prompts):
    for key, instr in prompts.items():
        # keys look like "create_query_hop2.predict"
        parts = key.split(".")
        obj = program
        for p in parts:
            obj = getattr(obj, p)
        set_predictor_instructions(obj, instr)


def build_prompt_dict(args, create_query_instruction):
    fixed = load_json(args.fixed_prompt_candidate)
    prompts = dict(fixed["prompts"])

    if args.base_prompt_candidate:
        base = load_json(args.base_prompt_candidate)
        if "create_query_hop2.predict" in base["prompts"]:
            prompts["create_query_hop2.predict"] = base["prompts"]["create_query_hop2.predict"]

    prompts["create_query_hop2.predict"] = create_query_instruction
    return prompts


def base_create_query_instruction(args):
    if args.base_prompt_candidate:
        base = load_json(args.base_prompt_candidate)
        return base["prompts"]["create_query_hop2.predict"]
    fixed = load_json(args.fixed_prompt_candidate)
    return fixed["prompts"]["create_query_hop2.predict"]


def patched_instruction(base_instruction, patch):
    return (
        base_instruction.rstrip()
        + "\n\n"
        + "# Trace-SGD one-step update patch\n"
        + str(patch).strip()
    )


def get_program(args, create_query_instruction):
    if not hasattr(_tls, "program_cache"):
        _tls.program_cache = {}

    h = hashlib.md5(create_query_instruction.encode("utf-8")).hexdigest()
    if h not in _tls.program_cache:
        program = HotpotMultiHop(k=args.retriever_k, retriever_dir=args.retriever_dir)
        prompts = build_prompt_dict(args, create_query_instruction)
        apply_prompts(program, prompts)
        _tls.program_cache[h] = program

    return _tls.program_cache[h]


# -------------------------
# State extraction / rollout
# -------------------------

def docs_to_titles(docs):
    return [title_from_doc(d) for d in docs]


def rollout_one(args, row, create_query_instruction, prompt_label):
    lm = get_lm(args)
    program = get_program(args, create_query_instruction)

    question = row["question"]
    summary_1 = row["summary_1"]
    gold_answers = gold_answers_of(row)
    gold_answer = gold_answers[0] if gold_answers else ""

    with dspy.context(lm=lm):
        q = program.create_query_hop2(question=question, summary_1=summary_1).query
        docs = program.retrieve_k(q).passages
        summary_2 = program.summarize2(
            question=question,
            context=summary_1,
            passages=docs,
        ).summary
        pred_answer = program.final_answer(
            question=question,
            summary_1=summary_1,
            summary_2=summary_2,
        ).answer

    sc = answer_score(pred_answer, gold_answers)

    return {
        "batch_id": row.get("batch_id"),
        "pool_label": row.get("pool_label"),
        "example_id": row.get("example_id"),
        "_id": row.get("_id"),
        "question": question,
        "gold_answer": gold_answer,
        "gold_answers": gold_answers,
        "prompt_label": prompt_label,
        "query": q,
        "retrieved_titles": docs_to_titles(docs),
        "retrieved_docs": docs,
        "summary_1": summary_1,
        "summary_2": summary_2,
        "pred_answer": pred_answer,
        "score": sc,
        "gold_support_titles": gold_support_titles_of(row),
        "missing_titles_after_hop1": missing_titles_of(row),
        "baseline_pool_score": row.get("score"),
        "baseline_pool_query": row.get("hop2_query"),
        "baseline_pool_titles": row.get("hop2_titles"),
    }


def rollout_many(args, rows, create_query_instruction, prompt_label, desc):
    if args.num_threads <= 1:
        return [
            rollout_one(args, r, create_query_instruction, prompt_label)
            for r in tqdm(rows, desc=desc, unit="ex", dynamic_ncols=True)
        ]

    out = []
    with ThreadPoolExecutor(max_workers=args.num_threads) as pool:
        futs = [
            pool.submit(rollout_one, args, r, create_query_instruction, prompt_label)
            for r in rows
        ]
        for fut in tqdm(as_completed(futs), total=len(futs), desc=desc, unit="ex", dynamic_ncols=True):
            out.append(fut.result())

    out.sort(key=lambda x: (str(x.get("batch_id")), str(x.get("pool_label")), str(x.get("question"))))
    return out


def state_by_question(states):
    return {s["question"]: s for s in states}


# -------------------------
# Oracle rows
# -------------------------

def load_oracle_map(path, arm):
    rows = read_jsonl(path)
    m = {}
    for r in rows:
        if r.get("arm") == arm:
            m[r.get("question")] = r
    return m


def oracle_state_from_row(r):
    if not r:
        return None
    docs = get_first(r, ["hop2_docs", "retrieved_docs", "docs", "passages"], [])
    titles = get_first(r, ["hop2_titles", "retrieved_titles", "titles"], None)
    if titles is None and docs:
        titles = docs_to_titles(docs)

    return {
        "query": get_first(r, ["hop2_query", "query", "candidate_query"], ""),
        "retrieved_titles": titles or [],
        "retrieved_docs": docs or [],
        "summary_2": get_first(r, ["summary_2"], ""),
        "pred_answer": get_first(r, ["pred_answer", "answer"], ""),
        "gold_answer": get_first(r, ["gold_answer"], ""),
        "score": get_first(r, ["score", "strict_em_existing"], None),
    }


# -------------------------
# Patch generation
# -------------------------

def format_state_for_prompt(s, max_docs=4):
    docs = s.get("retrieved_docs", []) or []
    docs_txt = "\n".join(f"- {truncate(d, 350)}" for d in docs[:max_docs])
    return f"""query: {s.get("query", "")}
retrieved_titles: {s.get("retrieved_titles", [])}
pred_answer: {s.get("pred_answer", "")}
score: {s.get("score", "")}
summary_2: {truncate(s.get("summary_2", ""), 500)}
retrieved_passages:
{docs_txt}
""".strip()




def patch_generator_variant_instruction(args):
    v = getattr(args, "patch_generator_variant", "default")

    if v == "default":
        return ""

    if v == "edit_script_bridge":
        return """
Additional patch-generation objective: reversible edit-script bridge update.

Do not generate surface-level synonym/quote patches first.
Represent each fail example as a reversible query edit script:
- KEEP: source anchors that must remain in the query
- RESTORE: missing relation or bridge cue needed for the second hop
- RETAIN: uncertain candidate set if multiple candidates are plausible
- DROP: noisy side entities that caused topic drift
- STYLE: compact BM25 keyword query

Generate patches that implement these edit operations as reusable conditional rules.
A good patch should change the query only when it can identify a missing bridge relation, over-collapsed candidate set, or noisy side entity.
Do not write domain-specific rules about films, albums, sports, churches, malls, protests, or episodes.
Do not add broad OR/quote expansion unless it is part of preserving an explicit candidate set from the input.
""".strip()

    if v == "gated_variant_expansion":
        return """
Additional patch-generation objective: gated lexical variant update.

Lexical variants are allowed only under a strict activation gate.
Generate patches that add aliases, quotes, OR variants, parenthetical disambiguators, dates, or title-type clues only when the question or summary_1 explicitly indicates ambiguity, alternate naming, title collision, spelling/diacritic mismatch, historical naming, or media/type ambiguity.

Each patch must include:
- activation condition
- no-op condition
- maximum added token budget
- what input evidence licenses the added variant

Do not add guessed aliases, guessed answer entities, or broad synonym lists.
Do not globally quote every multiword phrase.
Prefer at most two compact variants, and only when they are recoverable from question or summary_1.
""".strip()

    if v == "counterfactual_preservation":
        return """
Additional patch-generation objective: counterfactual preservation update.

Generate preservation-aware prompt patches.
For each candidate patch, first identify why it should not change the already-correct examples.
Then propose a minimal update that only activates on a failure pattern shared by the fail examples.

Each patch must be written as:
- Trigger: when this update applies
- Edit: what query movement it induces
- No-op: when the current query should be preserved
- Risk: what regression it could cause

Prefer patches whose trigger depends on query failure structure, not topic domain.
Do not generate patches that are always-on formatting changes.
Do not optimize for prettier query text; optimize for BM25-relevant evidence movement.
""".strip()

    raise ValueError(f"Unknown patch_generator_variant: {v}")


def make_patch_generation_prompt(args, batch_rows, base_states, oracle_map):
    base_by_q = state_by_question(base_states)

    fail_blocks = []
    correct_blocks = []

    for r in batch_rows:
        q = r["question"]
        base_s = base_by_q[q]
        if r["pool_label"].startswith("fail"):
            oracle = oracle_state_from_row(oracle_map.get(q))
            fail_blocks.append(f"""\
[Fail example]
Question: {q}
Gold answer: {gold_answer_of(r)}
Summary_1: {truncate(r.get("summary_1", ""), 900)}

Current prompt behavior:
{format_state_for_prompt(base_s, max_docs=3)}

Oracle/reference improved hop2 behavior:
{format_state_for_prompt(oracle or {}, max_docs=3)}
""")
        else:
            correct_blocks.append(f"""\
[Correct preservation example]
Question: {q}
Gold answer: {gold_answer_of(r)}
Summary_1: {truncate(r.get("summary_1", ""), 900)}

Current prompt behavior to preserve:
{format_state_for_prompt(base_s, max_docs=3)}
""")

    return f"""\
You are proposing one-step prompt update patches for the HotpotQA hop2 BM25 query writer.

We are doing an SGD-style random minibatch update.

Structural roles:
- Fail examples provide oracle/reference gradient directions: current query behavior should move toward the improved hop2 behavior.
- Correct examples provide prompt-equivalence preservation constraints: the updated prompt should preserve the current metric behavior class.

Your task:
Generate {args.num_patches} candidate prompt patches for `create_query_hop2.predict`.

Important constraints:
- Do NOT rewrite the full prompt.
- Each patch must be a localized instruction or short set of instructions.
- The patch should target common gradient directions across fail examples.
- The patch should avoid changing behavior on already-correct examples.
- BM25 behavior matters more than fluent wording.
- A query should remain compact and keyword-like.
- Do not leak gold titles or answers directly as literal rules.

{patch_generator_variant_instruction(args)}

Fail examples:
{chr(10).join(fail_blocks)}

Correct preservation examples:
{chr(10).join(correct_blocks)}

Return only JSON:
{{
  "patches": [
    {{
      "name": "short_snake_case_name",
      "patch": "instruction text to append to the hop2 query writer prompt",
      "gradient_intent": "what query movement this patch is trying to induce",
      "preservation_intent": "what behavior it tries not to change"
    }}
  ]
}}
""".strip()


def generate_patches(args, batch_rows, base_states, oracle_map):
    prompt = make_patch_generation_prompt(args, batch_rows, base_states, oracle_map)
    obj, raw, err = lm_json_call(args, prompt)
    patches = obj.get("patches", [])
    if not isinstance(patches, list):
        patches = []

    cleaned = []
    for i, p in enumerate(patches[:args.num_patches]):
        if not isinstance(p, dict):
            continue
        patch_text = str(p.get("patch", "")).strip()
        if not patch_text:
            continue
        cleaned.append({
            "candidate_id": len(cleaned),
            "name": str(p.get("name", f"patch_{i}")).strip() or f"patch_{i}",
            "patch": patch_text,
            "gradient_intent": str(p.get("gradient_intent", "")).strip(),
            "preservation_intent": str(p.get("preservation_intent", "")).strip(),
        })

    # Fallback patch if JSON was malformed.
    if not cleaned:
        cleaned.append({
            "candidate_id": 0,
            "name": "fallback_preserve_anchors",
            "patch": (
                "For the second-hop BM25 query, preserve task-relevant named entities, "
                "relation words, aliases, dates, and candidate sets from the question and summary_1. "
                "Remove distractor terms that are not needed for retrieving the missing bridge evidence."
            ),
            "gradient_intent": "fallback",
            "preservation_intent": "fallback",
        })

    return cleaned, prompt, raw, err


# -------------------------
# Equal / Compare judges
# -------------------------

def make_equal_prompt(row, base_state, patch_state):
    return f"""\
You are a metric-aware equivalence judge for a HotpotQA hop2 query writer prompt.

You are NOT judging whether two query strings are textually similar.
You are judging whether two prompts induce the same local metric behavior class for this sample.

Prompt A is the base prompt.
Prompt B is the patched prompt.

Two prompt-induced states are equivalent if:
- both recover the same task-relevant support/evidence, or
- both are successful in the same task-relevant way, or
- both fail in materially the same way.

They are NOT equivalent if one state recovers missing support or answer-sufficient evidence and the other does not, or if they fail for materially different retrieval reasons.

Question:
{row.get("question")}

Gold answer:
{gold_answer_of(row)}

Gold support titles:
{gold_support_titles_of(row)}

Missing support titles after hop1:
{missing_titles_of(row)}

State induced by Prompt A:
{format_state_for_prompt(base_state, max_docs=5)}

State induced by Prompt B:
{format_state_for_prompt(patch_state, max_docs=5)}

Return only JSON:
{{
  "equivalent": true or false,
  "relation": "same_success" | "same_failure" | "different_success_quality" | "different_failure_mode",
  "metric_basis": ["short reason 1", "short reason 2"],
  "material_difference": "none or short description",
  "confidence": 0.0
}}
""".strip()


def make_gradient_compare_prompt(row, base_state, patch_state, oracle_state):
    return f"""\
You are a local tool-aware gradient comparison judge for a HotpotQA hop2 BM25 query writer.

You do NOT compare query strings directly.
You compare two gradient/update directions induced from the same starting state.

Gradient A:
  start = current/base prompt state
  end = patched prompt state

Gradient B:
  start = current/base prompt state
  end = no-op state, i.e. the base prompt state again

Decide which gradient moves the sample closer to the success equivalence class.

A gradient is better if its end state better satisfies the local retrieval/answerability objective while preserving task-relevant anchors:
- retrieves missing support or answer-sufficient evidence
- preserves necessary entities, aliases, dates, and relations
- removes distractors that cause topic drift
- does not overfit to irrelevant titles or answer strings
- yields evidence more compatible with the gold support information

Tie-first calibration rule:
- If the two end states retrieve the same gold support titles and recover the same missing support titles, return "tie" unless one end state clearly provides more answer-sufficient evidence or avoids a clear task-relevant distractor.
- Do not prefer a gradient merely because the end query is more fluent, more compact, more canonical, or semantically more plausible.
- BM25-relevant evidence behavior dominates textual query quality.
- A local wording improvement is not a distance improvement unless it changes retrieved support, answerability, or a clear retrieval failure mode.

Question:
{row.get("question")}

Gold answer:
{gold_answer_of(row)}

Gold support titles:
{gold_support_titles_of(row)}

Missing support titles after hop1:
{missing_titles_of(row)}

Current/base state:
{format_state_for_prompt(base_state, max_docs=5)}

Reference oracle/improved end state:
{format_state_for_prompt(oracle_state or {}, max_docs=5)}

Gradient A end state, from patched prompt:
{format_state_for_prompt(patch_state, max_docs=5)}

Gradient B end state, no-op:
{format_state_for_prompt(base_state, max_docs=5)}

Return only JSON:
{{
  "closer": "A" | "B" | "tie" | "incomparable",
  "comparison_basis": ["short reason 1", "short reason 2"],
  "minimality_basis": ["what task-relevant behavior is preserved or minimally changed"],
  "confidence": 0.0
}}
""".strip()


def judge_equal(args, row, base_state, patch_state):
    prompt = make_equal_prompt(row, base_state, patch_state)
    obj, raw, err = lm_json_call(args, prompt)
    return {
        "judge_type": "equal_prompt_relation",
        "equivalent": bool(obj.get("equivalent", False)),
        "relation": obj.get("relation", ""),
        "metric_basis": obj.get("metric_basis", []),
        "material_difference": obj.get("material_difference", ""),
        "confidence": obj.get("confidence", None),
        "raw": raw,
        "error": err,
    }


def judge_compare(args, row, base_state, patch_state, oracle_state):
    prompt = make_gradient_compare_prompt(row, base_state, patch_state, oracle_state)
    obj, raw, err = lm_json_call(args, prompt)
    return {
        "judge_type": "compare_gradient_relation",
        "closer": obj.get("closer", ""),
        "comparison_basis": obj.get("comparison_basis", []),
        "minimality_basis": obj.get("minimality_basis", []),
        "confidence": obj.get("confidence", None),
        "raw": raw,
        "error": err,
    }


# -------------------------
# Metrics / selection
# -------------------------

def summarize_states(rows, base_states, patch_states):
    base = state_by_question(base_states)
    patch = state_by_question(patch_states)

    out = {
        "n": len(rows),
        "acc_before": mean(base[r["question"]]["score"] for r in rows) if rows else 0.0,
        "acc_after": mean(patch[r["question"]]["score"] for r in rows) if rows else 0.0,
    }

    flip = 0
    brk = 0
    for r in rows:
        b = base[r["question"]]["score"]
        a = patch[r["question"]]["score"]
        if b < 1.0 and a >= 1.0:
            flip += 1
        if b >= 1.0 and a < 1.0:
            brk += 1

    out["flip"] = flip
    out["break"] = brk
    out["net_gain"] = flip - brk
    return out


def choose_candidate(cands):
    # Prefer candidates with gradient gain, while preserving prompt-equivalence on correct examples.
    # correct_preserve_threshold is soft: if no candidate satisfies it, fall back to net judge score.
    eligible = [c for c in cands if c["correct_preserve"] >= c["correct_preserve_threshold"]]
    pool = eligible if eligible else cands

    pool = sorted(
        pool,
        key=lambda c: (
            c["wrong_gain"],
            c["correct_preserve"],
            c["batch_actual_net_gain"],
            c["batch_acc_after"],
        ),
        reverse=True,
    )
    return pool[0], bool(eligible)


def write_summary(path, trial_rows):
    lines = []
    lines.append("# Trace-SGD independent one-step summary\n")
    lines.append("| batch_id | selected | eligible | batch acc | batch flip | batch break | batch net | full acc | full flip | full break | full net | selected rank by actual net |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for r in trial_rows:
        lines.append(
            f"| {r['batch_id']} | {r['selected_patch_name']} | {int(r['selected_from_eligible'])} | "
            f"{r['batch_acc_before']:.3f}→{r['batch_acc_after']:.3f} | "
            f"{r['batch_flip']} | {r['batch_break']} | {r['batch_net_gain']} | "
            f"{r.get('full_acc_before', 0):.3f}→{r.get('full_acc_after', 0):.3f} | "
            f"{r.get('full_flip', 0)} | {r.get('full_break', 0)} | {r.get('full_net_gain', 0)} | "
            f"{r.get('selected_rank_by_actual_net_gain', '')} |"
        )

    if trial_rows:
        lines.append("\n## Aggregate\n")
        lines.append(f"- trials: {len(trial_rows)}")
        lines.append(f"- mean batch Δacc: {mean(r['batch_acc_after'] - r['batch_acc_before'] for r in trial_rows):+.3f}")
        lines.append(f"- mean batch net gain: {mean(r['batch_net_gain'] for r in trial_rows):+.3f}")
        if "full_acc_after" in trial_rows[0]:
            lines.append(f"- mean full Δacc: {mean(r['full_acc_after'] - r['full_acc_before'] for r in trial_rows):+.3f}")
            lines.append(f"- mean full net gain: {mean(r['full_net_gain'] for r in trial_rows):+.3f}")
        lines.append(f"- positive batch net trials: {sum(r['batch_net_gain'] > 0 for r in trial_rows)} / {len(trial_rows)}")
        lines.append(f"- nonnegative full net trials: {sum(r.get('full_net_gain', 0) >= 0 for r in trial_rows)} / {len(trial_rows)}")

    path.write_text("\n".join(lines))


# -------------------------
# Main
# -------------------------

def main():
    ap = argparse.ArgumentParser()

    ap.add_argument("--pool-dir", required=True)
    ap.add_argument("--minibatch-path", required=True)
    ap.add_argument("--batch-ids", default="0,1,2")

    ap.add_argument("--oracle-rows-path", required=True)
    ap.add_argument("--oracle-arm", default="support_aware_ideal_delta")

    ap.add_argument("--base-prompt-candidate", default="")
    ap.add_argument("--fixed-prompt-candidate", required=True)

    ap.add_argument("--num-patches", type=int, default=4)
    ap.add_argument(
        "--patch-generator-variant",
        default="default",
        choices=["default", "edit_script_bridge", "gated_variant_expansion", "counterfactual_preservation"],
    )
    ap.add_argument("--select-mode", default="equal_compare")
    ap.add_argument("--eval-full-pool", action="store_true")
    ap.add_argument("--base-full-cache-path", default="")

    ap.add_argument("--model", default=os.environ.get("TASK_MODEL", "openai/gpt-5-mini"))
    ap.add_argument("--api-base", default=os.environ.get("TASK_API_BASE", ""))
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--num-threads", type=int, default=4)

    ap.add_argument("--retriever-k", type=int, default=7)
    ap.add_argument("--retriever-dir", default=os.environ.get("HOTPOT_RETRIEVER_DIR", ""))

    ap.add_argument("--out-dir", required=True)

    args = ap.parse_args()

    if "gpt-5" in args.model:
        args.temperature = 1.0
        if args.max_tokens < 16000:
            args.max_tokens = 16000

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dspy.settings.configure(lm=make_lm(args))

    minibatch_rows = read_jsonl(args.minibatch_path)
    batch_ids = [int(x) for x in args.batch_ids.split(",") if x.strip()]

    by_batch = {}
    for b in batch_ids:
        rows = [r for r in minibatch_rows if int(r["batch_id"]) == b]
        if not rows:
            raise ValueError(f"No rows found for batch_id={b}")
        labels = {r["pool_label"] for r in rows}
        if len(labels) < 2:
            raise ValueError(f"Batch {b} does not contain both fail/correct labels: {labels}")
        by_batch[b] = rows

    mixed_pool = read_jsonl(Path(args.pool_dir) / "mixed_pool.jsonl") if args.eval_full_pool else []

    oracle_map = load_oracle_map(args.oracle_rows_path, args.oracle_arm)
    base_instr = base_create_query_instruction(args)

    all_trial_summaries = []
    all_patches = []
    all_judges = []
    all_batch_rollouts = []
    all_full_rollouts = []

    # Full-pool base cache, reused across trials.
    full_base_states = None
    if args.eval_full_pool:
        cache_path = Path(args.base_full_cache_path) if args.base_full_cache_path else None
        if cache_path and cache_path.exists():
            print("[full pool] loading cached base prompt states:", cache_path)
            full_base_states = read_jsonl(cache_path)
        else:
            print("[full pool] rolling out base prompt on mixed pool...")
            full_base_states = rollout_many(args, mixed_pool, base_instr, "base_prompt", "full base")
            if cache_path:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                write_jsonl(cache_path, full_base_states)
                print("[full pool] wrote cached base prompt states:", cache_path)

    for batch_id, batch_rows in by_batch.items():
        print(f"\n===== Batch {batch_id} =====")
        fail_rows = [r for r in batch_rows if r["pool_label"].startswith("fail")]
        correct_rows = [r for r in batch_rows if r["pool_label"].startswith("correct")]
        correct_preserve_threshold = max(0, len(correct_rows) - 1)

        print("[batch]", batch_id, "n", len(batch_rows), "fail", len(fail_rows), "correct", len(correct_rows))

        print("[batch] rolling out base prompt...")
        base_states = rollout_many(args, batch_rows, base_instr, f"batch{batch_id}_base", f"batch {batch_id} base")
        base_by_q = state_by_question(base_states)

        print("[batch] generating patches...")
        patches, patch_prompt, patch_raw, patch_err = generate_patches(args, batch_rows, base_states, oracle_map)

        for p in patches:
            p_row = {
                "batch_id": batch_id,
                **p,
                "generation_error": patch_err,
                "generation_raw": patch_raw,
            }
            all_patches.append(p_row)

        candidate_summaries = []

        for p in patches:
            cand_id = p["candidate_id"]
            patch_instr = patched_instruction(base_instr, p["patch"])
            prompt_label = f"batch{batch_id}_cand{cand_id}_{p['name']}"

            print(f"[batch {batch_id}] rolling out candidate {cand_id}: {p['name']}")
            patch_states = rollout_many(args, batch_rows, patch_instr, prompt_label, f"batch {batch_id} cand {cand_id}")
            patch_by_q = state_by_question(patch_states)

            for s in patch_states:
                all_batch_rollouts.append({
                    "batch_id": batch_id,
                    "candidate_id": cand_id,
                    "candidate_name": p["name"],
                    **s,
                })

            wrong_gain = 0
            correct_preserve = 0

            # Judges
            for r in batch_rows:
                q = r["question"]
                bstate = base_by_q[q]
                pstate = patch_by_q[q]

                if r["pool_label"].startswith("correct"):
                    j = judge_equal(args, r, bstate, pstate)
                    if j["equivalent"]:
                        correct_preserve += 1
                else:
                    oracle = oracle_state_from_row(oracle_map.get(q))
                    j = judge_compare(args, r, bstate, pstate, oracle)
                    if j["closer"] == "A":
                        wrong_gain += 1

                all_judges.append({
                    "batch_id": batch_id,
                    "candidate_id": cand_id,
                    "candidate_name": p["name"],
                    "pool_label": r["pool_label"],
                    "question": q,
                    **j,
                })

            batch_metrics = summarize_states(batch_rows, base_states, patch_states)

            cand_summary = {
                "batch_id": batch_id,
                "candidate_id": cand_id,
                "candidate_name": p["name"],
                "patch": p["patch"],
                "wrong_gain": wrong_gain,
                "correct_preserve": correct_preserve,
                "correct_preserve_threshold": correct_preserve_threshold,
                "batch_acc_before": batch_metrics["acc_before"],
                "batch_acc_after": batch_metrics["acc_after"],
                "batch_actual_flip": batch_metrics["flip"],
                "batch_actual_break": batch_metrics["break"],
                "batch_actual_net_gain": batch_metrics["net_gain"],
            }
            candidate_summaries.append(cand_summary)

        selected, from_eligible = choose_candidate(candidate_summaries)

        # Rank by actual net gain descending.
        ranked_actual = sorted(
            candidate_summaries,
            key=lambda c: (c["batch_actual_net_gain"], c["batch_acc_after"]),
            reverse=True,
        )
        actual_rank = 1 + [c["candidate_id"] for c in ranked_actual].index(selected["candidate_id"])

        print("[selected]", selected["candidate_id"], selected["candidate_name"], "rank_by_actual", actual_rank)

        selected_patch = next(p for p in patches if p["candidate_id"] == selected["candidate_id"])
        selected_instr = patched_instruction(base_instr, selected_patch["patch"])

        # Reuse selected candidate batch metrics from candidate_summaries.
        trial = {
            "batch_id": batch_id,
            "selected_candidate_id": selected["candidate_id"],
            "selected_patch_name": selected["candidate_name"],
            "selected_patch": selected["patch"],
            "selected_from_eligible": from_eligible,
            "wrong_gain_by_compare": selected["wrong_gain"],
            "correct_preserve_by_equal": selected["correct_preserve"],
            "correct_preserve_threshold": selected["correct_preserve_threshold"],
            "batch_acc_before": selected["batch_acc_before"],
            "batch_acc_after": selected["batch_acc_after"],
            "batch_flip": selected["batch_actual_flip"],
            "batch_break": selected["batch_actual_break"],
            "batch_net_gain": selected["batch_actual_net_gain"],
            "selected_rank_by_actual_net_gain": actual_rank,
        }

        if args.eval_full_pool:
            print(f"[batch {batch_id}] evaluating selected patch on full pool...")
            full_patch_states = rollout_many(
                args,
                mixed_pool,
                selected_instr,
                f"batch{batch_id}_selected_{selected_patch['name']}",
                f"full selected batch {batch_id}",
            )
            for s in full_patch_states:
                all_full_rollouts.append({
                    "batch_id": batch_id,
                    "selected_candidate_id": selected["candidate_id"],
                    "selected_patch_name": selected["candidate_name"],
                    **s,
                })

            full_metrics = summarize_states(mixed_pool, full_base_states, full_patch_states)
            fail_pool = [r for r in mixed_pool if r["pool_label"].startswith("fail")]
            correct_pool = [r for r in mixed_pool if r["pool_label"].startswith("correct")]
            fail_metrics = summarize_states(fail_pool, full_base_states, full_patch_states)
            correct_metrics = summarize_states(correct_pool, full_base_states, full_patch_states)

            trial.update({
                "full_acc_before": full_metrics["acc_before"],
                "full_acc_after": full_metrics["acc_after"],
                "full_flip": full_metrics["flip"],
                "full_break": full_metrics["break"],
                "full_net_gain": full_metrics["net_gain"],

                "fail_pool_acc_before": fail_metrics["acc_before"],
                "fail_pool_acc_after": fail_metrics["acc_after"],
                "correct_pool_acc_before": correct_metrics["acc_before"],
                "correct_pool_acc_after": correct_metrics["acc_after"],
            })

        all_trial_summaries.append(trial)

        print("\n[trial summary]")
        print("batch_id:", trial["batch_id"])
        print("selected:", trial["selected_patch_name"])
        print("wrong_gain_by_compare:", trial["wrong_gain_by_compare"])
        print("correct_preserve_by_equal:", trial["correct_preserve_by_equal"], "/", trial["correct_preserve_threshold"] + 1)
        print("batch acc:", trial["batch_acc_before"], "->", trial["batch_acc_after"])
        print("batch flip/break/net:", trial["batch_flip"], trial["batch_break"], trial["batch_net_gain"])
        if "full_acc_after" in trial:
            print("full acc:", trial["full_acc_before"], "->", trial["full_acc_after"])
            print("full flip/break/net:", trial["full_flip"], trial["full_break"], trial["full_net_gain"])
            print("fail pool acc:", trial["fail_pool_acc_before"], "->", trial["fail_pool_acc_after"])
            print("correct pool acc:", trial["correct_pool_acc_before"], "->", trial["correct_pool_acc_after"])
        print("selected rank by actual net:", trial["selected_rank_by_actual_net_gain"])

        write_jsonl(out_dir / "trial_summary.partial.jsonl", all_trial_summaries)
        write_summary(out_dir / "summary.partial.md", all_trial_summaries)

    write_jsonl(out_dir / "patches.jsonl", all_patches)
    write_jsonl(out_dir / "judge_rows.jsonl", all_judges)
    write_jsonl(out_dir / "batch_rollouts.jsonl", all_batch_rollouts)
    if all_full_rollouts:
        write_jsonl(out_dir / "full_rollouts.jsonl", all_full_rollouts)
    write_jsonl(out_dir / "trial_summary.jsonl", all_trial_summaries)
    write_summary(out_dir / "summary.md", all_trial_summaries)

    (out_dir / "config.json").write_text(json.dumps(vars(args), indent=2, ensure_ascii=False))

    print("\n[wrote]", out_dir / "summary.md")
    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
