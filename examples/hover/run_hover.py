# examples/hover/run_hover.py

import argparse
import json
import os
from pathlib import Path

import dspy

from gepa.api import optimize
from gepa.adapters.dspy_adapter.dspy_adapter import DspyAdapter

from examples.hover.data import load_hover_splits
from examples.hover.program import HoverMultiHop
from examples.hover.metric import discrete_retrieval_eval
from examples.hover.feedback import feedback_fn_map


def make_lm(
    model: str,
    api_key: str | None = None,
    api_base: str | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
):
    kwargs = {
        "model": model,
        "temperature": temperature,
    }

    if api_key:
        kwargs["api_key"] = api_key
    if api_base:
        kwargs["api_base"] = api_base
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    return dspy.LM(**kwargs)


def evaluate_program(program, testset, metric_fn, num_threads: int):
    evaluator = dspy.Evaluate(
        devset=testset,
        metric=metric_fn,
        num_threads=num_threads,
        display_progress=True,
        display_table=False,
    )
    result = evaluator(program)

    if hasattr(result, "score"):
        return result.score
    return result


def validate_feedback_keys(program, feedback_map):
    predictor_names = {name for name, _ in program.named_predictors()}
    feedback_names = set(feedback_map.keys())

    missing = predictor_names.difference(feedback_names)
    extra = feedback_names.difference(predictor_names)

    print("Predictors:")
    for name in sorted(predictor_names):
        print(f"  - {name}")

    print("Feedback keys:")
    for name in sorted(feedback_names):
        print(f"  - {name}")

    if missing:
        raise ValueError(f"Missing feedback keys: {sorted(missing)}")
    if extra:
        raise ValueError(f"Extra feedback keys: {sorted(extra)}")


def build_seed_candidate(program):
    return {
        name: pred.signature.instructions
        for name, pred in program.named_predictors()
    }


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--train-size", type=int, default=128)
    parser.add_argument("--val-size", type=int, default=128)
    parser.add_argument("--test-size", type=int, default=128)
    parser.add_argument("--seed", type=int, default=0)

    parser.add_argument("--task-model", type=str, required=True)
    parser.add_argument("--task-api-base", type=str, default=None)
    parser.add_argument("--task-api-key", type=str, default=None)
    parser.add_argument("--task-temperature", type=float, default=1.0)
    parser.add_argument("--task-max-tokens", type=int, default=None)

    parser.add_argument("--reflection-model", type=str, required=True)
    parser.add_argument("--reflection-api-base", type=str, default=None)
    parser.add_argument("--reflection-api-key", type=str, default=None)
    parser.add_argument("--reflection-temperature", type=float, default=1.0)
    parser.add_argument("--reflection-max-tokens", type=int, default=None)
    parser.add_argument("--reflection-minibatch-size", type=int, default=3)

    parser.add_argument("--run-dir", type=str, required=True)
    parser.add_argument("--max-metric-calls", type=int, default=200)
    parser.add_argument("--num-threads", type=int, default=1)

    parser.add_argument("--candidate-selection-strategy", type=str, default="pareto")
    parser.add_argument("--module-selector", type=str, default="round_robin")
    parser.add_argument("--frontier-type", type=str, default="instance")
    parser.add_argument("--acceptance-criterion", type=str, default="improvement_or_equal")

    parser.add_argument("--cache-evaluation", action="store_true")
    parser.add_argument("--use-merge", action="store_true")
    parser.add_argument("--display-progress-bar", action="store_true")
    parser.add_argument("--use-cloudpickle", action="store_true")
    parser.add_argument("--no-track-best-outputs", action="store_true")
    parser.add_argument("--warn-on-score-mismatch", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    trainset, valset, testset = load_hover_splits(
        train_size=args.train_size,
        val_size=args.val_size,
        test_size=args.test_size,
        seed=args.seed,
    )

    task_lm = make_lm(
        model=args.task_model,
        api_key=args.task_api_key or os.environ.get("OPENAI_API_KEY"),
        api_base=args.task_api_base,
        temperature=args.task_temperature,
        max_tokens=args.task_max_tokens,
    )
    dspy.configure(lm=task_lm)

    reflection_lm = make_lm(
        model=args.reflection_model,
        api_key=args.reflection_api_key or os.environ.get("OPENAI_API_KEY"),
        api_base=args.reflection_api_base,
        temperature=args.reflection_temperature,
        max_tokens=args.reflection_max_tokens,
    )

    program = HoverMultiHop()
    validate_feedback_keys(program, feedback_fn_map)

    seed_candidate = build_seed_candidate(program)
    save_json(run_dir / "seed_candidate.json", seed_candidate)

    adapter = DspyAdapter(
        student_module=program,
        metric_fn=discrete_retrieval_eval,
        feedback_map=feedback_fn_map,
        num_threads=args.num_threads,
        reflection_lm=reflection_lm,
        reflection_minibatch_size=args.reflection_minibatch_size,
        warn_on_score_mismatch=args.warn_on_score_mismatch,
    )

    print("\n=== Baseline evaluation ===")
    baseline_score = evaluate_program(
        program=program,
        testset=testset,
        metric_fn=discrete_retrieval_eval,
        num_threads=args.num_threads,
    )
    print(f"Baseline score: {baseline_score}")

    print("\n=== GEPA optimization ===")
    result = optimize(
        seed_candidate=seed_candidate,
        trainset=trainset,
        valset=valset,
        adapter=adapter,
        reflection_lm=None,
        candidate_selection_strategy=args.candidate_selection_strategy,
        frontier_type=args.frontier_type,
        skip_perfect_score=True,
        reflection_minibatch_size=args.reflection_minibatch_size,
        perfect_score=1.0,
        module_selector=args.module_selector,
        use_merge=args.use_merge,
        max_metric_calls=args.max_metric_calls,
        run_dir=str(run_dir),
        track_best_outputs=not args.no_track_best_outputs,
        display_progress_bar=args.display_progress_bar,
        use_cloudpickle=args.use_cloudpickle,
        cache_evaluation=args.cache_evaluation,
        seed=args.seed,
        raise_on_exception=False,
        acceptance_criterion=args.acceptance_criterion,
    )

    best_candidate = result.best_candidate
    save_json(run_dir / "best_candidate.json", best_candidate)

    optimized_program = HoverMultiHop()
    for name, pred in optimized_program.named_predictors():
        pred.signature.instructions = best_candidate[name]

    print("\n=== Optimized evaluation ===")
    optimized_score = evaluate_program(
        program=optimized_program,
        testset=testset,
        metric_fn=discrete_retrieval_eval,
        num_threads=args.num_threads,
    )
    print(f"Optimized score: {optimized_score}")

    summary = {
        "baseline_score": baseline_score,
        "optimized_score": optimized_score,
        "train_size": args.train_size,
        "val_size": args.val_size,
        "test_size": args.test_size,
        "max_metric_calls": args.max_metric_calls,
        "seed": args.seed,
    }
    save_json(run_dir / "summary.json", summary)

    print("\nSaved:")
    print(f"  {run_dir / 'seed_candidate.json'}")
    print(f"  {run_dir / 'best_candidate.json'}")
    print(f"  {run_dir / 'summary.json'}")


if __name__ == "__main__":
    main()