# examples/hover/metric.py

import dspy


def count_unique_docs(example) -> int:
    return len(set(fact["key"] for fact in example["supporting_facts"]))


def get_gold_titles(example) -> set[str]:
    return set(
        map(
            dspy.evaluate.normalize_text,
            [doc["key"] for doc in example.supporting_facts],
        )
    )


def get_found_titles(pred) -> set[str]:
    return set(
        map(
            dspy.evaluate.normalize_text,
            [doc.split(" | ")[0] for doc in pred.retrieved_docs],
        )
    )


def discrete_retrieval_eval(example, pred, trace=None) -> float:
    gold_titles = get_gold_titles(example)
    found_titles = get_found_titles(pred)

    return float(gold_titles.issubset(found_titles))


def discrete_retrieval_eval_with_feedback(example, pred, trace=None):
    gold_titles = get_gold_titles(example)
    found_titles = get_found_titles(pred)

    score = float(gold_titles.issubset(found_titles))

    gold_titles_found = gold_titles.intersection(found_titles)
    gold_titles_missing = gold_titles.difference(found_titles)

    feedback_text = (
        "Your queries correctly retrieved the following relevant evidence "
        f"documents: {gold_titles_found}, but missed the following relevant "
        f"evidence documents: {gold_titles_missing}."
    )

    return dspy.Prediction(
        score=score,
        feedback=feedback_text,
    )