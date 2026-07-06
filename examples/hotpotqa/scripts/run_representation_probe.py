#!/usr/bin/env python3
"""
Representation probe for HotpotQA GEPA traces.

This script:
1. Reads an existing GEPA run, e.g. outputs/hotpotqa2.
2. Selects create_query_hop2.predict feedback pairs from analysis/feedback_examples.jsonl.
3. Converts the same pairs into proposer-facing representations.
4. Uses InstructionProposalSignature to generate a new hop2 instruction.
5. Injects only that hop2 instruction into a base candidate.
6. Evaluates the resulting candidate on the fixed HotpotQA split.
7. Saves all probe outputs under a separate output root.

Main usage:
    # Group A: reversible representations only
    python examples/hotpotqa/scripts/run_representation_probe.py \
      --source-run outputs/hotpotqa2 \
      --output-root outputs/hotpotqa_representation_probe \
      --exp-name exp_A_reversible_seed_retrieval_failure_n3 \
      --base-candidate seed \
      --representation-group reversible \
      --pair-filter retrieval_failure \
      --num-pairs 3 \
      --env-file /home/jinwoo/gepa-official/.env \
      --proposer-model gpt-5-mini \
      --task-model openai/gpt-5-mini \
      --eval-split test \
      --train-size 100 \
      --val-size 100 \
      --test-size 100 \
      --seed 0 \
      --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \
      --num-threads 20 \
      --overwrite

    # Group B: diagnostic / non-reversible representations only
    python examples/hotpotqa/scripts/run_representation_probe.py \
      --source-run outputs/hotpotqa2 \
      --output-root outputs/hotpotqa_representation_probe \
      --exp-name exp_B_diagnostic_seed_retrieval_failure_n3 \
      --base-candidate seed \
      --representation-group diagnostic \
      --pair-filter retrieval_failure \
      --num-pairs 3 \
      --env-file /home/jinwoo/gepa-official/.env \
      --proposer-model gpt-5-mini \
      --task-model openai/gpt-5-mini \
      --eval-split test \
      --train-size 100 \
      --val-size 100 \
      --test-size 100 \
      --seed 0 \
      --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \
      --num-threads 20 \
      --overwrite
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

from tqdm.auto import tqdm

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"

# Prefer the local repository code over any installed `gepa` package in site-packages.
for _path in (str(ROOT), str(SRC)):
    if _path in sys.path:
        sys.path.remove(_path)

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

import dspy  # noqa: E402
from openai import OpenAI  # noqa: E402

from gepa.strategies.instruction_proposal import InstructionProposalSignature  # noqa: E402
from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter  # noqa: E402
from examples.hotpotqa.data import load_hotpot_splits  # noqa: E402
from examples.hotpotqa.feedback import feedback_fn_map  # noqa: E402
from examples.hotpotqa.metric import answer_exact_match  # noqa: E402
from examples.hotpotqa.program import HotpotMultiHop  # noqa: E402
from examples.hotpotqa.retriever import set_retriever_dir  # noqa: E402


TARGET_COMPONENT = "create_query_hop2.predict"


# ============================================================
# Basic IO
# ============================================================


def load_env_file(path: str | Path) -> None:
    """Minimal .env loader. Does not override existing env vars."""
    path = Path(path)
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value


def read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, obj: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not overwrite:
            raise FileExistsError(
                f"Output path already exists: {path}\n"
                f"Use --overwrite to replace it."
            )
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def load_candidate(path: str | Path) -> dict[str, str]:
    obj = read_json(path)

    if isinstance(obj, dict) and "prompts" in obj:
        prompts = obj["prompts"]
    else:
        prompts = obj

    if not isinstance(prompts, dict):
        raise TypeError(f"Candidate file does not contain a prompt dict: {path}")

    bad = {k: type(v).__name__ for k, v in prompts.items() if not isinstance(v, str)}
    if bad:
        raise TypeError(f"Non-string prompt values in candidate: {bad}")

    return dict(prompts)


def save_candidate(path: str | Path, name: str, prompts: dict[str, str]) -> None:
    write_json(
        path,
        {
            "name": name,
            "prompts": prompts,
        },
    )


def maybe_read_source_summary(source_run: Path) -> dict[str, Any] | None:
    summary_path = source_run / "summary.json"
    if not summary_path.exists():
        return None
    try:
        return read_json(summary_path)
    except Exception:
        return None


# ============================================================
# DSPy / OpenAI setup
# ============================================================


def make_dspy_lm(
    model: str,
    api_key: str | None = None,
    api_base: str | None = None,
    temperature: float | None = 0.0,
    max_tokens: int | None = 1024,
):
    """Small wrapper around dspy.LM to tolerate local version differences."""
    kwargs: dict[str, Any] = {}

    # DSPy enforces reasoning-model constraints for OpenAI GPT-5-family models.
    # Avoid ValueError from dspy.LM(openai/gpt-5*, temperature=0, max_tokens<16000).
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

    try:
        return dspy.LM(model, **kwargs)
    except TypeError:
        minimal_kwargs: dict[str, Any] = {}
        if api_key:
            minimal_kwargs["api_key"] = api_key
        if api_base:
            minimal_kwargs["api_base"] = api_base
        return dspy.LM(model, **minimal_kwargs)


def configure_task_lm(args: argparse.Namespace) -> None:
    api_key = args.task_api_key or os.environ.get("OPENAI_API_KEY")
    lm = make_dspy_lm(
        model=args.task_model,
        api_key=api_key,
        api_base=args.task_api_base,
        temperature=args.task_temperature,
        max_tokens=args.task_max_tokens,
    )
    dspy.configure(lm=lm)


def call_openai_proposer(
    *,
    model: str,
    prompt: str,
    temperature: float | None,
    max_tokens: int,
) -> str:
    """
    Call OpenAI directly for the proposer.

    The script uses OpenAI only for the representation -> instruction proposal step.
    The actual HotpotQA task model is configured through DSPy separately.
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Prefer Chat Completions because it is simple and compatible with many local
    # OpenAI-wrapper setups. Fallback logic handles model-specific argument issues.
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    if temperature is not None:
        kwargs["temperature"] = temperature

    try:
        resp = client.chat.completions.create(
            **kwargs,
            max_completion_tokens=max_tokens,
        )
    except Exception as e1:
        msg = str(e1).lower()

        if "temperature" in msg:
            kwargs.pop("temperature", None)

        try:
            resp = client.chat.completions.create(
                **kwargs,
                max_completion_tokens=max_tokens,
            )
        except Exception:
            resp = client.chat.completions.create(
                **kwargs,
                max_tokens=max_tokens,
            )

    content = resp.choices[0].message.content
    if content:
        return content

    finish_reason = getattr(resp.choices[0], "finish_reason", None)
    retry_tokens = max(max_tokens * 2, 16000)

    print(
        "[warn] proposer returned empty content; "
        f"finish_reason={finish_reason}; retrying with max_completion_tokens={retry_tokens}",
        file=sys.stderr,
    )

    retry_kwargs = dict(kwargs)
    retry_kwargs.pop("temperature", None)

    try:
        resp2 = client.chat.completions.create(
            **retry_kwargs,
            max_completion_tokens=retry_tokens,
        )
    except Exception:
        resp2 = client.chat.completions.create(
            **retry_kwargs,
            max_tokens=retry_tokens,
        )

    content2 = resp2.choices[0].message.content
    if content2:
        return content2

    finish_reason2 = getattr(resp2.choices[0], "finish_reason", None)
    raise RuntimeError(
        "Proposer returned empty content after retry. "
        f"first_finish_reason={finish_reason}, retry_finish_reason={finish_reason2}, "
        f"model={model}, initial_max_tokens={max_tokens}, retry_tokens={retry_tokens}"
    )


def propose_instruction(
    *,
    base_instruction: str,
    dataset_with_feedback: list[dict[str, Any]],
    proposer_model: str,
    proposer_temperature: float | None,
    proposer_max_tokens: int,
) -> dict[str, Any]:
    input_dict = {
        "current_instruction_doc": base_instruction,
        "dataset_with_feedback": dataset_with_feedback,
        "prompt_template": None,
    }

    rendered = InstructionProposalSignature.prompt_renderer(input_dict)
    if not isinstance(rendered, str):
        raise TypeError("This script currently expects text-only proposer prompts.")

    raw_lm_output = call_openai_proposer(
        model=proposer_model,
        prompt=rendered,
        temperature=proposer_temperature,
        max_tokens=proposer_max_tokens,
    )

    extracted = InstructionProposalSignature.output_extractor(raw_lm_output)
    new_instruction = extracted["new_instruction"]

    return {
        "reflection_prompt": rendered,
        "raw_lm_output": raw_lm_output,
        "raw_contains_think": "<think>" in raw_lm_output,
        "new_instruction": new_instruction,
        "new_instruction_contains_think": "<think>" in new_instruction,
    }


# ============================================================
# Pair selection
# ============================================================


def is_retrieval_failure(row: dict[str, Any]) -> bool:
    missing = row.get("missing_titles_after_hop2") or []
    recall = row.get("support_recall_total", 1.0)

    try:
        recall_val = float(recall)
    except (TypeError, ValueError):
        recall_val = 1.0

    return bool(missing) or recall_val < 1.0


def select_source_pairs(
    *,
    source_run: Path,
    target_component: str,
    pair_filter: str,
    num_pairs: int | None,
    shuffle: bool,
    seed: int,
) -> list[dict[str, Any]]:
    feedback_path = source_run / "analysis" / "feedback_examples.jsonl"
    if not feedback_path.exists():
        raise FileNotFoundError(f"feedback_examples.jsonl not found: {feedback_path}")

    rows = read_jsonl(feedback_path)
    rows = [r for r in rows if r.get("component") == target_component]

    if pair_filter == "all":
        pass
    elif pair_filter == "retrieval_failure":
        rows = [r for r in rows if is_retrieval_failure(r)]
    elif pair_filter == "score0":
        rows = [r for r in rows if float(r.get("module_score", 0.0)) == 0.0]
    else:
        raise ValueError(f"Unknown pair_filter: {pair_filter}")

    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(rows)

    if num_pairs is not None:
        rows = rows[:num_pairs]

    if not rows:
        raise ValueError(
            f"No source pairs selected. component={target_component}, "
            f"pair_filter={pair_filter}, num_pairs={num_pairs}"
        )

    return rows


# ============================================================
# Shared row helpers
# ============================================================


def _as_list(x: Any) -> list[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _predictor_inputs(row: dict[str, Any]) -> dict[str, Any]:
    x = row.get("predictor_inputs") or {}
    return x if isinstance(x, dict) else {}


def _predictor_outputs(row: dict[str, Any]) -> dict[str, Any]:
    x = row.get("predictor_outputs") or {}
    return x if isinstance(x, dict) else {}


def _generated_query(row: dict[str, Any]) -> str:
    return str(_predictor_outputs(row).get("query", ""))


def _generated_reasoning(row: dict[str, Any]) -> str:
    return str(_predictor_outputs(row).get("reasoning", ""))


def _question(row: dict[str, Any]) -> str:
    return str(_predictor_inputs(row).get("question", ""))


def _summary_1(row: dict[str, Any]) -> str:
    return str(_predictor_inputs(row).get("summary_1", ""))


def _simple_terms(text: str) -> list[str]:
    terms = re.findall(r"[A-Za-z0-9À-ÿ][A-Za-z0-9À-ÿ'’.\-]*", text)
    stop = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "for",
        "with",
        "what",
        "which",
        "who",
        "when",
        "where",
        "how",
        "is",
        "are",
        "was",
        "were",
        "do",
        "does",
        "did",
        "given",
        "that",
        "from",
        "provided",
        "summary",
        "summaries",
        "both",
        "share",
        "shared",
        "same",
        "compare",
        "comparison",
    }

    out: list[str] = []
    for t in terms:
        if t.lower() not in stop:
            out.append(t)
    return out



# ============================================================
# GEPA-style representation baseline
# ============================================================


def build_gepa_style_raw_feedback_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    GEPA-style baseline representation.

    This mirrors the standard GEPA reflective example shape:
    Inputs / Generated Outputs / Feedback.

    It is the proper representation baseline for this probe:
    same pairs, same proposer, same target component, but GEPA's original
    proposer-facing format.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Inputs": r.get("predictor_inputs", {}),
                "Generated Outputs": r.get("predictor_outputs", {}),
                "Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


# ============================================================
# Group A: reversible representations
# ============================================================


def build_json_reversible_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group A.
    Reversible JSON layout.

    Constraint:
    - Do not add diagnosis.
    - Do not add a better query.
    - Do not add desired behavior.
    - Only reorganize the logged case fields.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Case Record": {
                    "component": r.get("component"),
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                    "generated_reasoning": _generated_reasoning(r),
                    "generated_query": _generated_query(r),
                    "gold_answer": r.get("gold_answer"),
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "hop1_titles": r.get("hop1_titles", []),
                    "hop2_titles": r.get("hop2_titles", []),
                    "support_recall_hop1": r.get("support_recall_hop1"),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "module_score": r.get("module_score"),
                    "feedback_text": r.get("feedback_text", ""),
                }
            }
        )

    return dataset


def build_state_transition_reversible_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group A.
    Reversible state-transition layout.

    Coordinate transform:
    input state -> before hop2 -> hop2 action -> after hop2.

    This does not prescribe a better action.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Input State": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                },
                "Before Hop2": {
                    "hop1_titles": r.get("hop1_titles", []),
                    "support_recall_hop1": r.get("support_recall_hop1"),
                },
                "Hop2 Action": {
                    "generated_reasoning": _generated_reasoning(r),
                    "generated_query": _generated_query(r),
                },
                "After Hop2": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset




def build_io_trace_reversible_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group A.
    Reversible function-call trace layout.

    Coordinate transform:
    function identity -> inputs -> generated output -> observed downstream outcome.

    This emphasizes the create_query_hop2.predict interface without adding
    diagnosis, better query targets, or BM25-specific prescriptions.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Function Call": {
                    "component": r.get("component"),
                    "function": "create_query_hop2.predict",
                    "input_fields": ["question", "summary_1"],
                    "output_fields": ["reasoning", "query"],
                },
                "Inputs": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                },
                "Generated Output": {
                    "reasoning": _generated_reasoning(r),
                    "query": _generated_query(r),
                },
                "Downstream Observations": {
                    "gold_answer": r.get("gold_answer"),
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "hop1_titles": r.get("hop1_titles", []),
                    "hop2_titles": r.get("hop2_titles", []),
                    "support_recall_hop1": r.get("support_recall_hop1"),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_title_set_reversible_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group A.
    Reversible title-set relation layout.

    Coordinate transform:
    gold support title set, hop1 retrieved title set, hop2 retrieved title set,
    and remaining missing title set are displayed as set-like records.

    This highlights retrieval structure, but does not add a diagnosis or a
    recommended query.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Question Context": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                    "generated_query": _generated_query(r),
                    "generated_reasoning": _generated_reasoning(r),
                },
                "Title Sets": {
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "hop1_retrieved_titles": r.get("hop1_titles", []),
                    "hop2_retrieved_titles": r.get("hop2_titles", []),
                    "new_support_titles_retrieved_by_hop2": r.get("new_support_titles_hop2", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                },
                "Recall Scalars": {
                    "support_recall_hop1": r.get("support_recall_hop1"),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


# ============================================================
# Group B: diagnostic / non-reversible representations
# ============================================================


def build_contrastive_query_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group B.
    Non-reversible contrastive representation.

    Adds failure-to-action mapping:
    generated query -> observed failure -> better BM25 target.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        missing = _as_list(r.get("missing_titles_after_hop2"))
        new_support = _as_list(r.get("new_support_titles_hop2"))

        dataset.append(
            {
                "Case": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                },
                "Generated Query": _generated_query(r),
                "Observed Retrieval Outcome": {
                    "hop1_titles": r.get("hop1_titles", []),
                    "hop2_titles": r.get("hop2_titles", []),
                    "missing_titles_after_hop2": missing,
                    "new_support_titles_hop2": new_support,
                    "support_recall_total": r.get("support_recall_total"),
                },
                "Contrastive Interpretation": {
                    "bad_query_behavior": (
                        "The generated query did not retrieve the remaining support title(s)."
                        if missing
                        else "The logged case does not expose a remaining missing support title."
                    ),
                    "better_bm25_target": missing,
                    "pattern": (
                        "For BM25, the hop2 query should directly target the missing page/entity title "
                        "rather than restating the original question or mixing already-known and missing evidence."
                    ),
                },
            }
        )

    return dataset


def build_hop2_decision_trace_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group B.
    Non-reversible decision-trace representation.

    Adds latent reasoning decomposition:
    known evidence -> missing evidence -> BM25 target -> query shape.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        missing = _as_list(r.get("missing_titles_after_hop2"))

        dataset.append(
            {
                "Problem": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                },
                "Hop2 Decision Trace": {
                    "known_evidence_signal": (
                        "Use summary_1 to identify what evidence has already been surfaced."
                    ),
                    "missing_evidence_signal": missing,
                    "bm25_target": missing,
                    "generated_query": _generated_query(r),
                    "observed_hop2_titles": r.get("hop2_titles", []),
                },
                "Reasoning Pattern to Extract": {
                    "step_1": "Infer what support evidence is still missing after summary_1.",
                    "step_2": "Map that missing evidence to a likely Wikipedia title, entity, alias, or attribute phrase.",
                    "step_3": "Emit a short lexical BM25 query centered on that target.",
                    "step_4": "Avoid full-question restatement when a specific missing entity/title is available.",
                },
            }
        )

    return dataset


def build_bm25_signal_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group B.
    Strong BM25-signal representation.

    Adds lexical analysis of the generated query.
    This is the strongest intervention among the current representations.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        query = _generated_query(r)
        query_terms = _simple_terms(query)
        missing = _as_list(r.get("missing_titles_after_hop2"))
        hop1_titles = _as_list(r.get("hop1_titles"))

        known_title_mentions = []
        for title in hop1_titles:
            title_s = str(title)
            if title_s and title_s.lower() in query.lower():
                known_title_mentions.append(title_s)

        dataset.append(
            {
                "Case": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                },
                "BM25 Query Signal": {
                    "generated_query": query,
                    "query_terms": query_terms,
                    "missing_title_anchor": missing,
                    "already_retrieved_title_mentions_in_query": known_title_mentions,
                    "hop2_titles_retrieved": r.get("hop2_titles", []),
                },
                "BM25-Oriented Diagnosis": {
                    "main_issue": (
                        "The query failed to place enough lexical weight on the missing support title."
                        if missing
                        else "No missing support title is available for a direct BM25 diagnosis."
                    ),
                    "preferred_query_shape": (
                        "short query using the missing title/entity/alias and minimal attribute words"
                    ),
                    "avoid_query_shape": (
                        "long explanatory question, full original question, or generic comparison wording"
                    ),
                },
            }
        )

    return dataset



# ============================================================
# Group B: function-aware contextual / BM25-aware representations
# ============================================================


def _dedup_preserve_order(xs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _lower_simple_terms(text: str) -> list[str]:
    return _dedup_preserve_order([t.lower() for t in _simple_terms(text)])


def _title_terms(titles: Any) -> list[str]:
    terms: list[str] = []
    for title in _as_list(titles):
        terms.extend(_lower_simple_terms(str(title)))
    return _dedup_preserve_order(terms)


def _term_overlap(left: list[str], right: list[str]) -> list[str]:
    right_set = set(right)
    return [x for x in left if x in right_set]


def build_bm25_contract_surface_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group B.
    BM25-aware function contract representation.

    Converts the trace into a downstream-interface contract:
    create_query_hop2.predict emits only a query string, and the immediate
    consumer is a BM25 retriever that sees only lexical surface tokens.

    This does not directly prescribe a replacement query.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Function Contract": {
                    "function": "create_query_hop2.predict",
                    "input_fields": ["question", "summary_1"],
                    "output_field": "query",
                    "downstream_consumer": "BM25 retriever",
                    "consumer_visible_surface": "query string tokens only",
                },
                "Available Inputs": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                },
                "Produced Surface": {
                    "reasoning": _generated_reasoning(r),
                    "query": _generated_query(r),
                },
                "BM25 Response": {
                    "hop2_retrieved_titles": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                },
                "Coverage Record": {
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "hop1_titles": r.get("hop1_titles", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "support_recall_hop1": r.get("support_recall_hop1"),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_bm25_lexical_diagnostic_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group B.
    Strong BM25-aware lexical-surface representation.

    Adds deterministic lexical features from the logged query and title sets:
    query terms, title terms, and overlap patterns.

    The added features are derived from the raw trace, not externally annotated
    oracle queries.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        query = _generated_query(r)
        query_terms = _lower_simple_terms(query)

        gold_titles = r.get("gold_support_titles", [])
        hop1_titles = r.get("hop1_titles", [])
        hop2_titles = r.get("hop2_titles", [])
        missing_titles = r.get("missing_titles_after_hop2", [])

        gold_terms = _title_terms(gold_titles)
        hop1_terms = _title_terms(hop1_titles)
        hop2_terms = _title_terms(hop2_titles)
        missing_terms = _title_terms(missing_titles)

        dataset.append(
            {
                "Function Contract": {
                    "function": "create_query_hop2.predict",
                    "input_fields": ["question", "summary_1"],
                    "output_field": "query",
                    "downstream_consumer": "BM25 retriever",
                    "consumer_visible_surface": "lexical overlap between query terms and indexed document/title terms",
                },
                "Available Inputs": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                },
                "Generated Query Surface": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                    "query_terms": query_terms,
                },
                "Title-Surface Terms": {
                    "gold_support_titles": gold_titles,
                    "gold_support_title_terms": gold_terms,
                    "hop1_titles": hop1_titles,
                    "hop1_title_terms": hop1_terms,
                    "hop2_titles": hop2_titles,
                    "hop2_title_terms": hop2_terms,
                    "missing_titles_after_hop2": missing_titles,
                    "missing_title_terms": missing_terms,
                },
                "Lexical Overlap Record": {
                    "query_overlap_with_hop1_title_terms": _term_overlap(query_terms, hop1_terms),
                    "query_overlap_with_hop2_title_terms": _term_overlap(query_terms, hop2_terms),
                    "query_overlap_with_gold_support_title_terms": _term_overlap(query_terms, gold_terms),
                    "query_overlap_with_missing_title_terms": _term_overlap(query_terms, missing_terms),
                },
                "Retrieval Outcome": {
                    "support_recall_hop1": r.get("support_recall_hop1"),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_function_bottleneck_transduction_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group B.
    Function-aware transduction representation.

    Reframes create_query_hop2.predict as a bottleneck transducer:
    it must convert question + summary_1 into a compact retrieval-facing query.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Transduction Problem": {
                    "function": "create_query_hop2.predict",
                    "input_channel": ["question", "summary_1"],
                    "compressed_output_channel": "query",
                    "external_environment": "retriever",
                },
                "Input Channel Contents": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                    "hop1_titles": r.get("hop1_titles", []),
                },
                "Transduced Output": {
                    "reasoning": _generated_reasoning(r),
                    "query": _generated_query(r),
                },
                "Environment Response": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                },
                "Coverage State": {
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_evidence_state_machine_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group B.
    Function-aware state-machine representation.

    Reframes hop2 query generation as an action that changes evidence coverage
    from a partial support state to a post-retrieval state.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "State Machine": {
                    "state_s1": "partial evidence state after hop1",
                    "action_a2": "generated hop2 query",
                    "transition_system": "retriever",
                    "state_s2": "post-hop2 retrieved evidence state",
                    "terminal_objective": "cover gold support titles",
                },
                "State S1": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                    "hop1_titles": r.get("hop1_titles", []),
                    "support_recall_hop1": r.get("support_recall_hop1"),
                },
                "Action A2": {
                    "reasoning": _generated_reasoning(r),
                    "query": _generated_query(r),
                },
                "State S2": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                },
                "Uncovered Terminal State": {
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_bridge_attempt_context_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group B.
    Light contextual control.

    Reframes the hop2 query as a bridge attempt from the current partial context
    to additional supporting evidence.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Bridge Context": {
                    "question": _question(r),
                    "current_partial_context": _summary_1(r),
                    "known_titles_before_bridge": r.get("hop1_titles", []),
                },
                "Bridge Attempt": {
                    "reasoning": _generated_reasoning(r),
                    "query": _generated_query(r),
                },
                "Bridge Landing": {
                    "retrieved_titles_after_bridge": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                },
                "Reference Coverage": {
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_partial_context_expansion_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group B.
    Light contextual control.

    Reframes hop2 as expansion from partial context to retrieved context.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Partial Context Before Hop2": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                    "hop1_titles": r.get("hop1_titles", []),
                },
                "Expansion Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": _generated_query(r),
                },
                "Expanded Context After Hop2": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                },
                "Reference Full Context": {
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                },
                "Coverage Scalars": {
                    "support_recall_hop1": r.get("support_recall_hop1"),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset





# ============================================================
# Group C: gradient-skeleton function-aware representations
# ============================================================


def _c_dedup_preserve_order(xs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _c_terms(text: Any) -> list[str]:
    return _c_dedup_preserve_order([t.lower() for t in _simple_terms(str(text))])


def _c_title_terms(titles: Any) -> list[str]:
    terms: list[str] = []
    for title in _as_list(titles):
        terms.extend(_c_terms(str(title)))
    return _c_dedup_preserve_order(terms)


def _c_overlap(left: list[str], right: list[str]) -> list[str]:
    right_set = set(right)
    return [x for x in left if x in right_set]


def _c_raw_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9À-ÿ][A-Za-z0-9À-ÿ'’.\-]*", str(text)))


def _c_contains_any(text: str, patterns: list[str]) -> bool:
    text_l = str(text).lower()
    return any(p.lower() in text_l for p in patterns)


def _c_question_restated(query: str, question: str) -> bool:
    query_terms = _c_terms(query)
    question_terms = _c_terms(question)
    if not query_terms or not question_terms:
        return False

    overlap = _c_overlap(query_terms, question_terms)
    overlap_ratio = len(overlap) / max(1, len(query_terms))

    return (
        _c_raw_word_count(query) >= 9
        and overlap_ratio >= 0.60
    ) or str(query).strip().endswith("?")


def _c_focus_estimate(
    *,
    query_terms: list[str],
    missing_terms: list[str],
    known_terms: list[str],
    question_terms: list[str],
) -> str:
    missing_overlap = _c_overlap(query_terms, missing_terms)
    known_overlap = _c_overlap(query_terms, known_terms)
    question_overlap = _c_overlap(query_terms, question_terms)
    leading_terms = query_terms[:4]

    missing_in_lead = bool(_c_overlap(leading_terms, missing_terms))
    known_in_lead = bool(_c_overlap(leading_terms, known_terms))

    if missing_overlap and (missing_in_lead or len(missing_overlap) >= len(known_overlap)):
        return "missing-target-focused"
    if known_overlap and not missing_overlap:
        return "known-target-focused"
    if len(query_terms) >= 10 and len(question_overlap) >= max(3, len(query_terms) // 2):
        return "generic-question-focused"
    if missing_overlap or known_overlap:
        return "mixed-support-focused"
    return "unclear-or-generic"


def _c_capitalized_spans(text: str) -> list[str]:
    spans = re.findall(
        r"\b[A-Z][A-Za-z0-9'’.\-]*(?:\s+[A-Z][A-Za-z0-9'’.\-]*){0,5}",
        str(text),
    )
    bad = {
        "The", "A", "An", "This", "That", "These", "Those",
        "Given", "Question", "Summary", "Answer", "What", "Which",
        "Who", "When", "Where", "How"
    }
    spans = [s.strip() for s in spans if s.strip() and s.strip() not in bad]
    return _c_dedup_preserve_order(spans)


def _c_anchor_candidates(question: str, summary_1: str) -> list[str]:
    return _c_capitalized_spans(str(question) + " " + str(summary_1))


def _c_anchor_preservation(anchors: list[str], query: str) -> dict[str, Any]:
    query_l = str(query).lower()

    preserved_exact = [a for a in anchors if a.lower() in query_l]
    omitted_exact = [a for a in anchors if a.lower() not in query_l]

    anchor_terms: list[str] = []
    for a in anchors:
        anchor_terms.extend(_c_terms(a))
    anchor_terms = _c_dedup_preserve_order(anchor_terms)

    query_terms = _c_terms(query)

    return {
        "anchor_candidates": anchors,
        "anchors_preserved_as_exact_spans": preserved_exact,
        "anchors_not_preserved_as_exact_spans": omitted_exact,
        "anchor_terms": anchor_terms,
        "anchor_terms_preserved_in_query": _c_overlap(anchor_terms, query_terms),
    }


def build_bm25_missing_target_mainness_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group C.
    BM25-aware gradient-skeleton representation.

    Exposes whether the generated query made the still-missing support surface
    the main lexical focus, rather than spending the query on already-known
    support or generic question wording.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        query = _generated_query(r)
        question = _question(r)
        summary_1 = _summary_1(r)

        query_terms = _c_terms(query)
        question_terms = _c_terms(question)

        missing_titles = r.get("missing_titles_after_hop2", [])
        hop1_titles = r.get("hop1_titles", [])
        hop2_titles = r.get("hop2_titles", [])
        gold_titles = r.get("gold_support_titles", [])

        missing_terms = _c_title_terms(missing_titles)
        known_terms = _c_title_terms(hop1_titles)
        retrieved_terms = _c_title_terms(hop2_titles)
        gold_terms = _c_title_terms(gold_titles)

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "input_fields": ["question", "summary_1"],
                    "output_field": "query",
                    "downstream_consumer": "BM25 retriever",
                    "gradient_axis": "make the still-missing support surface the main lexical focus of the query",
                },
                "Inputs": {
                    "question": question,
                    "summary_1": summary_1,
                },
                "Generated Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                    "query_terms": query_terms,
                    "query_leading_terms": query_terms[:5],
                },
                "Support Surfaces": {
                    "gold_support_titles": gold_titles,
                    "gold_support_title_terms": gold_terms,
                    "already_known_hop1_titles": hop1_titles,
                    "already_known_title_terms": known_terms,
                    "hop2_retrieved_titles": hop2_titles,
                    "hop2_retrieved_title_terms": retrieved_terms,
                    "still_missing_titles_after_hop2": missing_titles,
                    "still_missing_title_terms": missing_terms,
                },
                "Mainness Indicators": {
                    "query_overlap_with_missing_title_terms": _c_overlap(query_terms, missing_terms),
                    "query_overlap_with_already_known_title_terms": _c_overlap(query_terms, known_terms),
                    "query_overlap_with_retrieved_title_terms": _c_overlap(query_terms, retrieved_terms),
                    "query_overlap_with_question_terms": _c_overlap(query_terms, question_terms),
                    "query_focus_estimate": _c_focus_estimate(
                        query_terms=query_terms,
                        missing_terms=missing_terms,
                        known_terms=known_terms,
                        question_terms=question_terms,
                    ),
                },
                "Retrieval Outcome": {
                    "support_recall_hop1": r.get("support_recall_hop1"),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_bm25_manual_clause_violation_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group C.
    Strong BM25-aware gradient-skeleton representation.

    Converts the observed query into clause-level behavioral diagnostics that
    mirror the discovered manual prompt dimensions without directly providing
    a replacement query.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        query = _generated_query(r)
        question = _question(r)
        summary_1 = _summary_1(r)

        query_terms = _c_terms(query)
        question_terms = _c_terms(question)

        hop1_titles = r.get("hop1_titles", [])
        missing_titles = r.get("missing_titles_after_hop2", [])
        gold_titles = r.get("gold_support_titles", [])

        known_terms = _c_title_terms(hop1_titles)
        missing_terms = _c_title_terms(missing_titles)
        gold_terms = _c_title_terms(gold_titles)

        missing_overlap = _c_overlap(query_terms, missing_terms)
        known_overlap = _c_overlap(query_terms, known_terms)

        anchors = _c_anchor_candidates(question, summary_1)
        anchor_record = _c_anchor_preservation(anchors, query)

        token_count = _c_raw_word_count(query)
        restates_question = _c_question_restated(query, question)
        long_or_explanatory = (
            token_count > 12
            or _c_contains_any(
                query,
                [
                    "because",
                    "based on",
                    "according to",
                    "given that",
                    "which of",
                    "what is",
                    "who is",
                    "where is",
                    "compare",
                    "comparison",
                ],
            )
        )

        missing_main_focus = bool(missing_overlap) and (
            len(missing_overlap) >= len(known_overlap)
            or bool(_c_overlap(query_terms[:4], missing_terms))
        )

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "input_fields": ["question", "summary_1"],
                    "output_field": "query",
                    "downstream_consumer": "BM25 retriever",
                    "gradient_axes": [
                        "missing target should be the main lexical focus",
                        "canonical anchors should be preserved",
                        "query should be short and disambiguating",
                        "full-question restatement should be avoided",
                        "already-known entities should not dominate the query",
                        "long explanations/background should be avoided",
                    ],
                },
                "Inputs": {
                    "question": question,
                    "summary_1": summary_1,
                },
                "Observed Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                    "query_terms": query_terms,
                    "token_count": token_count,
                },
                "Reference Surfaces": {
                    "gold_support_titles": gold_titles,
                    "gold_support_title_terms": gold_terms,
                    "already_known_hop1_titles": hop1_titles,
                    "already_known_title_terms": known_terms,
                    "still_missing_titles_after_hop2": missing_titles,
                    "still_missing_title_terms": missing_terms,
                },
                "Clause-Level Diagnostics": {
                    "missing_target_is_main_focus": missing_main_focus,
                    "preserves_canonical_anchor": (
                        bool(anchor_record["anchors_preserved_as_exact_spans"])
                        if anchors
                        else "unknown"
                    ),
                    "uses_only_short_disambiguating_surface": 1 <= token_count <= 8,
                    "restates_full_question": restates_question,
                    "includes_already_known_entities": bool(known_overlap),
                    "includes_long_explanation_or_background": long_or_explanatory,
                },
                "Diagnostic Evidence": {
                    "query_overlap_with_missing_title_terms": missing_overlap,
                    "query_overlap_with_already_known_title_terms": known_overlap,
                    "query_overlap_with_gold_support_title_terms": _c_overlap(query_terms, gold_terms),
                    "query_overlap_with_question_terms": _c_overlap(query_terms, question_terms),
                    **anchor_record,
                },
                "Retrieval Outcome": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "support_recall_hop1": r.get("support_recall_hop1"),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_missing_target_slot_gradient_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group C.
    Gradient-slot representation for missing-target selection.

    Splits the trace into already-grounded support, still-uncovered support,
    generated query target, and observed retrieval result.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "input_fields": ["question", "summary_1"],
                    "output_field": "query",
                    "gradient_variable": "which entity, attribute, or relation remains to be searched after summary_1",
                },
                "Input State": {
                    "question": _question(r),
                    "summary_1": _summary_1(r),
                },
                "Already-Grounded Support": {
                    "hop1_titles": r.get("hop1_titles", []),
                    "support_recall_hop1": r.get("support_recall_hop1"),
                },
                "Still-Uncovered Support": {
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                },
                "Generated Query Target": {
                    "reasoning": _generated_reasoning(r),
                    "query": _generated_query(r),
                },
                "Observed Retrieval Result": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_known_vs_missing_query_allocation_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group C.
    Gradient-skeleton representation for lexical allocation.

    Shows whether query terms are allocated to already-known support surfaces,
    still-missing support surfaces, or generic question terms.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        query = _generated_query(r)
        question = _question(r)

        query_terms = _c_terms(query)
        question_terms = _c_terms(question)
        known_terms = _c_title_terms(r.get("hop1_titles", []))
        missing_terms = _c_title_terms(r.get("missing_titles_after_hop2", []))
        gold_terms = _c_title_terms(r.get("gold_support_titles", []))

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "output_field": "query",
                    "gradient_variable": "how the query's lexical mass is allocated between already-known and still-missing support",
                },
                "Inputs": {
                    "question": question,
                    "summary_1": _summary_1(r),
                },
                "Generated Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                    "query_terms": query_terms,
                },
                "Known-vs-Missing Surfaces": {
                    "already_known_hop1_titles": r.get("hop1_titles", []),
                    "already_known_title_terms": known_terms,
                    "still_missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "still_missing_title_terms": missing_terms,
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "gold_support_title_terms": gold_terms,
                },
                "Lexical Allocation": {
                    "query_terms_allocated_to_already_known_titles": _c_overlap(query_terms, known_terms),
                    "query_terms_allocated_to_missing_titles": _c_overlap(query_terms, missing_terms),
                    "query_terms_allocated_to_gold_support_titles": _c_overlap(query_terms, gold_terms),
                    "query_terms_shared_with_original_question": _c_overlap(query_terms, question_terms),
                    "query_terms_not_tied_to_known_missing_or_gold_titles": [
                        t for t in query_terms
                        if t not in set(known_terms + missing_terms + gold_terms)
                    ],
                },
                "Retrieval Outcome": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_query_compression_violation_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group C.
    Gradient-skeleton representation for query compression.

    Exposes whether the generated query behaves like a compressed BM25 search
    key or like a verbose natural-language question/explanation.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        query = _generated_query(r)
        question = _question(r)
        query_terms = _c_terms(query)

        shape = {
            "token_count": _c_raw_word_count(query),
            "query_terms": query_terms,
            "leading_terms": query_terms[:5],
            "ends_with_question_mark": str(query).strip().endswith("?"),
            "restates_full_question": _c_question_restated(query, question),
            "contains_explanatory_phrases": _c_contains_any(
                query,
                [
                    "because",
                    "according to",
                    "based on",
                    "given",
                    "therefore",
                    "in order to",
                    "which of",
                    "what is",
                    "who is",
                    "where is",
                ],
            ),
            "contains_candidate_list_markers": _c_contains_any(
                query,
                [" or ", " and ", ",", ";", " vs ", " versus "],
            ),
        }

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "output_field": "query",
                    "downstream_consumer": "BM25 retriever",
                    "gradient_variable": "compressed lexical search key versus verbose/full-question query",
                },
                "Inputs": {
                    "question": question,
                    "summary_1": _summary_1(r),
                },
                "Generated Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                },
                "Query Shape Diagnostics": shape,
                "Retrieval Outcome": {
                    "hop1_titles": r.get("hop1_titles", []),
                    "hop2_titles": r.get("hop2_titles", []),
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_canonical_anchor_preservation_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group C.
    Gradient-skeleton representation for canonical anchor preservation.

    Exposes whether title-like names, aliases, and qualifiers from question
    and summary_1 are preserved in the emitted BM25 query surface.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        question = _question(r)
        summary_1 = _summary_1(r)
        query = _generated_query(r)

        anchors = _c_anchor_candidates(question, summary_1)
        anchor_record = _c_anchor_preservation(anchors, query)

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "input_fields": ["question", "summary_1"],
                    "output_field": "query",
                    "downstream_consumer": "BM25 retriever",
                    "gradient_variable": "preserve canonical names, aliases, and domain qualifiers as lexical anchors",
                },
                "Inputs": {
                    "question": question,
                    "summary_1": summary_1,
                },
                "Anchor Candidates from Inputs": anchor_record,
                "Generated Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                    "query_terms": _c_terms(query),
                },
                "Support / Retrieval Context": {
                    "hop1_titles": r.get("hop1_titles", []),
                    "hop2_titles": r.get("hop2_titles", []),
                    "gold_support_titles": r.get("gold_support_titles", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                },
                "Retrieval Outcome": {
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset



# ============================================================
# Group D: advanced gradient-skeleton representations
# ============================================================


def _d_dedup_preserve_order(xs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _d_terms(text: Any) -> list[str]:
    return _d_dedup_preserve_order([t.lower() for t in _simple_terms(str(text))])


def _d_title_terms(titles: Any) -> list[str]:
    terms: list[str] = []
    for title in _as_list(titles):
        terms.extend(_d_terms(str(title)))
    return _d_dedup_preserve_order(terms)


def _d_overlap(left: list[str], right: list[str]) -> list[str]:
    right_set = set(right)
    return [x for x in left if x in right_set]


def _d_raw_word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9À-ÿ][A-Za-z0-9À-ÿ'’.\-]*", str(text)))


def _d_contains_any(text: str, patterns: list[str]) -> bool:
    text_l = str(text).lower()
    return any(p.lower() in text_l for p in patterns)


def _d_question_restated(query: str, question: str) -> bool:
    query_terms = _d_terms(query)
    question_terms = _d_terms(question)
    if not query_terms or not question_terms:
        return False
    overlap = _d_overlap(query_terms, question_terms)
    overlap_ratio = len(overlap) / max(1, len(query_terms))
    return (
        _d_raw_word_count(query) >= 9
        and overlap_ratio >= 0.60
    ) or str(query).strip().endswith("?")


def _d_capitalized_spans(text: str) -> list[str]:
    spans = re.findall(
        r"\b[A-Z][A-Za-z0-9'’.\-]*(?:\s+[A-Z][A-Za-z0-9'’.\-]*){0,5}",
        str(text),
    )
    bad = {
        "The", "A", "An", "This", "That", "These", "Those",
        "Given", "Question", "Summary", "Answer", "What", "Which",
        "Who", "When", "Where", "How", "Input", "Output"
    }
    spans = [s.strip() for s in spans if s.strip() and s.strip() not in bad]
    return _d_dedup_preserve_order(spans)


def _d_anchor_candidates(question: str, summary_1: str) -> list[str]:
    return _d_capitalized_spans(str(question) + " " + str(summary_1))


def _d_anchor_record(question: str, summary_1: str, query: str) -> dict[str, Any]:
    anchors = _d_anchor_candidates(question, summary_1)
    query_l = str(query).lower()

    preserved = [a for a in anchors if a.lower() in query_l]
    omitted = [a for a in anchors if a.lower() not in query_l]

    anchor_terms: list[str] = []
    for a in anchors:
        anchor_terms.extend(_d_terms(a))
    anchor_terms = _d_dedup_preserve_order(anchor_terms)

    query_terms = _d_terms(query)

    return {
        "anchor_candidates_from_question_and_summary": anchors,
        "anchors_preserved_as_exact_spans": preserved,
        "anchors_not_preserved_as_exact_spans": omitted,
        "anchor_terms": anchor_terms,
        "anchor_terms_preserved_in_query": _d_overlap(anchor_terms, query_terms),
    }


def _d_query_shape(query: str, question: str) -> dict[str, Any]:
    terms = _d_terms(query)
    token_count = _d_raw_word_count(query)
    return {
        "token_count": token_count,
        "query_terms": terms,
        "leading_terms": terms[:5],
        "is_compact_keyword_query": 2 <= token_count <= 8 and not _d_question_restated(query, question),
        "restates_full_question": _d_question_restated(query, question),
        "contains_explanatory_phrases": _d_contains_any(
            query,
            [
                "because",
                "according to",
                "based on",
                "given that",
                "provided information",
                "which of",
                "what is",
                "who is",
                "where is",
                "how many",
            ],
        ),
        "contains_list_or_comparison_markers": _d_contains_any(
            query,
            [" or ", " and ", ",", ";", " vs ", " versus "],
        ),
    }


def _d_support_surfaces(row: dict[str, Any]) -> dict[str, Any]:
    hop1_titles = row.get("hop1_titles", [])
    hop2_titles = row.get("hop2_titles", [])
    gold_titles = row.get("gold_support_titles", [])
    missing_titles = row.get("missing_titles_after_hop2", [])

    return {
        "already_known_hop1_titles": hop1_titles,
        "already_known_title_terms": _d_title_terms(hop1_titles),
        "hop2_retrieved_titles": hop2_titles,
        "hop2_retrieved_title_terms": _d_title_terms(hop2_titles),
        "gold_support_titles": gold_titles,
        "gold_support_title_terms": _d_title_terms(gold_titles),
        "still_missing_titles_after_hop2": missing_titles,
        "still_missing_title_terms": _d_title_terms(missing_titles),
    }


def build_anchor_compression_joint_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group D.
    Joint advanced gradient representation.

    Combines the two successful C axes:
    canonical anchor preservation + compact BM25 keyword-query compression.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        question = _question(r)
        summary_1 = _summary_1(r)
        query = _generated_query(r)
        query_terms = _d_terms(query)
        surfaces = _d_support_surfaces(r)

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "input_fields": ["question", "summary_1"],
                    "output_field": "query",
                    "downstream_consumer": "BM25 retriever",
                    "advanced_gradient": "preserve canonical anchors while compressing the output into a short retrieval key",
                },
                "Inputs": {
                    "question": question,
                    "summary_1": summary_1,
                },
                "Observed Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                },
                "Anchor Axis": _d_anchor_record(question, summary_1, query),
                "Compression Axis": _d_query_shape(query, question),
                "Support Surfaces": surfaces,
                "Query-to-Support Allocation": {
                    "query_overlap_with_missing_title_terms": _d_overlap(query_terms, surfaces["still_missing_title_terms"]),
                    "query_overlap_with_already_known_title_terms": _d_overlap(query_terms, surfaces["already_known_title_terms"]),
                    "query_overlap_with_gold_support_title_terms": _d_overlap(query_terms, surfaces["gold_support_title_terms"]),
                },
                "Retrieval Outcome": {
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "support_recall_hop2_only": r.get("support_recall_hop2_only"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_query_key_edit_script_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group D.
    Edit-script representation over the query string.

    Exposes local output-edit axes without directly providing a replacement query:
    keep anchors, drop verbose/restated terms, add missing-surface anchors when visible,
    and compress to a BM25 key.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        question = _question(r)
        summary_1 = _summary_1(r)
        query = _generated_query(r)
        query_terms = _d_terms(query)
        surfaces = _d_support_surfaces(r)
        anchor_record = _d_anchor_record(question, summary_1, query)
        shape = _d_query_shape(query, question)

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "output_field": "query",
                    "edit_space": "local edits over the emitted query string",
                },
                "Inputs": {
                    "question": question,
                    "summary_1": summary_1,
                },
                "Observed Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                    "query_terms": query_terms,
                },
                "Edit Axes": {
                    "KEEP": {
                        "canonical_anchors_already_preserved": anchor_record["anchors_preserved_as_exact_spans"],
                        "query_terms_matching_gold_support_titles": _d_overlap(query_terms, surfaces["gold_support_title_terms"]),
                    },
                    "DROP_OR_DOWNWEIGHT": {
                        "full_question_restatement": shape["restates_full_question"],
                        "explanatory_or_filler_phrases": shape["contains_explanatory_phrases"],
                        "already_known_title_terms_in_query": _d_overlap(query_terms, surfaces["already_known_title_terms"]),
                    },
                    "ADD_OR_UPWEIGHT": {
                        "anchors_not_preserved_as_exact_spans": anchor_record["anchors_not_preserved_as_exact_spans"],
                        "missing_title_terms_not_in_query": [
                            t for t in surfaces["still_missing_title_terms"]
                            if t not in set(query_terms)
                        ],
                    },
                    "COMPRESS": {
                        "token_count": shape["token_count"],
                        "is_compact_keyword_query": shape["is_compact_keyword_query"],
                        "target_shape": "short noun/keyphrase surface for BM25",
                    },
                },
                "Support Surfaces": surfaces,
                "Retrieval Outcome": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_minimal_bm25_gradient_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group D.
    Minimal advanced gradient representation.

    Keeps only the few variables that matched the manual best prompt:
    missing target, canonical anchors, and compression status.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        question = _question(r)
        summary_1 = _summary_1(r)
        query = _generated_query(r)
        surfaces = _d_support_surfaces(r)

        dataset.append(
            {
                "Function": "create_query_hop2.predict(question, summary_1) -> query",
                "Downstream": "BM25 sees only query lexical tokens",
                "Inputs": {
                    "question": question,
                    "summary_1": summary_1,
                },
                "Observed Query": query,
                "Gradient Variables": {
                    "missing_support_surface": {
                        "missing_titles_after_hop2": surfaces["still_missing_titles_after_hop2"],
                        "missing_title_terms": surfaces["still_missing_title_terms"],
                    },
                    "canonical_anchor_surface": _d_anchor_record(question, summary_1, query),
                    "query_compression_surface": _d_query_shape(query, question),
                },
                "Outcome": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_anchor_disambiguator_budget_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group D.
    Budgeted query construction representation.

    Makes the output budget explicit: one canonical anchor plus one or two
    short disambiguators. This is stronger than raw anchor preservation but
    less checklist-heavy than manual clause diagnostics.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        question = _question(r)
        summary_1 = _summary_1(r)
        query = _generated_query(r)
        query_terms = _d_terms(query)
        surfaces = _d_support_surfaces(r)
        anchor_record = _d_anchor_record(question, summary_1, query)

        candidate_disambiguators = _d_dedup_preserve_order(
            surfaces["gold_support_title_terms"]
            + surfaces["still_missing_title_terms"]
            + _d_terms(summary_1)
        )

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "output_field": "query",
                    "construction_budget": "canonical anchor + one or two short disambiguators",
                },
                "Inputs": {
                    "question": question,
                    "summary_1": summary_1,
                },
                "Observed Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                    "query_terms": query_terms,
                },
                "Anchor Budget": {
                    "anchor_candidates": anchor_record["anchor_candidates_from_question_and_summary"],
                    "anchors_preserved": anchor_record["anchors_preserved_as_exact_spans"],
                    "anchors_omitted": anchor_record["anchors_not_preserved_as_exact_spans"],
                },
                "Disambiguator Budget": {
                    "candidate_disambiguator_terms_from_trace": candidate_disambiguators[:30],
                    "query_terms_used_as_disambiguators": [
                        t for t in query_terms
                        if t in set(candidate_disambiguators)
                    ],
                    "query_token_count": _d_raw_word_count(query),
                },
                "Support Surfaces": surfaces,
                "Retrieval Outcome": {
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_restatement_to_keyword_delta_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group D.
    Delta representation from question-like output to keyword-like output.

    Focuses the proposer on the transformation:
    verbose/full-question query -> compact lexical BM25 key.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        question = _question(r)
        summary_1 = _summary_1(r)
        query = _generated_query(r)
        query_terms = _d_terms(query)
        question_terms = _d_terms(question)
        surfaces = _d_support_surfaces(r)
        shape = _d_query_shape(query, question)

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "output_field": "query",
                    "delta_type": "question-like wording to keyword-like BM25 key",
                },
                "Inputs": {
                    "question": question,
                    "summary_1": summary_1,
                },
                "Observed Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                    "query_terms": query_terms,
                },
                "Question-Restatement Signal": {
                    "question_terms": question_terms,
                    "query_overlap_with_question_terms": _d_overlap(query_terms, question_terms),
                    "restates_full_question": shape["restates_full_question"],
                    "contains_explanatory_phrases": shape["contains_explanatory_phrases"],
                    "contains_list_or_comparison_markers": shape["contains_list_or_comparison_markers"],
                },
                "Keyword-Key Signal": {
                    "query_overlap_with_gold_support_title_terms": _d_overlap(query_terms, surfaces["gold_support_title_terms"]),
                    "query_overlap_with_missing_title_terms": _d_overlap(query_terms, surfaces["still_missing_title_terms"]),
                    "query_token_count": shape["token_count"],
                    "is_compact_keyword_query": shape["is_compact_keyword_query"],
                },
                "Support Surfaces": surfaces,
                "Retrieval Outcome": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "missing_titles_after_hop2": r.get("missing_titles_after_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


def build_evidence_gap_anchor_synthesis_v1(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group D.
    Evidence-gap to anchor-synthesis representation.

    Shows the path from partially covered evidence to candidate lexical anchors
    that could express the remaining support gap, without directly writing a
    replacement query.
    """
    dataset: list[dict[str, Any]] = []

    for r in rows:
        question = _question(r)
        summary_1 = _summary_1(r)
        query = _generated_query(r)
        surfaces = _d_support_surfaces(r)
        query_terms = _d_terms(query)

        gap_terms = _d_dedup_preserve_order(
            surfaces["still_missing_title_terms"]
            + [
                t for t in surfaces["gold_support_title_terms"]
                if t not in set(surfaces["already_known_title_terms"])
            ]
        )

        dataset.append(
            {
                "Function Under Optimization": {
                    "function": "create_query_hop2.predict",
                    "input_state": "question + summary_1",
                    "output_state": "lexical query for retrieving the evidence gap",
                    "gradient_variable": "synthesize a lexical anchor for the uncovered support gap",
                },
                "Partial Evidence State": {
                    "question": question,
                    "summary_1": summary_1,
                    "already_known_hop1_titles": surfaces["already_known_hop1_titles"],
                    "already_known_title_terms": surfaces["already_known_title_terms"],
                },
                "Evidence Gap Surface": {
                    "gold_support_titles": surfaces["gold_support_titles"],
                    "still_missing_titles_after_hop2": surfaces["still_missing_titles_after_hop2"],
                    "gap_terms_from_support_surfaces": gap_terms,
                },
                "Observed Query": {
                    "reasoning": _generated_reasoning(r),
                    "query": query,
                    "query_terms": query_terms,
                    "query_overlap_with_gap_terms": _d_overlap(query_terms, gap_terms),
                },
                "Anchor Candidates from Inputs": _d_anchor_record(question, summary_1, query),
                "Retrieval Outcome": {
                    "hop2_titles": r.get("hop2_titles", []),
                    "new_support_titles_hop2": r.get("new_support_titles_hop2", []),
                    "support_recall_total": r.get("support_recall_total"),
                    "module_score": r.get("module_score"),
                },
                "Original Feedback": r.get("feedback_text", ""),
            }
        )

    return dataset


REPRESENTATION_BUILDERS: dict[str, Callable[[list[dict[str, Any]]], list[dict[str, Any]]]] = {
    # GEPA-style representation baseline
    "gepa_style_raw_feedback_v1": build_gepa_style_raw_feedback_v1,

    # Group A: reversible
    "json_reversible_v1": build_json_reversible_v1,
    "state_transition_reversible_v1": build_state_transition_reversible_v1,
    "io_trace_reversible_v1": build_io_trace_reversible_v1,
    "title_set_reversible_v1": build_title_set_reversible_v1,

    # Group B: function-aware contextual / BM25-aware
    "bm25_contract_surface_v1": build_bm25_contract_surface_v1,
    "bm25_lexical_diagnostic_v1": build_bm25_lexical_diagnostic_v1,
    "function_bottleneck_transduction_v1": build_function_bottleneck_transduction_v1,
    "evidence_state_machine_v1": build_evidence_state_machine_v1,
    "bridge_attempt_context_v1": build_bridge_attempt_context_v1,
    "partial_context_expansion_v1": build_partial_context_expansion_v1,
    # Group C: gradient-skeleton representations
    "bm25_missing_target_mainness_v1": build_bm25_missing_target_mainness_v1,
    "bm25_manual_clause_violation_v1": build_bm25_manual_clause_violation_v1,
    "missing_target_slot_gradient_v1": build_missing_target_slot_gradient_v1,
    "known_vs_missing_query_allocation_v1": build_known_vs_missing_query_allocation_v1,
    "query_compression_violation_v1": build_query_compression_violation_v1,
    "canonical_anchor_preservation_v1": build_canonical_anchor_preservation_v1,

    # Group D: advanced gradient-skeleton representations
    "anchor_compression_joint_v1": build_anchor_compression_joint_v1,
    "query_key_edit_script_v1": build_query_key_edit_script_v1,
    "minimal_bm25_gradient_v1": build_minimal_bm25_gradient_v1,
    "anchor_disambiguator_budget_v1": build_anchor_disambiguator_budget_v1,
    "restatement_to_keyword_delta_v1": build_restatement_to_keyword_delta_v1,
    "evidence_gap_anchor_synthesis_v1": build_evidence_gap_anchor_synthesis_v1,

}


REPRESENTATION_GROUPS: dict[str, list[str]] = {
    "gepa_style": [
        "gepa_style_raw_feedback_v1",
    ],
    "reversible": [
        "json_reversible_v1",
        "state_transition_reversible_v1",
        "io_trace_reversible_v1",
        "title_set_reversible_v1",
    ],
    "diagnostic": [
        # BM25-aware conditions first, by design.
        "bm25_contract_surface_v1",
        "bm25_lexical_diagnostic_v1",

        # Function-aware semantic rewrites.
        "function_bottleneck_transduction_v1",
        "evidence_state_machine_v1",

        # Light contextual controls.
        "bridge_attempt_context_v1",
        "partial_context_expansion_v1",
    ],
    "gradient": [
        # Strong BM25-aware gradient skeletons first.
        "bm25_missing_target_mainness_v1",
        "bm25_manual_clause_violation_v1",

        # Other gradient-variable decompositions.
        "missing_target_slot_gradient_v1",
        "known_vs_missing_query_allocation_v1",
        "query_compression_violation_v1",
        "canonical_anchor_preservation_v1",
    ],
    "advanced_gradient": [
        # C-success-axis combinations first.
        "anchor_compression_joint_v1",
        "query_key_edit_script_v1",

        # Minimal / budgeted variants.
        "minimal_bm25_gradient_v1",
        "anchor_disambiguator_budget_v1",

        # Delta / synthesis variants.
        "restatement_to_keyword_delta_v1",
        "evidence_gap_anchor_synthesis_v1",
    ],
    "all": [
        "gepa_style_raw_feedback_v1",
        "json_reversible_v1",
        "state_transition_reversible_v1",
        "io_trace_reversible_v1",
        "title_set_reversible_v1",
        "bm25_contract_surface_v1",
        "bm25_lexical_diagnostic_v1",
        "function_bottleneck_transduction_v1",
        "evidence_state_machine_v1",
        "bridge_attempt_context_v1",
        "partial_context_expansion_v1",
        "bm25_missing_target_mainness_v1",
        "bm25_manual_clause_violation_v1",
        "missing_target_slot_gradient_v1",
        "known_vs_missing_query_allocation_v1",
        "query_compression_violation_v1",
        "canonical_anchor_preservation_v1",
        "anchor_compression_joint_v1",
        "query_key_edit_script_v1",
        "minimal_bm25_gradient_v1",
        "anchor_disambiguator_budget_v1",
        "restatement_to_keyword_delta_v1",
        "evidence_gap_anchor_synthesis_v1",
    ],
}



CONDITION_TO_GROUP: dict[str, str] = {}
for _group_name, _condition_names in REPRESENTATION_GROUPS.items():
    if _group_name == "all":
        continue
    for _condition_name in _condition_names:
        CONDITION_TO_GROUP[_condition_name] = _group_name


def resolve_conditions(args: argparse.Namespace) -> list[str]:
    if args.conditions:
        conditions = args.conditions
    else:
        conditions = REPRESENTATION_GROUPS[args.representation_group]

    unknown = [c for c in conditions if c not in REPRESENTATION_BUILDERS]
    if unknown:
        raise KeyError(
            f"Unknown condition(s): {unknown}. "
            f"Available: {sorted(REPRESENTATION_BUILDERS)}"
        )

    if args.representation_group != "all":
        allowed = set(REPRESENTATION_GROUPS[args.representation_group])
        illegal = [c for c in conditions if c not in allowed]
        if illegal:
            raise ValueError(
                f"Condition(s) {illegal} do not belong to group "
                f"{args.representation_group}. Use --representation-group all "
                f"or choose conditions from {sorted(allowed)}."
            )

    return conditions


# ============================================================
# Evaluation
# ============================================================


def load_splits(args: argparse.Namespace):
    try:
        return load_hotpot_splits(
            train_size=args.train_size,
            val_size=args.val_size,
            test_size=args.test_size,
            seed=args.seed,
        )
    except TypeError:
        return load_hotpot_splits(
            args.train_size,
            args.val_size,
            args.test_size,
            args.seed,
        )


def get_evalset(args: argparse.Namespace):
    trainset, valset, testset = load_splits(args)

    if args.eval_split == "train":
        return trainset
    if args.eval_split == "val":
        return valset
    if args.eval_split == "test":
        return testset

    raise ValueError(f"Unknown eval split: {args.eval_split}")


def _chunks(xs: list[Any], chunk_size: int):
    for i in range(0, len(xs), chunk_size):
        yield xs[i : i + chunk_size]


def summarize_rollouts(rollout_path: Path) -> dict[str, Any]:
    rows = read_jsonl(rollout_path)
    n = len(rows)

    if n == 0:
        return {
            "n": 0,
            "mean_score": None,
            "wrong_count": None,
        }

    scores = [float(r.get("score", 0.0)) for r in rows]

    support_total = [
        float(r.get("support_recall_total", 0.0))
        for r in rows
        if r.get("support_recall_total") is not None
    ]
    support_hop2 = [
        float(r.get("support_recall_hop2_only", 0.0))
        for r in rows
        if r.get("support_recall_hop2_only") is not None
    ]

    retrieval_failures = [
        r for r in rows if bool(r.get("missing_titles_after_hop2") or [])
    ]
    hop2_new_support_hits = [
        r for r in rows if bool(r.get("new_support_titles_hop2") or [])
    ]

    return {
        "n": n,
        "mean_score": sum(scores) / n,
        "wrong_count": sum(1 for s in scores if s < 1.0),
        "correct_count": sum(1 for s in scores if s >= 1.0),
        "avg_support_recall_total": (
            sum(support_total) / len(support_total) if support_total else None
        ),
        "avg_support_recall_hop2_only": (
            sum(support_hop2) / len(support_hop2) if support_hop2 else None
        ),
        "retrieval_failure_count": len(retrieval_failures),
        "retrieval_failure_ratio": len(retrieval_failures) / n,
        "hop2_new_support_hit_count": len(hop2_new_support_hits),
        "hop2_new_support_hit_ratio": len(hop2_new_support_hits) / n,
    }


def evaluate_candidate(
    *,
    args: argparse.Namespace,
    condition_name: str,
    condition_dir: Path,
    candidate_prompts: dict[str, str],
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
            phase="representation_probe",
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
        all_scores: list[float] = []
        eval_list = list(evalset)
        chunk_size = max(1, int(args.eval_progress_chunk_size))
        chunks = list(_chunks(eval_list, chunk_size))
        desc = (
            f"eval[{condition_name}] {args.eval_split} "
            f"chunksize={chunk_size} threads={args.num_threads}"
        )

        for chunk in tqdm(chunks, desc=desc, total=len(chunks), dynamic_ncols=True):
            chunk_batch = adapter.evaluate(
                chunk,
                candidate_prompts,
                capture_traces=False,
            )
            all_scores.extend(float(s) for s in chunk_batch.scores)

        raw_mean = sum(all_scores) / len(all_scores)
        eval_n = len(all_scores)
    else:
        eval_batch = adapter.evaluate(
            evalset,
            candidate_prompts,
            capture_traces=False,
        )
        raw_mean = sum(float(s) for s in eval_batch.scores) / len(eval_batch.scores)
        eval_n = len(eval_batch.scores)

    if hasattr(adapter, "clear_analysis_context"):
        adapter.clear_analysis_context()

    raw_summary = {
        "condition": condition_name,
        "representation_group": CONDITION_TO_GROUP.get(condition_name, "control"),
        "eval_split": args.eval_split,
        "n": eval_n,
        "mean_score_from_eval_batch": raw_mean,
    }

    rollout_summary = summarize_rollouts(analysis_dir / "rollout_traces.jsonl")
    summary = {**raw_summary, **rollout_summary}

    write_json(condition_dir / "summary.json", summary)
    return summary


# ============================================================
# CLI / Main
# ============================================================


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()

    p.add_argument("--source-run", type=Path, required=True)
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--exp-name", type=str, required=True)
    p.add_argument("--overwrite", action="store_true")

    p.add_argument(
        "--base-candidate",
        choices=["seed", "best"],
        default="seed",
        help="seed uses source-run/seed_candidate.json; best uses source-run/best_candidate.json.",
    )
    p.add_argument("--target-component", type=str, default=TARGET_COMPONENT)

    p.add_argument(
        "--representation-group",
        choices=["gepa_style", "reversible", "diagnostic", "gradient", "advanced_gradient", "all"],
        default="reversible",
        help=(
            "Which representation family to run. "
            "gepa_style = GEPA raw feedback baseline, reversible = Group A, diagnostic = Group B, gradient = Group C gradient-skeleton, advanced_gradient = Group D advanced gradient-skeleton, all = all registered conditions."
        ),
    )
    p.add_argument(
        "--conditions",
        nargs="*",
        default=None,
        help=(
            "Optional explicit condition list. If omitted, conditions are selected "
            "from --representation-group."
        ),
    )

    p.add_argument(
        "--include-baseline",
        action="store_true",
        help="Optionally evaluate the unchanged base candidate as a control.",
    )

    p.add_argument(
        "--pair-filter",
        choices=["all", "retrieval_failure", "score0"],
        default="retrieval_failure",
    )
    p.add_argument("--num-pairs", type=int, default=3)
    p.add_argument("--shuffle-pairs", action="store_true")

    p.add_argument("--env-file", type=Path, default=Path(".env"))

    p.add_argument("--proposer-model", type=str, default="gpt-5-mini")
    p.add_argument("--proposer-temperature", type=float, default=None)
    p.add_argument("--proposer-max-tokens", type=int, default=2048)

    p.add_argument("--task-model", type=str, default="openai/gpt-5-mini")
    p.add_argument("--task-api-key", type=str, default=None)
    p.add_argument("--task-api-base", type=str, default=None)
    p.add_argument("--task-temperature", type=float, default=0.0)
    p.add_argument("--task-max-tokens", type=int, default=1024)

    p.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    p.add_argument("--retrieval-k", type=int, default=7)

    p.add_argument("--train-size", type=int, default=100)
    p.add_argument("--val-size", type=int, default=100)
    p.add_argument("--test-size", type=int, default=100)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--eval-split", choices=["train", "val", "test"], default="test")
    p.add_argument("--num-threads", type=int, default=20)
    p.add_argument(
        "--show-eval-progress",
        action="store_true",
        help=(
            "Show tqdm ETA during evaluation. With --eval-progress-chunk-size > 1, "
            "each chunk is evaluated with DSPy num_threads."
        ),
    )
    p.add_argument(
        "--eval-progress-chunk-size",
        type=int,
        default=20,
        help=(
            "Chunk size for tqdm evaluation. Use 1 for per-example sequential progress; "
            "use >= num_threads for threaded chunk evaluation."
        ),
    )

    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.target_component != TARGET_COMPONENT:
        raise ValueError(
            f"This probe script currently supports only {TARGET_COMPONENT}; "
            f"got {args.target_component}"
        )

    load_env_file(args.env_file)
    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError(
            f"OPENAI_API_KEY not found. Checked env and {args.env_file}."
        )

    exp_dir = args.output_root / args.exp_name / f"base_{args.base_candidate}"
    prepare_output_dir(exp_dir, overwrite=args.overwrite)

    source_run = args.source_run
    source_summary = maybe_read_source_summary(source_run)

    candidate_file = (
        source_run / "seed_candidate.json"
        if args.base_candidate == "seed"
        else source_run / "best_candidate.json"
    )
    base_prompts = load_candidate(candidate_file)

    if TARGET_COMPONENT not in base_prompts:
        raise KeyError(
            f"{TARGET_COMPONENT} not found in base candidate keys: "
            f"{sorted(base_prompts)}"
        )

    condition_names = resolve_conditions(args)

    selected_pairs = select_source_pairs(
        source_run=source_run,
        target_component=TARGET_COMPONENT,
        pair_filter=args.pair_filter,
        num_pairs=args.num_pairs,
        shuffle=args.shuffle_pairs,
        seed=args.seed,
    )

    write_json(
        exp_dir / "config.json",
        {
            **vars(args),
            "source_run": str(args.source_run),
            "output_root": str(args.output_root),
            "env_file": str(args.env_file),
            "retriever_dir": str(args.retriever_dir),
            "base_candidate_file": str(candidate_file),
            "selected_pair_count": len(selected_pairs),
            "resolved_conditions": condition_names,
            "source_summary": source_summary,
        },
    )
    write_jsonl(exp_dir / "source_pairs.jsonl", selected_pairs)

    configure_task_lm(args)

    aggregate: dict[str, Any] = {
        "exp_dir": str(exp_dir),
        "source_run": str(source_run),
        "source_summary": source_summary,
        "base_candidate": args.base_candidate,
        "target_component": TARGET_COMPONENT,
        "representation_group": args.representation_group,
        "pair_filter": args.pair_filter,
        "num_pairs": len(selected_pairs),
        "conditions": {},
    }

    if args.include_baseline:
        condition_name = "baseline"
        condition_dir = exp_dir / "conditions" / condition_name
        condition_dir.mkdir(parents=True, exist_ok=True)

        save_candidate(
            condition_dir / "prompt_candidate.json",
            name=condition_name,
            prompts=base_prompts,
        )

        summary = evaluate_candidate(
            args=args,
            condition_name=condition_name,
            condition_dir=condition_dir,
            candidate_prompts=base_prompts,
        )
        aggregate["conditions"][condition_name] = summary

    for condition_name in condition_names:
        condition_dir = exp_dir / "conditions" / condition_name
        condition_dir.mkdir(parents=True, exist_ok=True)

        dataset_with_feedback = REPRESENTATION_BUILDERS[condition_name](selected_pairs)
        write_json(
            condition_dir / "dataset_with_feedback.json",
            dataset_with_feedback,
        )

        proposal = propose_instruction(
            base_instruction=base_prompts[TARGET_COMPONENT],
            dataset_with_feedback=dataset_with_feedback,
            proposer_model=args.proposer_model,
            proposer_temperature=args.proposer_temperature,
            proposer_max_tokens=args.proposer_max_tokens,
        )

        new_prompts = dict(base_prompts)
        new_prompts[TARGET_COMPONENT] = proposal["new_instruction"]

        proposal_event = {
            "condition": condition_name,
            "representation_group": CONDITION_TO_GROUP.get(condition_name, "mixed"),
            "source_run": str(source_run),
            "base_candidate": args.base_candidate,
            "target_component": TARGET_COMPONENT,
            "old_instruction": base_prompts[TARGET_COMPONENT],
            "new_instruction": proposal["new_instruction"],
            "reflection_prompt": proposal["reflection_prompt"],
            "raw_lm_output": proposal["raw_lm_output"],
            "raw_contains_think": proposal["raw_contains_think"],
            "new_instruction_contains_think": proposal["new_instruction_contains_think"],
            "selected_pair_count": len(selected_pairs),
            "dataset_with_feedback": dataset_with_feedback,
        }
        write_json(condition_dir / "proposal_event.json", proposal_event)

        save_candidate(
            condition_dir / "prompt_candidate.json",
            name=condition_name,
            prompts=new_prompts,
        )

        summary = evaluate_candidate(
            args=args,
            condition_name=condition_name,
            condition_dir=condition_dir,
            candidate_prompts=new_prompts,
        )
        aggregate["conditions"][condition_name] = summary

    write_json(exp_dir / "aggregate_summary.json", aggregate)

    print(json.dumps(aggregate, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()