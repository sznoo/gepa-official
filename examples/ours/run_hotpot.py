# /home/jinwoo/gepa-official/examples/ours/run_hotpot.py
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import dspy
from tqdm.auto import tqdm

from ours.prompts import (
    build_seed_candidate,
    load_prompt_candidate,
)
from ours.runtime import OursRuntime

from examples.ours.adapter import HotpotAdapter
from examples.ours.data import load_hotpot_splits
from examples.ours.metric import answer_exact_match
from examples.ours.program import HotpotMultiHop
from examples.ours.retriever import (
    DEFAULT_RETRIEVER_DIR,
    set_retriever_dir,
)


AGENTS = [
    "summary1",
    "query",
    "summary2",
    "final",
]


def make_dspy_lm(
    model: str,
    api_base: str | None,
    api_key: str,
    temperature: float,
    max_tokens: int,
):
    kwargs = {
        "api_key": api_key,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if api_base:
        kwargs["api_base"] = api_base

    return dspy.LM(model, **kwargs)


def save_json(path: str | Path, obj: Any):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            obj,
            indent=2,
            ensure_ascii=False,
        )
    )


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        default="smoke",
        choices=["smoke", "eval"],
    )

    # Data
    parser.add_argument("--train-size", type=int, default=150)
    parser.add_argument("--val-size", type=int, default=150)
    parser.add_argument("--test-size", type=int, default=150)
    parser.add_argument("--seed", type=int, default=0)

    parser.add_argument(
        "--split",
        default="train",
        choices=["train", "val", "test"],
    )
    parser.add_argument("--sample-index", type=int, default=0)

    # Program / retriever
    parser.add_argument(
        "--retriever-dir",
        default=os.environ.get(
            "HOTPOT_RETRIEVER_DIR",
            DEFAULT_RETRIEVER_DIR,
        ),
    )
    parser.add_argument("--k", type=int, default=7)

    # Task LM
    parser.add_argument(
        "--task-model",
        default=os.environ.get(
            "TASK_MODEL",
            "openai/Qwen/Qwen3-8B",
        ),
    )
    parser.add_argument(
        "--task-api-base",
        default=os.environ.get(
            "TASK_API_BASE",
            "http://localhost:8889/v1",
        ),
    )
    parser.add_argument(
        "--task-api-key",
        default=os.environ.get(
            "TASK_API_KEY",
            "dummy",
        ),
    )
    parser.add_argument(
        "--task-temperature",
        type=float,
        default=0.7,
    )
    parser.add_argument(
        "--task-max-tokens",
        type=int,
        default=4096,
    )

    # Candidate
    parser.add_argument(
        "--prompt-json",
        default=None,
        help=(
            "Optional JSON with top-level `prompts`. "
            "Uses baseline prompts when omitted."
        ),
    )

    # Evaluation
    parser.add_argument(
        "--num-threads",
        type=int,
        default=1,
        help=(
            "Number of samples evaluated concurrently. "
            "Use 1 for sequential evaluation."
        ),
    )

    # Cache / output
    parser.add_argument(
        "--cache-dir",
        default="examples/ours/cache",
    )
    parser.add_argument(
        "--run-dir",
        default="examples/ours/runs/adapter_smoke",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
    )

    return parser.parse_args()


def resolve_dataset(args, trainset, valset, testset):
    return {
        "train": trainset,
        "val": valset,
        "test": testset,
    }[args.split]


def run_smoke(
    runtime: OursRuntime,
    adapter: HotpotAdapter,
    dataset,
    candidate: dict[str, str],
    sample_index: int,
    run_dir: Path,
):
    example = dataset[sample_index]

    baseline_trace, baseline_cache_hit = runtime.forward(
        adapter=adapter,
        example=example,
        candidate=candidate,
        return_cache_hit=True,
    )

    save_json(
        run_dir / "baseline_trace.json",
        baseline_trace,
    )

    rerun_summaries = {}

    for agent in AGENTS:
        rerun_trace, cache_hit = runtime.rerun(
            adapter=adapter,
            example=example,
            candidate=candidate,
            start_agent=agent,
            baseline_trace=baseline_trace,
            return_cache_hit=True,
        )

        save_json(
            run_dir / f"rerun_{agent}.json",
            rerun_trace,
        )

        rerun_summaries[agent] = {
            "answer": rerun_trace["answer"],
            "score": rerun_trace["score"],
            "cache_hit": cache_hit,
        }

    summary = {
        "mode": "smoke",
        "sample_index": sample_index,
        "sample_id": baseline_trace.get("sample_id"),
        "baseline_answer": baseline_trace["answer"],
        "baseline_score": baseline_trace["score"],
        "baseline_cache_hit": baseline_cache_hit,
        "reruns": rerun_summaries,
    }

    save_json(
        run_dir / "summary.json",
        summary,
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


def run_eval(
    runtime: OursRuntime,
    adapter: HotpotAdapter,
    dataset,
    candidate: dict[str, str],
    run_dir: Path,
    num_threads: int,
):
    if num_threads < 1:
        raise ValueError(
            f"num_threads must be at least 1, got {num_threads}."
        )

    def evaluate_one(index, example):
        trace, cache_hit = runtime.forward(
            adapter=adapter,
            example=example,
            candidate=candidate,
            return_cache_hit=True,
        )

        return index, trace, cache_hit

    num_examples = len(dataset)

    # Futures finish out of order. Store each result at its original
    # dataset index so eval_rows.json remains deterministic.
    rows_by_index = [None] * num_examples
    scores_by_index = [None] * num_examples

    cache_hits = 0
    completed = 0
    correct = 0.0

    with ThreadPoolExecutor(
        max_workers=num_threads,
        thread_name_prefix="hotpot-eval",
    ) as executor:
        futures = {
            executor.submit(
                evaluate_one,
                index,
                example,
            ): index
            for index, example in enumerate(dataset)
        }

        with tqdm(
            total=num_examples,
            desc="Evaluating",
            unit="sample",
            dynamic_ncols=True,
        ) as progress:
            try:
                for future in as_completed(futures):
                    index, trace, cache_hit = future.result()

                    score = float(trace["score"])

                    scores_by_index[index] = score
                    rows_by_index[index] = {
                        "index": index,
                        "cache_hit": cache_hit,
                        **trace,
                    }

                    completed += 1
                    correct += score
                    cache_hits += int(cache_hit)

                    progress.update(1)
                    progress.set_postfix(
                        em=f"{correct / completed:.3f}",
                        correct=int(correct),
                        cache_hits=cache_hits,
                        threads=num_threads,
                        refresh=False,
                    )

            except Exception:
                # Prevent pending samples from starting after one worker fails.
                for pending_future in futures:
                    pending_future.cancel()
                raise

    if any(score is None for score in scores_by_index):
        missing = [
            index
            for index, score in enumerate(scores_by_index)
            if score is None
        ]
        raise RuntimeError(
            f"Evaluation finished with missing scores: {missing}"
        )

    if any(row is None for row in rows_by_index):
        missing = [
            index
            for index, row in enumerate(rows_by_index)
            if row is None
        ]
        raise RuntimeError(
            f"Evaluation finished with missing rows: {missing}"
        )

    scores = [
        float(score)
        for score in scores_by_index
    ]
    rows = list(rows_by_index)

    mean_score = (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )

    summary = {
        "mode": "eval",
        "num_examples": len(scores),
        "score": mean_score,
        "num_correct": int(sum(scores)),
        "cache_hits": cache_hits,
        "cache_misses": len(scores) - cache_hits,
        "num_threads": num_threads,
    }

    save_json(
        run_dir / "eval_rows.json",
        rows,
    )
    save_json(
        run_dir / "summary.json",
        summary,
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main():
    args = parse_args()

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    task_lm = make_dspy_lm(
        model=args.task_model,
        api_base=args.task_api_base,
        api_key=args.task_api_key,
        temperature=args.task_temperature,
        max_tokens=args.task_max_tokens,
    )
    dspy.configure(lm=task_lm)

    set_retriever_dir(args.retriever_dir)

    trainset, valset, testset = load_hotpot_splits(
        train_size=args.train_size,
        val_size=args.val_size,
        test_size=args.test_size,
        seed=args.seed,
    )

    dataset = resolve_dataset(
        args,
        trainset,
        valset,
        testset,
    )

    program = HotpotMultiHop(
        k=args.k,
        retriever_dir=args.retriever_dir,
    )

    if args.prompt_json:
        prompt_name, candidate = load_prompt_candidate(
            args.prompt_json,
            program=program,
        )
    else:
        prompt_name = "baseline"
        candidate = build_seed_candidate(program)

    save_json(
        run_dir / "candidate.json",
        {
            "name": prompt_name,
            "prompts": candidate,
        },
    )

    adapter = HotpotAdapter(
        program=program,
        metric_fn=answer_exact_match,
        runtime_config={
            "task_model": args.task_model,
            "task_api_base": args.task_api_base,
            "task_temperature": args.task_temperature,
            "task_max_tokens": args.task_max_tokens,
            "retriever_dir": args.retriever_dir,
            "k": args.k,
        },
    )

    runtime = OursRuntime(
        cache_dir=args.cache_dir,
        cache_enabled=not args.no_cache,
    )

    if args.mode == "smoke":
        run_smoke(
            runtime=runtime,
            adapter=adapter,
            dataset=dataset,
            candidate=candidate,
            sample_index=args.sample_index,
            run_dir=run_dir,
        )
        return

    run_eval(
        runtime=runtime,
        adapter=adapter,
        dataset=dataset,
        candidate=candidate,
        run_dir=run_dir,
        num_threads=args.num_threads,
    )


if __name__ == "__main__":
    main()
