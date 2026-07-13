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
- dominant_gap_type: mixed
- confidence: 0.78
- why: Segment B introduces additional and stronger anchor shifts (explicit manufacturer/distributor anchors and disambiguation markers) and a clearer noise-correction emphasis to avoid regional 'Solo' variants, producing a larger net retrieval-control change than A.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.72
- why: Segment A shifts the anchor set and disambiguation focus more substantially (from a broad, multi-anchor planning state to a concrete target with the canonical 'Solo (Australian)' anchor). Segment B mainly tweaks query wording/query-shape with smaller net anchor/bridge changes.

## 108__split1__seg1

- idx: 108
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.86
- why: B moves from general disambiguation to a concrete extraction target (infobox/lead stating country and manufacturer), introducing more specific anchors, a stronger bridge relation (explicitly linking Solo to Australia), a narrower evidence family, better noise avoidance, and a changed query shape toward extraction.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.91
- why: Both transitions implement essentially the same retrieval-control shift: disambiguate and retrieve the Solo (Australian soft drink) page (and its infobox/lead) to compare with La Croix. Neither introduces materially more or different anchor, bridge, evidence-type, noise-correction, or query-shape changes.

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
- confidence: 0.81
- why: Segment B changes the retrieval strategy: it pivots to a disambiguation-first flow (introducing a disambiguation anchor and manufacturer headers) rather than directly fetching the product page. This alters the bridge relation, the expected evidence page family, noise-avoidance behavior, and the BM25 query shape, so it represents a larger net retrieval-control shift.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment B moves from a disambiguation-focused retrieval control (multiple candidate meanings) to a targeted retrieval that resolves the Solo identity and then fetches production-origin evidence — this entails a stronger anchor shift (disambiguation → specific Australian product), clearer noise correction, and a change in query shape/expected evidence than A, whose from_state already targeted the Solo (Australian) page.

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
- confidence: 0.82
- why: Segment A introduces a new disambiguation-first retrieval strategy (adding 'Third Person' disambiguation and per-version candidate actor sets), explicitly corrects for noisy/distraction hits, and changes the query shape to a two-step disambiguate-then-query process. B mainly narrows anchors to specific actress names (a notable anchor change) but keeps the original cast-list evidence family and query pattern, so A represents the larger net retrieval-control shift.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.83
- why: Segment A shifts from a disambiguation/planning midpoint (listing candidate works and lead actresses) to a concrete cast-retrieval endpoint that adds specific actor anchors and moves the query shape from disambiguation-heavy to cast-focused intersection. Segment B already starts with version- and cast-specific queries, so its change to the same endpoint is minimal.

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
- confidence: 0.78
- why: Segment B makes a stronger, concrete shift: it replaces disambiguation-stage planning with explicit, year-disambiguated anchors (Third Person 2013; From Here to Eternity 1953), narrows the bridge to top-billed female-cast intersection, and prescribes precise title+year queries — producing larger anchor, query-shape, and noise-reduction changes than A.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: mixed
- confidence: 0.84
- why: Segment A moves from a broad disambiguation strategy (listing multiple candidate works/years and collecting actress sets per candidate) to targeted cast lookups — a substantive change in anchors, bridging strategy, noise filtering, and query shape. Segment B is already narrowed to specific title/year candidates, so its from->to change is much smaller.

## 132__split1__seg1

- idx: 132
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: answer_type
- confidence: 0.79
- why: Segment A adds a new evidence family requirement (explicit artist biography/occupation verification) and shifts the implied query shape from mid-granularity credit queries to short entity-centric jumps. Segment B mostly refines source preference toward release-level databases without introducing new evidence families or changing query shape materially.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.72
- why: Segment B shifts from purely release/credit-focused anchors (album page, label, AllMusic/Discogs) to also require linking that release attribution to the artist and her occupations — introducing an additional relation and expanding the needed evidence family (album metadata → artist/biography). A’s from_state already targets album/credit sources and so makes a smaller net change to the same endpoint.

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
- dominant_gap_type: query_shape
- confidence: 0.79
- why: Segment B shifts retrieval focus from album/biography lookups toward film-level credits and the lead encyclopedia sentence — changing the expected evidence family and the query shape more substantially than A's album-centered narrowing.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: answer_type
- confidence: 0.78
- why: Segment A moves from a broad biography/discography search (entity-centric, many noisy facets) to a focused album/soundtrack-level retrieval strategy, a larger net change in evidence family, noise pruning, bridge focus, and query shape than B's shift from film-page/encypedia-intro to album pages.

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
- dominant_gap_type: query_shape
- confidence: 0.72
- why: Segment B imposes a stronger retrieval-control shift: it moves from a general verification step to an explicit conjunctive cross-check (find a WPT champion who also has four WSOP bracelets and then get birth date). This requires a tighter bridge between WPT winners and WSOP bracelet counts and a more entity-centric, attribute-conjunctive query shape than A's primarily conditional verification of George Danzer.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.92
- why: Segment A moves from a narrow verification of 'George Danzer -> WPT' to a broader retrieval plan: search WPT champions, match a winner who has four WSOP bracelets, and then extract birth date. That introduces new anchors, a stronger bridge relation (matching list membership to bracelet count), and a shift in query shape; Segment B is already at or very near the same endpoint, so its transition is much smaller.

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
- confidence: 0.79
- why: Segment A extends the retrieval controls beyond just shortlisting candidates: it adds an explicit requirement to confirm which WPT champion has four WSOP bracelets and to extract that person's birth date — introducing an additional biographical-evidence retrieval and an extra relation to resolve (person -> birth date).

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.74
- why: Segment B moves from an aggregate multi-candidate scanning strategy (cross-referencing a WPT winners list with WSOP bracelet counts) to a focused retrieval of the winner's birth date, which entails a larger net change in anchors (many candidates → a specific person), bridge relations (matching list entries to bracelet-count bios then to a birthdate), and query shape (list-scan + per-candidate checks → single-entity biographical lookup). Segment A mostly refines a single-candidate verification (George Danzer) to also fetch a birth date, a smaller net shift.

## 140__split2__seg1

- idx: 140
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.84
- why: Segment B adds substantive retrieval controls beyond A: it not only fetches a WPT winners list but also cross-references each winner with authoritative bios/WSOP records to filter for exactly four bracelets. That introduces a new bridge (connecting WPT winners to WSOP bracelet counts), a different expected evidence family (biographical/WSOP records), active noise-filtering, and a more complex multi-step query shape.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.76
- why: Segment B moves from a single-document champions list extraction to adding a substantive cross-reference step (checking each winner's WSOP bracelet counts), changing the query shape and required bridge relation and evidence types. A mainly shifts focus from a specific-candidate check to a broader shortlist but already included the candidate-verification intent, so its net retrieval-control change is smaller.

## 149__split0__seg0

- idx: 149
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.86
- why: Both transitions perform the same net narrowing: focus on short, high-precision etymology/identity claims linking hulder ↔ Huld ↔ Holda, retain the same anchors, and imply similar query-shape shifts. No factor shows a materially larger retrieval-control change in either segment.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.8
- why: Segment A moves from an empty/no-retrieval midpoint to a focused endpoint, introducing anchors, bridge clues, and explicit expected evidence — a larger net retrieval-control shift than B, which already contained similar anchors and bridge clues and only changes query-shape modestly.

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
- dominant_gap_type: mixed
- confidence: 0.77
- why: Segment B expands the anchor set to explicitly include Holda/Frau Holle and changes the required bridge from merely etymological linking (hulder→Huld) to an explicit Huld↔Holda identity; it also tightens queries toward high-precision identity claims—overall a larger net retrieval-control shift. A mainly narrows to etymology and deliberately avoids Holda, which is a smaller, different change.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.86
- why: Segment B introduces new central anchors (Holda/Frau Holle) and a new bridge relation (adding the Huld↔Holda identity) that were absent in its from_state, whereas Segment A mostly narrows a broad multi-term query into a high-precision query without adding new anchors or relational links.

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
- why: Segment B shifts retrieval controls beyond name-origin verification toward cross‑regional comparative-mythology and cognacy evidence connecting Huld to Holda/Frau Holle. That requires different bridge relations, different evidence families (comparative analyses and primary medieval citations) and more relation‑focused queries, whereas A mostly tightens the existing etymology/encyclopaedia search to find explicit identity claims.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Segment A moves from a strictly etymology/Huld focus to explicitly introducing Holda/Frau Holle as a linked anchor and asserting an identity relation, which adds both a new central entity and a stronger bridge relation and changes the retrieval queries to include explicit identity claims. B is a refinement from comparative-mythology toward the same endpoint and thus represents a smaller net control shift.

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
- dominant_gap_type: bridge_relation
- confidence: 0.72
- why: Segment A moves retrieval control from general comparative groundwork to seeking concise, authoritative etymology/encyclopedic identity statements that explicitly link Huld↔Holda (a new, stronger bridge relation and a switch to high‑precision evidence), whereas B stays at motif/parallels and primary-attestation gathering (a narrower incremental change).

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.79
- why: Segment B moves from broad, primary-source and motif-focused comparative material (attestations and overlapping traits) to a narrow, high-precision search for explicit etymological/encyclopedic identity statements — a larger net change in the needed bridge relation, evidence family, and query shape than A, which was already oriented toward comparative-name links.

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
- confidence: 0.74
- why: Both transitions make near-identical, small retrieval-control refinements from the same base: they focus on the same anchors (team, coach, university), the same bridge relation (team represented university / coach = head coach), the same expected short authoritative evidence, and the same shift toward compact entity-focused queries. Neither introduces substantially more or different retrieval controls than the other.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: mixed
- confidence: 0.78
- why: Segment A moves from a broader, query-filled base state (explicit long query, extra distracting season titles and historical naming) to a focused endpoint that explicitly surfaces the coach page and canonical team/university titles. B starts from a midpoint already matching the endpoint, so A entails the larger net retrieval-control shift (anchors, noise reduction, and query shape).

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
- confidence: 0.84
- why: Both transitions make essentially the same retrieval-control changes: they keep the same anchors (team, coach, university), aim to surface short lead-paragraph affiliation lines, and propose narrowly focused queries to retrieve those pages. Neither introduces more or stronger anchor, bridge, or evidence-type changes.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.92
- why: Segment B moves from a broad, multi-term/endpoint retrieval state with many retrieved titles and noisy anchors to a narrowly focused, phrase-targeted retrieval strategy that explicitly reduces temporal and topical noise. A makes only a modest shift (title-targeting → phrase-focused) and adds a minor anchor; B's change is larger across query shape and noise/anchor narrowing.

## 150__split2__seg2

- idx: 150
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.86
- why: Both transitions make essentially the same retrieval-control changes: they keep the same anchors, aim to fetch the 2012 team page and Paul Winters bio, seek identical short affiliation lines, and prefer compact entity/title queries. Neither introduces materially more or different retrieval constraints.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.88
- why: Both transitions make the same net shift: from seeking explicit affiliation lines for the 2012 team and Paul Winters to the identical Rstar target that retrieves the same team/coach/university pages. There is no material difference in anchors, bridge relation, evidence type, noise corrections, or query shape.

## 150__split3__seg0

- idx: 150
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.86
- why: Segment B narrows retrieval from a dual-target (team page + coach bio) to a single, title-targeted season page whose lead sentence directly ties the team to the university and names the coach. That represents a stronger change in anchors (focus to the season-page lead), bridge relation (explicit team->university linking), evidence family (season-page lead vs. coach bio), noise pruning, and query shape (season-title-targeted).

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.78
- why: Segment B adds a new retrieval target (the coach/bio page) beyond the single season-page focus in its from_state, producing both an anchor addition and an evidence-family change. Segment A mainly refines query shaping toward title/lead-snippet targeting without introducing new anchors or evidence families.

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
- dominant_gap_type: mixed
- confidence: 0.92
- why: Segment B introduces additional and more specific retrieval controls (adds a Hall-of-Fame/obituary anchor), tightens the bridge relation language (exact phrase searches about doubling and the motorcycle jump), specifies authoritative evidence families (NYT/THR/IMDb/BFI/Hall-of-Fame) and explicit site/phrase filter query shape, and more precisely identifies noise to avoid — a broader and stronger net retrieval-context shift than A.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.82
- why: Both transitions move from very similar retrieval-focused states (anchors, bridge clues, noisy clues, and query-shape guidance) into the same Rstar_target with no substantive difference in the retrieval controls; changes are largely formatting/field redistribution rather than net retrieval-control shifts.

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
- dominant_gap_type: mixed
- confidence: 0.89
- why: Segment B extends the retrieval controls beyond A by explicitly adding Bullitt as an additional anchor, requiring primary-credit checks (IMDb/BFI/obituaries) to resolve that ambiguity, and shifting query shape to exact-phrase/site-filter searches plus a follow-up query — a broader and stronger net change in retrieval constraints than A, which focuses only on The Great Escape.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.82
- why: Segment B makes stronger retrieval-control changes: it adds an explicit new anchor (Bullitt) that expands the search target, shifts evidence priority toward primary credit sources (film-credit databases/primary credits) and enforces stricter query-shaping (exact-phrase + site filters and a targeted follow-up). Segment A is mostly a refinement of phrasing and filtering already present in its from_state.

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
- confidence: 0.83
- why: Segment A extends the retrieval control beyond identifying the 11th album to also require retrieving the album's official release date (additional evidence-family and bridging step). This adds a clear query-shape shift toward date-focused retrieval and an extra bridge from album identity to release-date evidence.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.79
- why: Segment A moves from confirming the 11th-album title (discography-counting) to also retrieving the album page and its release date, changing the required evidence family and the bridge from counting to document lookup. Segment B already targets both steps, so its net retrieval-control change is smaller.

## 180__split2__seg2

- idx: 180
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.63
- why: Segment A makes a bigger net retrieval-control shift by moving from confirming the band/album identity to selecting specific album anchors and retrieving the album's official release date (a new, higher-granularity evidence target). Segment B is a narrower refinement focusing on collecting candidate date sources for an already-identified album.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.83
- why: Segment A shifts retrieval controls more: it moves from an album-focused evidence-collection posture to needing band/album identification plus multi-source date-assembly, producing larger anchor and query-shape changes and a bigger bridge relation adjustment. Segment B mostly already covers band identification and ordinal counting and only adds a finer-grained evidence request (exact date).

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
- dominant_gap_type: query_shape
- confidence: 0.75
- why: Segment B extends the retrieval controls beyond simply gathering date entries: it adds new anchors (catalog numbers, label/catalog identifiers, edition/region qualifiers), changes the bridging relation to use catalog/edition-based matching to locate the original release record, and shifts the query strategy toward catalog-number/edition lookups. These are more and different retrieval-control changes than A's narrower shift to collecting date entries from standard album pages/databases.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.94
- why: Segment B moves from confirming the band identity and locating which album is the 11th (an entity/ordinal anchoring step that resolves potential distractors) to collecting release-date evidence — a substantive shift in central anchor, relation mapping (band→Nth album→date), evidence family, and query shape. Segment A is a narrower, incremental shift from collecting metadata/catalog identifiers to gathering date entries for an already-identified album.

## 227__split0__seg0

- idx: 227
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.71
- why: Segment B introduces the additional retrieval-control shift of moving from actor-filmation verification to explicit comic-character and publisher evidence: it adds a comic-page anchor (Quicksilver (comics)), expands the evidence family to include publisher/comics pages, and requires an extra bridge relation (actor -> character -> publisher). Segment A mainly narrows to actor->role checks and adds an avoidance constraint.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.89
- why: Segment A shifts from an actor->role confirmation focus that intentionally avoids publisher/comic pages to a target that explicitly adds the character->publisher anchor and requests comics/character pages. B already includes those anchors and query shape, so A represents the larger net retrieval-control change.

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
- dominant_gap_type: mixed
- confidence: 0.85
- why: Segment B makes a clearer, more complete switch from actor-centered retrieval to comic-character/publisher-centered retrieval: it drops actor-focused anchors, adopts publisher and character-infobox anchors, changes the bridge relation to character->publisher, shifts evidence family to comics/infobox pages, and alters query shape to publisher-focused entity queries. A mostly adds publisher confirmation while keeping actor-focused anchors.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.87
- why: Both transitions introduce a single symmetric retrieval-control shift: A adds the actor anchor (Evan Peters) and an actor→character bridge to a comics-focused state, while B adds the publisher/comics anchor and a character→publisher bridge to an actor-focused state. They require comparable changes in anchors, bridge relations, evidence family, and query shape.

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
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Segment B tightens the bridge relation (explicitly seeking quoted hashtags/petition titles and social‑media embeds) and changes the query shape (allowing wildcard/substring hashtag patterns and platform terms), whereas A mainly restates the original goal with minor wording differences.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.76
- why: Both transitions make only minor, largely redundant refinements toward locating a named online campaign/hashtag for the same event; neither changes anchors, bridging relation, evidence family, or query shape in any substantive way.

## 247__split1__seg0

- idx: 247
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.77
- why: Both transitions make essentially the same retrieval-control changes: they narrow from general Gitmo/detainee pages to Ghana-focused news and activist social posts and introduce the same campaign/token search terms (hashtag, petition, Facebook/Twitter). No factor shows a materially larger change in one segment versus the other.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.78
- why: A moves from a general Ghana-focused retrieval scope to a narrower requirement for contemporary coverage that explicitly quotes/reproduces campaign identifiers (a clear shift in the required evidence family and implied query shape). B's from-state already targets campaign names/hashtags, so its net control change to the same midpoint is smaller.

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
- dominant_gap_type: mixed
- confidence: 0.75
- why: Both transitions narrow from the same base, but B makes a stronger, more specific retrieval-control shift: it adds a new evidence family (Change.org/petition platforms), prescribes site-restricted searches of high-yield local outlets, and specifies embedded social-post/tweet-to-article bridging — all of which change anchors, bridge relations, and query shape more than A's broader Ghana-focused/local-social emphasis.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: Segment A shifts from a broad Gitmo/detainee-list focus to a specifically Ghana-local, social-media/petition-focused retrieval strategy — changing anchors, evidence family, removing noisy detainee-list pages, and altering query shape. B is a small retargeting between already similar, focused midpoints.

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
- dominant_gap_type: mixed
- confidence: 0.86
- why: Segment A shifts retrieval control from a game-centric credit search to a designer-centric search (different anchor emphasis), swaps the expected evidence family (designer filmography/credit aggregators vs. game/developer pages), changes the bridging relation to confirm via the creator's credits, explicitly calls out and reduces distracting Xeno-series noise, and therefore requires a larger change in query shape and retrieval strategy than B.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: Segment A shifts from a broad, designer-centric search (filmography/credits) with many distractors to a focused, game-specific retrieval target that adds explicit anchors (Xenoblade Chronicles X, Monolith Soft), tightens the bridge relation (designer→specific game), narrows expected evidence, and changes query shape—whereas B is already largely at that focused endpoint.

## 262__split3__seg2

- idx: 262
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.8
- why: Both transitions move from a mixed evidence-seeking focus to a similarly sized, but opposite, specificity: A narrows to per-title/game-credit sources (MobyGames, manual/end credits), B narrows to creator-centric filmography sources. They involve comparable anchor, query-shape, and evidence-family changes, so neither shows a materially larger retrieval-control change.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.8
- why: Segment B moves from a purely per-title, game-side credit focus (Xenoblade Chronicles X credits/pages) to a designer-centric retrieval target, which is a stronger anchor shift and entails a larger change in evidence family and query shape than A (A's from-state already included the designer as an anchor).
