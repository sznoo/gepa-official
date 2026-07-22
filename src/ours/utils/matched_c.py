# /home/jinwoo/gepa-official/src/ours/utils/matched_c.py
from __future__ import annotations

import hashlib
import json
import random
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from gepa.proposer.reflective_mutation.base import LanguageModel, Signature

from ours.analyze_attribute import AGENT_ORDER, compact_state
from ours.lm import run_signature
from ours.runtime import OursRuntime
from ours.utils.prompt_feedback import (
    AGENT_FUNCTIONS,
    AGENT_OUTPUT_CONTRACTS,
    AGENT_ROLES,
    PROVISIONAL_HYPOTHESIS_FIELDS,
)


SCRIPT_VERSION = "2026-07-16-v2-explicit-candidate-index"

DEFAULT_CHUNK_SIZE = 24
DEFAULT_MAX_CHUNK_CHARS = 90000
DEFAULT_MIN_BOUNDARY_SCORE = 0.55


__all__ = [
    "SCRIPT_VERSION",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_MAX_CHUNK_CHARS",
    "DEFAULT_MIN_BOUNDARY_SCORE",
    "MatchedCSelection",
    "build_correct_case_card",
    "build_w_context_card",
    "select_matched_c_rows",
]


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def _json_dumps(value: Any, *, indent: int | None = 2) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=indent,
        default=str,
        sort_keys=False,
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



_SCORE_TENS = {
    "ten": 10,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

_SCORE_ONES = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}


def _normalize_spelled_score_literals(text: str) -> str:
    """
    Recover malformed JSON score literals such as:

        "boundary_match_score": 0. ninety
        "semantic_similarity": 0. eighty-five

    Only the three bounded matched-C score fields are modified.
    """

    score_fields = (
        "boundary_match_score",
        "semantic_similarity",
        "overgeneralization_risk",
    )

    field_pattern = "|".join(
        re.escape(field)
        for field in score_fields
    )

    pattern = re.compile(
        rf'(?P<prefix>"(?:{field_pattern})"\s*:\s*)'
        rf'0\.\s*'
        rf'(?P<words>[A-Za-z]+(?:[\s-]+[A-Za-z]+)?)'
        rf'(?=\s*[,}}])',
        flags=re.IGNORECASE,
    )

    def replace(match: re.Match[str]) -> str:
        words = (
            match.group("words")
            .lower()
            .replace("-", " ")
            .split()
        )

        value: int | None = None

        if len(words) == 1:
            word = words[0]
            if word in _SCORE_TENS:
                value = _SCORE_TENS[word]
            elif word in _SCORE_ONES:
                # "0. nine" is interpreted as 0.9.
                return (
                    match.group("prefix")
                    + f"0.{_SCORE_ONES[word]}"
                )

        elif (
            len(words) == 2
            and words[0] in _SCORE_TENS
            and words[1] in _SCORE_ONES
        ):
            value = (
                _SCORE_TENS[words[0]]
                + _SCORE_ONES[words[1]]
            )

        if value is None:
            return match.group(0)

        return match.group("prefix") + f"{value / 100:.2f}"

    return pattern.sub(replace, text)


def _extract_json_object(text: str) -> dict[str, Any]:
    text = str(text or "").strip()
    text = _normalize_spelled_score_literals(text)

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


def _require_text(value: Any, *, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} cannot be empty.")
    return text


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _bounded_float(value: Any, *, field_name: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{field_name} must be in [0, 1].")
    return number


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


def _truncate_text(value: Any, *, max_chars: int) -> Any:
    if value is None:
        return None
    text = str(value)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 24] + " ...[truncated]"


def _compact_value(
    value: Any,
    *,
    max_text_chars: int = 2400,
    max_items: int = 12,
    depth: int = 0,
) -> Any:
    if value is None or isinstance(value, (bool, int, float)):
        return value

    if isinstance(value, str):
        return _truncate_text(value, max_chars=max_text_chars)

    if depth >= 3:
        return _truncate_text(value, max_chars=max_text_chars)

    if isinstance(value, Mapping):
        return {
            str(key): _compact_value(
                item,
                max_text_chars=max_text_chars,
                max_items=max_items,
                depth=depth + 1,
            )
            for key, item in list(value.items())[:max_items]
        }

    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        compact = [
            _compact_value(
                item,
                max_text_chars=max_text_chars,
                max_items=max_items,
                depth=depth + 1,
            )
            for item in list(value)[:max_items]
        ]
        if len(value) > max_items:
            compact.append(
                f"...[{len(value) - max_items} more items]"
            )
        return compact

    return _truncate_text(value, max_chars=max_text_chars)


def _row_sources(row: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    sources: list[Mapping[str, Any]] = []
    trace = row.get("trace")
    if isinstance(trace, Mapping):
        sources.append(trace)
    sources.append(row)
    return sources


def _first_present(
    row: Mapping[str, Any],
    *keys: str,
) -> Any:
    for source in _row_sources(row):
        for key in keys:
            value = source.get(key)
            if value is not None:
                return value
    return None


def _question(row: Mapping[str, Any]) -> str:
    return _require_text(
        _first_present(row, "question"),
        field_name="correct-row question",
    )


def _gold_answer(row: Mapping[str, Any]) -> Any:
    return _first_present(row, "gold_answer", "answer_gold")


def _summary1(row: Mapping[str, Any]) -> Any:
    return _first_present(
        row,
        "summary_1",
        "summary1",
        "first_summary",
    )


def _query(row: Mapping[str, Any]) -> Any:
    return _first_present(
        row,
        "query",
        "hop2_query",
        "query_hop2",
    )


def _summary2(row: Mapping[str, Any]) -> Any:
    return _first_present(
        row,
        "summary_2",
        "summary2",
        "second_summary",
    )


def _final_answer(row: Mapping[str, Any]) -> Any:
    return _first_present(
        row,
        "answer",
        "prediction",
        "predicted_answer",
    )


def _hop1_context(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "titles": _compact_value(
            _first_present(
                row,
                "hop1_titles",
                "retrieved_titles_hop1",
                "first_hop_titles",
            ),
            max_text_chars=900,
            max_items=8,
        ),
        "passages": _compact_value(
            _first_present(
                row,
                "hop1_docs",
                "hop1_passages",
                "retrieved_passages_hop1",
                "passages_hop1",
            ),
            max_text_chars=1200,
            max_items=4,
        ),
    }


def _hop2_context(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "titles": _compact_value(
            _first_present(
                row,
                "hop2_titles",
                "retrieved_titles_hop2",
                "second_hop_titles",
            ),
            max_text_chars=900,
            max_items=8,
        ),
        "passages": _compact_value(
            _first_present(
                row,
                "hop2_docs",
                "hop2_passages",
                "retrieved_passages_hop2",
                "passages_hop2",
            ),
            max_text_chars=1200,
            max_items=4,
        ),
    }


def _agent_case_view(
    *,
    agent: str,
    row: Mapping[str, Any],
) -> dict[str, Any]:
    question = _question(row)
    summary_1 = _summary1(row)
    query = _query(row)
    summary_2 = _summary2(row)
    answer = _final_answer(row)

    if agent == "summary1":
        return {
            "visible_inputs": {
                "question": question,
                "first_hop": _hop1_context(row),
            },
            "successful_output": _compact_value(
                summary_1,
                max_text_chars=2800,
            ),
        }

    if agent == "query":
        return {
            "visible_inputs": {
                "question": question,
                "summary_1": _compact_value(
                    summary_1,
                    max_text_chars=2800,
                ),
            },
            "successful_output": _compact_value(
                query,
                max_text_chars=900,
            ),
            "retrieval_result": {
                "hop2": _hop2_context(row),
                "support_recall_hop2": _first_present(
                    row,
                    "support_recall_hop2",
                ),
                "missing_recovery_rate": _first_present(
                    row,
                    "missing_recovery_rate",
                ),
            },
        }

    if agent == "summary2":
        return {
            "visible_inputs": {
                "question": question,
                "context": _compact_value(
                    summary_1,
                    max_text_chars=2800,
                ),
                "second_hop": _hop2_context(row),
            },
            "successful_output": _compact_value(
                summary_2,
                max_text_chars=2800,
            ),
        }

    if agent == "final":
        return {
            "visible_inputs": {
                "question": question,
                "summary_1": _compact_value(
                    summary_1,
                    max_text_chars=2800,
                ),
                "summary_2": _compact_value(
                    summary_2,
                    max_text_chars=2800,
                ),
            },
            "successful_output": _compact_value(
                answer,
                max_text_chars=900,
            ),
            "gold_answer": _compact_value(
                _gold_answer(row),
                max_text_chars=900,
            ),
        }

    raise ValueError(f"Unknown agent: {agent!r}.")


# ---------------------------------------------------------------------------
# Public compact cards
# ---------------------------------------------------------------------------


def build_correct_case_card(
    *,
    agent: str,
    eval_position: int,
    row: Mapping[str, Any],
) -> dict[str, Any]:
    if agent not in AGENT_ROLES:
        raise ValueError(f"Unknown agent: {agent!r}.")
    if float(row.get("score") or 0.0) != 1.0:
        raise ValueError(
            "Matched-C candidates must be baseline-correct rows: "
            f"eval_position={eval_position}."
        )

    return {
        "eval_position": int(eval_position),
        "row_index": row.get("index", eval_position),
        "sample_id": row.get("sample_id"),
        "stable_id": _stable_id(row, eval_position),
        "question": _question(row),
        "agent_case": _agent_case_view(
            agent=agent,
            row=row,
        ),
    }


def build_w_context_card(
    *,
    agent: str,
    material: Mapping[str, Any],
) -> dict[str, Any]:
    material_agent = str(material.get("agent") or "").strip()
    if material_agent != agent:
        raise ValueError(
            "Selected W material belongs to the wrong agent: "
            f"expected={agent!r}, actual={material_agent!r}."
        )

    states = list(material.get("states") or [])
    source_state = material.get("source_state")
    destination_state = material.get("destination_state")

    if source_state is None and states:
        source_state = states[0]
    if destination_state is None and states:
        destination_state = states[-1]

    def compact_optional_state(state: Any) -> Any:
        if not isinstance(state, Mapping):
            return None
        try:
            return _compact_value(
                compact_state(agent, state),
                max_text_chars=2400,
            )
        except Exception:
            return _compact_value(
                state,
                max_text_chars=2400,
            )

    return {
        "sample_index": int(material["sample_index"]),
        "stable_id": material.get("stable_id"),
        "question": material.get("question"),
        "gold_answer": material.get("gold_answer"),
        "baseline_answer": material.get("baseline_answer"),
        "source_state": compact_optional_state(source_state),
        "desired_state": compact_optional_state(destination_state),
        "delta_p_directions": [
            {
                "edge_index": int(item.get("edge_index", position)),
                "delta_p": _compact_value(
                    item.get("delta_p"),
                    max_text_chars=1800,
                ),
                "rationale": _compact_value(
                    item.get("rationale"),
                    max_text_chars=900,
                ),
            }
            for position, item in enumerate(
                material.get("delta_p_trace") or []
            )
        ],
    }


# ---------------------------------------------------------------------------
# LM ranking contract
# ---------------------------------------------------------------------------


class RankHypothesisMatchedCorrectCasesSignature(Signature):
    input_keys = [
        "selection_stage",
        "agent",
        "agent_role",
        "agent_function",
        "native_output_contract",
        "provisional_hypothesis",
        "selected_w_context",
        "candidate_correct_cases",
        "max_selections",
    ]
    output_keys = [
        "ranked_candidates",
        "selection_rationale",
        "coverage_assessment",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
You are selecting correct positive cases to test the applicability boundary
of one PROVISIONAL PROMPT-UPDATE HYPOTHESIS for a fixed agent in a
multi-agent HotpotQA pipeline.

The correct cases are not generic demonstrations and are not selected merely
for topical similarity. Select cases that are useful counterexamples to an
over-broad interpretation of the hypothesis.

A high-value matched correct case should satisfy as many of these properties
as possible:
1. It exercises the same agent-level semantic capability or decision as the
   proposed update.
2. Its visible inputs make the provisional update appear superficially
   applicable.
3. Its current successful behavior should nevertheless be preserved because
   the hypothesis's semantic condition is absent, reversed, or importantly
   different.
4. An over-generalized implementation of the proposed update could plausibly
   damage this case.
5. Its value comes from defining a semantic boundary, not from sharing proper
   nouns, punctuation, answer strings, document titles, or incidental lexical
   patterns with the repair cases.

Do not select a case solely because it resembles a repair case. Prefer a
semantically matched case on the opposite side of the proposed rule's
applicability boundary. It is valid to return fewer than max_selections when
few candidates are genuine boundary counterexamples.

For the final-answer agent, prefer cases that distinguish semantic answer-slot
selection or evidence derivation from mere string trimming. Do not favor a
case merely because it contains commas, parentheses, suffixes, wrappers, or
another lexical form mentioned by the hypothesis.

Selection stage:
{input_dict["selection_stage"]}

Agent:
{input_dict["agent"]}

Agent role:
{input_dict["agent_role"]}

Agent function:
{input_dict["agent_function"]}

Native output contract:
{input_dict["native_output_contract"]}

Provisional hypothesis:
{input_dict["provisional_hypothesis"]}

Repair-case context:
{input_dict["selected_w_context"]}

Candidate correct cases:
{input_dict["candidate_correct_cases"]}

Each candidate object contains both:
- candidate_index: the zero-based index local to this exact candidate list;
- eval_position: the original evaluation-row position.

In ranked_candidates, copy candidate_index exactly from the selected candidate.
Do not invent an index, do not return rank order, and do not return
eval_position as the selection identifier.

Maximum selections:
{input_dict["max_selections"]}

Return strict JSON only:
{{
  "ranked_candidates": [
    {{
      "candidate_index": 0,
      "is_boundary_counterexample": true,
      "boundary_match_score": 0.0,
      "semantic_similarity": 0.0,
      "overgeneralization_risk": 0.0,
      "boundary_relation": "semantic condition that separates this correct case from the repair cases",
      "counterexample_rationale": "why this successful behavior should be preserved and how an over-broad update could damage it"
    }}
  ],
  "selection_rationale": "overall ranking rationale",
  "coverage_assessment": "which parts of the provisional hypothesis are or are not tested by the selected cases"
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        raw_ranked = obj.get("ranked_candidates", [])
        if not isinstance(raw_ranked, list):
            raise TypeError("ranked_candidates must be a JSON list.")

        ranked = []
        seen_references: set[tuple[str, int]] = set()

        for position, item in enumerate(raw_ranked):
            if not isinstance(item, Mapping):
                raise TypeError(
                    "Each ranked_candidates item must be a JSON object."
                )

            candidate_index = item.get("candidate_index")
            eval_position = item.get("eval_position")

            if candidate_index is None and eval_position is None:
                raise ValueError(
                    "Each ranked candidate must contain candidate_index. "
                    "Legacy eval_position-only output is accepted only when "
                    "eval_position is present."
                )

            if candidate_index is not None:
                candidate_index = int(candidate_index)
                reference = ("candidate_index", candidate_index)
            else:
                eval_position = int(eval_position)
                reference = ("eval_position", eval_position)

            if reference in seen_references:
                raise ValueError(
                    "ranked_candidates contains a duplicate candidate "
                    f"reference: {reference}."
                )
            seen_references.add(reference)

            boundary_flag = item.get("is_boundary_counterexample")
            if not isinstance(boundary_flag, bool):
                raise TypeError(
                    "is_boundary_counterexample must be a JSON boolean at "
                    f"ranked_candidates[{position}]."
                )

            ranked.append({
                "candidate_index": candidate_index,
                "eval_position": (
                    int(eval_position)
                    if eval_position is not None
                    else None
                ),
                "is_boundary_counterexample": boundary_flag,
                "boundary_match_score": _bounded_float(
                    item.get("boundary_match_score", 0.0),
                    field_name=(
                        "ranked_candidates"
                        f"[{position}].boundary_match_score"
                    ),
                ),
                "semantic_similarity": _bounded_float(
                    item.get("semantic_similarity", 0.0),
                    field_name=(
                        "ranked_candidates"
                        f"[{position}].semantic_similarity"
                    ),
                ),
                "overgeneralization_risk": _bounded_float(
                    item.get("overgeneralization_risk", 0.0),
                    field_name=(
                        "ranked_candidates"
                        f"[{position}].overgeneralization_risk"
                    ),
                ),
                "boundary_relation": _require_text(
                    item.get("boundary_relation"),
                    field_name=(
                        "ranked_candidates"
                        f"[{position}].boundary_relation"
                    ),
                ),
                "counterexample_rationale": _require_text(
                    item.get("counterexample_rationale"),
                    field_name=(
                        "ranked_candidates"
                        f"[{position}].counterexample_rationale"
                    ),
                ),
            })

        selection_rationale = str(
            obj.get("selection_rationale") or ""
        ).strip()

        if not selection_rationale:
            selection_rationale = (
                "The LM returned ranked candidates without an explicit "
                "overall selection rationale."
            )

        coverage_assessment = str(
            obj.get("coverage_assessment") or ""
        ).strip()

        if not coverage_assessment:
            coverage_assessment = (
                "The LM returned no explicit hypothesis-coverage "
                "assessment."
            )

        return {
            "ranked_candidates": ranked,
            "selection_rationale": selection_rationale,
            "coverage_assessment": coverage_assessment,
        }



# ---------------------------------------------------------------------------
# Selection result
# ---------------------------------------------------------------------------


def _row_ref(
    eval_position: int,
    row: Mapping[str, Any],
    *,
    selection_kind: str,
) -> dict[str, Any]:
    return {
        "eval_position": int(eval_position),
        "row_index": row.get("index", eval_position),
        "sample_id": row.get("sample_id"),
        "stable_id": _stable_id(row, eval_position),
        "selection_kind": selection_kind,
    }


@dataclass
class MatchedCSelection:
    agent: str
    requested_k: int
    selected_rows: list[tuple[int, dict[str, Any]]]
    matched_rows: list[tuple[int, dict[str, Any]]]
    fallback_rows: list[tuple[int, dict[str, Any]]]
    rankings: list[dict[str, Any]]
    rationale: str
    coverage_assessment: str
    provisional_hypothesis_hash: str
    candidate_pool_hash: str
    lm_traces: list[dict[str, Any]] = field(default_factory=list)

    @property
    def effective_k(self) -> int:
        return len(self.selected_rows)

    def to_manifest(self) -> dict[str, Any]:
        return {
            "script_version": SCRIPT_VERSION,
            "agent": self.agent,
            "requested_k": int(self.requested_k),
            "effective_k": int(self.effective_k),
            "matched_count": len(self.matched_rows),
            "fallback_count": len(self.fallback_rows),
            "selected_c": [
                _row_ref(
                    eval_position,
                    row,
                    selection_kind=(
                        "matched_boundary"
                        if any(
                            eval_position == matched_position
                            for matched_position, _ in self.matched_rows
                        )
                        else "fallback_preservation"
                    ),
                )
                for eval_position, row in self.selected_rows
            ],
            "matched_c": [
                _row_ref(
                    eval_position,
                    row,
                    selection_kind="matched_boundary",
                )
                for eval_position, row in self.matched_rows
            ],
            "fallback_c": [
                _row_ref(
                    eval_position,
                    row,
                    selection_kind="fallback_preservation",
                )
                for eval_position, row in self.fallback_rows
            ],
            "rankings": self.rankings,
            "selection_rationale": self.rationale,
            "coverage_assessment": self.coverage_assessment,
            "provisional_hypothesis_hash": (
                self.provisional_hypothesis_hash
            ),
            "candidate_pool_hash": self.candidate_pool_hash,
        }


# ---------------------------------------------------------------------------
# Ranking execution
# ---------------------------------------------------------------------------


def _validate_provisional_hypothesis(
    hypothesis: Mapping[str, Any],
) -> dict[str, Any]:
    missing = [
        field_name
        for field_name in PROVISIONAL_HYPOTHESIS_FIELDS
        if field_name not in hypothesis
    ]
    if missing:
        raise ValueError(
            "Provisional hypothesis is missing required fields: "
            f"{missing}."
        )

    payload = {
        field_name: hypothesis.get(field_name)
        for field_name in PROVISIONAL_HYPOTHESIS_FIELDS
    }

    for field_name in (
        "failure_mechanism",
        "semantic_condition",
        "proposed_update_direction",
        "expected_behavior_change",
        "potential_overgeneralization",
    ):
        payload[field_name] = _require_text(
            payload[field_name],
            field_name=field_name,
        )

    for field_name in (
        "counterexample_search_criteria",
        "rejected_surface_patterns",
    ):
        value = payload[field_name]
        if not isinstance(value, list):
            raise TypeError(f"{field_name} must be a JSON list.")
        payload[field_name] = [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if not isinstance(payload["new_capability_required"], bool):
        raise TypeError(
            "new_capability_required must be a JSON boolean."
        )
    payload["confidence"] = _bounded_float(
        payload["confidence"],
        field_name="confidence",
    )
    return payload


def _partition_cards(
    cards: Sequence[Mapping[str, Any]],
    *,
    chunk_size: int,
    max_chunk_chars: int,
) -> list[list[dict[str, Any]]]:
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1.")
    if max_chunk_chars < 1000:
        raise ValueError("max_chunk_chars must be >= 1000.")

    chunks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []

    for source_card in cards:
        card = dict(source_card)
        proposed = current + [card]
        proposed_chars = len(_json_dumps(proposed))

        if current and (
            len(current) >= chunk_size
            or proposed_chars > max_chunk_chars
        ):
            chunks.append(current)
            current = [card]
        else:
            current = proposed

        if len(_json_dumps(current)) > max_chunk_chars:
            raise ValueError(
                "One compact correct-case card exceeds max_chunk_chars: "
                f"eval_position={card.get('eval_position')}, "
                f"max_chunk_chars={max_chunk_chars}."
            )

    if current:
        chunks.append(current)
    return chunks


def _run_ranking_call(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent: str,
    selection_stage: str,
    hypothesis_payload: Mapping[str, Any],
    w_cards: Sequence[Mapping[str, Any]],
    candidate_cards: Sequence[Mapping[str, Any]],
    max_selections: int,
    metadata: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    indexed_candidate_cards = [
        {
            "candidate_index": index,
            **dict(card),
        }
        for index, card in enumerate(candidate_cards)
    ]
    index_to_position = {
        int(card["candidate_index"]): int(card["eval_position"])
        for card in indexed_candidate_cards
    }
    allowed_positions = set(index_to_position.values())

    parsed, rendered_prompt, raw_output, cache_hit = run_signature(
        runtime=runtime,
        operation=(
            "prompt_update.matched_c_rank."
            f"{SCRIPT_VERSION}.{agent}.{selection_stage}"
        ),
        lm=lm,
        signature_cls=RankHypothesisMatchedCorrectCasesSignature,
        input_dict={
            "selection_stage": selection_stage,
            "agent": agent,
            "agent_role": AGENT_ROLES[agent],
            "agent_function": AGENT_FUNCTIONS[agent],
            "native_output_contract": (
                AGENT_OUTPUT_CONTRACTS[agent]
            ),
            "provisional_hypothesis": _json_dumps(
                hypothesis_payload
            ),
            "selected_w_context": _json_dumps(list(w_cards)),
            "candidate_correct_cases": _json_dumps(
                indexed_candidate_cards
            ),
            "max_selections": int(max_selections),
        },
        lm_config=lm_config,
        metadata={
            "script_version": SCRIPT_VERSION,
            "stage": "matched_c_ranking",
            "selection_stage": selection_stage,
            "agent": agent,
            "candidate_eval_positions": sorted(allowed_positions),
            **dict(metadata),
        },
        return_cache_hit=True,
    )

    ranked = list(parsed["ranked_candidates"])
    if len(ranked) > max_selections:
        ranked = ranked[:max_selections]

    normalized_ranked: list[dict[str, Any]] = []
    seen_positions: set[int] = set()

    for source_item in ranked:
        item = dict(source_item)
        candidate_index = item.get("candidate_index")
        raw_eval_position = item.get("eval_position")

        if candidate_index is not None:
            candidate_index = int(candidate_index)
            if candidate_index not in index_to_position:
                raise ValueError(
                    "Matched-C selector chose an unknown candidate_index: "
                    f"selected={candidate_index}, "
                    f"allowed={sorted(index_to_position)}."
                )
            eval_position = index_to_position[candidate_index]
            reference_mode = "candidate_index"
        elif raw_eval_position is not None:
            raw_eval_position = int(raw_eval_position)

            if raw_eval_position in allowed_positions:
                eval_position = raw_eval_position
                candidate_index = next(
                    index
                    for index, position in index_to_position.items()
                    if position == eval_position
                )
                reference_mode = "legacy_eval_position"
            elif raw_eval_position in index_to_position:
                # Backward-compatible recovery for the v1 prompt, whose
                # schema example encouraged models to return a local index
                # under the eval_position field.
                candidate_index = raw_eval_position
                eval_position = index_to_position[candidate_index]
                reference_mode = "legacy_local_index_recovered"
            else:
                raise ValueError(
                    "Matched-C selector chose an unknown eval position: "
                    f"selected={raw_eval_position}, "
                    f"allowed={sorted(allowed_positions)}."
                )
        else:
            raise ValueError(
                "Matched-C selector returned neither candidate_index nor "
                "eval_position."
            )

        if eval_position in seen_positions:
            raise ValueError(
                "Matched-C selector returned duplicate candidates after "
                f"normalization: eval_position={eval_position}."
            )
        seen_positions.add(eval_position)

        item["candidate_index"] = int(candidate_index)
        item["eval_position"] = int(eval_position)
        item["selection_reference_mode"] = reference_mode
        normalized_ranked.append(item)

    parsed = {
        **parsed,
        "ranked_candidates": normalized_ranked,
    }
    trace = {
        "selection_stage": selection_stage,
        "rendered_prompt": rendered_prompt,
        "raw_output": raw_output,
        "cache_hit": cache_hit,
    }
    return parsed, trace



def _ranking_score(item: Mapping[str, Any]) -> tuple[float, float, float]:
    return (
        float(item.get("boundary_match_score", 0.0)),
        float(item.get("overgeneralization_risk", 0.0)),
        float(item.get("semantic_similarity", 0.0)),
    )


def _deduplicate_rankings(
    rankings: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    best: dict[int, dict[str, Any]] = {}

    for source in rankings:
        item = dict(source)
        position = int(item["eval_position"])
        previous = best.get(position)
        if previous is None or _ranking_score(item) > _ranking_score(previous):
            best[position] = item

    return sorted(
        best.values(),
        key=lambda item: (
            -_ranking_score(item)[0],
            -_ranking_score(item)[1],
            -_ranking_score(item)[2],
            int(item["eval_position"]),
        ),
    )


def select_matched_c_rows(
    *,
    agent: str,
    provisional_hypothesis: Mapping[str, Any],
    selected_w: Sequence[Mapping[str, Any]],
    correct_pool: Sequence[tuple[int, Mapping[str, Any]]],
    k: int,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    seed: int,
    excluded_eval_positions: Sequence[int] | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS,
    min_boundary_score: float = DEFAULT_MIN_BOUNDARY_SCORE,
    fill_with_fallback: bool = True,
) -> MatchedCSelection:
    """
    Select correct C rows after a W-only provisional hypothesis exists.

    Selection is performed in two ranking levels:
      1. rank each compact chunk of the correct pool;
      2. rerank the union of chunk finalists when it exceeds k.

    Only rows explicitly marked as boundary counterexamples and meeting
    min_boundary_score count as matched C. If fewer than k matched rows are
    found and fill_with_fallback=True, deterministic preservation C rows fill
    the remaining budget. The result records matched and fallback rows
    separately.
    """
    if agent not in AGENT_ROLES:
        raise ValueError(f"Unknown agent: {agent!r}.")
    if k < 1:
        raise ValueError("k must be >= 1.")
    if not 0.0 <= min_boundary_score <= 1.0:
        raise ValueError("min_boundary_score must be in [0, 1].")
    if not selected_w:
        raise ValueError(
            "Matched-C selection requires at least one selected W material."
        )

    hypothesis_payload = _validate_provisional_hypothesis(
        provisional_hypothesis
    )
    hypothesis_hash = _canonical_hash(hypothesis_payload)

    excluded = {
        int(position)
        for position in (excluded_eval_positions or [])
    }
    eligible_rows: list[tuple[int, dict[str, Any]]] = []
    seen_positions: set[int] = set()

    for eval_position, source_row in correct_pool:
        eval_position = int(eval_position)
        if eval_position in excluded:
            continue
        if eval_position in seen_positions:
            raise ValueError(
                "correct_pool contains duplicate eval_position: "
                f"{eval_position}."
            )
        seen_positions.add(eval_position)

        row = dict(source_row)
        if float(row.get("score") or 0.0) != 1.0:
            raise ValueError(
                "correct_pool contains a non-correct row at "
                f"eval_position={eval_position}."
            )
        eligible_rows.append((eval_position, row))

    if len(eligible_rows) < k:
        raise ValueError(
            f"Need at least {k} eligible correct rows, "
            f"found {len(eligible_rows)}."
        )

    cards = [
        build_correct_case_card(
            agent=agent,
            eval_position=eval_position,
            row=row,
        )
        for eval_position, row in eligible_rows
    ]
    candidate_pool_hash = _canonical_hash(cards)
    cards_by_position = {
        int(card["eval_position"]): card
        for card in cards
    }
    rows_by_position = {
        int(eval_position): row
        for eval_position, row in eligible_rows
    }
    w_cards = [
        build_w_context_card(
            agent=agent,
            material=material,
        )
        for material in selected_w
    ]

    chunks = _partition_cards(
        cards,
        chunk_size=chunk_size,
        max_chunk_chars=max_chunk_chars,
    )

    all_rankings: list[dict[str, Any]] = []
    chunk_rationales: list[str] = []
    chunk_coverages: list[str] = []
    lm_traces: list[dict[str, Any]] = []

    for chunk_index, chunk in enumerate(chunks):
        parsed, trace = _run_ranking_call(
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            agent=agent,
            selection_stage=(
                f"chunk_{chunk_index + 1}_of_{len(chunks)}"
            ),
            hypothesis_payload=hypothesis_payload,
            w_cards=w_cards,
            candidate_cards=chunk,
            max_selections=min(k, len(chunk)),
            metadata={
                "chunk_index": chunk_index,
                "num_chunks": len(chunks),
                "provisional_hypothesis_hash": hypothesis_hash,
                "candidate_pool_hash": candidate_pool_hash,
            },
        )
        lm_traces.append(trace)
        chunk_rationales.append(parsed["selection_rationale"])
        chunk_coverages.append(parsed["coverage_assessment"])

        for rank_index, source_item in enumerate(
            parsed["ranked_candidates"]
        ):
            item = dict(source_item)
            item.update({
                "ranking_stage": "chunk",
                "chunk_index": chunk_index,
                "chunk_rank": rank_index,
            })
            all_rankings.append(item)

    finalists = _deduplicate_rankings(all_rankings)

    if len(finalists) > k:
        finalist_cards = []
        for finalist in finalists:
            eval_position = int(finalist["eval_position"])
            card = dict(cards_by_position[eval_position])
            card["prior_ranking"] = {
                key: finalist.get(key)
                for key in (
                    "is_boundary_counterexample",
                    "boundary_match_score",
                    "semantic_similarity",
                    "overgeneralization_risk",
                    "boundary_relation",
                    "counterexample_rationale",
                )
            }
            finalist_cards.append(card)

        parsed, trace = _run_ranking_call(
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            agent=agent,
            selection_stage="finalist_rerank",
            hypothesis_payload=hypothesis_payload,
            w_cards=w_cards,
            candidate_cards=finalist_cards,
            max_selections=k,
            metadata={
                "num_finalists": len(finalist_cards),
                "provisional_hypothesis_hash": hypothesis_hash,
                "candidate_pool_hash": candidate_pool_hash,
            },
        )
        lm_traces.append(trace)
        final_rationale = parsed["selection_rationale"]
        final_coverage = parsed["coverage_assessment"]
        final_rankings = []
        for rank_index, source_item in enumerate(
            parsed["ranked_candidates"]
        ):
            item = dict(source_item)
            item.update({
                "ranking_stage": "finalist_rerank",
                "final_rank": rank_index,
            })
            final_rankings.append(item)
    else:
        final_rankings = finalists[:k]
        final_rationale = (
            "Chunk-level ranking produced no more than the requested "
            "number of unique finalists; finalists were ordered by "
            "boundary score, overgeneralization risk, and semantic "
            "similarity without an additional LM rerank."
        )
        final_coverage = " | ".join(chunk_coverages)

    eligible_matched_rankings = [
        dict(item)
        for item in final_rankings
        if item.get("is_boundary_counterexample") is True
        and float(item.get("boundary_match_score", 0.0))
        >= min_boundary_score
    ]
    eligible_matched_rankings = _deduplicate_rankings(
        eligible_matched_rankings
    )[:k]

    matched_positions = [
        int(item["eval_position"])
        for item in eligible_matched_rankings
    ]
    matched_rows = [
        (position, dict(rows_by_position[position]))
        for position in matched_positions
    ]

    fallback_rows: list[tuple[int, dict[str, Any]]] = []
    if fill_with_fallback and len(matched_rows) < k:
        remaining_positions = [
            int(eval_position)
            for eval_position, _ in eligible_rows
            if int(eval_position) not in set(matched_positions)
        ]
        agent_offset = AGENT_ORDER.index(agent) + 1
        fallback_rng = random.Random(
            int(seed) + 104729 * agent_offset
        )
        fallback_rng.shuffle(remaining_positions)
        needed = k - len(matched_rows)
        fallback_rows = [
            (position, dict(rows_by_position[position]))
            for position in remaining_positions[:needed]
        ]

    selected_rows = matched_rows + fallback_rows
    if len(selected_rows) != k:
        raise RuntimeError(
            "Matched-C selection did not satisfy the requested C budget: "
            f"requested={k}, selected={len(selected_rows)}, "
            f"matched={len(matched_rows)}, fallback={len(fallback_rows)}."
        )

    ranking_log = _deduplicate_rankings(
        list(all_rankings) + list(final_rankings)
    )

    rationale_parts = [final_rationale]
    if chunk_rationales:
        rationale_parts.append(
            "Chunk assessments: " + " | ".join(chunk_rationales)
        )
    if fallback_rows:
        rationale_parts.append(
            f"Only {len(matched_rows)} valid boundary matches met "
            f"the score threshold {min_boundary_score:.2f}; "
            f"{len(fallback_rows)} deterministic preservation cases "
            "filled the remaining budget."
        )

    return MatchedCSelection(
        agent=agent,
        requested_k=int(k),
        selected_rows=selected_rows,
        matched_rows=matched_rows,
        fallback_rows=fallback_rows,
        rankings=ranking_log,
        rationale=" ".join(rationale_parts),
        coverage_assessment=final_coverage,
        provisional_hypothesis_hash=hypothesis_hash,
        candidate_pool_hash=candidate_pool_hash,
        lm_traces=lm_traces,
    )