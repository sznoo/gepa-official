#!/usr/bin/env python3
import argparse
import json
import random
from pathlib import Path

from datasets import load_dataset


def support_titles(row):
    sf = row.get("supporting_facts") or {}
    if isinstance(sf, dict):
        return list(dict.fromkeys(str(t).strip() for t in sf.get("title", []) if str(t).strip()))
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hf-split", default="train")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="experiments/feedback_distance_v2/cache/dev300_random_seed1.jsonl")
    ap.add_argument("--summary-out", default="experiments/feedback_distance_v2/cache/dev300_random_seed1_summary.json")
    args = ap.parse_args()

    raw = load_dataset("hotpot_qa", "fullwiki", split=args.hf_split)
    rows = [dict(r) for r in raw if r.get("question")]

    rng = random.Random(args.seed)
    sampled = rng.sample(rows, args.n)

    out_rows = []
    for i, row in enumerate(sampled):
        out_rows.append({
            "idx": str(row.get("_id") or row.get("id") or i),
            "question": row["question"],
            "gold_answer": row.get("answer"),
            "gold_support_titles": support_titles(row),
            "raw": row,
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    summary = {
        "dataset": "hotpot_qa/fullwiki",
        "hf_split": args.hf_split,
        "seed": args.seed,
        "n_source_valid_examples": len(rows),
        "n_sampled": len(out_rows),
        "out": str(out),
        "idxs": [r["idx"] for r in out_rows],
    }
    Path(args.summary_out).write_text(json.dumps(summary, ensure_ascii=False, indent=2))

    print("[wrote]", out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary, ensure_ascii=False, indent=2)[:3000])


if __name__ == "__main__":
    main()
