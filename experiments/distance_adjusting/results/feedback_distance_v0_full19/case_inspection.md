# Feedback distance case inspection

## left_fail (18 total, showing 12)

### 108__split1__seg1__feedback__left
- idx: 108
- split_iter: 1
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.72
- why_larger: Segment B changes the retrieval orientation (disambiguation -> focused extraction) and adds explicit infobox/lead extraction cues and manufacturer-location evidence, which meaningfully shifts query-shape and evidence targets beyond mere title-disambiguation in A.

#### Question
Are Solo and La Croix Sparkling Water produced in the same country ?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
Disambiguate "Solo" toward the Australian lemon-flavoured soft drink (focus on country of origin).

KEEP:
- Anchors: "Solo (Australian soft drink)"; "Solo (soft drink)"; "La Croix Sparkling Water"; "United States"; "Australia"
- Bridge clues to retain: presence of a page titled "Solo (Australian soft drink)"; lead/infobox text stating "Country of origin" / "Origin: Australia"; manufacturer or distributor entries implying Australian production (e.g., Schweppes Australia)
- Expected evidence type: short authoritative lead/infobox or manufacturer page explicitly naming Australia as Solo's country of origin/production

ADD_OR_RESTORE:
- BM25-relevant tokens and aliases to add: "Solo (Australian soft drink)", "Solo lemon-flavoured", "Solo Australia", "country of origin", "manufactured in Australia", "made in Australia", "Schweppes Australia", "Asahi Australia distributor", "infobox: Country of origin", "lead: Origin: Australia"
- Bridge cues to emphasize: exact-title match, infobox/lead lines, manufacturer location lines, phrases like "origin" or "manufactured" near "Australia"
- Noise-removal hints to restore: prefer pages whose title exactly matches "Solo (Australian soft drink)" and rank infobox/lead text higher than generic brand mentions

REMOVE_OR_AVOID:
- Distractors: "Solo (Norwegian soft drink)"; Trend Drinks; Geo. Hall & Sons; Rubicon Drinks; V (drink); Guaraná Antarctica
- Broad/ambiguous pages: global Schweppes/Asahi pages that do not mention Solo or a country-of-origin line; generic "soft drink" lists and unrelated beverage brand pages
- Terms to de-emphasize: generic "Solo" without geographic qualifier; distributor/manufacturer mentions that lack explicit Australian production info

QUERY_SHAPE:
Short disambiguation-style retrieval template that prioritizes exact-title and country cues: prioritize tokens ["Solo (Australian soft drink)", "Solo Australia", "country of origin", "manufactured in Australia", "Schweppes Australia"] and boost matches where those tokens appear in the page title or infobox/lead; downweight pages containing only generic brand lists or other regional "Solo" entries.

...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rmid_iter2_split1

step: 1
from: Rmid_iter1_split0
to: Rmid_iter2_split1
pgrad: TRIGGER:
Disambiguation step returned multiple "Solo" candidates but lacks a concise infobox/lead phrase stating Solo's country; switch to a focused extraction orientation to surface an explicit "Country/Origin: Australia" line and named Australian manufacturer.

KEEP:
- Anchors: "Solo (Australian soft drink)", "Solo (soft drink)", "La Croix Sparkling Water", "United States", "Australia"
- Manufacturer/distributor tokens from R_left: "Schweppes Australia", "Asahi", "Coca-Cola Amatil"
- Bridge clues indicating a canonical Solo page or disambiguation page title

ADD_OR_RESTORE:
- Infobox/lead extraction cues: exact strings "Country of origin", "Origin:", "Produced in", "produced in Australia", "Australian lemon-flavoured soft drink", "Solo is an Australian"
- Page-title targeting: canonical title token "Solo (Australian soft drink)" and common alias "Solo (Australia)"
- Manufacturer evidence tokens tied to production location: "Schweppes Australia (manufacturer)", "manufactured in Australia", "distributed in Australia"
- Type/date cues to prefer authoritative pages: "Wikipedia infobox", "lead sentence", "first produced 19XX" (to catch lead/summary lines)

REMOVE_OR_AVOID:
- Noisy regional variants and distractors: "Solo (Norwegian soft drink)", other regional Solo brands, generic beverage lists
- Broad manufacturer pages that mention Schweppes/Asahi globally without linking Solo to Australia
- News/distribution articles that discuss deals or export without stating production country
- Queries that only use the ambiguous token "Solo" without title or infobox anchors

QUERY_SHAPE:
Title-focused, disambiguation-to-extraction pattern: prefer exact-title OR title+country tokens (e.g., "Solo (Australian soft drink)" OR "Solo Australian") combined with infobox/lead anchors ("Country of origin" OR "Origin:" OR "produced in" OR "lead sentence") and manufacturer name tokens; deprioritize pages matching regional aliases (Norway) or global manufacturer pages.

WHY_THIS_MOVES_RETRIEVAL:
Adding infobox/lead anchors and exact-title tokens increases BM25 overlap with the canonical Solo page and its explicit origin line,
...[truncated]

---

### 108__split2__seg2__feedback__left
- idx: 108
- split_iter: 2
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why_larger: Segment B prescribes a procedural change to the retrieval strategy (a disambiguation-first, two-step chain: fetch disambiguation → follow confirmed product page → extract lead/infobox). This alters the query-generation control flow and candidate-following order, not just the tokens or anchors to add. A is mainly a focused reweighting/disambiguation of anchors and avoidance tokens, while B changes how results are retrieved and validated.

#### Question
Are Solo and La Croix Sparkling Water produced in the same country ?

#### Full-edge feedback
- edge: Rmid_iter2_split1 -> Rstar_target

step: 2
from: Rmid_iter2_split1
to: Rstar_target
pgrad: TRIGGER:
Step 2 — disambiguate Solo origin toward the Australian Solo page

KEEP:
- Anchors: "Solo (Australian soft drink)", "infobox/lead sentence", "Country of origin: Australia", "Manufacturer / Distributor (Schweppes Australia, Asahi, Coca‑Cola Amatil)"
- Bridge clues: lead phrasing like "Solo is an Australian...", infobox field "Origin" or "Country", phrases "Australian lemon‑flavoured soft drink", "produced in Australia"
- Query-shape intent: concise extraction-style focus on page lead/infobox lines

ADD_OR_RESTORE:
- Disambiguation tokens: include "(Australian)", "Australian", "lemon‑flavoured", "soft drink"
- Type and extraction cues: add exact‑phrase anchors such as "Origin: Australia", "Produced in Australia", "Manufacturer:", "Distributed by"
- Source preferring cues: "Wikipedia", "official site", "manufacturer page" to boost canonical pages
- Manufacturer aliases as bridge anchors: "Schweppes Australia", "Asahi", "Coca‑Cola Amatil"
- Explicit avoidance token to discourage variants: include negative/contrast clue like "not Norwegian / not 'Solo (Norwegian)'" (for filtering)

REMOVE_OR_AVOID:
- Noisy titles and topics: "Solo (Norwegian soft drink)", "Trend Drinks", "Geo. Hall & Sons", "Rubicon Drinks", "V (drink)", "Guaraná Antarctica"
- Generic/ambiguous tokens: single word "Solo" alone, broad lists of soft drinks, beverage manufacturer pages that mention brands in multiple countries without linking Solo to Australia
- Non‑evidence content: distribution deal articles or product lists that don't state production/origin

QUERY_SHAPE:
- Behavior: build a short, disambiguating extraction-style query that forces the Australian sense and targets lead/infobox lines and manufacturer pages. Example structure to aim for (do not use as final query): include the phrase "Solo (Australian)"/"Solo is an Australian" OR "Solo (Australian soft drink)" + one of ("Origin", "Country", "Produced in", "Manufacturer", "Distributed by", "infobox", "lead") and prefer site:wikipedia.org or the manufacturer's domain. Avoid queries that use only "Solo" or list-level terms.

WHY_THIS_MOVES_RETRIEVAL:
- Adds precise, high‑weig
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter2_split1 -> Rmid_iter3_split2

step: 2
from: Rmid_iter2_split1
to: Rmid_iter3_split2
pgrad: TRIGGER:
When the direct-target strategy (hit Solo (Australian soft drink) lead/infobox) produces ambiguous results or multiple "Solo" variants surface; switch to a disambiguation-first retrieval pass to confirm which "Solo" to follow.

KEEP:
- Anchors: Solo (Australian soft drink); infobox / lead sentence; "Country of origin: Australia"; manufacturer/distributor names (Schweppes Australia, Asahi, Coca-Cola Amatil).
- Bridge clues: lead phrasing like "Solo is an Australian..." or "lemon‑flavoured soft drink produced in Australia".
- Noise removal guidance from prior step: avoid long brand lists and unrelated beverage pages.

ADD_OR_RESTORE:
- Add disambiguation anchors: Solo (disambiguation), Solo (soft drink) summary line, disambiguation entry pointing to Solo (Australian soft drink).
- Add type and alias cues: "soft drink", "lemon-flavoured", "Australian", parenthetical forms (Solo (Australian soft drink), Solo (soft drink)).
- Add short manufacturer header cues: "Schweppes Australia", "Asahi", "Coca‑Cola Amatil" appearing in connection with Solo.
- Add extraction target order: disambiguation entry → linked product page lead/infobox → explicit "Country/Origin" and manufacturer line.

REMOVE_OR_AVOID:
- Avoid pages for Solo regional variants (Solo (Norwegian), other-country Solo brands).
- Avoid global manufacturer pages or long beverage lists that mention Solo without a country link.
- Avoid news/distribution articles that reference brand deals but do not state production/origin.

QUERY_SHAPE:
Behavioral chain: first fetch the Solo disambiguation/summary and extract the entry that names the Australian product (anchor: "Solo (disambiguation)" → "Solo (Australian soft drink)"); if disambiguation confirms the Australian entry, follow that link and extract lead/infobox lines for "Country of origin/produced in" and named manufacturer/distributor. Use parenthetical and type cues ("Solo (soft drink)", "lemon‑flavoured", "Australian") to boost BM25 matches; suppress broad list or manufacturer-only pages.

WHY_THIS_MOVES_RETRIEVAL:
Adding a disambiguation-first step steers BM25 toward the exact canonical page
...[truncated]

---

### 118__split0__seg0__feedback__left
- idx: 118
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.93
- why_larger: Segment A requires a structural change to query-generation: add an explicit disambiguation-first pass (enumerate Third Person candidates + years/synopses) then a dedicated cast-extraction pass producing version-tagged top-billed actress lists. This reorders and broadens the retrieval workflow and candidate set selection. Segment B mainly adds tighter surface anchors (years, named actors) and cross-check queries, which is a narrower, targeted refinement.

#### Question
What acress starred in both "Third Person" and "From Here to Eternity"?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
Initial hop yields disambiguation/TV/musical pages or unrelated titles (no clear authoritative cast page for Third Person and the 1953/1979 From Here to Eternity versions), or search results emphasize unrelated names (Kim Basinger, Heather O'Rourke) instead of credited cast.

KEEP:
- Preserve versioned anchors: "Third Person (film)", "From Here to Eternity (1953 film)", "From Here to Eternity (1979 miniseries)".
- Preserve bridge clues: "full cast lists / credited actor names", "matching performer names across lists", "version disambiguation".
- Preserve retrieval focus on authoritative cast/credit sources (Wikipedia film pages, IMDb, filmographies) and the intent to intersect named cast members.

ADD_OR_RESTORE:
- Add explicit year/alias anchors and star names to bias toward the canonical film pages: "Third Person (2013) / Third Person (film)"; "From Here to Eternity (1953)"; include actor anchors "Deborah Kerr", "Donna Reed".
- Add type cues and provenance tokens: "cast", "full cast", "credited", "IMDb full cast", "Wikipedia infobox cast", "filmography".
- Add action bridge: "actor filmography" and "appeared in" to support second-hop cross-checks (e.g., search an actor's filmography page to confirm presence in both titles).
- Add noise-suppression cue: prefer "film" + year phrases and "miniseries (1979) cast" for deliberate versioning.

REMOVE_OR_AVOID:
- Avoid disambiguation and non-film variants: "From Here to Eternity (disambiguation)", "From Here to Eternity (TV series)", "From Here to Eternity the Musical", "From Here to Eternity: Live".
- Avoid unrelated film noise and celebrity names not tied to these casts: "Eternal Sunshine of the Spotless Mind", "Kim Basinger", "Heather O'Rourke".
- Avoid generic, undated queries like "Third Person cast" without a year or source tag that permit ambiguous matches.

QUERY_SHAPE:
- Behavior: emit two precise second-hop queries and one cross-check query.
  1) Exact-title + year + provenance cue + cast token: [exact film title + (year)] + ("cast" OR "full cast" OR "IMDb" OR "Wikipedia infobox").
  2) Repeat for the specific From Here to Eternity version(s): [“From Her
...[truncated]

#### Sub-edge feedback
- edge: R0_base -> Rmid_iter1_split0

step: 0
from: R0_base
to: Rmid_iter1_split0
pgrad: TRIGGER:
When the cast-focused retrieval returns disambiguation pages, missing or non-specific 'Third Person' cast pages, or a mix of unrelated titles (musical/live adaptations, similarly named works) instead of clear, version-specific cast lists.

KEEP:
- Anchors: "Third Person (film)", "From Here to Eternity (1953 film)", "From Here to Eternity (1979 miniseries)".
- Retrieval focus on authoritative cast/credit sources (Wikipedia film pages with infobox "Starring", IMDb title pages, established filmographies).
- Bridge clues: "full cast lists", "matching performer names", "release year / title disambiguation".

ADD_OR_RESTORE:
- First perform a short disambiguation step for "Third Person" to enumerate candidate works and their release years (collect title + year + short synopsis).
- For each candidate Third Person and each relevant From Here to Eternity version, extract top-billed/principal actresses (use "Starring", "Top cast", "Principal cast" fields).
- Prefer compact, version-tagged actor lists (name + billed position + source line: e.g., "Deborah Kerr — 'Starring' (Wikipedia infobox)").
- Include explicit type cues (film vs. miniseries, release year) so names are tied to the correct work.
- Restore instruction to collect only pages that list credited cast (avoid news articles or fan lists).

REMOVE_OR_AVOID:
- Avoid retrieving musicals, stage/live adaptations, or unrelated films surfaced by broad title matches (e.g., "From Here to Eternity the Musical", "From Here to Eternity: Live", unrelated hits like "Eternal Sunshine...").
- Avoid broad/personal-name-heavy results that are not title-specific cast pages.
- Avoid pages lacking clear cast lists or release-year disambiguation.

QUERY_SHAPE:
Two-step, ordered behavior:
1) Disambiguation pass: find "Third Person" candidate entries (title + year + short synopsis) and confirm relevant versions of "From Here to Eternity" (1953 film, 1979 miniseries) — keep results small and version-tagged.
2) Cast-extraction pass: for each confirmed work, fetch authoritative cast blocks and return compact top-billed/principal-actress lists (name, billed role position, source ta
...[truncated]

---

### 118__split2__seg1__feedback__left
- idx: 118
- split_iter: 2
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.87
- why_larger: Segment B requires broader semantic changes: it expands candidate sets to include multiple versions (1953 and 1979), adds an explicit disambiguation phase, differentiates film vs. TV/miniseries, and adds director/year alias weighting and billing tags — all of which change which titles are retrieved and how results are labeled. Segment A is a tighter narrowing to two exact anchors and simpler extraction rules.

#### Question
What acress starred in both "Third Person" and "From Here to Eternity"?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rmid_iter2_split1

step: 1
from: Rmid_iter1_split0
to: Rmid_iter2_split1
pgrad: TRIGGER:
Step 1 — current step is performing broad title disambiguation for “Third Person” and checking which version of “From Here to Eternity” is intended.

KEEP:
- Preserve the goal of producing candidate actor sets per specific work/version (disambiguation → candidate actor lists).
- Keep use of authoritative film pages and disambiguation pages as primary sources (Wikipedia/IMDb/filmographies).
- Keep bridge clues: title + release year, lead/billed actresses, and 'starring' / cast-list sections as evidence targets.
- Keep explicit noise flags already listed (songs, books, unrelated similarly named works) so they remain deprioritized.

ADD_OR_RESTORE:
- Bias toward the single most-likely modern/main film for each ambiguous title by adding exact title+year aliases: "Third Person (2013 film)" and "From Here to Eternity (1953 film)" as primary anchors.
- Add behavior to preferentially fetch sections labeled "Starring", "Cast", or top-billed list entries on those exact-title pages and extract female performer names only.
- Restore targeted sources preference: open the title page (Wikipedia) then corroborate with IMDb cast section if needed; prefer pages where billing order is explicit.
- Add extraction constraint: return the first 2–4 top-billed female names per title (names and short role labels if present) to create compact candidate sets for intersection.
- Add alias and date cues: include common name variants (e.g., “From Here to Eternity 1953”, “Third Person 2013”) to match BM25 surface text in page headings.

REMOVE_OR_AVOID:
- Stop broad multi-year disambiguation sweeps that enumerate every work named "Third Person" (books, songs, shorts) unless 2013 is missing from top results.
- Avoid surfacing male-only cast lists, crew/production trivia, soundtrack, and unrelated remakes/adaptations (e.g., stage musical) as primary hits.
- Avoid large cast rosters beyond the top-billed performers and avoid pages that only mention titles in passing without a cast section.

QUERY_SHAPE:
- Two narrow, high-precision lookups (exact-title + year + cast cues), e.g.:
  1) [Title alias: "Third Person (2013)" OR text:
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rmid_iter3_split1

step: 1
from: Rmid_iter1_split0
to: Rmid_iter3_split1
pgrad: TRIGGER:
Narrow "Third Person" disambiguation to the few prominent film/TV title candidates (prioritize the 2013 feature) and extract top-billed female performers while simultaneously pulling principal female cast lists for the 1953 and 1979 versions of "From Here to Eternity."

KEEP:
- Preserve the two-step local order: (1) disambiguate "Third Person" to candidate titles/years, (2) pull top-billed actresses for each candidate and for the common "From Here to Eternity" versions.
- Keep anchor targets: "Third Person (disambiguation)", "From Here to Eternity (1953 film)", "From Here to Eternity (1979 miniseries)".
- Keep expected evidence type: authoritative title pages with clear "Starring"/"Cast" sections.

ADD_OR_RESTORE:
- Prioritize the prominent feature entry "Third Person (2013 film)" as the first candidate; include director/year alias cues (e.g., "Third Person 2013", "Paul Haggis") to weight BM25 ranking.
- Restore instructions to capture billing cues: prefer "Starring", top 2–4 billed names, and role annotations ("as ...") for each title.
- Add explicit type and date cues to queries: mark results as "film" vs "TV/miniseries" and attach release year to returned actor sets.
- Add alias handling: detect alternate title spellings/forms ("Third Person", "Third Person (film)", numeric/abbreviated forms) to avoid missing the 2013 entry.
- Require compact output per title: return a short list (2–4) of female names with year and billing indicator (lead/support) for fast intersection.

REMOVE_OR_AVOID:
- Avoid broad, unfocused disambiguation that returns non-film items (books, songs, plays) or exhaustive long cast lists.
- Filter out obscure shorts, festival entries, stage adaptations, and crew/trivia pages that do not list clear "starring" billing.
- Avoid mining full cast rosters or male-only cast sections that bury principal actresses.
- Exclude noisy pages whose primary purpose is production notes, soundtrack, or remake commentary rather than a clear billed cast list.

QUERY_SHAPE:
- Phase A (disambiguation-focused, narrow): run a short disambiguation lookup for "Third Person (disambiguation)" but imm
...[truncated]

---

### 140__split1__seg1__feedback__left
- idx: 140
- split_iter: 1
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.68
- why_larger: B changes the retrieval pipeline shape and candidate set: it shifts from a single-name check to a systematic, ordered two-step scan of authoritative WPT champions lists plus iterative filtering of each candidate’s bio by exact bracelet-count phrases. This re-centers retrieval (list-first, then per-name filtering) and adds new BM25 anchors and candidate seeds, a broader structural change than A’s targeted birth-date extraction and tie-break refinements.

#### Question
When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
Confirm which World Poker Tour (WPT) champion also has four World Series of Poker (WSOP) bracelets and extract that person’s birth date (hop 2).

KEEP:
- Anchors: "George Danzer", "List of World Poker Tour champions", "World Poker Tour winner", "four World Series of Poker bracelets".
- Bridge clue behavior: first check "George Danzer" + WPT connection; if absent, scan WPT champions list for a name with "four WSOP bracelets".
- Noise list to retain awareness of: pages about Danzer’s WSOP wins that lack WPT info; other WPT names (David Chiu, John Hennigan, Alexandre Gomes) as distractors to be validated.

ADD_OR_RESTORE:
- Add explicit extraction cues: look for "born", "birth date", "birthplace", "date of birth" or formatted dates (DD Month YYYY / YYYY) in player biographies.
- Add authoritative source anchors: "wpt.com champions list", "List of World Poker Tour champions", "player biography", "Wikipedia (player name) biography", "WSOP.com player profile".
- Add alias cues and variations: include name variants and diacritics (e.g., "George Danzer", "Danzer, George").
- Add type cues: prioritize pages labeled "champion", "winner", "biography", "profile", or "results".
- Add tie-break bridge: if candidate absent from WPT lists, search the WPT champions list for entries that co-occur with the phrase "four World Series of Poker bracelets", then open that entry’s biography to capture birth date.

REMOVE_OR_AVOID:
- Avoid pages that only discuss WSOP bracelet counts without any WPT mention.
- Avoid forum posts, blog recaps, or local event pages lacking structured biography fields.
- Avoid pages that conflate terms (e.g., "World Poker Tour bracelet") or use imprecise language that mixes WPT and WSOP.
- De-prioritize players known to have conflicting bracelet counts (e.g., David Chiu with five bracelets) unless the page explicitly lists four.

QUERY_SHAPE:
Entity-centric two-step retrieval: (1) lookup "George Danzer" + any WPT / champions-list signal to confirm presence on an official WPT winners page; (2) if absent, run a targeted scan of "List of World Poker Tour champions" for names that co-occur with the
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rmid_iter2_split1

step: 1
from: Rmid_iter1_split0
to: Rmid_iter2_split1
pgrad: TRIGGER:
If the single-name verification ("George Danzer" + "WPT" / "World Poker Tour") does not produce a WPT champion entry for Danzer, move from candidate-specific verification to systematic cross-referencing of WPT winners and their WSOP bracelet counts.

KEEP:
- Anchors: "George Danzer", "List of World Poker Tour champions", "World Poker Tour winner", "WPT winners list", "four World Series of Poker bracelets".
- Bridge behavior: first check "George Danzer WPT" / "George Danzer \"World Poker Tour\"" to confirm presence/absence on WPT lists before broadening.
- Noise flags to preserve: deprioritize pages that discuss only WSOP results without mentioning WPT, and forum/local reports flagged as non-authoritative.

ADD_OR_RESTORE:
- New BM25 anchors: "List of World Poker Tour champions", "World Poker Tour champions table", "WPT champions list", "WPT winners roster", "World Poker Tour winners by year".
- Candidate-name anchors to surface on WPT lists: "David Chiu", "John Hennigan", "Alexandre Gomes" (treat as query seeds, not assertions).
- Type cues for authoritative sources: "official WPT champions page", "WPT winners list (table)", "player biography", "WSOP records", "player profile — bracelet(s)".
- Phrase-level bracelet anchors to filter bios: "\"four-time World Series of Poker\" OR \"4-time World Series of Poker\" OR \"four WSOP bracelets\" OR \"4 WSOP bracelets\"".
- Step-order behavior: (1) retrieve authoritative WPT winners/champions list page(s) (table/roster) to extract candidate names; (2) for each candidate name from that list, fetch a short authoritative bio or WSOP record snippet that contains the bracelet-count phrase anchors above. Do NOT fetch birth dates in this step.
- Noise-reduction cues to restore: prefer pages with structured lists/tables and one-line bios (e.g., Wikipedia list pages, WPT official pages, WSOP player records).

REMOVE_OR_AVOID:
- Avoid relying on pages that only celebrate WSOP achievements without WPT context.
- Avoid discussion threads, fan blogs, local event reports, and pages that conflate WPT events with WSOP language (e.g., "World Poker Tour bracelet").
- Avo
...[truncated]

---

### 140__split3__seg2__feedback__left
- idx: 140
- split_iter: 3
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why_larger: Segment B requires a broader and deeper per-player retrieval: it adds canonical page/URL and normalized aliases, demands explicit birth-date lines as well as bracelet counts, and changes the output into a structured mapping per winner. This is a larger semantic shift than A, which only adds a check for a '4 bracelet' snippet while forbidding birthdate retrieval.

#### Question
When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

#### Full-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter2_split1

step: 2
from: Rmid_iter3_split1
to: Rmid_iter2_split1
pgrad: TRIGGER:
After extracting the WPT champions list, cross-check each winner for an explicit WSOP bracelet count and shortlist those described as four-time WSOP bracelet winners.

KEEP:
- Step 1 (preserve): Locate an authoritative, year-by-year "List of World Poker Tour champions" (official WPT site or Wikipedia) and extract winner names and years in order.
- Anchors to keep: "List of World Poker Tour champions", "World Poker Tour winners list (official site or Wikipedia)", "WPT champions by year", "WPT winner names (extracted list)", "George Danzer".
- Maintain output: a deduplicated short list of WPT winner names (to feed the next check).

ADD_OR_RESTORE:
- Step 2 (add): For each extracted WPT winner name, fetch a compact biographical snippet or WSOP record line that explicitly states that player's WSOP bracelet count (look for phrasing like "four-time World Series of Poker bracelet winner", "has four WSOP bracelets", or "4 bracelets").
- Anchors to add: "player name + 'World Series of Poker bracelet(s)'", "player name + 'four-time' + 'WSOP'", "WSOP player profile", "Wikipedia: [player name] (bracelets)", "WSOP.com player results".
- Aliases/type cues: include common name variants (e.g., "George Danzer", "David Chiu", "John Hennigan", "Alexandre Gomes") and prefer one-line authoritative sources (Wikipedia summary lines, WSOP.com stats, official player bios).
- Output requirement: return a shortlist of WPT winners with an attached one-line evidence snippet indicating "4 bracelets" (source label), but do NOT fetch birth dates or full biographies.

REMOVE_OR_AVOID:
- Avoid: fan forums, match reports, local news about individual events that are not consolidated lists; WSOP-only pages that do not confirm WPT winner status; pages that discuss bracelets qualitatively without a numeric count; pages conflating WPT events with WSOP bracelets.
- Avoid retrieving full biographical pages or birthdate fields at this step — only collect the minimal bracelet-count phrase.
- Avoid noisy long tournament recaps or site pages that mix small events with official WPT champions lists.

QUERY_SHAPE:
- Two-stage local pattern (
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter4_split2

step: 2
from: Rmid_iter3_split1
to: Rmid_iter4_split2
pgrad: TRIGGER:
R_left -> R_right handoff: after extracting WPT winners by year, immediately pivot to collecting per-player authoritative identifiers and explicit WSOP-bracelet and birth-date lines so R_right can map names → bracelet counts and filter for "4".

KEEP:
- Preserve the year-indexed WPT champions list extraction (source title, winner name, year) and deduplicated winner-name list from R_left.
- Keep anchors that locate an authoritative champions list: "List of World Poker Tour champions", "World Poker Tour winners list", "WPT champions by year".
- Keep the instruction to flag presence/absence of a candidate name on the champions list.

ADD_OR_RESTORE:
- For each extracted winner name, also fetch one authoritative player-level record (preferred order: Wikipedia player page infobox, official WSOP player profile, Hendon Mob profile) and return:
  - canonical page title / URL (preferred retrieval key for follow-up).
  - normalized name variants / aliases (common short forms, diacritics removed).
  - explicit infobox or first-line phrase containing "WSOP bracelet(s)", e.g., "4 WSOP bracelets" or "four-time World Series of Poker bracelet winner".
  - explicit birth date line (ISO or day-month-year, if present).
  - one-line evidence snippet: source title + quoted phrase containing bracelet count or birth date.
- Add BM25-relevant anchors and cues to each per-player retrieval: "player Wikipedia infobox", "World Series of Poker profile", "Hendon Mob player profile", "X WSOP bracelet(s)", "born DD Month YYYY", "aka / also known as".
- Restore type cues to prefer numeric counts (digit or spelled-out) and direct phrases like "four-time" or "4 bracelets" rather than aggregate tournament tallies.

REMOVE_OR_AVOID:
- Exclude noisy sources: match reports, single-event news that don't summarize career bracelet totals, fan forums, blogs, and pages that mix non-WPT local tournaments with official WPT titles.
- Avoid pages that only say "multiple bracelets" or ambiguous phrasing without a numeric indicator; mark those as 'unknown' but do not treat them as positive evidence.
- Avoid broad lists of poker players withou
...[truncated]

---

### 149__split2__seg1__feedback__left
- idx: 149
- split_iter: 2
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.82
- why_larger: Segment B introduces multiple new semantic directions — adding cognacy/comparative-mythology relations, medieval/early-modern primary-source cues, and role-comparison signals — which broaden and re-center retrieval toward different evidence families and relation types. This requires a bigger change to query-generation behavior than A's narrower shift toward short definitional lead‑sentences.

#### Question
A mythical forest creature that is seductive and from Sweden has the same being as what divine figure?

#### Full-edge feedback
- edge: Rmid_iter2_split0 -> Rmid_iter1_split0

step: 1
from: Rmid_iter2_split0
to: Rmid_iter1_split0
pgrad: TRIGGER:
Shift from name-origin focus to short authoritative identity statements: prioritize sources that pair hulder/skogsrå → Huld and Huld ↔ Holda/Frau Holle in a single definitional or etymological line. (Step 1)

KEEP:
- Anchors: Hulder, Skogsrå, Huld, Völva, huldr / huld (name-root), Tallemaja, ulda
- Bridge clues to preserve: etymology: hulder ← huldr / huld; citations noting Huld as a völva/seer; regional name citations and linguistic/philological commentary tying Huld to later folk‑figure names
- Expected evidence types to keep: etymological-dictionary entries, folklore encyclopaedia entries, comparative‑mythology summaries that treat name-derivation and Huld's role

ADD_OR_RESTORE:
- Anchors to add: Holda, Frau Holle, "Holda/Frau Holle" as alias pair
- Type cues: encyclopedia entry, etymological dictionary, folklore compendium, comparative‑mythology note, short definitional line
- Bridge clues to add: explicit short sentence(s) that say the hulder is originally the same being as Huld and that Huld is equated with Holda/Frau Holle; paired phrases like "hulder — Huld" and "Huld = Holda / Frau Holle" in one source; citations to 19th/early‑modern folklorists or philologists who state the identity
- Retrieval behavior: prefer passages that combine name-derivation + identity claim in one paragraph or lead‑sentence (high precision), prioritize authoritative sources (encyclopaedia, scholarly dictionaries)

REMOVE_OR_AVOID:
- Specific noise to avoid: "Coat of arms of Lardal", "872 Holda", "Haugtussa", "Spillaholle", "Gussy Holl"
- Types to avoid: heraldry/local civic pages, catalogue/list pages with numeric identifiers, creative retellings or modern fiction, index pages without definitional prose, broad cultural histories that lack concise etymology/identity statements

QUERY_SHAPE:
Short, high‑precision pairings that combine the folkloric term + authoritative cue + identity verb, e.g. templates like:
- [hulder OR skogsrå] + [etymology | "name derives"] + [Huld] + [encyclopaedia | "dictionary"]
- [Huld] + [Holda OR "Frau Holle"] + [= | "identif*"] + [folklore | "comparative mythology" | "encyclopaedia
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter2_split0 -> Rmid_iter3_split1

step: 1
from: Rmid_iter2_split0
to: Rmid_iter3_split1
pgrad: TRIGGER:
After confirming hulder ← huld name‑root and sources that present Huld as a völva/seer (local etymology + role evidence established).

KEEP:
Hulder; Skogsrå; Huld; Völva; huldr / huld (name‑root); Tallemaja; ulda; etymology entries, folklore encyclopedia/dictionary lines, philological/name‑history sections.

ADD_OR_RESTORE:
Holda / Hold(e)a; Frau Holle; cognate / cognacy / "related name"; comparative mythology; "shared root" or "semantic field" (hidden/covered); medieval / early‑modern source citations; role comparisons (seeress, household/ fertility/witch‑like attributes, seiðr); etymological/onomastic commentary proposing links; type cues: "encyclopaedia of folklore", "comparative‑mythology article", "onomastics", "Germanic studies", "primary medieval reference".

REMOVE_OR_AVOID:
Modern pop‑culture retellings and novels; municipal/heraldic pages; catalog or numeric list entries; long motif lists without etymological linking; isolated local tale pages that do not discuss name‑history; pages asserting definitive identity without comparative/etymological argumentation.

QUERY_SHAPE:
Behavioral pattern: expand from "hulder Huld etymology + völva" toward pairwise comparative searches that join Huld/Huldr with Holda/Holda/Frau Holle using relation keywords and period cues. Example search fragments to emulate (not final queries): 
- Huld Huldr + Holda Hold(e)a + cognate / cognacy / etymology
- "Huld" + "Frau Holle" + comparative mythology + medieval / early modern
- hulder skogsrå + Huld + Holda + etymological note / onomastics / folkloristic survey
Favor encyclopaedia/onomastic/academic pages and medieval source citations; deprioritize broad culture or name‑list pages.

WHY_THIS_MOVES_RETRIEVAL:
Adds the cross‑regional anchors (Holda / Frau Holle) and cognacy/comparative cues needed to surface scholarship that explicitly treats Huld and Holda as related names or archetypes. Keeps prior etymology and völva evidence so retrieved pages will connect name‑origin to broader Germanic parallels, while noise removal prevents pop‑culture, heraldry or motif‑list pages from diluting comparative/etymological 
...[truncated]

---

### 150__split1__seg0__feedback__left
- idx: 150
- split_iter: 1
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why_larger: Segment A prescribes a more targeted re-centering of retrieval: it enforces title-exact, lead/snippet-priority hits and explicit query shapes (title-targeted and person-role), plus a detailed remove list of confounding pages. Those instructions change query construction and ranking priorities more strongly than B's comparable but broader/token-focused suggestions.

#### Question
What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

#### Full-edge feedback
- edge: R0_base -> Rmid_iter1_split0

step: 0
from: R0_base
to: Rmid_iter1_split0
pgrad: TRIGGER:
Seed retrieval returned team and coach pages but lacked exact on-page affiliation phrasing; results include season pages and coach bios without a short sentence tying both to "Wayne State University".

KEEP:
- Anchors: 2012 Wayne State Warriors football team; Paul Winters; Wayne State University; Tom Adams Field
- Bridge clues to preserve: team-season affiliation language; coach listed as head coach of the Wayne State Warriors
- Retrieval focus: surface explicit affiliation lines that name the university on both season and coach pages

ADD_OR_RESTORE:
- Exact phrase cues: represented Wayne State University; head coach of the Wayne State Warriors; Paul Winters head coach Wayne State University
- Date and type tokens: 2012, season page, team roster, coach bio, coach biography
- Aliases and clarifiers: Wayne State Warriors (Wayne State University), Wayne State (Detroit)
- BM25-relevant anchors to boost: "represented Wayne State University", "head coach", "Wayne State University"
- Preference for short lines/sentences on page (lead sentence, infobox line)

REMOVE_OR_AVOID:
- Temporal/year noise: 2016, 2017, 1975, 1977, other seasons
- Role-count and career-history noise: "7th year", "13th year", previous positions
- Broad program or conference noise: GLIAC, Division II, general Wayne State Warriors history pages that lack an explicit affiliation line
- Distracting venue/conference detail when not adjacent to affiliation sentence

QUERY_SHAPE:
Compose compact, token-focused retrieval cues that prioritize exact affiliation phrasing plus role and year indicators (e.g., include tokens: 2012 · "Wayne State Warriors" · "represented Wayne State University" · Paul Winters · "head coach" · season page/coach bio). Favor short phrase matches and lead/infobox text over long historical pages.

WHY_THIS_MOVES_RETRIEVAL:
Adding exact affiliation phrases and role+year tokens increases BM25 signal for pages that contain the concise, on-page statements tying the 2012 team and Paul Winters to Wayne State University, while removing temporal and program-level noise prevents higher-scoring but irrelevant season histories or broa
...[truncated]

#### Sub-edge feedback
- edge: R0_base -> Rmid_iter2_split0

step: 0
from: R0_base
to: Rmid_iter2_split0
pgrad: TRIGGER:
narrow retrieval to page lead-lines: surface the 2012 season page lead and the Paul Winters coach/bio page (title-targeted, role-centered hits).

KEEP:
- anchors in order: "2012 Wayne State Warriors football team", "Paul Winters", "Wayne State Warriors", "Wayne State University"
- bridge clues in order: "season page lead sentence ties team to university", "Paul Winters described as head coach of the Wayne State Warriors", "program overview or roster/staff page mapping 'Wayne State Warriors' → 'Wayne State University'"

ADD_OR_RESTORE:
- type cues: "lead sentence", "first paragraph", "bio", "coach profile", "season page"
- BM25-boost phrases / exact-match anchors: "represented Wayne State University", "head coach Paul Winters", "Paul Winters bio", "2012 season", "title: 2012 Wayne State Warriors football team"
- retrieval behavior: prefer title-exact hits and snippet hits that include role+institution phrasing; surface short, authoritative lead-paragraph snippets

REMOVE_OR_AVOID:
- temporal / season noise: "2016", "2017", "2011", "other season pages"
- unrelated venues / confounds: "Tom Adams Field", "GLIAC", "NCAA Division II", "stadium", "conference"
- historical naming noise: "Wayne State Tartars", "older season pages (1975, 1977)"
- overly broad pages: generic program overview when lead does not state university affiliation explicitly

QUERY_SHAPE:
- title-targeted shape: [exact season title token(s)] + (lead|first paragraph|season page)
- person-role shape: [person name] + (head coach | bio | coach profile) + (Wayne State University | Wayne State Warriors)
- snippet-priority instruction: favor hits where snippet contains exact phrases "represented Wayne State University" or "head coach" near "Paul Winters"

WHY_THIS_MOVES_RETRIEVAL:
Focusing on exact title tokens and role phrases increases BM25 term overlap with lead-paragraph language that states institutional affiliation, so season-title hits and coach-bio hits will score higher than noisy season variants or venue/confference pages. Preferring short lead/snippet evidence and the phrases "represented Wayne State University" or "head coach Paul Win
...[truncated]

---

### 169__split3__seg2__feedback__left
- idx: 169
- split_iter: 3
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why_larger: Segment A adds more and finer-grained semantic constraints: new exact-phrase patterns, specific site filters (NYT/THR/Guardian), lifespan and alias tokens, plus explicit restore instructions to check filmography pages. These changes alter query construction and retrieval targeting more strongly than B's higher-level prioritization of authoritative sources.

#### Question
What movie did "the king of cool" play in with Bud Ekins as his stunt double?

#### Full-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter1_split0

step: 2
from: Rmid_iter3_split1
to: Rmid_iter1_split0
pgrad: TRIGGER:
Shift the local retrieval step from exploratory secondary-source signals toward authoritative credit-confirmation for Bud Ekins as Steve McQueen’s stunt double (emphasize explicit credit language and primary film-credit sources; still check Bullitt but as a narrow credit-resolution task).

KEEP:
- Anchors: Bud Ekins; Steve McQueen ("The King of Cool"); The Great Escape; "motorcycle jump" / motorcycle stunt.
- Bridge clues to preserve: phrases naming Ekins in connection with The Great Escape; obituary / Hall-of-Fame language crediting a famous motorcycle stunt.
- Exploratory caution: treat popular mentions of Bullitt as a signal to verify, not as proof.

ADD_OR_RESTORE:
- Add explicit type cues and source targets: "stunt double", "credited as stuntman", obituary, Stuntmen's Hall of Fame entry, filmography, IMDb, BFI, NYT/THR obituaries, reputable film-history essays.
- Add aliases and date cues to disambiguate: "Steve McQueen" ("The King of Cool"); Bud Ekins (May 11, 1930 – October 6, 2007).
- Bridge clues to add: exact-credit phrasing such as "stunt double for Steve McQueen", "performed the motorcycle jump", "credited in [film] credits".
- Instructional behavior: prioritize exact-phrase matches and primary credit databases and authoritative outlets before accepting secondary mentions; explicitly query filmography/credit pages for both The Great Escape and Bullitt.

REMOVE_OR_AVOID:
- Avoid noise: Triumph TR6 / motorcycle-spec pages, motoring-forum posts, unsourced fan claims, generic "stunt" pages, unrelated riders (e.g., Dave Ekins) unless they explicitly confirm credits.
- Avoid broad exploratory queries that return general motorcycling history rather than explicit credit language.

QUERY_SHAPE:
- First pass: targeted exact-phrase checks in authoritative outlets for explicit-credit language (seek lines like "Bud Ekins" + "stunt double" + "The Great Escape" or "performed the motorcycle jump" on obituary/Hall-of-Fame/major newspaper/film-history sites).
- Second pass: narrow primary-credit verification in film-credit databases and filmography pages (IMDb, BFI, official film-credit listings) fo
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter4_split2

step: 2
from: Rmid_iter3_split1
to: Rmid_iter4_split2
pgrad: TRIGGER:
Step 2 — Pivot from exploratory confirmation to authoritative secondary + filmography checks.

KEEP:
- Focus: confirm Bud Ekins as Steve McQueen’s stunt double for the motorcycle sequences in The Great Escape.
- Parallel lightweight check for mentions tying Ekins to Bullitt (exploratory, do not assume doubling).
- Anchors retained: "Bud Ekins", "Steve McQueen (\"The King of Cool\")", "The Great Escape", "motorcycle jump / motorcycle stunt", "Bullitt (exploratory)".
- Bridge clues retained: look for phrases explicitly naming Ekins as McQueen's stunt double on The Great Escape; obituaries/Hall-of-Fame language crediting the motorcycle stunt.

ADD_OR_RESTORE:
- Add authoritative source targets and type cues: "obituary", "Stuntmen's Hall of Fame", "film-history article", "NYT / Hollywood Reporter / Guardian", and filmography/databases: "IMDb", "BFI", "TCM".
- Add exact-phrase patterns to prefer: '"Bud Ekins" "The Great Escape"', '"Bud Ekins" "motorcycle jump"', '"Bud Ekins" "stunt double" "Steve McQueen"', and '"Bud Ekins" obituary' or '"Bud Ekins" "Stuntmen\'s Hall of Fame"'.
- Add role-clarification cue: prefer citations that use explicit credit language — e.g., "stunt double for Steve McQueen" vs "stunt performer on The Great Escape".
- Add date/alias hints to raise precision: include Ekins lifespan "May 11, 1930 – October 6, 2007" and McQueen alias "Steve McQueen (\"The King of Cool\")" when searching authoritatively to filter obituaries/biographies.
- Restore instruction to check filmography listing pages on imdb.com, bfi.org.uk, tcm.com for credit type (stunt performer vs stunt double) and capture exact credit wording.

REMOVE_OR_AVOID:
- Deprioritize and avoid: forum posts, unsourced fan blogs, social media, motorcycle-spec pages (Triumph TR6 technical discussions), pages about relatives (e.g., Dave Ekins) that don't state credits.
- Avoid primary-archive deep dives (studio call sheets, original credit scans) at this step — save for a later verification step.
- Avoid generic "stunt history" pages that lack explicit film-credit statements; avoid pages that mention Bullitt without explicit st
...[truncated]

---

### 180__split2__seg2__feedback__left
- idx: 180
- split_iter: 2
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.89
- why_larger: Segment B requires a broader change in retrieval behavior: instead of directly extracting a single canonical date, it instructs assembling a structured candidate set (multiple regioned dates, provenance, DB IDs, reissue tagging) across many evidence families — a more substantial semantic shift than A's focused move to extract a precise album-level release date.

#### Question
What is the date of released for the eleventh studio album of the highest-selling heavy metal group from Canada?

#### Full-edge feedback
- edge: Rmid_iter2_split1 -> Rstar_target

step: 2
from: Rmid_iter2_split1
to: Rstar_target
pgrad: TRIGGER:
Confirmed band = Annihilator and 11th-album title + release year identified in prior hop.

KEEP:
- Maintain the band identity confirmation step (Annihilator) and the validated 11th-album title and release year.
- Keep authoritative sources list: band page (Wikipedia lead / official site), discography listing, album page stub/infobox.
- Preserve the ordinal-check behavior (use discography or album page text that states "Nth studio album").

ADD_OR_RESTORE:
- Add an explicit step to extract the official full release date (day/month/year) for that 11th studio album from high-authority album-level sources: album infobox, release-history section, label press release, official band announcement, or major music databases (AllMusic, Discogs, MusicBrainz, Metal Archives).
- Anchor on BM25-relevant tokens when searching: "<Album Title>", "Annihilator", "released", "release date", "infobox", "release history", "label", "press release".
- Include common aliases/stylizations of the album title and the release year (e.g., alternate punctuation, subtitle, year in parentheses) to disambiguate.
- If multiple regional dates appear, prefer the original-market first-press release date (note region/label) and capture the primary day/month/year cited by authoritative sources.
- Restore discography-as-source fallback: if the album page lacks day/month, query the discography entry and linked citations for the album's release date.

REMOVE_OR_AVOID:
- Avoid extracting only the year (no partial-date stops); do not stop at year-only sources.
- Avoid counting or listing pages that mix compilations, live albums, reissues, or boxed sets with studio albums; ignore pages that do not clearly label "studio album" or the album's ordinal.
- Avoid low-authority fan forums, unsourced listicles, and unrelated Canadian acts (e.g., Thor, Anvil) that may appear in results.
- Avoid regional reissue/remaster dates unless the original-release date cannot be confirmed from primary sources.

QUERY_SHAPE:
- Two-step retrieval behavior (preserve step order):
  1) Open the confirmed album page / discography entry already found to re-check ordinal 
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter2_split1 -> Rmid_iter3_split2

step: 2
from: Rmid_iter2_split1
to: Rmid_iter3_split2
pgrad: TRIGGER:
Confirmation from prior step that the target band is Annihilator (or an authoritative source equating "highest‑selling Canadian heavy metal group" to that band) and that the 11th studio‑album title and its release year have been identified/saved.

KEEP:
- Band canonical name (Annihilator) and any verified aliases.
- The identified 11th studio‑album title and the noted release year.
- Saved album page URL(s) or record ID(s) (do not extract day/month yet).
- The constraint to avoid picking a final canonical date at this step.

ADD_OR_RESTORE:
- Open the album's primary article/page and extract the infobox "Released" field plus its citation URL.
- Fetch the band's official site / label press release pages mentioning the album and copy the announcement date and source URL.
- Query major music databases for versioned releases: Discogs release entries (catalogue number, regional pressing), MusicBrainz release groups/relations, AllMusic album page — capture any listed full release dates and their source links.
- Collect region qualifiers for each date candidate (e.g., Canada, Europe, Japan) and note which source asserts each.
- Record differences between original-release entries and later reissues/remasters; tag entries as "original" vs "reissue/deluxe".
- Preserve each candidate date together with its citation URL and a one‑line provenance note (site name, page title, region).
- Restore search for contemporary press/review dates (magazine archive lines or press-kit PDFs) that corroborate a launch day.

REMOVE_OR_AVOID:
- Do not re-run band‑identity confirmation searches or re-fetch general discography lists already used.
- Avoid fan forums, unsourced wiki edits, social posts, and pages that list only a year without citation.
- Exclude pages clearly about reissues, remasters, compilations, box sets (unless they explicitly state original-release day and are authoritative).
- Ignore aggregated lists that mix studio/live/compilation without explicit ordinal labeling (to prevent miscounting).

QUERY_SHAPE:
- Step 1 (album page): open "AlbumTitle" + site:wikipedia.org OR "AlbumTitle" album page — extract 
...[truncated]

---

### 247__split1__seg0__feedback__left
- idx: 247
- split_iter: 1
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.87
- why_larger: Segment A re-centers retrieval to a different candidate set and evidence family (local Ghana outlets and activist social posts), adds actor-account cues and strict date anchoring, and strongly prioritizes petition/hashtag/link tokens — a broader semantic shift than B's mainly query‑shaping and boosting of social/campaign tokens.

#### Question
What is another name for the online protest that opposed the transfer of ex-detainees from Guantanamo Bay in 2016?

#### Full-edge feedback
- edge: R0_base -> Rmid_iter1_split0

step: 0
from: R0_base
to: Rmid_iter1_split0
pgrad: TRIGGER:
Current retrieval returns general Gitmo/detainee lists and news about the January 2016 Ghana transfer but no quoted online campaign name, hashtag, or petition label.

KEEP:
- Anchor actor tokens: OccupyGhana (also "Occupy Ghana"), New Patriotic Party, Ghana.
- Event/date anchors: January 2016, 2016, Ghana transfer, Guantanamo, Gitmo, Yemeni ex-detainees.
- Retrieval focus phrasing: "locate news or social‑media mentions" that explicitly name an online protest/campaign.
- Bridge clues to retain: online campaign, hashtag, e‑petition, social media protest, named online protest, coverage of public reaction.

ADD_OR_RESTORE:
- Boost signals for media/type tokens: include explicit cues for "hashtag", "#", "petition", "e‑petition", "Facebook", "Twitter", "tweet", "campaign", "petition to", "online petition".
- Favor quoted labels and embeds: prefer documents that reproduce a quoted token (e.g., " #... ", "petition: '...'", tweet embeds).
- Alias and token variants: allow "Guantanamo" OR "Gitmo"; "OccupyGhana" OR "Occupy Ghana"; include substring/wildcard hashtag patterns (hashtag stems) rather than one exact tag.
- Narrow source/time scope: prioritize contemporary news/social‑media coverage circa Jan 2016 and immediate follow‑up reporting.
- Retrieval behavior: boost documents that pair an actor anchor (OccupyGhana/NPP) with a campaign-type token (hashtag/petition/Facebook/Twitter) in the same sentence or quoted excerpt.

REMOVE_OR_AVOID:
- Demote list/timeline/biography pages: "List of Yemeni detainees", timelines, individual detainee bios (Obaidullah, Inayatullah), hunger strike histories.
- Avoid historical/general Gitmo summaries and non‑campaign blog posts that lack embedded social posts or quoted campaign names.
- Filter out broad Guantanamo release roundups that do not quote campaign labels or social‑media tokens.

QUERY_SHAPE:
Construct a BM25‑style query that (1) requires an event + actor anchor and (2) boosts documents containing social‑media/campaign type tokens.
- Required proximity: (OccupyGhana OR "Occupy Ghana" OR "New Patriotic Party" OR NPP) near (Ghana OR Guantanamo OR Gitmo) near (Jan 2016 OR
...[truncated]

#### Sub-edge feedback
- edge: R0_base -> Rmid_iter2_split0

step: 0
from: R0_base
to: Rmid_iter2_split0
pgrad: TRIGGER:
R0_base -> Rmid_iter2_split0 — localize retrieval to Ghana-focused outlets and activist social posts; prefer campaign/hashtag/petition tokens.

KEEP:
- Anchors: OccupyGhana, New Patriotic Party (NPP), Ghana, January 2016 transfer, Yemeni ex-detainees, Guantanamo / Gitmo.
- Retrieval focus concept: look for news or social-media mentions tied to the Jan 2016 Ghana transfer that explicitly name an online campaign, petition, or hashtag.
- Bridge clues to preserve: "online campaign", "hashtag", "e-petition", "social media protest", "named online protest".

ADD_OR_RESTORE:
- Boost local Ghana news domains and site cues: GhanaWeb, JoyOnline, Citi Newsroom, Graphic Online, local .gh domains; prefer pages from these domains in scoring.
- Boost social-platform and campaign tokens: Change.org, petition, e-petition, Facebook, Twitter, tweet, hashtag, "#", embedded post, link to petition, press release.
- Add behavioral cue: prioritize documents containing quoted phrases, explicit hashtags (token with leading #), or links to petitions.
- Add actor-account cues: OccupyGhana (Facebook/Twitter), NPP social posts; favor matches that co-occur with those account names or handles.
- Date anchoring: prefer hits explicitly mentioning "January 2016" or "Jan 2016" near campaign tokens.

REMOVE_OR_AVOID:
- De-prioritize broad Gitmo lists, detainee biographies, timeline pages, and international summaries that lack campaign metadata.
- Avoid documents whose main focus is detainee rosters, hunger strikes, or historical analyses without local campaign or social-media tokens.
- Suppress generic search noise: non-Ghana international outlets that summarize the transfer without linking to local petitions or social posts.

QUERY_SHAPE:
Compose retrieval signals by conjoining three components (not a single literal query):
1) event anchors: {Ghana, "January 2016", Guantanamo OR Gitmo, Yemeni ex-detainees, OccupyGhana, NPP}
2) locality/type boosters: {site:local Ghana domains, GhanaWeb, JoyOnline, Graphic, Citi Newsroom, Facebook, Twitter}
3) campaign tokens (must appear or be boosted): {petition, Change.org, e-petition, "online campaign",
...[truncated]

---

### 262__split0__seg0__feedback__left
- idx: 262
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.86
- why_larger: Segment A instructs a broader semantic re-centering of retrieval from game/developer-centric pages to designer-centric candidate sets (filmography/credits/profiles), adds richer disambiguation signals (Japanese script, birth year, alternate name ordering) and enforces co-occurrence of name+per-title credit — a larger change in which anchors and result family to target. Segment B is a tighter, target-specific narrowing (exact-title + credit-source) rather than a re-centering of the candidate set.

#### Question
Kunihiko Tanaka designed the characters for which video game developed by Monolith Soft ?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER: narrow-to-explicit-credits-for-Xenoblade-Chronicles-X

KEEP: Kunihiko Tanaka; Xenoblade Chronicles X (exact title); Monolith Soft; role concept "character designer"

ADD_OR_RESTORE: explicit credit-source tokens and disambiguators — "credits", "staff", "official site", "game manual", "MobyGames", "Giant Bomb", "Nintendo", "filmography", "credit list"; release-year/platform cues "2015", "Wii U"; title alias "Xenoblade X"; full-name alias with birth date "Kunihiko Tanaka (born August 12, 1970)"

REMOVE_OR_AVOID: noisy Xeno-series pages and character names — "KOS-MOS", "Xenosaga", "Xenogears", "Xenoblade Chronicles 2", "Tetsuya Takahashi", general series summaries or fan pages that mention Tanaka tangentially

QUERY_SHAPE: form short conjunctive queries that prioritize exact-entity + role + exact-title + credit-source. Behavior: require the designer's exact name AND a role-token ("character designer" OR "character design") AND the full game title ("Xenoblade Chronicles X" OR "Xenoblade X"), then append a credit-source token (e.g., "credits", "official site", "MobyGames", "Nintendo", "staff list") and optionally a release-year/platform token ("2015", "Wii U") to boost pages with formal credits.

WHY_THIS_MOVES_RETRIEVAL: adding explicit role + exact game-title plus credit-source tokens raises BM25 overlap with official credits pages and filmography entries while excluding high-frequency but irrelevant Xeno-related terms; release-year/platform and full-name alias further disambiguate the designer from other credits, shifting results away from pages about KOS‑MOS/Xenosaga or general series histories toward authoritative game-credit pages that name Kunihiko Tanaka as a character designer for Xenoblade Chronicles X.

#### Sub-edge feedback
- edge: R0_base -> Rmid_iter1_split0

step: 0
from: R0_base
to: Rmid_iter1_split0
pgrad: TRIGGER:
When current retrieval returns developer- or title-centric pages (Xenosaga, KOS-MOS, Xenogears, Monolith Soft game lists) or generic game-credit pages instead of a designer-specific credits/filmography page for Kunihiko Tanaka.

KEEP:
- Anchors: "Kunihiko Tanaka", "Xenoblade Chronicles X", "character designer", "Monolith Soft".
- Expected evidence type: authoritative credits sources (official credits pages, reputable game-credit aggregators).
- Intent to confirm per-title role and credit attribution.

ADD_OR_RESTORE:
- Prioritize designer-focused tokens: "filmography", "works", "credits", "profile", "artist portfolio".
- Prioritize source signals: "Wikipedia (filmography)", "MobyGames", "Giant Bomb", "official artist/agency page", "game manual / official credits".
- Disambiguation cues: alternate name order "Tanaka Kunihiko", Japanese script "田中邦彦", birth year "1970" to filter homonyms.
- Bridge action: shift retrieval toward pages listing Kunihiko Tanaka's credited titles (then pivot to the game's credits if needed).
- Noise-reduction markers: require presence of both the designer's name and a per-title credit token (e.g., "character designer", "credits", "credited") in results ranking.

REMOVE_OR_AVOID:
- Tokens and pages that attract Xeno-series noise: "KOS-MOS", "Xenosaga", "Xenogears", broad Tetsuya Takahashi pages, other Xenoblade titles (e.g., Xenoblade Chronicles 2).
- Fan/forum posts, unverified blogs, and generic pages that mention the name without a credits/filmography section.
- Results that only list characters or lore without explicit credit role lines.

QUERY_SHAPE:
Use designer-centric BM25-friendly shapes combining full name + role/type cue + credential sources and optional disambiguators, for example:
- "<Kunihiko Tanaka> +(filmography|works|credits|profile|portfolio) +(MobyGames|Giant Bomb|Wikipedia|official)"
- "<Kunihiko Tanaka> +(character designer|credited|credits) +(<Xenoblade Chronicles X>|Monolith Soft) +(<1970|田中邦彦>)"
Emphasize co-occurrence of the designer's name and explicit credit-role tokens; prefer source-type tokens ("MobyGames", "Wikipedia", "official") to boost authori
...[truncated]

---

## right_fail (19 total, showing 12)

### 108__split3__seg3__feedback__right
- idx: 108
- split_iter: 3
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.72
- why_larger: Segment A instructs a stronger, more specific semantic shift: it not only adds exact-title anchors and manufacturer tokens but enforces an extraction-focused query shape (prefer 1–2 line lead/infobox snippets, explicit local ordering), and more aggressively removes corporate/aggregate pages and noisy same-name senses. Those directives change both which anchors are preserved and how results are scored/trimmed, a larger behavioral change than B's mainly BM25‑disambiguation boosts.

#### Question
Are Solo and La Croix Sparkling Water produced in the same country ?

#### Full-edge feedback
- edge: Rmid_iter3_split2 -> Rstar_target

step: 3
from: Rmid_iter3_split2
to: Rstar_target
pgrad: TRIGGER:
Disambiguation lead present or broad "Solo" hits returned but no document whose title or lead contains the exact tokens "Solo (Australian soft drink)" or the phrase "Solo is an Australian".

KEEP:
- Keep disambiguation-focused behavior: look for "Solo (disambiguation)" and short lead/infobox lines.
- Keep anchors: "Solo (soft drink)" alias, manufacturer names as candidate bridges (e.g., Schweppes Australia, Asahi, Coca‑Cola Amatil).
- Keep bridge clues: lead sentence patterns like "Solo is an Australian..." or "lemon‑flavoured soft drink produced in..."

ADD_OR_RESTORE:
- Add exact-title and alias anchors: the token sequence Solo (Australian soft drink), "Solo (soft drink)", and the phrase "Solo is an Australian".
- Add country/type tokens: Australia, "country of origin", "produced in", "manufactured in", "lemon‑flavoured".
- Add manufacturer/distributor anchors as connectors: Schweppes Australia, Asahi, Coca‑Cola Amatil (as short header/infobox hits).
- Favor lead/infobox cues: presence of an infobox line containing "Country" or "Origin: Australia" and short one‑sentence leads with "Australian".
- Include date/established cues only as supporting tokens if present in lead (e.g., first produced year) to prefer authoritative product pages.

REMOVE_OR_AVOID:
- Deprioritize or filter out pages and tokens: "Solo (Norwegian soft drink)", Trend Drinks, V (drink), Guaraná Antarctica, long brand lists, and global manufacturer pages that do not include "Australia" or explicit "produced in" lines.
- Avoid long news/distribution articles and pages that mention many beverages without an explicit country/origin token.

QUERY_SHAPE:
Local, BM25‑style disambiguation query that prioritizes documents whose title or lead/inbox contains the exact anchor tokens ("Solo (Australian soft drink)" OR "Solo is an Australian") AND includes one or more country/type tokens (Australia, "country of origin", "produced in", "manufactured in", "lemon‑flavoured"); use manufacturer tokens (Schweppes Australia, Asahi, Coca‑Cola Amatil) as secondary boosts; penalize documents matching distractor tokens ("Norwegian", "Trend Drinks", long
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter4_split3 -> Rstar_target

step: 4
from: Rmid_iter4_split3
to: Rstar_target
pgrad: TRIGGER:
When current summary shows La Croix produced in the United States and Solo's production country is missing or ambiguous.

KEEP:
- Narrow, extraction-style target: one-sentence lead and/or infobox line (country of origin; manufacturer/producer).
- Emphasis on a single authoritative short snippet rather than full lists or long manufacturer pages.
- Local order: first prefer page lead sentence, then infobox country/manufacturer line, then single-line manufacturer header.

ADD_OR_RESTORE:
- Disambiguation anchors and aliases: "Solo (Australian soft drink)", "Solo (soft drink)", "Solo — lemon‑flavoured (Australia)".
- BM25-tight clues: exact phrases "Country of origin: Australia", "produced in Australia", "manufactured in Australia", "made in Australia".
- Manufacturer name cues to help scoring: "Schweppes Australia", "Asahi", "Coca‑Cola Amatil" (as short brand/producer tokens).
- Date/type cue to narrow pages: include "Australian lemon‑flavoured soft drink" and "lead sentence / infobox".
- Instruction to prefer a single-line factual snippet (1–2 lines) that identifies Solo's country.

REMOVE_OR_AVOID:
- Broad lists and aggregator pages (e.g., "Trend Drinks", long manufacturer brand lists).
- Irrelevant similarly‑named titles: "Solo (Norwegian soft drink)" and other international "Solo" entries.
- Manufacturer corporate pages that list many brands without per‑brand country lines.
- News/global operations pages that mention international distribution without explicit country-of-origin lines.

QUERY_SHAPE:
An extraction-focused, disambiguating search behavior: bias toward the exact title "Solo (Australian soft drink)" and short infobox/lead-line matches containing tokens ["Country of origin", "produced in", "manufactured in", "Australia", manufacturer names], returning 1–2 lines (lead sentence first, infobox country/manufacturer line second).

WHY_THIS_MOVES_RETRIEVAL:
Adding precise title aliases and strong BM25 tokens ("Country of origin: Australia", manufacturer names, "Australian lemon‑flavoured") raises relevance for the Solo (Australian) page and depresses scores for similarly‑named or broad list pa
...[truncated]

---

### 118__split1__seg1__feedback__right
- idx: 118
- split_iter: 1
- task_kind: right_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.85
- why_larger: Segment B requires a bigger change: it broadens the candidate set from only top‑billed actresses to full credited casts, adds explicit actor anchor tokens (e.g., Deborah Kerr, Donna Reed) to bias retrieval, and changes the query shape to a two‑step confirm+fetch pattern. Those changes alter which entities are preserved/added and materially expand retrieval scope compared with A’s mainly versioned, top‑billing-focused cast lookups.

#### Question
What acress starred in both "Third Person" and "From Here to Eternity"?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
After the disambiguation hop returns one or more concrete "Third Person" title-year candidates and at least one identified version/year for "From Here to Eternity" (i.e., you have specific title+year pairs to test).

KEEP:
- Preserve the disambiguation ordering: list candidate works for "Third Person" with release years and candidate status (film/miniseries/TV).
- Keep anchors that guided disambiguation: "Third Person (disambiguation)", candidate years (e.g., 2013), "From Here to Eternity (1953 film)", "From Here to Eternity (1979 miniseries)".
- Retain the intent to extract lead/top-billed actresses (use "starring"/"lead"/"credited" cues) and short synopses to confirm which cast lists are primary.

ADD_OR_RESTORE:
- Immediately issue narrow, versioned cast lookups for each candidate title: exact-title + year + type + cast (target pages that list full credited cast).
- Prefer authoritative filmography sources (Wikipedia film pages, IMDb title pages, major film databases) and extract "starring / billed / credited" actress names; normalize name variants/aliases.
- If the question is underspecified, prioritize the 1953 film version of From Here to Eternity but still check the 1979 miniseries; enumerate both actor sets separately.
- Produce compact named-actor sets for each specific work/version to enable a direct intersection in the next step.

REMOVE_OR_AVOID:
- Avoid broad, undated title searches ("Third Person" alone) that surface disambiguation noise (books, songs, unrelated works).
- Avoid actor biography pages or news mentions unless they explicitly contain the title-specific credited cast section.
- Exclude tangential pages: TV-series adaptations, generic "From Here to Eternity (disambiguation)" results unless they link to the authoritative title pages.
- Suppress irrelevant celebrity hits (e.g., Kim Basinger, Heather O'Rourke) unless they appear on the authoritative cast lists for the specific title/version.

QUERY_SHAPE:
- Template 1 (film/miniseries cast): "<Exact Title> (<YYYY> film|miniseries|TV) cast" — e.g., "Third Person (2013 film) cast" or "From Here to Eternity (1953 film) cast".
- T
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter2_split1 -> Rstar_target

step: 2
from: Rmid_iter2_split1
to: Rstar_target
pgrad: TRIGGER:
If the previous hop produced small, non‑overlapping candidate actress sets or returned disambiguation/ambiguous title pages for either title (no clear full cast lists for the specified years).

KEEP:
- Preserve explicit year disambiguation tokens (e.g., "Third Person 2013", "From Here to Eternity 1953") and the step order: first resolve/confirm each title, then compare casts.
- Keep focus on authoritative cast sources (Wikipedia, IMDb, reputable filmographies).
- Keep bridge clues: "cast", "starring", "credited", "filmography", and role/’as’ annotations.

ADD_OR_RESTORE:
- Add alternate-version disambiguation for From Here to Eternity (include "1979 miniseries") so the retrieval will confirm which version is relevant.
- Add BM25‑friendly actor anchors to bias retrieval toward likely female leads (e.g., "Deborah Kerr", "Donna Reed") as verification checks.
- Add site/type cues to elevate authoritative sections: include tokens like site:wikipedia.org OR site:imdb.com, plus section hints: "cast" OR "starring" OR "credited".
- Restore broader cast scope (full credited cast lists) rather than only top 2–4 billed actresses—so overlaps in supporting cast are captured.
- Add alias/title templates to handle variations: exact-title + year in quotes, and parenthetical forms (e.g., "Third Person (2013 film)", "From Here to Eternity (1953 film)", "From Here to Eternity (1979 miniseries)").

REMOVE_OR_AVOID:
- Remove the overly narrow constraint that limits extraction to only the first 2–4 female names; avoid discarding supporting actresses.
- Avoid noisy tokens: "soundtrack", "trivia", "production", "release date", generic disambiguation pages (unless they lead to a specific film page).
- Avoid following unrelated names/pages flagged as noise (e.g., pages about Kim Basinger or Heather O'Rourke) unless they appear in the confirmed cast lists.

QUERY_SHAPE:
Steped two-query pattern (preserve order):
1) Confirm and fetch authoritative cast page for Third Person: ("Third Person" + 2013 + cast | "Third Person (2013 film)" + cast | site:wikipedia.org "Third Person (2013)" "Starring" | site:imdb.com "Third Person" cas
...[truncated]

---

### 140__split3__seg2__feedback__right
- idx: 140
- split_iter: 3
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.82
- why_larger: Segment A imposes more and narrower semantic constraints: it requires explicit token-pattern matching for the numeric '4' (BM25-friendly forms), enforces using structured infobox/lead fields, instructs capturing the exact matched token span to bridge to the next hop, and mandates labeling non-explicit candidates — all of which change retrieval/query-shaping and bridging behavior more than B's broader cross-check instruction.

#### Question
When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

#### Full-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter2_split1

step: 2
from: Rmid_iter3_split1
to: Rmid_iter2_split1
pgrad: TRIGGER:
After extracting the WPT champions list, cross-check each winner for an explicit WSOP bracelet count and shortlist those described as four-time WSOP bracelet winners.

KEEP:
- Step 1 (preserve): Locate an authoritative, year-by-year "List of World Poker Tour champions" (official WPT site or Wikipedia) and extract winner names and years in order.
- Anchors to keep: "List of World Poker Tour champions", "World Poker Tour winners list (official site or Wikipedia)", "WPT champions by year", "WPT winner names (extracted list)", "George Danzer".
- Maintain output: a deduplicated short list of WPT winner names (to feed the next check).

ADD_OR_RESTORE:
- Step 2 (add): For each extracted WPT winner name, fetch a compact biographical snippet or WSOP record line that explicitly states that player's WSOP bracelet count (look for phrasing like "four-time World Series of Poker bracelet winner", "has four WSOP bracelets", or "4 bracelets").
- Anchors to add: "player name + 'World Series of Poker bracelet(s)'", "player name + 'four-time' + 'WSOP'", "WSOP player profile", "Wikipedia: [player name] (bracelets)", "WSOP.com player results".
- Aliases/type cues: include common name variants (e.g., "George Danzer", "David Chiu", "John Hennigan", "Alexandre Gomes") and prefer one-line authoritative sources (Wikipedia summary lines, WSOP.com stats, official player bios).
- Output requirement: return a shortlist of WPT winners with an attached one-line evidence snippet indicating "4 bracelets" (source label), but do NOT fetch birth dates or full biographies.

REMOVE_OR_AVOID:
- Avoid: fan forums, match reports, local news about individual events that are not consolidated lists; WSOP-only pages that do not confirm WPT winner status; pages that discuss bracelets qualitatively without a numeric count; pages conflating WPT events with WSOP bracelets.
- Avoid retrieving full biographical pages or birthdate fields at this step — only collect the minimal bracelet-count phrase.
- Avoid noisy long tournament recaps or site pages that mix small events with official WPT champions lists.

QUERY_SHAPE:
- Two-stage local pattern (
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter4_split2 -> Rmid_iter2_split1

step: 3
from: Rmid_iter4_split2
to: Rmid_iter2_split1
pgrad: TRIGGER:
After producing a mapping of WPT winners -> WSOP bracelet counts, narrow to winners with an explicit numeric "4" bracelet claim.

KEEP:
- Use the WPT champions/winners list (previous-step output) as the input name list.
- For each listed winner, open authoritative player-level bios/profiles (Wikipedia infobox/lead, official WSOP player page, Hendon Mob summary, reputable news bios) and extract the exact phrase that states bracelet counts.
- Preserve the one-line evidence snippet policy: return source title + short quoted phrase showing the bracelet count.

ADD_OR_RESTORE:
- Target explicit numeric patterns for exactly four bracelets: tokens and phrases to match (BM25-friendly): "4", "4x", "four", "four-time", "four‑time World Series of Poker bracelet winner", "has won four World Series of Poker bracelets", "4 WSOP bracelets", "4 World Series of Poker bracelets".
- Prefer structured locations: infobox 'WSOP bracelets' field, first paragraph summary lines, or WSOP.com profile summary line. If multiple sources, prefer the most authoritative (official WSOP > Wikipedia > major news outlet > Hendon Mob).
- Include alias and disambiguation cues when searching each name: common nicknames, alternate spellings, and birth-year snippets (use birth year only to disambiguate identical names; do not extract full birthdates now).
- Produce a short filtered output: a deduplicated shortlist of WPT winner names that have an explicit numeric "4" statement plus the source snippet and URL. Mark any candidate lacking an explicit numeric "4" as "no-explicit-4" rather than inferring from event lists.
- Restore bridge behavior: for each candidate, capture the matched token span (e.g., "four-time World Series of Poker bracelet winner" or "4 WSOP bracelets") to feed the next hop (birth-date retrieval).

REMOVE_OR_AVOID:
- Avoid relying on pages that only list individual WSOP event wins or tournament cashes without an aggregated bracelet count.
- Exclude forum posts, fan pages, and summary tables that use vague language ("multiple", "several", "many") or outdated counts unless a secondary authoritative source confirms a n
...[truncated]

---

### 150__split2__seg2__feedback__right
- idx: 150
- split_iter: 2
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.63
- why_larger: Segment A imposes stronger, more specific changes to retrieval behavior: it mandates exact-title disambiguation (e.g., 'Paul Winters (American football)'), an explicit ordered retrieval strategy (season page → coach bio → fallback university page), and tightly constrained short BM25 query shapes. These require more concrete generator changes than B's mainly phrasing/affiliation bias and multi-hit suggestion.

#### Question
What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 2
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
Step2_move_affiliation_bias_toward_Wayne_State_University

KEEP:
- Anchor entity tokens: "2012 Wayne State Warriors football team", "Paul Winters", "Wayne State University", "Wayne State Warriors"
- Bridge clues to preserve: "head coach", "represented Wayne State University", "Wayne State Warriors football"
- Retrieval focus: look for short on-page affiliation lines (season page affiliation sentence; coach bio/team roster coach line)

ADD_OR_RESTORE:
- Boost exact phrase matches and aliases: "represented Wayne State University", "Paul Winters (American football)", "Wayne State (Detroit)", "Wayne State University — Detroit"
- Add type cues to favor: page types "2012 season page", "coach bio", "team roster", "university athletics page"
- Date cue to anchor year: "2012" combined with team name to prefer that season page
- Cross-phrase anchors to encourage co-occurrence: pair "Paul Winters" + "Wayne State University", and "2012 Wayne State Warriors" + "represented Wayne State University"
- Promote canonical institution name variants: "Wayne State University", "Wayne State", "Wayne State Warriors football"

REMOVE_OR_AVOID:
- De-emphasize noise tokens and pages: "Tom Adams Field", "GLIAC", "Division II", "stadium", and pages for other seasons (2011, 2016, 2017, 2008)
- Avoid over-weighting coach-tenure numbers and prior positions (e.g., "7th year", "13th/14th") that pull unrelated historical pages
- Suppress broad program-history or conference pages that don't include a short explicit affiliation line

QUERY_SHAPE:
- Emit compact, phrase-focused retrieval signals (not a single final query): short BM25-style clauses that pair entity + affiliation phrase or entity + type cue, e.g. [entity token] + ["represented Wayne State University"] or [entity token] + [type cue]
- Generate 2–3 short hits per entity: one targeting the 2012 season page (team name + 2012 + "represented Wayne State University" / "season"), one targeting the coach bio (Paul Winters + "head coach" + "Wayne State University"), and one targeting the canonical program/university athletics page (Wayne State Warriors + "Wayne State University")

...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter3_split2 -> Rstar_target

step: 3
from: Rmid_iter3_split2
to: Rstar_target
pgrad: TRIGGER:
Local step 3 — the question asks for the shared institution between "2012 Wayne State Warriors football team" and "Paul Winters"; current retrieval is too broad and should be tightened toward canonical team and coach pages.

KEEP:
- Preserve intent to fetch the canonical pages for the 2012 team and the coach bio.
- Keep anchors: "2012 Wayne State Warriors football team", "Paul Winters", "Wayne State University", "Wayne State Warriors football".
- Keep bridge clues: "head coach", "represented Wayne State University".
- Preserve preference for short, entity-focused queries rather than long natural-language questions.

ADD_OR_RESTORE:
- Add exact-title and disambiguated anchors: "Paul Winters (American football)", "2012 Wayne State Warriors football team".
- Add institution alias matches: "Wayne State University", "Wayne State Warriors".
- Add date/type cues: include year token "2012" and type token "team", and role token "head coach".
- Add ordered retrieval behavior: 1) target the 2012 team page (season title) 2) target the Paul Winters coach bio page 3) fallback to the Wayne State University/team program page for a concise affiliation line.
- Add BM25-friendly two-term shapes combining entity + institution (e.g., EntityName + Wayne State University) and title-only lookups to surface canonical pages.

REMOVE_OR_AVOID:
- Avoid season-noise and variant-year pages: "2011", "2016", "2017", "2008" season pages.
- Avoid venue/stadium and conference noise: "Tom Adams Field", "GLIAC", "NCAA Division II".
- Avoid coach-tenure counts, prior-position lists, and other biographical noise that distracts from the single-line affiliation.
- Avoid long narrative queries or queries that prioritize conference/venue over institution name.

QUERY_SHAPE:
- Prefer exact-title or short-phrase BM25 queries, executed in this order:
  1) title-style lookup: "2012 Wayne State Warriors football team" (season page)
  2) title-style lookup: "Paul Winters (American football)" or "Paul Winters Wayne State"
  3) short entity+institution phrase fallback: "Paul Winters Wayne State University" OR "Wayne State Warriors Wayne State Unive
...[truncated]

---

### 169__split0__seg0__feedback__right
- idx: 169
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.84
- why_larger: Segment A introduces a distinct two‑phase retrieval behavior plus explicit BM25 phrase‑weighting and document‑type promotion (authority/source filters, elevation of filmography formatting) that materially change query-generation and ranking behavior beyond the mainly additive, surface‑level constraints in B (dates, synonyms, and similar conjunctive query templates).

#### Question
What movie did "the king of cool" play in with Bud Ekins as his stunt double?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
Focus retrieval from broad "stunt" topic pages toward short, authoritative film‑credit statements that explicitly link Bud Ekins to Steve McQueen on The Great Escape.

KEEP:
- Anchors: Bud Ekins; Steve McQueen (alias: "The King of Cool"); The Great Escape; Bullitt (as a candidate to verify).
- Bridge clues: motorcycle stunt / famous motorcycle jump; stunt double credit; stunt credits in filmographies/IMDb; Stuntmen's Hall of Fame / obituary / biography entries.
- Expected evidence type: short biographical or film‑credit sentences explicitly stating Ekins doubled McQueen.
- Preserve intent to resolve whether Bullitt includes a doubling credit.

ADD_OR_RESTORE:
- Alias mapping: "The King of Cool" → Steve McQueen; include actor name variants ("Steve McQueen", "McQueen").
- Date/type cues: add film year ("The Great Escape" 1963), Bud Ekins dates (May 11, 1930 – Oct 6, 2007) for obituary/biography anchors.
- Role phrasing and synonyms to prioritize: "stunt double", "doubled for", "served as McQueen’s stunt double", "performed the motorcycle jump", "who did the motorcycle jump".
- Source/type filters and cues: IMDb filmography line, BFI entry, obituary headline, "Stuntmen's Hall of Fame" page, film credits/production notes.
- Restore narrow conjunctive phrasing that forces co‑occurrence of actor + stunt relation + film (with optional year).

REMOVE_OR_AVOID:
- Generic/ambiguous pages titled only "Stunt", "Stunt coordinator", or broad motorcycle‑riding pages.
- Irrelevant stuntmen noise: Butch Laswell, Corey Scott, Todd Bryant, Dave Ekins (unless explicitly linked to McQueen/Ekins credit).
- Equipment/vehicle pages (e.g., Triumph TR6 Trophy) and general "motorcycle stunt riding" sites that lack film‑credit sentences.
- Documents that list films without an explicit "doubled" / "stunt credit" phrase for Ekins.

QUERY_SHAPE:
- Behavior templates (not final queries): prioritize short conjunctive phrases that must contain anchor + role + film, e.g.
  - [Bud Ekins] AND [Steve McQueen|The King of Cool] AND [The Great Escape (1963)] AND ["stunt double" OR "doubled for" OR "performed the motorcycle jump" OR "who did the mot
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
When validating whether Bud Ekins served as Steve McQueen’s stunt double on The Great Escape (and disambiguating any Bullitt doubling claim) at step 1.

KEEP:
- Anchors: "Bud Ekins", "Steve McQueen" (alias: "The King of Cool"), "The Great Escape", "Bullitt".
- Retrieval focus: narrow, authoritative credit-confirmation (obituaries, reputable biographies, film-credit databases, Hall-of-Fame entries).
- Bridge clues: phrases like "stunt double for Steve McQueen", "performed the motorcycle jump", "credited as stuntman in filmography / IMDb / BFI".
- Expected evidence type: short, explicit credit statements (biographical lines, obituary sentences, filmography entries).

ADD_OR_RESTORE:
- Alias mapping: include "The King of Cool" -> Steve McQueen as alternate anchor tokens.
- Type cues and date anchors: add document types "obituary" (2007), "biography", "filmography", "Hall of Fame entry".
- Source filters / authority cues: prefer NYT, The Hollywood Reporter, IMDb, BFI, Stuntmen's Hall of Fame, major obituaries, reputable biographies — boost these in retrieval weighting.
- Two-phase behavior: first pass focus on exact-credit phrase for The Great Escape; second pass substitute Bullitt to resolve ambiguity.
- BM25-relevant phrase weighting: prioritize conjunctive exact-phrase matches combining actor + "stunt double" + film title; favor short sentences containing verbs like "served as", "doubled for", "was the stunt double for".
- Restore avoidance of generic pages by explicitly elevating pages with film-credit formatting (filmography tables, obituary ledes).

REMOVE_OR_AVOID:
- Noisy tokens and distractions: "Triumph TR6 Trophy", "Dave Ekins", motorcycling forums, fan pages, generic "stunt" or "stunt coordinator" pages without film-credit lines.
- Broad, topic-only pages about motorcycles or stunt riding that lack explicit film-credit statements.

QUERY_SHAPE:
Behavioral pattern (not a final query): 
- Conjoin exact-phrase segments: [actor-token OR alias] + ["stunt double" OR "doubled for" OR "served as stunt double"] + [film title]. 
- Run site/type-filtered passes that prioritize obituary/biography/filmo
...[truncated]

---

### 169__split3__seg2__feedback__right
- idx: 169
- split_iter: 3
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.79
- why_larger: Segment A prescribes more concrete, behavior-changing instructions (explicit query templates, negative/noise operators, a targeted follow-up slot for Bullitt, and a restore of authoritative-credit priority). These add new, specific query-shape and retrieval-prioritization constraints beyond the higher-level guidance in B, so A demands a larger semantic change to the generator.

#### Question
What movie did "the king of cool" play in with Bud Ekins as his stunt double?

#### Full-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter1_split0

step: 2
from: Rmid_iter3_split1
to: Rmid_iter1_split0
pgrad: TRIGGER:
Shift the local retrieval step from exploratory secondary-source signals toward authoritative credit-confirmation for Bud Ekins as Steve McQueen’s stunt double (emphasize explicit credit language and primary film-credit sources; still check Bullitt but as a narrow credit-resolution task).

KEEP:
- Anchors: Bud Ekins; Steve McQueen ("The King of Cool"); The Great Escape; "motorcycle jump" / motorcycle stunt.
- Bridge clues to preserve: phrases naming Ekins in connection with The Great Escape; obituary / Hall-of-Fame language crediting a famous motorcycle stunt.
- Exploratory caution: treat popular mentions of Bullitt as a signal to verify, not as proof.

ADD_OR_RESTORE:
- Add explicit type cues and source targets: "stunt double", "credited as stuntman", obituary, Stuntmen's Hall of Fame entry, filmography, IMDb, BFI, NYT/THR obituaries, reputable film-history essays.
- Add aliases and date cues to disambiguate: "Steve McQueen" ("The King of Cool"); Bud Ekins (May 11, 1930 – October 6, 2007).
- Bridge clues to add: exact-credit phrasing such as "stunt double for Steve McQueen", "performed the motorcycle jump", "credited in [film] credits".
- Instructional behavior: prioritize exact-phrase matches and primary credit databases and authoritative outlets before accepting secondary mentions; explicitly query filmography/credit pages for both The Great Escape and Bullitt.

REMOVE_OR_AVOID:
- Avoid noise: Triumph TR6 / motorcycle-spec pages, motoring-forum posts, unsourced fan claims, generic "stunt" pages, unrelated riders (e.g., Dave Ekins) unless they explicitly confirm credits.
- Avoid broad exploratory queries that return general motorcycling history rather than explicit credit language.

QUERY_SHAPE:
- First pass: targeted exact-phrase checks in authoritative outlets for explicit-credit language (seek lines like "Bud Ekins" + "stunt double" + "The Great Escape" or "performed the motorcycle jump" on obituary/Hall-of-Fame/major newspaper/film-history sites).
- Second pass: narrow primary-credit verification in film-credit databases and filmography pages (IMDb, BFI, official film-credit listings) fo
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter4_split2 -> Rmid_iter1_split0

step: 3
from: Rmid_iter4_split2
to: Rmid_iter1_split0
pgrad: TRIGGER:
narrow authoritative-credit check: explicit "stunt double" phrasing + resolve Bullitt ambiguity

KEEP:
- Anchors: "Bud Ekins"; "Steve McQueen" (alias: "The King of Cool"); "The Great Escape"; "motorcycle jump"/"motorcycle stunt"
- Source targets: IMDb, BFI, TCM, major obituaries (NYT, Hollywood Reporter), Stuntmen's Hall of Fame
- Approach: run exact-phrase/site-filter lookups and short corroborating statements rather than broad background pages

ADD_OR_RESTORE:
- Add explicit phrase matching for "stunt double" + principal actor: e.g., include tokens "stunt double" and "Steve McQueen" together with "Bud Ekins" and "The Great Escape"
- Restore priority for authoritative-credit-confirmation: prioritize obituaries, Hall-of-Fame pages, established film-history articles and the cast/crew credit pages (IMDb cast & crew, BFI/TCM film pages)
- Add a targeted follow-up slot to resolve Bullitt: search "Bud Ekins" + "Bullitt" + ("stunt" OR "stunt double" OR "credited")
- Add type cues and date/biographical anchors to raise precision: include Ekins dates "1930" "2007" and phrase "obituary" or "Hall of Fame" in queries
- Add explicit instruction to seek original credit language (e.g., "credited as stunt" or "credited as stunt double" in filmography/obit copy)

REMOVE_OR_AVOID:
- Avoid noisy/topical pages: motorcycle-spec articles, fan forums, unsourced blogs, general 'stunt' pages without film-credit lines
- Avoid non-authoritative phrasing that treats "Bullitt" appearance as confirmation (do not treat a film-listing alone as proof of doubling)
- Deprioritize generic keyword-only searches for "stunt" or "motorcycle" that lack actor-credit context

QUERY_SHAPE:
- Templates (behavioral; not final queries):
  1) exact-phrase + site filter for authoritative outlets: ["\"Bud Ekins\" \"stunt double\" \"Steve McQueen\""] + site:nytimes.com OR site:hollywoodreporter.com OR site:stuntmenshalloffame.org
  2) filmography credit check: ["\"Bud Ekins\" \"The Great Escape\" \"stunt\""] + site:imdb.com OR site:bfi.org.uk OR site:tcm.com; look for wording "credited" or "stunt double"
  3) ambiguity resolution for Bullitt:
...[truncated]

---

### 180__split1__seg1__feedback__right
- idx: 180
- split_iter: 1
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.86
- why_larger: Segment A imposes stronger, more specific semantic shifts: move retrieval from band/discography scope to album-level authoritative fields, require extracting a full day/month/year (not just year), prefer original-market first-press dates, and add specific high-authority sources and fallback behavior. These changes alter the target evidence family and the answer granularity much more than B's mainly procedural chaining and token tweaks.

#### Question
What is the date of released for the eleventh studio album of the highest-selling heavy metal group from Canada?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
When step 1 still only identifies the likely target band (Annihilator) and the 11th studio album title is unconfirmed — move from “confirm album ordinal/title” toward also obtaining the album’s official release date. Trigger when discography checks return album names but no explicit release-date line.

KEEP:
- Preserve the current focus on authoritative discographies and studio-only ordering:
  - Anchors: "Annihilator discography", "studio albums only (exclude EPs/compilations/live)", "ordinal position: 11th", "album title corresponding to 11th entry"
  - Bridge clues: prefer pages that state "X is the nth studio album by Annihilator" or show a chronological studio-albums list
  - Expected evidence: band/discography page or album page that confirms the 11th album title

ADD_OR_RESTORE:
- After confirming the band (alias cue: "highest-selling heavy metal group from Canada" → Annihilator), immediately chain to a date-focused retrieval for that confirmed album title:
  - New anchors for hop2: "Annihilator (band)", "Annihilator discography", "<Confirmed Album Title> release date", "released", "release date day month year", "label/region"
  - Bridge clues: open the album page or discography entry that lists the album and read the line like "Released: 12 March 2002" or lead sentence "X is the 11th studio album…released on <date>"
  - Type cues: prefer sources that format dates explicitly (Wikipedia album page, official band site, record label page, MusicBrainz, AllMusic)
  - Alias and noise tokens: include "highest-selling Canadian heavy metal band", "Annihilator discography", album-title variants (alternate spellings, regional titles)
  - Retrieval behavior: first confirm album title, then immediately issue a second subquery scoped to that album for its official release date (day/month/year and region/label if available)

REMOVE_OR_AVOID:
- Avoid pages and tokens that cause ordinal confusion or irrelevant noise:
  - Exclude EPs, compilations, live albums, reissues, deluxe-edition pages when counting studio albums
  - Avoid unrelated Canadian metal acts (e.g., Thor) and general music news lists that lack
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter2_split1 -> Rstar_target

step: 2
from: Rmid_iter2_split1
to: Rstar_target
pgrad: TRIGGER:
Confirmed band = Annihilator and 11th-album title + release year identified in prior hop.

KEEP:
- Maintain the band identity confirmation step (Annihilator) and the validated 11th-album title and release year.
- Keep authoritative sources list: band page (Wikipedia lead / official site), discography listing, album page stub/infobox.
- Preserve the ordinal-check behavior (use discography or album page text that states "Nth studio album").

ADD_OR_RESTORE:
- Add an explicit step to extract the official full release date (day/month/year) for that 11th studio album from high-authority album-level sources: album infobox, release-history section, label press release, official band announcement, or major music databases (AllMusic, Discogs, MusicBrainz, Metal Archives).
- Anchor on BM25-relevant tokens when searching: "<Album Title>", "Annihilator", "released", "release date", "infobox", "release history", "label", "press release".
- Include common aliases/stylizations of the album title and the release year (e.g., alternate punctuation, subtitle, year in parentheses) to disambiguate.
- If multiple regional dates appear, prefer the original-market first-press release date (note region/label) and capture the primary day/month/year cited by authoritative sources.
- Restore discography-as-source fallback: if the album page lacks day/month, query the discography entry and linked citations for the album's release date.

REMOVE_OR_AVOID:
- Avoid extracting only the year (no partial-date stops); do not stop at year-only sources.
- Avoid counting or listing pages that mix compilations, live albums, reissues, or boxed sets with studio albums; ignore pages that do not clearly label "studio album" or the album's ordinal.
- Avoid low-authority fan forums, unsourced listicles, and unrelated Canadian acts (e.g., Thor, Anvil) that may appear in results.
- Avoid regional reissue/remaster dates unless the original-release date cannot be confirmed from primary sources.

QUERY_SHAPE:
- Two-step retrieval behavior (preserve step order):
  1) Open the confirmed album page / discography entry already found to re-check ordinal 
...[truncated]

---

### 180__split2__seg2__feedback__right
- idx: 180
- split_iter: 2
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: Segment A requires a broader semantic change: it adds band-identity confirmation and discography-ordinal steps, introduces new entity anchors (band page, discography, album aliases, catalogue numbers), expands targeted database checks, and re-centers the retrieval pipeline from album-centric to identification→verification→evidence-assembly. B is narrower—it assumes the band and album are known and only tightens date-extraction steps.

#### Question
What is the date of released for the eleventh studio album of the highest-selling heavy metal group from Canada?

#### Full-edge feedback
- edge: Rmid_iter2_split1 -> Rstar_target

step: 2
from: Rmid_iter2_split1
to: Rstar_target
pgrad: TRIGGER:
Confirmed band = Annihilator and 11th-album title + release year identified in prior hop.

KEEP:
- Maintain the band identity confirmation step (Annihilator) and the validated 11th-album title and release year.
- Keep authoritative sources list: band page (Wikipedia lead / official site), discography listing, album page stub/infobox.
- Preserve the ordinal-check behavior (use discography or album page text that states "Nth studio album").

ADD_OR_RESTORE:
- Add an explicit step to extract the official full release date (day/month/year) for that 11th studio album from high-authority album-level sources: album infobox, release-history section, label press release, official band announcement, or major music databases (AllMusic, Discogs, MusicBrainz, Metal Archives).
- Anchor on BM25-relevant tokens when searching: "<Album Title>", "Annihilator", "released", "release date", "infobox", "release history", "label", "press release".
- Include common aliases/stylizations of the album title and the release year (e.g., alternate punctuation, subtitle, year in parentheses) to disambiguate.
- If multiple regional dates appear, prefer the original-market first-press release date (note region/label) and capture the primary day/month/year cited by authoritative sources.
- Restore discography-as-source fallback: if the album page lacks day/month, query the discography entry and linked citations for the album's release date.

REMOVE_OR_AVOID:
- Avoid extracting only the year (no partial-date stops); do not stop at year-only sources.
- Avoid counting or listing pages that mix compilations, live albums, reissues, or boxed sets with studio albums; ignore pages that do not clearly label "studio album" or the album's ordinal.
- Avoid low-authority fan forums, unsourced listicles, and unrelated Canadian acts (e.g., Thor, Anvil) that may appear in results.
- Avoid regional reissue/remaster dates unless the original-release date cannot be confirmed from primary sources.

QUERY_SHAPE:
- Two-step retrieval behavior (preserve step order):
  1) Open the confirmed album page / discography entry already found to re-check ordinal 
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter3_split2 -> Rstar_target

step: 3
from: Rmid_iter3_split2
to: Rstar_target
pgrad: TRIGGER:
When the supplied passages lack a named band or ordinal mapping but the summary suggests "highest-selling heavy metal group from Canada" (likely Annihilator) and the task requires the 11th studio-album release date.

KEEP:
- Preserve the R_left ordering: (A) once the target album name is known, open the album's main page and capture the infobox release field and its citation; (B) collect official band/label announcement pages; (C) check major music databases (Discogs, AllMusic, MusicBrainz) and reputable press reviews; (D) note region-specific release entries and annotate source provenance for each candidate date.
- Anchors to retain: "album page infobox", "official band/label announcement", "Discogs", "AllMusic", "MusicBrainz", "region-specific release".
- Expected evidence: candidate date entries (day/month/year or month/year) tied to source URLs and regional qualifiers.

ADD_OR_RESTORE:
- Prepend identity-and-ordinal steps: confirm band identity using band-page anchors and authoritative summaries (e.g., search for "Annihilator" with the phrase "highest‑selling Canadian heavy metal" or "Canada's best‑selling heavy metal band").
- Add an explicit discography-ordinal step: open "Annihilator discography" or the band page's "Studio albums" section to enumerate studio albums in release order and pick the 11th entry (capture the album title and any alternate/alias titles and original release year).
- Add alias and title-normalization: record alternate album spellings, regional title variants, and catalogue numbers to match database entries (e.g., alternate transliterations, punctuation, or parenthetical subtitles).
- Add targeted database checks after album-id: query "<Album Title> release date site:allmusic.com" and site:discogs.com and site:musicbrainz.org; also query "<Album Title> press release" and "<Album Title> site:annihilatormetal.com" (band/label official site).
- Add type cues: label the collected dates by source type (infobox citation, official press release, database release-version, contemporaneous review) and tag whether each is "original release", "regional release", or "reissue/remaste
...[truncated]

---

### 180__split3__seg2__feedback__right
- idx: 180
- split_iter: 3
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.88
- why_larger: Segment A prescribes a more extensive semantic shift: it not only directs collecting date candidates and provenance but adds stricter metadata-linking (catalog numbers, release-entry IDs), explicit capture of every quoted date string, region/edition tying, noise-suppression filters, and concrete BM25 query templates — changing both what is retrieved and how queries are formed.

#### Question
What is the date of released for the eleventh studio album of the highest-selling heavy metal group from Canada?

#### Full-edge feedback
- edge: Rmid_iter2_split1 -> Rmid_iter3_split2

step: 2
from: Rmid_iter2_split1
to: Rmid_iter3_split2
pgrad: TRIGGER:
Confirmation from prior step that the target band is Annihilator (or an authoritative source equating "highest‑selling Canadian heavy metal group" to that band) and that the 11th studio‑album title and its release year have been identified/saved.

KEEP:
- Band canonical name (Annihilator) and any verified aliases.
- The identified 11th studio‑album title and the noted release year.
- Saved album page URL(s) or record ID(s) (do not extract day/month yet).
- The constraint to avoid picking a final canonical date at this step.

ADD_OR_RESTORE:
- Open the album's primary article/page and extract the infobox "Released" field plus its citation URL.
- Fetch the band's official site / label press release pages mentioning the album and copy the announcement date and source URL.
- Query major music databases for versioned releases: Discogs release entries (catalogue number, regional pressing), MusicBrainz release groups/relations, AllMusic album page — capture any listed full release dates and their source links.
- Collect region qualifiers for each date candidate (e.g., Canada, Europe, Japan) and note which source asserts each.
- Record differences between original-release entries and later reissues/remasters; tag entries as "original" vs "reissue/deluxe".
- Preserve each candidate date together with its citation URL and a one‑line provenance note (site name, page title, region).
- Restore search for contemporary press/review dates (magazine archive lines or press-kit PDFs) that corroborate a launch day.

REMOVE_OR_AVOID:
- Do not re-run band‑identity confirmation searches or re-fetch general discography lists already used.
- Avoid fan forums, unsourced wiki edits, social posts, and pages that list only a year without citation.
- Exclude pages clearly about reissues, remasters, compilations, box sets (unless they explicitly state original-release day and are authoritative).
- Ignore aggregated lists that mix studio/live/compilation without explicit ordinal labeling (to prevent miscounting).

QUERY_SHAPE:
- Step 1 (album page): open "AlbumTitle" + site:wikipedia.org OR "AlbumTitle" album page — extract 
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter4_split2 -> Rmid_iter3_split2

step: 3
from: Rmid_iter4_split2
to: Rmid_iter3_split2
pgrad: TRIGGER:
After step 3 confirms the band identity and exact 11th-album title (album title, label and catalog identifiers captured) — expand retrieval to collect explicit release-date candidates and their source provenance for that album.

KEEP:
- Open the album's primary page(s) first (Wikipedia album article / band's official discography entry) and keep the exact album title-string as displayed and the infobox/label/catalog metadata already recorded.
- Retain captured authoritative URLs: album article URL, band/label press or discography URL, and identified Discogs/MusicBrainz/AllMusic entries (catalog numbers, release-version identifiers, region tags).
- Preserve notes about region-of-first-release and edition names (original pressing vs reissue) and the order of which edition appears original.

ADD_OR_RESTORE:
- Extract every explicitly stated release date string (full day/month/year or month/year) shown on those primary pages and record the exact quoted text plus its citation URL and the paragraph/infobox context.
- Open and record the release-date fields and the release-entry IDs on major databases (Discogs release page, MusicBrainz release, AllMusic entry) and capture the date field, catalog number match, and region tag for each release-version.
- Visit the band's official/label press announcement or archive page and capture the precise phrasing (e.g., "released on 12 March 2003", "released through [label] on [date]") and the announcement URL.
- Search for contemporary press/review pages (music magazines, press kits) that reference a release day and capture the quoted date and source URL.
- For each date candidate, save: (1) exact quoted date string, (2) source type (infobox citation / label press / Discogs / MusicBrainz / AllMusic / press review), (3) region/edition qualifier (Canada/Europe/Japan/original pressing vs reissue), and (4) the matching catalog number or release ID to tie versions together.
- Note and tag any discrepancies (different day values across sources) without resolving them; flag reissue/deluxe dates as such.

REMOVE_OR_AVOID:
- Do not treat reissue/remaster/deluxe-edition dat
...[truncated]

---

### 227__split0__seg0__feedback__right
- idx: 227
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.77
- why_larger: Segment A prescribes a more substantial semantic shift: it adds explicit character and publisher anchors (Quicksilver / Pietro Maximoff / Marvel Comics), enforces a two-hop actor→character then character→publisher retrieval flow, introduces cross-source exact-match matching and film-year disambiguation, and explicitly removes the prior prohibition on publisher pages. These changes require re-centering retrieval targets and the overall query workflow more than B's token/verb and preference refinements.

#### Question
Evan Peters had a role as the fictional superhero from comic books by what publisher?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
Step 0 — actor name present in the local context and retrieval returned a character page ("Quicksilver (comics)") but no explicit actor→character sentence; apply when actor+character ambiguity remains.

KEEP:
- Anchors: "Evan Peters", "Quicksilver", "Pietro Maximoff", "X‑Men: Days of Future Past", "X‑Men: Apocalypse", "Marvel Comics".
- Retrieval goal: surface short authoritative lead/filmography lines that link the actor name to the character name and a character page that names the publisher.
- Expected evidence type: concise declarative sentences (page leads, filmography credits, cast lists).

ADD_OR_RESTORE:
- Role-verbs and credit cues: "portrayed", "portrayed as", "credited as", "played", "cast as".
- Alias token: "Pietro Maximoff" (include parentheses/alias forms).
- Film-year anchors to disambiguate film roles: "2014" (Days of Future Past), "2016" (Apocalypse).
- Source-type cues: "Wikipedia lead", "filmography", "cast", "IMDb", "character page", "lead sentence".
- Publisher cue token: "Marvel Comics" tied to the character page.
- Retrieval preference: prefer pages whose first lines contain actor+role or character+publisher exact-token matches.

REMOVE_OR_AVOID:
- Series-level and event noise: "All-New X-Men", "Classic X-Men", "Son of M", "Ultimatum", "Random".
- Peripheral characters/family pages: "Luna Maximoff", "Scarlet Witch", "New Canaanites".
- Non-content pages: "disambiguation" pages.
- Long natural-language question phrasing or broad topical pages that dilute exact-name overlap.

QUERY_SHAPE:
Short, token-dense entity-to-entity patterns (3–6 tokens) combining:
- [actor name] + [role-verb] + [character name / alias] OR
- [actor name] + [character name] + [film title or year] OR
- [character name] + [publisher cue] + [character page indicator]
Prefer exact-title matches and lead/filmography lines rather than long narrative queries.

WHY_THIS_MOVES_RETRIEVAL:
Shifts scoring from broad topical matches to high BM25 token overlap on the specific actor→character relation and the character→publisher statement. Adding role-verbs, alias tokens, film-title/year anchors and "lead/filmography" type cues
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
Evan Peters role question (step 1): actor->character link needed to tie the credited role to a comic-book character and then to that character's publisher.

KEEP:
- Anchors: "Evan Peters", "Quicksilver", "Pietro Maximoff", "X‑Men: Days of Future Past", "X‑Men: Apocalypse", "filmography / cast list"
- Bridge cues to preserve: lead-sentence or filmography lines on an Evan Peters page that list Quicksilver; cast lists/credits for the two X‑Men films; reputable databases/news articles stating "Evan Peters as Quicksilver"
- Expected evidence type: short authoritative credit lines (filmography entries, cast credits, studio or news lines)
- Avoid: fan wikis, forum speculation, unrelated biographical details

ADD_OR_RESTORE:
- New BM25-relevant anchors: "Quicksilver (comics)", "Quicksilver (Pietro Maximoff)", "Marvel Comics", "Quicksilver publisher"
- Alias and type cues: include the alias form "Pietro Maximoff / Quicksilver (comics)", and type cue "comic-book superhero"
- Bridge clues to add: lead sentence from "Quicksilver (comics)" that includes "published by Marvel Comics"; short sentence linking the character name (Quicksilver / Pietro Maximoff) to Marvel Comics; cross-source matches where an Evan Peters credit names the same character string used on the comics page
- Date/film cues to anchor exact-match (reduce ambiguity): film years "2014" (Days of Future Past) and "2016" (Apocalypse) as context tokens to narrow to the film portrayal

REMOVE_OR_AVOID:
- Remove the earlier constraint to "intentionally avoid comic-book publisher pages" so publisher-confirmation pages are allowed
- Avoid noisy/distracting pages: Luna Maximoff / Scarlet Witch family pages, event/comic issues (Son of M, Ultimatum), minor character pages (Random), long historical comic analyses, and fan-edited content
- Avoid actor biography sections that do not mention the Quicksilver role or film cast credits

QUERY_SHAPE:
Preserve order as two short BM25-style hops (behavioral, not a final query):
1) Narrow actor→character exact-name hit: short tokenized actor+role/cast queries (e.g., actor name + character alias + film title/year or "
...[truncated]

---

### 247__split1__seg0__feedback__right
- idx: 247
- split_iter: 1
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.83
- why_larger: Segment A imposes stronger, more specific semantic constraints: it re-centers retrieval on local Ghana outlets and activist accounts, adds concrete surface-pattern matching (literal '#' tokens, quoted petition titles, Change.org/facebook/twitter URL patterns and site:gh), and prescribes tighter date/alias handling and noise removal — changes that materially alter which anchors and surface forms the query generator must preserve and prioritize.

#### Question
What is another name for the online protest that opposed the transfer of ex-detainees from Guantanamo Bay in 2016?

#### Full-edge feedback
- edge: R0_base -> Rmid_iter1_split0

step: 0
from: R0_base
to: Rmid_iter1_split0
pgrad: TRIGGER:
Current retrieval returns general Gitmo/detainee lists and news about the January 2016 Ghana transfer but no quoted online campaign name, hashtag, or petition label.

KEEP:
- Anchor actor tokens: OccupyGhana (also "Occupy Ghana"), New Patriotic Party, Ghana.
- Event/date anchors: January 2016, 2016, Ghana transfer, Guantanamo, Gitmo, Yemeni ex-detainees.
- Retrieval focus phrasing: "locate news or social‑media mentions" that explicitly name an online protest/campaign.
- Bridge clues to retain: online campaign, hashtag, e‑petition, social media protest, named online protest, coverage of public reaction.

ADD_OR_RESTORE:
- Boost signals for media/type tokens: include explicit cues for "hashtag", "#", "petition", "e‑petition", "Facebook", "Twitter", "tweet", "campaign", "petition to", "online petition".
- Favor quoted labels and embeds: prefer documents that reproduce a quoted token (e.g., " #... ", "petition: '...'", tweet embeds).
- Alias and token variants: allow "Guantanamo" OR "Gitmo"; "OccupyGhana" OR "Occupy Ghana"; include substring/wildcard hashtag patterns (hashtag stems) rather than one exact tag.
- Narrow source/time scope: prioritize contemporary news/social‑media coverage circa Jan 2016 and immediate follow‑up reporting.
- Retrieval behavior: boost documents that pair an actor anchor (OccupyGhana/NPP) with a campaign-type token (hashtag/petition/Facebook/Twitter) in the same sentence or quoted excerpt.

REMOVE_OR_AVOID:
- Demote list/timeline/biography pages: "List of Yemeni detainees", timelines, individual detainee bios (Obaidullah, Inayatullah), hunger strike histories.
- Avoid historical/general Gitmo summaries and non‑campaign blog posts that lack embedded social posts or quoted campaign names.
- Filter out broad Guantanamo release roundups that do not quote campaign labels or social‑media tokens.

QUERY_SHAPE:
Construct a BM25‑style query that (1) requires an event + actor anchor and (2) boosts documents containing social‑media/campaign type tokens.
- Required proximity: (OccupyGhana OR "Occupy Ghana" OR "New Patriotic Party" OR NPP) near (Ghana OR Guantanamo OR Gitmo) near (Jan 2016 OR
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter2_split0 -> Rmid_iter1_split0

step: 1
from: Rmid_iter2_split0
to: Rmid_iter1_split0
pgrad: TRIGGER:
When local Ghana coverage or OccupyGhana/NPP social posts are present for the Jan 2016 Gitmo transfer but no campaign name appears in top hits.

KEEP:
- Retrieval focus: stay limited to Ghana‑focused news outlets and OccupyGhana / NPP social pages covering the January 2016 transfer of Yemeni ex‑detainees from Guantanamo.
- Anchors: OccupyGhana (also allow "Occupy Ghana"), New Patriotic Party (NPP), GhanaWeb, JoyOnline, Citi Newsroom, Graphic Online, Guantanamo/Gitmo, January 2016.
- Bridge clues to preserve: petition, Change.org, Facebook campaign, tweet, hashtag, online petition link, press release linking to social campaign.
- Noisy_or_distracting_clues to keep filtering: deprioritize international summaries that lack local campaign details.
- Expected evidence type: a short reproduced campaign identifier in local copy (quoted hashtag, petition title, embedded tweet or a visible change.org/facebook link).
- Query shape implication: constrain to Ghana domains and activist accounts; combine event terms with campaign tokens.

ADD_OR_RESTORE:
- Add explicit surface patterns for campaign identifiers: search for literal '#' tokens and substring hashtag patterns (allow wildcard substring matches), quoted petition titles (look for quotation marks around short phrases), and URL patterns (change.org/p/ or change.org/), facebook.com/ and twitter.com/ or "via @".
- Add alias handling: both "OccupyGhana" and "Occupy Ghana"; allow "NPP" and "New Patriotic Party".
- Add date anchoring: force 2016 OR "January 2016" near campaign tokens.
- Add phrasing cues that often surround campaign names: "petition to", "signed", "call to", "use #", "hashtag", "campaign titled", "petition on Change.org", "Facebook campaign".
- Restore focus on embedded social excerpts: look for words like "tweeted", "posted", "embed", "via Twitter", or inline screenshots described in article copy.

REMOVE_OR_AVOID:
- Remove or downweight broad Gitmo background signals: detainee lists/biographies, historical analyses of Guantanamo releases, general timelines of detainee transfers.
- Avoid opinion pieces and international summaries that re
...[truncated]

---

### 268__split0__seg0__feedback__right
- idx: 268
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.88
- why_larger: A introduces more and deeper semantic changes: explicit alias mapping for Henry Green, many new occupation candidate tokens, additional book-title identity anchors, a negative anchor to filter Joseph Henry Chesterton, and specific lead/infobox-focused query templates — all of which materially change which entities and job-types the generator must preserve/add/remove and how queries are formed.

#### Question
Between G. K. Chesterton and Henry Green, who had more diverse job experiences?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
Current retrieval mixes multiple "Henry" entities and broad OR clauses (returns Joseph Henry Chesterton and unrelated Henrys); retrieval focus is ambiguous and noisy.

KEEP:
- Anchors: "G. K. Chesterton" + Orthodoxy (1908) — writer / Christian apologist; "Joseph Henry Chesterton" + plant collector (c.1840–26 Jan 1883).
- Objective: compare occupations/job lists for two named persons (Henry Green vs G. K. Chesterton) and avoid conflation.

ADD_OR_RESTORE:
- Exact-name aliases and pen-name tokens: "Henry Vincent Yorke" ; "Henry Green (novelist)"; "Henry Green Party Going" ; "Henry Yorke biography".
- Occupation and infobox cues: add tokens "biography", "occupations", "infobox", "career", "pen name", "novelist", "journalist", "editor", "civil service" (as candidate job-type cues).
- Disambiguation cue for the similarly named figure: "Joseph Henry Chesterton plant collector dates c.1840–1883".
- Date anchors where present to increase precision: "Orthodoxy 1908".

REMOVE_OR_AVOID:
- Broad OR-chains and multi-target compound query forms that returned many unrelated Henrys.
- Noisy author/title results that dominated earlier retrievals (Henry James, Nick Tosches, Henry F. Pringle, Bill Henry, etc.).
- Any phrasing that risks conflating Joseph Henry Chesterton with "Henry Green" (avoid generic "Henry Green" alone without pen-name/alias context).

QUERY_SHAPE:
Produce short, entity-centric retrieval prompts (keep order):
1) Exact-alias + occupation cue: ["Henry Vincent Yorke" biography occupations] or ["Henry Green (novelist)" occupations infobox].
2) Exact-entity + role-list cue for comparison: ["G. K. Chesterton" biography occupations infobox Orthodoxy 1908].
3) Disambiguation check: ["Joseph Henry Chesterton" plant collector dates] .
Prefer quoted exact names, include "biography"/"occupations"/"infobox"/"pen name"/notable-work tokens to boost BM25 signal; run separately rather than as a single OR query.

WHY_THIS_MOVES_RETRIEVAL:
Shifting from a lumped OR-style query to short, exact-name + occupation/infobox prompts raises BM25 relevance for pages that list jobs and career summaries, reduces hits for unrelated Hen
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
R_left lacks an explicit Henry Green (pen name Henry Vincent Yorke) identity and occupations; current evidence only lists G. K. Chesterton (author) and Joseph Henry Chesterton (plant collector) — ambiguous comparison step ready to pivot to targeted biographical retrieval.

KEEP:
- Maintain disambiguation intent: avoid conflating Henry Green with other Henrys or Joseph Henry Chesterton.
- Preserve goal: obtain concise occupation lists to judge job diversity.
- Keep emphasis on short encyclopedic leads/infoboxes as preferred evidence type.
- Retain ordering: resolve Henry Green identity first, then augment Chesterton occupations.

ADD_OR_RESTORE:
- Add alias mapping signals: "Henry Green = Henry Vincent Yorke", "pen name", "Henry Yorke".
- Add book-title anchors as identity cues: "Party Going", other known works (to confirm novelist).
- Add occupation candidate tokens: novelist, novelist-journalist, civil servant, editor, short-story writer, teacher, literary critic, biographical dates (e.g., birth/death years) — to match infobox fields.
- Restore disambiguation-cleanup anchor: explicit "Joseph Henry Chesterton plant collector 1840 1883 James Veitch & Sons" as negative anchor to filter out similar names.
- Add Chesterton occupation expansion cues: "G. K. Chesterton occupations", "Orthodoxy 1908", "Heretics" to pull fuller role list (essayist, journalist, critic, theologian).
- Add date/type cues to favor lead paragraphs: "born", "died", "occupation(s)", "infobox", "biography".

REMOVE_OR_AVOID:
- Avoid broad disambiguation result noise: queries or pages titled only "Henry Green (disambiguation)" without context.
- Avoid non-biographical sources (book reviews, full-text novel pages, library listings) that lack concise occupation lists.
- Filter out unrelated Henrys (Henry James, Henry F. Pringle, Bill Henry) and other Joseph Henry Chesterton results.
- Avoid multi-entity queries that mix many Henrys or general "Henry biography" without pen-name or title anchors.

QUERY_SHAPE:
- Exact-entity lead/inobox shape for Henry Green: include alias + occupation tokens + title cue; e.g., templates like [Henry Vi
...[truncated]

---

## tie_or_invalid_fail (6 total, showing 6)

### 118__split2__seg1__feedback__right
- idx: 118
- split_iter: 2
- task_kind: right_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.82
- why_larger: Both segments give effectively the same semantic update: lock ambiguous titles to specific film editions (Third Person→2013, From Here to Eternity→1953), bias queries to exact-title+year anchors, target 'Starring'/'Cast' sections, extract top-billed female names (2–4), and avoid non-film or broad disambiguation noise. Differences are minor (provenance/formatting notes and wording), so neither represents a materially larger semantic change.

#### Question
What acress starred in both "Third Person" and "From Here to Eternity"?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rmid_iter2_split1

step: 1
from: Rmid_iter1_split0
to: Rmid_iter2_split1
pgrad: TRIGGER:
Step 1 — current step is performing broad title disambiguation for “Third Person” and checking which version of “From Here to Eternity” is intended.

KEEP:
- Preserve the goal of producing candidate actor sets per specific work/version (disambiguation → candidate actor lists).
- Keep use of authoritative film pages and disambiguation pages as primary sources (Wikipedia/IMDb/filmographies).
- Keep bridge clues: title + release year, lead/billed actresses, and 'starring' / cast-list sections as evidence targets.
- Keep explicit noise flags already listed (songs, books, unrelated similarly named works) so they remain deprioritized.

ADD_OR_RESTORE:
- Bias toward the single most-likely modern/main film for each ambiguous title by adding exact title+year aliases: "Third Person (2013 film)" and "From Here to Eternity (1953 film)" as primary anchors.
- Add behavior to preferentially fetch sections labeled "Starring", "Cast", or top-billed list entries on those exact-title pages and extract female performer names only.
- Restore targeted sources preference: open the title page (Wikipedia) then corroborate with IMDb cast section if needed; prefer pages where billing order is explicit.
- Add extraction constraint: return the first 2–4 top-billed female names per title (names and short role labels if present) to create compact candidate sets for intersection.
- Add alias and date cues: include common name variants (e.g., “From Here to Eternity 1953”, “Third Person 2013”) to match BM25 surface text in page headings.

REMOVE_OR_AVOID:
- Stop broad multi-year disambiguation sweeps that enumerate every work named "Third Person" (books, songs, shorts) unless 2013 is missing from top results.
- Avoid surfacing male-only cast lists, crew/production trivia, soundtrack, and unrelated remakes/adaptations (e.g., stage musical) as primary hits.
- Avoid large cast rosters beyond the top-billed performers and avoid pages that only mention titles in passing without a cast section.

QUERY_SHAPE:
- Two narrow, high-precision lookups (exact-title + year + cast cues), e.g.:
  1) [Title alias: "Third Person (2013)" OR text:
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter2_split1

step: 2
from: Rmid_iter3_split1
to: Rmid_iter2_split1
pgrad: TRIGGER:
Lock ambiguous titles to their canonical film editions — treat "Third Person" as the 2013 feature and "From Here to Eternity" as the 1953 feature for the next lookup.

KEEP:
- Preserve disambiguation check behavior (look for title pages and disambiguation markers labeled "film", "TV", "short").
- Keep focus on authoritative sources (Wikipedia/IMDb/major filmographies) and extracting explicit "Starring"/"Cast" sections.
- Keep instruction to produce compact candidate actress lists (top-billed female names) for later intersection.

ADD_OR_RESTORE:
- Bias queries toward exact-title + year aliases: prefer "Third Person (2013 film)" and "From Here to Eternity (1953 film)" as primary anchors.
- Prefer pages/sections containing the tokens "Starring", "Cast", or top-billed credits and extract the first 2–4 female names listed.
- Add bridge clues to match BM25 signals: include year tokens + "cast" or "starring" (e.g., title + "2013 cast", title + "1953 starring") and prefer pages whose titles contain the year in parentheses.
- Restore explicit exclusion rule to only consider entries labeled "film" (not "book", "song", "play", or undated short/obscure items).
- Record source title and URL for each actress list to keep provenance.

REMOVE_OR_AVOID:
- Deprioritize wide disambiguation crawling that returns books, songs, plays, or obscure festival shorts titled "Third Person".
- Avoid long full cast lists where lead billing is unclear, crew/production/trivia pages, and pages focused on remakes/miniseries unless the year cue explicitly matches the question.
- Avoid retrieving male-only billing or irrelevant production details that do not contain "Starring"/lead actress signals.

QUERY_SHAPE:
Run two narrow, high-precision lookups: one targeting the 2013 feature and one the 1953 feature. For each lookup: locate title pages whose headers include the exact title + year and the label "film", open the "Starring"/"Cast" block, and extract a short ordered list (first 2–4) of female performer names (with source title/URL). Use query terms that combine title + year + ("cast" OR "starring") and limit matches to pages 
...[truncated]

---

### 267__split3__seg0__feedback__left
- idx: 267
- split_iter: 3
- task_kind: left_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.92
- why_larger: Both segments give nearly identical semantic instructions: shift retrieval from episode/person pages to show-level credit sources for Smallville, keep the same anchors (Smallville, Alfred Gough, Miles Millar, Justin Hartley), add similar show-level phrases (created by/writing credits/main article) and avoid episode and individual staff pages. Neither introduces a materially different anchor, relation, or candidate-family change.

#### Question
Who were the writers of an American television series based on the DC Comics character Superman, which starred an American actor known for his television roles that include Fox Crane on the NBC daytime soap opera "Passions"?

#### Full-edge feedback
- edge: R0_base -> Rmid_iter3_split0

step: 0
from: R0_base
to: Rmid_iter3_split0
pgrad: TRIGGER:
When next retrieving evidence for step 0 (confirming Smallville's writers) and current results are dominated by episode pages or individual staff biographies instead of a show-level credits page.

KEEP:
Smallville; writing credits; Alfred Gough; Miles Millar; List of Smallville episodes; Justin Hartley; Oliver Queen; Fox Crane; Passions.

ADD_OR_RESTORE:
Target-type cues and phrases: "Smallville (TV series)", "created by", "developed by", "credited as creators", "writing credits", "series main article", "episode list / consolidated credits", date range "2001–2011", "creator bios", "official press release" — restore focus on show-level sources and the two creator names as primary anchors.

REMOVE_OR_AVOID:
Avoid episode-specific titles (Pilot, Finale, Tempest, Reckoning), long enumerations of secondary writers (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer), individual person profile pages when they lack series-overview context, fan wikis, actor filmography pages, and unrelated DC property or news pages.

QUERY_SHAPE:
Prefer short, show-level retrieval patterns: show title + TV-series/type cue + credit phrase + creator names + consolidated-credits source. (e.g., prioritize "Smallville (TV series)" main article, "List of Smallville episodes" credit summary, and Alfred Gough / Miles Millar bios; include "created by"/"writing credits" and optionally "2001–2011" and Justin Hartley as a casting bridge; do not enumerate many secondary writer names or episode titles.)

WHY_THIS_MOVES_RETRIEVAL:
BM25 favors documents containing exact show-title + credit phrases; emphasizing "created by"/"writing credits" and the episode-list or series main article raises scores of authoritative series-level pages and creator bios while removing episode names and many person names reduces hits on episode pages and individual staff profiles. Including Justin Hartley as a bridge preserves the actor-to-series link without dragging retrieval toward actor filmographies or plot-focused episode pages. This refocuses retrieval from scattered person/episode pages to consolidated series-level credit sources.

#### Sub-edge feedback
- edge: R0_base -> Rmid_iter4_split0

step: 0
from: R0_base
to: Rmid_iter4_split0
pgrad: TRIGGER:
Shift away from long, name- and episode-heavy hits (episode pages, individual staff bios) toward the show-level credit lines that state who "created by"/"developed by" Smallville.

KEEP:
- Anchors: Smallville, Alfred Gough, Miles Millar
- Bridge actor cues: Justin Hartley, Oliver Queen, Fox Crane, Passions
- Type cue: series-level credit / main article / writing credits

ADD_OR_RESTORE:
- Add explicit show-level phrases: "Smallville (TV series) main article", "Created by", "Developed by", "writing credits", "series overview"
- Add compact disambiguators/aliases and date: "Smallville 2001–2011", "Smallville TV series"
- Reinstate creator-bio targets (Alfred Gough bio, Miles Millar bio) as primary evidence sources
- Keep the actor only as a casting bridge term for cross-checking (Justin Hartley, Fox Crane, Passions)

REMOVE_OR_AVOID:
- Episode-level pages and plot articles (Pilot, Finale, Tempest, Reckoning)
- Long enumerations of secondary writer names that return individual person pages (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer)
- Actor filmography/fan-wiki pages that mention Smallville without explicit creator credit
- Noise tokens: full episode titles, single-episode recaps, cast-only filmography lists

QUERY_SHAPE:
Show-centric template: [Smallville OR "Smallville (TV series)"] + ( "created by" OR "developed by" OR "writing credits" OR "series overview" ) + ( Alfred Gough OR Miles Millar ) + OPTIONAL [Justin Hartley OR "Fox Crane" OR Passions] + date cue ("2001–2011") — prioritize matches in the main article or creator bios over episode/person pages.

WHY_THIS_MOVES_RETRIEVAL:
Targeting explicit credit phrases ("created by"/"writing credits") plus the show title and creator names raises BM25 weight on the Smallville main article and creator bios (where creator-credit lines appear), while deprioritizing episode recaps and scattered staff pages that the original long, name-heavy query pulled in. Keeping the actor as a secondary bridge preserves the cast link without dragging in noisy filmography or fan pages.

---

### 60__split0__seg0__feedback__right
- idx: 60
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.85
- why_larger: Both segments request nearly identical semantic changes: preserve the same anchors (HST, STS-31, Discovery), add exact-date/year tokens and mission/infobox type cues, avoid instrument/other STS pages, and shape short entity→date queries. Differences are minor phrasing/level-of-detail rather than materially different retrieval targets or relation shifts.

#### Question
The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
Step 0 — need the year the telescope that observed HD 92945 (Hubble Space Telescope) was launched into low Earth orbit.

KEEP:
- Anchor tokens: "Hubble Space Telescope", "STS-31", "Space Shuttle Discovery", "launch date".
- Retrieval focus: prefer an authoritative mission/main-article page that states launch/deployment information.
- Expectation: single-document factual statement (entity → launch year).

ADD_OR_RESTORE:
- Boost exact-date and year tokens: "24 April 1990", "25 April 1990", "1990".
- Add alias/phrases: "HST launched into low Earth orbit", "STS‑31 (deployment of HST)", "Hubble launch year", "Hubble deployment date".
- Type cues to prioritize: "NASA mission page", "Hubble main article", "STS-31 mission page", "mission summary", "launch/deployment".
- Signal to prefer documents where the date/year appears in the first paragraph or infobox (concise factual statement).

REMOVE_OR_AVOID:
- Downweight or filter out instrument- or list-focused pages: "Goddard High Resolution Spectrograph", "ACS", "NICMOS", "List of Hubble anniversary images".
- Exclude unrelated STS mission pages and similarly numbered distractions: "STS-82", "STS-103", "STS-124", "STS-400", "STS-51", "STS-109".
- Avoid generic Space Shuttle overview pages that do not mention STS-31 or HST launch year explicitly.

QUERY_SHAPE:
Short entity→attribute hits: construct compact queries that pair the telescope or mission alias with a date-type attribute, e.g. [Hubble Space Telescope] + [launch year/date], or [STS-31] + [launch date / 24 April 1990 / 1990]; favor exact-date tokens and title-level matches rather than long natural-language questions.

WHY_THIS_MOVES_RETRIEVAL:
Boosting exact-date/year tokens and explicit mission aliases increases BM25 overlap with authoritative pages that state "24 April 1990" or "1990" in the title/lead/infobox. Simultaneously filtering instrument pages and other STS mission pages removes high-scoring but irrelevant documents with shared terms, shifting retrieval probability from noisy STS/instrument results toward the HST/STS‑31 mission pages that directly contain the launch-year fact.

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
Focus retrieval on an official mission-summary page that states the HST launch year.

KEEP:
- Anchors: STS-31; Space Shuttle Discovery; Hubble Space Telescope (HST).
- Bridge clues to preserve: "STS-31 deployed HST", "launched 24 April 1990", "deployment 25 April 1990".
- Expected evidence type: concise mission-summary / infobox line on an authoritative NASA/STS-31 page that lists the launch date/year.
- Maintain short, mission-focused query intent (mission name + launch date/year).

ADD_OR_RESTORE:
- Add exact date/year tokens as anchors: "1990", "24 April 1990", "25 April 1990".
- Add aliases and identifiers: "HST", "Hubble", "Space Shuttle Discovery (OV-103)".
- Add type cues: "NASA mission summary", "mission page", "infobox / launch date".
- Add explicit orbital phrase: "launched into low Earth orbit".
- Bridge phrasing to weight: "launched into low Earth orbit in 1990", "STS-31 launch 1990", "STS-31 mission summary (NASA)".

REMOVE_OR_AVOID:
- Avoid instrument- or image-focused pages: ACS, NICMOS instrument pages, Hubble image galleries, anniversary lists.
- Avoid other STS mission pages and unrelated mission numbers (STS-82, STS-109).
- Avoid pages that focus on instrumentation or scientific results rather than mission facts (Goddard instrument pages, observation papers).

QUERY_SHAPE:
Compose a short fact-seeking search that prioritizes mission-summary pages by combining one mission identifier (STS-31 OR Space Shuttle Discovery/OV-103 OR HST) + an explicit launch token ( "launch" / "launch date" ) + a year/date token ("1990" or "24 April 1990"), and prefer results labeled as "NASA", "mission summary", or an infobox. De-emphasize results with instrument, gallery, or other STS numbers in the title/snippet.

WHY_THIS_MOVES_RETRIEVAL:
Including exact date/year tokens and mission identifiers increases BM25 overlap with authoritative mission pages; adding aliases/OV-103 and type cues (NASA, mission summary, infobox) biases ranking toward concise launch facts; excluding instrument/anniversary and other STS numbers reduces noisy matches that mention HST but not the launch-year fact. These changes ti
...[truncated]

---

### 60__split2__seg1__feedback__right
- idx: 60
- split_iter: 2
- task_kind: right_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.89
- why_larger: Both segments make nearly identical semantic changes: re-center queries on the STS-31/Discovery mission anchor, add explicit launch-date tokens, prefer mission-summary/infobox sources, and avoid instrument or generic HST history pages. Neither introduces a materially larger or different semantic instruction.

#### Question
The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

#### Full-edge feedback
- edge: Rmid_iter2_split0 -> Rmid_iter1_split0

step: 1
from: Rmid_iter2_split0
to: Rmid_iter1_split0
pgrad: TRIGGER:
shift_focus_to_STS-31_mission_page

KEEP:
- Hubble Space Telescope (entity anchor)
- preference for authoritative, concise overviews (NASA Hubble site, encyclopedia/Wikipedia)
- explicit launch-date/year as the expected evidence type (infobox or lead sentence)
- launch year 1990 (keyword to preserve BM25 weight)

ADD_OR_RESTORE:
- STS-31 (primary mission anchor)
- Space Shuttle Discovery (launch vehicle alias)
- mission summary / mission page / NASA STS-31 page (type cue)
- launch date phrasing: "24 April 1990" and deployment phrasing: "25 April 1990" (date anchors)
- page features: mission infobox, mission summary line, launch/mission log entries (evidence-type cues)
- preferred hosts: official NASA mission pages, NASA press release/mission pages, or Wikipedia "STS-31" entry (site/type anchors)
- short mission-focused terms to combine with HST: "STS-31" OR "Discovery" + "launch date" OR "mission summary"

REMOVE_OR_AVOID:
- generic HST history or anniversary retrospectives that narrate events without a concise launch line
- instrument pages (ACS, NICMOS) and scientific result pages unrelated to launch details
- other STS mission pages (STS-82, STS-109, etc.) that mention HST servicing but are not STS-31
- image galleries, blog posts, and education pages lacking a clear mission-summary/infobox

QUERY_SHAPE:
Use a short mission-centered lookup: prioritize pages whose titles or infoboxes contain "STS-31" or "Space Shuttle Discovery" and explicit launch-date language (e.g., "24 April 1990" / "1990"); target official NASA mission pages or the Wikipedia STS-31 mission-summary entry rather than broad HST overviews or instrument/result pages.

WHY_THIS_MOVES_RETRIEVAL:
By adding mission-specific anchors ("STS-31", "Discovery", "mission summary") and date phrasings while removing instrument/history noise, BM25 will favor mission pages and infobox lead lines that state the HST launch date/year. The change narrows from general HST overviews to high-signal mission records where "launch date" co-occurs directly with STS-31/Discovery, increasing precision for the year 1990 evidence.

#### Sub-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter1_split0

step: 2
from: Rmid_iter3_split1
to: Rmid_iter1_split0
pgrad: TRIGGER:
Step 2 — nudge retrieval away from general HST history leads toward mission-specific authoritative pages by injecting mission-name and precise launch-date cues.

KEEP:
- Preserve Hubble-centered entity framing ("Hubble Space Telescope history / timeline", "HST Wikipedia lead/infobox", "concise timeline or infobox entry like 'Launched …' or '1990'").
- Keep bridge phrasing that links HST to a shuttle mission in one line (e.g., "HST … deployed by STS-31 / Discovery") rather than long mission narratives.

ADD_OR_RESTORE:
- Add mission-specific anchors and aliases: "STS-31", "STS31", "Space Shuttle Discovery", "Discovery (OV-103)".
- Add explicit launch-date tokens and variants: "24 April 1990", "25 April 1990", "1990", "launched 24 April 1990", "deployment 25 April 1990".
- Add source/type cues that signal authoritative mission summaries: "NASA mission page", "STS-31 mission summary", "mission infobox", "launch date / launch year".
- Reintroduce short authoritative-page indicators: title includes "STS-31" or "Discovery" or URL host contains "nasa.gov" / "history" / "mission" or encyclopedia infobox lines.

REMOVE_OR_AVOID:
- De-emphasize instrument/science-result pages (ACS, NICMOS) and image/gallery or anniversary blog posts that mention HST but do not state launch date clearly.
- Avoid long servicing-mission pages (STS-82, STS-109) and deep technical mission logs or multi-page PDFs that dilute short mission-summary signals.
- Avoid generic HST narrative pages where the launch year is buried rather than stated in a lead/infobox.

QUERY_SHAPE:
- Shift from an entity-overview shape to a mission-centric shape: prioritize documents whose titles or first lines contain mission tokens ("STS-31", "Space Shuttle Discovery") plus explicit date tokens ("24 April 1990" or "1990") and source cues ("NASA", "mission summary", "infobox"). Favor short mission-summary pages (NASA/STS-31 or encyclopedia infobox) over long narrative or instrument pages.

WHY_THIS_MOVES_RETRIEVAL:
- Adding highly specific mission tokens (STS-31, Discovery, exact date strings) raises BM25 term overlap with mission pages and NASA summ
...[truncated]

---

### 82__split1__seg0__feedback__left
- idx: 82
- split_iter: 1
- task_kind: left_recovery
- expected: A
- predicted: tie
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.77
- why_larger: Both segments request the same substantive semantic shift: re-anchor retrieval from broad/etymology and long biographies toward the robbery article lead and short Civil‑War/Missouri definitions for a single‑word irregular‑fighter label (guerrillas/bushwhackers/partisans). Differences are minor wording and query-detail preferences, not material changes to which anchors or relations to preserve or emphasize.

#### Question
What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?

#### Full-edge feedback
- edge: R0_base -> Rmid_iter1_split0

step: 0
from: R0_base
to: Rmid_iter1_split0
pgrad: TRIGGER:
Narrow labeling focus from Revolutionary‑War etymology → Missouri/Civil‑War usage; find which one‑word label (bushwhacker / guerrilla / partisan) is used in the robbery article lead and short Civil‑War definitions.

KEEP:
- Clay County Savings Association Building (Liberty, Missouri; Feb 13, 1866)
- Jesse James
- Archie Clement
- aliases: bushwhacker(s), guerrilla(s), partisan(s)
- Missouri / Civil War / Confederate irregulars

ADD_OR_RESTORE:
- Behavior: first confirm the exact lead/first‑sentence wording on the Clay County Savings Association Building page that labels the robbers (look for the single label word and phrasing like "former Confederate ___").
- Behavior: fetch concise lead/definition paragraphs for "bushwhacker" and "guerrilla" limited to Missouri/Civil‑War usage (prefer encyclopedia leads: Britannica, Civil War dictionaries, concise history entries).
- Use BM25‑friendly anchors and cues in each lookup: "lead sentence", "definition/lead paragraph", "Missouri", "Confederate irregulars", "Feb 13, 1866", "Liberty".
- Prefer short passages or first paragraphs over long biographies or gang timelines.

REMOVE_OR_AVOID:
- Avoid Revolutionary‑War etymology searches and origin‑history threads.
- Avoid full Jesse James/James–Younger Gang biographies, long operational histories, or international uses of "partisan"/"guerrilla".
- Avoid long multi‑entity queries that combine many names/dates into one search string (causes topical drift).

QUERY_SHAPE:
- Two tight lookups, executed in order:
  1) Confirmatory lookup: open the Clay County Savings Association Building article (lead/first paragraph) and extract the one‑word label used for the robbers (check exact phrasing including "former Confederate ___" and date/place anchors: Feb 13, 1866; Liberty, Missouri).
  2) Definition lookup: fetch the lead/definition lines for "bushwhacker" and for "guerrilla" restricted to Missouri/Civil‑War context (encyclopedia or Civil War dictionary lead paragraphs that tie the term to Confederate irregulars).
- Match retrieval to short lead paragraphs and exact label tokens (singular/plural forms, hyphenation) to boost B
...[truncated]

#### Sub-edge feedback
- edge: R0_base -> Rmid_iter2_split0

step: 0
from: R0_base
to: Rmid_iter2_split0
pgrad: TRIGGER:
Narrow retrieval when results include long biographies, gang timelines, or deep etymology; instead surface a single-word irregular‑fighter label used in encyclopedic lead lines for the Feb 13, 1866 Liberty, Missouri robbery.

KEEP:
- Anchors: "Clay County Savings Association Building", "Liberty, Missouri", "Feb 13 1866", "Jesse James", "Archie Clement", "former Confederate guerrillas".
- Candidate labels/aliases: "guerrillas", "bushwhackers", "partisans".
- Retrieval intent: confirm which one‑word label encyclopedic sources use to describe the robbers and short Civil‑War/Missouri usage notes.

ADD_OR_RESTORE:
- Behavior: fetch the robbery article's lead/first sentence (exact phrasing that names the perpetrators).
- Behavior: fetch short lead/definition lines for each candidate label limited to US/Civil‑War/Missouri context (e.g., "Missouri bushwhacker", "Confederate guerrilla").
- Anchors/bridge clues: "lead sentence", "first paragraph", "called", "described as", "Missouri bushwhackers", "former Confederate guerrillas (Missouri)", "short encyclopedia entry", sources: Britannica, state historical society, article lead.
- Query cues: include date/location/type cues ("Feb 13 1866", "Liberty Missouri", "robbery") and phrase match for one-word labels in quotes.

REMOVE_OR_AVOID:
- Full biographies and long gang histories (Jesse James detailed timelines, James–Younger Gang operations).
- Deep etymology or Revolutionary‑War origin searches at this step.
- Generic international or non‑US "partisan"/"guerrilla" usages.
- Long multi-entity queries that mix biographical noise with term origin.

QUERY_SHAPE:
Two tight, focused lookups in order:
1) Fetch the robbery article lead: exact-phrase/lead lookup for "Clay County Savings Association Building" + "Feb 13 1866" + look for lead sentence containing words in quotes like "guerrillas" OR "bushwhackers" OR "partisans".
2) For the label(s) found or suspected, fetch short definitions: lead/definition lines limited to Civil War/Missouri usage (queries like "Missouri bushwhacker definition", "Confederate guerrilla Missouri definition", source: Britannica/state historical
...[truncated]

---

### 82__split2__seg0__feedback__right
- idx: 82
- split_iter: 2
- task_kind: right_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.81
- why_larger: Both segments prescribe the same core semantic shift: a two-step, lead-sentence-first then short-definition lookup focused on Civil War/Missouri usage and single-word perpetrator labels, preserve the same anchors, and avoid biographies and deep etymology. Neither demands a materially larger change to query-generation behavior than the other.

#### Question
What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?

#### Full-edge feedback
- edge: R0_base -> Rmid_iter2_split0

step: 0
from: R0_base
to: Rmid_iter2_split0
pgrad: TRIGGER:
Narrow retrieval when results include long biographies, gang timelines, or deep etymology; instead surface a single-word irregular‑fighter label used in encyclopedic lead lines for the Feb 13, 1866 Liberty, Missouri robbery.

KEEP:
- Anchors: "Clay County Savings Association Building", "Liberty, Missouri", "Feb 13 1866", "Jesse James", "Archie Clement", "former Confederate guerrillas".
- Candidate labels/aliases: "guerrillas", "bushwhackers", "partisans".
- Retrieval intent: confirm which one‑word label encyclopedic sources use to describe the robbers and short Civil‑War/Missouri usage notes.

ADD_OR_RESTORE:
- Behavior: fetch the robbery article's lead/first sentence (exact phrasing that names the perpetrators).
- Behavior: fetch short lead/definition lines for each candidate label limited to US/Civil‑War/Missouri context (e.g., "Missouri bushwhacker", "Confederate guerrilla").
- Anchors/bridge clues: "lead sentence", "first paragraph", "called", "described as", "Missouri bushwhackers", "former Confederate guerrillas (Missouri)", "short encyclopedia entry", sources: Britannica, state historical society, article lead.
- Query cues: include date/location/type cues ("Feb 13 1866", "Liberty Missouri", "robbery") and phrase match for one-word labels in quotes.

REMOVE_OR_AVOID:
- Full biographies and long gang histories (Jesse James detailed timelines, James–Younger Gang operations).
- Deep etymology or Revolutionary‑War origin searches at this step.
- Generic international or non‑US "partisan"/"guerrilla" usages.
- Long multi-entity queries that mix biographical noise with term origin.

QUERY_SHAPE:
Two tight, focused lookups in order:
1) Fetch the robbery article lead: exact-phrase/lead lookup for "Clay County Savings Association Building" + "Feb 13 1866" + look for lead sentence containing words in quotes like "guerrillas" OR "bushwhackers" OR "partisans".
2) For the label(s) found or suspected, fetch short definitions: lead/definition lines limited to Civil War/Missouri usage (queries like "Missouri bushwhacker definition", "Confederate guerrilla Missouri definition", source: Britannica/state historical
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter3_split0 -> Rmid_iter2_split0

step: 1
from: Rmid_iter3_split0
to: Rmid_iter2_split0
pgrad: TRIGGER:
If the robbery article’s perpetrator-label is ambiguous, run a two-step, label-focused lookup targeting Civil War / Missouri usage rather than broader etymology.

KEEP:
- Confirm the exact one-word label used in contemporary/encyclopedic accounts for the Clay County Savings Association Building robbers (e.g., "guerrillas", "bushwhackers", "partisans").
- Preserve anchors: "Clay County Savings Association Building", "February 13, 1866", "Jesse James", "Archie Clement", "James–Younger Gang".
- Preserve constraint to extract short lead-sentence/first-paragraph phrasing from the robbery article and one- to two-line encyclopedia/dictionary lines only.
- Keep noise filters: avoid full biographies, long timelines, and broad multi-entity searches.

ADD_OR_RESTORE:
- Emphasize Civil War / Missouri context: include the phrase "former Confederate guerrillas" and "Missouri Civil War irregulars" as high-weight anchors.
- Add bridge targets: short Britannica/state historical society/encyclopedia lead lines defining "bushwhacker" and "guerrilla" in Missouri/Civil‑War usage and any phrase like "former Confederate guerrillas" in secondary sources.
- Prioritize capturing which label the robbery article uses as its primary descriptor (lead sentence), then immediately fetch concise Civil War–era definitions/usage notes for that label.
- Keep results tightly limited to lead/definition lines (one or two sentences) and citations that explicitly connect the term to Missouri/Civil War irregulars.

REMOVE_OR_AVOID:
- Remove the prior one- or two-line check for Revolutionary‑War usage as a required step (deprioritize Revolutionary‑War etymology).
- Avoid deep etymology tracing, international or modern generic uses of "partisan"/"guerrilla", and full biographies or comprehensive gang histories.
- Avoid multi-document mashups; do not expand into broad timelines or multi-entity comparative searches at this step.

QUERY_SHAPE:
1) Fetch the Clay County Savings Association Building article lead/first paragraph (include date Feb 13, 1866) to capture the exact one-word perpetrator label and the exact phrase used (e.g., "former 
...[truncated]

---

## pass (109 total, showing 12)

### 108__split0__seg0__feedback__left
- idx: 108
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: Segment A makes a broader semantic shift: it demands an explicit disambiguation anchor ("Solo (Australian soft drink)"), adds a locale anchor (Australia) plus a comparative anchor (La Croix United States) and multiple type/source cues, and specifies a wider set of removals to suppress noisy entities. This changes which entity anchors and comparison signals the generator must preserve and add, and re-centers retrieval behavior more strongly than B's narrower refinement.

#### Question
Are Solo and La Croix Sparkling Water produced in the same country ?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
If La Croix is identified as produced in the United States (La Crosse, Wisconsin, 1981) but the summary lacks Solo's production country.

KEEP:
Solo (soft drink); Solo (Australian soft drink); Solo (drink) alias; Australian; lemon‑flavoured; La Croix Sparkling Water; United States; La Crosse, Wisconsin; Schweppes; manufacturer / producer; country of origin / produced in.

ADD_OR_RESTORE:
Explicit disambiguation token "Solo (Australian soft drink)"; type cues "country of origin", "manufactured in", "produced in", "infobox"; source cues "Wikipedia", "manufacturer page", "product page"; locale anchor "Australia"; comparison anchor "La Croix United States" (to bias for cross‑country statements).

REMOVE_OR_AVOID:
Solo (Norwegian soft drink); Trend Drinks; Geo. Hall & Sons; Rubicon Drinks; V (drink); Passiona; Club (soft drink); Bitter lemon; Gini; Mitsuya Cider; Jaffa (drink); Guaraná Antarctica; generic global manufacturer tokens that introduce international subsidiary pages (e.g., unqualified "Asahi") unless paired with "Schweppes Australia".

QUERY_SHAPE:
Short disambiguation-style factoid prompt: target the exact page title/alias + infobox/type cue + locale. Example shape: [Solo (Australian soft drink)] + (country of origin | manufactured in | produced in | infobox | manufacturer) + (Australia) with an optional comparative anchor [La Croix United States] — keep the query compact and focused on origin/producer fields rather than flavor or related brands.

WHY_THIS_MOVES_RETRIEVAL:
Adding the exact article title and explicit type cues (country of origin / manufactured in / infobox / manufacturer) raises BM25 weight on pages that state production locale in short factual fields. The Australia locale anchor and disambiguation token suppresses returns for similarly named or regional Solos (Norwegian) and unrelated beverage brands; removing common soft‑drink noise (Passiona, Club, Bitter lemon, etc.) reduces spurious matches. Including La Croix/United States as a comparative anchor nudges retrieval toward sources that explicitly state Solo's country so the system can perform a direct country comparison.

#### Sub-edge feedback
- edge: R0_base -> Rmid_iter1_split0

step: 0
from: R0_base
to: Rmid_iter1_split0
pgrad: TRIGGER:
Ambiguous single-token "Solo" + noisy manufacturer phrase "Schweppes Asahi" returning unrelated soft-drink pages; failure to surface a page that explicitly states country/origin.

KEEP:
- Anchors: Solo (soft drink) / Solo (Australian soft drink), Australia, La Croix Sparkling Water, United States
- Useful manufacturer cue preserved but refined: Schweppes (as regional/Schweppes Australia)

ADD_OR_RESTORE:
- Exact disambiguation cue: "(Australian soft drink)" or canonical page title token
- Origin/type cues: "country of origin", "Origin: Australia", "manufactured in", "infobox", "lead"
- Source-type cues: "Wikipedia infobox", "official product page", "manufacturer page (Schweppes Australia)"
- Disambiguation signals: "Solo (Norwegian)" as negative contrast to prioritize Australian variant

REMOVE_OR_AVOID:
- Ambiguous bare token "Solo" without region
- Combined global corp token "Schweppes Asahi" (too broad; surfaces multinational pages)
- Noisy beverage-brand terms that matched previously (Passiona, Club, Bitter lemon, Gini, Mitsuya Cider, Jaffa)
- Generic manufacturer pages and international subsidiary pages that do not state Solo's production country

QUERY_SHAPE:
Concise disambiguation-style BM25 query behavior: prioritize exact canonical title or phrase matches ("Solo (Australian soft drink)" OR "Solo Australian") plus strong origin/type anchors ("country of origin", "Origin: Australia", "infobox", "manufactured in") and source-type anchors ("Wikipedia", "official", "manufacturer"). De-emphasize global corp tokens and add negative/contrast cues to push away regional variants (e.g., prefer Australian variant over "Norwegian").

WHY_THIS_MOVES_RETRIEVAL:
- Exact title and disambiguation cues raise BM25 term overlap with the canonical Solo (Australian soft drink) page, promoting the lead/infobox that contains "country of origin" phrasing.
- Adding "country of origin"/"infobox"/"manufactured in" steers ranking toward pages that present a short factual origin statement rather than broader brand histories.
- Refining Schweppes → "Schweppes Australia" keeps useful manufacturer confirmation without triggerin
...[truncated]

---

### 108__split0__seg0__feedback__right
- idx: 108
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why_larger: Segment B issues a broader semantic shift: it not only disambiguates to the Australian Solo but also explicitly adds a comparative anchor (La Croix/United States), a wider set of type/location tokens, and a longer removal list—changing which anchors and comparison relations the retriever should prioritize. Segment A is a narrower, focused reweighting to surface the Solo (Australian) page.

#### Question
Are Solo and La Croix Sparkling Water produced in the same country ?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
If La Croix is identified as produced in the United States (La Crosse, Wisconsin, 1981) but the summary lacks Solo's production country.

KEEP:
Solo (soft drink); Solo (Australian soft drink); Solo (drink) alias; Australian; lemon‑flavoured; La Croix Sparkling Water; United States; La Crosse, Wisconsin; Schweppes; manufacturer / producer; country of origin / produced in.

ADD_OR_RESTORE:
Explicit disambiguation token "Solo (Australian soft drink)"; type cues "country of origin", "manufactured in", "produced in", "infobox"; source cues "Wikipedia", "manufacturer page", "product page"; locale anchor "Australia"; comparison anchor "La Croix United States" (to bias for cross‑country statements).

REMOVE_OR_AVOID:
Solo (Norwegian soft drink); Trend Drinks; Geo. Hall & Sons; Rubicon Drinks; V (drink); Passiona; Club (soft drink); Bitter lemon; Gini; Mitsuya Cider; Jaffa (drink); Guaraná Antarctica; generic global manufacturer tokens that introduce international subsidiary pages (e.g., unqualified "Asahi") unless paired with "Schweppes Australia".

QUERY_SHAPE:
Short disambiguation-style factoid prompt: target the exact page title/alias + infobox/type cue + locale. Example shape: [Solo (Australian soft drink)] + (country of origin | manufactured in | produced in | infobox | manufacturer) + (Australia) with an optional comparative anchor [La Croix United States] — keep the query compact and focused on origin/producer fields rather than flavor or related brands.

WHY_THIS_MOVES_RETRIEVAL:
Adding the exact article title and explicit type cues (country of origin / manufactured in / infobox / manufacturer) raises BM25 weight on pages that state production locale in short factual fields. The Australia locale anchor and disambiguation token suppresses returns for similarly named or regional Solos (Norwegian) and unrelated beverage brands; removing common soft‑drink noise (Passiona, Club, Bitter lemon, etc.) reduces spurious matches. Including La Croix/United States as a comparative anchor nudges retrieval toward sources that explicitly state Solo's country so the system can perform a direct country comparison.

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
Disambiguate "Solo" toward the Australian lemon-flavoured soft drink (focus on country of origin).

KEEP:
- Anchors: "Solo (Australian soft drink)"; "Solo (soft drink)"; "La Croix Sparkling Water"; "United States"; "Australia"
- Bridge clues to retain: presence of a page titled "Solo (Australian soft drink)"; lead/infobox text stating "Country of origin" / "Origin: Australia"; manufacturer or distributor entries implying Australian production (e.g., Schweppes Australia)
- Expected evidence type: short authoritative lead/infobox or manufacturer page explicitly naming Australia as Solo's country of origin/production

ADD_OR_RESTORE:
- BM25-relevant tokens and aliases to add: "Solo (Australian soft drink)", "Solo lemon-flavoured", "Solo Australia", "country of origin", "manufactured in Australia", "made in Australia", "Schweppes Australia", "Asahi Australia distributor", "infobox: Country of origin", "lead: Origin: Australia"
- Bridge cues to emphasize: exact-title match, infobox/lead lines, manufacturer location lines, phrases like "origin" or "manufactured" near "Australia"
- Noise-removal hints to restore: prefer pages whose title exactly matches "Solo (Australian soft drink)" and rank infobox/lead text higher than generic brand mentions

REMOVE_OR_AVOID:
- Distractors: "Solo (Norwegian soft drink)"; Trend Drinks; Geo. Hall & Sons; Rubicon Drinks; V (drink); Guaraná Antarctica
- Broad/ambiguous pages: global Schweppes/Asahi pages that do not mention Solo or a country-of-origin line; generic "soft drink" lists and unrelated beverage brand pages
- Terms to de-emphasize: generic "Solo" without geographic qualifier; distributor/manufacturer mentions that lack explicit Australian production info

QUERY_SHAPE:
Short disambiguation-style retrieval template that prioritizes exact-title and country cues: prioritize tokens ["Solo (Australian soft drink)", "Solo Australia", "country of origin", "manufactured in Australia", "Schweppes Australia"] and boost matches where those tokens appear in the page title or infobox/lead; downweight pages containing only generic brand lists or other regional "Solo" entries.

...[truncated]

---

### 108__split1__seg1__feedback__right
- idx: 108
- split_iter: 1
- task_kind: right_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: A prescribes a broader, higher‑impact reweighting: it explicitly preserves both entity anchors (Solo and La Croix), adds multiple BM25 alias tokens, emphasizes exact‑title + infobox/lead signals, and gives detailed noise‑removal and query‑shaping instructions—requiring larger changes to which anchors and evidence are prioritized. B is a narrower, primarily Solo‑focused disambiguation and source-preference tweak.

#### Question
Are Solo and La Croix Sparkling Water produced in the same country ?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
Disambiguate "Solo" toward the Australian lemon-flavoured soft drink (focus on country of origin).

KEEP:
- Anchors: "Solo (Australian soft drink)"; "Solo (soft drink)"; "La Croix Sparkling Water"; "United States"; "Australia"
- Bridge clues to retain: presence of a page titled "Solo (Australian soft drink)"; lead/infobox text stating "Country of origin" / "Origin: Australia"; manufacturer or distributor entries implying Australian production (e.g., Schweppes Australia)
- Expected evidence type: short authoritative lead/infobox or manufacturer page explicitly naming Australia as Solo's country of origin/production

ADD_OR_RESTORE:
- BM25-relevant tokens and aliases to add: "Solo (Australian soft drink)", "Solo lemon-flavoured", "Solo Australia", "country of origin", "manufactured in Australia", "made in Australia", "Schweppes Australia", "Asahi Australia distributor", "infobox: Country of origin", "lead: Origin: Australia"
- Bridge cues to emphasize: exact-title match, infobox/lead lines, manufacturer location lines, phrases like "origin" or "manufactured" near "Australia"
- Noise-removal hints to restore: prefer pages whose title exactly matches "Solo (Australian soft drink)" and rank infobox/lead text higher than generic brand mentions

REMOVE_OR_AVOID:
- Distractors: "Solo (Norwegian soft drink)"; Trend Drinks; Geo. Hall & Sons; Rubicon Drinks; V (drink); Guaraná Antarctica
- Broad/ambiguous pages: global Schweppes/Asahi pages that do not mention Solo or a country-of-origin line; generic "soft drink" lists and unrelated beverage brand pages
- Terms to de-emphasize: generic "Solo" without geographic qualifier; distributor/manufacturer mentions that lack explicit Australian production info

QUERY_SHAPE:
Short disambiguation-style retrieval template that prioritizes exact-title and country cues: prioritize tokens ["Solo (Australian soft drink)", "Solo Australia", "country of origin", "manufactured in Australia", "Schweppes Australia"] and boost matches where those tokens appear in the page title or infobox/lead; downweight pages containing only generic brand lists or other regional "Solo" entries.

...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter2_split1 -> Rstar_target

step: 2
from: Rmid_iter2_split1
to: Rstar_target
pgrad: TRIGGER:
Step 2 — disambiguate Solo origin toward the Australian Solo page

KEEP:
- Anchors: "Solo (Australian soft drink)", "infobox/lead sentence", "Country of origin: Australia", "Manufacturer / Distributor (Schweppes Australia, Asahi, Coca‑Cola Amatil)"
- Bridge clues: lead phrasing like "Solo is an Australian...", infobox field "Origin" or "Country", phrases "Australian lemon‑flavoured soft drink", "produced in Australia"
- Query-shape intent: concise extraction-style focus on page lead/infobox lines

ADD_OR_RESTORE:
- Disambiguation tokens: include "(Australian)", "Australian", "lemon‑flavoured", "soft drink"
- Type and extraction cues: add exact‑phrase anchors such as "Origin: Australia", "Produced in Australia", "Manufacturer:", "Distributed by"
- Source preferring cues: "Wikipedia", "official site", "manufacturer page" to boost canonical pages
- Manufacturer aliases as bridge anchors: "Schweppes Australia", "Asahi", "Coca‑Cola Amatil"
- Explicit avoidance token to discourage variants: include negative/contrast clue like "not Norwegian / not 'Solo (Norwegian)'" (for filtering)

REMOVE_OR_AVOID:
- Noisy titles and topics: "Solo (Norwegian soft drink)", "Trend Drinks", "Geo. Hall & Sons", "Rubicon Drinks", "V (drink)", "Guaraná Antarctica"
- Generic/ambiguous tokens: single word "Solo" alone, broad lists of soft drinks, beverage manufacturer pages that mention brands in multiple countries without linking Solo to Australia
- Non‑evidence content: distribution deal articles or product lists that don't state production/origin

QUERY_SHAPE:
- Behavior: build a short, disambiguating extraction-style query that forces the Australian sense and targets lead/infobox lines and manufacturer pages. Example structure to aim for (do not use as final query): include the phrase "Solo (Australian)"/"Solo is an Australian" OR "Solo (Australian soft drink)" + one of ("Origin", "Country", "Produced in", "Manufacturer", "Distributed by", "infobox", "lead") and prefer site:wikipedia.org or the manufacturer's domain. Avoid queries that use only "Solo" or list-level terms.

WHY_THIS_MOVES_RETRIEVAL:
- Adds precise, high‑weig
...[truncated]

---

### 108__split2__seg2__feedback__right
- idx: 108
- split_iter: 2
- task_kind: right_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: Segment A specifies a broader, higher‑impact semantic shift: it not only adds precise disambiguation anchors and manufacturer aliases but also introduces source‑preference cues (Wikipedia/official site), explicit negative/avoidance tokens, and stronger removal rules and query‑shape constraints. These additions change which anchors are required, which noisy families are excluded, and how queries are shaped more than B's overlapping but narrower BM25/disambiguation guidance.

#### Question
Are Solo and La Croix Sparkling Water produced in the same country ?

#### Full-edge feedback
- edge: Rmid_iter2_split1 -> Rstar_target

step: 2
from: Rmid_iter2_split1
to: Rstar_target
pgrad: TRIGGER:
Step 2 — disambiguate Solo origin toward the Australian Solo page

KEEP:
- Anchors: "Solo (Australian soft drink)", "infobox/lead sentence", "Country of origin: Australia", "Manufacturer / Distributor (Schweppes Australia, Asahi, Coca‑Cola Amatil)"
- Bridge clues: lead phrasing like "Solo is an Australian...", infobox field "Origin" or "Country", phrases "Australian lemon‑flavoured soft drink", "produced in Australia"
- Query-shape intent: concise extraction-style focus on page lead/infobox lines

ADD_OR_RESTORE:
- Disambiguation tokens: include "(Australian)", "Australian", "lemon‑flavoured", "soft drink"
- Type and extraction cues: add exact‑phrase anchors such as "Origin: Australia", "Produced in Australia", "Manufacturer:", "Distributed by"
- Source preferring cues: "Wikipedia", "official site", "manufacturer page" to boost canonical pages
- Manufacturer aliases as bridge anchors: "Schweppes Australia", "Asahi", "Coca‑Cola Amatil"
- Explicit avoidance token to discourage variants: include negative/contrast clue like "not Norwegian / not 'Solo (Norwegian)'" (for filtering)

REMOVE_OR_AVOID:
- Noisy titles and topics: "Solo (Norwegian soft drink)", "Trend Drinks", "Geo. Hall & Sons", "Rubicon Drinks", "V (drink)", "Guaraná Antarctica"
- Generic/ambiguous tokens: single word "Solo" alone, broad lists of soft drinks, beverage manufacturer pages that mention brands in multiple countries without linking Solo to Australia
- Non‑evidence content: distribution deal articles or product lists that don't state production/origin

QUERY_SHAPE:
- Behavior: build a short, disambiguating extraction-style query that forces the Australian sense and targets lead/infobox lines and manufacturer pages. Example structure to aim for (do not use as final query): include the phrase "Solo (Australian)"/"Solo is an Australian" OR "Solo (Australian soft drink)" + one of ("Origin", "Country", "Produced in", "Manufacturer", "Distributed by", "infobox", "lead") and prefer site:wikipedia.org or the manufacturer's domain. Avoid queries that use only "Solo" or list-level terms.

WHY_THIS_MOVES_RETRIEVAL:
- Adds precise, high‑weig
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter3_split2 -> Rstar_target

step: 3
from: Rmid_iter3_split2
to: Rstar_target
pgrad: TRIGGER:
Disambiguation lead present or broad "Solo" hits returned but no document whose title or lead contains the exact tokens "Solo (Australian soft drink)" or the phrase "Solo is an Australian".

KEEP:
- Keep disambiguation-focused behavior: look for "Solo (disambiguation)" and short lead/infobox lines.
- Keep anchors: "Solo (soft drink)" alias, manufacturer names as candidate bridges (e.g., Schweppes Australia, Asahi, Coca‑Cola Amatil).
- Keep bridge clues: lead sentence patterns like "Solo is an Australian..." or "lemon‑flavoured soft drink produced in..."

ADD_OR_RESTORE:
- Add exact-title and alias anchors: the token sequence Solo (Australian soft drink), "Solo (soft drink)", and the phrase "Solo is an Australian".
- Add country/type tokens: Australia, "country of origin", "produced in", "manufactured in", "lemon‑flavoured".
- Add manufacturer/distributor anchors as connectors: Schweppes Australia, Asahi, Coca‑Cola Amatil (as short header/infobox hits).
- Favor lead/infobox cues: presence of an infobox line containing "Country" or "Origin: Australia" and short one‑sentence leads with "Australian".
- Include date/established cues only as supporting tokens if present in lead (e.g., first produced year) to prefer authoritative product pages.

REMOVE_OR_AVOID:
- Deprioritize or filter out pages and tokens: "Solo (Norwegian soft drink)", Trend Drinks, V (drink), Guaraná Antarctica, long brand lists, and global manufacturer pages that do not include "Australia" or explicit "produced in" lines.
- Avoid long news/distribution articles and pages that mention many beverages without an explicit country/origin token.

QUERY_SHAPE:
Local, BM25‑style disambiguation query that prioritizes documents whose title or lead/inbox contains the exact anchor tokens ("Solo (Australian soft drink)" OR "Solo is an Australian") AND includes one or more country/type tokens (Australia, "country of origin", "produced in", "manufactured in", "lemon‑flavoured"); use manufacturer tokens (Schweppes Australia, Asahi, Coca‑Cola Amatil) as secondary boosts; penalize documents matching distractor tokens ("Norwegian", "Trend Drinks", long
...[truncated]

---

### 108__split3__seg3__feedback__left
- idx: 108
- split_iter: 3
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.84
- why_larger: Segment A makes broader semantic changes to retrieval: it adds new exact-title and country/type anchors, reweights manufacturer anchors, and explicitly deprioritizes many distractor entity families—altering which candidate entities/documents are considered. Segment B is a narrower extraction-oriented refinement once the Australian 'Solo' variant is already identified.

#### Question
Are Solo and La Croix Sparkling Water produced in the same country ?

#### Full-edge feedback
- edge: Rmid_iter3_split2 -> Rstar_target

step: 3
from: Rmid_iter3_split2
to: Rstar_target
pgrad: TRIGGER:
Disambiguation lead present or broad "Solo" hits returned but no document whose title or lead contains the exact tokens "Solo (Australian soft drink)" or the phrase "Solo is an Australian".

KEEP:
- Keep disambiguation-focused behavior: look for "Solo (disambiguation)" and short lead/infobox lines.
- Keep anchors: "Solo (soft drink)" alias, manufacturer names as candidate bridges (e.g., Schweppes Australia, Asahi, Coca‑Cola Amatil).
- Keep bridge clues: lead sentence patterns like "Solo is an Australian..." or "lemon‑flavoured soft drink produced in..."

ADD_OR_RESTORE:
- Add exact-title and alias anchors: the token sequence Solo (Australian soft drink), "Solo (soft drink)", and the phrase "Solo is an Australian".
- Add country/type tokens: Australia, "country of origin", "produced in", "manufactured in", "lemon‑flavoured".
- Add manufacturer/distributor anchors as connectors: Schweppes Australia, Asahi, Coca‑Cola Amatil (as short header/infobox hits).
- Favor lead/infobox cues: presence of an infobox line containing "Country" or "Origin: Australia" and short one‑sentence leads with "Australian".
- Include date/established cues only as supporting tokens if present in lead (e.g., first produced year) to prefer authoritative product pages.

REMOVE_OR_AVOID:
- Deprioritize or filter out pages and tokens: "Solo (Norwegian soft drink)", Trend Drinks, V (drink), Guaraná Antarctica, long brand lists, and global manufacturer pages that do not include "Australia" or explicit "produced in" lines.
- Avoid long news/distribution articles and pages that mention many beverages without an explicit country/origin token.

QUERY_SHAPE:
Local, BM25‑style disambiguation query that prioritizes documents whose title or lead/inbox contains the exact anchor tokens ("Solo (Australian soft drink)" OR "Solo is an Australian") AND includes one or more country/type tokens (Australia, "country of origin", "produced in", "manufactured in", "lemon‑flavoured"); use manufacturer tokens (Schweppes Australia, Asahi, Coca‑Cola Amatil) as secondary boosts; penalize documents matching distractor tokens ("Norwegian", "Trend Drinks", long
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter3_split2 -> Rmid_iter4_split3

step: 3
from: Rmid_iter3_split2
to: Rmid_iter4_split3
pgrad: TRIGGER:
Step 3 → disambiguation step succeeded or returned a "Solo (soft drink)" / "Solo (disambiguation)" hit indicating an Australian variant is likely (i.e., the disambig/lead contains "Australian" or points to a "Solo (Australian soft drink)" article).

KEEP:
- Keep the local disambiguation anchors and short-source preference: "Solo (disambiguation) / 'Solo (soft drink)' summary line", "Short lead/infobox lines".
- Preserve bridge clues that signal country text: lead phrases like "Solo is an Australian..." and infobox fields (Country of origin, Manufacturer).
- Retain alias tokens for matching: "Solo (soft drink)", "Solo (drink)", "Solo lemon‑flavoured".

ADD_OR_RESTORE:
- Add tight extraction targets: request a one-line lead and the infobox fields "Country of origin" and "Manufacturer/Produced in".
- Add BM25-friendly anchors and tokens to prioritize: "Solo (Australian soft drink) lead", "Country of origin: Australia", "Produced in Australia", "Schweppes Australia", "Asahi", "Coca‑Cola Amatil", "lemon‑flavoured soft drink".
- Restore narrow manufacturer header retrieval: single-line manufacturer/distributor header that links Solo to Australia.
- Add alias and date cues to disambiguate if present: parenthetical "(Australia)", production/origin dates (e.g., "first produced in") only if they appear in the lead/infobox.

REMOVE_OR_AVOID:
- Avoid broader or noisy pages: "Solo (Norwegian ...)", other regional 'Solo' variants, long manufacturer pages listing many brands, beverage lists, and news pieces that mention global companies without per-brand country lines.
- Remove retrieval of full manufacturer corp pages, long lists, or multi-brand distribution pages that do not include a one-line country tie.
- Avoid multi-paragraph articles or results that do not include the infobox or first-sentence lead.

QUERY_SHAPE:
- Narrow, extraction-oriented prompt: ask for 1–2 authoritative lines — the lead sentence plus infobox entries "Country of origin" and "Manufacturer/Produced in" for "Solo (Australian soft drink)". Use BM25 tokens: "Solo (Australian soft drink) lead", "Country of origin Australia", "Manufactu
...[truncated]

---

### 118__split0__seg0__feedback__right
- idx: 118
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.82
- why_larger: B introduces broader semantic changes: it adds explicit actor-name anchors (e.g., Deborah Kerr, Donna Reed), prescribes an extra cross-check bridge (query actor filmographies / 'appeared in'), and defines a three-query workflow (two exact-title queries plus actor-filmography verification). A focuses more narrowly on precise title+year cast lookups and output normalization. B therefore changes both what anchors are injected and the bridging strategy between candidate lists, a larger shift in query-generation behavior.

#### Question
What acress starred in both "Third Person" and "From Here to Eternity"?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
Initial hop yields disambiguation/TV/musical pages or unrelated titles (no clear authoritative cast page for Third Person and the 1953/1979 From Here to Eternity versions), or search results emphasize unrelated names (Kim Basinger, Heather O'Rourke) instead of credited cast.

KEEP:
- Preserve versioned anchors: "Third Person (film)", "From Here to Eternity (1953 film)", "From Here to Eternity (1979 miniseries)".
- Preserve bridge clues: "full cast lists / credited actor names", "matching performer names across lists", "version disambiguation".
- Preserve retrieval focus on authoritative cast/credit sources (Wikipedia film pages, IMDb, filmographies) and the intent to intersect named cast members.

ADD_OR_RESTORE:
- Add explicit year/alias anchors and star names to bias toward the canonical film pages: "Third Person (2013) / Third Person (film)"; "From Here to Eternity (1953)"; include actor anchors "Deborah Kerr", "Donna Reed".
- Add type cues and provenance tokens: "cast", "full cast", "credited", "IMDb full cast", "Wikipedia infobox cast", "filmography".
- Add action bridge: "actor filmography" and "appeared in" to support second-hop cross-checks (e.g., search an actor's filmography page to confirm presence in both titles).
- Add noise-suppression cue: prefer "film" + year phrases and "miniseries (1979) cast" for deliberate versioning.

REMOVE_OR_AVOID:
- Avoid disambiguation and non-film variants: "From Here to Eternity (disambiguation)", "From Here to Eternity (TV series)", "From Here to Eternity the Musical", "From Here to Eternity: Live".
- Avoid unrelated film noise and celebrity names not tied to these casts: "Eternal Sunshine of the Spotless Mind", "Kim Basinger", "Heather O'Rourke".
- Avoid generic, undated queries like "Third Person cast" without a year or source tag that permit ambiguous matches.

QUERY_SHAPE:
- Behavior: emit two precise second-hop queries and one cross-check query.
  1) Exact-title + year + provenance cue + cast token: [exact film title + (year)] + ("cast" OR "full cast" OR "IMDb" OR "Wikipedia infobox").
  2) Repeat for the specific From Here to Eternity version(s): [“From Her
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
After the disambiguation hop returns one or more concrete "Third Person" title-year candidates and at least one identified version/year for "From Here to Eternity" (i.e., you have specific title+year pairs to test).

KEEP:
- Preserve the disambiguation ordering: list candidate works for "Third Person" with release years and candidate status (film/miniseries/TV).
- Keep anchors that guided disambiguation: "Third Person (disambiguation)", candidate years (e.g., 2013), "From Here to Eternity (1953 film)", "From Here to Eternity (1979 miniseries)".
- Retain the intent to extract lead/top-billed actresses (use "starring"/"lead"/"credited" cues) and short synopses to confirm which cast lists are primary.

ADD_OR_RESTORE:
- Immediately issue narrow, versioned cast lookups for each candidate title: exact-title + year + type + cast (target pages that list full credited cast).
- Prefer authoritative filmography sources (Wikipedia film pages, IMDb title pages, major film databases) and extract "starring / billed / credited" actress names; normalize name variants/aliases.
- If the question is underspecified, prioritize the 1953 film version of From Here to Eternity but still check the 1979 miniseries; enumerate both actor sets separately.
- Produce compact named-actor sets for each specific work/version to enable a direct intersection in the next step.

REMOVE_OR_AVOID:
- Avoid broad, undated title searches ("Third Person" alone) that surface disambiguation noise (books, songs, unrelated works).
- Avoid actor biography pages or news mentions unless they explicitly contain the title-specific credited cast section.
- Exclude tangential pages: TV-series adaptations, generic "From Here to Eternity (disambiguation)" results unless they link to the authoritative title pages.
- Suppress irrelevant celebrity hits (e.g., Kim Basinger, Heather O'Rourke) unless they appear on the authoritative cast lists for the specific title/version.

QUERY_SHAPE:
- Template 1 (film/miniseries cast): "<Exact Title> (<YYYY> film|miniseries|TV) cast" — e.g., "Third Person (2013 film) cast" or "From Here to Eternity (1953 film) cast".
- T
...[truncated]

---

### 118__split1__seg1__feedback__left
- idx: 118
- split_iter: 1
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why_larger: Segment A prescribes a broader, higher-impact change: it preserves disambiguation ordering and multiple title-year anchors, mandates per-version cast lookups, name normalization, and templates for post-processing intersections — a multi-pronged semantic re-centering of retrieval. B mainly narrows to particular title-year anchors and female top-billed extraction (a more localized restriction).

#### Question
What acress starred in both "Third Person" and "From Here to Eternity"?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
After the disambiguation hop returns one or more concrete "Third Person" title-year candidates and at least one identified version/year for "From Here to Eternity" (i.e., you have specific title+year pairs to test).

KEEP:
- Preserve the disambiguation ordering: list candidate works for "Third Person" with release years and candidate status (film/miniseries/TV).
- Keep anchors that guided disambiguation: "Third Person (disambiguation)", candidate years (e.g., 2013), "From Here to Eternity (1953 film)", "From Here to Eternity (1979 miniseries)".
- Retain the intent to extract lead/top-billed actresses (use "starring"/"lead"/"credited" cues) and short synopses to confirm which cast lists are primary.

ADD_OR_RESTORE:
- Immediately issue narrow, versioned cast lookups for each candidate title: exact-title + year + type + cast (target pages that list full credited cast).
- Prefer authoritative filmography sources (Wikipedia film pages, IMDb title pages, major film databases) and extract "starring / billed / credited" actress names; normalize name variants/aliases.
- If the question is underspecified, prioritize the 1953 film version of From Here to Eternity but still check the 1979 miniseries; enumerate both actor sets separately.
- Produce compact named-actor sets for each specific work/version to enable a direct intersection in the next step.

REMOVE_OR_AVOID:
- Avoid broad, undated title searches ("Third Person" alone) that surface disambiguation noise (books, songs, unrelated works).
- Avoid actor biography pages or news mentions unless they explicitly contain the title-specific credited cast section.
- Exclude tangential pages: TV-series adaptations, generic "From Here to Eternity (disambiguation)" results unless they link to the authoritative title pages.
- Suppress irrelevant celebrity hits (e.g., Kim Basinger, Heather O'Rourke) unless they appear on the authoritative cast lists for the specific title/version.

QUERY_SHAPE:
- Template 1 (film/miniseries cast): "<Exact Title> (<YYYY> film|miniseries|TV) cast" — e.g., "Third Person (2013 film) cast" or "From Here to Eternity (1953 film) cast".
- T
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rmid_iter2_split1

step: 1
from: Rmid_iter1_split0
to: Rmid_iter2_split1
pgrad: TRIGGER:
Step 1 — current step is performing broad title disambiguation for “Third Person” and checking which version of “From Here to Eternity” is intended.

KEEP:
- Preserve the goal of producing candidate actor sets per specific work/version (disambiguation → candidate actor lists).
- Keep use of authoritative film pages and disambiguation pages as primary sources (Wikipedia/IMDb/filmographies).
- Keep bridge clues: title + release year, lead/billed actresses, and 'starring' / cast-list sections as evidence targets.
- Keep explicit noise flags already listed (songs, books, unrelated similarly named works) so they remain deprioritized.

ADD_OR_RESTORE:
- Bias toward the single most-likely modern/main film for each ambiguous title by adding exact title+year aliases: "Third Person (2013 film)" and "From Here to Eternity (1953 film)" as primary anchors.
- Add behavior to preferentially fetch sections labeled "Starring", "Cast", or top-billed list entries on those exact-title pages and extract female performer names only.
- Restore targeted sources preference: open the title page (Wikipedia) then corroborate with IMDb cast section if needed; prefer pages where billing order is explicit.
- Add extraction constraint: return the first 2–4 top-billed female names per title (names and short role labels if present) to create compact candidate sets for intersection.
- Add alias and date cues: include common name variants (e.g., “From Here to Eternity 1953”, “Third Person 2013”) to match BM25 surface text in page headings.

REMOVE_OR_AVOID:
- Stop broad multi-year disambiguation sweeps that enumerate every work named "Third Person" (books, songs, shorts) unless 2013 is missing from top results.
- Avoid surfacing male-only cast lists, crew/production trivia, soundtrack, and unrelated remakes/adaptations (e.g., stage musical) as primary hits.
- Avoid large cast rosters beyond the top-billed performers and avoid pages that only mention titles in passing without a cast section.

QUERY_SHAPE:
- Two narrow, high-precision lookups (exact-title + year + cast cues), e.g.:
  1) [Title alias: "Third Person (2013)" OR text:
...[truncated]

---

### 118__split3__seg2__feedback__left
- idx: 118
- split_iter: 3
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why_larger: Segment A enacts a stronger re-centering: it locks ambiguous titles to specific canonical film editions (forcing Third Person→2013 and From Here to Eternity→1953), narrows queries to exact-title+year lookups, and removes broad disambiguation crawling. That is a more substantial semantic shift in anchors and retrieval shape than B’s more conservative/pipe-lined prioritization with fallbacks.

#### Question
What acress starred in both "Third Person" and "From Here to Eternity"?

#### Full-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter2_split1

step: 2
from: Rmid_iter3_split1
to: Rmid_iter2_split1
pgrad: TRIGGER:
Lock ambiguous titles to their canonical film editions — treat "Third Person" as the 2013 feature and "From Here to Eternity" as the 1953 feature for the next lookup.

KEEP:
- Preserve disambiguation check behavior (look for title pages and disambiguation markers labeled "film", "TV", "short").
- Keep focus on authoritative sources (Wikipedia/IMDb/major filmographies) and extracting explicit "Starring"/"Cast" sections.
- Keep instruction to produce compact candidate actress lists (top-billed female names) for later intersection.

ADD_OR_RESTORE:
- Bias queries toward exact-title + year aliases: prefer "Third Person (2013 film)" and "From Here to Eternity (1953 film)" as primary anchors.
- Prefer pages/sections containing the tokens "Starring", "Cast", or top-billed credits and extract the first 2–4 female names listed.
- Add bridge clues to match BM25 signals: include year tokens + "cast" or "starring" (e.g., title + "2013 cast", title + "1953 starring") and prefer pages whose titles contain the year in parentheses.
- Restore explicit exclusion rule to only consider entries labeled "film" (not "book", "song", "play", or undated short/obscure items).
- Record source title and URL for each actress list to keep provenance.

REMOVE_OR_AVOID:
- Deprioritize wide disambiguation crawling that returns books, songs, plays, or obscure festival shorts titled "Third Person".
- Avoid long full cast lists where lead billing is unclear, crew/production/trivia pages, and pages focused on remakes/miniseries unless the year cue explicitly matches the question.
- Avoid retrieving male-only billing or irrelevant production details that do not contain "Starring"/lead actress signals.

QUERY_SHAPE:
Run two narrow, high-precision lookups: one targeting the 2013 feature and one the 1953 feature. For each lookup: locate title pages whose headers include the exact title + year and the label "film", open the "Starring"/"Cast" block, and extract a short ordered list (first 2–4) of female performer names (with source title/URL). Use query terms that combine title + year + ("cast" OR "starring") and limit matches to pages 
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter4_split2

step: 2
from: Rmid_iter3_split1
to: Rmid_iter4_split2
pgrad: TRIGGER:
Step 2 — previous step returned a broad "Third Person" disambiguation result or mixed non-film items and did not commit to a primary film candidate; need to narrow sense toward film to produce compact top-billed female cast lists for intersection with "From Here to Eternity".

KEEP:
- Preserve ordered local plan: (1) consult disambiguation to enumerate candidate titles, (2) identify film-labeled entries, (3) fetch top-billed cast lists for each candidate, (4) produce compact 2–4 name female-cast lists per specific title/version for later intersection.
- Retain dual-path for "From Here to Eternity": prioritize 1953 film, keep 1979 miniseries as fallback.
- Keep bridge clues that use exact title + release year, 'Starring'/'Cast' sections, billing order, and female name prominence.

ADD_OR_RESTORE:
- Commit the "Third Person" sense to film and prioritize the 2013 feature as the primary candidate while still allowing other notable film-year candidates.
- Add explicit BM25 anchors and type cues to surface authoritative pages: "Third Person (2013 film) — Starring / Cast", "Third Person (disambiguation) — entries labeled 'film'", "From Here to Eternity (1953 film) — Starring / Cast", "From Here to Eternity (1979 miniseries) — Cast".
- Restore instruction to extract only top-billed female performers (2–4 names) and record release year and billing context ('Starring', billing order, role annotations) alongside each name.
- Add alias matching: treat queries for "Third Person film", "Third Person 2013", "Third Person (film) cast" as equivalent normalization to boost film pages.

REMOVE_OR_AVOID:
- Exclude non-film disambiguation entries (books, songs, plays), obscure shorts/festival entries, and non-authoritative noise pages.
- Avoid full long cast lists, crew/production/trivia/soundtrack pages, and pages where female performers are not top-billed (to prevent burying principal actresses).
- Avoid male-only cast lists and pages without explicit 'Starring'/'Cast' sections.

QUERY_SHAPE:
- Follow a small ordered pipeline of targeted lookups:
  1) "Third Person disambiguation" — filter entries labeled 'film'
...[truncated]

---

### 118__split3__seg2__feedback__right
- idx: 118
- split_iter: 3
- task_kind: right_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.83
- why_larger: Both updates re-anchor titles to exact yeared film pages (Third Person → 2013, From Here to Eternity → 1953), but A adds several additional semantic instructions that change retrieval behavior: explicit BM25 bridge clues, restoring an exclusion rule to only consider entries labeled 'film', preserving disambiguation-check behavior, and recording source provenance. These extra directives broaden the query-shaping and filtering semantics beyond the year-anchoring in B.

#### Question
What acress starred in both "Third Person" and "From Here to Eternity"?

#### Full-edge feedback
- edge: Rmid_iter3_split1 -> Rmid_iter2_split1

step: 2
from: Rmid_iter3_split1
to: Rmid_iter2_split1
pgrad: TRIGGER:
Lock ambiguous titles to their canonical film editions — treat "Third Person" as the 2013 feature and "From Here to Eternity" as the 1953 feature for the next lookup.

KEEP:
- Preserve disambiguation check behavior (look for title pages and disambiguation markers labeled "film", "TV", "short").
- Keep focus on authoritative sources (Wikipedia/IMDb/major filmographies) and extracting explicit "Starring"/"Cast" sections.
- Keep instruction to produce compact candidate actress lists (top-billed female names) for later intersection.

ADD_OR_RESTORE:
- Bias queries toward exact-title + year aliases: prefer "Third Person (2013 film)" and "From Here to Eternity (1953 film)" as primary anchors.
- Prefer pages/sections containing the tokens "Starring", "Cast", or top-billed credits and extract the first 2–4 female names listed.
- Add bridge clues to match BM25 signals: include year tokens + "cast" or "starring" (e.g., title + "2013 cast", title + "1953 starring") and prefer pages whose titles contain the year in parentheses.
- Restore explicit exclusion rule to only consider entries labeled "film" (not "book", "song", "play", or undated short/obscure items).
- Record source title and URL for each actress list to keep provenance.

REMOVE_OR_AVOID:
- Deprioritize wide disambiguation crawling that returns books, songs, plays, or obscure festival shorts titled "Third Person".
- Avoid long full cast lists where lead billing is unclear, crew/production/trivia pages, and pages focused on remakes/miniseries unless the year cue explicitly matches the question.
- Avoid retrieving male-only billing or irrelevant production details that do not contain "Starring"/lead actress signals.

QUERY_SHAPE:
Run two narrow, high-precision lookups: one targeting the 2013 feature and one the 1953 feature. For each lookup: locate title pages whose headers include the exact title + year and the label "film", open the "Starring"/"Cast" block, and extract a short ordered list (first 2–4) of female performer names (with source title/URL). Use query terms that combine title + year + ("cast" OR "starring") and limit matches to pages 
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter4_split2 -> Rmid_iter2_split1

step: 3
from: Rmid_iter4_split2
to: Rmid_iter2_split1
pgrad: TRIGGER: narrow_to_canonical_years_for_each_title

KEEP: film sense commitment for both titles; preference for authoritative title pages (Wikipedia/IMDb/major filmographies); focus on "Starring"/top-billed cast sections; extract compact female-cast lists (2–4 names) and preserve billing-order clues ('starring', first-listed, "as …").

ADD_OR_RESTORE: force exact title+year targets — treat "Third Person" as the 2013 feature and "From Here to Eternity" as the 1953 film; prioritize pages whose titles include those parenthetical years (e.g., "Third Person (2013 film)", "From Here to Eternity (1953 film)"); explicitly emit 2–4 top-billed female names per title (lead actresses only) in a compact set for an immediate intersection step; prefer pages with clear 'Starring' or top-billed headings and role annotations to confirm appearance.

REMOVE_OR_AVOID: drop disambiguation browsing and other-year/medium candidates for this step (no short films, books, songs, or 1979 miniseries detours); avoid long full-cast dumps, crew/trivia/soundtrack pages, and male-only billing lists; ignore pages without explicit 'Starring'/'Cast' ordering.

QUERY_SHAPE: two tight lookups constrained by exact-year film labels and cast-section anchors, returning compact female-name lists:
- Template A: [Third Person (2013 film) — page with "Starring" or "Cast" → output 2–4 top-billed female names]
- Template B: [From Here to Eternity (1953 film) — page with "Starring" or "Cast" → output 2–4 top-billed female names]
Expect output shape: {Third Person (2013): [Name1, Name2,…], From Here to Eternity (1953): [NameA, NameB,…]}.

WHY_THIS_MOVES_RETRIEVAL: narrowing to exact title+year pages and extracting only top-billed female names converts a broad, ambiguous candidate list into two small, high-precision actress sets — enabling a fast direct intersection. The year-parenthetical anchors and 'Starring' section cue boost BM25 relevance for the correct film pages and remove noisy disambiguation/extra-cast material that prevented a decisive match previously.

---

### 132__split0__seg0__feedback__left
- idx: 132
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.83
- why_larger: A prescribes a broader, higher-impact re-centering: it adds many BM25-rich anchors and type cues, specifies a new film→soundtrack→artist query shape, and instructs avoiding whole families of noisy pages. B is a narrower, mid-granularity credit-focused refinement that overlaps with A but makes fewer semantic changes.

#### Question
The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
Current retrieval returns general Björk pages or Vespertine-related results instead of pages whose titles/intro explicitly state "Selmasongs" or "Dancer in the Dark soundtrack" and list artist occupations.

KEEP:
- Anchors: Björk; Selmasongs; Dancer in the Dark; Selma Ježková; Lars von Trier
- Retrieval focus: artist/album pages and biographical pages that consolidate soundtrack credit + occupations

ADD_OR_RESTORE:
- BM25-rich phrases: "Dancer in the Dark soundtrack artist", "Selmasongs: Music from the Motion Picture Soundtrack", "Selmasongs credits", "performed by Björk", "Björk Guðmundsdóttir"
- Type cues: "album page", "soundtrack page", "artist biography", "official site", "One Little Indian Records"
- Bridge clues emphasizing credit and roles: "soundtrack artist", "music from the motion picture", "soundtrack credits", "Icelandic singer songwriter actress record producer DJ", release date cue "September 18, 2000"

REMOVE_OR_AVOID:
- Noisy distractions: Vespertine, Vespertine World Tour, Hidden Place, Björk (book), tríó Guðmundar Ingólfssonar, generic discography/tour pages, unrelated award lists (e.g., Anahí)
- Avoid broad film pages or pages focused on album-era collateral instead of explicit soundtrack/credit sections
- Avoid empty/blank query fragments

QUERY_SHAPE:
Short, entity-centric retrieval prompts that jump film→soundtrack→artist and surface album/credit pages; behavior examples (not final queries): prefer "film title + soundtrack artist" patterns, "Selmasongs album page" patterns, "Selmasongs credits Björk Guðmundsdóttir", or "Dancer in the Dark soundtrack artist biography"; bias toward pages with "Selmasongs" or "soundtrack" in title/lead and artist occupation lists.

WHY_THIS_MOVES_RETRIEVAL:
Adding explicit soundtrack- and credit-focused phrases plus the artist's full name and label/date cues boosts BM25 overlap with album/soundtrack and biography pages that state both the Selmasongs/Dancer in the Dark credit and occupational labels. Removing Vespertine/tour/book noise prevents high-scoring but irrelevant matches, steering retrieval from general Björk material toward pages whose titles an
...[truncated]

#### Sub-edge feedback
- edge: R0_base -> Rmid_iter1_split0

step: 0
from: R0_base
to: Rmid_iter1_split0
pgrad: TRIGGER:
When the entity-centric Björk biography query returns broad discography/biography pages but fails to surface an album/soundtrack page or liner-note–style credit that explicitly names the soundtrack artist.

KEEP:
- Anchors (preserve): Björk; Selmasongs; Dancer in the Dark; Selma Ježková; Lars von Trier
- Bridge clues (preserve): soundtrack; music from the motion picture; performed by; soundtrack credits; album "Selmasongs"
- Retrieval focus (preserve intent): find an authoritative artist/album page that ties Björk to the film soundtrack and lists occupations.

ADD_OR_RESTORE:
- Album-credit phrasing: "Selmasongs credits", "soundtrack artist credited", "credited to Björk", "performed by Björk"
- Aliases/type cues: "Björk Guðmundsdóttir", "Selmasongs (soundtrack)", "Dancer in the Dark soundtrack"
- Source/type targets: album page, liner notes, AllMusic, Discogs, Wikipedia album entry, official artist site, One Little Indian Records
- Specific identifiers (BM25 anchors to boost matches): release date "September 18, 2000"; label "One Little Indian Records"
- Occupation descriptors to surface on the same page: "Icelandic singer", "songwriter", "actress", "record producer", "DJ"

REMOVE_OR_AVOID:
- Noisy/distracting anchors: Vespertine; Vespertine World Tour; Hidden Place; Björk (book); tríó Guðmundar Ingólfssonar; general "List of songs recorded by Björk"
- Query focuses to avoid: broad biography birthdate searches, generalized discography lists, tour- or single-track pages

QUERY_SHAPE:
Issue a mid-granularity, credit-oriented prompt that favors pages where film+album+credit language co-occur. Target document types (album pages, liner notes, music-db entries) and surface phrase matches such as Selmasongs + (credits | "credited to" | "performed by") and Björk Guðmundsdóttir alongside occupation tokens. De-emphasize single-term entity jumps or biography-only tokens; prefer title-level matches (page title contains "Selmasongs" or "Dancer in the Dark (soundtrack)").

WHY_THIS_MOVES_RETRIEVAL:
Shifting from broad biography signals to album- and credit-specific terms (plus aliases, label/date, and music-database 
...[truncated]

---

### 132__split0__seg0__feedback__right
- idx: 132
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: candidate_set
- confidence: 0.78
- why_larger: Segment B is a full-edge update that re-centers retrieval from generic Björk/Vespertine results to album/soundtrack/credit pages and explicitly adds BM25-rich title/role/date cues; it prescribes a broader, more foundational shift in candidate set and retrieval focus, whereas A is a narrower, follow-up refinement focused on exact-title and source-type boosts.

#### Question
The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?

#### Full-edge feedback
- edge: R0_base -> Rstar_target

step: 0
from: R0_base
to: Rstar_target
pgrad: TRIGGER:
Current retrieval returns general Björk pages or Vespertine-related results instead of pages whose titles/intro explicitly state "Selmasongs" or "Dancer in the Dark soundtrack" and list artist occupations.

KEEP:
- Anchors: Björk; Selmasongs; Dancer in the Dark; Selma Ježková; Lars von Trier
- Retrieval focus: artist/album pages and biographical pages that consolidate soundtrack credit + occupations

ADD_OR_RESTORE:
- BM25-rich phrases: "Dancer in the Dark soundtrack artist", "Selmasongs: Music from the Motion Picture Soundtrack", "Selmasongs credits", "performed by Björk", "Björk Guðmundsdóttir"
- Type cues: "album page", "soundtrack page", "artist biography", "official site", "One Little Indian Records"
- Bridge clues emphasizing credit and roles: "soundtrack artist", "music from the motion picture", "soundtrack credits", "Icelandic singer songwriter actress record producer DJ", release date cue "September 18, 2000"

REMOVE_OR_AVOID:
- Noisy distractions: Vespertine, Vespertine World Tour, Hidden Place, Björk (book), tríó Guðmundar Ingólfssonar, generic discography/tour pages, unrelated award lists (e.g., Anahí)
- Avoid broad film pages or pages focused on album-era collateral instead of explicit soundtrack/credit sections
- Avoid empty/blank query fragments

QUERY_SHAPE:
Short, entity-centric retrieval prompts that jump film→soundtrack→artist and surface album/credit pages; behavior examples (not final queries): prefer "film title + soundtrack artist" patterns, "Selmasongs album page" patterns, "Selmasongs credits Björk Guðmundsdóttir", or "Dancer in the Dark soundtrack artist biography"; bias toward pages with "Selmasongs" or "soundtrack" in title/lead and artist occupation lists.

WHY_THIS_MOVES_RETRIEVAL:
Adding explicit soundtrack- and credit-focused phrases plus the artist's full name and label/date cues boosts BM25 overlap with album/soundtrack and biography pages that state both the Selmasongs/Dancer in the Dark credit and occupational labels. Removing Vespertine/tour/book noise prevents high-scoring but irrelevant matches, steering retrieval from general Björk material toward pages whose titles an
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
When shifting from a broad Björk-biography focus to confirm who is explicitly credited as the soundtrack artist and to surface a short artist descriptor (Icelandic singer/songwriter/actress/record producer/DJ) for Selmasongs — prioritize direct film→soundtrack→album-credit signals.

KEEP:
- Anchors: "Selmasongs", "Dancer in the Dark", "Björk"
- Bridge clues: "soundtrack credits", "performed by", "credited to", "album liner notes"
- Retrieval focus: narrow to authoritative soundtrack/album credit sources (album page, liner notes, reputable music databases)

ADD_OR_RESTORE:
- Exact-title anchors and aliases: "Selmasongs: Music from the Motion Picture", "Selmasongs (soundtrack)", "Selma Ježková"
- Artist alias: "Björk Guðmundsdóttir"
- Label/date cues and release metadata: "One Little Indian Records", "Released September 18, 2000"
- Source-type cues: "Wikipedia (Selmasongs)", "AllMusic Selmasongs credits", "Discogs release", "IMDb soundtrack", "official album page", "liner notes / credits list"
- Occupation keywords to surface on the same page: "Icelandic singer", "songwriter", "actress", "record producer", "DJ"
- BM25-friendly phrase fragments to prefer in results: "Selmasongs credits", "Dancer in the Dark soundtrack artist", "Selmasongs performed by Björk"

REMOVE_OR_AVOID:
- Distractors: "Vespertine", "Vespertine World Tour", "Björk (book)", "tríó Guðmundar Ingólfssonar"
- Generic discography or biography sweeps and birthdate-focused queries
- Irrelevant lists (e.g., awards pages for unrelated artists like Anahí)
- Empty/overly broad single-term queries ("Björk", "soundtrack") that surface unrelated releases

QUERY_SHAPE:
Use short, BM25-optimized, entity→credit templates and target-type cues rather than long biographies. Examples of shapes to generate (behavioral templates, not final single query):
- [film title] + "soundtrack artist" / "soundtrack credits"  -> target: soundtrack or album page
- [album exact title] + "credits" / "performed by" / "One Little Indian Records" -> target: release page, liner notes, Discogs/AllMusic/Wikipedia
- [album title] + [artist alias e.g., "Björk Guðmundsdóttir"]
...[truncated]

---

### 132__split1__seg1__feedback__left
- idx: 132
- split_iter: 1
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: Segment A makes a broader semantic shift: it re-centers retrieval on the film→soundtrack→album-credit relation and adds/changes many concrete anchors (exact album titles, artist legal name, occupation keywords, label/date, extra source types and BM25 phrase fragments). This requires more and different query-generation behavior than B's narrower release-level credit focus.

#### Question
The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?

#### Full-edge feedback
- edge: Rmid_iter1_split0 -> Rstar_target

step: 1
from: Rmid_iter1_split0
to: Rstar_target
pgrad: TRIGGER:
When shifting from a broad Björk-biography focus to confirm who is explicitly credited as the soundtrack artist and to surface a short artist descriptor (Icelandic singer/songwriter/actress/record producer/DJ) for Selmasongs — prioritize direct film→soundtrack→album-credit signals.

KEEP:
- Anchors: "Selmasongs", "Dancer in the Dark", "Björk"
- Bridge clues: "soundtrack credits", "performed by", "credited to", "album liner notes"
- Retrieval focus: narrow to authoritative soundtrack/album credit sources (album page, liner notes, reputable music databases)

ADD_OR_RESTORE:
- Exact-title anchors and aliases: "Selmasongs: Music from the Motion Picture", "Selmasongs (soundtrack)", "Selma Ježková"
- Artist alias: "Björk Guðmundsdóttir"
- Label/date cues and release metadata: "One Little Indian Records", "Released September 18, 2000"
- Source-type cues: "Wikipedia (Selmasongs)", "AllMusic Selmasongs credits", "Discogs release", "IMDb soundtrack", "official album page", "liner notes / credits list"
- Occupation keywords to surface on the same page: "Icelandic singer", "songwriter", "actress", "record producer", "DJ"
- BM25-friendly phrase fragments to prefer in results: "Selmasongs credits", "Dancer in the Dark soundtrack artist", "Selmasongs performed by Björk"

REMOVE_OR_AVOID:
- Distractors: "Vespertine", "Vespertine World Tour", "Björk (book)", "tríó Guðmundar Ingólfssonar"
- Generic discography or biography sweeps and birthdate-focused queries
- Irrelevant lists (e.g., awards pages for unrelated artists like Anahí)
- Empty/overly broad single-term queries ("Björk", "soundtrack") that surface unrelated releases

QUERY_SHAPE:
Use short, BM25-optimized, entity→credit templates and target-type cues rather than long biographies. Examples of shapes to generate (behavioral templates, not final single query):
- [film title] + "soundtrack artist" / "soundtrack credits"  -> target: soundtrack or album page
- [album exact title] + "credits" / "performed by" / "One Little Indian Records" -> target: release page, liner notes, Discogs/AllMusic/Wikipedia
- [album title] + [artist alias e.g., "Björk Guðmundsdóttir"]
...[truncated]

#### Sub-edge feedback
- edge: Rmid_iter1_split0 -> Rmid_iter2_split1

step: 1
from: Rmid_iter1_split0
to: Rmid_iter2_split1
pgrad: TRIGGER:
Narrow intent from broad Björk biography to release-level credit records for the Selmasongs/Dancer in the Dark soundtrack.

KEEP:
- Anchors: Selmasongs; Dancer in the Dark (soundtrack); Björk
- Bridge clues to preserve: "Selmasongs credits", "soundtrack artist credited", "performed by Björk", "soundtrack liner notes", "album liner notes"
- Query-shape orientation to keep: mid-granularity, album- and credit-oriented focus (avoid single-term artist jumps)

ADD_OR_RESTORE:
- Anchors/type cues to add: "Selmasongs (album) page", "Selmasongs: Music from the Motion Picture", "One Little Indian Records press/release", "AllMusic Selmasongs entry", "Discogs Selmasongs release", "Wikipedia album infobox"
- Bridge clues/phrases to add: "Artist: Björk", "credited to", "soundtrack performed by", "composer & performer listings", "album credits", "liner notes (scanned/track credits)"
- Date/alias cues: "Released September 18, 2000", "Selmasongs (soundtrack) / Selmasongs: Music from the Motion Picture"
- Query-shape additions: prefer source-type tokens (AllMusic | Discogs | One Little Indian | Wikipedia) combined with album-title and credit verbs

REMOVE_OR_AVOID:
- Noisy/distracting anchors to deprioritize: Vespertine; Vespertine World Tour; Björk (book); tríó Guðmundar Ingólfssonar; general discography pages; birthdate-focused biography pages
- Avoid document types: film reviews, plot summaries, broad biography pages, other Björk album pages and compilations

QUERY_SHAPE:
Shift to medium-granularity, credit-focused prompts that combine album title + source type + credit verbs. Example behavior tokens to drive BM25 matches (not a final query): include "Selmasongs credits" OR "Selmasongs AllMusic" OR "Selmasongs Discogs" OR "Selmasongs One Little Indian" + phrase-level anchors "Artist:" / "credited to" / "performed by" / "liner notes" + optional date "September 18, 2000" to boost precision.

WHY_THIS_MOVES_RETRIEVAL:
Adding release-level source types (AllMusic, Discogs, label, Wikipedia album page) and explicit credit phrases increases overlap with album/liner-note language that will score higher under BM25 th
...[truncated]

---
