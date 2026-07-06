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
    "additive_bridge_v2": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Use bridge-style retrieval as an additive operation, not as a replacement for existing lexical anchors.

Build the query from:
- the strongest canonical entity, title, name, or alias already present in `summary_1`;
- the unresolved relation, attribute, or answer type required by the original question;
- any distinctive title/entity surface form from the original question that helps BM25 disambiguation.

Rules:
- Do not remove canonical names from `summary_1`.
- Do not replace named entities with abstract role descriptions such as "lead singer born in 1960" if the actual name or title is available.
- Do not collapse the query to only the missing relation.
- Keep useful lexical redundancy when it helps retrieve the correct page.
- Prefer a compact keyword query, but allow enough context for BM25.

Output only the query.""",

    "controlled_redundancy_v1": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Produce a controlled-redundancy BM25 query.

Include:
- the main known entity or title from `summary_1`;
- the likely missing entity, relation, or answer type;
- important aliases, alternate titles, or candidate names when they are explicitly present in `question` or `summary_1`;
- relation words from the question if they distinguish the target page.

Rules:
- Do not make the query minimal if minimality would drop useful names.
- Do not output a full explanatory sentence.
- Do not invent aliases or candidate names.
- If several candidate entities are relevant, keep them rather than guessing one too early.
- Avoid generic-only queries made of words like "company profile", "band members", "release date", or "birth year" without a strong entity/title anchor.

Output only the query.""",

    "no_role_only_abstraction_v1": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Write a BM25 query that preserves concrete lexical anchors.

Rules:
- Never output a query that consists only of roles, descriptions, dates, or answer types.
- If a canonical entity name, title, person, band, album, organization, location, film, or work is available, include it.
- Use role descriptions only as supplements to names, not replacements.
- Preserve distinctive quoted titles and exact names from the question or `summary_1`.
- Include the unresolved relation or target needed for the second hop.
- Avoid over-general queries that could match many unrelated pages.

Output only the query.""",

    "overlap_candidate_preserving_v1": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

This prompt is for comparison, overlap, and intersection questions.

If the question asks which entity is shared between two works, groups, companies, teams, people, or events:
- preserve both compared entities or works;
- preserve multiple candidate names if they appear in `question` or `summary_1`;
- do not collapse to a single guessed candidate unless the evidence in `summary_1` is explicit;
- include the relation being tested, such as cast, starred in, member, formed, nationality, headquarters, conference, birth date, or role.

For non-overlap questions:
- preserve the strongest known anchor from `summary_1`;
- include the unresolved relation or answer type.

Rules:
- Keep useful candidate-set redundancy.
- Do not output an explanation.
- Do not invent new candidates.

Output only the query.""",

    "source_target_anchor_v1": """Given `question` and `summary_1`, produce a second-hop BM25 search query.

Construct the query with both source-side and target-side anchors.

Include:
1. a source-side anchor from the original question or `summary_1` that identifies where the question starts;
2. a target-side anchor, relation, or answer type that identifies what is still missing;
3. canonical names, titles, aliases, or distinctive modifiers needed for BM25 disambiguation.

Rules:
- Do not search only for the final target while dropping the source entity.
- Do not search only for the source entity while dropping the missing relation.
- Do not replace names with vague descriptions.
- Allow a moderately long keyword query if it preserves important anchors.
- Prefer concrete names and titles over generic relation words.

Output only the query.""",
}


if __name__ == "__main__":
    base.main()
