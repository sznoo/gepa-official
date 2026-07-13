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

from litellm import completion  # noqa: E402

from experiments.method_probe.src.cache import (  # noqa: E402
    CallCache,
    atomic_write_json,
)
from experiments.method_probe.src.config import (  # noqa: E402
    DISTANCE_GAP_TYPES,
    render_distance_comparison_prompt,
)
from experiments.method_probe.src.hotpot import (  # noqa: E402
    HotpotRuntime,
    configure_lm,
    load_jsonl,
)
from experiments.method_probe.src.landscape import (  # noqa: E402
    LandscapeBuilder,
    make_transition,
)
from experiments.method_probe.src.program import (  # noqa: E402
    ProgramOperator,
    load_current_query_prompt,
    run_operational_probe,
    validate_gradient_record,
    validate_transition,
)


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
            "Could not extract completion text."
        ) from exc

    text = _clean_text(content)

    if not text:
        raise ValueError(
            "Completion response has empty content."
        )

    return text


def _unique_endpoints(
    endpoints: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()

    for endpoint in endpoints:
        endpoint_id = _clean_text(
            endpoint.get("endpoint_id")
        )

        if not endpoint_id:
            endpoint_id = _stable_id(
                "anonymous_endpoint",
                {
                    "query": endpoint.get("query"),
                    "retrieved_titles": endpoint.get(
                        "retrieved_titles"
                    ),
                },
            )

        if endpoint_id not in seen:
            seen.add(endpoint_id)
            output.append(dict(endpoint))

    return output


# ---------------------------------------------------------------------------
# Feedback segment construction
# ---------------------------------------------------------------------------

def make_gradient_feedback_segment(
    gradient_record: Mapping[str, Any],
    *,
    segment_name: str,
) -> dict[str, Any]:
    """
    The distance prompt compares samplewise gradients, not complete prompts.
    """

    validate_gradient_record(gradient_record)

    return {
        "segment": segment_name,
        "gradient_id": gradient_record["gradient_id"],
        "transition_id": gradient_record[
            "transition_id"
        ],
        "gradient": gradient_record["gradient"],
        "rationale": gradient_record["rationale"],
        "expected_query_change": gradient_record.get(
            "expected_query_change"
        ),
        "constraints_to_preserve": (
            gradient_record.get(
                "constraints_to_preserve"
            )
            or []
        ),
        "failure_behavior_to_avoid": (
            gradient_record.get(
                "failure_behavior_to_avoid"
            )
            or []
        ),
    }


# ---------------------------------------------------------------------------
# Gradient-magnitude comparison
# ---------------------------------------------------------------------------

class DistanceComparator:
    def __init__(
        self,
        *,
        cache: CallCache,
        model: str = "openai/gpt-5-mini",
        temperature: float = 1.0,
        max_tokens: int = 16000,
        max_retries: int = 2,
    ):
        self.cache = cache
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

    def compare_gradient_magnitude(
        self,
        *,
        question: str,
        summary_1: str,
        gradient_a: Mapping[str, Any],
        gradient_b: Mapping[str, Any],
        comparison_role: str,
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        segment_a = make_gradient_feedback_segment(
            gradient_a,
            segment_name="A",
        )
        segment_b = make_gradient_feedback_segment(
            gradient_b,
            segment_name="B",
        )

        rendered_prompt = (
            render_distance_comparison_prompt(
                question=question,
                summary_1=summary_1,
                segments=[
                    segment_a,
                    segment_b,
                ],
            )
        )

        request = {
            "comparison_role": comparison_role,
            "question": question,
            "summary_1": summary_1,
            "segments": [
                segment_a,
                segment_b,
            ],
            "rendered_prompt": rendered_prompt,
        }

        messages = [
            {
                "role": "user",
                "content": rendered_prompt,
            }
        ]

        last_error: Optional[Exception] = None

        for retry_index in range(
            self.max_retries + 1
        ):
            try:
                parsed, cache_hit, call_record = (
                    self.cache.cached_call(
                        stage="distance_comparison",
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
                        metadata={
                            "comparison_role": (
                                comparison_role
                            ),
                            "gradient_a_id": (
                                gradient_a["gradient_id"]
                            ),
                            "gradient_b_id": (
                                gradient_b["gradient_id"]
                            ),
                            **dict(metadata or {}),
                        },
                        retry_index=retry_index,
                    )
                )

                larger_segment = _clean_text(
                    parsed.get("larger_segment")
                )

                if larger_segment not in {
                    "A",
                    "B",
                    "tie",
                }:
                    raise ValueError(
                        "larger_segment must be "
                        "A, B, or tie."
                    )

                expected_index = {
                    "A": 0,
                    "B": 1,
                    "tie": -1,
                }[larger_segment]

                raw_index = parsed.get(
                    "segment_index",
                    expected_index,
                )

                try:
                    segment_index = int(raw_index)
                except (TypeError, ValueError):
                    segment_index = expected_index

                # Normalize an inconsistent model response.
                if segment_index != expected_index:
                    segment_index = expected_index

                dominant_gap_type = _clean_text(
                    parsed.get("dominant_gap_type")
                )

                if (
                    dominant_gap_type
                    not in DISTANCE_GAP_TYPES
                ):
                    dominant_gap_type = (
                        "tie"
                        if larger_segment == "tie"
                        else "mixed"
                    )

                try:
                    confidence = float(
                        parsed.get("confidence", 0.0)
                    )
                except (TypeError, ValueError):
                    confidence = 0.0

                confidence = max(
                    0.0,
                    min(1.0, confidence),
                )

                comparison_id = _stable_id(
                    "distance_comparison",
                    {
                        "comparison_role": (
                            comparison_role
                        ),
                        "gradient_a_id": gradient_a[
                            "gradient_id"
                        ],
                        "gradient_b_id": gradient_b[
                            "gradient_id"
                        ],
                        "larger_segment": (
                            larger_segment
                        ),
                    },
                )

                return {
                    "comparison_id": comparison_id,
                    "comparison_role": (
                        comparison_role
                    ),
                    "segment_a": segment_a,
                    "segment_b": segment_b,
                    "larger_segment": (
                        larger_segment
                    ),
                    "segment_index": segment_index,
                    "why_larger": _clean_text(
                        parsed.get("why_larger")
                    ),
                    "dominant_gap_type": (
                        dominant_gap_type
                    ),
                    "confidence": confidence,
                    "cache_hit": cache_hit,
                    "call_input_hash": (
                        call_record.get("input_hash")
                    ),
                }

            except Exception as exc:
                last_error = exc

        assert last_error is not None
        raise last_error


# ---------------------------------------------------------------------------
# Midpoint sub-edge construction
# ---------------------------------------------------------------------------

def _make_existing_query_transition(
    *,
    source_endpoint: Mapping[str, Any],
    target_endpoint: Mapping[str, Any],
    parent_transition: Mapping[str, Any],
) -> dict[str, Any]:
    source_query = _clean_text(
        source_endpoint.get("query")
    )
    destination_query = _clean_text(
        target_endpoint.get("query")
    )

    if not source_query:
        raise ValueError(
            "Sub-edge source endpoint has no query."
        )

    if not destination_query:
        raise ValueError(
            "Sub-edge target endpoint has no query."
        )

    query_transition = {
        "source_query": source_query,
        "destination_query": destination_query,
        "inversion_method": (
            "existing_materialized_endpoint_pair"
        ),
        "inversion_rationale": (
            "The parent transition already contains a "
            "materialized destination query. The right "
            "sub-edge reuses that destination at the "
            "inner query boundary."
        ),
        "anchors_preserved": [],
        "anchors_added": [],
        "anchors_removed_or_disambiguated": [],
        "parent_transition_id": parent_transition[
            "transition_id"
        ],
    }

    query_transition["query_transition_id"] = (
        _stable_id(
            "query_transition",
            {
                "source_query": source_query,
                "destination_query": (
                    destination_query
                ),
                "parent_transition_id": (
                    parent_transition[
                        "transition_id"
                    ]
                ),
            },
        )
    )

    return query_transition


def build_midpoint_subtransitions(
    *,
    parent_transition: Mapping[str, Any],
    midpoint_result: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Split:

        source -> target

    into:

        source -> midpoint
        midpoint -> target
    """

    validate_transition(parent_transition)

    midpoint_endpoint = midpoint_result[
        "midpoint_endpoint"
    ]
    midpoint_target = midpoint_result[
        "retrieval_target"
    ]
    midpoint_query_transition = midpoint_result[
        "query_transition"
    ]

    source_endpoint = parent_transition[
        "source_endpoint"
    ]
    final_target_endpoint = parent_transition[
        "target_endpoint"
    ]

    source_status = parent_transition[
        "source_status"
    ]

    left_transition = make_transition(
        transition_type="retrieval_subedge",
        transition_role="midpoint_left",
        source_status=source_status,
        intended_target_status="midpoint",
        source_endpoint=source_endpoint,
        target_endpoint=midpoint_endpoint,
        retrieval_target=midpoint_target,
        query_transition=midpoint_query_transition,
        metadata={
            "parent_transition_id": (
                parent_transition[
                    "transition_id"
                ]
            ),
            "subedge_side": "left",
        },
    )

    right_query_transition = (
        _make_existing_query_transition(
            source_endpoint=midpoint_endpoint,
            target_endpoint=final_target_endpoint,
            parent_transition=parent_transition,
        )
    )

    # The final retrieval destination remains the parent destination.
    right_retrieval_target = dict(
        parent_transition["retrieval_target"]
    )

    right_transition = make_transition(
        transition_type="retrieval_subedge",
        transition_role="midpoint_right",
        source_status=source_status,
        intended_target_status=(
            parent_transition.get(
                "intended_target_status",
                "destination",
            )
        ),
        source_endpoint=midpoint_endpoint,
        target_endpoint=final_target_endpoint,
        retrieval_target=right_retrieval_target,
        query_transition=right_query_transition,
        metadata={
            "parent_transition_id": (
                parent_transition[
                    "transition_id"
                ]
            ),
            "subedge_side": "right",
        },
    )

    return left_transition, right_transition


# ---------------------------------------------------------------------------
# Midpoint validation through gradient magnitude
# ---------------------------------------------------------------------------

def validate_midpoint_by_gradient_distance(
    *,
    comparator: DistanceComparator,
    operator: ProgramOperator,
    parent_transition: Mapping[str, Any],
    left_transition: Mapping[str, Any],
    right_transition: Mapping[str, Any],
    full_gradient: Mapping[str, Any],
    current_prompt: str,
    prompt_version: Optional[int | str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """
    Validate:

        magnitude(left gradient) < magnitude(full gradient)
        magnitude(right gradient) < magnitude(full gradient)

    The supplied comparison prompt is pairwise, so each sub-edge is compared
    separately against the full edge.
    """

    source_endpoint = parent_transition[
        "source_endpoint"
    ]

    question = _clean_text(
        source_endpoint.get("question")
    )
    summary_1 = _clean_text(
        source_endpoint.get("summary_1")
    )

    left_gradient = operator.infer_sample_gradient(
        transition=left_transition,
        current_prompt=current_prompt,
        prompt_version=prompt_version,
        metadata={
            "distance_role": "left_subedge",
            "parent_transition_id": (
                parent_transition[
                    "transition_id"
                ]
            ),
            **dict(metadata or {}),
        },
    )

    right_gradient = operator.infer_sample_gradient(
        transition=right_transition,
        current_prompt=current_prompt,
        prompt_version=prompt_version,
        metadata={
            "distance_role": "right_subedge",
            "parent_transition_id": (
                parent_transition[
                    "transition_id"
                ]
            ),
            **dict(metadata or {}),
        },
    )

    full_vs_left = (
        comparator.compare_gradient_magnitude(
            question=question,
            summary_1=summary_1,
            gradient_a=full_gradient,
            gradient_b=left_gradient,
            comparison_role="full_vs_left",
            prompt_version=prompt_version,
            metadata={
                "parent_transition_id": (
                    parent_transition[
                        "transition_id"
                    ]
                ),
                **dict(metadata or {}),
            },
        )
    )

    full_vs_right = (
        comparator.compare_gradient_magnitude(
            question=question,
            summary_1=summary_1,
            gradient_a=full_gradient,
            gradient_b=right_gradient,
            comparison_role="full_vs_right",
            prompt_version=prompt_version,
            metadata={
                "parent_transition_id": (
                    parent_transition[
                        "transition_id"
                    ]
                ),
                **dict(metadata or {}),
            },
        )
    )

    left_is_smaller = (
        full_vs_left["larger_segment"] == "A"
    )
    right_is_smaller = (
        full_vs_right["larger_segment"] == "A"
    )

    valid_midpoint = (
        left_is_smaller
        and right_is_smaller
    )

    return {
        "validation_id": _stable_id(
            "midpoint_validation",
            {
                "parent_transition_id": (
                    parent_transition[
                        "transition_id"
                    ]
                ),
                "left_transition_id": (
                    left_transition[
                        "transition_id"
                    ]
                ),
                "right_transition_id": (
                    right_transition[
                        "transition_id"
                    ]
                ),
                "left_is_smaller": (
                    left_is_smaller
                ),
                "right_is_smaller": (
                    right_is_smaller
                ),
            },
        ),
        "parent_transition_id": (
            parent_transition[
                "transition_id"
            ]
        ),
        "left_transition_id": (
            left_transition["transition_id"]
        ),
        "right_transition_id": (
            right_transition["transition_id"]
        ),
        "full_gradient": dict(full_gradient),
        "left_gradient": left_gradient,
        "right_gradient": right_gradient,
        "full_vs_left": full_vs_left,
        "full_vs_right": full_vs_right,
        "left_is_smaller": left_is_smaller,
        "right_is_smaller": right_is_smaller,
        "valid_midpoint": valid_midpoint,
    }


# ---------------------------------------------------------------------------
# Recursive operational decomposition
# ---------------------------------------------------------------------------

class DistanceResolver:
    def __init__(
        self,
        *,
        landscape: LandscapeBuilder,
        operator: ProgramOperator,
        comparator: DistanceComparator,
        runtime: HotpotRuntime,
    ):
        self.landscape = landscape
        self.operator = operator
        self.comparator = comparator
        self.runtime = runtime

    def resolve_transition(
        self,
        *,
        row: Mapping[str, Any],
        baseline_rollout: Mapping[str, Any],
        transition: Mapping[str, Any],
        current_prompt: str,
        max_depth: int,
        depth: int = 0,
        gradient_trace_prefix: Sequence[
            Mapping[str, Any]
        ] = (),
        prompt_version: Optional[int | str] = None,
        initial_probe: Optional[
            Mapping[str, Any]
        ] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        validate_transition(transition)

        normalized_gradient_prefix: list[
            dict[str, Any]
        ] = []

        for gradient_record in gradient_trace_prefix:
            if not isinstance(
                gradient_record,
                Mapping,
            ):
                raise ValueError(
                    "gradient_trace_prefix must contain "
                    "gradient-record objects."
                )

            validate_gradient_record(
                gradient_record
            )

            normalized_gradient_prefix.append(
                dict(gradient_record)
            )

        if max_depth < 0:
            raise ValueError(
                "max_depth must be non-negative."
            )

        if initial_probe is not None:
            if (
                initial_probe.get("transition_id")
                != transition["transition_id"]
            ):
                raise ValueError(
                    "initial_probe transition mismatch."
                )

            operational_probe = dict(
                initial_probe
            )
        else:
            operational_probe = (
                run_operational_probe(
                    operator=self.operator,
                    runtime=self.runtime,
                    row=row,
                    baseline_rollout=(
                        baseline_rollout
                    ),
                    transition=transition,
                    current_prompt=current_prompt,
                    gradient_trace_prefix=(
                        normalized_gradient_prefix
                    ),
                    prompt_version=prompt_version,
                    metadata={
                        "distance_depth": depth,
                        **dict(metadata or {}),
                    },
                )
            )

        local_success = bool(
            operational_probe[
                "local_metric"
            ]["local_success"]
        )

        probe_gradient_trace = (
            operational_probe.get(
                "gradient_trace"
            )
        )

        if not isinstance(
            probe_gradient_trace,
            list,
        ):
            raise ValueError(
                "Operational probe has no gradient_trace list."
            )

        current_gradient_trace: list[
            dict[str, Any]
        ] = []

        for gradient_record in probe_gradient_trace:
            if not isinstance(
                gradient_record,
                Mapping,
            ):
                raise ValueError(
                    "Operational probe gradient trace contains "
                    "a non-object record."
                )

            validate_gradient_record(
                gradient_record
            )

            current_gradient_trace.append(
                dict(gradient_record)
            )

        if not current_gradient_trace:
            raise ValueError(
                "Operational probe returned an empty "
                "gradient trace."
            )

        if normalized_gradient_prefix:
            expected_prefix_ids = [
                record["gradient_id"]
                for record
                in normalized_gradient_prefix
            ]
            actual_prefix_ids = [
                record["gradient_id"]
                for record
                in current_gradient_trace[
                    : len(
                        normalized_gradient_prefix
                    )
                ]
            ]

            if (
                actual_prefix_ids
                != expected_prefix_ids
            ):
                raise ValueError(
                    "Operational probe did not preserve the "
                    "inherited gradient-trace prefix."
                )

        node_id = _stable_id(
            "decomposition_node",
            {
                "transition_id": transition[
                    "transition_id"
                ],
                "depth": depth,
                "local_success": local_success,
            },
        )

        current_attempt = {
            "node_id": node_id,
            "depth": depth,
            "transition_id": transition[
                "transition_id"
            ],
            "probe_id": operational_probe[
                "probe_id"
            ],
            "gradient_id": (
                operational_probe[
                    "gradient_record"
                ]["gradient_id"]
            ),
            "actual_query": (
                operational_probe[
                    "intervention_result"
                ]["actual_query"]
            ),
            "desired_recall": (
                operational_probe[
                    "local_metric"
                ]["desired_recall"]
            ),
            "local_success": local_success,
        }

        source_endpoint = transition[
            "source_endpoint"
        ]
        target_endpoint = transition[
            "target_endpoint"
        ]

        # Operational success is the final atomicity criterion.
        if local_success:
            return {
                "node_id": node_id,
                "status": "verified_atomic",
                "depth": depth,
                "root_transition_id": (
                    transition["transition_id"]
                ),
                "verified_atomic_transition": (
                    dict(transition)
                ),
                "verified_gradient": (
                    operational_probe[
                        "gradient_record"
                    ]
                ),
                "verified_probe": (
                    operational_probe
                ),
                "operational_probe": (
                    operational_probe
                ),
                "semantic_path": [
                    dict(source_endpoint),
                    dict(target_endpoint),
                ],
                "intervention_attempts": [
                    current_attempt
                ],
                "midpoint_validations": [],
                "generated_transitions": [
                    dict(transition)
                ],
                "unresolved_transition": None,
            }

        if depth >= max_depth:
            return {
                "node_id": node_id,
                "status": "max_depth",
                "depth": depth,
                "root_transition_id": (
                    transition["transition_id"]
                ),
                "verified_atomic_transition": None,
                "verified_gradient": None,
                "verified_probe": None,
                "operational_probe": (
                    operational_probe
                ),
                "semantic_path": [
                    dict(source_endpoint),
                    dict(target_endpoint),
                ],
                "intervention_attempts": [
                    current_attempt
                ],
                "midpoint_validations": [],
                "generated_transitions": [
                    dict(transition)
                ],
                "unresolved_transition": (
                    dict(transition)
                ),
            }

        midpoint_result = (
            self.landscape.generate_midpoint_endpoint(
                row=row,
                baseline_rollout=(
                    baseline_rollout
                ),
                source_endpoint=source_endpoint,
                target_endpoint=target_endpoint,
                prompt_version=prompt_version,
                metadata={
                    "distance_depth": depth,
                    "parent_transition_id": (
                        transition[
                            "transition_id"
                        ]
                    ),
                    **dict(metadata or {}),
                },
            )
        )

        midpoint_target = midpoint_result[
            "retrieval_target"
        ]

        # The current query-local metric is title-based MR.
        # A midpoint without a desired title cannot yet be operationally tested.
        if not (
            midpoint_target.get("desired_titles")
            or []
        ):
            return {
                "node_id": node_id,
                "status": (
                    "midpoint_without_desired_titles"
                ),
                "depth": depth,
                "root_transition_id": (
                    transition["transition_id"]
                ),
                "verified_atomic_transition": None,
                "verified_gradient": None,
                "verified_probe": None,
                "operational_probe": (
                    operational_probe
                ),
                "semantic_path": [
                    dict(source_endpoint),
                    dict(
                        midpoint_result[
                            "midpoint_endpoint"
                        ]
                    ),
                    dict(target_endpoint),
                ],
                "intervention_attempts": [
                    current_attempt
                ],
                "midpoint_validations": [],
                "generated_transitions": [
                    dict(transition)
                ],
                "unresolved_transition": (
                    dict(transition)
                ),
                "midpoint_result": midpoint_result,
            }

        (
            left_transition,
            right_transition,
        ) = build_midpoint_subtransitions(
            parent_transition=transition,
            midpoint_result=midpoint_result,
        )

        midpoint_validation = (
            validate_midpoint_by_gradient_distance(
                comparator=self.comparator,
                operator=self.operator,
                parent_transition=transition,
                left_transition=left_transition,
                right_transition=right_transition,
                full_gradient=(
                    operational_probe[
                        "gradient_record"
                    ]
                ),
                current_prompt=current_prompt,
                prompt_version=prompt_version,
                metadata={
                    "distance_depth": depth,
                    **dict(metadata or {}),
                },
            )
        )

        if not midpoint_validation[
            "valid_midpoint"
        ]:
            return {
                "node_id": node_id,
                "status": "invalid_midpoint",
                "depth": depth,
                "root_transition_id": (
                    transition["transition_id"]
                ),
                "verified_atomic_transition": None,
                "verified_gradient": None,
                "verified_probe": None,
                "operational_probe": (
                    operational_probe
                ),
                "semantic_path": [
                    dict(source_endpoint),
                    dict(
                        midpoint_result[
                            "midpoint_endpoint"
                        ]
                    ),
                    dict(target_endpoint),
                ],
                "intervention_attempts": [
                    current_attempt
                ],
                "midpoint_validations": [
                    midpoint_validation
                ],
                "generated_transitions": [
                    dict(transition),
                    left_transition,
                    right_transition,
                ],
                "unresolved_transition": (
                    dict(transition)
                ),
                "midpoint_result": midpoint_result,
            }

        # Attribution only needs the first reachable local transition.
        # Therefore recurse on source -> midpoint. The right sub-edge is retained
        # for distance validation and trace storage.
        child_result = self.resolve_transition(
            row=row,
            baseline_rollout=baseline_rollout,
            transition=left_transition,
            current_prompt=current_prompt,
            max_depth=max_depth,
            depth=depth + 1,
            gradient_trace_prefix=(
                current_gradient_trace
            ),
            prompt_version=prompt_version,
            initial_probe=None,
            metadata={
                "parent_transition_id": (
                    transition["transition_id"]
                ),
                **dict(metadata or {}),
            },
        )

        child_path = child_result[
            "semantic_path"
        ]

        semantic_path = _unique_endpoints([
            *child_path,
            target_endpoint,
        ])

        return {
            "node_id": node_id,
            "status": child_result["status"],
            "depth": depth,
            "root_transition_id": (
                transition["transition_id"]
            ),
            "verified_atomic_transition": (
                child_result[
                    "verified_atomic_transition"
                ]
            ),
            "verified_gradient": (
                child_result["verified_gradient"]
            ),
            "verified_probe": (
                child_result["verified_probe"]
            ),
            "operational_probe": (
                operational_probe
            ),
            "semantic_path": semantic_path,
            "intervention_attempts": [
                current_attempt,
                *child_result[
                    "intervention_attempts"
                ],
            ],
            "midpoint_validations": [
                midpoint_validation,
                *child_result[
                    "midpoint_validations"
                ],
            ],
            "generated_transitions": [
                dict(transition),
                left_transition,
                right_transition,
                *child_result[
                    "generated_transitions"
                ],
            ],
            "unresolved_transition": (
                child_result[
                    "unresolved_transition"
                ]
            ),
            "midpoint_result": midpoint_result,
            "child_result": child_result,
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve a query-retrieval transition through "
            "gradient-distance midpoint decomposition and "
            "operational MR verification."
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
        "--initial-probe",
        default=None,
        help=(
            "Optional existing program.py operational "
            "probe for the root transition."
        ),
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
        "--max-depth",
        type=int,
        default=3,
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
            "distance_smoke/events.jsonl"
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

    initial_probe = None
    if args.initial_probe:
        initial_probe = json.loads(
            Path(args.initial_probe).read_text(
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

    landscape = LandscapeBuilder(
        runtime=runtime,
        cache=cache,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        max_retries=args.max_retries,
    )

    operator = ProgramOperator(
        cache=cache,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        max_retries=args.max_retries,
    )

    comparator = DistanceComparator(
        cache=cache,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        max_retries=args.max_retries,
    )

    resolver = DistanceResolver(
        landscape=landscape,
        operator=operator,
        comparator=comparator,
        runtime=runtime,
    )

    result = resolver.resolve_transition(
        row=row,
        baseline_rollout=baseline_rollout,
        transition=transition,
        current_prompt=current_prompt,
        max_depth=args.max_depth,
        prompt_version=args.prompt_version,
        initial_probe=initial_probe,
        metadata={
            "entrypoint": "distance.py",
            "row_index": args.row_index,
        },
    )

    result["decomposition_id"] = _stable_id(
        "decomposition",
        {
            "root_transition_id": (
                transition["transition_id"]
            ),
            "status": result["status"],
            "max_depth": args.max_depth,
            "prompt_version": (
                args.prompt_version
            ),
        },
    )

    atomic_write_json(args.out, result)

    verified_transition = result.get(
        "verified_atomic_transition"
    )
    verified_gradient = result.get(
        "verified_gradient"
    )

    print(json.dumps({
        "decomposition_id": result[
            "decomposition_id"
        ],
        "root_transition_id": transition[
            "transition_id"
        ],
        "status": result["status"],
        "num_intervention_attempts": len(
            result["intervention_attempts"]
        ),
        "num_midpoint_validations": len(
            result["midpoint_validations"]
        ),
        "semantic_path_queries": [
            endpoint.get("query")
            for endpoint in result[
                "semantic_path"
            ]
        ],
        "verified_atomic_transition_id": (
            verified_transition.get(
                "transition_id"
            )
            if verified_transition
            else None
        ),
        "verified_gradient_id": (
            verified_gradient.get(
                "gradient_id"
            )
            if verified_gradient
            else None
        ),
        "saved": args.out,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
