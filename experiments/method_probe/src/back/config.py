from __future__ import annotations

import json
from typing import Any, Mapping, Sequence


DISTANCE_COMPARISON_PROMPT = """
You are judging semantic magnitude between two local prompt-feedback updates.

Each candidate segment contains feedback for the HotpotQA second-hop query generator.
Select the segment whose feedback text represents the larger semantic update.

Here, feedback magnitude means how much the query-generation behavior would need to change:
- which entity/title/alias anchors to preserve, add, remove, or disambiguate
- which bridge relation, comparison relation, or task relation to emphasize
- which evidence family or answer type to target
- which distractors, wrong senses, or noisy entity families to avoid
- whether the candidate set should be broadened, narrowed, preserved, or re-centered
- what kind of retrieval failure the feedback corrects

Important:
- Judge the semantic difference magnitude of the feedback itself.
- Do not judge which feedback is more correct or likely to improve retrieval.
- Do not choose a segment merely because it is longer or more detailed.
- Do not choose a segment merely because it mentions source style, infoboxes, lead sentences, cast sections, table rows, or list parsing.
- Extra detail counts only if it changes the semantic instruction to the query generator.
- A full-edge feedback update should usually be larger than a local sub-edge feedback update if the decomposition is semantically consistent.
- Return "tie" only when the two feedback updates ask for materially similar semantic changes.

Return JSON only:
{
  "larger_segment": "A" | "B" | "tie",
  "segment_index": 0 | 1 | -1,
  "why_larger": "short explanation focused on semantic feedback magnitude",
  "dominant_gap_type": "anchor|bridge_relation|surface_form|noisy_entity|answer_type|query_shape|candidate_set|evidence_family|mixed|tie",
  "confidence": 0.0
}

Question:
{question}

summary_1:
{summary_1}

Candidate feedback segments:
{segments_json}
""".strip()


DISTANCE_GAP_TYPES = {
    "anchor",
    "bridge_relation",
    "surface_form",
    "noisy_entity",
    "answer_type",
    "query_shape",
    "candidate_set",
    "evidence_family",
    "mixed",
    "tie",
}


def render_distance_comparison_prompt(
    *,
    question: str,
    summary_1: str,
    segments: Sequence[Mapping[str, Any]],
) -> str:
    """
    Render the distance prompt without using str.format(), since the prompt
    itself contains JSON braces.
    """

    segments_json = json.dumps(
        list(segments),
        ensure_ascii=False,
        indent=2,
    )

    return (
        DISTANCE_COMPARISON_PROMPT
        .replace("{question}", str(question).strip())
        .replace("{summary_1}", str(summary_1).strip())
        .replace("{segments_json}", segments_json)
    )


GRADIENT_AGGREGATION_SYSTEM_PROMPT = """
You update the instruction of one HotpotQA second-hop query-generation agent.

The agent is:

    query = Q(question, summary_1; prompt)

You are given:
- the current complete instruction for this agent,
- empirical evidence collected from local output transitions,
- samplewise prompt gradients inferred from those transitions,
- intervention labels determined by actual reruns.

The evidence labels have the following meanings:

- W_to_C:
  The gradient produced the intended local retrieval improvement.
  Extract the transferable query-generation behavior that should be encouraged.

- W_to_W:
  The gradient failed to produce the intended local retrieval improvement.
  Do not blindly incorporate it. Use it to avoid ineffective or insufficient
  update directions.

- C_to_C:
  The transported gradient was operationally realized while the originally
  correct end-to-end answer remained correct.
  Treat this as evidence that the corresponding behavior or constraint can be
  preserved safely.

- C_to_W:
  The transported gradient was operationally realized and broke an originally
  correct end-to-end answer.
  Treat this as negative evidence. Prevent the candidate prompt from inducing
  the harmful behavior.

Produce one complete replacement instruction for create_query_hop2.

Requirements:
- Aggregate gradients into one general query-generation policy.
- Do not output one prompt per sample.
- Do not concatenate gradients mechanically.
- Do not memorize sample-specific entities, titles, questions, or answers.
- Generalize across entity anchoring, bridge relations, ambiguity resolution,
  candidate-set control, evidence targeting, and distractor suppression.
- Preserve useful parts of the current instruction that are not contradicted
  by the evidence.
- Prefer W_to_C behaviors when they do not conflict with C_to_W evidence.
- Use C_to_C evidence to identify safe preservation constraints.
- Use W_to_W evidence to avoid ineffective or incomplete changes.
- C_to_W evidence has priority when a proposed behavior would damage an
  already-correct case.
- The result must be a complete executable DSPy instruction for the query
  generator.
- Do not mention gradients, labels, samples, interventions, retrieval states,
  or this aggregation process inside the candidate prompt.

Return JSON only:
{
  "candidate_prompt": "complete replacement instruction for create_query_hop2",
  "aggregation_rationale": "brief explanation of the synthesized policy",
  "used_evidence_ids": ["evidence ids actively incorporated"],
  "rejected_evidence_ids": ["evidence ids not incorporated"],
  "preserved_behaviors": ["behaviors retained from the current prompt"],
  "introduced_behaviors": ["new or strengthened behaviors"],
  "suppressed_behaviors": ["behaviors explicitly discouraged"]
}
""".strip()
