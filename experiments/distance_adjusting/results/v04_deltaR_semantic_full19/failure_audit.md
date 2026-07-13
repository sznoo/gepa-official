# Failure audit

- failed triples shown: 30

## 108__split0__seg0

- idx: 108
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: evidence_family
- confidence: 0.83
- why: A's to_state shows the actual target evidence retrieved (title 'Solo (Australian soft drink)'), shifting the state from a missing-target lookup to a concrete evidence set for comparing production countries. B remains a planning/disambiguation midpoint without retrieved results, so its semantic change is smaller.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: A moves from a disambiguation/midpoint state with many candidate anchors and a missing canonical Solo page to an endpoint that actually includes the Solo (Australian) title and narrows anchors—a substantive shift in the central retrieval target. B already contains the Solo (Australian) anchor and similar focus, so its transition is much smaller.

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
- confidence: 0.84
- why: A moves from an empty/goal-focused midpoint to an endpoint retrieval state with concrete retrieved titles (including 'Solo (Australian soft drink)' and other distractors) and explicit comparison anchor to La Croix — a substantive change in which entities/evidence are present. B only changes the retrieval strategy to a disambiguation step without introducing the actual target titles.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.84
- why: B changes the retrieval anchor from an ambiguous/disambiguation-oriented state to a resolved target (narrowing which 'Solo' is intended). A mostly goes from a targeted plan to having the same target retrieved, so B represents a bigger semantic shift (disambiguation → specific entity).

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
- why: B introduces concrete actor anchors (Deborah Kerr, Donna Reed, Kim Basinger, Heather O'Rourke) and retrieved person pages, shifting the retrieval state from disambiguation/planning to a focused, entity-centered cast-checking task. A mainly adds a disambiguation/coverage step for 'Third Person' without committing to specific actor anchors.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.77
- why: A moves from a planning/disambiguation midpoint with no retrieved titles to an endpoint that introduces concrete retrieved titles and specific cast anchors (Deborah Kerr, Donna Reed, etc.). B already started as an endpoint with version-specific anchors and queries and only adds cast names, so its semantic shift is smaller.

## 132__split0__seg0

- idx: 132
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.86
- why: Both transitions make a small, focused change from the same base: they keep the same central entity (Björk) and evidence target (Selmasongs/Dancer in the Dark) and only slightly differ in retrieval emphasis (A emphasizes confirming occupations on authoritative pages; B emphasizes album/liner-note credit sources). These are comparable, minor semantic refinements rather than qualitatively different evidence targets.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: breadth
- confidence: 0.86
- why: Segment B moves from a broader biographical/discography/filmography retrieval state (wide artist-focused query) to a narrowly targeted soundtrack/artist-credit endpoint, whereas A already begins with a mid-point narrowly focused on Selmasongs/soundtrack credits—so B exhibits a larger narrowing of the retrieval breadth and evidence target.

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
- dominant_gap_type: evidence_family
- confidence: 0.78
- why: B makes a stronger semantic shift from a broad biography+discography search to a narrowly scoped album/soundtrack evidence family and explicit domain restrictions (Wikipedia/Discogs/AllMusic/IMDb) while dropping the need for full biographical occupation lists—a larger change in the retrieval evidence family and query shape than A, which mainly narrows but retains the occupation/biography orientation.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: breadth
- confidence: 0.84
- why: A shifts from a broad, biography/discography–centered retrieval state (many anchors like Vespertine, general Björk pages) to a much narrower, album/soundtrack-credit focus (Selmasongs, liner notes). B starts already targeting album/soundtrack entries and its to_state largely reiterates that focus, so its semantic change is smaller.

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
- dominant_gap_type: evidence_family
- confidence: 0.83
- why: Segment B shifts the retrieval family and goal more: from the generic album/biography target in the base to film-level credits plus the encyclopedia lead (explicitly seeking the performer's occupations). A mostly narrows to album/soundtrack database pages, which is a smaller, more expected specialization of the base.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: evidence_family
- confidence: 0.84
- why: A moves from a broad, biography/discography/filmography–oriented state (many anchors like Vespertine, Selma Ježková, Lars von Trier and expectation of a full biographical page) to a narrowly focused album/soundtrack evidence family—removing multiple anchors and narrowing the evidence type. B only shifts between two similar mid-granularity soundtrack/film-focused states (film-credits vs. album-credits), so its semantic change is smaller.

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
- dominant_gap_type: anchor
- confidence: 0.78
- why: Segment B's to_state adds concrete new anchors (additional retrieved titles like John Hennigan and explicit WPT items) and shifts the state to a final endpoint focused on confirming which WPT champion has four WSOP bracelets and extracting a birth date. A remains a midpoint procedural verification step without new concrete retrieved evidence. The change in B thus alters the anchoring entities and evidence set more substantially.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: A moves from a generated midpoint with no retrieved titles and a narrow verification intent to a concrete target state that introduces specific retrieved anchors (George Danzer, WPT titles) and an explicit extraction goal (birth date). B is already at an endpoint with the same anchors and focus, so its to_state is nearly unchanged.

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
- confidence: 0.81
- why: A shifts the retrieval state from a broad multi-term exploratory search to a narrowly focused, high-precision etymology/identity query (drops some regional anchors, emphasizes an explicit identity sentence and concise pairwise queries). B mostly updates retrieved titles and keeps the same identity-focused goal, so its semantic change is smaller.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: breadth
- confidence: 0.86
- why: B moves from a broader, query-driven retrieval with extra noisy distractor entities (Spillaholle, Gussy Holl) and a wider anchor set to the focused Rstar_target; A was already a narrowly targeted midpoint and changes only minimally (small distractor pruning and minor anchor wording).

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
- dominant_gap_type: anchor
- confidence: 0.78
- why: A changes the central anchors and evidence target: it narrows the state to philological/etymological investigation of hulder→huld and emphasizes Huld as a völva while de-emphasizing or deferring the Holda/Frau Holle identity. B mostly keeps the same anchors but narrows to finding explicit identity/etymology statements—a smaller, more specific refinement.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.92
- why: B moves from a narrowly philological/etymology state (hulder←huldr, Huld as völva) to a state that explicitly adds and seeks identification between Huld and Holda/Frau Holle — introducing new anchors (Holda/Frau Holle) and a new identity bridge relation. A mainly narrows and cleans the same evidence target without changing the central entity or relation.

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
- confidence: 0.83
- why: A shifts the retrieval state from seeking comparative parallels to targeting explicit, authoritative identity/etymology claims (e.g., 'the hulder is originally the same being as Huld'), a substantive change in the asserted bridge relation and answer orientation. B remains within comparative/motif-level evidence and primary attestations, which is a smaller semantic refinement.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: B moves from a broad, mid‑tier comparative/attestation search (collecting primary-source mentions and motif parallels) to a narrowly focused search for authoritative, explicit identity claims equating hulder → Huld → Holda. That is a bigger semantic shift (changing the retrieval target from parallel evidence/attestations to a direct identity claim) than A’s more incremental narrowing from comparative-mythology toward authoritative etymology.

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
- confidence: 0.86
- why: Segment B moves from a broad base to a concretely re-focused endpoint by adding specific retrieved titles (notably a Paul Winters article) and narrowing the evidence family to canonical affiliation statements. Segment A mainly restates the same anchors and confirmation goal without changing the core retrieval anchors or adding concrete results.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.78
- why: Segment B moves from an abstract/midpoint state with no retrieved titles to a concrete target state listing multiple retrieved pages and explicit anchors — a substantive addition of the evidence set. Segment A already contained most of the same anchors and titles, so its change to the target is much smaller.

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
- why: Both transitions make the same small semantic shift: they narrow from a broad endpoint to targeting the same explicit affiliation lines on the 2012 season page and Paul Winters' coach/bio. Differences are only minor wording and a swapped anchor (Wayne State Warriors vs Tom Adams Field), not a change in central evidence target or relation.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: breadth
- confidence: 0.86
- why: B shifts from a broad, noisy endpoint (many season pages and distractor titles) to a narrow, confirmatory retrieval state focused on explicit affiliation lines; A only adds minor specificity (e.g., Tom Adams Field) while keeping the same core anchors.

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
- dominant_gap_type: breadth
- confidence: 0.85
- why: B expands the retrieval state from a narrow check for two specific affiliation lines into a broader endpoint listing multiple season pages and additional titles (more distractor seasons and a wider evidence set). A only narrows to fetch the two canonical pages, a smaller semantic shift.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.78
- why: Both transitions show essentially the same semantic change: moving from a planning midpoint (no retrieved titles, same intended anchors and bridge clues) to an endpoint that adds the same concrete retrieved titles and affirms the same anchors (2012 team, Paul Winters, Wayne State University). There is no material difference in which entity senses, bridge relation, or evidence family is introduced.

## 150__split3__seg0

- idx: 150
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: breadth
- confidence: 0.78
- why: B narrows the retrieval state from a general coach+team focus to a single, specific evidence target — the 2012 season page lead — changing the central evidence target and substantially reducing the breadth of the retrieval set. A is a minor refinement that keeps both season and coach pages as targets.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: breadth
- confidence: 0.85
- why: A shifts from a broad, noisy retrieval (many season pages and multiple anchors) to a narrowly focused target of the two primary pages, removing distractor seasons and tightening the evidence set. B only expands a single-season focus to also include the coach bio—a smaller, local change.

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
- dominant_gap_type: evidence_family
- confidence: 0.87
- why: Segment B shifts the retrieval state from a general verification goal to a narrowly focused, authoritative credit-confirmation task: it adds a new evidence anchor (Stuntmen's Hall of Fame/obituary), specifies exact credit-phrase bridge clues (e.g., 'performed the motorcycle jump'), and prioritizes primary sources—a substantive change in the evidence family and search intent compared with A's relatively similar/broader target.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.76
- why: Segment B's transition removes noisy/distractor retrieval items and a raw query, narrowing the evidence set to the targeted anchors (Bud Ekins, Steve McQueen, The Great Escape, Bullitt). Segment A mostly restates the same anchors and focus while moving from a midpoint to an endpoint, so its semantic retrieval-state change is smaller.

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
- dominant_gap_type: bridge_relation
- confidence: 0.85
- why: Both transitions narrow the broad base toward confirming Ekins as McQueen’s stunt double for The Great Escape, but B additionally adds an explicit, separate verification task (check primary credit sources) to resolve whether Ekins also doubled McQueen in Bullitt. That introduces a new retrieval target/bridge relation and a different evidence-check strategy, producing a larger semantic change than A, which focuses only on The Great Escape and defers Bullitt.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.88
- why: Segment B's to_state adds a new central anchor (Bullitt) and shifts the retrieval goal to explicitly resolve that ambiguity (a new evidence target), whereas A mainly refines source prioritization and noise filtering without changing the core evidence target.

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
- dominant_gap_type: anchor
- confidence: 0.88
- why: A shifts the retrieval state from a general discography check to concrete album-level evidence: it adds specific album-title anchors (e.g., Schizo Deluxe, Refresh the Demon) and expands the goal to fetch the album's official release date. B only narrows the task to identifying the 11th album's title (ordinal-confirmation) without adding new entity anchors or the release-date evidence goal.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.91
- why: A shifts the retrieval goal from merely confirming the 11th-album title to additionally identifying the band and retrieving the album's official release date (broader, new answer type and anchors). B's from_state already targeted the band, 11th album and release date, so its transition is minimal.

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
- dominant_gap_type: evidence_family
- confidence: 0.87
- why: From the same confirmation midpoint, A moves to a straightforward endpoint (find the 11th album and its release date). B instead shifts the retrieval state to a broader, different evidence-collection mode: gather all cited release-date variants and their provenance across multiple source families and regions (infobox citations, label/band announcements, Discogs/MusicBrainz/AllMusic). This introduces new evidence families and breadth of sources/variants rather than simply resolving the final date, so the semantic change is larger.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.89
- why: Segment A's from_state is narrowly anchored on a known album and focused on collecting candidate release-date sources; the to_state instead requires (re)identifying the band and the 11th-album target and then finding its release date. That shifts the central anchors and evidence family (album-specific sourcing → band/discography identification), a larger semantic change than B's minor step from year-only to full date.

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
- dominant_gap_type: bridge_relation
- confidence: 0.83
- why: A changes the retrieval goal from the original dual-hop (actor→character and character→publisher) to a single-hop focus on actor→character (filmography/cast evidence), removing the publisher hop and shifting the evidence family; B mostly preserves the original dual-hop target and simply tightens anchors.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A's from_state was narrowly focused on confirming an actor->role link and explicitly avoided publisher pages; the to_state adds a new publisher anchor (Marvel Comics) and shifts the retrieval focus from actor-only to actor->character->publisher, changing the central evidence target. Segment B already contained both actor+publisher anchors, so its transition is smaller.

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
- why: Segment B shifts the retrieval target away from an actor-centric verification (Evan Peters/filmography) to a comics/publisher–centric state (Quicksilver character entry, infobox, publication history), replacing the actor anchors with publisher/character anchors. A keeps the actor anchor and only adds publisher confirmation, a smaller semantic change.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.83
- why: A shifts the retrieval focus from a comics/publisher–centric state to one that explicitly brings in the actor (Evan Peters) as a new anchor, changing the evidence family and entity sense (comics entries → actor/filmography linkage). B instead only adds the publisher confirmation to an already actor-centered state, a smaller semantic extension.

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
- dominant_gap_type: mixed
- confidence: 0.84
- why: Segment B changes the retrieval state from a general search for mentions of an online protest to a narrowly focused evidence family (contemporary news and social‑media coverage) and explicitly requires quoted campaign identifiers (hashtags, e‑petitions, embedded tweets). This is a substantive shift in what counts as relevant evidence versus A, which mostly adds/changes retrieved titles but keeps the same overall target.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.83
- why: Segment B moves from a midpoint with no retrieved titles to a target state that adds concrete retrieved anchors/titles (e.g., 'Occupy Ghana', specific articles). A's change is a minor refinement where the same anchors and focus are already present, so B introduces a larger semantic shift by adding explicit entity anchors and evidence.

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
- confidence: 0.79
- why: A introduces a substantial anchor shift — constraining retrieval to Ghana-focused news outlets and local activist social pages (specific sites like GhanaWeb, JoyOnline, Citi, Graphic) and adding campaign-host platforms (Change.org) — changing the evidence sources and breadth. B is mostly a finer-grained refinement asking for quoted hashtags/petition labels within news/social coverage, which is a smaller, more focused adjustment.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: breadth
- confidence: 0.85
- why: Segment B moves from a broad endpoint search (general retrieved lists and mixed Gitmo pages) to a narrowly focused retrieval targeting explicit online campaign identifiers; Segment A already started Ghana‑focused and only narrows from focused to slightly more explicit, so B exhibits the larger semantic shift.

## 247__split2__seg0

- idx: 247
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.86
- why: Both transitions make the same semantic shift from a general Gitmo/detainee retrieval state to a Ghana-focused search for local news and online campaign artifacts (news sites, petitions, hashtags, OccupyGhana social posts). Their added anchors and evidence-family changes are effectively the same; differences are only in minor specificity.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: evidence_family
- confidence: 0.92
- why: A shifts from a broad, Gitmo/detainee-list oriented retrieval (general detainee bios and timelines) to a focused Ghana-local evidence set (Ghanaian news outlets and activist social pages). B changes only between two already-local retrieval focuses (specific high-yield local sites/Change.org → a slightly broader set of Ghanaian outlets), a much smaller semantic shift.

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
- dominant_gap_type: evidence_family
- confidence: 0.73
- why: A changes the evidence family and anchor: it pivots from a game-centered credit search to designer-centric filmography/credits (different retrieval target and source type). B largely keeps the original game-credit target (smaller semantic shift).

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: A shifts from a general, designer-focused retrieval state (seeking Kunihiko Tanaka's filmography/credits) to a specific target anchoring the game title and developer (Kunihiko Tanaka + Xenoblade Chronicles X + Monolith Soft). B already contained the same game/developer anchors in its from_state, so its transition is minimal.

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
- dominant_gap_type: evidence_family
- confidence: 0.82
- why: B shifts the retrieval family from game-centric evidence (Xenoblade Chronicles X credits) to designer-centric evidence (Kunihiko Tanaka filmography/credits), changing the primary anchors and evidence source type. A mostly narrows toward the same game-credits evidence already implied in the from_state, so its semantic change is smaller.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.8
- why: Segment B shifts from a strongly game-centric retrieval state (focused on Xenoblade Chronicles X credits, game databases, and the game's staff) to a designer-centric state (Kunihiko Tanaka filmography/credits). Segment A makes a similar shift but already included the designer anchor in the from_state, so its semantic change is smaller.

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
- dominant_gap_type: evidence_family
- confidence: 0.84
- why: Segment B changes the evidence family and anchor more substantially: it pivots from seeking game-side primary artifacts (artbook/press/interview about the title) to a designer-centric filmography/credits page for Kunihiko Tanaka, shifting the retrieval focus to the creator's authoritative list of works rather than title-focused credit artifacts. Segment A mainly narrows to per-title credit listings, which were already present as anchors in the from_state.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Both A and B shift from a Xenoblade Chronicles X–centered retrieval focus (A: artbooks/press/interviews tying Tanaka to the title; B: per-title credit listings/manuals/aggregators) to the same designer-centric to_state (Kunihiko Tanaka filmography/credits). The semantic change in retrieval anchor and evidence target is effectively the same magnitude in both segments.

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
- dominant_gap_type: bridge_relation
- confidence: 0.85
- why: B more strongly shifts the retrieval state from a noisy, name-heavy query to a focused, show-level evidence family and explicit creator-style bridge relation (prioritize 'created by / developed by' sources and creator bios). A mostly surfaces some titles but keeps actor/cast noise; B meaningfully narrows the evidence target and relation.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.86
- why: Segment B moves from a broad, name- and episode-heavy retrieval (many individual person and episode pages as distractors) to a focused, series-level creator/writer target. Segment A was already centered on the creators and thus undergoes a much smaller semantic narrowing.

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
- confidence: 0.85
- why: Both A and B perform essentially the same semantic change: they remove peripheral episode/person anchors and refocus the retrieval on show-level sources and the two primary creators (Alfred Gough and Miles Millar). The magnitude and type of retrieval-state change are materially similar.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.79
- why: Segment B moves from an endpoint long, name-heavy query that returns many episode/person pages to a concise, show-level retrieval targeting the series creators; that is a substantive shift in retrieval target and evidence family. Segment A's from_state is already focused on the same show+creator anchors, so its transition is much smaller.

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
- dominant_gap_type: query_shape
- confidence: 0.78
- why: Both transitions make the same semantic change: they narrow a long, name-heavy query to authoritative show-level sources (Smallville main article, list of episodes) and preserve the two primary creators (Alfred Gough, Miles Millar) while dropping peripheral episode/person pages. The differences are minor phrasing choices (A explicitly mentions keeping Justin Hartley as a bridge), so the overall retrieval-state change magnitude is essentially equal.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: breadth
- confidence: 0.91
- why: Segment A shifts from a broad, name- and episode-heavy retrieval state (many episode pages and secondary writers) to a focused show-level + primary creators state (Smallville main article and Alfred Gough/Miles Millar). Segment B starts already narrowed and changes to an essentially identical focused state, so A exhibits the larger semantic change.

## 267__split3__seg0

- idx: 267
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.86
- why: A makes a clearer semantic shift away from episode-level and person-page evidence toward series-level creator/credit anchors (explicitly avoiding episode pages and long enumerations). B is a narrower but more conservative change that still retains the 'List of Smallville episodes' evidence family, so its retrieval-state shift is smaller.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: breadth
- confidence: 0.92
- why: A moves from a broad, name- and episode-heavy retrieval (many episode pages and individual person pages) to a focused, authoritative show-level evidence set (main article, list of episodes, creator bios), a substantive narrowing/removal of noisy distractors. B's change is minor (already modestly focused to nearly identical target).
