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
- dominant_gap_type: anchor
- confidence: 0.85
- why: Segment A moves from a missing-evidence state to a target state that actually retrieves the 'Solo (Australian soft drink)' page, resolving the missing-entity gap and enabling a direct country-of-production comparison with La Croix. Segment B is an intermediate disambiguation/refinement step without concrete retrieval—less change in answerability/evidence.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A shows a bigger shift: the from_state is a disambiguation-focused, empty-retrieval midpoint (no retrieved titles) and broad anchor list, while the to_state contains concrete retrieved titles (including 'Solo (Australian soft drink)') and a narrowed retrieval focus. This represents a larger retrieval/anchor correction and disambiguation step than B, which already started with the Solo (Australian) title present and required only minor refinement.

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
- confidence: 0.78
- why: Segment A jumps directly to the target product page set (retrieved_titles include 'Solo (Australian soft drink)' and other product pages) and thus makes a larger retrieval-focus change—moving from a missing-entity hint to fetching the actual entity page—whereas B only performs a narrower disambiguation/preview step before full retrieval.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: noisy_entity
- confidence: 0.72
- why: Segment B introduces an explicit disambiguation step (resolve which 'Solo' is intended) and changes the retrieval strategy from directly targeting a specific product page to first resolving the ambiguous surface form. This is a larger correction addressing noisy-entity/alias ambiguity and alters the evidence-family (disambiguation entries → product page) more than the minor focus refinement in A.

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
- confidence: 0.86
- why: Segment B moves from a generic retrieval intent to concrete, answer-directed results — it adds specific candidate actresses and cast anchors (e.g., Donna Reed, Deborah Kerr, Kim Basinger) and thus materially narrows the search space toward answerability. Segment A only produces a disambiguation/plan step without adding concrete actor evidence.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.83
- why: Segment A moves from a disambiguation/candidate-generation focus (listing possible 'Third Person' works and candidate actress sets) to concrete authoritative cast retrieval and introduces specific actress anchors (e.g., Deborah Kerr, Donna Reed). This is a larger change in retrieval focus and required anchors than B, which already started with explicit film-year cast queries and thus required a smaller adjustment.

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
- confidence: 0.87
- why: Segment B makes a substantive shift from disambiguation to concrete, date-anchored targets: it narrows the ambiguous titles to specific years (Third Person → 2013; From Here to Eternity → 1953) and changes the retrieval goal to fetching top-billed actresses for those exact entries. That is a larger retrieval-focus and entity-anchoring change (resolves ambiguity and materially increases answerability) than A, which stays broader/endpoint-oriented and retains ambiguity.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: Segment A moves from a broad disambiguation task (enumerating all candidate 'Third Person' works and versions of 'From Here to Eternity' and pulling top-billed actresses for each) to focused authoritative cast retrieval — a substantial shift in retrieval focus and requires resolving title ambiguity and assembling multiple entity-specific cast sets. Segment B is already narrowed to a single candidate pair (2013 Third Person and 1953 From Here to Eternity) so its transition to the same target is much smaller.

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
- confidence: 0.82
- why: Segment B shifts the retrieval family from album/database pages toward film-level credits and encyclopedia intros that explicitly tie the soundtrack to its performer and list that performer's occupations. This is a bigger functional change in evidence type (adding occupation-summary sources) compared with A, which is only a narrower album/database focus and is closer to the original intent.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: Segment A changes from a broad biography/discography/filmography search (wide artist-focused query) to a narrowly targeted album/soundtrack entry search. Segment B already starts from a film-level/encyclopedia focus and makes a smaller, more incremental shift to album pages. A therefore represents a larger retrieval-focus and query-shape update.

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
- confidence: 0.84
- why: Segment B makes a more concrete, outcome-oriented change: it moves from a general verification goal to explicitly confirming which WPT champion has four WSOP bracelets and retrieving that person's birth date (and includes updated retrieved_titles). Segment A is an intermediate planning step that merely outlines search strategies without adding concrete retrieval targets or results. B therefore represents the larger retrieval-focus and evidence-seeking update (resolving the entity↔WPT link and extracting a date).

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.83
- why: Segment A's from_state is a narrower, earlier midpoint (no retrieved titles) focused on verifying the link between George Danzer and a WPT title; the to_state expands retrieval targets and introduces the explicit need to find a WPT champion who also has four WSOP bracelets and birth date. This is a larger correction (establishing/repairing the entity–event relationship) than B, whose from_state already contained many relevant anchors, titles, and the birth-date hypothesis.

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
- confidence: 0.82
- why: Segment A makes a bigger shift: it moves to an endpoint task that adds concrete retrieval targets (several specific pages/titles) and a new answer requirement (retrieve the winner's birth date and confirm the WPT↔four-WSOP-bracelets link). Segment B is a narrower, intermediate shortlist-building step and does not add the date/answer retrieval or the explicit document targets.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.78
- why: Segment B changes the retrieval shape and scope more — from verifying a single candidate to systematically cross-referencing the entire WPT champions list with WSOP bracelet counts to produce a shortlist. This requires broader retrieval, more relations to resolve, and more evidence-family changes than the targeted verification in A.

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
- confidence: 0.88
- why: Segment B moves beyond merely extracting a list of WPT winners (as in A) to cross-reference those winners with WSOP bracelet counts and produce a shortlist of WPT champions who have four WSOP bracelets. This requires an additional entity-attribute linking step and narrows retrieval toward the answer, so it represents a larger retrieval-focus change.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.87
- why: Segment B's from_state is focused narrowly on retrieving an authoritative, year-by-year WPT winners list and extracting names. Its to_state shifts the task substantially to cross-referencing those names with player bios/WSOP records to identify which WPT winners have four WSOP bracelets — a notable change in retrieval goal and required joins across sources. By contrast, segment A's from_state already contained the verification/cross-reference intent (checking Danzer and finding any WPT champion with four bracelets), so its transition to the same to_state is smaller.

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
- confidence: 0.82
- why: Segment A makes a substantive shift in retrieval focus and bridge clues — it narrows from a broad search to explicitly target authoritative etymology and comparative-mythology statements that assert an identity claim (explicit sentence: 'the hulder is originally the same being as Huld') and prioritizes encyclopedic/etymological sources. Segment B shows only minor endpoint tweaks to retrieved titles and keeps a very similar retrieval focus. Therefore A represents the larger update.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Segment A moves from an abstract generated midpoint (no retrieved titles, only a narrow search instruction and anchor list) to a concrete endpoint with many specific retrieved pages and explicit bridge clues asserting the identity claim. This is a bigger change in retrieval focus and the addition of direct evidence/links tying hulder to Huld/Holda than in B, which already started with similar anchors and retrieved titles and thus required a smaller adjustment.

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
- confidence: 0.78
- why: Segment A changes the retrieval goal more substantially: it narrows from verifying an identity chain (hulder→Huld→Holda) to a philological/etymological focus and explicitly drops/asserts less about the Huld↔Holda equation. This is a substantive bridge-relation/anchor correction (shifting which identity links are pursued) rather than a light rephrasing or source-type preference.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.83
- why: Segment A makes a larger shift in retrieval focus: it moves from a broad endpoint (many titles and a wide comparative/generic focus) to a tightly narrowed search for authoritative etymology and explicit identity claims (explicit sentence linking hulder→Huld and Huld↔Holda/Frau Holle). Segment B starts already narrowly focused on name-origin and Huld's role and only refines to the same target, so its update is smaller.

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
- confidence: 0.78
- why: Segment A shifts the retrieval focus from general comparative links to a narrowly targeted search for authoritative etymology/encyclopedic statements that explicitly identify the hulder with Huld and equate Huld with Holda/Frau Holle. This is a stronger, more specific change in evidence requirements (seeking an explicit identity sentence and high‑authority sources) than Segment B’s softer move toward comparative parallels and hypotheses, so A represents the larger update.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.85
- why: B shifts from gathering intermediate comparative attestations and motif-parallels (a scholarly-hypothesis/evidence-collection focus) to demanding authoritative, explicit etymology/encyclopedic identity statements that directly equate hulder→Huld→Holda/Frau Holle. This is a bigger change in the type of evidence sought (from parallels/attestations to one-line identity claims) than A, which was already moving toward comparative-mythology links and thus requires a smaller narrowing to explicit identity statements.

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
- confidence: 0.78
- why: Both segments make nearly identical updates: same start state and virtually the same retrieval focus, anchors, and bridge clues (both aim to locate the season page and coach bio to confirm affiliation). There is no substantive difference in retrieval direction or correction type to prefer one over the other.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.84
- why: Segment B moves from a broad, initial retrieval (explicit long query and many retrieved titles) to a focused confirmation state — a larger shift in retrieval focus and anchor consolidation (narrowing noisy candidates to the specific affiliation pages) than A, which already started targeted.

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
- confidence: 0.74
- why: Segment B moves from a planning-state to an endpoint with concrete retrieved titles and a focused retrieval goal, representing a bigger change in retrieval focus and evidence family. A only refines the fetch instruction without adding actual retrieval targets.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.9
- why: Both A and B show effectively the same retrieval-focus change: moving from a midpoint intent to fetch/confirm the season and coach pages toward the identical Rstar_target list and the same goal (establish affiliation with Wayne State University). The only minor difference is B's inclusion of 'Tom Adams Field' in anchors, which is a trivial, non-substantive addition. No segment shows a clearly larger change in focus, entities, or answerability.

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
- confidence: 0.81
- why: Segment B shifts the retrieval strategy from a general verification task to a focused, authoritative credit-confirmation approach: it adds new anchors (obituary / Stuntmen's Hall of Fame), specifies exact bridge phrases (e.g. "stunt double for Steve McQueen", "performed the motorcycle jump"), and changes expected evidence sources and query-shape (prioritize obits/biographies/film-credit databases). This is a larger change in retrieval focus and query formulation than A, which mainly lists retrieved titles and noisy items without substantially changing the evidence-selection strategy.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.87
- why: Segment A moves from a generated midpoint (planning-only focus, no retrieved titles) to a concrete endpoint with explicit retrieved documents, detailed retrieval_focus, expected evidence type, and query-shape guidance. Segment B already started as a full query/endpoint with similar retrieved titles and focus, so its change to the same target is much smaller.

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
- why: Segment A advances from merely confirming the band to actively locating the band's 11th studio album and its official release date (adds specific album pages and a date-focused retrieval step). This is a bigger shift in retrieval focus and requires resolving the answer-type (a date) and identifying the correct album entry, whereas B only aims to confirm ordinal position.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.83
- why: Segment A shifts from a narrow verification task (confirm the 11th studio album title/ordinal) to a broader target that now also requires the album's official release date and band identification—adding a new information type and additional page retrievals. Segment B already included the release-date goal in its initial query, so its transition is smaller.

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
- dominant_gap_type: answer_type
- confidence: 0.82
- why: Segment B moves beyond simply identifying the 11th album and a single 'official' date (segment A) to a deeper evidence-collection step: it gathers and reconciles multiple cited release-date entries, regional variants, and source provenance (infobox, label, databases, press). That represents a larger change in retrieval focus and a bigger evidence/answerability gap requiring disambiguation and cross-source reconciliation.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.86
- why: Segment A expands the retrieval focus substantially: instead of only confirming the band identity and the 11th-album title/year (as in B), it requires opening the album's primary pages, extracting multiple candidate release dates, capturing citation URLs, and reconciling region-specific date variants — a deeper, more complex evidence-collection and disambiguation step.

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
- confidence: 0.82
- why: Segment B makes a bigger shift in retrieval focus and evidence: it moves from the base intent to concrete endpoint results (adds 'Evan Peters' and 'Quicksilver (comics)' in retrieved titles) and explicitly targets both the actor->character link and the character->publisher confirmation. By contrast, A narrows the focus only to confirming the actor portrayal and explicitly avoids publisher pages, a smaller, more conservative refinement.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.84
- why: Segment A makes a substantive retrieval-focus shift: the from_state explicitly avoids publisher/comic pages and concentrates solely on actor->role confirmation, while the to_state adds the publisher confirmation (Marvel Comics) and new anchors (Quicksilver (comics), Marvel Comics). This introduces a new bridge (character->publisher) and changes the evidence-family sought. Segment B is already targeting both actor->character and publisher and shows minimal change.

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
- dominant_gap_type: bridge_relation
- confidence: 0.78
- why: Segment B makes a bigger retrieval-focus shift: it moves from actor/filmography verification to authoritative comics-character/publisher sources (a different evidence family) to confirm Quicksilver's publication provenance. This requires changing anchors and bridge relations (actor→character→publisher) and corrects the earlier actor-focused plan; A mostly augments the original focus by adding publisher confirmation and retrieved titles, so it is a smaller step.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.66
- why: Both segments make a symmetric, single-hop change: A moves from comics-only sources to also include the actor (Evan Peters), while B moves from actor/filmography sources to also include comics/publisher confirmation. Each adds a missing anchor of equal importance for answering the question, so neither shows a clearly larger retrieval-focus change.

## 227__split3__seg2

- idx: 227
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.78
- why: Segment B shifts retrieval focus from the generic character identity task toward confirming the actor→role mapping (Evan Peters → Quicksilver/Pietro Maximoff) and then gathering varied contextual signals (cast lists, filmography, team affiliations, issue references). This requires a larger bridge-relation correction and a broader change in source types (film/TV cast and entertainment pages plus comic-context), whereas A mainly targets authoritative comic pages to confirm the publisher (a narrower anchor/publisher check).

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.84
- why: Segment A moves retrieval focus more strongly from an actor-centric identity check (Evan Peters → Quicksilver/Pietro) to a distinct comics-authority lookup (Quicksilver (comics) / publisher lines). That is a larger entity-anchor shift (actor/film pages → canonical comic entry/publisher) than B, which already included comic-ecosystem signals (X‑Men/Marvel ties) and thus makes a smaller, more incremental shift to publisher confirmation.

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
- confidence: 0.8
- why: Segment B introduces a clear, substantive narrowing of retrieval scope: it shifts from a general topical search to explicitly targeting contemporary news and social‑media coverage that quote or reproduce campaign identifiers (hashtags, e‑petitions, Facebook/Twitter campaign names). That is a bigger change in retrieval shape and evidence family than A, which largely preserves the original focus and anchor set.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.74
- why: Segment B moves from a generated midpoint with no retrieved titles and a descriptive, narrow focus on social‑media/news quoting hashtags to a concrete target state that adds multiple retrieved titles and a clear retrieval goal — a larger shift in retrieval content and focus. Segment A’s transition is comparatively minor (similar anchors/bridge clues and only small changes in retrieved titles).

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
- confidence: 0.78
- why: Segment B narrows the retrieval focus more substantially by adding a new class of high-yield anchors (Change.org and major petition platforms) and specifying concrete signals to look for (petition titles/URLs, embedded tweets, quoted campaign names). This is a bigger shift from the base than A's broader emphasis on local news/outlet and social pages.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.88
- why: Segment A moves from a general R0 search (broad query and mixed retrieved titles) to a more focused plan that limits retrieval to Ghana-focused news outlets and activist social pages, adding specific local anchors and platform-oriented bridge clues (Change.org, Facebook, hashtags). Segment B shows little-to-no change (its from and to states are essentially the same targeted focus), so A represents the larger retrieval-focus/update magnitude.

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
- dominant_gap_type: answer_type
- confidence: 0.86
- why: Segment B moves from a general plan to a concrete, answerable endpoint: the retrieval_focus explicitly targets an authoritative credit/encyclopedia page that names the video game (Xenoblade Chronicles X) and the to_state includes retrieved_titles with the target. This is a clear answerability/evidence-family change. By contrast, Segment A only shifts the approach (game-centric → designer-centric) without producing the specific target or evidence, so its update magnitude is smaller.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A shifts retrieval focus more dramatically: it moves from a designer-centric, filmography/credits search to a game-specific verification target that adds explicit game anchors (Xenoblade Chronicles X, Monolith Soft) and prescribes exact-entity query shapes and evidence types. Segment B is already game/credit-focused, so its update to the same endpoint is a smaller refinement.

## 267__split0__seg0

- idx: 267
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
- why: Segment B represents a substantive shift in retrieval strategy: it corrects a noisy, name- and episode-heavy retrieval and refocuses on concise, show-level authoritative sources (Smallville main article, episode list, and creator bios). That change reduces noise and alters the query shape/target evidence family more than A, which only slightly adjusts retrieved titles while keeping the same goal.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: noisy_entity
- confidence: 0.86
- why: Segment A describes an explicit shift away from a noisy, name-heavy retrieval (many person/episode pages) to concise, show-level sources (Smallville main article, episode list, creator bios). That is a larger change in retrieval focus and correction of noisy-entity results than the B transition, whose from_state is already focused on the same target.

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
- confidence: 0.75
- why: Both segments perform effectively the same update: they shorten a verbose, name-heavy query to focus on show-level sources and the two primary creators (Alfred Gough and Miles Millar). The retrieval_focus, anchors, and bridge_clues in the to_state are nearly identical, with only minor wording differences that do not change the retrieval intent or magnitude.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment B moves from a verbose, name-heavy concrete query listing many episode- and person-level targets (multiple writer names and episode pages) to a concise, show-level retrieval focus that prioritizes the Smallville main article and the two creator bios. That is a larger pruning/change in retrieval focus than A, which is essentially a small rewording between two similar concise midpoints.

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
- why: Both segments perform nearly identical narrowing of the retrieval focus: they drop peripheral episode-level pages and many secondary writer names and redirect to authoritative show-level sources (Smallville main article, List of episodes, and creator bios for Alfred Gough and Miles Millar). The small wording differences (A explicitly keeps the actor bridge; B mentions press/industry pages) do not constitute a clear larger update in retrieval focus or correction magnitude, so neither segment is meaningfully larger.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.83
- why: Segment A moves from a verbose, name-heavy starting query with multiple retrieved episode/writer targets to a much more focused retrieval goal (Smallville main article and the two creator bios). That is a substantive reduction in retrieval scope and a clearer shift in focus. Segment B instead transitions between two very similar midpoints (both already narrowed to show-level sources and creators), so it represents a smaller, fine-grained refinement.

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
- dominant_gap_type: noisy_entity
- confidence: 0.76
- why: Segment A makes a stronger shift away from the original name-heavy, episode-level query by explicitly avoiding episode pages and long enumerations of secondary writers and refocusing on the series-level article and creator bios. That is a bigger retrieval-focus and noisy-entity correction than B, which largely preserves the 'list of episodes' anchor and thus makes a smaller narrowing.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.86
- why: Segment A shows a substantial narrowing of retrieval focus: it moves from a long, name-heavy query listing many individual writers and episode pages to a targeted intent for authoritative show-level sources (main article, list of episodes, creator bios). That change removes noisy secondary writer/episode hits and refocuses anchors to primary creators (Alfred Gough, Miles Millar) and the series page — a bigger correction than B, which only makes a modest rewording of an already similar series-level intent.

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
- confidence: 0.86
- why: Segment B shows a concrete retrieval outcome: it fills the missing Henry Green entity (adds retrieved titles like 'Henry Green', 'Party Going', 'Henry Yorke') and expands anchors, directly resolving the main gap. Segment A is a planning/intermediate step focused on how to search but does not add new retrieved evidence.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.78
- why: Segment A moves from a high-level generated midpoint (no retrieved titles) that frames a targeted need to resolve and disambiguate Henry Green to a concrete endpoint with explicit retrieved titles and a clarified retrieval focus. This is a bigger change in retrieval focus and grounding (adds explicit anchors and resolves the missing-entity/ambiguity planning) than B, whose from/to states are already similar and contain many of the same anchors.

## 268__split2__seg0

- idx: 268
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.79
- why: Segment A expands the retrieval focus more substantially — it shifts from a missing target to actively pulling disambiguation and multiple candidate biography pages to resolve which 'Henry Green' is relevant and to avoid conflation with Joseph Henry Chesterton. That requires broader entity disambiguation and candidate gathering rather than the narrow pen-name/lead confirmation in B.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.82
- why: Segment A moves from a broad base state that mixes multiple people (G. K. Chesterton, Joseph Henry Chesterton) and an absent target (Henry Green) to a focused identity-confirmation retrieval (pen-name mapping and concise lead). That is a larger retrieval-focus shift than B, which already starts narrowed toward Henry Green disambiguation and only tightens candidate-page selection.

## 268__split3__seg2

- idx: 268
- split_iter: 3
- num_edges_before_split: 4
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: surface_form
- confidence: 0.73
- why: Segment B expands the retrieval scope beyond identity confirmation to resolve full biographical/occupation information and notable roles, includes an explicit disambiguation check, and prepares a follow-up fetch for Chesterton’s occupations. That is a larger retrieval-focus change than A, which only seeks a lead sentence and a brief (1–3 role) career summary.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.75
- why: Segment B requests a wider retrieval (lead sentence plus the opening career/biography paragraph) versus A's single concise identity/infobox line. B therefore requires more new evidence and a larger change in retrieval focus—confirming the pen-name mapping and extracting multiple role mentions—so it produces a bigger update to the R-state.

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
- confidence: 0.82
- why: Segment A shifts the retrieval focus from confirming the film's nationality to a broader verification that links both items — it introduces the complementary entity (Amsterdam/Capital of the Netherlands), explicit 'Dutch culture' anchor, and endpoint evidence (retrieved titles) aimed at confirming a shared national/cultural origin. This is a larger conceptual and anchor-level change than B, which mainly pivots to city-specific supporting details.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.78
- why: Both segments perform essentially symmetric retrieval shifts: A moves from a film-centric focus (confirming Amsterdamned is Dutch) to a shared-culture verification (adding Amsterdam/Netherlands anchors), while B moves from a city-centric focus (confirming Amsterdam is the Dutch capital) to the same shared-culture target (adding the film anchor). Each introduces a comparable entity-anchor and bridge relation change with similar evidence-family implications, so neither clearly dominates.
