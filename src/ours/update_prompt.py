# /home/jinwoo/gepa-official/src/ours/update_prompt.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ours.utils.prompt_update import CONDITIONS
from ours.utils.update_pipeline import (
    BATCH_SELECTIONS,
    DEFAULT_AGENT_BATCH_SIZE,
    DEFAULT_ATTRIBUTE_ROWS,
    DEFAULT_CACHE_DIR,
    DEFAULT_ENV_FILE,
    DEFAULT_EVAL_ROWS,
    DEFAULT_NUM_FEEDBACK_CANDIDATES,
    DEFAULT_RUN_DIR,
    run_update_pipeline,
)

from examples.ours.retriever import DEFAULT_RETRIEVER_DIR


def _json_dumps(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        default=str,
        sort_keys=False,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build and evaluate exactly one multi-agent "
            "positive-safety prompt-update condition."
        )
    )

    parser.add_argument(
        "--condition",
        choices=CONDITIONS,
        required=True,
        help="Run exactly one prompt-update condition.",
    )
    parser.add_argument(
        "--eval-rows",
        default=DEFAULT_EVAL_ROWS,
    )
    parser.add_argument(
        "--source-eval-rows",
        default=None,
        help=(
            "Optional original flat eval_rows JSON used to supplement "
            "nested update_prompt eval_rows.jsonl traces."
        ),
    )
    parser.add_argument(
        "--base-candidate-path",
        default=None,
        help=(
            "Optional candidate.json from the previous iteration. "
            "If omitted, BASELINE_PROMPT_SET is used."
        ),
    )
    parser.add_argument(
        "--attribute-rows",
        default=DEFAULT_ATTRIBUTE_ROWS,
    )
    parser.add_argument(
        "--run-dir",
        default=DEFAULT_RUN_DIR,
        help=(
            "Shared experiment root. Condition-specific "
            "outputs are written under conditions/<condition>."
        ),
    )
    parser.add_argument(
        "--cache-dir",
        default=DEFAULT_CACHE_DIR,
    )
    parser.add_argument(
        "--env-file",
        default=DEFAULT_ENV_FILE,
    )
    parser.add_argument(
        "--retriever-dir",
        default=DEFAULT_RETRIEVER_DIR,
    )
    parser.add_argument("--k", type=int, default=7)

    parser.add_argument(
        "--model",
        default="openai/gpt-5-mini",
    )
    parser.add_argument(
        "--api-base",
        default="https://api.openai.com/v1",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=1.0,
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=16000,
    )

    parser.add_argument(
        "--batch-selection",
        choices=BATCH_SELECTIONS,
        default="random",
    )
    parser.add_argument(
        "--batch-size-final",
        type=int,
        default=DEFAULT_AGENT_BATCH_SIZE,
    )
    parser.add_argument(
        "--batch-size-summary2",
        type=int,
        default=DEFAULT_AGENT_BATCH_SIZE,
    )
    parser.add_argument(
        "--batch-size-query",
        type=int,
        default=DEFAULT_AGENT_BATCH_SIZE,
    )
    parser.add_argument(
        "--batch-size-summary1",
        type=int,
        default=DEFAULT_AGENT_BATCH_SIZE,
    )
    parser.add_argument(
        "--c-per-agent",
        type=int,
        default=5,
        help=(
            "Number of correct C rows assigned to each "
            "agent that has at least one selected W row."
        ),
    )
    parser.add_argument(
        "--num-feedback-candidates",
        type=int,
        default=DEFAULT_NUM_FEEDBACK_CANDIDATES,
        help=(
            "Number of distinct admissible integrated-feedback delta-p "
            "candidates generated per updated agent before the "
            "agent-specific minimum semantic-norm 1-to-N selection. "
            "Must be at least 2."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--delta-attempts",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--damage-attempts",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--max-evidence-chars",
        type=int,
        default=120000,
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        default=8,
    )
    parser.add_argument(
        "--limit-eval",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--skip-eval",
        action="store_true",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Replace only the selected condition's candidate, "
            "updater rows, and evaluation outputs."
        ),
    )
    parser.add_argument(
        "--overwrite-shared",
        action="store_true",
        help=(
            "Recreate the shared batch manifest and regenerate "
            "the selected C-side match/material rows."
        ),
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_update_pipeline(
        args,
        entrypoint_path=Path(__file__).resolve(),
    )
    print(_json_dumps(result))


if __name__ == "__main__":
    main()