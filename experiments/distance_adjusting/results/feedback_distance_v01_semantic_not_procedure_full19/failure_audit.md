# Failure audit

- failed triples shown: 30

## 108__split0__seg0__feedback

- idx: 108
- split_iter: 0
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.92
- why: Segment A makes a bigger semantic shift: it replaces the ambiguous 'Solo' anchor with the explicit title 'Solo (Australian soft drink)' and additionally introduces a comparative anchor ('La Croix United States') to bias retrieval toward explicit cross‑country production statements. This changes the central entity sense and the intended relation (direct country comparison) rather than only refining manufacturer or query wording.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Both feedback segments request the same core semantic change: disambiguate "Solo" to the Australian lemon-flavoured soft drink and prioritize lead/infobox or manufacturer statements that assert country of origin (Australia) so it can be compared with La Croix (United States). Neither feedback shifts to a different entity sense, evidence family, or answer type—both change the same anchors, avoid the same distractor families, and specify the same bridge relation (country-of-origin).

## 108__split1__seg1__feedback

- idx: 108
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.78
- why: Both segments make the same core semantic change: disambiguate “Solo” to the Australian lemon-flavoured soft drink and target explicit country-of-origin evidence (infobox/lead and manufacturer lines). Neither changes the central anchor, bridge relation, candidate set family, or answer type in a materially different way—differences are mainly procedural (disambiguation vs extraction emphasis) and token phrasing.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.84
- why: Both feedbacks make the same core semantic change: disambiguate 'Solo' to the Australian soft‑drink sense and target lead/infobox evidence stating country of origin (Australia), while avoiding similarly named non‑Australian brands. Differences are mainly procedural (query phrasing, source preferences, extra tokens) rather than a change in anchor, relation, evidence family, or candidate set.

## 108__split3__seg3__feedback

- idx: 108
- split_iter: 3
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A makes a substantive semantic shift by changing the retrieval anchors and candidate set: it explicitly targets the 'Solo (Australian soft drink)' sense, adds country/manufacturer tokens (Australia, Schweppes Australia, Asahi, Coca‑Cola Amatil), and tells the system to avoid other 'Solo' senses (e.g., Norwegian) — i.e., it re-centers the entity sense and disambiguation goal. Segment B is a narrower extraction refinement once that sense is found.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.68
- why: Both feedbacks request the same semantic change: disambiguate to the Solo (Australian soft drink) sense and steer retrieval toward a short lead/infobox snippet stating country of origin (Australia), while avoiding similarly‑named or broad manufacturer pages. Neither adds a materially different anchor, relation, answer type, or candidate set — they differ only in procedural/phrasing details.

## 118__split1__seg1__feedback

- idx: 118
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.91
- why: Segment B makes a stronger semantic shift: it fixes the candidate anchors to specific title-year pairs (e.g., Third Person (2013) and From Here to Eternity (1953)) and narrows the answer target to top-billed female performers only, changing both which works are considered and the answer type. Segment A mainly refines retrieval procedures while keeping a broader candidate set and checking multiple versions.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.91
- why: Segment B changes the semantic retrieval target: it expands the candidate set from only top‑billed/lead actresses to the full credited cast (supporting actors included), adds alternate-version disambiguation and named actor anchors, and thus alters which performers count as potential overlaps. This is a broader semantic shift than A, which mainly constrains to exact title+year lookups and top‑billed names.

## 118__split2__seg1__feedback

- idx: 118
- split_iter: 2
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.86
- why: Segment B changes the semantic target set: it expands disambiguation to multiple prominent candidates (keeps Third Person candidates rather than locking to a single year) and explicitly adds both the 1953 film and the 1979 miniseries of From Here to Eternity, plus type (film vs. miniseries) and director aliases. This alters the candidate set and anchor choices rather than only refining extraction constraints.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.89
- why: Both segments make the same major semantic change: they re-anchor ambiguous titles to the same canonical film editions (Third Person → 2013, From Here to Eternity → 1953), narrow candidate sets to top-billed female cast, and shift retrieval toward 'Starring'/'Cast' sections while avoiding non-film senses. The requested semantic targets, evidence family, and candidate-shaping are essentially identical.

## 118__split3__seg2__feedback

- idx: 118
- split_iter: 3
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.78
- why: Segment A issues a firmer semantic re-anchoring: it locks both titles to specific canonical film editions (Third Person → 2013, From Here to Eternity → 1953) and narrows the candidate set to only film-labeled pages, changing the core entity senses and retrieval targets more decisively than B, which retains fallback paths and a broader disambiguation pipeline.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.89
- why: Both segments enact the same substantial semantic change: they lock the two ambiguous titles to specific canonical film editions (Third Person → 2013; From Here to Eternity → 1953) and shift retrieval to top-billed female cast ('Starring'/'Cast') extraction. Their effects on anchors, evidence family, and candidate sets are functionally equivalent; differences are procedural/detail-level only.

## 132__split0__seg0__feedback

- idx: 132
- split_iter: 0
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.88
- why: Both segments request the same core semantic change: move retrieval from broad Björk/ Vespertine results to pages that explicitly tie Björk to the Selmasongs/Dancer in the Dark soundtrack and list occupation labels. They keep the same anchors and avoid the same noisy families; differences are procedural/source-level (BM25 phrasings vs. explicit source lists) rather than a change in entity sense, bridge relation, or target evidence family.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.73
- why: Both updates make the same core semantic change: shift retrieval from general Björk/Vespertine material to explicit soundtrack/album-credit evidence for Selmasongs and to surface Björk’s occupation labels. Neither changes the central entity or target relation differently — they differ only in procedural/detail emphasis.

## 132__split1__seg1__feedback

- idx: 132
- split_iter: 1
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: evidence_family
- confidence: 0.79
- why: Segment A makes a broader semantic shift: it explicitly directs retrieval to film→soundtrack→album-credit evidence (authoritative album pages/liner notes), adds the artist's full legal alias and occupation keywords to ensure the returned entity is the Icelandic singer/songwriter/actress/record producer/DJ, and injects exact-title, label and date anchors. Those changes alter the semantic target and evidence family more strongly than B's narrower release-level credit refinement.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.86
- why: Segment B changes the semantic retrieval target from album/release-level evidence to authoritative artist-biography/infobox evidence that explicitly ties the soundtrack credit to the person and lists occupations. That shifts the evidence family and the answer-type focus (occupation list), not just query phrasing or more exact titles.

## 132__split3__seg0__feedback

- idx: 132
- split_iter: 3
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.76
- why: Segment B shifts the semantic retrieval target to two distinct evidence families (film-credit pages + encyclopedic lead paragraphs) and introduces an explicit occupation-extraction goal (one-line bio/lead), changing both which documents are sought and the answer-type signal. A is a narrower redirection to album/soundtrack-level pages and credit lines, whereas B re-centers retrieval on film credits plus the artist lead, a broader semantic change.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: evidence_family
- confidence: 0.87
- why: Segment A makes a broader semantic shift from general biographical/film retrieval to explicitly targeting album/soundtrack-level evidence and authoritative music-database pages, changing the evidence family and candidate set to album credit pages. B is a narrower, conditional refinement when film-centered retrieval fails.

## 140__split0__seg0__feedback

- idx: 140
- split_iter: 0
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: mixed
- confidence: 0.86
- why: Segment B imposes a stronger, conjunctive semantic constraint on candidate selection (require both the WPT-win relation and the 'four WSOP bracelets' attribute together) and shifts retrieval toward person-centric authoritative biography evidence (adding aliases and explicit date anchors). That changes the candidate set and evidence family more substantially than A, which primarily prescribes a verification-first flow focused on the single initial anchor (George Danzer) with a conditional pivot.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.84
- why: Both segments request the same core semantic change: identify the World Poker Tour champion who also has four WSOP bracelets and extract that person’s birth date by linking WPT winners lists to authoritative biographical pages. They differ only in procedural phrasing and minor signal additions (A adds a tie-break scan behavior; B adds explicit date tokens), but neither introduces a materially different semantic target, bridge relation, or candidate family.

## 140__split1__seg1__feedback

- idx: 140
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.86
- why: Segment B changes the retrieval target from a single-name verification to a systematic cross-reference of the entire WPT champions set and their WSOP bracelet counts, widening the candidate set and altering the bridge relation (list->bio filtering). Segment A is mainly a refinement (add birth-date extraction, authoritative anchors) around the same entity-focused check.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.88
- why: Segment A makes a substantive semantic pivot by introducing a specific primary anchor ("George Danzer") and changing the retrieval goal to first confirm Danzer's WPT status or else search the WPT champions list for any name with exactly four WSOP bracelets. That shifts the central entity anchor and the candidate-selection logic, whereas B mainly refines second-hop query templates, ranking cues, and source preferences without changing the semantic target or candidate centering.

## 140__split3__seg2__feedback

- idx: 140
- split_iter: 3
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.88
- why: Segment B expands the semantic target beyond just identifying WPT winners with four WSOP bracelets: it requires canonical player records, normalized aliases, and explicitly pulls birth-date lines (answer-type) into the same step. That changes the evidence family and the final answer type the pipeline must return, whereas A only narrows candidates by bracelet count and explicitly avoids birth dates.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.79
- why: Segment A imposes stricter, new semantic constraints on which candidates count: it requires explicit numeric "4" pattern matches (with specific token variants), prefers structured infobox/lead/WSOP sources, forbids inferring counts from event lists, labels non-explicit matches as "no-explicit-4", and restores capturing the matched token span for the next hop. Those changes alter the evidence family and candidate-selection semantics more strongly than B's broader cross-check instruction.

## 149__split1__seg0__feedback

- idx: 149
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.82
- why: Segment A changes the core semantic target: it redirects retrieval away from comparative/modern identity pages toward philological/Old Norse etymology evidence and explicitly removes Holda/Frau Holle pages. That alters both the anchor sense (prioritizing Huld/huldr as a name‑root and Huld as a völva) and the evidence family (scholarly etymology sources) — a broader semantic shift than B, which mainly refines query shape to require explicit definitional clauses while keeping the same anchors including Holda.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.78
- why: Segment A introduces a stronger semantic redirection: it enforces a pairwise etymology chain (hulder → Huld → Holda) and requires explicit identity phrasing (e.g. "is originally the same being as") and canonical name‑variants to occur together. That changes the core bridge relation and candidate focus (which entity senses and identity claims count) rather than primarily adjusting source style or precision.

## 149__split2__seg1__feedback

- idx: 149
- split_iter: 2
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.88
- why: Segment B shifts the semantic target from simply locating a name‑derivation/identity line to a different kind of relation: comparative cognacy and archetypal/role equivalence across Germanic traditions (Huld ↔ Holda/Frau Holle), and it broadens the candidate set to onomastic, medieval primary, and comparative‑mythology sources. A mainly narrows evidence style toward short definitional/etymological lines without changing the underlying semantic relation.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.88
- why: Both feedback segments make the same substantive semantic shift: move retrieval from general name‑origin / comparative parallels to concise identity/etymology claims linking hulder → Huld → Holda/Frau Holle, and both add the same core anchors and avoid the same noise. Differences are mostly procedural refinements (date cues, exact‑phrase emphasis, query templates), not a change in the semantic target.

## 149__split3__seg2__feedback

- idx: 149
- split_iter: 3
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.83
- why: Segment A shifts the core semantic target from broad comparative parallels to an explicit identity/equation claim (hulder → Huld → Holda), changing the bridge relation and the evidence family sought (short authoritative etymology/definition lines asserting identity). This is a stronger semantic redirection than B's emphasis on comparative motifs and mid‑tier attestations.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.82
- why: Both segments enact the same semantic shift: they keep the same anchors (hulder, Huld, Holda/Frau Holle and aliases) and change the retrieval target from broad comparative/motif material to concise identity/etymology evidence (encyclopedia/etymological lemma, saga excerpts). Differences are mainly in phrasing and added query templates/details, not in a materially different semantic target.

## 150__split0__seg0__feedback

- idx: 150
- split_iter: 0
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: surface_form
- confidence: 0.85
- why: B introduces new canonical and alias anchors (e.g., 'Paul Winters (American football)', Wayne State University variants, 'formerly Wayne State Tartars') and expands the target candidate types (season page, coach biography, university page), shifting the semantic retrieval target and disambiguation strategy beyond the narrower exact-phrase focus in A.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.78
- why: Both segments target the same semantic correction: narrow retrieval to explicit institutional-affiliation signals linking the 2012 team and Paul Winters to Wayne State University. They keep the same anchors, add the same role+institution phrase cues and date/type tokens, and remove the same families of distracting pages. Differences are mainly procedural emphasis (A lists more exact-match alias cues and canonicalization; B emphasizes prioritizing lead-sentence affiliation lines), not a change in the semantic target or candidate set.

## 150__split1__seg0__feedback

- idx: 150
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.86
- why: Segment A makes a stronger, more specific semantic shift: it narrows the evidence family to page lead-lines and enforces title-exact, role-centered hits while excluding venue/conference and historical-name confounds. This changes which snippets and candidate pages are targeted (lead-paragraph season page + coach bio) rather than only tuning token boosts as in B.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.89
- why: Both segments request the same semantic redirection: concentrate retrieval on short, exact on-page affiliation phrasing that links the 2012 season page and Paul Winters to Wayne State University, using identical anchors, exact-phrase cues, and the same families of terms to avoid (other years, conference/program noise). Neither changes the central entity sense, bridge relation, or candidate set in a materially different way.

## 150__split2__seg2__feedback

- idx: 150
- split_iter: 2
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: candidate_set
- confidence: 0.86
- why: Segment B makes a broader semantic shift: it re-centers retrieval explicitly toward Wayne State University by boosting canonical institution variants, adding cross-phrase co-occurrence anchors, and expanding the candidate set (season page, coach bio, plus the program/university athletics page). Segment A narrows behavior to ordered title-lookups (a useful but more focused change), while B changes the center and breadth of targets and alias handling.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.78
- why: Both segments request essentially the same semantic change: tighten retrieval to the same canonical anchors (2012 season page, Paul Winters coach bio, Wayne State University), boost exact-title/phrase matches and institution co-occurrence, and avoid the same families of noise (other seasons, stadium/conference, tenure counts). Neither introduces a materially different central entity, bridge relation, or answer type — their differences are procedural/detail-level (ordering, phrasing, token counts) rather than a change in semantic target.

## 150__split3__seg0__feedback

- idx: 150
- split_iter: 3
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.9
- why: Both feedback segments make the same core semantic change: focus retrieval on the 2012 season page lead/first paragraph and the Paul Winters coach/bio page to surface the institutional affiliation (team → Wayne State University and Winters as head coach). They keep the same anchors, bridge relation, evidence family, and distractor families to avoid, so neither represents a larger semantic update.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.81
- why: Both segments make essentially the same semantic update: shift retrieval to two canonical targets (the 2012 season lead and a Paul Winters coach/bio/program page), prioritize lead/first-sentence affiliation lines and exact-title/name matches, and avoid venue/conference/other-season noise. Neither introduces a materially different anchor, bridge relation, evidence family, or candidate set beyond that shared change.

## 169__split2__seg1__feedback

- idx: 169
- split_iter: 2
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: evidence_family
- confidence: 0.84
- why: Segment A shifts the semantic target from broad secondary corroboration to authoritative credit-checks (explicitly adding IMDb/BFI/NYT/THR/Stuntmen's Hall of Fame filters) and explicitly resolves the Bullitt ambiguity — changing the evidence family and candidate set rather than just adding lightweight probes.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.78
- why: Both segments make the same substantive semantic changes: they shift retrieval from general corroboration to authoritative, phrase-level credit confirmation and both add the 'Bullitt' anchor to resolve ambiguity. Differences are mainly procedural/detail-level (ordering and phrasing), so their semantic update magnitude is effectively equal.

## 169__split3__seg2__feedback

- idx: 169
- split_iter: 3
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.79
- why: Both segments request essentially the same semantic shift: move from exploratory mentions to authoritative, explicit-credit confirmation that Bud Ekins was Steve McQueen’s stunt double for The Great Escape, while treating Bullitt only as a secondary credit-resolution check. Differences are procedural (ordering, specific site lists, minor scope tweaks) rather than changes to the semantic target, bridge relation, or evidence family.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.84
- why: Both segments make the same core semantic shift: move retrieval from broad/exploratory signals to authoritative credit-confirmation that Bud Ekins was Steve McQueen’s stunt double (targeting obituaries, Hall-of-Fame entries, IMDb/BFI/TCM, and explicit "stunt double" phrasing) and to resolve the Bullitt ambiguity. Neither changes the central anchors, the answer type, or the candidate entity family in a materially different way; differences are mainly procedural/query-template detail rather than a distinct semantic target.

## 180__split0__seg0__feedback

- idx: 180
- split_iter: 0
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: candidate_set
- confidence: 0.83
- why: A expands the semantic target beyond ordinal confirmation to include explicit album-title aliases, authoritative source cues, and a direct shift to album-page release-date extraction. It changes which documents and evidence fields must be retrieved (adds new anchors/candidate titles and a different evidence family) rather than merely refining ordinal identification as B does.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.78
- why: Both segments request the same semantic change: confirm the band (Annihilator) and move from identifying the 11th studio-album title to retrieving that album's official release date. Neither changes the central entity, bridge relation, evidence family, or candidate set in a materially different way—both preserve a two-step (discography → album page/date) retrieval target and avoid the same distractors—so their semantic updates are effectively equivalent.

## 180__split2__seg2__feedback

- idx: 180
- split_iter: 2
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.83
- why: Segment B shifts the retrieval goal from simply extracting a single authoritative release date to assembling a structured set of date candidates with region qualifiers, provenance, and distinction between original vs reissue. That expands the candidate set and evidence families to consult (Discogs, MusicBrainz, regional press, multiple release entries) and changes the semantic target of the hop; A mainly narrows/specializes extraction to a single original-market date.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.89
- why: A introduces a new central-entity identification step (confirming the band as Annihilator), adds an ordinal-discography mapping to select the 11th studio album, and shifts the retrieval pipeline to a broader identification→verification→evidence-assembly flow (including alias normalization and multi-database checks). B only refines extraction of the precise release date for an already-confirmed album. A therefore changes the semantic target and candidate set, not just the extraction detail.

## 180__split3__seg2__feedback

- idx: 180
- split_iter: 3
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: evidence_family
- confidence: 0.88
- why: Segment A shifts the semantic target from identity/metadata collection to assembling concrete date candidates and their provenance (infobox 'Released' field, press releases, DB release entries, region variants and original vs reissue tagging). B stays focused on canonical identifiers (title, label, catalog IDs) and deliberately avoids extracting dates — a narrower semantic change.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.87
- why: Both updates shift retrieval from identity to assembling release-date evidence, but A mandates a broader, deeper semantic change: it expands the evidence family to include catalog/release-entry linkage, regioned edition distinctions, and explicit date-string provenance (paragraph/infobox context) plus search templates and noise suppression — materially enlarging the candidate set and evidence types to be considered.

## 227__split0__seg0__feedback

- idx: 227
- split_iter: 0
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.87
- why: Segment B expands the semantic target beyond just confirming an actor→character cast credit (as A does) to also include the character→publisher link (adds 'Marvel Comics' as a retrieval anchor). That adds an additional bridge relation and evidence family to resolve in this hop, a larger semantic change than A's narrower focus on cast-credit lines and avoidance of publisher pages.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.78
- why: Segment A makes a bigger semantic shift: it introduces explicit new entity anchors (Quicksilver/Pietro Maximoff and comics article titles), and it changes the candidate set by removing a prior prohibition on publisher pages so the second hop can target canonical comic-article leads and cross-source matches. This alters which entities and sources are retrieved, not just query wording.

## 227__split2__seg1__feedback

- idx: 227
- split_iter: 2
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.87
- why: Segment B pivots the retrieval goal from confirming an actor→character link to verifying the character→publisher provenance, changing the target relation and evidence family (film/actor sources → comics/character/publisher sources). This is a broader semantic shift than A, which only adds alias anchors to strengthen the actor→character mapping.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.87
- why: Both segments request the same semantic pivot: after confirming Evan Peters → Quicksilver, shift retrieval from actor/film sources to authoritative comics/character sources by adding character anchors (e.g., Quicksilver (Pietro Maximoff), publisher, infobox) and avoiding actor/adaptation noise. They make equivalent changes to anchors, bridge relation (character→publisher), and evidence family; neither introduces a different entity sense, relation, or candidate set.

## 227__split3__seg2__feedback

- idx: 227
- split_iter: 3
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.85
- why: Segment A makes a more fundamental semantic shift by changing the central anchors from actor-centric pages to the comics character and publisher (explicitly prioritizing 'Quicksilver (comics)', 'Pietro Maximoff', 'Marvel Comics', infobox/lead lines). This redirects the query target itself (entity sense and evidence family) away from film/actor sources toward canonical comic‑book provenance, whereas B mainly refines actor→character evidence by adding comic‑context tokens (teams/series) without as strongly re-anchoring the search to the character/publisher page type.

### right

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.85
- why: Both segments make the same substantive semantic change: pivot retrieval from actor-centered pages to character/comics-centered pages to surface explicit publisher evidence (Quicksilver/Pietro Maximoff → Marvel Comics). Differences are mainly procedural detail and minor cue refinements, not a larger semantic shift.

## 247__split0__seg0__feedback

- idx: 247
- split_iter: 0
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.89
- why: Both segments make the same core semantic shift: keep the same actor/event anchors (OccupyGhana/NPP, Ghana, Guantanamo, Jan 2016) but change the evidence family and query target from roster/timeline/detainee-biography pages to news and social‑media passages that explicitly quote a campaign name/hashtag or petition title. Neither segment changes the central entity anchors or the ultimate answer type; they differ only in minor phrasing and retrieval-weighting details.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: evidence_family
- confidence: 0.86
- why: Segment A makes a broader semantic shift: it redirects retrieval away from roster/timeline/detainee-biography pages toward news and social‑media excerpts that quote campaign names, adds new medium/name tokens and alias/date variants, and removes entire noisy entity families. B is a narrower refinement that focuses on matching short quoted labels within that narrowed space.

## 247__split1__seg0__feedback

- idx: 247
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.95
- why: Segment A shifts the semantic retrieval target from general/global Gitmo coverage toward a distinct candidate set — local Ghana outlets and activist social-posts/accounts — and explicitly changes the evidence family (petition/hashtag embeds, account posts). That alters which documents and entity mentions are considered, a bigger semantic change than B's stronger query/shaping refinements.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.79
- why: Segment A imposes a stronger semantic shift: it narrows the candidate set to Ghana‑focused outlets and activist/NPP social pages and explicitly changes the evidence family to embedded social tokens (hashtags, Change.org/Facebook/Twitter URLs and quoted petition titles), whereas B mainly boosts social/campaign signals but keeps a broader source space. A therefore changes the search's semantic center and target evidence more dramatically.

## 247__split3__seg0__feedback

- idx: 247
- split_iter: 3
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: A
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.86
- why: Both segments make the same core semantic shift: move retrieval away from generic Gitmo/detainee lists toward evidence that names an online campaign/hashtag (local coverage, petitions, embedded social posts). They differ only in surface targeting (A emphasizes direct platform/petition sites; B emphasizes specific local news outlets and in-paragraph co-occurrence) but do not change the central entity, relation, or answer type.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: evidence_family
- confidence: 0.82
- why: Segment B makes a broader, earlier semantic change to retrieval: it shifts the search target from generic Ghana/Gitmo coverage to include petition platforms and OccupyGhana social handles via explicit site: filters and phrasing that prioritize primary campaign evidence (petition titles, hashtags, embedded tweets). A is a more specific refinement (open linked petitions/social posts) within that same target.
