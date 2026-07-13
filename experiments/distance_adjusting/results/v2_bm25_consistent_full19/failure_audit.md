# Failure audit

- failed triples shown: 30

## 108__split0__seg0

- idx: 108
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.84
- why: Transition B moves from a general mention of Solo+manufacturer to an explicit disambiguation-focused retrieval state that requires adding precise surface-form/title tokens (e.g., 'Solo (Australian soft drink)', 'Schweppes Australia') and actively excluding regional variants (Norwegian Solo) and noisy beverage pages—a clearer shift in BM25 query controls than A, which stays a straightforward single-entity fact lookup.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.74
- why: A moves from an empty/midpoint retrieval state to creating a concise, disambiguating BM25 query that must add exact title/entity tokens (e.g., "Solo (Australian soft drink)", "Australia") and avoid noisy regional variants — a larger shift in anchor/disambiguation tokens. B already contains explicit anchoring tokens and manufacturer clues, so it needs only minor retrieval-normalization.

## 108__split1__seg1

- idx: 108
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.79
- why: Both transitions start from the same disambiguation-focused state and need the same core BM25 changes (exact entity/title tokens to target 'Solo (Australian soft drink)' and disambiguation terms to avoid the Norwegian Solo). The B variant only adds extraction-style hinting (infobox/lead / 'country of origin') which is a small, local tightening of query tokens rather than a broad change in retrieval behavior, so neither transition is materially larger.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.86
- why: Both transitions require essentially the same small BM25 change: a concise disambiguating/extraction-style query to target the 'Solo (Australian soft drink)' page (avoid Norwegian/other Solo pages and noisy brand pages). Neither transition adds or removes distinct anchor tokens, bridge keywords, or broader candidate-set shifts.

## 108__split2__seg2

- idx: 108
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: From the same starting state, A preserves precise canonical-page targeting (tight title/infobox extraction). B shifts to a disambiguation-first, broader retrieval strategy—different tokens (e.g., 'disambiguation', 'Solo (soft drink)' summary), wider candidate set, and a different query shape—so it requires a larger BM25 query-control change.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.87
- why: B starts from a disambiguation-style, broad retrieval intent and must shift to a precise title/extraction query (add exact 'Solo (Australian soft drink)' tokens, remove noisy regional variants, and change query shape), whereas A already targets the canonical Solo page/infobox so requires a smaller BM25 query adjustment.

## 118__split0__seg0

- idx: 118
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: A moves from precise, title+cast lookups to a broader disambiguation-first strategy: it requires running 'Third Person' disambiguation queries, enumerating multiple year-specific candidates, and extracting top-billed actresses per candidate — increasing candidate-set breadth and changing the query shape and tokenization (more variant/year/role disambiguation tokens) compared with B’s focused exact title+"cast" queries.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.87
- why: A moves from a disambiguation-focused, exploratory state (no explicit exact-title queries) to issuing tight, exact-title + cast queries — a broader shift in query shape and addition of precise title/year tokens versus B, which already contains version-specific cast queries.

## 118__split1__seg1

- idx: 118
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.77
- why: B forces a clear shift from broad disambiguation to precise title+year targeting and an answer-type filter (top-billed female cast). That requires adding exact surface-form tokens (e.g., 'Third Person 2013', 'From Here to Eternity 1953') and changing query shape to highly constrained, small-candidate lookups — a bigger BM25 query-control change than A’s broader multi-version/disambiguation retrieval.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.92
- why: A moves from a broad disambiguation-style retrieval (many title variants, years, and candidate works to enumerate and filter) to tightly targeted title+cast lookups — a larger shift in tokens, disambiguation terms, and candidate-set narrowing than B, which already assumes exact title+year queries.

## 132__split2__seg0

- idx: 132
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why: Segment B requires a more substantial query-shape shift: moving from broad entity/biography searches to domain-restricted, album-level retrieval (site:discogs/allmusic/wikipedia/IMDB) and tightly targeting album entries; A is a smaller refinement toward soundtrack-credit pages while retaining biography/occupation tokens already present.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.84
- why: Transition A moves from a broad, entity-biography query (full name, birthdate, occupations, discography, Vespertine etc.) to a focused album/soundtrack-credit query — a substantial change in query shape: removing many noisy entity tokens, narrowing the candidate set to album-level pages and adding precise 'soundtrack/credits' constraints. Transition B is a smaller, local edit (album entries → album+short occupation descriptor).

## 140__split0__seg0

- idx: 140
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.85
- why: Transition B moves from verifying a single candidate to searching for a WPT champion who also has 'four WSOP bracelets' and a birth date — it requires adding explicit bridge-relation keywords linking WPT winners to bracelet counts, broadening the candidate set, and changing the query shape to a multi-constraint/entity-attribute search. Transition A is a narrow candidate-focused verification ("George Danzer" + WPT) and therefore a smaller BM25 query change.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.82
- why: From-state A is a vague/generated midpoint with no concrete query tokens, so reaching the target requires adding exact entity/title tokens (e.g., 'George Danzer'), disambiguation/bridge keywords ('World Poker Tour', 'List of World Poker Tour champions', 'four WSOP bracelets') and answer-type tokens ('birth date') — a broader shift in BM25 query control. B already contains those specific tokens, so its transition is a smaller adjustment.

## 140__split1__seg1

- idx: 140
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.84
- why: Segment B requires a broader multi-step retrieval: fetch the full WPT champions list, then run per-candidate checks for WSOP bracelet counts to produce a shortlist. That is a bigger BM25 query-shape and candidate-set breadth shift than A, which only adds a final biography/birthdate lookup for a single identified person.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: From-state A is a narrow, entity-centric check ('George Danzer WPT'). Reaching the target requires switching to list-level and bridge queries ('List of World Poker Tour champions', 'WPT winner + four WSOP bracelets') and adding answer-type tokens (birth date), i.e. a shift from a single-entity probe to broader list-scanning and different bridge/answer keywords.

## 140__split3__seg2

- idx: 140
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Moving to B shifts from a single-document WPT champions retrieval to many targeted per-player queries that must hit exact player pages/infobox lines and extract numeric 'WSOP bracelets' tokens. This requires adding precise entity/title tokens and changes the query shape to numerous small, exact-match retrievals.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.9
- why: B requires changing from a single-hop retrieval that fetches a consolidated WPT champions list to a multi-hop pattern that must retrieve many player-specific bios and explicitly look for ‘WSOP bracelet’ counts — adding new bridge-relation tokens and expanding the query shape from one document to many per-player queries.

## 149__split0__seg0

- idx: 149
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.86
- why: Both transitions make the same BM25-facing shift: from a multi-term, synonym-rich recall query to concise, high‑precision entity-equivalence/etymology queries that swap noisy terms for the same bridge tokens (e.g., 'hulder + Huld + Holda' with 'etymology'/'same being'/'völva') and prioritize authoritative sources. The implied token changes, removal of distractors, and query-shape tightening are materially similar.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: R0_base uses a multi-term, synonym-rich, verbose query (lots of role/variant terms) that must be trimmed and refocused into a compact, high-precision entity-equivalence query; A already prescribes concise pairwise/etymology queries so its shift to the target is much smaller.

## 149__split1__seg0

- idx: 149
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.8
- why: Segment A requires dropping the Holda/Frau Holle anchors and pivoting from a broad identity-query to philological/etymology queries that emphasize name-root tokens (huldr/huld) and role terms (völva) and avoid cultural/identity pages—a bigger shift in retrieval anchors and keywords than B's tighter, still identity-focused narrowing.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.82
- why: B introduces a new anchor entity (Holda/Frau Holle) and shifts the retrieval goal from strict philological/etymology matches to explicit comparative-identity claims, adding bridge-relation tokens like 'same as'/'identified with' and broadening candidate linking — a bigger change than A's narrowing from a multi-term synonym-rich query to higher-precision pairwise queries.

## 149__split2__seg1

- idx: 149
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Transition B shifts from a focused etymology/Huld-as-völva query to a broader comparative-mythology search adding Holda/Holda/Frau Holle variants, cognacy/parallels keywords, medieval-source relation tokens and a wider candidate set — a bigger change in bridge-relation and retrieval breadth than A's precise identity-targeting queries.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.93
- why: Transition A requires adding new anchor tokens (Holda / Frau Holle) and explicit identity-bridge keywords (e.g., 'same as', 'identical', 'Huld ↔ Holda') and shifting from broad etymology/role queries to high-precision identity queries—a larger change in token set and bridge-relation targeting than B's refinement of comparative-mythology evidence into authoritative statements.

## 149__split3__seg2

- idx: 149
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.75
- why: A requires a tighter, high‑precision BM25 query shift: move from broader comparative/motif queries to concise identity/etymology pairwise queries (add explicit identity tokens like 'same as'/'identity', prioritize encyclopedia/etymology sources, drop broader motif/attestation keywords). This is a bigger change in query shape and source targeting than B's move toward more attestations and motif-parallel searches, which is largely a lateral expansion of the existing comparative query behavior.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: Transition B requires a bigger BM25 shift: from broad, motif- and attestation-focused queries (many variant anchors, primary-source and trait keywords) to very narrow, high‑precision pairwise etymology/identity queries (exact pairings like 'hulder Huld etymology' or 'hulder same as Holda') — a substantial change in query shape and token precision.

## 150__split0__seg0

- idx: 150
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.72
- why: Both transitions require essentially the same, small BM25 query-control changes: target the same entity tokens (Paul Winters, 2012 Wayne State Warriors, Wayne State University) and short bridge keywords ('head coach', 'represented'); neither introduces new disambiguation, broader candidate sets, or removal of extra noisy terms.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: A requires shifting from a verbose, multi-token/noisy query (Tom Adams Field, GLIAC, Detroit, history) toward compact, entity-focused queries that drop distractors and target exact affiliation lines; B is already a compact, affiliation-focused midpoint with little change to reach the target.

## 150__split1__seg0

- idx: 150
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.81
- why: Both transitions require essentially the same BM25 query-control change: move from broader multi-season/program queries to compact, title-targeted or phrase-focused queries that surface the 2012 season page and Paul Winters' coach/bio lead lines. They imply near-identical anchor, bridge, and query-shape edits.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.87
- why: R0_base uses a long, noisy multi-term query (biography, history, venue, conference, city) and returns a broad candidate set; moving to the to_state requires stripping distractors and re-shaping the query into tight phrase/title-targeted queries that surface exact affiliation lines. A already targets season/coach titles, so it needs a smaller, local tightening.

## 150__split2__seg2

- idx: 150
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.81
- why: Segment B moves retrieval from compact, phrase-focused affiliation lookups toward a broader entity-focused candidate set (multiple season pages and coach pages) that tolerates extra season/stadium noise — a bigger shift in query targeting and result breadth than A’s change to precise page-title lookups.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.9
- why: Both transitions imply nearly identical BM25 query-control changes: entity/title-focused queries targeting the 2012 team and Paul Winters, same anchor tokens, similar noisy distractors, and identical query-shape implications. Neither requires a broader shift in tokens or retrieval strategy.

## 169__split0__seg0

- idx: 169
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: B moves from the base to a stricter BM25 query-control regime (exact-phrase quoting, site/source filters, explicit avoidance of noisy fan/forum pages and prioritization of authoritative obituaries/databases). A is a modest narrowing (conjunctive short queries and alias mapping) and thus requires a smaller change.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.79
- why: R0_base contains a noisy, multi-phrase freeform query and retrieved noisy distractor titles; moving to Rstar_target requires greater pruning of distracting tokens and tightening into focused exact-phrase/site-filter queries (removing extraneous names and location/detail chatter) than the already-focused Rmid_iter1.

## 169__split1__seg0

- idx: 169
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.78
- why: Transition B adds stricter exact-phrase + site-filter query shape and an explicit extra targeted check for 'Bud Ekins Bullitt' (additional anchor/surface token), shifting retrieval from a single focused credit check to multiple precise, source-filtered queries—a larger BM25 query-control change than A, which only narrows toward The Great Escape without aggressive site-filtering or the extra Bullitt query.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.75
- why: Transition B introduces an additional anchor (explicitly adds 'Bullitt') while also tightening query shape to exact-phrase + site/source filters and prioritizing primary-credit sources — a broader BM25-facing change (new entity tokens plus stricter phrase/site constraints) compared with A’s mainly query-shape tightening.

## 180__split0__seg0

- idx: 180
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: answer_type
- confidence: 0.86
- why: A requires an extra retrieval hop for the album's release date (adding date/answer-type tokens and precise album-page targeting) beyond merely identifying the 11th-album title in B, so it changes BM25 query shape and answer-type constraints more.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.83
- why: A moves from a discography/ordinal-confirmation focus (identify the 11th album title) to also requiring explicit release-date retrieval and band-identity confirmation — adding answer-type tokens (release date), a second-hop album-page query, and a broader two-step query shape. B already contains release-date and artist-identification tokens, so its change to the target is smaller.

## 180__split1__seg1

- idx: 180
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: answer_type
- confidence: 0.75
- why: B moves beyond discography-level ordinal confirmation to explicit album-page retrievals and full release-date extraction, requiring additional exact album-title tokens and 'release date' answer-type keywords (more precise title targeting and extra query shape changes).

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.84
- why: A adds a new verification step requiring the 'highest-selling Canadian heavy metal group' qualifier to be resolved (queries must include/target the phrase 'highest-selling' or equivalent authoritative bios) and requests the album release year—broadening candidate set and adding disambiguation/verification tokens versus B's narrow task of just counting studio albums.

## 180__split2__seg2

- idx: 180
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Transition B expands BM25 behavior from confirming band identity and picking the 11th-album page to an exhaustive multi-source collection of release-date variants — it requires adding many new query-control tokens (site/database names like Discogs/AllMusic/MusicBrainz, 'official site', 'press release', region-specific qualifiers), broader candidate-sourcing and de-duplication logic rather than the focused discography/album-title targeting in A.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Transition A moves from an album-specific, narrow retrieval state (album page + databases) to a state that first must identify the band and determine the 11th album via the band's discography — adding new anchor/entity tokens (band name, discography) and bridge queries rather than just extending date-detail queries. B only extends a year-to-full-date retrieval for an already-identified album.

## 180__split3__seg2

- idx: 180
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.67
- why: Moving to state B requires a bigger BM25-query shift from general album+date lookups to precise, targeted queries that include the exact album title string, label and catalog-number/edition identifiers, and region-of-first-release tokens — i.e., new exact surface-form tokens and much narrower candidate targeting — whereas A stays on the same album-focused path and mainly adds ‘release date’ / source keywords.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.87
- why: B moves from a band-identification/discography query (confirm 'highest-selling Canadian heavy metal group' = Annihilator and find the 11th-album title) to focused album-release-date retrieval, requiring a switch from broad band/profile tokens to precise album-title, label/catalog, region and date-keyword tokens—a larger BM25 query shift than A's local move from catalog/metadata gathering to extracting dates on the same album pages.

## 227__split0__seg0

- idx: 227
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.82
- why: A requires removing the publisher token and comic-page targets from the mixed actor+publisher query and refocusing retrieval toward narrow actor->role filmography/cast sources (avoid comic-book pages and series noise). That is a larger shift in evidence type and candidate-set targeting than B’s simpler entity-to-entity exact-name checks.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.84
- why: A's from_state intentionally avoids comic-book/publisher pages and uses narrow actor+role/filmography queries; reaching the target requires adding exact character-page and publisher tokens and switching retrieval focus to character->publisher relation. B already contains actor+character+Marvel tokens, so it needs a smaller query-change.

## 227__split1__seg1

- idx: 227
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: B requires a larger BM25 query shift: you must drop the actor-centric anchors (Evan Peters / filmography) and switch to character/comics-focused queries (Quicksilver (Pietro Maximoff) + publisher/infobox tokens), changing candidate set from film pages to comic-character pages and actively avoiding actor/noisy movie results. A is a smaller additive change (keep actor+role tokens and just add a publisher check).

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.82
- why: Moving A goes from a narrowly targeted comics/character query (Quicksilver publisher) that explicitly avoids actor pages to a target that requires adding actor tokens and actor→character bridge queries (Evan Peters→Quicksilver) plus publisher checks. That introduces new anchor tokens, a different retrieval focus (filmography/cast pages vs. comics infoboxes), broader candidate sets and a change in query shape — a bigger BM25 query-control shift than B, which merely adds a comics publisher lookup to an already actor-focused query.

## 247__split0__seg0

- idx: 247
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.77
- why: Transition B requires more substantive BM25 query-control changes: shifting from a compact actor+event keyword query to source‑type filtering (news/social media), adding phrase-level tokens like 'quoted hashtag'/'online petition', and enabling wildcard/substring hashtag matching — a broader query‑shape and matching-mode change than the relatively token-preserving shift in A.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.84
- why: Segment B moves from a vague, wildcard/OR, news‑social focus with no concrete query tokens to a compact, token‑rich target requiring exact campaign/hashtag and event tokens — a bigger BM25 query-shape and tokenization change than A, which already contained those tokens.

## 247__split1__seg0

- idx: 247
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: A requires shifting retrieval to a different candidate set and query shape — constraining to Ghana-focused news domains and local activist social pages (site/domain anchoring and social-media link/embed hunting) which is a bigger BM25 change than B’s mainly token-level refinements (wildcarded hashtags and actor/medium term combos).

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.72
- why: Transition B moves from a broad, detainee/Gitmo‑focused query (many noisy list/timeline pages) to a tightly shaped search for social‑media/news reproductions of campaign identifiers — requiring addition of media/hashtag/petition tokens, domain/source constraints, wildcard hashtag patterns and removal of noisy detainee-list terms, a bigger change than the localized tweak in A.

## 247__split2__seg0

- idx: 247
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: Transition B requires a stronger BM25-query-shift: it narrows candidate set via explicit site restrictions (site:ghanaweb/joyonline/change.org) and adds platform-specific anchors (Change.org, petition URLs) versus A's broader local-news/social-media focus and phrase-search tweaks.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.87
- why: A moves from a broad, general Gitmo/detainee query (which retrieves lists, timelines, and detainee bios) to a very different BM25 control: tightly constrained site/domain targeting (Ghanaian news + social platforms), plus adding campaign-specific tokens (petition, hashtag, Change.org, Facebook/Twitter). This is a bigger shift in query shape, anchor domains, and bridge-relation keywords than B, which is a narrower refinement among already targeted local/petition sources.

## 262__split0__seg0

- idx: 262
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.8
- why: Transition B shifts from a noisy/multi-entity query to a compact, exact-title+role query (adding the precise anchor 'Xenoblade Chronicles X' and 'character designer' while removing distractors like 'Xenosaga'/'KOS-MOS'), requiring a larger change in BM25 query tokens and targeting behavior.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: A moves from a broad, designer-centric search (filmography/credits queries with many noisy Xeno-related terms) to a compact exact-entity query targeting the specific game + role (adding the Xenoblade Chronicles X title token and 'character designer'), a substantive shift in anchor tokens and narrowing of candidate set.

## 262__split1__seg0

- idx: 262
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.88
- why: A requires shifting from a designer-centric query to a game-centric one: replace the anchor entity (Kunihiko Tanaka) with the exact game title and developer tokens ("Xenoblade Chronicles X", "Monolith Soft") and add credits/staff retrieval keywords (e.g., "credits", "character designer"). That is a bigger BM25-facing change than B, which stays designer-focused and mainly narrows to a filmography/credits page for Kunihiko Tanaka.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.86
- why: R0 -> designer-centric requires removing multiple noisy franchise/developer tokens (Xenosaga, KOS‑MOS, Monolith-focused phrasing) and shifting from a game-title+developer credit query to a designer-filmography query — a bigger change in anchor tokens and query target than the cleaner game-centric -> designer-centric move in B.

## 262__split3__seg2

- idx: 262
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Transition B shifts the retrieval anchor from a game-focused, per-title evidence search to a person-centric filmography search — requiring different primary tokens (designer name + 'filmography/credits/profile' and person-profile sites), a much broader candidate set of works to scan, and stronger avoidance of other Xeno-series noise. Transition A is a narrower pivot toward game-credit pages and reuses many of the same title-focused tokens.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.8
- why: Segment B starts from narrow, title-centric/aggregator credit queries (Xenoblade Chronicles X credits, MobyGames/Giant Bomb, manual scans) and must shift to person-centric filmography queries — a larger replacement of precise title/site tokens and credit-specific phrasing than A, which already includes the designer name and artifact-oriented queries.
