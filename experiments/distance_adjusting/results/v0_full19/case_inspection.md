# Distance case inspection

- tasks_path: `experiments/distance_adjusting/cache/full19_distance_tasks.jsonl`
- judgments_path: `experiments/distance_adjusting/results/v0_full19/judgments.jsonl`

## left_fail (24 total, showing 8)

### 108__split0__seg0__left

- idx: 108
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.78
- why_larger: Segment B introduces an explicit disambiguation step and expands the anchors/bridge clues (adds Norwegian variant, Schweppes Australia/Asahi distributor cues) and a new midpoint retrieval focus — a clearer change in retrieval focus and entity anchoring compared with A's minor refinement toward the same Solo page.

**Question**

Are Solo and La Croix Sparkling Water produced in the same country ?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Solo (soft drink) Australian lemon-flavoured carbonated drink produced in Australia manufacturer Schweppes Asahi
- retrieved_titles: Solo (Australian soft drink), Passiona, Club (soft drink), Bitter lemon, Gini (soft drink), Mitsuya Cider, Jaffa (drink)
- retrieval_focus: Locate the Solo (soft drink) / Solo (Australian soft drink) article or a manufacturer/source that states the country of production for Solo to compare with La Croix's U.S. origin.
- anchors: Solo (soft drink), Solo (Australian soft drink), La Croix Sparkling Water, United States, Australia, Schweppes/Asahi
- bridge_clues: Solo described as an Australian lemon-flavoured carbonated drink (country of production/origin), Manufacturer/distributor named for Solo (Schweppes/Asahi) that implies country of manufacture, La Croix origin/production: United States (La Crosse, Wisconsin)
- noisy_or_distracting_clues: Other soft drink pages returned (Passiona, Club, Bitter lemon, Gini, Mitsuya Cider, Jaffa) that are unrelated flavors/brands, Query tokens 'Schweppes Asahi' may surface international manufacturer pages (e.g., Japanese or global subsidiaries) not directly stating Solo's production country, Ambiguity of the name 'Solo' (could refer to different regional brands)
- expected_evidence_type: A short factual source (Wikipedia infobox or manufacturer/distributor page) for Solo explicitly stating country of origin/production (e.g., 'Country of origin: Australia' or production location).
- query_shape_implication: This is a focused single-entity follow-up hop: a factoid lookup/disambiguation query. The presence of manufacturer names in the query can bias retrieval; include 'Australian' or exact page title to disambiguate and retrieve the precise Solo page needed to answer the comparison with La Croix.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Solo (soft drink) Australian lemon-flavoured carbonated drink produced in Australia manufacturer Schweppes Asahi
- retrieved_titles: Solo (Australian soft drink), Passiona, Club (soft drink), Bitter lemon, Gini (soft drink), Mitsuya Cider, Jaffa (drink)
- retrieval_focus: Locate the Solo (soft drink) / Solo (Australian soft drink) article or a manufacturer/source that states the country of production for Solo to compare with La Croix's U.S. origin.
- anchors: Solo (soft drink), Solo (Australian soft drink), La Croix Sparkling Water, United States, Australia, Schweppes/Asahi
- bridge_clues: Solo described as an Australian lemon-flavoured carbonated drink (country of production/origin), Manufacturer/distributor named for Solo (Schweppes/Asahi) that implies country of manufacture, La Croix origin/production: United States (La Crosse, Wisconsin)
- noisy_or_distracting_clues: Other soft drink pages returned (Passiona, Club, Bitter lemon, Gini, Mitsuya Cider, Jaffa) that are unrelated flavors/brands, Query tokens 'Schweppes Asahi' may surface international manufacturer pages (e.g., Japanese or global subsidiaries) not directly stating Solo's production country, Ambiguity of the name 'Solo' (could refer to different regional brands)
- expected_evidence_type: A short factual source (Wikipedia infobox or manufacturer/distributor page) for Solo explicitly stating country of origin/production (e.g., 'Country of origin: Australia' or production location).
- query_shape_implication: This is a focused single-entity follow-up hop: a factoid lookup/disambiguation query. The presence of manufacturer names in the query can bias retrieval; include 'Australian' or exact page title to disambiguate and retrieve the precise Solo page needed to answer the comparison with La Croix.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate 'Solo' and retrieve the canonical 'Solo (Australian soft drink)' page or an authoritative manufacturer page that explicitly states Solo's country of origin/production (Australia) so it can be compared to La Croix (United States).
- anchors: Solo (Australian soft drink), Solo (Norwegian soft drink), Solo (soft drink), La Croix Sparkling Water, United States, Australia, Schweppes Australia, Asahi/Distributor
- bridge_clues: Presence of a page titled 'Solo (Australian soft drink)' in search results, Lead/infobox text on the Solo page stating 'Country of origin' or 'Origin: Australia' or production/manufacturer located in Australia, Manufacturer or distributor entries (e.g., Schweppes Australia) on the Solo page that imply Australian production, Explicit disambiguation markers distinguishing Australian Solo from a Norwegian Solo
- noisy_or_distracting_clues: Search hits for 'Solo (Norwegian soft drink)' or other regional 'Solo' brands, Unrelated beverage pages (Trend Drinks, Geo. Hall & Sons, Rubicon, Guaraná Antarctica), Global manufacturer pages that mention Schweppes/Asahi in other countries without specifying Solo's production location
- expected_evidence_type: A short authoritative page (Wikipedia article infobox/lead or manufacturer's product page) that explicitly states Solo's country of origin/production (e.g., 'Country of origin: Australia' or a clear manufacturer/production location in Australia).
- query_shape_implication: Use a concise disambiguation-style query targeting the canonical page title or the phrase 'Solo (Australian soft drink) country of origin' to avoid regional variants and noisy brand pages; this is a single-entity retrieval step focused on resolving ambiguity.

---

### 108__split2__seg2__left

- idx: 108
- split_iter: 2
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: noisy_entity
- confidence: 0.78
- why_larger: Segment B introduces a substantive shift in retrieval strategy: instead of directly fetching the Solo product page (A), it changes the query shape to explicitly disambiguate the 'Solo' entity first. That is a larger correction for noisy/ambiguous entity variants and changes the evidence-path (disambiguation → canonical page) rather than a simple extraction step.

**Question**

Are Solo and La Croix Sparkling Water produced in the same country ?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Target the Solo (Australian soft drink) page and extract the lead/infobox lines that state country of origin/production and the named manufacturer/distributor (evidence that Solo is produced in Australia).
- anchors: Solo (Australian soft drink), infobox/lead sentence, Country of origin: Australia, Manufacturer / Distributor (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil), Production location / brewed/produced in
- bridge_clues: Lead sentence beginning with 'Solo is an Australian...' or similar, Infobox field 'Origin' or 'Country' listed as Australia, Explicit mention of manufacturer/distributor that operates in Australia (Schweppes Australia, Asahi, etc.), Phrases like 'Australian lemon-flavoured soft drink' or 'produced in Australia' in the page lead/intro
- noisy_or_distracting_clues: Pages for 'Solo (Norwegian soft drink)' or other regional Solo brands, General beverage manufacturer pages that mention Schweppes/Asahi in multiple countries without linking Solo to Australia, Lists of soft drinks where Solo appears without context about origin, News/articles about distribution deals that don't state production country
- expected_evidence_type: Short authoritative textual evidence from the Solo page (Wikipedia infobox/lead or manufacturer product page) explicitly stating country of origin/production (Australia) and/or naming the Australian manufacturer/distributor.
- query_shape_implication: A concise extraction-style query targeting the canonical Solo (Australian soft drink) page and its infobox/lead (e.g., phrasing that requests 'Solo (Australian soft drink) infobox origin' or 'Solo lead sentence country of origin') to avoid returning regional variants or generic brand lists.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

**Sub segment**

from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Target the Solo (Australian soft drink) page and extract the lead/infobox lines that state country of origin/production and the named manufacturer/distributor (evidence that Solo is produced in Australia).
- anchors: Solo (Australian soft drink), infobox/lead sentence, Country of origin: Australia, Manufacturer / Distributor (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil), Production location / brewed/produced in
- bridge_clues: Lead sentence beginning with 'Solo is an Australian...' or similar, Infobox field 'Origin' or 'Country' listed as Australia, Explicit mention of manufacturer/distributor that operates in Australia (Schweppes Australia, Asahi, etc.), Phrases like 'Australian lemon-flavoured soft drink' or 'produced in Australia' in the page lead/intro
- noisy_or_distracting_clues: Pages for 'Solo (Norwegian soft drink)' or other regional Solo brands, General beverage manufacturer pages that mention Schweppes/Asahi in multiple countries without linking Solo to Australia, Lists of soft drinks where Solo appears without context about origin, News/articles about distribution deals that don't state production country
- expected_evidence_type: Short authoritative textual evidence from the Solo page (Wikipedia infobox/lead or manufacturer product page) explicitly stating country of origin/production (Australia) and/or naming the Australian manufacturer/distributor.
- query_shape_implication: A concise extraction-style query targeting the canonical Solo (Australian soft drink) page and its infobox/lead (e.g., phrasing that requests 'Solo (Australian soft drink) infobox origin' or 'Solo lead sentence country of origin') to avoid returning regional variants or generic brand lists.

to_state:
- name: Rmid_iter3_split2
- kind: generated_midpoint
- retrieval_focus: First disambiguate which 'Solo' is intended by retrieving the Solo disambiguation/summary and any immediate manufacturer or product-summary lines that link the brand name to a country (e.g., 'Solo (Australian soft drink)' or a manufacturer page that explicitly ties Solo to Australia). This narrows scope before fetching full product pages.
- anchors: Solo (disambiguation) / 'Solo (soft drink)' summary line, Disambiguation entry that points to 'Solo (Australian soft drink)', Short lead/infobox lines from Solo (Australian soft drink) confirming country or origin, Manufacturer/distributor short page or header (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil) that mentions Solo
- bridge_clues: Disambiguation text: 'Solo may refer to...' with a line for the Australian soft drink, Lead sentence on Solo (Australian soft drink) beginning 'Solo is an Australian...' or 'Solo is a lemon-flavoured soft drink produced in Australia', Infobox or parenthetical note that lists 'Country of origin: Australia' or similar, Short manufacturer header stating they produce/distribute Solo in Australia
- noisy_or_distracting_clues: Entries for Solo (Norwegian soft drink) or other regional variants that could be mistaken for the Australian product, Long lists of beverages or manufacturer pages that mention many brands without clear country attribution, News/distribution articles that mention global companies (Schweppes, Asahi) without explicitly tying Solo to a production country, Unrelated beverage pages (Trend Drinks, V (drink), Guaraná Antarctica) that surface in broad queries
- expected_evidence_type: Short, authoritative disambiguation line or one-sentence lead/infobox text that unambiguously links 'Solo' to the Australian product (or indicates multiple regional products), and/or a manufacturer header that names Australia as the production/origin location.
- query_shape_implication: A concise disambiguation-style query that first asks for 'Solo (soft drink) disambiguation' or 'Solo disambiguation lead' and/or a tight extraction like 'Solo (Australian soft drink) lead/origin' to confirm which Solo to follow up on in the next retrieval.

---

### 118__split0__seg0__left

- idx: 118
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: noisy_entity
- confidence: 0.78
- why_larger: Segment A shifts the retrieval focus to disambiguate the ambiguous title 'Third Person' and to construct candidate actor-sets per specific title/version (a structural query-shape and entity-disambiguation change). Segment B is a narrower, target-focused step that simply pulls authoritative cast lists and some actor anchors, so A requires a larger correction of noisy/ambiguous entity and a bigger change in query strategy.

**Question**

What acress starred in both "Third Person" and "From Here to Eternity"?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Third Person (2013 film) cast; From Here to Eternity (1953 film) cast; From Here to Eternity (1979 miniseries) cast
- retrieved_titles: From Here to Eternity (TV series), From Here to Eternity (miniseries), From Here to Eternity, From Here to Eternity (disambiguation), Eternal Sunshine of the Spotless Mind, From Here to Eternity the Musical, From Here to Eternity: Live
- retrieval_focus: Locate authoritative cast lists for Third Person (film) and for all relevant versions of From Here to Eternity (1953 film and 1979 miniseries) to determine any performer appearing in both works.
- anchors: Third Person (film), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: full cast lists / credited actor names, matching performer names across both cast lists, version disambiguation (1953 film vs 1979 miniseries)
- noisy_or_distracting_clues: From Here to Eternity (disambiguation), From Here to Eternity the Musical, From Here to Eternity: Live, Eternal Sunshine of the Spotless Mind (unrelated), retrieved_titles lack a clear 'Third Person' cast page
- expected_evidence_type: Reliable cast/credit pages (Wikipedia infobox cast, IMDb full cast, or other filmographies) for each work listing actor names so overlaps can be directly compared.
- query_shape_implication: Queries must be version-specific and cast-focused (e.g., 'Third Person (2013) cast' and 'From Here to Eternity (1953) cast' / 'From Here to Eternity (1979) cast'); perform exact-name matching across lists to spot overlap; if multiple 'From Here to Eternity' results exist, check each version’s cast.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: From Here to Eternity (TV series), From Here to Eternity, From Here to Eternity (miniseries), From Here to Eternity (disambiguation), Kim Basinger, Donna Reed, Heather O'Rourke
- retrieval_focus: Get authoritative cast lists for the specific works named (disambiguate which 'Third Person' and which version of 'From Here to Eternity') so we can find any overlapping performer.
- anchors: Third Person, Third Person (film), From Here to Eternity, From Here to Eternity (1953 film), From Here to Eternity (miniseries), cast, Deborah Kerr, Donna Reed
- bridge_clues: cast, starring, credited, filmography, appeared in, played
- noisy_or_distracting_clues: From Here to Eternity (disambiguation), From Here to Eternity (TV series), Kim Basinger, Heather O'Rourke
- expected_evidence_type: Primary film pages or reliable cast lists (Wikipedia film pages, IMDb/filmography entries, reputable biographies) showing full credited cast for each title/version.
- query_shape_implication: Issue two precise second-hop queries (exact title + 'cast' or year): e.g. 'Third Person (film) cast' and 'From Here to Eternity (1953 film) cast' (or 'From Here to Eternity (1979 miniseries) cast' if that version is intended), then intersect named cast members.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Third Person (2013 film) cast; From Here to Eternity (1953 film) cast; From Here to Eternity (1979 miniseries) cast
- retrieved_titles: From Here to Eternity (TV series), From Here to Eternity (miniseries), From Here to Eternity, From Here to Eternity (disambiguation), Eternal Sunshine of the Spotless Mind, From Here to Eternity the Musical, From Here to Eternity: Live
- retrieval_focus: Locate authoritative cast lists for Third Person (film) and for all relevant versions of From Here to Eternity (1953 film and 1979 miniseries) to determine any performer appearing in both works.
- anchors: Third Person (film), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: full cast lists / credited actor names, matching performer names across both cast lists, version disambiguation (1953 film vs 1979 miniseries)
- noisy_or_distracting_clues: From Here to Eternity (disambiguation), From Here to Eternity the Musical, From Here to Eternity: Live, Eternal Sunshine of the Spotless Mind (unrelated), retrieved_titles lack a clear 'Third Person' cast page
- expected_evidence_type: Reliable cast/credit pages (Wikipedia infobox cast, IMDb full cast, or other filmographies) for each work listing actor names so overlaps can be directly compared.
- query_shape_implication: Queries must be version-specific and cast-focused (e.g., 'Third Person (2013) cast' and 'From Here to Eternity (1953) cast' / 'From Here to Eternity (1979) cast'); perform exact-name matching across lists to spot overlap; if multiple 'From Here to Eternity' results exist, check each version’s cast.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the title 'Third Person' (list all films/TV works with that title and their release years) and pull the top-billed actresses for each candidate; simultaneously confirm which specific version(s) of 'From Here to Eternity' are relevant by listing the common versions and their principal actresses. The goal is to produce candidate actor sets per specific title/version so the next step can do direct cast-list intersection.
- anchors: Third Person (disambiguation), Third Person (film) — candidate years/entries (e.g., 2013), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: work title + release year (to disambiguate similarly titled works), lead/billed actresses for each candidate Third Person, lead/billed actresses for each candidate From Here to Eternity version, short film/TV synopses to confirm which cast lists are primary (e.g., 'starring', 'lead')
- noisy_or_distracting_clues: unrelated items on disambiguation pages (books, plays, songs titled 'Third Person'), other similarly named films (e.g., 'The Third Man', 'Third Wheel'), spin-off or stage adaptations of 'From Here to Eternity' (musical, live shows), celebrity names surfaced by broad searches that are not credited as cast
- expected_evidence_type: Disambiguation pages and individual film/TV pages or reliable filmographies that list release year and top-billed cast (Wikipedia film pages, IMDb title pages, or authoritative filmographies) so candidate actress sets can be created per specific work/version.
- query_shape_implication: Run narrow, title-disambiguation queries first (e.g., 'Third Person disambiguation' and 'Third Person (year) cast' for each candidate year found) and a small set of version-specific lookups for 'From Here to Eternity' (1953 and 1979) to extract lead actresses; this produces compact named-actor lists to intersect in the subsequent step.

---

### 118__split1__seg1__left

- idx: 118
- split_iter: 1
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.74
- why_larger: Segment B makes a concrete, high-impact shift from a broad disambiguation plan to committing to specific title-year anchors (Third Person → 2013 film; From Here to Eternity → 1953 film) and narrows the retrieval focus to top-billed female cast. This is a stronger change in retrieval focus and requires a larger entity-anchor correction and query-shape tightening than A’s more general endpoint request for authoritative cast lists.

**Question**

What acress starred in both "Third Person" and "From Here to Eternity"?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the title 'Third Person' (list all films/TV works with that title and their release years) and pull the top-billed actresses for each candidate; simultaneously confirm which specific version(s) of 'From Here to Eternity' are relevant by listing the common versions and their principal actresses. The goal is to produce candidate actor sets per specific title/version so the next step can do direct cast-list intersection.
- anchors: Third Person (disambiguation), Third Person (film) — candidate years/entries (e.g., 2013), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: work title + release year (to disambiguate similarly titled works), lead/billed actresses for each candidate Third Person, lead/billed actresses for each candidate From Here to Eternity version, short film/TV synopses to confirm which cast lists are primary (e.g., 'starring', 'lead')
- noisy_or_distracting_clues: unrelated items on disambiguation pages (books, plays, songs titled 'Third Person'), other similarly named films (e.g., 'The Third Man', 'Third Wheel'), spin-off or stage adaptations of 'From Here to Eternity' (musical, live shows), celebrity names surfaced by broad searches that are not credited as cast
- expected_evidence_type: Disambiguation pages and individual film/TV pages or reliable filmographies that list release year and top-billed cast (Wikipedia film pages, IMDb title pages, or authoritative filmographies) so candidate actress sets can be created per specific work/version.
- query_shape_implication: Run narrow, title-disambiguation queries first (e.g., 'Third Person disambiguation' and 'Third Person (year) cast' for each candidate year found) and a small set of version-specific lookups for 'From Here to Eternity' (1953 and 1979) to extract lead actresses; this produces compact named-actor lists to intersect in the subsequent step.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: From Here to Eternity (TV series), From Here to Eternity, From Here to Eternity (miniseries), From Here to Eternity (disambiguation), Kim Basinger, Donna Reed, Heather O'Rourke
- retrieval_focus: Get authoritative cast lists for the specific works named (disambiguate which 'Third Person' and which version of 'From Here to Eternity') so we can find any overlapping performer.
- anchors: Third Person, Third Person (film), From Here to Eternity, From Here to Eternity (1953 film), From Here to Eternity (miniseries), cast, Deborah Kerr, Donna Reed
- bridge_clues: cast, starring, credited, filmography, appeared in, played
- noisy_or_distracting_clues: From Here to Eternity (disambiguation), From Here to Eternity (TV series), Kim Basinger, Heather O'Rourke
- expected_evidence_type: Primary film pages or reliable cast lists (Wikipedia film pages, IMDb/filmography entries, reputable biographies) showing full credited cast for each title/version.
- query_shape_implication: Issue two precise second-hop queries (exact title + 'cast' or year): e.g. 'Third Person (film) cast' and 'From Here to Eternity (1953 film) cast' (or 'From Here to Eternity (1979 miniseries) cast' if that version is intended), then intersect named cast members.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the title 'Third Person' (list all films/TV works with that title and their release years) and pull the top-billed actresses for each candidate; simultaneously confirm which specific version(s) of 'From Here to Eternity' are relevant by listing the common versions and their principal actresses. The goal is to produce candidate actor sets per specific title/version so the next step can do direct cast-list intersection.
- anchors: Third Person (disambiguation), Third Person (film) — candidate years/entries (e.g., 2013), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: work title + release year (to disambiguate similarly titled works), lead/billed actresses for each candidate Third Person, lead/billed actresses for each candidate From Here to Eternity version, short film/TV synopses to confirm which cast lists are primary (e.g., 'starring', 'lead')
- noisy_or_distracting_clues: unrelated items on disambiguation pages (books, plays, songs titled 'Third Person'), other similarly named films (e.g., 'The Third Man', 'Third Wheel'), spin-off or stage adaptations of 'From Here to Eternity' (musical, live shows), celebrity names surfaced by broad searches that are not credited as cast
- expected_evidence_type: Disambiguation pages and individual film/TV pages or reliable filmographies that list release year and top-billed cast (Wikipedia film pages, IMDb title pages, or authoritative filmographies) so candidate actress sets can be created per specific work/version.
- query_shape_implication: Run narrow, title-disambiguation queries first (e.g., 'Third Person disambiguation' and 'Third Person (year) cast' for each candidate year found) and a small set of version-specific lookups for 'From Here to Eternity' (1953 and 1979) to extract lead actresses; this produces compact named-actor lists to intersect in the subsequent step.

to_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Narrow to the single most likely candidate for each ambiguous title: treat 'Third Person' as the 2013 feature film (the most prominent modern film by that title) and 'From Here to Eternity' as the original 1953 film. Retrieve the top-billed female cast (lead actresses) for those two specific entries to produce compact candidate actress sets for a direct intersection step.
- anchors: Third Person (2013 film) — cast/top-billed actors, From Here to Eternity (1953 film) — cast/top-billed actresses, Wikipedia or IMDb title pages for each film (cast sections), Lead billing / 'starring' lines on film pages
- bridge_clues: exact title + year (e.g., 'Third Person 2013 cast', 'From Here to Eternity 1953 cast'), sections labeled 'Starring' or top-billed cast, female names listed among top 3–5 billed performers, role names or 'as' annotations confirming performer appearance
- noisy_or_distracting_clues: other works titled 'Third Person' (short films, books, songs), later remakes or TV adaptations of From Here to Eternity (1979 miniseries) if the question intends a different version, male lead names and supporting male cast (not needed for actress intersection), crew, production, trivia, soundtrack, and release-date minutiae
- expected_evidence_type: Authoritative cast lists or 'Starring' sections from film pages (Wikipedia/IMDb/reliable filmographies) showing top-billed performers with clear ordering so a concise female-actor candidate set can be extracted for each specified title.
- query_shape_implication: Run two narrow queries: 'Third Person 2013 cast' and 'From Here to Eternity 1953 cast' (or targeted lookups of their Wikipedia/IMDb pages), then extract the top-billed female names (e.g., the first 2–4 actresses listed) to produce small, comparable sets for the next step.

---

### 132__split0__seg0__left

- idx: 132
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.75
- why_larger: Segment B makes a more substantive shift in retrieval focus and evidence family: it narrows from a broad biography-centric search to album- and credit-oriented sources (Selmasongs credits, liner notes, music-database entries), correcting noisy birthdate/biography distractions and changing the expected evidence type. Segment A remains an endpoint-level restatement of the original goal (artist/biography or album page) and thus is a smaller refinement.

**Question**

The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Björk Guðmundsdóttir biography birthdate occupations discography filmography "Selmasongs" soundtrack credits Vespertine production credits
- retrieved_titles: Vespertine World Tour, Selmasongs, Vespertine, Björk Guðmundsdóttir &amp; tríó Guðmundar Ingólfssonar, List of songs recorded by Björk, Hidden Place, Björk (book)
- retrieval_focus: Locate an authoritative artist/biography page or the Selmasongs album page that explicitly credits who performed the Dancer in the Dark soundtrack and lists that person's occupations.
- anchors: Björk, Selmasongs, Dancer in the Dark, Vespertine, Selma Ježková, Lars von Trier
- bridge_clues: soundtrack, music from the motion picture, performed by, artist, soundtrack credits, album 'Selmasongs'
- noisy_or_distracting_clues: Vespertine World Tour, Hidden Place, Björk (book), tríó Guðmundar Ingólfssonar, List of songs recorded by Björk
- expected_evidence_type: Biographical/artist page or album (Selmasongs) page that explicitly credits Björk for the soundtrack and lists her occupations (singer, songwriter, actress, record producer, DJ).
- query_shape_implication: Entity-centric query targeting Björk's biography/discography and the Selmasongs album; prefer high-authority pages (official site, major music databases, Wikipedia) that consolidate occupation and soundtrack credit.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Selmasongs, Björk, Vespertine, Björk (album), Björk (book), Björk Guðmundsdóttir &amp; tríó Guðmundar Ingólfssonar, List of awards and nominations received by Anahí
- retrieval_focus: Locate authoritative pages that state who performed/created the Selmasongs/Dancer in the Dark soundtrack and confirm that this person is an Icelandic singer, songwriter, actress, record producer, and DJ.
- anchors: Dancer in the Dark, Selmasongs, Björk, Icelandic singer-songwriter-actress
- bridge_clues: soundtrack, Selmasongs: Music from the Motion Picture, soundtrack artist, performed the soundtrack, Selma Ježková (role linked to performer)
- noisy_or_distracting_clues: Vespertine (related album, not the soundtrack), Björk (album), Björk (book), Björk Guðmundsdóttir & tríó Guðmundar Ingólfssonar (different release), List of awards and nominations received by Anahí (irrelevant), empty/blank query field
- expected_evidence_type: Album/soundtrack page or artist biography that explicitly names Björk as the artist of Selmasongs/Dancer in the Dark and lists her occupations (singer, songwriter, actress, record producer, DJ).
- query_shape_implication: Use short, entity-centric queries that jump film->soundtrack->artist (e.g., 'Dancer in the Dark soundtrack artist', 'Selmasongs artist Björk', 'Björk Selmasongs'); target artist/album pages or soundtrack sections rather than broad film pages.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Björk Guðmundsdóttir biography birthdate occupations discography filmography "Selmasongs" soundtrack credits Vespertine production credits
- retrieved_titles: Vespertine World Tour, Selmasongs, Vespertine, Björk Guðmundsdóttir &amp; tríó Guðmundar Ingólfssonar, List of songs recorded by Björk, Hidden Place, Björk (book)
- retrieval_focus: Locate an authoritative artist/biography page or the Selmasongs album page that explicitly credits who performed the Dancer in the Dark soundtrack and lists that person's occupations.
- anchors: Björk, Selmasongs, Dancer in the Dark, Vespertine, Selma Ježková, Lars von Trier
- bridge_clues: soundtrack, music from the motion picture, performed by, artist, soundtrack credits, album 'Selmasongs'
- noisy_or_distracting_clues: Vespertine World Tour, Hidden Place, Björk (book), tríó Guðmundar Ingólfssonar, List of songs recorded by Björk
- expected_evidence_type: Biographical/artist page or album (Selmasongs) page that explicitly credits Björk for the soundtrack and lists her occupations (singer, songwriter, actress, record producer, DJ).
- query_shape_implication: Entity-centric query targeting Björk's biography/discography and the Selmasongs album; prefer high-authority pages (official site, major music databases, Wikipedia) that consolidate occupation and soundtrack credit.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow from a broad Björk biography to authoritative soundtrack/album credit sources: find the Selmasongs (Dancer in the Dark soundtrack) album page, soundtrack credits or music-database entries that explicitly credit the soundtrack to Björk and also identify her occupations/nationality.
- anchors: Selmasongs, Dancer in the Dark (soundtrack), Björk, soundtrack credits, album liner notes
- bridge_clues: Selmasongs credits, soundtrack artist credited, performed by Björk, music from the motion picture Selmasongs, soundtrack liner notes / credits list
- noisy_or_distracting_clues: Vespertine, Vespertine World Tour, Björk (book), tríó Guðmundar Ingólfssonar, general discography lists, birthdate-focused biography searches
- expected_evidence_type: Album/soundtrack page, liner notes, or reputable music database article that names the soundtrack artist (Selmasongs) and includes a short artist descriptor (e.g., Icelandic singer/songwriter/actress/producer/DJ) tying Björk to the soundtrack.
- query_shape_implication: Use mid-granularity, album- and credit-oriented queries (film+soundtrack+credits or album-title+credits) rather than full biography dumps or single-term entity jumps; target pages with explicit 'credited to' language.

---

### 132__split3__seg0__left

- idx: 132
- split_iter: 3
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.78
- why_larger: Segment B changes the evidence family more strongly: it shifts from a generic artist/album lookup to film-level credits plus the lead of an encyclopedia entry to explicitly surface both the soundtrack performer and the performer’s listed occupations. That is a bigger retrieval-focus and answerability change than A’s narrower move to album-release/music-database pages.

**Question**

The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Björk Guðmundsdóttir biography birthdate occupations discography filmography "Selmasongs" soundtrack credits Vespertine production credits
- retrieved_titles: Vespertine World Tour, Selmasongs, Vespertine, Björk Guðmundsdóttir &amp; tríó Guðmundar Ingólfssonar, List of songs recorded by Björk, Hidden Place, Björk (book)
- retrieval_focus: Locate an authoritative artist/biography page or the Selmasongs album page that explicitly credits who performed the Dancer in the Dark soundtrack and lists that person's occupations.
- anchors: Björk, Selmasongs, Dancer in the Dark, Vespertine, Selma Ježková, Lars von Trier
- bridge_clues: soundtrack, music from the motion picture, performed by, artist, soundtrack credits, album 'Selmasongs'
- noisy_or_distracting_clues: Vespertine World Tour, Hidden Place, Björk (book), tríó Guðmundar Ingólfssonar, List of songs recorded by Björk
- expected_evidence_type: Biographical/artist page or album (Selmasongs) page that explicitly credits Björk for the soundtrack and lists her occupations (singer, songwriter, actress, record producer, DJ).
- query_shape_implication: Entity-centric query targeting Björk's biography/discography and the Selmasongs album; prefer high-authority pages (official site, major music databases, Wikipedia) that consolidate occupation and soundtrack credit.

to_state:
- name: Rmid_iter3_split0
- kind: generated_midpoint
- retrieval_focus: Target authoritative album/soundtrack entries and reputable music-database pages for 'Selmasongs' / Dancer in the Dark that explicitly list the performing artist (expect 'Björk') — e.g., Wikipedia album page, Discogs release, AllMusic entry, or the film's soundtrack section on IMDb.
- anchors: Selmasongs, Dancer in the Dark, Björk, soundtrack, album entry
- bridge_clues: Selmasongs (album) page, credited to Björk, performed by Björk, soundtrack listing / album credits (album-level), music-database album entry (Discogs, AllMusic, Wikipedia)
- noisy_or_distracting_clues: Vespertine, Vespertine World Tour, Björk biography deep-dives, books about Björk, session musicians and remix credits, label/release-format minutiae
- expected_evidence_type: Album- or soundtrack-level sources (Wikipedia album page, Discogs release page, AllMusic entry, IMDb soundtrack section) that name the artist credited for Selmasongs/Dancer in the Dark soundtrack (showing 'Björk' as performer).
- query_shape_implication: Mid-granularity queries combining album title + 'soundtrack' or 'Selmasongs' + 'credits' or 'performed by' and restricting to authoritative domains (site:wikipedia.org, site:discogs.com, site:allmusic.com, site:imdb.com). Aim for pages that state the soundtrack artist without yet requiring full biographical occupation lists.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Björk Guðmundsdóttir biography birthdate occupations discography filmography "Selmasongs" soundtrack credits Vespertine production credits
- retrieved_titles: Vespertine World Tour, Selmasongs, Vespertine, Björk Guðmundsdóttir &amp; tríó Guðmundar Ingólfssonar, List of songs recorded by Björk, Hidden Place, Björk (book)
- retrieval_focus: Locate an authoritative artist/biography page or the Selmasongs album page that explicitly credits who performed the Dancer in the Dark soundtrack and lists that person's occupations.
- anchors: Björk, Selmasongs, Dancer in the Dark, Vespertine, Selma Ježková, Lars von Trier
- bridge_clues: soundtrack, music from the motion picture, performed by, artist, soundtrack credits, album 'Selmasongs'
- noisy_or_distracting_clues: Vespertine World Tour, Hidden Place, Björk (book), tríó Guðmundar Ingólfssonar, List of songs recorded by Björk
- expected_evidence_type: Biographical/artist page or album (Selmasongs) page that explicitly credits Björk for the soundtrack and lists her occupations (singer, songwriter, actress, record producer, DJ).
- query_shape_implication: Entity-centric query targeting Björk's biography/discography and the Selmasongs album; prefer high-authority pages (official site, major music databases, Wikipedia) that consolidate occupation and soundtrack credit.

to_state:
- name: Rmid_iter4_split0
- kind: generated_midpoint
- retrieval_focus: Check film-level credits and concise encyclopedia introductions that tie the Dancer in the Dark soundtrack to its performer and list that performer's principal occupations — narrower than a full biography search but broader than album-release databases.
- anchors: Dancer in the Dark (film), Selmasongs, Björk, soundtrack credit, film credits, lead artist/performer
- bridge_clues: soundtrack credited to, film soundtrack section, starring Björk, Selmasongs referenced from the film page, lead paragraph of Björk's encyclopedia entry (occupations), credited performer / music by
- noisy_or_distracting_clues: Vespertine, Vespertine World Tour, session musicians and remix credits, record label release formats, books about Björk, deep discography lists
- expected_evidence_type: Film-page soundtrack / credits sections (Wikipedia, IMDb, press kits) and the lead of a trusted biographical entry that explicitly state the soundtrack performer and summarize occupations (e.g., 'Björk — Icelandic singer, songwriter, actress, record producer, DJ').
- query_shape_implication: Compose mid-granularity queries combining the film title + 'soundtrack' or 'credits' and the artist name, plus a focused lookup for the lead sentence of the artist's encyclopedia entry; prioritize authoritative domains (wikipedia.org, imdb.com, major news sites) rather than exhaustive album-release listings.

---

### 149__split0__seg0__left

- idx: 149
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.78
- why_larger: Segment A makes a clear, substantive shift in retrieval focus and query strategy: it narrows from a broad, multi-term synonym-rich search to high-precision pairwise queries aimed specifically at short definitional/etymological passages that explicitly state identity (e.g., 'the hulder is originally the same being as Huld'). It also prunes peripheral anchors (e.g., Tallemaja) and refocuses expected evidence type — a stronger, semantic change than B, which mainly shows a change in retrieved titles with persistent noisy items rather than a deeper query/evidence-type refinement.

**Question**

A mythical forest creature that is seductive and from Sweden has the same being as what divine figure?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Huld völva Holda Holle Germanic goddess origin of hulder skogsrå Tallemaja
- retrieved_titles: Hulder, Holda, Huld, Spillaholle, Gussy Holl, 872 Holda, Frau Holle
- retrieval_focus: Find authoritative statements and etymological evidence that equate the Swedish seductive forest-creature hulder (skogsrå) with the völva/divine figure Huld and the Germanic Holda/Frau Holle; confirm role shift from goddess/seer to folkloric forest spirit.
- anchors: Huld, Holda, Frau Holle, Hulder, Skogsrå, Völva, Tallemaja
- bridge_clues: hulder derives from Huld / shared name root, Huld described as a völva or divine seer, Holda/Frau Holle equated with Huld, etymology: huldr / huld = 'hidden/covered', transformation from goddess/seer to folk forest spirit, regional names linking hulder to Huld (skogsrå, Tallemaja, ulda)
- noisy_or_distracting_clues: Spillaholle, Gussy Holl, 872 Holda
- expected_evidence_type: encyclopedic or folklore entries and comparative-mythology or etymology discussions that explicitly link the names (Huld/Holda) to hulder/skogsrå and describe religious/functional equivalence (völva/goddess → forest spirit).
- query_shape_implication: Multi-term, synonym-rich query: combine exact name variants with role/etymology terms (e.g., 'Huld völva etymology', 'hulder origin Huld Holda', 'skogsrå Huld Holda') and prefer scholarly/encyclopedic sources to avoid unrelated hits.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Hulder, Huld, Holda, Coat of arms of Lardal, 872 Holda, Skogsrå, Haugtussa
- retrieval_focus: Locate authoritative statements linking the Swedish seductive forest spirit (hulder / skogsrå) to the divine/seer figure Huld and to the Germanic figure Holda/Frau Holle — i.e., evidence that they are the same being/origins.
- anchors: Hulder, Huld, Holda, Frau Holle, Skogsrå, völva
- bridge_clues: originally the same being, etymology of hulder (covered/secret), Huld as a völva (seer), Holda / Frau Holle equivalence, regional names: Tallemaja, ulda, Scandinavian / Germanic origin link
- noisy_or_distracting_clues: Coat of arms of Lardal, 872 Holda, Haugtussa
- expected_evidence_type: Short definitional/etymological sentences on Huld/Holda/Hulder pages explicitly stating identity/origin links (e.g., 'the hulder is originally the same being as Huld' or 'Huld equated with Holda/Frau Holle').
- query_shape_implication: Entity-to-entity equivalence query: short, high-precision search combining names and synonyms plus relationship keywords (e.g., hulder / skogsrå + Huld + Holda/Frau Holle + 'same being'|'originally'|'etymology'|'völva').

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Huld völva Holda Holle Germanic goddess origin of hulder skogsrå Tallemaja
- retrieved_titles: Hulder, Holda, Huld, Spillaholle, Gussy Holl, 872 Holda, Frau Holle
- retrieval_focus: Find authoritative statements and etymological evidence that equate the Swedish seductive forest-creature hulder (skogsrå) with the völva/divine figure Huld and the Germanic Holda/Frau Holle; confirm role shift from goddess/seer to folkloric forest spirit.
- anchors: Huld, Holda, Frau Holle, Hulder, Skogsrå, Völva, Tallemaja
- bridge_clues: hulder derives from Huld / shared name root, Huld described as a völva or divine seer, Holda/Frau Holle equated with Huld, etymology: huldr / huld = 'hidden/covered', transformation from goddess/seer to folk forest spirit, regional names linking hulder to Huld (skogsrå, Tallemaja, ulda)
- noisy_or_distracting_clues: Spillaholle, Gussy Holl, 872 Holda
- expected_evidence_type: encyclopedic or folklore entries and comparative-mythology or etymology discussions that explicitly link the names (Huld/Holda) to hulder/skogsrå and describe religious/functional equivalence (völva/goddess → forest spirit).
- query_shape_implication: Multi-term, synonym-rich query: combine exact name variants with role/etymology terms (e.g., 'Huld völva etymology', 'hulder origin Huld Holda', 'skogsrå Huld Holda') and prefer scholarly/encyclopedic sources to avoid unrelated hits.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow search to authoritative etymology and comparative-mythology statements that explicitly link the Swedish hulder/skogsrå name to Huld and show Huld's identification with Holda/Frau Holle; prioritize encyclopedia/folklore/etymology entries that give short identity claims rather than broader cultural history.
- anchors: Hulder, Huld, Holda, Skogsrå, Völva, Frau Holle
- bridge_clues: etymology: huldr / huld = 'hidden/covered' as name-root connection, explicit sentence: 'the hulder is originally the same being as Huld', scholarly/encyclopedic note equating Huld with Holda/Frau Holle, regional name citations (Tallemaja, ulda) used in etymology or name-history sections
- noisy_or_distracting_clues: Coat of arms of Lardal, 872 Holda, Haugtussa, Spillaholle, Gussy Holl
- expected_evidence_type: Short definitional or etymological passages in encyclopedia/folklore/dictionary entries or comparative-mythology summaries that state name-derivation and identity (e.g., a line that directly links hulder → Huld and Huld ↔ Holda/Frau Holle).
- query_shape_implication: Concise high-precision pairwise queries combining the folkloric term and candidate divine names with relationship keywords (examples to guide retrieval: 'hulder Huld etymology', 'hulder same as Holda', 'Huld völva Holda identity'), focusing on authoritative sources.

---

### 149__split3__seg2__left

- idx: 149
- split_iter: 3
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.75
- why_larger: Segment B shifts the retrieval focus more substantially: from a prior etymology/name-origin baseline it moves to a different evidence family (intermediate comparative material) that requires gathering primary attestations, motif-by-motif comparisons, and scholarly hypothesis arguments rather than just short etymological/encyclopedic identity lines. That is a broader change in what kinds of sources and query shapes are needed, whereas A is mainly a narrowing to high‑precision etymology/identity statements.

**Question**

A mythical forest creature that is seductive and from Sweden has the same being as what divine figure?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter3_split1
- kind: generated_midpoint
- retrieval_focus: Move from establishing hulder ← huld name-origin and Huld's role as a völva (R_left) toward comparative-mythology evidence that connects the name/figure Huld with the Germanic Holda/Frau Holle, without yet asserting a definitive identity. Look for sources that discuss cognate names, cross‑regional parallels, and scholarly claims that Huld and Holda/Frau Holle are related or derived from a common archetype.
- anchors: Hulder, Huld, Holda / Hold(e)a, Frau Holle, name cognates / etymology, comparative mythology
- bridge_clues: scholarly/comparative-mythology statements noting Huld and Holda as cognate or analogous figures, etymological notes showing Huld/Huldr and Holda/Holda share a root or semantic field (e.g., 'hidden', 'cover') or are treated as related names, encyclopaedia or folklore reference paragraphs that link Huld to Germanic Holda without full summary claims, comparisons of attributes/roles (seeress, household/fertility/witchy associations) used to argue a common origin, medieval or early-modern source citations where Huld/Holda appear in analogous contexts
- noisy_or_distracting_clues: modern pop-culture retellings or novels using 'Huld'/'Holda' names, local civic heraldry or municipal pages invoking similar names, unrelated personal names or catalog entries containing 'Holda' as an identifier, lists of folklore motifs that mention many superficially similar names without etymological linking
- expected_evidence_type: Comparative-mythology discussions, etymological dictionary entries that propose cognacy or close relation between Huld/Huldr and Holda/Holda, encyclopedia/folklore reference passages that present Huld↔Holda as a scholarly hypothesis or parallel (not necessarily a definitive equivalence), and citations of primary medieval references showing both names in related roles.
- query_shape_implication: Combine Huld/Huldr with Holda/Holda/Frau Holle using relation keywords (examples to guide retrieval: 'Huld Holda cognate', 'Huld Frau Holle comparative mythology', 'huldr holda etymology', 'Huld Holda parallels medieval sources'); favor comparative-mythology and etymology sources that evaluate the relationship rather than single-language name origins or purely local hulder tales.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow search to authoritative etymology and comparative-mythology statements that explicitly link the Swedish hulder/skogsrå name to Huld and show Huld's identification with Holda/Frau Holle; prioritize encyclopedia/folklore/etymology entries that give short identity claims rather than broader cultural history.
- anchors: Hulder, Huld, Holda, Skogsrå, Völva, Frau Holle
- bridge_clues: etymology: huldr / huld = 'hidden/covered' as name-root connection, explicit sentence: 'the hulder is originally the same being as Huld', scholarly/encyclopedic note equating Huld with Holda/Frau Holle, regional name citations (Tallemaja, ulda) used in etymology or name-history sections
- noisy_or_distracting_clues: Coat of arms of Lardal, 872 Holda, Haugtussa, Spillaholle, Gussy Holl
- expected_evidence_type: Short definitional or etymological passages in encyclopedia/folklore/dictionary entries or comparative-mythology summaries that state name-derivation and identity (e.g., a line that directly links hulder → Huld and Huld ↔ Holda/Frau Holle).
- query_shape_implication: Concise high-precision pairwise queries combining the folkloric term and candidate divine names with relationship keywords (examples to guide retrieval: 'hulder Huld etymology', 'hulder same as Holda', 'Huld völva Holda identity'), focusing on authoritative sources.

**Sub segment**

from_state:
- name: Rmid_iter3_split1
- kind: generated_midpoint
- retrieval_focus: Move from establishing hulder ← huld name-origin and Huld's role as a völva (R_left) toward comparative-mythology evidence that connects the name/figure Huld with the Germanic Holda/Frau Holle, without yet asserting a definitive identity. Look for sources that discuss cognate names, cross‑regional parallels, and scholarly claims that Huld and Holda/Frau Holle are related or derived from a common archetype.
- anchors: Hulder, Huld, Holda / Hold(e)a, Frau Holle, name cognates / etymology, comparative mythology
- bridge_clues: scholarly/comparative-mythology statements noting Huld and Holda as cognate or analogous figures, etymological notes showing Huld/Huldr and Holda/Holda share a root or semantic field (e.g., 'hidden', 'cover') or are treated as related names, encyclopaedia or folklore reference paragraphs that link Huld to Germanic Holda without full summary claims, comparisons of attributes/roles (seeress, household/fertility/witchy associations) used to argue a common origin, medieval or early-modern source citations where Huld/Holda appear in analogous contexts
- noisy_or_distracting_clues: modern pop-culture retellings or novels using 'Huld'/'Holda' names, local civic heraldry or municipal pages invoking similar names, unrelated personal names or catalog entries containing 'Holda' as an identifier, lists of folklore motifs that mention many superficially similar names without etymological linking
- expected_evidence_type: Comparative-mythology discussions, etymological dictionary entries that propose cognacy or close relation between Huld/Huldr and Holda/Holda, encyclopedia/folklore reference passages that present Huld↔Holda as a scholarly hypothesis or parallel (not necessarily a definitive equivalence), and citations of primary medieval references showing both names in related roles.
- query_shape_implication: Combine Huld/Huldr with Holda/Holda/Frau Holle using relation keywords (examples to guide retrieval: 'Huld Holda cognate', 'Huld Frau Holle comparative mythology', 'huldr holda etymology', 'Huld Holda parallels medieval sources'); favor comparative-mythology and etymology sources that evaluate the relationship rather than single-language name origins or purely local hulder tales.

to_state:
- name: Rmid_iter4_split2
- kind: generated_midpoint
- retrieval_focus: Find intermediate comparative-material that documents historical attestations and characteristic attributes of the name/figure Huld (Huldr) in Old Norse/Scandinavian sources and separately of Holda/Frau Holle in Germanic tradition, emphasizing overlapping roles/traits (seeress/witchcraft, household/fertility associations, 'hidden' semantics) and noting proposed name-form parallels without demanding an explicit one-line identification. Prioritize sources that present parallels and possible cognacy as a scholarly hypothesis or list of shared motifs rather than definitive encyclopedic identity statements.
- anchors: Huld / Huldr (attestations, Old Norse mentions), Hulder / skogsrå (Swedish folkloric descriptions), Holda / Hold(e)a / Frau Holle (Germanic tradition summaries), völva / seiðr (roles and practices), name-form variants and semantic field ('huld' = hidden/covered)
- bridge_clues: medieval/early-modern passages that mention a named Huld or Huldr acting as seeress, sorceress, or forest spirit, folklore compendia entries that compare attributes of hulder/skogsrå tales with Holda/Frau Holle motifs (e.g., household guardianship, nocturnal processions, witchcraft, gift/reward patterns), etymological notes that list the huld- root across Germanic languages and suggest semantic overlap (e.g., 'hidden, covered, gracious') without asserting full cognacy, comparative-mythology paragraphs that frame Huld and Holda as parallel figures in scholarship, presenting arguments and counterarguments, citations to primary sources or saga/chronicle passages where Huld/Huldr appears, and to Germanic folklore collections describing Holda/Frau Holle
- noisy_or_distracting_clues: modern novels, songs, or games using 'Huld'/'Holda' as character names, astronomical/object names (e.g., asteroid '872 Holda'), municipal or heraldic pages referencing local legends, databases or indexes that list many superficially similar folklore names without commentary, personal names, businesses, or unrelated species named 'Holda' or 'Huld'
- expected_evidence_type: Middle-tier comparative material: folklore encyclopedia paragraphs, scholarly articles or book chapters discussing motif overlap, primary-source quotes (saga/chronicle excerpts) showing Huld/Huldr occurrences, and etymological dictionary notes that point to shared huld- roots or semantic fields—materials that support a hypothesized link but stop short of a single definitive identity claim.
- query_shape_implication: Search for pairwise and motif-focused phrases that join attestations and attributes rather than asking for definitive equivalence (examples to guide retrieval: 'Huld saga attestation', 'Huldr völva seiðr sources', 'Huld Holda parallels motifs', 'huldr huld root Germanic semantics', 'skogsrå Holda comparison folklore'), favoring sources that enumerate parallels, primary citations, or cautious scholarly hypotheses.

---

## right_fail (22 total, showing 8)

### 108__split0__seg0__right

- idx: 108
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why_larger: Segment A moves from an empty/generated midpoint with no retrieved titles and a broad disambiguation focus to a concrete target state that includes the canonical 'Solo (Australian soft drink)' title and focused retrieval clues. This is a larger retrieval-focus and entity-anchor correction (resolving 'Solo' ambiguity) than B, which already started with a focused query and the Solo page present.

**Question**

Are Solo and La Croix Sparkling Water produced in the same country ?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Solo (soft drink) Australian lemon-flavoured carbonated drink produced in Australia manufacturer Schweppes Asahi
- retrieved_titles: Solo (Australian soft drink), Passiona, Club (soft drink), Bitter lemon, Gini (soft drink), Mitsuya Cider, Jaffa (drink)
- retrieval_focus: Locate the Solo (soft drink) / Solo (Australian soft drink) article or a manufacturer/source that states the country of production for Solo to compare with La Croix's U.S. origin.
- anchors: Solo (soft drink), Solo (Australian soft drink), La Croix Sparkling Water, United States, Australia, Schweppes/Asahi
- bridge_clues: Solo described as an Australian lemon-flavoured carbonated drink (country of production/origin), Manufacturer/distributor named for Solo (Schweppes/Asahi) that implies country of manufacture, La Croix origin/production: United States (La Crosse, Wisconsin)
- noisy_or_distracting_clues: Other soft drink pages returned (Passiona, Club, Bitter lemon, Gini, Mitsuya Cider, Jaffa) that are unrelated flavors/brands, Query tokens 'Schweppes Asahi' may surface international manufacturer pages (e.g., Japanese or global subsidiaries) not directly stating Solo's production country, Ambiguity of the name 'Solo' (could refer to different regional brands)
- expected_evidence_type: A short factual source (Wikipedia infobox or manufacturer/distributor page) for Solo explicitly stating country of origin/production (e.g., 'Country of origin: Australia' or production location).
- query_shape_implication: This is a focused single-entity follow-up hop: a factoid lookup/disambiguation query. The presence of manufacturer names in the query can bias retrieval; include 'Australian' or exact page title to disambiguate and retrieve the precise Solo page needed to answer the comparison with La Croix.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate 'Solo' and retrieve the canonical 'Solo (Australian soft drink)' page or an authoritative manufacturer page that explicitly states Solo's country of origin/production (Australia) so it can be compared to La Croix (United States).
- anchors: Solo (Australian soft drink), Solo (Norwegian soft drink), Solo (soft drink), La Croix Sparkling Water, United States, Australia, Schweppes Australia, Asahi/Distributor
- bridge_clues: Presence of a page titled 'Solo (Australian soft drink)' in search results, Lead/infobox text on the Solo page stating 'Country of origin' or 'Origin: Australia' or production/manufacturer located in Australia, Manufacturer or distributor entries (e.g., Schweppes Australia) on the Solo page that imply Australian production, Explicit disambiguation markers distinguishing Australian Solo from a Norwegian Solo
- noisy_or_distracting_clues: Search hits for 'Solo (Norwegian soft drink)' or other regional 'Solo' brands, Unrelated beverage pages (Trend Drinks, Geo. Hall & Sons, Rubicon, Guaraná Antarctica), Global manufacturer pages that mention Schweppes/Asahi in other countries without specifying Solo's production location
- expected_evidence_type: A short authoritative page (Wikipedia article infobox/lead or manufacturer's product page) that explicitly states Solo's country of origin/production (e.g., 'Country of origin: Australia' or a clear manufacturer/production location in Australia).
- query_shape_implication: Use a concise disambiguation-style query targeting the canonical page title or the phrase 'Solo (Australian soft drink) country of origin' to avoid regional variants and noisy brand pages; this is a single-entity retrieval step focused on resolving ambiguity.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

---

### 108__split2__seg2__right

- idx: 108
- split_iter: 2
- task_kind: right_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: Segment B performs an explicit disambiguation step—resolving which 'Solo' is intended and eliminating noisy variants before fetching the product page. That is a larger retrieval-focus change (anchor correction/ambiguity resolution) and a bigger evidence-family update than A, which already targeted the Solo (Australian) page directly.

**Question**

Are Solo and La Croix Sparkling Water produced in the same country ?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Target the Solo (Australian soft drink) page and extract the lead/infobox lines that state country of origin/production and the named manufacturer/distributor (evidence that Solo is produced in Australia).
- anchors: Solo (Australian soft drink), infobox/lead sentence, Country of origin: Australia, Manufacturer / Distributor (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil), Production location / brewed/produced in
- bridge_clues: Lead sentence beginning with 'Solo is an Australian...' or similar, Infobox field 'Origin' or 'Country' listed as Australia, Explicit mention of manufacturer/distributor that operates in Australia (Schweppes Australia, Asahi, etc.), Phrases like 'Australian lemon-flavoured soft drink' or 'produced in Australia' in the page lead/intro
- noisy_or_distracting_clues: Pages for 'Solo (Norwegian soft drink)' or other regional Solo brands, General beverage manufacturer pages that mention Schweppes/Asahi in multiple countries without linking Solo to Australia, Lists of soft drinks where Solo appears without context about origin, News/articles about distribution deals that don't state production country
- expected_evidence_type: Short authoritative textual evidence from the Solo page (Wikipedia infobox/lead or manufacturer product page) explicitly stating country of origin/production (Australia) and/or naming the Australian manufacturer/distributor.
- query_shape_implication: A concise extraction-style query targeting the canonical Solo (Australian soft drink) page and its infobox/lead (e.g., phrasing that requests 'Solo (Australian soft drink) infobox origin' or 'Solo lead sentence country of origin') to avoid returning regional variants or generic brand lists.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

**Sub segment**

from_state:
- name: Rmid_iter3_split2
- kind: generated_midpoint
- retrieval_focus: First disambiguate which 'Solo' is intended by retrieving the Solo disambiguation/summary and any immediate manufacturer or product-summary lines that link the brand name to a country (e.g., 'Solo (Australian soft drink)' or a manufacturer page that explicitly ties Solo to Australia). This narrows scope before fetching full product pages.
- anchors: Solo (disambiguation) / 'Solo (soft drink)' summary line, Disambiguation entry that points to 'Solo (Australian soft drink)', Short lead/infobox lines from Solo (Australian soft drink) confirming country or origin, Manufacturer/distributor short page or header (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil) that mentions Solo
- bridge_clues: Disambiguation text: 'Solo may refer to...' with a line for the Australian soft drink, Lead sentence on Solo (Australian soft drink) beginning 'Solo is an Australian...' or 'Solo is a lemon-flavoured soft drink produced in Australia', Infobox or parenthetical note that lists 'Country of origin: Australia' or similar, Short manufacturer header stating they produce/distribute Solo in Australia
- noisy_or_distracting_clues: Entries for Solo (Norwegian soft drink) or other regional variants that could be mistaken for the Australian product, Long lists of beverages or manufacturer pages that mention many brands without clear country attribution, News/distribution articles that mention global companies (Schweppes, Asahi) without explicitly tying Solo to a production country, Unrelated beverage pages (Trend Drinks, V (drink), Guaraná Antarctica) that surface in broad queries
- expected_evidence_type: Short, authoritative disambiguation line or one-sentence lead/infobox text that unambiguously links 'Solo' to the Australian product (or indicates multiple regional products), and/or a manufacturer header that names Australia as the production/origin location.
- query_shape_implication: A concise disambiguation-style query that first asks for 'Solo (soft drink) disambiguation' or 'Solo disambiguation lead' and/or a tight extraction like 'Solo (Australian soft drink) lead/origin' to confirm which Solo to follow up on in the next retrieval.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

---

### 118__split0__seg0__right

- idx: 118
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.85
- why_larger: Segment A moves from a disambiguation/planning state (broadly enumerating possible 'Third Person' works and candidate actress sets) to a targeted retrieval of authoritative cast lists for specific title/versions — a substantive shift in retrieval focus and resolution of ambiguous entity anchors. Segment B already starts with version-specific cast queries, so its transition is smaller.

**Question**

What acress starred in both "Third Person" and "From Here to Eternity"?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Third Person (2013 film) cast; From Here to Eternity (1953 film) cast; From Here to Eternity (1979 miniseries) cast
- retrieved_titles: From Here to Eternity (TV series), From Here to Eternity (miniseries), From Here to Eternity, From Here to Eternity (disambiguation), Eternal Sunshine of the Spotless Mind, From Here to Eternity the Musical, From Here to Eternity: Live
- retrieval_focus: Locate authoritative cast lists for Third Person (film) and for all relevant versions of From Here to Eternity (1953 film and 1979 miniseries) to determine any performer appearing in both works.
- anchors: Third Person (film), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: full cast lists / credited actor names, matching performer names across both cast lists, version disambiguation (1953 film vs 1979 miniseries)
- noisy_or_distracting_clues: From Here to Eternity (disambiguation), From Here to Eternity the Musical, From Here to Eternity: Live, Eternal Sunshine of the Spotless Mind (unrelated), retrieved_titles lack a clear 'Third Person' cast page
- expected_evidence_type: Reliable cast/credit pages (Wikipedia infobox cast, IMDb full cast, or other filmographies) for each work listing actor names so overlaps can be directly compared.
- query_shape_implication: Queries must be version-specific and cast-focused (e.g., 'Third Person (2013) cast' and 'From Here to Eternity (1953) cast' / 'From Here to Eternity (1979) cast'); perform exact-name matching across lists to spot overlap; if multiple 'From Here to Eternity' results exist, check each version’s cast.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: From Here to Eternity (TV series), From Here to Eternity, From Here to Eternity (miniseries), From Here to Eternity (disambiguation), Kim Basinger, Donna Reed, Heather O'Rourke
- retrieval_focus: Get authoritative cast lists for the specific works named (disambiguate which 'Third Person' and which version of 'From Here to Eternity') so we can find any overlapping performer.
- anchors: Third Person, Third Person (film), From Here to Eternity, From Here to Eternity (1953 film), From Here to Eternity (miniseries), cast, Deborah Kerr, Donna Reed
- bridge_clues: cast, starring, credited, filmography, appeared in, played
- noisy_or_distracting_clues: From Here to Eternity (disambiguation), From Here to Eternity (TV series), Kim Basinger, Heather O'Rourke
- expected_evidence_type: Primary film pages or reliable cast lists (Wikipedia film pages, IMDb/filmography entries, reputable biographies) showing full credited cast for each title/version.
- query_shape_implication: Issue two precise second-hop queries (exact title + 'cast' or year): e.g. 'Third Person (film) cast' and 'From Here to Eternity (1953 film) cast' (or 'From Here to Eternity (1979 miniseries) cast' if that version is intended), then intersect named cast members.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the title 'Third Person' (list all films/TV works with that title and their release years) and pull the top-billed actresses for each candidate; simultaneously confirm which specific version(s) of 'From Here to Eternity' are relevant by listing the common versions and their principal actresses. The goal is to produce candidate actor sets per specific title/version so the next step can do direct cast-list intersection.
- anchors: Third Person (disambiguation), Third Person (film) — candidate years/entries (e.g., 2013), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: work title + release year (to disambiguate similarly titled works), lead/billed actresses for each candidate Third Person, lead/billed actresses for each candidate From Here to Eternity version, short film/TV synopses to confirm which cast lists are primary (e.g., 'starring', 'lead')
- noisy_or_distracting_clues: unrelated items on disambiguation pages (books, plays, songs titled 'Third Person'), other similarly named films (e.g., 'The Third Man', 'Third Wheel'), spin-off or stage adaptations of 'From Here to Eternity' (musical, live shows), celebrity names surfaced by broad searches that are not credited as cast
- expected_evidence_type: Disambiguation pages and individual film/TV pages or reliable filmographies that list release year and top-billed cast (Wikipedia film pages, IMDb title pages, or authoritative filmographies) so candidate actress sets can be created per specific work/version.
- query_shape_implication: Run narrow, title-disambiguation queries first (e.g., 'Third Person disambiguation' and 'Third Person (year) cast' for each candidate year found) and a small set of version-specific lookups for 'From Here to Eternity' (1953 and 1979) to extract lead actresses; this produces compact named-actor lists to intersect in the subsequent step.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: From Here to Eternity (TV series), From Here to Eternity, From Here to Eternity (miniseries), From Here to Eternity (disambiguation), Kim Basinger, Donna Reed, Heather O'Rourke
- retrieval_focus: Get authoritative cast lists for the specific works named (disambiguate which 'Third Person' and which version of 'From Here to Eternity') so we can find any overlapping performer.
- anchors: Third Person, Third Person (film), From Here to Eternity, From Here to Eternity (1953 film), From Here to Eternity (miniseries), cast, Deborah Kerr, Donna Reed
- bridge_clues: cast, starring, credited, filmography, appeared in, played
- noisy_or_distracting_clues: From Here to Eternity (disambiguation), From Here to Eternity (TV series), Kim Basinger, Heather O'Rourke
- expected_evidence_type: Primary film pages or reliable cast lists (Wikipedia film pages, IMDb/filmography entries, reputable biographies) showing full credited cast for each title/version.
- query_shape_implication: Issue two precise second-hop queries (exact title + 'cast' or year): e.g. 'Third Person (film) cast' and 'From Here to Eternity (1953 film) cast' (or 'From Here to Eternity (1979 miniseries) cast' if that version is intended), then intersect named cast members.

---

### 140__split0__seg0__right

- idx: 140
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.87
- why_larger: Segment A starts from a narrow, Danzer-specific verification state (single-hop check whether George Danzer is a WPT champion) and must expand to a full entity search: find the correct WPT champion with four WSOP bracelets and then retrieve that person's birth date. Segment B's from-state already contains the broader multi-step retrieval intent (includes birth date and WPT-champion disambiguation), so A requires a larger change in retrieval focus and evidence type.

**Question**

When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: George Danzer World Poker Tour champion OR "List of World Poker Tour champions" "four World Series of Poker bracelets" birth date São Paulo
- retrieved_titles: George Danzer, World Poker Tour, World Poker Tour bracelet, Ron Rose, Alexandre Gomes, David Chiu (poker player), James Dempsey (poker player)
- retrieval_focus: Confirm which World Poker Tour (WPT) champion matches the description 'winner of the series started in 2002 by Steven Lipscomb' who 'has also won four WSOP bracelets', and retrieve that person's birth date (place and date).
- anchors: World Poker Tour, Steven Lipscomb, winner, List of World Poker Tour champions, George Danzer, four World Series of Poker bracelets, birth date, São Paulo, 17 July 1983
- bridge_clues: List of World Poker Tour champions, WPT champion + name, George Danzer biography, WPT winners list George Danzer, WPT event winner page
- noisy_or_distracting_clues: David Chiu (five WSOP bracelets) — similar name overlap on retrieved list, Ron Rose, Alexandre Gomes, James Dempsey — other WPT names, "World Poker Tour bracelet" (misleading phrase), pages about WPT events rather than person biographies
- expected_evidence_type: Authoritative WPT winners list or tournament page linking the winner's name, plus a biographical page (e.g., Wikipedia or official profile) that states the person's birth date and place.
- query_shape_implication: Two-step conjunctive retrieval: (a) find WPT champions list or event page that names the winner; (b) find the named person's biography to extract birth date. Queries should combine 'List of World Poker Tour champions' OR 'WPT champion' with the candidate name or 'four WSOP bracelets' to disambiguate from other winners.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: George Danzer, World Poker Tour bracelet, World Poker Tour, Ron Rose, Alexandre Gomes, David Chiu (poker player), John Hennigan (poker player)
- retrieval_focus: Confirm which World Poker Tour (WPT) champion also has four WSOP bracelets and retrieve that person's birth date; verify whether George Danzer is the correct WPT winner candidate.
- anchors: World Poker Tour (WPT) — series started 2002 by Steven Lipscomb, four World Series of Poker (WSOP) bracelets, WPT winner / list of WPT champions, George Danzer (candidate from summary_1)
- bridge_clues: Summary_1 identifies George Danzer as a four-time WSOP bracelet winner, Summary_1 lists World Poker Tour as the series referenced by the question, Need explicit link: 'George Danzer' <-> 'won a WPT event' (or find alternative WPT champion with 4 WSOP bracelets)
- noisy_or_distracting_clues: Retrieved title 'World Poker Tour bracelet' (mixed terminology conflating WPT and WSOP), David Chiu appears in results but has five WSOP bracelets per summary_1 (wrong bracelet count for target), Other retrieved names (Ron Rose, Alexandre Gomes, John Hennigan) that may be unrelated
- expected_evidence_type: Biographical page or authoritative WPT champions list that explicitly ties the person to a WPT title, lists number of WSOP bracelets, and gives the birth date.
- query_shape_implication: Second-hop should be entity-centric: search for 'X World Poker Tour winner four WSOP bracelets birth date' or 'George Danzer World Poker Tour' or 'List of World Poker Tour champions' and then follow to the person's biography to extract birth date.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Verify whether the candidate George Danzer is a World Poker Tour (WPT) champion (i.e., appears on a WPT winners/champions list or tournament-results page). If he is not, identify any WPT champion who has four World Series of Poker bracelets.
- anchors: George Danzer, List of World Poker Tour champions, World Poker Tour winner, four World Series of Poker bracelets, WPT winners list, tournament results page
- bridge_clues: Search for 'George Danzer World Poker Tour' or 'George Danzer WPT' to find any explicit link between Danzer and a WPT title, Look up 'List of World Poker Tour champions' for the presence/absence of George Danzer, If Danzer is absent, search the WPT champions list for players with 'four WSOP bracelets' to find the correct cross-over candidate
- noisy_or_distracting_clues: Pages that discuss George Danzer's WSOP bracelets and achievements but do not mention WPT results (may falsely suggest a WPT link), Other player names on WPT lists (David Chiu, John Hennigan, Alexandre Gomes, etc.) that have different bracelet counts, Articles conflating WPT event wins with WSOP bracelets or using imprecise phrasing ('World Poker Tour bracelet'), Local event reports or forums that mention wins but are not authoritative
- expected_evidence_type: A WPT champions/winners list or official tournament-results page naming the winner(s) (positive evidence that Danzer did or did not win a WPT event), or an authoritative biography that explicitly states WPT titles (or their absence).
- query_shape_implication: Single-hop verification query: 'George Danzer WPT' or 'George Danzer "World Poker Tour"'; if negative, follow-up single-hop: 'List of World Poker Tour champions + "four World Series of Poker bracelets"' to find a different matching champion.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: George Danzer, World Poker Tour bracelet, World Poker Tour, Ron Rose, Alexandre Gomes, David Chiu (poker player), John Hennigan (poker player)
- retrieval_focus: Confirm which World Poker Tour (WPT) champion also has four WSOP bracelets and retrieve that person's birth date; verify whether George Danzer is the correct WPT winner candidate.
- anchors: World Poker Tour (WPT) — series started 2002 by Steven Lipscomb, four World Series of Poker (WSOP) bracelets, WPT winner / list of WPT champions, George Danzer (candidate from summary_1)
- bridge_clues: Summary_1 identifies George Danzer as a four-time WSOP bracelet winner, Summary_1 lists World Poker Tour as the series referenced by the question, Need explicit link: 'George Danzer' <-> 'won a WPT event' (or find alternative WPT champion with 4 WSOP bracelets)
- noisy_or_distracting_clues: Retrieved title 'World Poker Tour bracelet' (mixed terminology conflating WPT and WSOP), David Chiu appears in results but has five WSOP bracelets per summary_1 (wrong bracelet count for target), Other retrieved names (Ron Rose, Alexandre Gomes, John Hennigan) that may be unrelated
- expected_evidence_type: Biographical page or authoritative WPT champions list that explicitly ties the person to a WPT title, lists number of WSOP bracelets, and gives the birth date.
- query_shape_implication: Second-hop should be entity-centric: search for 'X World Poker Tour winner four WSOP bracelets birth date' or 'George Danzer World Poker Tour' or 'List of World Poker Tour champions' and then follow to the person's biography to extract birth date.

---

### 140__split1__seg1__right

- idx: 140
- split_iter: 1
- task_kind: right_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.74
- why_larger: Segment B moves from a shortlist-only, cross-referencing phase (scan WPT winners and filter by WSOP bracelet counts) to a final verification plus extracting the person's birth date. This adds a new retrieval target (a date) and requires resolving a bridge relation across multiple candidate entities before selecting the final subject—a larger change in retrieval focus and required evidence than A, which was already centered on verifying Danzer and only modestly extended to fetch a birth date.

**Question**

When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Verify whether the candidate George Danzer is a World Poker Tour (WPT) champion (i.e., appears on a WPT winners/champions list or tournament-results page). If he is not, identify any WPT champion who has four World Series of Poker bracelets.
- anchors: George Danzer, List of World Poker Tour champions, World Poker Tour winner, four World Series of Poker bracelets, WPT winners list, tournament results page
- bridge_clues: Search for 'George Danzer World Poker Tour' or 'George Danzer WPT' to find any explicit link between Danzer and a WPT title, Look up 'List of World Poker Tour champions' for the presence/absence of George Danzer, If Danzer is absent, search the WPT champions list for players with 'four WSOP bracelets' to find the correct cross-over candidate
- noisy_or_distracting_clues: Pages that discuss George Danzer's WSOP bracelets and achievements but do not mention WPT results (may falsely suggest a WPT link), Other player names on WPT lists (David Chiu, John Hennigan, Alexandre Gomes, etc.) that have different bracelet counts, Articles conflating WPT event wins with WSOP bracelets or using imprecise phrasing ('World Poker Tour bracelet'), Local event reports or forums that mention wins but are not authoritative
- expected_evidence_type: A WPT champions/winners list or official tournament-results page naming the winner(s) (positive evidence that Danzer did or did not win a WPT event), or an authoritative biography that explicitly states WPT titles (or their absence).
- query_shape_implication: Single-hop verification query: 'George Danzer WPT' or 'George Danzer "World Poker Tour"'; if negative, follow-up single-hop: 'List of World Poker Tour champions + "four World Series of Poker bracelets"' to find a different matching champion.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: George Danzer, World Poker Tour bracelet, World Poker Tour, Ron Rose, Alexandre Gomes, David Chiu (poker player), John Hennigan (poker player)
- retrieval_focus: Confirm which World Poker Tour (WPT) champion also has four WSOP bracelets and retrieve that person's birth date; verify whether George Danzer is the correct WPT winner candidate.
- anchors: World Poker Tour (WPT) — series started 2002 by Steven Lipscomb, four World Series of Poker (WSOP) bracelets, WPT winner / list of WPT champions, George Danzer (candidate from summary_1)
- bridge_clues: Summary_1 identifies George Danzer as a four-time WSOP bracelet winner, Summary_1 lists World Poker Tour as the series referenced by the question, Need explicit link: 'George Danzer' <-> 'won a WPT event' (or find alternative WPT champion with 4 WSOP bracelets)
- noisy_or_distracting_clues: Retrieved title 'World Poker Tour bracelet' (mixed terminology conflating WPT and WSOP), David Chiu appears in results but has five WSOP bracelets per summary_1 (wrong bracelet count for target), Other retrieved names (Ron Rose, Alexandre Gomes, John Hennigan) that may be unrelated
- expected_evidence_type: Biographical page or authoritative WPT champions list that explicitly ties the person to a WPT title, lists number of WSOP bracelets, and gives the birth date.
- query_shape_implication: Second-hop should be entity-centric: search for 'X World Poker Tour winner four WSOP bracelets birth date' or 'George Danzer World Poker Tour' or 'List of World Poker Tour champions' and then follow to the person's biography to extract birth date.

**Sub segment**

from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Cross-reference the World Poker Tour (WPT) champions list with authoritative player bios or summaries of WSOP bracelet counts to produce a short list of WPT winners who have four World Series of Poker bracelets (or otherwise match the 'four WSOP bracelets' criterion). Do NOT yet retrieve birth dates—only identify candidate person(s) to check next.
- anchors: World Poker Tour champions list / WPT winners, players with four World Series of Poker (WSOP) bracelets, George Danzer, David Chiu, John Hennigan, Alexandre Gomes
- bridge_clues: Scan an official or well-sourced 'List of World Poker Tour champions' page to extract WPT winner names., For each extracted WPT winner, consult their biographical entry or WSOP records to note their WSOP bracelet count (look for phrases like 'x-time World Series of Poker bracelet winner')., Produce a shortlist of WPT winners whose bios/records state they have four WSOP bracelets (if any)., If George Danzer appears on the WPT winners list, include him in the shortlist; otherwise, exclude him and focus on other WPT winners who match the 'four bracelets' count.
- noisy_or_distracting_clues: Pages that discuss only WSOP results without indicating WPT wins (may list bracelet counts but not WPT titles)., Articles or fan sites that conflate WPT events with WSOP bracelets or use imprecise language ('World Poker Tour bracelet')., WPT winners lists that include many names (need to avoid assuming bracelet counts without checking each player's bio)., Players on WPT lists who have many WSOP-related mentions but ambiguous bracelet counts in summary lines.
- expected_evidence_type: A WPT champions/winners list (table or roster) plus one-line biographical entries or WSOP records for candidate winners indicating the number of WSOP bracelets (these should confirm which WPT winner(s), if any, have exactly four WSOP bracelets).
- query_shape_implication: Two-step single-hop pattern aggregated into this midpoint: (1) retrieve WPT winners list to get candidate names; (2) for each candidate, retrieve a brief authoritative bio or WSOP-record snippet mentioning 'X WSOP bracelet(s)' to filter to those with four. The next step (R_right) will take the shortlisted person and fetch their birth date.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: George Danzer, World Poker Tour bracelet, World Poker Tour, Ron Rose, Alexandre Gomes, David Chiu (poker player), John Hennigan (poker player)
- retrieval_focus: Confirm which World Poker Tour (WPT) champion also has four WSOP bracelets and retrieve that person's birth date; verify whether George Danzer is the correct WPT winner candidate.
- anchors: World Poker Tour (WPT) — series started 2002 by Steven Lipscomb, four World Series of Poker (WSOP) bracelets, WPT winner / list of WPT champions, George Danzer (candidate from summary_1)
- bridge_clues: Summary_1 identifies George Danzer as a four-time WSOP bracelet winner, Summary_1 lists World Poker Tour as the series referenced by the question, Need explicit link: 'George Danzer' <-> 'won a WPT event' (or find alternative WPT champion with 4 WSOP bracelets)
- noisy_or_distracting_clues: Retrieved title 'World Poker Tour bracelet' (mixed terminology conflating WPT and WSOP), David Chiu appears in results but has five WSOP bracelets per summary_1 (wrong bracelet count for target), Other retrieved names (Ron Rose, Alexandre Gomes, John Hennigan) that may be unrelated
- expected_evidence_type: Biographical page or authoritative WPT champions list that explicitly ties the person to a WPT title, lists number of WSOP bracelets, and gives the birth date.
- query_shape_implication: Second-hop should be entity-centric: search for 'X World Poker Tour winner four WSOP bracelets birth date' or 'George Danzer World Poker Tour' or 'List of World Poker Tour champions' and then follow to the person's biography to extract birth date.

---

### 149__split1__seg0__right

- idx: 149
- split_iter: 1
- task_kind: right_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.86
- why_larger: Segment B introduces a substantive new retrieval goal: it moves from verifying name-root/role (hulder ← huld; Huld as völva) to additionally asserting and sourcing the explicit identity link Huld ↔ Holda/Frau Holle and the claim that hulder is originally the same being as Huld. This is a larger conceptual/bridge addition than A’s primarily precision-focused narrowing of query shape and source type.

**Question**

A mythical forest creature that is seductive and from Sweden has the same being as what divine figure?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Huld völva Holda Holle Germanic goddess origin of hulder skogsrå Tallemaja
- retrieved_titles: Hulder, Holda, Huld, Spillaholle, Gussy Holl, 872 Holda, Frau Holle
- retrieval_focus: Find authoritative statements and etymological evidence that equate the Swedish seductive forest-creature hulder (skogsrå) with the völva/divine figure Huld and the Germanic Holda/Frau Holle; confirm role shift from goddess/seer to folkloric forest spirit.
- anchors: Huld, Holda, Frau Holle, Hulder, Skogsrå, Völva, Tallemaja
- bridge_clues: hulder derives from Huld / shared name root, Huld described as a völva or divine seer, Holda/Frau Holle equated with Huld, etymology: huldr / huld = 'hidden/covered', transformation from goddess/seer to folk forest spirit, regional names linking hulder to Huld (skogsrå, Tallemaja, ulda)
- noisy_or_distracting_clues: Spillaholle, Gussy Holl, 872 Holda
- expected_evidence_type: encyclopedic or folklore entries and comparative-mythology or etymology discussions that explicitly link the names (Huld/Holda) to hulder/skogsrå and describe religious/functional equivalence (völva/goddess → forest spirit).
- query_shape_implication: Multi-term, synonym-rich query: combine exact name variants with role/etymology terms (e.g., 'Huld völva etymology', 'hulder origin Huld Holda', 'skogsrå Huld Holda') and prefer scholarly/encyclopedic sources to avoid unrelated hits.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow search to authoritative etymology and comparative-mythology statements that explicitly link the Swedish hulder/skogsrå name to Huld and show Huld's identification with Holda/Frau Holle; prioritize encyclopedia/folklore/etymology entries that give short identity claims rather than broader cultural history.
- anchors: Hulder, Huld, Holda, Skogsrå, Völva, Frau Holle
- bridge_clues: etymology: huldr / huld = 'hidden/covered' as name-root connection, explicit sentence: 'the hulder is originally the same being as Huld', scholarly/encyclopedic note equating Huld with Holda/Frau Holle, regional name citations (Tallemaja, ulda) used in etymology or name-history sections
- noisy_or_distracting_clues: Coat of arms of Lardal, 872 Holda, Haugtussa, Spillaholle, Gussy Holl
- expected_evidence_type: Short definitional or etymological passages in encyclopedia/folklore/dictionary entries or comparative-mythology summaries that state name-derivation and identity (e.g., a line that directly links hulder → Huld and Huld ↔ Holda/Frau Holle).
- query_shape_implication: Concise high-precision pairwise queries combining the folkloric term and candidate divine names with relationship keywords (examples to guide retrieval: 'hulder Huld etymology', 'hulder same as Holda', 'Huld völva Holda identity'), focusing on authoritative sources.

**Sub segment**

from_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Establish the philological/etymological link from Swedish hulder/skogsrå to the name-root huld/huldr and confirm Huld's characterization as a völva/seer in sources. This narrows the search to name-origin and role-of-Huld material without yet asserting or heavily sourcing the Huld↔Holda/Frau Holle equation.
- anchors: Hulder, Skogsrå, Huld, Völva, huldr / huld (name-root), Tallemaja, ulda
- bridge_clues: etymology: hulder ← huldr / huld meaning 'hidden/covered' or similar, encyclopedic or dictionary lines that derive hulder/skogsrå from Huld, descriptions in folklore or Old Norse sources identifying Huld as a völva/seer, regional name citations (Tallemaja, ulda) used in name-history sections, linguistic/philological commentary tying the personal/divine name Huld to later folk-figure names
- noisy_or_distracting_clues: explicit Holda / Frau Holle articles (defer full equation to next step), local civic or heraldic pages (e.g., 'Coat of arms of Lardal'), modern cultural usages and creative retellings (e.g., 'Spillaholle', 'Gussy Holl'), catalog or list pages with numeric identifiers (e.g., '872 Holda')
- expected_evidence_type: Etymological dictionary entries, folklore encyclopaedia entries, comparative-mythology or name-origin sections that explicitly state hulder derives from huld/huldr and references or primary-source notes describing Huld as a völva/seer.
- query_shape_implication: Pair folkloric term + etymology and Huld + role keywords (examples to guide retrieval: 'hulder etymology huld', 'skogsrå huldr root', 'Huld völva sources'); favor linguistic/etymological and folklore-reference pages rather than broad cultural histories or explicit Huld↔Holda identity claims.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow search to authoritative etymology and comparative-mythology statements that explicitly link the Swedish hulder/skogsrå name to Huld and show Huld's identification with Holda/Frau Holle; prioritize encyclopedia/folklore/etymology entries that give short identity claims rather than broader cultural history.
- anchors: Hulder, Huld, Holda, Skogsrå, Völva, Frau Holle
- bridge_clues: etymology: huldr / huld = 'hidden/covered' as name-root connection, explicit sentence: 'the hulder is originally the same being as Huld', scholarly/encyclopedic note equating Huld with Holda/Frau Holle, regional name citations (Tallemaja, ulda) used in etymology or name-history sections
- noisy_or_distracting_clues: Coat of arms of Lardal, 872 Holda, Haugtussa, Spillaholle, Gussy Holl
- expected_evidence_type: Short definitional or etymological passages in encyclopedia/folklore/dictionary entries or comparative-mythology summaries that state name-derivation and identity (e.g., a line that directly links hulder → Huld and Huld ↔ Holda/Frau Holle).
- query_shape_implication: Concise high-precision pairwise queries combining the folkloric term and candidate divine names with relationship keywords (examples to guide retrieval: 'hulder Huld etymology', 'hulder same as Holda', 'Huld völva Holda identity'), focusing on authoritative sources.

---

### 149__split3__seg2__right

- idx: 149
- split_iter: 3
- task_kind: right_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: bridge_relation
- confidence: 0.8
- why_larger: Segment B shifts from a broad, primary-source and motif-focused retrieval (documenting attestations of Huld/Huldr and Holda/Frau Holle and their overlapping traits) to a narrow, high‑precision demand for authoritative etymological and encyclopedic identity statements linking hulder → Huld and Huld ↔ Holda. That is a bigger change in retrieval focus and evidence-family (from gathering parallels/attestations to seeking explicit equivalence claims) than A, which was already moving toward comparative-mythology evidence connecting Huld and Holda and only refines to authoritative identity statements.

**Question**

A mythical forest creature that is seductive and from Sweden has the same being as what divine figure?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter3_split1
- kind: generated_midpoint
- retrieval_focus: Move from establishing hulder ← huld name-origin and Huld's role as a völva (R_left) toward comparative-mythology evidence that connects the name/figure Huld with the Germanic Holda/Frau Holle, without yet asserting a definitive identity. Look for sources that discuss cognate names, cross‑regional parallels, and scholarly claims that Huld and Holda/Frau Holle are related or derived from a common archetype.
- anchors: Hulder, Huld, Holda / Hold(e)a, Frau Holle, name cognates / etymology, comparative mythology
- bridge_clues: scholarly/comparative-mythology statements noting Huld and Holda as cognate or analogous figures, etymological notes showing Huld/Huldr and Holda/Holda share a root or semantic field (e.g., 'hidden', 'cover') or are treated as related names, encyclopaedia or folklore reference paragraphs that link Huld to Germanic Holda without full summary claims, comparisons of attributes/roles (seeress, household/fertility/witchy associations) used to argue a common origin, medieval or early-modern source citations where Huld/Holda appear in analogous contexts
- noisy_or_distracting_clues: modern pop-culture retellings or novels using 'Huld'/'Holda' names, local civic heraldry or municipal pages invoking similar names, unrelated personal names or catalog entries containing 'Holda' as an identifier, lists of folklore motifs that mention many superficially similar names without etymological linking
- expected_evidence_type: Comparative-mythology discussions, etymological dictionary entries that propose cognacy or close relation between Huld/Huldr and Holda/Holda, encyclopedia/folklore reference passages that present Huld↔Holda as a scholarly hypothesis or parallel (not necessarily a definitive equivalence), and citations of primary medieval references showing both names in related roles.
- query_shape_implication: Combine Huld/Huldr with Holda/Holda/Frau Holle using relation keywords (examples to guide retrieval: 'Huld Holda cognate', 'Huld Frau Holle comparative mythology', 'huldr holda etymology', 'Huld Holda parallels medieval sources'); favor comparative-mythology and etymology sources that evaluate the relationship rather than single-language name origins or purely local hulder tales.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow search to authoritative etymology and comparative-mythology statements that explicitly link the Swedish hulder/skogsrå name to Huld and show Huld's identification with Holda/Frau Holle; prioritize encyclopedia/folklore/etymology entries that give short identity claims rather than broader cultural history.
- anchors: Hulder, Huld, Holda, Skogsrå, Völva, Frau Holle
- bridge_clues: etymology: huldr / huld = 'hidden/covered' as name-root connection, explicit sentence: 'the hulder is originally the same being as Huld', scholarly/encyclopedic note equating Huld with Holda/Frau Holle, regional name citations (Tallemaja, ulda) used in etymology or name-history sections
- noisy_or_distracting_clues: Coat of arms of Lardal, 872 Holda, Haugtussa, Spillaholle, Gussy Holl
- expected_evidence_type: Short definitional or etymological passages in encyclopedia/folklore/dictionary entries or comparative-mythology summaries that state name-derivation and identity (e.g., a line that directly links hulder → Huld and Huld ↔ Holda/Frau Holle).
- query_shape_implication: Concise high-precision pairwise queries combining the folkloric term and candidate divine names with relationship keywords (examples to guide retrieval: 'hulder Huld etymology', 'hulder same as Holda', 'Huld völva Holda identity'), focusing on authoritative sources.

**Sub segment**

from_state:
- name: Rmid_iter4_split2
- kind: generated_midpoint
- retrieval_focus: Find intermediate comparative-material that documents historical attestations and characteristic attributes of the name/figure Huld (Huldr) in Old Norse/Scandinavian sources and separately of Holda/Frau Holle in Germanic tradition, emphasizing overlapping roles/traits (seeress/witchcraft, household/fertility associations, 'hidden' semantics) and noting proposed name-form parallels without demanding an explicit one-line identification. Prioritize sources that present parallels and possible cognacy as a scholarly hypothesis or list of shared motifs rather than definitive encyclopedic identity statements.
- anchors: Huld / Huldr (attestations, Old Norse mentions), Hulder / skogsrå (Swedish folkloric descriptions), Holda / Hold(e)a / Frau Holle (Germanic tradition summaries), völva / seiðr (roles and practices), name-form variants and semantic field ('huld' = hidden/covered)
- bridge_clues: medieval/early-modern passages that mention a named Huld or Huldr acting as seeress, sorceress, or forest spirit, folklore compendia entries that compare attributes of hulder/skogsrå tales with Holda/Frau Holle motifs (e.g., household guardianship, nocturnal processions, witchcraft, gift/reward patterns), etymological notes that list the huld- root across Germanic languages and suggest semantic overlap (e.g., 'hidden, covered, gracious') without asserting full cognacy, comparative-mythology paragraphs that frame Huld and Holda as parallel figures in scholarship, presenting arguments and counterarguments, citations to primary sources or saga/chronicle passages where Huld/Huldr appears, and to Germanic folklore collections describing Holda/Frau Holle
- noisy_or_distracting_clues: modern novels, songs, or games using 'Huld'/'Holda' as character names, astronomical/object names (e.g., asteroid '872 Holda'), municipal or heraldic pages referencing local legends, databases or indexes that list many superficially similar folklore names without commentary, personal names, businesses, or unrelated species named 'Holda' or 'Huld'
- expected_evidence_type: Middle-tier comparative material: folklore encyclopedia paragraphs, scholarly articles or book chapters discussing motif overlap, primary-source quotes (saga/chronicle excerpts) showing Huld/Huldr occurrences, and etymological dictionary notes that point to shared huld- roots or semantic fields—materials that support a hypothesized link but stop short of a single definitive identity claim.
- query_shape_implication: Search for pairwise and motif-focused phrases that join attestations and attributes rather than asking for definitive equivalence (examples to guide retrieval: 'Huld saga attestation', 'Huldr völva seiðr sources', 'Huld Holda parallels motifs', 'huldr huld root Germanic semantics', 'skogsrå Holda comparison folklore'), favoring sources that enumerate parallels, primary citations, or cautious scholarly hypotheses.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow search to authoritative etymology and comparative-mythology statements that explicitly link the Swedish hulder/skogsrå name to Huld and show Huld's identification with Holda/Frau Holle; prioritize encyclopedia/folklore/etymology entries that give short identity claims rather than broader cultural history.
- anchors: Hulder, Huld, Holda, Skogsrå, Völva, Frau Holle
- bridge_clues: etymology: huldr / huld = 'hidden/covered' as name-root connection, explicit sentence: 'the hulder is originally the same being as Huld', scholarly/encyclopedic note equating Huld with Holda/Frau Holle, regional name citations (Tallemaja, ulda) used in etymology or name-history sections
- noisy_or_distracting_clues: Coat of arms of Lardal, 872 Holda, Haugtussa, Spillaholle, Gussy Holl
- expected_evidence_type: Short definitional or etymological passages in encyclopedia/folklore/dictionary entries or comparative-mythology summaries that state name-derivation and identity (e.g., a line that directly links hulder → Huld and Huld ↔ Holda/Frau Holle).
- query_shape_implication: Concise high-precision pairwise queries combining the folkloric term and candidate divine names with relationship keywords (examples to guide retrieval: 'hulder Huld etymology', 'hulder same as Holda', 'Huld völva Holda identity'), focusing on authoritative sources.

---

### 150__split3__seg0__right

- idx: 150
- split_iter: 3
- task_kind: right_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.78
- why_larger: Segment B changes retrieval focus more substantially: it goes from targeting only the 2012 season-page lead to adding the coach/bio/program pages (introducing Paul Winters as an explicit new anchor and adding the bridge evidence needed to link team→coach→university). Segment A is mainly a refinement/narrowing of an already multi-page focus, not the addition of a new anchor or evidence family.

**Question**

What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Paul Winters biography Wayne State University head coach Wayne State Warriors football program history Tom Adams Field GLIAC Detroit
- retrieved_titles: 2012 Wayne State Warriors football team, 2016 Wayne State Warriors football team, 2017 Wayne State Warriors football team, Wayne State Warriors football, 1975 Wayne State Tartars football team, Wayne State Warriors, 1977 Wayne State Tartars football team
- retrieval_focus: Identify the university that both the 2012 Wayne State Warriors football team and coach Paul Winters are affiliated with (the institution named on team and coach pages).
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State University, Wayne State Warriors, Tom Adams Field, GLIAC
- bridge_clues: team 'represented Wayne State University' (season page language tying team to institution), Paul Winters described as head coach of the Wayne State Warriors, coach/team affiliation language (head coach of X university's program), phrases linking program name to university name
- noisy_or_distracting_clues: other season pages (2016, 2017) that mention Winters' later years — temporal noise, older season pages (1975, 1977) irrelevant to 2012 or coach biography, general Wayne State Warriors page may be broader/ambiguous, Wayne State Tartars historical naming could cause confusion
- expected_evidence_type: Authoritative team season page or coach biography that explicitly states the university affiliation (e.g., 'represented Wayne State University' on the 2012 team page or 'head coach at Wayne State University' on Winters' bio).
- query_shape_implication: Use short, entity-centered queries that combine coach + university or team + university (e.g., 'Paul Winters Wayne State University', '2012 Wayne State Warriors represented Wayne State University') to surface pages with explicit affiliation; avoid queries that emphasize other seasons or historical names.

to_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Target retrieval of the two primary pages likely to contain affiliation statements: the 2012 Wayne State Warriors season page and Paul Winters' coach/bio or team staff page (or the program overview) so their lead sentences can be inspected.
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State Warriors, Wayne State University
- bridge_clues: season page lead sentence that ties the team to a university, coach/bio line identifying Paul Winters as head coach of the Warriors, program overview or roster/staff page that maps 'Wayne State Warriors' to 'Wayne State University'
- noisy_or_distracting_clues: other season pages (2011, 2016, 2017) referencing Winters' tenure, stadium/venue details (Tom Adams Field) that are not affiliation statements, conference and NCAA division information (GLIAC, Division II), historical names (Wayne State Tartars) and unrelated older seasons
- expected_evidence_type: Short, authoritative lead lines or first-paragraph snippets on the season page and coach bio explicitly naming Wayne State University as the institution affiliated with the team and the coach.
- query_shape_implication: Favor title-targeted retrieval that surfaces the season page and the coach/bio page and prioritize lead-paragraph/snippet hits; avoid broad or multi-season queries so the next step can verify exact affiliation text.

**Sub segment**

from_state:
- name: Rmid_iter4_split0
- kind: generated_midpoint
- retrieval_focus: Narrow to the 2012 Wayne State Warriors football team season page first — retrieve its lead/first-paragraph text that ties the team to Wayne State University and names the head coach; this is a smaller step toward also retrieving the coach bio page.
- anchors: 2012 Wayne State Warriors football team, Wayne State University, season page lead, head coach (Paul Winters), Tom Adams Field
- bridge_clues: season page lead sentence that states the team represented Wayne State University, explicit mention of the head coach on the season page (Paul Winters), phrases mapping 'Wayne State Warriors' to 'Wayne State University' in the first paragraph
- noisy_or_distracting_clues: other season pages (2011, 2016, 2017) that mention Winters' tenure, stadium/venue details (Tom Adams Field) that don't change institution affiliation, conference and NCAA division details (GLIAC, Division II), historical naming (Wayne State Tartars) and unrelated older seasons
- expected_evidence_type: Lead-paragraph snippet from the 2012 season page explicitly stating the team represented Wayne State University and naming Paul Winters as head coach.
- query_shape_implication: Use a title-targeted, season-page-focused retrieval (terms referencing the 2012 season page and lead/first paragraph) rather than broad coach- or program-wide queries, so the next step can add the coach bio page with minimal change.

to_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Target retrieval of the two primary pages likely to contain affiliation statements: the 2012 Wayne State Warriors season page and Paul Winters' coach/bio or team staff page (or the program overview) so their lead sentences can be inspected.
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State Warriors, Wayne State University
- bridge_clues: season page lead sentence that ties the team to a university, coach/bio line identifying Paul Winters as head coach of the Warriors, program overview or roster/staff page that maps 'Wayne State Warriors' to 'Wayne State University'
- noisy_or_distracting_clues: other season pages (2011, 2016, 2017) referencing Winters' tenure, stadium/venue details (Tom Adams Field) that are not affiliation statements, conference and NCAA division information (GLIAC, Division II), historical names (Wayne State Tartars) and unrelated older seasons
- expected_evidence_type: Short, authoritative lead lines or first-paragraph snippets on the season page and coach bio explicitly naming Wayne State University as the institution affiliated with the team and the coach.
- query_shape_implication: Favor title-targeted retrieval that surfaces the season page and the coach/bio page and prioritize lead-paragraph/snippet hits; avoid broad or multi-season queries so the next step can verify exact affiliation text.

---

## tie_or_invalid_fail (11 total, showing 8)

### 150__split1__seg0__left

- idx: 150
- split_iter: 1
- task_kind: left_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.73
- why_larger: Both segments make nearly identical, minimal refinements to the retrieval focus: target the 2012 season page and Paul Winters' bio to surface explicit affiliation lines. Neither introduces a new anchor, corrects a noisy entity, changes the bridge relation, or alters answerability — only minor wording differences about prioritizing lead-paragraph hits. No local order preference is justified.

**Question**

What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Paul Winters biography Wayne State University head coach Wayne State Warriors football program history Tom Adams Field GLIAC Detroit
- retrieved_titles: 2012 Wayne State Warriors football team, 2016 Wayne State Warriors football team, 2017 Wayne State Warriors football team, Wayne State Warriors football, 1975 Wayne State Tartars football team, Wayne State Warriors, 1977 Wayne State Tartars football team
- retrieval_focus: Identify the university that both the 2012 Wayne State Warriors football team and coach Paul Winters are affiliated with (the institution named on team and coach pages).
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State University, Wayne State Warriors, Tom Adams Field, GLIAC
- bridge_clues: team 'represented Wayne State University' (season page language tying team to institution), Paul Winters described as head coach of the Wayne State Warriors, coach/team affiliation language (head coach of X university's program), phrases linking program name to university name
- noisy_or_distracting_clues: other season pages (2016, 2017) that mention Winters' later years — temporal noise, older season pages (1975, 1977) irrelevant to 2012 or coach biography, general Wayne State Warriors page may be broader/ambiguous, Wayne State Tartars historical naming could cause confusion
- expected_evidence_type: Authoritative team season page or coach biography that explicitly states the university affiliation (e.g., 'represented Wayne State University' on the 2012 team page or 'head coach at Wayne State University' on Winters' bio).
- query_shape_implication: Use short, entity-centered queries that combine coach + university or team + university (e.g., 'Paul Winters Wayne State University', '2012 Wayne State Warriors represented Wayne State University') to surface pages with explicit affiliation; avoid queries that emphasize other seasons or historical names.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Confirm explicit, on-page affiliation lines that tie the 2012 Wayne State Warriors season and coach Paul Winters to Wayne State University (look for the short phrases on the season page and coach bio/team page).
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State University, Tom Adams Field
- bridge_clues: the 2012 team 'represented Wayne State University' (season-page affiliation sentence), Paul Winters listed as 'head coach' of the Wayne State Warriors, program affiliation language linking 'Wayne State Warriors' to 'Wayne State University'
- noisy_or_distracting_clues: other season pages and years (2011, 2016, 2017, etc.) that mention Winters' tenure, stadium and venue details (Tom Adams Field), conference or NCAA division information (GLIAC, Division II), coach year counts (7th, 13th/14th) and prior positions
- expected_evidence_type: Two short authoritative lines: one on the 2012 season page stating the team represented Wayne State University, and one on the coach page or team roster/bio stating Paul Winters is head coach at Wayne State University.
- query_shape_implication: Use compact, phrase-focused queries that surface exact affiliation lines (e.g., '2012 Wayne State Warriors represented Wayne State University' and 'Paul Winters head coach Wayne State University') rather than long historical or broad program queries.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Paul Winters biography Wayne State University head coach Wayne State Warriors football program history Tom Adams Field GLIAC Detroit
- retrieved_titles: 2012 Wayne State Warriors football team, 2016 Wayne State Warriors football team, 2017 Wayne State Warriors football team, Wayne State Warriors football, 1975 Wayne State Tartars football team, Wayne State Warriors, 1977 Wayne State Tartars football team
- retrieval_focus: Identify the university that both the 2012 Wayne State Warriors football team and coach Paul Winters are affiliated with (the institution named on team and coach pages).
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State University, Wayne State Warriors, Tom Adams Field, GLIAC
- bridge_clues: team 'represented Wayne State University' (season page language tying team to institution), Paul Winters described as head coach of the Wayne State Warriors, coach/team affiliation language (head coach of X university's program), phrases linking program name to university name
- noisy_or_distracting_clues: other season pages (2016, 2017) that mention Winters' later years — temporal noise, older season pages (1975, 1977) irrelevant to 2012 or coach biography, general Wayne State Warriors page may be broader/ambiguous, Wayne State Tartars historical naming could cause confusion
- expected_evidence_type: Authoritative team season page or coach biography that explicitly states the university affiliation (e.g., 'represented Wayne State University' on the 2012 team page or 'head coach at Wayne State University' on Winters' bio).
- query_shape_implication: Use short, entity-centered queries that combine coach + university or team + university (e.g., 'Paul Winters Wayne State University', '2012 Wayne State Warriors represented Wayne State University') to surface pages with explicit affiliation; avoid queries that emphasize other seasons or historical names.

to_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Target retrieval of the two primary pages likely to contain affiliation statements: the 2012 Wayne State Warriors season page and Paul Winters' coach/bio or team staff page (or the program overview) so their lead sentences can be inspected.
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State Warriors, Wayne State University
- bridge_clues: season page lead sentence that ties the team to a university, coach/bio line identifying Paul Winters as head coach of the Warriors, program overview or roster/staff page that maps 'Wayne State Warriors' to 'Wayne State University'
- noisy_or_distracting_clues: other season pages (2011, 2016, 2017) referencing Winters' tenure, stadium/venue details (Tom Adams Field) that are not affiliation statements, conference and NCAA division information (GLIAC, Division II), historical names (Wayne State Tartars) and unrelated older seasons
- expected_evidence_type: Short, authoritative lead lines or first-paragraph snippets on the season page and coach bio explicitly naming Wayne State University as the institution affiliated with the team and the coach.
- query_shape_implication: Favor title-targeted retrieval that surfaces the season page and the coach/bio page and prioritize lead-paragraph/snippet hits; avoid broad or multi-season queries so the next step can verify exact affiliation text.

---

### 150__split2__seg2__right

- idx: 150
- split_iter: 2
- task_kind: right_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.85
- why_larger: Both segments show effectively the same retrieval-focus update: moving from a midpoint plan to fetching the canonical team and coach pages to confirm a short affiliation line linking both to Wayne State University. Anchors, bridge clues, noisy clues, expected evidence type, and query-shape implications are functionally identical, so neither segment exhibits a clearly larger change in retrieval focus, entity correction, or answerability.

**Question**

What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Confirm explicit, on-page affiliation lines that tie the 2012 Wayne State Warriors season and coach Paul Winters to Wayne State University (look for the short phrases on the season page and coach bio/team page).
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State University, Tom Adams Field
- bridge_clues: the 2012 team 'represented Wayne State University' (season-page affiliation sentence), Paul Winters listed as 'head coach' of the Wayne State Warriors, program affiliation language linking 'Wayne State Warriors' to 'Wayne State University'
- noisy_or_distracting_clues: other season pages and years (2011, 2016, 2017, etc.) that mention Winters' tenure, stadium and venue details (Tom Adams Field), conference or NCAA division information (GLIAC, Division II), coach year counts (7th, 13th/14th) and prior positions
- expected_evidence_type: Two short authoritative lines: one on the 2012 season page stating the team represented Wayne State University, and one on the coach page or team roster/bio stating Paul Winters is head coach at Wayne State University.
- query_shape_implication: Use compact, phrase-focused queries that surface exact affiliation lines (e.g., '2012 Wayne State Warriors represented Wayne State University' and 'Paul Winters head coach Wayne State University') rather than long historical or broad program queries.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: 2012 Wayne State Warriors football team, 2017 Wayne State Warriors football team, 2016 Wayne State Warriors football team, Paul Winters (American football), Wayne State Warriors football, 2011 Wayne State Warriors football team, 2008 Wayne State Warriors football team
- retrieval_focus: Find a short authoritative statement that both the 2012 Wayne State Warriors football team and Paul Winters are affiliated with the same institution (Wayne State University). Target team, coach, or university pages that state affiliation.
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State Warriors football, Wayne State University
- bridge_clues: head coach, represented Wayne State University, member of Wayne State Warriors football program, played home games at Tom Adams Field (Wayne State)
- noisy_or_distracting_clues: other season pages (2011, 2016, 2017, 2008), Tom Adams Field / stadium details, GLIAC / NCAA Division II conference info, coach years (7th, 13th/14th) and prior positions
- expected_evidence_type: Short sentences on team and coach pages stating affiliation (e.g., 'the 2012 team represented Wayne State University' and 'Paul Winters is head coach at Wayne State University' or the university's roster/affiliation line).
- query_shape_implication: Use short entity-focused queries (e.g., 'Paul Winters Wayne State University', '2012 Wayne State Warriors represented Wayne State University', or simply 'Wayne State University Wayne State Warriors') rather than long natural-language questions; prioritize pages about the coach, the 2012 team, or the university for a single canonical institution name.

**Sub segment**

from_state:
- name: Rmid_iter3_split2
- kind: generated_midpoint
- retrieval_focus: Fetch the specific pages for the 2012 Wayne State Warriors football team and the Paul Winters coach biography to extract the short affiliation lines that tie both entities to Wayne State University.
- anchors: 2012 Wayne State Warriors football team, Paul Winters (American football), Wayne State University, Wayne State Warriors football
- bridge_clues: the 2012 team 'represented Wayne State University' (season page phrasing), Paul Winters described as 'head coach' of the Wayne State Warriors on his bio/team page, team page and coach bio both mention the institutional name 'Wayne State University'
- noisy_or_distracting_clues: other season pages and years (2011, 2016, 2017, 2008), stadium/venue details (Tom Adams Field), conference and division details (GLIAC, NCAA Division II), coach tenure counts and prior positions
- expected_evidence_type: Two short authoritative lines: one from the 2012 season page stating the team represented Wayne State University, and one from the Paul Winters bio or team page stating he is head coach at Wayne State University.
- query_shape_implication: Use exact-entity/title queries that return the canonical pages (e.g., the 2012 team page and the Paul Winters bio) so the affiliation lines are visible; prefer page-title lookups rather than broad natural-language queries.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: 2012 Wayne State Warriors football team, 2017 Wayne State Warriors football team, 2016 Wayne State Warriors football team, Paul Winters (American football), Wayne State Warriors football, 2011 Wayne State Warriors football team, 2008 Wayne State Warriors football team
- retrieval_focus: Find a short authoritative statement that both the 2012 Wayne State Warriors football team and Paul Winters are affiliated with the same institution (Wayne State University). Target team, coach, or university pages that state affiliation.
- anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State Warriors football, Wayne State University
- bridge_clues: head coach, represented Wayne State University, member of Wayne State Warriors football program, played home games at Tom Adams Field (Wayne State)
- noisy_or_distracting_clues: other season pages (2011, 2016, 2017, 2008), Tom Adams Field / stadium details, GLIAC / NCAA Division II conference info, coach years (7th, 13th/14th) and prior positions
- expected_evidence_type: Short sentences on team and coach pages stating affiliation (e.g., 'the 2012 team represented Wayne State University' and 'Paul Winters is head coach at Wayne State University' or the university's roster/affiliation line).
- query_shape_implication: Use short entity-focused queries (e.g., 'Paul Winters Wayne State University', '2012 Wayne State Warriors represented Wayne State University', or simply 'Wayne State University Wayne State Warriors') rather than long natural-language questions; prioritize pages about the coach, the 2012 team, or the university for a single canonical institution name.

---

### 227__split1__seg1__right

- idx: 227
- split_iter: 1
- task_kind: right_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: mixed
- confidence: 0.75
- why_larger: Both segments perform symmetric, large retrieval shifts: A moves from comics/publisher sources to add an actor (Evan Peters) anchor and actor-focused evidence; B moves from actor/filmography sources to add publisher/comic-character evidence. Each requires adding a new evidence family and an entity-anchor/bridge relation (actor↔character↔publisher). No clear local difference justifies preferring one over the other.

**Question**

Evan Peters had a role as the fictional superhero from comic books by what publisher?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Confirm that Evan Peters specifically portrayed the character Quicksilver (Pietro Maximoff) in the X‑Men films/TV appearances by retrieving authoritative cast lists, the actor's filmography, and contemporary coverage linking Evan Peters to the Quicksilver role. Intentionally avoid comic-book publisher pages at this step.
- anchors: Evan Peters, Quicksilver, Pietro Maximoff, X‑Men: Days of Future Past, X‑Men: Apocalypse, filmography / cast list
- bridge_clues: Lead sentence or filmography section on an 'Evan Peters' page listing 'Quicksilver' among credited roles, Cast lists or credits for 'X‑Men: Days of Future Past' and 'X‑Men: Apocalypse' naming Evan Peters as Quicksilver, News articles/reviews or press releases from film releases that mention 'Evan Peters as Quicksilver' or 'Pietro Maximoff', Database entries (IMDb, official studio cast pages) showing Evan Peters credited as Quicksilver
- noisy_or_distracting_clues: Comic‑book character history pages and Marvel publisher articles (these relate to publisher step but are intentionally postponed), Pages about other Maximoff family members (Scarlet Witch, Luna Maximoff) or unrelated characters, General biographical details about Evan Peters (personal life, TV roles) that do not mention the Quicksilver role, Fan wikis or forum posts with unverified claims
- expected_evidence_type: Short authoritative lines: filmography/cast credits or reputable news/encyclopedic sentences explicitly stating 'Evan Peters portrayed Quicksilver (Pietro Maximoff)' or equivalent phrasing.
- query_shape_implication: Use narrow actor+role queries such as 'Evan Peters portrayed Quicksilver', 'Evan Peters filmography Quicksilver', or open 'Evan Peters' filmography and X‑Men cast pages. Defer queries like 'Quicksilver publisher' until after this actor->character link is confirmed.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Quicksilver (comics), Luna Maximoff, Son of M, Ultimatum (comics), Scarlet Witch, Random (comics), Evan Peters
- retrieval_focus: Confirm that the character Evan Peters portrayed is Quicksilver and that Quicksilver comics are published by Marvel Comics.
- anchors: Evan Peters, Quicksilver (comics), Marvel Comics
- bridge_clues: Evan Peters credited role links him to a comic-book character (follow-up needed to name the character), Quicksilver (comics) is a retrieved title and is a known Marvel superhero, summary_1 states the superhero role originates from American comic books published by Marvel Comics
- noisy_or_distracting_clues: Luna Maximoff / Scarlet Witch–adjacent topics (related family/characters) that could distract, Event/comic titles (Son of M, Ultimatum) and minor characters (Random) that are contextually nearby but not the target, General page 'Evan Peters' may contain many non-character details
- expected_evidence_type: Short passages or lead sentences that explicitly state 'Evan Peters portrayed Quicksilver' and/or 'Quicksilver is a fictional superhero published by Marvel Comics.'
- query_shape_implication: Entity-to-entity short query (e.g., 'Evan Peters Quicksilver' or 'Quicksilver publisher') expecting exact-name matches rather than long natural-language questions.

**Sub segment**

from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Retrieve authoritative comic‑book sources for the character Quicksilver (Pietro Maximoff) to confirm the character's publication provenance (i.e., that Quicksilver appears in American comic books published by Marvel Comics). Avoid actor filmography pages in this step — focus on the comics/character entry, infobox, and publisher lines.
- anchors: Quicksilver (comics), Pietro Maximoff, Marvel Comics, character infobox / lead sentence, publication history
- bridge_clues: Lead sentence or opening paragraph on 'Quicksilver (comics)' stating 'Quicksilver (Pietro Maximoff) is a fictional superhero appearing in American comic books published by Marvel Comics.', Infobox field or publication header listing 'Publisher: Marvel Comics' on the Quicksilver page, Short encyclopedia or database lines (e.g., Britannica/Wikipedia/comics databases) linking the character name Pietro Maximoff / Quicksilver to Marvel Comics, History or publication sections that tie Quicksilver to Marvel titles (e.g., X‑Men, Avengers appearances)
- noisy_or_distracting_clues: Movie/film pages discussing Quicksilver portrayals (MCU/20th Century Fox) that emphasize actors rather than comic publisher, Other characters with the Maximoff surname (Scarlet Witch, Luna Maximoff) that may pull retrieval toward family relations instead of publisher, Alternate continuity pages (Ultimate, MCU adaptations) or fan wikis that conflate movie rights and publisher ownership, Lists of comic events or minor characters (Son of M, Ultimatum) that are relevant context but not necessary for confirming publisher
- expected_evidence_type: Concise authoritative lines from the character/comics entry or an encyclopedia infobox explicitly naming Marvel Comics as the publisher for Quicksilver/Pietro Maximoff.
- query_shape_implication: Short entity-focused queries such as 'Quicksilver (Pietro Maximoff) publisher', 'Quicksilver comics publisher Marvel', or 'Quicksilver (comics) lead' that return the character/comics page and infobox lines; avoid actor-centric queries here.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Quicksilver (comics), Luna Maximoff, Son of M, Ultimatum (comics), Scarlet Witch, Random (comics), Evan Peters
- retrieval_focus: Confirm that the character Evan Peters portrayed is Quicksilver and that Quicksilver comics are published by Marvel Comics.
- anchors: Evan Peters, Quicksilver (comics), Marvel Comics
- bridge_clues: Evan Peters credited role links him to a comic-book character (follow-up needed to name the character), Quicksilver (comics) is a retrieved title and is a known Marvel superhero, summary_1 states the superhero role originates from American comic books published by Marvel Comics
- noisy_or_distracting_clues: Luna Maximoff / Scarlet Witch–adjacent topics (related family/characters) that could distract, Event/comic titles (Son of M, Ultimatum) and minor characters (Random) that are contextually nearby but not the target, General page 'Evan Peters' may contain many non-character details
- expected_evidence_type: Short passages or lead sentences that explicitly state 'Evan Peters portrayed Quicksilver' and/or 'Quicksilver is a fictional superhero published by Marvel Comics.'
- query_shape_implication: Entity-to-entity short query (e.g., 'Evan Peters Quicksilver' or 'Quicksilver publisher') expecting exact-name matches rather than long natural-language questions.

---

### 262__split1__seg0__right

- idx: 262
- split_iter: 1
- task_kind: right_recovery
- expected: A
- predicted: tie
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.7
- why_larger: Both segments perform essentially the same retrieval-focus change: they shift from a game-centric search for Xenoblade Chronicles X credits to a designer-centric search for Kunihiko Tanaka's filmography/credits. The type and magnitude of the correction (anchor shift from game to designer) and the expected evidence types are effectively identical, so neither segment shows a clearly larger update.

**Question**

Kunihiko Tanaka designed the characters for which video game developed by Monolith Soft ?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Kunihiko Tanaka credits list Monolith Soft Xenosaga KOS-MOS character design
- retrieved_titles: KOS-MOS, Xenosaga: The Animation, Xenosaga Episode III, Kunihiko Tanaka, Xenosaga I &amp; II, Xenosaga: Pied Piper, Tetsuya Takahashi
- retrieval_focus: {
  "retrieval_focus": "Locate an authoritative credits page or developer/official game page for Xenoblade Chronicles X (Monolith Soft) that lists Kunihiko Tanaka as a character designer.",
  "anchors": ["Kunihiko Tanaka", "Xenoblade Chronicles X", "Monolith Soft"],
  "bridge_clues": ["Xenoblade Chronicles X credits", "character designer credit", "official game site or manual credits", "Kunihiko Tanaka filmography/credits page", "developer (Monolith Soft) credits list"],
  "noisy_or_distracting_clues": ["KOS-MOS", "Xenosaga", "Xenogears", "Tetsuya Takahashi", retrieved title pages about Xenosaga series that are related but not the target"],
  "expected_evidence_type": "Game credits / official developer page, reputable game database entry (e.g., MobyGames, Giant Bomb), or Kunihiko Tanaka filmography page that explicitly names Xenoblade Chronicles X and his role as character designer.",
  "query_shape_implication": "Use precise queries combining the full game title + developer + 'credits' or 'character designer' and the designer's name (e.g., \"Xenoblade Chronicles X credits Kunihiko Tanaka Monolith Soft\" or \"Kunihiko Tanaka character designer Xenoblade Chronicles X\")."
}

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Find a designer-centric, authoritative credits/filmography page for Kunihiko Tanaka that enumerates his game credits and roles (so the target title can be confirmed from the creator's side rather than the game's credits page).
- anchors: Kunihiko Tanaka, filmography, credits, works, game credits
- bridge_clues: Kunihiko Tanaka filmography or credits page, Kunihiko Tanaka Wikipedia biography, MobyGames / Giant Bomb profile for Kunihiko Tanaka, official artist portfolio or agency page listing works, lists of titles credited to Kunihiko Tanaka (look for Xenoblade Chronicles X among them)
- noisy_or_distracting_clues: KOS-MOS, Xenosaga, Xenogears, Tetsuya Takahashi, other Xenoblade titles (e.g., Xenoblade Chronicles 2), fan sites or forum mentions that are not authoritative
- expected_evidence_type: Designer-focused sources: Wikipedia filmography, official artist/agency portfolio, or reputable game-credit aggregators (MobyGames, Giant Bomb) that list per-title credits and explicitly name Kunihiko Tanaka's role on specific games.
- query_shape_implication: Use designer-focused queries (e.g., variations of 'Kunihiko Tanaka filmography' or 'Kunihiko Tanaka credits') to retrieve an authoritative list of works; once the designer's credits page confirms candidate titles, pivot to the game's official credits to verify role and developer.

**Sub segment**

from_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Locate a reputable game-centric source (e.g., the Xenoblade Chronicles X Wikipedia page, MobyGames, Giant Bomb, or an official game manual/credits page) that lists the game's staff/character designers so Kunihiko Tanaka's credit on Xenoblade Chronicles X can be confirmed from the game's side.
- anchors: Xenoblade Chronicles X, credits, character designer, Kunihiko Tanaka, MobyGames, Wikipedia
- bridge_clues: Xenoblade Chronicles X credits page, Xenoblade Chronicles X Wikipedia 'Staff' or 'Development' section, MobyGames Xenoblade Chronicles X credits, Giant Bomb Xenoblade Chronicles X credits, official game manual or digital credits PDF, developer (Monolith Soft) press release or credits listing
- noisy_or_distracting_clues: Xenogears, Xenosaga, KOS-MOS, Tetsuya Takahashi, other Xenoblade titles (e.g., Xenoblade Chronicles, Xenoblade Chronicles 2), fan wikis or forum posts that repeat unverified claims
- expected_evidence_type: Game-credits entries on Wikipedia or reputable game databases (MobyGames/Giant Bomb), or official manual/credits pages that explicitly list character designers for Xenoblade Chronicles X.
- query_shape_implication: Use game-centric queries combining the full title with 'credits', 'staff', or a database/site name (e.g., 'Xenoblade Chronicles X credits MobyGames', 'Xenoblade Chronicles X Wikipedia character designer') to retrieve an authoritative page that names the character designers.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Find a designer-centric, authoritative credits/filmography page for Kunihiko Tanaka that enumerates his game credits and roles (so the target title can be confirmed from the creator's side rather than the game's credits page).
- anchors: Kunihiko Tanaka, filmography, credits, works, game credits
- bridge_clues: Kunihiko Tanaka filmography or credits page, Kunihiko Tanaka Wikipedia biography, MobyGames / Giant Bomb profile for Kunihiko Tanaka, official artist portfolio or agency page listing works, lists of titles credited to Kunihiko Tanaka (look for Xenoblade Chronicles X among them)
- noisy_or_distracting_clues: KOS-MOS, Xenosaga, Xenogears, Tetsuya Takahashi, other Xenoblade titles (e.g., Xenoblade Chronicles 2), fan sites or forum mentions that are not authoritative
- expected_evidence_type: Designer-focused sources: Wikipedia filmography, official artist/agency portfolio, or reputable game-credit aggregators (MobyGames, Giant Bomb) that list per-title credits and explicitly name Kunihiko Tanaka's role on specific games.
- query_shape_implication: Use designer-focused queries (e.g., variations of 'Kunihiko Tanaka filmography' or 'Kunihiko Tanaka credits') to retrieve an authoritative list of works; once the designer's credits page confirms candidate titles, pivot to the game's official credits to verify role and developer.

---

### 267__split1__seg0__left

- idx: 267
- split_iter: 1
- task_kind: left_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.88
- why_larger: Both segments perform essentially the same update: they reduce a long, name-heavy query to a concise, show-focused retrieval targeting the Smallville main article and the two creators (Alfred Gough and Miles Millar). The anchors, bridge clues, noisy-clue eliminations, expected evidence types, and overall query-shape change are functionally equivalent, so neither segment shows a clearly larger retrieval-focus or evidence-type correction.

**Question**

Who were the writers of an American television series based on the DC Comics character Superman, which starred an American actor known for his television roles that include Fox Crane on the NBC daytime soap opera "Passions"?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Smallville writing credits Alfred Gough Miles Millar Kelly Souders Brian Peterson Todd Slavkin Darren Swimmer "List of Smallville episodes" writers
- retrieved_titles: Miles Millar, Finale (Smallville), Tempest (Smallville), Todd Slavkin, Pilot (Smallville), List of Smallville episodes, Reckoning (Smallville)
- retrieval_focus: Find authoritative series-level writing credits for Smallville that confirm the primary writers/creators (especially Alfred Gough and Miles Millar) and enumerate credited writers for the show.
- anchors: Smallville, writers, creators, Alfred Gough, Miles Millar, List of Smallville episodes, Smallville writing credits
- bridge_clues: Justin Hartley, Fox Crane, Passions, Oliver Queen, American television series based on Superman, starred in Smallville
- noisy_or_distracting_clues: Episode pages (Finale, Pilot, Tempest, Reckoning) — focus on single episodes rather than series-level credits, Individual staff names in the query (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) may return person pages rather than a consolidated credits list, Pages about single creators (e.g., Miles Millar) may appear before the main series article
- expected_evidence_type: Series-level writing credits such as the Smallville main article, an official 'writing credits' section, or the 'List of Smallville episodes' page; corroborating creator bios (Alfred Gough, Miles Millar) that state they created/wrote the series.
- query_shape_implication: The current long, name-heavy query will bias retrieval toward individual person pages and episode pages; to get the definitive writer list, target the show-level pages or the creators' bios rather than enumerating many staff names or episode titles.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Shift from a long, name-heavy retrieval that returns many person and episode pages toward concise, show-level sources that explicitly name the series creators/writers: prioritize the Smallville main article, the 'List of Smallville episodes' (writing credits section), and bios of the two primary creators (Alfred Gough and Miles Millar). This reduces noise while keeping the retrieval anchored on the core creators rather than enumerating the entire writing staff.
- anchors: Smallville, creators, writers, Alfred Gough, Miles Millar, List of Smallville episodes
- bridge_clues: Justin Hartley, Fox Crane, Passions, Oliver Queen, American TV series based on Superman, created by / developed by, series-level writing credits
- noisy_or_distracting_clues: Individual episode pages (Pilot, Tempest, Finale, specific episode credits), Individual staff/person pages for many writers (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer, etc.), Character pages (Chloe Sullivan, other cast-centric pages), Unrelated pilot pages or other DC projects (Aquaman pilot) that surface because of shared names
- expected_evidence_type: Authoritative series-level statements (Smallville main article or official credits) that explicitly identify the creators/writers (e.g., 'created by Alfred Gough and Miles Millar') and, as secondary confirmation, the episode list showing writer credits or creator biographies that state their role on the show.
- query_shape_implication: Move from long multi-name queries to concise show-focused retrieval gestures: emphasize the show plus 'creators'/'writers' and the two primary creator names as anchor terms. This shape avoids retrieving many separate person or episode pages and surfaces pages that consolidate writing credits.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Smallville writing credits Alfred Gough Miles Millar Kelly Souders Brian Peterson Todd Slavkin Darren Swimmer "List of Smallville episodes" writers
- retrieved_titles: Miles Millar, Finale (Smallville), Tempest (Smallville), Todd Slavkin, Pilot (Smallville), List of Smallville episodes, Reckoning (Smallville)
- retrieval_focus: Find authoritative series-level writing credits for Smallville that confirm the primary writers/creators (especially Alfred Gough and Miles Millar) and enumerate credited writers for the show.
- anchors: Smallville, writers, creators, Alfred Gough, Miles Millar, List of Smallville episodes, Smallville writing credits
- bridge_clues: Justin Hartley, Fox Crane, Passions, Oliver Queen, American television series based on Superman, starred in Smallville
- noisy_or_distracting_clues: Episode pages (Finale, Pilot, Tempest, Reckoning) — focus on single episodes rather than series-level credits, Individual staff names in the query (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) may return person pages rather than a consolidated credits list, Pages about single creators (e.g., Miles Millar) may appear before the main series article
- expected_evidence_type: Series-level writing credits such as the Smallville main article, an official 'writing credits' section, or the 'List of Smallville episodes' page; corroborating creator bios (Alfred Gough, Miles Millar) that state they created/wrote the series.
- query_shape_implication: The current long, name-heavy query will bias retrieval toward individual person pages and episode pages; to get the definitive writer list, target the show-level pages or the creators' bios rather than enumerating many staff names or episode titles.

to_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Reduce the long, name-heavy query by dropping many peripheral writer and episode names while keeping the show-level targets plus the two primary creators. Aim for the Smallville main article and the creator bios (Alfred Gough, Miles Millar) and any authoritative series-credit pages (e.g., 'List of Smallville episodes' credit summary, press/industry articles) that explicitly state who created/wrote the series.
- anchors: Smallville, created by, Alfred Gough, Miles Millar, series credits, List of Smallville episodes
- bridge_clues: Justin Hartley, Oliver Queen, Fox Crane, Passions, American TV series based on Superman, creators / developed by, primary writers
- noisy_or_distracting_clues: Full lists of episodic writers and individual episode pages (Pilot, Finale, Tempest, etc.), Person-specific pages for many secondary writers (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) that fragment search results, Fan wikis and character pages that focus on plot/characters rather than production credits, Unrelated DC projects or articles that mention 'Smallville' only tangentially
- expected_evidence_type: Authoritative series-level sources: the Smallville main article or official credits page stating 'created by' or 'developed by' Alfred Gough and Miles Millar; corroborating creator biographies or industry articles (e.g., Variety, Hollywood Reporter) that attribute creation/writing credit to them.
- query_shape_implication: Move from a long enumeration of names and episode titles to a concise, show-plus-creators shape: include 'Smallville' with phrases like 'created by' or 'writers' and the two creator names. This reduces retrieval of many individual person/episode pages while still anchoring on the primary creators.

---

### 267__split2__seg0__left

- idx: 267
- split_iter: 2
- task_kind: left_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.9
- why_larger: Both segments perform essentially the same narrowing: they remove noisy episode/person pages and refocus retrieval onto show-level sources (Smallville main article, list of episodes) and the primary creators (Alfred Gough, Miles Millar). Differences are only minor wording/anchor emphasis (e.g., mention of 'created by' vs explicitly keeping Justin Hartley), not a substantive change in retrieval focus or correction type, so neither has a clearly larger update.

**Question**

Who were the writers of an American television series based on the DC Comics character Superman, which starred an American actor known for his television roles that include Fox Crane on the NBC daytime soap opera "Passions"?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Smallville writing credits Alfred Gough Miles Millar Kelly Souders Brian Peterson Todd Slavkin Darren Swimmer "List of Smallville episodes" writers
- retrieved_titles: Miles Millar, Finale (Smallville), Tempest (Smallville), Todd Slavkin, Pilot (Smallville), List of Smallville episodes, Reckoning (Smallville)
- retrieval_focus: Find authoritative series-level writing credits for Smallville that confirm the primary writers/creators (especially Alfred Gough and Miles Millar) and enumerate credited writers for the show.
- anchors: Smallville, writers, creators, Alfred Gough, Miles Millar, List of Smallville episodes, Smallville writing credits
- bridge_clues: Justin Hartley, Fox Crane, Passions, Oliver Queen, American television series based on Superman, starred in Smallville
- noisy_or_distracting_clues: Episode pages (Finale, Pilot, Tempest, Reckoning) — focus on single episodes rather than series-level credits, Individual staff names in the query (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) may return person pages rather than a consolidated credits list, Pages about single creators (e.g., Miles Millar) may appear before the main series article
- expected_evidence_type: Series-level writing credits such as the Smallville main article, an official 'writing credits' section, or the 'List of Smallville episodes' page; corroborating creator bios (Alfred Gough, Miles Millar) that state they created/wrote the series.
- query_shape_implication: The current long, name-heavy query will bias retrieval toward individual person pages and episode pages; to get the definitive writer list, target the show-level pages or the creators' bios rather than enumerating many staff names or episode titles.

to_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Reduce the long, name-heavy query by dropping many peripheral writer and episode names while keeping the show-level targets plus the two primary creators. Aim for the Smallville main article and the creator bios (Alfred Gough, Miles Millar) and any authoritative series-credit pages (e.g., 'List of Smallville episodes' credit summary, press/industry articles) that explicitly state who created/wrote the series.
- anchors: Smallville, created by, Alfred Gough, Miles Millar, series credits, List of Smallville episodes
- bridge_clues: Justin Hartley, Oliver Queen, Fox Crane, Passions, American TV series based on Superman, creators / developed by, primary writers
- noisy_or_distracting_clues: Full lists of episodic writers and individual episode pages (Pilot, Finale, Tempest, etc.), Person-specific pages for many secondary writers (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) that fragment search results, Fan wikis and character pages that focus on plot/characters rather than production credits, Unrelated DC projects or articles that mention 'Smallville' only tangentially
- expected_evidence_type: Authoritative series-level sources: the Smallville main article or official credits page stating 'created by' or 'developed by' Alfred Gough and Miles Millar; corroborating creator biographies or industry articles (e.g., Variety, Hollywood Reporter) that attribute creation/writing credit to them.
- query_shape_implication: Move from a long enumeration of names and episode titles to a concise, show-plus-creators shape: include 'Smallville' with phrases like 'created by' or 'writers' and the two creator names. This reduces retrieval of many individual person/episode pages while still anchoring on the primary creators.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Smallville writing credits Alfred Gough Miles Millar Kelly Souders Brian Peterson Todd Slavkin Darren Swimmer "List of Smallville episodes" writers
- retrieved_titles: Miles Millar, Finale (Smallville), Tempest (Smallville), Todd Slavkin, Pilot (Smallville), List of Smallville episodes, Reckoning (Smallville)
- retrieval_focus: Find authoritative series-level writing credits for Smallville that confirm the primary writers/creators (especially Alfred Gough and Miles Millar) and enumerate credited writers for the show.
- anchors: Smallville, writers, creators, Alfred Gough, Miles Millar, List of Smallville episodes, Smallville writing credits
- bridge_clues: Justin Hartley, Fox Crane, Passions, Oliver Queen, American television series based on Superman, starred in Smallville
- noisy_or_distracting_clues: Episode pages (Finale, Pilot, Tempest, Reckoning) — focus on single episodes rather than series-level credits, Individual staff names in the query (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) may return person pages rather than a consolidated credits list, Pages about single creators (e.g., Miles Millar) may appear before the main series article
- expected_evidence_type: Series-level writing credits such as the Smallville main article, an official 'writing credits' section, or the 'List of Smallville episodes' page; corroborating creator bios (Alfred Gough, Miles Millar) that state they created/wrote the series.
- query_shape_implication: The current long, name-heavy query will bias retrieval toward individual person pages and episode pages; to get the definitive writer list, target the show-level pages or the creators' bios rather than enumerating many staff names or episode titles.

to_state:
- name: Rmid_iter3_split0
- kind: generated_midpoint
- retrieval_focus: Narrow from a long name-heavy query to authoritative show-level sources: target the Smallville main article (series overview and credits), the consolidated 'List of Smallville episodes' credits page, and the creator bios for Alfred Gough and Miles Millar. Keep the actor link (Justin Hartley) as a bridge to confirm casting but drop individual episode pages and most secondary writer names.
- anchors: Smallville (TV series) main article, List of Smallville episodes, Alfred Gough, Miles Millar, writing credits, Justin Hartley
- bridge_clues: American television series based on Superman, starred Justin Hartley, Oliver Queen, Fox Crane, Passions, created by / developed by, primary series creators
- noisy_or_distracting_clues: Individual episode pages (Pilot, Finale, Tempest, Reckoning) that focus on plot details, Long enumerations of secondary writers (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) that pull up person-specific pages, Fan wikis, character analyses, and actor filmographies that don't clearly list series-level writers, Unrelated DC property pages or news items that mention 'Smallville' only in passing
- expected_evidence_type: Series-level credit statements in the Smallville main article or episode-list credit summary (e.g., 'Created by Alfred Gough and Miles Millar'), corroborating creator biographies or reputable industry coverage (Variety, Hollywood Reporter, official press releases) that name the show's writers/creators.
- query_shape_implication: Shorten the query to: show title + 'created by'/'writing credits' + the two creator names, and include the episode-list as a consolidated credits source. This reduces retrieval of many person/episode pages while still surfacing the authoritative series- and creator-level pages needed to confirm writers.

---

### 267__split3__seg0__left

- idx: 267
- split_iter: 3
- task_kind: left_recovery
- expected: B
- predicted: tie
- correct: 0.0
- dominant_gap_type: tie
- confidence: 0.74
- why_larger: Both segments perform essentially the same retrieval-shape correction: they shorten a long, name-heavy query into a show-centric intent targeting the Smallville main article and the creators' bios, while keeping Justin Hartley as a casting bridge and de-emphasizing individual episode/person pages. The differences are only minor (A explicitly avoids episode pages; B explicitly includes the consolidated 'List of Smallville episodes' and mentions industry coverage), which do not justify preferring one as a substantially larger update.

**Question**

Who were the writers of an American television series based on the DC Comics character Superman, which starred an American actor known for his television roles that include Fox Crane on the NBC daytime soap opera "Passions"?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Smallville writing credits Alfred Gough Miles Millar Kelly Souders Brian Peterson Todd Slavkin Darren Swimmer "List of Smallville episodes" writers
- retrieved_titles: Miles Millar, Finale (Smallville), Tempest (Smallville), Todd Slavkin, Pilot (Smallville), List of Smallville episodes, Reckoning (Smallville)
- retrieval_focus: Find authoritative series-level writing credits for Smallville that confirm the primary writers/creators (especially Alfred Gough and Miles Millar) and enumerate credited writers for the show.
- anchors: Smallville, writers, creators, Alfred Gough, Miles Millar, List of Smallville episodes, Smallville writing credits
- bridge_clues: Justin Hartley, Fox Crane, Passions, Oliver Queen, American television series based on Superman, starred in Smallville
- noisy_or_distracting_clues: Episode pages (Finale, Pilot, Tempest, Reckoning) — focus on single episodes rather than series-level credits, Individual staff names in the query (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) may return person pages rather than a consolidated credits list, Pages about single creators (e.g., Miles Millar) may appear before the main series article
- expected_evidence_type: Series-level writing credits such as the Smallville main article, an official 'writing credits' section, or the 'List of Smallville episodes' page; corroborating creator bios (Alfred Gough, Miles Millar) that state they created/wrote the series.
- query_shape_implication: The current long, name-heavy query will bias retrieval toward individual person pages and episode pages; to get the definitive writer list, target the show-level pages or the creators' bios rather than enumerating many staff names or episode titles.

to_state:
- name: Rmid_iter3_split0
- kind: generated_midpoint
- retrieval_focus: Narrow from a long name-heavy query to authoritative show-level sources: target the Smallville main article (series overview and credits), the consolidated 'List of Smallville episodes' credits page, and the creator bios for Alfred Gough and Miles Millar. Keep the actor link (Justin Hartley) as a bridge to confirm casting but drop individual episode pages and most secondary writer names.
- anchors: Smallville (TV series) main article, List of Smallville episodes, Alfred Gough, Miles Millar, writing credits, Justin Hartley
- bridge_clues: American television series based on Superman, starred Justin Hartley, Oliver Queen, Fox Crane, Passions, created by / developed by, primary series creators
- noisy_or_distracting_clues: Individual episode pages (Pilot, Finale, Tempest, Reckoning) that focus on plot details, Long enumerations of secondary writers (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) that pull up person-specific pages, Fan wikis, character analyses, and actor filmographies that don't clearly list series-level writers, Unrelated DC property pages or news items that mention 'Smallville' only in passing
- expected_evidence_type: Series-level credit statements in the Smallville main article or episode-list credit summary (e.g., 'Created by Alfred Gough and Miles Millar'), corroborating creator biographies or reputable industry coverage (Variety, Hollywood Reporter, official press releases) that name the show's writers/creators.
- query_shape_implication: Shorten the query to: show title + 'created by'/'writing credits' + the two creator names, and include the episode-list as a consolidated credits source. This reduces retrieval of many person/episode pages while still surfacing the authoritative series- and creator-level pages needed to confirm writers.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Smallville writing credits Alfred Gough Miles Millar Kelly Souders Brian Peterson Todd Slavkin Darren Swimmer "List of Smallville episodes" writers
- retrieved_titles: Miles Millar, Finale (Smallville), Tempest (Smallville), Todd Slavkin, Pilot (Smallville), List of Smallville episodes, Reckoning (Smallville)
- retrieval_focus: Find authoritative series-level writing credits for Smallville that confirm the primary writers/creators (especially Alfred Gough and Miles Millar) and enumerate credited writers for the show.
- anchors: Smallville, writers, creators, Alfred Gough, Miles Millar, List of Smallville episodes, Smallville writing credits
- bridge_clues: Justin Hartley, Fox Crane, Passions, Oliver Queen, American television series based on Superman, starred in Smallville
- noisy_or_distracting_clues: Episode pages (Finale, Pilot, Tempest, Reckoning) — focus on single episodes rather than series-level credits, Individual staff names in the query (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) may return person pages rather than a consolidated credits list, Pages about single creators (e.g., Miles Millar) may appear before the main series article
- expected_evidence_type: Series-level writing credits such as the Smallville main article, an official 'writing credits' section, or the 'List of Smallville episodes' page; corroborating creator bios (Alfred Gough, Miles Millar) that state they created/wrote the series.
- query_shape_implication: The current long, name-heavy query will bias retrieval toward individual person pages and episode pages; to get the definitive writer list, target the show-level pages or the creators' bios rather than enumerating many staff names or episode titles.

to_state:
- name: Rmid_iter4_split0
- kind: generated_midpoint
- retrieval_focus: Move from a long, name-heavy query to a modestly focused retrieval intent: target the Smallville series-level article (overview/credits) and the creator bios for Alfred Gough and Miles Millar, while keeping Justin Hartley as a casting-bridge to confirm the actor link. Intentionally avoid episode pages and long enumerations of secondary writers.
- anchors: Smallville (TV series) main article / series overview, Created by / developed by (credit line), Alfred Gough, Miles Millar, Justin Hartley (casting / role confirmation)
- bridge_clues: American television series based on Superman, created by, series-level writing credits, starred Justin Hartley, Oliver Queen, Fox Crane / Passions (actor cross-reference)
- noisy_or_distracting_clues: Individual episode pages (Pilot, Finale, Tempest, Reckoning) that emphasize plot rather than series credits, Long lists of secondary writer names (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer) that pull up person pages, Actor filmographies and fan wikis that mention Smallville but don't state creator/writer credits clearly, News articles or pages that mention Justin Hartley but not series creators
- expected_evidence_type: Concise series-level credit statements (e.g., 'Created by Alfred Gough and Miles Millar') in the Smallville main article or in a consolidated credits section; corroborating lines in the Alfred Gough and Miles Millar bios that they developed/wrote the series.
- query_shape_implication: Shorten to a show-centric shape (show title + 'created by'/'writing credits' + creator names as keywords) rather than enumerating many staff or episode titles; include the actor name only as a secondary keyword for casting confirmation.

---

### 55__split1__seg1__right

- idx: 55
- split_iter: 1
- task_kind: right_recovery
- expected: A
- predicted: tie
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.82
- why_larger: Both segments make symmetric, comparable updates: each moves from an entity-specific lookup (A: film Amsterdamned; B: city Amsterdam) to a joint verification that both are Dutch. Each adds one new entity anchor and similar bridge clues (national/cultural affiliation), with no clear larger entity correction, relation change, or evidence-family shift. No local ordering justifies preferring one over the other.

**Question**

What culture do both the Capital of the Netherlands and Amsterdamned have in common?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Establish the nationality/origin of the film 'Amsterdamned' (confirm it is a 1988 Dutch film set in Amsterdam), as an intermediate step toward showing both entities share Dutch culture.
- anchors: Amsterdamned, Dick Maas, 1988, Dutch film, canals of Amsterdam, Huub Stapel
- bridge_clues: 1988 horror film, directed by Dick Maas, described as Dutch, set/uses Amsterdam canals, cast includes Huub Stapel
- noisy_or_distracting_clues: Other Dutch films (Sint, The Johnsons), Films with similar Amsterdam settings but different origins, New Amsterdam (place name confusion)
- expected_evidence_type: Short film-encyclopedia or database snippets/infobox lines that explicitly state: 'Amsterdamned is a 1988 Dutch horror film directed by Dick Maas' and mention its Amsterdam setting.
- query_shape_implication: Narrow, entity-focused lookup for film metadata (film title + year/director/descriptor), e.g., searches that retrieve the Amsterdamned film page or Dutch cinema listings rather than general culture pages.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Amsterdamned, The Johnsons, Capital of the Netherlands, Roman Catholic Diocese of Haarlem-Amsterdam, Sint, Netherlands, New Amsterdam
- retrieval_focus: Verify the shared cultural/national origin of the two entities (the Capital of the Netherlands / Amsterdam and the film Amsterdamned) — i.e., confirm they are associated with Dutch culture.
- anchors: Amsterdam, Amsterdamned, Netherlands, Dutch culture
- bridge_clues: Dutch, Netherlands, capital, Dutch film, canals of Amsterdam, 1988 horror film, Dick Maas
- noisy_or_distracting_clues: New Amsterdam (different place), Roman Catholic Diocese of Haarlem-Amsterdam (religious/administrative), The Johnsons (other film), Sint (other Dutch film)
- expected_evidence_type: Short authoritative statements or infobox lines stating nationality/origin (e.g., 'Amsterdam is the capital of the Netherlands' and 'Amsterdamned is a 1988 Dutch film') or pages titled 'Dutch culture' / 'Dutch cinema'.
- query_shape_implication: Entity-to-property lookups: compact queries like 'Amsterdam nationality/culture', 'Amsterdamned film nationality/origin', or 'Amsterdamned Dutch film' — expect a single-sentence confirmation per entity rather than long documents.

**Sub segment**

from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Establish that Amsterdam (the city) is the capital of the Netherlands and is associated with Dutch national/cultural identity (language, heritage, landmarks) as the complementary step to the film-focused R_left, moving toward confirming a shared Dutch culture.
- anchors: Amsterdam, Capital of the Netherlands, Netherlands, Dutch culture, canals, museums
- bridge_clues: officially the capital of the Netherlands, located in the Netherlands / North Holland, primary city associated with Dutch national identity, Dutch is the main language, cultural landmarks (canals, Rijksmuseum) tie city to Dutch heritage
- noisy_or_distracting_clues: The Hague (seat of government, not the capital confusion), New Amsterdam (historical/US place-name confusion), other places named Amsterdam (towns in US/elsewhere), events or entities named 'Amsterdam' unrelated to Dutch national identity
- expected_evidence_type: Short authoritative lines or infobox entries stating 'Amsterdam is the capital of the Netherlands' and noting national/cultural attributes (country = Netherlands, language = Dutch, notable Dutch cultural landmarks).
- query_shape_implication: Concise entity-to-property lookups such as 'Amsterdam capital of Netherlands', 'Amsterdam country/language', or a city infobox page (Amsterdam) rather than film or general culture pages.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Amsterdamned, The Johnsons, Capital of the Netherlands, Roman Catholic Diocese of Haarlem-Amsterdam, Sint, Netherlands, New Amsterdam
- retrieval_focus: Verify the shared cultural/national origin of the two entities (the Capital of the Netherlands / Amsterdam and the film Amsterdamned) — i.e., confirm they are associated with Dutch culture.
- anchors: Amsterdam, Amsterdamned, Netherlands, Dutch culture
- bridge_clues: Dutch, Netherlands, capital, Dutch film, canals of Amsterdam, 1988 horror film, Dick Maas
- noisy_or_distracting_clues: New Amsterdam (different place), Roman Catholic Diocese of Haarlem-Amsterdam (religious/administrative), The Johnsons (other film), Sint (other Dutch film)
- expected_evidence_type: Short authoritative statements or infobox lines stating nationality/origin (e.g., 'Amsterdam is the capital of the Netherlands' and 'Amsterdamned is a 1988 Dutch film') or pages titled 'Dutch culture' / 'Dutch cinema'.
- query_shape_implication: Entity-to-property lookups: compact queries like 'Amsterdam nationality/culture', 'Amsterdamned film nationality/origin', or 'Amsterdamned Dutch film' — expect a single-sentence confirmation per entity rather than long documents.

---

## pass (95 total, showing 8)

### 108__split1__seg1__left

- idx: 108
- split_iter: 1
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why_larger: Segment A moves from a disambiguation intent to actually obtaining the canonical 'Solo (Australian soft drink)' in retrieved_titles — it performs the core entity-anchor correction (finding the correct Solo page). Segment B only narrows the next-step extraction (infobox/lead) without showing the retrieval result, so A is the larger retrieval-focus change.

**Question**

Are Solo and La Croix Sparkling Water produced in the same country ?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate 'Solo' and retrieve the canonical 'Solo (Australian soft drink)' page or an authoritative manufacturer page that explicitly states Solo's country of origin/production (Australia) so it can be compared to La Croix (United States).
- anchors: Solo (Australian soft drink), Solo (Norwegian soft drink), Solo (soft drink), La Croix Sparkling Water, United States, Australia, Schweppes Australia, Asahi/Distributor
- bridge_clues: Presence of a page titled 'Solo (Australian soft drink)' in search results, Lead/infobox text on the Solo page stating 'Country of origin' or 'Origin: Australia' or production/manufacturer located in Australia, Manufacturer or distributor entries (e.g., Schweppes Australia) on the Solo page that imply Australian production, Explicit disambiguation markers distinguishing Australian Solo from a Norwegian Solo
- noisy_or_distracting_clues: Search hits for 'Solo (Norwegian soft drink)' or other regional 'Solo' brands, Unrelated beverage pages (Trend Drinks, Geo. Hall & Sons, Rubicon, Guaraná Antarctica), Global manufacturer pages that mention Schweppes/Asahi in other countries without specifying Solo's production location
- expected_evidence_type: A short authoritative page (Wikipedia article infobox/lead or manufacturer's product page) that explicitly states Solo's country of origin/production (e.g., 'Country of origin: Australia' or a clear manufacturer/production location in Australia).
- query_shape_implication: Use a concise disambiguation-style query targeting the canonical page title or the phrase 'Solo (Australian soft drink) country of origin' to avoid regional variants and noisy brand pages; this is a single-entity retrieval step focused on resolving ambiguity.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate 'Solo' and retrieve the canonical 'Solo (Australian soft drink)' page or an authoritative manufacturer page that explicitly states Solo's country of origin/production (Australia) so it can be compared to La Croix (United States).
- anchors: Solo (Australian soft drink), Solo (Norwegian soft drink), Solo (soft drink), La Croix Sparkling Water, United States, Australia, Schweppes Australia, Asahi/Distributor
- bridge_clues: Presence of a page titled 'Solo (Australian soft drink)' in search results, Lead/infobox text on the Solo page stating 'Country of origin' or 'Origin: Australia' or production/manufacturer located in Australia, Manufacturer or distributor entries (e.g., Schweppes Australia) on the Solo page that imply Australian production, Explicit disambiguation markers distinguishing Australian Solo from a Norwegian Solo
- noisy_or_distracting_clues: Search hits for 'Solo (Norwegian soft drink)' or other regional 'Solo' brands, Unrelated beverage pages (Trend Drinks, Geo. Hall & Sons, Rubicon, Guaraná Antarctica), Global manufacturer pages that mention Schweppes/Asahi in other countries without specifying Solo's production location
- expected_evidence_type: A short authoritative page (Wikipedia article infobox/lead or manufacturer's product page) that explicitly states Solo's country of origin/production (e.g., 'Country of origin: Australia' or a clear manufacturer/production location in Australia).
- query_shape_implication: Use a concise disambiguation-style query targeting the canonical page title or the phrase 'Solo (Australian soft drink) country of origin' to avoid regional variants and noisy brand pages; this is a single-entity retrieval step focused on resolving ambiguity.

to_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Target the Solo (Australian soft drink) page and extract the lead/infobox lines that state country of origin/production and the named manufacturer/distributor (evidence that Solo is produced in Australia).
- anchors: Solo (Australian soft drink), infobox/lead sentence, Country of origin: Australia, Manufacturer / Distributor (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil), Production location / brewed/produced in
- bridge_clues: Lead sentence beginning with 'Solo is an Australian...' or similar, Infobox field 'Origin' or 'Country' listed as Australia, Explicit mention of manufacturer/distributor that operates in Australia (Schweppes Australia, Asahi, etc.), Phrases like 'Australian lemon-flavoured soft drink' or 'produced in Australia' in the page lead/intro
- noisy_or_distracting_clues: Pages for 'Solo (Norwegian soft drink)' or other regional Solo brands, General beverage manufacturer pages that mention Schweppes/Asahi in multiple countries without linking Solo to Australia, Lists of soft drinks where Solo appears without context about origin, News/articles about distribution deals that don't state production country
- expected_evidence_type: Short authoritative textual evidence from the Solo page (Wikipedia infobox/lead or manufacturer product page) explicitly stating country of origin/production (Australia) and/or naming the Australian manufacturer/distributor.
- query_shape_implication: A concise extraction-style query targeting the canonical Solo (Australian soft drink) page and its infobox/lead (e.g., phrasing that requests 'Solo (Australian soft drink) infobox origin' or 'Solo lead sentence country of origin') to avoid returning regional variants or generic brand lists.

---

### 108__split1__seg1__right

- idx: 108
- split_iter: 1
- task_kind: right_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.82
- why_larger: Segment A requires resolving the ambiguous 'Solo' entity (disambiguation to the Australian Solo) and shifting retrieval focus to the canonical Solo page — a substantive entity-anchor correction. Segment B is a narrower extraction step (pulling infobox/lead once the correct page is targeted). The disambiguation/change of retrieval target in A is the larger update.

**Question**

Are Solo and La Croix Sparkling Water produced in the same country ?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate 'Solo' and retrieve the canonical 'Solo (Australian soft drink)' page or an authoritative manufacturer page that explicitly states Solo's country of origin/production (Australia) so it can be compared to La Croix (United States).
- anchors: Solo (Australian soft drink), Solo (Norwegian soft drink), Solo (soft drink), La Croix Sparkling Water, United States, Australia, Schweppes Australia, Asahi/Distributor
- bridge_clues: Presence of a page titled 'Solo (Australian soft drink)' in search results, Lead/infobox text on the Solo page stating 'Country of origin' or 'Origin: Australia' or production/manufacturer located in Australia, Manufacturer or distributor entries (e.g., Schweppes Australia) on the Solo page that imply Australian production, Explicit disambiguation markers distinguishing Australian Solo from a Norwegian Solo
- noisy_or_distracting_clues: Search hits for 'Solo (Norwegian soft drink)' or other regional 'Solo' brands, Unrelated beverage pages (Trend Drinks, Geo. Hall & Sons, Rubicon, Guaraná Antarctica), Global manufacturer pages that mention Schweppes/Asahi in other countries without specifying Solo's production location
- expected_evidence_type: A short authoritative page (Wikipedia article infobox/lead or manufacturer's product page) that explicitly states Solo's country of origin/production (e.g., 'Country of origin: Australia' or a clear manufacturer/production location in Australia).
- query_shape_implication: Use a concise disambiguation-style query targeting the canonical page title or the phrase 'Solo (Australian soft drink) country of origin' to avoid regional variants and noisy brand pages; this is a single-entity retrieval step focused on resolving ambiguity.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

**Sub segment**

from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Target the Solo (Australian soft drink) page and extract the lead/infobox lines that state country of origin/production and the named manufacturer/distributor (evidence that Solo is produced in Australia).
- anchors: Solo (Australian soft drink), infobox/lead sentence, Country of origin: Australia, Manufacturer / Distributor (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil), Production location / brewed/produced in
- bridge_clues: Lead sentence beginning with 'Solo is an Australian...' or similar, Infobox field 'Origin' or 'Country' listed as Australia, Explicit mention of manufacturer/distributor that operates in Australia (Schweppes Australia, Asahi, etc.), Phrases like 'Australian lemon-flavoured soft drink' or 'produced in Australia' in the page lead/intro
- noisy_or_distracting_clues: Pages for 'Solo (Norwegian soft drink)' or other regional Solo brands, General beverage manufacturer pages that mention Schweppes/Asahi in multiple countries without linking Solo to Australia, Lists of soft drinks where Solo appears without context about origin, News/articles about distribution deals that don't state production country
- expected_evidence_type: Short authoritative textual evidence from the Solo page (Wikipedia infobox/lead or manufacturer product page) explicitly stating country of origin/production (Australia) and/or naming the Australian manufacturer/distributor.
- query_shape_implication: A concise extraction-style query targeting the canonical Solo (Australian soft drink) page and its infobox/lead (e.g., phrasing that requests 'Solo (Australian soft drink) infobox origin' or 'Solo lead sentence country of origin') to avoid returning regional variants or generic brand lists.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

---

### 108__split3__seg3__left

- idx: 108
- split_iter: 3
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: Segment A performs a broader retrieval-step that establishes the correct entity anchor (finding and adding the Solo (Australian soft drink) page among other titles) and shifts the retrieval focus toward comparing that entity with La Croix. Segment B is a narrower, follow-up extraction targeting a single lead/infobox snippet from the already-identified Solo page. A therefore represents the larger change in retrieval focus and entity anchoring.

**Question**

Are Solo and La Croix Sparkling Water produced in the same country ?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter3_split2
- kind: generated_midpoint
- retrieval_focus: First disambiguate which 'Solo' is intended by retrieving the Solo disambiguation/summary and any immediate manufacturer or product-summary lines that link the brand name to a country (e.g., 'Solo (Australian soft drink)' or a manufacturer page that explicitly ties Solo to Australia). This narrows scope before fetching full product pages.
- anchors: Solo (disambiguation) / 'Solo (soft drink)' summary line, Disambiguation entry that points to 'Solo (Australian soft drink)', Short lead/infobox lines from Solo (Australian soft drink) confirming country or origin, Manufacturer/distributor short page or header (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil) that mentions Solo
- bridge_clues: Disambiguation text: 'Solo may refer to...' with a line for the Australian soft drink, Lead sentence on Solo (Australian soft drink) beginning 'Solo is an Australian...' or 'Solo is a lemon-flavoured soft drink produced in Australia', Infobox or parenthetical note that lists 'Country of origin: Australia' or similar, Short manufacturer header stating they produce/distribute Solo in Australia
- noisy_or_distracting_clues: Entries for Solo (Norwegian soft drink) or other regional variants that could be mistaken for the Australian product, Long lists of beverages or manufacturer pages that mention many brands without clear country attribution, News/distribution articles that mention global companies (Schweppes, Asahi) without explicitly tying Solo to a production country, Unrelated beverage pages (Trend Drinks, V (drink), Guaraná Antarctica) that surface in broad queries
- expected_evidence_type: Short, authoritative disambiguation line or one-sentence lead/infobox text that unambiguously links 'Solo' to the Australian product (or indicates multiple regional products), and/or a manufacturer header that names Australia as the production/origin location.
- query_shape_implication: A concise disambiguation-style query that first asks for 'Solo (soft drink) disambiguation' or 'Solo disambiguation lead' and/or a tight extraction like 'Solo (Australian soft drink) lead/origin' to confirm which Solo to follow up on in the next retrieval.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

**Sub segment**

from_state:
- name: Rmid_iter3_split2
- kind: generated_midpoint
- retrieval_focus: First disambiguate which 'Solo' is intended by retrieving the Solo disambiguation/summary and any immediate manufacturer or product-summary lines that link the brand name to a country (e.g., 'Solo (Australian soft drink)' or a manufacturer page that explicitly ties Solo to Australia). This narrows scope before fetching full product pages.
- anchors: Solo (disambiguation) / 'Solo (soft drink)' summary line, Disambiguation entry that points to 'Solo (Australian soft drink)', Short lead/infobox lines from Solo (Australian soft drink) confirming country or origin, Manufacturer/distributor short page or header (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil) that mentions Solo
- bridge_clues: Disambiguation text: 'Solo may refer to...' with a line for the Australian soft drink, Lead sentence on Solo (Australian soft drink) beginning 'Solo is an Australian...' or 'Solo is a lemon-flavoured soft drink produced in Australia', Infobox or parenthetical note that lists 'Country of origin: Australia' or similar, Short manufacturer header stating they produce/distribute Solo in Australia
- noisy_or_distracting_clues: Entries for Solo (Norwegian soft drink) or other regional variants that could be mistaken for the Australian product, Long lists of beverages or manufacturer pages that mention many brands without clear country attribution, News/distribution articles that mention global companies (Schweppes, Asahi) without explicitly tying Solo to a production country, Unrelated beverage pages (Trend Drinks, V (drink), Guaraná Antarctica) that surface in broad queries
- expected_evidence_type: Short, authoritative disambiguation line or one-sentence lead/infobox text that unambiguously links 'Solo' to the Australian product (or indicates multiple regional products), and/or a manufacturer header that names Australia as the production/origin location.
- query_shape_implication: A concise disambiguation-style query that first asks for 'Solo (soft drink) disambiguation' or 'Solo disambiguation lead' and/or a tight extraction like 'Solo (Australian soft drink) lead/origin' to confirm which Solo to follow up on in the next retrieval.

to_state:
- name: Rmid_iter4_split3
- kind: generated_midpoint
- retrieval_focus: Fetch the Solo (Australian soft drink) page's lead sentence and infobox lines (country of origin/produced in; manufacturer/distributor) or a single-line manufacturer header that explicitly ties Solo to Australia. Keep the retrieval narrowly focused on one authoritative short snippet rather than full related pages or lists.
- anchors: Solo (Australian soft drink) — lead sentence, Infobox fields: 'Country of origin', 'Manufacturer' or 'Produced in', Manufacturer/distributor header that names Solo and lists Australia (e.g., Schweppes Australia / Asahi / Coca‑Cola Amatil)
- bridge_clues: Lead phrase such as 'Solo is an Australian...' or 'Solo is a lemon-flavoured soft drink from Australia', Infobox entry 'Country of origin: Australia' or parenthetical '(Australia)' next to the brand name, Manufacturer/distributor one-line summary that states they produce/distribute Solo in Australia
- noisy_or_distracting_clues: Entries for other 'Solo' beverages (e.g., Solo (Norwegian soft drink)) that look similar in titles, Long manufacturer pages listing many brands without explicit per-brand country lines, News articles or distributor pages mentioning global operations without tying Solo to a production country, Lists of beverages where Solo appears among many international brands
- expected_evidence_type: A one-sentence lead and/or infobox line from the Solo (Australian soft drink) page or a single-line manufacturer header that unambiguously states Solo's country of origin/production (Australia).
- query_shape_implication: A highly targeted extraction-style query for a short factual snippet, e.g., 'Solo (Australian soft drink) lead sentence' or 'Solo (soft drink) infobox country of origin / manufacturer', returning 1–2 lines.

---

### 108__split3__seg3__right

- idx: 108
- split_iter: 3
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.82
- why_larger: Segment B introduces an explicit disambiguation step to resolve which 'Solo' is meant before fetching product info, correcting an ambiguous/noisy entity anchor and changing the retrieval shape (disambiguation → targeted evidence). Segment A already assumes the Australian Solo and only needs a narrow extraction, so B entails a larger retrieval-focus and entity-correction update.

**Question**

Are Solo and La Croix Sparkling Water produced in the same country ?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter3_split2
- kind: generated_midpoint
- retrieval_focus: First disambiguate which 'Solo' is intended by retrieving the Solo disambiguation/summary and any immediate manufacturer or product-summary lines that link the brand name to a country (e.g., 'Solo (Australian soft drink)' or a manufacturer page that explicitly ties Solo to Australia). This narrows scope before fetching full product pages.
- anchors: Solo (disambiguation) / 'Solo (soft drink)' summary line, Disambiguation entry that points to 'Solo (Australian soft drink)', Short lead/infobox lines from Solo (Australian soft drink) confirming country or origin, Manufacturer/distributor short page or header (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil) that mentions Solo
- bridge_clues: Disambiguation text: 'Solo may refer to...' with a line for the Australian soft drink, Lead sentence on Solo (Australian soft drink) beginning 'Solo is an Australian...' or 'Solo is a lemon-flavoured soft drink produced in Australia', Infobox or parenthetical note that lists 'Country of origin: Australia' or similar, Short manufacturer header stating they produce/distribute Solo in Australia
- noisy_or_distracting_clues: Entries for Solo (Norwegian soft drink) or other regional variants that could be mistaken for the Australian product, Long lists of beverages or manufacturer pages that mention many brands without clear country attribution, News/distribution articles that mention global companies (Schweppes, Asahi) without explicitly tying Solo to a production country, Unrelated beverage pages (Trend Drinks, V (drink), Guaraná Antarctica) that surface in broad queries
- expected_evidence_type: Short, authoritative disambiguation line or one-sentence lead/infobox text that unambiguously links 'Solo' to the Australian product (or indicates multiple regional products), and/or a manufacturer header that names Australia as the production/origin location.
- query_shape_implication: A concise disambiguation-style query that first asks for 'Solo (soft drink) disambiguation' or 'Solo disambiguation lead' and/or a tight extraction like 'Solo (Australian soft drink) lead/origin' to confirm which Solo to follow up on in the next retrieval.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

**Sub segment**

from_state:
- name: Rmid_iter4_split3
- kind: generated_midpoint
- retrieval_focus: Fetch the Solo (Australian soft drink) page's lead sentence and infobox lines (country of origin/produced in; manufacturer/distributor) or a single-line manufacturer header that explicitly ties Solo to Australia. Keep the retrieval narrowly focused on one authoritative short snippet rather than full related pages or lists.
- anchors: Solo (Australian soft drink) — lead sentence, Infobox fields: 'Country of origin', 'Manufacturer' or 'Produced in', Manufacturer/distributor header that names Solo and lists Australia (e.g., Schweppes Australia / Asahi / Coca‑Cola Amatil)
- bridge_clues: Lead phrase such as 'Solo is an Australian...' or 'Solo is a lemon-flavoured soft drink from Australia', Infobox entry 'Country of origin: Australia' or parenthetical '(Australia)' next to the brand name, Manufacturer/distributor one-line summary that states they produce/distribute Solo in Australia
- noisy_or_distracting_clues: Entries for other 'Solo' beverages (e.g., Solo (Norwegian soft drink)) that look similar in titles, Long manufacturer pages listing many brands without explicit per-brand country lines, News articles or distributor pages mentioning global operations without tying Solo to a production country, Lists of beverages where Solo appears among many international brands
- expected_evidence_type: A one-sentence lead and/or infobox line from the Solo (Australian soft drink) page or a single-line manufacturer header that unambiguously states Solo's country of origin/production (Australia).
- query_shape_implication: A highly targeted extraction-style query for a short factual snippet, e.g., 'Solo (Australian soft drink) lead sentence' or 'Solo (soft drink) infobox country of origin / manufacturer', returning 1–2 lines.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Solo (Australian soft drink), Trend Drinks, Geo. Hall &amp; Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: La Croix (United States), Solo (Australian soft drink), Solo (Norwegian soft drink)
- bridge_clues: summary states La Croix produced in United States (La Crosse, Wisconsin), summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink, retrieved title 'Solo (Australian soft drink)' is present
- noisy_or_distracting_clues: Trend Drinks, Geo. Hall & Sons, Rubicon Drinks, V (drink), Solo (Norwegian soft drink), Guaraná Antarctica
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

---

### 118__split1__seg1__right

- idx: 118
- split_iter: 1
- task_kind: right_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.88
- why_larger: Segment A moves from a broad disambiguation stance (listing all candidate 'Third Person' works and multiple versions of 'From Here to Eternity' and building actor sets per candidate) to targeted cast retrieval — a much larger change in retrieval focus and required anchor expansion/correction than B, which is already committed to a single-year pairing and only needs narrow cast lookups.

**Question**

What acress starred in both "Third Person" and "From Here to Eternity"?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the title 'Third Person' (list all films/TV works with that title and their release years) and pull the top-billed actresses for each candidate; simultaneously confirm which specific version(s) of 'From Here to Eternity' are relevant by listing the common versions and their principal actresses. The goal is to produce candidate actor sets per specific title/version so the next step can do direct cast-list intersection.
- anchors: Third Person (disambiguation), Third Person (film) — candidate years/entries (e.g., 2013), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: work title + release year (to disambiguate similarly titled works), lead/billed actresses for each candidate Third Person, lead/billed actresses for each candidate From Here to Eternity version, short film/TV synopses to confirm which cast lists are primary (e.g., 'starring', 'lead')
- noisy_or_distracting_clues: unrelated items on disambiguation pages (books, plays, songs titled 'Third Person'), other similarly named films (e.g., 'The Third Man', 'Third Wheel'), spin-off or stage adaptations of 'From Here to Eternity' (musical, live shows), celebrity names surfaced by broad searches that are not credited as cast
- expected_evidence_type: Disambiguation pages and individual film/TV pages or reliable filmographies that list release year and top-billed cast (Wikipedia film pages, IMDb title pages, or authoritative filmographies) so candidate actress sets can be created per specific work/version.
- query_shape_implication: Run narrow, title-disambiguation queries first (e.g., 'Third Person disambiguation' and 'Third Person (year) cast' for each candidate year found) and a small set of version-specific lookups for 'From Here to Eternity' (1953 and 1979) to extract lead actresses; this produces compact named-actor lists to intersect in the subsequent step.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: From Here to Eternity (TV series), From Here to Eternity, From Here to Eternity (miniseries), From Here to Eternity (disambiguation), Kim Basinger, Donna Reed, Heather O'Rourke
- retrieval_focus: Get authoritative cast lists for the specific works named (disambiguate which 'Third Person' and which version of 'From Here to Eternity') so we can find any overlapping performer.
- anchors: Third Person, Third Person (film), From Here to Eternity, From Here to Eternity (1953 film), From Here to Eternity (miniseries), cast, Deborah Kerr, Donna Reed
- bridge_clues: cast, starring, credited, filmography, appeared in, played
- noisy_or_distracting_clues: From Here to Eternity (disambiguation), From Here to Eternity (TV series), Kim Basinger, Heather O'Rourke
- expected_evidence_type: Primary film pages or reliable cast lists (Wikipedia film pages, IMDb/filmography entries, reputable biographies) showing full credited cast for each title/version.
- query_shape_implication: Issue two precise second-hop queries (exact title + 'cast' or year): e.g. 'Third Person (film) cast' and 'From Here to Eternity (1953 film) cast' (or 'From Here to Eternity (1979 miniseries) cast' if that version is intended), then intersect named cast members.

**Sub segment**

from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Narrow to the single most likely candidate for each ambiguous title: treat 'Third Person' as the 2013 feature film (the most prominent modern film by that title) and 'From Here to Eternity' as the original 1953 film. Retrieve the top-billed female cast (lead actresses) for those two specific entries to produce compact candidate actress sets for a direct intersection step.
- anchors: Third Person (2013 film) — cast/top-billed actors, From Here to Eternity (1953 film) — cast/top-billed actresses, Wikipedia or IMDb title pages for each film (cast sections), Lead billing / 'starring' lines on film pages
- bridge_clues: exact title + year (e.g., 'Third Person 2013 cast', 'From Here to Eternity 1953 cast'), sections labeled 'Starring' or top-billed cast, female names listed among top 3–5 billed performers, role names or 'as' annotations confirming performer appearance
- noisy_or_distracting_clues: other works titled 'Third Person' (short films, books, songs), later remakes or TV adaptations of From Here to Eternity (1979 miniseries) if the question intends a different version, male lead names and supporting male cast (not needed for actress intersection), crew, production, trivia, soundtrack, and release-date minutiae
- expected_evidence_type: Authoritative cast lists or 'Starring' sections from film pages (Wikipedia/IMDb/reliable filmographies) showing top-billed performers with clear ordering so a concise female-actor candidate set can be extracted for each specified title.
- query_shape_implication: Run two narrow queries: 'Third Person 2013 cast' and 'From Here to Eternity 1953 cast' (or targeted lookups of their Wikipedia/IMDb pages), then extract the top-billed female names (e.g., the first 2–4 actresses listed) to produce small, comparable sets for the next step.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: From Here to Eternity (TV series), From Here to Eternity, From Here to Eternity (miniseries), From Here to Eternity (disambiguation), Kim Basinger, Donna Reed, Heather O'Rourke
- retrieval_focus: Get authoritative cast lists for the specific works named (disambiguate which 'Third Person' and which version of 'From Here to Eternity') so we can find any overlapping performer.
- anchors: Third Person, Third Person (film), From Here to Eternity, From Here to Eternity (1953 film), From Here to Eternity (miniseries), cast, Deborah Kerr, Donna Reed
- bridge_clues: cast, starring, credited, filmography, appeared in, played
- noisy_or_distracting_clues: From Here to Eternity (disambiguation), From Here to Eternity (TV series), Kim Basinger, Heather O'Rourke
- expected_evidence_type: Primary film pages or reliable cast lists (Wikipedia film pages, IMDb/filmography entries, reputable biographies) showing full credited cast for each title/version.
- query_shape_implication: Issue two precise second-hop queries (exact title + 'cast' or year): e.g. 'Third Person (film) cast' and 'From Here to Eternity (1953 film) cast' (or 'From Here to Eternity (1979 miniseries) cast' if that version is intended), then intersect named cast members.

---

### 118__split2__seg1__left

- idx: 118
- split_iter: 2
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.83
- why_larger: Segment A makes a much larger retrieval-focus shift by decisively resolving the disambiguation to two specific anchors (Third Person → 2013 film; From Here to Eternity → 1953 film) and narrowing subsequent retrievals to those exact cast lists. That is a stronger entity-anchor/type correction and a bigger change in query shape than B, which retains multiple candidate titles/versions and only narrows to a small candidate set.

**Question**

What acress starred in both "Third Person" and "From Here to Eternity"?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the title 'Third Person' (list all films/TV works with that title and their release years) and pull the top-billed actresses for each candidate; simultaneously confirm which specific version(s) of 'From Here to Eternity' are relevant by listing the common versions and their principal actresses. The goal is to produce candidate actor sets per specific title/version so the next step can do direct cast-list intersection.
- anchors: Third Person (disambiguation), Third Person (film) — candidate years/entries (e.g., 2013), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: work title + release year (to disambiguate similarly titled works), lead/billed actresses for each candidate Third Person, lead/billed actresses for each candidate From Here to Eternity version, short film/TV synopses to confirm which cast lists are primary (e.g., 'starring', 'lead')
- noisy_or_distracting_clues: unrelated items on disambiguation pages (books, plays, songs titled 'Third Person'), other similarly named films (e.g., 'The Third Man', 'Third Wheel'), spin-off or stage adaptations of 'From Here to Eternity' (musical, live shows), celebrity names surfaced by broad searches that are not credited as cast
- expected_evidence_type: Disambiguation pages and individual film/TV pages or reliable filmographies that list release year and top-billed cast (Wikipedia film pages, IMDb title pages, or authoritative filmographies) so candidate actress sets can be created per specific work/version.
- query_shape_implication: Run narrow, title-disambiguation queries first (e.g., 'Third Person disambiguation' and 'Third Person (year) cast' for each candidate year found) and a small set of version-specific lookups for 'From Here to Eternity' (1953 and 1979) to extract lead actresses; this produces compact named-actor lists to intersect in the subsequent step.

to_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Narrow to the single most likely candidate for each ambiguous title: treat 'Third Person' as the 2013 feature film (the most prominent modern film by that title) and 'From Here to Eternity' as the original 1953 film. Retrieve the top-billed female cast (lead actresses) for those two specific entries to produce compact candidate actress sets for a direct intersection step.
- anchors: Third Person (2013 film) — cast/top-billed actors, From Here to Eternity (1953 film) — cast/top-billed actresses, Wikipedia or IMDb title pages for each film (cast sections), Lead billing / 'starring' lines on film pages
- bridge_clues: exact title + year (e.g., 'Third Person 2013 cast', 'From Here to Eternity 1953 cast'), sections labeled 'Starring' or top-billed cast, female names listed among top 3–5 billed performers, role names or 'as' annotations confirming performer appearance
- noisy_or_distracting_clues: other works titled 'Third Person' (short films, books, songs), later remakes or TV adaptations of From Here to Eternity (1979 miniseries) if the question intends a different version, male lead names and supporting male cast (not needed for actress intersection), crew, production, trivia, soundtrack, and release-date minutiae
- expected_evidence_type: Authoritative cast lists or 'Starring' sections from film pages (Wikipedia/IMDb/reliable filmographies) showing top-billed performers with clear ordering so a concise female-actor candidate set can be extracted for each specified title.
- query_shape_implication: Run two narrow queries: 'Third Person 2013 cast' and 'From Here to Eternity 1953 cast' (or targeted lookups of their Wikipedia/IMDb pages), then extract the top-billed female names (e.g., the first 2–4 actresses listed) to produce small, comparable sets for the next step.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the title 'Third Person' (list all films/TV works with that title and their release years) and pull the top-billed actresses for each candidate; simultaneously confirm which specific version(s) of 'From Here to Eternity' are relevant by listing the common versions and their principal actresses. The goal is to produce candidate actor sets per specific title/version so the next step can do direct cast-list intersection.
- anchors: Third Person (disambiguation), Third Person (film) — candidate years/entries (e.g., 2013), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: work title + release year (to disambiguate similarly titled works), lead/billed actresses for each candidate Third Person, lead/billed actresses for each candidate From Here to Eternity version, short film/TV synopses to confirm which cast lists are primary (e.g., 'starring', 'lead')
- noisy_or_distracting_clues: unrelated items on disambiguation pages (books, plays, songs titled 'Third Person'), other similarly named films (e.g., 'The Third Man', 'Third Wheel'), spin-off or stage adaptations of 'From Here to Eternity' (musical, live shows), celebrity names surfaced by broad searches that are not credited as cast
- expected_evidence_type: Disambiguation pages and individual film/TV pages or reliable filmographies that list release year and top-billed cast (Wikipedia film pages, IMDb title pages, or authoritative filmographies) so candidate actress sets can be created per specific work/version.
- query_shape_implication: Run narrow, title-disambiguation queries first (e.g., 'Third Person disambiguation' and 'Third Person (year) cast' for each candidate year found) and a small set of version-specific lookups for 'From Here to Eternity' (1953 and 1979) to extract lead actresses; this produces compact named-actor lists to intersect in the subsequent step.

to_state:
- name: Rmid_iter3_split1
- kind: generated_midpoint
- retrieval_focus: Reduce the broad disambiguation step by narrowing 'Third Person' to the small set of likely film/TV title candidates (prioritize the prominent 2013 feature but also detect any other notable films/TV works titled 'Third Person' that list credited actresses). At the same time, pull principal female cast lists for both commonly-referenced versions of 'From Here to Eternity' (the 1953 feature and the 1979 miniseries). Produce compact candidate actress lists for each specific title/version so the next step can perform a direct intersection.
- anchors: Third Person (disambiguation) page, Third Person (2013 film) — cast/top-billed performers, Other notable 'Third Person' title(s) (if present) — cast/top-billed performers, From Here to Eternity (1953 film) — cast/top-billed actresses, From Here to Eternity (1979 miniseries) — cast/top-billed actresses
- bridge_clues: exact title + release year to disambiguate (e.g., 'Third Person 2013 cast'), 'Starring' or 'Cast' sections that list top-billed performers, female names appearing in the top 2–5 billed positions for each candidate, role annotations ('as ...') or billing order to confirm primary vs. minor appearance, disambiguation page markers that label entries as 'film', 'TV series', 'short', or 'novel' to filter non-film items
- noisy_or_distracting_clues: non-film items on disambiguation pages (books, plays, songs titled 'Third Person'), minor short films, student films, or obscure festival entries with limited cast info, male-only cast listings or extensive full cast lists that bury principal actresses, production, crew, trivia, soundtrack, and remake notes that do not list principal cast
- expected_evidence_type: Authoritative title pages or filmographies (Wikipedia film/TV pages, IMDb title pages, or reliable film reference sites) showing release year and clear 'Starring'/'Cast' sections where top-billed female performers are identifiable.
- query_shape_implication: Run a small set of focused lookups: 'Third Person disambiguation' to find candidate titles, 'Third Person 2013 cast' and equivalent 'Third Person (other-year) cast' for any other prominent entries found, plus 'From Here to Eternity 1953 cast' and 'From Here to Eternity 1979 cast'. Extract compact lists of the top-billed actresses (2–4 names) per candidate for later intersection.

---

### 118__split2__seg1__right

- idx: 118
- split_iter: 2
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.85
- why_larger: Segment B's from_state performs a full disambiguation across all 'Third Person' works and pulls top-billed actresses for each candidate (a broad, multi-entity retrieval). Its to_state then collapses that wide candidate set to a single-year selection for both titles. That is a bigger retrieval-focus/anchor reduction than A, whose from_state was already narrowed (prioritizing 2013 and specific From Here to Eternity versions) before making the same single-candidate choice.

**Question**

What acress starred in both "Third Person" and "From Here to Eternity"?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the title 'Third Person' (list all films/TV works with that title and their release years) and pull the top-billed actresses for each candidate; simultaneously confirm which specific version(s) of 'From Here to Eternity' are relevant by listing the common versions and their principal actresses. The goal is to produce candidate actor sets per specific title/version so the next step can do direct cast-list intersection.
- anchors: Third Person (disambiguation), Third Person (film) — candidate years/entries (e.g., 2013), From Here to Eternity (1953 film), From Here to Eternity (1979 miniseries)
- bridge_clues: work title + release year (to disambiguate similarly titled works), lead/billed actresses for each candidate Third Person, lead/billed actresses for each candidate From Here to Eternity version, short film/TV synopses to confirm which cast lists are primary (e.g., 'starring', 'lead')
- noisy_or_distracting_clues: unrelated items on disambiguation pages (books, plays, songs titled 'Third Person'), other similarly named films (e.g., 'The Third Man', 'Third Wheel'), spin-off or stage adaptations of 'From Here to Eternity' (musical, live shows), celebrity names surfaced by broad searches that are not credited as cast
- expected_evidence_type: Disambiguation pages and individual film/TV pages or reliable filmographies that list release year and top-billed cast (Wikipedia film pages, IMDb title pages, or authoritative filmographies) so candidate actress sets can be created per specific work/version.
- query_shape_implication: Run narrow, title-disambiguation queries first (e.g., 'Third Person disambiguation' and 'Third Person (year) cast' for each candidate year found) and a small set of version-specific lookups for 'From Here to Eternity' (1953 and 1979) to extract lead actresses; this produces compact named-actor lists to intersect in the subsequent step.

to_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Narrow to the single most likely candidate for each ambiguous title: treat 'Third Person' as the 2013 feature film (the most prominent modern film by that title) and 'From Here to Eternity' as the original 1953 film. Retrieve the top-billed female cast (lead actresses) for those two specific entries to produce compact candidate actress sets for a direct intersection step.
- anchors: Third Person (2013 film) — cast/top-billed actors, From Here to Eternity (1953 film) — cast/top-billed actresses, Wikipedia or IMDb title pages for each film (cast sections), Lead billing / 'starring' lines on film pages
- bridge_clues: exact title + year (e.g., 'Third Person 2013 cast', 'From Here to Eternity 1953 cast'), sections labeled 'Starring' or top-billed cast, female names listed among top 3–5 billed performers, role names or 'as' annotations confirming performer appearance
- noisy_or_distracting_clues: other works titled 'Third Person' (short films, books, songs), later remakes or TV adaptations of From Here to Eternity (1979 miniseries) if the question intends a different version, male lead names and supporting male cast (not needed for actress intersection), crew, production, trivia, soundtrack, and release-date minutiae
- expected_evidence_type: Authoritative cast lists or 'Starring' sections from film pages (Wikipedia/IMDb/reliable filmographies) showing top-billed performers with clear ordering so a concise female-actor candidate set can be extracted for each specified title.
- query_shape_implication: Run two narrow queries: 'Third Person 2013 cast' and 'From Here to Eternity 1953 cast' (or targeted lookups of their Wikipedia/IMDb pages), then extract the top-billed female names (e.g., the first 2–4 actresses listed) to produce small, comparable sets for the next step.

**Sub segment**

from_state:
- name: Rmid_iter3_split1
- kind: generated_midpoint
- retrieval_focus: Reduce the broad disambiguation step by narrowing 'Third Person' to the small set of likely film/TV title candidates (prioritize the prominent 2013 feature but also detect any other notable films/TV works titled 'Third Person' that list credited actresses). At the same time, pull principal female cast lists for both commonly-referenced versions of 'From Here to Eternity' (the 1953 feature and the 1979 miniseries). Produce compact candidate actress lists for each specific title/version so the next step can perform a direct intersection.
- anchors: Third Person (disambiguation) page, Third Person (2013 film) — cast/top-billed performers, Other notable 'Third Person' title(s) (if present) — cast/top-billed performers, From Here to Eternity (1953 film) — cast/top-billed actresses, From Here to Eternity (1979 miniseries) — cast/top-billed actresses
- bridge_clues: exact title + release year to disambiguate (e.g., 'Third Person 2013 cast'), 'Starring' or 'Cast' sections that list top-billed performers, female names appearing in the top 2–5 billed positions for each candidate, role annotations ('as ...') or billing order to confirm primary vs. minor appearance, disambiguation page markers that label entries as 'film', 'TV series', 'short', or 'novel' to filter non-film items
- noisy_or_distracting_clues: non-film items on disambiguation pages (books, plays, songs titled 'Third Person'), minor short films, student films, or obscure festival entries with limited cast info, male-only cast listings or extensive full cast lists that bury principal actresses, production, crew, trivia, soundtrack, and remake notes that do not list principal cast
- expected_evidence_type: Authoritative title pages or filmographies (Wikipedia film/TV pages, IMDb title pages, or reliable film reference sites) showing release year and clear 'Starring'/'Cast' sections where top-billed female performers are identifiable.
- query_shape_implication: Run a small set of focused lookups: 'Third Person disambiguation' to find candidate titles, 'Third Person 2013 cast' and equivalent 'Third Person (other-year) cast' for any other prominent entries found, plus 'From Here to Eternity 1953 cast' and 'From Here to Eternity 1979 cast'. Extract compact lists of the top-billed actresses (2–4 names) per candidate for later intersection.

to_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Narrow to the single most likely candidate for each ambiguous title: treat 'Third Person' as the 2013 feature film (the most prominent modern film by that title) and 'From Here to Eternity' as the original 1953 film. Retrieve the top-billed female cast (lead actresses) for those two specific entries to produce compact candidate actress sets for a direct intersection step.
- anchors: Third Person (2013 film) — cast/top-billed actors, From Here to Eternity (1953 film) — cast/top-billed actresses, Wikipedia or IMDb title pages for each film (cast sections), Lead billing / 'starring' lines on film pages
- bridge_clues: exact title + year (e.g., 'Third Person 2013 cast', 'From Here to Eternity 1953 cast'), sections labeled 'Starring' or top-billed cast, female names listed among top 3–5 billed performers, role names or 'as' annotations confirming performer appearance
- noisy_or_distracting_clues: other works titled 'Third Person' (short films, books, songs), later remakes or TV adaptations of From Here to Eternity (1979 miniseries) if the question intends a different version, male lead names and supporting male cast (not needed for actress intersection), crew, production, trivia, soundtrack, and release-date minutiae
- expected_evidence_type: Authoritative cast lists or 'Starring' sections from film pages (Wikipedia/IMDb/reliable filmographies) showing top-billed performers with clear ordering so a concise female-actor candidate set can be extracted for each specified title.
- query_shape_implication: Run two narrow queries: 'Third Person 2013 cast' and 'From Here to Eternity 1953 cast' (or targeted lookups of their Wikipedia/IMDb pages), then extract the top-billed female names (e.g., the first 2–4 actresses listed) to produce small, comparable sets for the next step.

---

### 118__split3__seg2__left

- idx: 118
- split_iter: 3
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: Segment A makes a stronger, more decisive narrowing: it commits each ambiguous title to a single specific-year film (Third Person → 2013; From Here to Eternity → 1953) and shifts retrieval focus to retrieving top-billed female casts for those two exact entries. Segment B is more conservative — it prioritizes the same senses but preserves fallbacks (other Third Person films and the 1979 miniseries) and thus changes the retrieval focus less. A therefore produces the larger entity-disambiguation/anchor update and a bigger jump toward answerability.

**Question**

What acress starred in both "Third Person" and "From Here to Eternity"?

**Full segment: R_i -> R_next**

from_state:
- name: Rmid_iter3_split1
- kind: generated_midpoint
- retrieval_focus: Reduce the broad disambiguation step by narrowing 'Third Person' to the small set of likely film/TV title candidates (prioritize the prominent 2013 feature but also detect any other notable films/TV works titled 'Third Person' that list credited actresses). At the same time, pull principal female cast lists for both commonly-referenced versions of 'From Here to Eternity' (the 1953 feature and the 1979 miniseries). Produce compact candidate actress lists for each specific title/version so the next step can perform a direct intersection.
- anchors: Third Person (disambiguation) page, Third Person (2013 film) — cast/top-billed performers, Other notable 'Third Person' title(s) (if present) — cast/top-billed performers, From Here to Eternity (1953 film) — cast/top-billed actresses, From Here to Eternity (1979 miniseries) — cast/top-billed actresses
- bridge_clues: exact title + release year to disambiguate (e.g., 'Third Person 2013 cast'), 'Starring' or 'Cast' sections that list top-billed performers, female names appearing in the top 2–5 billed positions for each candidate, role annotations ('as ...') or billing order to confirm primary vs. minor appearance, disambiguation page markers that label entries as 'film', 'TV series', 'short', or 'novel' to filter non-film items
- noisy_or_distracting_clues: non-film items on disambiguation pages (books, plays, songs titled 'Third Person'), minor short films, student films, or obscure festival entries with limited cast info, male-only cast listings or extensive full cast lists that bury principal actresses, production, crew, trivia, soundtrack, and remake notes that do not list principal cast
- expected_evidence_type: Authoritative title pages or filmographies (Wikipedia film/TV pages, IMDb title pages, or reliable film reference sites) showing release year and clear 'Starring'/'Cast' sections where top-billed female performers are identifiable.
- query_shape_implication: Run a small set of focused lookups: 'Third Person disambiguation' to find candidate titles, 'Third Person 2013 cast' and equivalent 'Third Person (other-year) cast' for any other prominent entries found, plus 'From Here to Eternity 1953 cast' and 'From Here to Eternity 1979 cast'. Extract compact lists of the top-billed actresses (2–4 names) per candidate for later intersection.

to_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Narrow to the single most likely candidate for each ambiguous title: treat 'Third Person' as the 2013 feature film (the most prominent modern film by that title) and 'From Here to Eternity' as the original 1953 film. Retrieve the top-billed female cast (lead actresses) for those two specific entries to produce compact candidate actress sets for a direct intersection step.
- anchors: Third Person (2013 film) — cast/top-billed actors, From Here to Eternity (1953 film) — cast/top-billed actresses, Wikipedia or IMDb title pages for each film (cast sections), Lead billing / 'starring' lines on film pages
- bridge_clues: exact title + year (e.g., 'Third Person 2013 cast', 'From Here to Eternity 1953 cast'), sections labeled 'Starring' or top-billed cast, female names listed among top 3–5 billed performers, role names or 'as' annotations confirming performer appearance
- noisy_or_distracting_clues: other works titled 'Third Person' (short films, books, songs), later remakes or TV adaptations of From Here to Eternity (1979 miniseries) if the question intends a different version, male lead names and supporting male cast (not needed for actress intersection), crew, production, trivia, soundtrack, and release-date minutiae
- expected_evidence_type: Authoritative cast lists or 'Starring' sections from film pages (Wikipedia/IMDb/reliable filmographies) showing top-billed performers with clear ordering so a concise female-actor candidate set can be extracted for each specified title.
- query_shape_implication: Run two narrow queries: 'Third Person 2013 cast' and 'From Here to Eternity 1953 cast' (or targeted lookups of their Wikipedia/IMDb pages), then extract the top-billed female names (e.g., the first 2–4 actresses listed) to produce small, comparable sets for the next step.

**Sub segment**

from_state:
- name: Rmid_iter3_split1
- kind: generated_midpoint
- retrieval_focus: Reduce the broad disambiguation step by narrowing 'Third Person' to the small set of likely film/TV title candidates (prioritize the prominent 2013 feature but also detect any other notable films/TV works titled 'Third Person' that list credited actresses). At the same time, pull principal female cast lists for both commonly-referenced versions of 'From Here to Eternity' (the 1953 feature and the 1979 miniseries). Produce compact candidate actress lists for each specific title/version so the next step can perform a direct intersection.
- anchors: Third Person (disambiguation) page, Third Person (2013 film) — cast/top-billed performers, Other notable 'Third Person' title(s) (if present) — cast/top-billed performers, From Here to Eternity (1953 film) — cast/top-billed actresses, From Here to Eternity (1979 miniseries) — cast/top-billed actresses
- bridge_clues: exact title + release year to disambiguate (e.g., 'Third Person 2013 cast'), 'Starring' or 'Cast' sections that list top-billed performers, female names appearing in the top 2–5 billed positions for each candidate, role annotations ('as ...') or billing order to confirm primary vs. minor appearance, disambiguation page markers that label entries as 'film', 'TV series', 'short', or 'novel' to filter non-film items
- noisy_or_distracting_clues: non-film items on disambiguation pages (books, plays, songs titled 'Third Person'), minor short films, student films, or obscure festival entries with limited cast info, male-only cast listings or extensive full cast lists that bury principal actresses, production, crew, trivia, soundtrack, and remake notes that do not list principal cast
- expected_evidence_type: Authoritative title pages or filmographies (Wikipedia film/TV pages, IMDb title pages, or reliable film reference sites) showing release year and clear 'Starring'/'Cast' sections where top-billed female performers are identifiable.
- query_shape_implication: Run a small set of focused lookups: 'Third Person disambiguation' to find candidate titles, 'Third Person 2013 cast' and equivalent 'Third Person (other-year) cast' for any other prominent entries found, plus 'From Here to Eternity 1953 cast' and 'From Here to Eternity 1979 cast'. Extract compact lists of the top-billed actresses (2–4 names) per candidate for later intersection.

to_state:
- name: Rmid_iter4_split2
- kind: generated_midpoint
- retrieval_focus: Commit 'Third Person' to the film sense and prioritize the 2013 feature as the primary candidate while still collecting cast lists for any other notable film titled 'Third Person'. For 'From Here to Eternity', prioritize the original 1953 film but keep the 1979 miniseries as a fallback. Return compact top-billed female-cast lists for each candidate title/version so the next step can resolve a direct intersection.
- anchors: Third Person (disambiguation) — identify entries labeled 'film' only, Third Person (2013 film) — 'Starring' / cast section, Any other notable Third Person film entry (if present) — cast/top billing, From Here to Eternity (1953 film) — 'Starring' / cast section, From Here to Eternity (1979 miniseries) — cast section (fallback)
- bridge_clues: exact title + 'film' marker (e.g., 'Third Person film' or 'Third Person 2013') to exclude books/songs/plays, sections labeled 'Starring' or 'Cast' showing billing order, female names appearing among the top 2–4 billed performers for each film candidate, role annotations ('as ...') or billing order to confirm presence rather than cameo/extra
- noisy_or_distracting_clues: non-film disambiguation entries (books, songs, plays) for 'Third Person', obscure short films or festival shorts titled 'Third Person' with incomplete cast data, long full cast lists where principal actresses are buried among many names, production notes, crew lists, trivia, soundtrack pages that do not list principal cast
- expected_evidence_type: Authoritative title pages or filmographies (Wikipedia film pages, IMDb title pages, or other reliable film-reference sites) with clear 'Starring'/'Cast' sections that list top-billed performers and release year.
- query_shape_implication: Run targeted lookups: 'Third Person 2013 cast', 'Third Person (film) cast' for any other film-year candidates discovered on the disambiguation page, plus 'From Here to Eternity 1953 cast' (and optionally 'From Here to Eternity 1979 cast' as fallback). Extract 2–4 top-billed female names per candidate into compact lists for later intersection.

---
