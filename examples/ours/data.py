# /home/jinwoo/gepa-official/examples/hotpotqa/data.py
import random
from typing import Optional

import dspy
from datasets import load_dataset


def _to_example(row) -> dspy.Example:
    return dspy.Example(
        question=row["question"],
        answer=row["answer"],
        context=row["context"],
        supporting_facts=row["supporting_facts"],
        _id=row.get("_id", None),
        type=row.get("type", None),
        level=row.get("level", None),
    ).with_inputs("question")


def _take_split(items, start: int, size: Optional[int]):
    if size is None:
        return items[start:], len(items)
    end = start + size
    return items[start:end], end


def load_hotpot_splits(
    train_size: Optional[int] = 100,
    val_size: Optional[int] = 100,
    test_size: Optional[int] = 100,
    seed: int = 0,
    hf_split: str = "train",
):
    """
    Load HotpotQA fullwiki and create deterministic train/val/test splits.

    Args:
        train_size: number of train examples. None means use all remaining.
        val_size: number of validation examples. None means use all remaining.
        test_size: number of test examples. None means use all remaining.
        seed: shuffle seed.
        hf_split: HuggingFace split to draw from. Artifact used "train".

    Returns:
        trainset, valset, testset: lists of dspy.Example.
    """
    raw = load_dataset("hotpot_qa", "fullwiki", split=hf_split)

    examples = [_to_example(row) for row in raw]
    random.Random(seed).shuffle(examples)

    idx = 0
    trainset, idx = _take_split(examples, idx, train_size)
    valset, idx = _take_split(examples, idx, val_size)
    testset, idx = _take_split(examples, idx, test_size)

    if not trainset:
        raise ValueError("trainset is empty. Increase train_size or check dataset loading.")
    if not valset:
        raise ValueError("valset is empty. Increase val_size or check dataset loading.")
    if not testset:
        raise ValueError("testset is empty. Increase test_size or check dataset loading.")

    return trainset, valset, testset


def inspect_hotpot_splits(
    train_size: Optional[int] = 8,
    val_size: Optional[int] = 8,
    test_size: Optional[int] = 8,
    seed: int = 0,
):
    trainset, valset, testset = load_hotpot_splits(
        train_size=train_size,
        val_size=val_size,
        test_size=test_size,
        seed=seed,
    )

    print(f"train={len(trainset)}, val={len(valset)}, test={len(testset)}")
    ex = trainset[0]
    print("Example fields:", list(ex.keys()))
    print("Input keys:", ex.inputs().keys())
    print("Question:", ex.question)
    print("Answer:", ex.answer)
    print("Supporting titles:", ex.supporting_facts["title"])


if __name__ == "__main__":
    inspect_hotpot_splits()