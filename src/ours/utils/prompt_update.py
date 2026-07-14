from __future__ import annotations

import hashlib
import json
import random
import traceback
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from gepa.proposer.reflective_mutation.base import LanguageModel, Signature

from ours.analyze_attribute import (
    AGENT_ORDER,
    AGENT_ROLES,
    AGENT_TO_PROMPT_KEY,
    compact_state,
)
from ours.lm import run_signature
from ours.prompts import save_prompt_candidate, validate_candidate
from ours.runtime import OursRuntime


SCRIPT_VERSION = "2026-07-14-v4-function-aware-updater"

CONDITIONS = (
    "base",
    "delta_p_neg_only",
    "endpoint_delta_neg_only",
    "delta_p_custom_signed",
    "endpoint_delta_custom_signed",
    "endpoint_delta_contrastive_raw_C",
)

NEG_ONLY_CONDITIONS = frozenset({
    "delta_p_neg_only",
    "endpoint_delta_neg_only",
})

MIXED_CONDITIONS = frozenset({
    "delta_p_custom_signed",
    "endpoint_delta_custom_signed",
    "endpoint_delta_contrastive_raw_C",
})

ENDPOINT_CONDITIONS = frozenset({
    "endpoint_delta_neg_only",
    "endpoint_delta_custom_signed",
    "endpoint_delta_contrastive_raw_C",
})

SIGNED_CONDITIONS = frozenset({
    "delta_p_custom_signed",
    "endpoint_delta_custom_signed",
})

AGENT_OUTPUT_CONTRACTS = {
    "summary1": (
        "The prompt must instruct the module to consume question and passages "
        "and produce one summary field."
    ),
    "query": (
        "The prompt must instruct the module to consume question and summary_1 "
        "and produce exactly one compact second-hop query field."
    ),
    "summary2": (
        "The prompt must instruct the module to consume question, context, and "
        "passages and produce one summary field."
    ),
    "final": (
        "The prompt must instruct the module to consume question, summary_1, "
        "and summary_2 and produce one answer field."
    ),
}

AGENT_FUNCTIONS = {
    "summary1": (
        "Pipeline position: after first-hop retrieval and before second-hop "
        "query generation. Inputs are the original question and first-hop "
        "passages. Functional responsibility: compress grounded first-hop "
        "evidence into an intermediate state that helps the next agent identify "
        "and retrieve the missing second-hop information. This agent is not "
        "responsible for producing the final answer, and its state may normally "
        "describe an unresolved bridge."
    ),
    "query": (
        "Pipeline position: after summary1 and before second-hop retrieval. "
        "Inputs are the original question and the first-hop intermediate state. "
        "Functional responsibility: produce one focused retrieval query that "
        "is likely to recover the missing evidence needed by the downstream "
        "agents. Query quality is determined by evidence recovery, not by "
        "whether the query itself resembles or contains the final answer."
    ),
    "summary2": (
        "Pipeline position: after second-hop retrieval and before final-answer "
        "generation. Inputs are the original question, the first-hop context, "
        "and newly retrieved passages. Functional responsibility: integrate "
        "the accumulated evidence into a grounded post-retrieval state that "
        "preserves the information needed by the final agent. Resolve the "
        "earlier bridge when the supplied evidence supports doing so; retain "
        "uncertainty only when the post-retrieval evidence remains insufficient."
    ),
    "final": (
        "Pipeline position: after both retrieval hops and both summaries. "
        "summary_1 is a pre-second-hop intermediate state and may normally "
        "contain unresolved bridge or retrieval-oriented language. summary_2 "
        "is the later post-retrieval integrated evidence state. Functional "
        "responsibility: use the accumulated visible evidence, especially the "
        "later state, to emit the minimal final answer. Do not infer that the "
        "final state is unresolved merely because summary_1 describes an "
        "earlier unresolved bridge."
    ),
}

__all__ = [
    "SCRIPT_VERSION",
    "CONDITIONS",
    "NEG_ONLY_CONDITIONS",
    "MIXED_CONDITIONS",
    "ENDPOINT_CONDITIONS",
    "SIGNED_CONDITIONS",
    "AGENT_OUTPUT_CONTRACTS",
    "AGENT_FUNCTIONS",
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
    "update_agent_prompt",
    "build_condition_candidate",
]


# ---------------------------------------------------------------------------
# Internal JSON / validation helpers
# ---------------------------------------------------------------------------


def _json_dumps(value: Any, *, indent: int | None = 2) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=indent,
        default=str,
        sort_keys=False,
    )


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


def _validate_condition(condition: str) -> str:
    condition = str(condition or "").strip()
    if condition not in CONDITIONS:
        raise ValueError(
            f"Unknown condition {condition!r}. "
            f"Expected one of {list(CONDITIONS)}."
        )
    return condition


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
# Shared paired batch manifest
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


def evidence_mode_for_condition(condition: str) -> str:
    condition = _validate_condition(condition)

    if condition in {"delta_p_neg_only", "delta_p_custom_signed"}:
        return "delta_p"
    if condition == "endpoint_delta_contrastive_raw_C":
        return "endpoint_delta_raw_C"
    if condition in ENDPOINT_CONDITIONS:
        return "endpoint_delta"
    if condition == "base":
        return "none"

    raise AssertionError(f"Unhandled condition: {condition}")


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


# ---------------------------------------------------------------------------
# Batch prompt updater
# ---------------------------------------------------------------------------


class BatchPromptUpdateSignature(Signature):
    input_keys = [
        "condition",
        "agent",
        "agent_role",
        "agent_function",
        "native_output_contract",
        "base_prompt",
        "evidence_mode",
        "batch_evidence",
    ]
    output_keys = [
        "updated_prompt",
        "rationale",
        "absorbed_patterns",
        "preserved_patterns",
        "avoided_patterns",
    ]

    @classmethod
    def prompt_renderer(cls, input_dict: Mapping[str, Any]) -> str:
        return f"""
You are generating ONE SHARED prompt for one agent in a fixed multi-agent
HotpotQA pipeline.

The prompt must be directly usable as the instruction for the selected DSPy
predictor. It must generalize across samples rather than reproduce any batch
answer, query, summary, title, or entity.

Primary objective:
Revise the supplied base prompt so that the selected agent better realizes the
stated function at its position in the pipeline. Interpret all evidence through
that function and the temporal meaning of the agent's inputs.

Evidence roles:
- W_repair / encourage: shows a direction that improved realization of the
  stated agent function.
- C_signed_avoid / avoid: shows a transported change that degraded a previously
  successful realization of the function. Use it to understand which functional
  capability must not be lost; do not mechanically invert it into a rule.
- raw_C_success / preserve: shows successful current behavior whose functional
  capability should remain available after the update.

Representation modes:
- delta_p: evidence contains ordered structured prompt deltas only.
- endpoint_delta: evidence contains the ordered state path together with the
  ordered structured prompt deltas. Use endpoint contrasts to understand what
  changed functionally.
- endpoint_delta_raw_C: W evidence uses endpoint paths plus deltas, while C
  evidence shows successful current behavior to retain.

Strict requirements:
- Output a PROMPT, not an agent output.
- Preserve the native input/output interface exactly.
- Start from the supplied base prompt and make the smallest coherent shared
  update supported by the batch and the stated agent function.
- Keep the revised prompt complete and self-contained. Do not refer to an
  omitted "original prompt", "base rules", or instructions that are no longer
  written explicitly in the revised prompt.
- Preserve useful base behavior not contradicted by the functional evidence.
- Do not hard-code batch answers, queries, summaries, titles, or entities.
- Do not treat batch-local wording, section labels, formatting tokens, or
  incidental phrases as direct decision criteria. Interpret intermediate text
  according to its pipeline position and semantic role.
- Prefer general capability-level guidance over enumerating sample-specific
  triggers, exception lists, or local/global decision rules.
- The task is not to classify W and C examples. Infer one prompt that better
  realizes the stated function while retaining capabilities demonstrated by
  successful behavior.
- Resolve conflicts conservatively and keep instructions operational.
- Do not mention W, C, polarity labels, states, endpoints, deltas, metrics,
  attribution, training, batches, or this optimization process in the final
  prompt.

Condition:
{input_dict["condition"]}

Agent:
{input_dict["agent"]}

Agent role:
{input_dict["agent_role"]}

Agent function and pipeline position:
{input_dict["agent_function"]}

Native output contract:
{input_dict["native_output_contract"]}

Base prompt:
{input_dict["base_prompt"]}

Evidence mode:
{input_dict["evidence_mode"]}

Batch evidence:
{input_dict["batch_evidence"]}

Return strict JSON only:
{{
  "updated_prompt": "complete directly usable shared prompt",
  "rationale": "brief batch-level explanation",
  "absorbed_patterns": ["short function-level improvement"],
  "preserved_patterns": ["short functional capability retained"],
  "avoided_patterns": ["short functional regression avoided"]
}}
""".strip()

    @classmethod
    def output_extractor(cls, lm_out: str) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        updated_prompt = _require_text(
            obj.get("updated_prompt"),
            field="updated_prompt",
        )

        def text_list(key: str) -> list[str]:
            value = obj.get(key, [])
            if not isinstance(value, list):
                raise TypeError(f"{key} must be a JSON list.")
            return [
                str(item).strip()
                for item in value
                if str(item).strip()
            ]

        return {
            "updated_prompt": updated_prompt,
            "rationale": str(obj.get("rationale") or "").strip(),
            "absorbed_patterns": text_list("absorbed_patterns"),
            "preserved_patterns": text_list("preserved_patterns"),
            "avoided_patterns": text_list("avoided_patterns"),
        }


def update_agent_prompt(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    condition: str,
    agent: str,
    base_prompt: str,
    evidence: Sequence[Mapping[str, Any]],
    max_evidence_chars: int,
) -> dict[str, Any]:
    """
    Generate one shared prompt for one agent.

    Evidence is never silently truncated. Empty evidence preserves the
    AgentGrad base prompt without an LM call.
    """
    condition = _validate_condition(condition)
    if condition == "base":
        raise ValueError(
            "The base condition must not call update_agent_prompt()."
        )
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")

    base_prompt = _require_text(base_prompt, field="base_prompt")
    evidence_list = [dict(item) for item in evidence]
    evidence_hash = _canonical_hash(evidence_list)
    base_prompt_hash = _canonical_hash(base_prompt)

    if not evidence_list:
        return {
            "script_version": SCRIPT_VERSION,
            "condition": condition,
            "agent": agent,
            "status": "no_evidence_base_preserved",
            "updated_prompt": base_prompt,
            "rationale": "No material was assigned to this agent.",
            "absorbed_patterns": [],
            "preserved_patterns": [],
            "avoided_patterns": [],
            "n_evidence": 0,
            "evidence_mode": evidence_mode_for_condition(condition),
            "evidence_kinds": {},
            "base_prompt_hash": base_prompt_hash,
            "evidence_hash": evidence_hash,
            "lm_trace": None,
        }

    evidence_json = _json_dumps(evidence_list)
    if len(evidence_json) > max_evidence_chars:
        raise ValueError(
            f"Evidence payload for {condition}/{agent} has "
            f"{len(evidence_json)} chars, exceeding "
            f"max_evidence_chars={max_evidence_chars}. "
            "Increase the limit or reduce batch_size; evidence is not "
            "silently truncated."
        )

    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation=(
            f"prompt_update.batch_prompt.{SCRIPT_VERSION}."
            f"{condition}.{agent}"
        ),
        lm=lm,
        signature_cls=BatchPromptUpdateSignature,
        input_dict={
            "condition": condition,
            "agent": agent,
            "agent_role": AGENT_ROLES[agent],
            "agent_function": AGENT_FUNCTIONS[agent],
            "native_output_contract": AGENT_OUTPUT_CONTRACTS[agent],
            "base_prompt": base_prompt,
            "evidence_mode": evidence_mode_for_condition(condition),
            "batch_evidence": evidence_json,
        },
        lm_config=lm_config,
        metadata={
            "script_version": SCRIPT_VERSION,
            "condition": condition,
            "agent": agent,
            "n_evidence": len(evidence_list),
            "base_prompt_hash": base_prompt_hash,
            "evidence_hash": evidence_hash,
        },
        return_cache_hit=True,
    )

    return {
        "script_version": SCRIPT_VERSION,
        "condition": condition,
        "agent": agent,
        "status": "updated",
        **parsed,
        "n_evidence": len(evidence_list),
        "evidence_mode": evidence_mode_for_condition(condition),
        "evidence_kinds": dict(
            Counter(item["evidence_kind"] for item in evidence_list)
        ),
        "base_prompt_hash": base_prompt_hash,
        "evidence_hash": evidence_hash,
        "lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    }


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
        if len(mixed_w) != len(c_materials):
            raise ValueError(
                f"Condition {condition!r} requires paired mixed material, "
                f"but mixed_w={len(mixed_w)} and "
                f"c_materials={len(c_materials)}."
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


def _successful_updater_rows(
    *,
    updater_path: Path,
    condition: str,
) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    successful: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    for row in _read_jsonl(updater_path):
        if row.get("error"):
            continue
        if str(row.get("condition")) != condition:
            continue
        if str(row.get("script_version") or "") != SCRIPT_VERSION:
            continue

        required = (
            "agent",
            "base_prompt_hash",
            "evidence_hash",
            "updated_prompt",
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
    candidate_path: str | Path,
    max_evidence_chars: int,
    overwrite: bool = False,
    program: Any = None,
) -> dict[str, str]:
    """
    Build and save exactly one four-agent prompt candidate.

    Resume is keyed by:
        condition + agent + base-prompt hash + evidence hash.

    Error rows never block reruns.
    """
    condition = _validate_condition(condition)
    updater_path = Path(updater_path)
    candidate_path = Path(candidate_path)

    candidate = dict(base_candidate)
    validate_candidate(candidate, program=program)

    if condition == "base":
        save_prompt_candidate(
            candidate_path,
            name=condition,
            candidate=candidate,
            description="Unchanged AgentGrad base candidate.",
            program=program,
        )
        return candidate

    _validate_condition_material_inputs(
        condition=condition,
        neg_w=neg_w,
        mixed_w=mixed_w,
        c_materials=c_materials,
    )

    if overwrite and updater_path.exists():
        preserved_rows = [
            row
            for row in _read_jsonl(updater_path)
            if str(row.get("condition")) != condition
        ]
        _rewrite_jsonl(updater_path, preserved_rows)

    done = _successful_updater_rows(
        updater_path=updater_path,
        condition=condition,
    )

    for agent in AGENT_ORDER:
        prompt_key = AGENT_TO_PROMPT_KEY[agent]
        base_prompt = _require_text(
            base_candidate[prompt_key],
            field=f"base prompt for {agent}",
        )
        evidence = build_condition_evidence(
            condition=condition,
            agent=agent,
            neg_w=neg_w,
            mixed_w=mixed_w,
            c_materials=c_materials,
        )
        base_prompt_hash = _canonical_hash(base_prompt)
        evidence_hash = _canonical_hash(
            [dict(item) for item in evidence]
        )
        resume_key = (
            condition,
            agent,
            base_prompt_hash,
            evidence_hash,
        )
        row = done.get(resume_key)

        if row is None:
            try:
                row = update_agent_prompt(
                    runtime=runtime,
                    lm=lm,
                    lm_config=lm_config,
                    condition=condition,
                    agent=agent,
                    base_prompt=base_prompt,
                    evidence=evidence,
                    max_evidence_chars=max_evidence_chars,
                )
            except Exception as exc:
                row = {
                    "script_version": SCRIPT_VERSION,
                    "condition": condition,
                    "agent": agent,
                    "error": True,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "base_prompt_hash": base_prompt_hash,
                    "evidence_hash": evidence_hash,
                    "traceback": traceback.format_exc(),
                }

            _append_jsonl(updater_path, row)

        if row.get("error"):
            raise RuntimeError(
                f"Condition {condition!r} has a failed updater for "
                f"agent {agent!r}. Inspect {updater_path}."
            )

        candidate[prompt_key] = _require_text(
            row.get("updated_prompt"),
            field=f"updated prompt for {condition}/{agent}",
        )

    validate_candidate(candidate, program=program)
    save_prompt_candidate(
        candidate_path,
        name=condition,
        candidate=candidate,
        description=(
            "Four-agent AgentGrad candidate updated from paired "
            f"positive-safety evidence under {condition}."
        ),
        program=program,
    )
    return candidate
