#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from collections import defaultdict


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def short(x, n=1600):
    x = str(x or "").strip()
    return x if len(x) <= n else x[:n] + "\n...[truncated]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-path", required=True)
    ap.add_argument("--judgments-path", required=True)
    ap.add_argument("--out-path", required=True)
    ap.add_argument("--max-per-bucket", type=int, default=20)
    args = ap.parse_args()

    tasks = {r["task_id"]: r for r in read_jsonl(args.tasks_path)}
    js = read_jsonl(args.judgments_path)

    buckets = defaultdict(list)
    for r in js:
        if r.get("correct") == 1.0:
            buckets["pass"].append(r)
        elif r.get("predicted") in {"tie", "invalid"}:
            buckets["tie_or_invalid_fail"].append(r)
        elif r.get("task_kind") == "left_recovery":
            buckets["left_fail"].append(r)
        else:
            buckets["right_fail"].append(r)

    lines = ["# Feedback distance case inspection", ""]

    for bucket in ["left_fail", "right_fail", "tie_or_invalid_fail", "pass"]:
        xs = buckets[bucket][:args.max_per_bucket]
        lines += [f"## {bucket} ({len(buckets[bucket])} total, showing {len(xs)})", ""]

        for j in xs:
            t = tasks[j["task_id"]]
            obj = j.get("judge_obj") or {}
            lines += [
                f"### {j['task_id']}",
                f"- idx: {j.get('idx')}",
                f"- split_iter: {j.get('split_iter')}",
                f"- task_kind: {j.get('task_kind')}",
                f"- expected: {j.get('expected')}",
                f"- predicted: {j.get('predicted')}",
                f"- correct: {j.get('correct')}",
                f"- dominant_gap_type: {obj.get('dominant_gap_type')}",
                f"- confidence: {obj.get('confidence')}",
                f"- why_larger: {short(obj.get('why_larger') or j.get('raw'), 1000)}",
                "",
                "#### Question",
                short(t.get("question"), 700),
                "",
                "#### Full-edge feedback",
                f"- edge: {t['full_segment'].get('edge')}",
                "",
                short(t["full_segment"].get("feedback_text"), 2200),
                "",
                "#### Sub-edge feedback",
                f"- edge: {t['sub_segment'].get('edge')}",
                "",
                short(t["sub_segment"].get("feedback_text"), 2200),
                "",
                "---",
                "",
            ]

    Path(args.out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_path).write_text("\n".join(lines))
    print("[wrote]", args.out_path)


if __name__ == "__main__":
    main()
