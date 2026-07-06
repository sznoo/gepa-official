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


TARGET_COMPONENT = "final_answer.predict"


# ============================================================
# IO
# ============================================================


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


def load_candidate(path: Path) -> dict[str, str]:
    obj = read_json(path)
    prompts = obj["prompts"] if isinstance(obj, dict) and "prompts" in obj else obj

    if not isinstance(prompts, dict):
        raise TypeError(f"Candidate file does not contain a prompt dict: {path}")

    prompts = dict(prompts)

    if TARGET_COMPONENT not in prompts:
        raise KeyError(
            f"{TARGET_COMPONENT} not found. Available keys: {sorted(prompts.keys())}"
        )

    bad = {k: type(v).__name__ for k, v in prompts.items() if not isinstance(v, str)}
    if bad:
        raise TypeError(f"Non-string prompt values in candidate: {bad}")

    return prompts


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not overwrite:
            raise FileExistsError(f"{path} already exists. Use --overwrite.")
        shutil.rmtree(path)

    path.mkdir(parents=True, exist_ok=True)


def chunks(xs: list[Any], chunk_size: int):
    for i in range(0, len(xs), chunk_size):
        yield xs[i : i + chunk_size]


# ============================================================
# LM / data / eval
# ============================================================


def make_dspy_lm(
    model: str,
    api_key: str | None,
    api_base: str | None,
    temperature: float | None,
    max_tokens: int | None,
):
    kwargs: dict[str, Any] = {}

    model_l = model.lower()

    # GPT-5-family constraint handling.
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


def get_evalset(args: argparse.Namespace):
    trainset, valset, testset = load_hotpot_splits(
        train_size=args.train_size,
        val_size=args.val_size,
        test_size=args.test_size,
        seed=args.seed,
    )

    if args.eval_split == "train":
        return trainset
    if args.eval_split == "val":
        return valset
    if args.eval_split == "test":
        return testset

    raise ValueError(f"Unknown eval split: {args.eval_split}")


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
    condition_dir: Path,
    prompts: dict[str, str],
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
            phase="final_prompt_probe",
            split=args.eval_split,
            iteration=None,
            candidate_id=None,
            parent_candidate_id=None,
            updated_component=TARGET_COMPONENT,
            candidate_hash=None,
            capture_traces=False,
        )

    evalset = get_evalset(args)

    if args.show_eval_progress:
        scores: list[float] = []
        eval_list = list(evalset)
        chunk_size = max(1, int(args.eval_progress_chunk_size))
        chunk_list = list(chunks(eval_list, chunk_size))

        desc = (
            f"eval[{condition_name}] {args.eval_split} "
            f"chunksize={chunk_size} threads={args.num_threads}"
        )

        for chunk in tqdm(chunk_list, desc=desc, total=len(chunk_list), dynamic_ncols=True):
            batch = adapter.evaluate(chunk, prompts, capture_traces=False)
            scores.extend(float(s) for s in batch.scores)

        mean_score_from_eval_batch = sum(scores) / len(scores)
        eval_n = len(scores)
    else:
        batch = adapter.evaluate(evalset, prompts, capture_traces=False)
        scores = [float(s) for s in batch.scores]
        mean_score_from_eval_batch = sum(scores) / len(scores)
        eval_n = len(scores)

    if hasattr(adapter, "clear_analysis_context"):
        adapter.clear_analysis_context()

    rollout_summary = summarize_rollouts(analysis_dir / "rollout_traces.jsonl")

    summary = {
        "condition": condition_name,
        "target_component": TARGET_COMPONENT,
        "eval_split": args.eval_split,
        "n_from_eval_batch": eval_n,
        "mean_score_from_eval_batch": mean_score_from_eval_batch,
        **rollout_summary,
    }

    write_json(condition_dir / "summary.json", summary)
    return summary


# ============================================================
# The 5 final-answer prompts
# ============================================================


def final_em_span_calibration_v1() -> str:
    return """Given the fields `question`, `summary_1`, `summary_2`, produce the field `answer`.

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


def final_direct_answer_span_v1() -> str:
    return """Given the fields `question`, `summary_1`, `summary_2`, produce the field `answer`.

Extract the answer as a span from the summaries.

Procedure:
1. Look for lines beginning with or containing "Answer", "Direct answer", "Shared/answer", "answer:", or "answer)".
2. From that line, extract only the minimal phrase that answers the question.
3. If the direct-answer line is too verbose, compress it to the requested answer type.
4. If no direct-answer line exists, use the most explicit fact in `summary_2`, then `summary_1`.

Output constraints:
- Output only the answer.
- No full sentences.
- No explanation.
- No parenthetical elaboration.
- No extra geographical levels, dates, roles, or descriptions unless required by the question.
"""


def final_answer_type_granularity_v1() -> str:
    return """Given the fields `question`, `summary_1`, `summary_2`, produce the field `answer`.

Determine the expected answer type from the question and output only that type.

Answer type rules:
- "what period" -> period label only, e.g. "Baroque".
- "which genre" or "what genre" -> genre adjective/noun only, e.g. "animated".
- "what occupation" -> occupation phrase only, usually singular, e.g. "former tennis player".
- "what city" -> city name only.
- "which neighborhood" -> neighborhood answer phrase.
- "what year" -> year only.
- "what name" -> exact introduced name phrase from the evidence.
- "which bishop/person" -> full person name if available; do not return only title + nickname.
- "what do X and Y both refer to" -> the shared referent category, not a long classification description.

Use `summary_2` when it contains the second-hop answer-bearing fact.
Return only the final answer string.
"""


def final_conflict_entity_alignment_v1() -> str:
    return """Given the fields `question`, `summary_1`, `summary_2`, produce the field `answer`.

Answer by aligning the question's target entity or role with the explicit answer-bearing fact.

Rules:
- Do not choose an entity merely because it appears in the first-hop query or retrieval query.
- If multiple candidate entities appear, choose the one whose fact directly matches the question's requested relation.
- Prefer explicit facts over inferred facts.
- For "which year did the [role/person] leave the band/team/group" questions, choose the departure year explicitly attached to that role/person. Do not use an album release year, replacement year, or "final release to feature X" unless the question asks about that person specifically.
- For spouse/queen consort/wife questions, answer the spouse of the exact named person in the question, not a similarly named or later person.
- For comparison/shared-property questions, identify the property common to both entities and output only that shared property.

Return only the concise final answer.
No explanation.
"""


def final_hotpot_em_ceiling_v1() -> str:
    return """Given the fields `question`, `summary_1`, `summary_2`, produce the field `answer`.

Produce the HotpotQA-style exact answer.

Use the combined evidence from `summary_1` and `summary_2`, but output only the minimal answer span.

Priority:
1. If a summary contains an explicit direct answer, extract the minimal answer phrase from it.
2. Otherwise, use the most explicit answer-bearing fact in `summary_2`.
3. If `summary_2` adds a missing support document, prefer its answer-bearing fact over older or inferred facts from `summary_1`.
4. If candidates conflict, choose the candidate whose relation exactly matches the question.

Granularity:
- period: period name only.
- genre: genre label only.
- occupation: occupation phrase only.
- city: city only.
- neighborhood: neighborhood phrase.
- year: year only.
- person/bishop/spouse: full person name if available.
- name introduced as: exact phrase including attached location/context if stated in evidence.
- shared referent: concise category, not a descriptive sentence.

Formatting:
- Return only the answer.
- No sentence.
- No explanation.
- No parentheses.
- No "both are", "the answer is", "labels for", or title prefixes unless part of the name.
- Remove extra dates, countries, roles, and descriptions unless explicitly requested.
"""


FINAL_PROMPTS: dict[str, str] = {
    "final_em_span_calibration_v1": final_em_span_calibration_v1(),
    "final_direct_answer_span_v1": final_direct_answer_span_v1(),
    "final_answer_type_granularity_v1": final_answer_type_granularity_v1(),
    "final_conflict_entity_alignment_v1": final_conflict_entity_alignment_v1(),
    "final_hotpot_em_ceiling_v1": final_hotpot_em_ceiling_v1(),
}


# ============================================================
# Main
# ============================================================


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()

    p.add_argument("--base-candidate-file", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=Path("outputs/hotpotqa_final_prompt_probe"))
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
    p.add_argument("--test-size", type=int, default=100)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--eval-split", choices=["train", "val", "test"], default="test")
    p.add_argument("--num-threads", type=int, default=20)

    p.add_argument("--show-eval-progress", action="store_true")
    p.add_argument("--eval-progress-chunk-size", type=int, default=20)

    return p.parse_args()


def main() -> None:
    args = parse_args()

    load_env_file(args.env_file)
    configure_task_lm(args)

    base_prompts = load_candidate(args.base_candidate_file)

    exp_dir = args.output_root / args.exp_name
    prepare_output_dir(exp_dir, overwrite=args.overwrite)

    write_json(
        exp_dir / "config.json",
        {
            **vars(args),
            "base_candidate_file": str(args.base_candidate_file),
            "target_component": TARGET_COMPONENT,
            "conditions": list(FINAL_PROMPTS.keys()),
            "base_final_prompt": base_prompts[TARGET_COMPONENT],
        },
    )

    aggregate: dict[str, Any] = {
        "exp_dir": str(exp_dir),
        "base_candidate_file": str(args.base_candidate_file),
        "target_component": TARGET_COMPONENT,
        "conditions": {},
    }

    for condition_name, final_prompt in FINAL_PROMPTS.items():
        condition_dir = exp_dir / "conditions" / condition_name
        condition_dir.mkdir(parents=True, exist_ok=True)

        prompts = dict(base_prompts)
        old_prompt = prompts[TARGET_COMPONENT]
        prompts[TARGET_COMPONENT] = final_prompt

        write_json(
            condition_dir / "prompt_candidate.json",
            {
                "name": condition_name,
                "description": f"Final-only prompt probe: {condition_name}",
                "prompts": prompts,
            },
        )

        write_json(
            condition_dir / "final_prompt_event.json",
            {
                "condition": condition_name,
                "target_component": TARGET_COMPONENT,
                "old_instruction": old_prompt,
                "new_instruction": final_prompt,
                "base_candidate_file": str(args.base_candidate_file),
            },
        )

        summary = evaluate_condition(
            args=args,
            condition_name=condition_name,
            condition_dir=condition_dir,
            prompts=prompts,
        )

        aggregate["conditions"][condition_name] = summary
        write_json(exp_dir / "aggregate_summary.json", aggregate)

    print(json.dumps(aggregate, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
