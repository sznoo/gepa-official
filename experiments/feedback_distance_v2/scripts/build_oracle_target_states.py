# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/build_oracle_target_states.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

from examples.hotpotqa.retriever import search, set_retriever_dir  # noqa: E402


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def norm_title(t: str) -> str:
    return " ".join(str(t).strip().lower().split())


def extract_titles(docs: list[str]) -> list[str]:
    return [str(d).split(" | ", 1)[0].strip() for d in docs]


def make_oracle_query(row: dict[str, Any]) -> str:
    q = str(row.get("question") or "").strip()
    targets = [str(t).strip() for t in row.get("missing_after_hop2") or [] if str(t).strip()]
    return " ".join(targets + [q]).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--failure-pool", type=Path, default=Path("experiments/feedback_distance_v2/cache/natural_failure_pool.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("experiments/feedback_distance_v2/cache/oracle_targets.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/feedback_distance_v2/cache/oracle_targets_summary.json"))
    ap.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    ap.add_argument("--k", type=int, default=7)
    args = ap.parse_args()

    set_retriever_dir(str(args.retriever_dir))
    rows = read_jsonl(args.failure_pool)

    out_rows = []
    for row in rows:
        target_titles = list(row.get("missing_after_hop2") or [])
        target_norm = {norm_title(t) for t in target_titles}

        oracle_query = make_oracle_query(row)
        docs = list(search(oracle_query, k=args.k).passages)
        retrieved_titles = extract_titles(docs)
        retrieved_norm = {norm_title(t) for t in retrieved_titles}

        hit_norm = target_norm & retrieved_norm
        hit_titles = [t for t in target_titles if norm_title(t) in hit_norm]

        recovery = len(hit_norm) / len(target_norm) if target_norm else None

        out_rows.append({
            "idx": row.get("idx"),
            "question": row.get("question"),
            "summary_1": row.get("summary_1"),

            "gold_answer": row.get("gold_answer"),
            "gold_support_titles": row.get("gold_support_titles"),

            "current_query": row.get("current_query"),
            "current_hop2_titles": row.get("current_hop2_titles"),
            "missing_after_hop1": row.get("missing_after_hop1"),
            "missing_after_hop2": target_titles,

            "oracle_target_titles": target_titles,
            "oracle_target_query": oracle_query,
            "oracle_target_retrieved_titles": retrieved_titles,
            "oracle_target_retrieved_docs": docs,
            "oracle_target_hit_titles": hit_titles,
            "oracle_target_hit": bool(hit_norm),
            "oracle_target_missing_recovery_rate": recovery,

            "current_row": row,
        })

    write_jsonl(args.out, out_rows)

    success = [r for r in out_rows if r["oracle_target_hit"]]
    rates = [
        r["oracle_target_missing_recovery_rate"]
        for r in out_rows
        if r["oracle_target_missing_recovery_rate"] is not None
    ]

    summary = {
        "failure_pool": str(args.failure_pool),
        "out": str(args.out),
        "n": len(out_rows),
        "n_oracle_target_success": len(success),
        "oracle_target_success_rate": len(success) / len(out_rows) if out_rows else None,
        "mean_oracle_target_missing_recovery_rate": sum(rates) / len(rates) if rates else None,
        "retriever_dir": str(args.retriever_dir),
        "k": args.k,
        "oracle_query_rule": "missing_after_hop2_titles + question",
    }
    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
