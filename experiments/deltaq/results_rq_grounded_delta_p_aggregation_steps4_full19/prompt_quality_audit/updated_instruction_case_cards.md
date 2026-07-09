# Prompt quality case cards


## Top updated-instruction gains


========================================================================================================================

## IDX 55 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 6/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; multi_query_drift
- bad_patterns: boolean_heavy; multi_query
- risky titles: instr=[], query=[]

Question: What culture do both the Capital of the Netherlands and Amsterdamned have in common?

Current query: `Amsterdam Dutch culture; Amsterdamned (1988) Dutch horror film Dick Maas Dutch cinema`

New query: `Amsterdamned Dutch film Amsterdam capital Netherlands`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` for the second hop as a single compact BM25 query that verifies a shared national/cultural label between the two named entities. Rules: - Preserve exact entity anchors as retrieval seeds: the film title anchor (e.g., Amsterdamned) and the city anchor (Amsterdam). Do not broaden these anchors. - Inject concise relation/type/country cues adjacent to each entity to elicit lede/infobox-style hits: attach a short film-type nationality cue to the film anchor (prefer "Dutch film") and attach a short role/country cue to the city anchor (use "capital" and/or "Netherlands"). - Query ordering and shape: start with the film title anchor, then 1–3 tight disambiguators (prefer the phrase "Dutch film"); then include the city anchor with "capital" and "Netherlands" tokens. Form one plain space-separated token sequence (entity+property adjacency favored for BM25 proximity). - Keep the query short and noun-focused (prefer <12 ...
```

========================================================================================================================

## IDX 55 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 4/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; multi_query_drift; leakage_language
- bad_patterns: boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: What culture do both the Capital of the Netherlands and Amsterdamned have in common?

Current query: `Amsterdam Dutch culture; Amsterdamned (1988) Dutch horror film Dick Maas Dutch cinema`

New query: `Amsterdam capital Netherlands Dutch Amsterdamned Dutch film 1988`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop of a multi‑hop retrieval system. Preserve create_query_hop2’s role: return exactly one compact second‑hop BM25 query (a single plain text line of space‑separated tokens) that retrieves additional authoritative documents not captured in the first hop. Do not return multiple queries, examples, final answers, or retrieval scripts. Rules (apply in order): - Preserve source anchors: keep the core entity tokens found in the question and summary (e.g., film titles, person names, place names, aliases). Do not generalize these anchors into vague phrases. - Identify and add missing disambiguators from the summary as short literal tokens/phrases: use year tokens, nationality/country adjectives or names (e.g., Dutch, Netherlands), type/relation cues (e.g., film, horror, director, capital, city), and concise setting cues (e.g., canals, set in Amsterdam). Prefer 1–3 disambiguators per entity and ...
```

========================================================================================================================

## IDX 108 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 6/3
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta
- bad_patterns: boolean_heavy; multi_query
- risky titles: instr=[], query=[]

Question: Are Solo and La Croix Sparkling Water produced in the same country ?

Current query: `Solo (soft drink) Australian lemon-flavoured carbonated drink produced in Australia manufacturer Schweppes Asahi`

New query: `Solo (Australian) origin soft drink`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second retrieval hop. When the question compares production/origin countries and one brand name is ambiguous or missing an explicit production-country in the summary, force a disambiguation-before-compare retrieval step: emit exactly one compact BM25 query that disambiguates the ambiguous brand and targets a lead/infobox country-of-origin statement. Rules: - Preserve the canonical entity name tokens and, if needed for disambiguation, a short parenthetical disambiguator immediately after the name (e.g., (Australian) ). - Restore an explicit country/origin extraction cue (examples: origin, country, country of origin, produced in) to steer retrieval to a lead or infobox line. - Optionally include one short descriptive type token (e.g., soft drink) only if it aids disambiguation; otherwise omit. - Drop manufacturer, distributor, global-brand, flavor, and other noisy tokens (examples: Schweppes, ...
```

========================================================================================================================

## IDX 108 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 4/2
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; multi_query_drift; leakage_language
- bad_patterns: boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: Are Solo and La Croix Sparkling Water produced in the same country ?

Current query: `Solo (soft drink) Australian lemon-flavoured carbonated drink produced in Australia manufacturer Schweppes Asahi`

New query: `Solo (soft drink) origin`

Updated instruction excerpt:
```text
Given the fields question and summary_1, produce the field query optimized for the second hop. Follow these rules: - Purpose: retrieve additional authoritative lead/infobox or disambiguation lines needed to resolve missing production/origin facts (e.g., when comparing whether two beverages are produced in the same country). - Identify missing entities or ambiguous names in summary_1 and target those for disambiguation before comparison. - If one brand is ambiguous or missing origin info, force a disambiguation-first, extraction-oriented query that returns a short lead/infobox line stating country/origin. - Query shape (must produce exactly one BM25 query string): prefer 2–4 high-precision tokens in this order — 1) brand name token, 2) optional parenthetical disambiguator immediately after the brand (e.g., (Australian soft drink)) if needed to resolve ambiguity, 3) one short extraction cue token such as origin or country or produced. Example structure: [Brand][(disambiguator)] ...
```

========================================================================================================================

## IDX 82 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 3/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?

Current query: `"Clay County Savings Association robbery" 1866 Liberty Missouri Jesse James Archie Clement James–Younger Gang guerrillas bushwhackers partisans term origin Revolutionary War usage`

New query: `Clay County Savings Association robbery Missouri guerrilla bushwhacker partisan definition called`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. Generate exactly one compact BM25-style bag-of-words query (single line, plain text, no operators, no punctuation beyond bare words, no multiple queries) that prioritizes short encyclopedia/dictionary lead lines naming the robbers with a single label. Preserve: - The event anchor (the robbery name or short event phrase, e.g., "Clay County Savings Association robbery" or a concise variant) and a location token ("Liberty", "Missouri" or "Missouri Civil War") so the robbery article ranks high. - A small candidate set of one-word perpetrator-label tokens (e.g., guerrilla, bushwhacker, partisan). Keep these tokens together in the query. - A short context cue to bias toward concise definitions or lead sentences: one of "definition", "lead", or "perpetrators" and a Civil‑War/Missouri context token ("Civil War" or "Missouri"). Restore/include cues that force short-label retrieval: - An ...
```

========================================================================================================================

## IDX 82 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 3/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?

Current query: `"Clay County Savings Association robbery" 1866 Liberty Missouri Jesse James Archie Clement James–Younger Gang guerrillas bushwhackers partisans term origin Revolutionary War usage`

New query: `Clay County Savings Association robbery Liberty Missouri perpetrators guerrillas bushwhackers Civil War`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` containing exactly one compact BM25-style bag-of-words query optimized for the SECOND hop. Your goal is to retrieve concise documents missed by the first hop (e.g., an article lead sentence or a short definition) that supply a single noun-label or tightly focused context needed to answer the question. Rules: - Preserve event and location anchors from the sample (keep the robbery/event phrase and place tokens as plain words). - Preserve a small candidate set of one-word label tokens when uncertain (e.g., guerrillas, bushwhackers, partisan) rather than expanding into many synonyms. - Restore retrieval cues that bias toward short lead/definition evidence: include an action/label cue such as robbers called or perpetrators or robbers were described as, plus a short context token like definition and a locality/context specifier (Civil War or Missouri). - Drop noisy side entities and long biographical or etymology ...
```

========================================================================================================================

## IDX 150 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 3/0
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

Current query: `Paul Winters biography Wayne State University head coach Wayne State Warriors football program history Tom Adams Field GLIAC Detroit`

New query: `Paul Winters head coach Wayne State University 2012 Wayne State Warriors football team`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. Generate exactly one compact BM25 query (single line) that targets short, authoritative lead/title lines tying a named season/team page and a named person page to the same institution. Rules: - Preserve only the core retrieval anchors: the exact season+team identifier (year + team name as it appears) and the person’s full name. Preserve a program alias only if it is identical to those anchors. - Restore the explicit institution token (the university name) if available; include it in the query to force the affiliation bridge. - Include one concise role/relation cue (e.g., head coach or coach) adjacent to the person anchor to favor coach-bio affiliation lines. - Drop noisy or broad tokens that dilute lead-line matches: biography/history, stadium/venue names, conference/division labels, city/location names, extra season years, tenure counts, long descriptive phrases, and other ...
```

========================================================================================================================

## IDX 150 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 3/1
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

Current query: `Paul Winters biography Wayne State University head coach Wayne State Warriors football program history Tom Adams Field GLIAC Detroit`

New query: `Paul Winters 2012 Wayne State Warriors head coach Wayne State University`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. When the task is to identify a shared institutional affiliation between a specific season/team and a person, follow these rules: preserve only the core anchors from the inputs (the season+team identifier and the person name) and keep the original source anchor from summary_1; restore an explicit institution token (the university name) and a single role/relation cue (e.g., head coach or coach) so the query targets short lead-paragraph affiliation lines; drop noisy side tokens (biography, history, stadium names, conference/division labels, city names, other years, historical aliases, tenure counts and other broad modifiers); optionally keep a single venue token last only if it is necessary and unambiguous. Emit exactly one compact, single-line BM25-style query string composed of contiguous title-like tokens: cluster {person name} + {season team (year + team)} + {role cue} + ...
```

========================================================================================================================

## IDX 60 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 5/2
- patterns: restore_relation_or_type; drop_noisy_entity; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta
- bad_patterns: web_syntax; boolean_heavy; multi_query
- risky titles: instr=[], query=[]

Question: The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

Current query: `Hubble Space Telescope STS-31 Space Shuttle Discovery launch date launch year`

New query: `STS-31 launch`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce exactly one compact BM25-style keyword query optimized for the second hop to retrieve a concise launch-date statement. Rules: - Goal: surface an authoritative mission- or overview-level page that explicitly states the telescope's launch year/date. - Primary path (when a mission identifier appears in context): emit a 1–3 token query that foregrounds the mission identifier followed by a single date/relation cue. Structure: [MISSION_ID] + [launch|launch date|launch year] (optionally include the four-digit year as a third token). Do not include telescope/instrument names or other side entities. - Fallback path (when no mission identifier is available): emit a 2–4 token query that uses the canonical telescope name or common alias (e.g., Hubble, HST, or the provided telescope name) + a single date/relation cue (launch|launch date|launch year). Optionally append one short overview cue (overview or infobox) to bias summary pages. - ...
```

========================================================================================================================

## IDX 60 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 3/2
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

Current query: `Hubble Space Telescope STS-31 Space Shuttle Discovery launch date launch year`

New query: `STS-31 launch year`

Updated instruction excerpt:
```text
Given fields `question` and `summary_1`, produce exactly one compact BM25-style keyword query (2–6 tokens) optimized for the second hop to retrieve a telescope's launch year/date. Trigger: when the question asks for the launch year/date of a named telescope or the summary references the telescope's launch. Selection logic: - If a specific mission identifier (exact mission code, e.g., "STS-31") or a clear launch vehicle token appears in the context, prefer a mission-focused query with the mission id first, then a single date/relation cue: [MISSION_ID] + [launch|launch date|launch year] (e.g., STS-31 launch date). - Otherwise, emit an entity-centric query: [canonical telescope name or common alias] + [launch|launch date|launch year]. Optionally append one short type cue ('history' or 'overview') or the four-digit year token if it is already known and will tighten results. Preserve: the exact canonical telescope name or exact mission identifier/alias as present in inputs. Preserve a ...
```

## Worst updated-instruction losses


========================================================================================================================

## IDX 90 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 1.000 → 0.000 (-1.000)
- generality/locality: 3/3
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: Imiliya is a town located in what pilgrimage site?

Current query: `Imiliya Kapilvastu Lumbini Nepal Maya Devi Temple sacred garden monastic zone UNESCO coordinates proximity`

New query: `Imiliya Kapilvastu Lumbini Mayadevi temple birthplace`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop of a multi‑hop retrieval system. Return exactly one compact BM25 query string (single line, whitespace‑separated tokens only) that will surface authoritative pages which (A) identify the pilgrimage site and its key landmark/authority statements and (B) connect that pilgrimage identity to the sampled place’s locality. Rules: - When the question links a named settlement to a pilgrimage site, compose one short bag‑of‑words BM25 query that conjunctively combines: the sampled place name token, its administrative district token, the pilgrimage site name token, one principal pilgrimage landmark token, and one site‑type or authority cue. Example token types: PLACE_NAME DISTRICT LUMBINI Mayadevi Rummindei Ashoka pillar pilgrimage birthplace UNESCO Lumbini Development Trust Siddhartha Gautama. - Always preserve the exact sampled place name and its administrative district as anchor tokens. - ...
```

========================================================================================================================

## IDX 60 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 5/2
- patterns: restore_relation_or_type; drop_noisy_entity; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta
- bad_patterns: web_syntax; boolean_heavy; multi_query
- risky titles: instr=[], query=[]

Question: The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

Current query: `Hubble Space Telescope STS-31 Space Shuttle Discovery launch date launch year`

New query: `STS-31 launch`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce exactly one compact BM25-style keyword query optimized for the second hop to retrieve a concise launch-date statement. Rules: - Goal: surface an authoritative mission- or overview-level page that explicitly states the telescope's launch year/date. - Primary path (when a mission identifier appears in context): emit a 1–3 token query that foregrounds the mission identifier followed by a single date/relation cue. Structure: [MISSION_ID] + [launch|launch date|launch year] (optionally include the four-digit year as a third token). Do not include telescope/instrument names or other side entities. - Fallback path (when no mission identifier is available): emit a 2–4 token query that uses the canonical telescope name or common alias (e.g., Hubble, HST, or the provided telescope name) + a single date/relation cue (launch|launch date|launch year). Optionally append one short overview cue (overview or infobox) to bias summary pages. - ...
```

========================================================================================================================

## IDX 60 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 3/2
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

Current query: `Hubble Space Telescope STS-31 Space Shuttle Discovery launch date launch year`

New query: `STS-31 launch year`

Updated instruction excerpt:
```text
Given fields `question` and `summary_1`, produce exactly one compact BM25-style keyword query (2–6 tokens) optimized for the second hop to retrieve a telescope's launch year/date. Trigger: when the question asks for the launch year/date of a named telescope or the summary references the telescope's launch. Selection logic: - If a specific mission identifier (exact mission code, e.g., "STS-31") or a clear launch vehicle token appears in the context, prefer a mission-focused query with the mission id first, then a single date/relation cue: [MISSION_ID] + [launch|launch date|launch year] (e.g., STS-31 launch date). - Otherwise, emit an entity-centric query: [canonical telescope name or common alias] + [launch|launch date|launch year]. Optionally append one short type cue ('history' or 'overview') or the four-digit year token if it is already known and will tighten results. Preserve: the exact canonical telescope name or exact mission identifier/alias as present in inputs. Preserve a ...
```

========================================================================================================================

## IDX 77 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 1.000 → 1.000 (+0.000)
- generality/locality: 5/5
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta
- bad_patterns: web_syntax; boolean_heavy; multi_query
- risky titles: instr=[], query=[]

Question: The winner of the first season of "Next Great Baker" would win an apprenticeship at the bakery owned by who?

Current query: `Next Great Baker season 1 winner Carlo's Bake Shop`

New query: `Buddy Valastro Carlo's Bake Shop owner`

Updated instruction excerpt:
```text
Given the fields question and summary_1, produce the field query optimized for the second hop. Emit exactly one compact BM25-style query (single plain-text line, 2–7 space-separated tokens) that shifts retrieval from show/season/prize pages to authoritative place or person pages that explicitly state who owns the named bakery. Rules: - Preserve the exact place-name anchor or its primary alias from inputs (e.g., Carlo's Bake Shop or Buddy's bakery). - Restore an explicit ownership relation cue adjacent to that anchor (use owner, owns, proprietor, runs). The query must target a PERSON as the expected answer type. - If a likely proprietor/person-name is visible in the inputs (e.g., Buddy Valastro), prefer person-first ordering: person-name + bakery-anchor + ownership cue (or person-name + owner + bakery-anchor). If no clear person-name is present, use bakery-anchor + owner (e.g., Carlo's Bake Shop owner). - Keep only tokens that help identify the bakery or the proprietor role; drop ...
```

========================================================================================================================

## IDX 77 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 1.000 → 1.000 (+0.000)
- generality/locality: 5/5
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; wrong_candidate_relaxation; entity_level_over_location_event; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; leakage_language
- risky titles: instr=[], query=[]

Question: The winner of the first season of "Next Great Baker" would win an apprenticeship at the bakery owned by who?

Current query: `Next Great Baker season 1 winner Carlo's Bake Shop`

New query: `Buddy Valastro owner Carlo's Bake Shop`

Updated instruction excerpt:
```text
Given fields `question` and `summary_1`, produce the field `query` optimized for the second hop. Your goal is a single compact BM25 query that retrieves authoritative season- or entity-level documents needed to resolve who owns a named prize location (expected answer type: a PERSON). Rules: TRIGGER: Apply when the question asks who owns or is proprietor of a place referenced as an apprenticeship/prize location (phrases like “owned by who”, “apprenticeship at the bakery owned by”, etc.). PRESERVE: Keep the exact named-place anchor or its common alias from inputs (e.g., Carlo's Bake Shop, Buddy's bakery). Preserve visible person anchors from the question/summary when present (e.g., Buddy Valastro) and the expectation that the answer is a PERSON. TWO-STAGE RESTORE: First-stage (if season/prize confirmation is needed) — include show title + explicit season marker + the place name + a prize relation token (apprenticeship/prize/grand prize) to surface season pages, press releases, or ...
```

========================================================================================================================

## IDX 6 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 4/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; entity_level_over_location_event; bm25_interface_guard; single_query_guard; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: Smith Creek is a 35.5 mi tributary stream of the North Fork of a river that passes through which US states?

Current query: `Shenandoah River North Fork flows through which states Virginia West Virginia Harpers Ferry`

New query: `Shenandoah River Harpers Ferry states`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop of a multi-hop retrieval system. Your output must be exactly one compact BM25-style keyword query (single line, plain space-separated tokens, no punctuation, no boolean operators, no quotes, no multiple queries) that will retrieve authoritative river-level pages (lead/infobox/course) listing the U.S. states the river traverses. Rule set for composing the hop2 query: - Trigger: Apply these edits when the question names a small tributary or a fork (e.g., "Smith Creek" or "North Fork ...") and the goal is to find which U.S. states the parent/main river passes through. - Anchor preservation: Use the main river name as the primary anchor token exactly as available in the inputs (treat fork/tributary names only as aliases, not the primary token). - Bridge restoration: Include one concise downstream/confluence landmark token (for example Harpers Ferry or Potomac) to connect the river anchor ...
```

========================================================================================================================

## IDX 6 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 6/3
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta
- bad_patterns: boolean_heavy; multi_query
- risky titles: instr=[], query=[]

Question: Smith Creek is a 35.5 mi tributary stream of the North Fork of a river that passes through which US states?

Current query: `Shenandoah River North Fork flows through which states Virginia West Virginia Harpers Ferry`

New query: `Shenandoah River Harpers Ferry states`

Updated instruction excerpt:
```text
Given fields question and summary_1, produce the single field query optimized for the second hop. Trigger: apply when the question asks which U.S. state(s) a river passes through and the context names a small tributary or a fork. Rules: (1) Preserve the source anchor exactly as given, but use the main river name as the primary retrieval anchor (prefer the river name over a tributary/fork token); if the main river name is not explicit, preserve the fork-level phrase as the anchor. (2) Restore a concise downstream/confluence bridge token drawn from the context (for example: Harpers Ferry, Potomac, confluence, lower course) to connect the anchor to the river’s lower reach. (3) Add a single attribute cue to bias for lead/infobox/course summaries (prefer the token states; alternatively course or infobox). (4) Optionally include candidate state names only when those state tokens appear in the question or summary_1 and their inclusion is needed to boost recall; otherwise omit explicit ...
```

========================================================================================================================

## IDX 90 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 1.000 → 1.000 (+0.000)
- generality/locality: 3/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: Imiliya is a town located in what pilgrimage site?

Current query: `Imiliya Kapilvastu Lumbini Nepal Maya Devi Temple sacred garden monastic zone UNESCO coordinates proximity`

New query: `Imiliya Kapilvastu Lumbini Mayadevi Temple pilgrimage`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. This composer is used when the question asks which pilgrimage site contains a named settlement (town → pilgrimage containment). Output exactly one single-line BM25 query string and nothing else. Rules: - Purpose: retrieve authoritative, locality- and heritage-focused passages that tie the sampled place to a pilgrimage site (site identity and locality/proximity), without asserting interior containment inside a sacred enclosure. - Preserve anchors: include the settlement name token exactly as in the inputs and its administrative district token (e.g., "Imiliya" and "Kapilvastu"). These are required. - Restore high-signal pilgrimage cues: include the pilgrimage-site name (e.g., "Lumbini") plus one principal landmark or authority token (choose one: "Mayadevi Temple", "Rummindei", "Ashoka pillar", or "UNESCO") and one site-type relation cue such as "pilgrimage" or "birthplace". Prefer one ...
```

========================================================================================================================

## IDX 118 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.500 → 0.500 (+0.000)
- generality/locality: 5/0
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift
- bad_patterns: web_syntax; boolean_heavy; multi_query
- risky titles: instr=[], query=[]

Question: What acress starred in both "Third Person" and "From Here to Eternity"?

Current query: `Third Person (2013 film) cast; From Here to Eternity (1953 film) cast; From Here to Eternity (1979 miniseries) cast`

New query: `Third Person 2013 cast From Here to Eternity 1953 cast`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. Follow these rules exactly. - Role and intent: If the question asks which performer (actress) “starred in both” / “appeared in both” two named works, preserve that relation cue and the answer type (PERSON — actress). Treat the two named works as TitleA and TitleB whose top-billed female cast sets will be intersected. - Disambiguation requirement: For any ambiguous title, attach an explicit disambiguator token (a release year or a format token such as miniseries/film). Prefer the most likely canonical/prolific release year by default unless the user specifies otherwise. - Cast-targeting tokens: For each title, append a cast retrieval cue (use 'cast' or 'starring') so returned documents contain authoritative "Cast"/"Starring" sections with top-billed performers. Prefer the single token 'cast' when possible. - Query shape: Output exactly one compact BM25-style single-line query formed ...
```

========================================================================================================================

## IDX 118 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.500 → 0.500 (+0.000)
- generality/locality: 5/0
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift
- bad_patterns: web_syntax; boolean_heavy; multi_query
- risky titles: instr=[], query=[]

Question: What acress starred in both "Third Person" and "From Here to Eternity"?

Current query: `Third Person (2013 film) cast; From Here to Eternity (1953 film) cast; From Here to Eternity (1979 miniseries) cast`

New query: `Third Person 2013 cast From Here to Eternity 1953 cast`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. Output exactly one compact BM25 query string (single-line, plain tokens) that retrieves authoritative cast/starring pages for the two named works so their top-billed female performers can be compared. Rules: preserve the relation cue (the question’s “starred in both” / overlap-of-cast) and the expected answer type (person — actress). Treat the two titles as distinct anchors (SOURCE_TITLE and TARGET_TITLE). Disambiguate ambiguous titles by appending the canonical release year or format token (e.g., a year or the word miniseries) for each title; when the summary or common usage implies a most-likely year, prefer that year. Append the token cast (or starring) tied to each title to prioritize pages with clear cast sections. Produce one plain text bag-of-words query following the template: <TitleA> <YearA> cast <TitleB> <YearB> cast. Keep the string short (aim ~6–12 tokens), use no ...
```

## Flagged updated instructions


========================================================================================================================

## IDX 247 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 1/5
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[Occupy Ghana], query=[]

Question: What is another name for the online protest that opposed the transfer of ex-detainees from Guantanamo Bay in 2016?

Current query: `OccupyGhana online protest name hashtag 2016 Ghana transfer Guantanamo Yemeni ex-detainees`

New query: `occupyghana petition ghana guantanamo 2016`

Updated instruction excerpt:
```text
Given the fields question and summary_1, produce the field query optimized for the second hop of a multi‑hop retrieval system. Your goal is to retrieve local news items or social/petition pages that reproduce a named online protest label (campaign title, e‑petition name, or hashtag) tied to the event. When the question asks for an alternate name/label or hashtag for an online protest opposing Ghana’s January 2016 acceptance/transfer of Guantanamo ex‑detainees, follow these rules: - Preserve core anchors: include at least one actor alias token (OccupyGhana or Occupy Ghana; you may optionally include NPP), the place token Ghana, an event token Guantanamo or Gitmo, and the year token 2016. These ensure event specificity. - Restore campaign/medium cues: include at least one campaign-medium token such as petition, hashtag, Change.org, online, e-petition, Facebook, or Twitter to bias retrieval toward campaign metadata and embedded social posts. - Drop noisy side tokens: remove detainee- ...
```

========================================================================================================================

## IDX 247 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 2/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; leakage_language
- risky titles: instr=[Occupy Ghana], query=[]

Question: What is another name for the online protest that opposed the transfer of ex-detainees from Guantanamo Bay in 2016?

Current query: `OccupyGhana online protest name hashtag 2016 Ghana transfer Guantanamo Yemeni ex-detainees`

New query: `occupyghana npp ghana gitmo 2016 hashtag`

Updated instruction excerpt:
```text
Given the fields question and summary_1, produce the field query optimized for the second hop: output exactly one compact BM25-style keyword query (a single line of 4–8 plain lowercase tokens separated by single spaces) that will retrieve a named online campaign label, petition title, or hashtag used to oppose Ghana’s January 2016 transfer of Guantanamo detainees. Rules: - Preserve event and actor anchors: include at least OccupyGhana or Occupy Ghana, Ghana, and a Guantanamo/Gitmo token, plus the year token 2016. When uncertain, keep both OccupyGhana (or Occupy Ghana) and NPP as candidate anchors. - Restore a campaign-medium bridge token: include at least one of petition, e-petition, Change.org, hashtag, online, online campaign, online protest, Twitter, or Facebook. At most two platform/outlet tokens may be included (e.g., GhanaWeb JoyOnline Graphic CitiNewsroom). - Query shape: single-line bag of 4–8 high-value noun tokens (no Boolean operators, no quotes, no site: syntax, no ...
```

========================================================================================================================

## IDX 90 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 1.000 → 0.000 (-1.000)
- generality/locality: 3/3
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: Imiliya is a town located in what pilgrimage site?

Current query: `Imiliya Kapilvastu Lumbini Nepal Maya Devi Temple sacred garden monastic zone UNESCO coordinates proximity`

New query: `Imiliya Kapilvastu Lumbini Mayadevi temple birthplace`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop of a multi‑hop retrieval system. Return exactly one compact BM25 query string (single line, whitespace‑separated tokens only) that will surface authoritative pages which (A) identify the pilgrimage site and its key landmark/authority statements and (B) connect that pilgrimage identity to the sampled place’s locality. Rules: - When the question links a named settlement to a pilgrimage site, compose one short bag‑of‑words BM25 query that conjunctively combines: the sampled place name token, its administrative district token, the pilgrimage site name token, one principal pilgrimage landmark token, and one site‑type or authority cue. Example token types: PLACE_NAME DISTRICT LUMBINI Mayadevi Rummindei Ashoka pillar pilgrimage birthplace UNESCO Lumbini Development Trust Siddhartha Gautama. - Always preserve the exact sampled place name and its administrative district as anchor tokens. - ...
```

========================================================================================================================

## IDX 82 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 3/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?

Current query: `"Clay County Savings Association robbery" 1866 Liberty Missouri Jesse James Archie Clement James–Younger Gang guerrillas bushwhackers partisans term origin Revolutionary War usage`

New query: `Clay County Savings Association robbery Missouri guerrilla bushwhacker partisan definition called`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. Generate exactly one compact BM25-style bag-of-words query (single line, plain text, no operators, no punctuation beyond bare words, no multiple queries) that prioritizes short encyclopedia/dictionary lead lines naming the robbers with a single label. Preserve: - The event anchor (the robbery name or short event phrase, e.g., "Clay County Savings Association robbery" or a concise variant) and a location token ("Liberty", "Missouri" or "Missouri Civil War") so the robbery article ranks high. - A small candidate set of one-word perpetrator-label tokens (e.g., guerrilla, bushwhacker, partisan). Keep these tokens together in the query. - A short context cue to bias toward concise definitions or lead sentences: one of "definition", "lead", or "perpetrators" and a Civil‑War/Missouri context token ("Civil War" or "Missouri"). Restore/include cues that force short-label retrieval: - An ...
```

========================================================================================================================

## IDX 82 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 3/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?

Current query: `"Clay County Savings Association robbery" 1866 Liberty Missouri Jesse James Archie Clement James–Younger Gang guerrillas bushwhackers partisans term origin Revolutionary War usage`

New query: `Clay County Savings Association robbery Liberty Missouri perpetrators guerrillas bushwhackers Civil War`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` containing exactly one compact BM25-style bag-of-words query optimized for the SECOND hop. Your goal is to retrieve concise documents missed by the first hop (e.g., an article lead sentence or a short definition) that supply a single noun-label or tightly focused context needed to answer the question. Rules: - Preserve event and location anchors from the sample (keep the robbery/event phrase and place tokens as plain words). - Preserve a small candidate set of one-word label tokens when uncertain (e.g., guerrillas, bushwhackers, partisan) rather than expanding into many synonyms. - Restore retrieval cues that bias toward short lead/definition evidence: include an action/label cue such as robbers called or perpetrators or robbers were described as, plus a short context token like definition and a locality/context specifier (Civil War or Missouri). - Drop noisy side entities and long biographical or etymology ...
```

========================================================================================================================

## IDX 150 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 3/0
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

Current query: `Paul Winters biography Wayne State University head coach Wayne State Warriors football program history Tom Adams Field GLIAC Detroit`

New query: `Paul Winters head coach Wayne State University 2012 Wayne State Warriors football team`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. Generate exactly one compact BM25 query (single line) that targets short, authoritative lead/title lines tying a named season/team page and a named person page to the same institution. Rules: - Preserve only the core retrieval anchors: the exact season+team identifier (year + team name as it appears) and the person’s full name. Preserve a program alias only if it is identical to those anchors. - Restore the explicit institution token (the university name) if available; include it in the query to force the affiliation bridge. - Include one concise role/relation cue (e.g., head coach or coach) adjacent to the person anchor to favor coach-bio affiliation lines. - Drop noisy or broad tokens that dilute lead-line matches: biography/history, stadium/venue names, conference/division labels, city/location names, extra season years, tenure counts, long descriptive phrases, and other ...
```

========================================================================================================================

## IDX 150 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 1.000 (+1.000)
- generality/locality: 3/1
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

Current query: `Paul Winters biography Wayne State University head coach Wayne State Warriors football program history Tom Adams Field GLIAC Detroit`

New query: `Paul Winters 2012 Wayne State Warriors head coach Wayne State University`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. When the task is to identify a shared institutional affiliation between a specific season/team and a person, follow these rules: preserve only the core anchors from the inputs (the season+team identifier and the person name) and keep the original source anchor from summary_1; restore an explicit institution token (the university name) and a single role/relation cue (e.g., head coach or coach) so the query targets short lead-paragraph affiliation lines; drop noisy side tokens (biography, history, stadium names, conference/division labels, city names, other years, historical aliases, tenure counts and other broad modifiers); optionally keep a single venue token last only if it is necessary and unambiguous. Emit exactly one compact, single-line BM25-style query string composed of contiguous title-like tokens: cluster {person name} + {season team (year + team)} + {role cue} + ...
```

========================================================================================================================

## IDX 60 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 3/2
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

Current query: `Hubble Space Telescope STS-31 Space Shuttle Discovery launch date launch year`

New query: `STS-31 launch year`

Updated instruction excerpt:
```text
Given fields `question` and `summary_1`, produce exactly one compact BM25-style keyword query (2–6 tokens) optimized for the second hop to retrieve a telescope's launch year/date. Trigger: when the question asks for the launch year/date of a named telescope or the summary references the telescope's launch. Selection logic: - If a specific mission identifier (exact mission code, e.g., "STS-31") or a clear launch vehicle token appears in the context, prefer a mission-focused query with the mission id first, then a single date/relation cue: [MISSION_ID] + [launch|launch date|launch year] (e.g., STS-31 launch date). - Otherwise, emit an entity-centric query: [canonical telescope name or common alias] + [launch|launch date|launch year]. Optionally append one short type cue ('history' or 'overview') or the four-digit year token if it is already known and will tighten results. Preserve: the exact canonical telescope name or exact mission identifier/alias as present in inputs. Preserve a ...
```

========================================================================================================================

## IDX 90 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 1.000 → 1.000 (+0.000)
- generality/locality: 3/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: Imiliya is a town located in what pilgrimage site?

Current query: `Imiliya Kapilvastu Lumbini Nepal Maya Devi Temple sacred garden monastic zone UNESCO coordinates proximity`

New query: `Imiliya Kapilvastu Lumbini Mayadevi Temple pilgrimage`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. This composer is used when the question asks which pilgrimage site contains a named settlement (town → pilgrimage containment). Output exactly one single-line BM25 query string and nothing else. Rules: - Purpose: retrieve authoritative, locality- and heritage-focused passages that tie the sampled place to a pilgrimage site (site identity and locality/proximity), without asserting interior containment inside a sacred enclosure. - Preserve anchors: include the settlement name token exactly as in the inputs and its administrative district token (e.g., "Imiliya" and "Kapilvastu"). These are required. - Restore high-signal pilgrimage cues: include the pilgrimage-site name (e.g., "Lumbini") plus one principal landmark or authority token (choose one: "Mayadevi Temple", "Rummindei", "Ashoka pillar", or "UNESCO") and one site-type relation cue such as "pilgrimage" or "birthplace". Prefer one ...
```

========================================================================================================================

## IDX 132 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 3/5
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?

Current query: `Björk Guðmundsdóttir biography birthdate occupations discography filmography "Selmasongs" soundtrack credits Vespertine production credits`

New query: `Selmasongs soundtrack Bjork`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop of a multi‑hop retrieval system. Instruction (apply when the question asks who performed/is credited for a named film soundtrack or soundtrack album, e.g., contains the word "soundtrack", "soundtrack to", a film title, or an album title): - Goal: emit exactly one compact BM25-style keyword query (one single-line, space-separated string) that surfaces album-/release-level sources (album page, soundtrack credits, liner notes, reputable music-database entries) which explicitly credit the soundtrack artist and, when helpful, include a short artist descriptor. - Preserve high-priority anchors from the input: the album or soundtrack title token(s) and/or film title, the plain-stage artist token if already visible, and the relation cue "soundtrack" (treat these anchors as required tokens). - Restore concise album/credit bridge cues to target release-level evidence. Include exactly one or ...
```

========================================================================================================================

## IDX 140 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 3/5
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

Current query: `George Danzer World Poker Tour champion OR "List of World Poker Tour champions" "four World Series of Poker bracelets" birth date São Paulo`

New query: `George Danzer World Poker Tour`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. The generator must emit exactly one compact BM25-style keyword query (single-line, 3–6 tokens where possible) and nothing else. Choose one of the following three rule-driven templates depending on the retrieval trigger inferred from `summary_1` and prior hop state: 1) Candidate‑verification trigger (the next hop must verify whether a named candidate person is a World Poker Tour winner): - Preserve the candidate-person anchor (the person’s full name) and restore the canonical series anchor. - Drop list-oriented, birthdate/place, bracelet-count, other-player, and search‑operator tokens. - Template (single compact BM25 query): [PERSON] World Poker Tour - Purpose: surface pages that explicitly tie the named person to the World Poker Tour. 2) List‑lookup trigger (the retrieval goal is an authoritative, consolidated WPT winners/champions list to check presence of names): - Remove person- ...
```

========================================================================================================================

## IDX 140 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 3/5
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

Current query: `George Danzer World Poker Tour champion OR "List of World Poker Tour champions" "four World Series of Poker bracelets" birth date São Paulo`

New query: `George Danzer World Poker Tour born`

Updated instruction excerpt:
```text
Given the fields question and summary_1, produce the field query optimized for the second hop as a single compact BM25 keyword phrase according to the following rules. 1) Decision and anchors - If summary_1 yields one high-confidence candidate person (a single named "Candidate person" or an obvious person anchor), preserve that person's full name as the primary anchor token. - If the candidate is absent or uncertain and the task is to find which WPT winner matches a bracelet-count constraint, do not include any person name; instead target an authoritative winners/champions list and the bracelet-count cue. 2) Relation and cue restoration - Always restore an explicit World Poker Tour relation cue to force pages that tie people to the series (use tokens such as World Poker Tour or WPT plus a short relation token like winner or champions). - When seeking a birth date (final entity-centric hop), add a brief birth cue only when the birthplace is already present in summary_1 (use born or ...
```

========================================================================================================================

## IDX 149 | prompt_update_Rq_delta_p_only_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 3/4
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: A mythical forest creature that is seductive and from Sweden has the same being as what divine figure?

Current query: `Huld völva Holda Holle Germanic goddess origin of hulder skogsrå Tallemaja`

New query: `hulder Huld Holda völva identity`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. Generate exactly one compact BM25-style keyword query (one line, tokens separated by single spaces) that retrieves concise etymology/identity or comparative‑mythology passages linking a folkloric term to an older/divine/seer figure. Rules: - Preserve core canonical anchors (prefer the 1–3 most common forms): hulder Huld Holda. If the visible inputs include a specific form, prefer that canonical spelling. Do not list long orthographic variant sets unless present in inputs. - Restore a role/type cue and at least one relation/bridge cue: include the role token völva (or seer) and an etymology/identity marker such as etymology origin identity originally same being cognate. Ensure at least one etymology marker and the role marker are present. - Query ordering and shape: place 1–3 preserved entity anchors first, then one role/type token (völva/seer), then 1–2 relation tokens (etymology ...
```

========================================================================================================================

## IDX 149 | prompt_update_Rq_full_context_aggregate_steps_4
- MR: 0.000 → 0.000 (+0.000)
- generality/locality: 3/5
- patterns: preserve_anchor; restore_relation_or_type; drop_noisy_entity; candidate_uncertainty; bm25_interface_guard; single_query_guard; web_search_drift; multi_query_drift; query_string_like_delta; leakage_language
- bad_patterns: web_syntax; boolean_heavy; multi_query; leakage_language
- risky titles: instr=[], query=[]

Question: A mythical forest creature that is seductive and from Sweden has the same being as what divine figure?

Current query: `Huld völva Holda Holle Germanic goddess origin of hulder skogsrå Tallemaja`

New query: `hulder Huld Holda völva identity etymology`

Updated instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop of a multi-hop retrieval system. Your job is to output exactly one compact BM25-style query (one line, tokens separated by single spaces) that retrieves additional authoritative etymology/identity or comparative‑mythology passages not found in the first hop. Do not return multiple queries, explanations, titles, answers, or search-engine syntax. Trigger: apply when the question asks which older/divine/seer figure a folkloric term is “the same being as” or asks for the original identity of a named Swedish seductive forest-creature (e.g., hulder, skogsrå, local variants). Preserve: keep 1–3 primary entity anchors in canonical spellings (examples: hulder, Huld, Holda, Frau Holle). Preserve role/type cue token völva (or seer) and at least one philological marker (examples: etymology, origin, identity, huldr, huld, cognate). Restore: if the generator omits role/type or philological ...
```