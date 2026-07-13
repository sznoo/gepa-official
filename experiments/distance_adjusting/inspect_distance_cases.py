#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from collections import defaultdict


def read_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def fmt_state(s):
    if not isinstance(s, dict):
        return str(s)

    fields = [
        ("name", s.get("name")),
        ("kind", s.get("kind")),
        ("query", s.get("query")),
        ("retrieved_titles", s.get("retrieved_titles")),
        ("retrieval_focus", s.get("retrieval_focus")),
        ("anchors", s.get("anchors")),
        ("bridge_clues", s.get("bridge_clues")),
        ("noisy_or_distracting_clues", s.get("noisy_or_distracting_clues")),
        ("expected_evidence_type", s.get("expected_evidence_type")),
        ("query_shape_implication", s.get("query_shape_implication")),
    ]

    out = []
    for k, v in fields:
        if v in [None, "", [], {}]:
            continue
        if isinstance(v, list):
            v = ", ".join(map(str, v))
        out.append(f"- {k}: {v}")
    return "\n".join(out)


def short(x, n=1000):
    x = str(x or "").strip()
    return x if len(x) <= n else x[:n] + "\n...[truncated]"


def classify_case(j):
    correct = bool(j.get("correct"))
    pred = j.get("predicted")
    task_kind = j.get("task_kind")

    if correct:
        return "pass"
    if pred in {"tie", "invalid"}:
        return "tie_or_invalid_fail"
    if task_kind == "left_recovery":
        return "left_fail"
    if task_kind == "right_recovery":
        return "right_fail"
    return "fail"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-path", required=True)
    ap.add_argument("--judgments-path", required=True)
    ap.add_argument("--out-path", required=True)
    ap.add_argument("--max-per-bucket", type=int, default=8)
    ap.add_argument("--only-split-iter", default=None)
    args = ap.parse_args()

    tasks = {r["task_id"]: r for r in read_jsonl(args.tasks_path)}
    judgments = read_jsonl(args.judgments_path)

    if args.only_split_iter is not None:
        judgments = [
            r for r in judgments
            if str(r.get("split_iter")) == str(args.only_split_iter)
        ]

    buckets = defaultdict(list)
    for j in judgments:
        buckets[classify_case(j)].append(j)

    lines = []
    lines.append("# Distance case inspection")
    lines.append("")
    lines.append(f"- tasks_path: `{args.tasks_path}`")
    lines.append(f"- judgments_path: `{args.judgments_path}`")
    if args.only_split_iter is not None:
        lines.append(f"- only_split_iter: `{args.only_split_iter}`")
    lines.append("")

    for bucket in ["left_fail", "right_fail", "tie_or_invalid_fail", "pass"]:
        xs = buckets.get(bucket, [])[:args.max_per_bucket]
        lines.append(f"## {bucket} ({len(buckets.get(bucket, []))} total, showing {len(xs)})")
        lines.append("")

        for j in xs:
            t = tasks.get(j["task_id"])
            if not t:
                continue

            obj = j.get("judge_obj") or {}

            lines.append(f"### {j['task_id']}")
            lines.append("")
            lines.append(f"- idx: {j.get('idx')}")
            lines.append(f"- split_iter: {j.get('split_iter')}")
            lines.append(f"- task_kind: {j.get('task_kind')}")
            lines.append(f"- expected: {j.get('expected')}")
            lines.append(f"- predicted: {j.get('predicted')}")
            lines.append(f"- correct: {j.get('correct')}")
            lines.append(f"- dominant_gap_type: {obj.get('dominant_gap_type')}")
            lines.append(f"- confidence: {obj.get('confidence')}")
            lines.append(f"- why_larger: {short(obj.get('why_larger') or j.get('raw'), 900)}")
            lines.append("")
            lines.append("**Question**")
            lines.append("")
            lines.append(short(t.get("question"), 800))
            lines.append("")
            lines.append("**Full segment: R_i -> R_next**")
            lines.append("")
            lines.append("from_state:")
            lines.append(fmt_state(t["full_segment"]["from_state"]))
            lines.append("")
            lines.append("to_state:")
            lines.append(fmt_state(t["full_segment"]["to_state"]))
            lines.append("")
            lines.append("**Sub segment**")
            lines.append("")
            lines.append("from_state:")
            lines.append(fmt_state(t["sub_segment"]["from_state"]))
            lines.append("")
            lines.append("to_state:")
            lines.append(fmt_state(t["sub_segment"]["to_state"]))
            lines.append("")
            lines.append("---")
            lines.append("")

    Path(args.out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_path).write_text("\n".join(lines))
    print("[wrote]", args.out_path)


if __name__ == "__main__":
    main()
