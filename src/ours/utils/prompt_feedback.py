from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from gepa.proposer.reflective_mutation.base import LanguageModel, Signature

from ours.analyze_attribute import (
    AGENT_ROLES,
    AGENT_TO_PROMPT_KEY,
)
from ours.lm import run_signature
from ours.prompts import render_method_prompt
from ours.runtime import OursRuntime


SCRIPT_VERSION = "2026-07-16-v8-hypothesis-conditioned-c-ready"

COUNTEREXAMPLE_REVISION_PROMPT_VERSION = (
    "2026-07-16-v2-composition-preserving"
)

PROMPT_REWRITE_PROMPT_VERSION = (
    "2026-07-16-v2-minimal-composition-preserving"
)

FEEDBACK_CANDIDATE_GENERATION_PROMPT_VERSION = (
    "2026-07-16-v0-multi-candidate-delta-p"
)

FEEDBACK_NORM_SELECTION_PROMPT_VERSION = (
    "2026-07-16-v0-agent-semantic-order"
)


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


PROVISIONAL_HYPOTHESIS_FIELDS = (
    "failure_mechanism",
    "semantic_condition",
    "proposed_update_direction",
    "expected_behavior_change",
    "potential_overgeneralization",
    "counterexample_search_criteria",
    "rejected_surface_patterns",
    "new_capability_required",
    "confidence",
)


INTEGRATED_FEEDBACK_FIELDS = (
    "integrated_feedback",
    "update_directions",
    "preservation_constraints",
    "edit_recommendations",
    "rejected_local_patterns",
    "new_capability_required",
    "length_increase_justified",
    "generalization_rationale",
    "generalization_check",
)


REVISED_FEEDBACK_METADATA_FIELDS = (
    "hypothesis_decision",
    "semantic_boundary",
    "counterexample_analysis",
)


HYPOTHESIS_DECISIONS = frozenset({
    "retain",
    "narrow",
    "replace",
    "reject",
})


HYPOTHESIS_DECISION_ALIASES = {
    # The LM occasionally copies the edit-action vocabulary into the
    # hypothesis-decision field. Clarifying the applicability boundary
    # corresponds to narrowing the provisional hypothesis.
    "clarify": "narrow",
}


EDIT_ACTIONS = frozenset({
    "clarify",
    "merge",
    "replace",
    "add",
    "keep",
})


EDIT_ACTION_ALIASES = {
    # `narrow` is a valid hypothesis decision, but not a separate
    # canonical edit operation. Narrowing an existing instruction is
    # represented as clarification of its applicability boundary.
    "narrow": "clarify",
}


FEEDBACK_NORM_METHOD_PROMPTS = {
    "final": "feedback_norm_1n_final_v0",
    "summary2": "feedback_norm_1n_summary2_v0",
    "query": "feedback_norm_1n_query_v0",
    "summary1": "feedback_norm_1n_summary1_v0",
}


__all__ = [
    "SCRIPT_VERSION",
    "COUNTEREXAMPLE_REVISION_PROMPT_VERSION",
    "PROMPT_REWRITE_PROMPT_VERSION",
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
    "evidence_mode_for_condition",
    "generate_provisional_hypothesis",
    "revise_hypothesis_with_positive_cases",
    "generate_candidate_feedbacks_with_positive_cases",
    "select_minimum_norm_feedback",
    "synthesize_batch_feedback",
    "update_agent_prompt",
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

# ---------------------------------------------------------------------------
# Hypothesis, counterexample revision, feedback synthesis, and rewrite
# ---------------------------------------------------------------------------


def _text_list(
    obj: Mapping[str, Any],
    key: str,
) -> list[str]:
    value = obj.get(key, [])
    if not isinstance(value, list):
        raise TypeError(
            f"{key} must be a JSON list."
        )
    return [
        str(item).strip()
        for item in value
        if str(item).strip()
    ]


def _bool_field(
    obj: Mapping[str, Any],
    key: str,
) -> bool:
    value = obj.get(key)
    if not isinstance(value, bool):
        raise TypeError(
            f"{key} must be a JSON boolean."
        )
    return value


def _edit_recommendations(
    obj: Mapping[str, Any],
) -> list[dict[str, str]]:
    value = obj.get("edit_recommendations", [])
    if not isinstance(value, list):
        raise TypeError(
            "edit_recommendations must be a JSON list."
        )

    recommendations = []
    for position, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise TypeError(
                "Each edit_recommendations item must "
                "be a JSON object."
            )

        raw_action = str(
            item.get("action") or ""
        ).strip().lower()

        action = EDIT_ACTION_ALIASES.get(
            raw_action,
            raw_action,
        )

        if action not in EDIT_ACTIONS:
            raise ValueError(
                "Unknown edit action at position "
                f"{position}: {raw_action!r}."
            )

        recommendations.append({
            "action": action,
            "target_behavior": _require_text(
                item.get("target_behavior"),
                field=(
                    "edit_recommendations"
                    f"[{position}].target_behavior"
                ),
            ),
            "proposed_change": str(
                item.get("proposed_change") or ""
            ).strip(),
            "reason": _require_text(
                item.get("reason"),
                field=(
                    "edit_recommendations"
                    f"[{position}].reason"
                ),
            ),
        })

    return recommendations


def _confidence_field(
    obj: Mapping[str, Any],
    key: str = "confidence",
) -> float:
    value = float(obj.get(key, 0.0))
    if not 0.0 <= value <= 1.0:
        raise ValueError(
            f"{key} must be in [0, 1], got {value}."
        )
    return value


def _hypothesis_decision(
    obj: Mapping[str, Any],
) -> str:
    raw_decision = str(
        obj.get("hypothesis_decision") or ""
    ).strip().lower()

    decision = HYPOTHESIS_DECISION_ALIASES.get(
        raw_decision,
        raw_decision,
    )

    # Recover adjacent edit-action vocabulary emitted by the LM.
    if raw_decision == "add":
        decision = "narrow"

    # Recover an enum-choice string copied verbatim by the LM.
    compact_decision = raw_decision.replace(" ", "")
    if compact_decision in {"retain|narrow", "narrow|retain"}:
        decision = "narrow"

    if decision not in HYPOTHESIS_DECISIONS:
        raise ValueError(
            "hypothesis_decision must be one of "
            f"{sorted(HYPOTHESIS_DECISIONS)}, "
            f"got {raw_decision!r}."
        )

    return decision


def _provisional_hypothesis_payload(
    row: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        key: row.get(key)
        for key in PROVISIONAL_HYPOTHESIS_FIELDS
    }


class WOnlyProvisionalHypothesisSignature(Signature):
    input_keys = [
        "condition",
        "agent",
        "agent_role",
        "agent_function",
        "native_output_contract",
        "base_prompt",
        "evidence_mode",
        "w_evidence",
    ]
    output_keys = list(PROVISIONAL_HYPOTHESIS_FIELDS)

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
You are proposing one PROVISIONAL UPDATE HYPOTHESIS for one agent in a
fixed multi-agent HotpotQA pipeline.

This stage sees only repair evidence from currently failing cases. It does
not see positive counterexamples yet. Therefore, do not write the updated
prompt and do not claim that the proposed change is already safe or final.

Your task is to identify the smallest semantic failure mechanism that
coherently explains the repair evidence and to describe what kinds of
currently-correct cases would be most informative for testing whether the
hypothesis overgeneralizes.

Abstraction requirements:
- State the failure in terms of semantic roles, evidence use, relation
  composition, answer-slot selection, retrieval intent, uncertainty, or the
  agent's native responsibility.
- Do not define the hypothesis by sample-specific names, answers, question
  strings, document titles, page titles, locations, acronyms, copied phrases,
  punctuation templates, wrapper syntax, token positions, or enumerated
  answer types.
- Do not produce one rule per case.
- Treat recurring lexical forms as symptoms unless the evidence establishes
  that formatting itself is the true failure mechanism.
- The proposed direction must preserve the native input/output interface and
  the agent's pipeline role.
- If the evidence supports multiple interpretations, choose the smallest
  coherent hypothesis and lower confidence rather than enumerating local
  fixes.
- ``counterexample_search_criteria`` must describe semantic properties of
  correct cases that would expose an overly broad version of the hypothesis.
  These criteria will be used by a later matched-C selector.
- ``rejected_surface_patterns`` must list tempting case-specific shortcuts
  that should not be promoted into shared prompt rules.

For the final-answer agent:
- Distinguish relation derivation or semantic answer-slot errors from genuine
  serialization-only errors.
- Do not propose substring, punctuation, suffix-removal, wrapper-removal, or
  answer-type-specific extraction rules unless the repair evidence proves
  that the semantic answer was already correctly derived and only the fixed
  output serialization was wrong.

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

Current base prompt:
{input_dict["base_prompt"]}

Evidence mode:
{input_dict["evidence_mode"]}

W-only repair evidence:
{input_dict["w_evidence"]}

Return strict JSON only:
{{
  "failure_mechanism": "one compact semantic diagnosis",
  "semantic_condition": "the semantic condition under which behavior should change",
  "proposed_update_direction": "one provisional reusable behavioral change",
  "expected_behavior_change": "how the agent's behavior should change when the condition holds",
  "potential_overgeneralization": "how an overly broad form of the hypothesis could damage correct behavior",
  "counterexample_search_criteria": [
    "semantic property of a currently-correct case that would test the proposed boundary"
  ],
  "rejected_surface_patterns": [
    "tempting lexical or case-specific shortcut that must not become a rule"
  ],
  "new_capability_required": false,
  "confidence": 0.0
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        criteria = _text_list(
            obj,
            "counterexample_search_criteria",
        )
        if not criteria:
            raise ValueError(
                "counterexample_search_criteria must contain "
                "at least one semantic criterion."
            )

        return {
            "failure_mechanism": _require_text(
                obj.get("failure_mechanism"),
                field="failure_mechanism",
            ),
            "semantic_condition": _require_text(
                obj.get("semantic_condition"),
                field="semantic_condition",
            ),
            "proposed_update_direction": _require_text(
                obj.get("proposed_update_direction"),
                field="proposed_update_direction",
            ),
            "expected_behavior_change": _require_text(
                obj.get("expected_behavior_change"),
                field="expected_behavior_change",
            ),
            "potential_overgeneralization": _require_text(
                obj.get("potential_overgeneralization"),
                field="potential_overgeneralization",
            ),
            "counterexample_search_criteria": criteria,
            "rejected_surface_patterns": _text_list(
                obj,
                "rejected_surface_patterns",
            ),
            "new_capability_required": _bool_field(
                obj,
                "new_capability_required",
            ),
            "confidence": _confidence_field(obj),
        }


class CounterexampleRevisionSignature(Signature):
    input_keys = [
        "condition",
        "agent",
        "agent_role",
        "agent_function",
        "native_output_contract",
        "base_prompt",
        "evidence_mode",
        "provisional_hypothesis",
        "w_evidence",
        "matched_c_evidence",
    ]
    output_keys = [
        *REVISED_FEEDBACK_METADATA_FIELDS,
        *INTEGRATED_FEEDBACK_FIELDS,
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
You are revising one provisional prompt-update hypothesis after seeing
hypothesis-matched positive counterexamples for one agent in a fixed
multi-agent HotpotQA pipeline.

This is an abstraction and edit-planning stage. Do not write the updated
agent prompt.

The provisional hypothesis was inferred from currently failing repair cases.
The matched positive cases test whether that hypothesis can be applied
without removing behavior that is already correct.

Choose exactly one decision:
- retain: the same semantic mechanism and applicability boundary remain valid;
- narrow: the core mechanism is valid, but its applicability condition must
  be restricted without removing valid existing capability;
- replace: a different compact semantic mechanism better explains both the
  repair and preservation evidence;
- reject: no coherent reusable and capability-preserving update remains, so
  the current base prompt should be preserved.

Core distinction: unsupported inference versus licensed composition
- Unsupported inference introduces a fact, entity identity, relation, or
  answer that is not licensed by the visible evidence.
- Licensed composition combines multiple visible, identity-aligned facts
  according to the relation requested by the question.
- A conclusion may be licensed even when no single passage states the entire
  final relation in one direct sentence.
- Do not require a single-passage direct predication when the necessary
  premises and identity links are explicitly visible across the supplied
  states.
- Do not treat ordinary multi-hop composition, comparison, transitive
  relation resolution, alias alignment, or answer extraction as unsupported
  merely because more than one visible fact is required.
- Preserve uncertainty only when a required premise, identity link, or
  relation is genuinely absent or conflicting.

How to use the matched positive cases
- Treat each positive case as evidence about the semantic applicability
  boundary, not as a command to freeze every surface behavior it exhibits.
- Determine which capability made the positive case succeed and whether the
  provisional update would actually remove or distort that capability.
- Narrow only the part of the provisional hypothesis that causes the
  demonstrated damage.
- Do not narrow by replacing a useful reasoning capability with a stricter
  evidence-acceptance rule.
- If a proposed narrowing would cause derivable multi-hop cases to emit
  uncertainty, discard the narrowing and choose replace or reject.
- If the positive evidence shows only a surface-form difference, do not
  convert that difference into a semantic prohibition.
- A transported C-minus is a diagnostic counterfactual, not proof that every
  behavior resembling it must be prohibited globally.

Semantic-boundary requirements
- State the boundary in terms of available premises, entity alignment,
  requested relation, retrieval need, answer-slot support, or the agent's
  pipeline responsibility.
- The boundary must not be defined mainly by proper names, answer strings,
  punctuation, wrappers, token positions, copied wording, document titles,
  or an enumerated list of observed answer types.
- Do not introduce a direct-statement-only boundary.
- Do not introduce an exhaustive taxonomy of entity types, question types,
  relation types, output formats, or retrieval cases.
- Do not create a new sentinel value, structured output protocol, rigid query
  grammar, or multi-branch decision procedure unless that interface already
  exists in the native contract.
- Do not convert a local counterexample into a global ban on relation words,
  aliases, qualifiers, parentheses, or other lexical forms.

Capability-preservation test
Before returning retain, narrow, or replace, verify all of the following:
1. The revised direction still permits identity-aligned composition of
   multiple visible facts.
2. It does not force uncertainty when the requested answer is logically
   derivable from the visible states.
3. It does not remove useful retrieval anchors or relation terms merely to
   enforce a preferred query shape.
4. It does not replace semantic answer selection with surface normalization.
5. It preserves the native input/output interface and the agent's pipeline
   role.
6. It changes only behavior implicated by the W repair evidence.

If these conditions cannot be satisfied with one compact semantic change,
choose reject.

Edit-planning discipline
- Prefer clarify, merge, or replace over add.
- ``update_directions`` must contain at most one semantic capability change.
- Do not add independent rules for every observed failure or positive case.
- Do not add examples, answer-type lists, retrieval taxonomies, or formatting
  taxonomies to make the rule appear precise.
- A more restrictive policy is not automatically safer.
- When ``new_capability_required`` is false, do not recommend a new prompt
  section or a new output protocol.
- ``length_increase_justified`` should be true only when a genuinely absent
  capability cannot be expressed by replacing or clarifying current text.
- When in doubt between a complex narrowed rule and preserving the current
  behavior, choose reject.

Agent-specific safeguards
- summary1:
  Preserve concise grounded compression and useful bridge information.
  Do not require a larger structured reporting protocol or an exhaustive
  retrieval-priority taxonomy merely to handle selected failures.

- query:
  Optimize for recovery of the missing support evidence. Do not impose one
  rigid noun-phrase grammar, prohibit useful relation terms, or remove
  evidence-grounded anchors solely for stylistic consistency.

- summary2:
  Preserve grounded integration of first-hop and second-hop evidence.
  Permit logically licensed composition across visible, identity-aligned
  facts. Do not require the complete answer relation to appear as one direct
  predication in a single passage.

- final:
  Preserve semantic premise use, relation composition, answer-slot
  identification, conflict handling, and minimal answer emission.
  Do not create taxonomies for parentheses, suffixes, punctuation,
  administrative labels, aliases, answer types, or other surface variants.
  Formatting guidance is justified only when the semantic answer is already
  correct and serialization alone causes the failure.

If ``hypothesis_decision`` is reject:
- return an empty ``update_directions`` list;
- recommend keep-only behavior;
- set ``new_capability_required`` to false;
- set ``length_increase_justified`` to false;
- state that the base prompt should remain unchanged.

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

Current base prompt:
{input_dict["base_prompt"]}

Evidence mode:
{input_dict["evidence_mode"]}

Provisional hypothesis:
{input_dict["provisional_hypothesis"]}

W repair evidence:
{input_dict["w_evidence"]}

Hypothesis-matched positive counterexample evidence:
{input_dict["matched_c_evidence"]}

Return strict JSON only:
{{
  "hypothesis_decision": "retain|narrow|replace|reject",
  "semantic_boundary": "compact semantic condition separating behavior that should change from behavior that should remain unchanged",
  "counterexample_analysis": "how the positive evidence tests the hypothesis while distinguishing unsupported inference from licensed composition",
  "integrated_feedback": "compact unified diagnosis and final capability-preserving edit direction",
  "update_directions": [
    "at most one reusable semantic behavior to change, or an empty list for reject"
  ],
  "preservation_constraints": [
    "existing capability that must remain available after the update"
  ],
  "edit_recommendations": [
    {{
      "action": "clarify|merge|replace|add|keep",
      "target_behavior": "behavior or instruction in the current prompt",
      "proposed_change": "concise recommended revision; empty only for keep",
      "reason": "why this is the smallest capability-preserving edit"
    }}
  ],
  "rejected_local_patterns": [
    "surface heuristic, rigid protocol, or local exception that must not become a shared rule"
  ],
  "new_capability_required": false,
  "length_increase_justified": false,
  "generalization_rationale": "why the direction transfers without blocking valid multi-hop composition",
  "generalization_check": "confirmation that the direction is semantic, compact, and not a sample-indexed rulebook"
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        decision = _hypothesis_decision(obj)

        parsed = {
            "hypothesis_decision": decision,
            "semantic_boundary": _require_text(
                obj.get("semantic_boundary"),
                field="semantic_boundary",
            ),
            "counterexample_analysis": _require_text(
                obj.get("counterexample_analysis"),
                field="counterexample_analysis",
            ),
            "integrated_feedback": _require_text(
                obj.get("integrated_feedback"),
                field="integrated_feedback",
            ),
            "update_directions": _text_list(
                obj,
                "update_directions",
            ),
            "preservation_constraints": _text_list(
                obj,
                "preservation_constraints",
            ),
            "edit_recommendations": _edit_recommendations(obj),
            "rejected_local_patterns": _text_list(
                obj,
                "rejected_local_patterns",
            ),
            "new_capability_required": _bool_field(
                obj,
                "new_capability_required",
            ),
            "length_increase_justified": _bool_field(
                obj,
                "length_increase_justified",
            ),
            "generalization_rationale": _require_text(
                obj.get("generalization_rationale"),
                field="generalization_rationale",
            ),
            "generalization_check": _require_text(
                obj.get("generalization_check"),
                field="generalization_check",
            ),
        }

        if decision == "reject":
            if parsed["update_directions"]:
                raise ValueError(
                    "Rejected hypotheses must return an empty "
                    "update_directions list."
                )
            if parsed["new_capability_required"]:
                raise ValueError(
                    "Rejected hypotheses cannot require a new capability."
                )
            if parsed["length_increase_justified"]:
                raise ValueError(
                    "Rejected hypotheses cannot justify prompt growth."
                )
            non_keep = [
                item
                for item in parsed["edit_recommendations"]
                if item["action"] != "keep"
            ]
            if non_keep:
                raise ValueError(
                    "Rejected hypotheses may only recommend keep actions."
                )

        return parsed



def _candidate_feedback_from_object(
    obj: Mapping[str, Any],
    *,
    position: int,
) -> dict[str, Any]:
    candidate_index_raw = obj.get("candidate_index")
    if isinstance(candidate_index_raw, bool):
        raise TypeError(
            "candidate_index must be an integer, not a boolean."
        )
    try:
        candidate_index = int(candidate_index_raw)
    except (TypeError, ValueError) as exc:
        raise TypeError(
            "candidate_index must be an integer."
        ) from exc
    if candidate_index < 0:
        raise ValueError(
            "candidate_index must be non-negative."
        )

    decision = _hypothesis_decision(obj)
    if decision == "reject":
        raise ValueError(
            "Candidate feedback items must describe non-empty delta-p "
            "updates. Use top-level no_admissible_update=true when no "
            "valid update remains."
        )

    update_directions = _text_list(
        obj,
        "update_directions",
    )
    if len(update_directions) != 1:
        raise ValueError(
            "Each candidate feedback must contain exactly one semantic "
            "update direction; candidate position "
            f"{position} returned {len(update_directions)}."
        )

    return {
        "candidate_index": candidate_index,
        "hypothesis_decision": decision,
        "semantic_boundary": _require_text(
            obj.get("semantic_boundary"),
            field=(
                "candidate_feedbacks"
                f"[{position}].semantic_boundary"
            ),
        ),
        "counterexample_analysis": _require_text(
            obj.get("counterexample_analysis"),
            field=(
                "candidate_feedbacks"
                f"[{position}].counterexample_analysis"
            ),
        ),
        "integrated_feedback": _require_text(
            obj.get("integrated_feedback"),
            field=(
                "candidate_feedbacks"
                f"[{position}].integrated_feedback"
            ),
        ),
        "update_directions": update_directions,
        "preservation_constraints": _text_list(
            obj,
            "preservation_constraints",
        ),
        "edit_recommendations": _edit_recommendations(obj),
        "rejected_local_patterns": _text_list(
            obj,
            "rejected_local_patterns",
        ),
        "new_capability_required": _bool_field(
            obj,
            "new_capability_required",
        ),
        "length_increase_justified": _bool_field(
            obj,
            "length_increase_justified",
        ),
        "generalization_rationale": _require_text(
            obj.get("generalization_rationale"),
            field=(
                "candidate_feedbacks"
                f"[{position}].generalization_rationale"
            ),
        ),
        "generalization_check": _require_text(
            obj.get("generalization_check"),
            field=(
                "candidate_feedbacks"
                f"[{position}].generalization_check"
            ),
        ),
    }


class CandidateCounterexampleRevisionSignature(Signature):
    input_keys = [
        "condition",
        "agent",
        "agent_role",
        "agent_function",
        "native_output_contract",
        "base_prompt",
        "evidence_mode",
        "provisional_hypothesis",
        "w_evidence",
        "matched_c_evidence",
        "num_candidates",
    ]
    output_keys = [
        "no_admissible_update",
        "no_admissible_update_reason",
        "candidate_feedbacks",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
You are generating multiple alternative prompt-feedback updates for one
agent in a fixed multi-agent HotpotQA pipeline.

This is an abstraction and edit-planning stage. Do not write the updated
agent prompt. Do not rank the candidates and do not assign numeric or verbal
magnitude labels such as small, medium, or large.

The provisional hypothesis was inferred from failing repair cases. The
matched positive cases test which existing capability must be preserved.
Generate exactly {input_dict["num_candidates"]} materially distinct candidate
feedback updates that are all admissible under the same evidence.

Admissibility requirements for every candidate:
- It must address the W repair mechanism rather than merely restating the
  observed outputs.
- It must preserve the capability demonstrated by the matched positive cases.
- It must preserve the agent's native role and input/output contract.
- It must contain exactly one coherent semantic update direction.
- It must not depend mainly on proper names, copied wording, punctuation,
  answer strings, document titles, or an enumerated case list.
- It must distinguish unsupported inference from licensed composition of
  visible, identity-aligned facts.
- It must not require one direct sentence to state the entire multi-hop
  relation when the necessary premises and links are visible across states.
- It must not create an exhaustive entity, question, relation, retrieval, or
  answer-format taxonomy.
- It must not add a new sentinel, rigid output protocol, rigid query grammar,
  or multi-branch procedure unless the native interface already requires it.

Candidate diversity requirements:
- Candidates must differ in the semantic behavior they propose changing, the
  semantic applicability boundary, or how the existing instruction should be
  clarified, merged, or replaced.
- Do not generate paraphrases that imply materially equivalent behavior.
- Do not make a candidate longer or more detailed merely to create apparent
  diversity.
- Do not intentionally order candidates from smaller to larger change.
- Do not state which candidate is preferable. A separate agent-specific
  semantic-order judge will select the minimum-norm update.

Agent-specific admissibility:
- summary1: preserve grounded first-hop evidence and useful bridge or
  missing-information signals without expanding into an exhaustive retrieval
  taxonomy.
- query: preserve evidence-grounded anchors and useful relation terms; judge
  queries by the evidence they target, not by one mandatory surface grammar.
- summary2: preserve grounded integration across both hops and permit
  logically licensed composition across explicit identity-aligned premises.
- final: preserve semantic answer selection and emit only the answer required
  by the question; do not replace this with a list of surface-format cases.

If no non-empty semantic update can satisfy all admissibility requirements,
return no_admissible_update=true and an empty candidate_feedbacks list.
Do not include a reject/no-op item among ordinary candidates, because a
separate pipeline path handles preservation of the base prompt.

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

Current base prompt:
{input_dict["base_prompt"]}

Evidence mode:
{input_dict["evidence_mode"]}

Provisional hypothesis:
{input_dict["provisional_hypothesis"]}

W repair evidence:
{input_dict["w_evidence"]}

Hypothesis-matched positive counterexample evidence:
{input_dict["matched_c_evidence"]}

Return strict JSON only:
{{
  "no_admissible_update": false,
  "no_admissible_update_reason": "empty when candidates are returned",
  "candidate_feedbacks": [
    {{
      "candidate_index": 0,
      "hypothesis_decision": "retain|narrow|replace",
      "semantic_boundary": "semantic condition separating behavior that changes from behavior that remains",
      "counterexample_analysis": "how the matched positive evidence constrains this candidate",
      "integrated_feedback": "compact unified diagnosis and edit direction",
      "update_directions": [
        "exactly one reusable semantic behavior to change"
      ],
      "preservation_constraints": [
        "existing capability that must remain available"
      ],
      "edit_recommendations": [
        {{
          "action": "clarify|merge|replace|add|keep",
          "target_behavior": "behavior or instruction in the current prompt",
          "proposed_change": "concise recommended revision; empty only for keep",
          "reason": "why this implements this candidate's semantic boundary"
        }}
      ],
      "rejected_local_patterns": [
        "surface heuristic or local exception that must not become a shared rule"
      ],
      "new_capability_required": false,
      "length_increase_justified": false,
      "generalization_rationale": "why this candidate transfers beyond the selected cases",
      "generalization_check": "confirmation that this is one semantic update rather than a sample-indexed rulebook"
    }}
  ]
}}

Requirements:
- When no_admissible_update is false, return exactly
  {input_dict["num_candidates"]} candidates.
- Candidate indices must be the consecutive integers from 0 through
  {int(input_dict["num_candidates"]) - 1}.
- When no_admissible_update is true, candidate_feedbacks must be empty and
  no_admissible_update_reason must explain why no safe non-empty delta-p
  remains.
- Do not return markdown or additional keys.
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        no_admissible = _bool_field(
            obj,
            "no_admissible_update",
        )
        reason = str(
            obj.get("no_admissible_update_reason") or ""
        ).strip()

        raw_candidates = obj.get("candidate_feedbacks", [])
        if not isinstance(raw_candidates, list):
            raise TypeError(
                "candidate_feedbacks must be a JSON list."
            )

        candidates = [
            _candidate_feedback_from_object(
                item,
                position=position,
            )
            for position, item in enumerate(raw_candidates)
            if isinstance(item, Mapping)
        ]
        if len(candidates) != len(raw_candidates):
            raise TypeError(
                "Each candidate_feedbacks item must be a JSON object."
            )

        if no_admissible:
            if candidates:
                raise ValueError(
                    "no_admissible_update=true requires an empty "
                    "candidate_feedbacks list."
                )
            if not reason:
                raise ValueError(
                    "no_admissible_update_reason is required when no "
                    "admissible update exists."
                )
        else:
            if not candidates:
                raise ValueError(
                    "At least one candidate feedback is required when "
                    "no_admissible_update=false."
                )

        indices = [
            item["candidate_index"]
            for item in candidates
        ]
        if len(indices) != len(set(indices)):
            raise ValueError(
                "candidate_index values must be unique."
            )

        return {
            "no_admissible_update": no_admissible,
            "no_admissible_update_reason": reason,
            "candidate_feedbacks": candidates,
        }


class MinimumNormFeedbackSelectionSignature(Signature):
    input_keys = [
        "agent",
        "base_prompt",
        "candidate_feedbacks",
    ]
    output_keys = [
        "selected_candidate_index",
        "minimum_update_pattern",
        "rationale",
        "confidence",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        agent = str(input_dict["agent"])
        try:
            method_prompt = FEEDBACK_NORM_METHOD_PROMPTS[agent]
        except KeyError as exc:
            raise ValueError(
                f"Unknown agent for feedback norm selection: {agent!r}."
            ) from exc

        return render_method_prompt(
            method_prompt,
            agent=agent,
            base_prompt=input_dict["base_prompt"],
            candidates_json=input_dict["candidate_feedbacks"],
        )

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        selected_raw = obj.get("selected_candidate_index")
        if isinstance(selected_raw, bool):
            raise TypeError(
                "selected_candidate_index must be an integer."
            )
        try:
            selected = int(selected_raw)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "selected_candidate_index must be an integer."
            ) from exc

        return {
            "selected_candidate_index": selected,
            "minimum_update_pattern": _require_text(
                obj.get("minimum_update_pattern"),
                field="minimum_update_pattern",
            ),
            "rationale": _require_text(
                obj.get("rationale"),
                field="rationale",
            ),
            "confidence": _confidence_field(obj),
        }


def generate_provisional_hypothesis(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    condition: str,
    agent: str,
    base_prompt: str,
    w_evidence: Sequence[Mapping[str, Any]],
    max_evidence_chars: int,
) -> dict[str, Any]:
    """
    Propose a W-only hypothesis used by the later matched-C selector.

    This function never rewrites the prompt. Its output is intentionally
    provisional and contains explicit semantic counterexample-search criteria.
    """
    condition = _validate_condition(condition)
    if condition == "base":
        raise ValueError(
            "The base condition must not generate an update hypothesis."
        )
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")

    base_prompt = _require_text(
        base_prompt,
        field="base_prompt",
    )
    evidence_list = [
        dict(item)
        for item in w_evidence
    ]
    if not evidence_list:
        raise ValueError(
            "generate_provisional_hypothesis() requires "
            "at least one W evidence item."
        )

    invalid_kinds = [
        item.get("evidence_kind")
        for item in evidence_list
        if item.get("evidence_kind") != "W_repair"
    ]
    if invalid_kinds:
        raise ValueError(
            "W-only hypothesis generation received non-W evidence: "
            f"{invalid_kinds}."
        )

    base_prompt_hash = _canonical_hash(base_prompt)
    w_evidence_hash = _canonical_hash(evidence_list)
    evidence_json = _json_dumps(evidence_list)
    if len(evidence_json) > max_evidence_chars:
        raise ValueError(
            f"W evidence payload for {condition}/{agent} has "
            f"{len(evidence_json)} chars, exceeding "
            f"max_evidence_chars={max_evidence_chars}."
        )

    evidence_mode = evidence_mode_for_condition(condition)
    provisional_input = {
        "condition": condition,
        "agent": agent,
        "agent_role": AGENT_ROLES[agent],
        "agent_function": AGENT_FUNCTIONS[agent],
        "native_output_contract": AGENT_OUTPUT_CONTRACTS[agent],
        "base_prompt": base_prompt,
        "evidence_mode": evidence_mode,
        "w_evidence": evidence_json,
    }

    provisional_metadata = {
        "script_version": SCRIPT_VERSION,
        "stage": "provisional_hypothesis",
        "condition": condition,
        "agent": agent,
        "n_w_evidence": len(evidence_list),
        "base_prompt_hash": base_prompt_hash,
        "w_evidence_hash": w_evidence_hash,
    }

    base_operation = (
        "prompt_update.provisional_hypothesis."
        f"{SCRIPT_VERSION}.{condition}.{agent}"
    )

    last_error: Exception | None = None

    for hypothesis_attempt in range(3):
        operation = (
            base_operation
            if hypothesis_attempt == 0
            else (
                f"{base_operation}."
                f"retry_{hypothesis_attempt}"
            )
        )

        try:
            parsed, prompt, raw, cache_hit = run_signature(
                runtime=runtime,
                operation=operation,
                lm=lm,
                signature_cls=WOnlyProvisionalHypothesisSignature,
                input_dict=provisional_input,
                lm_config=lm_config,
                metadata={
                    **provisional_metadata,
                    "hypothesis_attempt": int(
                        hypothesis_attempt
                    ),
                },
                return_cache_hit=True,
            )
            break

        except (TypeError, ValueError) as exc:
            last_error = exc
            print(
                "[prompt_feedback] provisional hypothesis retry"
                f" | agent={agent}"
                f" attempt={hypothesis_attempt + 1}/3"
                f" error={type(exc).__name__}: {exc}",
                flush=True,
            )

    else:
        assert last_error is not None
        raise RuntimeError(
            "Failed to generate a schema-valid provisional "
            f"hypothesis after 3 attempts for agent={agent}: "
            f"{last_error}"
        ) from last_error

    hypothesis_payload = dict(parsed)
    return {
        "script_version": SCRIPT_VERSION,
        "row_type": "provisional_hypothesis",
        "condition": condition,
        "agent": agent,
        "status": "proposed",
        **hypothesis_payload,
        "n_w_evidence": len(evidence_list),
        "evidence_mode": evidence_mode,
        "base_prompt_hash": base_prompt_hash,
        "w_evidence_hash": w_evidence_hash,
        "provisional_hypothesis_hash": _canonical_hash(
            hypothesis_payload
        ),
        "lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    }


def revise_hypothesis_with_positive_cases(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    condition: str,
    agent: str,
    base_prompt: str,
    provisional_hypothesis_row: Mapping[str, Any],
    w_evidence: Sequence[Mapping[str, Any]],
    c_evidence: Sequence[Mapping[str, Any]],
    max_evidence_chars: int,
) -> dict[str, Any]:
    """
    Reassess a W-only hypothesis against hypothesis-matched positive cases.

    The returned row is compatible with ``update_agent_prompt()`` because it
    contains all ``INTEGRATED_FEEDBACK_FIELDS`` plus explicit revision
    metadata.
    """
    condition = _validate_condition(condition)
    if condition == "base":
        raise ValueError(
            "The base condition must not revise an update hypothesis."
        )
    if condition not in MIXED_CONDITIONS:
        raise ValueError(
            "Positive-case hypothesis revision requires a mixed condition."
        )
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")
    if provisional_hypothesis_row.get("error"):
        raise ValueError(
            "Cannot revise a failed provisional hypothesis."
        )

    base_prompt = _require_text(
        base_prompt,
        field="base_prompt",
    )
    hypothesis_payload = _provisional_hypothesis_payload(
        provisional_hypothesis_row
    )
    for field in (
        "failure_mechanism",
        "semantic_condition",
        "proposed_update_direction",
        "expected_behavior_change",
        "potential_overgeneralization",
    ):
        _require_text(
            hypothesis_payload.get(field),
            field=f"provisional_hypothesis.{field}",
        )

    w_list = [dict(item) for item in w_evidence]
    c_list = [dict(item) for item in c_evidence]
    if not w_list:
        raise ValueError(
            "Hypothesis revision requires at least one W evidence item."
        )
    invalid_w = [
        item.get("evidence_kind")
        for item in w_list
        if item.get("evidence_kind") != "W_repair"
    ]
    if invalid_w:
        raise ValueError(
            "Hypothesis revision received non-W evidence "
            f"in w_evidence: {invalid_w}."
        )

    valid_c_kinds = {
        "C_signed_avoid",
        "raw_C_success",
    }
    invalid_c = [
        item.get("evidence_kind")
        for item in c_list
        if item.get("evidence_kind") not in valid_c_kinds
    ]
    if invalid_c:
        raise ValueError(
            "Hypothesis revision received invalid C evidence kinds: "
            f"{invalid_c}."
        )

    base_prompt_hash = _canonical_hash(base_prompt)
    w_evidence_hash = _canonical_hash(w_list)
    c_evidence_hash = _canonical_hash(c_list)
    provisional_hypothesis_hash = _canonical_hash(
        hypothesis_payload
    )
    combined_evidence_hash = _canonical_hash({
        "w_evidence": w_list,
        "c_evidence": c_list,
    })

    hypothesis_json = _json_dumps(hypothesis_payload)
    w_json = _json_dumps(w_list)
    c_json = _json_dumps(c_list)
    payload_chars = (
        len(hypothesis_json)
        + len(w_json)
        + len(c_json)
    )
    if payload_chars > max_evidence_chars:
        raise ValueError(
            f"Hypothesis revision payload for {condition}/{agent} has "
            f"{payload_chars} chars, exceeding "
            f"max_evidence_chars={max_evidence_chars}."
        )

    evidence_mode = evidence_mode_for_condition(condition)
    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation=(
            "prompt_update.counterexample_revision."
            f"{COUNTEREXAMPLE_REVISION_PROMPT_VERSION}."
            f"{condition}.{agent}"
        ),
        lm=lm,
        signature_cls=CounterexampleRevisionSignature,
        input_dict={
            "condition": condition,
            "agent": agent,
            "agent_role": AGENT_ROLES[agent],
            "agent_function": AGENT_FUNCTIONS[agent],
            "native_output_contract": AGENT_OUTPUT_CONTRACTS[agent],
            "base_prompt": base_prompt,
            "evidence_mode": evidence_mode,
            "provisional_hypothesis": hypothesis_json,
            "w_evidence": w_json,
            "matched_c_evidence": c_json,
        },
        lm_config=lm_config,
        metadata={
            "script_version": SCRIPT_VERSION,
            "prompt_version": (
                COUNTEREXAMPLE_REVISION_PROMPT_VERSION
            ),
            "stage": "counterexample_revision",
            "condition": condition,
            "agent": agent,
            "n_w_evidence": len(w_list),
            "n_c_evidence": len(c_list),
            "base_prompt_hash": base_prompt_hash,
            "w_evidence_hash": w_evidence_hash,
            "c_evidence_hash": c_evidence_hash,
            "provisional_hypothesis_hash": (
                provisional_hypothesis_hash
            ),
            "evidence_hash": combined_evidence_hash,
        },
        return_cache_hit=True,
    )

    return {
        "script_version": SCRIPT_VERSION,
        "row_type": "integrated_feedback",
        "condition": condition,
        "agent": agent,
        "status": "revised_with_matched_positive_cases",
        **parsed,
        "n_evidence": len(w_list) + len(c_list),
        "n_w_evidence": len(w_list),
        "n_c_evidence": len(c_list),
        "evidence_mode": evidence_mode,
        "evidence_kinds": dict(
            Counter(
                item["evidence_kind"]
                for item in [*w_list, *c_list]
            )
        ),
        "base_prompt_hash": base_prompt_hash,
        "w_evidence_hash": w_evidence_hash,
        "c_evidence_hash": c_evidence_hash,
        "evidence_hash": combined_evidence_hash,
        "provisional_hypothesis_hash": (
            provisional_hypothesis_hash
        ),
        "lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    }



def generate_candidate_feedbacks_with_positive_cases(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    condition: str,
    agent: str,
    base_prompt: str,
    provisional_hypothesis_row: Mapping[str, Any],
    w_evidence: Sequence[Mapping[str, Any]],
    c_evidence: Sequence[Mapping[str, Any]],
    max_evidence_chars: int,
    num_candidates: int,
) -> dict[str, Any]:
    """
    Generate multiple admissible integrated-feedback delta-p candidates.

    This stage does not rank candidates. A separate agent-specific semantic
    norm selector chooses one candidate by relative order only.
    """
    condition = _validate_condition(condition)
    if condition == "base":
        raise ValueError(
            "The base condition must not generate feedback candidates."
        )
    if condition not in MIXED_CONDITIONS:
        raise ValueError(
            "Positive-case candidate generation requires a mixed condition."
        )
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")
    if provisional_hypothesis_row.get("error"):
        raise ValueError(
            "Cannot generate candidates from a failed provisional "
            "hypothesis."
        )
    if isinstance(num_candidates, bool) or int(num_candidates) < 2:
        raise ValueError(
            "num_candidates must be an integer greater than or equal to 2."
        )
    num_candidates = int(num_candidates)

    base_prompt = _require_text(
        base_prompt,
        field="base_prompt",
    )
    hypothesis_payload = _provisional_hypothesis_payload(
        provisional_hypothesis_row
    )
    for field in (
        "failure_mechanism",
        "semantic_condition",
        "proposed_update_direction",
        "expected_behavior_change",
        "potential_overgeneralization",
    ):
        _require_text(
            hypothesis_payload.get(field),
            field=f"provisional_hypothesis.{field}",
        )

    w_list = [dict(item) for item in w_evidence]
    c_list = [dict(item) for item in c_evidence]
    if not w_list:
        raise ValueError(
            "Candidate generation requires at least one W evidence item."
        )

    invalid_w = [
        item.get("evidence_kind")
        for item in w_list
        if item.get("evidence_kind") != "W_repair"
    ]
    if invalid_w:
        raise ValueError(
            "Candidate generation received non-W evidence in w_evidence: "
            f"{invalid_w}."
        )

    valid_c_kinds = {
        "C_signed_avoid",
        "raw_C_success",
    }
    invalid_c = [
        item.get("evidence_kind")
        for item in c_list
        if item.get("evidence_kind") not in valid_c_kinds
    ]
    if invalid_c:
        raise ValueError(
            "Candidate generation received invalid C evidence kinds: "
            f"{invalid_c}."
        )

    base_prompt_hash = _canonical_hash(base_prompt)
    w_evidence_hash = _canonical_hash(w_list)
    c_evidence_hash = _canonical_hash(c_list)
    provisional_hypothesis_hash = _canonical_hash(
        hypothesis_payload
    )
    combined_evidence_hash = _canonical_hash({
        "w_evidence": w_list,
        "c_evidence": c_list,
    })

    hypothesis_json = _json_dumps(hypothesis_payload)
    w_json = _json_dumps(w_list)
    c_json = _json_dumps(c_list)
    payload_chars = (
        len(hypothesis_json)
        + len(w_json)
        + len(c_json)
    )
    if payload_chars > max_evidence_chars:
        raise ValueError(
            f"Candidate-generation payload for {condition}/{agent} has "
            f"{payload_chars} chars, exceeding "
            f"max_evidence_chars={max_evidence_chars}."
        )

    evidence_mode = evidence_mode_for_condition(condition)
    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation=(
            "prompt_update.feedback_candidate_generation."
            f"{FEEDBACK_CANDIDATE_GENERATION_PROMPT_VERSION}."
            f"k{num_candidates}.{condition}.{agent}"
        ),
        lm=lm,
        signature_cls=CandidateCounterexampleRevisionSignature,
        input_dict={
            "condition": condition,
            "agent": agent,
            "agent_role": AGENT_ROLES[agent],
            "agent_function": AGENT_FUNCTIONS[agent],
            "native_output_contract": AGENT_OUTPUT_CONTRACTS[agent],
            "base_prompt": base_prompt,
            "evidence_mode": evidence_mode,
            "provisional_hypothesis": hypothesis_json,
            "w_evidence": w_json,
            "matched_c_evidence": c_json,
            "num_candidates": num_candidates,
        },
        lm_config=lm_config,
        metadata={
            "script_version": SCRIPT_VERSION,
            "prompt_version": (
                FEEDBACK_CANDIDATE_GENERATION_PROMPT_VERSION
            ),
            "stage": "feedback_candidate_generation",
            "condition": condition,
            "agent": agent,
            "requested_num_candidates": num_candidates,
            "n_w_evidence": len(w_list),
            "n_c_evidence": len(c_list),
            "base_prompt_hash": base_prompt_hash,
            "w_evidence_hash": w_evidence_hash,
            "c_evidence_hash": c_evidence_hash,
            "provisional_hypothesis_hash": (
                provisional_hypothesis_hash
            ),
            "evidence_hash": combined_evidence_hash,
        },
        return_cache_hit=True,
    )

    raw_candidates = list(parsed["candidate_feedbacks"])
    no_admissible = bool(parsed["no_admissible_update"])
    if no_admissible:
        if raw_candidates:
            raise AssertionError(
                "No-admissible result unexpectedly contained candidates."
            )
    else:
        if len(raw_candidates) != num_candidates:
            raise ValueError(
                "Candidate generator returned "
                f"{len(raw_candidates)} candidates; expected "
                f"{num_candidates}."
            )
        expected_indices = list(range(num_candidates))
        actual_indices = sorted(
            item["candidate_index"]
            for item in raw_candidates
        )
        if actual_indices != expected_indices:
            raise ValueError(
                "Candidate indices must be consecutive from 0 through "
                f"{num_candidates - 1}; got {actual_indices}."
            )

    common = {
        "script_version": SCRIPT_VERSION,
        "condition": condition,
        "agent": agent,
        "n_evidence": len(w_list) + len(c_list),
        "n_w_evidence": len(w_list),
        "n_c_evidence": len(c_list),
        "evidence_mode": evidence_mode,
        "evidence_kinds": dict(
            Counter(
                item["evidence_kind"]
                for item in [*w_list, *c_list]
            )
        ),
        "base_prompt_hash": base_prompt_hash,
        "w_evidence_hash": w_evidence_hash,
        "c_evidence_hash": c_evidence_hash,
        "evidence_hash": combined_evidence_hash,
        "provisional_hypothesis_hash": (
            provisional_hypothesis_hash
        ),
    }

    candidate_rows = [
        {
            **common,
            "row_type": "candidate_integrated_feedback",
            "status": "candidate_generated",
            **candidate,
            "candidate_feedback_hash": _canonical_hash(candidate),
        }
        for candidate in raw_candidates
    ]

    return {
        **common,
        "row_type": "candidate_feedback_set",
        "status": (
            "no_admissible_update"
            if no_admissible
            else "candidates_generated"
        ),
        "requested_num_candidates": num_candidates,
        "num_candidates": len(candidate_rows),
        "no_admissible_update": no_admissible,
        "no_admissible_update_reason": parsed[
            "no_admissible_update_reason"
        ],
        "candidate_feedbacks": candidate_rows,
        "candidate_feedback_set_hash": _canonical_hash(
            [
                {
                    key: row.get(key)
                    for key in (
                        "candidate_index",
                        *REVISED_FEEDBACK_METADATA_FIELDS,
                        *INTEGRATED_FEEDBACK_FIELDS,
                    )
                }
                for row in candidate_rows
            ]
        ),
        "lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    }


def _rejected_feedback_from_candidate_set(
    candidate_feedback_set_row: Mapping[str, Any],
) -> dict[str, Any]:
    reason = str(
        candidate_feedback_set_row.get(
            "no_admissible_update_reason"
        )
        or "No admissible non-empty semantic update was generated."
    ).strip()

    return {
        "script_version": SCRIPT_VERSION,
        "row_type": "integrated_feedback",
        "condition": candidate_feedback_set_row.get("condition"),
        "agent": candidate_feedback_set_row.get("agent"),
        "status": "no_admissible_update_base_preserved",
        "hypothesis_decision": "reject",
        "semantic_boundary": (
            "No non-empty semantic update satisfies both repair and "
            "preservation constraints."
        ),
        "counterexample_analysis": reason,
        "integrated_feedback": (
            "Preserve the current base prompt because no admissible "
            "non-empty update remains."
        ),
        "update_directions": [],
        "preservation_constraints": [
            "Preserve the current prompt behavior."
        ],
        "edit_recommendations": [
            {
                "action": "keep",
                "target_behavior": "current base prompt",
                "proposed_change": "",
                "reason": reason,
            }
        ],
        "rejected_local_patterns": [],
        "new_capability_required": False,
        "length_increase_justified": False,
        "generalization_rationale": (
            "No admissible update can be generalized safely from the "
            "available evidence."
        ),
        "generalization_check": (
            "The no-op path is represented as rejection rather than as a "
            "minimum-norm candidate."
        ),
        "n_evidence": int(
            candidate_feedback_set_row.get("n_evidence", 0)
        ),
        "n_w_evidence": int(
            candidate_feedback_set_row.get("n_w_evidence", 0)
        ),
        "n_c_evidence": int(
            candidate_feedback_set_row.get("n_c_evidence", 0)
        ),
        "evidence_mode": candidate_feedback_set_row.get(
            "evidence_mode"
        ),
        "evidence_kinds": dict(
            candidate_feedback_set_row.get("evidence_kinds")
            or {}
        ),
        "base_prompt_hash": candidate_feedback_set_row.get(
            "base_prompt_hash"
        ),
        "w_evidence_hash": candidate_feedback_set_row.get(
            "w_evidence_hash"
        ),
        "c_evidence_hash": candidate_feedback_set_row.get(
            "c_evidence_hash"
        ),
        "evidence_hash": candidate_feedback_set_row.get(
            "evidence_hash"
        ),
        "provisional_hypothesis_hash": (
            candidate_feedback_set_row.get(
                "provisional_hypothesis_hash"
            )
        ),
        "candidate_feedback_set_hash": (
            candidate_feedback_set_row.get(
                "candidate_feedback_set_hash"
            )
        ),
        "num_feedback_candidates": 0,
        "selected_candidate_index": None,
        "feedback_norm_selection": None,
        "lm_trace": None,
    }


def select_minimum_norm_feedback(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    condition: str,
    agent: str,
    base_prompt: str,
    candidate_feedback_set_row: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Select one candidate by agent-specific semantic norm order.

    No scalar distance is produced. The selector compares all candidate
    delta-p feedbacks in one 1-to-N call and returns one candidate index.
    """
    condition = _validate_condition(condition)
    if condition == "base":
        raise ValueError(
            "The base condition must not select an update feedback."
        )
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")

    base_prompt = _require_text(
        base_prompt,
        field="base_prompt",
    )
    row_condition = str(
        candidate_feedback_set_row.get("condition") or ""
    )
    row_agent = str(
        candidate_feedback_set_row.get("agent") or ""
    )
    if row_condition and row_condition != condition:
        raise ValueError(
            "Candidate feedback set condition mismatch: "
            f"{row_condition!r} != {condition!r}."
        )
    if row_agent and row_agent != agent:
        raise ValueError(
            "Candidate feedback set agent mismatch: "
            f"{row_agent!r} != {agent!r}."
        )

    candidate_rows = [
        dict(item)
        for item in (
            candidate_feedback_set_row.get("candidate_feedbacks")
            or []
        )
    ]
    if candidate_feedback_set_row.get("no_admissible_update"):
        if candidate_rows:
            raise ValueError(
                "no_admissible_update set cannot contain candidates."
            )
        return _rejected_feedback_from_candidate_set(
            candidate_feedback_set_row
        )
    if not candidate_rows:
        raise ValueError(
            "Minimum-norm selection requires at least one candidate."
        )

    indices = [
        int(row["candidate_index"])
        for row in candidate_rows
    ]
    if len(indices) != len(set(indices)):
        raise ValueError(
            "Candidate feedback indices must be unique."
        )

    comparison_payload = [
        {
            "candidate_index": row["candidate_index"],
            **{
                key: row.get(key)
                for key in (
                    *REVISED_FEEDBACK_METADATA_FIELDS,
                    *INTEGRATED_FEEDBACK_FIELDS,
                )
            },
        }
        for row in candidate_rows
    ]
    candidates_json = _json_dumps(comparison_payload)
    base_prompt_hash = _canonical_hash(base_prompt)
    candidate_feedback_set_hash = _canonical_hash(
        comparison_payload
    )

    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation=(
            "prompt_update.feedback_norm_selection."
            f"{FEEDBACK_NORM_SELECTION_PROMPT_VERSION}."
            f"{condition}.{agent}"
        ),
        lm=lm,
        signature_cls=MinimumNormFeedbackSelectionSignature,
        input_dict={
            "agent": agent,
            "base_prompt": base_prompt,
            "candidate_feedbacks": candidates_json,
        },
        lm_config=lm_config,
        metadata={
            "script_version": SCRIPT_VERSION,
            "prompt_version": FEEDBACK_NORM_SELECTION_PROMPT_VERSION,
            "method_prompt": FEEDBACK_NORM_METHOD_PROMPTS[agent],
            "stage": "feedback_norm_selection",
            "condition": condition,
            "agent": agent,
            "num_candidates": len(candidate_rows),
            "candidate_indices": indices,
            "base_prompt_hash": base_prompt_hash,
            "candidate_feedback_set_hash": (
                candidate_feedback_set_hash
            ),
            "evidence_hash": candidate_feedback_set_row.get(
                "evidence_hash"
            ),
        },
        return_cache_hit=True,
    )

    selected_index = parsed["selected_candidate_index"]
    by_index = {
        int(row["candidate_index"]): row
        for row in candidate_rows
    }
    if selected_index not in by_index:
        raise ValueError(
            "Minimum-norm selector returned candidate index "
            f"{selected_index}, but available indices are "
            f"{sorted(by_index)}."
        )

    selected = dict(by_index[selected_index])
    selected.update({
        "script_version": SCRIPT_VERSION,
        "row_type": "integrated_feedback",
        "status": "selected_minimum_semantic_norm",
        "condition": condition,
        "agent": agent,
        "selected_candidate_index": selected_index,
        "num_feedback_candidates": len(candidate_rows),
        "candidate_feedback_set_hash": (
            candidate_feedback_set_hash
        ),
        "feedback_norm_selection": dict(parsed),
        "lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    })
    return selected


class BatchFeedbackSynthesisSignature(Signature):
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
    output_keys = list(INTEGRATED_FEEDBACK_FIELDS)

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
You are synthesizing one INTEGRATED PROMPT FEEDBACK object for one agent
in a fixed multi-agent HotpotQA pipeline.

This is an abstraction and edit-planning stage. Do not write the updated
agent prompt. The separate rewrite stage will see the current base prompt
and this feedback object, but not the raw evidence.

Infer the smallest reusable behavioral change that explains the evidence
while accounting for the current prompt.

Generalization requirements:
- Do not include sample-specific proper nouns, answers, question strings,
  document titles, page titles, locations, source names, acronyms, literal
  section labels, or copied phrases from individual examples.
- Do not produce one rule per example or a case-specific exception list.
- Replace concrete entities with abstract semantic roles such as bridge
  entity, target relation, comparison attribute, missing evidence,
  post-retrieval fact, or answer-bearing span.
- Interpret evidence according to this agent's pipeline position and
  functional responsibility.
- Keep all guidance operational and compatible with the native interface.
- Do not mention training, attribution, W/C labels, optimization, batches,
  endpoints, deltas, metrics, or sample indices in the synthesized content.

Evidence interpretation:
- Treat encourage evidence as the primary source of behavioral change.
- Avoid or preserve evidence should mainly constrain, qualify, or reject a
  proposed change.
- Avoid or preserve evidence may contribute an independent invariant when
  it is repeated across the batch or is necessary to retain a clearly
  existing general capability. Do not promote a one-off successful behavior
  into an independent rule merely because it appears once.
- Prefer one coherent update when the evidence shares a common behavioral
  cause. If genuinely independent failure modes remain, return the smallest
  non-overlapping set, normally no more than three directions.

Edit preference:
Use the least additive edit that fully explains the evidence. Prefer:
1. clarify or narrow an existing instruction;
2. merge overlapping instructions;
3. replace an incorrect or overly broad instruction;
4. add a new instruction for a genuinely missing capability.

This ordering is a preference, not an absolute prohibition. A new
instruction is appropriate when the capability is genuinely absent from
the current prompt. Prompt growth may be justified in that case, but
redundant, overlapping, or superseded guidance should still be identified.

For the final-answer agent in particular:
- Avoid creating separate extractors for individual answer types when the
  behavior can be expressed as one evidence-grounded extraction principle.
- Do not elevate incidental surface properties such as token length,
  parenthetical formatting, list order, candidate uniqueness, or one-sided
  metadata into selection rules unless the visible evidence explicitly
  entails the requested relation.

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

Current base prompt:
{input_dict["base_prompt"]}

Evidence mode:
{input_dict["evidence_mode"]}

Raw batch evidence:
{input_dict["batch_evidence"]}

Return strict JSON only:
{{
  "integrated_feedback": "compact unified diagnosis and edit direction",
  "update_directions": [
    "general reusable behavior to change; normally no more than three"
  ],
  "preservation_constraints": [
    "existing capability that the proposed change could actually threaten"
  ],
  "edit_recommendations": [
    {{
      "action": "clarify|merge|replace|add|keep",
      "target_behavior": "behavior or instruction in the current prompt",
      "proposed_change": "concise recommended revision; empty only for keep",
      "reason": "why this edit best explains the evidence"
    }}
  ],
  "rejected_local_patterns": [
    "surface heuristic or case-specific pattern that should not become a shared rule"
  ],
  "new_capability_required": false,
  "length_increase_justified": false,
  "generalization_rationale": "why the proposed directions transfer beyond the observed cases",
  "generalization_check": "confirmation that the result is not a sample-indexed rulebook"
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)

        return {
            "integrated_feedback": _require_text(
                obj.get("integrated_feedback"),
                field="integrated_feedback",
            ),
            "update_directions": _text_list(
                obj,
                "update_directions",
            ),
            "preservation_constraints": _text_list(
                obj,
                "preservation_constraints",
            ),
            "edit_recommendations": (
                _edit_recommendations(obj)
            ),
            "rejected_local_patterns": _text_list(
                obj,
                "rejected_local_patterns",
            ),
            "new_capability_required": _bool_field(
                obj,
                "new_capability_required",
            ),
            "length_increase_justified": _bool_field(
                obj,
                "length_increase_justified",
            ),
            "generalization_rationale": _require_text(
                obj.get("generalization_rationale"),
                field="generalization_rationale",
            ),
            "generalization_check": _require_text(
                obj.get("generalization_check"),
                field="generalization_check",
            ),
        }


class PromptRewriteFromIntegratedFeedbackSignature(
    Signature
):
    input_keys = [
        "condition",
        "agent",
        "agent_role",
        "agent_function",
        "native_output_contract",
        "base_prompt",
        "integrated_feedback",
    ]
    output_keys = [
        "updated_prompt",
        "clarified_instructions",
        "merged_instructions",
        "replaced_instructions",
        "added_instructions",
        "remaining_conflicts",
        "rationale",
    ]

    @classmethod
    def prompt_renderer(
        cls,
        input_dict: Mapping[str, Any],
    ) -> str:
        return f"""
You are rewriting one agent prompt in a fixed multi-agent HotpotQA
pipeline.

You receive only:
1. the current base prompt;
2. one already-synthesized integrated feedback object.

You do not have access to the raw optimization cases. Do not reconstruct,
invent, or encode sample-specific examples.

Produce one complete, directly usable shared prompt.

Primary objective
Apply the smallest coherent edit that realizes the integrated feedback while
preserving every useful capability of the base prompt that the feedback does
not directly invalidate.

The base prompt is authoritative. The integrated feedback is an edit plan,
not text to append verbatim.

Composition-preservation requirements
- Distinguish unsupported inference from licensed multi-hop composition.
- The prompt must continue to permit combining multiple visible,
  identity-aligned facts according to the relation requested by the question.
- Do not require the entire answer relation to appear as one direct statement
  in one passage when the necessary premises and links are visible across the
  provided states.
- Do not make uncertainty the default response merely because composition,
  comparison, alias resolution, or transitive reasoning is required.
- Uncertainty should be emitted only when a required premise, identity link,
  or relation is genuinely missing, ambiguous, or conflicting.
- Do not replace semantic reasoning with a direct-predication-only policy.

Minimal-edit requirements
- Preserve the native input/output interface exactly.
- Start from the supplied base prompt.
- Modify only the behavior named by the integrated feedback.
- Keep unrelated sections unchanged where practical.
- Prefer clarifying, merging, or replacing existing text over appending a new
  rule block.
- If ``new_capability_required`` is false, do not introduce a new protocol,
  new output section, new sentinel token, new decision tree, or new taxonomy.
- If ``length_increase_justified`` is false, the rewritten prompt should not
  materially grow. Merge or replace existing guidance instead.
- Remove or consolidate redundant instructions created by the edit.
- Do not turn one semantic direction into several answer-type, entity-type,
  relation-type, or formatting-specific rules.
- Treat edit recommendations as an edit plan, not as literal prose to append.

Forbidden over-specification
- Do not add an exhaustive COMPLETE/INCOMPLETE taxonomy beyond what already
  exists in the base prompt.
- Do not add a new structured report format unless required by the native
  output contract.
- Do not add a rigid noun-phrase query grammar.
- Do not globally prohibit relation words or ordinary retrieval terms.
- Do not require single-passage direct predication.
- Do not create separate rules for parentheses, suffixes, aliases,
  punctuation, acronyms, administrative labels, dates, locations, or other
  answer-surface categories.
- Do not add proper nouns, document titles, answers, copied phrases,
  locations, literal case labels, or sample-specific exception lists.
- Do not include optimization terminology in the final prompt.

Agent-specific safeguards
- summary1:
  Preserve concise grounded first-hop compression and useful bridge or
  missing-evidence information. Do not expand the state into a larger
  protocol or retrieval taxonomy unless the integrated feedback proves that
  a genuinely absent capability requires it.

- query:
  Preserve concrete evidence-grounded anchors and relation terms that help
  BM25 recover missing support. Retrieval effectiveness takes priority over
  enforcing one grammatical query template.

- summary2:
  Preserve integration across first-hop context and second-hop passages.
  Allow conclusions licensed by multiple explicit, identity-aligned facts,
  even when no one sentence states the complete relation.

- final:
  Emit the minimal answer supported by the visible summaries, but do not
  implement minimality through a surface-form taxonomy. Preserve qualifiers
  required for identity or requested answer content; omit unsupported or
  unnecessary explanatory material using one semantic sufficiency rule.

Conflict handling
- If an edit recommendation conflicts with composition preservation, the
  native interface, or a preservation constraint, do not apply that
  recommendation.
- Record any such conflict in ``remaining_conflicts``.
- Do not compensate for a conflict by adding further exceptions.
- If no safe change remains, return the base prompt unchanged.

Final quality check
Before returning, verify:
1. The prompt still supports valid multi-hop reasoning.
2. It does not force uncertainty for derivable cases.
3. It does not impose a stricter output or query protocol than required.
4. It contains no case-indexed or surface-category rulebook.
5. It is no more complex than necessary.
6. Every material change is traceable to the integrated feedback.

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

Integrated feedback:
{input_dict["integrated_feedback"]}

Return strict JSON only:
{{
  "updated_prompt": "complete directly usable shared prompt",
  "clarified_instructions": [
    "existing behavior clarified or narrowed"
  ],
  "merged_instructions": [
    "overlapping behaviors consolidated"
  ],
  "replaced_instructions": [
    "incorrect or overly broad behavior replaced"
  ],
  "added_instructions": [
    "genuinely missing capability added"
  ],
  "remaining_conflicts": [
    "recommendation not safely applied, or an empty list"
  ],
  "rationale": "brief explanation of the minimal capability-preserving edit strategy"
}}
""".strip()

    @classmethod
    def output_extractor(
        cls,
        lm_out: str,
    ) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        return {
            "updated_prompt": _require_text(
                obj.get("updated_prompt"),
                field="updated_prompt",
            ),
            "clarified_instructions": _text_list(
                obj,
                "clarified_instructions",
            ),
            "merged_instructions": _text_list(
                obj,
                "merged_instructions",
            ),
            "replaced_instructions": _text_list(
                obj,
                "replaced_instructions",
            ),
            "added_instructions": _text_list(
                obj,
                "added_instructions",
            ),
            "remaining_conflicts": _text_list(
                obj,
                "remaining_conflicts",
            ),
            "rationale": str(
                obj.get("rationale") or ""
            ).strip(),
        }


def _integrated_feedback_payload(
    row: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        key: row.get(key)
        for key in (
            *REVISED_FEEDBACK_METADATA_FIELDS,
            *INTEGRATED_FEEDBACK_FIELDS,
        )
    }


def synthesize_batch_feedback(
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
    condition = _validate_condition(condition)
    if condition == "base":
        raise ValueError(
            "The base condition must not synthesize feedback."
        )
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")

    base_prompt = _require_text(
        base_prompt,
        field="base_prompt",
    )
    base_prompt_hash = _canonical_hash(
        base_prompt
    )
    evidence_list = [
        dict(item)
        for item in evidence
    ]
    evidence_hash = _canonical_hash(
        evidence_list
    )
    evidence_mode = evidence_mode_for_condition(
        condition
    )

    if not evidence_list:
        return {
            "script_version": SCRIPT_VERSION,
            "row_type": "integrated_feedback",
            "condition": condition,
            "agent": agent,
            "status": "no_evidence",
            "integrated_feedback": (
                "No update evidence was assigned; preserve "
                "the current prompt unchanged."
            ),
            "update_directions": [],
            "preservation_constraints": [
                "Preserve the current prompt behavior."
            ],
            "edit_recommendations": [],
            "rejected_local_patterns": [],
            "new_capability_required": False,
            "length_increase_justified": False,
            "generalization_rationale": (
                "No evidence supports a general behavioral change."
            ),
            "generalization_check": (
                "No sample-specific content is present."
            ),
            "n_evidence": 0,
            "evidence_mode": evidence_mode,
            "evidence_kinds": {},
            "base_prompt_hash": base_prompt_hash,
            "evidence_hash": evidence_hash,
            "lm_trace": None,
        }

    evidence_json = _json_dumps(
        evidence_list
    )
    if len(evidence_json) > max_evidence_chars:
        raise ValueError(
            f"Evidence payload for {condition}/{agent} has "
            f"{len(evidence_json)} chars, exceeding "
            f"max_evidence_chars={max_evidence_chars}."
        )

    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation=(
            "prompt_update.feedback_synthesis."
            f"{SCRIPT_VERSION}.{condition}.{agent}"
        ),
        lm=lm,
        signature_cls=(
            BatchFeedbackSynthesisSignature
        ),
        input_dict={
            "condition": condition,
            "agent": agent,
            "agent_role": AGENT_ROLES[agent],
            "agent_function": AGENT_FUNCTIONS[agent],
            "native_output_contract": (
                AGENT_OUTPUT_CONTRACTS[agent]
            ),
            "base_prompt": base_prompt,
            "evidence_mode": evidence_mode,
            "batch_evidence": evidence_json,
        },
        lm_config=lm_config,
        metadata={
            "script_version": SCRIPT_VERSION,
            "stage": "feedback_synthesis",
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
        "row_type": "integrated_feedback",
        "condition": condition,
        "agent": agent,
        "status": "synthesized",
        **parsed,
        "n_evidence": len(evidence_list),
        "evidence_mode": evidence_mode,
        "evidence_kinds": dict(
            Counter(
                item["evidence_kind"]
                for item in evidence_list
            )
        ),
        "base_prompt_hash": base_prompt_hash,
        "evidence_hash": evidence_hash,
        "lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    }


def update_agent_prompt(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    condition: str,
    agent: str,
    base_prompt: str,
    integrated_feedback_row: Mapping[str, Any],
) -> dict[str, Any]:
    condition = _validate_condition(condition)
    if condition == "base":
        raise ValueError(
            "The base condition must not call update_agent_prompt()."
        )
    if agent not in AGENT_TO_PROMPT_KEY:
        raise ValueError(f"Unknown agent: {agent!r}.")

    base_prompt = _require_text(
        base_prompt,
        field="base_prompt",
    )
    base_prompt_hash = _canonical_hash(
        base_prompt
    )
    feedback_payload = (
        _integrated_feedback_payload(
            integrated_feedback_row
        )
    )
    integrated_feedback_hash = (
        _canonical_hash(feedback_payload)
    )
    evidence_hash = str(
        integrated_feedback_row.get(
            "evidence_hash"
        )
        or ""
    )
    n_evidence = int(
        integrated_feedback_row.get(
            "n_evidence",
            0,
        )
    )
    hypothesis_decision = str(
        integrated_feedback_row.get(
            "hypothesis_decision"
        )
        or ""
    ).strip()

    if hypothesis_decision == "reject":
        return {
            "script_version": SCRIPT_VERSION,
            "row_type": "prompt_rewrite",
            "condition": condition,
            "agent": agent,
            "status": "hypothesis_rejected_base_preserved",
            "updated_prompt": base_prompt,
            "clarified_instructions": [],
            "merged_instructions": [],
            "replaced_instructions": [],
            "added_instructions": [],
            "remaining_conflicts": [],
            "rationale": (
                "Matched positive counterexamples rejected "
                "the provisional update hypothesis."
            ),
            "hypothesis_decision": "reject",
            "semantic_boundary": feedback_payload.get(
                "semantic_boundary"
            ),
            "counterexample_analysis": feedback_payload.get(
                "counterexample_analysis"
            ),
            "update_directions": [],
            "preservation_constraints": list(
                feedback_payload.get(
                    "preservation_constraints"
                )
                or []
            ),
            "edit_recommendations": list(
                feedback_payload.get(
                    "edit_recommendations"
                )
                or []
            ),
            "rejected_local_patterns": list(
                feedback_payload.get(
                    "rejected_local_patterns"
                )
                or []
            ),
            "new_capability_required": False,
            "length_increase_justified": False,
            "n_evidence": n_evidence,
            "base_prompt_chars": len(base_prompt),
            "updated_prompt_chars": len(base_prompt),
            "net_prompt_chars": 0,
            "base_prompt_hash": base_prompt_hash,
            "evidence_hash": evidence_hash,
            "integrated_feedback_hash": (
                integrated_feedback_hash
            ),
            "lm_trace": None,
        }

    if n_evidence == 0:
        return {
            "script_version": SCRIPT_VERSION,
            "row_type": "prompt_rewrite",
            "condition": condition,
            "agent": agent,
            "status": "no_evidence_base_preserved",
            "updated_prompt": base_prompt,
            "clarified_instructions": [],
            "merged_instructions": [],
            "replaced_instructions": [],
            "added_instructions": [],
            "remaining_conflicts": [],
            "rationale": (
                "No evidence was assigned to this agent."
            ),
            "hypothesis_decision": (
                hypothesis_decision or None
            ),
            "semantic_boundary": feedback_payload.get(
                "semantic_boundary"
            ),
            "counterexample_analysis": feedback_payload.get(
                "counterexample_analysis"
            ),
            "update_directions": [],
            "preservation_constraints": list(
                feedback_payload.get(
                    "preservation_constraints"
                )
                or []
            ),
            "edit_recommendations": [],
            "rejected_local_patterns": [],
            "new_capability_required": False,
            "length_increase_justified": False,
            "n_evidence": 0,
            "base_prompt_chars": len(base_prompt),
            "updated_prompt_chars": len(base_prompt),
            "net_prompt_chars": 0,
            "base_prompt_hash": base_prompt_hash,
            "evidence_hash": evidence_hash,
            "integrated_feedback_hash": (
                integrated_feedback_hash
            ),
            "lm_trace": None,
        }

    integrated_feedback_json = _json_dumps(
        feedback_payload
    )

    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation=(
            "prompt_update.rewrite_from_feedback."
            f"{PROMPT_REWRITE_PROMPT_VERSION}."
            f"{condition}.{agent}"
        ),
        lm=lm,
        signature_cls=(
            PromptRewriteFromIntegratedFeedbackSignature
        ),
        input_dict={
            "condition": condition,
            "agent": agent,
            "agent_role": AGENT_ROLES[agent],
            "agent_function": AGENT_FUNCTIONS[agent],
            "native_output_contract": (
                AGENT_OUTPUT_CONTRACTS[agent]
            ),
            "base_prompt": base_prompt,
            "integrated_feedback": (
                integrated_feedback_json
            ),
        },
        lm_config=lm_config,
        metadata={
            "script_version": SCRIPT_VERSION,
            "prompt_version": (
                PROMPT_REWRITE_PROMPT_VERSION
            ),
            "stage": "prompt_rewrite",
            "condition": condition,
            "agent": agent,
            "n_evidence": n_evidence,
            "base_prompt_hash": base_prompt_hash,
            "evidence_hash": evidence_hash,
            "integrated_feedback_hash": (
                integrated_feedback_hash
            ),
        },
        return_cache_hit=True,
    )

    updated_prompt = parsed["updated_prompt"]

    return {
        "script_version": SCRIPT_VERSION,
        "row_type": "prompt_rewrite",
        "condition": condition,
        "agent": agent,
        "status": "updated",
        **parsed,
        "hypothesis_decision": (
            hypothesis_decision or None
        ),
        "semantic_boundary": feedback_payload.get(
            "semantic_boundary"
        ),
        "counterexample_analysis": feedback_payload.get(
            "counterexample_analysis"
        ),
        "update_directions": list(
            feedback_payload.get(
                "update_directions"
            )
            or []
        ),
        "preservation_constraints": list(
            feedback_payload.get(
                "preservation_constraints"
            )
            or []
        ),
        "edit_recommendations": list(
            feedback_payload.get(
                "edit_recommendations"
            )
            or []
        ),
        "rejected_local_patterns": list(
            feedback_payload.get(
                "rejected_local_patterns"
            )
            or []
        ),
        "new_capability_required": bool(
            feedback_payload.get(
                "new_capability_required"
            )
        ),
        "length_increase_justified": bool(
            feedback_payload.get(
                "length_increase_justified"
            )
        ),
        "n_evidence": n_evidence,
        "base_prompt_chars": len(base_prompt),
        "updated_prompt_chars": len(
            updated_prompt
        ),
        "net_prompt_chars": (
            len(updated_prompt)
            - len(base_prompt)
        ),
        "base_prompt_hash": base_prompt_hash,
        "evidence_hash": evidence_hash,
        "integrated_feedback_hash": (
            integrated_feedback_hash
        ),
        "lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    }