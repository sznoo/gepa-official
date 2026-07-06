#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import inspect
import json
import sys
from pathlib import Path
from functools import wraps

ROOT = Path(__file__).resolve().parents[3]
BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"

if not BASE_SCRIPT.exists():
    raise FileNotFoundError(f"Base script not found: {BASE_SCRIPT}")

spec = importlib.util.spec_from_file_location("_hop2_candidate_search_base", BASE_SCRIPT)
base = importlib.util.module_from_spec(spec)
sys.modules["_hop2_candidate_search_base"] = base
assert spec.loader is not None
spec.loader.exec_module(base)


AGENTGRAD_SENTINEL = "__AGENTGRAD_BEST_FULL_SENTINEL__"


FINAL_V2_SPAN_RECOVER = """Given the fields `question`, `summary_1`, `summary_2`, produce the field `answer`.

Answer with the shortest exact answer span supported by the summaries.

Use these rules:
- Return only the final answer string. No explanation.
- Prefer an explicit "Answer", "Direct answer", "Shared/answer", "answer:", "Answerable fact", or "Primary answer" phrase in `summary_1` or `summary_2` when present.
- If the question is yes/no, answer only `yes` or `no`.
- Strip explanatory prefixes such as "both are", "labels for", "the answer is", "entity:", "film title:", "primary answer:", "direct answer:".
- Strip leading prepositions such as "for", "in", "at", "by", "from", and "because" when they are not part of the named answer.
- Strip trailing periods.

Span calibration:
- Prefer the shortest span that still exactly answers the requested type.
- Strip parenthetical acronyms and aliases after names unless the question explicitly asks for the acronym or alias.
- Strip trailing country when the direct location is city + state/province and the country is only extra context.
- Strip leading weekday names from dates unless the question explicitly asks for the weekday.
- Strip role suffixes such as "ruler", "city", "country", "album", "film", or "TV series" when the requested answer is the bare ordinal/name/title/date and the suffix is only explanatory.

For location questions asking where, birthplace, headquarters, based in what city, or located where:
- Prefer a city + state/province/country phrase if that exact phrase appears in the summaries.
- Do not output only the city if the summary gives a more specific answer phrase such as `London, England`, `Mississauga, Ontario`, `Independence, Kansas`, `Columbus, Ohio`, or `Footscray, Australia`.
- Strip trailing country if the expected Hotpot-style answer is city + state/province.

For work titles:
- Strip disambiguating parentheticals such as `(TV series)`, `(film)`, or alternate-language titles when the shorter title is the requested title and remains unambiguous.
- Preserve parentheticals that are part of the canonical title itself, such as `America (The Book)`.
- Strip subtitles after a colon unless the question asks for the full subtitle.

For people:
- If the question identifies a person by a descriptive biography phrase and the summary gives both a short/stage name and a full legal name, prefer the full name.

For common-attribute questions:
- If the question asks what occupation, institution, category, type, genre, or commonality two entities have in common, answer with the common type word or phrase when that is what the question requests.

For numeric/count/date questions:
- Prefer the exact phrase used in the summary when the question wording asks for a credited/stated phrase.
- Otherwise return the minimal number/date/unit phrase.
- Do not include weekday names unless asked.

Do not output multiple candidates unless the question explicitly asks for multiple answers.
"""


# =========================
# AgentGrad-best full prompts
# =========================

AGENTGRAD_SUMMARIZE1 = """Given inputs question (string) and passages (list of strings), produce a single textual output to populate the field "summary". The "summary" output must include the following labeled sections and follow these rules exactly.

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
- Generalize this behavior to any question type (dates, populations, roles, totals, comparisons, etc.).
"""

AGENTGRAD_CREATE_QUERY_HOP2 = """Given the fields `question`, `summary_1`, produce the fields `query`."""

AGENTGRAD_SUMMARIZE2 = """Given the fields `question`, `context`, `passages`, produce the fields `summary`."""

AGENTGRAD_FINAL = """You are given three fields as input: question, summary_1, summary_2. Produce output containing exactly two blocks in this order and exact format (no other text, blocks, or commentary):

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

Follow these rules for every input.
"""

AGENTGRAD_PROMPTS = {
    "summarize1.predict": AGENTGRAD_SUMMARIZE1,
    "create_query_hop2.predict": AGENTGRAD_CREATE_QUERY_HOP2,
    "summarize2.predict": AGENTGRAD_SUMMARIZE2,
    "final_answer.predict": AGENTGRAD_FINAL,
}


# =========================
# Our comparison prompts
# =========================

OUR_RETRIEVAL_BEST_R6_ORIGINAL = """Given `question` and `summary_1`, produce a second-hop BM25 search query.

The query must be a compact keyword query, not an explanation.

Reversibility constraints:
- Preserve task-relevant named entities, titles, aliases, dates, relations, and uncertainty markers that are present in `question` or `summary_1`.
- Do not introduce new entities, aliases, facts, candidate answers, or support titles not present in the input.
- If a candidate is uncertain, preserve it as uncertain; do not treat it as confirmed.
- If multiple candidates are present, keep them as a candidate set rather than collapsing to one candidate.
- The original retrieval problem and correction direction should be recoverable from the query behavior.

Optimization-usefulness constraints:
- Do not merely restate the full question.
- Do not produce generic role-only queries when concrete names or titles are available.
- Make the query expose a useful retrieval direction: what to preserve, what to verify, and what missing relation to target.

Representation guide:
Use a reversible edit-script representation.
Imagine transforming a weak query into a stronger one:
keep essential anchors, restore missing relation words, retain uncertain candidates as a set, and delete only irrelevant verbosity.
The final query should reflect the edited behavior.

Minibatch emphasis:
Prioritize missing-support recovery.
The useful query should retrieve the page that was missing after the first hop or after a weak second-hop query.
Favor terms that identify the support page, relation evidence, and answer-bearing page.

Rewrite style:
Be conservative.
Prefer high reversibility and explicit lexical preservation.
Use enough context for BM25, but avoid long explanatory sentences.
Do not over-generalize.

Output rules:
- Output only the query.
- Use concrete names, titles, aliases, and relation terms.
- Do not output bullet points, explanations, or JSON.
- Do not invent facts.
"""

OUR_EM_BEST_R6V2 = """Given `question` and `summary_1`, produce a second-hop BM25 search query.

The query must be a compact keyword query, not an explanation.

Core reversibility constraints:
- Preserve task-relevant named entities, titles, aliases, dates, relations, and uncertainty markers that are present in `question` or `summary_1`.
- Do not introduce new entities, aliases, facts, candidate answers, or support titles not present in the input.
- If a candidate is uncertain, preserve it as uncertain; do not treat it as confirmed.
- If multiple candidates are present, keep them as a candidate set rather than collapsing to one candidate.
- Never convert a query into attribute-only descriptors when canonical names or titles are available.
- The original retrieval problem and correction direction should be recoverable from the query behavior.

Core optimization constraints:
- Do not merely restate the full question.
- Do not produce generic role-only, date-only, or attribute-only queries when concrete names or titles are available.
- Preserve at least one concrete source anchor and one target relation or missing-support cue whenever available.
- Prefer BM25-useful lexical anchors over abstract descriptions.

Representation guide:
Use a conservative reversible edit script.
Transform a weak query by restoring only the minimal lexical cues needed to retrieve the missing support page:
canonical title, source anchor, target relation, answer-type term, and one disambiguating clue.
Delete irrelevant verbosity, but do not delete names/titles that make the query reversible.

Minibatch emphasis:
Prioritize missing-support recovery.
The useful query should retrieve the page that was missing after the first hop or after a weak second-hop query.
Favor terms that identify the support page, relation evidence, and answer-bearing page.
But do not sacrifice reversibility by dropping concrete anchors.

Rewrite style:
Be more expressive.
Surface the optimization direction more strongly: missing-support cue restoration, source-target coupling, relation-target preservation, and uncertainty control.
Still obey all reversibility constraints.

Output rules:
- Output only the query.
- Use concrete names, titles, aliases, and relation terms.
- Do not output bullet points, explanations, or JSON.
- Do not invent facts.
"""


# Patch final-answer prompt globals for normal non-agentgrad conditions.
patched = False
for attr in [
    "MANUAL_FINAL_PROMPT",
    "FINAL_MANUAL_PROMPT",
    "FINAL_EM_SPAN_CALIBRATION_PROMPT",
    "FINAL_ANSWER_PROMPT",
]:
    if hasattr(base, attr):
        setattr(base, attr, FINAL_V2_SPAN_RECOVER)
        patched = True

for attr in ["FINAL_PROMPTS", "FINAL_ANSWER_PROMPTS", "MANUAL_FINAL_PROMPTS"]:
    if hasattr(base, attr) and isinstance(getattr(base, attr), dict):
        d = getattr(base, attr)
        for k in list(d.keys()):
            if "final" in str(k).lower() or "span" in str(k).lower() or "manual" in str(k).lower():
                d[k] = FINAL_V2_SPAN_RECOVER
                patched = True

if not patched:
    print(
        "[WARN] Could not find a known final prompt variable to patch. "
        "Normal conditions may not be using FINAL_V2_SPAN_RECOVER.",
        file=sys.stderr,
    )


# Base runner will treat these as hop2 candidates.
# The sentinel condition is then upgraded to full-module agentgrad by the monkeypatch below.
base.HOP2_CANDIDATES = {
    "our_retrieval_best_R6_original": OUR_RETRIEVAL_BEST_R6_ORIGINAL,
    "our_em_best_R6v2": OUR_EM_BEST_R6V2,
    "agentgrad_best_full": AGENTGRAD_SENTINEL,
}


# =========================
# Generic full-module override monkeypatch
# =========================

def contains_sentinel(obj) -> bool:
    if isinstance(obj, str):
        return AGENTGRAD_SENTINEL in obj
    if isinstance(obj, dict):
        return any(contains_sentinel(k) or contains_sentinel(v) for k, v in obj.items())
    if isinstance(obj, (list, tuple)):
        return any(contains_sentinel(v) for v in obj)
    return False


def set_instruction_container(d: dict, text: str) -> None:
    changed = False
    for key in [
        "instruction",
        "instructions",
        "prompt",
        "system_prompt",
        "old_instruction",
        "new_instruction",
    ]:
        if key in d and isinstance(d[key], str):
            d[key] = text
            changed = True
    if not changed:
        d["instruction"] = text


def apply_agentgrad_full(obj):
    """Mutate prompt-candidate-like objects so the sentinel condition becomes full agentgrad-best."""
    if isinstance(obj, dict):
        # Direct module-key style: {"summarize1.predict": "..."}
        for module, text in AGENTGRAD_PROMPTS.items():
            if module in obj:
                if isinstance(obj[module], str):
                    obj[module] = text
                elif isinstance(obj[module], dict):
                    set_instruction_container(obj[module], text)

        # Record style: {"module": "summarize1.predict", "instruction": "..."}
        possible_name = None
        for name_key in [
            "module",
            "module_name",
            "component",
            "component_name",
            "predictor",
            "name",
            "field",
        ]:
            if name_key in obj and isinstance(obj[name_key], str):
                if obj[name_key] in AGENTGRAD_PROMPTS:
                    possible_name = obj[name_key]
                    break

        if possible_name is not None:
            set_instruction_container(obj, AGENTGRAD_PROMPTS[possible_name])

        for k, v in list(obj.items()):
            if isinstance(v, str) and AGENTGRAD_SENTINEL in v:
                obj[k] = AGENTGRAD_CREATE_QUERY_HOP2
            else:
                apply_agentgrad_full(v)

    elif isinstance(obj, list):
        for v in obj:
            apply_agentgrad_full(v)

    elif isinstance(obj, tuple):
        for v in obj:
            apply_agentgrad_full(v)

    return obj


def maybe_agentgrad(obj):
    if contains_sentinel(obj):
        obj = copy.deepcopy(obj)
        apply_agentgrad_full(obj)
    return obj


# Patch json serialization, because the base runner usually writes prompt_candidate.json.
_original_json_dump = json.dump
_original_json_dumps = json.dumps

def patched_json_dump(obj, fp, *args, **kwargs):
    return _original_json_dump(maybe_agentgrad(obj), fp, *args, **kwargs)

def patched_json_dumps(obj, *args, **kwargs):
    return _original_json_dumps(maybe_agentgrad(obj), *args, **kwargs)

json.dump = patched_json_dump
json.dumps = patched_json_dumps


# Patch functions in the base script so in-memory prompt candidates are also upgraded.
def wrap_function(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if any(contains_sentinel(a) for a in args) or any(contains_sentinel(v) for v in kwargs.values()):
            args = tuple(maybe_agentgrad(a) for a in args)
            kwargs = {k: maybe_agentgrad(v) for k, v in kwargs.items()}
        out = fn(*args, **kwargs)
        if contains_sentinel(out):
            out = maybe_agentgrad(out)
        return out
    return wrapped


for name, fn in list(vars(base).items()):
    if inspect.isfunction(fn) and getattr(fn, "__module__", None) == base.__name__:
        setattr(base, name, wrap_function(fn))


print("[INFO] Loaded conditions:", file=sys.stderr)
for k in base.HOP2_CANDIDATES:
    print(f"[INFO]   {k}", file=sys.stderr)

print("[INFO] agentgrad_best_full will override:", file=sys.stderr)
for k in AGENTGRAD_PROMPTS:
    print(f"[INFO]   {k}", file=sys.stderr)


if __name__ == "__main__":
    base.main()
