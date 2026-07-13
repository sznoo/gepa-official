# v0 pass but v02 semantic-feedback prompt fail

## 108__split1__seg1__left
- idx: 108
- split_iter: 1
- task_kind: left_recovery
- expected: A
- v0 predicted: A
- v02 predicted: B
- v0 why: Segment A moves from a disambiguation intent to actually obtaining the canonical 'Solo (Australian soft drink)' in retrieved_titles — it performs the core entity-anchor correction (finding the correct Solo page). Segment B only narrows the next-step extraction (infobox/lead) without showing the retrieval result, so A is the larger retrieval-focus change.
- v02 why: Segment B adds a substantive shift from simply disambiguating and retrieving the Solo page (A) to explicitly targeting and extracting specific evidence types (infobox/lead lines and manufacturer/production statements). That requires changing the prompt to emphasize extraction-style queries, concrete infobox anchors, and explicit evidence fields rather than just locating the canonical page — a broader semantic change to retrieval instructions.

### Full segment
from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate 'Solo' and retrieve the canonical 'Solo (Australian soft drink)' page or an authoritative manufacturer page that explicitly states Solo's country of origin/production (Australia) so it can be compared to La Croix (United States).
- anchors: ['Solo (Australian soft drink)', 'Solo (Norwegian soft drink)', 'Solo (soft drink)', 'La Croix Sparkling Water', 'United States', 'Australia', 'Schweppes Australia', 'Asahi/Distributor']
- bridge_clues: ["Presence of a page titled 'Solo (Australian soft drink)' in search results", "Lead/infobox text on the Solo page stating 'Country of origin' or 'Origin: Australia' or production/manufacturer located in Australia", 'Manufacturer or distributor entries (e.g., Schweppes Australia) on the Solo page that imply Australian production', 'Explicit disambiguation markers distinguishing Australian Solo from a Norwegian Solo']
- noisy_or_distracting_clues: ["Search hits for 'Solo (Norwegian soft drink)' or other regional 'Solo' brands", 'Unrelated beverage pages (Trend Drinks, Geo. Hall & Sons, Rubicon, Guaraná Antarctica)', "Global manufacturer pages that mention Schweppes/Asahi in other countries without specifying Solo's production location"]
- expected_evidence_type: A short authoritative page (Wikipedia article infobox/lead or manufacturer's product page) that explicitly states Solo's country of origin/production (e.g., 'Country of origin: Australia' or a clear manufacturer/production location in Australia).
- query_shape_implication: Use a concise disambiguation-style query targeting the canonical page title or the phrase 'Solo (Australian soft drink) country of origin' to avoid regional variants and noisy brand pages; this is a single-entity retrieval step focused on resolving ambiguity.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Solo (Australian soft drink)', 'Trend Drinks', 'Geo. Hall &amp; Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: ['La Croix (United States)', 'Solo (Australian soft drink)', 'Solo (Norwegian soft drink)']
- bridge_clues: ['summary states La Croix produced in United States (La Crosse, Wisconsin)', 'summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink', "retrieved title 'Solo (Australian soft drink)' is present"]
- noisy_or_distracting_clues: ['Trend Drinks', 'Geo. Hall & Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

### Sub segment
from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate 'Solo' and retrieve the canonical 'Solo (Australian soft drink)' page or an authoritative manufacturer page that explicitly states Solo's country of origin/production (Australia) so it can be compared to La Croix (United States).
- anchors: ['Solo (Australian soft drink)', 'Solo (Norwegian soft drink)', 'Solo (soft drink)', 'La Croix Sparkling Water', 'United States', 'Australia', 'Schweppes Australia', 'Asahi/Distributor']
- bridge_clues: ["Presence of a page titled 'Solo (Australian soft drink)' in search results", "Lead/infobox text on the Solo page stating 'Country of origin' or 'Origin: Australia' or production/manufacturer located in Australia", 'Manufacturer or distributor entries (e.g., Schweppes Australia) on the Solo page that imply Australian production', 'Explicit disambiguation markers distinguishing Australian Solo from a Norwegian Solo']
- noisy_or_distracting_clues: ["Search hits for 'Solo (Norwegian soft drink)' or other regional 'Solo' brands", 'Unrelated beverage pages (Trend Drinks, Geo. Hall & Sons, Rubicon, Guaraná Antarctica)', "Global manufacturer pages that mention Schweppes/Asahi in other countries without specifying Solo's production location"]
- expected_evidence_type: A short authoritative page (Wikipedia article infobox/lead or manufacturer's product page) that explicitly states Solo's country of origin/production (e.g., 'Country of origin: Australia' or a clear manufacturer/production location in Australia).
- query_shape_implication: Use a concise disambiguation-style query targeting the canonical page title or the phrase 'Solo (Australian soft drink) country of origin' to avoid regional variants and noisy brand pages; this is a single-entity retrieval step focused on resolving ambiguity.

to_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Target the Solo (Australian soft drink) page and extract the lead/infobox lines that state country of origin/production and the named manufacturer/distributor (evidence that Solo is produced in Australia).
- anchors: ['Solo (Australian soft drink)', 'infobox/lead sentence', 'Country of origin: Australia', 'Manufacturer / Distributor (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil)', 'Production location / brewed/produced in']
- bridge_clues: ["Lead sentence beginning with 'Solo is an Australian...' or similar", "Infobox field 'Origin' or 'Country' listed as Australia", 'Explicit mention of manufacturer/distributor that operates in Australia (Schweppes Australia, Asahi, etc.)', "Phrases like 'Australian lemon-flavoured soft drink' or 'produced in Australia' in the page lead/intro"]
- noisy_or_distracting_clues: ["Pages for 'Solo (Norwegian soft drink)' or other regional Solo brands", 'General beverage manufacturer pages that mention Schweppes/Asahi in multiple countries without linking Solo to Australia', 'Lists of soft drinks where Solo appears without context about origin', "News/articles about distribution deals that don't state production country"]
- expected_evidence_type: Short authoritative textual evidence from the Solo page (Wikipedia infobox/lead or manufacturer product page) explicitly stating country of origin/production (Australia) and/or naming the Australian manufacturer/distributor.
- query_shape_implication: A concise extraction-style query targeting the canonical Solo (Australian soft drink) page and its infobox/lead (e.g., phrasing that requests 'Solo (Australian soft drink) infobox origin' or 'Solo lead sentence country of origin') to avoid returning regional variants or generic brand lists.

---

## 108__split1__seg1__right
- idx: 108
- split_iter: 1
- task_kind: right_recovery
- expected: A
- v0 predicted: A
- v02 predicted: B
- v0 why: Segment A requires resolving the ambiguous 'Solo' entity (disambiguation to the Australian Solo) and shifting retrieval focus to the canonical Solo page — a substantive entity-anchor correction. Segment B is a narrower extraction step (pulling infobox/lead once the correct page is targeted). The disambiguation/change of retrieval target in A is the larger update.
- v02 why: Segment B requires a stronger refocus: not just disambiguating the 'Solo' title (as in A) but targeting specific evidence fields (infobox/lead/manufacturer) and an extraction-style query. That changes the retrieval specification more (expected evidence family and extraction shape) than A's primarily disambiguation/noise-avoidance instruction.

### Full segment
from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate 'Solo' and retrieve the canonical 'Solo (Australian soft drink)' page or an authoritative manufacturer page that explicitly states Solo's country of origin/production (Australia) so it can be compared to La Croix (United States).
- anchors: ['Solo (Australian soft drink)', 'Solo (Norwegian soft drink)', 'Solo (soft drink)', 'La Croix Sparkling Water', 'United States', 'Australia', 'Schweppes Australia', 'Asahi/Distributor']
- bridge_clues: ["Presence of a page titled 'Solo (Australian soft drink)' in search results", "Lead/infobox text on the Solo page stating 'Country of origin' or 'Origin: Australia' or production/manufacturer located in Australia", 'Manufacturer or distributor entries (e.g., Schweppes Australia) on the Solo page that imply Australian production', 'Explicit disambiguation markers distinguishing Australian Solo from a Norwegian Solo']
- noisy_or_distracting_clues: ["Search hits for 'Solo (Norwegian soft drink)' or other regional 'Solo' brands", 'Unrelated beverage pages (Trend Drinks, Geo. Hall & Sons, Rubicon, Guaraná Antarctica)', "Global manufacturer pages that mention Schweppes/Asahi in other countries without specifying Solo's production location"]
- expected_evidence_type: A short authoritative page (Wikipedia article infobox/lead or manufacturer's product page) that explicitly states Solo's country of origin/production (e.g., 'Country of origin: Australia' or a clear manufacturer/production location in Australia).
- query_shape_implication: Use a concise disambiguation-style query targeting the canonical page title or the phrase 'Solo (Australian soft drink) country of origin' to avoid regional variants and noisy brand pages; this is a single-entity retrieval step focused on resolving ambiguity.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Solo (Australian soft drink)', 'Trend Drinks', 'Geo. Hall &amp; Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: ['La Croix (United States)', 'Solo (Australian soft drink)', 'Solo (Norwegian soft drink)']
- bridge_clues: ['summary states La Croix produced in United States (La Crosse, Wisconsin)', 'summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink', "retrieved title 'Solo (Australian soft drink)' is present"]
- noisy_or_distracting_clues: ['Trend Drinks', 'Geo. Hall & Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

### Sub segment
from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Target the Solo (Australian soft drink) page and extract the lead/infobox lines that state country of origin/production and the named manufacturer/distributor (evidence that Solo is produced in Australia).
- anchors: ['Solo (Australian soft drink)', 'infobox/lead sentence', 'Country of origin: Australia', 'Manufacturer / Distributor (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil)', 'Production location / brewed/produced in']
- bridge_clues: ["Lead sentence beginning with 'Solo is an Australian...' or similar", "Infobox field 'Origin' or 'Country' listed as Australia", 'Explicit mention of manufacturer/distributor that operates in Australia (Schweppes Australia, Asahi, etc.)', "Phrases like 'Australian lemon-flavoured soft drink' or 'produced in Australia' in the page lead/intro"]
- noisy_or_distracting_clues: ["Pages for 'Solo (Norwegian soft drink)' or other regional Solo brands", 'General beverage manufacturer pages that mention Schweppes/Asahi in multiple countries without linking Solo to Australia', 'Lists of soft drinks where Solo appears without context about origin', "News/articles about distribution deals that don't state production country"]
- expected_evidence_type: Short authoritative textual evidence from the Solo page (Wikipedia infobox/lead or manufacturer product page) explicitly stating country of origin/production (Australia) and/or naming the Australian manufacturer/distributor.
- query_shape_implication: A concise extraction-style query targeting the canonical Solo (Australian soft drink) page and its infobox/lead (e.g., phrasing that requests 'Solo (Australian soft drink) infobox origin' or 'Solo lead sentence country of origin') to avoid returning regional variants or generic brand lists.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Solo (Australian soft drink)', 'Trend Drinks', 'Geo. Hall &amp; Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: ['La Croix (United States)', 'Solo (Australian soft drink)', 'Solo (Norwegian soft drink)']
- bridge_clues: ['summary states La Croix produced in United States (La Crosse, Wisconsin)', 'summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink', "retrieved title 'Solo (Australian soft drink)' is present"]
- noisy_or_distracting_clues: ['Trend Drinks', 'Geo. Hall & Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

---

## 108__split3__seg3__right
- idx: 108
- split_iter: 3
- task_kind: right_recovery
- expected: B
- v0 predicted: B
- v02 predicted: tie
- v0 why: Segment B introduces an explicit disambiguation step to resolve which 'Solo' is meant before fetching product info, correcting an ambiguous/noisy entity anchor and changing the retrieval shape (disambiguation → targeted evidence). Segment A already assumes the Australian Solo and only needs a narrow extraction, so B entails a larger retrieval-focus and entity-correction update.
- v02 why: Both transitions require only minor, similar prompt updates: preserve the Solo-vs-La Croix comparison target, disambiguate which 'Solo' to target (avoid the Norwegian variant), and issue a short extraction-style query for Solo's country. Neither transition introduces a substantially different retrieval focus or new bridge relation.

### Full segment
from_state:
- name: Rmid_iter3_split2
- kind: generated_midpoint
- retrieval_focus: First disambiguate which 'Solo' is intended by retrieving the Solo disambiguation/summary and any immediate manufacturer or product-summary lines that link the brand name to a country (e.g., 'Solo (Australian soft drink)' or a manufacturer page that explicitly ties Solo to Australia). This narrows scope before fetching full product pages.
- anchors: ["Solo (disambiguation) / 'Solo (soft drink)' summary line", "Disambiguation entry that points to 'Solo (Australian soft drink)'", 'Short lead/infobox lines from Solo (Australian soft drink) confirming country or origin', 'Manufacturer/distributor short page or header (e.g., Schweppes Australia, Asahi, Coca-Cola Amatil) that mentions Solo']
- bridge_clues: ["Disambiguation text: 'Solo may refer to...' with a line for the Australian soft drink", "Lead sentence on Solo (Australian soft drink) beginning 'Solo is an Australian...' or 'Solo is a lemon-flavoured soft drink produced in Australia'", "Infobox or parenthetical note that lists 'Country of origin: Australia' or similar", 'Short manufacturer header stating they produce/distribute Solo in Australia']
- noisy_or_distracting_clues: ['Entries for Solo (Norwegian soft drink) or other regional variants that could be mistaken for the Australian product', 'Long lists of beverages or manufacturer pages that mention many brands without clear country attribution', 'News/distribution articles that mention global companies (Schweppes, Asahi) without explicitly tying Solo to a production country', 'Unrelated beverage pages (Trend Drinks, V (drink), Guaraná Antarctica) that surface in broad queries']
- expected_evidence_type: Short, authoritative disambiguation line or one-sentence lead/infobox text that unambiguously links 'Solo' to the Australian product (or indicates multiple regional products), and/or a manufacturer header that names Australia as the production/origin location.
- query_shape_implication: A concise disambiguation-style query that first asks for 'Solo (soft drink) disambiguation' or 'Solo disambiguation lead' and/or a tight extraction like 'Solo (Australian soft drink) lead/origin' to confirm which Solo to follow up on in the next retrieval.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Solo (Australian soft drink)', 'Trend Drinks', 'Geo. Hall &amp; Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: ['La Croix (United States)', 'Solo (Australian soft drink)', 'Solo (Norwegian soft drink)']
- bridge_clues: ['summary states La Croix produced in United States (La Crosse, Wisconsin)', 'summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink', "retrieved title 'Solo (Australian soft drink)' is present"]
- noisy_or_distracting_clues: ['Trend Drinks', 'Geo. Hall & Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

### Sub segment
from_state:
- name: Rmid_iter4_split3
- kind: generated_midpoint
- retrieval_focus: Fetch the Solo (Australian soft drink) page's lead sentence and infobox lines (country of origin/produced in; manufacturer/distributor) or a single-line manufacturer header that explicitly ties Solo to Australia. Keep the retrieval narrowly focused on one authoritative short snippet rather than full related pages or lists.
- anchors: ['Solo (Australian soft drink) — lead sentence', "Infobox fields: 'Country of origin', 'Manufacturer' or 'Produced in'", 'Manufacturer/distributor header that names Solo and lists Australia (e.g., Schweppes Australia / Asahi / Coca‑Cola Amatil)']
- bridge_clues: ["Lead phrase such as 'Solo is an Australian...' or 'Solo is a lemon-flavoured soft drink from Australia'", "Infobox entry 'Country of origin: Australia' or parenthetical '(Australia)' next to the brand name", 'Manufacturer/distributor one-line summary that states they produce/distribute Solo in Australia']
- noisy_or_distracting_clues: ["Entries for other 'Solo' beverages (e.g., Solo (Norwegian soft drink)) that look similar in titles", 'Long manufacturer pages listing many brands without explicit per-brand country lines', 'News articles or distributor pages mentioning global operations without tying Solo to a production country', 'Lists of beverages where Solo appears among many international brands']
- expected_evidence_type: A one-sentence lead and/or infobox line from the Solo (Australian soft drink) page or a single-line manufacturer header that unambiguously states Solo's country of origin/production (Australia).
- query_shape_implication: A highly targeted extraction-style query for a short factual snippet, e.g., 'Solo (Australian soft drink) lead sentence' or 'Solo (soft drink) infobox country of origin / manufacturer', returning 1–2 lines.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Solo (Australian soft drink)', 'Trend Drinks', 'Geo. Hall &amp; Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- retrieval_focus: Find the Solo (soft drink) page or manufacturer info that states Solo's country of production/origin so it can be compared to La Croix (United States).
- anchors: ['La Croix (United States)', 'Solo (Australian soft drink)', 'Solo (Norwegian soft drink)']
- bridge_clues: ['summary states La Croix produced in United States (La Crosse, Wisconsin)', 'summary notes Solo production country is missing and likely refers to Australian lemon-flavoured drink', "retrieved title 'Solo (Australian soft drink)' is present"]
- noisy_or_distracting_clues: ['Trend Drinks', 'Geo. Hall & Sons', 'Rubicon Drinks', 'V (drink)', 'Solo (Norwegian soft drink)', 'Guaraná Antarctica']
- expected_evidence_type: Authoritative page (Wikipedia or manufacturer/distributor source) that explicitly states Solo's country of production/origin (e.g., Australia) or identifies it as a different-country product to compare with La Croix (United States).
- query_shape_implication: Use a disambiguating, short factual query targeting Solo's origin (e.g., "Solo (Australian soft drink) country of origin", "Solo soft drink manufacturer production country") to avoid Norwegian Solo and unrelated beverage pages.

---

## 118__split1__seg1__right
- idx: 118
- split_iter: 1
- task_kind: right_recovery
- expected: A
- v0 predicted: A
- v02 predicted: B
- v0 why: Segment A moves from a broad disambiguation stance (listing all candidate 'Third Person' works and multiple versions of 'From Here to Eternity' and building actor sets per candidate) to targeted cast retrieval — a much larger change in retrieval focus and required anchor expansion/correction than B, which is already committed to a single-year pairing and only needs narrow cast lookups.
- v02 why: Segment B commits to a narrow, single-year interpretation (Third Person 2013 / From Here to Eternity 1953). Moving to the target requires adding broad disambiguation, multiple version anchors, and a more exploratory query shape (extract cast lists per candidate) — a bigger semantic shift than A, which already encodes disambiguation and multi-version candidate extraction.

### Full segment
from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the title 'Third Person' (list all films/TV works with that title and their release years) and pull the top-billed actresses for each candidate; simultaneously confirm which specific version(s) of 'From Here to Eternity' are relevant by listing the common versions and their principal actresses. The goal is to produce candidate actor sets per specific title/version so the next step can do direct cast-list intersection.
- anchors: ['Third Person (disambiguation)', 'Third Person (film) — candidate years/entries (e.g., 2013)', 'From Here to Eternity (1953 film)', 'From Here to Eternity (1979 miniseries)']
- bridge_clues: ['work title + release year (to disambiguate similarly titled works)', 'lead/billed actresses for each candidate Third Person', 'lead/billed actresses for each candidate From Here to Eternity version', "short film/TV synopses to confirm which cast lists are primary (e.g., 'starring', 'lead')"]
- noisy_or_distracting_clues: ["unrelated items on disambiguation pages (books, plays, songs titled 'Third Person')", "other similarly named films (e.g., 'The Third Man', 'Third Wheel')", "spin-off or stage adaptations of 'From Here to Eternity' (musical, live shows)", 'celebrity names surfaced by broad searches that are not credited as cast']
- expected_evidence_type: Disambiguation pages and individual film/TV pages or reliable filmographies that list release year and top-billed cast (Wikipedia film pages, IMDb title pages, or authoritative filmographies) so candidate actress sets can be created per specific work/version.
- query_shape_implication: Run narrow, title-disambiguation queries first (e.g., 'Third Person disambiguation' and 'Third Person (year) cast' for each candidate year found) and a small set of version-specific lookups for 'From Here to Eternity' (1953 and 1979) to extract lead actresses; this produces compact named-actor lists to intersect in the subsequent step.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['From Here to Eternity (TV series)', 'From Here to Eternity', 'From Here to Eternity (miniseries)', 'From Here to Eternity (disambiguation)', 'Kim Basinger', 'Donna Reed', "Heather O'Rourke"]
- retrieval_focus: Get authoritative cast lists for the specific works named (disambiguate which 'Third Person' and which version of 'From Here to Eternity') so we can find any overlapping performer.
- anchors: ['Third Person', 'Third Person (film)', 'From Here to Eternity', 'From Here to Eternity (1953 film)', 'From Here to Eternity (miniseries)', 'cast', 'Deborah Kerr', 'Donna Reed']
- bridge_clues: ['cast', 'starring', 'credited', 'filmography', 'appeared in', 'played']
- noisy_or_distracting_clues: ['From Here to Eternity (disambiguation)', 'From Here to Eternity (TV series)', 'Kim Basinger', "Heather O'Rourke"]
- expected_evidence_type: Primary film pages or reliable cast lists (Wikipedia film pages, IMDb/filmography entries, reputable biographies) showing full credited cast for each title/version.
- query_shape_implication: Issue two precise second-hop queries (exact title + 'cast' or year): e.g. 'Third Person (film) cast' and 'From Here to Eternity (1953 film) cast' (or 'From Here to Eternity (1979 miniseries) cast' if that version is intended), then intersect named cast members.

### Sub segment
from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Narrow to the single most likely candidate for each ambiguous title: treat 'Third Person' as the 2013 feature film (the most prominent modern film by that title) and 'From Here to Eternity' as the original 1953 film. Retrieve the top-billed female cast (lead actresses) for those two specific entries to produce compact candidate actress sets for a direct intersection step.
- anchors: ['Third Person (2013 film) — cast/top-billed actors', 'From Here to Eternity (1953 film) — cast/top-billed actresses', 'Wikipedia or IMDb title pages for each film (cast sections)', "Lead billing / 'starring' lines on film pages"]
- bridge_clues: ["exact title + year (e.g., 'Third Person 2013 cast', 'From Here to Eternity 1953 cast')", "sections labeled 'Starring' or top-billed cast", 'female names listed among top 3–5 billed performers', "role names or 'as' annotations confirming performer appearance"]
- noisy_or_distracting_clues: ["other works titled 'Third Person' (short films, books, songs)", 'later remakes or TV adaptations of From Here to Eternity (1979 miniseries) if the question intends a different version', 'male lead names and supporting male cast (not needed for actress intersection)', 'crew, production, trivia, soundtrack, and release-date minutiae']
- expected_evidence_type: Authoritative cast lists or 'Starring' sections from film pages (Wikipedia/IMDb/reliable filmographies) showing top-billed performers with clear ordering so a concise female-actor candidate set can be extracted for each specified title.
- query_shape_implication: Run two narrow queries: 'Third Person 2013 cast' and 'From Here to Eternity 1953 cast' (or targeted lookups of their Wikipedia/IMDb pages), then extract the top-billed female names (e.g., the first 2–4 actresses listed) to produce small, comparable sets for the next step.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['From Here to Eternity (TV series)', 'From Here to Eternity', 'From Here to Eternity (miniseries)', 'From Here to Eternity (disambiguation)', 'Kim Basinger', 'Donna Reed', "Heather O'Rourke"]
- retrieval_focus: Get authoritative cast lists for the specific works named (disambiguate which 'Third Person' and which version of 'From Here to Eternity') so we can find any overlapping performer.
- anchors: ['Third Person', 'Third Person (film)', 'From Here to Eternity', 'From Here to Eternity (1953 film)', 'From Here to Eternity (miniseries)', 'cast', 'Deborah Kerr', 'Donna Reed']
- bridge_clues: ['cast', 'starring', 'credited', 'filmography', 'appeared in', 'played']
- noisy_or_distracting_clues: ['From Here to Eternity (disambiguation)', 'From Here to Eternity (TV series)', 'Kim Basinger', "Heather O'Rourke"]
- expected_evidence_type: Primary film pages or reliable cast lists (Wikipedia film pages, IMDb/filmography entries, reputable biographies) showing full credited cast for each title/version.
- query_shape_implication: Issue two precise second-hop queries (exact title + 'cast' or year): e.g. 'Third Person (film) cast' and 'From Here to Eternity (1953 film) cast' (or 'From Here to Eternity (1979 miniseries) cast' if that version is intended), then intersect named cast members.

---

## 140__split2__seg1__right
- idx: 140
- split_iter: 2
- task_kind: right_recovery
- expected: A
- v0 predicted: A
- v02 predicted: B
- v0 why: Segment A requires an extra verification/correction step: confirm whether George Danzer (an anchored candidate) is actually a WPT champion and, if not, search the WPT winners list and cross-reference each winner's WSOP bracelet count to find a four-bracelet match. That involves both disputing an entity-anchor (Danzer's presumed WPT status) and a cross-source relation check to match WPT winners to WSOP bracelet counts. Segment B is a simpler single-hop extraction of the champions list and names without the additional verification and cross-referencing.
- v02 why: Transition B requires a broader change in retrieval instructions: move from a narrow, single-person verification to fetching and parsing an authoritative, year-by-year WPT champions list, extracting and deduplicating many candidate names. That expands anchors, changes the query shape (from targeted lookup to list extraction + parsing), and shifts expected evidence and filtering behavior—so it is a larger semantic prompt-feedback update than the focused Danzer check in A.

### Full segment
from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Verify whether the candidate George Danzer is a World Poker Tour (WPT) champion (i.e., appears on a WPT winners/champions list or tournament-results page). If he is not, identify any WPT champion who has four World Series of Poker bracelets.
- anchors: ['George Danzer', 'List of World Poker Tour champions', 'World Poker Tour winner', 'four World Series of Poker bracelets', 'WPT winners list', 'tournament results page']
- bridge_clues: ["Search for 'George Danzer World Poker Tour' or 'George Danzer WPT' to find any explicit link between Danzer and a WPT title", "Look up 'List of World Poker Tour champions' for the presence/absence of George Danzer", "If Danzer is absent, search the WPT champions list for players with 'four WSOP bracelets' to find the correct cross-over candidate"]
- noisy_or_distracting_clues: ["Pages that discuss George Danzer's WSOP bracelets and achievements but do not mention WPT results (may falsely suggest a WPT link)", 'Other player names on WPT lists (David Chiu, John Hennigan, Alexandre Gomes, etc.) that have different bracelet counts', "Articles conflating WPT event wins with WSOP bracelets or using imprecise phrasing ('World Poker Tour bracelet')", 'Local event reports or forums that mention wins but are not authoritative']
- expected_evidence_type: A WPT champions/winners list or official tournament-results page naming the winner(s) (positive evidence that Danzer did or did not win a WPT event), or an authoritative biography that explicitly states WPT titles (or their absence).
- query_shape_implication: Single-hop verification query: 'George Danzer WPT' or 'George Danzer "World Poker Tour"'; if negative, follow-up single-hop: 'List of World Poker Tour champions + "four World Series of Poker bracelets"' to find a different matching champion.

to_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Cross-reference the World Poker Tour (WPT) champions list with authoritative player bios or summaries of WSOP bracelet counts to produce a short list of WPT winners who have four World Series of Poker bracelets (or otherwise match the 'four WSOP bracelets' criterion). Do NOT yet retrieve birth dates—only identify candidate person(s) to check next.
- anchors: ['World Poker Tour champions list / WPT winners', 'players with four World Series of Poker (WSOP) bracelets', 'George Danzer', 'David Chiu', 'John Hennigan', 'Alexandre Gomes']
- bridge_clues: ["Scan an official or well-sourced 'List of World Poker Tour champions' page to extract WPT winner names.", "For each extracted WPT winner, consult their biographical entry or WSOP records to note their WSOP bracelet count (look for phrases like 'x-time World Series of Poker bracelet winner').", 'Produce a shortlist of WPT winners whose bios/records state they have four WSOP bracelets (if any).', "If George Danzer appears on the WPT winners list, include him in the shortlist; otherwise, exclude him and focus on other WPT winners who match the 'four bracelets' count."]
- noisy_or_distracting_clues: ['Pages that discuss only WSOP results without indicating WPT wins (may list bracelet counts but not WPT titles).', "Articles or fan sites that conflate WPT events with WSOP bracelets or use imprecise language ('World Poker Tour bracelet').", "WPT winners lists that include many names (need to avoid assuming bracelet counts without checking each player's bio).", 'Players on WPT lists who have many WSOP-related mentions but ambiguous bracelet counts in summary lines.']
- expected_evidence_type: A WPT champions/winners list (table or roster) plus one-line biographical entries or WSOP records for candidate winners indicating the number of WSOP bracelets (these should confirm which WPT winner(s), if any, have exactly four WSOP bracelets).
- query_shape_implication: Two-step single-hop pattern aggregated into this midpoint: (1) retrieve WPT winners list to get candidate names; (2) for each candidate, retrieve a brief authoritative bio or WSOP-record snippet mentioning 'X WSOP bracelet(s)' to filter to those with four. The next step (R_right) will take the shortlisted person and fetch their birth date.

### Sub segment
from_state:
- name: Rmid_iter3_split1
- kind: generated_midpoint
- retrieval_focus: Retrieve an authoritative, year-by-year list of World Poker Tour (WPT) champions/winners and extract the winner names (and years). Mark whether George Danzer appears on that list. Produce a cleaned list of candidate WPT winner names to be passed to the next step for WSOP-bracelet-count checks.
- anchors: ['List of World Poker Tour champions', 'World Poker Tour winners list (official site or Wikipedia)', 'WPT champions by year', 'George Danzer', 'WPT winner names (extracted list)']
- bridge_clues: ["Find an authoritative page titled like 'List of World Poker Tour champions' or 'World Poker Tour winners' (official WPT site or Wikipedia) and extract the winners' names and years.", "Scan the extracted names for 'George Danzer' and flag presence/absence.", 'Produce a deduplicated short list of WPT winner names (without yet checking WSOP bracelet counts) to feed into the next retrieval step.']
- noisy_or_distracting_clues: ["Match reports or news articles about individual WPT events that mention winners but aren't consolidated lists (may omit context or year indexing).", 'Pages focused on WSOP results or player biographies that discuss bracelets but do not confirm WPT championship status.', 'Fan sites, forum threads, or local tournament reports mixing smaller events with official WPT titles.', "Lists of poker players or tournament results that do not clearly indicate 'WPT champion' status or year."]
- expected_evidence_type: An official WPT winners/champions list or a well-sourced aggregated table (e.g., Wikipedia 'List of World Poker Tour champions') that lists winners by year and includes clear player names for extraction; a clear indication (present/absent) of George Danzer on that list.
- query_shape_implication: Single-hop retrieval to fetch and parse a champions/winners list (one document). Output is a parsed list of winner names and a flag for George Danzer's presence. The subsequent step (R_right) will take those names and query each player's WSOP bracelet count to shortlist those with four bracelets.

to_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Cross-reference the World Poker Tour (WPT) champions list with authoritative player bios or summaries of WSOP bracelet counts to produce a short list of WPT winners who have four World Series of Poker bracelets (or otherwise match the 'four WSOP bracelets' criterion). Do NOT yet retrieve birth dates—only identify candidate person(s) to check next.
- anchors: ['World Poker Tour champions list / WPT winners', 'players with four World Series of Poker (WSOP) bracelets', 'George Danzer', 'David Chiu', 'John Hennigan', 'Alexandre Gomes']
- bridge_clues: ["Scan an official or well-sourced 'List of World Poker Tour champions' page to extract WPT winner names.", "For each extracted WPT winner, consult their biographical entry or WSOP records to note their WSOP bracelet count (look for phrases like 'x-time World Series of Poker bracelet winner').", 'Produce a shortlist of WPT winners whose bios/records state they have four WSOP bracelets (if any).', "If George Danzer appears on the WPT winners list, include him in the shortlist; otherwise, exclude him and focus on other WPT winners who match the 'four bracelets' count."]
- noisy_or_distracting_clues: ['Pages that discuss only WSOP results without indicating WPT wins (may list bracelet counts but not WPT titles).', "Articles or fan sites that conflate WPT events with WSOP bracelets or use imprecise language ('World Poker Tour bracelet').", "WPT winners lists that include many names (need to avoid assuming bracelet counts without checking each player's bio).", 'Players on WPT lists who have many WSOP-related mentions but ambiguous bracelet counts in summary lines.']
- expected_evidence_type: A WPT champions/winners list (table or roster) plus one-line biographical entries or WSOP records for candidate winners indicating the number of WSOP bracelets (these should confirm which WPT winner(s), if any, have exactly four WSOP bracelets).
- query_shape_implication: Two-step single-hop pattern aggregated into this midpoint: (1) retrieve WPT winners list to get candidate names; (2) for each candidate, retrieve a brief authoritative bio or WSOP-record snippet mentioning 'X WSOP bracelet(s)' to filter to those with four. The next step (R_right) will take the shortlisted person and fetch their birth date.

---

## 149__split1__seg0__left
- idx: 149
- split_iter: 1
- task_kind: left_recovery
- expected: B
- v0 predicted: B
- v02 predicted: A
- v0 why: Segment B expands and shifts the retrieval focus more: it adds Holda/Frau Holle as active anchors and demands explicit identity claims linking hulder → Huld and Huld ↔ Holda/Frau Holle (short definitional/comparative-mythology evidence). A only narrows to philological/etymological linkage and Huld's role as a völva, deferring the Holda equation. B therefore requires a larger bridge/identity correction and a stronger change in expected evidence.
- v02 why: A changes the retrieval spec more fundamentally: it drops the Huld↔Holda/Frau Holle identity emphasis (removing those anchors/distractors) and refocuses the query on philological/etymological evidence and Huld-as-völva. B mainly tightens source style and requests explicit identity sentences but keeps the same anchors and identity target. Removing an anchor and shifting the core bridge relation is a bigger semantic update than narrowing evidence style.

### Full segment
from_state:
- name: R0_base
- kind: endpoint
- query: Huld völva Holda Holle Germanic goddess origin of hulder skogsrå Tallemaja
- retrieved_titles: ['Hulder', 'Holda', 'Huld', 'Spillaholle', 'Gussy Holl', '872 Holda', 'Frau Holle']
- retrieval_focus: Find authoritative statements and etymological evidence that equate the Swedish seductive forest-creature hulder (skogsrå) with the völva/divine figure Huld and the Germanic Holda/Frau Holle; confirm role shift from goddess/seer to folkloric forest spirit.
- anchors: ['Huld', 'Holda', 'Frau Holle', 'Hulder', 'Skogsrå', 'Völva', 'Tallemaja']
- bridge_clues: ['hulder derives from Huld / shared name root', 'Huld described as a völva or divine seer', 'Holda/Frau Holle equated with Huld', "etymology: huldr / huld = 'hidden/covered'", 'transformation from goddess/seer to folk forest spirit', 'regional names linking hulder to Huld (skogsrå, Tallemaja, ulda)']
- noisy_or_distracting_clues: ['Spillaholle', 'Gussy Holl', '872 Holda']
- expected_evidence_type: encyclopedic or folklore entries and comparative-mythology or etymology discussions that explicitly link the names (Huld/Holda) to hulder/skogsrå and describe religious/functional equivalence (völva/goddess → forest spirit).
- query_shape_implication: Multi-term, synonym-rich query: combine exact name variants with role/etymology terms (e.g., 'Huld völva etymology', 'hulder origin Huld Holda', 'skogsrå Huld Holda') and prefer scholarly/encyclopedic sources to avoid unrelated hits.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow search to authoritative etymology and comparative-mythology statements that explicitly link the Swedish hulder/skogsrå name to Huld and show Huld's identification with Holda/Frau Holle; prioritize encyclopedia/folklore/etymology entries that give short identity claims rather than broader cultural history.
- anchors: ['Hulder', 'Huld', 'Holda', 'Skogsrå', 'Völva', 'Frau Holle']
- bridge_clues: ["etymology: huldr / huld = 'hidden/covered' as name-root connection", "explicit sentence: 'the hulder is originally the same being as Huld'", 'scholarly/encyclopedic note equating Huld with Holda/Frau Holle', 'regional name citations (Tallemaja, ulda) used in etymology or name-history sections']
- noisy_or_distracting_clues: ['Coat of arms of Lardal', '872 Holda', 'Haugtussa', 'Spillaholle', 'Gussy Holl']
- expected_evidence_type: Short definitional or etymological passages in encyclopedia/folklore/dictionary entries or comparative-mythology summaries that state name-derivation and identity (e.g., a line that directly links hulder → Huld and Huld ↔ Holda/Frau Holle).
- query_shape_implication: Concise high-precision pairwise queries combining the folkloric term and candidate divine names with relationship keywords (examples to guide retrieval: 'hulder Huld etymology', 'hulder same as Holda', 'Huld völva Holda identity'), focusing on authoritative sources.

### Sub segment
from_state:
- name: R0_base
- kind: endpoint
- query: Huld völva Holda Holle Germanic goddess origin of hulder skogsrå Tallemaja
- retrieved_titles: ['Hulder', 'Holda', 'Huld', 'Spillaholle', 'Gussy Holl', '872 Holda', 'Frau Holle']
- retrieval_focus: Find authoritative statements and etymological evidence that equate the Swedish seductive forest-creature hulder (skogsrå) with the völva/divine figure Huld and the Germanic Holda/Frau Holle; confirm role shift from goddess/seer to folkloric forest spirit.
- anchors: ['Huld', 'Holda', 'Frau Holle', 'Hulder', 'Skogsrå', 'Völva', 'Tallemaja']
- bridge_clues: ['hulder derives from Huld / shared name root', 'Huld described as a völva or divine seer', 'Holda/Frau Holle equated with Huld', "etymology: huldr / huld = 'hidden/covered'", 'transformation from goddess/seer to folk forest spirit', 'regional names linking hulder to Huld (skogsrå, Tallemaja, ulda)']
- noisy_or_distracting_clues: ['Spillaholle', 'Gussy Holl', '872 Holda']
- expected_evidence_type: encyclopedic or folklore entries and comparative-mythology or etymology discussions that explicitly link the names (Huld/Holda) to hulder/skogsrå and describe religious/functional equivalence (völva/goddess → forest spirit).
- query_shape_implication: Multi-term, synonym-rich query: combine exact name variants with role/etymology terms (e.g., 'Huld völva etymology', 'hulder origin Huld Holda', 'skogsrå Huld Holda') and prefer scholarly/encyclopedic sources to avoid unrelated hits.

to_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Establish the philological/etymological link from Swedish hulder/skogsrå to the name-root huld/huldr and confirm Huld's characterization as a völva/seer in sources. This narrows the search to name-origin and role-of-Huld material without yet asserting or heavily sourcing the Huld↔Holda/Frau Holle equation.
- anchors: ['Hulder', 'Skogsrå', 'Huld', 'Völva', 'huldr / huld (name-root)', 'Tallemaja', 'ulda']
- bridge_clues: ["etymology: hulder ← huldr / huld meaning 'hidden/covered' or similar", 'encyclopedic or dictionary lines that derive hulder/skogsrå from Huld', 'descriptions in folklore or Old Norse sources identifying Huld as a völva/seer', 'regional name citations (Tallemaja, ulda) used in name-history sections', 'linguistic/philological commentary tying the personal/divine name Huld to later folk-figure names']
- noisy_or_distracting_clues: ['explicit Holda / Frau Holle articles (defer full equation to next step)', "local civic or heraldic pages (e.g., 'Coat of arms of Lardal')", "modern cultural usages and creative retellings (e.g., 'Spillaholle', 'Gussy Holl')", "catalog or list pages with numeric identifiers (e.g., '872 Holda')"]
- expected_evidence_type: Etymological dictionary entries, folklore encyclopaedia entries, comparative-mythology or name-origin sections that explicitly state hulder derives from huld/huldr and references or primary-source notes describing Huld as a völva/seer.
- query_shape_implication: Pair folkloric term + etymology and Huld + role keywords (examples to guide retrieval: 'hulder etymology huld', 'skogsrå huldr root', 'Huld völva sources'); favor linguistic/etymological and folklore-reference pages rather than broad cultural histories or explicit Huld↔Holda identity claims.

---

## 169__split1__seg0__right
- idx: 169
- split_iter: 1
- task_kind: right_recovery
- expected: A
- v0 predicted: A
- v02 predicted: B
- v0 why: Segment A shows a bigger shift from a broad, noisy starting state to a narrowly focused, authoritative credit-verification plan: it adds specific target sources, explicit bridge phrases ('"stunt double for Steve McQueen"', '"performed the motorcycle jump"'), and concrete query-shape guidance. Segment B is already largely focused and its to_state is very similar, so its transition is much smaller.
- v02 why: Transition B adds a new anchor (explicitly checking 'Bullitt'), tightens source requirements, and turns a deferred ambiguity into an immediate verification step — a broader semantic change to what entities and checks the query generator must include than the relatively small refinement in A.

### Full segment
from_state:
- name: R0_base
- kind: endpoint
- query: Bud Ekins Steve McQueen stunt double Bullitt? "The Great Escape" motorcycle stunt details who performed jump stunt credits filming location
- retrieved_titles: ['Bud Ekins', 'Stunt double', 'Stunt coordinator', 'Stunt', 'Butch Laswell', 'Corey Scott', 'Todd Bryant']
- retrieval_focus: Verify and cite which Steve McQueen film(s) Bud Ekins served as a stunt double for, with primary focus on confirming the motorcycle-stunt credit in The Great Escape and resolving the ambiguity about Bullitt.
- anchors: ['Bud Ekins', 'Steve McQueen ("The King of Cool")', 'The Great Escape', 'Bullitt']
- bridge_clues: ['motorcycle stunt / famous motorcycle jump', 'stunt double credit', 'stunt credits in filmographies/IMDb', "Stuntmen's Hall of Fame / obituary / biography entries"]
- noisy_or_distracting_clues: ['Butch Laswell', 'Corey Scott', 'Todd Bryant', "generic pages titled 'Stunt' or 'Stunt coordinator' that do not mention McQueen or Ekins"]
- expected_evidence_type: Authoritative film-credit records or reputable secondary sources (IMDb/BFI entries, film credits, biographies, obituaries, Hall of Fame pages, production notes) explicitly stating Ekins doubled McQueen on The Great Escape and listing any other films where he doubled McQueen.
- query_shape_implication: Use narrow, factual queries and source filters (e.g., 'Bud Ekins Steve McQueen The Great Escape stunt double', 'Bud Ekins Bullitt stunt double', 'who did the motorcycle jump in The Great Escape') aimed at crediting sources rather than broad 'stunt' topic searches.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow to authoritative credit-confirmation: verify that Bud Ekins served as Steve McQueen's stunt double on The Great Escape (especially the motorcycle jump) and explicitly check primary credit sources to resolve whether he also doubled McQueen in Bullitt. Prioritize obituaries, reputable biographies, film-credit databases, and Hall-of-Fame entries rather than generic 'stunt' pages.
- anchors: ['Bud Ekins', 'Steve McQueen ("The King of Cool")', 'The Great Escape', 'Bullitt', "Stuntmen's Hall of Fame / obituary"]
- bridge_clues: ['"stunt double for Steve McQueen"', '"performed the motorcycle jump"', 'credited as stuntman in filmography / IMDb / BFI', 'obituary or Hall of Fame entry mentioning The Great Escape']
- noisy_or_distracting_clues: ['Triumph TR6 Trophy (motorcycle model) references', 'Dave Ekins (relative/other rider)', "general pages titled 'Stunt' or 'Stunt coordinator' without film credits", 'motorcycling forums or fan pages that repeat claims without sourcing']
- expected_evidence_type: Short, explicit credit statements from authoritative sources (IMDb/BFI entries, NYT/THR obituaries, reputable biographies, Stuntmen's Hall of Fame) that say 'Bud Ekins served as Steve McQueen's stunt double on The Great Escape' and, separately, clear statements confirming or denying a doubling credit on Bullitt.
- query_shape_implication: Use focused phrase searches and source filters (exact phrase + site filters) such as '"Bud Ekins" "stunt double" "The Great Escape"' across reputable outlets; then a narrow follow-up search for 'Bud Ekins Bullitt' to resolve that single ambiguity. Avoid broad 'stunt' or generic motorcycle-topic queries.

### Sub segment
from_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Confirm with reliable secondary sources that Bud Ekins served as Steve McQueen’s stunt double for the motorcycle sequences in The Great Escape (especially the famous jump), prioritizing obituaries, reputable biographies, Hall-of-Fame entries, and filmography summaries. Defer a decisive check about Bullitt to a subsequent step.
- anchors: ['Bud Ekins', 'Steve McQueen ("The King of Cool")', 'The Great Escape', 'motorcycle jump / motorcycle stunt', "obituary / Stuntmen's Hall of Fame"]
- bridge_clues: ['named as stunt double for Steve McQueen on The Great Escape', 'credited with performing the motorcycle jump', 'mentions in reputable obituaries or biographies', 'filmography entries listing Ekins on The Great Escape']
- noisy_or_distracting_clues: ["generic 'stunt' pages without film-specific credits", 'motorcycling forums and fan posts repeating unsourced claims', "other stunt performers' pages (e.g., unrelated names) that do not mention Ekins/McQueen", "technical motorcycle model discussions (Triumph TR6) that don't address credits"]
- expected_evidence_type: Short, explicit statements in reputable secondary sources (major-obituary writeups, recognized filmographies, Hall-of-Fame/biography pages, or established film-reference sites) that attribute the motorcycle stunt in The Great Escape to Bud Ekins and identify him as McQueen's stunt double for those sequences.
- query_shape_implication: Move from broad topic searches to focused phrase-level searches about Ekins + The Great Escape + 'motorcycle' or 'stunt' across reputable outlets (obituaries, biographies, established film-reference pages), but do not yet enforce aggressive site-filtering or an explicit separate check for Bullitt.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow to authoritative credit-confirmation: verify that Bud Ekins served as Steve McQueen's stunt double on The Great Escape (especially the motorcycle jump) and explicitly check primary credit sources to resolve whether he also doubled McQueen in Bullitt. Prioritize obituaries, reputable biographies, film-credit databases, and Hall-of-Fame entries rather than generic 'stunt' pages.
- anchors: ['Bud Ekins', 'Steve McQueen ("The King of Cool")', 'The Great Escape', 'Bullitt', "Stuntmen's Hall of Fame / obituary"]
- bridge_clues: ['"stunt double for Steve McQueen"', '"performed the motorcycle jump"', 'credited as stuntman in filmography / IMDb / BFI', 'obituary or Hall of Fame entry mentioning The Great Escape']
- noisy_or_distracting_clues: ['Triumph TR6 Trophy (motorcycle model) references', 'Dave Ekins (relative/other rider)', "general pages titled 'Stunt' or 'Stunt coordinator' without film credits", 'motorcycling forums or fan pages that repeat claims without sourcing']
- expected_evidence_type: Short, explicit credit statements from authoritative sources (IMDb/BFI entries, NYT/THR obituaries, reputable biographies, Stuntmen's Hall of Fame) that say 'Bud Ekins served as Steve McQueen's stunt double on The Great Escape' and, separately, clear statements confirming or denying a doubling credit on Bullitt.
- query_shape_implication: Use focused phrase searches and source filters (exact phrase + site filters) such as '"Bud Ekins" "stunt double" "The Great Escape"' across reputable outlets; then a narrow follow-up search for 'Bud Ekins Bullitt' to resolve that single ambiguity. Avoid broad 'stunt' or generic motorcycle-topic queries.

---

## 180__split1__seg1__right
- idx: 180
- split_iter: 1
- task_kind: right_recovery
- expected: B
- v0 predicted: B
- v02 predicted: A
- v0 why: Segment B's from-state only aims to identify the album ordinal/title (11th) and excludes date information, so the transition must add the album anchor (identify the correct album) and then extract its precise release date. Segment A's from-state already confirms the band identity and the album title plus the release year, so its transition only requires filling in the exact day/month (a smaller, single-date refinement). Thus B requires a larger entity-anchor + date addition.
- v02 why: Segment A adds substantive new instructions beyond identifying the 11th album: it requires confirming the ambiguous phrase maps to a specific anchor (Annihilator), requests extracting the album release year (not just the title/ordinal), and explicitly warns against pulling full day/month details. This broadens the retrieval spec (additional anchor verification, extra evidence field, and refined avoidance rule) compared with B's narrower ordinal-identification task.

### Full segment
from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Confirm which studio album is Annihilator's 11th (identify the album title and verify its ordinal position in the band's official discography). Do not yet retrieve the album's release date.
- anchors: ['Annihilator discography (ordered list of studio albums)', 'studio albums only (exclude EPs/compilations/live albums)', 'ordinal position: 11th', 'album title corresponding to 11th entry']
- bridge_clues: ["The band's discography page or a reputable music database will list studio albums in chronological order and allow unambiguous counting to the 11th entry.", "Some album pages include a lead sentence like 'X is the nth studio album by Annihilator' — that directly confirms ordinal without counting.", 'Cross-checking two authoritative sources (e.g., band/Wikipedia/discography database) reduces risk of miscounting due to non-studio releases being mixed in.']
- noisy_or_distracting_clues: ['EPs, compilations, live albums and reissues that are often shown alongside studio albums and can lead to miscounting.', "Self-titled album names or similarly named releases (e.g., 'Annihilator') that might be confused with other entries.", 'Regional/label variations and deluxe editions that change listed release years but do not change album ordinal.', "References to other Canadian metal acts (e.g., Thor) in the supplied context — irrelevant to identifying Annihilator's 11th studio album."]
- expected_evidence_type: An authoritative discography or band page that either labels the album as the band's '11th studio album' or provides a clear chronological list of studio albums from which the 11th entry (album title) can be unambiguously determined.
- query_shape_implication: Focus the next retrieval on the discography or album-listing page (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') and either open the album page that explicitly states 'X is the 11th studio album' or count studio entries on the discography to extract the 11th album title. Defer querying for the release date until after the 11th album title is confirmed.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Annihilator (band)', 'Annihilator discography', 'Set the World on Fire (Annihilator album)', 'All for You (Annihilator album)', 'Metal (Annihilator album)', 'Schizo Deluxe', 'Refresh the Demon']
- retrieval_focus: Identify the band referenced (likely Annihilator), find which studio album is their 11th, and retrieve that album's official release date.
- anchors: ['Annihilator (band)', 'Annihilator discography', 'retrieved album titles (Set the World on Fire, All for You, Metal, Schizo Deluxe, Refresh the Demon)']
- bridge_clues: ["Confirm that 'highest-selling heavy metal group from Canada' refers to Annihilator via a summary or band page", 'Use the discography page to determine the ordered list of studio albums and pick the 11th entry', 'Open the 11th-album page (or the discography entry) to read the official release date']
- noisy_or_distracting_clues: ['Multiple album titles present that are not labeled by ordinal — risk of miscounting which is 11th', 'Summary mentions Thor (unrelated) and other passages with no clear link to this query, creating irrelevant context']
- expected_evidence_type: Discography listing or band page that enumerates studio albums in order, and the specific album page or discography entry that gives the album's official release date (day/month/year and region/label if available).
- query_shape_implication: First query should target the band discography (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') to get album order; second query should target the identified album name plus 'release date' (e.g., '<Album Name> release date' or 'Annihilator 11th studio album release date').

### Sub segment
from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Confirm that the phrase 'the highest-selling heavy metal group from Canada' refers to Annihilator, and identify which album in Annihilator's official studio-album sequence is the 11th (extract the album title and, if easily available, the release year only). Do not retrieve the full release date (day/month/year) yet.
- anchors: ["Verify band identity: evidence that 'highest-selling Canadian heavy metal group' = Annihilator (authoritative bio or reliable secondary source)", 'Annihilator discography (ordered list of studio albums)', 'Explicit statement or unambiguous counting that identifies the 11th studio album', 'Album title for the 11th studio album (and release year, but not full date)']
- bridge_clues: ['Band profile pages (Wikipedia lead, official band site, AllMusic) often state prominent claims and provide a discography link to confirm identity.', "Discography pages list studio albums chronologically; some album pages include phrasing like 'X is the Nth studio album by Annihilator' which directly confirms ordinal.", "Press articles or reputable music databases can corroborate the 'highest-selling' claim if the band page is ambiguous.", 'Album pages commonly show at least the release year in the infobox/header even if the exact day is elsewhere; record the year but skip detailed date fields for now.']
- noisy_or_distracting_clues: ['Some sources may label compilations, live albums or reissues alongside studio albums and cause miscounting.', 'Other Canadian metal or rock acts may appear in search results (e.g., Anvil, Thor) and distract from the target.', "Conflicting or unsourced claims about 'highest-selling' status — prefer authoritative or corroborated references.", 'Regional/label-specific release date entries that include release-day detail (avoid extracting those now).']
- expected_evidence_type: An authoritative band profile or reputable music-database discography that (a) links the 'highest-selling Canadian heavy metal group' description to Annihilator and (b) either labels the album as the band's 11th studio album or provides a clear chronological list from which the 11th studio-album title (and release year) can be unambiguously determined.
- query_shape_implication: First retrieve a reliable band/profile page to confirm the 'highest-selling Canadian heavy metal group' identity; then open the discography or the specific album page to extract the album title and release year. Do not follow through to day/month release-date details — save the identified album page/URL for the subsequent precise-date retrieval.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Annihilator (band)', 'Annihilator discography', 'Set the World on Fire (Annihilator album)', 'All for You (Annihilator album)', 'Metal (Annihilator album)', 'Schizo Deluxe', 'Refresh the Demon']
- retrieval_focus: Identify the band referenced (likely Annihilator), find which studio album is their 11th, and retrieve that album's official release date.
- anchors: ['Annihilator (band)', 'Annihilator discography', 'retrieved album titles (Set the World on Fire, All for You, Metal, Schizo Deluxe, Refresh the Demon)']
- bridge_clues: ["Confirm that 'highest-selling heavy metal group from Canada' refers to Annihilator via a summary or band page", 'Use the discography page to determine the ordered list of studio albums and pick the 11th entry', 'Open the 11th-album page (or the discography entry) to read the official release date']
- noisy_or_distracting_clues: ['Multiple album titles present that are not labeled by ordinal — risk of miscounting which is 11th', 'Summary mentions Thor (unrelated) and other passages with no clear link to this query, creating irrelevant context']
- expected_evidence_type: Discography listing or band page that enumerates studio albums in order, and the specific album page or discography entry that gives the album's official release date (day/month/year and region/label if available).
- query_shape_implication: First query should target the band discography (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') to get album order; second query should target the identified album name plus 'release date' (e.g., '<Album Name> release date' or 'Annihilator 11th studio album release date').

---

## 180__split2__seg2__right
- idx: 180
- split_iter: 2
- task_kind: right_recovery
- expected: B
- v0 predicted: B
- v02 predicted: A
- v0 why: Segment B moves from an ambiguous phrase to explicitly confirming the target band (resolving the 'highest-selling Canadian heavy metal group' reference) and determining the 11th studio-album title (an anchor/ordinal resolution), then expands scope from only the release year to the full official release date. This corrects an entity/noisy-mention and an ordinal-gap and changes answer-type/detail. Segment A mostly refines evidence for an already-identified album (collecting candidate dates/sources), which is a narrower, post-identification collation step.
- v02 why: Segment A prescribes collecting multiple candidate dates/sources assuming the band and album are already known; moving to the endpoint requires adding band-identification anchors and shifting from broad candidate-assembly to selecting a single authoritative release date. That combines adding new anchors (band ID) and changing the evidence/answer type — a larger semantic change than B's narrower step from year-only to full date.

### Full segment
from_state:
- name: Rmid_iter2_split1
- kind: generated_midpoint
- retrieval_focus: Confirm that the phrase 'the highest-selling heavy metal group from Canada' refers to Annihilator, and identify which album in Annihilator's official studio-album sequence is the 11th (extract the album title and, if easily available, the release year only). Do not retrieve the full release date (day/month/year) yet.
- anchors: ["Verify band identity: evidence that 'highest-selling Canadian heavy metal group' = Annihilator (authoritative bio or reliable secondary source)", 'Annihilator discography (ordered list of studio albums)', 'Explicit statement or unambiguous counting that identifies the 11th studio album', 'Album title for the 11th studio album (and release year, but not full date)']
- bridge_clues: ['Band profile pages (Wikipedia lead, official band site, AllMusic) often state prominent claims and provide a discography link to confirm identity.', "Discography pages list studio albums chronologically; some album pages include phrasing like 'X is the Nth studio album by Annihilator' which directly confirms ordinal.", "Press articles or reputable music databases can corroborate the 'highest-selling' claim if the band page is ambiguous.", 'Album pages commonly show at least the release year in the infobox/header even if the exact day is elsewhere; record the year but skip detailed date fields for now.']
- noisy_or_distracting_clues: ['Some sources may label compilations, live albums or reissues alongside studio albums and cause miscounting.', 'Other Canadian metal or rock acts may appear in search results (e.g., Anvil, Thor) and distract from the target.', "Conflicting or unsourced claims about 'highest-selling' status — prefer authoritative or corroborated references.", 'Regional/label-specific release date entries that include release-day detail (avoid extracting those now).']
- expected_evidence_type: An authoritative band profile or reputable music-database discography that (a) links the 'highest-selling Canadian heavy metal group' description to Annihilator and (b) either labels the album as the band's 11th studio album or provides a clear chronological list from which the 11th studio-album title (and release year) can be unambiguously determined.
- query_shape_implication: First retrieve a reliable band/profile page to confirm the 'highest-selling Canadian heavy metal group' identity; then open the discography or the specific album page to extract the album title and release year. Do not follow through to day/month release-date details — save the identified album page/URL for the subsequent precise-date retrieval.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Annihilator (band)', 'Annihilator discography', 'Set the World on Fire (Annihilator album)', 'All for You (Annihilator album)', 'Metal (Annihilator album)', 'Schizo Deluxe', 'Refresh the Demon']
- retrieval_focus: Identify the band referenced (likely Annihilator), find which studio album is their 11th, and retrieve that album's official release date.
- anchors: ['Annihilator (band)', 'Annihilator discography', 'retrieved album titles (Set the World on Fire, All for You, Metal, Schizo Deluxe, Refresh the Demon)']
- bridge_clues: ["Confirm that 'highest-selling heavy metal group from Canada' refers to Annihilator via a summary or band page", 'Use the discography page to determine the ordered list of studio albums and pick the 11th entry', 'Open the 11th-album page (or the discography entry) to read the official release date']
- noisy_or_distracting_clues: ['Multiple album titles present that are not labeled by ordinal — risk of miscounting which is 11th', 'Summary mentions Thor (unrelated) and other passages with no clear link to this query, creating irrelevant context']
- expected_evidence_type: Discography listing or band page that enumerates studio albums in order, and the specific album page or discography entry that gives the album's official release date (day/month/year and region/label if available).
- query_shape_implication: First query should target the band discography (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') to get album order; second query should target the identified album name plus 'release date' (e.g., '<Album Name> release date' or 'Annihilator 11th studio album release date').

### Sub segment
from_state:
- name: Rmid_iter3_split2
- kind: generated_midpoint
- retrieval_focus: Given the confirmed band identity and the 11th studio-album title (from R_left), open that album's primary pages and collect all cited release-date entries and their sources (infobox release field, label/press release, major music databases). Do not yet pick the final authoritative date — assemble candidate dates and source provenance to enable a small final disambiguation step.
- anchors: ["The album's main page (e.g., Wikipedia album article) — capture the infobox release field and any cited reference for the date", "Official band/label announcement or archive page that lists the album's release date(s)", 'Major music databases (AllMusic, Discogs, MusicBrainz) and reputable press reviews that include release-date detail', 'Identify any region-specific release entries (e.g., Canada, Europe, Japan) and note which source asserts each']
- bridge_clues: ['Album article infoboxes often show a full release date and cite a source link — capture that citation URL', "Labels or the band's official site may post the precise release day (authoritative for the 'official' date)", 'Databases like Discogs and MusicBrainz list release versions and regional dates which explain discrepancies', "Contemporary press reviews/releases around the album's launch (magazine archives, press kits) can corroborate the correct date"]
- noisy_or_distracting_clues: ['Reissues, remasters or deluxe-edition pages that show later release dates (avoid conflating these with the original release)', "Region-specific release variants that list different days (these are legitimate but can confuse 'official' single-date answers)", 'Unofficial fan sites or unsourced wiki edits that provide a date without verifying references', 'Pages that list only the release year (useful but incomplete for the final answer)']
- expected_evidence_type: A set of candidate release-date entries (day/month/year or month/year) each tied to a source: album-page infobox citation, official band/label announcement, and at least one major music-database entry. Each candidate should include the source URL and any regional qualifier so the final step can choose the authoritative original-release date.
- query_shape_implication: Target the identified album by name: (1) open the album page and extract the infobox date and its citation; (2) query the band's official site/label press release for the announcement; (3) check Discogs/AllMusic/MusicBrainz for release-version listings. Collect all date variants and source links, but do not resolve to a single 'official' date here.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Annihilator (band)', 'Annihilator discography', 'Set the World on Fire (Annihilator album)', 'All for You (Annihilator album)', 'Metal (Annihilator album)', 'Schizo Deluxe', 'Refresh the Demon']
- retrieval_focus: Identify the band referenced (likely Annihilator), find which studio album is their 11th, and retrieve that album's official release date.
- anchors: ['Annihilator (band)', 'Annihilator discography', 'retrieved album titles (Set the World on Fire, All for You, Metal, Schizo Deluxe, Refresh the Demon)']
- bridge_clues: ["Confirm that 'highest-selling heavy metal group from Canada' refers to Annihilator via a summary or band page", 'Use the discography page to determine the ordered list of studio albums and pick the 11th entry', 'Open the 11th-album page (or the discography entry) to read the official release date']
- noisy_or_distracting_clues: ['Multiple album titles present that are not labeled by ordinal — risk of miscounting which is 11th', 'Summary mentions Thor (unrelated) and other passages with no clear link to this query, creating irrelevant context']
- expected_evidence_type: Discography listing or band page that enumerates studio albums in order, and the specific album page or discography entry that gives the album's official release date (day/month/year and region/label if available).
- query_shape_implication: First query should target the band discography (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') to get album order; second query should target the identified album name plus 'release date' (e.g., '<Album Name> release date' or 'Annihilator 11th studio album release date').

---

## 268__split0__seg0__right
- idx: 268
- split_iter: 0
- task_kind: right_recovery
- expected: B
- v0 predicted: B
- v02 predicted: A
- v0 why: R0_base (B) starts with a broad, multi-target and noisy query and returns largely irrelevant titles; the to_state shifts to a focused, disambiguated, entity-centric retrieval plan for Henry Green and G. K. Chesterton. This is a larger correction (resolving query-shape ambiguity and noisy results) than A, which already embodies a focused midpoint plan and only refines retrieval targets.
- v02 why: Segment A requires a stronger reorientation: it adds an explicit pen-name anchor (Henry Green = Henry Vincent Yorke), prioritizes disambiguation before any comparison, and mandates an exact-entity query shape to avoid confusing similarly named persons. B largely makes a narrower correction (split an ambiguous multi-target query into two focused queries). A therefore changes the retrieval instructions more substantially.

### Full segment
from_state:
- name: R0_base
- kind: endpoint
- query: Henry Green novelist Henry Vincent Yorke biography occupations OR "Henry Green (novelist)" occupations biography; "G. K. Chesterton" biography occupations journalist novelist poet critic lay theologian
- retrieved_titles: ['Henry Green (disambiguation)', 'Henry James (biographer)', 'Henry F. Pringle', 'Nick Tosches', 'J. M. Aimot', 'Henry Payne (engineer)', 'Philip Norman (author)']
- retrieval_focus: Find a biographic / career summary for Henry Green (the novelist Henry Vincent Yorke) and a full list of G. K. Chesterton's occupations so the two can be compared; also disambiguate Joseph Henry Chesterton (plant collector) to avoid confusion.
- anchors: ['G. K. Chesterton — author of Orthodoxy (writer, Christian apologist) (present in passages)', 'Joseph Henry Chesterton — 19th-century plant collector (present in passages)', 'Henry Green — missing (should be Henry Vincent Yorke, novelist)']
- bridge_clues: ['Henry Green occupations', 'Henry Vincent Yorke biography occupations', '"Henry Green (novelist)" occupations', 'G. K. Chesterton biography occupations', 'Joseph Henry Chesterton plant collector (to confirm identity and avoid conflation)']
- noisy_or_distracting_clues: ['Retrieved titles are largely unrelated (Henry James, Nick Tosches, Henry F. Pringle, etc.)', 'Henry Green (disambiguation) may return many persons and add ambiguity', "Presence of Joseph Henry Chesterton in passages risks name confusion with 'Henry' in query"]
- expected_evidence_type: Short encyclopedic/biography lead paragraphs or career sections listing occupations and notable roles (e.g., novelist, journalist, editor, poet, critic, theologian) and dates to assess diversity of jobs.
- query_shape_implication: Current multi-target query is ambiguous and returns noisy hits — perform two focused, disambiguated queries: one exact-match for "Henry Vincent Yorke" or "Henry Green (novelist)" + 'occupations/biography', and one for "G. K. Chesterton" + 'occupations/biography'. Also include a disambiguation check for Joseph Henry Chesterton to avoid conflation.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Henry Green (disambiguation)', 'Henry Green', 'Party Going', 'Henry James (biographer)', 'Henry Yorke', 'Henry F. Pringle', 'Bill Henry (New York Yankees pitcher)']
- retrieval_focus: Locate biographical/occupation information for Henry Green (pen name of Henry Yorke) and a full occupations list for G. K. Chesterton; disambiguate Joseph Henry Chesterton (plant collector) to avoid conflation.
- anchors: ['Henry Green (disambiguation)', 'Henry Green', 'Henry Yorke', 'Party Going', 'G. K. Chesterton', 'Joseph Henry Chesterton']
- bridge_clues: ['Henry Green occupations', 'Henry Yorke biography occupations', 'Henry Green Party Going author Henry Yorke', 'G. K. Chesterton occupations biography', 'Joseph Henry Chesterton plant collector (to confirm different person)']
- noisy_or_distracting_clues: ['Henry James (biographer)', 'Henry F. Pringle', 'Bill Henry (New York Yankees pitcher)']
- expected_evidence_type: Lead/infobox or biography sections that list occupations (e.g., novelist, journalist, civil servant, author, apologist, plant collector) and career summaries for Henry Green/Henry Yorke and G. K. Chesterton.
- query_shape_implication: Use short entity-centric queries ('<Name> biography' / '<Name> occupations' / '<Name> infobox') and disambiguation queries ('Henry Green vs Henry Yorke', 'Joseph Henry Chesterton') to retrieve pages that explicitly list roles to support a diversity-of-jobs comparison.

### Sub segment
from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Resolve and retrieve clear biographical/occupation information for Henry Green (pen name of Henry Vincent Yorke) — verify identity, primary occupations, and notable roles — to remove ambiguity before fetching a full occupations list for G. K. Chesterton. Also include a short disambiguation check to avoid confusing Henry Green with other Henrys.
- anchors: ['Henry Green — pen name of Henry Vincent Yorke (missing from R_left passages)', 'Need for occupation list (novelist, journalist, civil servant, etc.) to compare job diversity', "Avoid conflation with other 'Henry' results and with Joseph Henry Chesterton"]
- bridge_clues: ['"Henry Vincent Yorke" biography occupations', '"Henry Green (novelist)" infobox occupations', '"Henry Green" Party Going author Henry Yorke biography', 'Henry Green pen name Henry Vincent Yorke career summary']
- noisy_or_distracting_clues: ['Henry Green (disambiguation) pages listing many unrelated Henrys', 'Search results for other Henrys (Henry James, Henry F. Pringle, Bill Henry)', 'Joseph Henry Chesterton (similar name) which could distract from Henry Green identity']
- expected_evidence_type: Short encyclopedic lead/infobox or biography section that explicitly lists occupations and notable roles (e.g., novelist, journalist, civil servant, editor) with brief dates/notes to assess diversity of jobs.
- query_shape_implication: Use an exact-entity query shape: 'Henry Vincent Yorke biography' or 'Henry Green (novelist) occupations' and include the pen-name mapping ('Henry Green = Henry Vincent Yorke') to return a concise lead/infobox. Avoid broad multi-entity queries in this step.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Henry Green (disambiguation)', 'Henry Green', 'Party Going', 'Henry James (biographer)', 'Henry Yorke', 'Henry F. Pringle', 'Bill Henry (New York Yankees pitcher)']
- retrieval_focus: Locate biographical/occupation information for Henry Green (pen name of Henry Yorke) and a full occupations list for G. K. Chesterton; disambiguate Joseph Henry Chesterton (plant collector) to avoid conflation.
- anchors: ['Henry Green (disambiguation)', 'Henry Green', 'Henry Yorke', 'Party Going', 'G. K. Chesterton', 'Joseph Henry Chesterton']
- bridge_clues: ['Henry Green occupations', 'Henry Yorke biography occupations', 'Henry Green Party Going author Henry Yorke', 'G. K. Chesterton occupations biography', 'Joseph Henry Chesterton plant collector (to confirm different person)']
- noisy_or_distracting_clues: ['Henry James (biographer)', 'Henry F. Pringle', 'Bill Henry (New York Yankees pitcher)']
- expected_evidence_type: Lead/infobox or biography sections that list occupations (e.g., novelist, journalist, civil servant, author, apologist, plant collector) and career summaries for Henry Green/Henry Yorke and G. K. Chesterton.
- query_shape_implication: Use short entity-centric queries ('<Name> biography' / '<Name> occupations' / '<Name> infobox') and disambiguation queries ('Henry Green vs Henry Yorke', 'Joseph Henry Chesterton') to retrieve pages that explicitly list roles to support a diversity-of-jobs comparison.

---

## 268__split2__seg0__left
- idx: 268
- split_iter: 2
- task_kind: left_recovery
- expected: B
- v0 predicted: B
- v02 predicted: A
- v0 why: Segment B moves from a broad, noisy multi-target query to an exact identity/pen-name resolution (Henry Green = Henry Vincent Yorke) and requests a concise lead/infobox mapping of name → primary role. That is a stronger, more decisive anchor/alias correction and narrows retrieval focus substantially more than A's incremental disambiguation/multi-hit narrowing.
- v02 why: Segment A requires a broader shift in retrieval instructions: move from an ambiguous multi-target query to an entity-centered multi-hit strategy that explicitly pulls disambiguation pages and multiple candidate biography leads (avoiding name-conflation with Joseph Henry Chesterton). That changes the query shape, candidate breadth, and noise-avoidance guidance more than B’s narrower identity-confirmation step.

### Full segment
from_state:
- name: R0_base
- kind: endpoint
- query: Henry Green novelist Henry Vincent Yorke biography occupations OR "Henry Green (novelist)" occupations biography; "G. K. Chesterton" biography occupations journalist novelist poet critic lay theologian
- retrieved_titles: ['Henry Green (disambiguation)', 'Henry James (biographer)', 'Henry F. Pringle', 'Nick Tosches', 'J. M. Aimot', 'Henry Payne (engineer)', 'Philip Norman (author)']
- retrieval_focus: Find a biographic / career summary for Henry Green (the novelist Henry Vincent Yorke) and a full list of G. K. Chesterton's occupations so the two can be compared; also disambiguate Joseph Henry Chesterton (plant collector) to avoid confusion.
- anchors: ['G. K. Chesterton — author of Orthodoxy (writer, Christian apologist) (present in passages)', 'Joseph Henry Chesterton — 19th-century plant collector (present in passages)', 'Henry Green — missing (should be Henry Vincent Yorke, novelist)']
- bridge_clues: ['Henry Green occupations', 'Henry Vincent Yorke biography occupations', '"Henry Green (novelist)" occupations', 'G. K. Chesterton biography occupations', 'Joseph Henry Chesterton plant collector (to confirm identity and avoid conflation)']
- noisy_or_distracting_clues: ['Retrieved titles are largely unrelated (Henry James, Nick Tosches, Henry F. Pringle, etc.)', 'Henry Green (disambiguation) may return many persons and add ambiguity', "Presence of Joseph Henry Chesterton in passages risks name confusion with 'Henry' in query"]
- expected_evidence_type: Short encyclopedic/biography lead paragraphs or career sections listing occupations and notable roles (e.g., novelist, journalist, editor, poet, critic, theologian) and dates to assess diversity of jobs.
- query_shape_implication: Current multi-target query is ambiguous and returns noisy hits — perform two focused, disambiguated queries: one exact-match for "Henry Vincent Yorke" or "Henry Green (novelist)" + 'occupations/biography', and one for "G. K. Chesterton" + 'occupations/biography'. Also include a disambiguation check for Joseph Henry Chesterton to avoid conflation.

to_state:
- name: Rmid_iter2_split0
- kind: generated_midpoint
- retrieval_focus: Disambiguate the target 'Henry Green' by confirming the pen name mapping (Henry Green = Henry Vincent Yorke) and retrieve a concise lead/infobox line that states his primary vocation(s) and life dates. Keep scope limited to identity confirmation and primary role(s) (e.g., 'novelist'), not a full detailed occupations list.
- anchors: ['G. K. Chesterton — present in passages as author/apologist (already known and does not need further narrowing at this step)', 'Joseph Henry Chesterton — present in passages and a potential source of name confusion', 'Missing target: Henry Green (pen name) — needs identity confirmation (Henry Vincent Yorke) and a primary-role label']
- bridge_clues: ['"Henry Green" pen name "Henry Vincent Yorke"', '"Henry Vincent Yorke" lead paragraph biography', '"Henry Green" novelist "Party Going" author Henry Vincent Yorke', 'Henry Green (novelist) one-line summary occupations']
- noisy_or_distracting_clues: ['Henry Green (disambiguation) pages listing multiple people named Henry Green', 'Search results for other prominent Henrys (Henry James, Henry F. Pringle, etc.)', 'Joseph Henry Chesterton (similar name) which could pull botanical/19th-century references']
- expected_evidence_type: Short encyclopedic lead or infobox snippet that maps the pen name to the real name and gives a one-line occupation label and dates (e.g., 'Henry Green (born Henry Vincent Yorke; 1905–1973) was an English novelist').
- query_shape_implication: Use an exact-entity identity query shape focused on the pen-name mapping and lead sentence (e.g., 'Henry Green = Henry Vincent Yorke' or 'Henry Vincent Yorke biography lead') rather than a broad multi-entity occupations query; this should return concise identity confirmation without exhaustive job listings.

### Sub segment
from_state:
- name: R0_base
- kind: endpoint
- query: Henry Green novelist Henry Vincent Yorke biography occupations OR "Henry Green (novelist)" occupations biography; "G. K. Chesterton" biography occupations journalist novelist poet critic lay theologian
- retrieved_titles: ['Henry Green (disambiguation)', 'Henry James (biographer)', 'Henry F. Pringle', 'Nick Tosches', 'J. M. Aimot', 'Henry Payne (engineer)', 'Philip Norman (author)']
- retrieval_focus: Find a biographic / career summary for Henry Green (the novelist Henry Vincent Yorke) and a full list of G. K. Chesterton's occupations so the two can be compared; also disambiguate Joseph Henry Chesterton (plant collector) to avoid confusion.
- anchors: ['G. K. Chesterton — author of Orthodoxy (writer, Christian apologist) (present in passages)', 'Joseph Henry Chesterton — 19th-century plant collector (present in passages)', 'Henry Green — missing (should be Henry Vincent Yorke, novelist)']
- bridge_clues: ['Henry Green occupations', 'Henry Vincent Yorke biography occupations', '"Henry Green (novelist)" occupations', 'G. K. Chesterton biography occupations', 'Joseph Henry Chesterton plant collector (to confirm identity and avoid conflation)']
- noisy_or_distracting_clues: ['Retrieved titles are largely unrelated (Henry James, Nick Tosches, Henry F. Pringle, etc.)', 'Henry Green (disambiguation) may return many persons and add ambiguity', "Presence of Joseph Henry Chesterton in passages risks name confusion with 'Henry' in query"]
- expected_evidence_type: Short encyclopedic/biography lead paragraphs or career sections listing occupations and notable roles (e.g., novelist, journalist, editor, poet, critic, theologian) and dates to assess diversity of jobs.
- query_shape_implication: Current multi-target query is ambiguous and returns noisy hits — perform two focused, disambiguated queries: one exact-match for "Henry Vincent Yorke" or "Henry Green (novelist)" + 'occupations/biography', and one for "G. K. Chesterton" + 'occupations/biography'. Also include a disambiguation check for Joseph Henry Chesterton to avoid conflation.

to_state:
- name: Rmid_iter3_split0
- kind: generated_midpoint
- retrieval_focus: Narrow the retrieval to pages explicitly about 'Henry Green' (the novelist) by fetching the disambiguation entry plus candidate biography/encyclopedia leads for Henry Green; confirm candidate pages that plausibly contain the novelist's life dates, primary vocation(s), and any pen-name mention, while not yet forcing a single exact-infobox mapping.
- anchors: ['G. K. Chesterton — known from passages as an author/apologist (retain as comparison endpoint)', 'Joseph Henry Chesterton — present in passages and a possible source of name confusion', 'Missing target: Henry Green — focus now on pulling disambiguation and candidate biography pages that will identify which Henry Green is the novelist']
- bridge_clues: ['"Henry Green (novelist)" biography', '"Henry Green" disambiguation', '"Henry Green" novelist "Party Going"', '"Henry Green" pen name "Henry Vincent Yorke"', '"Henry Vincent Yorke" biography OR \'Henry Vincent Yorke\' novelist']
- noisy_or_distracting_clues: ['Search results for many other Henrys (Henry James, Henry F. Pringle, etc.)', 'Disambiguation pages listing multiple people named Henry Green', "Joseph Henry Chesterton (botanical collector) appearing because of the shared 'Henry/Chesterton' tokens"]
- expected_evidence_type: Disambiguation entries and short encyclopedic lead paragraphs or biography summaries that list the subject's primary vocation(s), notable works, and possibly the real name/pen name (but not necessarily a single-line infobox extraction).
- query_shape_implication: Use an entity-centered multi-hit query shape (target the 'Henry Green' disambiguation and the likely novelist page(s) with queries like 'Henry Green (novelist)' or 'Henry Green Party Going') so results narrow to candidate Henry Green pages without yet restricting to one exact lead sentence.

---

## 6__split0__seg0__left
- idx: 6
- split_iter: 0
- task_kind: left_recovery
- expected: A
- v0 predicted: A
- v02 predicted: B
- v0 why: Segment A introduces the main target entity page ('Shenandoah River') into the retrieved set and shifts the retrieval focus from many noisy local pages to an authoritative river article that can explicitly list the states (resolving the missing West Virginia linkage). This is a bigger answerability/evidence-family and entity-anchor correction than B, which only narrows toward the North Fork and downstream landmarks but does not surface the main river page or explicit interstate evidence.
- v02 why: Segment B refocuses the retrieval from a generic river-level 'which states' query to a fork-level, connector-driven search: it introduces a different primary anchor (North Fork Shenandoah River), adds downstream landmark anchors (Harpers Ferry, Potomac) and a new bridge relation (confluence/state-boundary evidence). This is a broader semantic change to what to target and how to link the fork to interstate course than A’s relatively small shift to a straightforward 'Shenandoah River states' query.

### Full segment
from_state:
- name: R0_base
- kind: endpoint
- query: Shenandoah River North Fork flows through which states Virginia West Virginia Harpers Ferry
- retrieved_titles: ['Little Dry River', 'Virginius Island, West Virginia', 'Harpers Ferry, West Virginia', 'German River', 'Middle River (Virginia)', 'Baltimore and Ohio Railroad', 'Lynch River']
- retrieval_focus: Locate an authoritative page for the Shenandoah River (or the North Fork Shenandoah River) that explicitly states which U.S. states the river passes through — confirm whether the river flows through Virginia and West Virginia (look for mentions of Harpers Ferry or the river's lower course).
- anchors: ['Shenandoah River', 'North Fork Shenandoah River', 'Smith Creek', 'Harpers Ferry', 'Virginia', 'West Virginia']
- bridge_clues: ['passes through', 'flows through', 'states', 'lower course toward Harpers Ferry', 'confluence with Potomac', 'Shenandoah Valley']
- noisy_or_distracting_clues: ['other local river/place pages (Little Dry River, Middle River, Lynch River)', 'railroad or island pages (Baltimore and Ohio Railroad, Virginius Island)', "titles referring to local features that don't state overall river course"]
- expected_evidence_type: Encyclopedic/geographic article for 'Shenandoah River' or 'North Fork Shenandoah River' that describes the river's course and explicitly lists the U.S. states traversed (mentions Virginia and West Virginia or cites Harpers Ferry in West Virginia).
- query_shape_implication: Short, place-centered query: a single precise second-hop to the main Shenandoah River page (or North Fork page) should answer the question; must avoid being misled by many local tributary/place pages with similar geographic names.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: ['Little Dry River', 'Shenandoah River', 'German River', 'Cootes Store, Virginia', 'North River (South Fork Shenandoah River)', 'Cedar Creek (North Fork Shenandoah River)', 'Smith Creek (Virginia)']
- retrieval_focus: Locate an authoritative page that states which US states the Shenandoah River (including its North Fork) flows through to confirm whether it passes through Virginia and West Virginia.
- anchors: ['Smith Creek', 'North Fork of the Shenandoah River', 'Shenandoah River', 'Rockingham County, Virginia', 'Mount Jackson, Virginia']
- bridge_clues: ['Smith Creek is a tributary of the North Fork of the Shenandoah River', 'The North Fork is part of the Shenandoah River system', "Need a source that lists the states traversed by the Shenandoah River (to link Smith Creek's river to states)"]
- noisy_or_distracting_clues: ['Little Dry River', 'German River', 'Cootes Store, Virginia', 'North River (South Fork Shenandoah River)', 'Cedar Creek (North Fork Shenandoah River)']
- expected_evidence_type: Encyclopedic or geographic source (river article, infobox, or authoritative map/state resource) explicitly listing the states the Shenandoah River flows through (e.g., Virginia; West Virginia).
- query_shape_implication: Short, entity-focused queries using the river name plus 'states' or 'flows through' (examples: 'Shenandoah River states', 'Which states does the Shenandoah River flow through?', optionally add 'North Fork Shenandoah River').

### Sub segment
from_state:
- name: R0_base
- kind: endpoint
- query: Shenandoah River North Fork flows through which states Virginia West Virginia Harpers Ferry
- retrieved_titles: ['Little Dry River', 'Virginius Island, West Virginia', 'Harpers Ferry, West Virginia', 'German River', 'Middle River (Virginia)', 'Baltimore and Ohio Railroad', 'Lynch River']
- retrieval_focus: Locate an authoritative page for the Shenandoah River (or the North Fork Shenandoah River) that explicitly states which U.S. states the river passes through — confirm whether the river flows through Virginia and West Virginia (look for mentions of Harpers Ferry or the river's lower course).
- anchors: ['Shenandoah River', 'North Fork Shenandoah River', 'Smith Creek', 'Harpers Ferry', 'Virginia', 'West Virginia']
- bridge_clues: ['passes through', 'flows through', 'states', 'lower course toward Harpers Ferry', 'confluence with Potomac', 'Shenandoah Valley']
- noisy_or_distracting_clues: ['other local river/place pages (Little Dry River, Middle River, Lynch River)', 'railroad or island pages (Baltimore and Ohio Railroad, Virginius Island)', "titles referring to local features that don't state overall river course"]
- expected_evidence_type: Encyclopedic/geographic article for 'Shenandoah River' or 'North Fork Shenandoah River' that describes the river's course and explicitly lists the U.S. states traversed (mentions Virginia and West Virginia or cites Harpers Ferry in West Virginia).
- query_shape_implication: Short, place-centered query: a single precise second-hop to the main Shenandoah River page (or North Fork page) should answer the question; must avoid being misled by many local tributary/place pages with similar geographic names.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Target the North Fork Shenandoah River (the immediate parent watercourse of Smith Creek) or a page that connects the North Fork to the main Shenandoah River and mentions downstream landmarks (Harpers Ferry, confluence with the Potomac) that indicate the river crosses state lines.
- anchors: ['North Fork Shenandoah River', 'Shenandoah River', 'Smith Creek', 'Harpers Ferry', 'Potomac River', 'Virginia', 'West Virginia']
- bridge_clues: ['North Fork is part of the Shenandoah River system', 'confluence near Harpers Ferry', 'flows into the Potomac', 'mentions downstream course or lower reaches', 'references the river crossing a state boundary']
- noisy_or_distracting_clues: ['local tributary pages (Little Dry River, Cedar Creek, North River)', 'county- or town-level pages (Mount Jackson, Rockingham County)', 'pages about railroads or islands (Baltimore and Ohio Railroad, Virginius Island) that mention Harpers Ferry but not river states']
- expected_evidence_type: An encyclopedic/geographic article focused on the North Fork Shenandoah River or on the Shenandoah River that explicitly connects the fork to the main river and/or names downstream locations (Harpers Ferry, Potomac) or lists the U.S. states traversed (Virginia; West Virginia).
- query_shape_implication: A fork-level, entity-specific query (e.g., 'North Fork Shenandoah River' + downstream landmark terms) that is narrower than a broad 'Shenandoah River states' query but still surfaces statements linking the fork to the main river and its interstate course.

---
