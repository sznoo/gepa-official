# /home/jinwoo/gepa-official/src/ours/utils/materialize.py
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from examples.ours.metric import answer_exact_match


AGENTS = {
    "summary1",
    "query",
    "summary2",
    "final",
}

STATE_KINDS = {
    "endpoint",
    "intermediate",
}


_TRACE_ALIASES = {
    "hop1_docs": (
        "hop1_docs",
        "current_hop1_docs",
    ),
    "hop1_titles": (
        "hop1_titles",
        "current_hop1_titles",
    ),
    "hop2_query": (
        "hop2_query",
        "current_query",
        "current_hop2_query",
        "generated_query",
    ),
    "hop2_docs": (
        "hop2_docs",
        "current_hop2_docs",
    ),
    "hop2_titles": (
        "hop2_titles",
        "current_hop2_titles",
        "retrieved_titles",
    ),
    "summary_1": (
        "summary_1",
        "current_summary_1",
    ),
    "summary_2": (
        "summary_2",
        "current_summary_2",
    ),
    "answer": (
        "answer",
        "pred_answer",
        "current_answer",
    ),
    "score": (
        "score",
        "answer_score",
        "current_score",
    ),
}

_MISSING_AFTER_HOP1_KEYS = (
    "missing_titles_after_hop1",
    "missing_after_hop1",
)


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------


def _get(
    obj: Any,
    key: str,
    default: Any = None,
) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    if hasattr(obj, key):
        return getattr(obj, key)
    try:
        return obj[key]
    except Exception:
        return default


def _has_field(
    obj: Any,
    key: str,
) -> bool:
    if isinstance(obj, Mapping):
        return key in obj
    return hasattr(obj, key)


def _trace_value(
    row: Mapping[str, Any],
    field: str,
    default: Any = None,
) -> Any:
    keys = _TRACE_ALIASES.get(
        field,
        (field,),
    )

    for key in keys:
        if _has_field(row, key):
            value = _get(row, key)
            if value is not None:
                return value

    return default


def _normalize_title(title: Any) -> str:
    return " ".join(
        str(title or "").strip().lower().split()
    )


def _clean_titles(values: Any) -> list[str]:
    return list(
        dict.fromkeys(
            str(value).strip()
            for value in (values or [])
            if str(value or "").strip()
        )
    )


def _normalized_title_set(
    titles: Any,
) -> set[str]:
    return {
        _normalize_title(title)
        for title in (titles or [])
        if str(title or "").strip()
    }


def _extract_titles(
    docs: list[Any] | None,
) -> list[str]:
    return [
        str(doc).split(" | ", 1)[0].strip()
        for doc in (docs or [])
        if str(doc or "").strip()
    ]


def _gold_support_titles(
    row: Mapping[str, Any],
) -> list[str]:
    stored = _clean_titles(
        _get(row, "gold_support_titles", [])
    )
    if stored:
        return stored

    supporting_facts = (
        _get(row, "supporting_facts", {}) or {}
    )

    return _clean_titles(
        _get(supporting_facts, "title", [])
    )


def _missing_after_hop1_titles(
    row: Mapping[str, Any],
    *,
    gold_titles: list[str],
    hop1_titles: list[str],
) -> list[str]:
    for key in _MISSING_AFTER_HOP1_KEYS:
        if _has_field(row, key):
            return _clean_titles(
                _get(row, key, [])
            )

    gold_map = {
        _normalize_title(title): title
        for title in gold_titles
    }
    hop1 = _normalized_title_set(
        hop1_titles
    )

    return [
        gold_map[title]
        for title in sorted(
            set(gold_map) - hop1
        )
    ]


def _require_text(
    value: Any,
    *,
    name: str,
) -> str:
    text = str(value or "").strip()

    if not text:
        raise ValueError(
            f"{name} cannot be empty."
        )

    return text


def _query_from_output(
    output: Any,
) -> str:
    if isinstance(output, Mapping):
        output = output.get("query")

    return _require_text(
        output,
        name="query output",
    )


def _validate_agent_output(
    *,
    agent: str,
    output: Any,
) -> str | dict[str, str]:
    if agent == "query":
        return {
            "query": _query_from_output(output),
        }

    return _require_text(
        output,
        name=f"{agent} output",
    )


def _validate_state_provenance(
    *,
    state_kind: str,
    state_origin: str,
) -> tuple[str, str]:
    state_kind = str(state_kind or "").strip()
    state_origin = str(state_origin or "").strip()

    if state_kind not in STATE_KINDS:
        raise ValueError(
            f"Unknown state_kind {state_kind!r}. "
            f"Expected one of {sorted(STATE_KINDS)}."
        )

    if not state_origin:
        raise ValueError(
            "state_origin cannot be empty."
        )

    return state_kind, state_origin


def _set_state_provenance(
    state: dict[str, Any],
    *,
    state_kind: str,
    state_origin: str,
) -> dict[str, Any]:
    state_kind, state_origin = (
        _validate_state_provenance(
            state_kind=state_kind,
            state_origin=state_origin,
        )
    )

    state["state_kind"] = state_kind
    state["state_origin"] = state_origin
    return state


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _compute_support_metrics(
    *,
    row: Mapping[str, Any],
    gold_titles: list[str],
    hop1_titles: list[str],
    hop2_titles: list[str],
) -> dict[str, Any]:
    gold_norm_to_original = {
        _normalize_title(title): title
        for title in gold_titles
    }

    gold = set(gold_norm_to_original)
    hop1 = _normalized_title_set(
        hop1_titles
    )
    hop2 = _normalized_title_set(
        hop2_titles
    )

    hit_hop1 = gold & hop1
    hit_hop2 = gold & hop2
    hit_total = gold & (hop1 | hop2)

    new_hop2 = hit_hop2 - hit_hop1
    missing_after_hop2 = gold - hit_total

    explicit_missing_after_hop1 = (
        _missing_after_hop1_titles(
            row,
            gold_titles=gold_titles,
            hop1_titles=hop1_titles,
        )
    )
    missing_after_hop1_map = {
        _normalize_title(title): title
        for title in explicit_missing_after_hop1
    }
    missing_after_hop1 = set(
        missing_after_hop1_map
    )

    recovered_missing = (
        missing_after_hop1 & hop2
    )
    still_missing_after_hop2 = (
        missing_after_hop1 - hop2
    )

    gold_denominator = len(gold)
    missing_denominator = len(
        missing_after_hop1
    )

    def original_title(
        normalized: str,
    ) -> str:
        return (
            gold_norm_to_original.get(normalized)
            or missing_after_hop1_map.get(normalized)
            or normalized
        )

    return {
        "support_recall_hop1": (
            len(hit_hop1) / gold_denominator
            if gold_denominator
            else 0.0
        ),
        "support_recall_hop2": (
            len(hit_hop2) / gold_denominator
            if gold_denominator
            else 0.0
        ),
        "support_recall_hop2_only": (
            len(new_hop2) / gold_denominator
            if gold_denominator
            else 0.0
        ),
        "support_recall_total": (
            len(hit_total) / gold_denominator
            if gold_denominator
            else 0.0
        ),
        "missing_recovery_rate": (
            len(recovered_missing)
            / missing_denominator
            if missing_denominator
            else None
        ),
        "missing_titles_after_hop1": [
            original_title(title)
            for title in sorted(
                missing_after_hop1
            )
        ],
        "recovered_missing_titles_hop2": [
            original_title(title)
            for title in sorted(
                recovered_missing
            )
        ],
        "unrecovered_missing_titles_hop2": [
            original_title(title)
            for title in sorted(
                still_missing_after_hop2
            )
        ],
        "new_support_titles_hop2": [
            original_title(title)
            for title in sorted(new_hop2)
        ],
        "missing_titles_after_hop2": [
            original_title(title)
            for title in sorted(
                missing_after_hop2
            )
        ],
        "hit_titles_hop1": [
            original_title(title)
            for title in sorted(hit_hop1)
        ],
        "hit_titles_hop2": [
            original_title(title)
            for title in sorted(hit_hop2)
        ],
        "hit_titles_total": [
            original_title(title)
            for title in sorted(hit_total)
        ],
    }


def _answer_score(
    answer: Any,
    gold_answer: Any,
) -> float | None:
    if gold_answer is None:
        return None

    example = {
        "answer": gold_answer,
    }
    prediction = {
        "answer": str(answer or ""),
    }

    return float(
        answer_exact_match(
            example,
            prediction,
        )
    )


# ---------------------------------------------------------------------------
# Program execution helpers
# ---------------------------------------------------------------------------


def _retrieve(
    program: Any,
    query: str,
) -> list[str]:
    result = program.retrieve_hop2(
        query
    )

    passages = _get(
        result,
        "passages",
        result,
    )

    return [
        str(passage)
        for passage in (passages or [])
    ]


def _run_query_writer(
    program: Any,
    *,
    question: str,
    summary_1: str,
) -> str:
    result = program.run_query(
        question,
        summary_1,
    )

    return _require_text(
        _get(result, "query", result),
        name="generated query",
    )


def _run_summary2(
    program: Any,
    *,
    question: str,
    summary_1: str,
    passages: list[str],
) -> str:
    result = program.run_summary2(
        question,
        summary_1,
        passages,
    )

    return _require_text(
        _get(result, "summary", result),
        name="summary2 output",
    )


def _run_final(
    program: Any,
    *,
    question: str,
    summary_1: str,
    summary_2: str,
) -> str:
    result = program.run_final(
        question,
        summary_1,
        summary_2,
    )

    return _require_text(
        _get(result, "answer", result),
        name="final answer",
    )


def _base_fields(
    row: Mapping[str, Any],
    *,
    agent: str,
    forced_output: Any,
) -> dict[str, Any]:
    return {
        "agent": agent,
        "output": forced_output,
        "question": _get(row, "question"),
        "gold_answer": _get(
            row,
            "gold_answer",
            _get(row, "answer"),
        ),
        "gold_support_titles": (
            _gold_support_titles(row)
        ),
    }


def _row_hop1_docs(
    row: Mapping[str, Any],
) -> list[str]:
    return [
        str(doc)
        for doc in (
            _trace_value(
                row,
                "hop1_docs",
                [],
            )
            or []
        )
    ]


def _row_hop2_docs(
    row: Mapping[str, Any],
) -> list[str]:
    return [
        str(doc)
        for doc in (
            _trace_value(
                row,
                "hop2_docs",
                [],
            )
            or []
        )
    ]


def _row_titles(
    row: Mapping[str, Any],
    *,
    field: str,
    docs: list[str],
) -> list[str]:
    return _clean_titles(
        _trace_value(
            row,
            field,
            [],
        )
        or _extract_titles(docs)
    )


def _query_downstream(
    *,
    program: Any,
    row: Mapping[str, Any],
    query: str,
    summary_1: str,
) -> dict[str, Any]:
    question = _require_text(
        _get(row, "question"),
        name="question",
    )

    hop1_docs = _row_hop1_docs(row)
    hop1_titles = _row_titles(
        row,
        field="hop1_titles",
        docs=hop1_docs,
    )

    hop2_docs = _retrieve(
        program,
        query,
    )
    hop2_titles = _extract_titles(
        hop2_docs,
    )

    summary_2 = _run_summary2(
        program,
        question=question,
        summary_1=summary_1,
        passages=hop2_docs,
    )

    answer = _run_final(
        program,
        question=question,
        summary_1=summary_1,
        summary_2=summary_2,
    )

    gold_titles = _gold_support_titles(row)
    gold_answer = _get(
        row,
        "gold_answer",
        _get(row, "answer"),
    )

    return {
        "summary_1": summary_1,
        "hop1_titles": hop1_titles,
        "hop1_docs": hop1_docs,
        "hop2_query": query,
        "hop2_titles": hop2_titles,
        "hop2_docs": hop2_docs,
        "summary_2": summary_2,
        "answer": answer,
        "score": _answer_score(
            answer,
            gold_answer,
        ),
        **_compute_support_metrics(
            row=row,
            gold_titles=gold_titles,
            hop1_titles=hop1_titles,
            hop2_titles=hop2_titles,
        ),
    }


# ---------------------------------------------------------------------------
# Agent materialization
# ---------------------------------------------------------------------------


def materialize_summary1_state(
    *,
    program: Any,
    row: Mapping[str, Any],
    summary_1: str,
) -> dict[str, Any]:
    """
    Force summary1 and run query -> retrieval -> summary2 -> final.

    `program` must be a sample-local copy with the intended prompt
    candidate already applied.
    """
    summary_1 = _require_text(
        summary_1,
        name="summary1 output",
    )
    question = _require_text(
        _get(row, "question"),
        name="question",
    )

    query = _run_query_writer(
        program,
        question=question,
        summary_1=summary_1,
    )

    downstream = _query_downstream(
        program=program,
        row=row,
        query=query,
        summary_1=summary_1,
    )

    return {
        **_base_fields(
            row,
            agent="summary1",
            forced_output=summary_1,
        ),
        "materialized": True,
        "forced_agent": "summary1",
        **downstream,
    }


def materialize_query_state(
    *,
    program: Any,
    row: Mapping[str, Any],
    query: str | Mapping[str, Any],
    summary_1: str | None = None,
) -> dict[str, Any]:
    """
    Force query and run retrieval -> summary2 -> final.

    `program` must be a sample-local copy with the intended prompt
    candidate already applied.
    """
    query_text = _query_from_output(query)

    if summary_1 is None:
        summary_1 = _trace_value(
            row,
            "summary_1",
        )

    summary_1 = _require_text(
        summary_1,
        name="summary1 context",
    )

    downstream = _query_downstream(
        program=program,
        row=row,
        query=query_text,
        summary_1=summary_1,
    )

    return {
        **_base_fields(
            row,
            agent="query",
            forced_output={
                "query": query_text,
            },
        ),
        "materialized": True,
        "forced_agent": "query",
        **downstream,
    }


def materialize_summary2_state(
    *,
    program: Any,
    row: Mapping[str, Any],
    summary_2: str,
    summary_1: str | None = None,
) -> dict[str, Any]:
    """
    Force summary2 and run final.

    `program` must be a sample-local copy with the intended prompt
    candidate already applied.
    """
    question = _require_text(
        _get(row, "question"),
        name="question",
    )
    summary_2 = _require_text(
        summary_2,
        name="summary2 output",
    )

    if summary_1 is None:
        summary_1 = _trace_value(
            row,
            "summary_1",
        )

    summary_1 = _require_text(
        summary_1,
        name="summary1 context",
    )

    answer = _run_final(
        program,
        question=question,
        summary_1=summary_1,
        summary_2=summary_2,
    )

    hop1_docs = _row_hop1_docs(row)
    hop2_docs = _row_hop2_docs(row)
    hop1_titles = _row_titles(
        row,
        field="hop1_titles",
        docs=hop1_docs,
    )
    hop2_titles = _row_titles(
        row,
        field="hop2_titles",
        docs=hop2_docs,
    )

    gold_titles = _gold_support_titles(row)
    gold_answer = _get(
        row,
        "gold_answer",
        _get(row, "answer"),
    )

    return {
        **_base_fields(
            row,
            agent="summary2",
            forced_output=summary_2,
        ),
        "materialized": True,
        "forced_agent": "summary2",
        "summary_1": summary_1,
        "hop1_titles": hop1_titles,
        "hop1_docs": hop1_docs,
        "hop2_query": _trace_value(
            row,
            "hop2_query",
        ),
        "hop2_titles": hop2_titles,
        "hop2_docs": hop2_docs,
        "summary_2": summary_2,
        "answer": answer,
        "score": _answer_score(
            answer,
            gold_answer,
        ),
        **_compute_support_metrics(
            row=row,
            gold_titles=gold_titles,
            hop1_titles=hop1_titles,
            hop2_titles=hop2_titles,
        ),
    }


def materialize_final_state(
    *,
    row: Mapping[str, Any],
    answer: Any,
) -> dict[str, Any]:
    """Final is terminal, so no downstream call is required."""
    answer = _require_text(
        answer,
        name="final answer",
    )

    gold_answer = _get(
        row,
        "gold_answer",
        _get(row, "answer"),
    )

    return {
        **_base_fields(
            row,
            agent="final",
            forced_output=answer,
        ),
        "materialized": True,
        "forced_agent": "final",
        "summary_1": _trace_value(
            row,
            "summary_1",
        ),
        "summary_2": _trace_value(
            row,
            "summary_2",
        ),
        "answer": answer,
        "score": _answer_score(
            answer,
            gold_answer,
        ),
    }


def materialize_agent_state(
    *,
    agent: str,
    program: Any,
    row: Mapping[str, Any],
    output: Any,
    summary_1: str | None = None,
    state_kind: str = "endpoint",
    state_origin: str = "forced_output",
) -> dict[str, Any]:
    """
    Materialize a forced output at one agent boundary.

    Upstream values come from `row` unless explicitly overridden. The
    supplied `program` must be a sample-local, candidate-applied copy.
    """
    if agent not in AGENTS:
        raise ValueError(
            f"Unknown agent {agent!r}. "
            f"Expected one of {sorted(AGENTS)}."
        )

    normalized_output = _validate_agent_output(
        agent=agent,
        output=output,
    )

    if agent == "summary1":
        state = materialize_summary1_state(
            program=program,
            row=row,
            summary_1=normalized_output,
        )

    elif agent == "query":
        state = materialize_query_state(
            program=program,
            row=row,
            query=normalized_output,
            summary_1=summary_1,
        )

    elif agent == "summary2":
        state = materialize_summary2_state(
            program=program,
            row=row,
            summary_2=normalized_output,
            summary_1=summary_1,
        )

    else:
        state = materialize_final_state(
            row=row,
            answer=normalized_output,
        )

    return _set_state_provenance(
        state,
        state_kind=state_kind,
        state_origin=state_origin,
    )


def _destination_recovery_metadata(
    *,
    destination: Mapping[str, Any],
    state: Mapping[str, Any],
) -> dict[str, Any]:
    target_titles = _clean_titles(
        destination.get("target_titles", [])
    )

    if not target_titles:
        return {}

    target_map = {
        _normalize_title(title): title
        for title in target_titles
    }
    retrieved = _normalized_title_set(
        _get(state, "hop2_titles", [])
    )

    recovered = set(target_map) & retrieved
    missing = set(target_map) - retrieved

    return {
        "destination_target_titles": target_titles,
        "destination_recovered_titles": [
            target_map[title]
            for title in sorted(recovered)
        ],
        "destination_missing_titles": [
            target_map[title]
            for title in sorted(missing)
        ],
        "destination_recovery_rate": (
            len(recovered) / len(target_map)
        ),
        "destination_any_hit": bool(
            recovered
        ),
        "destination_all_recovered": (
            not missing
        ),
    }


def materialize_destination(
    *,
    program: Any,
    row: Mapping[str, Any],
    destination: Mapping[str, Any],
    summary_1: str | None = None,
) -> dict[str, Any]:
    """Materialize an available destination.py endpoint."""
    if not isinstance(destination, Mapping):
        raise TypeError(
            "destination must be a mapping."
        )

    if destination.get("available") is False:
        reason = str(
            destination.get("reason")
            or "destination is unavailable"
        )
        raise ValueError(
            f"Cannot materialize unavailable destination: {reason}"
        )

    agent = str(
        destination.get("agent") or ""
    ).strip()

    if "output" not in destination:
        raise ValueError(
            "Destination is missing `output`."
        )

    state = materialize_agent_state(
        agent=agent,
        program=program,
        row=row,
        output=destination["output"],
        summary_1=summary_1,
        state_kind="endpoint",
        state_origin="gold_destination",
    )

    state.update({
        "destination_available": True,
        "destination_kind": destination.get(
            "target_kind"
        ),
        "destination_rationale": destination.get(
            "rationale"
        ),
    })
    state.update(
        _destination_recovery_metadata(
            destination=destination,
            state=state,
        )
    )

    return state


# ---------------------------------------------------------------------------
# Trace -> state
# ---------------------------------------------------------------------------


def state_from_trace(
    *,
    agent: str,
    row: Mapping[str, Any],
    state_kind: str = "endpoint",
    state_origin: str = "baseline_rollout",
) -> dict[str, Any]:
    """Build a validated agent state from a rollout trace."""
    if agent not in AGENTS:
        raise ValueError(
            f"Unknown agent {agent!r}."
        )

    state_kind, state_origin = (
        _validate_state_provenance(
            state_kind=state_kind,
            state_origin=state_origin,
        )
    )

    question = _require_text(
        _get(row, "question"),
        name="question",
    )
    gold_answer = _get(
        row,
        "gold_answer",
        _get(row, "answer"),
    )

    hop1_docs = _row_hop1_docs(row)
    hop2_docs = _row_hop2_docs(row)
    hop1_titles = _row_titles(
        row,
        field="hop1_titles",
        docs=hop1_docs,
    )
    hop2_titles = _row_titles(
        row,
        field="hop2_titles",
        docs=hop2_docs,
    )

    summary_1 = _trace_value(
        row,
        "summary_1",
    )
    hop2_query = _trace_value(
        row,
        "hop2_query",
    )
    summary_2 = _trace_value(
        row,
        "summary_2",
    )
    answer = _trace_value(
        row,
        "answer",
    )

    if agent == "summary1":
        output = _validate_agent_output(
            agent=agent,
            output=summary_1,
        )
    elif agent == "query":
        output = _validate_agent_output(
            agent=agent,
            output={
                "query": hop2_query,
            },
        )
    elif agent == "summary2":
        output = _validate_agent_output(
            agent=agent,
            output=summary_2,
        )
    else:
        output = _validate_agent_output(
            agent=agent,
            output=answer,
        )

    support_metrics = _compute_support_metrics(
        row=row,
        gold_titles=_gold_support_titles(row),
        hop1_titles=hop1_titles,
        hop2_titles=hop2_titles,
    )

    score = _trace_value(
        row,
        "score",
    )
    if score is None:
        score = _answer_score(
            answer,
            gold_answer,
        )

    return {
        "agent": agent,
        "output": output,
        "materialized": False,
        "forced_agent": None,
        "state_kind": state_kind,
        "state_origin": state_origin,
        "question": question,
        "gold_answer": gold_answer,
        "gold_support_titles": (
            _gold_support_titles(row)
        ),
        "summary_1": summary_1,
        "hop1_titles": hop1_titles,
        "hop1_docs": hop1_docs,
        "hop2_query": hop2_query,
        "hop2_titles": hop2_titles,
        "hop2_docs": hop2_docs,
        "summary_2": summary_2,
        "answer": answer,
        "score": score,
        **support_metrics,
    }


# ---------------------------------------------------------------------------
# Agent-local metrics
# ---------------------------------------------------------------------------


def _state_recovered_missing_titles(
    state: Mapping[str, Any],
) -> set[str]:
    stored = _get(
        state,
        "recovered_missing_titles_hop2",
    )
    if stored is not None:
        return _normalized_title_set(stored)

    missing = _normalized_title_set(
        _get(
            state,
            "missing_titles_after_hop1",
            [],
        )
    )
    hop2 = _normalized_title_set(
        _get(state, "hop2_titles", [])
    )
    return missing & hop2


def compute_local_metric(
    *,
    agent: str,
    state: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Compute the current Hotpot probe metric for one agent.

    summary1, query:
        missing-support recovery by the downstream second-hop retrieval.

    summary2:
        downstream answer exact match. This remains provisional until the
        summary2-local metric is finalized.

    final:
        answer exact match.
    """
    if agent not in AGENTS:
        raise ValueError(
            f"Unknown agent {agent!r}."
        )

    state_agent = _get(state, "agent")
    if state_agent not in {None, agent}:
        raise ValueError(
            f"State agent {state_agent!r} does not "
            f"match requested agent {agent!r}."
        )

    if agent in {"query", "summary1"}:
        missing_titles = _normalized_title_set(
            _get(
                state,
                "missing_titles_after_hop1",
                [],
            )
        )
        recovered_titles = (
            _state_recovered_missing_titles(
                state
            )
        )
        unrecovered_titles = (
            missing_titles - recovered_titles
        )

        denominator = len(missing_titles)
        value = (
            len(recovered_titles) / denominator
            if denominator
            else 0.0
        )

        return {
            "metric_name": (
                "query_missing_recovery"
                if agent == "query"
                else "summary1_downstream_missing_recovery"
            ),
            "value": value,
            "available": bool(denominator),
            "hit_titles": sorted(
                recovered_titles
            ),
            "recovered_missing_titles": sorted(
                recovered_titles
            ),
            "missing_titles": sorted(
                unrecovered_titles
            ),
            "n_missing_after_hop1": denominator,
        }

    score = _get(state, "score")

    if score is None:
        score = _answer_score(
            _get(state, "answer"),
            _get(state, "gold_answer"),
        )

    score = float(score or 0.0)

    return {
        "metric_name": (
            "summary2_downstream_answer_score"
            if agent == "summary2"
            else "answer_score"
        ),
        "value": score,
        "available": (
            _get(state, "gold_answer")
            is not None
        ),
        "answer": _get(state, "answer"),
    }


# ---------------------------------------------------------------------------
# Atomicity helpers
#
# These functions are intentionally kept separate from materialization and
# local metric construction. Their certification semantics remain unchanged
# pending the dedicated atomicity discussion.
# ---------------------------------------------------------------------------


def evaluate_endpoint_solvability(
    *,
    agent: str,
    source_state: Mapping[str, Any],
    target_state: Mapping[str, Any],
    realized_state: Mapping[str, Any],
) -> dict[str, Any]:
    if _get(source_state, "state_kind") != "endpoint":
        raise ValueError(
            "source_state must be an endpoint."
        )

    if _get(target_state, "state_kind") != "endpoint":
        raise ValueError(
            "target_state must be an endpoint."
        )

    source_metric = compute_local_metric(
        agent=agent,
        state=source_state,
    )
    target_metric = compute_local_metric(
        agent=agent,
        state=target_state,
    )
    realized_metric = compute_local_metric(
        agent=agent,
        state=realized_state,
    )

    if agent in {"query", "summary1"}:
        source_hits = set(
            source_metric["hit_titles"]
        )
        target_hits = set(
            target_metric["hit_titles"]
        )
        realized_hits = set(
            realized_metric["hit_titles"]
        )

        required_target_hits = (
            target_hits - source_hits
        )
        recovered_target_hits = (
            required_target_hits
            & realized_hits
        )
        missing_target_hits = (
            target_hits - realized_hits
        )
        lost_source_hits = (
            source_hits - realized_hits
        )

        target_solved = (
            not missing_target_hits
            and not lost_source_hits
        )
        no_regression = (
            not lost_source_hits
        )

        return {
            "metric_name": (
                realized_metric["metric_name"]
            ),
            "target_solved": target_solved,
            "no_regression": no_regression,
            "source_metric": source_metric,
            "target_metric": target_metric,
            "realized_metric": realized_metric,
            "required_target_hits": sorted(
                required_target_hits
            ),
            "recovered_target_hits": sorted(
                recovered_target_hits
            ),
            "missing_target_hits": sorted(
                missing_target_hits
            ),
            "lost_source_hits": sorted(
                lost_source_hits
            ),
        }

    source_value = float(
        source_metric["value"]
    )
    target_value = float(
        target_metric["value"]
    )
    realized_value = float(
        realized_metric["value"]
    )

    no_regression = (
        realized_value >= source_value
    )
    target_solved = (
        realized_value >= target_value
        and no_regression
    )

    return {
        "metric_name": (
            realized_metric["metric_name"]
        ),
        "target_solved": target_solved,
        "no_regression": no_regression,
        "source_metric": source_metric,
        "target_metric": target_metric,
        "realized_metric": realized_metric,
        "source_value": source_value,
        "target_value": target_value,
        "realized_value": realized_value,
    }


def _distance_comparison_is_compatible(
    comparison: Mapping[str, Any],
) -> bool:
    explicit = comparison.get(
        "candidate_atomic_compatible"
    )
    if isinstance(explicit, bool):
        return explicit

    relation = str(
        comparison.get("relation") or ""
    ).strip()

    return relation in {
        "candidate_smaller",
        "approximately_equal",
    }


def is_atomic(
    *,
    agent: str,
    source_state: Mapping[str, Any],
    target_state: Mapping[str, Any],
    realized_state: Mapping[str, Any] | None = None,
    distance_comparisons: list[
        Mapping[str, Any]
    ] | None = None,
) -> dict[str, Any]:
    """
    Existing atomicity helper retained for later semantic revision.

    Materialization functions do not call this function automatically.
    """
    if agent not in AGENTS:
        raise ValueError(
            f"Unknown agent {agent!r}."
        )

    source_kind = _get(
        source_state,
        "state_kind",
    )
    target_kind = _get(
        target_state,
        "state_kind",
    )

    if source_kind not in STATE_KINDS:
        raise ValueError(
            f"Invalid source state_kind: "
            f"{source_kind!r}."
        )

    if target_kind not in STATE_KINDS:
        raise ValueError(
            f"Invalid target state_kind: "
            f"{target_kind!r}."
        )

    both_endpoints = (
        source_kind == "endpoint"
        and target_kind == "endpoint"
    )

    if both_endpoints:
        if realized_state is None:
            raise ValueError(
                "Endpoint atomicity requires "
                "realized_state."
            )

        metric_result = (
            evaluate_endpoint_solvability(
                agent=agent,
                source_state=source_state,
                target_state=target_state,
                realized_state=realized_state,
            )
        )

        return {
            "agent": agent,
            "is_atomic": bool(
                metric_result["target_solved"]
            ),
            "certification": "metric",
            "source_kind": source_kind,
            "target_kind": target_kind,
            "metric_result": metric_result,
        }

    comparisons = list(
        distance_comparisons or []
    )

    if not comparisons:
        return {
            "agent": agent,
            "is_atomic": None,
            "certification": "unavailable",
            "source_kind": source_kind,
            "target_kind": target_kind,
            "reason": (
                "no_metric_certified_atomic_reference"
            ),
            "distance_comparisons": [],
        }

    compatible = [
        comparison
        for comparison in comparisons
        if _distance_comparison_is_compatible(
            comparison
        )
    ]
    incompatible = [
        comparison
        for comparison in comparisons
        if not _distance_comparison_is_compatible(
            comparison
        )
    ]

    return {
        "agent": agent,
        "is_atomic": (
            len(compatible) > len(incompatible)
        ),
        "certification": "distance",
        "source_kind": source_kind,
        "target_kind": target_kind,
        "compatible_votes": len(
            compatible
        ),
        "incompatible_votes": len(
            incompatible
        ),
        "n_references": len(comparisons),
        "distance_comparisons": comparisons,
    }