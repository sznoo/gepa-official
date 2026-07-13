# /home/jinwoo/gepa-official/src/ours/prompts.py
import json
from pathlib import Path
from typing import Any


BASELINE_PROMPT_SET = {
    "name": "baseline",
    "description": (
        "Default DSPy ChainOfThought instructions generated from the "
        "original HotpotMultiHop signatures."
    ),
    "prompts": {
        "summarize1.predict": (
            "Given the fields `question`, `passages`, "
            "produce the fields `summary`."
        ),
        "create_query_hop2.predict": (
            "Given the fields `question`, `summary_1`, "
            "produce the fields `query`."
        ),
        "summarize2.predict": (
            "Given the fields `question`, `context`, `passages`, "
            "produce the fields `summary`."
        ),
        "final_answer.predict": (
            "Given the fields `question`, `summary_1`, `summary_2`, "
            "produce the fields `answer`."
        ),
    },
}


AGENTGRAD_PROMPT_SET = {
    "name": "agentgrad_best",
    "description": (
        "AgentGrad-optimized HotpotMultiHop instructions. "
        "summarize1.predict and final_answer.predict are optimized; "
        "create_query_hop2.predict and summarize2.predict retain their "
        "baseline instructions."
    ),
    "prompts": {
        "summarize1.predict": """Given inputs question (string) and passages (list of strings), produce a single textual output to populate the field "summary". The "summary" output must include the following labeled sections and follow these rules exactly.

1) Format
- Begin with: [[ ## reasoning ## ]]
- End the reasoning block and then include: [[ ## summary ## ]]
- The final output may optionally end with: [[ ## completed ## ]]

2) Reasoning section (required)
- For each passage i, include a concise mapping that:
  - Quotes or paraphrases the exact supporting text from Passage [i] (use quotation marks or exact substring).
  - Explicitly maps each quoted fact to the entity and scope it supports (e.g., "Passage [3] → ENTITY: Dan Boren; SCOPE: biographical birth date"; or "Passage [1] → ENTITY: Ilha (Santana); SCOPE: parish-level population 2011").
  - If a passage contains only lower-level, local, or different-scope facts that are NOT sufficient to answer the question (e.g., parish populations when the question asks for archipelago total), explicitly state that and refuse to treat them as the final answer.

- After mapping passages, state whether the exact target fact required by the question is present in the provided passages:
  - If present: identify the exact sentence(s) and supporting-text pattern matched (literal pattern required, e.g., "ENTITY_NAME (born <date>)" or "The population in 2011 was <number>"). Cite passage indices that contain that exact supporting text.
  - If not present: explain precisely which fact is missing and why the existing passage facts are insufficient (cite passage indices).

3) If missing: prioritized next-hop retrieval plan (required when exact supporting text is absent)
- Name the target entity to retrieve (canonical/title-first form) and give one-sentence rationale linking it to the question (use the bridging passage index).
- Provide at least three disambiguating short query variants (each a short search phrase). At least one variant must begin with the canonical/title-first suggestion. Include scope/context tokens (e.g., "birth date", "2011 population", "archipelago", "U.S. Representative", "politician", location).
- Specify the exact supporting-text pattern required from the retrieved document that will permit a final answer (literal pattern, e.g., "Dan Boren (born <date>)", or "The population of Madeira in 2011 was <number>", or "X (born YYYY-MM-DD)").
- Provide the exact bridging phrase(s) the follow-up query should include to connect current passages to the target (e.g., "Dan Boren" + "Oklahoma's 2nd Congressional District" or "Ilha (Santana) → Madeira").
- Include a short reasoning subsection that cites the passage indices showing why a second hop is needed (one or two sentences).

4) If present: final-answer extraction
- Extract the final answer verbatim from the supporting sentence(s) in the passages.
- State the exact supporting-text pattern matched.
- Cite the passage index(es) that contain the supporting text.

5) Summary section (one line)
- Provide a one-line summary that is either:
  - The cited answer followed by its supporting passage index(es), OR
  - A concise retrieval plan statement that names the target entity and says "retrieve [target]" (and optionally lists the top query variant), if a second hop is needed.
- Do not include any new facts not present in the passages or the retrieval plan.

6) Constraints and behavior
- Never answer from memory. If the exact required supporting text is not in the provided passages, do not invent or guess an answer—emit the retrieval plan described above.
- Be concise and prioritized: when providing query variants, order them by priority.
- Always include passage indices in reasoning to justify conclusions.
- Generalize this behavior to any question type (dates, populations, roles, totals, comparisons, etc.).""",

        "create_query_hop2.predict": (
            "Given the fields `question`, `summary_1`, "
            "produce the fields `query`."
        ),

        "summarize2.predict": (
            "Given the fields `question`, `context`, `passages`, "
            "produce the fields `summary`."
        ),

        "final_answer.predict": """You are given three fields as input: question, summary_1, summary_2. Produce output containing exactly two blocks in this order and exact format (no other text, blocks, or commentary):

[[ ## reasoning ## ]]
[[ ## answer ## ]]

Rules for [[ ## reasoning ## ]]:
- Use only the contents of summary_1 and summary_2 to support premises and the final answer, except for one allowed metadata line: you must include a single numbered item that documents the detected question type and the chosen output form (see "Question type detection" below). All other numbered items must attribute their content to a summary.
- Present a short, numbered sequence of concise premises and a brief derivation, or a statement that the conclusion cannot be reached. Keep the reasoning to one or two lines per numbered item where possible while still numbered and sufficient to show the inference.
- Each numbered item that cites a summary must explicitly attribute its content using one of these exact phrasings: "summary_1 states: \\"...\\"" or "summary_2 states: \\"...\\"" (you may paraphrase the quoted text but must include the exact label). If both summaries supply the same premise, you may combine it and indicate both sources as "(summary_1, summary_2)".
- If you remove any parenthetical content or editorial qualifiers from a name/title to create a canonical form for the answer, list each removed parenthetical or qualifier in the reasoning block and attribute it to the summary that contained it using the exact phrasing above (e.g. summary_2 states: "X (the Mighty Handful)"; removed: "(the Mighty Handful)").
- The reasoning must show which premises were used and how the conclusion follows, or why it cannot be reached (conflict or silence). Keep steps concise and numbered.
- Question type detection: before applying normalization or selecting the output token, determine whether the question is a confirmation (yes/no), a request for a category/label, or another type. Include exactly one numbered reasoning item that states the detected question type and the chosen output form. This metadata item need not quote a summary; phrase it clearly, e.g. "Detected question type: confirmation. Chosen output form: yes/no/insufficient information." Place this metadata item as the first or last numbered item in the reasoning.

Normalization and selection rule (Generalized Update Direction):
- If the detected question type is confirmation, answer exactly "yes", "no", or "insufficient information" as supported by the summaries.
- When the required answer is an occupation or category label, normalize it to a single canonical noun phrase in singular form and lowercase (unless the label is a proper noun). Prefer the more specific supported label when the summaries differ (for example, prefer "professional wrestler" over "wrestler" if one summary supplies the more specific form). If neither summary clearly supports a more specific label (conflict or different incompatible categories), return "insufficient information".
- Provide the normalization in the reasoning (cite which summary supports the chosen normalized label). The reasoning should be one or two concise numbered items that cite summary_1 and/or summary_2 for the normalization.

Rules for [[ ## answer ## ]]:
- The answer block must contain only the minimal required token or short label derived solely from the reasoning block and nothing else (no punctuation, no extra words, no capitalization beyond the canonicalization rule).
- If the question is a confirmation, the answer must be exactly one of: yes, no, insufficient information.
- If the answer is a name/title, return the cleaned canonical string by stripping nonessential parenthetical content and editorial qualifiers (do not include the removed parentheticals or qualifiers in this field). Prefer the base token exactly as present in the summaries where possible.
- For occupation/category outputs follow the normalization rule: singular noun phrase, lowercase (unless proper noun), and choose the more specific supported label when summaries differ.
- If the summaries do not provide enough information or they conflict on the needed point(s), return exactly: insufficient information
- Do not add any extra text, salutations, or sections. The answer block must be a single minimal token or short label only.

Strict hygiene:
- Emit exactly the two blocks shown above and nothing else.
- The reasoning must be numbered and cite which summary supplied each premise using the exact phrasings required, except for the one permitted question-type metadata item.
- Use only summary_1 and summary_2 to derive the answer (aside from the required question-type metadata line).
- The reasoning must include the detected question type and the chosen output form as specified.

Follow these rules for every input."""
    },
}


CANDIDATE_PROMPT_SETS = {
    "baseline": BASELINE_PROMPT_SET,
    "agentgrad_best": AGENTGRAD_PROMPT_SET,
}


FEEDBACK_DISTANCE_PROMPT_V0 = """You are judging semantic magnitude between two local prompt-feedback updates.

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
{{
  "larger_segment": "A" | "B" | "tie",
  "segment_index": 0 | 1 | -1,
  "why_larger": "short explanation focused on semantic feedback magnitude",
  "dominant_gap_type": "anchor|bridge_relation|surface_form|noisy_entity|answer_type|query_shape|candidate_set|evidence_family|mixed|tie",
  "confidence": 0.0
}}

Question:
{question}

summary_1:
{summary_1}

Candidate feedback segments:
{segments_json}"""


METHOD_PROMPTS = {
    "feedback_distance_v0": FEEDBACK_DISTANCE_PROMPT_V0,
}


def build_seed_candidate(program=None) -> dict[str, str]:
    candidate = dict(BASELINE_PROMPT_SET["prompts"])

    if program is not None:
        validate_candidate(candidate, program=program)

    return candidate


def validate_candidate(
    candidate: dict[str, str],
    program=None,
) -> None:
    if not isinstance(candidate, dict):
        raise TypeError("Candidate must be a dict[str, str].")

    for key, value in candidate.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("Candidate must be a dict[str, str].")

    if program is None:
        expected = set(BASELINE_PROMPT_SET["prompts"])
    else:
        expected = {
            name
            for name, _ in program.named_predictors()
        }

    actual = set(candidate)

    missing = expected - actual
    extra = actual - expected

    if missing:
        raise ValueError(
            f"Prompt candidate is missing predictor keys: {sorted(missing)}"
        )

    if extra:
        raise ValueError(
            f"Prompt candidate has unknown predictor keys: {sorted(extra)}"
        )


def load_prompt_candidate(
    path: str | Path,
    program=None,
) -> tuple[str, dict[str, str]]:
    path = Path(path)
    obj = json.loads(path.read_text())

    if "prompts" not in obj:
        raise ValueError(
            f"Prompt JSON must contain top-level `prompts`: {path}"
        )

    candidate = obj["prompts"]
    validate_candidate(candidate, program=program)

    name = str(obj.get("name", path.stem))
    return name, dict(candidate)


def save_prompt_candidate(
    path: str | Path,
    name: str,
    candidate: dict[str, str],
    description: str | None = None,
    program=None,
) -> None:
    validate_candidate(candidate, program=program)

    obj: dict[str, Any] = {
        "name": name,
        "prompts": candidate,
    }

    if description is not None:
        obj["description"] = description

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            obj,
            indent=2,
            ensure_ascii=False,
        )
    )


def get_method_prompt(name: str) -> str:
    try:
        return METHOD_PROMPTS[name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown method prompt: {name}. "
            f"Available prompts: {sorted(METHOD_PROMPTS)}"
        ) from exc


def render_method_prompt(
    name: str,
    **inputs: Any,
) -> str:
    return get_method_prompt(name).format(**inputs)
