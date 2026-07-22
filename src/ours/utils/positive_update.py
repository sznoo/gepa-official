# /home/jinwoo/gepa-official/src/ours/utils/positive_update.py
from __future__ import annotations

import hashlib
import json
import traceback
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from gepa.proposer.reflective_mutation.base import LanguageModel, Signature

from ours.analyze_attribute import (
    AGENT_ROLES,
    AGENT_TO_PROMPT_KEY,
    build_agent_inputs,
    build_delta_p_trace,
    compact_state,
    normalize_direct_output,
)
from ours.lm import run_signature
from ours.runtime import OursRuntime
from ours.utils.materialize import (
    compute_local_metric,
    materialize_agent_state,
    state_from_trace,
)


SCRIPT_VERSION = "2026-07-15-v3-decoupled-c-budget"

MAX_VISIBLE_INPUT_CHARS = 12000
MAX_CANDIDATE_STATE_CHARS = 7000
MAX_MATCH_CANDIDATES_CHARS = 50000
MAX_REPAIR_DELTA_CHARS = 24000

RAW_MATERIAL_KIND = "C_raw_success"
SIGNED_MATERIAL_KIND = "C_signed_avoid"

__all__ = [
    "SCRIPT_VERSION",
    "RAW_MATERIAL_KIND",
    "SIGNED_MATERIAL_KIND",
    "MatchTransportableWSignature",
    "GenerateTransportedDamageSignature",
    "compact_w_candidate_for_match",
    "match_c_to_w",
    "generate_c_damage",
    "build_raw_c_material",
    "build_signed_c_material",
    "build_delta_q_analysis",
    "prepare_positive_materials",
]


# ---------------------------------------------------------------------------
# Internal JSON / identity helpers
# ---------------------------------------------------------------------------


def _json_dumps(value: Any, *, indent: int | None = 2) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=indent,
        default=str,
        sort_keys=False,
    )


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def _append_jsonl(path: str | Path, row: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(_json_dumps(dict(row), indent=None) + "\n")


def _rewrite_jsonl(
    path: str | Path,
    rows: Sequence[Mapping[str, Any]],
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(_json_dumps(dict(row), indent=None) + "\n")


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
        if isinstance(value, dict):
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
        f"{text[:800]}"
    )


def _require_text(value: Any, *, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} cannot be empty.")
    return text


def _truncate(value: Any, limit: int) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[:limit] + " ...[truncated]"


def _stable_id(row: Mapping[str, Any], fallback_index: int) -> str:
    for key in ("sample_id", "_id", "id"):
        value = row.get(key)
        if value not in {None, ""}:
            return str(value)

    return str(
        row.get(
            "index",
            row.get("sample_index", fallback_index),
        )
    )


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _normalized_text(value: Any) -> str:
    text = str(value or "").lower()
    chars = [character if character.isalnum() else " " for character in text]
    return " ".join("".join(chars).split())


def _same_output(left: Any, right: Any) -> bool:
    return _normalized_text(
        _json_dumps(left, indent=None)
    ) == _normalized_text(
        _json_dumps(right, indent=None)
    )


def _validate_agent(agent: Any) -> str:
    agent = str(agent or "").strip()
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(
            f"Unknown agent {agent!r}. "
            f"Expected one of {sorted(AGENT_TO_PROMPT_KEY)}."
        )
    return agent


def _validate_w_material(w: Mapping[str, Any]) -> None:
    if w.get("material_kind") != "W_repair":
        raise ValueError("Expected canonical W_repair material.")
    if w.get("polarity") != "encourage":
        raise ValueError("W repair material must have polarity='encourage'.")

    _validate_agent(w.get("agent"))

    states = list(w.get("states") or [])
    deltas = list(w.get("delta_p_trace") or [])
    if len(states) < 2:
        raise ValueError("W material must contain at least two states.")
    if len(deltas) != len(states) - 1:
        raise ValueError(
            "W material edge mismatch: "
            f"states={len(states)}, deltas={len(deltas)}."
        )

    for position, delta_row in enumerate(deltas):
        if int(delta_row.get("edge_index", -1)) != position:
            raise ValueError(
                "W delta-p trace is not in adjacent-edge order: "
                f"position={position}, edge_index="
                f"{delta_row.get('edge_index')}."
            )
        if not isinstance(delta_row.get("delta_p"), Mapping):
            raise TypeError(
                "Each W delta-p trace row must contain mapping-valued delta_p."
            )


def _validate_selected_inputs(
    *,
    selected_c_rows: Sequence[tuple[int, Mapping[str, Any]]],
    selected_w_materials: Sequence[Mapping[str, Any]],
) -> None:
    if not selected_c_rows:
        raise ValueError("selected_c_rows cannot be empty.")
    if not selected_w_materials:
        raise ValueError("selected_w_materials cannot be empty.")
    c_positions = [int(position) for position, _ in selected_c_rows]
    if len(set(c_positions)) != len(c_positions):
        raise ValueError("selected_c_rows contains duplicate eval positions.")

    w_indices = []
    for w in selected_w_materials:
        _validate_w_material(w)
        w_indices.append(int(w["sample_index"]))
    if len(set(w_indices)) != len(w_indices):
        raise ValueError("selected_w_materials contains duplicate sample indices.")

    for position, row in selected_c_rows:
        if float(row.get("score") or 0.0) != 1.0:
            raise ValueError(
                f"C row at eval position {position} is not baseline-correct."
            )


def _row_identity_payload(
    c_position: int,
    c_row: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "c_eval_position": int(c_position),
        "c_stable_id": _stable_id(c_row, c_position),
        "question": c_row.get("question"),
        "gold_answer": c_row.get("gold_answer"),
        "gold_support_titles": c_row.get("gold_support_titles"),
        "hop1_docs": c_row.get("hop1_docs"),
        "summary_1": c_row.get("summary_1"),
        "hop2_query": c_row.get("hop2_query"),
        "hop2_docs": c_row.get("hop2_docs"),
        "summary_2": c_row.get("summary_2"),
        "answer": c_row.get("answer"),
        "score": c_row.get("score"),
    }


def _compact_w_delta_trace(
    delta_p_trace: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "edge_index": int(item["edge_index"]),
            "delta_p": dict(item["delta_p"]),
        }
        for item in delta_p_trace
    ]


def _w_candidate_set_hash(
    *,
    c_row: Mapping[str, Any],
    w_candidates: Sequence[Mapping[str, Any]],
) -> str:
    payload = [
        compact_w_candidate_for_match(w, c_row)
        for w in w_candidates
    ]
    return _canonical_hash(payload)


def _match_fingerprint(
    *,
    c_position: int,
    c_row: Mapping[str, Any],
    w_candidates: Sequence[Mapping[str, Any]],
    lm_config: Mapping[str, Any],
) -> str:
    return _canonical_hash({
        "script_version": SCRIPT_VERSION,
        "row": _row_identity_payload(c_position, c_row),
        "w_candidate_set_hash": _w_candidate_set_hash(
            c_row=c_row,
            w_candidates=w_candidates,
        ),
        "lm_config": dict(lm_config),
    })


def _match_semantic_payload(match: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in match.items()
        if key not in {"lm_trace", "match_fingerprint"}
    }


def _material_fingerprint(
    *,
    material_kind: str,
    c_position: int,
    c_row: Mapping[str, Any],
    match: Mapping[str, Any],
    base_candidate: Mapping[str, str],
    lm_config: Mapping[str, Any],
    materialization_config: Mapping[str, Any] | None,
    damage_attempts: int,
    delta_attempts: int,
) -> str:
    return _canonical_hash({
        "script_version": SCRIPT_VERSION,
        "material_kind": material_kind,
        "row": _row_identity_payload(c_position, c_row),
        "match_fingerprint": match.get("match_fingerprint"),
        "match": _match_semantic_payload(match),
        "base_candidate": dict(base_candidate),
        "lm_config": dict(lm_config),
        "materialization_config": dict(materialization_config or {}),
        "damage_attempts": int(damage_attempts),
        "delta_attempts": int(delta_attempts),
    })


# ---------------------------------------------------------------------------
# C-side W-to-C transport matching
# ---------------------------------------------------------------------------


class MatchTransportableWSignature(Signature):
    input_keys = [
        "target_case",
        "candidate_transitions",
    ]
    output_keys = [
        "selected_w_sample_index",
        "dominant_gap_type",
        "transported_damage_hypothesis",
        "expected_damaged_behavior",
        "rationale",
        "confidence",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
You are matching one correct HotpotQA target case C to exactly one W-side
agent-repair transition whose FAILURE PATTERN can be transported locally.

The W transition is represented in repair direction W_minus -> W_plus.
A later damage generator will use the reverse failure pattern to construct
C_plus -> C_minus. Select based on semantic transferability, not lexical or
entity overlap.

Criteria:
- the same kind of anchor, bridge relation, entity disambiguation, qualifier,
  noisy entity, candidate-set, evidence-family, output-shape, or answer-
  selection failure can plausibly occur at the target agent boundary;
- transfer only the failure pattern, never W-side entities, titles, answers,
  or sample-specific literals;
- the resulting damage should remain a local neighbor of C_plus;
- no answer flip is required;
- choose exactly one listed candidate and do not invent an ID.

Target C case:
{_truncate(_json_dumps(input_dict["target_case"]), MAX_CANDIDATE_STATE_CHARS)}

Candidate W repair transitions:
{_truncate(_json_dumps(input_dict["candidate_transitions"]), MAX_MATCH_CANDIDATES_CHARS)}

Allowed W sample indices:
{_json_dumps([
    int(candidate["w_sample_index"])
    for candidate in input_dict["candidate_transitions"]
])}

Return strict JSON only.
The selected_w_sample_index must be the exact w_sample_index value copied
from one listed candidate. Do not return a zero-based or one-based list
position and do not invent a new ID.
{{
  "selected_w_sample_index": {int(input_dict["candidate_transitions"][0]["w_sample_index"])},
  "dominant_gap_type": "anchor|bridge_relation|entity_disambiguation|missing_qualifier|surface_form|noisy_entity|answer_type|query_shape|candidate_set|evidence_family|output_selection|mixed",
  "transported_damage_hypothesis": "short target-specific hypothesis",
  "expected_damaged_behavior": "short description at the selected agent boundary",
  "rationale": "why this W failure pattern is the most transferable",
  "confidence": 0.0
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)

        try:
            selected = int(obj["selected_w_sample_index"])
        except Exception as exc:
            raise ValueError(
                "selected_w_sample_index must be an integer."
            ) from exc

        confidence = float(obj.get("confidence", 0.0))
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1].")

        return {
            "selected_w_sample_index": selected,
            "dominant_gap_type": _require_text(
                obj.get("dominant_gap_type"),
                field="dominant_gap_type",
            ),
            "transported_damage_hypothesis": _require_text(
                obj.get("transported_damage_hypothesis"),
                field="transported_damage_hypothesis",
            ),
            "expected_damaged_behavior": _require_text(
                obj.get("expected_damaged_behavior"),
                field="expected_damaged_behavior",
            ),
            "rationale": _require_text(
                obj.get("rationale"),
                field="rationale",
            ),
            "confidence": confidence,
        }


def compact_w_candidate_for_match(
    w: Mapping[str, Any],
    c_row: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build one candidate-specific matching view.

    The target C state is materialized from the saved correct rollout at the
    candidate W agent boundary. This allows the matcher to choose both a W
    failure pattern and the agent boundary to which it is transportable.
    """
    _validate_w_material(w)
    agent = _validate_agent(w["agent"])

    c_plus = state_from_trace(
        agent=agent,
        row=c_row,
        state_kind="endpoint",
        state_origin="baseline_correct",
    )

    return {
        "w_sample_index": int(w["sample_index"]),
        "w_stable_id": str(w["stable_id"]),
        "agent": agent,
        "w_question": w.get("question"),
        "w_minus": compact_state(agent, w["states"][0]),
        "w_plus": compact_state(agent, w["states"][-1]),
        "w_ordered_delta_p": _compact_w_delta_trace(
            w["delta_p_trace"]
        ),
        "target_c_plus_for_agent": compact_state(agent, c_plus),
    }


def match_c_to_w(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    c_position: int,
    c_row: Mapping[str, Any],
    w_candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not w_candidates:
        raise ValueError("w_candidates cannot be empty.")
    if float(c_row.get("score") or 0.0) != 1.0:
        raise ValueError(
            f"C row at eval position {c_position} is not baseline-correct."
        )

    candidate_payload = [
        compact_w_candidate_for_match(w, c_row)
        for w in w_candidates
    ]
    allowed = {
        int(candidate["w_sample_index"]): index
        for index, candidate in enumerate(candidate_payload)
    }
    if len(allowed) != len(candidate_payload):
        raise ValueError("W candidate sample indices must be unique.")

    fingerprint = _match_fingerprint(
        c_position=c_position,
        c_row=c_row,
        w_candidates=w_candidates,
        lm_config=lm_config,
    )

    match_input = {
        "target_case": {
            "eval_position": int(c_position),
            "stable_id": _stable_id(c_row, c_position),
            "question": c_row.get("question"),
            "summary_1": c_row.get("summary_1"),
            "hop2_query": c_row.get("hop2_query"),
            "summary_2": c_row.get("summary_2"),
            "answer": c_row.get("answer"),
            "gold_support_titles": c_row.get(
                "gold_support_titles"
            ),
        },
        "candidate_transitions": candidate_payload,
    }

    match_metadata = {
        "c_eval_position": int(c_position),
        "c_stable_id": _stable_id(c_row, c_position),
        "candidate_w_sample_indices": sorted(allowed),
        "match_fingerprint": fingerprint,
    }

    last_error: Exception | None = None

    for match_attempt in range(3):
        operation = (
            "prompt_update.c_transport_match"
            if match_attempt == 0
            else (
                "prompt_update.c_transport_match."
                f"retry_{match_attempt}"
            )
        )

        try:
            parsed, prompt, raw, cache_hit = run_signature(
                runtime=runtime,
                operation=operation,
                lm=lm,
                signature_cls=MatchTransportableWSignature,
                input_dict=match_input,
                lm_config=lm_config,
                metadata={
                    **match_metadata,
                    "match_attempt": int(match_attempt),
                },
                return_cache_hit=True,
            )

            selected = int(
                parsed["selected_w_sample_index"]
            )

            if selected not in allowed:
                raise ValueError(
                    "Matcher selected unknown W sample "
                    f"{selected}; allowed={sorted(allowed)}."
                )

            break

        except (TypeError, ValueError) as exc:
            last_error = exc

            print(
                "[positive_update] C-to-W match retry"
                f" | c_position={c_position}"
                f" attempt={match_attempt + 1}/3"
                f" error={type(exc).__name__}: {exc}",
                flush=True,
            )

    else:
        assert last_error is not None
        raise RuntimeError(
            "Failed to match C to W after 3 schema/parser "
            f"attempts: {last_error}"
        ) from last_error

    selected_w = w_candidates[allowed[selected]]
    selected_agent = _validate_agent(selected_w["agent"])

    return {
        "row_type": "positive_match",
        "script_version": SCRIPT_VERSION,
        "match_fingerprint": fingerprint,
        "c_eval_position": int(c_position),
        "c_stable_id": _stable_id(c_row, c_position),
        "selected_candidate_position": int(allowed[selected]),
        "selected_w_sample_index": selected,
        "selected_w_stable_id": str(selected_w["stable_id"]),
        "agent": selected_agent,
        **parsed,
        "lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    }


# ---------------------------------------------------------------------------
# C-side transported damage generation
# ---------------------------------------------------------------------------


class GenerateTransportedDamageSignature(Signature):
    input_keys = [
        "agent",
        "agent_role",
        "base_prompt",
        "visible_c_inputs",
        "c_plus_state",
        "w_minus_state",
        "w_plus_state",
        "w_ordered_repair_delta_p",
        "match",
        "repair_feedback",
    ]
    output_keys = [
        "damaged_output",
        "transported_failure_pattern",
        "expected_damage",
        "locality_check",
        "confidence",
        "rationale",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
You are constructing a target-specific transported damaged output C_minus
for one agent in a fixed HotpotQA multi-agent pipeline.

Inputs:
- C_plus is a correct current output/state for the target sample.
- W_minus -> W_plus is a matched W-side repair transition.
- The ordered W delta-p trace describes the repair behavior.

Task:
Infer the reverse W failure pattern and apply only that failure pattern to
the target sample's own visible inputs, producing a plausible LOCAL neighbor
C_minus of C_plus.

Strict rules:
- Produce an actual output for the selected agent boundary, not a prompt.
- Preserve the agent's native input/output contract.
- Use only visible_c_inputs as factual content.
- Never copy W-side entities, answers, titles, or sample-specific literals
  unless they independently occur in visible_c_inputs.
- Do not create unrelated corruption. Preserve enough useful C context for
  the result to remain a local neighbor.
- Damage one coherent behavior: weaken, remove, or blur an anchor, relation,
  qualifier, candidate distinction, evidence integration, output selection,
  or another matched failure pattern.
- An answer flip is not required and must not be claimed.
- Do not mention gold labels, oracle targets, evaluation metrics, source or
  target states, transport, prompt updates, or optimization in damaged_output.
- Do not wrap damaged_output in explanatory prose.

Agent:
{input_dict["agent"]}

Agent role:
{input_dict["agent_role"]}

Base prompt:
{input_dict["base_prompt"]}

Visible C inputs:
{_truncate(_json_dumps(input_dict["visible_c_inputs"]), MAX_VISIBLE_INPUT_CHARS)}

C_plus state:
{_json_dumps(input_dict["c_plus_state"])}

Matched W_minus state:
{_json_dumps(input_dict["w_minus_state"])}

Matched W_plus state:
{_json_dumps(input_dict["w_plus_state"])}

Ordered W repair delta-p:
{_truncate(_json_dumps(input_dict["w_ordered_repair_delta_p"]), MAX_REPAIR_DELTA_CHARS)}

Match explanation:
{_json_dumps(input_dict["match"])}

Repair feedback from a rejected attempt:
{_json_dumps(input_dict.get("repair_feedback") or {})}

Return strict JSON only:
{{
  "damaged_output": <native agent output; query must be {{"query": "..."}}, other agents use a string>,
  "transported_failure_pattern": "short abstract failure pattern",
  "expected_damage": "short target-specific behavioral effect",
  "locality_check": {{
    "is_local_neighbor_of_c_plus": true,
    "preserved_context": ["short preserved cue"],
    "why_not_unrelated": "brief reason"
  }},
  "confidence": 0.0,
  "rationale": "brief explanation without hidden reasoning"
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        if "damaged_output" not in obj:
            raise ValueError("Missing damaged_output.")

        locality = obj.get("locality_check")
        if not isinstance(locality, Mapping):
            raise TypeError("locality_check must be a JSON object.")
        if locality.get("is_local_neighbor_of_c_plus") is not True:
            raise ValueError(
                "Damage generator did not certify a local neighbor."
            )

        preserved_context = locality.get("preserved_context", [])
        if not isinstance(preserved_context, list):
            raise TypeError(
                "locality_check.preserved_context must be a JSON list."
            )
        preserved_context = [
            str(item).strip()
            for item in preserved_context
            if str(item).strip()
        ]
        if not preserved_context:
            raise ValueError(
                "locality_check.preserved_context cannot be empty."
            )

        why_not_unrelated = _require_text(
            locality.get("why_not_unrelated"),
            field="locality_check.why_not_unrelated",
        )

        confidence = float(obj.get("confidence", 0.0))
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1].")

        return {
            "damaged_output": obj["damaged_output"],
            "transported_failure_pattern": _require_text(
                obj.get("transported_failure_pattern"),
                field="transported_failure_pattern",
            ),
            "expected_damage": _require_text(
                obj.get("expected_damage"),
                field="expected_damage",
            ),
            "locality_check": {
                "is_local_neighbor_of_c_plus": True,
                "preserved_context": preserved_context,
                "why_not_unrelated": why_not_unrelated,
            },
            "confidence": confidence,
            "rationale": _require_text(
                obj.get("rationale"),
                field="rationale",
            ),
        }


_GENERIC_W_LITERALS = {
    "yes",
    "no",
    "insufficient information",
    "unknown",
    "none",
    "summary of retrieved evidence",
}


def _candidate_w_literals(
    *,
    w: Mapping[str, Any],
    visible_c_inputs: Mapping[str, Any],
) -> list[str]:
    """
    Collect sample-specific W literals that must not be copied into C_minus.

    Long summary outputs are not used as single leakage literals because they
    are too coarse. Titles, answers, and short native outputs are retained.
    """
    visible = _normalized_text(
        _json_dumps(visible_c_inputs, indent=None)
    )
    candidates: list[str] = []

    gold_answer = w.get("gold_answer")
    if isinstance(gold_answer, (list, tuple)):
        candidates.extend(str(item) for item in gold_answer)
    elif gold_answer is not None:
        candidates.append(str(gold_answer))

    for state in (w["states"][0], w["states"][-1]):
        for title_key in (
            "gold_support_titles",
            "hop1_titles",
            "hop2_titles",
        ):
            candidates.extend(
                str(item)
                for item in (state.get(title_key) or [])
            )

        output = state.get("output")
        output_values = (
            list(output.values())
            if isinstance(output, Mapping)
            else [output]
        )
        for value in output_values:
            text = str(value or "").strip()
            normalized = _normalized_text(text)
            if 4 <= len(normalized) <= 160:
                candidates.append(text)

    hidden = []
    seen = set()
    for literal in candidates:
        normalized = _normalized_text(literal)
        if (
            len(normalized) < 4
            or normalized in seen
            or normalized in _GENERIC_W_LITERALS
        ):
            continue
        seen.add(normalized)
        if normalized not in visible:
            hidden.append(str(literal))

    return hidden


def _candidate_c_hidden_literals(
    *,
    c_plus: Mapping[str, Any],
    visible_c_inputs: Mapping[str, Any],
) -> list[str]:
    """Collect C-side downstream/gold literals not visible at the agent boundary."""
    visible = _normalized_text(
        _json_dumps(visible_c_inputs, indent=None)
    )
    candidates: list[str] = []

    gold_answer = c_plus.get("gold_answer")
    if isinstance(gold_answer, (list, tuple)):
        candidates.extend(str(item) for item in gold_answer)
    elif gold_answer is not None:
        candidates.append(str(gold_answer))

    for title_key in (
        "gold_support_titles",
        "hop1_titles",
        "hop2_titles",
    ):
        candidates.extend(
            str(item)
            for item in (c_plus.get(title_key) or [])
        )

    for value in (
        c_plus.get("answer"),
        c_plus.get("summary_2"),
    ):
        text = str(value or "").strip()
        normalized = _normalized_text(text)
        if 4 <= len(normalized) <= 160:
            candidates.append(text)

    hidden = []
    seen = set()
    for literal in candidates:
        normalized = _normalized_text(literal)
        if (
            len(normalized) < 4
            or normalized in seen
            or normalized in _GENERIC_W_LITERALS
        ):
            continue
        seen.add(normalized)
        if normalized not in visible:
            hidden.append(str(literal))

    return hidden


def _detect_literal_leaks(
    output: Any,
    hidden_literals: Sequence[str],
) -> list[str]:
    output_text = _normalized_text(
        _json_dumps(output, indent=None)
    )
    leaks = []
    for literal in hidden_literals:
        normalized = _normalized_text(literal)
        if normalized and normalized in output_text:
            leaks.append(str(literal))
    return leaks


def generate_c_damage(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent: str,
    base_prompt: str,
    visible_c_inputs: Mapping[str, Any],
    c_plus: Mapping[str, Any],
    w: Mapping[str, Any],
    match: Mapping[str, Any],
    c_position: int,
    max_attempts: int,
) -> dict[str, Any]:
    agent = _validate_agent(agent)
    _validate_w_material(w)

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1.")

    if int(match["selected_w_sample_index"]) != int(w["sample_index"]):
        raise ValueError("Match and selected W material disagree.")
    if str(match["agent"]) != agent:
        raise ValueError("Match agent and selected W agent disagree.")

    repair_feedback: dict[str, Any] = {}
    last_error: Exception | None = None
    w_hidden_literals = _candidate_w_literals(
        w=w,
        visible_c_inputs=visible_c_inputs,
    )
    c_hidden_literals = _candidate_c_hidden_literals(
        c_plus=c_plus,
        visible_c_inputs=visible_c_inputs,
    )
    hidden_literals = list(dict.fromkeys([
        *w_hidden_literals,
        *c_hidden_literals,
    ]))

    for attempt in range(max_attempts):
        try:
            parsed, prompt, raw, cache_hit = run_signature(
                runtime=runtime,
                operation=f"prompt_update.c_damage.attempt_{attempt}",
                lm=lm,
                signature_cls=GenerateTransportedDamageSignature,
                input_dict={
                    "agent": agent,
                    "agent_role": AGENT_ROLES[agent],
                    "base_prompt": base_prompt,
                    "visible_c_inputs": dict(visible_c_inputs),
                    "c_plus_state": compact_state(agent, c_plus),
                    "w_minus_state": compact_state(
                        agent,
                        w["states"][0],
                    ),
                    "w_plus_state": compact_state(
                        agent,
                        w["states"][-1],
                    ),
                    "w_ordered_repair_delta_p": (
                        _compact_w_delta_trace(w["delta_p_trace"])
                    ),
                    "match": _match_semantic_payload(match),
                    "repair_feedback": repair_feedback,
                },
                lm_config=lm_config,
                metadata={
                    "c_eval_position": int(c_position),
                    "c_stable_id": match.get("c_stable_id"),
                    "w_sample_index": int(w["sample_index"]),
                    "w_stable_id": str(w["stable_id"]),
                    "agent": agent,
                    "damage_attempt": int(attempt),
                    "match_fingerprint": match.get("match_fingerprint"),
                },
                return_cache_hit=True,
            )

            damaged_output = normalize_direct_output(
                agent,
                parsed["damaged_output"],
            )
            if _same_output(damaged_output, c_plus.get("output")):
                raise ValueError(
                    "damaged_output is identical to C_plus output."
                )

            leaks = _detect_literal_leaks(
                damaged_output,
                hidden_literals,
            )
            if leaks:
                repair_feedback = {
                    "rejected": True,
                    "reason": "hidden literal leakage",
                    "leaked_literals": leaks,
                    "instruction": (
                        "Regenerate using only the abstract W failure pattern "
                        "and only the target C sample's visible literals."
                    ),
                }
                last_error = ValueError(
                    f"Hidden literal leakage: {leaks}"
                )
                continue

            return {
                **parsed,
                "damaged_output": damaged_output,
                "leak_check": {
                    "passed": True,
                    "w_hidden_literal_count": len(w_hidden_literals),
                    "c_hidden_literal_count": len(c_hidden_literals),
                    "checked_literal_count": len(hidden_literals),
                    "checked_literals": hidden_literals,
                },
                "lm_trace": {
                    "rendered_prompt": prompt,
                    "raw_output": raw,
                    "cache_hit": cache_hit,
                    "attempt": int(attempt),
                },
            }

        except Exception as exc:
            last_error = exc
            repair_feedback = {
                "rejected": True,
                "reason": type(exc).__name__,
                "message": str(exc),
                "instruction": (
                    "Return strict JSON, preserve the native output "
                    "contract, produce a non-identical local neighbor, "
                    "and avoid W-side literals."
                ),
            }

    assert last_error is not None
    raise RuntimeError(
        f"Failed to generate C damage after {max_attempts} attempts: "
        f"{last_error}"
    ) from last_error


# ---------------------------------------------------------------------------
# Positive material construction
# ---------------------------------------------------------------------------


def _select_matched_w(
    *,
    match: Mapping[str, Any],
    w_candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    selected_index = int(match["selected_w_sample_index"])
    matches = [
        dict(w)
        for w in w_candidates
        if int(w["sample_index"]) == selected_index
    ]
    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one W material for selected sample_index "
            f"{selected_index}, found {len(matches)}."
        )

    selected_w = matches[0]
    if str(selected_w["stable_id"]) != str(
        match["selected_w_stable_id"]
    ):
        raise ValueError("Match and selected W stable_id disagree.")
    if str(selected_w["agent"]) != str(match["agent"]):
        raise ValueError("Match and selected W agent disagree.")
    return selected_w


def build_raw_c_material(
    *,
    c_position: int,
    c_row: Mapping[str, Any],
    match: Mapping[str, Any],
    w_candidates: Sequence[Mapping[str, Any]],
    material_fingerprint: str,
) -> dict[str, Any]:
    """Build the matched raw-C success boundary only."""
    selected_w = _select_matched_w(
        match=match,
        w_candidates=w_candidates,
    )
    agent = _validate_agent(selected_w["agent"])

    c_plus = state_from_trace(
        agent=agent,
        row=c_row,
        state_kind="endpoint",
        state_origin="baseline_correct",
    )
    visible_inputs = build_agent_inputs(agent, c_row)

    return {
        "row_type": "positive_material",
        "script_version": SCRIPT_VERSION,
        "material_fingerprint": material_fingerprint,
        "material_kind": RAW_MATERIAL_KIND,
        "polarity": "preserve",
        "c_eval_position": int(c_position),
        "c_row_index": c_row.get("index", c_position),
        "c_sample_id": c_row.get("sample_id"),
        "c_stable_id": _stable_id(c_row, c_position),
        "question": c_row.get("question"),
        "agent": agent,
        "base_prompt_key": AGENT_TO_PROMPT_KEY[agent],
        "matched_w_sample_index": int(selected_w["sample_index"]),
        "matched_w_stable_id": str(selected_w["stable_id"]),
        "match": dict(match),
        "visible_inputs": visible_inputs,
        "c_plus_state": c_plus,
        "raw_only": True,
    }


def build_delta_q_analysis(
    *,
    agent: str,
    states: Sequence[Mapping[str, Any]],
    polarity: str,
) -> list[dict[str, Any]]:
    """
    Build query-pair diagnostics only.

    No experiment condition consumes this as a separate delta-q arm. Endpoint
    conditions already carry query movement through their ordered state path.
    """
    agent = _validate_agent(agent)
    if agent != "query":
        return []
    if len(states) < 2:
        raise ValueError("Delta-q analysis requires at least two states.")

    rows = []
    for edge_index in range(len(states) - 1):
        source = states[edge_index]
        target = states[edge_index + 1]

        source_output = source.get("output")
        target_output = target.get("output")
        source_query = (
            source_output.get("query")
            if isinstance(source_output, Mapping)
            else source_output
        )
        target_query = (
            target_output.get("query")
            if isinstance(target_output, Mapping)
            else target_output
        )

        rows.append({
            "edge_index": int(edge_index),
            "source_query": _require_text(
                source_query,
                field="delta-q source_query",
            ),
            "target_query": _require_text(
                target_query,
                field="delta-q target_query",
            ),
            "polarity": str(polarity),
            "source_titles": list(source.get("hop2_titles") or []),
            "target_titles": list(target.get("hop2_titles") or []),
            "source_missing_recovery_rate": source.get(
                "missing_recovery_rate"
            ),
            "target_missing_recovery_rate": target.get(
                "missing_recovery_rate"
            ),
            "source_score": source.get("score"),
            "target_score": target.get("score"),
            "note": (
                "Directional query pair diagnostic; not an additive vector "
                "and not a separate prompt-update condition."
            ),
        })

    return rows


def build_signed_c_material(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    c_position: int,
    c_row: Mapping[str, Any],
    match: Mapping[str, Any],
    w_candidates: Sequence[Mapping[str, Any]],
    base_program: Any,
    base_candidate: Mapping[str, str],
    delta_attempts: int,
    damage_attempts: int,
    material_fingerprint: str,
) -> dict[str, Any]:
    if delta_attempts < 1:
        raise ValueError("delta_attempts must be at least 1.")
    if damage_attempts < 1:
        raise ValueError("damage_attempts must be at least 1.")

    selected_w = _select_matched_w(
        match=match,
        w_candidates=w_candidates,
    )
    agent = _validate_agent(selected_w["agent"])
    prompt_key = AGENT_TO_PROMPT_KEY[agent]
    if prompt_key not in base_candidate:
        raise KeyError(
            f"Base candidate is missing prompt key {prompt_key!r}."
        )
    base_prompt = _require_text(
        base_candidate[prompt_key],
        field=f"base prompt {prompt_key}",
    )

    c_plus = state_from_trace(
        agent=agent,
        row=c_row,
        state_kind="endpoint",
        state_origin="baseline_correct",
    )
    visible_inputs = build_agent_inputs(agent, c_row)

    damage = generate_c_damage(
        runtime=runtime,
        lm=lm,
        lm_config=lm_config,
        agent=agent,
        base_prompt=base_prompt,
        visible_c_inputs=visible_inputs,
        c_plus=c_plus,
        w=selected_w,
        match=match,
        c_position=c_position,
        max_attempts=damage_attempts,
    )

    summary_1_override = c_row.get("summary_1")
    c_minus = materialize_agent_state(
        agent=agent,
        program=base_program,
        row=c_row,
        output=damage["damaged_output"],
        summary_1=(
            str(summary_1_override)
            if summary_1_override is not None
            else None
        ),
        state_kind="endpoint",
        state_origin="transported_damage",
    )

    if _same_output(c_plus.get("output"), c_minus.get("output")):
        raise ValueError(
            "Materialized C_minus output is identical to C_plus."
        )

    states = [c_plus, c_minus]
    c_delta_p_trace = build_delta_p_trace(
        runtime=runtime,
        lm=lm,
        lm_config=lm_config,
        agent=agent,
        current_prompt=base_prompt,
        task_context={
            "question": c_row.get("question"),
            "agent": agent,
            "agent_role": AGENT_ROLES[agent],
            "direction": "C_plus_to_C_minus_avoid",
        },
        visible_inputs=visible_inputs,
        states=states,
        destination={
            "agent": agent,
            "output": damage["damaged_output"],
            "target_titles": list(c_minus.get("hop2_titles") or []),
        },
        row=c_row,
        metadata={
            "sample_index": int(c_position),
            "row_index": c_row.get("index", c_position),
            "material_role": "C_signed_avoid",
            "matched_w_sample_index": int(selected_w["sample_index"]),
            "matched_w_stable_id": str(selected_w["stable_id"]),
            "bisection_round": 0,
            "material_fingerprint": material_fingerprint,
        },
        max_attempts=delta_attempts,
        verbose=False,
    )

    if len(c_delta_p_trace) != 1:
        raise ValueError(
            "C_plus -> C_minus must produce exactly one adjacent delta-p edge."
        )
    if int(c_delta_p_trace[0].get("edge_index", -1)) != 0:
        raise ValueError("C-side delta-p edge_index must be 0.")

    before_metric = compute_local_metric(
        agent=agent,
        state=c_plus,
    )
    after_metric = compute_local_metric(
        agent=agent,
        state=c_minus,
    )
    before_value = before_metric.get("value")
    after_value = after_metric.get("value")
    degraded = (
        before_value is not None
        and after_value is not None
        and float(after_value) < float(before_value)
    )

    return {
        "row_type": "positive_material",
        "script_version": SCRIPT_VERSION,
        "material_fingerprint": material_fingerprint,
        "material_kind": SIGNED_MATERIAL_KIND,
        "polarity": "avoid",
        "c_eval_position": int(c_position),
        "c_row_index": c_row.get("index", c_position),
        "c_sample_id": c_row.get("sample_id"),
        "c_stable_id": _stable_id(c_row, c_position),
        "question": c_row.get("question"),
        "agent": agent,
        "base_prompt_key": prompt_key,
        "matched_w_sample_index": int(selected_w["sample_index"]),
        "matched_w_stable_id": str(selected_w["stable_id"]),
        "match": dict(match),
        "visible_inputs": visible_inputs,
        "c_plus_state": c_plus,
        "c_minus_state": c_minus,
        "states": states,
        "delta_p_trace": c_delta_p_trace,
        "delta_q_analysis": build_delta_q_analysis(
            agent=agent,
            states=states,
            polarity="avoid",
        ),
        "damage_generation": damage,
        "diagnostics": {
            "before_metric": before_metric,
            "after_metric": after_metric,
            "observed_metric_degradation": degraded,
            "answer_flip_required": False,
            "c_plus_correct": (
                float(c_row.get("score") or 0.0) == 1.0
            ),
            "c_plus_score": c_plus.get("score"),
            "c_minus_score": c_minus.get("score"),
        },
    }


# ---------------------------------------------------------------------------
# Resumable integrated positive-material preparation
# ---------------------------------------------------------------------------


def _successful_rows_by_fingerprint(
    rows: Sequence[Mapping[str, Any]],
    *,
    fingerprint_key: str,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("error"):
            continue
        fingerprint = str(row.get(fingerprint_key) or "").strip()
        if not fingerprint:
            continue
        result[fingerprint] = dict(row)
    return result


def _strip_selected_positions(
    rows: Sequence[Mapping[str, Any]],
    selected_positions: set[int],
) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in rows
        if int(row.get("c_eval_position", -1)) not in selected_positions
    ]


def prepare_positive_materials(
    *,
    require_signed: bool,
    selected_c_rows: Sequence[tuple[int, Mapping[str, Any]]],
    selected_w_materials: Sequence[Mapping[str, Any]],
    base_program: Any,
    base_candidate: Mapping[str, str],
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    match_path: str | Path,
    material_path: str | Path,
    damage_attempts: int,
    delta_attempts: int,
    materialization_config: Mapping[str, Any] | None = None,
    overwrite: bool = False,
) -> list[dict[str, Any]]:
    """
    Prepare all positive-side material required by one mixed condition.

    `require_signed=False`:
        matching + raw correct C boundary only.

    `require_signed=True`:
        matching + C_plus -> C_minus materialization + guarded avoid delta-p
        + query-pair diagnostics.

    Successful rows are resumed only when their full fingerprints match the
    current C row, selected W candidate set, LM config, base candidate, and
    materialization config. Error rows never block reruns.
    """
    _validate_selected_inputs(
        selected_c_rows=selected_c_rows,
        selected_w_materials=selected_w_materials,
    )
    if damage_attempts < 1:
        raise ValueError("damage_attempts must be at least 1.")
    if delta_attempts < 1:
        raise ValueError("delta_attempts must be at least 1.")

    match_path = Path(match_path)
    material_path = Path(material_path)
    if match_path.resolve() == material_path.resolve():
        raise ValueError("match_path and material_path must be different files.")
    selected_positions = {
        int(position)
        for position, _ in selected_c_rows
    }

    existing_match_rows = _read_jsonl(match_path)
    existing_material_rows = _read_jsonl(material_path)

    if overwrite:
        existing_match_rows = _strip_selected_positions(
            existing_match_rows,
            selected_positions,
        )
        existing_material_rows = _strip_selected_positions(
            existing_material_rows,
            selected_positions,
        )
        _rewrite_jsonl(match_path, existing_match_rows)
        _rewrite_jsonl(material_path, existing_material_rows)

    matches_by_fingerprint = _successful_rows_by_fingerprint(
        existing_match_rows,
        fingerprint_key="match_fingerprint",
    )
    materials_by_fingerprint = _successful_rows_by_fingerprint(
        existing_material_rows,
        fingerprint_key="material_fingerprint",
    )

    requested_kind = (
        SIGNED_MATERIAL_KIND
        if require_signed
        else RAW_MATERIAL_KIND
    )
    prepared: list[dict[str, Any]] = []

    for c_position, c_row_value in selected_c_rows:
        c_position = int(c_position)
        c_row = dict(c_row_value)

        match_fingerprint = _match_fingerprint(
            c_position=c_position,
            c_row=c_row,
            w_candidates=selected_w_materials,
            lm_config=lm_config,
        )
        match = matches_by_fingerprint.get(match_fingerprint)

        if match is None:
            try:
                match = match_c_to_w(
                    runtime=runtime,
                    lm=lm,
                    lm_config=lm_config,
                    c_position=c_position,
                    c_row=c_row,
                    w_candidates=selected_w_materials,
                )
            except Exception as exc:
                error_row = {
                    "row_type": "positive_match",
                    "script_version": SCRIPT_VERSION,
                    "match_fingerprint": match_fingerprint,
                    "c_eval_position": c_position,
                    "c_stable_id": _stable_id(c_row, c_position),
                    "error": True,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "traceback": traceback.format_exc(),
                }
                _append_jsonl(match_path, error_row)

                # A selected preservation case may fail to produce a
                # schema-valid C-to-W transport match after all retries.
                # Exclude only that C case rather than aborting the entire
                # agent-level proposal.
                if (
                    "Failed to match C to W after"
                    in str(exc)
                ):
                    print(
                        "[positive_update] skipping unmatchable C"
                        f" | c_position={c_position}"
                        f" error={type(exc).__name__}: {exc}",
                        flush=True,
                    )
                    continue

                raise RuntimeError(
                    "Positive matching failed for C eval position "
                    f"{c_position}. Inspect {match_path}."
                ) from exc

            if str(match["match_fingerprint"]) != match_fingerprint:
                raise RuntimeError(
                    "Internal match fingerprint mismatch."
                )
            _append_jsonl(match_path, match)
            matches_by_fingerprint[match_fingerprint] = match

        material_fingerprint = _material_fingerprint(
            material_kind=requested_kind,
            c_position=c_position,
            c_row=c_row,
            match=match,
            base_candidate=base_candidate,
            lm_config=lm_config,
            materialization_config=materialization_config,
            damage_attempts=damage_attempts,
            delta_attempts=delta_attempts,
        )
        material = materials_by_fingerprint.get(material_fingerprint)

        if material is None:
            try:
                if require_signed:
                    material = build_signed_c_material(
                        runtime=runtime,
                        lm=lm,
                        lm_config=lm_config,
                        c_position=c_position,
                        c_row=c_row,
                        match=match,
                        w_candidates=selected_w_materials,
                        base_program=base_program,
                        base_candidate=base_candidate,
                        delta_attempts=delta_attempts,
                        damage_attempts=damage_attempts,
                        material_fingerprint=material_fingerprint,
                    )
                else:
                    material = build_raw_c_material(
                        c_position=c_position,
                        c_row=c_row,
                        match=match,
                        w_candidates=selected_w_materials,
                        material_fingerprint=material_fingerprint,
                    )
            except Exception as exc:
                error_row = {
                    "row_type": "positive_material",
                    "script_version": SCRIPT_VERSION,
                    "material_fingerprint": material_fingerprint,
                    "material_kind": requested_kind,
                    "requested_level": (
                        "signed" if require_signed else "raw_only"
                    ),
                    "c_eval_position": c_position,
                    "c_row_index": c_row.get("index", c_position),
                    "c_stable_id": _stable_id(c_row, c_position),
                    "match_fingerprint": match_fingerprint,
                    "error": True,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "traceback": traceback.format_exc(),
                }
                _append_jsonl(material_path, error_row)

                # A matched preservation case is not necessarily
                # transportable into a valid signed C_minus. Exclude only
                # exhausted damage-generation cases; preserve hard failures
                # for unrelated implementation/API errors.
                if "Failed to generate C damage" in str(exc):
                    continue

                raise RuntimeError(
                    "Positive material generation failed for C eval "
                    f"position {c_position}. Inspect {material_path}."
                ) from exc

            if str(material["material_fingerprint"]) != material_fingerprint:
                raise RuntimeError(
                    "Internal material fingerprint mismatch."
                )
            _append_jsonl(material_path, material)
            materials_by_fingerprint[material_fingerprint] = material

        if material.get("material_kind") != requested_kind:
            raise RuntimeError(
                "Resumed positive material has the wrong material_kind: "
                f"expected={requested_kind!r}, "
                f"actual={material.get('material_kind')!r}."
            )
        if int(material["c_eval_position"]) != c_position:
            raise RuntimeError(
                "Resumed positive material has the wrong C eval position."
            )
        if str(material["c_stable_id"]) != _stable_id(c_row, c_position):
            raise RuntimeError(
                "Resumed positive material has a stale C stable_id."
            )

        prepared.append(dict(material))

    if not prepared:
        raise RuntimeError(
            "No positive material could be prepared from the selected C rows."
        )

    return prepared
