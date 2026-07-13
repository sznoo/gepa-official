# Failure audit

- failed triples shown: 30

## 108__split0__seg0

- idx: 108
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.72
- why: Transition B adds more specific disambiguation and anchor guidance (explicit canonical-title targeting, manufacturer anchors like 'Schweppes Australia' / Asahi, and explicit markers to avoid regional variants and global manufacturer pages). These instructions change retrieval behavior more (which anchors to include and which noisy variants to exclude) than the relatively smaller, redundant disambiguation cue in A.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why: B requires a substantive change to the query-generation instructions — remove/avoid manufacturer tokens that bias retrieval, refocus on the canonical disambiguation title and adopt a concise disambiguation query shape. A is already framed as a disambiguation-focused step and needs only minor refinement.

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
- dominant_gap_type: answer_type
- confidence: 0.88
- why: Segment B adds a substantive shift from simply disambiguating and retrieving the Solo page (A) to explicitly targeting and extracting specific evidence types (infobox/lead lines and manufacturer/production statements). That requires changing the prompt to emphasize extraction-style queries, concrete infobox anchors, and explicit evidence fields rather than just locating the canonical page — a broader semantic change to retrieval instructions.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.8
- why: Segment B requires a stronger refocus: not just disambiguating the 'Solo' title (as in A) but targeting specific evidence fields (infobox/lead/manufacturer) and an extraction-style query. That changes the retrieval specification more (expected evidence family and extraction shape) than A's primarily disambiguation/noise-avoidance instruction.

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
- why: Segment B adds a substantive change to retrieval behavior: it introduces an explicit disambiguation-first step (retrieve the 'Solo' disambiguation/summary) and changes the query shape from a single direct extraction to a two-step confirm-then-fetch workflow, plus new anchors (disambiguation entry) and filters to avoid regional variants. This is a broader semantic update than A's narrower instruction to target the canonical Australian Solo page.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: noisy_entity
- confidence: 0.87
- why: Segment B adds a disambiguation step and explicitly changes retrieval behavior to first resolve which 'Solo' is meant (disambiguation page / summary) before fetching product pages; this is a broader semantic change than A's narrower instruction to directly target the Australian Solo page and extract its infobox/lead.

## 108__split3__seg3

- idx: 108
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.89
- why: A adds a new comparison anchor (La Croix/US) and broadens the retrieval goal to reach an endpoint set of pages for cross-entity comparison, changing what entities to preserve and the overall retrieval scope; B is a narrower refinement focused only on extracting a short lead/infobox snippet for Solo.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.75
- why: Both transitions require only minor, similar prompt updates: preserve the Solo-vs-La Croix comparison target, disambiguate which 'Solo' to target (avoid the Norwegian variant), and issue a short extraction-style query for Solo's country. Neither transition introduces a substantially different retrieval focus or new bridge relation.

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
- confidence: 0.87
- why: A requires a broader change to the query-generation prompt: add systematic title disambiguation (list all 'Third Person' candidates), extract top-billed actresses per candidate, and produce per-version candidate sets for intersection. That modifies the retrieval shape and candidate-set breadth much more than B’s narrower, version-specific cast lookups.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.9
- why: A’s from_state is a mid-point that emphasizes broad title disambiguation, candidate-generation, and avoiding noisy disambiguation items; moving to the endpoint requires a substantial refocus: shift from broad disambiguation to precise, authoritative cast-list retrieval, add specific actress anchors (e.g., Deborah Kerr/Donna Reed), tighten query shape to exact-title+cast lookups, and remove disambiguation noise. B already starts with version-specific, cast-focused queries so its update to the same endpoint is smaller.

## 118__split1__seg1

- idx: 118
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
- why: Segment B forces concrete disambiguation (fixing 'Third Person'→2013 and 'From Here to Eternity'→1953) and narrows the retrieval target to top-billed female cast—a substantive change in anchors, candidate breadth, and query shape versus A, which keeps broader disambiguation and simply requests authoritative cast pages.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment B commits to a narrow, single-year interpretation (Third Person 2013 / From Here to Eternity 1953). Moving to the target requires adding broad disambiguation, multiple version anchors, and a more exploratory query shape (extract cast lists per candidate) — a bigger semantic shift than A, which already encodes disambiguation and multi-version candidate extraction.

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
- confidence: 0.88
- why: Transition B imposes a more specific shift in retrieval behavior: it redirects the search from broad biography/discography pages to a different evidence family (album pages, liner notes, and explicit soundtrack-credit language), removes biography/birthdate–focused noise, and prescribes mid-granularity, credit-oriented query shapes. That is a bigger semantic change than A’s lighter rewording to shorter entity-centric queries targeting artist/album pages.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.88
- why: Segment B moves from a broad, biography- and discography-focused query (includes birthdate, filmography, Vespertine production credits and many potential anchors) to a tightly targeted film->soundtrack->artist instruction. That requires removing multiple noisy anchors and extra evidence types and changing the query shape and focus more substantially than A, whose from_state was already album/credit-centered and only needs a modest shift to shorter entity-centric queries.

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
- dominant_gap_type: mixed
- confidence: 0.78
- why: Transition B requires a bigger change to the query-generation instructions: it reanchors retrieval from album-release databases to film-level credits plus the lead sentence of an encyclopedia entry (a different evidence family) and explicitly preserves occupation-listing in the lead. That both redirects the main anchor (film page vs album entry) and adds a new requirement (grab the lead encyclopedia line for occupations), which is a broader semantic shift than A’s narrower refocus to album-level sources only.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: A requires a bigger semantic re-write of the query-generation prompt: it moves from a broad, entity/biography-centric retrieval (full Björk biography, discography, filmography) to a focused album/soundtrack retrieval strategy that adds domain restrictions (Discogs/AllMusic/Wikipedia album page), reprioritizes album-level anchors (Selmasongs entries) and drops the need for deep biographical details. B is a narrower shift from film-page/lead-bio to album entries and therefore implies a smaller, more local refocus.

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
- dominant_gap_type: mixed
- confidence: 0.88
- why: Segment B expands and strengthens the retrieval instruction: it not only asks to verify the WPT<->person link (as in A) but also adds a concrete filter ('also has four WSOP bracelets') and an explicit answer extraction target (birth date). That changes anchors, the bridge relation to enforce a cross-attribute match, and the expected answer type and query shape — a broader semantic update than A's narrower verification step.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.83
- why: The midpoint (A) is a narrower verification step (check whether George Danzer is a WPT winner) and lacks explicit instruction to extract the subject's birth date/place or to prefer an entity-centric two-step retrieval; moving it to the target requires adding anchors (birth date/place), broadening the candidate set (if Danzer isn't the WPT winner, search WPT champions for anyone with four WSOP bracelets), and shifting the query shape from a single-hop verification to an entity-centric follow-up. B is already close to the target (it includes the birth-date/place anchors and a two-step query shape), so its implied prompt update is smaller.

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
- confidence: 0.86
- why: Transition B adds a substantive new retrieval requirement: not only fetch a WPT champions list but also consult player bios/WSOP records and cross-reference bracelet counts to filter winners to those with exactly four bracelets. That changes the retrieval spec (evidence families, multi-document joins, and filtering logic) more than A, which only asks to fetch and parse a single champions list.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Transition B requires a broader change in retrieval instructions: move from a narrow, single-person verification to fetching and parsing an authoritative, year-by-year WPT champions list, extracting and deduplicating many candidate names. That expands anchors, changes the query shape (from targeted lookup to list extraction + parsing), and shifts expected evidence and filtering behavior—so it is a larger semantic prompt-feedback update than the focused Danzer check in A.

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
- dominant_gap_type: answer_type
- confidence: 0.72
- why: A imposes a stronger, more specific change: it narrows the evidence family to concise etymological/identity statements, prioritizes encyclopedic/folklore sources, and prescribes pairwise high-precision query shapes while de-emphasizing broader cultural history. That is a broader retrieval-behavior revision than B's similar but less prescriptive equivalence-focused endpoint.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.79
- why: Transition B requires a bigger semantic shift: it moves from a broad, synonym-rich, transformation-focused retrieval instruction (multi-term queries that probe 'role shift' and many variants) to a narrow, high-precision entity-equivalence instruction emphasizing short pairwise queries and explicit 'originally the same being' links. That changes the query shape, relation emphasis (transformation → identity), and which distractor/variant terms to drop—whereas A's from_state is already narrowly aligned with the target.

## 149__split1__seg0

- idx: 149
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.87
- why: A changes the retrieval spec more fundamentally: it drops the Huld↔Holda/Frau Holle identity emphasis (removing those anchors/distractors) and refocuses the query on philological/etymological evidence and Huld-as-völva. B mainly tightens source style and requests explicit identity sentences but keeps the same anchors and identity target. Removing an anchor and shifting the core bridge relation is a bigger semantic update than narrowing evidence style.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: mixed
- confidence: 0.9
- why: Transition A changes the retrieval instructions more broadly: it narrows the evidence family (from broad cultural/history to concise etymology/encyclopedia statements), removes some peripheral anchors/noise, and shifts query shape to high‑precision pairwise queries. Transition B is a smaller, targeted addition (primarily adding the explicit Huld↔Holda identification) on top of an already etymology‑focused prompt.

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
- dominant_gap_type: mixed
- confidence: 0.87
- why: B requires a broader semantic shift: it moves the retrieval instruction from seeking comparative/etymological syntheses to actively retrieving primary attestations, motif-focused parallels, and mid-tier comparative scholarship. That changes anchors (attestations, saga/chronicle sources, motif lists), evidence family (primary sources and motif comparisons rather than just encyclopedia etymologies), and query shapes (attestation- and motif-focused queries), whereas A is mainly a narrowing to high‑precision authoritative identity/etymology statements.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.9
- why: Segment B starts from a broader, motif- and attestation-focused retrieval stance (looking for parallels, primary-source excerpts, and cautious hypothesizing). Moving it to the target state requires a bigger semantic rewrite: drop the emphasis on comparative motifs and primary attestations, add a strong preference for authoritative etymology/encyclopaedia identity-claims, and shift query shape toward high-precision pairwise identity queries. Segment A is already comparative/cognacy-focused, so its change to explicit identity is a smaller, more local narrowing.

## 150__split1__seg0

- idx: 150
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.73
- why: A's midpoint prescribes a broader retrieval-behavior change (favor title-targeted retrieval and explicitly prioritize lead-paragraph/snippet hits and surfacing the two primary pages) versus B's narrower tweak (use compact phrase-focused queries to surface exact affiliation lines). Title-targeting and hit-priority change query shaping and ranking instructions more substantially.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment B changes the retrieval instruction more substantially: it moves from a broad, noisy, multi-term biography/history query that surfaces many season pages and historical names to a narrowly focused prompt that asks for exact on-page affiliation lines and compact, phrase-targeted queries. This shifts both what distractors to remove (other seasons, historical 'Tartars', wide program pages) and the query shape to use, a bigger semantic update than A's minor addition (e.g., adding Tom Adams Field and slight phrasing tweaks).

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
- dominant_gap_type: mixed
- confidence: 0.78
- why: Transition B moves from a compact verification instruction to a broader endpoint that changes retrieval targets and priorities (explicit retrieved_titles, multiple season pages, and prioritizing coach/team/university pages for a canonical institution). That alters anchors, candidate breadth, and target page selection more than A's relatively narrow shift to page-title lookups.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.78
- why: Both transitions request essentially the same semantic change: preserve the same entity anchors (2012 team, Paul Winters, Wayne State University), target short on-page affiliation lines, avoid season/stadium/confference noise, and shift the query shape toward concise entity/phrase queries. The only minor wording difference (A favors page-title lookups; B favors compact phrase-focused queries) does not create a meaningful difference in retrieval-specification scope, so the implied prompt-feedback magnitudes are equivalent.

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
- dominant_gap_type: noisy_entity
- confidence: 0.74
- why: B imposes a more substantial change to retrieval instructions (prioritizes authoritative evidence families like obituaries/Hall-of-Fame, explicitly excludes noisy forums/irrelevant motorcycle pages, and prescribes exact-phrase + site-filter query shapes and follow-ups). A is mainly a narrower, surface-level refocus (alias mapping and conjunctive short queries) while B alters source preferences, noise filtering, and query shaping—a broader semantic update.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.85
- why: Both transitions require only small, similar refinements toward the same endpoint: preserving the same anchors (Bud Ekins, Steve McQueen, The Great Escape, Bullitt), emphasizing authoritative credit sources, and switching to narrow conjunctive phrase queries (with alias mapping). Neither from-state differs enough from the target to imply a substantially larger semantic update than the other.

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
- dominant_gap_type: anchor
- confidence: 0.92
- why: B expands the retrieval instruction beyond confirming The Great Escape: it explicitly reintroduces and requires resolution of the 'Bullitt' ambiguity, adds stronger requirement for primary/authoritative site-filtering and a separate follow-up search to confirm or deny Bullitt credits. That adds a new anchor and tighter query-shape constraints compared with A, which only narrows to The Great Escape and defers Bullitt.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.85
- why: Transition B adds a new anchor (explicitly checking 'Bullitt'), tightens source requirements, and turns a deferred ambiguity into an immediate verification step — a broader semantic change to what entities and checks the query generator must include than the relatively small refinement in A.

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
- confidence: 0.85
- why: A requires a broader prompt update: beyond confirming the artist and identifying the 11th studio album (what B requests), it also instructs the retriever to fetch the album’s official release date and target the specific album page/authoritative discography. That adds a new answer type (date), additional anchors (the album’s page), and extra evidence/verification steps, so it changes the retrieval instructions more than B’s narrower ordinal-identification focus.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.85
- why: Transition A changes the retrieval goal from merely identifying the 11th-album title (and avoiding non-studio releases) to also confirming the band identity in the question and extracting the album's official release date — a substantive addition to what evidence and answer type the query must target.

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
- confidence: 0.92
- why: Transition B requires an additional, qualitatively different retrieval goal — not only confirm band identity and the 11th-album title (as in A) but also to open the album page and extract the precise official release date (day/month/year). That expands the expected evidence type, adds a new query step targeting album-specific metadata, and tightens answer granularity, so it changes the prompt instructions more than A's year/identity-focused update.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.89
- why: Segment A adds substantive new instructions beyond identifying the 11th album: it requires confirming the ambiguous phrase maps to a specific anchor (Annihilator), requests extracting the album release year (not just the title/ordinal), and explicitly warns against pulling full day/month details. This broadens the retrieval spec (additional anchor verification, extra evidence field, and refined avoidance rule) compared with B's narrower ordinal-identification task.

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
- dominant_gap_type: query_shape
- confidence: 0.82
- why: From the shared midpoint, A only adds a single finalization step (retrieve the album's official release date). B, by contrast, expands the retrieval behavior substantially: it requires gathering multiple candidate dates, source provenance, region-specific variants, and cross-checking across album infoboxes, label/band announcements and major music databases. That is a broader change to what evidence to fetch and how queries should be shaped and prioritized.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.78
- why: Segment A prescribes collecting multiple candidate dates/sources assuming the band and album are already known; moving to the endpoint requires adding band-identification anchors and shifting from broad candidate-assembly to selecting a single authoritative release date. That combines adding new anchors (band ID) and changing the evidence/answer type — a larger semantic change than B's narrower step from year-only to full date.

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
- dominant_gap_type: mixed
- confidence: 0.86
- why: B changes the retrieval instructions more broadly: it adds the publisher anchor and requires the query to simultaneously confirm actor->character and character->publisher links (two-hop coupling and different evidence families), whereas A is a narrower refocus that only preserves actor->role anchors and intentionally defers the publisher step.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.87
- why: Segment A requires changing the prompt from a narrowly actor-focused step that intentionally avoids publisher/comics pages to one that also seeks and anchors the character->publisher link (adding Marvel Comics as an explicit anchor, removing the ‘avoid publisher pages’ constraint and emphasizing the character→publisher bridge). Segment B already includes both actor+character and publisher intent, so its update is smaller.

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
- confidence: 0.92
- why: Segment B requires a substantive refocus of retrieval anchors and behavior — it removes the actor-centered instruction and redirects queries to character/comics pages and infobox publisher lines. A mainly preserves the original actor->character focus and only adds a publisher-check, a smaller additive change.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.84
- why: B requires flipping an explicit avoidance (no publisher/comics pages) and adding a new evidence family and anchors (Quicksilver (comics), Marvel Comics, publisher lines) on top of the existing actor->character focus. A mostly only needs to add an actor anchor to an already comics/publisher-focused prompt, so B implies a broader semantic change to the retrieval instructions.

## 247__split0__seg0

- idx: 247
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: A represents the full endpoint shift to explicitly seek a named online protest label (campaign title/hashtag) and to reorient queries toward news/social media coverage of the 2016 Ghana transfer—a broader change in retrieval goals and anchors. B is a narrower midpoint that mainly tightens evidence type (quoted hashtags/embeds, wildcarded hashtag patterns) without changing the overall goal as much.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.74
- why: Both transitions ask essentially the same semantic update: refocus the hop-2 query on finding a named online campaign/hashtag in contemporary news or social media tied to the Jan 2016 Ghana Gitmo transfer. Neither imposes a substantially different set of anchors, bridge relation, evidence type, or avoidance of distractors.

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
- why: Segment A imposes a stronger change in retrieval behavior by shifting source anchors to Ghana-focused news outlets and activist social pages (specific domains and social accounts) and adding new bridge clues like Change.org/embedded links — a substantive redirection of where and how to search. Segment B mostly refines query phrasing and token matching (quoted hashtags, wildcarding) without as large a change to source anchoring.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.9
- why: Segment B moves from a generic base query to a focused retrieval specification that adds multiple constraints (limit to contemporary Ghanaian news/social media, emphasize reproduced/quoted campaign identifiers, target OccupyGhana/NPP links to online actions, and change query shape to allow hashtag/petition patterns). A is a much smaller, local narrowing (minor tweaks like preferring quoted identifiers and wildcarded hashtags) from an already-specific state.

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
- confidence: 0.82
- why: Segment B prescribes a more substantial change to the query-generator: it adds specific high-value anchors (GhanaWeb, JoyOnline, Change.org) and explicit site-restriction/search tactics and example campaign-name targets, shifting both where to search and how to shape queries. A is a milder, more general local-focus refinement.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.78
- why: Transition A changes retrieval focus broadly from general Gitmo/detainee pages to a Ghana-centered, social-media-and-local-news oriented search: it adds new anchors (Ghanaian outlets, OccupyGhana social pages), introduces platform-specific bridge clues (Change.org, Facebook, hashtag), and narrows noisy sources to avoid — a bigger semantic rewrite of what to look for than B, which is a smaller refinement among already-local sources.

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
- confidence: 0.82
- why: Segment A shifts the retrieval strategy from a game-centric lookup to a designer-centric one — it changes the primary anchor (focus on Kunihiko Tanaka's filmography/credits), adds new target sources (artist portfolio, filmography pages), alters noisy-entity avoidance, and changes the query pivoting behavior. B is mainly a narrower refinement (exact-entity queries confirming the same game/credit), so A implies a broader semantic update.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.84
- why: A's transition requires a bigger semantic shift: it moves from a designer-centric, filmography-focused retrieval strategy (preserve artist/credits anchors, avoid noisy Xeno-series links) to a game-centric, exact-role verification strategy targeting Xenoblade Chronicles X and Monolith Soft. That changes the primary anchors, the bridge relation (creator-side evidence → game-credit confirmation), and the query focus more than B's smaller refinement.

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
- dominant_gap_type: query_shape
- confidence: 0.83
- why: Segment B prescribes a more substantive reframing: it not only asks for concise show-focused queries but explicitly reorders retrieval priorities (main series article, episode list, creator bios), specifies bridge phrasing ('created by / developed by'), and enumerates noisy sources to avoid. That is a broader, more specific change to retrieval behavior than A's relatively general instruction to use concise show+writer keywords and avoid actor-centric queries.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.95
- why: Segment B starts from a long, name- and episode-heavy query and requires a broader rewrite: remove enumerated person/episode tokens, de-emphasize actor-centric anchors, and replace with concise show-focused instructions (e.g., 'Smallville creators/writers' or creator names). Segment A already encodes much of that shift (a midpoint that narrows focus), so B implies a larger semantic update to the query-generation prompt.

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
- dominant_gap_type: query_shape
- confidence: 0.72
- why: Both transitions propose the same semantic change: collapse a long, name-heavy query into a concise, show-focused query that preserves 'Smallville' and the two primary creators (Alfred Gough, Miles Millar), adds explicit 'created by' / series-credit framing, and removes peripheral episode and secondary-writer anchors. The requested retrieval refocusing and noise removal are essentially identical in scope.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.79
- why: Segment B spans a bigger semantic shift: it moves from a long, name- and episode-enumerating query (many noisy person/episode anchors) to a concise show-focused query that explicitly anchors on the series and its two creators. Segment A is a smaller, local refinement between two already-similar midpoint states.

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
- confidence: 0.61
- why: Both transitions propose essentially the same semantic update: move from a long, name-heavy query to a concise, show-level query that preserves the Smallville anchor and the two primary creators (Alfred Gough, Miles Millar), drops peripheral episode and secondary-writer anchors, and keeps the actor (Justin Hartley) only as a bridge. The differences are minor wording/emphasis rather than substantive changes to retrieval instructions.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Transition A changes the query shape substantially: it moves from a long, name- and episode-heavy query to a concise, show-plus-creators form, explicitly removing many noisy person/episode anchors and refocusing retrieval on series-level credits and the two primary creators. Transition B is a much smaller refinement from an already narrowed, similar midpoint to the same target.

## 268__split0__seg0

- idx: 268
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.73
- why: Segment B prescribes a broader semantic change: it expands and adds anchors/entities (Henry Yorke, Party Going, Henry Green page) and explicitly instructs retrieving occupation lists for both Henry Green and G.K. Chesterton, increasing the candidate set and disambiguation targets. Segment A is a narrower, incremental step focused mainly on resolving Henry Green first.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.83
- why: Segment A requires a stronger reorientation: it adds an explicit pen-name anchor (Henry Green = Henry Vincent Yorke), prioritizes disambiguation before any comparison, and mandates an exact-entity query shape to avoid confusing similarly named persons. B largely makes a narrower correction (split an ambiguous multi-target query into two focused queries). A therefore changes the retrieval instructions more substantially.
