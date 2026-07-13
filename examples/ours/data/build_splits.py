#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from datasets import load_dataset


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    tmp.replace(path)


def make_rows(
    rows: list[dict[str, Any]],
    *,
    split_name: str,
) -> list[dict[str, Any]]:
    out = []

    for split_index, row in enumerate(rows):
        source_id = row.get("id")
        if source_id is None:
            raise ValueError(
                f"Raw HotpotQA row has no id: "
                f"split={split_name}, index={split_index}, keys={list(row.keys())}"
            )

        out.append({
            "sample_id": str(source_id),
            "split": split_name,
            "split_index": split_index,
            "question": row["question"],
            "answer": row["answer"],
            "context": row["context"],
            "supporting_facts": row["supporting_facts"],
            "id": str(source_id),
            "type": row.get("type"),
            "level": row.get("level"),
        })

    return out


def validate_disjoint(
    train_rows: list[dict[str, Any]],
    val_rows: list[dict[str, Any]],
    test_rows: list[dict[str, Any]],
) -> None:
    train_ids = {r["sample_id"] for r in train_rows}
    val_ids = {r["sample_id"] for r in val_rows}
    test_ids = {r["sample_id"] for r in test_rows}

    if len(train_ids) != len(train_rows):
        raise ValueError("Duplicate IDs in train split.")
    if len(val_ids) != len(val_rows):
        raise ValueError("Duplicate IDs in validation split.")
    if len(test_ids) != len(test_rows):
        raise ValueError("Duplicate IDs in test split.")

    if train_ids & val_ids:
        raise ValueError("Train/validation overlap detected.")
    if train_ids & test_ids:
        raise ValueError("Train/test overlap detected.")
    if val_ids & test_ids:
        raise ValueError("Validation/test overlap detected.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--train-size", type=int, default=150)
    parser.add_argument("--val-size", type=int, default=150)
    parser.add_argument("--test-size", type=int, default=150)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--hf-split", type=str, default="train")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("experiments/method_probe/data"),
    )
    parser.add_argument("--overwrite", action="store_true")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "train": args.out_dir / f"train{args.train_size}_seed{args.seed}.jsonl",
        "val": args.out_dir / f"val{args.val_size}_seed{args.seed}.jsonl",
        "test": args.out_dir / f"test{args.test_size}_seed{args.seed}.jsonl",
        "manifest": args.out_dir / "split.json",
    }

    existing = [p for p in paths.values() if p.exists()]
    if existing and not args.overwrite:
        raise FileExistsError(
            "Output files already exist. Use --overwrite:\n"
            + "\n".join(str(p) for p in existing)
        )

    raw = load_dataset(
        "hotpot_qa",
        "fullwiki",
        split=args.hf_split,
    )

    rows = [dict(row) for row in raw]
    random.Random(args.seed).shuffle(rows)

    total_required = args.train_size + args.val_size + args.test_size
    if len(rows) < total_required:
        raise ValueError(
            f"Not enough rows: available={len(rows)}, required={total_required}"
        )

    train_raw = rows[:args.train_size]

    val_start = args.train_size
    val_end = val_start + args.val_size
    val_raw = rows[val_start:val_end]

    test_start = val_end
    test_end = test_start + args.test_size
    test_raw = rows[test_start:test_end]

    train_rows = make_rows(train_raw, split_name="train")
    val_rows = make_rows(val_raw, split_name="val")
    test_rows = make_rows(test_raw, split_name="test")

    validate_disjoint(train_rows, val_rows, test_rows)

    write_jsonl(paths["train"], train_rows)
    write_jsonl(paths["val"], val_rows)
    write_jsonl(paths["test"], test_rows)

    manifest = {
        "dataset": "hotpot_qa",
        "dataset_config": "fullwiki",
        "hf_split": args.hf_split,
        "seed": args.seed,
        "sampling": "shuffle_once_then_contiguous_slice",
        "sizes": {
            "train": len(train_rows),
            "val": len(val_rows),
            "test": len(test_rows),
        },
        "files": {
            "train": paths["train"].name,
            "val": paths["val"].name,
            "test": paths["test"].name,
        },
        "sample_ids": {
            "train": [r["sample_id"] for r in train_rows],
            "val": [r["sample_id"] for r in val_rows],
            "test": [r["sample_id"] for r in test_rows],
        },
    }

    tmp = paths["manifest"].with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(paths["manifest"])

    print(json.dumps({
        "out_dir": str(args.out_dir.resolve()),
        "sizes": manifest["sizes"],
        "first_ids": {
            "train": train_rows[0]["sample_id"],
            "val": val_rows[0]["sample_id"],
            "test": test_rows[0]["sample_id"],
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
