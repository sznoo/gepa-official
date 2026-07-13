#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

import dspy  # noqa: E402
from litellm import completion  # noqa: E402

from experiments.method_probe.src.cache import (  # noqa: E402
    CallCache,
    atomic_write_json,
)
from experiments.method_probe.src.config import (  # noqa: E402
    GRADIENT_AGGREGATION_SYSTEM_PROMPT,
)
from experiments.method_probe.src.hotpot import (  # noqa: E402
    HotpotRuntime,
    configure_lm,
    load_jsonl,
    titles_from_passages,
)


QUERY_PROMPT_KEY_ALIASES = (
    "create_query_hop2.predict",
    "create_query_hop2",
)
QUERY_PROMPT_KEY = QUERY_PROMPT_KEY_ALIASES[0]


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

DEFAULT_SAMPLE_GRADIENT_SYSTEM_PROMPT = """
You infer a local textual gradient for a HotpotQA second-hop query-generation
prompt.

The query-generation module is:

    q = Q(question, summary_1; p_query)

and the retrieval tool is:

    R = T(q)

A retrieval-state transition has already been explicitly inverted into a query
transition:

    R_source -> R_destination
    q_source -> q_destination

Your task is to infer a local prompt gradient that would make the query writer
move from q_source toward q_destination for the given input.

A prompt gradient is not a complete replacement prompt. It is a concise,
operational description of how the current prompt should change.

Requirements:
- Do not output a complete rewritten prompt.
- Do not merely restate the source and destination queries.
- Infer the query-writing behavior responsible for the transition.
- Ground the gradient in the query transition and retrieval behavior.
- Describe the smallest useful behavioral adjustment.
- Preserve useful capabilities that are unrelated to this transition.
- Avoid memorizing sample-specific names, titles, or answers as a global rule.
- The gradient may refer to general behaviors such as entity anchoring,
  relation preservation, bridge resolution, ambiguity control, candidate
  breadth, title targeting, and distractor suppression.

Return JSON only:
{
  "gradient": "operational textual gradient, not a complete prompt",
  "rationale": "why this gradient should produce the destination query behavior",
  "constraints_to_preserve": [
    "existing query-writing behaviors that should remain unchanged"
  ],
  "failure_behavior_to_avoid": [
    "behaviors that would prevent the intended transition"
  ],
  "expected_query_change": "concise description of the expected query change"
}
""".strip()


DEFAULT_TRIAL_COMPOSITION_SYSTEM_PROMPT = """
You compose a temporary trial prompt for operational intervention.

You are given:
- one base prompt for a HotpotQA second-hop query generator,
- an ordered trace of local textual gradients inferred for one sample.

Apply the gradient trace to the base prompt and return one complete trial
instruction.

This trial prompt is used only to test whether the local output transition is
operationally achievable. It is not a batch-level aggregate prompt and should
not introduce lessons from any other sample.

Requirements:
- Apply all gradients in the supplied order.
- Preserve unrelated capabilities of the base prompt.
- Resolve conflicts in favor of the later gradient in the trace.
- Produce a complete executable instruction.
- Do not mention gradients, intervention, source states, or destination states.
- Do not include sample-specific answers or memorize sample-specific facts.
- Keep the instruction operational and reasonably concise.

Return JSON only:
{
  "trial_prompt": "complete temporary query-writer instruction",
  "composition_rationale": "how the gradient trace was applied",
  "applied_gradient_ids": ["gradient identifiers applied in order"]
}
""".strip()


# ---------------------------------------------------------------------------
# Generic utilities
# ---------------------------------------------------------------------------

def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _stable_id(
    prefix: str,
    payload: Mapping[str, Any],
) -> str:
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    digest = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()[:20]

    return f"{prefix}_{digest}"


def _unique_strings(
    values: Iterable[Any],
) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()

    for value in values:
        text = _clean_text(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)

    return output


def _json_string_list(
    value: Any,
    field_name: str,
) -> list[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(
            f"{field_name} must be a JSON list."
        )

    return _unique_strings(value)


def _parse_json_object(text: Any) -> dict[str, Any]:
    text = _clean_text(text)

    if not text:
        raise ValueError("Model returned an empty response.")

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s*```$", "", text)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start < 0 or end <= start:
            raise ValueError(
                f"No JSON object found in response: "
                f"{text[:500]}"
            )

        parsed = json.loads(text[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError(
            f"Expected JSON object, got "
            f"{type(parsed).__name__}."
        )

    return parsed


def _completion_text(response: Any) -> str:
    try:
        content = response.choices[0].message.content
    except (
        AttributeError,
        IndexError,
        KeyError,
        TypeError,
    ) as exc:
        raise ValueError(
            "Could not extract text from LiteLLM response."
        ) from exc

    text = _clean_text(content)

    if not text:
        raise ValueError(
            "LiteLLM response has empty content."
        )

    return text


def _normalize_title(title: Any) -> str:
    text = _clean_text(title).lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _title_matches(
    expected: str,
    actual_titles: Sequence[str],
) -> bool:
    expected_norm = _normalize_title(expected)

    return any(
        _normalize_title(actual) == expected_norm
        for actual in actual_titles
    )


def _compact_endpoint(
    endpoint: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "endpoint_id": endpoint.get("endpoint_id"),
        "endpoint_type": endpoint.get(
            "endpoint_type"
        ),
        "materialization": endpoint.get(
            "materialization"
        ),
        "question": endpoint.get("question"),
        "summary_1": endpoint.get("summary_1"),
        "query": endpoint.get("query"),
        "retrieved_titles": endpoint.get(
            "retrieved_titles"
        ) or [],
        "summary_2": endpoint.get("summary_2"),
        "pred_answer": endpoint.get("pred_answer"),
        "metrics": endpoint.get("metrics") or {},
        "retrieval": endpoint.get("retrieval") or {},
        "retrieval_target": endpoint.get(
            "retrieval_target"
        ),
    }


def _compact_retrieval_target(
    target: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "retrieval_target_id": target.get(
            "retrieval_target_id"
        ),
        "target_type": target.get("target_type"),
        "desired_titles": target.get(
            "desired_titles"
        ) or [],
        "preserve_titles": target.get(
            "preserve_titles"
        ) or [],
        "avoid_titles": target.get(
            "avoid_titles"
        ) or [],
        "target_behavior": target.get(
            "target_behavior"
        ),
        "rationale": target.get("rationale"),
        "gold_privileged": target.get(
            "gold_privileged"
        ),
    }


# ---------------------------------------------------------------------------
# 1. Prompt snapshot and schema helpers
# ---------------------------------------------------------------------------

def default_query_prompt() -> str:
    """
    Extract the default instruction used by:

        dspy.ChainOfThought("question,summary_1->query")
    """

    module = dspy.ChainOfThought(
        "question,summary_1->query"
    )

    predictor = getattr(module, "predict", module)
    signature = getattr(predictor, "signature", None)

    if signature is None:
        raise AttributeError(
            "Could not find the DSPy query signature."
        )

    instruction = getattr(
        signature,
        "instructions",
        None,
    )

    if not instruction:
        raise AttributeError(
            "Could not extract default query instructions."
        )

    return _clean_text(instruction)


def normalize_prompt_snapshot(
    snapshot: Mapping[str, Any],
) -> dict[str, str]:
    if isinstance(snapshot.get("prompts"), Mapping):
        snapshot = snapshot["prompts"]

    normalized: dict[str, str] = {}

    for key, value in snapshot.items():
        text = _clean_text(value)

        if text:
            normalized[str(key)] = text

    return normalized


def get_query_prompt(
    snapshot: Mapping[str, Any],
) -> str:
    normalized = normalize_prompt_snapshot(snapshot)

    for key in [
        *QUERY_PROMPT_KEY_ALIASES,
        "query_prompt",
    ]:
        prompt = _clean_text(normalized.get(key))

        if prompt:
            return prompt

    raise KeyError(
        f"No query prompt found. "
        f"Expected key {QUERY_PROMPT_KEY}."
    )


def replace_query_prompt(
    snapshot: Mapping[str, Any],
    new_prompt: str,
) -> dict[str, str]:
    new_prompt = _clean_text(new_prompt)

    if not new_prompt:
        raise ValueError(
            "new_prompt must not be empty."
        )

    updated = normalize_prompt_snapshot(snapshot)

    target_key = next(
        (
            key
            for key in QUERY_PROMPT_KEY_ALIASES
            if key in updated
        ),
        QUERY_PROMPT_KEY,
    )
    updated[target_key] = new_prompt

    return updated


def load_current_query_prompt(
    *,
    current_prompt: Optional[str] = None,
    prompt_file: Optional[str | Path] = None,
) -> str:
    if current_prompt and prompt_file:
        raise ValueError(
            "Use either current_prompt or prompt_file, "
            "not both."
        )

    if current_prompt:
        prompt = _clean_text(current_prompt)

        if not prompt:
            raise ValueError(
                "current_prompt is empty."
            )

        return prompt

    if prompt_file:
        path = Path(prompt_file)
        raw = path.read_text(encoding="utf-8")

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            prompt = _clean_text(raw)

            if not prompt:
                raise ValueError(
                    f"Prompt file is empty: {path}"
                )

            return prompt

        if isinstance(parsed, str):
            prompt = _clean_text(parsed)

            if not prompt:
                raise ValueError(
                    f"Prompt file is empty: {path}"
                )

            return prompt

        if isinstance(parsed, Mapping):
            return get_query_prompt(parsed)

        raise ValueError(
            f"Unsupported prompt file format: {path}"
        )

    return default_query_prompt()


def validate_transition(
    transition: Mapping[str, Any],
) -> None:
    required_top_level = [
        "transition_id",
        "transition_role",
        "sample_id",
        "source_status",
        "source_endpoint",
        "target_endpoint",
        "retrieval_target",
        "query_transition",
    ]

    for key in required_top_level:
        if transition.get(key) is None:
            raise ValueError(
                f"Transition is missing {key}."
            )

    if transition["source_status"] not in {"W", "C"}:
        raise ValueError(
            "source_status must be W or C."
        )

    source = transition["source_endpoint"]
    target = transition["target_endpoint"]
    retrieval_target = transition["retrieval_target"]
    query_transition = transition["query_transition"]

    if not isinstance(source, Mapping):
        raise ValueError(
            "source_endpoint must be an object."
        )

    if not isinstance(target, Mapping):
        raise ValueError(
            "target_endpoint must be an object."
        )

    if not isinstance(retrieval_target, Mapping):
        raise ValueError(
            "retrieval_target must be an object."
        )

    if not isinstance(query_transition, Mapping):
        raise ValueError(
            "query_transition must be an object."
        )

    sample_id = _clean_text(
        transition["sample_id"]
    )

    if _clean_text(source.get("sample_id")) != sample_id:
        raise ValueError(
            "Source endpoint sample ID mismatch."
        )

    if _clean_text(target.get("sample_id")) != sample_id:
        raise ValueError(
            "Target endpoint sample ID mismatch."
        )

    if (
        _clean_text(retrieval_target.get("sample_id"))
        != sample_id
    ):
        raise ValueError(
            "Retrieval target sample ID mismatch."
        )

    source_query = _clean_text(
        query_transition.get("source_query")
    )
    destination_query = _clean_text(
        query_transition.get("destination_query")
    )

    if not source_query:
        raise ValueError(
            "query_transition has no source_query."
        )

    if not destination_query:
        raise ValueError(
            "query_transition has no destination_query."
        )

    endpoint_source_query = _clean_text(
        source.get("query")
    )

    if source_query != endpoint_source_query:
        raise ValueError(
            "query_transition.source_query does not match "
            "source_endpoint.query."
        )


def validate_gradient_record(
    gradient_record: Mapping[str, Any],
) -> None:
    required = [
        "gradient_id",
        "transition_id",
        "sample_id",
        "agent_name",
        "gradient",
        "rationale",
        "query_transition",
    ]

    for key in required:
        if not gradient_record.get(key):
            raise ValueError(
                f"Gradient record is missing {key}."
            )

    if (
        gradient_record["agent_name"]
        != "create_query_hop2"
    ):
        raise ValueError(
            "Only create_query_hop2 is supported."
        )


# ---------------------------------------------------------------------------
# Shared cached JSON caller
# ---------------------------------------------------------------------------

class ProgramOperator:
    def __init__(
        self,
        *,
        cache: CallCache,
        model: str = "openai/gpt-5-mini",
        temperature: float = 1.0,
        max_tokens: int = 16000,
        max_retries: int = 2,
        sample_gradient_system_prompt: str = (
            DEFAULT_SAMPLE_GRADIENT_SYSTEM_PROMPT
        ),
        trial_composition_system_prompt: str = (
            DEFAULT_TRIAL_COMPOSITION_SYSTEM_PROMPT
        ),
    ):
        self.cache = cache
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

        self.sample_gradient_system_prompt = (
            sample_gradient_system_prompt
        )
        self.trial_composition_system_prompt = (
            trial_composition_system_prompt
        )

    def _cached_json_call(
        self,
        *,
        stage: str,
        system_prompt: str,
        payload: Mapping[str, Any],
        prompt_version: Optional[int | str],
        metadata: Optional[Mapping[str, Any]],
    ) -> tuple[dict[str, Any], bool, dict[str, Any]]:
        request = {
            "system_prompt": system_prompt,
            "payload": dict(payload),
        }

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(
                    payload,
                    ensure_ascii=False,
                    indent=2,
                ),
            },
        ]

        last_error: Optional[Exception] = None

        for retry_index in range(
            self.max_retries + 1
        ):
            try:
                parsed, cache_hit, record = (
                    self.cache.cached_call(
                        stage=stage,
                        request=request,
                        call_fn=lambda: _completion_text(
                            completion(
                                model=self.model,
                                messages=messages,
                                temperature=self.temperature,
                                max_tokens=self.max_tokens,
                            )
                        ),
                        parse_fn=_parse_json_object,
                        model=self.model,
                        generation={
                            "temperature": self.temperature,
                            "max_tokens": self.max_tokens,
                        },
                        prompt_version=prompt_version,
                        metadata=metadata,
                        retry_index=retry_index,
                    )
                )

                if not isinstance(parsed, dict):
                    raise ValueError(
                        "Parsed response is not an object."
                    )

                return parsed, cache_hit, record

            except Exception as exc:
                last_error = exc

        assert last_error is not None
        raise last_error

    # ------------------------------------------------------------------
    # 2. Samplewise gradient inference
    # ------------------------------------------------------------------

    def infer_sample_gradient(
        self,
        *,
        transition: Mapping[str, Any],
        current_prompt: str,
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        validate_transition(transition)

        current_prompt = _clean_text(current_prompt)

        if not current_prompt:
            raise ValueError(
                "current_prompt must not be empty."
            )

        source_endpoint = transition[
            "source_endpoint"
        ]
        target_endpoint = transition[
            "target_endpoint"
        ]
        retrieval_target = transition[
            "retrieval_target"
        ]
        query_transition = transition[
            "query_transition"
        ]

        payload = {
            "agent_name": "create_query_hop2",
            "agent_input": {
                "question": source_endpoint.get(
                    "question"
                ),
                "summary_1": source_endpoint.get(
                    "summary_1"
                ),
            },
            "current_prompt": current_prompt,
            "transition_context": {
                "transition_id": transition[
                    "transition_id"
                ],
                "transition_role": transition[
                    "transition_role"
                ],
                "source_status": transition[
                    "source_status"
                ],
                "source_retrieval_endpoint": (
                    _compact_endpoint(
                        source_endpoint
                    )
                ),
                "destination_retrieval_target": (
                    _compact_retrieval_target(
                        retrieval_target
                    )
                ),
                "materialized_destination_endpoint": (
                    _compact_endpoint(
                        target_endpoint
                    )
                ),
                "query_transition": {
                    "source_query": (
                        query_transition.get(
                            "source_query"
                        )
                    ),
                    "destination_query": (
                        query_transition.get(
                            "destination_query"
                        )
                    ),
                    "inversion_rationale": (
                        query_transition.get(
                            "inversion_rationale"
                        )
                    ),
                    "anchors_preserved": (
                        query_transition.get(
                            "anchors_preserved"
                        )
                        or []
                    ),
                    "anchors_added": (
                        query_transition.get(
                            "anchors_added"
                        )
                        or []
                    ),
                    "anchors_removed_or_disambiguated": (
                        query_transition.get(
                            "anchors_removed_or_disambiguated"
                        )
                        or []
                    ),
                },
            },
        }

        parsed, cache_hit, call_record = (
            self._cached_json_call(
                stage="sample_gradient_inference",
                system_prompt=(
                    self.sample_gradient_system_prompt
                ),
                payload=payload,
                prompt_version=prompt_version,
                metadata={
                    "sample_id": transition[
                        "sample_id"
                    ],
                    "transition_id": transition[
                        "transition_id"
                    ],
                    "transition_role": transition[
                        "transition_role"
                    ],
                    **dict(metadata or {}),
                },
            )
        )

        gradient = _clean_text(
            parsed.get("gradient")
        )
        rationale = _clean_text(
            parsed.get("rationale")
        )
        expected_query_change = _clean_text(
            parsed.get("expected_query_change")
        )

        if not gradient:
            raise ValueError(
                "Gradient inference returned no gradient."
            )

        if not rationale:
            raise ValueError(
                "Gradient inference returned no rationale."
            )

        if not expected_query_change:
            raise ValueError(
                "Gradient inference returned no "
                "expected_query_change."
            )

        constraints_to_preserve = _json_string_list(
            parsed.get("constraints_to_preserve"),
            "constraints_to_preserve",
        )
        failure_behavior_to_avoid = (
            _json_string_list(
                parsed.get(
                    "failure_behavior_to_avoid"
                ),
                "failure_behavior_to_avoid",
            )
        )

        gradient_id = _stable_id(
            "gradient",
            {
                "transition_id": transition[
                    "transition_id"
                ],
                "current_prompt": current_prompt,
                "gradient": gradient,
                "prompt_version": prompt_version,
            },
        )

        result = {
            "gradient_id": gradient_id,
            "transition_id": transition[
                "transition_id"
            ],
            "transition_role": transition[
                "transition_role"
            ],
            "sample_id": transition["sample_id"],
            "source_status": transition[
                "source_status"
            ],
            "agent_name": "create_query_hop2",
            "prompt_version": prompt_version,
            "base_prompt_hash": hashlib.sha256(
                current_prompt.encode("utf-8")
            ).hexdigest(),
            "agent_input": {
                "question": source_endpoint.get(
                    "question"
                ),
                "summary_1": source_endpoint.get(
                    "summary_1"
                ),
            },
            "query_transition": {
                "source_query": (
                    query_transition.get(
                        "source_query"
                    )
                ),
                "destination_query": (
                    query_transition.get(
                        "destination_query"
                    )
                ),
                "query_transition_id": (
                    query_transition.get(
                        "query_transition_id"
                    )
                ),
            },
            "retrieval_transition": {
                "source_titles": (
                    source_endpoint.get(
                        "retrieved_titles"
                    )
                    or []
                ),
                "materialized_destination_titles": (
                    target_endpoint.get(
                        "retrieved_titles"
                    )
                    or []
                ),
                "desired_titles": (
                    retrieval_target.get(
                        "desired_titles"
                    )
                    or []
                ),
                "preserve_titles": (
                    retrieval_target.get(
                        "preserve_titles"
                    )
                    or []
                ),
                "avoid_titles": (
                    retrieval_target.get(
                        "avoid_titles"
                    )
                    or []
                ),
                "target_behavior": (
                    retrieval_target.get(
                        "target_behavior"
                    )
                ),
            },
            "gradient": gradient,
            "rationale": rationale,
            "constraints_to_preserve": (
                constraints_to_preserve
            ),
            "failure_behavior_to_avoid": (
                failure_behavior_to_avoid
            ),
            "expected_query_change": (
                expected_query_change
            ),
            "cache_hit": cache_hit,
            "call_input_hash": call_record.get(
                "input_hash"
            ),
        }

        validate_gradient_record(result)
        return result

    # ------------------------------------------------------------------
    # 3. Gradient trace composition
    # ------------------------------------------------------------------

    def compose_trial_prompt(
        self,
        *,
        current_prompt: str,
        gradient_trace: Sequence[
            Mapping[str, Any]
        ],
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        current_prompt = _clean_text(current_prompt)

        if not current_prompt:
            raise ValueError(
                "current_prompt must not be empty."
            )

        if not gradient_trace:
            raise ValueError(
                "gradient_trace must not be empty."
            )

        normalized_trace: list[dict[str, Any]] = []

        for index, record in enumerate(
            gradient_trace
        ):
            validate_gradient_record(record)

            normalized_trace.append({
                "trace_index": index,
                "gradient_id": record[
                    "gradient_id"
                ],
                "transition_id": record[
                    "transition_id"
                ],
                "gradient": record["gradient"],
                "rationale": record["rationale"],
                "constraints_to_preserve": (
                    record.get(
                        "constraints_to_preserve"
                    )
                    or []
                ),
                "failure_behavior_to_avoid": (
                    record.get(
                        "failure_behavior_to_avoid"
                    )
                    or []
                ),
                "expected_query_change": (
                    record.get(
                        "expected_query_change"
                    )
                ),
            })

        payload = {
            "agent_name": "create_query_hop2",
            "base_prompt": current_prompt,
            "ordered_gradient_trace": (
                normalized_trace
            ),
        }

        gradient_ids = [
            record["gradient_id"]
            for record in gradient_trace
        ]

        parsed, cache_hit, call_record = (
            self._cached_json_call(
                stage="trial_prompt_composition",
                system_prompt=(
                    self.trial_composition_system_prompt
                ),
                payload=payload,
                prompt_version=prompt_version,
                metadata={
                    "num_gradients": len(
                        gradient_trace
                    ),
                    "gradient_ids": gradient_ids,
                    **dict(metadata or {}),
                },
            )
        )

        trial_prompt = _clean_text(
            parsed.get("trial_prompt")
        )
        composition_rationale = _clean_text(
            parsed.get("composition_rationale")
        )
        applied_gradient_ids = _json_string_list(
            parsed.get("applied_gradient_ids"),
            "applied_gradient_ids",
        )

        if not trial_prompt:
            raise ValueError(
                "Composition returned no trial_prompt."
            )

        if not composition_rationale:
            raise ValueError(
                "Composition returned no rationale."
            )

        missing_ids = [
            gradient_id
            for gradient_id in gradient_ids
            if gradient_id
            not in applied_gradient_ids
        ]

        if missing_ids:
            raise ValueError(
                "Composition omitted gradient IDs: "
                + ", ".join(missing_ids)
            )

        composition_id = _stable_id(
            "composition",
            {
                "base_prompt": current_prompt,
                "gradient_ids": gradient_ids,
                "trial_prompt": trial_prompt,
            },
        )

        return {
            "composition_id": composition_id,
            "agent_name": "create_query_hop2",
            "prompt_version": prompt_version,
            "base_prompt": current_prompt,
            "gradient_ids": gradient_ids,
            "trial_prompt": trial_prompt,
            "composition_rationale": (
                composition_rationale
            ),
            "applied_gradient_ids": (
                applied_gradient_ids
            ),
            "cache_hit": cache_hit,
            "call_input_hash": call_record.get(
                "input_hash"
            ),
        }


# ---------------------------------------------------------------------------
# DSPy query predictor with temporary instruction
# ---------------------------------------------------------------------------

def _make_query_predictor(
    instruction: str,
) -> dspy.Module:
    """
    Create a fresh query predictor so the shared HotpotRuntime is not mutated.
    """

    instruction = _clean_text(instruction)

    if not instruction:
        raise ValueError(
            "Query instruction must not be empty."
        )

    module = dspy.ChainOfThought(
        "question,summary_1->query"
    )

    predictor = getattr(module, "predict", module)
    signature = getattr(predictor, "signature", None)

    if signature is None:
        raise AttributeError(
            "Could not find DSPy predictor signature."
        )

    if hasattr(signature, "with_instructions"):
        predictor.signature = (
            signature.with_instructions(instruction)
        )
    elif hasattr(signature, "instructions"):
        # Fallback for older DSPy variants.
        signature.instructions = instruction
    else:
        raise AttributeError(
            "DSPy signature does not support "
            "instruction replacement."
        )

    return module


# ---------------------------------------------------------------------------
# 4. Query writer + retrieval intervention
# ---------------------------------------------------------------------------

def run_query_intervention(
    *,
    runtime: HotpotRuntime,
    row: Mapping[str, Any],
    baseline_rollout: Mapping[str, Any],
    trial_prompt: str,
) -> dict[str, Any]:
    """
    Re-run only the parameterized query writer and the retrieval tool.

    Fixed from the baseline trace:
        question
        R1 / hop1 documents
        summary_1

    Re-executed:
        q_trial = Q(question, summary_1; trial_prompt)
        R2_trial = T(q_trial)
    """

    sample_id = _clean_text(
        baseline_rollout.get("sample_id")
    )
    row_sample_id = _clean_text(
        row.get("sample_id") or row.get("id")
    )

    if sample_id != row_sample_id:
        raise ValueError(
            "Row and baseline rollout sample IDs differ."
        )

    question = _clean_text(
        baseline_rollout.get("question")
        or row.get("question")
    )
    summary_1 = _clean_text(
        baseline_rollout.get("summary_1")
    )

    if not question:
        raise ValueError(
            "Baseline trace has no question."
        )

    if not summary_1:
        raise ValueError(
            "Baseline trace has no summary_1."
        )

    query_predictor = _make_query_predictor(
        trial_prompt
    )

    prediction = query_predictor(
        question=question,
        summary_1=summary_1,
    )

    actual_query = _clean_text(
        prediction.query
    )

    if not actual_query:
        raise ValueError(
            "Trial query writer produced an empty query."
        )

    actual_hop2_docs = runtime.retrieve(
        actual_query
    )
    actual_hop2_titles = titles_from_passages(
        actual_hop2_docs
    )

    fixed_hop1_titles = _unique_strings(
        baseline_rollout.get("hop1_titles") or []
    )

    actual_total_titles = _unique_strings(
        [
            *fixed_hop1_titles,
            *actual_hop2_titles,
        ]
    )

    intervention_id = _stable_id(
        "intervention",
        {
            "sample_id": sample_id,
            "trial_prompt": trial_prompt,
            "actual_query": actual_query,
            "actual_hop2_titles": (
                actual_hop2_titles
            ),
        },
    )

    return {
        "intervention_id": intervention_id,
        "sample_id": sample_id,
        "agent_name": "create_query_hop2",
        "fixed_trace": {
            "question": question,
            "summary_1": summary_1,
            "hop1_titles": fixed_hop1_titles,
            "hop1_docs": list(
                baseline_rollout.get(
                    "hop1_docs"
                )
                or []
            ),
        },
        "trial_prompt": trial_prompt,
        "actual_query": actual_query,
        "actual_hop2_titles": (
            actual_hop2_titles
        ),
        "actual_hop2_docs": actual_hop2_docs,
        "actual_total_titles": (
            actual_total_titles
        ),
    }


# ---------------------------------------------------------------------------
# 5. Query-agent local MR metric
# ---------------------------------------------------------------------------

def evaluate_query_local_metric(
    *,
    retrieval_target: Mapping[str, Any],
    intervention_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    First-pass query-agent metric:

        MR = recall of desired retrieval titles in
             fixed hop1 titles union trial hop2 titles

    Atomic success requires full desired-title recall.
    """

    desired_titles = _unique_strings(
        retrieval_target.get("desired_titles")
        or []
    )
    preserve_titles = _unique_strings(
        retrieval_target.get("preserve_titles")
        or []
    )
    avoid_titles = _unique_strings(
        retrieval_target.get("avoid_titles")
        or []
    )

    if not desired_titles:
        raise ValueError(
            "MR evaluation requires at least one "
            "desired title."
        )

    actual_titles = _unique_strings(
        intervention_result.get(
            "actual_total_titles"
        )
        or []
    )

    recovered_titles = [
        title
        for title in desired_titles
        if _title_matches(title, actual_titles)
    ]

    unrecovered_titles = [
        title
        for title in desired_titles
        if not _title_matches(title, actual_titles)
    ]

    preserved_titles = [
        title
        for title in preserve_titles
        if _title_matches(title, actual_titles)
    ]

    lost_preserve_titles = [
        title
        for title in preserve_titles
        if not _title_matches(title, actual_titles)
    ]

    avoid_hits = [
        title
        for title in avoid_titles
        if _title_matches(title, actual_titles)
    ]

    desired_recall = (
        len(recovered_titles)
        / len(desired_titles)
    )

    preserve_recall = (
        len(preserved_titles)
        / len(preserve_titles)
        if preserve_titles
        else None
    )

    local_success = desired_recall == 1.0

    return {
        "metric_name": "missing_recall",
        "metric_scope": (
            "fixed_hop1_union_trial_hop2"
        ),
        "desired_titles": desired_titles,
        "recovered_titles": recovered_titles,
        "unrecovered_titles": (
            unrecovered_titles
        ),
        "desired_recall": desired_recall,
        "preserve_titles": preserve_titles,
        "preserved_titles": preserved_titles,
        "lost_preserve_titles": (
            lost_preserve_titles
        ),
        "preserve_recall": preserve_recall,
        "avoid_titles": avoid_titles,
        "avoid_hits": avoid_hits,
        "local_success": local_success,
        "success_rule": (
            "desired_recall == 1.0"
        ),
    }


# ---------------------------------------------------------------------------
# Combined 1-5 operational probe
# ---------------------------------------------------------------------------

def run_operational_probe(
    *,
    operator: ProgramOperator,
    runtime: HotpotRuntime,
    row: Mapping[str, Any],
    baseline_rollout: Mapping[str, Any],
    transition: Mapping[str, Any],
    current_prompt: str,
    gradient_trace_prefix: Sequence[
        Mapping[str, Any]
    ] = (),
    prompt_version: Optional[int | str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """
    Execute stages 1-5 for one output transition.

    A gradient trace prefix supports later recursive decomposition:

        [g_0, ..., g_{k-1}] + newly inferred g_k
    """

    gradient_record = (
        operator.infer_sample_gradient(
            transition=transition,
            current_prompt=current_prompt,
            prompt_version=prompt_version,
            metadata=metadata,
        )
    )

    full_gradient_trace = [
        *gradient_trace_prefix,
        gradient_record,
    ]

    composition_record = (
        operator.compose_trial_prompt(
            current_prompt=current_prompt,
            gradient_trace=full_gradient_trace,
            prompt_version=prompt_version,
            metadata={
                "sample_id": transition[
                    "sample_id"
                ],
                "transition_id": transition[
                    "transition_id"
                ],
                **dict(metadata or {}),
            },
        )
    )

    intervention_result = (
        run_query_intervention(
            runtime=runtime,
            row=row,
            baseline_rollout=baseline_rollout,
            trial_prompt=composition_record[
                "trial_prompt"
            ],
        )
    )

    local_metric = evaluate_query_local_metric(
        retrieval_target=transition[
            "retrieval_target"
        ],
        intervention_result=intervention_result,
    )

    probe_id = _stable_id(
        "operational_probe",
        {
            "transition_id": transition[
                "transition_id"
            ],
            "gradient_ids": [
                record["gradient_id"]
                for record in full_gradient_trace
            ],
            "intervention_id": (
                intervention_result[
                    "intervention_id"
                ]
            ),
            "local_success": local_metric[
                "local_success"
            ],
        },
    )

    return {
        "probe_id": probe_id,
        "transition_id": transition[
            "transition_id"
        ],
        "sample_id": transition["sample_id"],
        "source_status": transition[
            "source_status"
        ],
        "transition_role": transition[
            "transition_role"
        ],
        "prompt_version": prompt_version,
        "gradient_record": gradient_record,
        "gradient_trace": list(
            full_gradient_trace
        ),
        "composition_record": (
            composition_record
        ),
        "intervention_result": (
            intervention_result
        ),
        "local_metric": local_metric,
        # Assigned in a later evidence-building stage.
        "intervention_label": None,
    }



# ---------------------------------------------------------------------------
# 6. Downstream execution after query intervention
# ---------------------------------------------------------------------------

def run_query_intervention_with_downstream(
    *,
    runtime: HotpotRuntime,
    row: Mapping[str, Any],
    baseline_rollout: Mapping[str, Any],
    intervention_result: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Continue an existing query-only intervention through summarize2 and final.

    The query writer has already been executed under the temporary trial
    prompt. This function reuses its actual query rather than running the query
    writer again.

    Fixed from the baseline trace:
        question
        R1 / hop1 documents
        summary_1

    Re-executed under the current non-query prompts:
        BM25(actual_query)
        summarize2
        final_answer
    """

    sample_id = _clean_text(
        baseline_rollout.get("sample_id")
    )
    row_sample_id = _clean_text(
        row.get("sample_id") or row.get("id")
    )
    intervention_sample_id = _clean_text(
        intervention_result.get("sample_id")
    )

    if not sample_id:
        raise ValueError(
            "Baseline rollout has no sample_id."
        )

    if row_sample_id != sample_id:
        raise ValueError(
            "Dataset row and baseline rollout sample IDs differ."
        )

    if intervention_sample_id != sample_id:
        raise ValueError(
            "Intervention and baseline rollout sample IDs differ."
        )

    actual_query = _clean_text(
        intervention_result.get("actual_query")
    )

    if not actual_query:
        raise ValueError(
            "Intervention result has no actual_query."
        )

    downstream_rollout = runtime.run_from_hop2_query(
        row,
        hop1_docs=(
            baseline_rollout.get("hop1_docs")
            or []
        ),
        hop1_titles=(
            baseline_rollout.get("hop1_titles")
            or []
        ),
        hop1_query=baseline_rollout.get(
            "hop1_query"
        ),
        summary_1=_clean_text(
            baseline_rollout.get("summary_1")
        ),
        hop2_query=actual_query,
    )

    baseline_em = int(
        baseline_rollout.get("score", 0)
    )
    trial_em = int(
        downstream_rollout.get("score", 0)
    )

    result = {
        "downstream_execution_id": _stable_id(
            "downstream_execution",
            {
                "sample_id": sample_id,
                "intervention_id": (
                    intervention_result.get(
                        "intervention_id"
                    )
                ),
                "actual_query": actual_query,
                "baseline_em": baseline_em,
                "trial_em": trial_em,
            },
        ),
        "sample_id": sample_id,
        "intervention_id": (
            intervention_result.get(
                "intervention_id"
            )
        ),
        "actual_query": actual_query,
        "baseline_em": baseline_em,
        "trial_em": trial_em,
        "end_to_end_correct_preserved": (
            baseline_em == 1
            and trial_em == 1
        ),
        "end_to_end_regressed": (
            baseline_em == 1
            and trial_em == 0
        ),
        "downstream_rollout": downstream_rollout,
    }

    return result


# ---------------------------------------------------------------------------
# Evidence-record helpers
# ---------------------------------------------------------------------------

def _collect_probe_records(
    decomposition_result: Mapping[str, Any],
    extra_probe_records: Sequence[
        Mapping[str, Any]
    ] = (),
) -> list[dict[str, Any]]:
    """
    Collect full operational-probe records available in a decomposition tree.

    Current distance.py always preserves the successful probe as
    `verified_probe`. Future versions may also store failed probes as
    `operational_probe`. Both schemas are supported here.

    Failed probe summaries in `intervention_attempts` are not treated as full
    records because they do not contain the complete gradient trace.
    """

    collected: list[dict[str, Any]] = []
    seen_probe_ids: set[str] = set()

    def add_probe(value: Any) -> None:
        if not isinstance(value, Mapping):
            return

        probe_id = _clean_text(
            value.get("probe_id")
        )

        if not probe_id:
            return

        if probe_id in seen_probe_ids:
            return

        seen_probe_ids.add(probe_id)
        collected.append(dict(value))

    def walk(node: Any) -> None:
        if not isinstance(node, Mapping):
            return

        add_probe(node.get("verified_probe"))
        add_probe(node.get("operational_probe"))

        child = node.get("child_result")
        if isinstance(child, Mapping):
            walk(child)

    walk(decomposition_result)

    for probe in extra_probe_records:
        add_probe(probe)

    return collected


def _collect_unique_gradient_trace(
    probe_records: Sequence[
        Mapping[str, Any]
    ],
) -> list[dict[str, Any]]:
    """
    Merge gradient traces while preserving first-observed order.
    """

    output: list[dict[str, Any]] = []
    seen_gradient_ids: set[str] = set()

    for probe in probe_records:
        trace = probe.get("gradient_trace")

        if not isinstance(trace, list):
            gradient_record = probe.get(
                "gradient_record"
            )
            trace = (
                [gradient_record]
                if isinstance(
                    gradient_record,
                    Mapping,
                )
                else []
            )

        for gradient_record in trace:
            if not isinstance(
                gradient_record,
                Mapping,
            ):
                continue

            validate_gradient_record(
                gradient_record
            )

            gradient_id = _clean_text(
                gradient_record.get(
                    "gradient_id"
                )
            )

            if gradient_id in seen_gradient_ids:
                continue

            seen_gradient_ids.add(gradient_id)
            output.append(
                dict(gradient_record)
            )

    return output


def _last_probe_local_metric(
    probe_records: Sequence[
        Mapping[str, Any]
    ],
) -> Optional[dict[str, Any]]:
    for probe in reversed(probe_records):
        metric = probe.get("local_metric")

        if isinstance(metric, Mapping):
            return dict(metric)

    return None


def _validate_decomposition_sample(
    *,
    transition: Mapping[str, Any],
    decomposition_result: Mapping[str, Any],
) -> None:
    validate_transition(transition)

    root_transition_id = _clean_text(
        decomposition_result.get(
            "root_transition_id"
        )
    )

    if (
        root_transition_id
        != _clean_text(
            transition.get("transition_id")
        )
    ):
        raise ValueError(
            "Decomposition root transition does not "
            "match the supplied transition."
        )


# ---------------------------------------------------------------------------
# 7. Wrong-side empirical evidence
# ---------------------------------------------------------------------------

def build_wrong_evidence(
    *,
    root_transition: Mapping[str, Any],
    decomposition_result: Mapping[str, Any],
    extra_probe_records: Sequence[
        Mapping[str, Any]
    ] = (),
) -> dict[str, Any]:
    """
    Convert wrong-side operational attribution into empirical evidence.

    Labels:
        verified_atomic -> W_to_C

        terminal operational failure with at least one complete probe
            -> W_to_W

        no complete failed probe available
            -> unresolved, transition_label=None

    `extra_probe_records` should contain the original program.py root probe when
    the decomposition failed before distance.py retained a complete failed
    probe record.
    """

    _validate_decomposition_sample(
        transition=root_transition,
        decomposition_result=decomposition_result,
    )

    if root_transition["source_status"] != "W":
        raise ValueError(
            "build_wrong_evidence requires source_status=W."
        )

    status = _clean_text(
        decomposition_result.get("status")
    )

    probe_records = _collect_probe_records(
        decomposition_result,
        extra_probe_records=extra_probe_records,
    )
    gradient_trace = (
        _collect_unique_gradient_trace(
            probe_records
        )
    )
    local_metric = _last_probe_local_metric(
        probe_records
    )

    verified_probe = decomposition_result.get(
        "verified_probe"
    )
    verified_transition = (
        decomposition_result.get(
            "verified_atomic_transition"
        )
    )

    if (
        status == "verified_atomic"
        and isinstance(
            verified_probe,
            Mapping,
        )
        and isinstance(
            verified_transition,
            Mapping,
        )
        and bool(
            verified_probe.get(
                "local_metric",
                {},
            ).get("local_success")
        )
    ):
        transition_label = "W_to_C"
        evidence_status = (
            "verified_wrong_repair"
        )
        selected_probe = dict(verified_probe)
        selected_transition = dict(
            verified_transition
        )

    elif probe_records and gradient_trace:
        transition_label = "W_to_W"
        evidence_status = (
            "failed_wrong_intervention"
        )
        selected_probe = dict(
            probe_records[-1]
        )
        selected_transition = None

    else:
        transition_label = None
        evidence_status = (
            "unresolved_missing_full_probe"
        )
        selected_probe = None
        selected_transition = None

    output_trace = decomposition_result.get(
        "semantic_path"
    )

    if not isinstance(output_trace, list):
        output_trace = [
            root_transition["source_endpoint"],
            root_transition["target_endpoint"],
        ]

    evidence_id = _stable_id(
        "evidence",
        {
            "sample_id": root_transition[
                "sample_id"
            ],
            "root_transition_id": (
                root_transition[
                    "transition_id"
                ]
            ),
            "transition_label": transition_label,
            "decomposition_status": status,
            "gradient_ids": [
                gradient["gradient_id"]
                for gradient in gradient_trace
            ],
        },
    )

    return {
        "evidence_id": evidence_id,
        "agent_name": "create_query_hop2",
        "sample_id": root_transition[
            "sample_id"
        ],
        "source_status": "W",
        "transition_label": transition_label,
        "evidence_status": evidence_status,
        "root_transition_id": (
            root_transition["transition_id"]
        ),
        "decomposition_id": (
            decomposition_result.get(
                "decomposition_id"
            )
        ),
        "decomposition_status": status,
        "output_trace": output_trace,
        "gradient_trace": gradient_trace,
        "verified_atomic_transition": (
            selected_transition
        ),
        "selected_probe": selected_probe,
        "local_metric": local_metric,
        "intervention_attempts": list(
            decomposition_result.get(
                "intervention_attempts"
            )
            or []
        ),
        "midpoint_validations": list(
            decomposition_result.get(
                "midpoint_validations"
            )
            or []
        ),
        "aggregation_eligible": (
            transition_label
            in {"W_to_C", "W_to_W"}
            and bool(gradient_trace)
        ),
    }


# ---------------------------------------------------------------------------
# 8. Correct-side empirical evidence
# ---------------------------------------------------------------------------

def build_correct_evidence(
    *,
    transport_transition: Mapping[str, Any],
    decomposition_result: Mapping[str, Any],
    downstream_result: Optional[
        Mapping[str, Any]
    ],
    matched_wrong_evidence_id: str,
    extra_probe_records: Sequence[
        Mapping[str, Any]
    ] = (),
) -> dict[str, Any]:
    """
    Construct correct-case evidence.

    Two distinct conditions are recorded:

    1. Transport realization:
       Did the trial prompt produce the virtual retrieval destination according
       to the query-local MR metric?

    2. Safety outcome:
       Did the originally correct end-to-end answer remain correct?

    C_to_C/C_to_W is assigned only when transport realization succeeded.
    A non-realized transport is not positive preservation evidence.
    """

    _validate_decomposition_sample(
        transition=transport_transition,
        decomposition_result=decomposition_result,
    )

    if transport_transition["source_status"] != "C":
        raise ValueError(
            "build_correct_evidence requires source_status=C."
        )

    matched_wrong_evidence_id = _clean_text(
        matched_wrong_evidence_id
    )

    if not matched_wrong_evidence_id:
        raise ValueError(
            "matched_wrong_evidence_id must not be empty."
        )

    status = _clean_text(
        decomposition_result.get("status")
    )

    probe_records = _collect_probe_records(
        decomposition_result,
        extra_probe_records=extra_probe_records,
    )
    gradient_trace = (
        _collect_unique_gradient_trace(
            probe_records
        )
    )

    verified_probe = decomposition_result.get(
        "verified_probe"
    )

    transport_realized = (
        status == "verified_atomic"
        and isinstance(
            verified_probe,
            Mapping,
        )
        and bool(
            verified_probe.get(
                "local_metric",
                {},
            ).get("local_success")
        )
    )

    local_metric = (
        dict(
            verified_probe.get(
                "local_metric"
            )
        )
        if (
            isinstance(
                verified_probe,
                Mapping,
            )
            and isinstance(
                verified_probe.get(
                    "local_metric"
                ),
                Mapping,
            )
        )
        else _last_probe_local_metric(
            probe_records
        )
    )

    baseline_em: Optional[int] = None
    trial_em: Optional[int] = None
    downstream_execution_id = None
    downstream_rollout = None

    if downstream_result is not None:
        if not isinstance(
            downstream_result,
            Mapping,
        ):
            raise ValueError(
                "downstream_result must be an object."
            )

        downstream_sample_id = _clean_text(
            downstream_result.get("sample_id")
        )

        if (
            downstream_sample_id
            != transport_transition["sample_id"]
        ):
            raise ValueError(
                "Downstream result sample ID mismatch."
            )

        baseline_em = int(
            downstream_result.get(
                "baseline_em",
                0,
            )
        )
        trial_em = int(
            downstream_result.get(
                "trial_em",
                0,
            )
        )
        downstream_execution_id = (
            downstream_result.get(
                "downstream_execution_id"
            )
        )
        downstream_rollout = (
            downstream_result.get(
                "downstream_rollout"
            )
        )

    if transport_realized:
        if downstream_result is None:
            transition_label = None
            evidence_status = (
                "transport_realized_downstream_missing"
            )

        elif baseline_em != 1:
            raise ValueError(
                "Correct-side evidence requires "
                "baseline end-to-end EM=1."
            )

        elif trial_em == 1:
            transition_label = "C_to_C"
            evidence_status = (
                "transport_realized_correct_preserved"
            )

        else:
            transition_label = "C_to_W"
            evidence_status = (
                "transport_realized_correct_broken"
            )

    else:
        transition_label = None
        evidence_status = (
            "transport_not_realized"
        )

    output_trace = decomposition_result.get(
        "semantic_path"
    )

    if not isinstance(output_trace, list):
        output_trace = [
            transport_transition[
                "source_endpoint"
            ],
            transport_transition[
                "target_endpoint"
            ],
        ]

    evidence_id = _stable_id(
        "evidence",
        {
            "sample_id": transport_transition[
                "sample_id"
            ],
            "transport_transition_id": (
                transport_transition[
                    "transition_id"
                ]
            ),
            "matched_wrong_evidence_id": (
                matched_wrong_evidence_id
            ),
            "transport_realized": (
                transport_realized
            ),
            "transition_label": transition_label,
            "baseline_em": baseline_em,
            "trial_em": trial_em,
            "gradient_ids": [
                gradient["gradient_id"]
                for gradient in gradient_trace
            ],
        },
    )

    return {
        "evidence_id": evidence_id,
        "agent_name": "create_query_hop2",
        "sample_id": transport_transition[
            "sample_id"
        ],
        "source_status": "C",
        "transition_label": transition_label,
        "evidence_status": evidence_status,
        "transport_transition_id": (
            transport_transition[
                "transition_id"
            ]
        ),
        "matched_wrong_evidence_id": (
            matched_wrong_evidence_id
        ),
        "decomposition_id": (
            decomposition_result.get(
                "decomposition_id"
            )
        ),
        "decomposition_status": status,
        "transport_realized": (
            transport_realized
        ),
        "transport_local_metric": (
            local_metric
        ),
        "baseline_em": baseline_em,
        "trial_em": trial_em,
        "downstream_execution_id": (
            downstream_execution_id
        ),
        "downstream_rollout": (
            downstream_rollout
        ),
        "output_trace": output_trace,
        "gradient_trace": gradient_trace,
        "verified_atomic_transition": (
            decomposition_result.get(
                "verified_atomic_transition"
            )
        ),
        "verified_probe": (
            dict(verified_probe)
            if isinstance(
                verified_probe,
                Mapping,
            )
            else None
        ),
        "intervention_attempts": list(
            decomposition_result.get(
                "intervention_attempts"
            )
            or []
        ),
        "aggregation_eligible": (
            transition_label
            in {"C_to_C", "C_to_W"}
            and transport_realized
            and bool(gradient_trace)
        ),
    }




# ---------------------------------------------------------------------------
# 9. Agent-wise gradient aggregation
# ---------------------------------------------------------------------------

HOTPOT_PROMPT_ALIASES = {
    "summarize1": (
        "summarize1.predict",
        "summarize1",
    ),
    "create_query_hop2": (
        "create_query_hop2.predict",
        "create_query_hop2",
    ),
    "summarize2": (
        "summarize2.predict",
        "summarize2",
    ),
    "final_answer": (
        "final_answer.predict",
        "final_answer",
    ),
}

AGGREGATION_LABELS = (
    "W_to_C",
    "W_to_W",
    "C_to_C",
    "C_to_W",
)


def resolve_candidate_prompt_key(
    candidate: Mapping[str, Any],
    base_name: str,
) -> str:
    if base_name not in HOTPOT_PROMPT_ALIASES:
        raise KeyError(
            f"Unknown Hotpot predictor base name: {base_name}"
        )

    matches = [
        key
        for key in HOTPOT_PROMPT_ALIASES[base_name]
        if key in candidate
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one candidate key for "
            f"{base_name}, found {matches}."
        )

    return matches[0]


def normalize_full_candidate(
    candidate: Mapping[str, Any],
) -> dict[str, str]:
    """
    Accept raw candidates and wrapped eval-only candidates while preserving
    the actual DSPy predictor-key style.
    """

    if not isinstance(candidate, Mapping):
        raise ValueError(
            "Candidate must be an object."
        )

    if isinstance(
        candidate.get("prompts"),
        Mapping,
    ):
        candidate = candidate["prompts"]
    elif isinstance(
        candidate.get("candidate"),
        Mapping,
    ):
        candidate = candidate["candidate"]

    normalized: dict[str, str] = {}

    for key, value in candidate.items():
        text = _clean_text(value)

        if text:
            normalized[str(key)] = text

    known_aliases = {
        alias
        for aliases in HOTPOT_PROMPT_ALIASES.values()
        for alias in aliases
    }

    unknown = set(normalized) - known_aliases
    if unknown:
        raise ValueError(
            "Candidate has unknown predictor keys: "
            + ", ".join(sorted(unknown))
        )

    for base_name in HOTPOT_PROMPT_ALIASES:
        resolve_candidate_prompt_key(
            normalized,
            base_name,
        )

    return normalized



def build_full_candidate(
    *,
    current_candidate: Mapping[str, Any],
    query_candidate_prompt: str,
) -> dict[str, str]:
    """
    Replace only create_query_hop2 and preserve all other agents.
    """

    current = normalize_full_candidate(
        current_candidate
    )

    query_candidate_prompt = _clean_text(
        query_candidate_prompt
    )

    if not query_candidate_prompt:
        raise ValueError(
            "query_candidate_prompt must not be empty."
        )

    updated = dict(current)
    query_key = resolve_candidate_prompt_key(
        updated,
        "create_query_hop2",
    )
    updated[query_key] = query_candidate_prompt

    return updated


def _compact_output_trace(
    output_trace: Any,
) -> list[dict[str, Any]]:
    if not isinstance(output_trace, list):
        return []

    compact: list[dict[str, Any]] = []

    for endpoint in output_trace:
        if not isinstance(endpoint, Mapping):
            continue

        retrieval_target = endpoint.get(
            "retrieval_target"
        )

        if not isinstance(
            retrieval_target,
            Mapping,
        ):
            retrieval_target = {}

        compact.append({
            "endpoint_id": endpoint.get(
                "endpoint_id"
            ),
            "endpoint_type": endpoint.get(
                "endpoint_type"
            ),
            "materialization": endpoint.get(
                "materialization"
            ),
            "query": endpoint.get("query"),
            "retrieved_titles": list(
                endpoint.get(
                    "retrieved_titles"
                )
                or []
            ),
            "desired_titles": list(
                retrieval_target.get(
                    "desired_titles"
                )
                or []
            ),
            "preserve_titles": list(
                retrieval_target.get(
                    "preserve_titles"
                )
                or []
            ),
            "avoid_titles": list(
                retrieval_target.get(
                    "avoid_titles"
                )
                or []
            ),
            "target_behavior": (
                retrieval_target.get(
                    "target_behavior"
                )
            ),
        })

    return compact


def _compact_gradient_trace(
    gradient_trace: Any,
) -> list[dict[str, Any]]:
    if not isinstance(gradient_trace, list):
        return []

    compact: list[dict[str, Any]] = []

    for gradient_record in gradient_trace:
        if not isinstance(
            gradient_record,
            Mapping,
        ):
            continue

        validate_gradient_record(
            gradient_record
        )

        compact.append({
            "gradient_id": gradient_record[
                "gradient_id"
            ],
            "transition_id": gradient_record[
                "transition_id"
            ],
            "transition_role": (
                gradient_record.get(
                    "transition_role"
                )
            ),
            "gradient": gradient_record[
                "gradient"
            ],
            "rationale": gradient_record[
                "rationale"
            ],
            "expected_query_change": (
                gradient_record.get(
                    "expected_query_change"
                )
            ),
            "constraints_to_preserve": list(
                gradient_record.get(
                    "constraints_to_preserve"
                )
                or []
            ),
            "failure_behavior_to_avoid": list(
                gradient_record.get(
                    "failure_behavior_to_avoid"
                )
                or []
            ),
            "query_transition": dict(
                gradient_record.get(
                    "query_transition"
                )
                or {}
            ),
            "retrieval_transition": dict(
                gradient_record.get(
                    "retrieval_transition"
                )
                or {}
            ),
        })

    return compact


def compact_aggregation_evidence(
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Retain output-delta, prompt-gradient, empirical label, and metric context.

    Trial prompts and full downstream rollouts are intentionally excluded.
    Aggregation operates on verified gradients rather than samplewise prompts.
    """

    evidence_id = _clean_text(
        evidence.get("evidence_id")
    )
    transition_label = _clean_text(
        evidence.get("transition_label")
    )

    if not evidence_id:
        raise ValueError(
            "Evidence has no evidence_id."
        )

    if transition_label not in AGGREGATION_LABELS:
        raise ValueError(
            "Unsupported aggregation label: "
            f"{transition_label}"
        )

    if not bool(
        evidence.get("aggregation_eligible")
    ):
        raise ValueError(
            f"Evidence {evidence_id} is not "
            "aggregation eligible."
        )

    gradient_trace = _compact_gradient_trace(
        evidence.get("gradient_trace")
    )

    if not gradient_trace:
        raise ValueError(
            f"Evidence {evidence_id} has no "
            "usable gradient trace."
        )

    local_metric = (
        evidence.get("local_metric")
        or evidence.get(
            "transport_local_metric"
        )
        or {}
    )

    return {
        "evidence_id": evidence_id,
        "sample_id": evidence.get(
            "sample_id"
        ),
        "source_status": evidence.get(
            "source_status"
        ),
        "transition_label": transition_label,
        "evidence_status": evidence.get(
            "evidence_status"
        ),
        "output_trace": _compact_output_trace(
            evidence.get("output_trace")
        ),
        "gradient_trace": gradient_trace,
        "local_metric": dict(local_metric),
        "transport_realized": evidence.get(
            "transport_realized"
        ),
        "baseline_em": evidence.get(
            "baseline_em"
        ),
        "trial_em": evidence.get(
            "trial_em"
        ),
        "matched_wrong_evidence_id": (
            evidence.get(
                "matched_wrong_evidence_id"
            )
        ),
    }


def prepare_aggregation_evidence(
    evidence_records: Sequence[
        Mapping[str, Any]
    ],
) -> tuple[
    list[dict[str, Any]],
    dict[str, int],
]:
    if not evidence_records:
        raise ValueError(
            "evidence_records must not be empty."
        )

    compact_records: list[
        dict[str, Any]
    ] = []
    seen_evidence_ids: set[str] = set()

    counts = {
        label: 0
        for label in AGGREGATION_LABELS
    }

    for evidence in evidence_records:
        compact = compact_aggregation_evidence(
            evidence
        )

        evidence_id = compact["evidence_id"]

        if evidence_id in seen_evidence_ids:
            raise ValueError(
                "Duplicate evidence_id: "
                f"{evidence_id}"
            )

        seen_evidence_ids.add(evidence_id)

        counts[
            compact["transition_label"]
        ] += 1

        compact_records.append(compact)

    label_order = {
        label: index
        for index, label in enumerate(
            AGGREGATION_LABELS
        )
    }

    compact_records.sort(
        key=lambda record: (
            label_order[
                record["transition_label"]
            ],
            str(record["evidence_id"]),
        )
    )

    return compact_records, counts


def aggregate_gradients(
    *,
    operator: ProgramOperator,
    current_candidate: Mapping[str, Any],
    evidence_records: Sequence[
        Mapping[str, Any]
    ],
    prompt_version: Optional[int | str] = None,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> dict[str, Any]:
    """
    Aggregate samplewise verified gradients into one query-agent prompt.

    This is the first point at which a reusable candidate prompt is produced.
    """

    normalized_candidate = (
        normalize_full_candidate(
            current_candidate
        )
    )

    query_key = resolve_candidate_prompt_key(
        normalized_candidate,
        "create_query_hop2",
    )
    current_query_prompt = (
        normalized_candidate[query_key]
    )

    compact_evidence, evidence_counts = (
        prepare_aggregation_evidence(
            evidence_records
        )
    )

    eligible_evidence_ids = [
        record["evidence_id"]
        for record in compact_evidence
    ]

    payload = {
        "agent_name": "create_query_hop2",
        "current_prompt": current_query_prompt,
        "evidence_counts": evidence_counts,
        "empirical_evidence": (
            compact_evidence
        ),
    }

    parsed, cache_hit, call_record = (
        operator._cached_json_call(
            stage="gradient_aggregation",
            system_prompt=(
                GRADIENT_AGGREGATION_SYSTEM_PROMPT
            ),
            payload=payload,
            prompt_version=prompt_version,
            metadata={
                "agent_name": (
                    "create_query_hop2"
                ),
                "num_evidence": len(
                    compact_evidence
                ),
                "evidence_counts": (
                    evidence_counts
                ),
                "evidence_ids": (
                    eligible_evidence_ids
                ),
                **dict(metadata or {}),
            },
        )
    )

    candidate_prompt = _clean_text(
        parsed.get("candidate_prompt")
    )
    aggregation_rationale = _clean_text(
        parsed.get(
            "aggregation_rationale"
        )
    )

    if not candidate_prompt:
        raise ValueError(
            "Aggregation returned no "
            "candidate_prompt."
        )

    if not aggregation_rationale:
        raise ValueError(
            "Aggregation returned no rationale."
        )

    used_evidence_ids = _json_string_list(
        parsed.get("used_evidence_ids"),
        "used_evidence_ids",
    )
    rejected_evidence_ids = (
        _json_string_list(
            parsed.get(
                "rejected_evidence_ids"
            ),
            "rejected_evidence_ids",
        )
    )

    unknown_used = (
        set(used_evidence_ids)
        - set(eligible_evidence_ids)
    )
    unknown_rejected = (
        set(rejected_evidence_ids)
        - set(eligible_evidence_ids)
    )

    if unknown_used:
        raise ValueError(
            "Aggregation returned unknown used "
            "evidence IDs: "
            + ", ".join(sorted(unknown_used))
        )

    if unknown_rejected:
        raise ValueError(
            "Aggregation returned unknown rejected "
            "evidence IDs: "
            + ", ".join(
                sorted(unknown_rejected)
            )
        )

    overlap = (
        set(used_evidence_ids)
        & set(rejected_evidence_ids)
    )

    if overlap:
        raise ValueError(
            "Evidence IDs appear in both used and "
            "rejected lists: "
            + ", ".join(sorted(overlap))
        )

    covered = (
        set(used_evidence_ids)
        | set(rejected_evidence_ids)
    )
    missing_decisions = (
        set(eligible_evidence_ids)
        - covered
    )

    if missing_decisions:
        raise ValueError(
            "Aggregation did not classify evidence "
            "IDs as used or rejected: "
            + ", ".join(
                sorted(missing_decisions)
            )
        )

    if not used_evidence_ids:
        raise ValueError(
            "Aggregation rejected every evidence "
            "record."
        )

    preserved_behaviors = (
        _json_string_list(
            parsed.get(
                "preserved_behaviors"
            ),
            "preserved_behaviors",
        )
    )
    introduced_behaviors = (
        _json_string_list(
            parsed.get(
                "introduced_behaviors"
            ),
            "introduced_behaviors",
        )
    )
    suppressed_behaviors = (
        _json_string_list(
            parsed.get(
                "suppressed_behaviors"
            ),
            "suppressed_behaviors",
        )
    )

    full_candidate = build_full_candidate(
        current_candidate=(
            normalized_candidate
        ),
        query_candidate_prompt=(
            candidate_prompt
        ),
    )

    aggregation_id = _stable_id(
        "aggregation",
        {
            "prompt_version": prompt_version,
            "current_query_prompt": (
                current_query_prompt
            ),
            "candidate_prompt": (
                candidate_prompt
            ),
            "used_evidence_ids": (
                used_evidence_ids
            ),
            "rejected_evidence_ids": (
                rejected_evidence_ids
            ),
        },
    )

    return {
        "aggregation_id": aggregation_id,
        "agent_name": "create_query_hop2",
        "prompt_version": prompt_version,
        "current_prompt": (
            current_query_prompt
        ),
        "candidate_prompt": (
            candidate_prompt
        ),
        "full_candidate": full_candidate,
        "aggregation_rationale": (
            aggregation_rationale
        ),
        "evidence_counts": evidence_counts,
        "eligible_evidence_ids": (
            eligible_evidence_ids
        ),
        "used_evidence_ids": (
            used_evidence_ids
        ),
        "rejected_evidence_ids": (
            rejected_evidence_ids
        ),
        "preserved_behaviors": (
            preserved_behaviors
        ),
        "introduced_behaviors": (
            introduced_behaviors
        ),
        "suppressed_behaviors": (
            suppressed_behaviors
        ),
        "compact_evidence": (
            compact_evidence
        ),
        "cache_hit": cache_hit,
        "call_input_hash": (
            call_record.get("input_hash")
        ),
    }


def save_aggregation_candidate(
    *,
    run_dir: str | Path,
    aggregation_result: Mapping[
        str,
        Any,
    ],
    name: Optional[str] = None,
) -> dict[str, str]:
    """
    Save both candidate representations used by the official Hotpot runner.

    candidate.json:
        raw dict[str, str], directly usable by adapter.evaluate()

    prompt_candidate.json:
        top-level {"name": ..., "prompts": ...}, usable with --eval-only
    """

    run_dir = Path(run_dir)
    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    full_candidate = (
        normalize_full_candidate(
            aggregation_result[
                "full_candidate"
            ]
        )
    )

    aggregation_id = _clean_text(
        aggregation_result.get(
            "aggregation_id"
        )
    )

    candidate_name = (
        _clean_text(name)
        or aggregation_id
        or "method_probe_candidate"
    )

    raw_candidate_path = (
        run_dir / "candidate.json"
    )
    wrapped_candidate_path = (
        run_dir / "prompt_candidate.json"
    )
    aggregation_path = (
        run_dir / "aggregation.json"
    )

    atomic_write_json(
        raw_candidate_path,
        full_candidate,
    )

    atomic_write_json(
        wrapped_candidate_path,
        {
            "name": candidate_name,
            "prompts": full_candidate,
        },
    )

    atomic_write_json(
        aggregation_path,
        dict(aggregation_result),
    )

    return {
        "candidate": str(
            raw_candidate_path
        ),
        "prompt_candidate": str(
            wrapped_candidate_path
        ),
        "aggregation": str(
            aggregation_path
        ),
    }



# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Infer a local query-prompt gradient, "
            "compose a temporary prompt, execute the "
            "query-retrieval intervention, and evaluate MR."
        )
    )

    parser.add_argument(
        "--transition",
        required=True,
    )
    parser.add_argument(
        "--baseline-rollout",
        required=True,
    )
    parser.add_argument(
        "--data",
        required=True,
    )
    parser.add_argument(
        "--row-index",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--current-prompt",
        default=None,
    )
    parser.add_argument(
        "--prompt-file",
        default=None,
    )

    parser.add_argument(
        "--model",
        default="openai/gpt-5-mini",
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
        "--max-retries",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--prompt-version",
        type=int,
        default=0,
    )

    parser.add_argument(
        "--retriever-dir",
        default="examples/hotpotqa",
    )
    parser.add_argument(
        "--retrieval-k",
        type=int,
        default=7,
    )

    parser.add_argument(
        "--cache-root",
        default=(
            "experiments/method_probe/cache/calls"
        ),
    )
    parser.add_argument(
        "--events",
        default=(
            "experiments/method_probe/runs/"
            "program_smoke/events.jsonl"
        ),
    )
    parser.add_argument(
        "--out",
        required=True,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    rows = load_jsonl(args.data)

    if args.row_index < 0:
        raise ValueError(
            "row-index must be non-negative."
        )

    if args.row_index >= len(rows):
        raise IndexError(
            f"row-index {args.row_index} exceeds "
            f"dataset size {len(rows)}."
        )

    row = rows[args.row_index]

    transition = json.loads(
        Path(args.transition).read_text(
            encoding="utf-8"
        )
    )
    baseline_rollout = json.loads(
        Path(args.baseline_rollout).read_text(
            encoding="utf-8"
        )
    )

    sample_id = _clean_text(
        transition.get("sample_id")
    )

    if (
        _clean_text(
            row.get("sample_id") or row.get("id")
        )
        != sample_id
    ):
        raise ValueError(
            "Dataset row does not match transition."
        )

    if (
        _clean_text(
            baseline_rollout.get("sample_id")
        )
        != sample_id
    ):
        raise ValueError(
            "Baseline rollout does not match transition."
        )

    current_prompt = load_current_query_prompt(
        current_prompt=args.current_prompt,
        prompt_file=args.prompt_file,
    )

    configure_lm(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    runtime = HotpotRuntime(
        retrieval_k=args.retrieval_k,
        retriever_dir=args.retriever_dir,
    )

    cache = CallCache(
        args.cache_root,
        events_path=args.events,
    )

    operator = ProgramOperator(
        cache=cache,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        max_retries=args.max_retries,
    )

    result = run_operational_probe(
        operator=operator,
        runtime=runtime,
        row=row,
        baseline_rollout=baseline_rollout,
        transition=transition,
        current_prompt=current_prompt,
        prompt_version=args.prompt_version,
        metadata={
            "entrypoint": "program.py",
            "row_index": args.row_index,
        },
    )

    atomic_write_json(args.out, result)

    print(json.dumps({
        "probe_id": result["probe_id"],
        "sample_id": result["sample_id"],
        "transition_id": result[
            "transition_id"
        ],
        "gradient_id": result[
            "gradient_record"
        ]["gradient_id"],
        "gradient": result[
            "gradient_record"
        ]["gradient"],
        "trial_prompt": result[
            "composition_record"
        ]["trial_prompt"],
        "source_query": transition[
            "query_transition"
        ]["source_query"],
        "destination_query": transition[
            "query_transition"
        ]["destination_query"],
        "actual_query": result[
            "intervention_result"
        ]["actual_query"],
        "actual_hop2_titles": result[
            "intervention_result"
        ]["actual_hop2_titles"],
        "desired_titles": result[
            "local_metric"
        ]["desired_titles"],
        "recovered_titles": result[
            "local_metric"
        ]["recovered_titles"],
        "desired_recall": result[
            "local_metric"
        ]["desired_recall"],
        "local_success": result[
            "local_metric"
        ]["local_success"],
        "intervention_label": result[
            "intervention_label"
        ],
        "saved": args.out,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
