# /home/jinwoo/gepa-official/src/ours/utils/destination.py
from __future__ import annotations

import json
from collections.abc import Mapping
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
        "Integrate second-hop evidence with first-hop context and retain "
        "the facts needed to answer the question."
    ),
    "final": (
        "Derive the minimal final answer supported by the supplied "
        "intermediate summaries."
    ),
}


DESTINATION_REQUIREMENTS = {
    "summary1": """
Produce an ideal summary1 output using only information available at the
summary1 boundary.

The output should:
- summarize useful evidence from the actual first-hop retrieval;
- identify the bridge entity, relation, or missing evidence needed next;
- expose a compact retrieval direction for the query agent;
- remain a summary1 output rather than a final answer;
- not state hidden second-hop facts or the gold answer;
- treat missing support titles only as retrieval targets, not as evidence
  that their unseen documents contain a particular answer fact.
""".strip(),
    "summary2": """
Produce an ideal summary2 output using only information available at the
summary2 boundary.

The output should:
- integrate the actual summary1 context with gold supporting evidence that
  is genuinely present in the second-hop retrieval;
- retain the exact visible facts needed by the final-answer agent;
- make the answer derivable when the supplied evidence supports it;
- remain an evidence summary rather than a final-answer response;
- not add facts from gold documents that are absent from the actual inputs;
- not use or mention the gold answer.
""".strip(),
}


_MISSING_AFTER_HOP2_KEYS = (
    "missing_titles_after_hop2",
    "missing_after_hop2",
)


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


def _has_field(obj: Any, key: str) -> bool:
    if isinstance(obj, Mapping):
        return key in obj
    return hasattr(obj, key)


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


def _extract_titles(docs: Any) -> list[str]:
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
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        obj = json.loads(text)
        if not isinstance(obj, dict):
            raise TypeError("Expected a JSON object.")
        return obj
    except Exception:
        pass

    decoder = json.JSONDecoder()

    for index, char in enumerate(text):
        if char != "{":
            continue

        try:
            obj, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue

        if isinstance(obj, dict):
            return obj

    raise ValueError(
        "Could not extract JSON object from LM output: "
        f"{text[:500]}"
    )


def extract_gold_support(
    row: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """
    Recover every unique HotpotQA gold supporting sentence.

    The extraction is strict: if any requested (title, sent_id) pair cannot
    be resolved from context, destination generation stops instead of using
    a partial gold target.
    """
    context = _get(row, "context", {}) or {}
    supporting_facts = (
        _get(row, "supporting_facts", {}) or {}
    )

    context_titles = list(
        _get(context, "title", []) or []
    )
    context_sentences = list(
        _get(context, "sentences", []) or []
    )

    support_titles = list(
        _get(supporting_facts, "title", []) or []
    )
    support_sent_ids = list(
        _get(supporting_facts, "sent_id", []) or []
    )

    if len(support_titles) != len(support_sent_ids):
        raise ValueError(
            "supporting_facts.title and supporting_facts.sent_id "
            "must have equal lengths."
        )

    requested: list[tuple[str, int, str]] = []
    seen_requests: set[tuple[str, int]] = set()

    for title, sent_id_raw in zip(
        support_titles,
        support_sent_ids,
    ):
        title_text = str(title or "").strip()
        if not title_text:
            raise ValueError(
                "A supporting-fact title is empty."
            )

        try:
            sent_id = int(sent_id_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid supporting-fact sent_id: {sent_id_raw!r}."
            ) from exc

        key = (_normalize_title(title_text), sent_id)
        if key in seen_requests:
            continue

        seen_requests.add(key)
        requested.append((key[0], sent_id, title_text))

    if not requested:
        raise ValueError(
            "No gold supporting facts are present in the row."
        )

    title_to_indices: dict[str, list[int]] = {}
    for index, title in enumerate(context_titles):
        title_to_indices.setdefault(
            _normalize_title(title),
            [],
        ).append(index)

    records: list[dict[str, Any]] = []
    missing_refs: list[dict[str, Any]] = []

    for title_key, sent_id, requested_title in requested:
        resolved = None

        for context_index in title_to_indices.get(
            title_key,
            [],
        ):
            if context_index >= len(context_sentences):
                continue

            document_sentences = (
                context_sentences[context_index] or []
            )
            if not 0 <= sent_id < len(document_sentences):
                continue

            sentence = str(
                document_sentences[sent_id] or ""
            ).strip()
            if not sentence:
                continue

            resolved = {
                "title": str(
                    context_titles[context_index]
                ).strip(),
                "sent_id": sent_id,
                "sentence": sentence,
            }
            break

        if resolved is None:
            missing_refs.append({
                "title": requested_title,
                "sent_id": sent_id,
            })
        else:
            records.append(resolved)

    if missing_refs:
        raise ValueError(
            "Could not extract all gold supporting sentences. "
            f"Missing references: {_json_dumps(missing_refs)}"
        )

    return records


def _split_gold_support_by_titles(
    gold_support: list[dict[str, Any]],
    visible_titles: Any,
    *,
    visible_key: str,
    missing_key: str,
) -> dict[str, list[dict[str, Any]]]:
    visible_title_set = {
        _normalize_title(title)
        for title in (visible_titles or [])
        if str(title or "").strip()
    }

    visible = []
    missing = []

    for record in gold_support:
        if (
            _normalize_title(record["title"])
            in visible_title_set
        ):
            visible.append(record)
        else:
            missing.append(record)

    return {
        visible_key: visible,
        missing_key: missing,
    }


def split_gold_support_for_summary1(
    row: Mapping[str, Any],
    gold_support: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    hop1_titles = list(
        _get(row, "hop1_titles", [])
        or _extract_titles(
            _get(row, "hop1_docs", [])
        )
    )

    return _split_gold_support_by_titles(
        gold_support,
        hop1_titles,
        visible_key="visible_in_hop1",
        missing_key="missing_after_hop1",
    )


def split_gold_support_for_summary2(
    row: Mapping[str, Any],
    gold_support: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    hop2_titles = list(
        _get(row, "hop2_titles", [])
        or _extract_titles(
            _get(row, "hop2_docs", [])
        )
    )

    return _split_gold_support_by_titles(
        gold_support,
        hop2_titles,
        visible_key="visible_in_hop2",
        missing_key="missing_from_hop2",
    )


def get_missing_titles_after_hop2(
    row: Mapping[str, Any],
) -> list[str]:
    """
    Read either current or legacy trace fields.

    An explicitly stored empty list is authoritative and does not fall back
    to all gold titles. If neither field exists, derive the missing set from
    gold support titles and retrieved titles.
    """
    for key in _MISSING_AFTER_HOP2_KEYS:
        if _has_field(row, key):
            return _clean_titles(
                _get(row, key, [])
            )

    gold_titles = {
        _normalize_title(title): title
        for title in _gold_support_titles(row)
    }

    hop1_titles = list(
        _get(row, "hop1_titles", [])
        or _extract_titles(
            _get(row, "hop1_docs", [])
        )
    )
    hop2_titles = list(
        _get(row, "hop2_titles", [])
        or _extract_titles(
            _get(row, "hop2_docs", [])
        )
    )

    retrieved = {
        _normalize_title(title)
        for title in [*hop1_titles, *hop2_titles]
    }

    return [
        original
        for normalized, original in gold_titles.items()
        if normalized not in retrieved
    ]


def make_oracle_query(
    row: Mapping[str, Any],
) -> tuple[str, list[str]]:
    """
    Existing query-agent oracle rule:

        missing_after_hop2_titles + question
    """
    question = str(
        _get(row, "question", "") or ""
    ).strip()
    if not question:
        raise ValueError("Question cannot be empty.")

    target_titles = get_missing_titles_after_hop2(
        row
    )
    if not target_titles:
        raise ValueError(
            "No missing support title remains after hop2; "
            "query destination is unavailable."
        )

    query = " ".join(
        [*target_titles, question]
    ).strip()

    return query, target_titles


def _missing_target_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {"title": title}
        for title in _clean_titles(
            record.get("title")
            for record in records
        )
    ]


def _unavailable_destination(
    *,
    agent: str,
    target_kind: str,
    reason: str,
    row: Mapping[str, Any],
    gold_support: list[dict[str, Any]],
    **details: Any,
) -> dict[str, Any]:
    return {
        "agent": agent,
        "target_kind": target_kind,
        "available": False,
        "reason": reason,
        "gold_answer": _get(row, "gold_answer"),
        "gold_support": gold_support,
        **details,
    }


class GenerateGoldDestinationSignature(Signature):
    input_keys = [
        "agent",
        "agent_role",
        "destination_requirements",
        "question",
        "current_output",
        "upstream_context",
        "visible_gold_support",
        "missing_support_targets",
    ]
    output_keys = [
        "destination_output",
        "rationale",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
You are generating a gold-conditioned destination output for one agent
inside a multi-agent question-answering pipeline.

The destination is not a prompt update. It is an ideal output that remains
possible from the selected agent's actual input boundary.

Use only:
- the supplied task and upstream context;
- gold supporting sentences explicitly listed as visible_gold_support;
- missing support titles only as retrieval targets.

Do not infer or state the hidden contents of a missing support document.
Do not use or guess the gold answer. Preserve the functional role of the
selected agent.

Agent:
{input_dict["agent"]}

Agent role:
{input_dict["agent_role"]}

Destination requirements:
{input_dict["destination_requirements"]}

Question:
{input_dict["question"]}

Current agent output:
{_json_dumps(input_dict["current_output"])}

Actual upstream context:
{_json_dumps(input_dict["upstream_context"])}

Gold supporting evidence visible at this agent boundary:
{_json_dumps(input_dict["visible_gold_support"])}

Missing support titles that may be named only as retrieval targets:
{_json_dumps(input_dict["missing_support_targets"])}

Return strict JSON only:
{{
  "destination_output": "<ideal agent output>",
  "rationale": "<brief explanation grounded only in the supplied visible evidence>"
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)

        output = str(
            obj.get("destination_output") or ""
        ).strip()
        if not output:
            raise ValueError(
                "`destination_output` cannot be empty."
            )

        return {
            "destination_output": output,
            "rationale": str(
                obj.get("rationale") or ""
            ).strip(),
        }


def _generate_text_destination(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent: str,
    row: Mapping[str, Any],
    upstream_context: Mapping[str, Any],
    visible_gold_support: list[dict[str, Any]],
    missing_support_targets: list[dict[str, Any]],
    gold_support: list[dict[str, Any]],
    metadata: Mapping[str, Any] | None = None,
    return_metadata: bool = False,
):
    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation=f"destination.generate.{agent}",
        lm=lm,
        signature_cls=GenerateGoldDestinationSignature,
        input_dict={
            "agent": agent,
            "agent_role": AGENT_ROLES[agent],
            "destination_requirements": (
                DESTINATION_REQUIREMENTS[agent]
            ),
            "question": _get(row, "question"),
            "current_output": (
                _get(row, "summary_1")
                if agent == "summary1"
                else _get(row, "summary_2")
            ),
            "upstream_context": dict(upstream_context),
            "visible_gold_support": list(
                visible_gold_support
            ),
            "missing_support_targets": list(
                missing_support_targets
            ),
        },
        lm_config=lm_config,
        metadata={
            "agent": agent,
            **dict(metadata or {}),
        },
        return_cache_hit=True,
    )

    destination = {
        "agent": agent,
        "target_kind": "gold_conditioned",
        "available": True,
        "output": parsed["destination_output"],
        "rationale": parsed["rationale"],
        "gold_answer": _get(row, "gold_answer"),
        "gold_support": gold_support,
        "visible_gold_support": list(
            visible_gold_support
        ),
        "missing_support_targets": list(
            missing_support_targets
        ),
    }

    if return_metadata:
        return (
            destination,
            prompt,
            raw,
            cache_hit,
        )

    return destination


def build_summary1_destination(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    row: Mapping[str, Any],
    metadata: Mapping[str, Any] | None = None,
    return_metadata: bool = False,
):
    gold_support = extract_gold_support(row)
    partition = split_gold_support_for_summary1(
        row,
        gold_support,
    )

    missing_targets = _missing_target_records(
        partition["missing_after_hop1"]
    )

    upstream_context = {
        "question": _get(row, "question"),
        "hop1_query": _get(row, "hop1_query"),
        "hop1_titles": _get(row, "hop1_titles"),
        "hop1_docs": _get(row, "hop1_docs"),
    }

    return _generate_text_destination(
        runtime=runtime,
        lm=lm,
        lm_config=lm_config,
        agent="summary1",
        row=row,
        upstream_context=upstream_context,
        visible_gold_support=(
            partition["visible_in_hop1"]
        ),
        missing_support_targets=missing_targets,
        gold_support=gold_support,
        metadata=metadata,
        return_metadata=return_metadata,
    )


def build_query_destination(
    *,
    row: Mapping[str, Any],
    return_metadata: bool = False,
):
    gold_support = extract_gold_support(row)

    try:
        query, target_titles = make_oracle_query(
            row
        )
    except ValueError as exc:
        destination = _unavailable_destination(
            agent="query",
            target_kind="gold_oracle_query",
            reason=str(exc),
            row=row,
            gold_support=gold_support,
            target_titles=[],
        )

        if return_metadata:
            return destination, None, None, False
        return destination

    destination = {
        "agent": "query",
        "target_kind": "gold_oracle_query",
        "available": True,
        "output": {
            "query": query,
        },
        "rationale": (
            "Constructed with the oracle rule: missing support "
            "titles after hop2 followed by the question."
        ),
        "target_titles": target_titles,
        "gold_answer": _get(row, "gold_answer"),
        "gold_support": gold_support,
    }

    if return_metadata:
        return destination, None, None, False

    return destination


def build_summary2_destination(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    row: Mapping[str, Any],
    summary_1: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    return_metadata: bool = False,
):
    gold_support = extract_gold_support(row)
    partition = split_gold_support_for_summary2(
        row,
        gold_support,
    )
    missing_after_hop2 = (
        get_missing_titles_after_hop2(row)
    )

    if missing_after_hop2:
        destination = _unavailable_destination(
            agent="summary2",
            target_kind="gold_conditioned",
            reason=(
                "Required gold support is absent after the second-hop "
                "retrieval; a supported summary2 destination cannot "
                "be generated at this boundary."
            ),
            row=row,
            gold_support=gold_support,
            missing_support_titles=missing_after_hop2,
            visible_gold_support=(
                partition["visible_in_hop2"]
            ),
        )

        if return_metadata:
            return destination, None, None, False
        return destination

    upstream_context = {
        "question": _get(row, "question"),
        "summary_1": (
            summary_1
            if summary_1 is not None
            else _get(row, "summary_1")
        ),
        "hop2_query": _get(row, "hop2_query"),
        "hop2_titles": _get(row, "hop2_titles"),
        "hop2_docs": _get(row, "hop2_docs"),
    }

    return _generate_text_destination(
        runtime=runtime,
        lm=lm,
        lm_config=lm_config,
        agent="summary2",
        row=row,
        upstream_context=upstream_context,
        visible_gold_support=(
            partition["visible_in_hop2"]
        ),
        missing_support_targets=[],
        gold_support=gold_support,
        metadata=metadata,
        return_metadata=return_metadata,
    )


def _normalize_gold_answer_output(
    gold_answer: Any,
) -> str:
    values = (
        gold_answer
        if isinstance(gold_answer, (list, tuple))
        else [gold_answer]
    )

    for value in values:
        text = str(value or "").strip()
        if text:
            return text

    raise ValueError(
        "The row does not contain a non-empty gold answer."
    )


def build_final_destination(
    *,
    row: Mapping[str, Any],
    return_metadata: bool = False,
):
    gold_support = extract_gold_support(row)
    answer = _normalize_gold_answer_output(
        _get(row, "gold_answer")
    )

    destination = {
        "agent": "final",
        "target_kind": "gold_answer",
        "available": True,
        "output": answer,
        "rationale": (
            "The final-agent destination is the normalized gold answer."
        ),
        "gold_answer": _get(row, "gold_answer"),
        "gold_support": gold_support,
    }

    if return_metadata:
        return destination, None, None, False

    return destination


def build_agent_destination(
    *,
    agent: str,
    row: Mapping[str, Any],
    runtime: OursRuntime | None = None,
    lm: LanguageModel | None = None,
    lm_config: Mapping[str, Any] | None = None,
    summary_1: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    return_metadata: bool = False,
):
    if agent == "query":
        return build_query_destination(
            row=row,
            return_metadata=return_metadata,
        )

    if agent == "final":
        return build_final_destination(
            row=row,
            return_metadata=return_metadata,
        )

    if agent not in {"summary1", "summary2"}:
        raise ValueError(
            f"Unknown agent {agent!r}. "
            f"Expected one of {sorted(AGENT_ROLES)}."
        )

    if runtime is None or lm is None or lm_config is None:
        raise ValueError(
            f"{agent} destination generation requires "
            "runtime, lm, and lm_config."
        )

    if agent == "summary1":
        return build_summary1_destination(
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            row=row,
            metadata=metadata,
            return_metadata=return_metadata,
        )

    return build_summary2_destination(
        runtime=runtime,
        lm=lm,
        lm_config=lm_config,
        row=row,
        summary_1=summary_1,
        metadata=metadata,
        return_metadata=return_metadata,
    )