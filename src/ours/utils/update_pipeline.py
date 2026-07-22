# /home/jinwoo/gepa-official/src/ours/utils/update_pipeline.py
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import random
import shutil
import traceback
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv
from gepa.proposer.reflective_mutation.base import Signature
from tqdm.auto import tqdm

from ours.analyze_attribute import (
    AGENT_ORDER,
    AGENT_TO_PROMPT_KEY,
    load_candidate_file,
    normalize_eval_rows,
)
from ours.lm import run_signature
from ours.prompts import (
    BASELINE_PROMPT_SET,
    get_method_prompt,
    save_prompt_candidate,
    validate_candidate,
)
from ours.runtime import OursRuntime
from ours.utils.matched_c import (
    SCRIPT_VERSION as MATCHED_C_UTIL_VERSION,
    MatchedCSelection,
    select_matched_c_rows,
)
from ours.utils.positive_update import (
    SCRIPT_VERSION as POSITIVE_UTIL_VERSION,
    prepare_positive_materials,
)
from ours.utils.prompt_update import (
    SCRIPT_VERSION as PROMPT_UTIL_VERSION,
    FEEDBACK_CANDIDATE_GENERATION_PROMPT_VERSION,
    FEEDBACK_NORM_SELECTION_PROMPT_VERSION,
    CONDITIONS,
    MIXED_CONDITIONS,
    PROVISIONAL_HYPOTHESIS_FIELDS,
    SIGNED_CONDITIONS,
    build_c_only_evidence,
    build_condition_candidate,
    build_w_only_evidence,
    extract_w_materials,
    find_correct_rows,
    generate_provisional_hypothesis,
    generate_candidate_feedbacks_with_positive_cases,
    index_w_materials,
    select_minimum_norm_feedback,
    update_agent_prompt,
)

from examples.ours.adapter import HotpotAdapter
from examples.ours.metric import answer_exact_match
from examples.ours.program import HotpotMultiHop
from examples.ours.retriever import (
    DEFAULT_RETRIEVER_DIR,
    set_retriever_dir,
)


SCRIPT_VERSION = "2026-07-16-v14-semantic-min-norm-feedback"

DEFAULT_EVAL_ROWS = (
    "examples/ours/runs/"
    "gpt5mini_agentgrad_best_test150/eval_rows.json"
)
DEFAULT_ATTRIBUTE_ROWS = (
    "examples/ours/runs/"
    "gpt5mini_agentgrad_best_test150/"
    "backward_attribution_agent_iters/attribute_rows.jsonl"
)
DEFAULT_RUN_DIR = (
    "examples/ours/runs/"
    "gpt5mini_agentgrad_best_test150/prompt_update_v2"
)
DEFAULT_CACHE_DIR = "examples/ours/cache/prompt_update_v2"
DEFAULT_ENV_FILE = "/home/jinwoo/gepa-official/.env"


BATCH_SELECTIONS = (
    "random",
    "min_distance",
)

DEFAULT_AGENT_BATCH_SIZE = 5
DEFAULT_NUM_FEEDBACK_CANDIDATES = 4

DISTANCE_PROMPT_KEYS = {
    "final": "feedback_distance_1n_final_v0",
    "summary2": "feedback_distance_1n_summary2_v0",
    "query": "feedback_distance_1n_query_v0",
    "summary1": "feedback_distance_1n_summary1_v0",
}



# ---------------------------------------------------------------------------
# JSON / identity helpers
# ---------------------------------------------------------------------------


def _json_dumps(value: Any, *, indent: int | None = 2) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=indent,
        default=str,
        sort_keys=False,
    )


def _progress(message: str, **fields: Any) -> None:
    suffix = "" if not fields else " | " + " ".join(f"{k}={v}" for k, v in fields.items())
    print(f"[update_prompt] {message}{suffix}", flush=True)


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def write_json(path: str | Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _json_dumps(value),
        encoding="utf-8",
    )


def append_jsonl(
    path: str | Path,
    row: Mapping[str, Any],
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(
            _json_dumps(dict(row), indent=None)
            + "\n"
        )


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()





def resolve_agent_batch_manifest(
    *,
    manifest: Mapping[str, Any],
    w_by_sample_index: Mapping[int, Mapping[str, Any]],
    eval_rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Resolve the W-first agent manifest against current source rows.

    C references are optional because hypothesis-conditioned C selection occurs
    only after the provisional W-only hypothesis has been generated.
    """
    if manifest.get("manifest_type") != "selected_agent_batches_v2_w_first":
        raise ValueError(
            "Expected selected_agent_batches_v2_w_first manifest."
        )

    resolved: dict[str, dict[str, Any]] = {}

    for agent in AGENT_ORDER:
        batch = (
            manifest.get("agent_batches", {})
            .get(agent)
        )
        if batch is None:
            continue

        selected_w = []
        for ref in batch.get("w", []):
            sample_index = int(ref["sample_index"])
            if sample_index not in w_by_sample_index:
                raise KeyError(
                    f"Manifest W sample {sample_index} is unavailable."
                )

            material = dict(w_by_sample_index[sample_index])
            if str(material.get("agent")) != agent:
                raise ValueError(
                    f"W sample {sample_index} belongs to "
                    f"{material.get('agent')}, not {agent}."
                )

            expected_id = str(ref.get("stable_id"))
            actual_id = str(material.get("stable_id"))
            if expected_id != actual_id:
                raise ValueError(
                    "Manifest W stable_id mismatch for "
                    f"sample_index={sample_index}: "
                    f"expected={expected_id!r}, actual={actual_id!r}."
                )
            selected_w.append(material)

        selected_c = []
        for ref in batch.get("c", []):
            position = int(ref["eval_position"])
            if not 0 <= position < len(eval_rows):
                raise IndexError(
                    f"Manifest C eval position is out of range: {position}."
                )
            row = dict(eval_rows[position])
            if float(row.get("score") or 0.0) != 1.0:
                raise ValueError(
                    f"C row at eval position {position} "
                    "is no longer baseline-correct."
                )
            selected_c.append((position, row))

        resolved[agent] = {
            "w": selected_w,
            "c": selected_c,
        }

    return resolved



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


def requested_agent_batch_sizes(
    args: argparse.Namespace,
) -> dict[str, int]:
    return {
        "final": int(args.batch_size_final),
        "summary2": int(args.batch_size_summary2),
        "query": int(args.batch_size_query),
        "summary1": int(args.batch_size_summary1),
    }


def effective_condition_for_selection(
    *,
    condition: str,
    batch_selection: str,
) -> str:
    return condition


def _w_ref(
    row: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "sample_index": int(row["sample_index"]),
        "row_index": row.get("row_index"),
        "stable_id": row.get("stable_id"),
        "agent": str(row["agent"]),
    }


def _distance_material(
    row: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        **_w_ref(row),
        "question": row.get("question"),
        "delta_p_trace": [
            {
                "edge_index": int(
                    delta["edge_index"]
                ),
                "delta_p": dict(delta["delta_p"]),
            }
            for delta in (
                row.get("delta_p_trace") or []
            )
        ],
    }


class SelectNearestDeltaPTraceSignature(Signature):
    input_keys = [
        "agent",
        "anchor_material",
        "candidate_materials",
    ]
    output_keys = [
        "selected_sample_index",
        "shared_update_pattern",
        "rationale",
        "confidence",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        agent = str(input_dict["agent"])
        return get_method_prompt(
            DISTANCE_PROMPT_KEYS[agent]
        ).format(
            agent=agent,
            anchor_json=_json_dumps(
                input_dict["anchor_material"]
            ),
            candidates_json=_json_dumps(
                input_dict["candidate_materials"]
            ),
        )

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        confidence = float(
            obj.get("confidence", 0.0)
        )
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be in [0, 1]."
            )

        return {
            "selected_sample_index": int(
                obj["selected_sample_index"]
            ),
            "shared_update_pattern": str(
                obj.get(
                    "shared_update_pattern",
                    "",
                )
            ).strip(),
            "rationale": str(
                obj.get("rationale", "")
            ).strip(),
            "confidence": confidence,
        }


def select_min_distance_batch(
    *,
    agent: str,
    pool: Sequence[Mapping[str, Any]],
    requested_batch_size: int,
    seed: int,
    runtime: OursRuntime,
    lm: Any,
    lm_config: Mapping[str, Any],
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
]:
    effective_batch_size = min(
        int(requested_batch_size),
        len(pool),
    )
    if effective_batch_size == 0:
        return [], {
            "anchor_sample_index": None,
            "selection_steps": [],
        }

    agent_index = AGENT_ORDER.index(agent)
    rng = random.Random(
        seed + 1009 * (agent_index + 1)
    )
    anchor = dict(rng.choice(list(pool)))
    anchor_index = int(anchor["sample_index"])

    selected = [anchor]
    remaining = [
        dict(row)
        for row in pool
        if int(row["sample_index"])
        != anchor_index
    ]
    steps = []

    while len(selected) < effective_batch_size:
        candidates = sorted(
            (
                _distance_material(row)
                for row in remaining
            ),
            key=lambda row: int(
                row["sample_index"]
            ),
        )
        parsed, _, _, cache_hit = run_signature(
            runtime=runtime,
            operation=(
                "prompt_update."
                f"min_distance.{agent}"
            ),
            lm=lm,
            signature_cls=(
                SelectNearestDeltaPTraceSignature
            ),
            input_dict={
                "agent": agent,
                "anchor_material": (
                    _distance_material(anchor)
                ),
                "candidate_materials": candidates,
            },
            lm_config=lm_config,
            metadata={
                "agent": agent,
                "anchor_sample_index": (
                    anchor_index
                ),
                "candidate_sample_indices": [
                    int(row["sample_index"])
                    for row in candidates
                ],
            },
            return_cache_hit=True,
        )

        selected_index = int(
            parsed["selected_sample_index"]
        )
        allowed = {
            int(row["sample_index"]): row
            for row in remaining
        }
        if selected_index not in allowed:
            raise ValueError(
                "Min-distance selector chose an "
                "unknown sample: "
                f"agent={agent}, "
                f"selected={selected_index}, "
                f"allowed={sorted(allowed)}."
            )

        selected.append(
            dict(allowed[selected_index])
        )
        remaining = [
            row
            for row in remaining
            if int(row["sample_index"])
            != selected_index
        ]
        steps.append({
            "selected_sample_index": (
                selected_index
            ),
            "shared_update_pattern": (
                parsed[
                    "shared_update_pattern"
                ]
            ),
            "rationale": parsed["rationale"],
            "confidence": parsed["confidence"],
            "cache_hit": cache_hit,
        })

    return selected, {
        "anchor_sample_index": anchor_index,
        "selection_steps": steps,
    }


def load_or_create_selected_agent_manifest(
    *,
    path: str | Path,
    w_materials: Sequence[Mapping[str, Any]],
    requested_batch_sizes: Mapping[str, int],
    batch_selection: str,
    seed: int,
    runtime: OursRuntime,
    lm: Any,
    lm_config: Mapping[str, Any],
    overwrite: bool,
) -> dict[str, Any]:
    """Create the W-first manifest used by all non-base conditions.

    Only W rows are selected here. Mixed-condition C rows are selected later,
    after a provisional W-only hypothesis exists for the corresponding agent.
    """
    path = Path(path)

    available_w_by_agent = {
        agent: sum(
            str(row.get("agent")) == agent
            for row in w_materials
        )
        for agent in AGENT_ORDER
    }
    source_pool_hash = canonical_hash(
        sorted(
            (
                _distance_material(row)
                for row in w_materials
            ),
            key=lambda row: int(row["sample_index"]),
        )
    )
    identity = {
        "batch_selection": batch_selection,
        "seed": int(seed),
        "requested_batch_sizes": {
            agent: int(requested_batch_sizes[agent])
            for agent in AGENT_ORDER
        },
        "available_w_by_agent": available_w_by_agent,
        "source_pool_hash": source_pool_hash,
    }

    if path.exists() and not overwrite:
        manifest = read_json(path)
        if (
            manifest.get("manifest_type")
            != "selected_agent_batches_v2_w_first"
        ):
            raise ValueError(
                f"{path} is not a W-first selected-agent manifest. "
                "Use --overwrite-shared or a new run directory."
            )

        actual = {
            key: manifest.get(key)
            for key in identity
        }
        if actual != identity:
            raise ValueError(
                "Existing W-first manifest does not match the current "
                "request/source pool. "
                f"expected={identity}, actual={actual}. "
                "Use --overwrite-shared or a new run directory."
            )
        return dict(manifest)

    selected_by_agent: dict[str, list[dict[str, Any]]] = {}
    selection_metadata: dict[str, dict[str, Any]] = {}

    for agent_index, agent in enumerate(AGENT_ORDER):
        pool = [
            dict(row)
            for row in w_materials
            if str(row.get("agent")) == agent
        ]
        requested = int(requested_batch_sizes[agent])

        if batch_selection == "random":
            random.Random(
                seed + 1009 * (agent_index + 1)
            ).shuffle(pool)
            selected = pool[:min(requested, len(pool))]
            metadata = {
                "anchor_sample_index": None,
                "selection_steps": [],
            }
        else:
            selected, metadata = select_min_distance_batch(
                agent=agent,
                pool=pool,
                requested_batch_size=requested,
                seed=seed,
                runtime=runtime,
                lm=lm,
                lm_config=lm_config,
            )

        selected_by_agent[agent] = selected
        selection_metadata[agent] = metadata

    agent_batches = {}
    for agent in AGENT_ORDER:
        selected_w = selected_by_agent[agent]
        agent_batches[agent] = {
            "requested_batch_size": int(
                requested_batch_sizes[agent]
            ),
            "available_w": int(
                available_w_by_agent[agent]
            ),
            "effective_batch_size": len(selected_w),
            **selection_metadata[agent],
            "w": [_w_ref(row) for row in selected_w],
            "provisional_hypothesis": None,
            "c_selection": None,
            "c": [],
        }

    manifest = {
        "script_version": SCRIPT_VERSION,
        "manifest_type": "selected_agent_batches_v2_w_first",
        "sampling_policy": (
            "agent-specific W selection first; C selected only after "
            "the W-only provisional hypothesis"
        ),
        **identity,
        "effective_batch_sizes": {
            agent: int(
                agent_batches[agent]["effective_batch_size"]
            )
            for agent in AGENT_ORDER
        },
        "agent_batches": agent_batches,
    }
    write_json(path, manifest)
    return manifest


def _upsert_jsonl(
    path: str | Path,
    row: Mapping[str, Any],
    *,
    key_fields: Sequence[str],
) -> None:
    """Replace a same-identity JSONL row, preserving unrelated rows."""
    path = Path(path)
    incoming = dict(row)
    incoming_key = tuple(
        str(incoming.get(field) or "")
        for field in key_fields
    )

    retained = []
    for existing in read_jsonl(path):
        existing_key = tuple(
            str(existing.get(field) or "")
            for field in key_fields
        )
        if existing_key != incoming_key:
            retained.append(existing)
    retained.append(incoming)

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as file:
        for item in retained:
            file.write(_json_dumps(item, indent=None) + "\n")
    tmp_path.replace(path)


def _remove_condition_rows(
    path: str | Path,
    *,
    condition: str,
) -> None:
    path = Path(path)
    if not path.exists():
        return
    retained = [
        row
        for row in read_jsonl(path)
        if str(row.get("condition")) != condition
    ]
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as file:
        for row in retained:
            file.write(_json_dumps(row, indent=None) + "\n")
    tmp_path.replace(path)


def _provisional_manifest_payload(
    row: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "status": row.get("status"),
        **{
            field: row.get(field)
            for field in PROVISIONAL_HYPOTHESIS_FIELDS
        },
        "base_prompt_hash": row.get("base_prompt_hash"),
        "w_evidence_hash": row.get("w_evidence_hash"),
        "provisional_hypothesis_hash": row.get(
            "provisional_hypothesis_hash"
        ),
    }


def update_agent_manifest_after_c_selection(
    *,
    path: str | Path,
    agent: str,
    provisional_hypothesis_row: Mapping[str, Any],
    selection: MatchedCSelection,
) -> dict[str, Any]:
    """Persist hypothesis and matched/fallback C references atomically."""
    path = Path(path)
    manifest = read_json(path)
    if (
        manifest.get("manifest_type")
        != "selected_agent_batches_v2_w_first"
    ):
        raise ValueError(
            "Cannot update a non-W-first agent manifest."
        )
    if agent not in manifest.get("agent_batches", {}):
        raise KeyError(f"Manifest has no agent entry for {agent!r}.")

    selection_manifest = selection.to_manifest()
    entry = manifest["agent_batches"][agent]
    entry["provisional_hypothesis"] = (
        _provisional_manifest_payload(
            provisional_hypothesis_row
        )
    )
    entry["c_selection"] = selection_manifest
    entry["c"] = list(selection_manifest["selected_c"])
    manifest["matched_c_utility_version"] = (
        MATCHED_C_UTIL_VERSION
    )
    manifest["c_selection_policy"] = (
        "hypothesis-conditioned boundary matching with deterministic "
        "preservation fallback"
    )

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(
        _json_dumps(manifest),
        encoding="utf-8",
    )
    tmp_path.replace(path)
    return manifest


def _selection_kind_by_position(
    selection: MatchedCSelection,
) -> dict[int, str]:
    kinds = {
        int(position): "matched_boundary"
        for position, _ in selection.matched_rows
    }
    kinds.update({
        int(position): "fallback_preservation"
        for position, _ in selection.fallback_rows
    })
    return kinds


def _build_hypothesis_matched_candidate(
    *,
    condition: str,
    base_candidate: Mapping[str, str],
    agent_batches: Mapping[str, Mapping[str, Any]],
    correct_rows: Sequence[tuple[int, Mapping[str, Any]]],
    c_per_agent: int,
    seed: int,
    runtime: OursRuntime,
    lm: Any,
    lm_config: Mapping[str, Any],
    base_program: Any,
    program_template: Any,
    runtime_config: Mapping[str, Any],
    manifest_path: Path,
    provisional_path: Path,
    selection_path: Path,
    match_path: Path,
    material_path: Path,
    candidate_feedback_path: Path,
    norm_selection_path: Path,
    feedback_path: Path,
    updater_path: Path,
    candidate_path: Path,
    damage_attempts: int,
    delta_attempts: int,
    max_evidence_chars: int,
    num_feedback_candidates: int,
    overwrite: bool,
) -> tuple[dict[str, str], dict[str, Any]]:
    """Run W hypothesis -> matched C -> multi-delta-p -> min-norm rewrite."""
    if condition not in MIXED_CONDITIONS:
        raise ValueError(
            "Hypothesis-matched candidate construction requires a "
            "mixed condition."
        )

    if overwrite:
        for path in (
            provisional_path,
            selection_path,
            candidate_feedback_path,
            norm_selection_path,
            feedback_path,
            updater_path,
        ):
            _remove_condition_rows(
                path,
                condition=condition,
            )

    candidate = dict(base_candidate)
    validate_candidate(candidate, program=program_template)

    all_w: list[dict[str, Any]] = []
    all_c_rows: list[tuple[int, dict[str, Any]]] = []
    all_c_materials: list[dict[str, Any]] = []
    agent_results: dict[str, dict[str, Any]] = {}

    for agent in AGENT_ORDER:
        batch = agent_batches.get(agent, {"w": []})
        agent_w = [dict(row) for row in batch.get("w", [])]
        prompt_key = AGENT_TO_PROMPT_KEY[agent]
        base_prompt = str(base_candidate[prompt_key]).strip()

        if not agent_w:
            agent_results[agent] = {
                "status": "no_w_base_preserved",
                "W": 0,
                "C": 0,
                "matched_C": 0,
                "fallback_C": 0,
                "hypothesis_decision": None,
            }
            continue

        if len(correct_rows) < c_per_agent:
            raise ValueError(
                f"Agent {agent!r} requires {c_per_agent} correct C rows, "
                f"but only {len(correct_rows)} are available."
            )

        all_w.extend(agent_w)
        w_evidence = build_w_only_evidence(
            condition=condition,
            agent=agent,
            w_materials=agent_w,
        )

        _progress(
            "provisional hypothesis start",
            agent=agent,
            n_w=len(agent_w),
        )
        try:
            provisional = generate_provisional_hypothesis(
                runtime=runtime,
                lm=lm,
                lm_config=lm_config,
                condition=condition,
                agent=agent,
                base_prompt=base_prompt,
                w_evidence=w_evidence,
                max_evidence_chars=max_evidence_chars,
            )

        except RuntimeError as exc:
            _progress(
                "provisional hypothesis failed; base preserved",
                agent=agent,
                error=f"{type(exc).__name__}: {exc}",
            )

            agent_results[agent] = {
                "status": (
                    "provisional_failed_base_preserved"
                ),
                "W": len(agent_w),
                "C": 0,
                "matched_C": 0,
                "fallback_C": 0,
                "hypothesis_decision": None,
                "error": str(exc),
            }
            continue

        _upsert_jsonl(
            provisional_path,
            provisional,
            key_fields=(
                "condition",
                "agent",
                "base_prompt_hash",
                "w_evidence_hash",
            ),
        )

        _progress(
            "matched C selection start",
            agent=agent,
            c_budget=c_per_agent,
            n_correct_pool=len(correct_rows),
        )
        selection = select_matched_c_rows(
            agent=agent,
            provisional_hypothesis=provisional,
            selected_w=agent_w,
            correct_pool=correct_rows,
            k=c_per_agent,
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            seed=seed,
        )
        selection_manifest = selection.to_manifest()
        selection_row = {
            **selection_manifest,
            "script_version": SCRIPT_VERSION,
            "matched_c_utility_version": MATCHED_C_UTIL_VERSION,
            "row_type": "matched_c_selection",
            "condition": condition,
            "agent": agent,
            "lm_traces": selection.lm_traces,
        }
        _upsert_jsonl(
            selection_path,
            selection_row,
            key_fields=(
                "condition",
                "agent",
                "provisional_hypothesis_hash",
                "candidate_pool_hash",
                "requested_k",
            ),
        )
        update_agent_manifest_after_c_selection(
            path=manifest_path,
            agent=agent,
            provisional_hypothesis_row=provisional,
            selection=selection,
        )

        agent_c = [
            (int(position), dict(row))
            for position, row in selection.selected_rows
        ]
        all_c_rows.extend(agent_c)

        _progress(
            "positive material start",
            agent=agent,
            mode=(
                "signed"
                if condition in SIGNED_CONDITIONS
                else "raw_C"
            ),
            n_w=len(agent_w),
            n_c=len(agent_c),
            matched_c=len(selection.matched_rows),
            fallback_c=len(selection.fallback_rows),
        )
        generated = prepare_positive_materials(
            require_signed=(condition in SIGNED_CONDITIONS),
            selected_c_rows=agent_c,
            selected_w_materials=agent_w,
            base_program=base_program,
            base_candidate=base_candidate,
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            match_path=match_path,
            material_path=material_path,
            damage_attempts=damage_attempts,
            delta_attempts=delta_attempts,
            materialization_config=runtime_config,
            overwrite=False,
        )

        selection_kinds = _selection_kind_by_position(selection)
        agent_materials = []
        for source_material in generated:
            material = dict(source_material)
            position = int(material["c_eval_position"])
            if position not in selection_kinds:
                raise ValueError(
                    "Positive material was generated for an unselected C "
                    f"row: agent={agent}, eval_position={position}."
                )
            material["c_selection_kind"] = selection_kinds[position]
            agent_materials.append(material)
        all_c_materials.extend(agent_materials)

        c_evidence = build_c_only_evidence(
            condition=condition,
            agent=agent,
            c_materials=agent_materials,
        )
        for evidence in c_evidence:
            position = int(evidence["c_eval_position"])
            evidence["c_selection_kind"] = selection_kinds[position]

        if not c_evidence:
            raise RuntimeError(
                f"No C evidence was materialized for mixed agent {agent!r}."
            )

        _progress(
            "feedback candidate generation start",
            agent=agent,
            num_candidates=num_feedback_candidates,
        )
        candidate_feedback_set = (
            generate_candidate_feedbacks_with_positive_cases(
                runtime=runtime,
                lm=lm,
                lm_config=lm_config,
                condition=condition,
                agent=agent,
                base_prompt=base_prompt,
                provisional_hypothesis_row=provisional,
                w_evidence=w_evidence,
                c_evidence=c_evidence,
                max_evidence_chars=max_evidence_chars,
                num_candidates=num_feedback_candidates,
            )
        )
        candidate_feedback_set.update({
            "matched_c_count": len(selection.matched_rows),
            "fallback_c_count": len(selection.fallback_rows),
            "c_selection_rationale": selection.rationale,
            "c_coverage_assessment": selection.coverage_assessment,
        })
        _upsert_jsonl(
            candidate_feedback_path,
            candidate_feedback_set,
            key_fields=(
                "condition",
                "agent",
                "base_prompt_hash",
                "evidence_hash",
                "requested_num_candidates",
            ),
        )

        _progress(
            "minimum semantic norm selection start",
            agent=agent,
            num_candidates=candidate_feedback_set.get(
                "num_candidates",
                0,
            ),
            no_admissible_update=candidate_feedback_set.get(
                "no_admissible_update",
                False,
            ),
        )
        selected_feedback = select_minimum_norm_feedback(
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            condition=condition,
            agent=agent,
            base_prompt=base_prompt,
            candidate_feedback_set_row=candidate_feedback_set,
        )
        selected_feedback.update({
            "matched_c_count": len(selection.matched_rows),
            "fallback_c_count": len(selection.fallback_rows),
            "c_selection_rationale": selection.rationale,
            "c_coverage_assessment": selection.coverage_assessment,
        })

        norm_selection_row = {
            "script_version": SCRIPT_VERSION,
            "row_type": "feedback_norm_selection",
            "condition": condition,
            "agent": agent,
            "status": selected_feedback.get("status"),
            "base_prompt_hash": selected_feedback.get(
                "base_prompt_hash"
            ),
            "evidence_hash": selected_feedback.get("evidence_hash"),
            "candidate_feedback_set_hash": selected_feedback.get(
                "candidate_feedback_set_hash"
            ),
            "num_feedback_candidates": selected_feedback.get(
                "num_feedback_candidates",
                0,
            ),
            "selected_candidate_index": selected_feedback.get(
                "selected_candidate_index"
            ),
            "feedback_norm_selection": selected_feedback.get(
                "feedback_norm_selection"
            ),
            "lm_trace": selected_feedback.get("lm_trace"),
        }
        _upsert_jsonl(
            norm_selection_path,
            norm_selection_row,
            key_fields=(
                "condition",
                "agent",
                "base_prompt_hash",
                "evidence_hash",
                "candidate_feedback_set_hash",
            ),
        )
        _upsert_jsonl(
            feedback_path,
            selected_feedback,
            key_fields=(
                "condition",
                "agent",
                "base_prompt_hash",
                "evidence_hash",
            ),
        )

        updater_row = update_agent_prompt(
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            condition=condition,
            agent=agent,
            base_prompt=base_prompt,
            integrated_feedback_row=selected_feedback,
        )
        _upsert_jsonl(
            updater_path,
            updater_row,
            key_fields=(
                "condition",
                "agent",
                "base_prompt_hash",
                "integrated_feedback_hash",
            ),
        )

        candidate[prompt_key] = str(
            updater_row["updated_prompt"]
        ).strip()
        agent_results[agent] = {
            "status": updater_row.get("status"),
            "W": len(agent_w),
            "C": len(agent_c),
            "matched_C": len(selection.matched_rows),
            "fallback_C": len(selection.fallback_rows),
            "hypothesis_decision": selected_feedback.get(
                "hypothesis_decision"
            ),
            "provisional_hypothesis_hash": provisional.get(
                "provisional_hypothesis_hash"
            ),
            "evidence_hash": selected_feedback.get("evidence_hash"),
            "candidate_feedback_set_hash": candidate_feedback_set.get(
                "candidate_feedback_set_hash"
            ),
            "num_feedback_candidates": candidate_feedback_set.get(
                "num_candidates",
                0,
            ),
            "selected_candidate_index": selected_feedback.get(
                "selected_candidate_index"
            ),
            "feedback_norm_selection": selected_feedback.get(
                "feedback_norm_selection"
            ),
            "integrated_feedback_hash": updater_row.get(
                "integrated_feedback_hash"
            ),
        }
        _progress(
            "agent update complete",
            agent=agent,
            decision=selected_feedback.get("hypothesis_decision"),
            status=updater_row.get("status"),
        )

    validate_candidate(candidate, program=program_template)
    save_prompt_candidate(
        candidate_path,
        name=condition,
        candidate=candidate,
        description=(
            "Four-agent candidate produced by W-only provisional "
            "hypotheses, hypothesis-conditioned matched positive cases, "
            "multiple admissible delta-p feedback candidates, "
            "agent-specific minimum semantic norm selection, and prompt "
            "rewrite."
        ),
        program=program_template,
    )

    return candidate, {
        "mixed_w": all_w,
        "mixed_c": all_c_rows,
        "c_materials": all_c_materials,
        "agent_results": agent_results,
    }



# ---------------------------------------------------------------------------
# Runtime setup
# ---------------------------------------------------------------------------


def make_dspy_lm(
    *,
    model: str,
    api_base: str | None,
    api_key: str,
    temperature: float,
    max_tokens: int,
):
    kwargs: dict[str, Any] = {
        "api_key": api_key,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if api_base:
        kwargs["api_base"] = api_base

    return dspy.LM(model, **kwargs)


def requested_num_feedback_candidates(
    args: argparse.Namespace,
) -> int:
    return int(
        getattr(
            args,
            "num_feedback_candidates",
            DEFAULT_NUM_FEEDBACK_CANDIDATES,
        )
    )


def validate_cli_args(args: argparse.Namespace) -> None:
    if args.condition not in CONDITIONS:
        raise ValueError(
            f"Unknown condition: {args.condition!r}."
        )

    if args.batch_selection not in BATCH_SELECTIONS:
        raise ValueError(
            "Unknown --batch-selection: "
            f"{args.batch_selection!r}."
        )

    if args.condition != "base":
        for agent, batch_size in (
            requested_agent_batch_sizes(args)
            .items()
        ):
            if batch_size < 1:
                raise ValueError(
                    f"--batch-size-{agent} must "
                    "be at least 1."
                )

    if args.c_per_agent < 1:
        raise ValueError(
            "--c-per-agent must be >= 1."
        )

    if requested_num_feedback_candidates(args) < 2:
        raise ValueError(
            "--num-feedback-candidates must be >= 2."
        )

    if args.delta_attempts < 1:
        raise ValueError("--delta-attempts must be >= 1.")
    if args.damage_attempts < 1:
        raise ValueError("--damage-attempts must be >= 1.")
    if args.max_evidence_chars < 1:
        raise ValueError(
            "--max-evidence-chars must be >= 1."
        )
    if args.num_threads < 1:
        raise ValueError("--num-threads must be >= 1.")
    if (
        args.limit_eval is not None
        and args.limit_eval < 0
    ):
        raise ValueError(
            "--limit-eval must be non-negative."
        )

    normalized_model = str(args.model).lower()
    if (
        "gpt-5" in normalized_model
        and args.max_tokens < 16000
    ):
        raise ValueError(
            "GPT-5-family DSPy runs require "
            "--max-tokens >= 16000 in this project."
        )


def setup_runtime(
    args: argparse.Namespace,
    base_candidate: Mapping[str, str],
) -> tuple[
    OursRuntime,
    Any,
    dict[str, Any],
    HotpotMultiHop,
    HotpotAdapter,
    Any,
    dict[str, Any],
]:
    load_dotenv(args.env_file)
    api_key = os.environ.get(
        "OPENAI_API_KEY",
        "",
    ).strip()
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is missing after loading "
            f"{args.env_file}."
        )

    lm = make_dspy_lm(
        model=args.model,
        api_base=args.api_base,
        api_key=api_key,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    dspy.configure(lm=lm)

    lm_config = {
        "model": args.model,
        "api_base": args.api_base,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }

    set_retriever_dir(args.retriever_dir)
    program_template = HotpotMultiHop(
        k=args.k,
        retriever_dir=args.retriever_dir,
    )

    runtime_config = {
        "task_model": args.model,
        "task_api_base": args.api_base,
        "task_temperature": args.temperature,
        "task_max_tokens": args.max_tokens,
        "retriever_dir": str(args.retriever_dir),
        "k": args.k,
    }
    adapter = HotpotAdapter(
        program=program_template,
        metric_fn=answer_exact_match,
        runtime_config=runtime_config,
    )

    validate_candidate(
        base_candidate,
        program=program_template,
    )
    base_program = adapter.build_program(
        base_candidate
    )

    runtime = OursRuntime(
        cache_dir=args.cache_dir,
        cache_enabled=not args.no_cache,
    )

    return (
        runtime,
        lm,
        lm_config,
        program_template,
        adapter,
        base_program,
        runtime_config,
    )


# ---------------------------------------------------------------------------
# End-to-end evaluation
# ---------------------------------------------------------------------------


def make_eval_example(
    row: Mapping[str, Any],
    position: int,
) -> dict[str, Any]:
    gold_answer = row.get("gold_answer")
    if gold_answer is None:
        raise ValueError(
            "Evaluation row is missing gold_answer at "
            f"position {position}."
        )

    question = str(
        row.get("question") or ""
    ).strip()
    if not question:
        raise ValueError(
            "Evaluation row has an empty question at "
            f"position {position}."
        )

    return {
        "_id": row.get(
            "sample_id",
            row.get("index", position),
        ),
        "question": question,
        # HotpotAdapter treats `answer` as the gold answer.
        "answer": gold_answer,
        "context": row.get("context"),
        "supporting_facts": row.get(
            "supporting_facts"
        ),
    }


def evaluation_fingerprint(
    *,
    condition: str,
    candidate_hash: str,
    example: Mapping[str, Any],
    runtime_config: Mapping[str, Any],
) -> tuple[str, str, str]:
    example_hash = canonical_hash(example)
    runtime_config_hash = canonical_hash(
        runtime_config
    )
    fingerprint = canonical_hash({
        "script_version": SCRIPT_VERSION,
        "condition": condition,
        "candidate_hash": candidate_hash,
        "example_hash": example_hash,
        "runtime_config_hash": runtime_config_hash,
    })
    return (
        fingerprint,
        example_hash,
        runtime_config_hash,
    )


def _eval_one(
    *,
    runtime: OursRuntime,
    adapter: HotpotAdapter,
    condition: str,
    candidate: Mapping[str, str],
    candidate_hash: str,
    runtime_config: Mapping[str, Any],
    position: int,
    row: Mapping[str, Any],
) -> dict[str, Any]:
    example = make_eval_example(row, position)
    (
        eval_fingerprint,
        example_hash,
        runtime_config_hash,
    ) = evaluation_fingerprint(
        condition=condition,
        candidate_hash=candidate_hash,
        example=example,
        runtime_config=runtime_config,
    )

    trace, cache_hit = runtime.forward(
        adapter=adapter,
        example=example,
        candidate=dict(candidate),
        return_cache_hit=True,
    )

    return {
        "row_type": "prompt_update_evaluation",
        "script_version": SCRIPT_VERSION,
        "condition": condition,
        "candidate_hash": candidate_hash,
        "eval_fingerprint": eval_fingerprint,
        "example_hash": example_hash,
        "runtime_config_hash": (
            runtime_config_hash
        ),
        "eval_position": int(position),
        "row_index": row.get(
            "index",
            position,
        ),
        "sample_id": row.get("sample_id"),
        "original_baseline_score": float(
            row.get("score") or 0.0
        ),
        "trace": trace,
        "score": float(trace["score"]),
        "cache_hit": cache_hit,
    }


def evaluate_condition(
    *,
    runtime: OursRuntime,
    adapter: HotpotAdapter,
    runtime_config: Mapping[str, Any],
    condition: str,
    candidate: Mapping[str, str],
    eval_rows: Sequence[Mapping[str, Any]],
    eval_path: str | Path,
    num_threads: int,
    limit_eval: int | None,
    overwrite: bool,
) -> list[dict[str, Any]]:
    eval_path = Path(eval_path)
    if overwrite and eval_path.exists():
        eval_path.unlink()

    candidate_hash = canonical_hash(
        dict(candidate)
    )
    positions = list(range(len(eval_rows)))
    if limit_eval is not None:
        positions = positions[:limit_eval]

    requested: dict[int, dict[str, str]] = {}
    for position in positions:
        example = make_eval_example(
            eval_rows[position],
            position,
        )
        (
            fingerprint,
            example_hash,
            runtime_config_hash,
        ) = evaluation_fingerprint(
            condition=condition,
            candidate_hash=candidate_hash,
            example=example,
            runtime_config=runtime_config,
        )
        requested[position] = {
            "eval_fingerprint": fingerprint,
            "example_hash": example_hash,
            "runtime_config_hash": (
                runtime_config_hash
            ),
        }

    existing = read_jsonl(eval_path)
    successful_by_fingerprint = {
        str(row["eval_fingerprint"]): row
        for row in existing
        if not row.get("error")
        and row.get("eval_fingerprint")
    }

    tasks = [
        position
        for position in positions
        if requested[position]["eval_fingerprint"]
        not in successful_by_fingerprint
    ]

    def run(position: int) -> dict[str, Any]:
        row = eval_rows[position]
        metadata = requested[position]

        try:
            return _eval_one(
                runtime=runtime,
                adapter=adapter,
                condition=condition,
                candidate=candidate,
                candidate_hash=candidate_hash,
                runtime_config=runtime_config,
                position=position,
                row=row,
            )
        except Exception as exc:
            return {
                "row_type": (
                    "prompt_update_evaluation"
                ),
                "script_version": SCRIPT_VERSION,
                "condition": condition,
                "candidate_hash": candidate_hash,
                "eval_fingerprint": metadata[
                    "eval_fingerprint"
                ],
                "example_hash": metadata[
                    "example_hash"
                ],
                "runtime_config_hash": metadata[
                    "runtime_config_hash"
                ],
                "eval_position": int(position),
                "row_index": row.get(
                    "index",
                    position,
                ),
                "sample_id": row.get("sample_id"),
                "error": True,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "traceback": traceback.format_exc(),
            }

    if num_threads <= 1:
        iterator = (run(position) for position in tasks)
        for result in tqdm(
            iterator,
            total=len(tasks),
            desc=f"Evaluate {condition}",
        ):
            append_jsonl(eval_path, result)
    else:
        with cf.ThreadPoolExecutor(
            max_workers=num_threads
        ) as executor:
            futures = [
                executor.submit(run, position)
                for position in tasks
            ]
            for future in tqdm(
                cf.as_completed(futures),
                total=len(futures),
                desc=f"Evaluate {condition}",
            ):
                append_jsonl(
                    eval_path,
                    future.result(),
                )

    final_rows = read_jsonl(eval_path)
    latest_success = {
        str(row["eval_fingerprint"]): row
        for row in final_rows
        if not row.get("error")
        and row.get("eval_fingerprint")
    }

    return [
        dict(latest_success[
            requested[position]["eval_fingerprint"]
        ])
        for position in positions
        if requested[position]["eval_fingerprint"]
        in latest_success
    ]


def mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _optional_mean(
    values: Sequence[Any],
) -> float | None:
    numeric = [
        float(value)
        for value in values
        if value is not None
    ]
    if not numeric:
        return None
    return mean(numeric)


def _load_base_reference(
    *,
    run_dir: Path,
    current_rows: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    base_path = (
        run_dir
        / "conditions"
        / "base"
        / "eval_rows.jsonl"
    )
    if not base_path.exists():
        return {}

    current_identity = {
        (
            int(row["eval_position"]),
            str(row["example_hash"]),
            str(row["runtime_config_hash"]),
        )
        for row in current_rows
    }

    selected: dict[int, Mapping[str, Any]] = {}
    for row in read_jsonl(base_path):
        if row.get("error"):
            continue

        key = (
            int(row.get("eval_position", -1)),
            str(row.get("example_hash") or ""),
            str(
                row.get("runtime_config_hash")
                or ""
            ),
        )
        if key not in current_identity:
            continue
        selected[key[0]] = row

    return selected


def build_eval_summary(
    *,
    condition: str,
    rows: Sequence[Mapping[str, Any]],
    expected_examples: int,
    run_dir: Path,
) -> dict[str, Any]:
    condition_rows = sorted(
        (
            row
            for row in rows
            if not row.get("error")
        ),
        key=lambda row: int(
            row["eval_position"]
        ),
    )
    scores = [
        float(row["score"])
        for row in condition_rows
    ]

    traces = [
        row.get("trace") or {}
        for row in condition_rows
    ]
    base_by_position = (
        {
            int(row["eval_position"]): row
            for row in condition_rows
        }
        if condition == "base"
        else _load_base_reference(
            run_dir=run_dir,
            current_rows=condition_rows,
        )
    )

    flips = {
        "W_to_R": 0,
        "R_to_W": 0,
        "stable_R": 0,
        "stable_W": 0,
    }
    paired = 0

    for row in condition_rows:
        position = int(row["eval_position"])
        base_row = base_by_position.get(position)
        if base_row is None:
            continue

        paired += 1
        base_correct = (
            float(base_row["score"]) == 1.0
        )
        current_correct = (
            float(row["score"]) == 1.0
        )

        if not base_correct and current_correct:
            flips["W_to_R"] += 1
        elif base_correct and not current_correct:
            flips["R_to_W"] += 1
        elif base_correct and current_correct:
            flips["stable_R"] += 1
        else:
            flips["stable_W"] += 1

    return {
        "script_version": SCRIPT_VERSION,
        "condition": condition,
        "n_ok": len(condition_rows),
        "n_expected": expected_examples,
        "complete": (
            len(condition_rows)
            == expected_examples
        ),
        "score": mean(scores),
        "num_correct": int(sum(scores)),
        "mean_support_recall_hop1": (
            _optional_mean([
                trace.get("support_recall_hop1")
                for trace in traces
            ])
        ),
        "mean_support_recall_hop2": (
            _optional_mean([
                trace.get("support_recall_hop2")
                for trace in traces
            ])
        ),
        "mean_support_recall_total": (
            _optional_mean([
                trace.get("support_recall_total")
                for trace in traces
            ])
        ),
        "mean_missing_recovery_rate": (
            _optional_mean([
                trace.get("missing_recovery_rate")
                for trace in traces
            ])
        ),
        "base_reference_available": bool(
            base_by_position
        ),
        "paired_with_base": paired,
        **flips,
        "net_flip": (
            flips["W_to_R"]
            - flips["R_to_W"]
        ),
    }


# ---------------------------------------------------------------------------
# Pipeline orchestration
# ---------------------------------------------------------------------------


def run_update_pipeline(
    args: argparse.Namespace,
    *,
    entrypoint_path: str | Path | None = None,
) -> dict[str, Any]:
    validate_cli_args(args)

    requested_batch_sizes = requested_agent_batch_sizes(args)
    num_feedback_candidates = (
        requested_num_feedback_candidates(args)
    )
    effective_condition = effective_condition_for_selection(
        condition=args.condition,
        batch_selection=args.batch_selection,
    )
    custom_materials_enabled = (
        effective_condition in MIXED_CONDITIONS
    )

    _progress(
        "start",
        condition=args.condition,
        effective_condition=effective_condition,
        batch_selection=args.batch_selection,
        batch_sizes=requested_batch_sizes,
        num_feedback_candidates=num_feedback_candidates,
        run_dir=args.run_dir,
        seed=args.seed,
    )

    run_dir = Path(args.run_dir)
    condition_dir = run_dir / "conditions" / args.condition
    if args.overwrite and condition_dir.exists():
        shutil.rmtree(condition_dir)

    run_dir.mkdir(parents=True, exist_ok=True)
    condition_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = run_dir / "agent_batch_manifest.json"
    provisional_path = (
        run_dir / "provisional_hypothesis_rows.jsonl"
    )
    selection_path = (
        run_dir / "matched_c_selection_rows.jsonl"
    )
    match_path = run_dir / "positive_matches.jsonl"
    material_path = run_dir / "positive_materials.jsonl"
    candidate_feedback_path = (
        run_dir / "candidate_feedback_rows.jsonl"
    )
    norm_selection_path = (
        run_dir / "feedback_norm_selection_rows.jsonl"
    )
    updater_path = run_dir / "updater_rows.jsonl"
    feedback_path = run_dir / "integrated_feedback_rows.jsonl"

    candidate_path = condition_dir / "candidate.json"
    eval_path = condition_dir / "eval_rows.jsonl"
    summary_path = condition_dir / "summary.json"
    config_path = condition_dir / "config.json"

    if args.base_candidate_path:
        base_candidate, base_candidate_name = load_candidate_file(
            args.base_candidate_path
        )
        base_candidate_path = str(Path(args.base_candidate_path))
    else:
        base_candidate = dict(BASELINE_PROMPT_SET["prompts"])
        base_candidate_name = BASELINE_PROMPT_SET["name"]
        base_candidate_path = None

    base_candidate_hash = canonical_hash(base_candidate)
    eval_rows = normalize_eval_rows(
        eval_rows_path=args.eval_rows,
        source_eval_rows_path=args.source_eval_rows,
        expected_candidate_hash=(
            base_candidate_hash
            if args.base_candidate_path
            else None
        ),
    )
    if not eval_rows:
        raise ValueError("No usable evaluation rows were loaded.")

    _progress(
        "base candidate ready",
        name=base_candidate_name,
        candidate_hash=base_candidate_hash[:12],
        candidate_path=base_candidate_path or "builtin",
        n_eval_rows=len(eval_rows),
    )

    (
        runtime,
        lm,
        lm_config,
        program_template,
        adapter,
        base_program,
        runtime_config,
    ) = setup_runtime(args, base_candidate)
    _progress(
        "runtime ready",
        model=args.model,
        retriever_dir=args.retriever_dir,
        k=args.k,
        cache_enabled=not args.no_cache,
    )

    neg_w: list[dict[str, Any]] = []
    mixed_w: list[dict[str, Any]] = []
    mixed_c: list[tuple[int, dict[str, Any]]] = []
    c_materials: list[dict[str, Any]] = []
    agent_update_results: dict[str, dict[str, Any]] = {}
    agent_batch_counts: dict[str, dict[str, int]] = {}
    available_w_by_agent: dict[str, int] = {}
    effective_batch_sizes: dict[str, int] = {}
    attribute_source_candidate_hash: str | None = None
    available_w_count: int | None = None
    correct_rows: list[tuple[int, Mapping[str, Any]]] = []
    agent_batches: dict[str, dict[str, Any]] = {}

    if args.condition != "base":
        _progress(
            "loading existing attribution rows",
            path=args.attribute_rows,
        )
        attribute_rows = read_jsonl(args.attribute_rows)
        if not attribute_rows:
            raise ValueError(
                "No attribute rows were loaded from "
                f"{args.attribute_rows}."
            )

        attribute_hashes = {
            str(source_hash)
            for row in attribute_rows
            for source_hash in [
                row.get("source_candidate_hash")
                or row.get("candidate_hash")
            ]
            if source_hash
        }
        if len(attribute_hashes) == 1:
            attribute_source_candidate_hash = next(
                iter(attribute_hashes)
            )

        if args.base_candidate_path:
            if len(attribute_hashes) != 1:
                raise ValueError(
                    "Explicit iterative updates require exactly one "
                    "source_candidate_hash in the attribution rows. "
                    f"Found: {sorted(attribute_hashes)}"
                )
            if attribute_source_candidate_hash != base_candidate_hash:
                raise ValueError(
                    "Attribution source candidate does not match "
                    "--base-candidate-path. "
                    f"attribute={attribute_source_candidate_hash} "
                    f"base={base_candidate_hash}"
                )

        w_materials = extract_w_materials(attribute_rows)
        w_by_sample_index = index_w_materials(w_materials)
        available_w_count = len(w_materials)
        correct_rows = find_correct_rows(eval_rows)
        _progress(
            "source pools ready",
            n_attribute_rows=len(attribute_rows),
            n_w_materials=len(w_materials),
            n_correct_rows=len(correct_rows),
        )

        manifest = load_or_create_selected_agent_manifest(
            path=manifest_path,
            w_materials=w_materials,
            requested_batch_sizes=requested_batch_sizes,
            batch_selection=args.batch_selection,
            seed=args.seed,
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            overwrite=args.overwrite_shared,
        )
        agent_batches = resolve_agent_batch_manifest(
            manifest=manifest,
            w_by_sample_index=w_by_sample_index,
            eval_rows=eval_rows,
        )
        available_w_by_agent = {
            agent: int(manifest["available_w_by_agent"][agent])
            for agent in AGENT_ORDER
        }
        effective_batch_sizes = {
            agent: int(manifest["effective_batch_sizes"][agent])
            for agent in AGENT_ORDER
        }
        agent_batch_counts = {
            agent: {
                "W": len(agent_batches.get(agent, {}).get("w", [])),
                "C": 0,
                "matched_C": 0,
                "fallback_C": 0,
            }
            for agent in AGENT_ORDER
        }
        _progress(
            "W-first agent batches resolved",
            batch_selection=args.batch_selection,
            counts=agent_batch_counts,
        )

        if args.overwrite_shared:
            for shared_path in (match_path, material_path):
                if shared_path.exists():
                    shared_path.unlink()

    _progress(
        "candidate update start",
        condition=args.condition,
        effective_condition=effective_condition,
    )

    if custom_materials_enabled:
        candidate, mixed_result = _build_hypothesis_matched_candidate(
            condition=effective_condition,
            base_candidate=base_candidate,
            agent_batches=agent_batches,
            correct_rows=correct_rows,
            c_per_agent=args.c_per_agent,
            seed=args.seed,
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            base_program=base_program,
            program_template=program_template,
            runtime_config=runtime_config,
            manifest_path=manifest_path,
            provisional_path=provisional_path,
            selection_path=selection_path,
            match_path=match_path,
            material_path=material_path,
            candidate_feedback_path=candidate_feedback_path,
            norm_selection_path=norm_selection_path,
            feedback_path=feedback_path,
            updater_path=updater_path,
            candidate_path=candidate_path,
            damage_attempts=args.damage_attempts,
            delta_attempts=args.delta_attempts,
            max_evidence_chars=args.max_evidence_chars,
            num_feedback_candidates=num_feedback_candidates,
            overwrite=args.overwrite,
        )
        mixed_w = list(mixed_result["mixed_w"])
        mixed_c = list(mixed_result["mixed_c"])
        c_materials = list(mixed_result["c_materials"])
        agent_update_results = dict(
            mixed_result["agent_results"]
        )
        for agent in AGENT_ORDER:
            result = agent_update_results.get(agent, {})
            agent_batch_counts[agent] = {
                "W": int(result.get("W", 0)),
                "C": int(result.get("C", 0)),
                "matched_C": int(result.get("matched_C", 0)),
                "fallback_C": int(result.get("fallback_C", 0)),
            }
    else:
        if args.condition != "base":
            neg_w = [
                dict(row)
                for agent in AGENT_ORDER
                for row in agent_batches.get(agent, {"w": []})["w"]
            ]
        candidate = build_condition_candidate(
            condition=effective_condition,
            base_candidate=base_candidate,
            neg_w=neg_w,
            mixed_w=[],
            c_materials=[],
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            updater_path=updater_path,
            feedback_path=feedback_path,
            candidate_path=candidate_path,
            max_evidence_chars=args.max_evidence_chars,
            overwrite=args.overwrite,
            program=program_template,
        )

    _progress(
        "candidate update complete",
        candidate=candidate_path,
        candidate_hash=canonical_hash(candidate)[:12],
    )

    config = {
        "script": str(Path(entrypoint_path or __file__).resolve()),
        "pipeline_module": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "prompt_utility_version": PROMPT_UTIL_VERSION,
        "positive_utility_version": POSITIVE_UTIL_VERSION,
        "matched_c_utility_version": MATCHED_C_UTIL_VERSION,
        "feedback_candidate_generation_prompt_version": (
            FEEDBACK_CANDIDATE_GENERATION_PROMPT_VERSION
        ),
        "feedback_norm_selection_prompt_version": (
            FEEDBACK_NORM_SELECTION_PROMPT_VERSION
        ),
        "condition": args.condition,
        "effective_condition": effective_condition,
        "batch_selection": args.batch_selection,
        "eval_rows": str(args.eval_rows),
        "source_eval_rows": (
            str(args.source_eval_rows)
            if args.source_eval_rows
            else None
        ),
        "attribute_rows": (
            str(args.attribute_rows)
            if args.condition != "base"
            else None
        ),
        "run_dir": str(run_dir),
        "condition_dir": str(condition_dir),
        "candidate_path": str(candidate_path),
        "batch_manifest": (
            str(manifest_path)
            if args.condition != "base"
            else None
        ),
        "provisional_hypothesis_rows": (
            str(provisional_path)
            if custom_materials_enabled
            else None
        ),
        "matched_c_selection_rows": (
            str(selection_path)
            if custom_materials_enabled
            else None
        ),
        "positive_matches": (
            str(match_path)
            if custom_materials_enabled
            else None
        ),
        "positive_materials": (
            str(material_path)
            if custom_materials_enabled
            else None
        ),
        "candidate_feedback_rows": (
            str(candidate_feedback_path)
            if custom_materials_enabled
            else None
        ),
        "feedback_norm_selection_rows": (
            str(norm_selection_path)
            if custom_materials_enabled
            else None
        ),
        "updater_rows": str(updater_path),
        "integrated_feedback_rows": str(feedback_path),
        "base_candidate_name": base_candidate_name,
        "base_candidate_path": base_candidate_path,
        "base_candidate_hash": base_candidate_hash,
        "attribute_source_candidate_hash": (
            attribute_source_candidate_hash
        ),
        "candidate_hash": canonical_hash(candidate),
        "batch_sizes_requested": requested_batch_sizes,
        "batch_sizes_effective": effective_batch_sizes,
        "available_w_materials": available_w_count,
        "available_w_by_agent": available_w_by_agent,
        "agent_batch_counts": agent_batch_counts,
        "agent_update_results": agent_update_results,
        "custom_materials_enabled": custom_materials_enabled,
        "c_per_agent": args.c_per_agent,
        "num_feedback_candidates": num_feedback_candidates,
        "feedback_selection": (
            "agent_specific_semantic_min_norm_1n"
            if custom_materials_enabled
            else None
        ),
        "seed": args.seed,
        "delta_attempts": args.delta_attempts,
        "damage_attempts": args.damage_attempts,
        "max_evidence_chars": args.max_evidence_chars,
        "model": lm_config,
        "runtime_config": runtime_config,
        "cache_dir": str(args.cache_dir),
        "cache_enabled": not args.no_cache,
        "overwrite_condition": args.overwrite,
        "overwrite_shared": args.overwrite_shared,
        "contract": {
            "one_condition_per_run": True,
            "w_delta_p_regenerated": False,
            "w_complete_ordered_trace_preserved": True,
            "individual_w_edges_claimed_atomic": False,
            "w_selected_before_c": True,
            "provisional_hypothesis_uses_w_only": True,
            "c_selected_after_provisional_hypothesis": (
                custom_materials_enabled
            ),
            "c_selection_is_hypothesis_conditioned": (
                custom_materials_enabled
            ),
            "matched_and_fallback_c_are_distinguished": (
                custom_materials_enabled
            ),
            "fallback_c_is_deterministic": (
                custom_materials_enabled
            ),
            "c_selection_is_independent_across_agents": True,
            "c_damage_materialized_through_program": (
                custom_materials_enabled
            ),
            "c_answer_flip_required": False,
            "feedback_candidates_generated_before_rewrite": (
                custom_materials_enabled
            ),
            "feedback_candidates_are_non_noop": (
                custom_materials_enabled
            ),
            "feedback_candidate_count_fixed_per_agent": (
                custom_materials_enabled
            ),
            "feedback_norm_is_order_based_not_scalar": (
                custom_materials_enabled
            ),
            "feedback_norm_selection_is_agent_specific": (
                custom_materials_enabled
            ),
            "feedback_norm_selector_does_not_judge_correctness": (
                custom_materials_enabled
            ),
            "no_admissible_update_preserves_base_prompt": True,
            "selected_feedback_only_reaches_rewrite": (
                custom_materials_enabled
            ),
            "counterexample_revision_decisions": [
                "retain",
                "narrow",
                "replace",
                "reject",
            ],
            "reject_preserves_base_prompt": True,
            "agent_specific_batch_sizes": True,
            "c_budget_decoupled_from_w_count": True,
            "c_assigned_only_when_agent_has_w": True,
            "agent_batches_are_independent": True,
            "prompt_rewrite_sees_raw_batch_evidence": False,
            "min_distance_anchor_is_fixed": True,
            "endpoint_delta_includes_delta_p": True,
            "eval_uses_gold_answer_field": True,
            "iterative_base_candidate_supported": True,
            "attribute_candidate_hash_verified": bool(
                args.base_candidate_path
            ),
            "agent_batch_sizes_are_upper_bounds": True,
        },
    }
    write_json(config_path, config)

    if args.skip_eval:
        return {
            "status": "candidate_generated",
            "condition": args.condition,
            "effective_condition": effective_condition,
            "batch_selection": args.batch_selection,
            "run_dir": str(run_dir),
            "condition_dir": str(condition_dir),
            "candidate": str(candidate_path),
            "candidate_hash": canonical_hash(candidate),
            "provisional_hypothesis_rows": (
                str(provisional_path)
                if custom_materials_enabled
                else None
            ),
            "matched_c_selection_rows": (
                str(selection_path)
                if custom_materials_enabled
                else None
            ),
            "candidate_feedback_rows": (
                str(candidate_feedback_path)
                if custom_materials_enabled
                else None
            ),
            "feedback_norm_selection_rows": (
                str(norm_selection_path)
                if custom_materials_enabled
                else None
            ),
            "integrated_feedback_rows": str(feedback_path),
        }

    _progress(
        "evaluation start",
        n_examples=(
            min(len(eval_rows), args.limit_eval)
            if args.limit_eval is not None
            else len(eval_rows)
        ),
        num_threads=args.num_threads,
    )
    evaluated_rows = evaluate_condition(
        runtime=runtime,
        adapter=adapter,
        runtime_config=runtime_config,
        condition=args.condition,
        candidate=candidate,
        eval_rows=eval_rows,
        eval_path=eval_path,
        num_threads=args.num_threads,
        limit_eval=args.limit_eval,
        overwrite=args.overwrite,
    )
    _progress(
        "evaluation complete",
        n_rows=len(evaluated_rows),
        path=eval_path,
    )

    expected_examples = (
        min(len(eval_rows), args.limit_eval)
        if args.limit_eval is not None
        else len(eval_rows)
    )
    summary = build_eval_summary(
        condition=args.condition,
        rows=evaluated_rows,
        expected_examples=expected_examples,
        run_dir=run_dir,
    )
    summary.update({
        "run_dir": str(run_dir),
        "condition_dir": str(condition_dir),
        "candidate": str(candidate_path),
        "candidate_hash": canonical_hash(candidate),
        "eval_rows": str(eval_path),
        "config": str(config_path),
        "batch_manifest": (
            str(manifest_path)
            if args.condition != "base"
            else None
        ),
        "effective_condition": effective_condition,
        "batch_selection": args.batch_selection,
        "provisional_hypothesis_rows": (
            str(provisional_path)
            if custom_materials_enabled
            else None
        ),
        "matched_c_selection_rows": (
            str(selection_path)
            if custom_materials_enabled
            else None
        ),
        "positive_matches": (
            str(match_path)
            if custom_materials_enabled
            else None
        ),
        "positive_materials": (
            str(material_path)
            if custom_materials_enabled
            else None
        ),
        "candidate_feedback_rows": (
            str(candidate_feedback_path)
            if custom_materials_enabled
            else None
        ),
        "feedback_norm_selection_rows": (
            str(norm_selection_path)
            if custom_materials_enabled
            else None
        ),
        "updater_rows": str(updater_path),
        "integrated_feedback_rows": str(feedback_path),
        "agent_update_results": agent_update_results,
    })
    write_json(summary_path, summary)
    _progress(
        "summary saved",
        path=summary_path,
        score=summary.get("score"),
        n_ok=summary.get("n_ok"),
    )
    return summary