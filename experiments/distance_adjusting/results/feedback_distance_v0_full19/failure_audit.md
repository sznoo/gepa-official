# Failure audit

- failed triples shown: 30

## 108__split1__seg1__feedback

- idx: 108
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.72
- why: Segment B changes the retrieval orientation (disambiguation -> focused extraction) and adds explicit infobox/lead extraction cues and manufacturer-location evidence, which meaningfully shifts query-shape and evidence targets beyond mere title-disambiguation in A.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: A prescribes a broader, higher‑impact reweighting: it explicitly preserves both entity anchors (Solo and La Croix), adds multiple BM25 alias tokens, emphasizes exact‑title + infobox/lead signals, and gives detailed noise‑removal and query‑shaping instructions—requiring larger changes to which anchors and evidence are prioritized. B is a narrower, primarily Solo‑focused disambiguation and source-preference tweak.

## 108__split2__seg2__feedback

- idx: 108
- split_iter: 2
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why: Segment B prescribes a procedural change to the retrieval strategy (a disambiguation-first, two-step chain: fetch disambiguation → follow confirmed product page → extract lead/infobox). This alters the query-generation control flow and candidate-following order, not just the tokens or anchors to add. A is mainly a focused reweighting/disambiguation of anchors and avoidance tokens, while B changes how results are retrieved and validated.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A specifies a broader, higher‑impact semantic shift: it not only adds precise disambiguation anchors and manufacturer aliases but also introduces source‑preference cues (Wikipedia/official site), explicit negative/avoidance tokens, and stronger removal rules and query‑shape constraints. These additions change which anchors are required, which noisy families are excluded, and how queries are shaped more than B's overlapping but narrower BM25/disambiguation guidance.

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
- confidence: 0.84
- why: Segment A makes broader semantic changes to retrieval: it adds new exact-title and country/type anchors, reweights manufacturer anchors, and explicitly deprioritizes many distractor entity families—altering which candidate entities/documents are considered. Segment B is a narrower extraction-oriented refinement once the Australian 'Solo' variant is already identified.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.72
- why: Segment A instructs a stronger, more specific semantic shift: it not only adds exact-title anchors and manufacturer tokens but enforces an extraction-focused query shape (prefer 1–2 line lead/infobox snippets, explicit local ordering), and more aggressively removes corporate/aggregate pages and noisy same-name senses. Those directives change both which anchors are preserved and how results are scored/trimmed, a larger behavioral change than B's mainly BM25‑disambiguation boosts.

## 118__split0__seg0__feedback

- idx: 118
- split_iter: 0
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.93
- why: Segment A requires a structural change to query-generation: add an explicit disambiguation-first pass (enumerate Third Person candidates + years/synopses) then a dedicated cast-extraction pass producing version-tagged top-billed actress lists. This reorders and broadens the retrieval workflow and candidate set selection. Segment B mainly adds tighter surface anchors (years, named actors) and cross-check queries, which is a narrower, targeted refinement.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: bridge_relation
- confidence: 0.82
- why: B introduces broader semantic changes: it adds explicit actor-name anchors (e.g., Deborah Kerr, Donna Reed), prescribes an extra cross-check bridge (query actor filmographies / 'appeared in'), and defines a three-query workflow (two exact-title queries plus actor-filmography verification). A focuses more narrowly on precise title+year cast lookups and output normalization. B therefore changes both what anchors are injected and the bridging strategy between candidate lists, a larger shift in query-generation behavior.

## 118__split1__seg1__feedback

- idx: 118
- split_iter: 1
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Segment A prescribes a broader, higher-impact change: it preserves disambiguation ordering and multiple title-year anchors, mandates per-version cast lookups, name normalization, and templates for post-processing intersections — a multi-pronged semantic re-centering of retrieval. B mainly narrows to particular title-year anchors and female top-billed extraction (a more localized restriction).

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.85
- why: Segment B requires a bigger change: it broadens the candidate set from only top‑billed actresses to full credited casts, adds explicit actor anchor tokens (e.g., Deborah Kerr, Donna Reed) to bias retrieval, and changes the query shape to a two‑step confirm+fetch pattern. Those changes alter which entities are preserved/added and materially expand retrieval scope compared with A’s mainly versioned, top‑billing-focused cast lookups.

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
- confidence: 0.87
- why: Segment B requires broader semantic changes: it expands candidate sets to include multiple versions (1953 and 1979), adds an explicit disambiguation phase, differentiates film vs. TV/miniseries, and adds director/year alias weighting and billing tags — all of which change which titles are retrieved and how results are labeled. Segment A is a tighter narrowing to two exact anchors and simpler extraction rules.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Both segments give effectively the same semantic update: lock ambiguous titles to specific film editions (Third Person→2013, From Here to Eternity→1953), bias queries to exact-title+year anchors, target 'Starring'/'Cast' sections, extract top-billed female names (2–4), and avoid non-film or broad disambiguation noise. Differences are minor (provenance/formatting notes and wording), so neither represents a materially larger semantic change.

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
- dominant_gap_type: query_shape
- confidence: 0.68
- why: B changes the retrieval pipeline shape and candidate set: it shifts from a single-name check to a systematic, ordered two-step scan of authoritative WPT champions lists plus iterative filtering of each candidate’s bio by exact bracelet-count phrases. This re-centers retrieval (list-first, then per-name filtering) and adds new BM25 anchors and candidate seeds, a broader structural change than A’s targeted birth-date extraction and tie-break refinements.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.91
- why: Segment A prescribes a broader, higher-impact reorientation: it adds new authoritative anchors (wpt.com, champions list, player bios), a tie-break bridge behavior, explicit extraction cues for birth dates, and stronger avoid/retain rules—changing which entities and sources the generator must prioritize and how it falls back. Segment B mainly refines second-hop query templates and ranking cues, a narrower verification step.

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
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment B requires a broader and deeper per-player retrieval: it adds canonical page/URL and normalized aliases, demands explicit birth-date lines as well as bracelet counts, and changes the output into a structured mapping per winner. This is a larger semantic shift than A, which only adds a check for a '4 bracelet' snippet while forbidding birthdate retrieval.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.82
- why: Segment A imposes more and narrower semantic constraints: it requires explicit token-pattern matching for the numeric '4' (BM25-friendly forms), enforces using structured infobox/lead fields, instructs capturing the exact matched token span to bridge to the next hop, and mandates labeling non-explicit candidates — all of which change retrieval/query-shaping and bridging behavior more than B's broader cross-check instruction.

## 149__split2__seg1__feedback

- idx: 149
- split_iter: 2
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.82
- why: Segment B introduces multiple new semantic directions — adding cognacy/comparative-mythology relations, medieval/early-modern primary-source cues, and role-comparison signals — which broaden and re-center retrieval toward different evidence families and relation types. This requires a bigger change to query-generation behavior than A's narrower shift toward short definitional lead‑sentences.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A makes a broader semantic shift: it re-centers retrieval from a general name‑origin exploration to prioritizing short, authoritative identity/etymology lines and explicitly adds the Holda/Frau Holle anchors. B is a narrower tightening (token/phrase tuning, date cues, alias expansion) that refines retrieval rather than changing the main anchor set or the high‑level retrieval goal.

## 150__split1__seg0__feedback

- idx: 150
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: Segment A prescribes a more targeted re-centering of retrieval: it enforces title-exact, lead/snippet-priority hits and explicit query shapes (title-targeted and person-role), plus a detailed remove list of confounding pages. Those instructions change query construction and ranking priorities more strongly than B's comparable but broader/token-focused suggestions.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.84
- why: Segment B is a full-edge update from the base retrieval state and prescribes a broader, higher-impact change to seed retrieval: it re-centers queries on exact affiliation phrasing, role+year tokens, and lead/infobox text to correct the initial retrieval distribution. A is a narrower, implementation-level refinement (title/lead boosting, 1–2 phrase clauses) that builds on the same semantic goal. B therefore represents the larger semantic shift.

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
- why: Segment B prescribes a broader, multi-dimensional change to retrieval behavior: boosting exact-phrase anchors and aliases, adding type and date cues, encouraging cross-phrase co-occurrence, promoting canonical institution variants, and expanding the candidate set to 2–3 hits per entity (season page, coach bio, program/athletics page). A is narrower, primarily switching to two ordered title-lookups. B therefore represents a larger semantic update.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.63
- why: Segment A imposes stronger, more specific changes to retrieval behavior: it mandates exact-title disambiguation (e.g., 'Paul Winters (American football)'), an explicit ordered retrieval strategy (season page → coach bio → fallback university page), and tightly constrained short BM25 query shapes. These require more concrete generator changes than B's mainly phrasing/affiliation bias and multi-hit suggestion.

## 169__split0__seg0__feedback

- idx: 169
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
- why: Segment A makes broader semantic changes: it re-centers retrieval around explicit actor/film/role anchors (including alias mapping), adds date and source-type anchoring, expands prioritized role-phrasing and filters, and prescribes a conjunctive query shape—changes that alter which anchors are required and how queries are formed. B is a narrower, procedural two-step narrowing focused on exact-phrase and domain filters.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.84
- why: Segment A introduces a distinct two‑phase retrieval behavior plus explicit BM25 phrase‑weighting and document‑type promotion (authority/source filters, elevation of filmography formatting) that materially change query-generation and ranking behavior beyond the mainly additive, surface‑level constraints in B (dates, synonyms, and similar conjunctive query templates).

## 169__split3__seg2__feedback

- idx: 169
- split_iter: 3
- num_edges_before_split: None
- left_recovery: False
- right_recovery: False

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: Segment A adds more and finer-grained semantic constraints: new exact-phrase patterns, specific site filters (NYT/THR/Guardian), lifespan and alias tokens, plus explicit restore instructions to check filmography pages. These changes alter query construction and retrieval targeting more strongly than B's higher-level prioritization of authoritative sources.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.79
- why: Segment A prescribes more concrete, behavior-changing instructions (explicit query templates, negative/noise operators, a targeted follow-up slot for Bullitt, and a restore of authoritative-credit priority). These add new, specific query-shape and retrieval-prioritization constraints beyond the higher-level guidance in B, so A demands a larger semantic change to the generator.

## 180__split1__seg1__feedback

- idx: 180
- split_iter: 1
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment B extends behavior beyond band/album identification to an immediate, scoped second hop that fetches the album’s full official release date (day/month/year, label/region) and prescribes a two-step query shape and new BM25/date anchors. This is a broader semantic change than A, which only adds band-confirmation and a year-level extraction while explicitly avoiding day/month detail.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.86
- why: Segment A imposes stronger, more specific semantic shifts: move retrieval from band/discography scope to album-level authoritative fields, require extracting a full day/month/year (not just year), prefer original-market first-press dates, and add specific high-authority sources and fallback behavior. These changes alter the target evidence family and the answer granularity much more than B's mainly procedural chaining and token tweaks.

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
- confidence: 0.89
- why: Segment B requires a broader change in retrieval behavior: instead of directly extracting a single canonical date, it instructs assembling a structured candidate set (multiple regioned dates, provenance, DB IDs, reissue tagging) across many evidence families — a more substantial semantic shift than A's focused move to extract a precise album-level release date.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A requires a broader semantic change: it adds band-identity confirmation and discography-ordinal steps, introduces new entity anchors (band page, discography, album aliases, catalogue numbers), expands targeted database checks, and re-centers the retrieval pipeline from album-centric to identification→verification→evidence-assembly. B is narrower—it assumes the band and album are known and only tightens date-extraction steps.

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
- dominant_gap_type: candidate_set
- confidence: 0.87
- why: Segment A expands the retrieval goal from identifying the band/album to actively assembling a structured set of full release-date candidates (day/month/year), region variants, and provenance across authoritative sources — requiring additional queries, new evidence families, and different filtering rules. B only gathers canonical identifiers and stops before day-level date extraction.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.88
- why: Segment A prescribes a more extensive semantic shift: it not only directs collecting date candidates and provenance but adds stricter metadata-linking (catalog numbers, release-entry IDs), explicit capture of every quoted date string, region/edition tying, noise-suppression filters, and concrete BM25 query templates — changing both what is retrieved and how queries are formed.

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
- confidence: 0.9
- why: B expands the retrieval goal beyond just tying Evan Peters to his role — it explicitly preserves the publisher anchor and pushes the generator to surface both actor→character and character→publisher evidence in one step. A narrows the step to only actor→role cast-credit patterns and explicitly avoids publisher pages. That broader change in which relations and anchors to target is a larger semantic update.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.77
- why: Segment A prescribes a more substantial semantic shift: it adds explicit character and publisher anchors (Quicksilver / Pietro Maximoff / Marvel Comics), enforces a two-hop actor→character then character→publisher retrieval flow, introduces cross-source exact-match matching and film-year disambiguation, and explicitly removes the prior prohibition on publisher pages. These changes require re-centering retrieval targets and the overall query workflow more than B's token/verb and preference refinements.

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
- confidence: 0.87
- why: Segment A re-centers retrieval to a different candidate set and evidence family (local Ghana outlets and activist social posts), adds actor-account cues and strict date anchoring, and strongly prioritizes petition/hashtag/link tokens — a broader semantic shift than B's mainly query‑shaping and boosting of social/campaign tokens.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.83
- why: Segment A imposes stronger, more specific semantic constraints: it re-centers retrieval on local Ghana outlets and activist accounts, adds concrete surface-pattern matching (literal '#' tokens, quoted petition titles, Change.org/facebook/twitter URL patterns and site:gh), and prescribes tighter date/alias handling and noise removal — changes that materially alter which anchors and surface forms the query generator must preserve and prioritize.

## 262__split0__seg0__feedback

- idx: 262
- split_iter: 0
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.86
- why: Segment A instructs a broader semantic re-centering of retrieval from game/developer-centric pages to designer-centric candidate sets (filmography/credits/profiles), adds richer disambiguation signals (Japanese script, birth year, alternate name ordering) and enforces co-occurrence of name+per-title credit — a larger change in which anchors and result family to target. Segment B is a tighter, target-specific narrowing (exact-title + credit-source) rather than a re-centering of the candidate set.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.78
- why: Segment B enforces a stricter, end-to-end change in query shape and retrieval targeting (require exact-name + role + full-title conjunctive queries, then append credit-source tokens and optional year/platform), which is a broader semantic re-centering of query generation compared with A's iterative prioritization and host-boosting suggestions.

## 267__split1__seg0__feedback

- idx: 267
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.82
- why: A introduces additional semantic constraints beyond the shared show-level focus: it adds explicit authoritative source cues (Variety, Hollywood Reporter, press releases, IMDb), a canonical-title descriptor, and concrete query connectors/prioritization rules. Those additions change which evidence families and source types to target and add stronger re-centering of the candidate set.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.88
- why: Segment B describes a broader, higher-level shift in retrieval behavior — re-centering queries from long, episode/name-heavy searches to concise, show-level creator/writing-credit sources and prescribing a new query-shape template. Segment A mainly refines and tightens that shift (co-occurrence enforcement, stricter avoidance lists and source preferences), so B represents the larger semantic update.

## 267__split3__seg0__feedback

- idx: 267
- split_iter: 3
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: evidence_family
- confidence: 0.92
- why: Both segments give nearly identical semantic instructions: shift retrieval from episode/person pages to show-level credit sources for Smallville, keep the same anchors (Smallville, Alfred Gough, Miles Millar, Justin Hartley), add similar show-level phrases (created by/writing credits/main article) and avoid episode and individual staff pages. Neither introduces a materially different anchor, relation, or candidate-family change.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.77
- why: Segment A gives a broader, higher-impact semantic reorientation: it restores show-level source focus, explicitly re-centers the two creator anchors (Alfred Gough, Miles Millar), adds many target-type cues (press releases, creator bios, consolidated credits) and specifies a wide set of documents to avoid. This requires larger changes to which anchors and evidence families the generator prioritizes versus the narrower, reiterative token-weighting and query-shape suggestions in B.

## 268__split0__seg0__feedback

- idx: 268
- split_iter: 0
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why: Segment B prescribes a broader, multi-step change to retrieval behavior: it re-centers queries to exact-name aliases for both targets, adds date anchors and candidate occupation types, and prescribes separate entity-centric queries (including a disambiguation check). That is a larger semantic shift than A, which mainly tightens single-entity Henry Green anchors and avoids noisy Henry hits.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.88
- why: A introduces more and deeper semantic changes: explicit alias mapping for Henry Green, many new occupation candidate tokens, additional book-title identity anchors, a negative anchor to filter Joseph Henry Chesterton, and specific lead/infobox-focused query templates — all of which materially change which entities and job-types the generator must preserve/add/remove and how queries are formed.

## 268__split2__seg0__feedback

- idx: 268
- split_iter: 2
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.89
- why: Segment A prescribes a structural change to retrieval (switching from one ambiguous multi-target string to an entity-centered multi-hit shape: disambiguation check + alias/novelist hit + Chesterton anchor) and adds multiple new exact anchors and filtering rules. That alters which candidates are requested and how results are combined, a broader semantic shift than B's narrower focus on exact pen-name mapping and lead-snippet constraints.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.89
- why: Segment A imposes a broader and more prescriptive semantic shift: it mandates a two-step identity-confirmation then one-line occupation capture, adds explicit date-anchor and exact-match pen-name mapping templates, and tightens scope to lead/infobox snippets while forbidding mixed-entity queries. B is similar but narrower and less prescriptive.

## 55__split2__seg1__feedback

- idx: 55
- split_iter: 2
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.94
- why: Segment A makes a broader, re-centering change to retrieval: it shifts emphasis away from film-only metadata toward city/nation infobox facts, adds many city/nation anchors and type cues, and prescribes avoiding entire families of spurious anchors. This requires larger changes to which anchors and document types the generator prioritizes versus B's more targeted conjunctive pairing and overlap-filter step.

### right

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.84
- why: A prescribes a stronger, more explicit re-centering of retrieval onto city-level anchors and infobox-style facts (adds 'Capital of the Netherlands', 'country', 'language', specific type cues, and conjunctive query shapes) and more aggressively removes film/placename noise. B is similar but more conservative, keeping more film metadata and making a smaller shift.

## 6__split1__seg1__feedback

- idx: 6
- split_iter: 1
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: candidate_set
- confidence: 0.86
- why: B asks for a substantive re-center of retrieval from fork/local pages to river-level pages that explicitly list states (adds explicit 'states/flows through' tokens and an infobox/lead evidence preference). That requires broader changes to anchors, query templates, and the candidate set compared with A, which mostly augments fork-level queries with downstream landmarks while preserving fork specificity.

### right

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.82
- why: Both segments shift retrieval toward river-level pages, but B prescribes stronger, more specific semantic changes: explicit 'states/flows through' tokens, geographic boundary anchors (VA–WV), authority signals (infobox/'States:' lines), and strict title/snippet filters. Those prescriptions materially change query construction and filtering behavior beyond A's more general re-centering on river-level/state cues.

## 6__split3__seg2__feedback

- idx: 6
- split_iter: 3
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: candidate_set
- confidence: 0.86
- why: Segment A makes a more substantial semantic re-center: it shifts retrieval from upstream/VA-only documents to town-level confluence pages and map captions, adds new Potomac/Harpers Ferry/Jefferson County anchors and explicit confluence relations, and instructs avoiding broader Potomac or upstream noise — a bigger change to which documents and anchors are prioritized than B's lead/infobox emphasis.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.84
- why: Segment B gives a broader, more prescriptive semantic change: it not only shifts retrieval to lead/infobox/course language and title-matched Shenandoah River pages but also adds explicit BM25 anchor phrases, additional bridge clues to surface, and explicit avoid-rules (e.g., do not target only 'North Fork' or local place names). This requires a larger change to query shape, anchor selection, and candidate scoring than A's narrower landmark-to-lead refocus.

## 60__split0__seg0__feedback

- idx: 60
- split_iter: 0
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.77
- why: Segment A issues a broader, more fundamental re-centering: it preserves telescope and mission anchors, mandates boosting exact-date/year tokens and aliases, specifies preferring lead/infobox factual placements, and prescribes a direct entity→attribute query shape. B is a narrower mission-centric rerank/switch with domain cues. A therefore requires larger changes to which anchors, tokens, and retrieval signals the generator must preserve and prioritize.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.85
- why: Both segments request nearly identical semantic changes: preserve the same anchors (HST, STS-31, Discovery), add exact-date/year tokens and mission/infobox type cues, avoid instrument/other STS pages, and shape short entity→date queries. Differences are minor phrasing/level-of-detail rather than materially different retrieval targets or relation shifts.

## 60__split2__seg1__feedback

- idx: 60
- split_iter: 2
- num_edges_before_split: None
- left_recovery: True
- right_recovery: False

### left

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why: Segment A instructs a substantive re-anchor of retrieval from a Hubble-overview focus to the STS-31 mission entity (add STS-31, Discovery, mission pages, mission-infobox date phrases) — a change in which entity/title anchors and target document family to prioritize. B is a narrower refinement that keeps Hubble as the primary anchor and only tweaks timeline/infobox cues and token boosts. A therefore requires a larger semantic change to query-generation behavior.

### right

- predicted: tie
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.89
- why: Both segments make nearly identical semantic changes: re-center queries on the STS-31/Discovery mission anchor, add explicit launch-date tokens, prefer mission-summary/infobox sources, and avoid instrument or generic HST history pages. Neither introduces a materially larger or different semantic instruction.

## 77__split1__seg0__feedback

- idx: 77
- split_iter: 1
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: B
- expected: A
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why: Segment B prescribes a more substantial semantic shift: it re-centers queries on the person-as-owner bridge (explicit ownership verbs), prescribes quoted-name + ownership phrase patterns, and adds site-type filters (Wikipedia/news/profile) and tight BM25-friendly token spans. These instructions change which relation (ownership) and which sources to target more strongly than A's entity-centered exact-phrase and bakery-site emphasis.

### right

- predicted: A
- expected: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.8
- why: Segment A issues a broader, higher-level shift in retrieval focus (move away from show/prize context toward the bakery entity), prescribes new exact-owner phrase anchors, phrase-order preferences, and broader removal of noise—changing which anchors are prioritized and how queries are shaped. B is a narrower, tactical refinement targeting the same anchor set and BM25 tokens.

## 77__split2__seg0__feedback

- idx: 77
- split_iter: 2
- num_edges_before_split: None
- left_recovery: False
- right_recovery: True

### left

- predicted: A
- expected: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.82
- why: Segment A prescribes a substantive re-centering of retrieval anchors and evidence family — moving from person/ownership pages to season-level, prize-focused documents with exact-phrase prize links, date/site filters, and explicit avoidance of owner-centered tokens. That changes which entities, bridge signals, and target document types the generator must produce much more than B's simpler person-centered reweighting.

### right

- predicted: B
- expected: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.68
- why: Segment B is a broader, higher-level rerouting from base retrieval to person-centered ownership queries and specifies additional semantic query-shaping changes (short 3–6 token phrase matches, BM25-boosting quoted-name + ownership patterns, site-type hints, optional locality/date tokens). Those directions change query construction and scoring more extensively than A's narrower shift and filtering heuristics.
