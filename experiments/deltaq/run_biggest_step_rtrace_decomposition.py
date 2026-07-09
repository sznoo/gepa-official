# /home/jinwoo/gepa-official/experiments/deltaq/run_biggest_step_rtrace_decomposition.py
import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import dspy
from tqdm import tqdm


def read_jsonl(p):
    rows = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(p, rows):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def as_set(xs):
    return {str(x).strip() for x in (xs or []) if str(x).strip()}


def arm_order(arm):
    if arm == "base_query":
        return 0
    if arm == "target_query":
        return 10_000
    m = re.search(r"trace_step_(\d+)", arm or "")
    if m:
        return int(m.group(1))
    return None


def group_qtrace(rows):
    by = defaultdict(list)
    for r in rows:
        by[str(r["idx"])].append(r)

    groups = {}
    for idx, xs in by.items():
        base = next((r for r in xs if r.get("arm") == "base_query"), None)
        target = next((r for r in xs if r.get("arm") == "target_query"), None)
        if base and target:
            groups[idx] = {"idx": idx, "base": base, "target": target}
    return groups


def collect_strings(obj, path=""):
    out = []
    if isinstance(obj, str):
        out.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(collect_strings(v, path + "." + str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(collect_strings(v, path + f"[{i}]"))
    return out


def find_key_subtree(obj, keyword):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if keyword in str(k):
                return v
        for v in obj.values():
            found = find_key_subtree(v, keyword)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = find_key_subtree(v, keyword)
            if found is not None:
                return found
    return None


def load_create_query_instruction(path):
    data = json.loads(Path(path).read_text())
    subtree = find_key_subtree(data, "create_query_hop2") or find_key_subtree(data, "hop2") or data

    strings = collect_strings(subtree)
    candidates = []
    for p, s in strings:
        ss = s.strip()
        if len(ss) < 40:
            continue
        low = ss.lower()
        score = 0
        for kw in ["query", "search", "question", "summary", "hop"]:
            if kw in low:
                score += 1
        candidates.append((score, len(ss), p, ss))

    if candidates:
        candidates.sort(reverse=True)
        score, length, p, instr = candidates[0]
        print(f"[create_query_hop2 instruction] extracted from {p}, chars={length}, score={score}")
        return instr

    print("[warn] create_query_hop2 instruction not found; using fallback")
    return "Generate a compact second-hop BM25 search query from the question and first-hop summary."


def clean_lm_text(x):
    if x is None:
        return ""
    if isinstance(x, str):
        y = x.strip()
    elif isinstance(x, (list, tuple)):
        vals = [clean_lm_text(v) for v in x]
        y = next((v for v in vals if v), "")
    elif isinstance(x, dict):
        if "choices" in x and x["choices"]:
            vals = []
            for c in x["choices"]:
                if isinstance(c, dict):
                    msg = c.get("message") or {}
                    vals.append(msg.get("content") or c.get("text") or "")
            y = next((str(v).strip() for v in vals if str(v).strip()), "")
        else:
            vals = [clean_lm_text(v) for v in x.values()]
            y = next((v for v in vals if v), "")
    else:
        y = str(x).strip()

    y = re.sub(r"^```(?:text|json)?", "", y).strip()
    y = re.sub(r"```$", "", y).strip()
    return y.strip().strip('"').strip("'").strip()


def call_lm(prompt, retries=3):
    last = None
    sigs = [
        ("prompt -> response", "response"),
        ("prompt -> text", "text"),
        ("prompt -> answer", "answer"),
        ("prompt -> query", "query"),
        ("prompt -> output", "output"),
    ]
    for _ in range(retries):
        for sig, attr in sigs:
            try:
                pred = dspy.Predict(sig)(prompt=prompt)
                out = clean_lm_text(getattr(pred, attr, None))
                if out:
                    return out
            except Exception as e:
                last = e
        try:
            out = clean_lm_text(dspy.settings.lm(prompt))
            if out:
                return out
        except Exception as e:
            last = e

    if last:
        print("[warn] LLM failed:", repr(last), file=sys.stderr)
    return "EMPTY_LLM_OUTPUT"


def jsonish_extract(text):
    text = clean_lm_text(text)
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def log_progress(args, msg):
    if getattr(args, "log_progress", False):
        print(msg, flush=True)


def load_retriever(args):
    sys.path.insert(0, str(Path.cwd()))
    from examples.hotpotqa.retriever import search, set_retriever_dir

    retriever_dir = args.retriever_dir or os.environ.get("HOTPOT_RETRIEVER_DIR", "")
    if retriever_dir:
        set_retriever_dir(retriever_dir)

    k = int(args.retriever_k)
    print(f"[retriever] search(query, k={k})")
    if retriever_dir:
        print(f"[retriever] dir: {retriever_dir}")

    def _ret(q):
        return search(q, k)

    return _ret


def normalize_titles(out):
    if out is None:
        return []
    if hasattr(out, "passages"):
        return normalize_titles(getattr(out, "passages"))
    if hasattr(out, "docs"):
        return normalize_titles(getattr(out, "docs"))
    if hasattr(out, "titles"):
        return normalize_titles(getattr(out, "titles"))
    if isinstance(out, dict):
        for k in ["titles", "retrieved_titles", "passages", "docs", "ctxs", "contexts"]:
            if k in out:
                return normalize_titles(out[k])
        return []
    if isinstance(out, str):
        return [out.split(" | ", 1)[0].strip()]
    if isinstance(out, (list, tuple)):
        titles = []
        for x in out:
            if isinstance(x, str):
                titles.append(x.split(" | ", 1)[0].strip())
            elif isinstance(x, dict):
                t = x.get("title") or x.get("wikipedia_title") or x.get("page_title")
                if t:
                    titles.append(str(t).strip())
            elif hasattr(x, "title"):
                titles.append(str(getattr(x, "title")).strip())
            else:
                sx = str(x).strip()
                if sx:
                    titles.append(sx.split(" | ", 1)[0].strip())

        out_titles = []
        seen = set()
        for t in titles:
            if t and t not in seen:
                seen.add(t)
                out_titles.append(t)
        return out_titles
    return []


def score_titles(titles, gold_support_titles, missing_titles):
    got = as_set(titles)
    gold = as_set(gold_support_titles)
    missing = as_set(missing_titles)

    support_hit = got & gold
    missing_hit = got & missing

    return {
        "retrieved_titles": list(titles),
        "support_hit_count": len(support_hit),
        "support_recall_hop2": len(support_hit) / max(1, len(gold)),
        "recovered_missing_titles": sorted(missing_hit),
        "missing_recovered_count": len(missing_hit),
        "missing_recovery_rate": len(missing_hit) / max(1, len(missing)),
    }


def make_endpoint_state(name, qrow, expose_query=False):
    titles = list(qrow.get("retrieved_titles") or [])
    recovered = list(qrow.get("recovered_missing_titles") or [])
    state = {
        "name": name,
        "kind": "endpoint",
        "query_visible": expose_query,
        "query": qrow.get("query") if expose_query else "",
        "retrieved_titles": titles[:10],
        "retrieval_focus": "",
        "anchors": [],
        "bridge_clues": [],
        "noisy_or_distracting_clues": [],
        "expected_evidence_type": "",
        "query_shape_implication": "",
        "diagnostic_hidden": {
            "mr": float(qrow.get("missing_recovery_rate") or 0),
            "hop2_recall": float(qrow.get("support_recall_hop2") or 0),
            "recovered_missing_titles": recovered,
        },
    }
    return state


def compact_state_for_prompt(s):
    # Do not expose hidden diagnostics to the LLM judge/generator.
    return {
        "name": s.get("name"),
        "kind": s.get("kind"),
        "query": s.get("query") if s.get("query_visible") else "",
        "retrieved_titles": s.get("retrieved_titles") or [],
        "retrieval_focus": s.get("retrieval_focus") or "",
        "anchors": s.get("anchors") or [],
        "bridge_clues": s.get("bridge_clues") or [],
        "noisy_or_distracting_clues": s.get("noisy_or_distracting_clues") or [],
        "expected_evidence_type": s.get("expected_evidence_type") or "",
        "query_shape_implication": s.get("query_shape_implication") or "",
    }


def compact_json(x):
    return json.dumps(x, ensure_ascii=False, indent=2)


def prompt_describe_endpoint(question, summary_1, state):
    return f"""
Describe this retrieval state as a compact R-state for second-hop HotpotQA retrieval.

Do not use gold support labels or evaluation metrics. Use only the visible state: query if visible, retrieved titles, question, and summary_1.

Output JSON with exactly:
{{
  "retrieval_focus": "...",
  "anchors": ["..."],
  "bridge_clues": ["..."],
  "noisy_or_distracting_clues": ["..."],
  "expected_evidence_type": "...",
  "query_shape_implication": "..."
}}

Question:
{question}

summary_1:
{summary_1}

Visible retrieval state:
{compact_json(compact_state_for_prompt(state))}
""".strip()


def fill_endpoint_description(args, question, summary_1, state):
    out = call_lm(prompt_describe_endpoint(question, summary_1, state), args.retries)
    js = jsonish_extract(out)
    s = dict(state)
    if isinstance(js, dict):
        for k in ["retrieval_focus", "anchors", "bridge_clues", "noisy_or_distracting_clues", "expected_evidence_type", "query_shape_implication"]:
            if k in js:
                s[k] = js[k]
    else:
        s["retrieval_focus"] = out
    return s


def prompt_select_longest_edge(question, summary_1, states):
    segments = []
    for i in range(len(states) - 1):
        segments.append({
            "segment_index": i,
            "from_state": compact_state_for_prompt(states[i]),
            "to_state": compact_state_for_prompt(states[i + 1]),
        })

    return f"""
You are judging retrieval-context update magnitude for HotpotQA BM25.

Given an ordered R-trace, select the single adjacent segment with the largest update magnitude.

This is adapted from a pairwise gradient comparison judge:
- Prefer the segment where retrieval focus changes most.
- Prefer the segment requiring the largest entity-anchor, bridge-relation, type/alias/date, or noisy-entity correction.
- Prefer the segment with the largest answerability/evidence-family change.
- Do NOT prefer a segment merely because it is more verbose.
- If two segments are similar, choose the earlier unresolved coarse segment.

Return JSON only:
{{
  "segment_index": <integer>,
  "why_largest": "...",
  "dominant_gap_type": "anchor|bridge_relation|surface_form|noisy_entity|answer_type|query_shape|mixed"
}}

Question:
{question}

summary_1:
{summary_1}

Ordered states and adjacent segments:
{compact_json(segments)}
""".strip()


def select_longest_edge(args, question, summary_1, states):
    if len(states) <= 2:
        return 0, {"why_largest": "only segment", "dominant_gap_type": "mixed"}

    out = call_lm(prompt_select_longest_edge(question, summary_1, states), args.retries)
    js = jsonish_extract(out)
    if isinstance(js, dict):
        idx = js.get("segment_index", 0)
        try:
            idx = int(idx)
        except Exception:
            idx = 0
        idx = max(0, min(idx, len(states) - 2))
        return idx, js

    m = re.search(r"\bsegment[_ ]?index\b\D+(\d+)", out, flags=re.I)
    if m:
        idx = int(m.group(1))
        idx = max(0, min(idx, len(states) - 2))
        return idx, {"raw": out}

    return 0, {"raw": out, "fallback": True}


def prompt_split_edge(question, summary_1, left, right):
    return f"""
Generate ONE intermediate retrieval state R_mid that splits the largest retrieval-context update.

The goal is greedy biggest-step decomposition:
R_left -> R_right is currently too coarse.
Produce R_mid so that:
- R_left -> R_mid is a smaller local update.
- R_mid -> R_right is a smaller local update.
- R_mid is not equivalent to either endpoint.
- R_mid should preserve ordered progress toward R_right.
- Do not output a final query.
- Do not copy R_right completely.
- Do not use gold support labels or evaluation metrics.

Output JSON only:
{{
  "name": "R_mid",
  "kind": "generated_midpoint",
  "retrieval_focus": "...",
  "anchors": ["..."],
  "bridge_clues": ["..."],
  "noisy_or_distracting_clues": ["..."],
  "expected_evidence_type": "...",
  "query_shape_implication": "...",
  "split_rationale": "..."
}}

Question:
{question}

summary_1:
{summary_1}

R_left:
{compact_json(compact_state_for_prompt(left))}

R_right:
{compact_json(compact_state_for_prompt(right))}
""".strip()


def split_edge(args, question, summary_1, left, right, new_name):
    out = call_lm(prompt_split_edge(question, summary_1, left, right), args.retries)
    js = jsonish_extract(out)
    if not isinstance(js, dict):
        js = {
            "name": new_name,
            "kind": "generated_midpoint",
            "retrieval_focus": out,
            "anchors": [],
            "bridge_clues": [],
            "noisy_or_distracting_clues": [],
            "expected_evidence_type": "",
            "query_shape_implication": "",
            "split_rationale": "fallback_raw_text",
        }
    js["name"] = new_name
    js["kind"] = "generated_midpoint"
    js["query_visible"] = False
    js["query"] = ""
    js["retrieved_titles"] = js.get("retrieved_titles") or []
    return js


def prompt_transition_to_pgrad(question, summary_1, left, right, step_idx):
    return f"""
Convert one adjacent R-state transition into a local prompt-gradient descriptor for create_query_hop2.

This is not a query. It is a local prompt update that would move retrieval behavior from R_left toward R_right.

Output exactly these fields:
TRIGGER:
KEEP:
ADD_OR_RESTORE:
REMOVE_OR_AVOID:
QUERY_SHAPE:
WHY_THIS_MOVES_RETRIEVAL:

Rules:
- Preserve local step order.
- Express behavior, not a final query.
- Use BM25-relevant anchors, bridge clues, aliases, dates, type cues, and noise removal.
- Do not mention gold labels or evaluation metrics.
- Do not say "retrieve the missing support".
- Avoid generic advice.

Step index: {step_idx}

Question:
{question}

summary_1:
{summary_1}

R_left:
{compact_json(compact_state_for_prompt(left))}

R_right:
{compact_json(compact_state_for_prompt(right))}
""".strip()


def rtrace_to_pgrad_list(args, question, summary_1, states):
    pgrads = []
    for i in range(len(states) - 1):
        pg = call_lm(prompt_transition_to_pgrad(question, summary_1, states[i], states[i + 1], i), args.retries)
        pgrads.append({
            "step": i,
            "from": states[i].get("name", f"R{i}"),
            "to": states[i + 1].get("name", f"R{i+1}"),
            "pgrad": pg,
        })
    return pgrads


def format_pgrad_list(pgrads):
    return "\n\n".join([
        f"STEP {x['step']} PROMPT_GRADIENT ({x['from']} -> {x['to']}):\n{x['pgrad']}"
        for x in pgrads
    ])


def build_query_prompt(base_instruction, question, summary_1, current_query, pgrad_list_text):
    inj = ""
    if pgrad_list_text:
        inj = f"""
Sample-specific ordered R-trace prompt-gradient program:
{pgrad_list_text}

Apply these local prompt-gradient edits in order when generating the hop2 query.
The list describes how retrieval context should move, not the final answer.
"""

    return f"""
You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.

Base create_query_hop2 instruction:
{base_instruction}

Inputs:
Question:
{question}

summary_1:
{summary_1}

Current baseline hop2 query:
{current_query}

{inj}

Output requirements:
- Output only one second-hop BM25 query.
- Keep it compact and keyword-like.
- Preserve useful anchors.
- Restore needed bridge/type/alias/date clues.
- Drop noisy side entities if they distract retrieval.
- Do not output explanations.
- Do not output the answer.
- Do not output placeholders such as missing_input, MISSING_CONTEXT, additional relevant documents, or search query.
""".strip()


def rollout(args, retrieve, base_instruction, idx, arm, question, summary_1, current_query, pgrad_text, gold_support_titles, missing_titles):
    prompt = build_query_prompt(base_instruction, question, summary_1, current_query, pgrad_text)
    query = call_lm(prompt, args.retries)
    titles = normalize_titles(retrieve(query))
    sc = score_titles(titles, gold_support_titles, missing_titles)
    return {
        "idx": idx,
        "arm": arm,
        "query": query,
        **sc,
        "meta": {
            "question": question,
            "summary_1": summary_1,
            "current_query": current_query,
            "num_steps": int(arm.split("_")[-1]) if arm.startswith("rtrace_steps_") else 0,
        },
    }


def process_one(args, row, qgroups, base_instruction, retrieve):
    idx = str(row["idx"])
    g = qgroups[idx]
    base = g["base"]
    target = g["target"]

    question = row.get("question", "")
    summary_1 = row.get("summary_1", "")
    current_query = base.get("query") or row.get("qtrace_base_query") or row.get("matched_query") or ""

    gold_support_titles = base.get("gold_support_titles") or row.get("gold_support_titles") or []
    missing_titles = base.get("base_missing") or row.get("base_missing") or []

    expose_qstar = args.endpoint_mode == "R_plus_qstar"

    log_progress(args, f"[RTRACE] idx={idx} start mode={args.endpoint_mode} max_splits={args.max_splits}")

    R0 = make_endpoint_state("R0_base", base, expose_query=True)
    Rstar = make_endpoint_state("Rstar_target", target, expose_query=expose_qstar)

    R0 = fill_endpoint_description(args, question, summary_1, R0)
    Rstar = fill_endpoint_description(args, question, summary_1, Rstar)

    states = [R0, Rstar]
    aux_iters = []
    rollouts = []

    # Baseline LLM rollout with no R-trace.
    base_roll = rollout(
        args, retrieve, base_instruction, idx,
        "prompt_current_query",
        question, summary_1, current_query, "",
        gold_support_titles, missing_titles,
    )
    rollouts.append(base_roll)
    log_progress(args, f"[RTRACE] idx={idx} current MR={float(base_roll.get('missing_recovery_rate') or 0):.3f}")

    # Existing endpoint diagnostics.
    rollouts.append({
        "idx": idx,
        "arm": "base_existing",
        "query": base.get("query"),
        "retrieved_titles": base.get("retrieved_titles") or [],
        "support_hit_count": base.get("support_hit_count"),
        "support_recall_hop2": float(base.get("support_recall_hop2") or 0),
        "recovered_missing_titles": base.get("recovered_missing_titles") or [],
        "missing_recovered_count": int(base.get("missing_recovered_count") or 0),
        "missing_recovery_rate": float(base.get("missing_recovery_rate") or 0),
        "meta": {"question": question, "summary_1": summary_1, "current_query": current_query, "num_steps": 0},
    })
    rollouts.append({
        "idx": idx,
        "arm": "target_existing",
        "query": target.get("query"),
        "retrieved_titles": target.get("retrieved_titles") or [],
        "support_hit_count": target.get("support_hit_count"),
        "support_recall_hop2": float(target.get("support_recall_hop2") or 0),
        "recovered_missing_titles": target.get("recovered_missing_titles") or [],
        "missing_recovered_count": int(target.get("missing_recovered_count") or 0),
        "missing_recovery_rate": float(target.get("missing_recovery_rate") or 0),
        "meta": {"question": question, "summary_1": summary_1, "current_query": current_query, "num_steps": -1},
    })

    # Evaluate initial 1-step R0 -> R*.
    for split_iter in range(0, args.max_splits + 1):
        num_edges = len(states) - 1
        pgrads = rtrace_to_pgrad_list(args, question, summary_1, states)
        pgrad_text = format_pgrad_list(pgrads)

        step_roll = rollout(
            args, retrieve, base_instruction, idx,
            f"rtrace_steps_{num_edges}",
            question, summary_1, current_query, pgrad_text,
            gold_support_titles, missing_titles,
        )
        rollouts.append(step_roll)
        log_progress(args, f"[RTRACE] idx={idx} eval steps={num_edges} MR={float(step_roll.get('missing_recovery_rate') or 0):.3f}")

        aux_iters.append({
            "split_iter": split_iter,
            "num_edges": num_edges,
            "states": states,
            "pgrads": pgrads,
        })

        if split_iter == args.max_splits:
            break

        seg_idx, max_info = select_longest_edge(args, question, summary_1, states)
        gap = max_info.get("dominant_gap_type") if isinstance(max_info, dict) else ""
        log_progress(args, f"[RTRACE] idx={idx} split_iter={split_iter+1} edges={len(states)-1} selected={seg_idx} gap={gap}")
        left = states[seg_idx]
        right = states[seg_idx + 1]
        mid_name = f"Rmid_iter{split_iter+1}_split{seg_idx}"
        mid = split_edge(args, question, summary_1, left, right, mid_name)

        states = states[:seg_idx + 1] + [mid] + states[seg_idx + 1:]

        aux_iters[-1]["selected_segment_for_next_split"] = seg_idx
        aux_iters[-1]["max_info"] = max_info
        aux_iters[-1]["inserted_mid_state"] = mid

    aux = {
        "idx": idx,
        "question": question,
        "summary_1": summary_1,
        "current_query": current_query,
        "endpoint_mode": args.endpoint_mode,
        "iterations": aux_iters,
    }
    best_mr = max(float(r.get("missing_recovery_rate") or 0) for r in rollouts if str(r.get("arm", "")).startswith("rtrace_steps_"))
    log_progress(args, f"[RTRACE] idx={idx} done best_MR={best_mr:.3f}")
    return rollouts, aux


def summarize_rows(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["arm"]].append(r)

    lines = []
    lines.append("# Biggest-Step R-Trace Decomposition\n")
    lines.append("| arm | n | mean MR | mean hop2 recall | mean recovered |")
    lines.append("|---|---:|---:|---:|---:|")
    for arm in sorted(by):
        xs = by[arm]
        n = len(xs)
        mr = sum(float(x.get("missing_recovery_rate") or 0) for x in xs) / max(1, n)
        h2 = sum(float(x.get("support_recall_hop2") or 0) for x in xs) / max(1, n)
        rec = sum(float(x.get("missing_recovered_count") or 0) for x in xs) / max(1, n)
        lines.append(f"| {arm} | {n} | {mr:.3f} | {h2:.3f} | {rec:.3f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qtrace-path", required=True)
    ap.add_argument("--meta-path", required=True)
    ap.add_argument("--base-prompt-candidate", required=True)
    ap.add_argument("--out-dir", required=True)

    ap.add_argument("--endpoint-mode", choices=["R_only", "R_plus_qstar"], default="R_only")
    ap.add_argument("--max-splits", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--require-summary1", action="store_true")
    ap.add_argument("--num-threads", type=int, default=4)
    ap.add_argument("--log-progress", action="store_true")

    ap.add_argument("--model", default="openai/gpt-5-mini")
    ap.add_argument("--api-base", default="")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--retries", type=int, default=3)

    ap.add_argument("--retriever-dir", default="")
    ap.add_argument("--retriever-k", type=int, default=7)
    args = ap.parse_args()

    if args.retriever_dir:
        os.environ["HOTPOT_RETRIEVER_DIR"] = args.retriever_dir

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lm_kwargs = {
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_base:
        lm_kwargs["api_base"] = args.api_base
    dspy.settings.configure(lm=dspy.LM(**lm_kwargs))

    base_instruction = load_create_query_instruction(args.base_prompt_candidate)
    (out_dir / "base_instruction.txt").write_text(base_instruction)

    qgroups = group_qtrace(read_jsonl(args.qtrace_path))
    meta_rows = read_jsonl(args.meta_path)

    rows = []
    for r in meta_rows:
        idx = str(r["idx"])
        if idx not in qgroups:
            continue
        if not r.get("question"):
            continue
        if args.require_summary1 and not r.get("summary_1"):
            continue
        rows.append(r)

    rows = sorted(rows, key=lambda r: int(r["idx"]) if str(r["idx"]).isdigit() else str(r["idx"]))
    if args.limit:
        rows = rows[:args.limit]

    print("[rows]", len(rows))
    print("[with summary_1]", sum(1 for r in rows if r.get("summary_1")))
    print("[endpoint_mode]", args.endpoint_mode)
    print("[max_splits]", args.max_splits, "=> max rtrace edges", args.max_splits + 1)

    retrieve = load_retriever(args)

    all_rollouts = []
    aux_rows = []

    with ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(process_one, args, r, qgroups, base_instruction, retrieve) for r in rows]
        for fut in tqdm(as_completed(futs), total=len(futs), desc="biggest-step rtrace"):
            rollouts, aux = fut.result()
            all_rollouts.extend(rollouts)
            aux_rows.append(aux)
            write_jsonl(out_dir / "rows.partial.jsonl", all_rollouts)
            write_jsonl(out_dir / "rtrace_aux.partial.jsonl", aux_rows)
            (out_dir / "summary.partial.md").write_text(summarize_rows(all_rollouts))

    write_jsonl(out_dir / "rows.jsonl", all_rollouts)
    write_jsonl(out_dir / "rtrace_aux.jsonl", aux_rows)
    (out_dir / "summary.md").write_text(summarize_rows(all_rollouts))

    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
