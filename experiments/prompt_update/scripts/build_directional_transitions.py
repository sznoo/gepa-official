# /home/jinwoo/gepa-official/experiments/prompt_update/scripts/build_directional_transitions.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


# Deterministically assemble transition rows for later:
#   directional transition -> delta_q -> delta_p
#
# No LLM call here.
# This script only normalizes all endpoint sources into one JSONL table.

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.open("r", encoding="utf-8") if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")


def compact_actual_state(s: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize a real rollout/oracle state."""
    s = s or {}
    return {
        "state_role": s.get("state_role"),
        "query": s.get("query"),
        "retrieved_titles": s.get("retrieved_titles") or [],
        "summary_2": s.get("summary_2"),
        "retrieved_docs": s.get("retrieved_docs") or [],
        "missing_titles_after_hop2": s.get("missing_titles_after_hop2") or [],
        "new_support_titles_hop2": s.get("new_support_titles_hop2") or [],
        "support_recall_total": s.get("support_recall_total"),
        "support_recall_hop2_only": s.get("support_recall_hop2_only"),
        "missing_recovery_rate": s.get("missing_recovery_rate"),
        "base_score": s.get("base_score"),
        "strong_score": s.get("strong_score"),
        "score": s.get("score"),
    }


def compact_expected_damaged_state(rminus: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize generated semantic endpoint R_C^-.

    This is not an actual BM25 result.
    Keep expected_* naming to avoid mixing with real retrieved titles.
    """
    rminus = rminus or {}
    return {
        "state_role": rminus.get("state_role") or "transported_damaged",
        "query": rminus.get("damaged_query"),
        "expected_retrieved_titles": rminus.get("expected_retrieved_titles") or [],
        "expected_missing_or_weakened_support_titles": rminus.get("expected_missing_or_weakened_support_titles") or [],
        "summary_2": rminus.get("damaged_retrieval_summary"),
        "expected_effect": rminus.get("expected_effect"),
        "is_semantic_endpoint": True,
        "is_actual_bm25_result": False,
    }


def base_meta(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": int(rec["case_id"]),
        "bucket": rec.get("bucket"),
        "question": rec.get("question"),
        "gold_answer": rec.get("gold_answer"),
        "gold_support_titles": rec.get("gold_support_titles") or [],
        "summary_1": rec.get("summary_1"),
    }


def make_transition_id(batch_id: int, case_id: int, transition_family: str) -> str:
    return f"b{batch_id}_case{case_id}_{transition_family}"


def make_transition(
    *,
    batch_id: int,
    rec: dict[str, Any],
    transition_family: str,
    direction_label: str,
    polarity: str,
    source_R: dict[str, Any],
    target_R: dict[str, Any],
    endpoint_source: str,
    source_R_role: str,
    target_R_role: str,
    delta_R_prime: dict[str, Any] | None = None,
    matched_w_case_id: int | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    cid = int(rec["case_id"])
    return {
        "row_type": "directional_transition",
        "transition_id": make_transition_id(batch_id, cid, transition_family),
        "batch_id": batch_id,
        **base_meta(rec),
        "transition_family": transition_family,
        "direction_label": direction_label,
        "polarity": polarity,
        "endpoint_source": endpoint_source,
        "source_R_role": source_R_role,
        "target_R_role": target_R_role,
        "source_R": source_R,
        "target_R": target_R,
        "delta_R_prime": delta_R_prime,
        "matched_w_case_id": matched_w_case_id,
        "notes": notes or [],
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()

    ap.add_argument("--split", type=Path, default=Path("experiments/prompt_update/data/positive_safety_b10_split_seed0.json"))
    ap.add_argument("--case-state-index", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/case_state_index.json"))
    ap.add_argument("--transported-endpoints", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_c_transported_endpoints.jsonl"))

    ap.add_argument("--batch-id", type=int, default=0)
    ap.add_argument("--composition", type=str, default="mixed_custom")

    ap.add_argument("--out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_directional_transitions.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_directional_transitions.summary.json"))

    return ap.parse_args()


def main() -> None:
    args = parse_args()

    split = read_json(args.split)
    index = read_json(args.case_state_index)
    transported_rows = [r for r in read_jsonl(args.transported_endpoints) if not r.get("error")]

    transported_by_case = {int(r["case_id"]): r for r in transported_rows}

    batch = split["update_batches"]["compositions"][args.composition]["batches"][args.batch_id]
    by_bucket = batch["case_ids_by_bucket"]

    rows: list[dict[str, Any]] = []

    # 1) W_retrieval: ordinary repair-candidate transition.
    for cid in by_bucket.get("W_retrieval", []):
        rec = dict(index["cases"][str(cid)])
        rec["case_id"] = int(cid)

        if not rec.get("oracle_available"):
            raise ValueError(f"W_retrieval case {cid} has no oracle target")

        rows.append(make_transition(
            batch_id=args.batch_id,
            rec=rec,
            transition_family="w_retrieval_repair",
            direction_label="repair_candidate",
            polarity="encourage",
            endpoint_source="current_failed_to_oracle_target",
            source_R_role="current_failed",
            target_R_role="oracle_target",
            source_R=compact_actual_state(rec["current_state"]),
            target_R=compact_actual_state(rec["oracle_state"]),
            notes=[
                "W-side repair candidate.",
                "This transition is used by neg_only and custom conditions."
            ],
        ))

    # 2) C_fragile: no generated damaged endpoint; current fragile is R_minus.
    for cid in by_bucket.get("C_fragile", []):
        rec = dict(index["cases"][str(cid)])
        rec["case_id"] = int(cid)

        if not rec.get("oracle_available"):
            raise ValueError(f"C_fragile case {cid} has no oracle target")

        current_fragile = compact_actual_state(rec["current_state"])
        oracle_target = compact_actual_state(rec["oracle_state"])

        rows.append(make_transition(
            batch_id=args.batch_id,
            rec=rec,
            transition_family="c_fragile_preserve",
            direction_label="recover_or_preserve_reference",
            polarity="encourage",
            endpoint_source="current_fragile_to_oracle_target",
            source_R_role="current_fragile",
            target_R_role="oracle_target",
            source_R=current_fragile,
            target_R=oracle_target,
            notes=[
                "C_fragile is already answer-correct but retrieval-incomplete.",
                "No transported damaged endpoint is generated; current fragile state is R_minus."
            ],
        ))

        rows.append(make_transition(
            batch_id=args.batch_id,
            rec=rec,
            transition_family="c_fragile_signed",
            direction_label="downhill_avoid",
            polarity="avoid",
            endpoint_source="oracle_target_to_current_fragile",
            source_R_role="oracle_target",
            target_R_role="current_fragile",
            source_R=oracle_target,
            target_R=current_fragile,
            notes=[
                "Signed C-side representation.",
                "This is an avoid/downhill transition; do not invert the resulting delta_p."
            ],
        ))

    # 3) C_clean and W_other: use generated R_minus = R_plus + transported delta_R_prime.
    for bucket in ["C_clean", "W_other"]:
        for cid in by_bucket.get(bucket, []):
            cid = int(cid)
            rec = dict(index["cases"][str(cid)])
            rec["case_id"] = cid

            if cid not in transported_by_case:
                raise ValueError(f"missing transported endpoint for case {cid}")

            trow = transported_by_case[cid]
            R_plus = compact_actual_state(rec["current_state"])
            R_minus = compact_expected_damaged_state(trow["R_minus"])
            delta_R_prime = trow.get("delta_R_prime")

            rows.append(make_transition(
                batch_id=args.batch_id,
                rec=rec,
                transition_family=f"{bucket.lower()}_preserve",
                direction_label="recover_or_preserve_reference",
                polarity="encourage",
                endpoint_source="transported_damaged_to_current_reference",
                source_R_role="transported_damaged_R_minus",
                target_R_role="current_reference_R_plus",
                source_R=R_minus,
                target_R=R_plus,
                delta_R_prime=delta_R_prime,
                matched_w_case_id=trow.get("matched_w_case_id"),
                notes=[
                    "Preserve/recovery representation.",
                    "R_minus was generated as R_plus + transported delta_R_prime."
                ],
            ))

            rows.append(make_transition(
                batch_id=args.batch_id,
                rec=rec,
                transition_family=f"{bucket.lower()}_signed",
                direction_label="downhill_avoid",
                polarity="avoid",
                endpoint_source="current_reference_to_transported_damaged",
                source_R_role="current_reference_R_plus",
                target_R_role="transported_damaged_R_minus",
                source_R=R_plus,
                target_R=R_minus,
                delta_R_prime=delta_R_prime,
                matched_w_case_id=trow.get("matched_w_case_id"),
                notes=[
                    "Signed-landscape representation.",
                    "This is an avoid/downhill transition; do not invert preserve delta_p."
                ],
            ))

    write_jsonl(args.out, rows)

    summary = {
        "script": "build_directional_transitions.py",
        "batch_id": args.batch_id,
        "composition": args.composition,
        "out": str(args.out),
        "n_rows": len(rows),
        "counts_by_transition_family": {},
        "counts_by_bucket": {},
        "counts_by_polarity": {},
        "rows": [
            {
                "transition_id": r["transition_id"],
                "case_id": r["case_id"],
                "bucket": r["bucket"],
                "transition_family": r["transition_family"],
                "polarity": r["polarity"],
                "direction_label": r["direction_label"],
                "source_R_role": r["source_R_role"],
                "target_R_role": r["target_R_role"],
                "matched_w_case_id": r.get("matched_w_case_id"),
            }
            for r in rows
        ],
    }

    for r in rows:
        summary["counts_by_transition_family"][r["transition_family"]] = summary["counts_by_transition_family"].get(r["transition_family"], 0) + 1
        summary["counts_by_bucket"][r["bucket"]] = summary["counts_by_bucket"].get(r["bucket"], 0) + 1
        summary["counts_by_polarity"][r["polarity"]] = summary["counts_by_polarity"].get(r["polarity"], 0) + 1

    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps({
        "n_rows": summary["n_rows"],
        "counts_by_transition_family": summary["counts_by_transition_family"],
        "counts_by_bucket": summary["counts_by_bucket"],
        "counts_by_polarity": summary["counts_by_polarity"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
