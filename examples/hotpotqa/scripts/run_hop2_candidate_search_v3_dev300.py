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


base.HOP2_CANDIDATES = {
    "source_target_no_lockin_v3": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

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

    "overlap_candidate_set_v3": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

This is for overlap, intersection, comparison, and "which one / both / in common / also appeared" questions.

If the question asks for a shared person, cast member, member, player, role, property, occupation, nationality, or common attribute:
- preserve both compared entities, works, teams, organizations, or events;
- preserve multiple candidate names if `summary_1` lists them;
- retrieve the evidence page or list that can decide among candidates;
- do not collapse the query to one guessed candidate unless the evidence is explicit.

Good query ingredients:
- source work/entity title;
- target work/entity title;
- relation word such as cast, starred, member, lineup, born, nationality, occupation, conference, headquarters, director, author;
- candidate names only when they are useful as a set.

Avoid:
- single-candidate lock-in;
- generic role-only queries;
- long explanations.

Output only the query.""",

    "verification_page_first_v3": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Prioritize retrieving the page that verifies the missing relation, not merely a plausible answer candidate.

Use this strategy:
1. Identify the entity/page whose article is most likely to contain the deciding evidence.
2. Include the source-side anchor from the question.
3. Include the missing relation or answer type.
4. Include candidate names only as secondary terms unless one is explicitly confirmed.

Examples of verification pages:
- a film/work page listing cast;
- an album/game page listing credits or cover athletes;
- a team/page listing members or venue;
- a biography page confirming full name, birth date, occupation, or affiliation;
- an event/tournament page listing winner or participant.

Rules:
- Prefer evidence-list pages over a single guessed candidate page when the candidate is uncertain.
- Preserve exact titles and canonical names.
- Do not output an explanation.
- Do not invent entities.

Output only the query.""",

    "source_target_conservative_v3": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Construct a conservative source-target query.

Include:
- one source-side anchor from the original question or `summary_1`;
- one target-side relation or answer-type phrase;
- one or more exact title/name surfaces needed for disambiguation.

Conservative constraints:
- Do not over-expand the query with many weak aliases.
- Do not add a candidate if `summary_1` marks it as unverified or only plausible.
- Do not remove the source entity when searching for the target relation.
- Do not remove the target relation when preserving the source entity.
- If the question is an overlap/comparison question, keep both compared entities rather than guessing one answer.
- Keep the query readable as a compact BM25 keyword query.

Output only the query.""",
}


if __name__ == "__main__":
    base.main()
