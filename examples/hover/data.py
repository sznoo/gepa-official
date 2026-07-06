# examples/hover/data.py

import random
from typing import Optional

import dspy
from datasets import load_dataset
from tqdm import tqdm


def count_unique_docs(example) -> int:
    return len(set(fact["key"] for fact in example["supporting_facts"]))


def to_dspy_example(example) -> dspy.Example:
    return dspy.Example(
        claim=example["claim"],
        supporting_facts=example["supporting_facts"],
        label=example["label"],
    ).with_inputs("claim")


def load_hover_examples(
    seed: int = 0,
    max_examples: Optional[int] = None,
):
    dataset = load_dataset("hover", trust_remote_code=True)
    hf_trainset = dataset["train"]

    examples = []

    for ex in tqdm(hf_trainset, desc="Loading HoVer 3-hop examples"):
        if count_unique_docs(ex) != 3:
            continue

        examples.append(
            {
                "claim": ex["claim"],
                "supporting_facts": ex["supporting_facts"],
                "label": ex["label"],
            }
        )

    rng = random.Random(seed)
    rng.shuffle(examples)

    if max_examples is not None:
        examples = examples[:max_examples]

    return examples


def load_hover_splits(
    train_size: int = 128,
    val_size: int = 128,
    test_size: int = 128,
    seed: int = 0,
):
    total_size = train_size + val_size + test_size

    examples = load_hover_examples(
        seed=seed,
        max_examples=total_size,
    )

    if len(examples) < total_size:
        raise ValueError(
            f"Requested {total_size} examples, but only found {len(examples)} "
            "3-hop HoVer examples."
        )

    train_raw = examples[:train_size]
    val_raw = examples[train_size : train_size + val_size]
    test_raw = examples[train_size + val_size : total_size]

    trainset = [to_dspy_example(ex) for ex in train_raw]
    valset = [to_dspy_example(ex) for ex in val_raw]
    testset = [to_dspy_example(ex) for ex in test_raw]

    return trainset, valset, testset


if __name__ == "__main__":
    trainset, valset, testset = load_hover_splits(
        train_size=8,
        val_size=8,
        test_size=8,
        seed=0,
    )

    print(f"train: {len(trainset)}")
    print(f"val:   {len(valset)}")
    print(f"test:  {len(testset)}")
    print(trainset[0])