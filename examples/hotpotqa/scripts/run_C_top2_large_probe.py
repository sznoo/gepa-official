#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from tqdm.auto import tqdm

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"

for _path in (str(ROOT), str(SRC)):
    if _path in sys.path:
        sys.path.remove(_path)

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

import dspy  # noqa: E402

from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter  # noqa: E402
from examples.hotpotqa.data import load_hotpot_splits  # noqa: E402
from examples.hotpotqa.feedback import feedback_fn_map  # noqa: E402
from examples.hotpotqa.metric import answer_exact_match  # noqa: E402
from examples.hotpotqa.program import HotpotMultiHop  # noqa: E402
from examples.hotpotqa.retriever import set_retriever_dir  # noqa: E402


HOP2_COMPONENT = "create_query_hop2.predict"
FINAL_COMPONENT = "final_answer.predict"


MANUAL_FINAL_PROMPT = """Given the fields `question`, `summary_1`, `summary_2`, produce the field `answer`.

Answer with the shortest exact answer span supported by the summaries.

Use these rules:
- Return only the final answer string. No explanation.
- Prefer an explicit "Answer", "Direct answer", "Shared/answer", or "answer:" phrase in `summary_1` or `summary_2` when present.
- Match the granularity requested by the question:
  - what period -> period name only, not dates.
  - what genre -> genre label only, not "feature film" or a description.
  - what city -> city only, not state/region/country.
  - which neighborhood -> neighborhood name plus "neighborhood" if that is the natural answer phrase.
  - what occupation -> singular occupation label if the question asks which occupation.
  - what name -> the full name phrase given in the evidence, including location/context if the evidence states it as part of the introduced name.
- Strip explanatory prefixes such as "both are", "labels for", "bishop", "the answer is".
- Strip parenthetical details, dates, roles, and extra descriptors unless the question explicitly asks for them.
- Do not output multiple candidates unless the question explicitly asks for multiple answers.
"""


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not overwrite:
            raise FileExistsError(f"{path} exists. Use --overwrite.")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def load_condition_prompts(condition_dir: Path) -> tuple[dict[str, str], str, str]:
    """
    Returns:
      candidate_prompts: full prompt dict after condition injection
      old_hop2: original GEPA/best hop2 instruction from proposal_event.json
      new_hop2: condition-specific hop2 instruction from prompt_candidate.json
    """
    candidate_path = condition_dir / "prompt_candidate.json"
    event_path = condition_dir / "proposal_event.json"

    candidate = read_json(candidate_path)
    prompts = candidate["prompts"] if "prompts" in candidate else candidate
    prompts = dict(prompts)

    if HOP2_COMPONENT not in prompts:
        raise KeyError(f"{HOP2_COMPONENT} not found in {candidate_path}")
    if FINAL_COMPONENT not in prompts:
        raise KeyError(f"{FINAL_COMPONENT} not found in {candidate_path}")

    event = read_json(event_path)

    old_hop2 = event.get("old_instruction")
    if not old_hop2:
        raise KeyError(f"old_instruction not found in {event_path}")

    new_hop2 = prompts[HOP2_COMPONENT]

    return prompts, old_hop2, new_hop2


def make_dspy_lm(
    model: str,
    api_key: str | None,
    api_base: str | None,
    temperature: float | None,
    max_tokens: int | None,
):
    kwargs: dict[str, Any] = {}

    model_l = model.lower()
    if "openai/gpt-5" in model_l or model_l.startswith("gpt-5"):
        if temperature is not None and temperature != 1.0:
            temperature = 1.0
        if max_tokens is not None and max_tokens < 16000:
            max_tokens = 16000

    if api_key:
        kwargs["api_key"] = api_key
    if api_base:
        kwargs["api_base"] = api_base
    if temperature is not None:
        kwargs["temperature"] = temperature
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    return dspy.LM(model, **kwargs)


def configure_task_lm(args: argparse.Namespace) -> None:
    api_key = args.task_api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not found.")

    lm = make_dspy_lm(
        model=args.task_model,
        api_key=api_key,
        api_base=args.task_api_base,
        temperature=args.task_temperature,
        max_tokens=args.task_max_tokens,
    )
    dspy.configure(lm=lm)


def chunks(xs: list[Any], chunk_size: int):
    for i in range(0, len(xs), chunk_size):
        yield xs[i : i + chunk_size]


def get_evalset(args: argparse.Namespace):
    trainset, valset, testset = load_hotpot_splits(
        train_size=args.train_size,
        val_size=args.val_size,
        test_size=args.test_size,
        seed=args.seed,
    )

    split_map = {
        "train": trainset,
        "val": valset,
        "test": testset,
    }

    evalset = list(split_map[args.eval_split])
    start = args.eval_offset
    end = None if args.eval_limit is None else start + args.eval_limit
    sliced = evalset[start:end]

    if not sliced:
        raise ValueError(
            f"Empty evalset after slicing. split={args.eval_split}, "
            f"loaded={len(evalset)}, offset={args.eval_offset}, limit={args.eval_limit}"
        )

    return sliced


def summarize_rollouts(rollout_path: Path) -> dict[str, Any]:
    rows = read_jsonl(rollout_path)
    n = len(rows)

    if n == 0:
        return {
            "n": 0,
            "mean_score": None,
            "wrong_count": None,
            "correct_count": None,
            "avg_support_recall_total": None,
            "avg_support_recall_hop2_only": None,
            "retrieval_failure_count": None,
            "retrieval_failure_ratio": None,
            "hop2_new_support_hit_count": None,
            "hop2_new_support_hit_ratio": None,
        }

    scores = [float(r.get("score", 0.0)) for r in rows]

    support_total = [
        float(r["support_recall_total"])
        for r in rows
        if r.get("support_recall_total") is not None
    ]

    support_hop2 = [
        float(r["support_recall_hop2_only"])
        for r in rows
        if r.get("support_recall_hop2_only") is not None
    ]

    retrieval_failures = [
        r for r in rows
        if bool(r.get("missing_titles_after_hop2") or [])
    ]

    hop2_new_support_hits = [
        r for r in rows
        if bool(r.get("new_support_titles_hop2") or [])
    ]

    return {
        "n": n,
        "mean_score": sum(scores) / n,
        "wrong_count": sum(1 for s in scores if s < 1.0),
        "correct_count": sum(1 for s in scores if s >= 1.0),
        "avg_support_recall_total": (
            sum(support_total) / len(support_total)
            if support_total else None
        ),
        "avg_support_recall_hop2_only": (
            sum(support_hop2) / len(support_hop2)
            if support_hop2 else None
        ),
        "retrieval_failure_count": len(retrieval_failures),
        "retrieval_failure_ratio": len(retrieval_failures) / n,
        "hop2_new_support_hit_count": len(hop2_new_support_hits),
        "hop2_new_support_hit_ratio": len(hop2_new_support_hits) / n,
    }


def evaluate_condition(
    *,
    args: argparse.Namespace,
    condition_name: str,
    prompts: dict[str, str],
    condition_dir: Path,
) -> dict[str, Any]:
    analysis_dir = condition_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    set_retriever_dir(str(args.retriever_dir))

    program = HotpotMultiHop(
        k=args.retrieval_k,
        retriever_dir=str(args.retriever_dir),
    )

    adapter = HotpotLoggingDspyAdapter(
        student_module=program,
        metric_fn=answer_exact_match,
        feedback_map=feedback_fn_map,
        failure_score=0.0,
        num_threads=args.num_threads,
        reflection_lm=None,
        analysis_log_dir=str(analysis_dir),
        run_id=str(condition_dir),
        log_rollouts=True,
        log_feedback=False,
        log_proposals=False,
        log_instructions_in_rollout=True,
    )

    if hasattr(adapter, "set_analysis_context"):
        adapter.set_analysis_context(
            phase="c_top2_large_probe",
            split=args.eval_split,
            iteration=None,
            candidate_id=None,
            parent_candidate_id=None,
            updated_component="c_top2_manual_probe",
            candidate_hash=None,
            capture_traces=False,
        )

    evalset = get_evalset(args)

    if args.show_eval_progress:
        all_scores: list[float] = []
        eval_chunks = list(chunks(evalset, max(1, args.eval_progress_chunk_size)))

        desc = (
            f"eval[{condition_name}] {args.eval_split} "
            f"offset={args.eval_offset} n={len(evalset)}"
        )

        for chunk in tqdm(eval_chunks, desc=desc, total=len(eval_chunks), dynamic_ncols=True):
            batch = adapter.evaluate(chunk, prompts, capture_traces=False)
            all_scores.extend(float(s) for s in batch.scores)

        mean_score_from_eval_batch = sum(all_scores) / len(all_scores)
        eval_n = len(all_scores)
    else:
        batch = adapter.evaluate(evalset, prompts, capture_traces=False)
        scores = [float(s) for s in batch.scores]
        mean_score_from_eval_batch = sum(scores) / len(scores)
        eval_n = len(scores)

    if hasattr(adapter, "clear_analysis_context"):
        adapter.clear_analysis_context()

    summary = {
        "condition": condition_name,
        "eval_split": args.eval_split,
        "eval_offset": args.eval_offset,
        "eval_limit": args.eval_limit,
        "n_from_eval_batch": eval_n,
        "mean_score_from_eval_batch": mean_score_from_eval_batch,
        **summarize_rollouts(analysis_dir / "rollout_traces.jsonl"),
    }

    write_json(condition_dir / "summary.json", summary)
    return summary


def build_conditions(
    *,
    gepa_prompts: dict[str, str],
    canonical_hop2: str,
    query_compression_hop2: str,
    manual_final: str,
) -> dict[str, dict[str, str]]:
    conditions: dict[str, dict[str, str]] = {}

    conditions["gepa_best"] = dict(gepa_prompts)

    final_only = dict(gepa_prompts)
    final_only[FINAL_COMPONENT] = manual_final
    conditions["final_manual_only"] = final_only

    canonical_only = dict(gepa_prompts)
    canonical_only[HOP2_COMPONENT] = canonical_hop2
    conditions["canonical_hop2_only"] = canonical_only

    canonical_final = dict(gepa_prompts)
    canonical_final[HOP2_COMPONENT] = canonical_hop2
    canonical_final[FINAL_COMPONENT] = manual_final
    conditions["canonical_hop2_final_manual"] = canonical_final

    query_only = dict(gepa_prompts)
    query_only[HOP2_COMPONENT] = query_compression_hop2
    conditions["query_compression_hop2_only"] = query_only

    query_final = dict(gepa_prompts)
    query_final[HOP2_COMPONENT] = query_compression_hop2
    query_final[FINAL_COMPONENT] = manual_final
    conditions["query_compression_hop2_final_manual"] = query_final

    return conditions


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()

    p.add_argument("--canonical-condition-dir", type=Path, required=True)
    p.add_argument("--query-compression-condition-dir", type=Path, required=True)

    p.add_argument("--output-root", type=Path, default=Path("outputs/hotpotqa_c_top2_large_probe"))
    p.add_argument("--exp-name", type=str, required=True)
    p.add_argument("--overwrite", action="store_true")

    p.add_argument("--env-file", type=Path, default=Path(".env"))

    p.add_argument("--task-model", type=str, default="openai/gpt-5-mini")
    p.add_argument("--task-api-key", type=str, default=None)
    p.add_argument("--task-api-base", type=str, default=None)
    p.add_argument("--task-temperature", type=float, default=1.0)
    p.add_argument("--task-max-tokens", type=int, default=16000)

    p.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    p.add_argument("--retrieval-k", type=int, default=7)

    p.add_argument("--train-size", type=int, default=100)
    p.add_argument("--val-size", type=int, default=100)
    p.add_argument("--test-size", type=int, default=400)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--eval-split", choices=["train", "val", "test"], default="test")

    p.add_argument("--eval-offset", type=int, default=100)
    p.add_argument("--eval-limit", type=int, default=300)

    p.add_argument("--num-threads", type=int, default=20)
    p.add_argument("--show-eval-progress", action="store_true")
    p.add_argument("--eval-progress-chunk-size", type=int, default=20)

    return p.parse_args()


def main() -> None:
    args = parse_args()

    load_env_file(args.env_file)
    configure_task_lm(args)

    exp_dir = args.output_root / args.exp_name
    prepare_output_dir(exp_dir, overwrite=args.overwrite)

    canonical_prompts, canonical_old_hop2, canonical_hop2 = load_condition_prompts(
        args.canonical_condition_dir
    )
    query_prompts, query_old_hop2, query_hop2 = load_condition_prompts(
        args.query_compression_condition_dir
    )

    if canonical_old_hop2 != query_old_hop2:
        print("[WARN] old_hop2 differs between C top-2 condition dirs.")
        print("[WARN] Using canonical condition old_hop2 as GEPA/base hop2.")

    # Reconstruct GEPA best by taking the canonical condition prompt set
    # and restoring create_query_hop2.predict to old_instruction.
    gepa_prompts = dict(canonical_prompts)
    gepa_prompts[HOP2_COMPONENT] = canonical_old_hop2

    # Keep original final prompt from the GEPA/base prompt set.
    # Manual final is only injected in *_final_manual conditions.
    manual_final = MANUAL_FINAL_PROMPT

    conditions = build_conditions(
        gepa_prompts=gepa_prompts,
        canonical_hop2=canonical_hop2,
        query_compression_hop2=query_hop2,
        manual_final=manual_final,
    )

    write_json(
        exp_dir / "config.json",
        {
            **vars(args),
            "canonical_condition_dir": str(args.canonical_condition_dir),
            "query_compression_condition_dir": str(args.query_compression_condition_dir),
            "conditions": list(conditions.keys()),
            "hop2_component": HOP2_COMPONENT,
            "final_component": FINAL_COMPONENT,
            "gepa_hop2_instruction": gepa_prompts[HOP2_COMPONENT],
            "canonical_hop2_instruction": canonical_hop2,
            "query_compression_hop2_instruction": query_hop2,
            "gepa_final_instruction": gepa_prompts[FINAL_COMPONENT],
            "manual_final_instruction": manual_final,
        },
    )

    aggregate: dict[str, Any] = {
        "exp_dir": str(exp_dir),
        "eval_split": args.eval_split,
        "test_size_loaded": args.test_size,
        "eval_offset": args.eval_offset,
        "eval_limit": args.eval_limit,
        "conditions": {},
    }

    for condition_name, prompts in conditions.items():
        condition_dir = exp_dir / "conditions" / condition_name
        condition_dir.mkdir(parents=True, exist_ok=True)

        write_json(
            condition_dir / "prompt_candidate.json",
            {
                "name": condition_name,
                "description": f"C top-2 heldout probe: {condition_name}",
                "prompts": prompts,
            },
        )

        summary = evaluate_condition(
            args=args,
            condition_name=condition_name,
            prompts=prompts,
            condition_dir=condition_dir,
        )

        aggregate["conditions"][condition_name] = summary
        write_json(exp_dir / "aggregate_summary.json", aggregate)

    print(json.dumps(aggregate, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
