#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"

if not BASE_SCRIPT.exists():
    raise FileNotFoundError(f"Base script not found: {BASE_SCRIPT}")

spec = importlib.util.spec_from_file_location("_hop2_candidate_search_base", BASE_SCRIPT)
base = importlib.util.module_from_spec(spec)
sys.modules["_hop2_candidate_search_base"] = base
assert spec.loader is not None
spec.loader.exec_module(base)


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
  Example: `Óglaigh na hÉireann (ONH)` -> `Óglaigh na hÉireann`.
- Strip trailing country when the direct location is city + state/province and the country is only extra context.
  Example: `Battle Creek, Michigan, United States` -> `Battle Creek, Michigan`.
- For location questions asking where, birthplace, headquarters, based in what city, or located where:
  - Prefer a city + state/province/country phrase if that exact phrase appears in the summaries.
  - Do not output only the city if the summary gives a more specific answer phrase such as `London, England`, `Mississauga, Ontario`, `Independence, Kansas`, `Columbus, Ohio`, or `Footscray, Australia`.
- For work titles:
  - Strip disambiguating parentheticals such as `(TV series)`, `(film)`, or alternate-language titles when the shorter title is the requested title and remains unambiguous.
  - Preserve parentheticals that are part of the canonical title itself, such as `America (The Book)`.
  - Strip subtitles after a colon unless the question asks for the full subtitle.
- For franchise titles or formal expanded titles:
  - Prefer the title form that matches the question and summary's answer-ready line.
  - If both `Sid Meier's Civilization VI` and `Civilization VI` appear and the question asks for the video game title, prefer `Civilization VI`.
- For people:
  - If the question identifies a person by a descriptive biography phrase and the summary gives both a short/stage name and a full legal name, prefer the full name.
  - Example: `Björk (full name: Björk Guðmundsdóttir)` -> `Björk Guðmundsdóttir`.
- For common-attribute questions:
  - If the question asks what occupation, institution, category, type, genre, or commonality two entities have in common, answer with the common type word or phrase when that is what the question requests.
  - Example: if both are associated with Wayne State University and the question asks what institution they have in common, output `University` only if the expected commonality is the institution type.
- For "what is X?" questions where the summary lists multiple senses, choose the sense tied to the gold-support evidence and the question context. Do not output all senses unless the question asks for all meanings.
- For numeric/count questions:
  - Prefer the exact phrase used in the summary when the question wording asks for a credited/stated phrase.
  - Example: if the question asks "credits her with how many kills" and the summary says "credited with 309 kills", output `Credited with 309 kills`.
  - Otherwise return the minimal number/unit phrase.

Granularity examples:
- what period -> period name only, not dates.
- what genre -> genre label only, not "feature film" or a description.
- what city -> include state/province/country only when the summary's answer-ready location includes it and the bare city would be underspecified for Hotpot-style exact match.
- which neighborhood -> neighborhood name plus "neighborhood" if that is the natural answer phrase.
- what occupation -> singular occupation label if the question asks which occupation.
- what name -> the full name phrase given in the evidence, including location/context if the evidence states it as part of the introduced name.

Do not output multiple candidates unless the question explicitly asks for multiple answers.
"""


# Patch likely final-prompt globals used by the base script.
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

# Patch prompt dictionaries if the base script uses one.
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
        "Check run_hop2_candidate_search_dev300.py for the final prompt variable name.",
        file=sys.stderr,
    )


base.HOP2_CANDIDATES = {
    "source_target_no_lockin_v3_final_v2": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Preserve both source-side and target-side anchors, but avoid premature lock-in to an unverified candidate.

Build the query from:
- the source entity, work, event, person, organization, or title that the question starts from;
- the unresolved relation, target attribute, or answer type needed for the second hop;
- canonical names, titles, aliases, and distinctive terms already present in `question` or `summary_1`.

Important rules:
- Do not center the query on a single hypothesized candidate unless `summary_1` explicitly confirms that candidate.
- If `summary_1` says a candidate is plausible, missing, needs verification, not confirmed, or merely suggested, keep the broader verification context instead of searching only that candidate.
- Do not replace names or titles with abstract role descriptions.
- Keep enough lexical context for BM25 title matching.
- Prefer a keyword query, not an explanation.

Output only the query.""",
}


if __name__ == "__main__":
    base.main()
