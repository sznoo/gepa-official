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


HOP2_CANDIDATES: dict[str, str] = {
    "less_constrained_bm25_v1": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Write a compact but sufficiently informative search query for retrieving the missing second-hop evidence.

Guidelines:
- Include the unresolved entity, relation, attribute, or answer type implied by the question.
- Keep the strongest known anchor entity from `summary_1` when it helps disambiguate the target.
- Preserve canonical names, titles, aliases, and distinctive surface forms.
- Use relation words from the original question when they are useful for retrieval.
- Do not over-compress: the query should usually contain 4 to 10 meaningful words.
- Avoid full-sentence explanations, but do not remove useful lexical context just to make the query short.

Output only the query.""",

    "anchor_preserving_bm25_v1": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Construct the query by preserving the best anchor terms.

Include:
- the most specific named entity, title, person, organization, work, or place already identified in `summary_1`;
- the missing relation or target requested by the original question;
- one answer-type or relation keyword when useful, such as spouse, director, genre, period, city, occupation, author, member, language, or year.

Rules:
- Preserve exact capitalization and canonical surface forms when possible.
- Do not drop the anchor entity unless the summary clearly shows it is irrelevant.
- Do not output a full question.
- Do not output reasoning or explanations.

Output only the query.""",

    "bridge_relation_bm25_v1": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Use a bridge-style query.

The query should combine:
1. the bridge entity or intermediate entity established in `summary_1`;
2. the relation or property still needed to answer the original question;
3. a short answer-type hint if it improves retrieval.

This is a BM25 query, so lexical overlap matters. Keep enough names and relation words to identify the correct page.

Avoid:
- replacing the bridge entity with a vague description;
- using only the missing target type without an anchor;
- long explanations;
- candidate lists.

Output only the query.""",

    "moderate_compression_v1": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Compress the original question and `summary_1` into a focused keyword query, but keep enough context for disambiguation.

Procedure:
1. Identify the known anchor from `summary_1`.
2. Identify the unresolved relation or target from the question.
3. Produce a 5 to 12 word query containing both.

Rules:
- Prefer names, titles, and relation-bearing nouns/verbs.
- Keep distinctive modifiers if they disambiguate the entity.
- Do not write a complete sentence.
- Do not make the query shorter than needed.
- Do not include irrelevant background from `summary_1`.

Output only the query.""",

    "query_expansion_safe_v1": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Produce a safe expanded keyword query for BM25 retrieval.

Include multiple useful lexical surfaces when they are available:
- canonical entity name or title;
- short alias or alternate title from `summary_1`;
- relation words from the question;
- expected answer type.

The query may contain several keywords rather than a minimal phrase. Prefer retrieval robustness over extreme brevity.

Rules:
- Do not invent aliases or facts not supported by `question` or `summary_1`.
- Do not output a full explanatory sentence.
- Do not output multiple separate queries.
- Do not include reasoning.

Output only the query.""",
}


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


def load_base_prompts_from_condition_dir(condition_dir: Path) -> tuple[dict[str, str], str]:
    """
    Reconstruct the old/basic hop2 baseline from an existing condition dir.

    The condition dir is only used as a convenient source for:
    - prompt_candidate.json: full prompt dict
    - proposal_event.json: old_instruction for create_query_hop2.predict
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

    base_prompts = dict(prompts)
    base_prompts[HOP2_COMPONENT] = old_hop2

    return base_prompts, old_hop2


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
            phase="hop2_candidate_search_dev300",
            split=args.eval_split,
            iteration=None,
            candidate_id=None,
            parent_candidate_id=None,
            updated_component="hop2_candidate_search",
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


def build_conditions(base_prompts: dict[str, str]) -> dict[str, dict[str, str]]:
    conditions: dict[str, dict[str, str]] = {}

    # Reference: original/base final.
    conditions["gepa_best"] = dict(base_prompts)

    # Main semi-optimized downstream baseline.
    final_only = dict(base_prompts)
    final_only[FINAL_COMPONENT] = MANUAL_FINAL_PROMPT
    conditions["final_manual_only"] = final_only

    # Hop2 candidates, all evaluated with manual best final fixed.
    for name, hop2_prompt in HOP2_CANDIDATES.items():
        prompts = dict(base_prompts)
        prompts[HOP2_COMPONENT] = hop2_prompt
        prompts[FINAL_COMPONENT] = MANUAL_FINAL_PROMPT
        conditions[name] = prompts

    return conditions


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()

    p.add_argument(
        "--source-condition-dir",
        type=Path,
        required=True,
        help=(
            "Any condition dir containing prompt_candidate.json and proposal_event.json. "
            "Used to reconstruct base/gepa hop2 via proposal_event.old_instruction."
        ),
    )

    p.add_argument("--output-root", type=Path, default=Path("outputs/hotpotqa_hop2_candidate_search"))
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

    base_prompts, old_hop2 = load_base_prompts_from_condition_dir(args.source_condition_dir)
    conditions = build_conditions(base_prompts)

    write_json(
        exp_dir / "config.json",
        {
            **vars(args),
            "source_condition_dir": str(args.source_condition_dir),
            "conditions": list(conditions.keys()),
            "hop2_component": HOP2_COMPONENT,
            "final_component": FINAL_COMPONENT,
            "base_hop2_instruction": old_hop2,
            "base_final_instruction": base_prompts[FINAL_COMPONENT],
            "manual_final_instruction": MANUAL_FINAL_PROMPT,
            "hop2_candidates": HOP2_CANDIDATES,
        },
    )

    aggregate: dict[str, Any] = {
        "exp_dir": str(exp_dir),
        "source_condition_dir": str(args.source_condition_dir),
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
                "description": f"Hop2 candidate search with manual final fixed: {condition_name}",
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
