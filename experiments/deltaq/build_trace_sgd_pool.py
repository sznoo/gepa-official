import argparse
import json
import random
from pathlib import Path


def read_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def as_set(x):
    return set(x or [])


def score(row):
    try:
        return float(row.get("score", 0.0))
    except Exception:
        return 0.0


def is_wrong_hop2_miss(r):
    gold = as_set(r.get("gold_support_titles"))
    hop1 = as_set(r.get("hop1_titles"))
    missing_after_hop1 = gold - hop1
    missing_after_hop2 = as_set(r.get("missing_titles_after_hop2"))

    return (
        score(r) < 1.0
        and len(missing_after_hop1) > 0
        and len(missing_after_hop2) > 0
    )


def hop2_dependent_signal(r):
    """
    Diagnostic only. Not used for selecting correct_pool by default.
    """
    gold = as_set(r.get("gold_support_titles"))
    hop1 = as_set(r.get("hop1_titles"))
    hop2 = as_set(r.get("hop2_titles"))
    missing_after_hop1 = gold - hop1
    recovered_by_hop2 = missing_after_hop1 & hop2

    new_support = as_set(r.get("new_support_titles_hop2"))

    try:
        recall_total = float(r.get("support_recall_total", 0.0))
        recall_hop1 = float(r.get("support_recall_hop1", 0.0))
    except Exception:
        recall_total, recall_hop1 = 0.0, 0.0

    return (
        len(recovered_by_hop2) > 0
        or len(new_support) > 0
        or recall_total > recall_hop1
    )


def compact_trace(r, label):
    gold = as_set(r.get("gold_support_titles"))
    hop1 = as_set(r.get("hop1_titles"))
    hop2 = as_set(r.get("hop2_titles"))

    missing_after_hop1 = sorted(gold - hop1)
    recovered_by_hop2 = sorted((gold - hop1) & hop2)

    return {
        "pool_label": label,
        "eval_index": r.get("eval_index"),
        "example_id": r.get("example_id"),
        "_id": r.get("_id"),

        "question": r.get("question"),
        "gold_answer": r.get("gold_answer"),
        "pred_answer": r.get("pred_answer"),
        "score": r.get("score"),

        "hop1_query": r.get("hop1_query"),
        "hop1_titles": r.get("hop1_titles"),
        "summary_1": r.get("summary_1"),

        "hop2_query": r.get("hop2_query"),
        "hop2_titles": r.get("hop2_titles"),
        "summary_2": r.get("summary_2"),

        "gold_support_titles": r.get("gold_support_titles"),
        "new_support_titles_hop2": r.get("new_support_titles_hop2"),
        "missing_titles_after_hop1": missing_after_hop1,
        "recovered_missing_titles_hop2": recovered_by_hop2,
        "missing_titles_after_hop2": r.get("missing_titles_after_hop2"),

        "support_recall_hop1": r.get("support_recall_hop1"),
        "support_recall_hop2_only": r.get("support_recall_hop2_only"),
        "support_recall_total": r.get("support_recall_total"),

        # Diagnostic only. Not a selection criterion unless explicitly used later.
        "hop2_dependent_signal": hop2_dependent_signal(r),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--trace-path",
        default=(
            "outputs/hotpotqa_representation_prompt_screening/"
            "rep_prompt_screening_24_dev300_final_v2/conditions/"
            "final_manual_only/analysis/rollout_traces.jsonl"
        ),
    )
    ap.add_argument("--out-dir", default="experiments/deltaq/trace_sgd_pool")
    ap.add_argument("--seed", type=int, default=13)

    ap.add_argument("--n-fail", type=int, default=41)
    ap.add_argument("--n-correct", type=int, default=41)

    ap.add_argument("--batch-size", type=int, default=10)
    ap.add_argument("--num-batches", type=int, default=10)
    ap.add_argument("--fail-per-batch", type=int, default=None)

    args = ap.parse_args()

    rng = random.Random(args.seed)
    rows = read_jsonl(args.trace_path)

    fail_all = [r for r in rows if is_wrong_hop2_miss(r)]
    correct_all = [r for r in rows if score(r) >= 1.0]

    rng.shuffle(fail_all)
    rng.shuffle(correct_all)

    fail_sel = fail_all[: min(args.n_fail, len(fail_all))]
    correct_sel = correct_all[: min(args.n_correct, len(correct_all))]

    fail_out = [compact_trace(r, "fail_wrong_hop2_miss") for r in fail_sel]
    correct_out = [compact_trace(r, "correct_random_preserve") for r in correct_sel]

    mixed = fail_out + correct_out
    rng.shuffle(mixed)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    write_jsonl(out_dir / "fail_pool.jsonl", fail_out)
    write_jsonl(out_dir / "correct_pool.jsonl", correct_out)
    write_jsonl(out_dir / "mixed_pool.jsonl", mixed)

    # Balanced by default: half fail, half correct.
    if args.fail_per_batch is None:
        fail_per_batch = args.batch_size // 2
    else:
        fail_per_batch = args.fail_per_batch

    correct_per_batch = args.batch_size - fail_per_batch

    batches = []
    for b in range(args.num_batches):
        f_batch = rng.sample(fail_out, min(fail_per_batch, len(fail_out)))
        c_batch = rng.sample(correct_out, min(correct_per_batch, len(correct_out)))

        batch = f_batch + c_batch
        rng.shuffle(batch)

        for item in batch:
            x = dict(item)
            x["batch_id"] = b
            batches.append(x)

    write_jsonl(out_dir / "minibatches.jsonl", batches)

    correct_hop2_dep = sum(1 for r in correct_out if r["hop2_dependent_signal"])
    fail_hop2_dep = sum(1 for r in fail_out if r["hop2_dependent_signal"])

    print("[trace path]", args.trace_path)
    print("[total rows]", len(rows))
    print("[fail wrong_hop2_miss available]", len(fail_all))
    print("[correct score==1 available]", len(correct_all))
    print("[selected fail]", len(fail_out))
    print("[selected correct]", len(correct_out))
    print("[selected correct hop2_dependent_signal diagnostic]", correct_hop2_dep)
    print("[selected fail hop2_dependent_signal diagnostic]", fail_hop2_dep)
    print("[mixed pool]", len(mixed))
    print("[batch size]", args.batch_size)
    print("[fail per batch]", fail_per_batch)
    print("[correct per batch]", correct_per_batch)
    print("[num batches]", args.num_batches)
    print("[minibatch rows]", len(batches))
    print("[out dir]", out_dir)


if __name__ == "__main__":
    main()
