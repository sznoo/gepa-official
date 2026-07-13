#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import dspy
from tqdm.auto import tqdm

from ours.attribute import (
    AGENT_ORDER,
    AttributionConfig,
    AttributionRunner,
    summarize_endpoint_attempts,
    summarize_midpoint_attempts,
)
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


def read_json(
    path: str | Path,
) -> Any:
    return json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )


def read_jsonl(
    path: str | Path,
) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def write_json(
    path: str | Path,
    value: Any,
) -> None:
    path = Path(path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )


def append_jsonl(
    path: str | Path,
    row: dict[str, Any],
) -> None:
    path = Path(path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    with path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                row,
                ensure_ascii=False,
                default=str,
            )
            + "\n"
        )


def make_dspy_lm(
    *,
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

    return dspy.LM(
        model,
        **kwargs,
    )


def parse_indices(
    text: str | None,
) -> list[int] | None:
    if text is None:
        return None

    values = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        values.append(int(part))

    return values


def parse_agents(
    text: str,
) -> list[str]:
    agents = [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]

    invalid = [
        agent
        for agent in agents
        if agent not in AGENT_ORDER
    ]
    if invalid:
        raise ValueError(
            f"Unknown agents: {invalid}. "
            f"Expected subset of {AGENT_ORDER}."
        )

    return agents


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--phase",
        choices=[
            "endpoint",
            "midpoint",
            "all",
        ],
        default="all",
    )

    parser.add_argument(
        "--split",
        choices=[
            "train",
            "val",
            "test",
        ],
        default="test",
    )
    parser.add_argument(
        "--train-size",
        type=int,
        default=150,
    )
    parser.add_argument(
        "--val-size",
        type=int,
        default=150,
    )
    parser.add_argument(
        "--test-size",
        type=int,
        default=150,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--indices",
        default=None,
        help=(
            "Comma-separated dataset indices. "
            "Uses the split prefix when omitted."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--agents",
        default="final,summary2,query,summary1",
    )

    parser.add_argument(
        "--retriever-dir",
        default=os.environ.get(
            "HOTPOT_RETRIEVER_DIR",
            DEFAULT_RETRIEVER_DIR,
        ),
    )
    parser.add_argument(
        "--k",
        type=int,
        default=7,
    )

    parser.add_argument(
        "--task-model",
        default=os.environ.get(
            "TASK_MODEL",
            "openai/gpt-5-mini",
        ),
    )
    parser.add_argument(
        "--task-api-base",
        default=os.environ.get(
            "TASK_API_BASE",
            "https://api.openai.com/v1",
        ),
    )
    parser.add_argument(
        "--task-api-key",
        default=os.environ.get(
            "TASK_API_KEY",
            os.environ.get(
                "OPENAI_API_KEY",
                "",
            ),
        ),
    )
    parser.add_argument(
        "--task-temperature",
        type=float,
        default=1.0,
    )
    parser.add_argument(
        "--task-max-tokens",
        type=int,
        default=16000,
    )

    parser.add_argument(
        "--reflection-model",
        default=os.environ.get(
            "REFLECTION_MODEL",
            "openai/gpt-5-mini",
        ),
    )
    parser.add_argument(
        "--reflection-api-base",
        default=os.environ.get(
            "REFLECTION_API_BASE",
            "https://api.openai.com/v1",
        ),
    )
    parser.add_argument(
        "--reflection-api-key",
        default=os.environ.get(
            "REFLECTION_API_KEY",
            os.environ.get(
                "OPENAI_API_KEY",
                "",
            ),
        ),
    )
    parser.add_argument(
        "--reflection-temperature",
        type=float,
        default=1.0,
    )
    parser.add_argument(
        "--reflection-max-tokens",
        type=int,
        default=16000,
    )

    parser.add_argument(
        "--prompt-json",
        default=None,
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        help=(
            "Run directory containing the atomic bank "
            "and attribution outputs."
        ),
    )
    parser.add_argument(
        "--cache-dir",
        default="examples/ours/cache/attribute",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
    )

    parser.add_argument(
        "--reference-limit",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--max-midpoint-depth",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--max-midpoint-nodes",
        type=int,
        default=31,
    )
    parser.add_argument(
        "--no-midpoint-verification",
        action="store_true",
    )

    parser.add_argument(
        "--overwrite-attribution",
        action="store_true",
    )

    return parser.parse_args()


def resolve_dataset(
    *,
    split: str,
    trainset,
    valset,
    testset,
):
    return {
        "train": trainset,
        "val": valset,
        "test": testset,
    }[split]


def select_indices(
    *,
    dataset_size: int,
    explicit: list[int] | None,
    limit: int | None,
) -> list[int]:
    if explicit is None:
        indices = list(
            range(dataset_size)
        )
    else:
        indices = list(explicit)

    for index in indices:
        if (
            index < 0
            or index >= dataset_size
        ):
            raise IndexError(
                f"Dataset index {index} is out of "
                f"range for size {dataset_size}."
            )

    if limit is not None:
        if limit < 0:
            raise ValueError(
                "--limit must be non-negative."
            )
        indices = indices[:limit]

    return indices


def main():
    args = parse_args()

    run_dir = Path(args.run_dir)
    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    attribution_dir = (
        run_dir / "attribution"
    )
    attribution_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    endpoint_path = (
        attribution_dir
        / "endpoint_attempts.jsonl"
    )
    failure_path = (
        attribution_dir
        / "endpoint_failures.jsonl"
    )
    midpoint_path = (
        attribution_dir
        / "midpoint_attempts.jsonl"
    )
    summary_path = (
        attribution_dir / "summary.json"
    )

    if args.overwrite_attribution:
        for path in (
            endpoint_path,
            failure_path,
            midpoint_path,
            summary_path,
        ):
            if path.exists():
                path.unlink()

    if not args.task_api_key:
        raise EnvironmentError(
            "Task API key is empty."
        )
    if not args.reflection_api_key:
        raise EnvironmentError(
            "Reflection API key is empty."
        )

    task_lm = make_dspy_lm(
        model=args.task_model,
        api_base=args.task_api_base,
        api_key=args.task_api_key,
        temperature=args.task_temperature,
        max_tokens=args.task_max_tokens,
    )
    dspy.configure(lm=task_lm)

    reflection_lm = make_dspy_lm(
        model=args.reflection_model,
        api_base=args.reflection_api_base,
        api_key=args.reflection_api_key,
        temperature=(
            args.reflection_temperature
        ),
        max_tokens=(
            args.reflection_max_tokens
        ),
    )

    reflection_lm_config = {
        "model": args.reflection_model,
        "api_base": (
            args.reflection_api_base
        ),
        "temperature": (
            args.reflection_temperature
        ),
        "max_tokens": (
            args.reflection_max_tokens
        ),
    }

    set_retriever_dir(
        args.retriever_dir
    )

    trainset, valset, testset = (
        load_hotpot_splits(
            train_size=args.train_size,
            val_size=args.val_size,
            test_size=args.test_size,
            seed=args.seed,
        )
    )
    dataset = resolve_dataset(
        split=args.split,
        trainset=trainset,
        valset=valset,
        testset=testset,
    )

    indices = select_indices(
        dataset_size=len(dataset),
        explicit=parse_indices(
            args.indices
        ),
        limit=args.limit,
    )
    agents = parse_agents(
        args.agents
    )

    program = HotpotMultiHop(
        k=args.k,
        retriever_dir=args.retriever_dir,
    )

    if args.prompt_json:
        prompt_name, candidate = (
            load_prompt_candidate(
                args.prompt_json,
                program=program,
            )
        )
    else:
        prompt_name = "baseline"
        candidate = build_seed_candidate(
            program
        )

    adapter = HotpotAdapter(
        program=program,
        metric_fn=answer_exact_match,
        runtime_config={
            "task_model": args.task_model,
            "task_api_base": (
                args.task_api_base
            ),
            "task_temperature": (
                args.task_temperature
            ),
            "task_max_tokens": (
                args.task_max_tokens
            ),
            "retriever_dir": (
                args.retriever_dir
            ),
            "k": args.k,
        },
    )

    runtime = OursRuntime(
        cache_dir=args.cache_dir,
        cache_enabled=(
            not args.no_cache
        ),
    )

    runner = AttributionRunner(
        runtime=runtime,
        adapter=adapter,
        candidate=candidate,
        reflection_lm=reflection_lm,
        reflection_lm_config=(
            reflection_lm_config
        ),
        config=AttributionConfig(
            run_dir=str(run_dir),
            reference_limit=(
                args.reference_limit
            ),
            max_midpoint_depth=(
                args.max_midpoint_depth
            ),
            max_midpoint_nodes=(
                args.max_midpoint_nodes
            ),
            verify_midpoints=(
                not args.no_midpoint_verification
            ),
        ),
    )

    write_json(
        attribution_dir
        / "config.json",
        {
            "phase": args.phase,
            "split": args.split,
            "indices": indices,
            "agents": agents,
            "prompt_name": prompt_name,
            "candidate": candidate,
            "task_lm": {
                "model": args.task_model,
                "api_base": (
                    args.task_api_base
                ),
                "temperature": (
                    args.task_temperature
                ),
                "max_tokens": (
                    args.task_max_tokens
                ),
            },
            "reflection_lm": (
                reflection_lm_config
            ),
            "retriever_dir": (
                args.retriever_dir
            ),
            "k": args.k,
            "reference_limit": (
                args.reference_limit
            ),
            "max_midpoint_depth": (
                args.max_midpoint_depth
            ),
            "max_midpoint_nodes": (
                args.max_midpoint_nodes
            ),
        },
    )

    if args.phase in {
        "endpoint",
        "all",
    }:
        existing_endpoint = (
            read_jsonl(endpoint_path)
        )
        done = {
            (
                int(row["sample_index"]),
                str(row["agent"]),
            )
            for row in existing_endpoint
            if (
                row.get("sample_index")
                is not None
                and row.get("agent")
            )
        }

        total = len(indices) * len(agents)

        with tqdm(
            total=total,
            desc="Endpoint attribution",
            unit="edge",
            dynamic_ncols=True,
        ) as progress:
            for sample_index in indices:
                example = dataset[
                    sample_index
                ]

                baseline_trace, _ = (
                    runtime.forward(
                        adapter=adapter,
                        example=example,
                        candidate=candidate,
                        return_cache_hit=True,
                    )
                )

                for agent in agents:
                    key = (
                        sample_index,
                        agent,
                    )

                    if key in done:
                        progress.update(1)
                        continue

                    row = (
                        runner
                        .attribute_endpoint_safe(
                            example=example,
                            baseline_trace=(
                                baseline_trace
                            ),
                            agent=agent,
                            sample_index=(
                                sample_index
                            ),
                        )
                    )

                    append_jsonl(
                        endpoint_path,
                        row,
                    )

                    if (
                        not row.get("error")
                        and (
                            row.get(
                                "atomicity"
                            )
                            or {}
                        ).get("is_atomic")
                        is not True
                    ):
                        append_jsonl(
                            failure_path,
                            row,
                        )

                    progress.update(1)
                    progress.set_postfix(
                        agent=agent,
                        atomic=(
                            (
                                row.get(
                                    "atomicity"
                                )
                                or {}
                            ).get(
                                "is_atomic"
                            )
                        ),
                        refresh=False,
                    )

    if args.phase in {
        "midpoint",
        "all",
    }:
        failure_rows = read_jsonl(
            failure_path
        )
        existing_midpoint = read_jsonl(
            midpoint_path
        )
        done_midpoint = {
            (
                int(row["sample_index"]),
                str(row["agent"]),
            )
            for row in existing_midpoint
            if (
                row.get("sample_index")
                is not None
                and row.get("agent")
            )
        }

        pending = [
            row
            for row in failure_rows
            if (
                int(row["sample_index"]),
                str(row["agent"]),
            )
            not in done_midpoint
        ]

        for failure in tqdm(
            pending,
            desc="Midpoint decomposition",
            unit="edge",
            dynamic_ncols=True,
        ):
            result = (
                runner
                .decompose_failed_endpoint_safe(
                    failure_record=failure
                )
            )
            append_jsonl(
                midpoint_path,
                result,
            )

    endpoint_rows = read_jsonl(
        endpoint_path
    )
    midpoint_rows = read_jsonl(
        midpoint_path
    )

    summary = {
        "phase": args.phase,
        "split": args.split,
        "indices": indices,
        "agents": agents,
        "endpoint": (
            summarize_endpoint_attempts(
                endpoint_rows
            )
        ),
        "midpoint": (
            summarize_midpoint_attempts(
                midpoint_rows
            )
        ),
        "paths": {
            "endpoint_attempts": str(
                endpoint_path
            ),
            "endpoint_failures": str(
                failure_path
            ),
            "midpoint_attempts": str(
                midpoint_path
            ),
            "atomic_bank": str(
                run_dir
                / "atomic_bank.jsonl"
            ),
        },
    }

    write_json(
        summary_path,
        summary,
    )

    print(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()