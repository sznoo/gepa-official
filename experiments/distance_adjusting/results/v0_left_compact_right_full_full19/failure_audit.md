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
- dominant_gap_type: anchor
- confidence: 0.83
- why: Segment B changes retrieval focus from a generic search for 'Solo' to an explicit disambiguation step: it introduces a clear intent to resolve which 'Solo' (Australian vs Norwegian) is meant and adds manufacturer/distributor anchors (Schweppes Australia/Asahi). This is a substantive entity-anchor correction that shifts evidence family and improves answerability, whereas A mostly keeps the original focus and already shows the desired Solo title in results.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A moves from an abstract disambiguation midpoint with no retrieved titles and a broad retrieval focus into a concrete target state that includes the specific 'Solo (Australian soft drink)' hit. This involves a larger shift in retrieval focus (resolving the ambiguous 'Solo' anchor and selecting the correct regional entity) compared with Segment B, which already began with a specific, targeted query and similar retrieved titles—so B's update is smaller/confirmatory.

## 108__split2__seg2

- idx: 108
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A makes a larger retrieval jump: it goes to the endpoint state with concrete retrieved titles (including 'Solo (Australian soft drink)') and a clear retrieval focus to fetch the Solo page and production country. This produces a larger change in evidence and answerability compared with B, which is an intermediate disambiguation step that only narrows scope without reaching the final target.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment B moves from an ambiguous / disambiguation-focused retrieval to a targeted product page, resolving which 'Solo' is intended. This is a substantive anchor/entity-disambiguation correction (changing retrieval focus and evidence family), whereas A already targeted the Australian Solo and is a smaller, more direct refinement.

## 118__split0__seg0

- idx: 118
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Segment B moves from a generic instruction to locate cast lists to concrete, targeted retrieval: it adds specific performer anchors (e.g., Deborah Kerr, Donna Reed, Kim Basinger) and retrieved titles that point to candidate matches. This is a bigger shift in retrieval focus and requires correcting/anchoring against particular entity names to resolve the question, whereas A mainly refines disambiguation and planning without introducing specific entity candidates.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A moves from an abstract/disambiguation midpoint with no retrieved titles to a concrete target state that introduces specific film pages and named actor anchors (e.g., Deborah Kerr, Donna Reed) and a clear cast-focused retrieval goal, representing a larger shift in retrieval focus and answerability. Segment B already starts with explicit cast queries and related retrieved titles, so its transition is much smaller.

## 132__split0__seg0

- idx: 132
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.74
- why: Segment B tightens the retrieval focus from a broad Björk biography to a specific query shape seeking the Selmasongs album page and explicit soundtrack/liner-credit sources. This is a substantive narrowing of search strategy and bridge clues (soundtrack credits) compared with A’s more confirmatory endpoint refinement.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why: Segment B moves from a broad, multi-topic biography/discography/filmography query (with many noisy clues) to a tightly targeted endpoint focused on the Selmasongs soundtrack and artist — a substantial narrowing and refocusing of the query. Segment A is already narrowly focused on soundtrack/album credit sources, so its change to the same target is much smaller.

## 132__split3__seg0

- idx: 132
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.77
- why: Segment B shifts the evidence family more substantially — from music/album database searches to film-level credits and encyclopedia lead paragraphs that both tie the soundtrack to the performer and explicitly list occupations. This adds an answer-type verification (confirming the performer’s occupations) and a different bridge (film credits) rather than just narrowing to album pages, so it represents a larger retrieval-focus change.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.72
- why: Segment A makes a bigger shift from a broad, biography/discography and birthdate–oriented retrieval focus to a narrowly targeted album/soundtrack–credits search (Selmasongs). This requires dropping broader biographical anchors and noisy discography items and reshaping the query to album-level authoritative sources — a larger change in retrieval focus and query shape than B, which was already film/encyclopedia-focused and only needed a modest pivot to album entries.

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
- confidence: 0.78
- why: Segment B moves from the planning/base state to a concrete endpoint: it changes retrieval focus from tentative verification to definitive confirmation of which WPT champion has four WSOP bracelets and to retrieving that person's birth date. It also adjusts the retrieved results (adds different candidate titles) and thus represents a bigger shift in evidence/focus than A's intermediate verification plan.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.84
- why: Segment A shows a much bigger shift: its from_state is a generated midpoint with no retrieved titles and a narrow verification focus (is Danzer a WPT champion?), while its to_state is the full target requiring identifying the correct WPT champion and extracting a birth date. B's from_state already contains a concrete query, retrieved titles, and the same retrieval focus as its to_state, so B entails a smaller update.

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
- dominant_gap_type: answer_type
- confidence: 0.82
- why: Segment B requires a deeper, more concrete retrieval and extraction step: given the WPT winners it must fetch individual authoritative biographical/WSOP records and extract explicit numeric bracelet counts for each name (a per-entity attribute-mapping). Segment A only narrows/filter the champions list to produce a shortlist of candidates with four bracelets (higher-level cross-referencing). B therefore changes the retrieval focus more (from list-level to per-player evidence extraction) and demands larger entity-attribute resolution.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Segment B's from_state is a single-hop retrieval that only extracts a WPT winners list (names). Its to_state requires adding a second retrieval step for each extracted name to obtain WSOP bracelet counts and then filter to four-bracelet winners — a substantial added retrieval/processing step. By contrast, Segment A's from_state already gathers per-player bracelet counts and the to_state merely filters that existing mapping to a shortlist, a much smaller change.

## 149__split0__seg0

- idx: 149
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Segment A makes a stronger, more focused change in retrieval intent: it narrows from a broad hunt for related pages to explicitly seeking authoritative etymology and comparative-mythology statements (including an explicit identity sentence linking hulder to Huld/Holda). B mainly adjusts retrieved titles but keeps the same high-level goal. A therefore represents a larger retrieval-focus and bridge-relation update.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.85
- why: Segment A moves from an abstract, narrow retrieval plan (no retrieved titles listed) to a concrete target state with key authoritative pages added (Hulder, Huld, Holda, Skogsrå). This is a substantive shift from planning to actual entity-focused retrieval/evidence—whereas segment B already contained a similar set of retrieved titles and an equivalent retrieval focus, so its transition is much smaller.

## 149__split1__seg0

- idx: 149
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.84
- why: Segment B shifts the retrieval focus from a cautious etymology-only probe to actively seeking explicit, authoritative identity claims linking hulder → Huld and Huld → Holda/Frau Holle. That adds a stronger comparative-mythology/identity search (more anchors and a different evidence family) rather than just philological/name‑origin material in A.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.83
- why: Segment B changes the retrieval focus from a narrow etymology/role check (hulder ← huld; Huld as völva) to explicitly asserting and seeking the Huld↔Holda/Frau Holle identity. That adds a new anchor/entity (Holda/Frau Holle) and a substantive bridge-relation (identity/equivalence) and shifts the expected evidence family (from philological entries to comparative-mythology identity claims). Segment A is mostly a precision narrowing of similar anchors and expectations, so B represents the larger update.

## 149__split3__seg2

- idx: 149
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Segment B shifts retrieval from a general comparative claim-seeking focus to a substantially broader evidence search: it adds many new anchors (attestations of Huld/Huldr, primary medieval/early‑modern passages, völva/seiðr context, name‑form variants) and expands the evidence family to include primary sources and motif comparisons rather than just concise encyclopedic identity statements. This is a bigger retrieval-focus and anchor/evidence-family change than A’s tighter narrowing to authoritative etymology and one-line identity claims.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.8
- why: Segment B shifts from collecting intermediate comparative attestations, motifs and primary-source parallels (a broad evidence-assembly task) to a narrow, high-precision search for authoritative, explicit identity/etymology claims. That is a bigger change in retrieval focus and evidence family than A, which already aimed toward comparative-mythology linking and only modestly narrowed to authoritative etymology.

## 150__split0__seg0

- idx: 150
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.78
- why: Segment B moves from a general base focus to a concrete target that adds the coach's page to retrieved results and seeks an authoritative, short affiliation statement tying both entities to Wayne State University. This introduces a new explicit anchor (Paul Winters page) and shifts retrieval toward definitive evidence, a larger retrieval-focus and anchor correction than A's minor confirmation refinement.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment B moves from an empty/undeveloped retrieval state (no retrieved titles) to a focused target state with multiple concrete anchors (team page and Paul Winters coach page) and explicit evidence targets. This is a bigger change than A, which mainly refines an already-populated retrieval set by swapping some season pages and adding the Paul Winters title—i.e., A is a narrower refinement, while B is an initial, substantive anchor/evidence addition.

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
- confidence: 0.4
- why: Both segments make nearly identical, small refinements to the retrieval focus toward the same primary pages (the 2012 season page and Paul Winters/coach bio) to confirm affiliation. Segment A is marginally broader (adds program overview/roster as possible sources) but not a materially larger change in retrieval focus or anchor/bridge correction. No segment shows a clear bigger-step update.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Segment B transitions from a broad, noisy initial retrieval (explicit query and many season/historical hits) to a focused confirmation of the institution, removing temporal/historical noise and narrowing to exact affiliation lines. Segment A is already narrowly targeted and shows only a small refinement, so B exhibits the larger retrieval-focus and evidence-shape change.

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
- confidence: 0.86
- why: Segment B moves from a generic confirmation focus to an endpoint state that lists specific retrieved pages and a clearer authoritative-evidence retrieval aim. It introduces concrete retrieved_titles and a stronger shift in retrieval targets (team, coach, and program pages), representing a larger change in retrieval focus and evidence gathering than the modest specificity increase in A.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.85
- why: Both segments show nearly identical retrieval-focus, anchors, bridge clues, noisy clues, and expected evidence types (finding short affiliation lines tying both entities to Wayne State University). There is no meaningful difference in entity-anchor, bridge-relation, answerability, or query-shape change between A and B.

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
- confidence: 0.81
- why: Segment A advances from confirming the target band to both identifying the 11th studio album and retrieving its official release date. B only determines the album's ordinal title (stops before getting the date). A therefore requires a larger shift in retrieval focus and an added answer-type (date) lookup plus confirmation of the entity, so it is a bigger update.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.82
- why: Segment A's from_state is narrowly focused on confirming the 11th studio album title only and explicitly defers the release date. Its to_state expands scope to include band identification (confirming Annihilator) plus retrieving the album's official release date and adds multiple retrieved album titles — a substantive change in retrieval focus and required evidence. Segment B's from_state already encompassed both band confirmation and release-date retrieval, so its transition to the same to_state is much smaller.

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
- dominant_gap_type: anchor
- confidence: 0.75
- why: Segment A makes a larger shift in retrieval focus and evidence family: it narrows from a combined actor+publisher goal to specifically targeting actor->role confirmation via filmography/cast lists (different anchors and sources such as IMDb, cast pages, news). This is a substantive anchor/evidence-type change compared with B, which mostly consolidates existing actor+publisher targets and adds expected titles (a smaller, confirmatory update).

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.82
- why: Segment A’s from_state is a narrow, intentionally actor->role focused midpoint that avoids publisher pages; to reach the target it must add the additional bridge linking the confirmed character (Quicksilver) to its publisher (Marvel Comics) and broaden retrieval scope. B already includes actor+publisher in its initial query and retrieved titles, so B requires a smaller change.

## 227__split1__seg1

- idx: 227
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.76
- why: Segment B makes a bigger pivot in retrieval focus: it moves away from actor/filmography verification to authoritative comic‑book/character sources and publisher metadata, replacing the Evan Peters anchor with a publisher/infobox anchor and requiring a different evidence family (publication history/infobox) — a larger entity-anchor and evidence-type change than A, which mainly combines actor and character confirmation.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.64
- why: Segment B requires a larger shift in retrieval focus: it moves from an actor/filmography evidence family (cast lists, IMDb, news about Evan Peters) to additionally retrieving comics/publisher sources that were explicitly excluded in the from_state. That introduces a new evidence family and a new entity anchor (publisher/comics pages) and therefore a bigger bridge relation change than A, which only adds the actor anchor to an already comics-focused search.

## 227__split2__seg1

- idx: 227
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.78
- why: Segment B shifts the retrieval focus from actor/filmography verification to a different evidence family — authoritative comic-book character pages and publisher information — requiring a new bridge (character→publisher). This is a larger change than A, which is an alias/identity refinement (confirming Pietro Maximoff) within the same actor→character focus.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.78
- why: Both segments perform essentially the same retrieval-step: they start by confirming Evan Peters' association with Quicksilver/Pietro Maximoff (actor->role) and then shift to retrieving the Quicksilver comics entry to confirm publisher (character->Marvel). The retrieval-focus change, required bridge corrections, noisy-clue risks, and final evidence type are nearly identical, so no segment shows a clearly larger update magnitude.

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
- confidence: 0.74
- why: Segment B changes the retrieval focus more substantially: it narrows the search to contemporary news and social‑media coverage and explicitly requests quoted campaign identifiers (hashtags, e‑petitions, Facebook/Twitter campaign names) and links to OccupyGhana/NPP statements. That is a stronger, more specific shift in query shape and bridging clues than A, which retains the original endpoint goal with only modest refinement.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.83
- why: Segment B moves from a largely empty/generated midpoint (no retrieved titles, no explicit query) to a full endpoint that explicitly shifts the retrieval focus to contemporary news and social‑media coverage (quoted hashtags, e‑petitions, embedded tweets). This is a bigger change in evidence family and retrieval focus than A, which mainly refines wording and retrieved titles but keeps the same anchor set and bridge clues.

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
- confidence: 0.74
- why: Segment A imposes a stronger, concrete anchor shift — it narrows retrieval to Ghana-focused news outlets and specific local sites (GhanaWeb, JoyOnline, Citi Newsroom, Graphic Online) and local activist social pages, and adds new bridge clues (Change.org, Facebook campaign, press-release links). B is a finer content-level narrowing (looking for quoted identifiers) but does not introduce as many new entity/source anchors.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why: Segment B moves from the broad base endpoint query to a much more focused retrieval posture that requires explicit evidence-format constraints (contemporary news/social embeds that quote or reproduce campaign identifiers and tie them to OccupyGhana/NPP). This is a bigger shift in retrieval focus and expected evidence family than A, which is only a tighter refinement of an already Ghana-focused search.

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
- dominant_gap_type: anchor
- confidence: 0.8
- why: Segment B makes a stronger retrieval shift: it narrows focus to specific high-yield sources (GhanaWeb, JoyOnline, Change.org) and OccupyGhana social accounts and introduces platform-specific evidence targets (petition titles/URLs, embedded tweets/hashtags). This is a bigger change in anchors and query shape than A's broader Ghana-focused refinement.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.78
- why: Segment A moves from a broad Gitmo/detainee-focused retrieval (general lists and timelines) to a sharply constrained focus on Ghanaian news outlets and activist social pages looking specifically for named online campaigns/hashtags — a substantive anchor and query-shape narrowing. By contrast, B is a smaller refinement between two already-localized midpoints (targeting specific sites/platforms), so its change is smaller.

## 262__split0__seg0

- idx: 262
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A shifts the retrieval focus from finding a game/developer credits page to a designer-centric filmography/credits search — a substantial change in anchor and evidence family requiring different queries and sources (designer portfolio/Wikipedia/MobyGames) rather than game pages. Segment B is a narrower, target-confirming refinement of the original focus.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.84
- why: Segment A changes retrieval focus more: it moves from a general, designer-centric filmography/credits search for Kunihiko Tanaka to an explicit, title-targeted verification (Xenoblade Chronicles X) and shifts the query shape toward exact-entity confirmation. Segment B shows only a minor restatement of a similar game-credits target. A therefore requires a larger anchor/target and query-shape correction.

## 267__split0__seg0

- idx: 267
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: noisy_entity
- confidence: 0.75
- why: Segment B performs a substantive strategy shift: it moves from a name- and episode-heavy retrieval to a concise, show-level focus that explicitly prioritizes the Smallville main article, episode list, and creator bios (removing noisy person/episode hits). That is a larger change in retrieval focus and correction of noisy-entity hits than A, which only slightly adjusted retrieved titles and aimed at the same endpoint.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.8
- why: Segment B moves from a long, name- and episode-heavy query that retrieved many episode and person pages (noisy, episode-level focus) to a concise, show-level target that centers on the primary creators. This is a larger retrieval-focus and query-shape correction than A, whose from-state was already reframed toward show-level anchors (Alfred Gough, Miles Millar) and thus required a smaller adjustment.

## 267__split1__seg0

- idx: 267
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.8
- why: Both segments perform essentially the same update: they reduce a long, name-heavy query to concise, show-level retrieval targets (Smallville main article, List of Smallville episodes, and bios for Alfred Gough and Miles Millar). The anchors, bridge clues, and stated retrieval focus are nearly identical, so neither segment represents a larger change in retrieval focus or correction.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment B moves from a long, name-heavy endpoint query that returns many episode/person pages (noisy, fragmented results) to a concise, show-focused retrieval anchored on the series and its two creators. This is a bigger shift in retrieval focus and query shape (removing many noisy entity terms and episode pages) than Segment A, which is a smaller refinement between two already similar midpoints.

## 267__split2__seg0

- idx: 267
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.65
- why: Both segments make a very similar, modest narrowing of the original long, name-heavy query to authoritative show-level sources and the two primary creators. Neither introduces a substantially different anchor, corrects a major noisy entity, or changes answerability; differences (A keeping the actor link explicit, B mentioning press/industry sources) are minor and do not justify preferring one over the other.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.88
- why: Segment A makes a substantial retrieval-focus change: it collapses a long, name- and episode-heavy query into a concise show-plus-creators shape by removing many peripheral writer and episode anchors, shifting retrieval from scattered person/episode pages to authoritative series- and creator-level sources. Segment B is a minor rewording/narrowing that largely matches the same target state and therefore represents a much smaller update.

## 267__split3__seg0

- idx: 267
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.74
- why: Both segments perform the same, modest narrowing of the retrieval focus from a long, name-heavy query to authoritative series-level sources (Smallville main article and creator bios for Alfred Gough and Miles Millar) while retaining Justin Hartley as a casting bridge. The only minor difference is that A explicitly avoids episode pages whereas B still targets the consolidated 'List of Smallville episodes' credits page; this is a small implementation detail and does not constitute a substantially larger retrieval update.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment A moves from a long, name-heavy, noisy query that biased retrieval toward episode and person pages to a much narrower, show-level focus (Smallville main article, episode-list, and creator bios). That is a larger change in retrieval focus and correction of noisy inputs than B, which starts already modestly focused and only tightens to the same show-level targets.

## 55__split0__seg0

- idx: 55
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
- why: Segment B adds explicit, new anchors and evidence (e.g., 'Capital of the Netherlands', 'Netherlands', additional retrieved titles) and shifts the retrieval to verify both entities' national/cultural linkage — a larger change in retrieval focus and evidence family than A, which mainly narrows to confirming the film's nationality as an intermediate step.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.88
- why: Segment A moves from a narrow film-centric lookup (establishing Amsterdamned as a Dutch 1988 film) to a broader verification that links that film to the city/Capital (Amsterdam) and Dutch culture. It introduces a new primary anchor (Amsterdam/Capital of the Netherlands) and expands the retrieval focus and required evidence (single-entity film metadata → cross-entity shared-culture confirmation), a larger change than B which already contained both anchors.

## 55__split1__seg1

- idx: 55
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.88
- why: Segment A moves from a film-focused midstate to the endpoint that explicitly brings in the city (Amsterdam), the Capital-of-the-Netherlands page, and the explicit ‘Dutch culture’ anchor — shifting retrieval from verifying a single entity’s nationality to synthesizing both entities and confirming shared culture (answerability/evidence-family change). This is a larger retrieval-focus and anchor addition than B’s complementary city-focused midstep.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.55
- why: Both segments perform nearly symmetric updates: A moves from a film-centric focus (Amsterdamned) to a joint verification including Amsterdam and Dutch culture, while B moves from a city/capital focus (Amsterdam) to the same joint verification including the film. Each requires adding the other entity as an anchor and confirming shared Dutch nationality; neither involves a substantially larger bridge, correction, or answerability change.

## 55__split3__seg1

- idx: 55
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Segment B shifts focus from confirming the film's nationality to a new, distinct retrieval goal: verifying Amsterdam's status as the capital of the Netherlands. That introduces a new entity-role anchor ('capital of the Netherlands') and a different evidence family (infobox/lede confirmation of city status) rather than merely linking both items as 'Dutch' as in A, so it represents a larger retrieval-change.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.84
- why: Segment A shifts retrieval from a narrow film-only focus (confirming Amsterdamned's metadata) to a comparative goal that brings in a new primary entity (Amsterdam) and must explicitly link the film and the city via a shared national/cultural label. That requires adding an entity anchor plus establishing the bridge relation (both are 'Dutch'), a bigger change than B, which starts already focused on Amsterdam and only needs to add/verify the film's shared label.

## 6__split0__seg0

- idx: 6
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A introduces a concrete retrieval target (the Shenandoah River page) and refines the retrieval focus to confirm which states the river passes through, adding an explicit entity anchor and shifting evidence-family toward an authoritative source. Segment B is only a generated midpoint with no new retrieved titles or concrete evidence added.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.8
- why: Segment B moves from a generated midpoint with no retrieved results and a more fork-level intent to an endpoint that includes the authoritative Shenandoah River page—a substantive addition of the main anchor/evidence source and a resolution of the key answerability gap. Segment A is a smaller, incremental correction (adding the Shenandoah page to an already focused query with distractors).

## 6__split1__seg1

- idx: 6
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: answer_type
- confidence: 0.78
- why: Segment B moves from a general midpoint focus to an endpoint with concrete retrieved titles (including a Shenandoah River page) and an explicit aim to confirm which states the river flows through, a bigger shift in answerability/evidence than A’s narrower refinement toward Harpers Ferry/lower-course clues.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.85
- why: Both segments perform very similar retrieval shifts: each moves from a fork- or landmark-focused search (linking the North Fork/Shenandoah to downstream landmarks like Harpers Ferry) to an endpoint that explicitly lists the states the Shenandoah River flows through. Neither requires substantially more entity correction, relation change, or a different evidence family than the other, so no single segment clearly has a larger update magnitude.
