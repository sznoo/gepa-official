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


FEEDBACK_DISTANCE_1N_FINAL_PROMPT_V0 = """You are selecting the local prompt-feedback update that is semantically closest to a fixed anchor update.

Each material contains feedback for the HotpotQA final-answer generator.
Compare the anchor against all candidate materials and select exactly one candidate whose feedback represents the most similar behavioral update.

Here, semantic distance means how differently the final-answer behavior would need to change:
- which answer span, alias, title, name, category, number, or location to select
- which parenthetical, qualifier, appositive, descriptor, or locative detail to preserve or remove
- whether to keep the outer canonical span or instead select an inner alias, translation, abbreviation, or alternate form
- whether to normalize morphology, plurality, spelling, numeric representation, or answer framing
- how conflicting or incomplete summaries should be prioritized
- whether the update relies only on visible summary text or permits limited internal knowledge
- whether the output change is surface formatting, answer-span replacement, evidence arbitration, or answer-type reinterpretation

Important:
- Judge the semantic update represented by the feedback itself.
- Do not judge which update is more correct, useful, general, or likely to improve accuracy.
- Do not select a candidate merely because it shares entities, topics, question wording, answer strings, or punctuation with the anchor.
- Do not select a candidate merely because its feedback is longer or more detailed.
- Generic instructions about minimal answers, punctuation, capitalization, and the output block are mostly boilerplate.
- Similar textual triggers can still represent different updates. In particular, removing parenthetical content and selecting parenthetical content are opposite selection directions.
- If a material contains multiple delta_p edges, compare the complete ordered behavioral update.
- Select exactly one candidate. If multiple candidates request materially equivalent updates, choose the one with the smallest sample_index.

Return JSON only:
{{
  "selected_sample_index": 0,
  "shared_update_pattern": "short description of the behavioral update shared by the anchor and selected candidate",
  "rationale": "short explanation of why this candidate is semantically closest to the anchor",
  "confidence": 0.0
}}

Requirements:
- selected_sample_index must exactly match one candidate sample_index.
- confidence must be between 0.0 and 1.0.
- Do not return markdown or additional keys.

Agent:
{agent}

Anchor feedback material:
{anchor_json}

Candidate feedback materials:
{candidates_json}"""

FEEDBACK_DISTANCE_1N_SUMMARY2_PROMPT_V0 = """You are selecting the local prompt-feedback update that is semantically closest to a fixed anchor update.

Each material contains feedback for the HotpotQA second-hop summarization agent.
Compare the anchor against all candidate materials and select exactly one candidate whose feedback represents the most similar summarization behavior update.

Here, semantic distance means how differently summary2 would need to integrate first-hop context with retrieved second-hop passages:
- which existing first-hop claim, answer entity, relation, or numeric fact to preserve
- which passage-backed facts to add as corroboration, justification, clarification, or metadata
- whether to expand a bare answer into an evidence-backed summary
- whether one passage is sufficient or multiple complementary passages must be connected
- which bridge relation between an entity, role, work, location, definition, or target property must be retained
- whether passages directly support the claim or provide only identity or metadata
- which facts must be explicitly retained for the downstream final-answer agent
- whether the update changes evidence integration, attribution, summary structure, or output granularity

Important:
- Judge the semantic update represented by the feedback itself.
- Do not judge which update is more correct, useful, general, or likely to improve final-answer accuracy.
- Do not select a candidate merely because it shares entities, topics, passage titles, question wording, or answer strings with the anchor.
- Do not select a candidate merely because its feedback is longer or requests more sentences.
- Formatting details such as section labels, bullets, quotations, passage-title notation, and exact sentence counts are secondary unless they change the evidence-integration behavior.
- Distinguish direct corroboration from complementary bridge integration and from metadata-only retention.
- Expanding a bare entity with one supporting role fact is different from combining multiple passages to construct a bridge relation.
- If a material contains multiple delta_p edges, compare the complete ordered behavioral update.
- Select exactly one candidate. If candidates request materially equivalent updates, choose the one with the smallest sample_index.

Return JSON only:
{{
  "selected_sample_index": 0,
  "shared_update_pattern": "short description of the evidence-integration behavior shared by the anchor and selected candidate",
  "rationale": "short explanation of why this candidate is semantically closest to the anchor",
  "confidence": 0.0
}}

Requirements:
- selected_sample_index must exactly match one candidate sample_index.
- confidence must be between 0.0 and 1.0.
- Do not return markdown or additional keys.

Agent:
{agent}

Anchor feedback material:
{anchor_json}

Candidate feedback materials:
{candidates_json}"""

FEEDBACK_DISTANCE_1N_QUERY_PROMPT_V0 = """You are selecting the local prompt-feedback update that is semantically closest to a fixed anchor update.

Each material contains feedback for the HotpotQA second-hop query generator.
Compare the anchor against all candidate materials and select exactly one candidate whose feedback represents the most similar query-generation behavior update.

Here, semantic distance means how differently the retrieval query behavior would need to change:
- which entity, title, alias, location, class, or task anchors to preserve, add, remove, or disambiguate
- whether an anchor is grounded in the visible inputs, misleading, or an unsupported hypothesized answer
- which bridge relation, comparison relation, role, property, or information need to emphasize
- which evidence family, domain, or answer type the query should target
- which distractors, wrong senses, prior answers, or noisy entity families to avoid
- whether the candidate scope should be broadened, narrowed, preserved, or re-centered
- whether the query should use compact keywords, preserve a comparison, or restate an open information need
- what retrieval failure the feedback is intended to correct

Important:
- Judge the semantic update represented by the feedback itself.
- Do not judge which update is more correct or likely to improve retrieval.
- Do not select a candidate merely because it shares entities, topics, question wording, or query tokens with the anchor.
- Do not select a candidate merely because its feedback is longer or more detailed.
- Source-style details such as infoboxes, lead sentences, cast sections, tables, or list parsing are secondary unless they change the retrieval target.
- Broadening from one entity to multiple comparison subjects is different from narrowing a broad query to one missing entity.
- Removing a misleading visible anchor is different from preventing insertion of an unsupported candidate.
- Changing from a verbose sentence to compact keywords matters only when it changes the retrieval strategy or target.
- If a material contains multiple delta_p edges, compare the complete ordered trace and its net retrieval-policy change, not only matching individual edges.
- Select exactly one candidate. If candidates request materially equivalent updates, choose the one with the smallest sample_index.

Return JSON only:
{{
  "selected_sample_index": 0,
  "shared_update_pattern": "short description of the retrieval-policy update shared by the anchor and selected candidate",
  "rationale": "short explanation of why this candidate is semantically closest to the anchor",
  "confidence": 0.0
}}

Requirements:
- selected_sample_index must exactly match one candidate sample_index.
- confidence must be between 0.0 and 1.0.
- Do not return markdown or additional keys.

Agent:
{agent}

Anchor feedback material:
{anchor_json}

Candidate feedback materials:
{candidates_json}"""

FEEDBACK_DISTANCE_1N_SUMMARY1_PROMPT_V0 = """You are selecting the local prompt-feedback update that is semantically closest to a fixed anchor update.

Each material contains feedback for the HotpotQA first-hop summarization agent.
Compare the anchor against all candidate materials and select exactly one candidate whose feedback represents the most similar summary1 behavior update.

Here, semantic distance means how differently summary1 would need to expose the first-hop evidence and prepare the next retrieval hop:
- which passage-supported entity, relation, work, event, or attribute to preserve
- whether to replace a bare answer, premature conclusion, refusal, or clarification-only response
- which parts of the question are already supported and which remain unverified
- whether the bridge is a named entity, an ambiguous identity, a missing attribute, or an unknown intersection between two sets
- which irrelevant, wrong-sense, or insufficient passages to identify
- whether to defer an unsupported final answer or candidate commitment
- which article, biography, cast list, filmography, event page, or list page the next hop should retrieve
- whether retrieval requires one direct lookup or an ordered multi-step plan

Important:
- Judge the semantic update represented by the feedback itself.
- Do not judge which update is more correct, useful, general, or likely to improve retrieval.
- Do not select a candidate merely because it shares entities, topics, passage titles, question wording, or answer strings with the anchor.
- Do not select a candidate merely because its feedback is longer or contains more retrieval suggestions.
- Formatting details such as labels, bullets, quotations, exact sentence counts, and phrases like "not a final answer" are secondary.
- Extracting a named bridge entity is different from searching for an unknown intersection entity.
- Identifying an ambiguous person is different from retrieving a missing attribute of an already identified entity.
- Converting a bare answer into evidence plus a retrieval plan is different from converting a generic inability statement into a targeted next-hop request.
- A single-page lookup is different from an ordered plan that first identifies a bridge entity and then retrieves that entity's requested attribute.
- If a material contains multiple delta_p edges, compare the complete ordered trace and its net evidence-to-retrieval behavior change.
- Select exactly one candidate. If candidates request materially equivalent updates, choose the one with the smallest sample_index.

Return JSON only:
{{
  "selected_sample_index": 0,
  "shared_update_pattern": "short description of the first-hop evidence and bridge behavior shared by the anchor and selected candidate",
  "rationale": "short explanation of why this candidate is semantically closest to the anchor",
  "confidence": 0.0
}}

Requirements:
- selected_sample_index must exactly match one candidate sample_index.
- confidence must be between 0.0 and 1.0.
- Do not return markdown or additional keys.

Agent:
{agent}

Anchor feedback material:
{anchor_json}

Candidate feedback materials:
{candidates_json}"""


FEEDBACK_NORM_1N_FINAL_PROMPT_V0 = """You are selecting the candidate prompt-feedback update with the smallest semantic norm relative to the current HotpotQA final-answer behavior.

Each candidate is an admissible feedback update for the final-answer generator. The upstream generation stage has already required every candidate to address the supplied repair and preservation evidence. Your task here is not to re-evaluate correctness. Compare all candidate feedback updates and select exactly one whose requested behavioral change is semantically smallest relative to leaving the current prompt unchanged.

This is an order-based semantic comparison:
- Do not assign or estimate a numeric distance, score, radius, or magnitude.
- Do not combine semantic norm with expected accuracy, usefulness, generality, confidence, or implementation quality.
- Select the minimum element among the supplied candidates according to the semantic-change criteria below.
- If multiple candidates request materially equivalent minimum changes, choose the one with the smallest candidate_index.

For the final-answer generator, a feedback update has smaller semantic norm when it changes fewer existing answer behaviors and preserves more of the current policy, including:
- which visible premise or summary is treated as decisive
- how conflicts or incomplete summaries are resolved
- which answer-bearing entity, span, alias, title, category, number, date, or location is selected
- whether an outer canonical expression or an inner alias, translation, abbreviation, or alternate form is emitted
- whether qualifiers, parentheticals, appositives, descriptors, locative details, morphology, plurality, spelling, or numeric representation are preserved or removed
- whether the update changes semantic answer selection, evidence arbitration, uncertainty behavior, answer-type interpretation, or only final serialization
- how many distinct question intents, answer families, or behavioral regions are affected

Semantic norm principles:
- A clarification of one existing semantic principle is smaller than adding several independent rules.
- A change limited to the demonstrated answer-selection condition is smaller than a global normalization policy.
- Preserving the current evidence-use and uncertainty behavior is smaller than introducing new abstention, conflict, or direct-support requirements.
- One general sufficiency condition is smaller than a taxonomy of aliases, punctuation, parentheticals, locations, dates, categories, or answer types.
- Replacing an existing behavior only where necessary is smaller than rewriting unrelated answer-selection policy.
- A short feedback is not necessarily smaller, and a long feedback is not necessarily larger.
- Textual overlap with the current prompt is not the semantic norm.
- Wording, formatting, bullet count, sentence count, and verbosity are secondary unless they introduce additional behavioral commitments.

Important exclusions:
- Do not judge which candidate is more correct, safer, more useful, more general, or more likely to improve exact match.
- Do not prefer a candidate because it sounds conservative or detailed.
- Do not prefer a candidate because it contains more preservation language.
- Do not use proper-noun overlap, answer-string overlap, shared examples, or copied phrasing as evidence of smaller norm.
- Do not select a no-op interpretation unless a candidate explicitly requests no behavioral change; all ordinary candidates should be compared as proposed updates.

Return JSON only:
{{
  "selected_candidate_index": 0,
  "minimum_update_pattern": "short description of the smallest semantic behavior change",
  "rationale": "short explanation of why this candidate changes less final-answer behavior than the alternatives",
  "confidence": 0.0
}}

Requirements:
- selected_candidate_index must exactly match one candidate_index.
- confidence must be between 0.0 and 1.0.
- Do not return a numeric semantic norm.
- Do not return markdown or additional keys.

Agent:
{agent}

Current base prompt:
{base_prompt}

Candidate feedback updates:
{candidates_json}"""


FEEDBACK_NORM_1N_SUMMARY2_PROMPT_V0 = """You are selecting the candidate prompt-feedback update with the smallest semantic norm relative to the current HotpotQA second-hop summarization behavior.

Each candidate is an admissible feedback update for the summary2 agent. The upstream generation stage has already required every candidate to address the supplied repair and preservation evidence. Your task here is not to re-evaluate correctness. Compare all candidate feedback updates and select exactly one whose requested behavioral change is semantically smallest relative to leaving the current prompt unchanged.

This is an order-based semantic comparison:
- Do not assign or estimate a numeric distance, score, radius, or magnitude.
- Do not combine semantic norm with expected accuracy, usefulness, generality, confidence, or implementation quality.
- Select the minimum element among the supplied candidates according to the semantic-change criteria below.
- If multiple candidates request materially equivalent minimum changes, choose the one with the smallest candidate_index.

For summary2, a feedback update has smaller semantic norm when it changes fewer existing evidence-integration behaviors and preserves more of the current policy, including:
- which first-hop claims, bridge entities, answer candidates, relations, or numeric facts are retained from context
- which retrieved passage facts are incorporated as corroboration, clarification, metadata, identity evidence, or answer-bearing support
- whether one passage is sufficient or several complementary passages must be composed
- which entity alignments, aliases, roles, dates, works, locations, or target properties are considered identity-compatible
- whether visible facts may be composed to derive the requested relation
- when the summary preserves uncertainty rather than resolving the bridge
- which facts must remain explicit for the downstream final-answer agent
- whether the update changes evidence admission, cross-passage composition, attribution, summary granularity, or output structure
- how many distinct relation families, evidence families, or behavioral regions are affected

Semantic norm principles:
- Clarifying one existing integration condition is smaller than introducing several independent passage-handling rules.
- A change restricted to the demonstrated bridge or evidence-use failure is smaller than a global direct-predication policy.
- Preserving currently allowed identity-aligned composition is smaller than introducing new restrictions on implication, transitivity, or multi-passage reasoning.
- One general grounding condition is smaller than a taxonomy of passage types, relation types, entity types, support patterns, or summary formats.
- Retaining existing uncertainty behavior is smaller than creating new abstention triggers.
- Replacing only the implicated evidence-integration rule is smaller than restructuring the entire summary protocol.
- A short feedback is not necessarily smaller, and a long feedback is not necessarily larger.
- Textual overlap with the current prompt is not the semantic norm.
- Wording, formatting, bullet count, sentence count, and verbosity are secondary unless they introduce additional behavioral commitments.

Important exclusions:
- Do not judge which candidate is more correct, safer, more useful, more general, or more likely to improve the final answer.
- Do not prefer a candidate because it sounds more grounded, explicit, cautious, or detailed.
- Do not use shared entities, passage titles, relation words, answer strings, or copied phrasing as evidence of smaller norm.
- Do not treat direct-statement requirements as inherently smaller merely because they narrow the accepted evidence set; removing a previously available composition capability is a semantic change.
- Do not select a no-op interpretation unless a candidate explicitly requests no behavioral change; all ordinary candidates should be compared as proposed updates.

Return JSON only:
{{
  "selected_candidate_index": 0,
  "minimum_update_pattern": "short description of the smallest semantic evidence-integration change",
  "rationale": "short explanation of why this candidate changes less summary2 behavior than the alternatives",
  "confidence": 0.0
}}

Requirements:
- selected_candidate_index must exactly match one candidate_index.
- confidence must be between 0.0 and 1.0.
- Do not return a numeric semantic norm.
- Do not return markdown or additional keys.

Agent:
{agent}

Current base prompt:
{base_prompt}

Candidate feedback updates:
{candidates_json}"""


FEEDBACK_NORM_1N_QUERY_PROMPT_V0 = """You are selecting the candidate prompt-feedback update with the smallest semantic norm relative to the current HotpotQA second-hop query-generation behavior.

Each candidate is an admissible feedback update for the query agent. The upstream generation stage has already required every candidate to address the supplied repair and preservation evidence. Your task here is not to re-evaluate correctness. Compare all candidate feedback updates and select exactly one whose requested behavioral change is semantically smallest relative to leaving the current prompt unchanged.

This is an order-based semantic comparison:
- Do not assign or estimate a numeric distance, score, radius, or magnitude.
- Do not combine semantic norm with expected retrieval quality, usefulness, generality, confidence, or implementation quality.
- Select the minimum element among the supplied candidates according to the semantic-change criteria below.
- If multiple candidates request materially equivalent minimum changes, choose the one with the smallest candidate_index.

For the query generator, a feedback update has smaller semantic norm when it changes fewer existing retrieval behaviors and preserves more of the current policy, including:
- which visible entity, title, alias, location, class, work, event, or task anchors are retained, added, removed, or disambiguated
- whether an anchor is treated as grounded, misleading, ambiguous, or an unsupported hypothesized answer
- which bridge relation, comparison relation, role, property, or missing information need is expressed
- which evidence family, domain, document type, or answer type is targeted
- which distractors, wrong senses, prior answers, or noisy entity families are excluded
- whether candidate scope is broadened, narrowed, preserved, or re-centered
- whether the query uses compact keywords, a page-title lookup, a comparison-preserving form, or an open information need
- whether the update changes retrieval target, anchor policy, query scope, relation expression, or only surface phrasing
- how many distinct query families, question types, or behavioral regions are affected

Semantic norm principles:
- Clarifying one anchor-selection or retrieval-target condition is smaller than introducing several independent query-construction rules.
- A change restricted to the demonstrated missing bridge is smaller than a global query grammar.
- Preserving useful visible anchors and relation terms is smaller than globally banning lexical forms or forcing one noun-phrase template.
- One general retrieval-intent principle is smaller than a taxonomy of dates, occupations, biographies, institutions, page titles, answer types, or relation tokens.
- Retaining current fallback and ambiguity behavior is smaller than introducing new sentinel outputs or abstention branches.
- Replacing only the implicated retrieval behavior is smaller than restructuring unrelated query-generation policy.
- A short feedback is not necessarily smaller, and a long feedback is not necessarily larger.
- Textual overlap with the current prompt is not the semantic norm.
- Wording, formatting, token count, and verbosity are secondary unless they introduce additional behavioral commitments.

Important exclusions:
- Do not judge which candidate is more correct, safer, more useful, more general, or more likely to improve retrieval.
- Do not prefer a candidate because it sounds more specific, compact, constrained, or detailed.
- Do not use shared entities, question wording, query tokens, relation words, or copied phrasing as evidence of smaller norm.
- Do not treat a narrower query grammar as inherently smaller; forbidding previously valid query forms changes behavior.
- Do not select a no-op interpretation unless a candidate explicitly requests no behavioral change; all ordinary candidates should be compared as proposed updates.

Return JSON only:
{{
  "selected_candidate_index": 0,
  "minimum_update_pattern": "short description of the smallest semantic retrieval-policy change",
  "rationale": "short explanation of why this candidate changes less query-generation behavior than the alternatives",
  "confidence": 0.0
}}

Requirements:
- selected_candidate_index must exactly match one candidate_index.
- confidence must be between 0.0 and 1.0.
- Do not return a numeric semantic norm.
- Do not return markdown or additional keys.

Agent:
{agent}

Current base prompt:
{base_prompt}

Candidate feedback updates:
{candidates_json}"""


FEEDBACK_NORM_1N_SUMMARY1_PROMPT_V0 = """You are selecting the candidate prompt-feedback update with the smallest semantic norm relative to the current HotpotQA first-hop summarization behavior.

Each candidate is an admissible feedback update for the summary1 agent. The upstream generation stage has already required every candidate to address the supplied repair and preservation evidence. Your task here is not to re-evaluate correctness. Compare all candidate feedback updates and select exactly one whose requested behavioral change is semantically smallest relative to leaving the current prompt unchanged.

This is an order-based semantic comparison:
- Do not assign or estimate a numeric distance, score, radius, or magnitude.
- Do not combine semantic norm with expected retrieval quality, usefulness, generality, confidence, or implementation quality.
- Select the minimum element among the supplied candidates according to the semantic-change criteria below.
- If multiple candidates request materially equivalent minimum changes, choose the one with the smallest candidate_index.

For summary1, a feedback update has smaller semantic norm when it changes fewer existing first-hop evidence and bridge-preparation behaviors and preserves more of the current policy, including:
- which passage-supported entities, relations, works, events, locations, dates, or attributes are retained
- whether a bare answer, premature conclusion, refusal, clarification-only response, or unsupported candidate commitment is replaced
- which parts of the question are treated as supported, ambiguous, missing, or unverified
- whether the unresolved bridge is a named entity, ambiguous identity, missing attribute, comparison operand, or unknown intersection
- which irrelevant, wrong-sense, insufficient, or distractor passages are identified
- whether an unsupported final answer is deferred
- which retrieval target or information need is exposed to the next-hop query agent
- whether retrieval requires one direct lookup or an ordered multi-step plan
- whether the update changes evidence compression, bridge representation, missing-information reporting, retrieval planning, or output structure
- how many distinct question families, bridge types, or behavioral regions are affected

Semantic norm principles:
- Clarifying one existing evidence-to-bridge condition is smaller than introducing several independent report sections or retrieval branches.
- A change restricted to the demonstrated missing information is smaller than a global COMPLETE/INCOMPLETE decision procedure.
- Preserving concise grounded compression is smaller than introducing a larger mandatory reporting protocol.
- One general bridge-exposure principle is smaller than a taxonomy of biographies, attributes, dates, works, institutions, page types, or retrieval priorities.
- Retaining current uncertainty behavior is smaller than creating new abstention, sentinel, or clarification branches.
- Replacing only the implicated first-hop behavior is smaller than restructuring unrelated summarization policy.
- A short feedback is not necessarily smaller, and a long feedback is not necessarily larger.
- Textual overlap with the current prompt is not the semantic norm.
- Wording, formatting, bullet count, sentence count, and verbosity are secondary unless they introduce additional behavioral commitments.

Important exclusions:
- Do not judge which candidate is more correct, safer, more useful, more general, or more likely to improve retrieval.
- Do not prefer a candidate because it sounds more comprehensive, structured, grounded, or detailed.
- Do not use shared entities, passage titles, question wording, answer strings, or copied phrasing as evidence of smaller norm.
- Do not treat a more elaborate structured report as a smaller update merely because it preserves more explicit information; adding required behavior is a semantic change.
- Do not select a no-op interpretation unless a candidate explicitly requests no behavioral change; all ordinary candidates should be compared as proposed updates.

Return JSON only:
{{
  "selected_candidate_index": 0,
  "minimum_update_pattern": "short description of the smallest semantic first-hop behavior change",
  "rationale": "short explanation of why this candidate changes less summary1 behavior than the alternatives",
  "confidence": 0.0
}}

Requirements:
- selected_candidate_index must exactly match one candidate_index.
- confidence must be between 0.0 and 1.0.
- Do not return a numeric semantic norm.
- Do not return markdown or additional keys.

Agent:
{agent}

Current base prompt:
{base_prompt}

Candidate feedback updates:
{candidates_json}"""


METHOD_PROMPTS = {
    "feedback_distance_v0": FEEDBACK_DISTANCE_PROMPT_V0,
    "feedback_distance_1n_final_v0": FEEDBACK_DISTANCE_1N_FINAL_PROMPT_V0,
    "feedback_distance_1n_summary2_v0": FEEDBACK_DISTANCE_1N_SUMMARY2_PROMPT_V0,
    "feedback_distance_1n_query_v0": FEEDBACK_DISTANCE_1N_QUERY_PROMPT_V0,
    "feedback_distance_1n_summary1_v0": FEEDBACK_DISTANCE_1N_SUMMARY1_PROMPT_V0,
    "feedback_norm_1n_final_v0": FEEDBACK_NORM_1N_FINAL_PROMPT_V0,
    "feedback_norm_1n_summary2_v0": FEEDBACK_NORM_1N_SUMMARY2_PROMPT_V0,
    "feedback_norm_1n_query_v0": FEEDBACK_NORM_1N_QUERY_PROMPT_V0,
    "feedback_norm_1n_summary1_v0": FEEDBACK_NORM_1N_SUMMARY1_PROMPT_V0,
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
        prompt = METHOD_PROMPTS[name]
    except KeyError as exc:
        raise KeyError(
            f"Unknown method prompt: {name}. "
            f"Available prompts: {sorted(METHOD_PROMPTS)}"
        ) from exc

    if not prompt.strip():
        raise ValueError(
            f"Method prompt is empty: {name}"
        )

    return prompt


def render_method_prompt(
    name: str,
    **inputs: Any,
) -> str:
    return get_method_prompt(name).format(**inputs)