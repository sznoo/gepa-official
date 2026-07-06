# /home/jinwoo/gepa-official/examples/hotpotqa/run_hotpot.py
import argparse
import json
import os
from pathlib import Path

import dspy

from gepa.api import optimize
from gepa.adapters.dspy_adapter.dspy_adapter import DspyAdapter

from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter
from examples.hotpotqa.data import load_hotpot_splits
from examples.hotpotqa.feedback import feedback_fn_map
from examples.hotpotqa.metric import answer_exact_match
from examples.hotpotqa.program import HotpotMultiHop
from examples.hotpotqa.retriever import DEFAULT_RETRIEVER_DIR, set_retriever_dir


ANALYSIS_LOG_FILES = [
    "rollout_traces.jsonl",
    "feedback_examples.jsonl",
    "proposal_events.jsonl",
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


def build_seed_candidate(program: dspy.Module) -> dict[str, str]:
    return {
        name: pred.signature.instructions
        for name, pred in program.named_predictors()
    }


def validate_feedback_keys(program: dspy.Module):
    predictor_names = {name for name, _ in program.named_predictors()}
    feedback_names = set(feedback_fn_map.keys())

    missing = predictor_names - feedback_names
    extra = feedback_names - predictor_names

    print("Named predictors:")
    for name in sorted(predictor_names):
        print(f"  - {name}")

    if missing:
        raise ValueError(f"Missing feedback functions for predictors: {sorted(missing)}")
    if extra:
        raise ValueError(f"Feedback map has unknown predictor keys: {sorted(extra)}")


def validate_candidate_keys(program: dspy.Module, candidate: dict[str, str]):
    predictor_names = {name for name, _ in program.named_predictors()}
    candidate_names = set(candidate.keys())

    missing = predictor_names - candidate_names
    extra = candidate_names - predictor_names

    if missing:
        raise ValueError(f"Prompt candidate is missing predictor keys: {sorted(missing)}")
    if extra:
        raise ValueError(f"Prompt candidate has unknown predictor keys: {sorted(extra)}")


def load_prompt_candidate(path: str | Path) -> tuple[str, dict[str, str]]:
    path = Path(path)
    obj = json.loads(path.read_text())

    if "prompts" not in obj:
        raise ValueError(f"Prompt JSON must contain top-level `prompts`: {path}")

    prompts = obj["prompts"]
    if not isinstance(prompts, dict):
        raise ValueError(f"`prompts` must be a dict: {path}")

    for key, value in prompts.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError(f"`prompts` must be dict[str, str]: {path}")

    name = obj.get("name", path.stem)
    return name, prompts


def evaluate_candidate(
    adapter: DspyAdapter,
    dataset,
    candidate: dict[str, str],
    label: str,
    split: str | None = None,
    phase: str | None = None,
    candidate_id: int | None = None,
):
    if hasattr(adapter, "set_analysis_context"):
        adapter.set_analysis_context(
            split=split,
            phase=phase or label,
            candidate_id=candidate_id,
        )

    try:
        eval_batch = adapter.evaluate(dataset, candidate, capture_traces=False)
    finally:
        if hasattr(adapter, "clear_analysis_context"):
            adapter.clear_analysis_context()

    scores = eval_batch.scores
    score = sum(scores) / len(scores) if scores else 0.0

    print(f"{label} score: {score:.4f} ({sum(scores):.1f}/{len(scores)})")
    return score


def save_json(path: str | Path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def resolve_analysis_log_dir(args) -> Path | None:
    if args.analysis_log_dir:
        return Path(args.analysis_log_dir)

    if args.analysis_name:
        return Path(args.run_dir) / f"analysis_{args.analysis_name}"

    return None


def overwrite_analysis_logs(analysis_log_dir: Path):
    analysis_log_dir.mkdir(parents=True, exist_ok=True)

    for filename in ANALYSIS_LOG_FILES:
        path = analysis_log_dir / filename
        if path.exists():
            path.unlink()


def parse_args():
    parser = argparse.ArgumentParser()

    # Data
    parser.add_argument("--train-size", type=int, default=8)
    parser.add_argument("--val-size", type=int, default=8)
    parser.add_argument("--test-size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)

    # Retriever / program
    parser.add_argument("--retriever-dir", default=os.environ.get("HOTPOT_RETRIEVER_DIR", DEFAULT_RETRIEVER_DIR))
    parser.add_argument("--k", type=int, default=7)

    # Task LM
    parser.add_argument("--task-model", default=os.environ.get("TASK_MODEL", "openai/Qwen/Qwen3-8B"))
    parser.add_argument("--task-api-base", default=os.environ.get("TASK_API_BASE", "http://localhost:8889/v1"))
    parser.add_argument("--task-api-key", default=os.environ.get("TASK_API_KEY", "dummy"))
    parser.add_argument("--task-temperature", type=float, default=0.7)
    parser.add_argument("--task-max-tokens", type=int, default=4096)

    # Reflection LM
    parser.add_argument("--reflection-model", default=os.environ.get("REFLECTION_MODEL", "openai/Qwen/Qwen3-8B"))
    parser.add_argument("--reflection-api-base", default=os.environ.get("REFLECTION_API_BASE", "http://localhost:8889/v1"))
    parser.add_argument("--reflection-api-key", default=os.environ.get("REFLECTION_API_KEY", "dummy"))
    parser.add_argument("--reflection-temperature", type=float, default=0.7)
    parser.add_argument("--reflection-max-tokens", type=int, default=8192)
    parser.add_argument("--reflection-minibatch-size", type=int, default=2)

    # Fixed candidate evaluation
    parser.add_argument(
        "--eval-only",
        action="store_true",
        help="Only evaluate the prompt candidate loaded from --prompt-json; skip GEPA optimization.",
    )
    parser.add_argument(
        "--prompt-json",
        default=None,
        help="Path to a prompt JSON file with a top-level `prompts` dict.",
    )
    parser.add_argument(
        "--eval-split",
        default="test",
        choices=["train", "val", "test"],
        help="Dataset split to evaluate in --eval-only mode.",
    )

    # GEPA optimization
    parser.add_argument("--run-dir", default="outputs/hotpotqa_smoke")
    parser.add_argument("--max-metric-calls", type=int, default=40)
    parser.add_argument("--num-threads", type=int, default=1)
    parser.add_argument(
        "--candidate-selection-strategy",
        default="pareto",
        choices=["pareto", "current_best", "epsilon_greedy", "top_k_pareto"],
    )
    parser.add_argument(
        "--module-selector",
        default="round_robin",
        choices=["round_robin", "all"],
    )
    parser.add_argument(
        "--frontier-type",
        default="instance",
        choices=["instance", "objective", "hybrid", "cartesian"],
    )
    parser.add_argument(
        "--acceptance-criterion",
        default="strict_improvement",
        choices=["strict_improvement", "improvement_or_equal"],
    )
    parser.add_argument("--cache-evaluation", action="store_true")
    parser.add_argument("--use-merge", action="store_true")
    parser.add_argument("--display-progress-bar", action="store_true")
    parser.add_argument("--use-cloudpickle", action="store_true")
    parser.add_argument("--no-track-best-outputs", action="store_true")
    parser.add_argument("--warn-on-score-mismatch", action="store_true")

    # Analysis logging
    parser.add_argument("--analysis-log-dir", default=None)
    parser.add_argument(
        "--analysis-name",
        default=None,
        help="If set, logs are written to <run-dir>/analysis_<analysis-name>. Ignored when --analysis-log-dir is provided.",
    )
    parser.add_argument(
        "--overwrite-analysis",
        action="store_true",
        help="Delete existing analysis JSONL files in the selected analysis log directory before running.",
    )
    parser.add_argument("--no-analysis-rollouts", action="store_true")
    parser.add_argument("--no-analysis-feedback", action="store_true")
    parser.add_argument("--no-analysis-proposals", action="store_true")
    parser.add_argument("--no-log-instructions-in-rollout", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.eval_only and not args.prompt_json:
        raise ValueError("--eval-only requires --prompt-json")

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    analysis_log_dir = resolve_analysis_log_dir(args)
    if analysis_log_dir:
        analysis_log_dir.mkdir(parents=True, exist_ok=True)
        if args.overwrite_analysis:
            overwrite_analysis_logs(analysis_log_dir)

        print(f"Analysis logging enabled: {analysis_log_dir}")
    else:
        print("Analysis logging disabled.")

    print("Loading HotpotQA splits...")
    trainset, valset, testset = load_hotpot_splits(
        train_size=args.train_size,
        val_size=args.val_size,
        test_size=args.test_size,
        seed=args.seed,
    )
    print(f"Split sizes: train={len(trainset)}, val={len(valset)}, test={len(testset)}")

    print("Configuring DSPy task LM...")
    task_lm = make_dspy_lm(
        model=args.task_model,
        api_base=args.task_api_base,
        api_key=args.task_api_key,
        temperature=args.task_temperature,
        max_tokens=args.task_max_tokens,
    )
    dspy.configure(lm=task_lm)

    print(f"Using BM25 retriever dir: {args.retriever_dir}")
    set_retriever_dir(args.retriever_dir)

    program = HotpotMultiHop(
        k=args.k,
        retriever_dir=args.retriever_dir,
    )

    validate_feedback_keys(program)

    seed_candidate = build_seed_candidate(program)

    print("Seed candidate components:")
    for name, text in seed_candidate.items():
        print(f"  - {name}: {text[:120].replace(chr(10), ' ')}")

    reflection_lm = make_dspy_lm(
        model=args.reflection_model,
        api_base=args.reflection_api_base,
        api_key=args.reflection_api_key,
        temperature=args.reflection_temperature,
        max_tokens=args.reflection_max_tokens,
    )

    adapter_cls = HotpotLoggingDspyAdapter if analysis_log_dir else DspyAdapter

    adapter_kwargs = {
        "student_module": program,
        "metric_fn": answer_exact_match,
        "feedback_map": feedback_fn_map,
        "num_threads": args.num_threads,
        "reflection_lm": reflection_lm,
        "reflection_minibatch_size": args.reflection_minibatch_size,
        "warn_on_score_mismatch": args.warn_on_score_mismatch,
    }

    if analysis_log_dir:
        adapter_kwargs.update({
            "analysis_log_dir": str(analysis_log_dir),
            "run_id": str(args.run_dir),
            "log_rollouts": not args.no_analysis_rollouts,
            "log_feedback": not args.no_analysis_feedback,
            "log_proposals": not args.no_analysis_proposals,
            "log_instructions_in_rollout": not args.no_log_instructions_in_rollout,
        })

    adapter = adapter_cls(**adapter_kwargs)

    save_json(run_dir / "seed_candidate.json", seed_candidate)

    if args.eval_only:
        prompt_name, fixed_candidate = load_prompt_candidate(args.prompt_json)
        validate_candidate_keys(program, fixed_candidate)

        eval_dataset_map = {"train": trainset, "val": valset, "test": testset}
        evalset = eval_dataset_map[args.eval_split]

        print(f"\nLoaded fixed prompt candidate: {prompt_name}")
        print(f"Prompt JSON: {args.prompt_json}")
        print(f"Eval split: {args.eval_split} ({len(evalset)} examples)")

        save_json(run_dir / f"{prompt_name}.json", {
            "name": prompt_name,
            "prompt_json": args.prompt_json,
            "candidate": fixed_candidate,
            "eval_split": args.eval_split,
        })

        print(f"\nEvaluating fixed candidate on {args.eval_split}set...")
        fixed_eval_score = evaluate_candidate(
            adapter,
            evalset,
            fixed_candidate,
            f"{prompt_name} {args.eval_split}",
            split=args.eval_split,
            phase=f"{prompt_name}_{args.eval_split}",
            candidate_id=0,
        )

        summary = {
            "mode": "eval_only",
            "prompt_name": prompt_name,
            "prompt_json": args.prompt_json,
            "eval_split": args.eval_split,
            "eval_score": fixed_eval_score,
            "test_score": fixed_eval_score if args.eval_split == "test" else None,
            "run_dir": args.run_dir,
            "analysis_name": args.analysis_name,
            "analysis_log_dir": str(analysis_log_dir) if analysis_log_dir else None,
            "overwrite_analysis": args.overwrite_analysis,
            "train_size": len(trainset),
            "val_size": len(valset),
            "test_size": len(testset),
            "num_threads": args.num_threads,
            "retriever_dir": args.retriever_dir,
        }
        save_json(run_dir / f"summary_{prompt_name}.json", summary)

        print("\nSummary:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    print("\nEvaluating baseline on testset...")
    baseline_test_score = evaluate_candidate(
        adapter,
        testset,
        seed_candidate,
        "Baseline test",
        split="test",
        phase="baseline_test",
        candidate_id=0,
    )

    print("\nStarting GEPA optimization...")
    if hasattr(adapter, "set_analysis_context"):
        adapter.set_analysis_context(
            split="train",
            phase="optimization",
            candidate_id=None,
        )

    try:
        result = optimize(
            seed_candidate=seed_candidate,
            trainset=trainset,
            valset=valset,
            adapter=adapter,
            reflection_lm=None,  # DspyAdapter owns proposal via adapter.propose_new_texts().
            candidate_selection_strategy=args.candidate_selection_strategy,
            frontier_type=args.frontier_type,
            skip_perfect_score=True,
            reflection_minibatch_size=args.reflection_minibatch_size,
            perfect_score=1.0,
            module_selector=args.module_selector,
            use_merge=args.use_merge,
            max_metric_calls=args.max_metric_calls,
            run_dir=args.run_dir,
            track_best_outputs=not args.no_track_best_outputs,
            display_progress_bar=args.display_progress_bar,
            use_cloudpickle=args.use_cloudpickle,
            cache_evaluation=args.cache_evaluation,
            seed=args.seed,
            raise_on_exception=False,
            acceptance_criterion=args.acceptance_criterion,
        )
    finally:
        if hasattr(adapter, "clear_analysis_context"):
            adapter.clear_analysis_context()

    best_candidate = result.best_candidate
    print("\nBest candidate:")
    print(json.dumps(best_candidate, indent=2, ensure_ascii=False))
    save_json(run_dir / "best_candidate.json", best_candidate)

    print("\nEvaluating best candidate on testset...")
    optimized_test_score = evaluate_candidate(
        adapter,
        testset,
        best_candidate,
        "Optimized test",
        split="test",
        phase="optimized_test",
        candidate_id=None,
    )

    summary = {
        "mode": "optimize",
        "baseline_test_score": baseline_test_score,
        "optimized_test_score": optimized_test_score,
        "improvement": optimized_test_score - baseline_test_score,
        "run_dir": args.run_dir,
        "analysis_name": args.analysis_name,
        "analysis_log_dir": str(analysis_log_dir) if analysis_log_dir else None,
        "overwrite_analysis": args.overwrite_analysis,
        "train_size": len(trainset),
        "val_size": len(valset),
        "test_size": len(testset),
        "max_metric_calls": args.max_metric_calls,
        "num_threads": args.num_threads,
        "retriever_dir": args.retriever_dir,
    }
    save_json(run_dir / "summary.json", summary)

    print("\nSummary:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()