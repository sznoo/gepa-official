from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from gepa.proposer.reflective_mutation.base import (
    LanguageModel,
    Signature,
)

from ours.lm import run_signature
from ours.runtime import OursRuntime


AGENT_ROLES = {
    "summary1": (
        "Summarize first-hop evidence and expose the bridge entity, "
        "missing fact, or retrieval direction needed for the next hop."
    ),
    "query": (
        "Produce one compact second-hop retrieval query targeting the "
        "missing bridge or supporting evidence."
    ),
    "summary2": (
        "Integrate second-hop evidence with the first-hop context and "
        "retain the facts needed to answer the question."
    ),
    "final": (
        "Derive the minimal final answer supported by the supplied "
        "intermediate summaries."
    ),
}

STATE_KINDS = {
    "endpoint",
    "intermediate",
}

MAX_DOCS = 7
MAX_DOC_CHARS = 500
MAX_SUMMARY_CHARS = 1200


SEMANTIC_DISTANCE_SPEC = """
You are working with a functional semantic distance over states of one
agent in a multi-agent pipeline.

Each state contains the selected agent's output and may also contain the
downstream consequences produced by that output while the rest of the
pipeline is held fixed. The agent output is the primary object of the
transition. Downstream evidence and metrics are supporting evidence about
its functional effect.

The distance is not surface text edit distance and is not a correctness
score. It measures how much task-relevant behavior and information must
change to move from one state to another.

Judge distance using:
1. Agent-output behavior: what the output is trying to accomplish for the
   selected agent's role.
2. Task-relevant information: which entities, relations, evidence,
   conclusions, or answer constraints are preserved, added, removed, or
   corrected.
3. Downstream consequence: how the output changes retrieval, evidence,
   answerability, or information available to later agents.
4. Transition utility: whether a state is a meaningful intermediate step
   between two endpoint states.

Do not infer distance from text length, token count, document count, or
lexical overlap. Do not treat a state as closer merely because its metric
or final answer is better. Metrics are evidence of functional consequence,
not the distance definition itself.

A midpoint output o_mid between o_left and o_right must:
- preserve useful task-relevant behavior or information from o_left;
- make concrete semantic progress toward o_right;
- differ meaningfully from both endpoint outputs;
- not merely paraphrase or copy o_left;
- not simply copy o_right;
- represent two smaller functional transitions than the original edge.
""".strip()


OUTPUT_FORMATS = {
    "summary1": (
        'Return `mid_output` as one non-empty string containing a summary1 '
        "output."
    ),
    "query": (
        'Return `mid_output` as exactly one object of the form '
        '{"query": "<one compact second-hop BM25 query>"}.'
    ),
    "summary2": (
        'Return `mid_output` as one non-empty string containing a summary2 '
        "output."
    ),
    "final": (
        'Return `mid_output` as one non-empty string containing the final '
        "agent output."
    ),
}


def _json_dumps(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        default=str,
    )


def _extract_json_object(text: str) -> dict[str, Any]:
    text = str(text or "").strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        value = json.loads(text)
        if not isinstance(value, dict):
            raise TypeError("Expected a JSON object.")
        return value
    except Exception:
        pass

    decoder = json.JSONDecoder()

    for index, character in enumerate(text):
        if character != "{":
            continue

        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue

        if isinstance(value, dict):
            return value

    raise ValueError(
        "Could not extract a JSON object from LM output: "
        f"{text[:500]}"
    )


def _require_bool(
    value: Any,
    *,
    field: str,
) -> bool:
    if isinstance(value, bool):
        return value

    raise TypeError(
        f"Expected boolean field {field!r}, got {value!r}."
    )


def _normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _truncate(value: Any, limit: int) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[:limit] + " ...[truncated]"


def _get(
    obj: Mapping[str, Any],
    key: str,
    default: Any = None,
) -> Any:
    return obj.get(key, default)


def _first_present(
    state: Mapping[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    for key in keys:
        if key in state and state[key] is not None:
            return state[key]
    return default


def _resolve_agent_role(
    agent: str,
    agent_role: str | None,
) -> str:
    agent = str(agent or "").strip()
    if not agent:
        raise ValueError("Agent name cannot be empty.")

    if agent_role is not None:
        role = str(agent_role).strip()
        if not role:
            raise ValueError("agent_role cannot be empty.")
        return role

    try:
        return AGENT_ROLES[agent]
    except KeyError as exc:
        raise ValueError(
            f"Unknown agent {agent!r}. "
            "Provide agent_role explicitly or use one of "
            f"{sorted(AGENT_ROLES)}."
        ) from exc


def _validate_task_context(
    task_context: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(task_context, Mapping):
        raise TypeError("task_context must be a mapping.")
    return dict(task_context)


def _validate_state(
    state: Mapping[str, Any],
    *,
    name: str,
    agent: str,
) -> dict[str, Any]:
    if not isinstance(state, Mapping):
        raise TypeError(f"{name} must be a mapping.")

    normalized = dict(state)

    state_agent = normalized.get("agent")
    if state_agent is not None and str(state_agent) != agent:
        raise ValueError(
            f"{name} belongs to agent {state_agent!r}, "
            f"not {agent!r}."
        )

    state_kind = normalized.get("state_kind")
    if state_kind is not None and state_kind not in STATE_KINDS:
        raise ValueError(
            f"{name}.state_kind must be one of "
            f"{sorted(STATE_KINDS)}, got {state_kind!r}."
        )

    return normalized


def _validate_states(
    states: Sequence[Mapping[str, Any]],
    *,
    agent: str,
) -> list[dict[str, Any]]:
    if isinstance(states, (str, bytes)):
        raise TypeError("states must be a sequence of mappings.")

    if len(states) < 2:
        raise ValueError(
            "states must contain at least two endpoint states."
        )

    return [
        _validate_state(
            state,
            name=f"states[{index}]",
            agent=agent,
        )
        for index, state in enumerate(states)
    ]


def _validate_agent_output(
    agent: str,
    output: Any,
) -> str | dict[str, str]:
    if agent == "query":
        if not isinstance(output, Mapping):
            raise TypeError(
                "Query midpoint output must be a mapping with `query`."
            )

        query = _normalize_text(output.get("query"))
        if not query:
            raise ValueError("Query midpoint output cannot be empty.")

        return {"query": query}

    if agent not in {"summary1", "summary2", "final"}:
        raise ValueError(
            f"Unknown agent {agent!r}. Expected one of "
            f"{sorted(AGENT_ROLES)}."
        )

    if not isinstance(output, str):
        raise TypeError(
            f"{agent} midpoint output must be a string."
        )

    output = output.strip()
    if not output:
        raise ValueError(f"{agent} midpoint output cannot be empty.")

    return output


def _state_output(
    agent: str,
    state: Mapping[str, Any],
) -> str | dict[str, str]:
    output = state.get("output")

    if output is None:
        if agent == "summary1":
            output = state.get("summary_1")
        elif agent == "query":
            output = {
                "query": _first_present(
                    state,
                    "hop2_query",
                    "query",
                )
            }
        elif agent == "summary2":
            output = state.get("summary_2")
        else:
            output = _first_present(
                state,
                "answer",
                "final_answer",
            )

    return _validate_agent_output(agent, output)


def _canonical_output(
    agent: str,
    output: Any,
) -> str:
    normalized = _validate_agent_output(agent, output)

    if agent == "query":
        return normalized["query"]

    return _normalize_text(normalized)


def _doc_snippets(
    state: Mapping[str, Any],
) -> list[str]:
    docs = _first_present(
        state,
        "hop2_docs",
        "retrieved_docs",
        default=[],
    ) or []

    return [
        _truncate(doc, MAX_DOC_CHARS)
        for doc in list(docs)[:MAX_DOCS]
    ]


def _project_state(
    agent: str,
    state: Mapping[str, Any],
) -> dict[str, Any]:
    output = _state_output(agent, state)

    provenance = {
        "state_kind": _first_present(
            state,
            "state_kind",
            "kind",
        ),
        "state_origin": state.get("state_origin"),
        "output": output,
    }

    if agent == "summary1":
        return {
            **provenance,
            "hop2_query": _first_present(
                state,
                "hop2_query",
                "query",
            ),
            "hop2_titles": list(
                _first_present(
                    state,
                    "hop2_titles",
                    "retrieved_titles",
                    default=[],
                )
                or []
            ),
            "hop2_doc_snippets": _doc_snippets(state),
            "new_support_titles_hop2": list(
                state.get("new_support_titles_hop2") or []
            ),
            "missing_titles_after_hop2": list(
                _first_present(
                    state,
                    "missing_titles_after_hop2",
                    "missing_after_hop2",
                    default=[],
                )
                or []
            ),
            "support_recall_total": state.get(
                "support_recall_total"
            ),
            "missing_recovery_rate": state.get(
                "missing_recovery_rate"
            ),
            "summary_2": _truncate(
                state.get("summary_2"),
                MAX_SUMMARY_CHARS,
            ),
            "answer": _first_present(
                state,
                "answer",
                "strong_answer",
                "base_answer",
            ),
            "score": _first_present(
                state,
                "score",
                "strong_score",
                "base_score",
            ),
        }

    if agent == "query":
        return {
            **provenance,
            "hop2_titles": list(
                _first_present(
                    state,
                    "hop2_titles",
                    "retrieved_titles",
                    default=[],
                )
                or []
            ),
            "hop2_doc_snippets": _doc_snippets(state),
            "support_recall_hop2": _first_present(
                state,
                "support_recall_hop2",
                "support_recall_hop2_only",
            ),
            "support_recall_total": state.get(
                "support_recall_total"
            ),
            "missing_recovery_rate": state.get(
                "missing_recovery_rate"
            ),
            "new_support_titles_hop2": list(
                state.get("new_support_titles_hop2") or []
            ),
            "missing_titles_after_hop2": list(
                _first_present(
                    state,
                    "missing_titles_after_hop2",
                    "missing_after_hop2",
                    default=[],
                )
                or []
            ),
            "summary_2": _truncate(
                state.get("summary_2"),
                MAX_SUMMARY_CHARS,
            ),
            "answer": _first_present(
                state,
                "answer",
                "strong_answer",
                "base_answer",
            ),
            "score": _first_present(
                state,
                "score",
                "strong_score",
                "base_score",
            ),
        }

    if agent == "summary2":
        return {
            **provenance,
            "hop2_titles": list(
                _first_present(
                    state,
                    "hop2_titles",
                    "retrieved_titles",
                    default=[],
                )
                or []
            ),
            "hop2_doc_snippets": _doc_snippets(state),
            "answer": _first_present(
                state,
                "answer",
                "strong_answer",
                "base_answer",
            ),
            "score": _first_present(
                state,
                "score",
                "strong_score",
                "base_score",
            ),
        }

    return {
        **provenance,
        "score": _first_present(
            state,
            "score",
            "strong_score",
            "base_score",
        ),
    }


def _normalize_retry_feedback(
    retry_feedback: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if retry_feedback is None:
        return None

    if not isinstance(retry_feedback, Mapping):
        raise TypeError("retry_feedback must be a mapping.")

    return {
        "left_valid": _require_bool(
            retry_feedback.get("left_valid"),
            field="left_valid",
        ),
        "right_valid": _require_bool(
            retry_feedback.get("right_valid"),
            field="right_valid",
        ),
        "left_reason": str(
            retry_feedback.get("left_reason") or ""
        ).strip(),
        "right_reason": str(
            retry_feedback.get("right_reason") or ""
        ).strip(),
    }


class SelectLargestEdgeSignature(Signature):
    input_keys = [
        "agent",
        "agent_role",
        "task_context",
        "edges",
    ]
    output_keys = [
        "edge_index",
        "rationale",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
{SEMANTIC_DISTANCE_SPEC}

Compare all adjacent transitions jointly and select the single edge with
the largest functional semantic distance.

Use the same distance definition for every edge. If two edges are
functionally tied, select the lower edge_index.

Agent:
{input_dict["agent"]}

Agent role:
{input_dict["agent_role"]}

Task context:
{_json_dumps(input_dict["task_context"])}

Adjacent projected state edges:
{_json_dumps(input_dict["edges"])}

Return strict JSON only:
{{
  "edge_index": <zero-based integer>,
  "rationale": "<brief functional-semantic reason>"
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)

        if "edge_index" not in obj:
            raise ValueError("Selector output is missing `edge_index`.")

        try:
            edge_index = int(obj["edge_index"])
        except (TypeError, ValueError) as exc:
            raise ValueError("`edge_index` must be an integer.") from exc

        return {
            "edge_index": edge_index,
            "rationale": str(
                obj.get("rationale") or ""
            ).strip(),
        }


class GenerateMidpointSignature(Signature):
    input_keys = [
        "agent",
        "agent_role",
        "output_format",
        "task_context",
        "left_state",
        "right_state",
        "retry_feedback",
    ]
    output_keys = [
        "mid_output",
        "rationale",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        retry_feedback = input_dict.get("retry_feedback")

        retry_section = ""
        if retry_feedback:
            retry_section = f"""
A previous midpoint candidate failed an optional distance diagnostic.

Verifier feedback:
{_json_dumps(retry_feedback)}

Revise the midpoint:
- If right_valid is false, make more concrete semantic progress toward
  the right endpoint.
- If left_valid is false, preserve more of the left endpoint and avoid
  jumping too abruptly toward the right endpoint.
"""

        return f"""
{SEMANTIC_DISTANCE_SPEC}

Generate one midpoint output between the left and right projected states.
The midpoint output will be used directly as the destination output for a
local prompt-update inference step. Do not output a prompt update.

Make the smallest meaningful functional change from the left output toward
the right output. Adopt at least one task-relevant entity, relation,
evidence requirement, conclusion, output property, or behavioral intention
that is present in the right state but weak or absent in the left state.

Required output representation:
{input_dict["output_format"]}

Agent:
{input_dict["agent"]}

Agent role:
{input_dict["agent_role"]}

Task context:
{_json_dumps(input_dict["task_context"])}

Left projected state:
{_json_dumps(input_dict["left_state"])}

Right projected state:
{_json_dumps(input_dict["right_state"])}

{retry_section}

Return strict JSON only:
{{
  "mid_output": <agent-specific output described above>,
  "rationale": "<why this output is functionally between the endpoints>"
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)

        if "mid_output" not in obj:
            raise ValueError(
                "Midpoint output is missing `mid_output`."
            )

        return {
            "mid_output": obj["mid_output"],
            "rationale": str(
                obj.get("rationale") or ""
            ).strip(),
        }


class VerifyMidpointSignature(Signature):
    input_keys = [
        "agent",
        "agent_role",
        "task_context",
        "left_state",
        "mid_state",
        "right_state",
    ]
    output_keys = [
        "left_valid",
        "right_valid",
        "both_valid",
        "left_reason",
        "right_reason",
        "confidence",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
{SEMANTIC_DISTANCE_SPEC}

This is an optional diagnostic. Verify whether the proposed midpoint state
satisfies both semantic midpoint inequalities under the same functional
distance specification.

Check independently:

left_valid:
d(o_left, o_mid) < d(o_left, o_right)

right_valid:
d(o_mid, o_right) < d(o_left, o_right)

Agent:
{input_dict["agent"]}

Agent role:
{input_dict["agent_role"]}

Task context:
{_json_dumps(input_dict["task_context"])}

Left projected state:
{_json_dumps(input_dict["left_state"])}

Proposed midpoint projected state:
{_json_dumps(input_dict["mid_state"])}

Right projected state:
{_json_dumps(input_dict["right_state"])}

Return strict JSON only:
{{
  "left_valid": true,
  "right_valid": true,
  "both_valid": true,
  "left_reason": "<brief reason>",
  "right_reason": "<brief reason>",
  "confidence": <number between 0 and 1>
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)

        left_valid = _require_bool(
            obj.get("left_valid"),
            field="left_valid",
        )
        right_valid = _require_bool(
            obj.get("right_valid"),
            field="right_valid",
        )

        try:
            confidence = float(obj.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        confidence = max(0.0, min(confidence, 1.0))

        return {
            "left_valid": left_valid,
            "right_valid": right_valid,
            "both_valid": left_valid and right_valid,
            "left_reason": str(
                obj.get("left_reason") or ""
            ).strip(),
            "right_reason": str(
                obj.get("right_reason") or ""
            ).strip(),
            "confidence": confidence,
        }


def select_largest_edge(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent: str,
    task_context: Mapping[str, Any],
    states: Sequence[Mapping[str, Any]],
    agent_role: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    return_metadata: bool = False,
):
    role = _resolve_agent_role(agent, agent_role)
    context = _validate_task_context(task_context)
    normalized_states = _validate_states(
        states,
        agent=agent,
    )

    edges = [
        {
            "edge_index": index,
            "left_state": _project_state(
                agent,
                normalized_states[index],
            ),
            "right_state": _project_state(
                agent,
                normalized_states[index + 1],
            ),
        }
        for index in range(len(normalized_states) - 1)
    ]

    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation="midpoint.select_largest_edge",
        lm=lm,
        signature_cls=SelectLargestEdgeSignature,
        input_dict={
            "agent": agent,
            "agent_role": role,
            "task_context": context,
            "edges": edges,
        },
        lm_config=lm_config,
        metadata={
            "agent": agent,
            **dict(metadata or {}),
        },
        return_cache_hit=True,
    )

    edge_index = parsed["edge_index"]
    if not 0 <= edge_index < len(edges):
        raise ValueError(
            f"Selected edge_index={edge_index} is outside "
            f"[0, {len(edges) - 1}]."
        )

    result = {
        "edge_index": edge_index,
        "source_state": normalized_states[edge_index],
        "target_state": normalized_states[edge_index + 1],
        "rationale": parsed["rationale"],
        "n_states": len(normalized_states),
        "n_edges": len(edges),
    }

    if return_metadata:
        return result, prompt, raw, cache_hit

    return result


def generate_midpoint(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent: str,
    task_context: Mapping[str, Any],
    left_state: Mapping[str, Any],
    right_state: Mapping[str, Any],
    agent_role: str | None = None,
    retry_feedback: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    return_metadata: bool = False,
):
    role = _resolve_agent_role(agent, agent_role)
    context = _validate_task_context(task_context)
    left = _validate_state(
        left_state,
        name="left_state",
        agent=agent,
    )
    right = _validate_state(
        right_state,
        name="right_state",
        agent=agent,
    )

    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation="midpoint.generate",
        lm=lm,
        signature_cls=GenerateMidpointSignature,
        input_dict={
            "agent": agent,
            "agent_role": role,
            "output_format": OUTPUT_FORMATS[agent],
            "task_context": context,
            "left_state": _project_state(agent, left),
            "right_state": _project_state(agent, right),
            "retry_feedback": _normalize_retry_feedback(
                retry_feedback
            ),
        },
        lm_config=lm_config,
        metadata={
            "agent": agent,
            **dict(metadata or {}),
        },
        return_cache_hit=True,
    )

    mid_output = _validate_agent_output(
        agent,
        parsed["mid_output"],
    )

    mid_key = _canonical_output(agent, mid_output)
    left_key = _canonical_output(
        agent,
        _state_output(agent, left),
    )
    right_key = _canonical_output(
        agent,
        _state_output(agent, right),
    )

    if mid_key == left_key:
        raise ValueError(
            "Generated midpoint output is identical to the left endpoint."
        )

    if mid_key == right_key:
        raise ValueError(
            "Generated midpoint output is identical to the right endpoint."
        )

    result = {
        "mid_output": mid_output,
        "rationale": parsed["rationale"],
    }

    if return_metadata:
        return result, prompt, raw, cache_hit

    return result


def verify_midpoint(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent: str,
    task_context: Mapping[str, Any],
    left_state: Mapping[str, Any],
    mid_state: Mapping[str, Any],
    right_state: Mapping[str, Any],
    agent_role: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    return_metadata: bool = False,
):
    role = _resolve_agent_role(agent, agent_role)
    context = _validate_task_context(task_context)
    left = _validate_state(
        left_state,
        name="left_state",
        agent=agent,
    )
    mid = _validate_state(
        mid_state,
        name="mid_state",
        agent=agent,
    )
    right = _validate_state(
        right_state,
        name="right_state",
        agent=agent,
    )

    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation="midpoint.verify",
        lm=lm,
        signature_cls=VerifyMidpointSignature,
        input_dict={
            "agent": agent,
            "agent_role": role,
            "task_context": context,
            "left_state": _project_state(agent, left),
            "mid_state": _project_state(agent, mid),
            "right_state": _project_state(agent, right),
        },
        lm_config=lm_config,
        metadata={
            "agent": agent,
            **dict(metadata or {}),
        },
        return_cache_hit=True,
    )

    if return_metadata:
        return parsed, prompt, raw, cache_hit

    return parsed


__all__ = [
    "AGENT_ROLES",
    "SEMANTIC_DISTANCE_SPEC",
    "GenerateMidpointSignature",
    "SelectLargestEdgeSignature",
    "VerifyMidpointSignature",
    "generate_midpoint",
    "select_largest_edge",
    "verify_midpoint",
]