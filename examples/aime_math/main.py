import dspy

from examples.aime_math.utils import evaluate_on_dataset, load_math_dataset, math_metric, run_llm
from gepa.optimize_anything import (
    EngineConfig,
    GEPAConfig,
    ReflectionConfig,
    SideInfo,
    optimize_anything,
)


def evaluate(candidate: str, example) -> tuple[float, SideInfo]:
    try:
        prediction = run_llm(example, candidate)
        score, feedback = math_metric(example, prediction)
        output = getattr(prediction, "answer", "")
        reasoning = getattr(prediction, "reasoning", "")
    except Exception as e:
        score = 0.0
        output = ""
        reasoning = ""
        feedback = f"Execution failed with {type(e).__name__}: {e}"

    side_info = {
        "score": score,
        "input": example.input,
        "prompt": candidate,
        "output": output,
        "reasoning": reasoning,
        "execution_feedback": feedback,
    }

    return score, side_info


def main():
    INITIAL_PROMPT = (
        "Solve the math problem internally. Return only the final numerical answer as an integer. "
        "Do not include reasoning, explanation, markdown, or extra text."
    )

    api_base = "http://localhost:8889/v1"
    model_name = "openai/Qwen/Qwen3-8B"

    solver_lm = dspy.LM(
        model_name,
        api_key="dummy",
        api_base=api_base,
        temperature=0.7,
        max_tokens=256,
    )
    dspy.configure(lm=solver_lm)

    trainset, valset, testset = load_math_dataset()

    print(f"Split sizes: train={len(trainset)}, val={len(valset)}, test={len(testset)}")

    gepa_config = GEPAConfig(
        engine=EngineConfig(
            run_dir="outputs/aime_math_qwen_fullsplit_smoke",
            max_metric_calls=150,
            track_best_outputs=True,
            parallel=False,
            max_workers=1,
            cache_evaluation=True,
        ),
        reflection=ReflectionConfig(
            reflection_lm=model_name,
            reflection_lm_kwargs={
                "api_key": "dummy",
                "api_base": api_base,
                "temperature": 0.7,
                "max_tokens": 2048,
            },
            reflection_minibatch_size=2,
        ),
    )

    result = optimize_anything(
        seed_candidate=INITIAL_PROMPT,
        evaluator=evaluate,
        dataset=trainset,
        valset=valset,
        config=gepa_config,
    )

    print("\nEvaluating Baseline (Initial Prompt)...")
    baseline_score = evaluate_on_dataset(INITIAL_PROMPT, testset)

    print("\nEvaluating Best Optimized Program...")
    best_prompt = result.best_candidate
    print(f"Best Prompt Found:\n{best_prompt}")

    optimized_score = evaluate_on_dataset(best_prompt, testset)

    print(f"Baseline Score: {baseline_score:.2%}")
    print(f"Optimized Score: {optimized_score:.2%}")
    print(f"Improvement: {optimized_score - baseline_score:.2%}")
    print(f"Run dir: {gepa_config.engine.run_dir}")


if __name__ == "__main__":
    main()
