import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from statistics import mean

import dspy

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from examples.hotpotqa.program import HotpotMultiHop
from examples.hotpotqa.retriever import set_retriever_dir
from examples.hotpotqa.metric import answer_match_fn

try:
    from examples.hotpotqa.data import load_hotpot_splits
except Exception:
    load_hotpot_splits = None

try:
    from tqdm.auto import tqdm
except Exception:
    def tqdm(x, **kwargs):
        return x


DEFAULT_ROOT = (
    "outputs/hotpotqa_representation_prompt_screening/"
    "rep_prompt_screening_24_dev300_final_v2/conditions"
)

DEFAULT_FIXED_PROMPT = (
    DEFAULT_ROOT + "/final_manual_only/prompt_candidate.json"
)

DEFAULT_R6_PROMPT = (
    DEFAULT_ROOT
    + "/R6_hybrid_edit_script__MB1_retrieval_gain_recover__S1_conservative_reversible"
    + "/prompt_candidate.json"
)

DEFAULT_TRACE = (
    DEFAULT_ROOT + "/final_manual_only/analysis/rollout_traces.jsonl"
)

DEFAULT_ARMS = [
    "baseline_cached",
    "r6_global",
    "support_aware_ideal_delta",
    "answer_aware_ideal_delta",
    "support_title_ceiling",
]


def _get(obj, key, default=None):
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]
    except Exception:
        return default


def parse_arms(s):
    if not s or s == "all":
        return DEFAULT_ARMS
    arms = [x.strip() for x in s.split(",") if x.strip()]
    bad = [a for a in arms if a not in DEFAULT_ARMS and a != "baseline_recomputed"]
    if bad:
        raise ValueError(f"Unknown arms: {bad}")
    return arms


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


def title_from_doc(doc):
    return str(doc).split(" | ", 1)[0].strip()


def title_set_from_docs(docs):
    return set(title_from_doc(d) for d in (docs or []) if str(d).strip())


def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def normalize_answer(text):
    text = str(text).lower().strip()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def clean_lm_text(x):
    if isinstance(x, list):
        x = x[0] if x else ""
    x = str(x).strip()
    x = x.strip("` \n")
    if x.lower().startswith("json"):
        x = x[4:].strip()
    return x


def clean_query(x):
    x = clean_lm_text(x)

    # Try JSON first.
    try:
        obj = json.loads(x)
        if isinstance(obj, dict):
            for k in ["query", "rewritten_query", "hop2_query"]:
                if k in obj:
                    return str(obj[k]).strip()
    except Exception:
        pass

    # Strip common labels.
    lines = [l.strip() for l in x.splitlines() if l.strip()]
    if not lines:
        return ""

    for l in lines:
        m = re.match(r"^(query|rewritten query|hop2 query)\s*:\s*(.+)$", l, re.I)
        if m:
            return m.group(2).strip().strip('"')

    # Prefer the last non-bulleted short line if output is verbose.
    short = [l for l in lines if len(l.split()) <= 24 and not l.startswith(("-", "*"))]
    if short:
        return short[-1].strip().strip('"')

    return lines[-1].strip().strip('"')


def lm_raw_call(lm, prompt, retries=3, sleep_s=2.0):
    last_err = None
    for i in range(retries):
        try:
            out = lm(prompt)
            return clean_lm_text(out), None
        except Exception as e:
            last_err = str(e)
            if i + 1 < retries:
                time.sleep(sleep_s * (i + 1))
    return "", last_err


def set_instructions_on_predictor(predictor, instructions):
    # DSPy signatures usually support with_instructions.
    try:
        predictor.signature = predictor.signature.with_instructions(instructions)
        return
    except Exception:
        pass

    # Fallback for mutable signature objects.
    try:
        predictor.signature.instructions = instructions
        return
    except Exception:
        pass

    raise RuntimeError("Could not set predictor instructions.")


def apply_prompt_candidate(program, prompt_candidate_path):
    data = json.load(open(prompt_candidate_path))
    prompts = data.get("prompts", {})
    for full_key, instr in prompts.items():
        if "." not in full_key:
            continue
        module_name, pred_name = full_key.split(".", 1)
        if not hasattr(program, module_name):
            continue
        module = getattr(program, module_name)
        predictor = getattr(module, pred_name, None)
        if predictor is None:
            # Some DSPy modules directly expose signature.
            predictor = module
        set_instructions_on_predictor(predictor, str(instr))
    return data


def load_eval_examples(args):
    """
    Load the same deterministic Hotpot split only to recover full gold support evidence.
    The rollout trace already contains question/answer/titles, so failure here is non-fatal.
    """
    if load_hotpot_splits is None:
        return {}

    try:
        trainset, valset, testset = load_hotpot_splits(
            train_size=args.train_size,
            val_size=args.val_size,
            test_size=args.test_size,
            seed=args.seed,
            hf_split=args.hf_split,
        )
        if args.eval_split == "train":
            base = trainset
        elif args.eval_split == "val":
            base = valset
        else:
            base = testset

        # Existing summaries show eval_split=test, eval_offset=100, eval_limit=300.
        eval_slice = base[args.eval_offset: args.eval_offset + args.eval_limit]
        q_to_ex = {ex.question: ex for ex in eval_slice}
        # Also include full base in case eval_index is absolute or offset handling differs.
        q_to_ex.update({ex.question: ex for ex in base})
        return q_to_ex
    except Exception as e:
        print(f"[warn] could not load Hotpot examples for support evidence: {e}")
        return {}


def support_evidence_from_example(ex):
    if ex is None:
        return ""

    context = _get(ex, "context", {}) or {}
    supporting_facts = _get(ex, "supporting_facts", {}) or {}

    titles = context.get("title", [])
    sentences = context.get("sentences", [])
    title_to_sents = {t: s for t, s in zip(titles, sentences)}

    support_titles = supporting_facts.get("title", [])
    support_sent_ids = supporting_facts.get("sent_id", [])

    chunks = []
    for title, sent_id in zip(support_titles, support_sent_ids):
        sents = title_to_sents.get(title, [])
        if isinstance(sent_id, int) and 0 <= sent_id < len(sents):
            chunks.append(f"{title} | {sents[sent_id]}")
        elif sents:
            chunks.append(f"{title} | {' '.join(sents)}")

    if chunks:
        return "\n".join(chunks)

    # Fallback: all documents whose titles are support titles.
    for title in sorted(set(support_titles)):
        sents = title_to_sents.get(title, [])
        if sents:
            chunks.append(f"{title} | {' '.join(sents)}")
    return "\n".join(chunks)


def support_titles_from_trace(t):
    return set(str(x).strip() for x in t.get("gold_support_titles", []) if str(x).strip())


def select_traces(traces, subset):
    selected = []
    for t in traces:
        score = safe_float(t.get("score", 0.0))
        missing_after_hop2 = set(t.get("missing_titles_after_hop2", []) or [])
        hop1_titles = set(t.get("hop1_titles", []) or [])
        gold_titles = support_titles_from_trace(t)
        missing_after_hop1 = gold_titles - hop1_titles

        if subset == "all":
            keep = True
        elif subset == "wrong":
            keep = score < 1.0
        elif subset == "hop2_miss":
            keep = len(missing_after_hop2) > 0
        elif subset == "wrong_hop2_miss":
            keep = score < 1.0 and len(missing_after_hop2) > 0
        elif subset == "wrong_missing_after_hop1":
            keep = score < 1.0 and len(missing_after_hop1) > 0
        else:
            raise ValueError(f"Unknown subset: {subset}")

        if keep:
            selected.append(t)
    return selected


def retrieval_metrics(trace, hop2_docs):
    gold = support_titles_from_trace(trace)
    hop1_titles = set(trace.get("hop1_titles", []) or [])
    hop2_titles = title_set_from_docs(hop2_docs)
    all_titles = hop1_titles | hop2_titles

    missing_after_hop1 = gold - hop1_titles
    recovered_missing = missing_after_hop1 & hop2_titles
    hit_total = gold & all_titles
    hit_hop2 = gold & hop2_titles

    denom_total = max(1, len(gold))
    denom_missing = max(1, len(missing_after_hop1))

    return {
        "gold_support_titles": sorted(gold),
        "hop1_titles": sorted(hop1_titles),
        "hop2_titles": sorted(hop2_titles),
        "hit_titles_total": sorted(hit_total),
        "hit_titles_hop2": sorted(hit_hop2),
        "missing_titles_after_hop1": sorted(missing_after_hop1),
        "recovered_missing_titles_hop2": sorted(recovered_missing),
        "missing_titles_after_hop2": sorted(gold - all_titles),
        "support_recall_total": len(hit_total) / denom_total,
        "support_recall_hop2_only": len(hit_hop2) / denom_total,
        "missing_recovery_rate": len(recovered_missing) / denom_missing,
        "hop2_support_hit": float(len(hit_hop2) > 0),
        "hop2_new_support_hit": float(len(recovered_missing) > 0),
        "retrieval_failure": float(len(hit_total) == 0),
    }


def make_support_aware_delta_prompt(trace, support_evidence):
    question = trace["question"]
    summary_1 = trace.get("summary_1", "")
    current_query = trace.get("hop2_query", "")
    hop1_titles = trace.get("hop1_titles", [])
    hop2_titles = trace.get("hop2_titles", [])
    gold_titles = trace.get("gold_support_titles", [])
    missing_after_hop2 = trace.get("missing_titles_after_hop2", [])

    return f"""\
You are constructing an oracle local query-delta descriptor for the second hop of a HotpotQA BM25 retriever.

The descriptor will be used to rewrite the current second-hop query.
Do NOT answer the question.
Do NOT output a query.
Output only a concise local query-delta descriptor: what to preserve, add, remove, or refocus.

Question:
{question}

First-hop summary:
{summary_1}

Current second-hop query:
{current_query}

First-hop retrieved titles:
{hop1_titles}

Current second-hop retrieved titles:
{hop2_titles}

Oracle support titles:
{gold_titles}

Support evidence:
{support_evidence if support_evidence else "(support evidence unavailable; use support titles only)"}

Titles still missing after the current second hop:
{missing_after_hop2}

Write the ideal BM25-facing local query delta.
Focus on:
- anchors or aliases to preserve
- missing relation cues to add
- candidate entities to keep as uncertain candidates
- noisy entities or relations to remove
- answer-type words that may help retrieval

Do not include the final answer string unless it is itself a support-page title or explicit query anchor.
""".strip()


def make_answer_aware_delta_prompt(trace, support_evidence):
    base = make_support_aware_delta_prompt(trace, support_evidence)
    return base + f"""

Additional oracle answer information:
- Current predicted answer: {trace.get("pred_answer")}
- Gold answer: {trace.get("gold_answer")}

Use the gold answer only to infer what evidence relation or entity type the second-hop query should target.
Do not write a final answer. Output only the local query-delta descriptor.
""".strip()


def make_query_rewrite_prompt(trace, delta_context):
    return f"""\
You are rewriting a HotpotQA second-hop BM25 query.

Question:
{trace["question"]}

First-hop summary:
{trace.get("summary_1", "")}

Current second-hop query:
{trace.get("hop2_query", "")}

Local query-delta descriptor:
{delta_context}

Rewrite the second-hop BM25 query.

Rules:
- Output only the rewritten query.
- Use compact keyword-query style, not a full explanation.
- Preserve useful named entities, titles, aliases, dates, and relation words.
- Add only terms suggested by the question, summary, or descriptor.
- Remove distractor terms that would pull BM25 to the wrong page.
- Do not output the final answer.
""".strip()


def run_downstream(program, trace, query, retriever_k, retries=1):
    hop2_docs = program.retrieve_k(query).passages
    summary_2 = program.summarize2(
        question=trace["question"],
        context=trace.get("summary_1", ""),
        passages=hop2_docs,
    ).summary
    answer = program.final_answer(
        question=trace["question"],
        summary_1=trace.get("summary_1", ""),
        summary_2=summary_2,
    ).answer

    gold = trace.get("gold_answer")
    score = float(answer_match_fn(answer, [gold], frac=1.0))

    met = retrieval_metrics(trace, hop2_docs)

    return {
        "hop2_query": query,
        "hop2_docs": hop2_docs,
        "summary_2": summary_2,
        "pred_answer": answer,
        "score": score,
        **met,
    }


def baseline_cached_row(trace):
    met = {
        "gold_support_titles": trace.get("gold_support_titles", []),
        "hop1_titles": trace.get("hop1_titles", []),
        "hop2_titles": trace.get("hop2_titles", []),
        "hit_titles_total": trace.get("hit_titles_total", []),
        "hit_titles_hop2": sorted(
            set(trace.get("gold_support_titles", [])) & set(trace.get("hop2_titles", []))
        ),
        "missing_titles_after_hop1": sorted(
            set(trace.get("gold_support_titles", [])) - set(trace.get("hop1_titles", []))
        ),
        "recovered_missing_titles_hop2": sorted(
            (set(trace.get("gold_support_titles", [])) - set(trace.get("hop1_titles", [])))
            & set(trace.get("hop2_titles", []))
        ),
        "missing_titles_after_hop2": trace.get("missing_titles_after_hop2", []),
        "support_recall_total": safe_float(trace.get("support_recall_total")),
        "support_recall_hop2_only": safe_float(trace.get("support_recall_hop2_only")),
        "missing_recovery_rate": 0.0,
        "hop2_support_hit": float(
            len(set(trace.get("gold_support_titles", [])) & set(trace.get("hop2_titles", []))) > 0
        ),
        "hop2_new_support_hit": float(len(trace.get("new_support_titles_hop2", []) or []) > 0),
        "retrieval_failure": float(safe_float(trace.get("support_recall_total")) == 0.0),
    }

    missing_after_hop1 = set(met["missing_titles_after_hop1"])
    recovered = set(met["recovered_missing_titles_hop2"])
    met["missing_recovery_rate"] = len(recovered) / max(1, len(missing_after_hop1))

    return {
        "hop2_query": trace.get("hop2_query", ""),
        "hop2_docs": trace.get("hop2_docs", []),
        "summary_2": trace.get("summary_2", ""),
        "pred_answer": trace.get("pred_answer", ""),
        "score": safe_float(trace.get("score")),
        **met,
    }


def support_title_ceiling_query(trace):
    base_q = str(trace.get("hop2_query", "")).strip()
    gold = support_titles_from_trace(trace)
    hop1 = set(trace.get("hop1_titles", []) or [])
    missing_after_hop1 = sorted(gold - hop1)

    if missing_after_hop1:
        titles = " ".join(missing_after_hop1)
    else:
        titles = " ".join(sorted(gold))

    return f"{base_q} {titles}".strip()


def aggregate(rows):
    groups = {}
    for r in rows:
        groups.setdefault(r["arm"], []).append(r)

    metric_keys = [
        "score",
        "support_recall_total",
        "support_recall_hop2_only",
        "missing_recovery_rate",
        "hop2_support_hit",
        "hop2_new_support_hit",
        "retrieval_failure",
        "final_corrected_vs_baseline",
        "retrieval_improved_vs_baseline",
        "retrieval_improved_but_final_wrong",
    ]

    out = []
    for arm, rs in sorted(groups.items()):
        d = {"arm": arm, "n": len(rs)}
        for k in metric_keys:
            vals = [safe_float(r.get(k, 0.0)) for r in rs]
            d[k] = mean(vals) if vals else 0.0
        out.append(d)
    return out


def write_summary(path, rows, selected_count):
    agg = aggregate(rows)

    lines = []
    lines.append("# Ideal context upper-bound summary\n")
    lines.append(f"Selected examples: {selected_count}\n")
    lines.append("\n## By arm\n")
    header = [
        "arm", "n", "EM", "total recall", "hop2 recall", "MR",
        "hop2 hit", "new hit", "retrieval fail",
        "corrected", "ret improved", "ret improved final wrong",
    ]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] + ["---:"] * (len(header) - 1)) + "|")
    for d in agg:
        lines.append(
            "| {arm} | {n} | {score:.3f} | {support_recall_total:.3f} | "
            "{support_recall_hop2_only:.3f} | {missing_recovery_rate:.3f} | "
            "{hop2_support_hit:.3f} | {hop2_new_support_hit:.3f} | "
            "{retrieval_failure:.3f} | {final_corrected_vs_baseline:.3f} | "
            "{retrieval_improved_vs_baseline:.3f} | "
            "{retrieval_improved_but_final_wrong:.3f} |".format(**d)
        )

    lines.append("\n## Interpretation handles\n")
    lines.append("- `corrected`: baseline cached answer was wrong, but this arm is correct.")
    lines.append("- `ret improved`: total support recall is higher than baseline cached.")
    lines.append("- `ret improved final wrong`: retrieval improved but final answer remains wrong.")
    path.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--trace-path", default=DEFAULT_TRACE)
    parser.add_argument("--fixed-prompt-candidate", default=DEFAULT_FIXED_PROMPT)
    parser.add_argument("--r6-prompt-candidate", default=DEFAULT_R6_PROMPT)
    parser.add_argument("--out-dir", default="experiments/deltaq/results_hotpot_ideal_context_upper_bound")

    parser.add_argument("--retriever-dir", default=os.environ.get("HOTPOT_RETRIEVER_DIR"))
    parser.add_argument("--k", type=int, default=7)

    parser.add_argument("--subset", default="wrong_hop2_miss",
                        choices=["all", "wrong", "hop2_miss", "wrong_hop2_miss", "wrong_missing_after_hop1"])
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--arms", default="all")

    parser.add_argument("--model", default=os.environ.get("TASK_MODEL", "openai/gpt-5-mini"))
    parser.add_argument("--api-base", default=os.environ.get("TASK_API_BASE", ""))
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=16000)
    parser.add_argument("--retries", type=int, default=3)

    # Split reconstruction only for support evidence.
    parser.add_argument("--hf-split", default="train")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-size", type=int, default=100)
    parser.add_argument("--val-size", type=int, default=100)
    parser.add_argument("--test-size", type=int, default=500)
    parser.add_argument("--eval-split", default="test", choices=["train", "val", "test"])
    parser.add_argument("--eval-offset", type=int, default=100)
    parser.add_argument("--eval-limit", type=int, default=300)

    args = parser.parse_args()

    if "gpt-5" in args.model:
        if args.temperature not in (1.0, None):
            print(f"[warn] GPT-5 model requires temperature=1.0 or None; overriding {args.temperature} -> 1.0")
            args.temperature = 1.0
        if args.max_tokens is not None and args.max_tokens < 16000:
            print(f"[warn] GPT-5 model requires max_tokens>=16000 or None; overriding {args.max_tokens} -> 16000")
            args.max_tokens = 16000

    if args.retriever_dir:
        set_retriever_dir(args.retriever_dir)

    lm_kwargs = {
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_key:
        lm_kwargs["api_key"] = args.api_key
    if args.api_base:
        lm_kwargs["api_base"] = args.api_base

    lm = dspy.LM(args.model, **lm_kwargs)
    dspy.settings.configure(lm=lm)

    fixed_program = HotpotMultiHop(k=args.k, retriever_dir=args.retriever_dir)
    apply_prompt_candidate(fixed_program, args.fixed_prompt_candidate)

    r6_program = HotpotMultiHop(k=args.k, retriever_dir=args.retriever_dir)
    apply_prompt_candidate(r6_program, args.r6_prompt_candidate)

    traces_all = read_jsonl(args.trace_path)
    traces = select_traces(traces_all, args.subset)
    traces = traces[args.offset:]
    if args.limit is not None:
        traces = traces[:args.limit]

    arms = parse_arms(args.arms)

    q_to_ex = load_eval_examples(args)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[info] trace_path: {args.trace_path}")
    print(f"[info] total traces: {len(traces_all)}")
    print(f"[info] selected subset={args.subset}: {len(traces)}")
    print(f"[info] arms: {arms}")
    print(f"[info] out_dir: {out_dir}")

    rows = []
    selected_meta = []

    for t in tqdm(traces, desc="ideal-context upper bound", unit="ex", dynamic_ncols=True):
        question = t["question"]
        ex = q_to_ex.get(question)
        support_evidence = support_evidence_from_example(ex)

        base = baseline_cached_row(t)
        selected_meta.append({
            "eval_index": t.get("eval_index"),
            "example_id": t.get("example_id"),
            "question": question,
            "gold_answer": t.get("gold_answer"),
            "baseline_score": base["score"],
            "baseline_support_recall_total": base["support_recall_total"],
            "baseline_missing_titles_after_hop2": base["missing_titles_after_hop2"],
        })

        for arm in arms:
            error = None
            delta_context = None

            try:
                if arm == "baseline_cached":
                    result = base

                elif arm == "baseline_recomputed":
                    result = run_downstream(
                        fixed_program,
                        t,
                        t.get("hop2_query", ""),
                        retriever_k=args.k,
                    )

                elif arm == "r6_global":
                    q = r6_program.create_query_hop2(
                        question=question,
                        summary_1=t.get("summary_1", ""),
                    ).query
                    q = clean_query(q)
                    result = run_downstream(fixed_program, t, q, retriever_k=args.k)

                elif arm == "support_aware_ideal_delta":
                    delta_prompt = make_support_aware_delta_prompt(t, support_evidence)
                    delta_context, error = lm_raw_call(lm, delta_prompt, retries=args.retries)
                    rewrite_prompt = make_query_rewrite_prompt(t, delta_context)
                    q_raw, err2 = lm_raw_call(lm, rewrite_prompt, retries=args.retries)
                    if err2:
                        error = (error or "") + "\n" + err2
                    q = clean_query(q_raw)
                    result = run_downstream(fixed_program, t, q, retriever_k=args.k)
                    result["delta_prompt"] = delta_prompt
                    result["rewrite_prompt"] = rewrite_prompt

                elif arm == "answer_aware_ideal_delta":
                    delta_prompt = make_answer_aware_delta_prompt(t, support_evidence)
                    delta_context, error = lm_raw_call(lm, delta_prompt, retries=args.retries)
                    rewrite_prompt = make_query_rewrite_prompt(t, delta_context)
                    q_raw, err2 = lm_raw_call(lm, rewrite_prompt, retries=args.retries)
                    if err2:
                        error = (error or "") + "\n" + err2
                    q = clean_query(q_raw)
                    result = run_downstream(fixed_program, t, q, retriever_k=args.k)
                    result["delta_prompt"] = delta_prompt
                    result["rewrite_prompt"] = rewrite_prompt

                elif arm == "support_title_ceiling":
                    q = support_title_ceiling_query(t)
                    result = run_downstream(fixed_program, t, q, retriever_k=args.k)

                else:
                    raise ValueError(f"unknown arm: {arm}")

            except Exception as e:
                error = str(e)
                result = {
                    "hop2_query": "",
                    "hop2_docs": [],
                    "summary_2": "",
                    "pred_answer": "",
                    "score": 0.0,
                    **retrieval_metrics(t, []),
                }

            row = {
                "arm": arm,
                "eval_index": t.get("eval_index"),
                "example_id": t.get("example_id"),
                "question": question,
                "gold_answer": t.get("gold_answer"),
                "baseline_hop2_query": t.get("hop2_query", ""),
                "delta_context": delta_context,
                "error": error,

                "baseline_score": base["score"],
                "baseline_support_recall_total": base["support_recall_total"],
                "baseline_support_recall_hop2_only": base["support_recall_hop2_only"],
                "baseline_missing_recovery_rate": base["missing_recovery_rate"],

                **result,
            }

            row["final_corrected_vs_baseline"] = float(
                base["score"] < 1.0 and row["score"] >= 1.0
            )
            row["retrieval_improved_vs_baseline"] = float(
                row["support_recall_total"] > base["support_recall_total"]
            )
            row["retrieval_improved_but_final_wrong"] = float(
                row["support_recall_total"] > base["support_recall_total"]
                and row["score"] < 1.0
            )
            rows.append(row)

    write_jsonl(out_dir / "rows.jsonl", rows)
    write_jsonl(out_dir / "selected_examples.jsonl", selected_meta)
    write_summary(out_dir / "summary.md", rows, selected_count=len(traces))

    config = vars(args)
    config["arms"] = arms
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False))

    print()
    print("[wrote]", out_dir / "rows.jsonl")
    print("[wrote]", out_dir / "selected_examples.jsonl")
    print("[wrote]", out_dir / "summary.md")
    print()
    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
