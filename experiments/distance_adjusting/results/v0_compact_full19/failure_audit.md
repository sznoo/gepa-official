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
- confidence: 0.78
- why: Segment B introduces an explicit disambiguation step and expands the anchors/bridge clues (adds Norwegian variant, Schweppes Australia/Asahi distributor cues) and a new midpoint retrieval focus — a clearer change in retrieval focus and entity anchoring compared with A's minor refinement toward the same Solo page.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: Segment A moves from an empty/generated midpoint with no retrieved titles and a broad disambiguation focus to a concrete target state that includes the canonical 'Solo (Australian soft drink)' title and focused retrieval clues. This is a larger retrieval-focus and entity-anchor correction (resolving 'Solo' ambiguity) than B, which already started with a focused query and the Solo page present.

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
- dominant_gap_type: noisy_entity
- confidence: 0.78
- why: Segment B introduces a substantive shift in retrieval strategy: instead of directly fetching the Solo product page (A), it changes the query shape to explicitly disambiguate the 'Solo' entity first. That is a larger correction for noisy/ambiguous entity variants and changes the evidence-path (disambiguation → canonical page) rather than a simple extraction step.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment B performs an explicit disambiguation step—resolving which 'Solo' is intended and eliminating noisy variants before fetching the product page. That is a larger retrieval-focus change (anchor correction/ambiguity resolution) and a bigger evidence-family update than A, which already targeted the Solo (Australian) page directly.

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
- dominant_gap_type: noisy_entity
- confidence: 0.78
- why: Segment A shifts the retrieval focus to disambiguate the ambiguous title 'Third Person' and to construct candidate actor-sets per specific title/version (a structural query-shape and entity-disambiguation change). Segment B is a narrower, target-focused step that simply pulls authoritative cast lists and some actor anchors, so A requires a larger correction of noisy/ambiguous entity and a bigger change in query strategy.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.85
- why: Segment A moves from a disambiguation/planning state (broadly enumerating possible 'Third Person' works and candidate actress sets) to a targeted retrieval of authoritative cast lists for specific title/versions — a substantive shift in retrieval focus and resolution of ambiguous entity anchors. Segment B already starts with version-specific cast queries, so its transition is smaller.

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
- dominant_gap_type: anchor
- confidence: 0.74
- why: Segment B makes a concrete, high-impact shift from a broad disambiguation plan to committing to specific title-year anchors (Third Person → 2013 film; From Here to Eternity → 1953 film) and narrows the retrieval focus to top-billed female cast. This is a stronger change in retrieval focus and requires a larger entity-anchor correction and query-shape tightening than A’s more general endpoint request for authoritative cast lists.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.88
- why: Segment A moves from a broad disambiguation stance (listing all candidate 'Third Person' works and multiple versions of 'From Here to Eternity' and building actor sets per candidate) to targeted cast retrieval — a much larger change in retrieval focus and required anchor expansion/correction than B, which is already committed to a single-year pairing and only needs narrow cast lookups.

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
- dominant_gap_type: answer_type
- confidence: 0.75
- why: Segment B makes a more substantive shift in retrieval focus and evidence family: it narrows from a broad biography-centric search to album- and credit-oriented sources (Selmasongs credits, liner notes, music-database entries), correcting noisy birthdate/biography distractions and changing the expected evidence type. Segment A remains an endpoint-level restatement of the original goal (artist/biography or album page) and thus is a smaller refinement.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why: Segment B shows a bigger narrowing and correction: it moves from a broad, multi-term biography/discography query (including birthdate, filmography, Vespertine noise) to a tightly focused target that explicitly confirms soundtrack credit and occupations. Segment A is already mid-granularity and only makes a small refinement to entity/album-centric queries.

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
- confidence: 0.78
- why: Segment B changes the evidence family more strongly: it shifts from a generic artist/album lookup to film-level credits plus the lead of an encyclopedia entry to explicitly surface both the soundtrack performer and the performer’s listed occupations. That is a bigger retrieval-focus and answerability change than A’s narrower move to album-release/music-database pages.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment A shifts from a broad, entity-centric biography/discography query (including full-name, birthdate, occupations) to a narrowly focused album/soundtrack evidence family (music-database album pages). That is a bigger retrieval-focus and evidence-family change than B, which already targeted film-level credits/encyclopedia leads and only moves to album pages.

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
- dominant_gap_type: answer_type
- confidence: 0.85
- why: Segment B moves beyond mere verification of whether George Danzer is a WPT champion (segment A) to a full answer-oriented retrieval: it must both confirm the correct WPT champion who has four WSOP bracelets and extract the person's birth date. This is a larger shift in retrieval focus and expected evidence (from checking a winners list to acquiring biographical/date information and tying together bracelet count and WPT title).

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.87
- why: Segment A starts from a narrow, Danzer-specific verification state (single-hop check whether George Danzer is a WPT champion) and must expand to a full entity search: find the correct WPT champion with four WSOP bracelets and then retrieve that person's birth date. Segment B's from-state already contains the broader multi-step retrieval intent (includes birth date and WPT-champion disambiguation), so A requires a larger change in retrieval focus and evidence type.

## 140__split1__seg1

- idx: 140
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: answer_type
- confidence: 0.86
- why: Segment A moves to an endpoint requiring explicit confirmation of which WPT champion has four WSOP bracelets and retrieval of that person's birth date (a new answer-type: date). This is a bigger shift in retrieval focus and evidence requirements than B, which only builds an intermediate shortlist of candidate WPT winners (no date retrieval).

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.74
- why: Segment B moves from a shortlist-only, cross-referencing phase (scan WPT winners and filter by WSOP bracelet counts) to a final verification plus extracting the person's birth date. This adds a new retrieval target (a date) and requires resolving a bridge relation across multiple candidate entities before selecting the final subject—a larger change in retrieval focus and required evidence than A, which was already centered on verifying Danzer and only modestly extended to fetch a birth date.

## 149__split0__seg0

- idx: 149
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.78
- why: Segment A makes a clear, substantive shift in retrieval focus and query strategy: it narrows from a broad, multi-term synonym-rich search to high-precision pairwise queries aimed specifically at short definitional/etymological passages that explicitly state identity (e.g., 'the hulder is originally the same being as Huld'). It also prunes peripheral anchors (e.g., Tallemaja) and refocuses expected evidence type — a stronger, semantic change than B, which mainly shows a change in retrieved titles with persistent noisy items rather than a deeper query/evidence-type refinement.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.8
- why: Segment B starts from a broader R0 baseline with noisy/distraction hits (Spillaholle, Gussy Holl, 872 Holda, etc.) and an explicit multi-term query, then moves to a focused Rstar_target removing those noisy results and concentrating on authoritative Hulder/Huld/Holda pages. Segment A was already a narrowly targeted midpoint (explicitly aiming at etymology and identity claims) and its transition to the same target is minimal. Thus B requires the larger retrieval-correction (removing noisy hits and refocusing).

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
- confidence: 0.86
- why: Segment B expands and shifts the retrieval focus more: it adds Holda/Frau Holle as active anchors and demands explicit identity claims linking hulder → Huld and Huld ↔ Holda/Frau Holle (short definitional/comparative-mythology evidence). A only narrows to philological/etymological linkage and Huld's role as a völva, deferring the Holda equation. B therefore requires a larger bridge/identity correction and a stronger change in expected evidence.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Segment B introduces a substantive new retrieval goal: it moves from verifying name-root/role (hulder ← huld; Huld as völva) to additionally asserting and sourcing the explicit identity link Huld ↔ Holda/Frau Holle and the claim that hulder is originally the same being as Huld. This is a larger conceptual/bridge addition than A’s primarily precision-focused narrowing of query shape and source type.

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
- dominant_gap_type: answer_type
- confidence: 0.75
- why: Segment B shifts the retrieval focus more substantially: from a prior etymology/name-origin baseline it moves to a different evidence family (intermediate comparative material) that requires gathering primary attestations, motif-by-motif comparisons, and scholarly hypothesis arguments rather than just short etymological/encyclopedic identity lines. That is a broader change in what kinds of sources and query shapes are needed, whereas A is mainly a narrowing to high‑precision etymology/identity statements.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.8
- why: Segment B shifts from a broad, primary-source and motif-focused retrieval (documenting attestations of Huld/Huldr and Holda/Frau Holle and their overlapping traits) to a narrow, high‑precision demand for authoritative etymological and encyclopedic identity statements linking hulder → Huld and Huld ↔ Holda. That is a bigger change in retrieval focus and evidence-family (from gathering parallels/attestations to seeking explicit equivalence claims) than A, which was already moving toward comparative-mythology evidence connecting Huld and Holda and only refines to authoritative identity statements.

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
- confidence: 0.73
- why: Both segments make nearly identical, minimal refinements to the retrieval focus: target the 2012 season page and Paul Winters' bio to surface explicit affiliation lines. Neither introduces a new anchor, corrects a noisy entity, changes the bridge relation, or alters answerability — only minor wording differences about prioritizing lead-paragraph hits. No local order preference is justified.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.85
- why: Segment B moves from a broad, noisy initial state (explicit query and many retrieved season/history pages) to a tightly focused verification of on-page affiliation lines. This corrects noisy retrieval results and reshapes the query focus to exact affiliation snippets. Segment A is only a small refinement between two already-focused midpoints.

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
- dominant_gap_type: anchor
- confidence: 0.75
- why: Segment B moves from an empty retrieved set to a concrete list of retrieved titles (including the canonical 2012 team and Paul Winters pages plus related noisy season pages), representing a larger change in retrieval state than A, which only refines focus toward fetching those pages. B therefore captures a bigger step in resolving the entity/anchor targets and surfacing noisy alternatives.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.85
- why: Both segments show effectively the same retrieval-focus update: moving from a midpoint plan to fetching the canonical team and coach pages to confirm a short affiliation line linking both to Wayne State University. Anchors, bridge clues, noisy clues, expected evidence type, and query-shape implications are functionally identical, so neither segment exhibits a clearly larger change in retrieval focus, entity correction, or answerability.

## 150__split3__seg0

- idx: 150
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: A changes the retrieval focus more: it explicitly expands to target both the 2012 season page and a separate Paul Winters coach/bio page (an added entity anchor and an additional evidence family). B is a narrower, incremental step that only targets the season-page lead. A therefore requires a larger anchor/bridge retrieval update to fetch an extra authoritative source.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.78
- why: Segment B changes retrieval focus more substantially: it goes from targeting only the 2012 season-page lead to adding the coach/bio/program pages (introducing Paul Winters as an explicit new anchor and adding the bridge evidence needed to link team→coach→university). Segment A is mainly a refinement/narrowing of an already multi-page focus, not the addition of a new anchor or evidence family.

## 169__split0__seg0

- idx: 169
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.8
- why: B narrows the retrieval much more concretely: it adds prioritized authoritative-source anchors (obituary/Hall of Fame), explicit bridge phrases (exact 'stunt double' and 'performed the motorcycle jump'), and prescriptive query-shape guidance (exact-phrase + site filters and a focused follow-up for Bullitt). A is a milder refinement toward verifying The Great Escape and Bullitt but is less specific and omits the added source-anchor and operational query instructions.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.7
- why: Segment A transitions from a detailed, procedural midpoint (explicit source priorities, noise filters, anchor list and precise query-shape guidance) to the Rstar_target endpoint with finalized retrieval focus and concrete retrieved titles. That represents a bigger shift in retrieval strategy and query shape than B, which already starts as a straightforward base query/verification state and moves to the same endpoint.

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
- confidence: 0.82
- why: A advances the retrieval goal from confirming the likely band to a full endpoint: it not only anchors the entity (Annihilator) but also adds retrieving the 11th-album page and the album's official release date (a date-type answer). B only narrows the task to identifying the 11th album title (ordinal) and explicitly defers the release-date lookup, so A represents a larger change in retrieval focus and evidence-type requirements.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.86
- why: Segment A's from_state is a narrow midpoint focused only on confirming the 11th-album identity (no retrieved titles and explicitly defers the release date). Its to_state expands scope to the full endpoint: identifies the band, adds multiple retrieved album titles, and explicitly adds retrieval of the album's official release date. That is a larger shift (adds concrete anchors and a new answer-type/date retrieval) than B, whose from_state already contained similar retrieved titles and an endpoint-like retrieval_focus.

## 180__split2__seg2

- idx: 180
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.83
- why: Segment B moves beyond identifying the band/album to a complex evidence-assembly task: it requires opening the album page plus multiple external sources (infobox citations, label/band announcement, Discogs/MusicBrainz) and reconciling region-specific and reissue variants to produce candidate dates and provenance. That is a larger retrieval/evidence-family change than A, which is a more direct single-step extraction of an official release date once the album is identified.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.85
- why: Segment B moves from an ambiguous phrase to explicitly confirming the target band (resolving the 'highest-selling Canadian heavy metal group' reference) and determining the 11th studio-album title (an anchor/ordinal resolution), then expands scope from only the release year to the full official release date. This corrects an entity/noisy-mention and an ordinal-gap and changes answer-type/detail. Segment A mostly refines evidence for an already-identified album (collecting candidate dates/sources), which is a narrower, post-identification collation step.

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
- dominant_gap_type: query_shape
- confidence: 0.85
- why: Segment A makes a substantive shift in retrieval focus and query shape: it narrows from a dual actor->character+publisher goal to exclusively confirming Evan Peters portrayed Quicksilver, changing expected evidence type to filmography/cast credits and altering bridge clues and query-shape implications. Segment B mostly preserves the original dual-focus (actor->character plus publisher) and therefore is a smaller update.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A shifts retrieval focus more: its from_state intentionally avoids publisher pages and targets only confirming Evan Peters->Quicksilver, while its to_state (Rstar_target) adds the publisher/character confirmation (Marvel Comics + Quicksilver). This introduces a new entity-anchor and an added actor->character->publisher linkage that B already included in its from_state, so A requires a larger update.

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
- dominant_gap_type: query_shape
- confidence: 0.78
- why: Segment B requires a bigger shift in retrieval focus and evidence family: it moves from actor-centric filmography queries to comic-character/comics-publisher sources, intentionally avoiding actor pages and targeting infobox/publication history. That is a larger change in query shape and anchor (character→publisher) than A, which mainly augments the existing actor->character check with a publisher confirmation but stays actor-focused.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.75
- why: Both segments perform symmetric, large retrieval shifts: A moves from comics/publisher sources to add an actor (Evan Peters) anchor and actor-focused evidence; B moves from actor/filmography sources to add publisher/comic-character evidence. Each requires adding a new evidence family and an entity-anchor/bridge relation (actor↔character↔publisher). No clear local difference justifies preferring one over the other.

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
- confidence: 0.86
- why: B moves from a general retrieval focus to a much more specific, actionable search posture: it narrows to contemporary news/social‑media coverage that reproduces quoted hashtags/e‑petitions, adds explicit bridge clues (quoted hashtag, e‑petition, tweet embed), and prescribes concrete query construction (ORs, wildcards). This is a larger change in retrieval focus and query shape than A’s modest refinement.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.78
- why: Segment B moves from a generated midpoint with no query and no retrieved titles to a focused endpoint—requiring creation of a concrete query shape and retrieval of news/social posts (hashtags, petition titles). That is a bigger shift in retrieval focus and required query formation than A, which already had a specific query and many candidate titles.

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
- confidence: 0.78
- why: Segment A shifts retrieval focus more strongly toward new entity anchors (specific Ghanaian news outlets and local activist social pages), adding concrete site targets (GhanaWeb, JoyOnline, Citi, Graphic) and thus a larger anchor-level change from the original broad query. B mainly refines expected evidence format (quoted campaign identifiers and hashtag-wildcarding), which is a narrower query-shape/evidence tweak.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.87
- why: Segment B moves from a broad endpoint query (general keywords and many noisy detainee/list results) to a narrowly shaped retrieval that explicitly targets campaign identifiers (hashtags, petitions, embeds). This is a larger shift in retrieval focus and query shape and involves removing noisy/distractor sources, whereas A is a smaller refinement between two already-Ghana-focused midpoints.

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
- confidence: 0.72
- why: Segment B narrows and refocuses retrieval more strongly: it adds explicit high-yield platforms (Change.org) and prescribes site-constrained searches (GhanaWeb, JoyOnline, Change.org) plus concrete evidence artifacts (petition title/URL, embedded tweet). This is a clearer, larger change in query shape and targeted sources compared with A's broader local-news/social-media focus.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.78
- why: Segment A moves from a broad, Gitmo-focused retrieval (detainee lists, timelines, general coverage) to a much narrower Ghana-local + activist social-media focus (explicitly adding Ghanaian news sites and OccupyGhana/social accounts and campaign-related tokens). That is a larger retrieval-focus/anchor shift than B, which already targeted local sites and petition platforms and only slightly refines constraints to the same midpoint.

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
- dominant_gap_type: answer_type
- confidence: 0.84
- why: Segment A shifts retrieval focus substantially from finding the game's credits page to switching to a designer-centric evidence family (Kunihiko Tanaka filmography/credits). This is a larger change in retrieval strategy and evidence type (source family and query shape) than B, which only refines the original game-credit target toward Xenoblade Chronicles X.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.85
- why: Segment A shifts the retrieval anchor/focus from a designer-centric search (find Kunihiko Tanaka's filmography/credits) to directly targeting the game credit that names the Monolith Soft title (game-centric verification). This is a substantive anchor/bridge change and an evidence-family shift (designer sources → game/credit page). Segment B mainly refines/cleans a noisy initial query but already targeted the same game-credit endpoint, so its update magnitude is smaller.

## 262__split1__seg0

- idx: 262
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.87
- why: Segment B pivots the retrieval focus away from the originally-stated game-centric evidence target to a designer-centric evidence family (Kunihiko Tanaka filmography). This is a bigger change in retrieval anchors and evidence type (switching which entity is primary and which source family to consult) versus A, which refines the original game-credits focus without changing the anchor.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.7
- why: Both segments perform essentially the same retrieval-focus change: they shift from a game-centric search for Xenoblade Chronicles X credits to a designer-centric search for Kunihiko Tanaka's filmography/credits. The type and magnitude of the correction (anchor shift from game to designer) and the expected evidence types are effectively identical, so neither segment shows a clearly larger update.

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
- confidence: 0.87
- why: Segment B makes a substantive shift away from the long, name-heavy query toward a concise, show-focused retrieval strategy: it re-anchors retrieval on the Smallville main article and the two primary creators (Alfred Gough and Miles Millar), explicitly deprioritizes noisy episode/person pages, and changes the query shape to surface series-level writing credits. Segment A only slightly refines the focus and keeps similar retrieved titles and noise. B therefore represents the larger retrieval-correction.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why: Segment B shows a larger retrieval-focus shift: it moves from a long, name- and episode-heavy query that surfaces many individual person/episode pages (noisy entities) to a concise, show-focused target that should surface authoritative series-level creator/writer pages. Segment A is already a mid-step that has mostly refocused onto show-level anchors (Alfred Gough, Miles Millar, Smallville), so its remaining change to the same target is smaller.

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
- confidence: 0.88
- why: Both segments perform essentially the same update: they reduce a long, name-heavy query to a concise, show-focused retrieval targeting the Smallville main article and the two creators (Alfred Gough and Miles Millar). The anchors, bridge clues, noisy-clue eliminations, expected evidence types, and overall query-shape change are functionally equivalent, so neither segment shows a clearly larger retrieval-focus or evidence-type correction.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.87
- why: Segment B moves from a concrete, long/noisy endpoint query that returns many episode and individual-person pages (biased retrieval) to a concise, show-focused retrieval shape targeting the Smallville main article and creator bios. This is a larger correction in retrieval focus and query shape than Segment A, which is a minor refinement between two similar midpoints already aiming at the same creators and series-level sources.

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
- dominant_gap_type: anchor
- confidence: 0.9
- why: Both segments perform essentially the same narrowing: they remove noisy episode/person pages and refocus retrieval onto show-level sources (Smallville main article, list of episodes) and the primary creators (Alfred Gough, Miles Millar). Differences are only minor wording/anchor emphasis (e.g., mention of 'created by' vs explicitly keeping Justin Hartley), not a substantive change in retrieval focus or correction type, so neither has a clearly larger update.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.93
- why: Segment A changes retrieval focus the most: it moves from a long, name- and episode-heavy query that pulls up individual person and episode pages to a concise, show-plus-creators shape (explicitly targeting the Smallville main article and creator bios). This removes many noisy entity/episode anchors and substantially re-anchors the search on the series-level creators. Segment B is a minor refinement (its from_state already matches the condensed target), so A requires the larger correction.

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
- dominant_gap_type: tie
- confidence: 0.74
- why: Both segments perform essentially the same retrieval-shape correction: they shorten a long, name-heavy query into a show-centric intent targeting the Smallville main article and the creators' bios, while keeping Justin Hartley as a casting bridge and de-emphasizing individual episode/person pages. The differences are only minor (A explicitly avoids episode pages; B explicitly includes the consolidated 'List of Smallville episodes' and mentions industry coverage), which do not justify preferring one as a substantially larger update.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.87
- why: Segment A makes a substantial retrieval-focus shift: it moves from a long, name- and episode-heavy query that biases toward individual person and episode pages (noisy results) to a concise, show-centric target (Smallville main article, list of episodes, and creator bios for Alfred Gough and Miles Millar). Segment B is a minor restatement/refinement that is already close to the target state, so A requires the larger corrective update.

## 55__split0__seg0

- idx: 55
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.8
- why: A shifts the retrieval focus substantially from a conjunctive confirmation about both entities to a narrow, entity-focused lookup for the film (establishing Amsterdamned's nationality/origin). This is a clear change in query shape and retrieval strategy (and narrows anchors to film-specific metadata), whereas B mainly consolidates/validates the original joint verification with only minor anchor additions.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: Segment A shifts from a narrow, film-focused intermediate (establishing Amsterdamned's nationality) to a broader verification that both the film and the city share Dutch culture — it adds new anchors (Amsterdam, Netherlands) and expands bridge clues to connect two entities rather than confirming one. Segment B shows little change (its from_state already targets both entities).

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
- dominant_gap_type: mixed
- confidence: 0.78
- why: A shifts from a film-focused lookup to an integrated verification that both the film and the city share Dutch culture — adding multiple anchors (Amsterdam, Netherlands, 'Dutch culture') and requiring a change in evidence family (film metadata plus city/country cultural statements). B merely pivots from the film to city-specific confirmation, a narrower anchor change.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Both segments make symmetric, comparable updates: each moves from an entity-specific lookup (A: film Amsterdamned; B: city Amsterdam) to a joint verification that both are Dutch. Each adds one new entity anchor and similar bridge clues (national/cultural affiliation), with no clear larger entity correction, relation change, or evidence-family shift. No local ordering justifies preferring one over the other.
