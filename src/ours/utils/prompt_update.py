# /home/jinwoo/gepa-official/src/ours/utils/prompt_update.py
from __future__ import annotations

import json
import random
import traceback
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from gepa.proposer.reflective_mutation.base import LanguageModel

from ours.analyze_attribute import (
    AGENT_ORDER,
    AGENT_TO_PROMPT_KEY,
    compact_state,
)
from ours.prompts import save_prompt_candidate, validate_candidate
from ours.runtime import OursRuntime
from ours.utils.prompt_feedback import (
    SCRIPT_VERSION,
    FEEDBACK_CANDIDATE_GENERATION_PROMPT_VERSION,
    FEEDBACK_NORM_SELECTION_PROMPT_VERSION,
    FEEDBACK_NORM_METHOD_PROMPTS,
    CONDITIONS,
    NEG_ONLY_CONDITIONS,
    MIXED_CONDITIONS,
    ENDPOINT_CONDITIONS,
    SIGNED_CONDITIONS,
    AGENT_OUTPUT_CONTRACTS,
    AGENT_FUNCTIONS,
    PROVISIONAL_HYPOTHESIS_FIELDS,
    INTEGRATED_FEEDBACK_FIELDS,
    REVISED_FEEDBACK_METADATA_FIELDS,
    HYPOTHESIS_DECISIONS,
    EDIT_ACTIONS,
    _canonical_hash,
    _integrated_feedback_payload,
    _json_dumps,
    _require_text,
    _validate_condition,
    evidence_mode_for_condition,
    generate_provisional_hypothesis,
    revise_hypothesis_with_positive_cases,
    generate_candidate_feedbacks_with_positive_cases,
    select_minimum_norm_feedback,
    synthesize_batch_feedback,
    update_agent_prompt,
)


__all__ = [
    "SCRIPT_VERSION",
    "FEEDBACK_CANDIDATE_GENERATION_PROMPT_VERSION",
    "FEEDBACK_NORM_SELECTION_PROMPT_VERSION",
    "FEEDBACK_NORM_METHOD_PROMPTS",
    "CONDITIONS",
    "NEG_ONLY_CONDITIONS",
    "MIXED_CONDITIONS",
    "ENDPOINT_CONDITIONS",
    "SIGNED_CONDITIONS",
    "AGENT_OUTPUT_CONTRACTS",
    "AGENT_FUNCTIONS",
    "PROVISIONAL_HYPOTHESIS_FIELDS",
    "INTEGRATED_FEEDBACK_FIELDS",
    "REVISED_FEEDBACK_METADATA_FIELDS",
    "HYPOTHESIS_DECISIONS",
    "EDIT_ACTIONS",
    "successful_attempt",
    "make_w_material",
    "extract_w_materials",
    "index_w_materials",
    "find_correct_rows",
    "build_batch_manifest",
    "load_or_create_batch_manifest",
    "resolve_manifest_rows",
    "evidence_mode_for_condition",
    "build_condition_evidence",
    "build_w_only_evidence",
    "build_c_only_evidence",
    "generate_provisional_hypothesis",
    "revise_hypothesis_with_positive_cases",
    "generate_candidate_feedbacks_with_positive_cases",
    "select_minimum_norm_feedback",
    "synthesize_batch_feedback",
    "update_agent_prompt",
    "build_condition_candidate",
]


# ---------------------------------------------------------------------------
# Local JSON / file helpers
# ---------------------------------------------------------------------------


def _read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def _write_json(path: str | Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json_dumps(value), encoding="utf-8")


def _append_jsonl(path: str | Path, row: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(_json_dumps(dict(row), indent=None) + "\n")


def _rewrite_jsonl(path: str | Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(_json_dumps(dict(row), indent=None) + "\n")


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

# ---------------------------------------------------------------------------
# Canonical W-side extraction
# ---------------------------------------------------------------------------


def successful_attempt(
    attribute_row: Mapping[str, Any],
) -> Mapping[str, Any]:
    """
    Return the unique successful attribution attempt.

    The successful attempt is selected by `attributed=True`; callers must not
    assume that it is the last attempt.
    """
    if attribute_row.get("attributed") is not True:
        raise ValueError("Attribute row is not attributed.")

    attempts = [
        attempt
        for attempt in (attribute_row.get("attempts", []) or [])
        if attempt.get("attributed") is True
    ]
    if len(attempts) != 1:
        raise ValueError(
            "Expected exactly one successful attribution attempt, "
            f"got {len(attempts)}."
        )
    return attempts[0]


def make_w_material(
    attribute_row: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Convert one attributed row into canonical sample-level W material.

    The complete ordered state path and complete ordered delta-p trace are
    retained. Individual edges are not relabeled as independently verified.
    """
    attempt = successful_attempt(attribute_row)
    probes = list(attempt.get("probes") or [])
    if not probes:
        raise ValueError("Successful attempt has no probes.")

    probe = probes[-1]
    endpoint_solvability = probe.get("endpoint_solvability") or {}
    if endpoint_solvability.get("target_solved") is not True:
        raise ValueError(
            "The final successful probe does not certify target_solved=True."
        )

    states = list(probe.get("states") or [])
    deltas = list(probe.get("delta_p_trace") or [])

    if len(states) < 2:
        raise ValueError("Successful W trace must contain at least two states.")
    if len(deltas) != len(states) - 1:
        raise ValueError(
            "W trace edge mismatch: "
            f"states={len(states)}, deltas={len(deltas)}."
        )

    for edge_position, delta_row in enumerate(deltas):
        edge_index = int(delta_row.get("edge_index", -1))
        if edge_index != edge_position:
            raise ValueError(
                "W delta-p trace is not in canonical adjacent-edge order: "
                f"position={edge_position}, edge_index={edge_index}."
            )
        if not isinstance(delta_row.get("delta_p"), Mapping):
            raise TypeError(
                "Each W delta-p row must contain a mapping-valued `delta_p`."
            )

    agent = str(
        attempt.get("agent")
        or attribute_row.get("attributed_agent")
        or ""
    ).strip()
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown attributed agent: {agent!r}.")

    sample_index = int(attribute_row["sample_index"])

    return {
        "material_kind": "W_repair",
        "polarity": "encourage",
        "sample_index": sample_index,
        "row_index": attribute_row.get("row_index"),
        "sample_id": attribute_row.get("sample_id"),
        "stable_id": _stable_id(attribute_row, sample_index),
        "question": attribute_row.get("question"),
        "gold_answer": attribute_row.get("gold_answer"),
        "baseline_answer": attribute_row.get("baseline_answer"),
        "agent": agent,
        "base_prompt_key": attempt.get("base_prompt_key"),
        "base_prompt": attempt.get("base_prompt"),
        "states": states,
        "delta_p_trace": deltas,
        "source_state": attempt.get("source_state"),
        "destination_state": attempt.get("destination_state"),
        "successful_bisection_round": attempt.get(
            "successful_bisection_round"
        ),
        "n_edges": int(probe.get("n_edges", len(deltas))),
        "endpoint_solvability": endpoint_solvability,
        "trace_endpoint_solved": True,
        "edge_individually_verified": False,
    }


def extract_w_materials(
    attribute_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """
    Extract all attributed W rows and reject duplicate sample indices.
    """
    materials = [
        make_w_material(row)
        for row in attribute_rows
        if row.get("attributed") is True
    ]
    index_w_materials(materials)
    return materials


def index_w_materials(
    w_materials: Sequence[Mapping[str, Any]],
) -> dict[int, dict[str, Any]]:
    indexed: dict[int, dict[str, Any]] = {}

    for material in w_materials:
        sample_index = int(material["sample_index"])
        if sample_index in indexed:
            raise ValueError(
                f"Duplicate W material sample_index: {sample_index}."
            )
        indexed[sample_index] = dict(material)

    return indexed


def find_correct_rows(
    eval_rows: Sequence[Mapping[str, Any]],
) -> list[tuple[int, Mapping[str, Any]]]:
    return [
        (position, row)
        for position, row in enumerate(eval_rows)
        if float(row.get("score") or 0.0) == 1.0
    ]

# ---------------------------------------------------------------------------
# Legacy shared paired batch manifest
# ---------------------------------------------------------------------------


def build_batch_manifest(
    *,
    w_materials: Sequence[Mapping[str, Any]],
    correct_rows: Sequence[tuple[int, Mapping[str, Any]]],
    batch_size: int,
    seed: int,
) -> dict[str, Any]:
    """
    Build one deterministic paired manifest shared across all conditions.

    Neg-only:
        `batch_size` attributed W samples.

    Mixed:
        the first `batch_size / 2` samples from the neg W selection and
        `batch_size / 2` correct C samples.
    """
    if batch_size < 2:
        raise ValueError("batch_size must be at least 2.")
    if batch_size % 2 != 0:
        raise ValueError(
            "batch_size must be even because mixed conditions use an exact "
            "half-W / half-C composition."
        )
    if len(w_materials) < batch_size:
        raise ValueError(
            f"Need {batch_size} attributed W rows, found {len(w_materials)}."
        )

    half = batch_size // 2
    if len(correct_rows) < half:
        raise ValueError(
            f"Need {half} correct C rows, found {len(correct_rows)}."
        )

    rng = random.Random(seed)
    w_order = list(range(len(w_materials)))
    c_order = list(range(len(correct_rows)))
    rng.shuffle(w_order)
    rng.shuffle(c_order)

    neg_indices = w_order[:batch_size]
    mixed_w_indices = neg_indices[:half]
    mixed_c_indices = c_order[:half]

    neg_w = [dict(w_materials[index]) for index in neg_indices]
    mixed_w = [dict(w_materials[index]) for index in mixed_w_indices]

    mixed_c = []
    for index in mixed_c_indices:
        eval_position, row = correct_rows[index]
        mixed_c.append({
            "eval_position": int(eval_position),
            "row_index": row.get("index", eval_position),
            "sample_id": row.get("sample_id"),
            "stable_id": _stable_id(row, eval_position),
            "question": row.get("question"),
        })

    manifest = {
        "script_version": SCRIPT_VERSION,
        "seed": int(seed),
        "batch_size": int(batch_size),
        "mixed_half_size": int(half),
        "neg_w": [
            {
                "sample_index": int(row["sample_index"]),
                "row_index": row.get("row_index"),
                "stable_id": row["stable_id"],
                "agent": row["agent"],
            }
            for row in neg_w
        ],
        "mixed_w": [
            {
                "sample_index": int(row["sample_index"]),
                "row_index": row.get("row_index"),
                "stable_id": row["stable_id"],
                "agent": row["agent"],
            }
            for row in mixed_w
        ],
        "mixed_c": mixed_c,
        "sampling_policy": {
            "neg": "batch_size attributed W rows",
            "mixed": "first half of neg W selection + half correct C rows",
            "replacement": False,
        },
    }
    _validate_manifest_shape(manifest)
    return manifest


def _validate_manifest_shape(manifest: Mapping[str, Any]) -> None:
    batch_size = int(manifest["batch_size"])
    half = int(manifest["mixed_half_size"])

    if batch_size < 2:
        raise ValueError("Manifest batch_size must be at least 2.")
    if batch_size % 2 != 0:
        raise ValueError("Manifest batch_size must be even.")
    if half != batch_size // 2:
        raise ValueError(
            "Manifest mixed_half_size does not match batch_size / 2."
        )

    neg_w = list(manifest.get("neg_w") or [])
    mixed_w = list(manifest.get("mixed_w") or [])
    mixed_c = list(manifest.get("mixed_c") or [])

    if len(neg_w) != batch_size:
        raise ValueError(
            "Manifest neg_w count mismatch: "
            f"expected={batch_size}, actual={len(neg_w)}."
        )
    if len(mixed_w) != half:
        raise ValueError(
            "Manifest mixed_w count mismatch: "
            f"expected={half}, actual={len(mixed_w)}."
        )
    if len(mixed_c) != half:
        raise ValueError(
            "Manifest mixed_c count mismatch: "
            f"expected={half}, actual={len(mixed_c)}."
        )

    neg_indices = [int(ref["sample_index"]) for ref in neg_w]
    mixed_indices = [int(ref["sample_index"]) for ref in mixed_w]
    c_positions = [int(ref["eval_position"]) for ref in mixed_c]

    if len(set(neg_indices)) != len(neg_indices):
        raise ValueError("Manifest neg_w contains duplicate samples.")
    if len(set(c_positions)) != len(c_positions):
        raise ValueError("Manifest mixed_c contains duplicate samples.")
    if mixed_indices != neg_indices[:half]:
        raise ValueError(
            "Manifest mixed_w must equal the first half of neg_w."
        )


def load_or_create_batch_manifest(
    *,
    path: str | Path,
    w_materials: Sequence[Mapping[str, Any]],
    correct_rows: Sequence[tuple[int, Mapping[str, Any]]],
    batch_size: int,
    seed: int,
    overwrite: bool = False,
) -> dict[str, Any]:
    """
    Load the shared manifest or create it deterministically.
    """
    path = Path(path)

    if path.exists() and not overwrite:
        manifest = _read_json(path)
        if not isinstance(manifest, Mapping):
            raise TypeError("Batch manifest must be a JSON object.")

        _validate_manifest_shape(manifest)

        if int(manifest["batch_size"]) != int(batch_size):
            raise ValueError(
                "Existing manifest batch_size differs from the requested "
                "batch size. Use --overwrite or the original value."
            )
        if int(manifest["seed"]) != int(seed):
            raise ValueError(
                "Existing manifest seed differs from the requested seed. "
                "Use --overwrite or the original value."
            )
        return dict(manifest)

    manifest = build_batch_manifest(
        w_materials=w_materials,
        correct_rows=correct_rows,
        batch_size=batch_size,
        seed=seed,
    )
    _write_json(path, manifest)
    return manifest


def resolve_manifest_rows(
    *,
    manifest: Mapping[str, Any],
    w_by_sample_index: Mapping[int, Mapping[str, Any]],
    eval_rows: Sequence[Mapping[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[tuple[int, dict[str, Any]]],
]:
    """
    Resolve manifest references against the current W and eval inputs.

    Stable IDs, W agents, and C correctness are checked to detect stale
    manifests.
    """
    _validate_manifest_shape(manifest)

    def resolve_w(
        refs: Sequence[Mapping[str, Any]],
        *,
        label: str,
    ) -> list[dict[str, Any]]:
        resolved = []

        for ref in refs:
            sample_index = int(ref["sample_index"])
            if sample_index not in w_by_sample_index:
                raise KeyError(
                    f"Manifest {label} sample {sample_index} is unavailable."
                )

            material = dict(w_by_sample_index[sample_index])
            expected_id = str(ref["stable_id"])
            actual_id = str(material["stable_id"])
            if expected_id != actual_id:
                raise ValueError(
                    f"Manifest {label} stable_id mismatch for "
                    f"sample_index={sample_index}: "
                    f"expected={expected_id!r}, actual={actual_id!r}."
                )

            expected_agent = str(ref["agent"])
            actual_agent = str(material["agent"])
            if expected_agent != actual_agent:
                raise ValueError(
                    f"Manifest {label} agent mismatch for "
                    f"sample_index={sample_index}: "
                    f"expected={expected_agent!r}, actual={actual_agent!r}."
                )

            resolved.append(material)

        return resolved

    neg_w = resolve_w(manifest["neg_w"], label="neg_w")
    mixed_w = resolve_w(manifest["mixed_w"], label="mixed_w")

    mixed_c = []
    for ref in manifest["mixed_c"]:
        position = int(ref["eval_position"])
        if not 0 <= position < len(eval_rows):
            raise IndexError(
                f"Manifest C eval position is out of range: {position}."
            )

        row = dict(eval_rows[position])
        if float(row.get("score") or 0.0) != 1.0:
            raise ValueError(
                f"Manifest C sample at eval position {position} "
                "is no longer correct."
            )

        expected_id = str(ref["stable_id"])
        actual_id = _stable_id(row, position)
        if expected_id != actual_id:
            raise ValueError(
                "Manifest C stable_id mismatch at "
                f"eval_position={position}: "
                f"expected={expected_id!r}, actual={actual_id!r}."
            )

        mixed_c.append((position, row))

    return neg_w, mixed_w, mixed_c

# ---------------------------------------------------------------------------
# Condition evidence construction
# ---------------------------------------------------------------------------


def _compact_delta_trace(
    delta_p_trace: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    compact = []

    for position, item in enumerate(delta_p_trace):
        edge_index = int(item["edge_index"])
        if edge_index != position:
            raise ValueError(
                "delta_p_trace is not in canonical adjacent-edge order: "
                f"position={position}, edge_index={edge_index}."
            )

        delta_p = item.get("delta_p")
        if not isinstance(delta_p, Mapping):
            raise TypeError(
                "delta_p_trace item must contain mapping-valued `delta_p`."
            )

        compact.append({
            "edge_index": edge_index,
            "delta_p": dict(delta_p),
            "rationale": item.get("rationale"),
        })

    return compact


def _compact_state_path(
    agent: str,
    states: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if len(states) < 2:
        raise ValueError("Endpoint evidence requires at least two states.")

    return [
        {
            "state_index": index,
            **compact_state(agent, state),
        }
        for index, state in enumerate(states)
    ]


def _w_evidence(
    w: Mapping[str, Any],
    *,
    include_endpoint: bool,
) -> dict[str, Any]:
    if w.get("trace_endpoint_solved") is not True:
        raise ValueError("W evidence must be trace-endpoint verified.")

    evidence = {
        "evidence_kind": "W_repair",
        "instructional_role": "encourage",
        "sample_index": int(w["sample_index"]),
        "stable_id": w.get("stable_id"),
        "question": w.get("question"),
        "ordered_delta_p_trace": _compact_delta_trace(w["delta_p_trace"]),
        "trace_endpoint_solved": True,
        "edge_individually_verified": False,
    }
    if include_endpoint:
        evidence["ordered_state_path"] = _compact_state_path(
            str(w["agent"]),
            w["states"],
        )
    return evidence


def _c_signed_evidence(
    c: Mapping[str, Any],
    *,
    include_endpoint: bool,
) -> dict[str, Any]:
    if c.get("polarity") != "avoid":
        raise ValueError("Signed C evidence must have polarity='avoid'.")
    if c.get("c_plus_state") is None or c.get("c_minus_state") is None:
        raise ValueError(
            "Signed C evidence requires C_plus and C_minus states."
        )
    if c.get("delta_p_trace") is None:
        raise ValueError("Signed C evidence requires a delta_p_trace.")

    damage_generation = c.get("damage_generation") or {}
    evidence = {
        "evidence_kind": "C_signed_avoid",
        "instructional_role": "avoid",
        "c_eval_position": int(c["c_eval_position"]),
        "c_stable_id": c.get("c_stable_id"),
        "question": c.get("question"),
        "matched_w_sample_index": int(c["matched_w_sample_index"]),
        "matched_w_stable_id": c.get("matched_w_stable_id"),
        "transported_failure_pattern": damage_generation.get(
            "transported_failure_pattern"
        ),
        "expected_damage": damage_generation.get("expected_damage"),
        "ordered_delta_p_trace": _compact_delta_trace(c["delta_p_trace"]),
        "answer_flip_required": False,
    }
    if include_endpoint:
        evidence["ordered_state_path"] = _compact_state_path(
            str(c["agent"]),
            c["states"],
        )
    return evidence


def _raw_c_evidence(c: Mapping[str, Any]) -> dict[str, Any]:
    if c.get("c_plus_state") is None:
        raise ValueError("Raw-C evidence requires c_plus_state.")

    agent = str(c["agent"])
    return {
        "evidence_kind": "raw_C_success",
        "instructional_role": "preserve",
        "c_eval_position": int(c["c_eval_position"]),
        "c_stable_id": c.get("c_stable_id"),
        "question": c.get("question"),
        "visible_inputs": c.get("visible_inputs"),
        "successful_state": compact_state(agent, c["c_plus_state"]),
        "successful_output": c["c_plus_state"].get("output"),
    }


def build_condition_evidence(
    *,
    condition: str,
    agent: str,
    neg_w: Sequence[Mapping[str, Any]],
    mixed_w: Sequence[Mapping[str, Any]],
    c_materials: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build the exact agent-specific evidence for one experiment condition.
    """
    condition = _validate_condition(condition)
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")
    if condition == "base":
        return []

    include_endpoint = condition in ENDPOINT_CONDITIONS
    evidence: list[dict[str, Any]] = []

    selected_w = neg_w if condition in NEG_ONLY_CONDITIONS else mixed_w
    for w in selected_w:
        if str(w["agent"]) == agent:
            evidence.append(
                _w_evidence(w, include_endpoint=include_endpoint)
            )

    if condition in SIGNED_CONDITIONS:
        for c in c_materials:
            if str(c["agent"]) == agent:
                evidence.append(
                    _c_signed_evidence(c, include_endpoint=include_endpoint)
                )

    if condition == "endpoint_delta_contrastive_raw_C":
        for c in c_materials:
            if str(c["agent"]) == agent:
                evidence.append(_raw_c_evidence(c))

    return evidence


def build_w_only_evidence(
    *,
    condition: str,
    agent: str,
    w_materials: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build only the W-side evidence used to propose a provisional hypothesis.

    Unlike ``build_condition_evidence()``, this helper intentionally excludes
    all C-side material. It is the first stage of hypothesis-conditioned C
    selection:

        selected W -> provisional hypothesis -> matched C selection
    """
    condition = _validate_condition(condition)
    if condition == "base":
        return []
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")

    include_endpoint = condition in ENDPOINT_CONDITIONS
    return [
        _w_evidence(
            material,
            include_endpoint=include_endpoint,
        )
        for material in w_materials
        if str(material.get("agent")) == agent
    ]


def build_c_only_evidence(
    *,
    condition: str,
    agent: str,
    c_materials: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build only the C-side evidence after matched C rows are materialized.

    Signed conditions expose transported-damage evidence. The raw-C condition
    exposes the preserved successful state. Neg-only and base conditions do not
    have C evidence.
    """
    condition = _validate_condition(condition)
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")
    if condition == "base" or condition in NEG_ONLY_CONDITIONS:
        return []

    include_endpoint = condition in ENDPOINT_CONDITIONS
    evidence: list[dict[str, Any]] = []

    if condition in SIGNED_CONDITIONS:
        for material in c_materials:
            if str(material.get("agent")) != agent:
                continue
            evidence.append(
                _c_signed_evidence(
                    material,
                    include_endpoint=include_endpoint,
                )
            )
        return evidence

    if condition == "endpoint_delta_contrastive_raw_C":
        for material in c_materials:
            if str(material.get("agent")) != agent:
                continue
            evidence.append(_raw_c_evidence(material))
        return evidence

    raise AssertionError(f"Unhandled mixed condition: {condition}")

# ---------------------------------------------------------------------------
# Single-condition candidate construction
# ---------------------------------------------------------------------------


def _validate_condition_material_inputs(
    *,
    condition: str,
    neg_w: Sequence[Mapping[str, Any]],
    mixed_w: Sequence[Mapping[str, Any]],
    c_materials: Sequence[Mapping[str, Any]],
) -> None:
    """
    Reject incomplete or mismatched condition material before any LM call.
    """
    for label, materials in (
        ("neg_w", neg_w),
        ("mixed_w", mixed_w),
        ("c_materials", c_materials),
    ):
        for position, material in enumerate(materials):
            agent = str(material.get("agent") or "").strip()
            if agent not in AGENT_TO_PROMPT_KEY:
                raise ValueError(
                    f"{label}[{position}] has unknown agent {agent!r}."
                )

    if condition in NEG_ONLY_CONDITIONS:
        if not neg_w:
            raise ValueError(
                f"Condition {condition!r} requires non-empty neg_w material."
            )
        return

    if condition in MIXED_CONDITIONS:
        if not mixed_w and not c_materials:
            return

        if not mixed_w:
            raise ValueError(
                f"Condition {condition!r} requires non-empty mixed_w material."
            )
        if not c_materials:
            raise ValueError(
                f"Condition {condition!r} requires non-empty C material."
            )
        w_agents = {
            str(material["agent"])
            for material in mixed_w
        }
        for position, material in enumerate(
            c_materials
        ):
            c_agent = str(material["agent"])
            if c_agent not in w_agents:
                raise ValueError(
                    f"c_materials[{position}] belongs "
                    f"to agent {c_agent!r}, but that "
                    "agent has no selected W material."
                )

        if condition in SIGNED_CONDITIONS:
            for position, material in enumerate(c_materials):
                if material.get("polarity") != "avoid":
                    raise ValueError(
                        f"c_materials[{position}] must have polarity='avoid' "
                        f"for {condition!r}."
                    )
                if material.get("c_minus_state") is None:
                    raise ValueError(
                        f"c_materials[{position}] is missing c_minus_state "
                        f"for {condition!r}."
                    )
                if material.get("delta_p_trace") is None:
                    raise ValueError(
                        f"c_materials[{position}] is missing delta_p_trace "
                        f"for {condition!r}."
                    )

        if condition == "endpoint_delta_contrastive_raw_C":
            for position, material in enumerate(c_materials):
                if material.get("c_plus_state") is None:
                    raise ValueError(
                        f"c_materials[{position}] is missing c_plus_state "
                        "for the raw-C condition."
                    )
        return

    raise AssertionError(f"Unhandled non-base condition: {condition}")


def _successful_feedback_rows(
    *,
    feedback_path: Path,
    condition: str,
) -> dict[
    tuple[str, str, str, str],
    dict[str, Any],
]:
    successful = {}

    for row in _read_jsonl(feedback_path):
        if row.get("error"):
            continue
        if str(row.get("condition")) != condition:
            continue
        if (
            str(row.get("script_version") or "")
            != SCRIPT_VERSION
        ):
            continue

        required = (
            "agent",
            "base_prompt_hash",
            "evidence_hash",
            "integrated_feedback",
        )
        if any(key not in row for key in required):
            continue

        key = (
            condition,
            str(row["agent"]),
            str(row["base_prompt_hash"]),
            str(row["evidence_hash"]),
        )
        successful[key] = dict(row)

    return successful


def _successful_updater_rows(
    *,
    updater_path: Path,
    condition: str,
) -> dict[
    tuple[str, str, str, str],
    dict[str, Any],
]:
    successful = {}

    for row in _read_jsonl(updater_path):
        if row.get("error"):
            continue
        if str(row.get("condition")) != condition:
            continue
        if (
            str(row.get("script_version") or "")
            != SCRIPT_VERSION
        ):
            continue

        required = (
            "agent",
            "base_prompt_hash",
            "integrated_feedback_hash",
            "updated_prompt",
        )
        if any(key not in row for key in required):
            continue

        key = (
            condition,
            str(row["agent"]),
            str(row["base_prompt_hash"]),
            str(row["integrated_feedback_hash"]),
        )
        successful[key] = dict(row)

    return successful


def build_condition_candidate(
    *,
    condition: str,
    base_candidate: Mapping[str, str],
    neg_w: Sequence[Mapping[str, Any]],
    mixed_w: Sequence[Mapping[str, Any]],
    c_materials: Sequence[Mapping[str, Any]],
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    updater_path: str | Path,
    feedback_path: str | Path | None = None,
    candidate_path: str | Path,
    max_evidence_chars: int,
    overwrite: bool = False,
    program: Any = None,
) -> dict[str, str]:
    """
    Build one four-agent candidate through two independent LM stages:

        batch evidence -> integrated feedback
        base prompt + integrated feedback -> updated prompt

    The rewrite stage never receives raw batch evidence.
    """
    condition = _validate_condition(condition)
    updater_path = Path(updater_path)
    feedback_path = (
        Path(feedback_path)
        if feedback_path is not None
        else updater_path.with_name(
            "integrated_feedback_rows.jsonl"
        )
    )
    candidate_path = Path(candidate_path)

    candidate = dict(base_candidate)
    validate_candidate(
        candidate,
        program=program,
    )

    if condition == "base":
        save_prompt_candidate(
            candidate_path,
            name=condition,
            candidate=candidate,
            description=(
                "Unchanged AgentGrad base candidate."
            ),
            program=program,
        )
        return candidate

    _validate_condition_material_inputs(
        condition=condition,
        neg_w=neg_w,
        mixed_w=mixed_w,
        c_materials=c_materials,
    )

    if overwrite:
        for path in (
            feedback_path,
            updater_path,
        ):
            if not path.exists():
                continue
            preserved_rows = [
                row
                for row in _read_jsonl(path)
                if (
                    str(row.get("condition"))
                    != condition
                )
            ]
            _rewrite_jsonl(
                path,
                preserved_rows,
            )

    feedback_done = (
        _successful_feedback_rows(
            feedback_path=feedback_path,
            condition=condition,
        )
    )
    updater_done = (
        _successful_updater_rows(
            updater_path=updater_path,
            condition=condition,
        )
    )

    for agent in AGENT_ORDER:
        prompt_key = AGENT_TO_PROMPT_KEY[agent]
        base_prompt = _require_text(
            base_candidate[prompt_key],
            field=f"base prompt for {agent}",
        )
        base_prompt_hash = _canonical_hash(
            base_prompt
        )

        evidence = build_condition_evidence(
            condition=condition,
            agent=agent,
            neg_w=neg_w,
            mixed_w=mixed_w,
            c_materials=c_materials,
        )
        evidence_list = [
            dict(item)
            for item in evidence
        ]
        evidence_hash = _canonical_hash(
            evidence_list
        )

        feedback_key = (
            condition,
            agent,
            base_prompt_hash,
            evidence_hash,
        )
        feedback_row = feedback_done.get(
            feedback_key
        )

        if feedback_row is None:
            try:
                feedback_row = (
                    synthesize_batch_feedback(
                        runtime=runtime,
                        lm=lm,
                        lm_config=lm_config,
                        condition=condition,
                        agent=agent,
                        base_prompt=base_prompt,
                        evidence=evidence_list,
                        max_evidence_chars=(
                            max_evidence_chars
                        ),
                    )
                )
            except Exception as exc:
                feedback_row = {
                    "script_version": SCRIPT_VERSION,
                    "row_type": (
                        "integrated_feedback"
                    ),
                    "condition": condition,
                    "agent": agent,
                    "error": True,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "base_prompt_hash": (
                        base_prompt_hash
                    ),
                    "evidence_hash": evidence_hash,
                    "traceback": traceback.format_exc(),
                }

            _append_jsonl(
                feedback_path,
                feedback_row,
            )

        if feedback_row.get("error"):
            raise RuntimeError(
                f"Condition {condition!r} has a "
                f"failed feedback synthesis for "
                f"agent {agent!r}. Inspect "
                f"{feedback_path}."
            )

        feedback_payload = (
            _integrated_feedback_payload(
                feedback_row
            )
        )
        integrated_feedback_hash = (
            _canonical_hash(
                feedback_payload
            )
        )
        updater_key = (
            condition,
            agent,
            base_prompt_hash,
            integrated_feedback_hash,
        )
        updater_row = updater_done.get(
            updater_key
        )

        if updater_row is None:
            try:
                updater_row = update_agent_prompt(
                    runtime=runtime,
                    lm=lm,
                    lm_config=lm_config,
                    condition=condition,
                    agent=agent,
                    base_prompt=base_prompt,
                    integrated_feedback_row=(
                        feedback_row
                    ),
                )
            except Exception as exc:
                updater_row = {
                    "script_version": SCRIPT_VERSION,
                    "row_type": "prompt_rewrite",
                    "condition": condition,
                    "agent": agent,
                    "error": True,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "base_prompt_hash": (
                        base_prompt_hash
                    ),
                    "evidence_hash": (
                        evidence_hash
                    ),
                    "integrated_feedback_hash": (
                        integrated_feedback_hash
                    ),
                    "traceback": traceback.format_exc(),
                }

            _append_jsonl(
                updater_path,
                updater_row,
            )

        if updater_row.get("error"):
            raise RuntimeError(
                f"Condition {condition!r} has a "
                f"failed prompt rewrite for agent "
                f"{agent!r}. Inspect "
                f"{updater_path}."
            )

        candidate[prompt_key] = _require_text(
            updater_row.get("updated_prompt"),
            field=(
                f"updated prompt for "
                f"{condition}/{agent}"
            ),
        )

    validate_candidate(
        candidate,
        program=program,
    )
    save_prompt_candidate(
        candidate_path,
        name=condition,
        candidate=candidate,
        description=(
            "Four-agent candidate produced through "
            "independent batch-feedback synthesis "
            "and prompt-rewrite stages under "
            f"{condition}."
        ),
        program=program,
    )
    return candidate