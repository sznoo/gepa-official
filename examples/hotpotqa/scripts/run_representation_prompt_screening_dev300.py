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
- Strip trailing country when the direct location is city + state/province and the country is only extra context.
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
- For common-attribute questions:
  - If the question asks what occupation, institution, category, type, genre, or commonality two entities have in common, answer with the common type word or phrase when that is what the question requests.
- For "what is X?" questions where the summary lists multiple senses, choose the sense tied to the question context. Do not output all senses unless the question asks for all meanings.
- For numeric/count questions:
  - Prefer the exact phrase used in the summary when the question wording asks for a credited/stated phrase.
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


# Patch final-answer prompt globals used by the imported base script.
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
        "Check run_hop2_candidate_search_dev300.py for the final prompt variable name.",
        file=sys.stderr,
    )


COMMON_HEADER = """Given `question` and `summary_1`, produce a second-hop BM25 search query.

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
"""


REPRESENTATIONS = {
    "R1_fixed_slot_source_target": """Representation guide:
Use a slot-like source-target decomposition.
Preserve the source anchor, the target relation, and the missing answer type.
The query should contain both the entity/work/page where the question starts and the relation/page needed for the second hop.
Do not let either side disappear.""",

    "R2_fixed_slot_error_delta": """Representation guide:
Use an error-delta view.
Identify what the weak query would lose: source title, target relation, candidate uncertainty, or missing support.
Rewrite the query to explicitly preserve the lost information while avoiding extra invented facts.
The query should make the correction direction visible.""",

    "R3_free_behavior_delta": """Representation guide:
Use a free-form reversible behavioral rewrite.
Describe the retrieval behavior implied by the question and summary_1, then compress that behavior into a BM25 query.
Keep the surface different from the original wording, but preserve every task-relevant entity, relation, and uncertainty signal.""",

    "R4_free_prompt_gradient": """Representation guide:
Use a prompt-gradient view.
Infer the edit direction from the trace: preserve lexical anchors, downweight unverified guesses, target missing support, and avoid over-compression.
The query should be a concrete realization of that edit direction, not a copy of the question.""",

    "R5_hybrid_anchor_free": """Representation guide:
Use a hybrid representation.
First keep all exact anchors that must not be lost: names, titles, aliases, and relation words.
Then freely rewrite the retrieval intent around those anchors.
The output should look like a useful BM25 keyword query rather than a schema.""",

    "R6_hybrid_edit_script": """Representation guide:
Use a reversible edit-script representation.
Imagine transforming a weak query into a stronger one:
keep essential anchors, restore missing relation words, retain uncertain candidates as a set, and delete only irrelevant verbosity.
The final query should reflect the edited behavior."""
}


MINIBATCH_GUIDES = {
    "MB1_retrieval_gain_recover": """Minibatch emphasis:
Prioritize missing-support recovery.
The useful query should retrieve the page that was missing after the first hop or after a weak second-hop query.
Favor terms that identify the support page, relation evidence, and answer-bearing page.""",

    "MB2_lockin_loss_guard": """Minibatch emphasis:
Prioritize candidate-lock-in prevention.
When summary_1 contains a plausible but unverified candidate, do not center the query only on that candidate.
Keep source and target anchors, and preserve candidate sets as auxiliary terms when useful."""
}


REWRITE_STYLES = {
    "S1_conservative_reversible": """Rewrite style:
Be conservative.
Prefer high reversibility and explicit lexical preservation.
Use enough context for BM25, but avoid long explanatory sentences.
Do not over-generalize.""",

    "S2_gradient_expressive": """Rewrite style:
Be more expressive.
Surface the optimization direction more strongly: source-target coupling, missing-support recovery, uncertainty control, and answer-ready relation targeting.
Still obey all reversibility constraints."""
}


COMMON_FOOTER = """Output rules:
- Output only the query.
- Use concrete names, titles, aliases, and relation terms.
- Do not output bullet points, explanations, or JSON.
- Do not invent facts.
"""


def build_candidates() -> dict[str, str]:
    candidates = {}
    for r_name, r_text in REPRESENTATIONS.items():
        for mb_name, mb_text in MINIBATCH_GUIDES.items():
            for s_name, s_text in REWRITE_STYLES.items():
                name = f"{r_name}__{mb_name}__{s_name}"
                candidates[name] = "\n\n".join([
                    COMMON_HEADER.strip(),
                    r_text.strip(),
                    mb_text.strip(),
                    s_text.strip(),
                    COMMON_FOOTER.strip(),
                ])
    return candidates


base.HOP2_CANDIDATES = build_candidates()

if len(base.HOP2_CANDIDATES) != 24:
    raise RuntimeError(f"Expected 24 candidates, got {len(base.HOP2_CANDIDATES)}")

print("[INFO] Loaded 24 representation-guided hop2 prompt candidates.", file=sys.stderr)
for k in base.HOP2_CANDIDATES:
    print(f"[INFO] candidate: {k}", file=sys.stderr)


if __name__ == "__main__":
    base.main()
