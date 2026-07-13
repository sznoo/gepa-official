#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_jsonl(p: Path):
    with p.open() as f:
        return [json.loads(l) for l in f if l.strip()]


def trunc(s, n=700):
    s = str(s or "")
    return s if len(s) <= n else s[:n] + " ...[truncated]"


def fmt_state(s):
    return f"""query:
{trunc(s.get("query"), 400)}

titles:
{json.dumps(s.get("retrieved_titles"), ensure_ascii=False)}

MR: {s.get("missing_recovery_rate")}
support_recall: {s.get("support_recall_hop2")}
strong_score: {s.get("strong_score")}

summary_2:
{trunc(s.get("summary_2"), 900)}
"""


def render_attempt(a):
    j = a.get("judge", {})
    gen = a.get("midpoint_generation", {})
    return f"""## case={a.get("case_id")} iter={a.get("iter")} attempt={a.get("attempt_no")}

question:
{a.get("question", "")}

### Verdict

left_valid: {a.get("left_valid")}
right_valid: {a.get("right_valid")}
both_valid: {a.get("both_valid")}
inserted: {a.get("inserted")}

left_reason:
{j.get("left_reason")}

right_reason:
{j.get("right_reason")}

### Generated midpoint rationale

{gen.get("rationale")}

### R_left

{fmt_state(a.get("left_state", {}))}

### R_mid

{fmt_state(a.get("mid_state", {}))}

### R_right

{fmt_state(a.get("right_state", {}))}

---
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n-valid", type=int, default=5)
    ap.add_argument("--n-right-fail", type=int, default=8)
    ap.add_argument("--n-left-fail", type=int, default=4)
    ap.add_argument("--n-both-fail", type=int, default=4)
    args = ap.parse_args()

    rows = read_jsonl(args.attempts)
    first = [r for r in rows if int(r.get("attempt_no", 0)) == 0]

    valid = [r for r in first if r.get("both_valid")]
    right_fail = [r for r in first if r.get("left_valid") and not r.get("right_valid")]
    left_fail = [r for r in first if not r.get("left_valid") and r.get("right_valid")]
    both_fail = [r for r in first if not r.get("left_valid") and not r.get("right_valid")]

    chunks = []
    chunks.append("# Qwen Distance Qualitative Examples\n")
    chunks.append("## Counts\n")
    chunks.append(f"- first-pass attempts: {len(first)}\n")
    chunks.append(f"- valid: {len(valid)}\n")
    chunks.append(f"- right_fail: {len(right_fail)}\n")
    chunks.append(f"- left_fail: {len(left_fail)}\n")
    chunks.append(f"- both_fail: {len(both_fail)}\n\n")

    groups = [
        ("Valid midpoint examples", valid[:args.n_valid]),
        ("Right-valid failure examples", right_fail[:args.n_right_fail]),
        ("Left-valid failure examples", left_fail[:args.n_left_fail]),
        ("Both-side failure examples", both_fail[:args.n_both_fail]),
    ]

    for title, rs in groups:
        chunks.append(f"# {title}\n\n")
        for r in rs:
            chunks.append(render_attempt(r))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(chunks), encoding="utf-8")
    print("[wrote]", args.out)


if __name__ == "__main__":
    main()
