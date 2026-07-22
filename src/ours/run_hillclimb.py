#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from dotenv import dotenv_values

from ours.analyze_attribute import load_candidate_file
from ours.prompts import BASELINE_PROMPT_SET
from ours.utils.prompt_update import CONDITIONS


SCRIPT_VERSION = "2026-07-17-v4-retriever-and-vllm-token-guards"


def _json_dumps(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        default=str,
        sort_keys=False,
    )


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def _read_rows_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        value = [
            json.loads(line)
            for line in text.splitlines()
            if line.strip()
        ]

    if isinstance(value, Mapping):
        rows = value.get("rows")
        value = rows if isinstance(rows, list) else [value]

    if not isinstance(value, list):
        raise TypeError(f"{path} must contain a JSON list or JSONL rows.")
    if not all(isinstance(row, Mapping) for row in value):
        raise TypeError(f"{path} contains a non-object row.")
    return [dict(row) for row in value]


def _is_nonstring_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    )


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if _is_nonstring_sequence(value):
        return list(value)
    return [value]


def _normalize_sentences(value: Any) -> list[str]:
    return [
        str(item)
        for item in _as_list(value)
        if str(item or "").strip()
    ]


def _normalize_context(context: Any, *, position: int) -> dict[str, Any]:
    """Normalize Hotpot context to datasets-style dict-of-lists."""
    if isinstance(context, Mapping):
        if "title" in context and "sentences" in context:
            titles = _as_list(context.get("title"))
            sentences = _as_list(context.get("sentences"))
        else:
            # Also accept {title: [sentences]} mappings.
            titles = list(context.keys())
            sentences = list(context.values())
    elif _is_nonstring_sequence(context):
        titles = []
        sentences = []
        for item_index, item in enumerate(context):
            if isinstance(item, Mapping):
                title = item.get("title")
                sentence_value = item.get(
                    "sentences",
                    item.get("sentence", item.get("text")),
                )
            elif _is_nonstring_sequence(item) and len(item) >= 2:
                title = item[0]
                sentence_value = item[1]
            else:
                raise TypeError(
                    "Unsupported context item at "
                    f"row={position}, item={item_index}: {type(item).__name__}"
                )
            titles.append(title)
            sentences.append(sentence_value)
    else:
        raise TypeError(
            "Evaluation row context must be a mapping or list of pairs at "
            f"position {position}; got {type(context).__name__}."
        )

    if len(titles) != len(sentences):
        raise ValueError(
            "Context title/sentences length mismatch at "
            f"position {position}: titles={len(titles)}, "
            f"sentences={len(sentences)}."
        )

    normalized_titles = [str(title or "").strip() for title in titles]
    if any(not title for title in normalized_titles):
        raise ValueError(f"Context contains an empty title at position {position}.")

    return {
        "title": normalized_titles,
        "sentences": [
            _normalize_sentences(sentence_value)
            for sentence_value in sentences
        ],
    }


def _normalize_supporting_facts(
    supporting_facts: Any,
    *,
    position: int,
) -> dict[str, Any]:
    """Normalize Hotpot supporting facts to datasets-style dict-of-lists."""
    if isinstance(supporting_facts, Mapping):
        titles = _as_list(
            supporting_facts.get(
                "title",
                supporting_facts.get("titles"),
            )
        )
        sent_ids = _as_list(
            supporting_facts.get(
                "sent_id",
                supporting_facts.get(
                    "sent_ids",
                    supporting_facts.get("sentence_id"),
                ),
            )
        )
    elif _is_nonstring_sequence(supporting_facts):
        titles = []
        sent_ids = []
        for item_index, item in enumerate(supporting_facts):
            if isinstance(item, Mapping):
                title = item.get("title")
                sent_id = item.get(
                    "sent_id",
                    item.get("sentence_id", item.get("id")),
                )
            elif _is_nonstring_sequence(item) and len(item) >= 2:
                title = item[0]
                sent_id = item[1]
            else:
                raise TypeError(
                    "Unsupported supporting_facts item at "
                    f"row={position}, item={item_index}: "
                    f"{type(item).__name__}"
                )
            titles.append(title)
            sent_ids.append(sent_id)
    else:
        raise TypeError(
            "Evaluation row supporting_facts must be a mapping or list of "
            f"pairs at position {position}; got "
            f"{type(supporting_facts).__name__}."
        )

    if len(titles) != len(sent_ids):
        raise ValueError(
            "Supporting-fact title/sent_id length mismatch at "
            f"position {position}: titles={len(titles)}, "
            f"sent_ids={len(sent_ids)}."
        )

    normalized_titles = [str(title or "").strip() for title in titles]
    if any(not title for title in normalized_titles):
        raise ValueError(
            f"Supporting facts contain an empty title at position {position}."
        )

    normalized_sent_ids: list[int] = []
    for sent_id in sent_ids:
        try:
            normalized_sent_ids.append(int(sent_id))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Supporting facts contain a non-integer sent_id at "
                f"position {position}: {sent_id!r}."
            ) from exc

    return {
        "title": normalized_titles,
        "sent_id": normalized_sent_ids,
    }


def _support_titles(supporting_facts: Any) -> list[str]:
    if isinstance(supporting_facts, Mapping):
        values = _as_list(
            supporting_facts.get(
                "title",
                supporting_facts.get("titles"),
            )
        )
        return list(dict.fromkeys(
            str(value).strip()
            for value in values
            if str(value or "").strip()
        ))

    titles: list[str] = []
    seen: set[str] = set()
    for item in supporting_facts or []:
        title: Any = None
        if isinstance(item, Mapping):
            title = item.get("title")
        elif _is_nonstring_sequence(item) and item:
            title = item[0]

        text = str(title or "").strip()
        if text and text not in seen:
            seen.add(text)
            titles.append(text)
    return titles

def _ensure_normalized_source_rows(
    *,
    source_path: Path,
    output_path: Path,
) -> Path:
    source_hash = _file_hash(source_path)
    metadata_path = output_path.with_suffix(output_path.suffix + ".meta.json")

    if output_path.exists() and metadata_path.exists():
        metadata = _read_json(metadata_path)
        if (
            metadata.get("source_hash") == source_hash
            and metadata.get("normalization_version") == SCRIPT_VERSION
        ):
            return output_path

    rows = _read_rows_file(source_path)
    normalized: list[dict[str, Any]] = []

    for position, source_row in enumerate(rows):
        row = dict(source_row)

        if row.get("gold_answer") is None:
            if row.get("answer") is not None:
                row["gold_answer"] = row["answer"]
            elif row.get("answer_gold") is not None:
                row["gold_answer"] = row["answer_gold"]
            else:
                raise ValueError(
                    "Source row is missing gold_answer/answer at "
                    f"position {position}: {source_path}"
                )

        row["context"] = _normalize_context(
            row.get("context"),
            position=position,
        )
        row["supporting_facts"] = _normalize_supporting_facts(
            row.get("supporting_facts"),
            position=position,
        )

        row.setdefault("index", position)
        if row.get("sample_id") in {None, ""}:
            for key in ("_id", "id"):
                if row.get(key) not in {None, ""}:
                    row["sample_id"] = row[key]
                    break

        if row.get("gold_support_titles") is None:
            titles = _support_titles(row.get("supporting_facts"))
            if titles:
                row["gold_support_titles"] = titles

        normalized.append(row)

    _write_jsonl(output_path, normalized)
    _write_json(
        metadata_path,
        {
            "normalization_version": SCRIPT_VERSION,
            "source_path": str(source_path),
            "source_hash": source_hash,
            "num_rows": len(normalized),
            "context_format": "dict_of_lists",
            "supporting_facts_format": "dict_of_lists",
        },
    )
    print(
        "[hillclimb] normalized source rows | "
        f"source={source_path} output={output_path} n={len(normalized)}",
        flush=True,
    )
    return output_path


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(_json_dumps(value), encoding="utf-8")
    tmp.replace(path)


def _write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(dict(row), ensure_ascii=False, default=str) + "\n")
    tmp.replace(path)


def _write_candidate(
    path: Path,
    *,
    name: str,
    candidate: Mapping[str, str],
    description: str,
) -> None:
    _write_json(
        path,
        {
            "candidate_name": name,
            "description": description,
            "candidate": dict(candidate),
        },
    )


def _copy_candidate(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _candidate_hash(path: Path) -> str:
    candidate, _ = load_candidate_file(path)
    return _canonical_hash(candidate)


def _command_env(env_file: Path) -> dict[str, str]:
    env = dict(os.environ)
    for key, value in dotenv_values(env_file).items():
        if value is not None:
            env[str(key)] = str(value)
    if not env.get("OPENAI_API_KEY", "").strip():
        raise EnvironmentError(
            f"OPENAI_API_KEY is missing from {env_file}."
        )
    return env


def _run(command: Sequence[str], *, cwd: Path, env: Mapping[str, str]) -> None:
    print(f"[hillclimb] run | {shlex.join(list(command))}", flush=True)
    subprocess.run(
        list(command),
        cwd=cwd,
        env=dict(env),
        check=True,
    )


def _require_complete_summary(path: Path) -> dict[str, Any]:
    summary = _read_json(path)
    if summary.get("complete") is not True:
        eval_path = path.with_name("eval_rows.jsonl")
        error_rows = [
            row
            for row in _read_jsonl(eval_path)
            if row.get("error")
        ]
        error_counts = Counter(
            (
                str(row.get("error_type") or "UnknownError"),
                str(row.get("error_message") or ""),
            )
            for row in error_rows
        )
        top_errors = [
            {
                "count": count,
                "error_type": error_type,
                "error_message": error_message,
            }
            for (error_type, error_message), count
            in error_counts.most_common(3)
        ]
        raise RuntimeError(
            f"Incomplete evaluation at {path}: "
            f"n_ok={summary.get('n_ok')} "
            f"n_expected={summary.get('n_expected')} "
            f"n_error_rows={len(error_rows)} "
            f"top_errors={top_errors}"
        )
    return dict(summary)


def _eval_paths(eval_root: Path) -> tuple[Path, Path]:
    condition_dir = eval_root / "conditions" / "base"
    return (
        condition_dir / "eval_rows.jsonl",
        condition_dir / "summary.json",
    )


def _ensure_evaluation(
    *,
    repo_root: Path,
    update_script: Path,
    env: Mapping[str, str],
    candidate_path: Path,
    source_rows: Path,
    eval_root: Path,
    cache_dir: Path,
    args: argparse.Namespace,
    limit_eval: int | None,
) -> tuple[Path, dict[str, Any]]:
    eval_rows_path, summary_path = _eval_paths(eval_root)
    candidate_hash = _candidate_hash(candidate_path)

    if summary_path.exists():
        summary = _read_json(summary_path)
        if (
            summary.get("complete") is True
            and str(summary.get("candidate_hash")) == candidate_hash
        ):
            return eval_rows_path, dict(summary)

    command = [
        sys.executable,
        str(update_script),
        "--condition",
        "base",
        "--eval-rows",
        str(source_rows),
        "--base-candidate-path",
        str(candidate_path),
        "--run-dir",
        str(eval_root),
        "--cache-dir",
        str(cache_dir),
        "--env-file",
        str(args.env_file),
        "--retriever-dir",
        str(args.retriever_dir),
        "--k",
        str(args.k),
        "--model",
        args.model,
        "--api-base",
        args.api_base,
        "--temperature",
        str(args.temperature),
        "--max-tokens",
        str(args.eval_max_tokens),
        "--num-threads",
        str(args.num_threads),
    ]
    if limit_eval is not None:
        command += ["--limit-eval", str(limit_eval)]
    if args.no_cache:
        command.append("--no-cache")

    _run(command, cwd=repo_root, env=env)
    return eval_rows_path, _require_complete_summary(summary_path)


def _ensure_attribution(
    *,
    repo_root: Path,
    attribute_script: Path,
    env: Mapping[str, str],
    candidate_path: Path,
    source_rows: Path,
    train_eval_rows: Path,
    attribution_dir: Path,
    cache_dir: Path,
    args: argparse.Namespace,
) -> tuple[Path, dict[str, Any]]:
    attribute_rows_path = attribution_dir / "attribute_rows.jsonl"
    summary_path = attribution_dir / "summary.json"
    config_path = attribution_dir / "config.json"
    candidate_hash = _candidate_hash(candidate_path)

    if summary_path.exists() and config_path.exists():
        config = _read_json(config_path)
        if str(config.get("candidate_hash")) == candidate_hash:
            return attribute_rows_path, dict(_read_json(summary_path))

    command = [
        sys.executable,
        str(attribute_script),
        "--eval-rows",
        str(train_eval_rows),
        "--source-eval-rows",
        str(source_rows),
        "--candidate-path",
        str(candidate_path),
        "--run-dir",
        str(attribution_dir),
        "--cache-dir",
        str(cache_dir),
        "--env-file",
        str(args.env_file),
        "--retriever-dir",
        str(args.retriever_dir),
        "--k",
        str(args.k),
        "--model",
        args.model,
        "--api-base",
        args.api_base,
        "--temperature",
        str(args.temperature),
        "--max-tokens",
        str(args.attribution_max_tokens),
        "--final-max-iter",
        str(args.final_max_iter),
        "--summary2-max-iter",
        str(args.summary2_max_iter),
        "--query-max-iter",
        str(args.query_max_iter),
        "--summary1-max-iter",
        str(args.summary1_max_iter),
        "--delta-attempts",
        str(args.delta_attempts),
        "--num-threads",
        str(args.num_threads),
    ]
    if args.no_cache:
        command.append("--no-cache")
    if args.no_verbose_attribution:
        command.append("--no-verbose")

    _run(command, cwd=repo_root, env=env)
    return attribute_rows_path, dict(_read_json(summary_path))


def _ensure_proposal(
    *,
    repo_root: Path,
    update_script: Path,
    env: Mapping[str, str],
    source_candidate: Path,
    source_rows: Path,
    train_eval_rows: Path,
    attribute_rows: Path,
    update_root: Path,
    cache_dir: Path,
    iteration_seed: int,
    args: argparse.Namespace,
) -> Path:
    proposal_path = (
        update_root
        / "conditions"
        / args.condition
        / "candidate.json"
    )
    if proposal_path.exists():
        return proposal_path

    command = [
        sys.executable,
        str(update_script),
        "--condition",
        args.condition,
        "--eval-rows",
        str(train_eval_rows),
        "--source-eval-rows",
        str(source_rows),
        "--base-candidate-path",
        str(source_candidate),
        "--attribute-rows",
        str(attribute_rows),
        "--run-dir",
        str(update_root),
        "--cache-dir",
        str(cache_dir),
        "--env-file",
        str(args.env_file),
        "--retriever-dir",
        str(args.retriever_dir),
        "--k",
        str(args.k),
        "--model",
        args.model,
        "--api-base",
        args.api_base,
        "--temperature",
        str(args.temperature),
        "--max-tokens",
        str(args.update_max_tokens),
        "--batch-selection",
        args.batch_selection,
        "--batch-size-final",
        str(args.batch_size_final),
        "--batch-size-summary2",
        str(args.batch_size_summary2),
        "--batch-size-query",
        str(args.batch_size_query),
        "--batch-size-summary1",
        str(args.batch_size_summary1),
        "--c-per-agent",
        str(args.c_per_agent),
        "--num-feedback-candidates",
        str(args.num_feedback_candidates),
        "--seed",
        str(iteration_seed),
        "--delta-attempts",
        str(args.delta_attempts),
        "--damage-attempts",
        str(args.damage_attempts),
        "--max-evidence-chars",
        str(args.max_evidence_chars),
        "--num-threads",
        str(args.num_threads),
        "--skip-eval",
    ]
    if args.no_cache:
        command.append("--no-cache")

    _run(command, cwd=repo_root, env=env)
    if not proposal_path.exists():
        raise FileNotFoundError(
            f"Prompt update completed without producing {proposal_path}."
        )
    return proposal_path


def _compare_eval_rows(
    previous_path: Path,
    proposal_path: Path,
) -> dict[str, int]:
    previous = {
        int(row["eval_position"]): float(row["score"])
        for row in _read_jsonl(previous_path)
        if not row.get("error")
    }
    proposal = {
        int(row["eval_position"]): float(row["score"])
        for row in _read_jsonl(proposal_path)
        if not row.get("error")
    }

    flips = {
        "W_to_R": 0,
        "R_to_W": 0,
        "stable_R": 0,
        "stable_W": 0,
        "paired": 0,
    }
    for position in sorted(set(previous) & set(proposal)):
        flips["paired"] += 1
        was_correct = previous[position] == 1.0
        now_correct = proposal[position] == 1.0
        if not was_correct and now_correct:
            flips["W_to_R"] += 1
        elif was_correct and not now_correct:
            flips["R_to_W"] += 1
        elif was_correct:
            flips["stable_R"] += 1
        else:
            flips["stable_W"] += 1
    flips["net_flip"] = flips["W_to_R"] - flips["R_to_W"]
    return flips


def _rebuild_history(run_dir: Path) -> None:
    decisions = []
    iteration_root = run_dir / "iterations"
    if iteration_root.exists():
        for path in sorted(iteration_root.glob("iter_*/decision.json")):
            decisions.append(_read_json(path))
    _write_jsonl(run_dir / "history.jsonl", decisions)


def _apply_decision(state: dict[str, Any], decision: Mapping[str, Any]) -> None:
    if decision.get("accepted") is True:
        state["best_candidate_hash"] = decision["proposal_candidate_hash"]
        state["best_val_score"] = decision["proposal_val_score"]
        state["best_val_num_correct"] = decision["proposal_val_num_correct"]
        state["best_val_eval_rows"] = decision["proposal_val_eval_rows"]
    state["next_iteration"] = int(decision["iteration"]) + 1
    if decision.get("stop_reason"):
        state["stop_reason"] = decision["stop_reason"]


def _static_config(args: argparse.Namespace, initial_hash: str) -> dict[str, Any]:
    return {
        "script_version": SCRIPT_VERSION,
        "train_rows": str(args.train_rows),
        "train_rows_hash": _file_hash(args.train_rows),
        "val_rows": str(args.val_rows),
        "val_rows_hash": _file_hash(args.val_rows),
        "test_rows": str(args.test_rows),
        "test_rows_hash": _file_hash(args.test_rows),
        "initial_candidate_hash": initial_hash,
        "condition": args.condition,
        "max_iters": args.max_iters,
        "batch_selection": args.batch_selection,
        "batch_sizes": {
            "final": args.batch_size_final,
            "summary2": args.batch_size_summary2,
            "query": args.batch_size_query,
            "summary1": args.batch_size_summary1,
        },
        "c_per_agent": args.c_per_agent,
        "num_feedback_candidates": args.num_feedback_candidates,
        "seed": args.seed,
        "agent_max_iters": {
            "final": args.final_max_iter,
            "summary2": args.summary2_max_iter,
            "query": args.query_max_iter,
            "summary1": args.summary1_max_iter,
        },
        "delta_attempts": args.delta_attempts,
        "damage_attempts": args.damage_attempts,
        "max_evidence_chars": args.max_evidence_chars,
        "model": args.model,
        "api_base": args.api_base,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "stage_max_tokens": {
            "evaluation": args.eval_max_tokens,
            "attribution": args.attribution_max_tokens,
            "update": args.update_max_tokens,
        },
        "retriever_dir": str(args.retriever_dir),
        "k": args.k,
        "limit_train": args.limit_train,
        "limit_val": args.limit_val,
        "limit_test": args.limit_test,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Iterative train attribution -> prompt proposal -> validation "
            "hill climb, followed by one final test evaluation."
        )
    )
    parser.add_argument("--train-rows", type=Path, required=True)
    parser.add_argument("--val-rows", type=Path, required=True)
    parser.add_argument("--test-rows", type=Path, required=True)
    parser.add_argument("--initial-candidate-path", type=Path, default=None)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--max-iters", type=int, required=True)

    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path("/home/jinwoo/gepa-official/.env"),
    )
    parser.add_argument(
        "--retriever-dir",
        type=Path,
        default=Path("examples/ours"),
    )
    parser.add_argument("--k", type=int, default=7)
    parser.add_argument("--model", default="openai/gpt-5-mini")
    parser.add_argument("--api-base", default="https://api.openai.com/v1")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=16000)
    parser.add_argument("--eval-max-tokens", type=int, default=None)
    parser.add_argument("--attribution-max-tokens", type=int, default=None)
    parser.add_argument("--update-max-tokens", type=int, default=None)
    parser.add_argument("--num-threads", type=int, default=8)

    parser.add_argument(
        "--batch-selection",
        choices=("random", "min_distance"),
        default="min_distance",
    )
    parser.add_argument("--batch-size-final", type=int, default=5)
    parser.add_argument("--batch-size-summary2", type=int, default=5)
    parser.add_argument("--batch-size-query", type=int, default=5)
    parser.add_argument("--batch-size-summary1", type=int, default=5)
    parser.add_argument("--c-per-agent", type=int, default=5)
    parser.add_argument("--num-feedback-candidates", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)

    parser.add_argument("--final-max-iter", type=int, default=0)
    parser.add_argument("--summary2-max-iter", type=int, default=0)
    parser.add_argument("--query-max-iter", type=int, default=1)
    parser.add_argument("--summary1-max-iter", type=int, default=1)
    parser.add_argument("--delta-attempts", type=int, default=3)
    parser.add_argument("--damage-attempts", type=int, default=3)
    parser.add_argument("--max-evidence-chars", type=int, default=120000)

    parser.add_argument("--limit-train", type=int, default=None)
    parser.add_argument("--limit-val", type=int, default=None)
    parser.add_argument("--limit-test", type=int, default=None)
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--no-verbose-attribution", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.max_iters < 1:
        raise ValueError("--max-iters must be >= 1.")
    if args.condition == "base":
        raise ValueError("Hill climbing requires a non-base update condition.")

    repo_root = Path(__file__).resolve().parents[2]
    update_script = repo_root / "src" / "ours" / "update_prompt.py"
    attribute_script = repo_root / "src" / "ours" / "analyze_attribute.py"

    args.train_rows = args.train_rows.expanduser().resolve()
    args.val_rows = args.val_rows.expanduser().resolve()
    args.test_rows = args.test_rows.expanduser().resolve()
    args.env_file = args.env_file.expanduser().resolve()
    args.retriever_dir = args.retriever_dir.expanduser().resolve()
    args.run_dir = args.run_dir.expanduser().resolve()

    # Resolve stage-specific output budgets. Qwen served through a local
    # OpenAI-compatible vLLM endpoint commonly uses a 32K context window.
    # Reserving 16K output tokens leaves too little room for matched-C and
    # feedback prompts, so use conservative defaults unless explicitly set.
    model_lower = str(args.model).lower()
    api_base_lower = str(args.api_base).lower()
    is_local_qwen = (
        "qwen" in model_lower
        and "api.openai.com" not in api_base_lower
    )
    if args.eval_max_tokens is None:
        args.eval_max_tokens = min(args.max_tokens, 4096) if is_local_qwen else args.max_tokens
    if args.attribution_max_tokens is None:
        args.attribution_max_tokens = min(args.max_tokens, 8192) if is_local_qwen else args.max_tokens
    if args.update_max_tokens is None:
        args.update_max_tokens = min(args.max_tokens, 8192) if is_local_qwen else args.max_tokens

    for label, value in (
        ("eval", args.eval_max_tokens),
        ("attribution", args.attribution_max_tokens),
        ("update", args.update_max_tokens),
    ):
        if int(value) < 1:
            raise ValueError(f"--{label}-max-tokens must be >= 1.")

    if is_local_qwen:
        print(
            "[hillclimb] local Qwen token budgets | "
            f"eval={args.eval_max_tokens} "
            f"attribution={args.attribution_max_tokens} "
            f"update={args.update_max_tokens}",
            flush=True,
        )
    if args.initial_candidate_path is not None:
        args.initial_candidate_path = (
            args.initial_candidate_path.expanduser().resolve()
        )

    for path in (args.train_rows, args.val_rows, args.test_rows, args.env_file):
        if not path.exists():
            raise FileNotFoundError(path)

    retriever_index = args.retriever_dir / "bm25s_retriever"
    if not retriever_index.exists():
        raise FileNotFoundError(
            "BM25 retriever index not found. --retriever-dir must be the "
            "parent directory containing bm25s_retriever. Expected: "
            f"{retriever_index}"
        )

    if args.overwrite and args.run_dir.exists():
        shutil.rmtree(args.run_dir)
    args.run_dir.mkdir(parents=True, exist_ok=True)

    normalized_root = args.run_dir / "normalized_inputs"
    train_rows = _ensure_normalized_source_rows(
        source_path=args.train_rows,
        output_path=normalized_root / "train.jsonl",
    )
    val_rows = _ensure_normalized_source_rows(
        source_path=args.val_rows,
        output_path=normalized_root / "val.jsonl",
    )
    test_rows = _ensure_normalized_source_rows(
        source_path=args.test_rows,
        output_path=normalized_root / "test.jsonl",
    )

    env = _command_env(args.env_file)
    initial_path = args.run_dir / "initial_candidate.json"
    best_path = args.run_dir / "best" / "candidate.json"

    if not initial_path.exists():
        if args.initial_candidate_path is None:
            _write_candidate(
                initial_path,
                name=str(BASELINE_PROMPT_SET["name"]),
                candidate=dict(BASELINE_PROMPT_SET["prompts"]),
                description="Initial candidate for validation-gated hill climbing.",
            )
        else:
            candidate, candidate_name = load_candidate_file(
                args.initial_candidate_path
            )
            _write_candidate(
                initial_path,
                name=candidate_name,
                candidate=candidate,
                description=(
                    "Normalized initial candidate for validation-gated "
                    "hill climbing."
                ),
            )

    initial_hash = _candidate_hash(initial_path)
    static_config = _static_config(args, initial_hash)
    config_path = args.run_dir / "config.json"
    if config_path.exists():
        existing = _read_json(config_path)
        if existing != static_config:
            raise ValueError(
                "Existing hillclimb config differs from the current request. "
                "Use a new --run-dir or --overwrite."
            )
    else:
        _write_json(config_path, static_config)

    state_path = args.run_dir / "state.json"
    eval_cache = args.run_dir / "cache" / "evaluation"
    attribution_cache = args.run_dir / "cache" / "attribution"
    update_cache = args.run_dir / "cache" / "update"

    if not state_path.exists():
        _copy_candidate(initial_path, best_path)
        initial_val_rows, initial_val_summary = _ensure_evaluation(
            repo_root=repo_root,
            update_script=update_script,
            env=env,
            candidate_path=best_path,
            source_rows=val_rows,
            eval_root=args.run_dir / "initial_validation",
            cache_dir=eval_cache,
            args=args,
            limit_eval=args.limit_val,
        )
        state = {
            "script_version": SCRIPT_VERSION,
            "next_iteration": 0,
            "best_candidate": str(best_path),
            "best_candidate_hash": _candidate_hash(best_path),
            "best_val_score": float(initial_val_summary["score"]),
            "best_val_num_correct": int(initial_val_summary["num_correct"]),
            "best_val_eval_rows": str(initial_val_rows),
            "evaluated_candidates": {
                _candidate_hash(best_path): {
                    "score": float(initial_val_summary["score"]),
                    "num_correct": int(initial_val_summary["num_correct"]),
                    "eval_rows": str(initial_val_rows),
                    "summary": str(
                        args.run_dir
                        / "initial_validation"
                        / "conditions"
                        / "base"
                        / "summary.json"
                    ),
                }
            },
            "stop_reason": None,
            "final_test_complete": False,
        }
        _write_json(state_path, state)
    else:
        state = dict(_read_json(state_path))

    while (
        int(state["next_iteration"]) < args.max_iters
        and not state.get("stop_reason")
    ):
        iteration = int(state["next_iteration"])
        iteration_dir = (
            args.run_dir / "iterations" / f"iter_{iteration:03d}"
        )
        iteration_dir.mkdir(parents=True, exist_ok=True)
        decision_path = iteration_dir / "decision.json"

        if decision_path.exists():
            decision = dict(_read_json(decision_path))
            if decision.get("accepted") is True:
                _copy_candidate(Path(decision["proposal_candidate"]), best_path)
            _apply_decision(state, decision)
            _write_json(state_path, state)
            _rebuild_history(args.run_dir)
            continue

        source_candidate = best_path
        source_hash = _candidate_hash(source_candidate)
        if source_hash != state["best_candidate_hash"]:
            raise RuntimeError("best/candidate.json and state.json disagree.")

        candidate_cache = (
            args.run_dir / "candidate_cache" / source_hash
        )
        train_eval_rows, train_summary = _ensure_evaluation(
            repo_root=repo_root,
            update_script=update_script,
            env=env,
            candidate_path=source_candidate,
            source_rows=train_rows,
            eval_root=candidate_cache / "train_eval",
            cache_dir=eval_cache,
            args=args,
            limit_eval=args.limit_train,
        )

        attribute_rows, attribute_summary = _ensure_attribution(
            repo_root=repo_root,
            attribute_script=attribute_script,
            env=env,
            candidate_path=source_candidate,
            source_rows=train_rows,
            train_eval_rows=train_eval_rows,
            attribution_dir=candidate_cache / "attribution",
            cache_dir=attribution_cache,
            args=args,
        )

        source_record = {
            "iteration": iteration,
            "source_candidate": str(source_candidate),
            "source_candidate_hash": source_hash,
            "train_eval_rows": str(train_eval_rows),
            "train_summary": train_summary,
            "attribute_rows": str(attribute_rows),
            "attribute_summary": attribute_summary,
        }
        _write_json(iteration_dir / "source.json", source_record)

        num_wrong = int(attribute_summary.get("num_wrong_rows_selected", 0))
        num_attributed = int(attribute_summary.get("num_attributed", 0))
        if num_wrong == 0 or num_attributed == 0:
            stop_reason = (
                "no_wrong_train_rows"
                if num_wrong == 0
                else "no_attributed_train_repairs"
            )
            decision = {
                "iteration": iteration,
                "iteration_seed": args.seed + iteration,
                "source_candidate": str(source_candidate),
                "source_candidate_hash": source_hash,
                "proposal_candidate": None,
                "proposal_candidate_hash": None,
                "previous_best_val_score": state["best_val_score"],
                "previous_best_val_num_correct": state[
                    "best_val_num_correct"
                ],
                "proposal_val_score": None,
                "proposal_val_num_correct": None,
                "proposal_val_eval_rows": None,
                "accepted": False,
                "status": stop_reason,
                "stop_reason": stop_reason,
            }
            _write_json(decision_path, decision)
            _apply_decision(state, decision)
            _write_json(state_path, state)
            _rebuild_history(args.run_dir)
            break

        iteration_seed = args.seed + iteration
        proposal_path = _ensure_proposal(
            repo_root=repo_root,
            update_script=update_script,
            env=env,
            source_candidate=source_candidate,
            source_rows=train_rows,
            train_eval_rows=train_eval_rows,
            attribute_rows=attribute_rows,
            update_root=iteration_dir / "update",
            cache_dir=update_cache,
            iteration_seed=iteration_seed,
            args=args,
        )
        proposal_hash = _candidate_hash(proposal_path)

        evaluated = state.setdefault("evaluated_candidates", {})
        if proposal_hash in evaluated:
            proposal_eval = dict(evaluated[proposal_hash])
            proposal_val_rows = Path(proposal_eval["eval_rows"])
            proposal_val_score = float(proposal_eval["score"])
            proposal_val_num_correct = int(proposal_eval["num_correct"])
            validation_status = "reused_candidate_evaluation"
        else:
            proposal_val_rows, proposal_val_summary = _ensure_evaluation(
                repo_root=repo_root,
                update_script=update_script,
                env=env,
                candidate_path=proposal_path,
                source_rows=val_rows,
                eval_root=iteration_dir / "validation",
                cache_dir=eval_cache,
                args=args,
                limit_eval=args.limit_val,
            )
            proposal_val_score = float(proposal_val_summary["score"])
            proposal_val_num_correct = int(
                proposal_val_summary["num_correct"]
            )
            evaluated[proposal_hash] = {
                "score": proposal_val_score,
                "num_correct": proposal_val_num_correct,
                "eval_rows": str(proposal_val_rows),
                "summary": str(
                    iteration_dir
                    / "validation"
                    / "conditions"
                    / "base"
                    / "summary.json"
                ),
            }
            validation_status = "evaluated"

        previous_best_rows = Path(state["best_val_eval_rows"])
        flips = _compare_eval_rows(
            previous_best_rows,
            proposal_val_rows,
        )
        accepted = (
            proposal_val_num_correct
            > int(state["best_val_num_correct"])
        )

        decision = {
            "iteration": iteration,
            "iteration_seed": iteration_seed,
            "source_candidate": str(source_candidate),
            "source_candidate_hash": source_hash,
            "proposal_candidate": str(proposal_path),
            "proposal_candidate_hash": proposal_hash,
            "previous_best_val_score": float(state["best_val_score"]),
            "previous_best_val_num_correct": int(
                state["best_val_num_correct"]
            ),
            "proposal_val_score": proposal_val_score,
            "proposal_val_num_correct": proposal_val_num_correct,
            "proposal_val_eval_rows": str(proposal_val_rows),
            "validation_status": validation_status,
            "validation_flips_against_best": flips,
            "accepted": accepted,
            "status": "accepted" if accepted else "rejected",
            "stop_reason": None,
        }
        _write_json(decision_path, decision)

        if accepted:
            _copy_candidate(proposal_path, best_path)
        _apply_decision(state, decision)
        _write_json(state_path, state)
        _rebuild_history(args.run_dir)

        print(
            "[hillclimb] decision | "
            f"iteration={iteration} accepted={accepted} "
            f"best_before={decision['previous_best_val_score']:.6f} "
            f"proposal={proposal_val_score:.6f}",
            flush=True,
        )

    best_candidate = best_path
    best_hash = _candidate_hash(best_candidate)
    final_test_rows, final_test_summary = _ensure_evaluation(
        repo_root=repo_root,
        update_script=update_script,
        env=env,
        candidate_path=best_candidate,
        source_rows=test_rows,
        eval_root=args.run_dir / "final_test",
        cache_dir=eval_cache,
        args=args,
        limit_eval=args.limit_test,
    )

    state["best_candidate_hash"] = best_hash
    state["final_test_complete"] = True
    state["final_test_score"] = float(final_test_summary["score"])
    state["final_test_num_correct"] = int(final_test_summary["num_correct"])
    state["final_test_eval_rows"] = str(final_test_rows)
    _write_json(state_path, state)

    final_summary = {
        "script_version": SCRIPT_VERSION,
        "status": "complete",
        "iterations_completed": int(state["next_iteration"]),
        "max_iters": args.max_iters,
        "stop_reason": state.get("stop_reason"),
        "best_candidate": str(best_candidate),
        "best_candidate_hash": best_hash,
        "best_validation_score": float(state["best_val_score"]),
        "best_validation_num_correct": int(state["best_val_num_correct"]),
        "test_score": float(final_test_summary["score"]),
        "test_num_correct": int(final_test_summary["num_correct"]),
        "test_eval_rows": str(final_test_rows),
        "history": str(args.run_dir / "history.jsonl"),
        "state": str(state_path),
    }
    _write_json(args.run_dir / "final_summary.json", final_summary)
    print(_json_dumps(final_summary))


if __name__ == "__main__":
    main()