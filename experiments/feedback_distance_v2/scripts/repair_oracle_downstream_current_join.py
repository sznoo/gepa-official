#!/usr/bin/env python3
# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/repair_oracle_downstream_current_join.py
from __future__ import annotations

import argparse
import json
import re
import string
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


def normalize_answer(s: Any) -> str:
    s = str(s or "")

    def lower(text: str) -> str:
        return text.lower()

    def remove_punc(text: str) -> str:
        return "".join(ch for ch in text if ch not in set(string.punctuation))

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def make_key(row: dict[str, Any]) -> tuple[str, str]:
    return (
        " ".join(str(row.get("question") or "").split()),
        normalize_answer(row.get("gold_answer")),
    )


def mean_bool(rows: list[dict[str, Any]], key: str) -> float | None:
    if not rows:
        return None
    return sum(bool(r.get(key)) for r in rows) / len(rows)


def count_bool(rows: list[dict[str, Any]], key: str) -> int:
    return sum(bool(r.get(key)) for r in rows)


def summarize_subset(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    n = len(rows)

    base_default_em = mean_bool(rows, "current_base_score")
    base_oracle_em = mean_bool(rows, "oracle_base_score")
    strong_default_em = mean_bool(rows, "current_strong_score")
    strong_oracle_em = mean_bool(rows, "oracle_strong_score")

    return {
        "name": name,
        "n": n,
        "base": {
            "default_hop2_em": base_default_em,
            "oracle_query_em": base_oracle_em,
            "oracle_gap": None if base_default_em is None or base_oracle_em is None else base_oracle_em - base_default_em,
            "default_hop2_correct": count_bool(rows, "current_base_score"),
            "oracle_query_correct": count_bool(rows, "oracle_base_score"),
            "oracle_gain_count": count_bool(rows, "oracle_base_gain"),
            "oracle_loss_count": count_bool(rows, "oracle_base_loss"),
        },
        "strong": {
            "default_hop2_em": strong_default_em,
            "oracle_query_em": strong_oracle_em,
            "oracle_gap": None if strong_default_em is None or strong_oracle_em is None else strong_oracle_em - strong_default_em,
            "default_hop2_correct": count_bool(rows, "current_strong_score"),
            "oracle_query_correct": count_bool(rows, "oracle_strong_score"),
            "oracle_gain_count": count_bool(rows, "oracle_strong_gain"),
            "oracle_loss_count": count_bool(rows, "oracle_strong_loss"),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--oracle-eval", type=Path, default=Path("experiments/feedback_distance_v2/results/oracle_query_downstream_eval.jsonl"))
    ap.add_argument("--current-final-eval", type=Path, default=Path("experiments/feedback_distance_v2/results/final_answerer_current_summary_eval.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("experiments/feedback_distance_v2/results/oracle_query_downstream_eval.repaired.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/feedback_distance_v2/results/oracle_query_downstream_summary.repaired.json"))
    args = ap.parse_args()

    oracle_rows = read_jsonl(args.oracle_eval)
    current_rows = read_jsonl(args.current_final_eval)

    current_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    duplicates = []
    for r in current_rows:
        k = make_key(r)
        if k in current_by_key:
            duplicates.append(k)
        current_by_key[k] = r

    if duplicates:
        raise RuntimeError(f"duplicate question+gold keys in current eval: {len(duplicates)}")

    repaired = []
    missing = []
    for r in oracle_rows:
        k = make_key(r)
        cur = current_by_key.get(k)
        if cur is None:
            missing.append(k)
            continue

        rr = dict(r)

        rr["current_base_answer"] = cur.get("base_answer")
        rr["current_base_score"] = bool(cur.get("base_score"))
        rr["current_strong_answer"] = cur.get("strong_answer")
        rr["current_strong_score"] = bool(cur.get("strong_score"))

        rr["oracle_base_gain"] = (not rr["current_base_score"]) and bool(rr.get("oracle_base_score"))
        rr["oracle_base_loss"] = rr["current_base_score"] and (not bool(rr.get("oracle_base_score")))

        rr["oracle_strong_gain"] = (not rr["current_strong_score"]) and bool(rr.get("oracle_strong_score"))
        rr["oracle_strong_loss"] = rr["current_strong_score"] and (not bool(rr.get("oracle_strong_score")))

        rr["current_eval_row"] = cur
        repaired.append(rr)

    if missing:
        raise RuntimeError(f"missing matches: {len(missing)}")

    write_jsonl(args.out, repaired)

    hit_rows = [r for r in repaired if r.get("oracle_target_hit")]
    miss_rows = [r for r in repaired if not r.get("oracle_target_hit")]

    summary = {
        "oracle_eval_source": str(args.oracle_eval),
        "current_final_eval": str(args.current_final_eval),
        "out": str(args.out),
        "n": len(repaired),
        "main_table": summarize_subset(repaired, "all_oracle_targets_65"),
        "by_oracle_target_hit": {
            "hit": summarize_subset(hit_rows, "oracle_target_hit"),
            "miss": summarize_subset(miss_rows, "oracle_target_miss"),
        },
        "sanity": {
            "current_base_correct_on_65": count_bool(repaired, "current_base_score"),
            "current_strong_correct_on_65": count_bool(repaired, "current_strong_score"),
            "oracle_base_correct_on_65": count_bool(repaired, "oracle_base_score"),
            "oracle_strong_correct_on_65": count_bool(repaired, "oracle_strong_score"),
        },
    }

    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary["main_table"], ensure_ascii=False, indent=2))
    print("\n[sanity]")
    print(json.dumps(summary["sanity"], ensure_ascii=False, indent=2))
    print("\n[by_oracle_target_hit]")
    print(json.dumps(summary["by_oracle_target_hit"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
