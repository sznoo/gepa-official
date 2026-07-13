#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Optional

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from experiments.method_probe.src.cache import (  # noqa: E402
    CallCache,
    atomic_write_json,
)
from experiments.method_probe.src.distance import (  # noqa: E402
    DistanceComparator,
    DistanceResolver,
)
from experiments.method_probe.src.hotpot import (  # noqa: E402
    HotpotRuntime,
    configure_lm,
    load_jsonl,
)
from experiments.method_probe.src.landscape import (  # noqa: E402
    LandscapeBuilder,
    make_query_endpoint,
)
from experiments.method_probe.src.program import (  # noqa: E402
    ProgramOperator,
    build_correct_evidence,
    build_wrong_evidence,
    load_current_query_prompt,
    run_query_intervention_with_downstream,
)


# ---------------------------------------------------------------------------
# Utilities
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


def load_json(path: str | Path) -> dict[str, Any]:
    path = Path(path)

    parsed = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(parsed, dict):
        raise ValueError(
            f"Expected JSON object in {path}."
        )

    return parsed


def save_artifact(
    run_dir: Path,
    filename: str,
    value: Any,
) -> Path:
    path = run_dir / filename
    atomic_write_json(path, value)
    return path


def validate_sample_alignment(
    *,
    row: Mapping[str, Any],
    rollout: Mapping[str, Any],
) -> str:
    row_sample_id = _clean_text(
        row.get("sample_id") or row.get("id")
    )
    rollout_sample_id = _clean_text(
        rollout.get("sample_id")
    )

    if not row_sample_id:
        raise ValueError(
            "Dataset row has no sample ID."
        )

    if row_sample_id != rollout_sample_id:
        raise ValueError(
            "Dataset row and rollout sample IDs differ: "
            f"{row_sample_id} != {rollout_sample_id}"
        )

    return row_sample_id


def attach_decomposition_id(
    *,
    decomposition_result: dict[str, Any],
    transition_id: str,
    max_depth: int,
    prompt_version: int,
) -> dict[str, Any]:
    if decomposition_result.get(
        "decomposition_id"
    ):
        return decomposition_result

    decomposition_result["decomposition_id"] = (
        _stable_id(
            "decomposition",
            {
                "root_transition_id": transition_id,
                "status": decomposition_result.get(
                    "status"
                ),
                "max_depth": max_depth,
                "prompt_version": prompt_version,
            },
        )
    )

    return decomposition_result


# ---------------------------------------------------------------------------
# Main transport unit
# ---------------------------------------------------------------------------

def run_correct_transport_unit(
    *,
    wrong_transition: Mapping[str, Any],
    wrong_decomposition: Mapping[str, Any],
    wrong_root_probe: Optional[
        Mapping[str, Any]
    ],
    correct_row: Mapping[str, Any],
    correct_rollout: Mapping[str, Any],
    current_prompt: str,
    runtime: HotpotRuntime,
    landscape: LandscapeBuilder,
    operator: ProgramOperator,
    comparator: DistanceComparator,
    max_depth: int,
    prompt_version: int,
    metadata: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """
    Execute one verified-W to one correct-sample transport unit.
    """

    sample_id = validate_sample_alignment(
        row=correct_row,
        rollout=correct_rollout,
    )

    baseline_em = int(
        correct_rollout.get("score", 0)
    )

    if baseline_em != 1:
        raise ValueError(
            "Correct-case transport requires a rollout "
            "with baseline end-to-end EM=1."
        )

    # ------------------------------------------------------------------
    # 1. Finalize wrong-side evidence.
    # ------------------------------------------------------------------

    extra_wrong_probes = (
        [wrong_root_probe]
        if wrong_root_probe is not None
        else []
    )

    wrong_evidence = build_wrong_evidence(
        root_transition=wrong_transition,
        decomposition_result=wrong_decomposition,
        extra_probe_records=extra_wrong_probes,
    )

    if (
        wrong_evidence.get("transition_label")
        != "W_to_C"
    ):
        raise ValueError(
            "Correct transport currently requires "
            "verified W_to_C evidence. Got: "
            f"{wrong_evidence.get('transition_label')}"
        )

    if not wrong_evidence.get(
        "aggregation_eligible"
    ):
        raise ValueError(
            "Wrong evidence is not eligible for reuse."
        )

    verified_wrong_transition = (
        wrong_evidence.get(
            "verified_atomic_transition"
        )
    )

    if not isinstance(
        verified_wrong_transition,
        Mapping,
    ):
        raise ValueError(
            "Wrong evidence has no verified atomic "
            "transition."
        )

    # ------------------------------------------------------------------
    # 2. Construct the current correct retrieval endpoint.
    # ------------------------------------------------------------------

    correct_endpoint = make_query_endpoint(
        correct_rollout,
        endpoint_type="current_correct",
        materialization="actual",
        metadata={
            "baseline_end_to_end_em": 1,
            **dict(metadata or {}),
        },
    )

    # ------------------------------------------------------------------
    # 3. Match a transferable wrong-side transition.
    #
    # The first implementation has one verified candidate. The same API
    # naturally extends to multiple candidate transitions later.
    # ------------------------------------------------------------------

    transport_match = (
        landscape.match_repair_transition(
            correct_endpoint=correct_endpoint,
            candidate_transitions=[
                verified_wrong_transition
            ],
            prompt_version=prompt_version,
            metadata={
                "correct_sample_id": sample_id,
                "wrong_evidence_id": (
                    wrong_evidence["evidence_id"]
                ),
                **dict(metadata or {}),
            },
        )
    )

    matched_transition = (
        transport_match["matched_transition"]
    )

    # ------------------------------------------------------------------
    # 4. Generate a virtual damaged retrieval destination and q target.
    # ------------------------------------------------------------------

    transported_result = (
        landscape.generate_transported_endpoint(
            correct_endpoint=correct_endpoint,
            matched_transition=matched_transition,
            prompt_version=prompt_version,
            metadata={
                "correct_sample_id": sample_id,
                "wrong_evidence_id": (
                    wrong_evidence["evidence_id"]
                ),
                "transport_match_id": (
                    transport_match["match_id"]
                ),
                **dict(metadata or {}),
            },
        )
    )

    transport_transition = (
        landscape.build_transport_transition(
            correct_endpoint=correct_endpoint,
            transported_endpoint=(
                transported_result[
                    "transported_endpoint"
                ]
            ),
            retrieval_target=(
                transported_result[
                    "retrieval_target"
                ]
            ),
            query_transition=(
                transported_result[
                    "query_transition"
                ]
            ),
            matched_transition_id=(
                matched_transition[
                    "transition_id"
                ]
            ),
        )
    )

    # ------------------------------------------------------------------
    # 5. Operationally test and decompose the transported transition.
    # ------------------------------------------------------------------

    resolver = DistanceResolver(
        landscape=landscape,
        operator=operator,
        comparator=comparator,
        runtime=runtime,
    )

    correct_decomposition = (
        resolver.resolve_transition(
            row=correct_row,
            baseline_rollout=correct_rollout,
            transition=transport_transition,
            current_prompt=current_prompt,
            max_depth=max_depth,
            prompt_version=prompt_version,
            metadata={
                "phase": "correct_transport",
                "correct_sample_id": sample_id,
                "wrong_evidence_id": (
                    wrong_evidence["evidence_id"]
                ),
                "transport_match_id": (
                    transport_match["match_id"]
                ),
                **dict(metadata or {}),
            },
        )
    )

    attach_decomposition_id(
        decomposition_result=correct_decomposition,
        transition_id=transport_transition[
            "transition_id"
        ],
        max_depth=max_depth,
        prompt_version=prompt_version,
    )

    # ------------------------------------------------------------------
    # 6. If the virtual retrieval transition was realized, continue the
    #    actual query through summarize2 and final answer.
    # ------------------------------------------------------------------

    downstream_result = None

    verified_probe = (
        correct_decomposition.get(
            "verified_probe"
        )
    )

    transport_realized = (
        correct_decomposition.get("status")
        == "verified_atomic"
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

    if transport_realized:
        intervention_result = (
            verified_probe.get(
                "intervention_result"
            )
        )

        if not isinstance(
            intervention_result,
            Mapping,
        ):
            raise ValueError(
                "Verified correct-side probe has no "
                "intervention result."
            )

        downstream_result = (
            run_query_intervention_with_downstream(
                runtime=runtime,
                row=correct_row,
                baseline_rollout=correct_rollout,
                intervention_result=(
                    intervention_result
                ),
            )
        )

    # ------------------------------------------------------------------
    # 7. Assign C_to_C / C_to_W only after transport realization and
    #    downstream EM evaluation.
    # ------------------------------------------------------------------

    correct_evidence = build_correct_evidence(
        transport_transition=transport_transition,
        decomposition_result=(
            correct_decomposition
        ),
        downstream_result=downstream_result,
        matched_wrong_evidence_id=(
            wrong_evidence["evidence_id"]
        ),
    )

    unit_id = _stable_id(
        "transport_unit",
        {
            "wrong_evidence_id": (
                wrong_evidence["evidence_id"]
            ),
            "correct_sample_id": sample_id,
            "transport_transition_id": (
                transport_transition[
                    "transition_id"
                ]
            ),
            "correct_evidence_id": (
                correct_evidence["evidence_id"]
            ),
        },
    )

    return {
        "unit_id": unit_id,
        "wrong_evidence": wrong_evidence,
        "correct_endpoint": correct_endpoint,
        "transport_match": transport_match,
        "transported_result": transported_result,
        "transport_transition": (
            transport_transition
        ),
        "correct_decomposition": (
            correct_decomposition
        ),
        "downstream_result": downstream_result,
        "correct_evidence": correct_evidence,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run one verified wrong-side retrieval "
            "transition through correct-case transport."
        )
    )

    # Wrong-side artifacts.
    parser.add_argument(
        "--wrong-transition",
        required=True,
        help=(
            "Root W-side transition JSON generated "
            "by landscape.py."
        ),
    )
    parser.add_argument(
        "--wrong-decomposition",
        required=True,
        help=(
            "W-side distance decomposition JSON."
        ),
    )
    parser.add_argument(
        "--wrong-root-probe",
        default=None,
        help=(
            "Optional original program.py probe. "
            "Mainly needed when preserving a failed "
            "root intervention for W_to_W evidence."
        ),
    )

    # Correct sample.
    parser.add_argument(
        "--correct-rollout",
        required=True,
    )
    parser.add_argument(
        "--data",
        required=True,
    )
    parser.add_argument(
        "--correct-row-index",
        type=int,
        required=True,
    )

    # Current prompt.
    parser.add_argument(
        "--current-prompt",
        default=None,
    )
    parser.add_argument(
        "--prompt-file",
        default=None,
    )
    parser.add_argument(
        "--prompt-version",
        type=int,
        default=0,
    )

    # Models/runtime.
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

    # Logging/output.
    parser.add_argument(
        "--cache-root",
        default=(
            "experiments/method_probe/cache/calls"
        ),
    )
    parser.add_argument(
        "--run-dir",
        required=True,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    run_dir = Path(args.run_dir)
    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    events_path = run_dir / "events.jsonl"

    rows = load_jsonl(args.data)

    if args.correct_row_index < 0:
        raise ValueError(
            "correct-row-index must be non-negative."
        )

    if args.correct_row_index >= len(rows):
        raise IndexError(
            f"correct-row-index "
            f"{args.correct_row_index} exceeds "
            f"dataset size {len(rows)}."
        )

    correct_row = rows[
        args.correct_row_index
    ]

    wrong_transition = load_json(
        args.wrong_transition
    )
    wrong_decomposition = load_json(
        args.wrong_decomposition
    )
    correct_rollout = load_json(
        args.correct_rollout
    )

    wrong_root_probe = (
        load_json(args.wrong_root_probe)
        if args.wrong_root_probe
        else None
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
        events_path=events_path,
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

    result = run_correct_transport_unit(
        wrong_transition=wrong_transition,
        wrong_decomposition=(
            wrong_decomposition
        ),
        wrong_root_probe=wrong_root_probe,
        correct_row=correct_row,
        correct_rollout=correct_rollout,
        current_prompt=current_prompt,
        runtime=runtime,
        landscape=landscape,
        operator=operator,
        comparator=comparator,
        max_depth=args.max_depth,
        prompt_version=args.prompt_version,
        metadata={
            "entrypoint": "main.py",
            "correct_row_index": (
                args.correct_row_index
            ),
        },
    )

    # Save each stage independently.
    paths = {
        "wrong_evidence": save_artifact(
            run_dir,
            "wrong_evidence.json",
            result["wrong_evidence"],
        ),
        "correct_endpoint": save_artifact(
            run_dir,
            "correct_endpoint.json",
            result["correct_endpoint"],
        ),
        "transport_match": save_artifact(
            run_dir,
            "transport_match.json",
            result["transport_match"],
        ),
        "transported_result": save_artifact(
            run_dir,
            "transported_result.json",
            result["transported_result"],
        ),
        "transport_transition": save_artifact(
            run_dir,
            "transport_transition.json",
            result["transport_transition"],
        ),
        "correct_decomposition": save_artifact(
            run_dir,
            "correct_decomposition.json",
            result["correct_decomposition"],
        ),
        "correct_evidence": save_artifact(
            run_dir,
            "correct_evidence.json",
            result["correct_evidence"],
        ),
    }

    if result["downstream_result"] is not None:
        paths["downstream_result"] = (
            save_artifact(
                run_dir,
                "downstream_result.json",
                result["downstream_result"],
            )
        )

    summary = {
        "unit_id": result["unit_id"],
        "wrong_sample_id": result[
            "wrong_evidence"
        ]["sample_id"],
        "wrong_evidence_id": result[
            "wrong_evidence"
        ]["evidence_id"],
        "wrong_transition_label": result[
            "wrong_evidence"
        ]["transition_label"],
        "correct_sample_id": result[
            "correct_evidence"
        ]["sample_id"],
        "transport_match_id": result[
            "transport_match"
        ]["match_id"],
        "matched_wrong_transition_id": (
            result[
                "transport_match"
            ]["matched_transition_id"]
        ),
        "transport_transition_id": result[
            "transport_transition"
        ]["transition_id"],
        "decomposition_status": result[
            "correct_decomposition"
        ]["status"],
        "transport_realized": result[
            "correct_evidence"
        ]["transport_realized"],
        "baseline_em": result[
            "correct_evidence"
        ]["baseline_em"],
        "trial_em": result[
            "correct_evidence"
        ]["trial_em"],
        "correct_transition_label": result[
            "correct_evidence"
        ]["transition_label"],
        "aggregation_eligible": result[
            "correct_evidence"
        ]["aggregation_eligible"],
        "artifacts": {
            name: str(path)
            for name, path in paths.items()
        },
    }

    summary_path = save_artifact(
        run_dir,
        "summary.json",
        summary,
    )

    print(json.dumps({
        **summary,
        "summary_path": str(summary_path),
    }, ensure_ascii=False, indent=2))




# ---------------------------------------------------------------------------
# Batch iteration
# ---------------------------------------------------------------------------

def _load_current_candidate(
    *,
    path: Optional[str],
    k: int,
    retriever_dir: str,
) -> dict[str, str]:
    from experiments.method_probe.src.hotpot import (
        build_seed_prompt_candidate,
    )

    if path:
        obj = load_json(path)

        if isinstance(
            obj.get("prompts"),
            Mapping,
        ):
            return {
                str(key): str(value)
                for key, value
                in obj["prompts"].items()
            }

        if isinstance(
            obj.get("candidate"),
            Mapping,
        ):
            return {
                str(key): str(value)
                for key, value
                in obj["candidate"].items()
            }

        return {
            str(key): str(value)
            for key, value in obj.items()
        }

    return build_seed_prompt_candidate(
        k=k,
        retriever_dir=retriever_dir,
    )


def _save_iteration_artifact(
    run_dir: Path,
    filename: str,
    value: Any,
) -> str:
    path = run_dir / filename
    atomic_write_json(path, value)
    return str(path)


def run_batch_iteration(
    *,
    train_rows: list[Mapping[str, Any]],
    val_rows: list[Mapping[str, Any]],
    current_candidate: Mapping[str, Any],
    runtime: HotpotRuntime,
    landscape: LandscapeBuilder,
    operator: ProgramOperator,
    comparator: DistanceComparator,
    retriever_dir: str,
    retrieval_k: int,
    max_depth: int,
    max_wrong: int,
    max_correct: int,
    prompt_version: int,
    require_correct_evidence: bool,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> dict[str, Any]:
    from experiments.method_probe.src.distance import (
        DistanceResolver,
    )
    from experiments.method_probe.src.hotpot import (
        evaluate_candidate_rows,
    )
    from experiments.method_probe.src.landscape import (
        classify_rollout,
        make_query_endpoint,
    )
    from experiments.method_probe.src.program import (
        aggregate_gradients,
        build_correct_evidence,
        build_wrong_evidence,
        run_operational_probe,
        run_query_intervention_with_downstream,
    )

    resolver = DistanceResolver(
        landscape=landscape,
        operator=operator,
        comparator=comparator,
        runtime=runtime,
    )

    train_evaluation = evaluate_candidate_rows(
        rows=train_rows,
        candidate=current_candidate,
        k=retrieval_k,
        retriever_dir=retriever_dir,
        candidate_id=(
            f"current_train_v{prompt_version}"
        ),
    )

    rollout_pairs = list(
        zip(
            train_rows,
            train_evaluation["rollouts"],
        )
    )

    wrong_pairs: list[
        tuple[Mapping[str, Any], Mapping[str, Any]]
    ] = []
    wrong_sample_ids: set[str] = set()

    for row, rollout in rollout_pairs:
        classification = classify_rollout(
            rollout,
            success_policy="natural_failure",
        )

        if classification["label"] != "W":
            continue

        wrong_pairs.append((row, rollout))
        wrong_sample_ids.add(
            str(rollout["sample_id"])
        )

        if len(wrong_pairs) >= max_wrong:
            break

    correct_pairs: list[
        tuple[Mapping[str, Any], Mapping[str, Any]]
    ] = []

    for row, rollout in rollout_pairs:
        sample_id = str(
            rollout["sample_id"]
        )

        if sample_id in wrong_sample_ids:
            continue

        if int(rollout.get("score", 0)) != 1:
            continue

        correct_pairs.append((row, rollout))

        if len(correct_pairs) >= max_correct:
            break

    wrong_records: list[dict[str, Any]] = []
    wrong_evidence: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    # --------------------------------------------------------------
    # Wrong-side attribution.
    # --------------------------------------------------------------

    for row, rollout in wrong_pairs:
        sample_id = str(
            rollout["sample_id"]
        )

        try:
            transition = (
                landscape.build_repair_transition(
                    row=row,
                    rollout=rollout,
                    prompt_version=prompt_version,
                    metadata={
                        "phase": "batch_wrong",
                        "sample_id": sample_id,
                        **dict(metadata or {}),
                    },
                )
            )

            root_probe = run_operational_probe(
                operator=operator,
                runtime=runtime,
                row=row,
                baseline_rollout=rollout,
                transition=transition,
                current_prompt=(
                    next(
                        value
                        for key, value
                        in current_candidate.items()
                        if (
                            key
                            in {
                                "create_query_hop2",
                                "create_query_hop2.predict",
                            }
                        )
                    )
                ),
                prompt_version=prompt_version,
                metadata={
                    "phase": "batch_wrong_root",
                    "sample_id": sample_id,
                },
            )

            decomposition = (
                resolver.resolve_transition(
                    row=row,
                    baseline_rollout=rollout,
                    transition=transition,
                    current_prompt=(
                        root_probe[
                            "composition_record"
                        ]["base_prompt"]
                    ),
                    max_depth=max_depth,
                    prompt_version=prompt_version,
                    initial_probe=root_probe,
                    metadata={
                        "phase": (
                            "batch_wrong_decomposition"
                        ),
                        "sample_id": sample_id,
                    },
                )
            )

            attach_decomposition_id(
                decomposition_result=(
                    decomposition
                ),
                transition_id=(
                    transition["transition_id"]
                ),
                max_depth=max_depth,
                prompt_version=prompt_version,
            )

            evidence = build_wrong_evidence(
                root_transition=transition,
                decomposition_result=(
                    decomposition
                ),
                extra_probe_records=[
                    root_probe
                ],
            )

            wrong_records.append({
                "sample_id": sample_id,
                "rollout": rollout,
                "transition": transition,
                "root_probe": root_probe,
                "decomposition": decomposition,
                "evidence": evidence,
            })
            wrong_evidence.append(evidence)

        except Exception as exc:
            errors.append({
                "phase": "wrong_side",
                "sample_id": sample_id,
                "error": repr(exc),
            })

    verified_wrong_evidence = [
        evidence
        for evidence in wrong_evidence
        if (
            evidence.get("transition_label")
            == "W_to_C"
            and evidence.get(
                "aggregation_eligible"
            )
            and isinstance(
                evidence.get(
                    "verified_atomic_transition"
                ),
                Mapping,
            )
        )
    ]

    verified_wrong_transitions = [
        evidence[
            "verified_atomic_transition"
        ]
        for evidence
        in verified_wrong_evidence
    ]

    correct_records: list[
        dict[str, Any]
    ] = []
    correct_evidence: list[
        dict[str, Any]
    ] = []

    # --------------------------------------------------------------
    # Correct-case transport.
    # --------------------------------------------------------------

    if verified_wrong_transitions:
        for row, rollout in correct_pairs:
            sample_id = str(
                rollout["sample_id"]
            )

            try:
                correct_endpoint = (
                    make_query_endpoint(
                        rollout,
                        endpoint_type=(
                            "current_correct"
                        ),
                        materialization="actual",
                        metadata={
                            "baseline_em": 1,
                        },
                    )
                )

                transport_match = (
                    landscape.match_repair_transition(
                        correct_endpoint=(
                            correct_endpoint
                        ),
                        candidate_transitions=(
                            verified_wrong_transitions
                        ),
                        prompt_version=(
                            prompt_version
                        ),
                        metadata={
                            "phase": (
                                "batch_correct_match"
                            ),
                            "sample_id": sample_id,
                        },
                    )
                )

                matched_transition = (
                    transport_match[
                        "matched_transition"
                    ]
                )

                matched_wrong_evidence = next(
                    evidence
                    for evidence
                    in verified_wrong_evidence
                    if (
                        evidence[
                            "verified_atomic_transition"
                        ]["transition_id"]
                        == matched_transition[
                            "transition_id"
                        ]
                    )
                )

                transported_result = (
                    landscape
                    .generate_transported_endpoint(
                        correct_endpoint=(
                            correct_endpoint
                        ),
                        matched_transition=(
                            matched_transition
                        ),
                        prompt_version=(
                            prompt_version
                        ),
                        metadata={
                            "phase": (
                                "batch_correct_transport"
                            ),
                            "sample_id": sample_id,
                        },
                    )
                )

                transport_transition = (
                    landscape
                    .build_transport_transition(
                        correct_endpoint=(
                            correct_endpoint
                        ),
                        transported_endpoint=(
                            transported_result[
                                "transported_endpoint"
                            ]
                        ),
                        retrieval_target=(
                            transported_result[
                                "retrieval_target"
                            ]
                        ),
                        query_transition=(
                            transported_result[
                                "query_transition"
                            ]
                        ),
                        matched_transition_id=(
                            matched_transition[
                                "transition_id"
                            ]
                        ),
                    )
                )

                query_prompt = next(
                    value
                    for key, value
                    in current_candidate.items()
                    if key in {
                        "create_query_hop2",
                        "create_query_hop2.predict",
                    }
                )

                root_probe = (
                    run_operational_probe(
                        operator=operator,
                        runtime=runtime,
                        row=row,
                        baseline_rollout=rollout,
                        transition=(
                            transport_transition
                        ),
                        current_prompt=query_prompt,
                        prompt_version=(
                            prompt_version
                        ),
                        metadata={
                            "phase": (
                                "batch_correct_root"
                            ),
                            "sample_id": sample_id,
                        },
                    )
                )

                decomposition = (
                    resolver.resolve_transition(
                        row=row,
                        baseline_rollout=rollout,
                        transition=(
                            transport_transition
                        ),
                        current_prompt=(
                            query_prompt
                        ),
                        max_depth=max_depth,
                        prompt_version=(
                            prompt_version
                        ),
                        initial_probe=root_probe,
                        metadata={
                            "phase": (
                                "batch_correct_"
                                "decomposition"
                            ),
                            "sample_id": sample_id,
                        },
                    )
                )

                attach_decomposition_id(
                    decomposition_result=(
                        decomposition
                    ),
                    transition_id=(
                        transport_transition[
                            "transition_id"
                        ]
                    ),
                    max_depth=max_depth,
                    prompt_version=(
                        prompt_version
                    ),
                )

                verified_probe = (
                    decomposition.get(
                        "verified_probe"
                    )
                )

                transport_realized = (
                    decomposition.get(
                        "status"
                    )
                    == "verified_atomic"
                    and isinstance(
                        verified_probe,
                        Mapping,
                    )
                    and bool(
                        verified_probe.get(
                            "local_metric",
                            {},
                        ).get(
                            "local_success"
                        )
                    )
                )

                downstream_result = None

                if transport_realized:
                    downstream_result = (
                        run_query_intervention_with_downstream(
                            runtime=runtime,
                            row=row,
                            baseline_rollout=rollout,
                            intervention_result=(
                                verified_probe[
                                    "intervention_result"
                                ]
                            ),
                        )
                    )

                evidence = build_correct_evidence(
                    transport_transition=(
                        transport_transition
                    ),
                    decomposition_result=(
                        decomposition
                    ),
                    downstream_result=(
                        downstream_result
                    ),
                    matched_wrong_evidence_id=(
                        matched_wrong_evidence[
                            "evidence_id"
                        ]
                    ),
                    extra_probe_records=[
                        root_probe
                    ],
                )

                correct_records.append({
                    "sample_id": sample_id,
                    "rollout": rollout,
                    "correct_endpoint": (
                        correct_endpoint
                    ),
                    "transport_match": (
                        transport_match
                    ),
                    "transported_result": (
                        transported_result
                    ),
                    "transport_transition": (
                        transport_transition
                    ),
                    "root_probe": root_probe,
                    "decomposition": (
                        decomposition
                    ),
                    "downstream_result": (
                        downstream_result
                    ),
                    "evidence": evidence,
                })
                correct_evidence.append(
                    evidence
                )

            except Exception as exc:
                errors.append({
                    "phase": "correct_side",
                    "sample_id": sample_id,
                    "error": repr(exc),
                })

    eligible_wrong = [
        evidence
        for evidence in wrong_evidence
        if evidence.get(
            "aggregation_eligible"
        )
    ]
    eligible_correct = [
        evidence
        for evidence in correct_evidence
        if evidence.get(
            "aggregation_eligible"
        )
    ]

    evidence_records = [
        *eligible_wrong,
        *eligible_correct,
    ]

    status = "ready_for_aggregation"

    if not verified_wrong_evidence:
        status = (
            "no_verified_wrong_evidence"
        )
    elif (
        require_correct_evidence
        and not eligible_correct
    ):
        status = (
            "no_verified_correct_evidence"
        )
    elif not evidence_records:
        status = "no_eligible_evidence"

    aggregation_result = None
    validation = None
    accepted_candidate = dict(
        current_candidate
    )

    if status == "ready_for_aggregation":
        aggregation_result = (
            aggregate_gradients(
                operator=operator,
                current_candidate=(
                    current_candidate
                ),
                evidence_records=(
                    evidence_records
                ),
                prompt_version=(
                    prompt_version
                ),
                metadata={
                    "phase": (
                        "batch_aggregation"
                    ),
                    **dict(metadata or {}),
                },
            )
        )

        candidate = aggregation_result[
            "full_candidate"
        ]

        current_val = (
            evaluate_candidate_rows(
                rows=val_rows,
                candidate=current_candidate,
                k=retrieval_k,
                retriever_dir=retriever_dir,
                candidate_id=(
                    f"current_val_v"
                    f"{prompt_version}"
                ),
            )
        )

        candidate_val = (
            evaluate_candidate_rows(
                rows=val_rows,
                candidate=candidate,
                k=retrieval_k,
                retriever_dir=retriever_dir,
                candidate_id=(
                    f"candidate_val_v"
                    f"{prompt_version}"
                ),
            )
        )

        accepted = (
            candidate_val["score"]
            > current_val["score"]
        )

        accepted_candidate = (
            candidate
            if accepted
            else dict(current_candidate)
        )

        validation = {
            "criterion": (
                "strict_improvement"
            ),
            "current_score": (
                current_val["score"]
            ),
            "candidate_score": (
                candidate_val["score"]
            ),
            "score_delta": (
                candidate_val["score"]
                - current_val["score"]
            ),
            "accepted": accepted,
            "current_evaluation": (
                current_val
            ),
            "candidate_evaluation": (
                candidate_val
            ),
        }

        status = (
            "accepted"
            if accepted
            else "rejected_by_val_gate"
        )

    return {
        "status": status,
        "prompt_version": prompt_version,
        "current_candidate": dict(
            current_candidate
        ),
        "accepted_candidate": (
            accepted_candidate
        ),
        "train_evaluation": (
            train_evaluation
        ),
        "selected_wrong_count": len(
            wrong_pairs
        ),
        "selected_correct_count": len(
            correct_pairs
        ),
        "wrong_records": wrong_records,
        "correct_records": (
            correct_records
        ),
        "wrong_evidence": (
            wrong_evidence
        ),
        "correct_evidence": (
            correct_evidence
        ),
        "eligible_evidence": (
            evidence_records
        ),
        "aggregation_result": (
            aggregation_result
        ),
        "validation": validation,
        "errors": errors,
    }


def parse_iteration_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run one method-probe optimization "
            "iteration with a strict validation gate."
        )
    )

    parser.add_argument(
        "--train-data",
        required=True,
    )
    parser.add_argument(
        "--val-data",
        required=True,
    )
    parser.add_argument(
        "--current-candidate",
        default=None,
    )

    parser.add_argument(
        "--batch-start",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--max-wrong",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--max-correct",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--val-limit",
        type=int,
        default=50,
    )

    parser.add_argument(
        "--allow-no-correct-evidence",
        action="store_true",
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
        "--prompt-version",
        type=int,
        default=0,
    )

    parser.add_argument(
        "--cache-root",
        default=(
            "experiments/method_probe/"
            "cache/calls"
        ),
    )
    parser.add_argument(
        "--run-dir",
        required=True,
    )

    return parser.parse_args()


def iteration_main() -> None:
    from experiments.method_probe.src.program import (
        save_aggregation_candidate,
    )

    args = parse_iteration_args()

    run_dir = Path(args.run_dir)
    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_rows_all = load_jsonl(
        args.train_data
    )
    val_rows_all = load_jsonl(
        args.val_data
    )

    start = args.batch_start
    end = start + args.batch_size

    train_rows = train_rows_all[
        start:end
    ]
    val_rows = val_rows_all[
        : args.val_limit
    ]

    if not train_rows:
        raise ValueError(
            "Selected training batch is empty."
        )

    if not val_rows:
        raise ValueError(
            "Validation subset is empty."
        )

    current_candidate = (
        _load_current_candidate(
            path=args.current_candidate,
            k=args.retrieval_k,
            retriever_dir=(
                args.retriever_dir
            ),
        )
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
        events_path=(
            run_dir / "events.jsonl"
        ),
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

    result = run_batch_iteration(
        train_rows=train_rows,
        val_rows=val_rows,
        current_candidate=current_candidate,
        runtime=runtime,
        landscape=landscape,
        operator=operator,
        comparator=comparator,
        retriever_dir=(
            args.retriever_dir
        ),
        retrieval_k=args.retrieval_k,
        max_depth=args.max_depth,
        max_wrong=args.max_wrong,
        max_correct=args.max_correct,
        prompt_version=args.prompt_version,
        require_correct_evidence=(
            not args
            .allow_no_correct_evidence
        ),
        metadata={
            "entrypoint": (
                "main.py --iteration"
            ),
            "batch_start": (
                args.batch_start
            ),
            "batch_size": (
                args.batch_size
            ),
        },
    )

    _save_iteration_artifact(
        run_dir,
        "current_candidate.json",
        result["current_candidate"],
    )
    _save_iteration_artifact(
        run_dir,
        "train_evaluation.json",
        result["train_evaluation"],
    )
    _save_iteration_artifact(
        run_dir,
        "wrong_records.json",
        result["wrong_records"],
    )
    _save_iteration_artifact(
        run_dir,
        "correct_records.json",
        result["correct_records"],
    )
    _save_iteration_artifact(
        run_dir,
        "evidence.json",
        result["eligible_evidence"],
    )
    _save_iteration_artifact(
        run_dir,
        "errors.json",
        result["errors"],
    )

    aggregation_paths = None

    if result["aggregation_result"]:
        aggregation_paths = (
            save_aggregation_candidate(
                run_dir=(
                    run_dir / "aggregation"
                ),
                aggregation_result=(
                    result[
                        "aggregation_result"
                    ]
                ),
                name=(
                    f"method_probe_v"
                    f"{args.prompt_version}"
                ),
            )
        )

    if result["validation"]:
        _save_iteration_artifact(
            run_dir,
            "validation.json",
            result["validation"],
        )

    _save_iteration_artifact(
        run_dir,
        "accepted_candidate.json",
        result["accepted_candidate"],
    )
    _save_iteration_artifact(
        run_dir,
        "accepted_prompt_candidate.json",
        {
            "name": (
                f"method_probe_accepted_v"
                f"{args.prompt_version}"
            ),
            "prompts": (
                result[
                    "accepted_candidate"
                ]
            ),
        },
    )

    summary = {
        "status": result["status"],
        "prompt_version": (
            args.prompt_version
        ),
        "batch_start": (
            args.batch_start
        ),
        "batch_size": len(train_rows),
        "val_size": len(val_rows),
        "selected_wrong_count": (
            result[
                "selected_wrong_count"
            ]
        ),
        "selected_correct_count": (
            result[
                "selected_correct_count"
            ]
        ),
        "wrong_evidence_counts": {
            label: sum(
                evidence.get(
                    "transition_label"
                )
                == label
                for evidence
                in result[
                    "wrong_evidence"
                ]
            )
            for label in (
                "W_to_C",
                "W_to_W",
            )
        },
        "correct_evidence_counts": {
            label: sum(
                evidence.get(
                    "transition_label"
                )
                == label
                for evidence
                in result[
                    "correct_evidence"
                ]
            )
            for label in (
                "C_to_C",
                "C_to_W",
            )
        },
        "num_errors": len(
            result["errors"]
        ),
        "validation": (
            {
                key: value
                for key, value
                in result[
                    "validation"
                ].items()
                if key not in {
                    "current_evaluation",
                    "candidate_evaluation",
                }
            }
            if result["validation"]
            else None
        ),
        "aggregation_paths": (
            aggregation_paths
        ),
    }

    summary_path = (
        _save_iteration_artifact(
            run_dir,
            "summary.json",
            summary,
        )
    )

    print(json.dumps({
        **summary,
        "summary_path": summary_path,
    }, ensure_ascii=False, indent=2))



if __name__ == "__main__":
    if "--iteration" in sys.argv:
        sys.argv.remove("--iteration")
        iteration_main()
    else:
        main()
