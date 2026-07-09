#!/usr/bin/env python3
# /home/jinwoo/gepa-official/experiments/deltaq/run_rtrace_midpoint_distance_judge.py
import argparse
import json
import os
import random
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

import dspy

try:
    from dotenv import load_dotenv
    load_dotenv("/home/jinwoo/gepa-official/.env")
except Exception:
    pass

try:
    from tqdm.auto import tqdm
except Exception:
    def tqdm(x, **kwargs):
        return x


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Reuse R-state formatting / LLM parsing helpers from the original R-trace script.
from run_biggest_step_rtrace_decomposition import (
    compact_state_for_prompt,
    compact_json,
    call_lm,
    jsonish_extract,
)


def read_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def state_name(s):
    if isinstance(s, dict):
        return str(s.get("name") or s.get("state_id") or s.get("kind") or "UNKNOWN")
    return "UNKNOWN"


def make_two_segment_distance_prompt(question, summary_1, segment_a, segment_b):
    """
    Same distance criterion as prompt_select_longest_edge in run_biggest_step_rtrace_decomposition.py,
    but with exactly two explicit segments.

    We use this instead of make_compare_prompt from run_qtrace_order_judge_probe.py because
    make_compare_prompt compares states by closeness to success equivalence class, not endpoint-anchored
    transition distance.
    """
    segments = [
        {
            "segment_index": 0,
            "segment_label": "A",
            "from_state": compact_state_for_prompt(segment_a["from"]),
            "to_state": compact_state_for_prompt(segment_a["to"]),
        },
        {
            "segment_index": 1,
            "segment_label": "B",
            "from_state": compact_state_for_prompt(segment_b["from"]),
            "to_state": compact_state_for_prompt(segment_b["to"]),
        },
    ]

    return f"""
You are judging retrieval-context update magnitude for HotpotQA BM25.

Given two R-state transitions, select the single segment with the larger update magnitude.

This uses the same criterion as the biggest-step R-trace decomposition judge:
- Prefer the segment where retrieval focus changes most.
- Prefer the segment requiring the largest entity-anchor, bridge-relation, type/alias/date, or noisy-entity correction.
- Prefer the segment with the largest answerability/evidence-family change.
- Do NOT prefer a segment merely because it is more verbose.
- If two segments are similar and no local order is justified, return "tie".

Return JSON only:
{{
  "larger_segment": "A" | "B" | "tie",
  "segment_index": 0 | 1 | -1,
  "why_larger": "...",
  "dominant_gap_type": "anchor|bridge_relation|surface_form|noisy_entity|answer_type|query_shape|mixed|tie",
  "confidence": 0.0
}}

Question:
{question}

summary_1:
{summary_1}

Candidate segments:
{compact_json(segments)}
""".strip()


def parse_larger_segment(out):
    js = jsonish_extract(out)
    if isinstance(js, dict):
        val = str(js.get("larger_segment", "")).strip().upper()
        if val in {"A", "B", "TIE"}:
            return "tie" if val == "TIE" else val, js

        idx = js.get("segment_index", None)
        try:
            idx = int(idx)
            if idx == 0:
                return "A", js
            if idx == 1:
                return "B", js
            if idx < 0:
                return "tie", js
        except Exception:
            pass

    text = str(out).strip().upper()
    if re.search(r'\bTIE\b|\bEQUAL\b|\bSIMILAR\b', text):
        return "tie", js or {"raw": out}
    if re.search(r'\bA\b', text):
        return "A", js or {"raw": out}
    if re.search(r'\bB\b', text):
        return "B", js or {"raw": out}
    return "invalid", js or {"raw": out}


def extract_midpoint_triples(aux_rows):
    """
    Extract actual generated midpoint triples from rtrace_aux.jsonl.

    For each split iteration:
      original edge = states[seg_idx] -> states[seg_idx + 1]
      generated midpoint = inserted_mid_state

    This is the real R_mid produced by prompt_split_edge.
    """
    triples = []

    for row in aux_rows:
        idx = str(row["idx"])
        question = row.get("question", "")
        summary_1 = row.get("summary_1", "")

        for it in row.get("iterations", []):
            if "selected_segment_for_next_split" not in it:
                continue
            if "inserted_mid_state" not in it:
                continue

            states = it.get("states") or []
            seg_idx = safe_int(it.get("selected_segment_for_next_split"), 0)

            if seg_idx < 0 or seg_idx + 1 >= len(states):
                continue

            left = states[seg_idx]
            right = states[seg_idx + 1]
            mid = it["inserted_mid_state"]

            triples.append({
                "idx": idx,
                "question": question,
                "summary_1": summary_1,
                "split_iter": it.get("split_iter"),
                "num_edges_before_split": it.get("num_edges"),
                "selected_segment_for_next_split": seg_idx,
                "R_i": left,
                "R_mid": mid,
                "R_next": right,
                "R_i_name": state_name(left),
                "R_mid_name": state_name(mid),
                "R_next_name": state_name(right),
                "max_info": it.get("max_info", {}),
            })

    return triples


def build_tasks(triples, shuffle_pair_order, rng):
    tasks = []

    for t in triples:
        R_i = t["R_i"]
        R_mid = t["R_mid"]
        R_next = t["R_next"]

        # Left inequality:
        # d_T(R_i, R_mid) < d_T(R_i, R_next)
        # So original segment R_i -> R_next must be larger than subsegment R_i -> R_mid.
        sub_left = {"from": R_i, "to": R_mid}
        orig = {"from": R_i, "to": R_next}

        seg_a, seg_b = sub_left, orig
        expected = "B"
        if shuffle_pair_order and rng.random() < 0.5:
            seg_a, seg_b = seg_b, seg_a
            expected = "A"

        tasks.append({
            "idx": t["idx"],
            "question": t["question"],
            "summary_1": t["summary_1"],
            "split_iter": t["split_iter"],
            "num_edges_before_split": t["num_edges_before_split"],
            "selected_segment_for_next_split": t["selected_segment_for_next_split"],
            "task_kind": "left_pass",
            "definition": "d_T(R_i, R_mid) < d_T(R_i, R_next)",
            "R_i_name": t["R_i_name"],
            "R_mid_name": t["R_mid_name"],
            "R_next_name": t["R_next_name"],
            "segment_A": seg_a,
            "segment_B": seg_b,
            "expected": expected,
        })

        # Right inequality:
        # d_T(R_mid, R_next) < d_T(R_i, R_next)
        # So original segment R_i -> R_next must be larger than subsegment R_mid -> R_next.
        sub_right = {"from": R_mid, "to": R_next}
        orig = {"from": R_i, "to": R_next}

        seg_a, seg_b = sub_right, orig
        expected = "B"
        if shuffle_pair_order and rng.random() < 0.5:
            seg_a, seg_b = seg_b, seg_a
            expected = "A"

        tasks.append({
            "idx": t["idx"],
            "question": t["question"],
            "summary_1": t["summary_1"],
            "split_iter": t["split_iter"],
            "num_edges_before_split": t["num_edges_before_split"],
            "selected_segment_for_next_split": t["selected_segment_for_next_split"],
            "task_kind": "right_pass",
            "definition": "d_T(R_mid, R_next) < d_T(R_i, R_next)",
            "R_i_name": t["R_i_name"],
            "R_mid_name": t["R_mid_name"],
            "R_next_name": t["R_next_name"],
            "segment_A": seg_a,
            "segment_B": seg_b,
            "expected": expected,
        })

    return tasks


def run_task(args, task):
    prompt = make_two_segment_distance_prompt(
        question=task["question"],
        summary_1=task["summary_1"],
        segment_a=task["segment_A"],
        segment_b=task["segment_B"],
    )

    raw = call_lm(prompt, args.retries)
    pred, obj = parse_larger_segment(raw)
    correct = pred == task["expected"]

    out = {
        "idx": task["idx"],
        "split_iter": task["split_iter"],
        "num_edges_before_split": task["num_edges_before_split"],
        "selected_segment_for_next_split": task["selected_segment_for_next_split"],
        "task_kind": task["task_kind"],
        "definition": task["definition"],
        "R_i_name": task["R_i_name"],
        "R_mid_name": task["R_mid_name"],
        "R_next_name": task["R_next_name"],
        "expected": task["expected"],
        "predicted": pred,
        "correct": float(correct),
        "judge_obj": obj,
        "raw": raw,
        "prompt": prompt if args.save_prompts else None,
    }
    return out


def summarize(results):
    left = [r for r in results if r["task_kind"] == "left_pass"]
    right = [r for r in results if r["task_kind"] == "right_pass"]

    by_triple = defaultdict(dict)
    for r in results:
        key = (r["idx"], r["split_iter"], r["selected_segment_for_next_split"])
        by_triple[key][r["task_kind"]] = bool(r["correct"])

    both = []
    for d in by_triple.values():
        if "left_pass" in d and "right_pass" in d:
            both.append(d["left_pass"] and d["right_pass"])

    def rate(xs):
        return sum(xs) / len(xs) if xs else 0.0

    return {
        "n_tasks": len(results),
        "n_midpoint_triples": len(by_triple),
        "left_pass_rate": rate([r["correct"] for r in left]),
        "right_pass_rate": rate([r["correct"] for r in right]),
        "both_pass_rate": rate([float(x) for x in both]),
        "mean_shrink_score": rate([r["correct"] for r in results]),
        "tie_or_invalid_rate": rate([float(r["predicted"] in {"tie", "invalid"}) for r in results]),
    }


def write_summary_md(path, args, summary):
    lines = []
    lines.append("# R-trace midpoint distance utility judge")
    lines.append("")
    lines.append(f"- rtrace_aux_path: `{args.rtrace_aux_path}`")
    lines.append("- judge criterion: same update-magnitude criterion as biggest-step R-trace decomposition")
    lines.append("- evaluated condition:")
    lines.append("")
    lines.append("```latex")
    lines.append("\\begin{aligned}")
    lines.append("d_T(R_i, R_{\\mathrm{mid}}) &< d_T(R_i, R_{i+1}) \\\\")
    lines.append("d_T(R_{\\mathrm{mid}}, R_{i+1}) &< d_T(R_i, R_{i+1})")
    lines.append("\\end{aligned}")
    lines.append("```")
    lines.append("")
    for k, v in summary.items():
        if isinstance(v, float):
            lines.append(f"- {k}: {v:.4f}")
        else:
            lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Definitions")
    lines.append("")
    lines.append("- left_pass: original edge \\(R_i \\to R_{i+1}\\) is judged larger than \\(R_i \\to R_{mid}\\).")
    lines.append("- right_pass: original edge \\(R_i \\to R_{i+1}\\) is judged larger than \\(R_{mid} \\to R_{i+1}\\).")
    lines.append("- both_pass: both midpoint inequalities hold for the same generated midpoint.")
    Path(path).write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--rtrace-aux-path",
        default="experiments/deltaq/results_biggest_step_rtrace_full19_Ronly/rtrace_aux.jsonl",
    )
    ap.add_argument(
        "--out-dir",
        default="experiments/deltaq/results_rtrace_midpoint_distance_judge_full19",
    )
    ap.add_argument("--model", default=os.environ.get("TASK_MODEL", "openai/gpt-5-mini"))
    ap.add_argument("--api-base", default=os.environ.get("TASK_API_BASE", ""))
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--num-threads", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--shuffle-pair-order", action="store_true")
    ap.add_argument("--save-prompts", action="store_true")
    ap.add_argument("--inspect-only", action="store_true")
    args = ap.parse_args()

    if "gpt-5" in args.model:
        args.temperature = 1.0
        if args.max_tokens < 16000:
            args.max_tokens = 16000

    lm_kwargs = {
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_base:
        lm_kwargs["api_base"] = args.api_base
    if args.api_key:
        lm_kwargs["api_key"] = args.api_key

    dspy.settings.configure(lm=dspy.LM(**lm_kwargs))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    aux_rows = read_jsonl(args.rtrace_aux_path)
    triples = extract_midpoint_triples(aux_rows)

    rng = random.Random(args.seed)
    tasks = build_tasks(triples, args.shuffle_pair_order, rng)

    if args.limit:
        tasks = tasks[:args.limit]

    # Write light previews without huge prompts/states.
    preview_triples = []
    for t in triples[:10]:
        preview_triples.append({
            "idx": t["idx"],
            "split_iter": t["split_iter"],
            "num_edges_before_split": t["num_edges_before_split"],
            "selected_segment_for_next_split": t["selected_segment_for_next_split"],
            "R_i_name": t["R_i_name"],
            "R_mid_name": t["R_mid_name"],
            "R_next_name": t["R_next_name"],
            "R_i_titles": t["R_i"].get("retrieved_titles", []) if isinstance(t["R_i"], dict) else [],
            "R_mid_focus": t["R_mid"].get("retrieval_focus", "") if isinstance(t["R_mid"], dict) else "",
            "R_next_titles": t["R_next"].get("retrieved_titles", []) if isinstance(t["R_next"], dict) else [],
        })

    (out_dir / "midpoint_triples_preview.json").write_text(
        json.dumps(preview_triples, ensure_ascii=False, indent=2)
    )

    task_preview = []
    for t in tasks[:10]:
        task_preview.append({
            "idx": t["idx"],
            "split_iter": t["split_iter"],
            "task_kind": t["task_kind"],
            "definition": t["definition"],
            "expected": t["expected"],
            "R_i_name": t["R_i_name"],
            "R_mid_name": t["R_mid_name"],
            "R_next_name": t["R_next_name"],
        })
    (out_dir / "tasks_preview.json").write_text(json.dumps(task_preview, ensure_ascii=False, indent=2))

    print("[rtrace_aux_path]", args.rtrace_aux_path)
    print("[aux rows]", len(aux_rows))
    print("[midpoint triples]", len(triples))
    print("[tasks]", len(tasks))
    print("[out dir]", out_dir)
    print("[preview]", out_dir / "midpoint_triples_preview.json")
    print("[task preview]", out_dir / "tasks_preview.json")

    if args.inspect_only:
        return

    results = []

    if args.num_threads <= 1:
        for t in tqdm(tasks, desc="judging midpoint distance", unit="task", dynamic_ncols=True):
            results.append(run_task(args, t))
    else:
        with ThreadPoolExecutor(max_workers=args.num_threads) as pool:
            futs = [pool.submit(run_task, args, t) for t in tasks]
            for fut in tqdm(as_completed(futs), total=len(futs), desc="judging midpoint distance", unit="task", dynamic_ncols=True):
                results.append(fut.result())

    results.sort(key=lambda r: (
        str(r["idx"]),
        int(r["split_iter"]) if r["split_iter"] is not None else -1,
        str(r["task_kind"]),
    ))

    write_jsonl(out_dir / "judgments.jsonl", results)

    summary = summarize(results)
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    write_summary_md(out_dir / "summary.md", args, summary)

    print()
    print("[wrote]", out_dir / "summary.md")
    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
