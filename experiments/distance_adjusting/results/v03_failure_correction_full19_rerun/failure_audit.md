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
- confidence: 0.86
- why: Segment B more strongly fixes the core failure: it explicitly instructs disambiguation to the canonical 'Solo (Australian soft drink)' page, enumerates the concrete infobox/lead/manufacturer signals to look for, and broadens anchors to avoid the Norwegian/other-Solo senses. A mainly narrows the query wording (add 'Australian' / exact title) and is a smaller refinement.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.87
- why: Segment A explicitly changes the core retrieval target by correcting the ambiguous entity anchor — it demands disambiguation to the canonical 'Solo (Australian soft drink)' page and instructs the query to avoid regional/noisy variants. B mostly refines wording and warns about manufacturer tokens biasing results, a smaller, surface-level refinement.

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
- confidence: 0.91
- why: Segment A directly corrects the main retrieval failure by anchoring the query to the canonical target entity (Solo (Australian soft drink)) and specifying extraction from its infobox/lead, which changes the generator's core retrieval target. Segment B mainly adds a disambiguation-step/process refinement rather than replacing the wrong anchor itself.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.86
- why: Segment B changes the query-generator behavior to perform explicit disambiguation of the ambiguous title 'Solo' (resolve which regional product is meant) before fetching details. That resolves the core ambiguity/anchor failure, whereas A assumes the Australian page and only narrows extraction to its infobox/lead (a smaller, post-anchor refinement).

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
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A directs a fundamental change: disambiguate the title 'Third Person' and build candidate actor sets per specific work/version before intersecting—fixing the main anchor ambiguity. Segment B only prescribes running precise cast queries (a narrower, extraction-focused refinement).

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.95
- why: Segment A forces a structural change: disambiguate the ambiguous title 'Third Person', enumerate candidate works/years and produce per-version actress sets before intersecting with 'From Here to Eternity' — correcting the main anchor and candidate-selection failure. Segment B merely refines to specific year/version cast queries (a narrower, downstream extraction step).

## 132__split0__seg0

- idx: 132
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.95
- why: A shifts the core query behavior: it redirects generation from broad biography/film pages to short, entity-centric jumps (film -> soundtrack -> artist) and explicitly prioritizes artist/album pages — a fundamental change to the retrieval target and query shape. B is a narrower refinement (seek album credits/liner notes) after the correct target is already identified.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.87
- why: Segment A shifts the retrieval candidate set and removes broad-biography distractions by explicitly steering queries toward authoritative soundtrack/album credit sources and album-credit–oriented query shapes (mid-granularity) instead of generic biography dumps. This corrects the core retrieval failure (targeting the soundtrack credit) rather than only refining query wording.

## 132__split1__seg1

- idx: 132
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment B changes the retrieval target set and query behavior more fundamentally — it redirects the generator from generic entity jumps to album/release-level authoritative sources (Wikipedia album page, label press release, AllMusic/Discogs) to establish soundtrack attribution. That is a bigger failure-mode correction than A's simpler entity-centric/jump query and occupation-confirmation phrasing, which is more of a narrower refinement.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Segment A shifts the retrieval anchor from broad Björk bios to authoritative album/soundtrack credit sources and explicitly demands linking the Selmasongs soundtrack to Björk (and her occupations/nationality), a broader correction to the core retrieval target and query shape. B mainly narrows to album-level attribution only and defers occupation verification, so it is a smaller, more incremental fix.

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
- confidence: 0.91
- why: Segment B pivots the retrieval target from album-release databases to film-level credits plus the artist lead paragraph — a broader change in query strategy and candidate set that alters the bridge relation (film→performer) and the query shape more fundamentally than A’s narrower album-focused redirection.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.95
- why: A corrects the main retrieval failure by shifting from a broad biography/discography search (which produced noisy touring/book results) to a targeted album/soundtrack evidence family (Selmasongs/album-level pages). This changes the query shape and retrieval target more fundamentally than B, which is already film/lead-paragraph focused and only refines to album entries.

## 140__split0__seg0

- idx: 140
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
- why: Segment A explicitly changes the core anchor strategy—first verify whether George Danzer is actually a WPT champion and, if not, switch to searching the WPT champions list for any player with four WSOP bracelets—thus altering the candidate set and primary retrieval target. B mostly refines the verification and extraction steps without as strongly shifting the anchor.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A changes the core retrieval anchor and strategy: it explicitly questions the assumed candidate (George Danzer), directs a verification step, and, if Danzer is not the WPT winner, instructs searching the WPT champions list for an alternative with four WSOP bracelets — a fundamental change in which entity set the second-hop must target.

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
- dominant_gap_type: anchor
- confidence: 0.81
- why: Segment A directly corrects the primary retrieval failure by insisting on verifying the WPT↔four-WSOP-bracelets link for the candidate and then extracting the birth date — it changes the anchor/target and final extraction goal. Segment B only reorganizes the search into a shortlist step (procedural refinement) without fixing the core anchor/extraction in one step.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.88
- why: Segment B changes the retrieval strategy fundamentally: instead of a narrow verification of one candidate (Danzer) with a possible fallback, it instructs a systematic cross-reference of the entire WPT champions list against WSOP bracelet counts to produce a shortlist. That alters the query shape and candidate set the generator must produce, a bigger behavioral correction than A's targeted check.

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
- dominant_gap_type: query_shape
- confidence: 0.77
- why: Both transitions apply the same substantive correction: shift from broad multi-term retrieval to short, high‑precision entity-to-entity/etymology queries that seek an explicit definitional sentence linking hulder↔Huld↔Holda. Neither changes the main anchors, bridge relation, or candidate set, so their prompt-feedback magnitude is effectively equal.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why: Segment A changes the retrieval strategy more fundamentally — it shifts from a broader or underspecified search to a narrow, high‑precision etymology/identity emphasis (concise pairwise queries and prioritizing short authoritative identity claims), removing distracting hits and focusing the query shape and evidence type. B is already close to the desired multi-term target and represents a smaller refinement.

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
- confidence: 0.89
- why: Segment B corrects the core retrieval failure by demanding explicit, authoritative identity claims linking hulder→Huld and Huld↔Holda/Frau Holle (changing the bridge relation and target evidence). Segment A only narrows to etymology and Huld's role (a partial, smaller step toward the full identity claim).

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Segment B adds the key identity/bridge (Huld ↔ Holda/Frau Holle) that was missing in the from_state, changing the retrieval target and required relation to be expressed. A mainly refines source type and query shape around anchors already present, so it is a smaller, precision-focused update.

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
- confidence: 0.91
- why: Segment A forces a fundamental change in retrieval behavior: move from exploratory comparative material to high‑precision, authoritative identity claims (explicit one-line equivalence hulder → Huld and Huld ↔ Holda). That corrects the main failure (no direct identity anchor) rather than merely gathering parallel motifs or attestations as in B.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.81
- why: Both transitions make a comparable, substantive shift: they move from gathering comparative/motif evidence toward requiring concise authoritative etymology or an explicit identity claim linking hulder→Huld and Huld↔Holda/Frau Holle. Each changes the bridge relation the query must express (from parallels/hypotheses to a direct identity statement) rather than merely refining extraction details, so their failure‑correction magnitude is similar.

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
- dominant_gap_type: query_shape
- confidence: 0.68
- why: Both transitions make the same, small correction: they keep the same anchors (team, coach, university) and mainly refine the query shape to surface explicit affiliation lines. Neither changes the main retrieval target or fixes a core anchor/bridge error, so their feedback magnitudes are equivalent.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.72
- why: A corrects the core query-shape and distractor problems (replacing a long noisy query with short entity-centered queries and warning about historical name noise), which changes retrieval behavior more fundamentally; B mainly refines evidence phrasing to surface exact affiliation lines.

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
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Both segments correct the same core failure: they steer the query generator away from broad/multi-season noise toward short, title- or phrase-focused queries that surface explicit affiliation lines on the season and coach pages. Neither introduces a fundamentally different anchor, bridge relation, or candidate set—both are comparable, small refinements to query shape and target snippets.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: Segment B corrects a noisy, over-broad endpoint query into compact, title-targeted phrase queries that remove multi-season and topic noise—this is a substantive change to the query shape and retrieval target. Segment A already targets the correct pages and mostly refines snippet/lead-paragraph focus, so its feedback is smaller.

## 150__split2__seg2

- idx: 150
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment A requires a stronger behavioral change: switch to exact page-title/entity lookups to fetch the canonical 2012 team and Paul Winters pages and extract explicit affiliation lines. B gives a similar goal but is a softer, more permissive instruction (short entity queries and a wider candidate list) so it is more of a refinement than a corrective shift.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Both segments correct the same primary retrieval failure (targeting the canonical team and coach pages to extract affiliation lines) and differ only in minor query-shaping preference (A favors exact page-title lookups; B favors compact phrase queries). Neither makes a broader correction to anchors, bridge relation, or candidate set, so their feedback magnitude is equivalent and small.

## 169__split0__seg0

- idx: 169
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.72
- why: Segment A directly fixes the core anchor/surface-form problem by explicitly mapping the nickname 'The King of Cool' to Steve McQueen and prescribing conjunctive queries to target that entity; B mainly refines source selection and phrasing (authoritative filters) without changing the main retrieval anchor.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: noisy_entity
- confidence: 0.88
- why: Segment A explicitly redirects the generator to an authoritative credit-confirmation strategy (prioritizing obituaries, biographies, film-credit DBs and Hall-of-Fame entries) and instructs avoiding noisy fan/forum pages — a substantive change to the candidate set and noise filter rather than a mere wording or extraction refinement present in B.

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
- why: Segment B enforces a substantive change in query behavior: require authoritative, primary-credit checks (exact-phrase + site filters) and an explicit follow-up to resolve whether Ekins doubled McQueen in Bullitt. A only narrows to confirming The Great Escape and defers the Bullitt ambiguity, so B corrects the core retrieval/role-ambiguity more fundamentally.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: B fixes a core retrieval omission by adding the missing candidate/anchor (explicitly checking whether Ekins doubled McQueen in Bullitt), whereas A mainly refines source selection and query phrasing without changing the main retrieval target set.

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
- confidence: 0.86
- why: Segment A corrects the core retrieval failure by anchoring the query on the correct band (Annihilator) and instructing retrieval of the band's 11th studio album and its release date—changing the primary target and retrieval goal. Segment B only splits the task into an intermediate step (confirming the 11th-album title) and defers the main evidence extraction, which is a smaller, procedural refinement.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A redirects the retrieval strategy to first fix the primary missing anchor (which album is Annihilator's 11th) and explicitly changes the query shape (use discography/ordinal confirmation, exclude EPs, defer release-date lookup). That corrects the main retrieval failure rather than merely refining search phrasing.

## 180__split1__seg1

- idx: 180
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.85
- why: Segment A adds a core anchor-correction: explicitly resolving whether 'highest-selling heavy metal group from Canada' refers to Annihilator and requires confirming the band's identity before counting albums. This changes the query-generator's behavior (add a verification step and alter query shape) rather than merely refining extraction of a known album/date.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.9
- why: Segment A explicitly corrects the main anchor — it mandates confirming that 'highest-selling heavy metal group from Canada' refers to Annihilator (and seeks the 11th album title/year). B only focuses on identifying the 11th album given Annihilator, a narrower refinement. Verifying the correct band is a broader, higher-impact correction to the query generator.

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
- confidence: 0.85
- why: Segment A fixes the main retrieval failure by establishing the correct band anchor (likely Annihilator) and identifying which album is the 11th — a fundamental change to what the second-hop query must target. Segment B only refines evidence collection (gathering candidate release-date sources) after the album is already known, so it is a smaller, follow-up correction.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.79
- why: Segment A changes the generator’s retrieval behavior more fundamentally: it redirects queries to a different evidence family and collection strategy (album page infobox, label/press release, Discogs/AllMusic/MusicBrainz) to assemble competing release-date candidates and provenance. B only narrows/validates the anchor (confirm band identity and the 11th-album title/year), which is a smaller, preparatory correction.

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
- confidence: 0.85
- why: Segment A enforces a step-change in retrieval strategy: it corrects the primary missing anchor by forcing actor->character confirmation first (filmography/cast evidence) and deliberately defers publisher lookup, removing distracting comic-pages and guiding narrow actor+role queries. This is a more fundamental correction than B, which only requests short entity-to-entity matches without changing the retrieval order or removing the key distraction.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment A changes the retrieval strategy/order: it instructs the generator to first confirm the actor->character anchor (Evan Peters→Quicksilver) and explicitly defer publisher/comic-book pages. That is a substantive shift in query shape and target selection versus B, which only narrows an already mixed actor+character+publisher query.

## 227__split1__seg1

- idx: 227
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A corrects the primary missing anchor by directing the agent to confirm the actor->character link (Evan Peters → Quicksilver) — a fundamental retrieval failure — whereas B only refines which character/comics pages to hit for publisher confirmation after the character is known.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: Segment A changes the core retrieval target and candidate set—it redirects the generator from actor/filmography sources to the character/comics entry and infobox (explicitly avoiding actor pages) to get the publisher. This corrects the main anchor and evidence family rather than merely refining an actor→character confirmation.

## 227__split2__seg1

- idx: 227
- split_iter: 2
- num_edges_before_split: 3
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.87
- why: A fixes the primary missing anchor by forcing confirmation of the actor->character mapping (Evan Peters → Quicksilver/Pietro Maximoff), which changes the core query target and retrieval behavior; B only refines the subsequent publisher lookup once the character is already assumed.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.85
- why: Segment A enforces resolving the core anchor ambiguity by mapping the onscreen role to the canonical comic identity (Pietro Maximoff/Quicksilver), removing alternate 'Quicksilver' senses and changing the query generator to target the correct character identity before fetching publisher info. B only narrows to actor-filmography confirmation (a smaller, actor-centric refinement).

## 247__split0__seg0

- idx: 247
- split_iter: 0
- num_edges_before_split: 1
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.78
- why: Both A and B address the same core failure: they shift the retrieval target from generic detainee/timeline pages to contemporary news and social‑media coverage and instruct the generator to look for campaign names/hashtags. Neither one corrects a different main anchor or bridge relation; B mainly adds query-shape refinements (wildcards, ORs) rather than a fundamentally larger correction, so the magnitude of feedback is essentially the same.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.84
- why: Both segments target the same missing information (a named online campaign/hashtag) and differ only in query-shaping details (A already includes explicit hashtag/online campaign terms; B emphasizes news/social-media scope and wildcard/OR query patterns). Neither corrects a core anchor or bridge relation, so their feedback magnitudes are equivalent.

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
- why: Segment A redirects retrieval to a different candidate set (Ghana-focused news outlets and local activist social pages, plus petition platforms) — a substantive change to the anchor/sources the query must target. B mainly refines query shape (wildcarded hashtags, actor+medium combination) to extract the campaign label once the correct source family is already known.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.84
- why: Segment B moves from a generic base query to an explicitly narrowed query shape that must find quoted campaign identifiers (hashtags/e‑petitions) in local coverage — a fundamental change in what to search for. A is already constrained to Ghanaian outlets and activist pages and mostly refines where to look, so its feedback is smaller.

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
- confidence: 0.79
- why: Segment B makes a more substantive retrieval correction: it changes the candidate set and query shape by explicitly targeting specific high-yield sites (GhanaWeb, JoyOnline, Change.org) and instructing site-constrained searches and petition-platform inspection, rather than the broader, less prescriptive Ghana-focused/news-and-social approach in A. This shifts the generator's behavior more fundamentally toward the likely evidence family.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A corrects the main retrieval failure by shifting anchors and the candidate set away from general Gitmo/detainee pages to Ghana-focused news and activist social media and by adding campaign-specific tokens (hashtag/petition). B is primarily a narrower site-level refinement of that same idea.

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
- dominant_gap_type: bridge_relation
- confidence: 0.82
- why: Segment A changes the retrieval strategy and candidate set: it flips the bridge from game-centric pages to a designer-centric authoritative filmography/credits source, correcting the core retrieval target and where to look for evidence. Segment B merely narrows query phrasing to retrieve the same game-credit evidence (a smaller, shape-level refinement).

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.88
- why: Segment A redirects retrieval from game-centric credit checks to a designer-centric strategy (seek Kunihiko Tanaka filmography/credits first). That corrects the primary anchor/target of the query generator and changes the query shape fundamentally, rather than merely refining a game-credits query as in B.

## 262__split1__seg0

- idx: 262
- split_iter: 1
- num_edges_before_split: 2
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Segment A changes the retrieval strategy from a designer-centric noisy query to a game-centric, authoritative target (Xenoblade Chronicles X credits). This is a substantive bridge/target shift (changes the evidence family and query shape) rather than the narrower refinement in B, which simply tightens designer-filmography queries.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.75
- why: Both transitions make the same substantial correction: they shift the retrieval target from the game's credits to a designer-centric (Kunihiko Tanaka) filmography/credits page. This changes the primary anchor/candidate set the query must hit rather than only refining snippet or field-level details.

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
- dominant_gap_type: anchor
- confidence: 0.83
- why: Segment B explicitly shifts the retrieval anchor and query shape away from a long, name-heavy/episode-centric query toward show-level sources and the two primary creators (Alfred Gough, Miles Millar), a broader corrective change to what the query generator should target rather than a minor refinement.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.88
- why: Both A and B correct the same primary failure: the long, name- and episode-heavy query shape that pulls person/episode pages instead of concise show-level sources. Each transition directs the generator to target the Smallville main article, the episode list, and the two creator bios (Alfred Gough and Miles Millar), so they imply materially similar prompt-feedback changes.

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
- confidence: 0.78
- why: Both transitions propose the same corrective change: collapse the long, name-heavy query into a concise show-focused query that anchors on Smallville and the two primary creators (Alfred Gough and Miles Millar), removing peripheral episode/person noise. The semantic correction magnitude is effectively identical.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: B corrects the core failure: it replaces a long, name-heavy query that returns episode/person pages with a concise show-plus-creators query, changing the retrieval target and overall query shape. A describes a narrower refinement from an already reduced state and is a smaller, follow-up tweak.

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
- confidence: 0.72
- why: Both segments make the same substantive correction: they remove noisy person/episode terms and reshape the query to target show-level pages and the two primary creators (Alfred Gough, Miles Millar). Neither changes the anchor set or bridge relation more fundamentally than the other—differences are only in wording/extra emphasis (A keeps the actor bridge explicit).

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.69
- why: Segment A describes a bigger corrective shift from a long, name- and episode-heavy query to a concise show-plus-creator query, removing major noisy targets and changing the query shape to surface series-level credits. B is essentially the same refinement but starts already partially narrowed, so it is a smaller/local update.
