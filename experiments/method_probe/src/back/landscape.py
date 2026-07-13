#!/usr/bin/env python3
from __future__ import annotations

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

from litellm import completion  # noqa: E402

from experiments.method_probe.src.cache import CallCache  # noqa: E402
from experiments.method_probe.src.hotpot import HotpotRuntime  # noqa: E402


# ---------------------------------------------------------------------------
# Default prompts
# ---------------------------------------------------------------------------

DEFAULT_DESTINATION_QUERY_SYSTEM_PROMPT = """
You invert a desired HotpotQA retrieval-state transition into a destination
second-hop query.

The query writer receives the original question and summary_1. A search tool
then maps the query into a retrieval state.

You are given:
- the current query,
- the current retrieval state,
- a desired retrieval target.

Infer one executable destination query that should move the search tool from
the current retrieval state toward the desired retrieval target.

Requirements:
- Preserve useful entity, title, alias, and relation anchors from the source.
- Add the anchors needed to reach the desired evidence.
- Remove or disambiguate anchors that caused irrelevant retrieval.
- Do not simply output an answer.
- Do not mention this instruction or the transition representation.
- Return one search query, not a prompt update.
- The result represents q_destination in the inversion:
      delta R -> delta q

Return JSON only:
{
  "destination_query": "one executable second-hop query",
  "inversion_rationale": "why this query should produce the target retrieval",
  "anchors_preserved": ["..."],
  "anchors_added": ["..."],
  "anchors_removed_or_disambiguated": ["..."]
}
""".strip()


DEFAULT_MIDPOINT_RETRIEVAL_SYSTEM_PROMPT = """
You generate a semantic midpoint retrieval target between two HotpotQA
retrieval endpoints.

The midpoint is defined in retrieval-output space, not query-text space.

Construct a retrieval target R_mid that makes only part of the semantic move
from the source endpoint toward the destination endpoint.

It should:
- preserve useful evidence already present in the source,
- introduce only part of the missing destination evidence or behavior,
- avoid simply copying the full destination state,
- remain relevant to the original question and summary_1.

Return JSON only:
{
  "desired_titles": ["titles or evidence families desired at the midpoint"],
  "preserve_titles": ["source evidence that should remain"],
  "avoid_titles": ["irrelevant evidence that should be suppressed"],
  "target_behavior": "semantic description of the midpoint retrieval state",
  "rationale": "why this is between source and destination"
}
""".strip()


DEFAULT_TRANSPORT_MATCH_SYSTEM_PROMPT = """
You select the wrong-side retrieval repair transition that is most transferable
to a given correct HotpotQA retrieval state.

Match retrieval behavior rather than topic similarity alone:
- entity, title, and alias anchoring,
- bridge or comparison relation,
- distractor and wrong-sense behavior,
- candidate-set breadth,
- evidence family,
- query shape.

Return JSON only:
{
  "matched_transition_id": "one candidate transition id",
  "rationale": "why its retrieval transition is transferable",
  "confidence": 0.0
}
""".strip()


DEFAULT_TRANSPORT_RETRIEVAL_SYSTEM_PROMPT = """
You transport a wrong-side retrieval transition onto a correct HotpotQA
retrieval state.

You are given:
1. a correct reference retrieval endpoint,
2. a wrong-side transition from a failed retrieval state to a repaired state.

Infer the failure behavior removed by the wrong-side repair. Apply that failure
behavior locally to the correct reference state to define a virtual damaged
retrieval target.

Define the virtual target in retrieval-output space. Do not directly write a
prompt update. Do not assume that the virtual state has already been produced
by BM25.

Return JSON only:
{
  "desired_titles": ["titles or evidence families likely in the damaged state"],
  "preserve_titles": ["reference evidence that should remain"],
  "avoid_titles": ["reference evidence likely lost or displaced"],
  "target_behavior": "the transported damaged retrieval behavior",
  "expected_failure_behavior": "the wrong-side failure being transported",
  "locality_check": "why the damage remains local to the correct sample",
  "rationale": "how the retrieval transition was transported"
}
""".strip()


# ---------------------------------------------------------------------------
# Generic utilities
# ---------------------------------------------------------------------------

def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _unique_strings(values: Iterable[Any]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()

    for value in values:
        text = _clean_text(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)

    return output


def _json_string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a JSON list.")

    return _unique_strings(value)


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
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
                f"No JSON object found in response: {text[:500]}"
            )

        parsed = json.loads(text[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError(
            f"Expected JSON object, got {type(parsed).__name__}."
        )

    return parsed


def _completion_text(response: Any) -> str:
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, KeyError, TypeError) as exc:
        raise ValueError(
            f"Could not extract completion text from "
            f"{type(response).__name__}."
        ) from exc

    text = _clean_text(content)
    if not text:
        raise ValueError("Completion response has empty content.")

    return text


def _metric_value(
    endpoint: Mapping[str, Any],
    key: str,
) -> Optional[float]:
    metrics = endpoint.get("metrics") or {}
    value = metrics.get(key)

    if value is None:
        return None

    return float(value)


def _metric_delta(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    key: str,
) -> Optional[float]:
    source_value = _metric_value(source, key)
    target_value = _metric_value(target, key)

    if source_value is None or target_value is None:
        return None

    return target_value - source_value


# ---------------------------------------------------------------------------
# Endpoint normalization
# ---------------------------------------------------------------------------

def make_query_endpoint(
    rollout: Mapping[str, Any],
    *,
    endpoint_type: str,
    materialization: str = "actual",
    metadata: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """
    Normalize an actual query-retrieval endpoint.

    The endpoint stores both the inner query q and the outer retrieval state R.
    """

    sample_id = _clean_text(
        rollout.get("sample_id") or rollout.get("id")
    )
    question = _clean_text(rollout.get("question"))
    summary_1 = _clean_text(rollout.get("summary_1"))
    query = _clean_text(
        rollout.get("hop2_query") or rollout.get("query")
    )

    if not sample_id:
        raise ValueError("Endpoint rollout has no sample_id.")
    if not question:
        raise ValueError(
            f"Endpoint {sample_id} has no question."
        )
    if not query:
        raise ValueError(
            f"Endpoint {sample_id} has no hop2 query."
        )

    endpoint = {
        "sample_id": sample_id,
        "endpoint_type": endpoint_type,
        "materialization": materialization,
        "question": question,
        "summary_1": summary_1,
        "query": query,
        "retrieved_titles": _unique_strings(
            rollout.get("hop2_titles") or []
        ),
        "retrieved_docs": list(
            rollout.get("hop2_docs") or []
        ),
        "summary_2": _clean_text(
            rollout.get("summary_2")
        ),
        "pred_answer": _clean_text(
            rollout.get("pred_answer")
        ),
        "metrics": {
            "missing_recovery_rate": rollout.get(
                "missing_recovery_rate"
            ),
            "support_recall_hop1": rollout.get(
                "support_recall_hop1"
            ),
            "support_recall_hop2_only": rollout.get(
                "support_recall_hop2_only"
            ),
            "support_recall_total": rollout.get(
                "support_recall_total"
            ),
            "exact_match": (
                int(rollout.get("score", 0))
                if rollout.get("score") is not None
                else None
            ),
            "natural_retrieval_failure": (
                bool(rollout.get("natural_retrieval_failure"))
                if rollout.get("natural_retrieval_failure")
                is not None
                else None
            ),
        },
        "retrieval": {
            "gold_support_titles": _unique_strings(
                rollout.get("gold_support_titles") or []
            ),
            "hop1_titles": _unique_strings(
                rollout.get("hop1_titles") or []
            ),
            "hop2_titles": _unique_strings(
                rollout.get("hop2_titles") or []
            ),
            "missing_after_hop1": _unique_strings(
                rollout.get("missing_after_hop1") or []
            ),
            "recovered_missing_titles": _unique_strings(
                rollout.get("recovered_missing_titles") or []
            ),
            "missing_after_hop2": _unique_strings(
                rollout.get("missing_after_hop2") or []
            ),
        },
        "metadata": dict(metadata or {}),
    }

    endpoint["endpoint_id"] = _stable_id(
        "endpoint",
        {
            "sample_id": sample_id,
            "endpoint_type": endpoint_type,
            "materialization": materialization,
            "query": query,
            "retrieved_titles": endpoint["retrieved_titles"],
        },
    )

    return endpoint


def make_semantic_endpoint(
    *,
    sample_id: str,
    endpoint_type: str,
    question: str,
    summary_1: str,
    query: str,
    retrieval_target: Mapping[str, Any],
    metadata: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """
    Construct a semantic endpoint that has not been executed by BM25.

    This is used for virtual transported destinations.
    """

    desired_titles = _unique_strings(
        retrieval_target.get("desired_titles") or []
    )

    endpoint = {
        "sample_id": _clean_text(sample_id),
        "endpoint_type": endpoint_type,
        "materialization": "semantic",
        "question": _clean_text(question),
        "summary_1": _clean_text(summary_1),
        "query": _clean_text(query),
        "retrieved_titles": desired_titles,
        "retrieved_docs": [],
        "summary_2": "",
        "pred_answer": "",
        "metrics": {
            "missing_recovery_rate": None,
            "support_recall_hop1": None,
            "support_recall_hop2_only": None,
            "support_recall_total": None,
            "exact_match": None,
            "natural_retrieval_failure": None,
        },
        "retrieval": {
            "gold_support_titles": [],
            "hop1_titles": [],
            "hop2_titles": desired_titles,
            "missing_after_hop1": [],
            "recovered_missing_titles": [],
            "missing_after_hop2": [],
        },
        "retrieval_target": dict(retrieval_target),
        "metadata": dict(metadata or {}),
    }

    if not endpoint["sample_id"]:
        raise ValueError("Semantic endpoint has no sample_id.")
    if not endpoint["query"]:
        raise ValueError("Semantic endpoint has no destination query.")

    endpoint["endpoint_id"] = _stable_id(
        "endpoint",
        {
            "sample_id": endpoint["sample_id"],
            "endpoint_type": endpoint_type,
            "query": endpoint["query"],
            "retrieval_target_id": retrieval_target.get(
                "retrieval_target_id"
            ),
        },
    )

    return endpoint


# ---------------------------------------------------------------------------
# Binary local state classification
# ---------------------------------------------------------------------------

def classify_rollout(
    rollout: Mapping[str, Any],
    *,
    success_policy: str = "natural_failure",
    support_recall_threshold: float = 1.0,
) -> dict[str, Any]:
    """
    Binary C/W classification without error subtypes.

    This classification describes the current local query-retrieval state.
    It is not an intervention result such as W->C or W->W.
    """

    missing_after_hop1 = list(
        rollout.get("missing_after_hop1") or []
    )
    missing_after_hop2 = list(
        rollout.get("missing_after_hop2") or []
    )
    missing_recovery_rate = rollout.get(
        "missing_recovery_rate"
    )
    support_recall_total = rollout.get(
        "support_recall_total"
    )
    exact_match = int(rollout.get("score", 0))

    if success_policy == "natural_failure":
        success = not bool(missing_after_hop2)

    elif success_policy == "full_missing_recovery":
        success = (
            not missing_after_hop1
            or not missing_after_hop2
        )

    elif success_policy == "positive_missing_recovery":
        success = (
            not missing_after_hop1
            or (
                missing_recovery_rate is not None
                and float(missing_recovery_rate) > 0.0
            )
        )

    elif success_policy == "support_recall_threshold":
        success = (
            support_recall_total is not None
            and float(support_recall_total)
            >= float(support_recall_threshold)
        )

    elif success_policy == "exact_match":
        success = exact_match == 1

    else:
        raise ValueError(
            f"Unsupported success policy: {success_policy}"
        )

    return {
        "sample_id": _clean_text(
            rollout.get("sample_id")
        ),
        "label": "C" if success else "W",
        "success": bool(success),
        "success_policy": success_policy,
        "support_recall_threshold": support_recall_threshold,
        "observed": {
            "missing_after_hop1": _unique_strings(
                missing_after_hop1
            ),
            "missing_after_hop2": _unique_strings(
                missing_after_hop2
            ),
            "missing_recovery_rate": missing_recovery_rate,
            "support_recall_total": support_recall_total,
            "exact_match": exact_match,
        },
    }


# ---------------------------------------------------------------------------
# Retrieval-target specifications
# ---------------------------------------------------------------------------

def make_retrieval_target(
    *,
    sample_id: str,
    target_type: str,
    question: str,
    summary_1: str,
    desired_titles: Sequence[str],
    preserve_titles: Sequence[str] = (),
    avoid_titles: Sequence[str] = (),
    target_behavior: str = "",
    rationale: str = "",
    gold_privileged: bool = False,
    metadata: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    target = {
        "sample_id": _clean_text(sample_id),
        "target_type": _clean_text(target_type),
        "question": _clean_text(question),
        "summary_1": _clean_text(summary_1),
        "desired_titles": _unique_strings(desired_titles),
        "preserve_titles": _unique_strings(preserve_titles),
        "avoid_titles": _unique_strings(avoid_titles),
        "target_behavior": _clean_text(target_behavior),
        "rationale": _clean_text(rationale),
        "gold_privileged": bool(gold_privileged),
        "metadata": dict(metadata or {}),
    }

    if not target["sample_id"]:
        raise ValueError("Retrieval target has no sample_id.")
    if not target["target_type"]:
        raise ValueError("Retrieval target has no target_type.")
    if not target["desired_titles"] and not target["target_behavior"]:
        raise ValueError(
            "Retrieval target needs desired_titles or target_behavior."
        )

    target["retrieval_target_id"] = _stable_id(
        "retrieval_target",
        {
            "sample_id": target["sample_id"],
            "target_type": target["target_type"],
            "desired_titles": target["desired_titles"],
            "preserve_titles": target["preserve_titles"],
            "avoid_titles": target["avoid_titles"],
            "target_behavior": target["target_behavior"],
        },
    )

    return target


def build_oracle_retrieval_target(
    rollout: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Define gold-privileged R* without directly constructing q*.
    """

    sample_id = _clean_text(rollout.get("sample_id"))
    missing_titles = _unique_strings(
        rollout.get("missing_after_hop2") or []
    )
    preserve_titles = _unique_strings(
        rollout.get("hit_support_titles_total") or []
    )

    if not missing_titles:
        raise ValueError(
            "Cannot build oracle retrieval target: "
            "no gold title remains missing after hop2."
        )

    return make_retrieval_target(
        sample_id=sample_id,
        target_type="oracle_repair",
        question=_clean_text(rollout.get("question")),
        summary_1=_clean_text(rollout.get("summary_1")),
        desired_titles=missing_titles,
        preserve_titles=preserve_titles,
        target_behavior=(
            "Recover the remaining missing gold support evidence while "
            "preserving already retrieved relevant evidence."
        ),
        rationale=(
            "Gold-privileged destination for constructing a local "
            "query-retrieval repair transition."
        ),
        gold_privileged=True,
        metadata={
            "missing_after_hop2": missing_titles,
        },
    )


# ---------------------------------------------------------------------------
# Transition records
# ---------------------------------------------------------------------------

def make_transition(
    *,
    transition_type: str,
    transition_role: str,
    source_status: str,
    intended_target_status: str,
    source_endpoint: Mapping[str, Any],
    target_endpoint: Mapping[str, Any],
    retrieval_target: Optional[Mapping[str, Any]] = None,
    query_transition: Optional[Mapping[str, Any]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """
    Construct an output-space transition.

    No W->C/W->W/C->C/C->W label is assigned here. Such labels are produced
    only after gradient intervention and local-metric verification.
    """

    sample_id = _clean_text(
        source_endpoint.get("sample_id")
    )

    if sample_id != _clean_text(
        target_endpoint.get("sample_id")
    ):
        raise ValueError(
            "Source and target endpoint sample IDs differ."
        )

    if source_status not in {"W", "C"}:
        raise ValueError(
            f"Unsupported source_status: {source_status}"
        )

    transition = {
        "transition_type": transition_type,
        "transition_role": transition_role,
        "sample_id": sample_id,
        "source_status": source_status,
        "intended_target_status": intended_target_status,
        "source_endpoint": dict(source_endpoint),
        "target_endpoint": dict(target_endpoint),
        "retrieval_target": (
            dict(retrieval_target)
            if retrieval_target is not None
            else None
        ),
        "query_transition": (
            dict(query_transition)
            if query_transition is not None
            else None
        ),
        "metric_delta": {
            "missing_recovery_rate": _metric_delta(
                source_endpoint,
                target_endpoint,
                "missing_recovery_rate",
            ),
            "support_recall_total": _metric_delta(
                source_endpoint,
                target_endpoint,
                "support_recall_total",
            ),
            "exact_match": _metric_delta(
                source_endpoint,
                target_endpoint,
                "exact_match",
            ),
        },
        "intervention_label": None,
        "metadata": dict(metadata or {}),
    }

    transition["transition_id"] = _stable_id(
        "transition",
        {
            "transition_type": transition_type,
            "transition_role": transition_role,
            "sample_id": sample_id,
            "source_endpoint_id": source_endpoint.get(
                "endpoint_id"
            ),
            "target_endpoint_id": target_endpoint.get(
                "endpoint_id"
            ),
            "retrieval_target_id": (
                retrieval_target.get("retrieval_target_id")
                if retrieval_target is not None
                else None
            ),
        },
    )

    return transition


def compact_endpoint(
    endpoint: Mapping[str, Any],
    *,
    include_docs: bool = False,
) -> dict[str, Any]:
    compact = {
        "endpoint_id": endpoint.get("endpoint_id"),
        "sample_id": endpoint.get("sample_id"),
        "endpoint_type": endpoint.get("endpoint_type"),
        "materialization": endpoint.get("materialization"),
        "question": endpoint.get("question"),
        "summary_1": endpoint.get("summary_1"),
        "query": endpoint.get("query"),
        "retrieved_titles": endpoint.get(
            "retrieved_titles"
        ),
        "summary_2": endpoint.get("summary_2"),
        "pred_answer": endpoint.get("pred_answer"),
        "metrics": endpoint.get("metrics"),
        "retrieval": endpoint.get("retrieval"),
        "retrieval_target": endpoint.get(
            "retrieval_target"
        ),
        "metadata": endpoint.get("metadata"),
    }

    if include_docs:
        compact["retrieved_docs"] = endpoint.get(
            "retrieved_docs"
        )

    return compact


def compact_retrieval_target(
    target: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "retrieval_target_id": target.get(
            "retrieval_target_id"
        ),
        "sample_id": target.get("sample_id"),
        "target_type": target.get("target_type"),
        "question": target.get("question"),
        "summary_1": target.get("summary_1"),
        "desired_titles": target.get("desired_titles"),
        "preserve_titles": target.get("preserve_titles"),
        "avoid_titles": target.get("avoid_titles"),
        "target_behavior": target.get("target_behavior"),
        "rationale": target.get("rationale"),
        "gold_privileged": target.get("gold_privileged"),
        "metadata": target.get("metadata"),
    }


def compact_transition(
    transition: Mapping[str, Any],
    *,
    include_docs: bool = False,
) -> dict[str, Any]:
    return {
        "transition_id": transition.get("transition_id"),
        "transition_type": transition.get(
            "transition_type"
        ),
        "transition_role": transition.get(
            "transition_role"
        ),
        "sample_id": transition.get("sample_id"),
        "source_status": transition.get("source_status"),
        "intended_target_status": transition.get(
            "intended_target_status"
        ),
        "source_endpoint": compact_endpoint(
            transition.get("source_endpoint") or {},
            include_docs=include_docs,
        ),
        "target_endpoint": compact_endpoint(
            transition.get("target_endpoint") or {},
            include_docs=include_docs,
        ),
        "retrieval_target": transition.get(
            "retrieval_target"
        ),
        "query_transition": transition.get(
            "query_transition"
        ),
        "metric_delta": transition.get("metric_delta"),
        "metadata": transition.get("metadata"),
    }


# ---------------------------------------------------------------------------
# Landscape builder
# ---------------------------------------------------------------------------

class LandscapeBuilder:
    """
    Construct retrieval targets and explicitly invert them into query targets.

    Core sequence:

        R_source -> R_destination specification
        R transition -> q_destination
        q_destination -> actual BM25 endpoint, when materialization is required
    """

    def __init__(
        self,
        *,
        runtime: HotpotRuntime,
        cache: CallCache,
        model: str = "openai/gpt-5-mini",
        temperature: float = 1.0,
        max_tokens: int = 16000,
        max_retries: int = 2,
        destination_query_system_prompt: str = (
            DEFAULT_DESTINATION_QUERY_SYSTEM_PROMPT
        ),
        midpoint_retrieval_system_prompt: str = (
            DEFAULT_MIDPOINT_RETRIEVAL_SYSTEM_PROMPT
        ),
        transport_match_system_prompt: str = (
            DEFAULT_TRANSPORT_MATCH_SYSTEM_PROMPT
        ),
        transport_retrieval_system_prompt: str = (
            DEFAULT_TRANSPORT_RETRIEVAL_SYSTEM_PROMPT
        ),
    ):
        self.runtime = runtime
        self.cache = cache
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

        self.destination_query_system_prompt = (
            destination_query_system_prompt
        )
        self.midpoint_retrieval_system_prompt = (
            midpoint_retrieval_system_prompt
        )
        self.transport_match_system_prompt = (
            transport_match_system_prompt
        )
        self.transport_retrieval_system_prompt = (
            transport_retrieval_system_prompt
        )

    def _cached_json_call(
        self,
        *,
        stage: str,
        system_prompt: str,
        payload: Mapping[str, Any],
        metadata: Optional[Mapping[str, Any]] = None,
        prompt_version: Optional[int | str] = None,
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

        for retry_index in range(self.max_retries + 1):
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
                        "Parsed response is not a JSON object."
                    )

                return parsed, cache_hit, record

            except Exception as exc:
                last_error = exc

        assert last_error is not None
        raise last_error

    # ------------------------------------------------------------------
    # Explicit R -> q inversion
    # ------------------------------------------------------------------

    def infer_destination_query(
        self,
        *,
        source_endpoint: Mapping[str, Any],
        retrieval_target: Mapping[str, Any],
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        sample_id = _clean_text(
            source_endpoint.get("sample_id")
        )

        if sample_id != _clean_text(
            retrieval_target.get("sample_id")
        ):
            raise ValueError(
                "Source endpoint and retrieval target sample IDs differ."
            )

        payload = {
            "question": source_endpoint.get("question"),
            "summary_1": source_endpoint.get("summary_1"),
            "source_query": source_endpoint.get("query"),
            "source_retrieval_endpoint": compact_endpoint(
                source_endpoint
            ),
            "destination_retrieval_target": (
                compact_retrieval_target(retrieval_target)
            ),
        }

        parsed, cache_hit, call_record = (
            self._cached_json_call(
                stage="retrieval_to_query_inversion",
                system_prompt=(
                    self.destination_query_system_prompt
                ),
                payload=payload,
                prompt_version=prompt_version,
                metadata={
                    "sample_id": sample_id,
                    "source_endpoint_id": source_endpoint.get(
                        "endpoint_id"
                    ),
                    "retrieval_target_id": retrieval_target.get(
                        "retrieval_target_id"
                    ),
                    **dict(metadata or {}),
                },
            )
        )

        destination_query = _clean_text(
            parsed.get("destination_query")
        )

        if not destination_query:
            raise ValueError(
                "Inversion returned no destination_query."
            )

        query_transition = {
            "source_query": _clean_text(
                source_endpoint.get("query")
            ),
            "destination_query": destination_query,
            "inversion_method": "retrieval_to_query",
            "inversion_rationale": _clean_text(
                parsed.get("inversion_rationale")
            ),
            "anchors_preserved": _json_string_list(
                parsed.get("anchors_preserved"),
                "anchors_preserved",
            ),
            "anchors_added": _json_string_list(
                parsed.get("anchors_added"),
                "anchors_added",
            ),
            "anchors_removed_or_disambiguated": (
                _json_string_list(
                    parsed.get(
                        "anchors_removed_or_disambiguated"
                    ),
                    "anchors_removed_or_disambiguated",
                )
            ),
            "cache_hit": cache_hit,
            "call_input_hash": call_record.get(
                "input_hash"
            ),
        }

        query_transition["query_transition_id"] = _stable_id(
            "query_transition",
            {
                "source_endpoint_id": source_endpoint.get(
                    "endpoint_id"
                ),
                "retrieval_target_id": retrieval_target.get(
                    "retrieval_target_id"
                ),
                "source_query": query_transition[
                    "source_query"
                ],
                "destination_query": destination_query,
            },
        )

        return {
            "sample_id": sample_id,
            "retrieval_target": dict(retrieval_target),
            "query_transition": query_transition,
            "cache_hit": cache_hit,
            "call_record": call_record,
        }

    # ------------------------------------------------------------------
    # Actual endpoint materialization
    # ------------------------------------------------------------------

    def materialize_destination_endpoint(
        self,
        *,
        row: Mapping[str, Any],
        baseline_rollout: Mapping[str, Any],
        destination_query: str,
        endpoint_type: str,
        retrieval_target: Mapping[str, Any],
        query_transition: Mapping[str, Any],
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        destination_rollout = self.runtime.run_from_hop2_query(
            row,
            hop1_docs=baseline_rollout.get("hop1_docs") or [],
            hop1_titles=(
                baseline_rollout.get("hop1_titles") or []
            ),
            hop1_query=baseline_rollout.get("hop1_query"),
            summary_1=_clean_text(
                baseline_rollout.get("summary_1")
            ),
            hop2_query=_clean_text(destination_query),
        )

        endpoint = make_query_endpoint(
            destination_rollout,
            endpoint_type=endpoint_type,
            materialization="actual",
            metadata={
                "retrieval_target_id": retrieval_target.get(
                    "retrieval_target_id"
                ),
                "query_transition_id": query_transition.get(
                    "query_transition_id"
                ),
                **dict(metadata or {}),
            },
        )

        endpoint["retrieval_target"] = dict(
            retrieval_target
        )

        return {
            "endpoint": endpoint,
            "rollout": destination_rollout,
        }

    # ------------------------------------------------------------------
    # Wrong-side repair
    # ------------------------------------------------------------------

    def build_repair_transition(
        self,
        *,
        row: Mapping[str, Any],
        rollout: Mapping[str, Any],
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Build:

            R_failed
            -> oracle retrieval target R*
            -> inferred destination query q*
            -> actual BM25 endpoint
        """

        classification = classify_rollout(
            rollout,
            success_policy="natural_failure",
        )

        if classification["label"] != "W":
            raise ValueError(
                "build_repair_transition requires a W rollout."
            )

        source_endpoint = make_query_endpoint(
            rollout,
            endpoint_type="current_failed",
        )

        retrieval_target = build_oracle_retrieval_target(
            rollout
        )

        inversion = self.infer_destination_query(
            source_endpoint=source_endpoint,
            retrieval_target=retrieval_target,
            prompt_version=prompt_version,
            metadata={
                "transition_role": "wrong_repair",
                **dict(metadata or {}),
            },
        )

        query_transition = inversion["query_transition"]

        materialized = self.materialize_destination_endpoint(
            row=row,
            baseline_rollout=rollout,
            destination_query=query_transition[
                "destination_query"
            ],
            endpoint_type="oracle_repair_materialized",
            retrieval_target=retrieval_target,
            query_transition=query_transition,
            metadata={
                "gold_privileged_target": True,
            },
        )

        target_endpoint = materialized["endpoint"]

        transition = make_transition(
            transition_type="retrieval_repair",
            transition_role="wrong_repair",
            source_status="W",
            intended_target_status="C",
            source_endpoint=source_endpoint,
            target_endpoint=target_endpoint,
            retrieval_target=retrieval_target,
            query_transition=query_transition,
            metadata={
                "target_is_gold_privileged": True,
                **dict(metadata or {}),
            },
        )

        transition["target_rollout"] = materialized[
            "rollout"
        ]
        transition["observed_target_change"] = {
            "support_recall_improved": (
                transition["metric_delta"][
                    "support_recall_total"
                ]
                is not None
                and transition["metric_delta"][
                    "support_recall_total"
                ] > 0
            ),
            "missing_after_hop2": (
                target_endpoint["retrieval"][
                    "missing_after_hop2"
                ]
            ),
            "exact_match_improved": (
                transition["metric_delta"]["exact_match"]
                is not None
                and transition["metric_delta"][
                    "exact_match"
                ] > 0
            ),
        }

        return transition

    # ------------------------------------------------------------------
    # Retrieval-space midpoint
    # ------------------------------------------------------------------

    def generate_midpoint_retrieval_target(
        self,
        *,
        source_endpoint: Mapping[str, Any],
        target_endpoint: Mapping[str, Any],
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        sample_id = _clean_text(
            source_endpoint.get("sample_id")
        )

        if sample_id != _clean_text(
            target_endpoint.get("sample_id")
        ):
            raise ValueError(
                "Midpoint endpoints belong to different samples."
            )

        payload = {
            "question": source_endpoint.get("question"),
            "summary_1": source_endpoint.get("summary_1"),
            "source_retrieval_endpoint": compact_endpoint(
                source_endpoint
            ),
            "destination_retrieval_endpoint": compact_endpoint(
                target_endpoint
            ),
        }

        parsed, cache_hit, call_record = (
            self._cached_json_call(
                stage="midpoint_retrieval_target",
                system_prompt=(
                    self.midpoint_retrieval_system_prompt
                ),
                payload=payload,
                prompt_version=prompt_version,
                metadata={
                    "sample_id": sample_id,
                    "source_endpoint_id": source_endpoint.get(
                        "endpoint_id"
                    ),
                    "target_endpoint_id": target_endpoint.get(
                        "endpoint_id"
                    ),
                    **dict(metadata or {}),
                },
            )
        )

        target = make_retrieval_target(
            sample_id=sample_id,
            target_type="semantic_midpoint",
            question=_clean_text(
                source_endpoint.get("question")
            ),
            summary_1=_clean_text(
                source_endpoint.get("summary_1")
            ),
            desired_titles=_json_string_list(
                parsed.get("desired_titles"),
                "desired_titles",
            ),
            preserve_titles=_json_string_list(
                parsed.get("preserve_titles"),
                "preserve_titles",
            ),
            avoid_titles=_json_string_list(
                parsed.get("avoid_titles"),
                "avoid_titles",
            ),
            target_behavior=_clean_text(
                parsed.get("target_behavior")
            ),
            rationale=_clean_text(
                parsed.get("rationale")
            ),
            gold_privileged=False,
            metadata={
                "source_endpoint_id": source_endpoint.get(
                    "endpoint_id"
                ),
                "target_endpoint_id": target_endpoint.get(
                    "endpoint_id"
                ),
                "cache_hit": cache_hit,
                "call_input_hash": call_record.get(
                    "input_hash"
                ),
            },
        )

        return {
            "retrieval_target": target,
            "generation": parsed,
            "cache_hit": cache_hit,
            "call_record": call_record,
        }

    def generate_midpoint_endpoint(
        self,
        *,
        row: Mapping[str, Any],
        baseline_rollout: Mapping[str, Any],
        source_endpoint: Mapping[str, Any],
        target_endpoint: Mapping[str, Any],
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Correct midpoint sequence:

            generate R_mid
            -> infer q_mid from R_source -> R_mid
            -> run BM25(q_mid)
            -> obtain actual midpoint endpoint
        """

        target_result = (
            self.generate_midpoint_retrieval_target(
                source_endpoint=source_endpoint,
                target_endpoint=target_endpoint,
                prompt_version=prompt_version,
                metadata=metadata,
            )
        )

        retrieval_target = target_result[
            "retrieval_target"
        ]

        inversion = self.infer_destination_query(
            source_endpoint=source_endpoint,
            retrieval_target=retrieval_target,
            prompt_version=prompt_version,
            metadata={
                "transition_role": "midpoint",
                **dict(metadata or {}),
            },
        )

        query_transition = inversion["query_transition"]

        if query_transition["destination_query"] in {
            _clean_text(source_endpoint.get("query")),
            _clean_text(target_endpoint.get("query")),
        }:
            raise ValueError(
                "Midpoint destination query duplicates an endpoint query."
            )

        materialized = self.materialize_destination_endpoint(
            row=row,
            baseline_rollout=baseline_rollout,
            destination_query=query_transition[
                "destination_query"
            ],
            endpoint_type="midpoint_materialized",
            retrieval_target=retrieval_target,
            query_transition=query_transition,
            metadata={
                "source_endpoint_id": source_endpoint.get(
                    "endpoint_id"
                ),
                "target_endpoint_id": target_endpoint.get(
                    "endpoint_id"
                ),
            },
        )

        return {
            "sample_id": source_endpoint.get("sample_id"),
            "source_endpoint_id": source_endpoint.get(
                "endpoint_id"
            ),
            "target_endpoint_id": target_endpoint.get(
                "endpoint_id"
            ),
            "retrieval_target": retrieval_target,
            "query_transition": query_transition,
            "midpoint_endpoint": materialized["endpoint"],
            "midpoint_rollout": materialized["rollout"],
            "target_generation": target_result,
            "query_inversion": inversion,
        }

    # ------------------------------------------------------------------
    # Correct-side transport
    # ------------------------------------------------------------------

    def match_repair_transition(
        self,
        *,
        correct_endpoint: Mapping[str, Any],
        candidate_transitions: Sequence[
            Mapping[str, Any]
        ],
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        if not candidate_transitions:
            raise ValueError(
                "No wrong-side repair transitions were provided."
            )

        candidates = [
            compact_transition(transition)
            for transition in candidate_transitions
        ]

        sample_id = _clean_text(
            correct_endpoint.get("sample_id")
        )

        payload = {
            "correct_reference_endpoint": compact_endpoint(
                correct_endpoint
            ),
            "candidate_wrong_repair_transitions": candidates,
        }

        parsed, cache_hit, call_record = (
            self._cached_json_call(
                stage="transport_match",
                system_prompt=(
                    self.transport_match_system_prompt
                ),
                payload=payload,
                prompt_version=prompt_version,
                metadata={
                    "sample_id": sample_id,
                    "num_candidates": len(candidates),
                    **dict(metadata or {}),
                },
            )
        )

        matched_id = _clean_text(
            parsed.get("matched_transition_id")
        )

        transition_by_id = {
            _clean_text(t.get("transition_id")): t
            for t in candidate_transitions
        }

        if matched_id not in transition_by_id:
            raise ValueError(
                "Transport matcher returned unknown transition: "
                f"{matched_id}"
            )

        return {
            "match_id": _stable_id(
                "match",
                {
                    "sample_id": sample_id,
                    "matched_transition_id": matched_id,
                },
            ),
            "target_sample_id": sample_id,
            "matched_transition_id": matched_id,
            "matched_transition": dict(
                transition_by_id[matched_id]
            ),
            "rationale": _clean_text(
                parsed.get("rationale")
            ),
            "confidence": float(
                parsed.get("confidence", 0.0)
            ),
            "cache_hit": cache_hit,
            "call_record": call_record,
        }

    def generate_transported_retrieval_target(
        self,
        *,
        correct_endpoint: Mapping[str, Any],
        matched_transition: Mapping[str, Any],
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        sample_id = _clean_text(
            correct_endpoint.get("sample_id")
        )

        payload = {
            "correct_reference_endpoint": compact_endpoint(
                correct_endpoint
            ),
            "matched_wrong_repair_transition": (
                compact_transition(matched_transition)
            ),
        }

        parsed, cache_hit, call_record = (
            self._cached_json_call(
                stage="transported_retrieval_target",
                system_prompt=(
                    self.transport_retrieval_system_prompt
                ),
                payload=payload,
                prompt_version=prompt_version,
                metadata={
                    "sample_id": sample_id,
                    "matched_transition_id": (
                        matched_transition.get(
                            "transition_id"
                        )
                    ),
                    **dict(metadata or {}),
                },
            )
        )

        target = make_retrieval_target(
            sample_id=sample_id,
            target_type="transported_virtual_damage",
            question=_clean_text(
                correct_endpoint.get("question")
            ),
            summary_1=_clean_text(
                correct_endpoint.get("summary_1")
            ),
            desired_titles=_json_string_list(
                parsed.get("desired_titles"),
                "desired_titles",
            ),
            preserve_titles=_json_string_list(
                parsed.get("preserve_titles"),
                "preserve_titles",
            ),
            avoid_titles=_json_string_list(
                parsed.get("avoid_titles"),
                "avoid_titles",
            ),
            target_behavior=_clean_text(
                parsed.get("target_behavior")
            ),
            rationale=_clean_text(
                parsed.get("rationale")
            ),
            gold_privileged=False,
            metadata={
                "matched_wrong_transition_id": (
                    matched_transition.get(
                        "transition_id"
                    )
                ),
                "expected_failure_behavior": (
                    parsed.get(
                        "expected_failure_behavior"
                    )
                ),
                "locality_check": parsed.get(
                    "locality_check"
                ),
                "cache_hit": cache_hit,
                "call_input_hash": call_record.get(
                    "input_hash"
                ),
            },
        )

        return {
            "retrieval_target": target,
            "generation": parsed,
            "cache_hit": cache_hit,
            "call_record": call_record,
        }

    def generate_transported_endpoint(
        self,
        *,
        correct_endpoint: Mapping[str, Any],
        matched_transition: Mapping[str, Any],
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Correct transport sequence:

            wrong-side delta R
            -> virtual correct-side retrieval target R_virtual
            -> infer q_virtual
            -> store semantic destination endpoint

        The virtual endpoint is not executed by BM25 at this stage.
        """

        target_result = (
            self.generate_transported_retrieval_target(
                correct_endpoint=correct_endpoint,
                matched_transition=matched_transition,
                prompt_version=prompt_version,
                metadata=metadata,
            )
        )

        retrieval_target = target_result[
            "retrieval_target"
        ]

        inversion = self.infer_destination_query(
            source_endpoint=correct_endpoint,
            retrieval_target=retrieval_target,
            prompt_version=prompt_version,
            metadata={
                "transition_role": "correct_transport",
                **dict(metadata or {}),
            },
        )

        query_transition = inversion["query_transition"]

        if (
            query_transition["destination_query"]
            == _clean_text(correct_endpoint.get("query"))
        ):
            raise ValueError(
                "Transported destination query is unchanged."
            )

        endpoint = make_semantic_endpoint(
            sample_id=_clean_text(
                correct_endpoint.get("sample_id")
            ),
            endpoint_type="transported_virtual_damage",
            question=_clean_text(
                correct_endpoint.get("question")
            ),
            summary_1=_clean_text(
                correct_endpoint.get("summary_1")
            ),
            query=query_transition["destination_query"],
            retrieval_target=retrieval_target,
            metadata={
                "reference_endpoint_id": (
                    correct_endpoint.get("endpoint_id")
                ),
                "matched_wrong_transition_id": (
                    matched_transition.get(
                        "transition_id"
                    )
                ),
                "query_transition_id": (
                    query_transition.get(
                        "query_transition_id"
                    )
                ),
            },
        )

        return {
            "sample_id": correct_endpoint.get("sample_id"),
            "reference_endpoint": dict(correct_endpoint),
            "matched_transition_id": (
                matched_transition.get("transition_id")
            ),
            "retrieval_target": retrieval_target,
            "query_transition": query_transition,
            "transported_endpoint": endpoint,
            "target_generation": target_result,
            "query_inversion": inversion,
        }

    def build_transport_transition(
        self,
        *,
        correct_endpoint: Mapping[str, Any],
        transported_endpoint: Mapping[str, Any],
        retrieval_target: Mapping[str, Any],
        query_transition: Mapping[str, Any],
        matched_transition_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Construct C -> virtual output transition.

        Whether the later prompt intervention produces C->C or C->W is not
        determined here.
        """

        return make_transition(
            transition_type="transported_retrieval",
            transition_role="correct_transport",
            source_status="C",
            intended_target_status="virtual_damage",
            source_endpoint=correct_endpoint,
            target_endpoint=transported_endpoint,
            retrieval_target=retrieval_target,
            query_transition=query_transition,
            metadata={
                "matched_wrong_transition_id": (
                    matched_transition_id
                ),
                "target_is_semantic": True,
            },
        )
