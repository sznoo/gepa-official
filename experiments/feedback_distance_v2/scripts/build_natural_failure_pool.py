# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/build_natural_failure_pool.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollout", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_rollout_dev300.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("experiments/feedback_distance_v2/cache/natural_failure_pool.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/feedback_distance_v2/cache/natural_failure_pool_summary.json"))
    args = ap.parse_args()

    rows = read_jsonl(args.rollout)

    eligible = [r for r in rows if r.get("missing_after_hop1")]
    failures = [
        {
            **r,
            "failure_pool_source": "fixed_prompt_rollout_dev300",
            "failure_definition": "missing_after_hop1_nonempty_and_missing_after_hop2_nonempty",
        }
        for r in eligible
        if r.get("missing_after_hop2")
    ]

    write_jsonl(args.out, failures)

    summary = {
        "rollout": str(args.rollout),
        "out": str(args.out),
        "n_total": len(rows),
        "n_eligible_second_hop": len(eligible),
        "n_natural_retrieval_failures": len(failures),
        "eligible_rate": len(eligible) / len(rows) if rows else None,
        "failure_rate_total": len(failures) / len(rows) if rows else None,
        "failure_rate_among_eligible": len(failures) / len(eligible) if eligible else None,
    }
    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
