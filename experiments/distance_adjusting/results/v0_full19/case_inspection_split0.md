# Distance case inspection

- tasks_path: `experiments/distance_adjusting/cache/full19_distance_tasks.jsonl`
- judgments_path: `experiments/distance_adjusting/results/v0_full19/judgments.jsonl`
- only_split_iter: `0`

## left_fail (12 total, showing 12)

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

### 169__split0__seg0__left

- idx: 169
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.8
- why_larger: B narrows the retrieval much more concretely: it adds prioritized authoritative-source anchors (obituary/Hall of Fame), explicit bridge phrases (exact 'stunt double' and 'performed the motorcycle jump'), and prescriptive query-shape guidance (exact-phrase + site filters and a focused follow-up for Bullitt). A is a milder refinement toward verifying The Great Escape and Bullitt but is less specific and omits the added source-anchor and operational query instructions.

**Question**

What movie did "the king of cool" play in with Bud Ekins as his stunt double?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Bud Ekins Steve McQueen stunt double Bullitt? "The Great Escape" motorcycle stunt details who performed jump stunt credits filming location
- retrieved_titles: Bud Ekins, Stunt double, Stunt coordinator, Stunt, Butch Laswell, Corey Scott, Todd Bryant
- retrieval_focus: Verify and cite which Steve McQueen film(s) Bud Ekins served as a stunt double for, with primary focus on confirming the motorcycle-stunt credit in The Great Escape and resolving the ambiguity about Bullitt.
- anchors: Bud Ekins, Steve McQueen ("The King of Cool"), The Great Escape, Bullitt
- bridge_clues: motorcycle stunt / famous motorcycle jump, stunt double credit, stunt credits in filmographies/IMDb, Stuntmen's Hall of Fame / obituary / biography entries
- noisy_or_distracting_clues: Butch Laswell, Corey Scott, Todd Bryant, generic pages titled 'Stunt' or 'Stunt coordinator' that do not mention McQueen or Ekins
- expected_evidence_type: Authoritative film-credit records or reputable secondary sources (IMDb/BFI entries, film credits, biographies, obituaries, Hall of Fame pages, production notes) explicitly stating Ekins doubled McQueen on The Great Escape and listing any other films where he doubled McQueen.
- query_shape_implication: Use narrow, factual queries and source filters (e.g., 'Bud Ekins Steve McQueen The Great Escape stunt double', 'Bud Ekins Bullitt stunt double', 'who did the motorcycle jump in The Great Escape') aimed at crediting sources rather than broad 'stunt' topic searches.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Bud Ekins, The Great Escape (film), Triumph TR6 Trophy, Steve McQueen, Stunt double, Dave Ekins, Motorcycle stunt riding
- retrieval_focus: {
  "retrieval_focus": "Verify which film(s) Bud Ekins served as Steve McQueen’s stunt double — primary candidate: The Great Escape; check whether he also doubled McQueen in Bullitt or only appears in Bullitt credits.",
  "anchors": ["Bud Ekins", "Steve McQueen (\"The King of Cool\")", "The Great Escape", "Bullitt"],
  "bridge_clues": ["stunt double", "doubled for", "motorcycle stunt", "stunt credits", "famous motorcycle jump"],
  "noisy_or_distracting_clues": ["Triumph TR6 Trophy", "Dave Ekins", "Motorcycle stunt riding (general)", "Stunt double (generic page)", empty],
  "expected_evidence_type": "Short biographical or film-credit sentences explicitly stating 'Bud Ekins served as Steve McQueen’s stunt double' on The Great Escape (and any mentions clarifying whether he doubled McQueen in Bullitt).",
  "query_shape_implication": "Use conjunctive short queries combining actor alias and stunt relation, e.g. 'Bud Ekins Steve McQueen stunt double The Great Escape' and a follow-up 'Bud Ekins Steve McQueen stunt double Bullitt' ; include alias mapping ('The King of Cool' -> Steve McQueen)."
}

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Bud Ekins Steve McQueen stunt double Bullitt? "The Great Escape" motorcycle stunt details who performed jump stunt credits filming location
- retrieved_titles: Bud Ekins, Stunt double, Stunt coordinator, Stunt, Butch Laswell, Corey Scott, Todd Bryant
- retrieval_focus: Verify and cite which Steve McQueen film(s) Bud Ekins served as a stunt double for, with primary focus on confirming the motorcycle-stunt credit in The Great Escape and resolving the ambiguity about Bullitt.
- anchors: Bud Ekins, Steve McQueen ("The King of Cool"), The Great Escape, Bullitt
- bridge_clues: motorcycle stunt / famous motorcycle jump, stunt double credit, stunt credits in filmographies/IMDb, Stuntmen's Hall of Fame / obituary / biography entries
- noisy_or_distracting_clues: Butch Laswell, Corey Scott, Todd Bryant, generic pages titled 'Stunt' or 'Stunt coordinator' that do not mention McQueen or Ekins
- expected_evidence_type: Authoritative film-credit records or reputable secondary sources (IMDb/BFI entries, film credits, biographies, obituaries, Hall of Fame pages, production notes) explicitly stating Ekins doubled McQueen on The Great Escape and listing any other films where he doubled McQueen.
- query_shape_implication: Use narrow, factual queries and source filters (e.g., 'Bud Ekins Steve McQueen The Great Escape stunt double', 'Bud Ekins Bullitt stunt double', 'who did the motorcycle jump in The Great Escape') aimed at crediting sources rather than broad 'stunt' topic searches.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow to authoritative credit-confirmation: verify that Bud Ekins served as Steve McQueen's stunt double on The Great Escape (especially the motorcycle jump) and explicitly check primary credit sources to resolve whether he also doubled McQueen in Bullitt. Prioritize obituaries, reputable biographies, film-credit databases, and Hall-of-Fame entries rather than generic 'stunt' pages.
- anchors: Bud Ekins, Steve McQueen ("The King of Cool"), The Great Escape, Bullitt, Stuntmen's Hall of Fame / obituary
- bridge_clues: "stunt double for Steve McQueen", "performed the motorcycle jump", credited as stuntman in filmography / IMDb / BFI, obituary or Hall of Fame entry mentioning The Great Escape
- noisy_or_distracting_clues: Triumph TR6 Trophy (motorcycle model) references, Dave Ekins (relative/other rider), general pages titled 'Stunt' or 'Stunt coordinator' without film credits, motorcycling forums or fan pages that repeat claims without sourcing
- expected_evidence_type: Short, explicit credit statements from authoritative sources (IMDb/BFI entries, NYT/THR obituaries, reputable biographies, Stuntmen's Hall of Fame) that say 'Bud Ekins served as Steve McQueen's stunt double on The Great Escape' and, separately, clear statements confirming or denying a doubling credit on Bullitt.
- query_shape_implication: Use focused phrase searches and source filters (exact phrase + site filters) such as '"Bud Ekins" "stunt double" "The Great Escape"' across reputable outlets; then a narrow follow-up search for 'Bud Ekins Bullitt' to resolve that single ambiguity. Avoid broad 'stunt' or generic motorcycle-topic queries.

---

### 227__split0__seg0__left

- idx: 227
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why_larger: Segment A makes a substantive shift in retrieval focus and query shape: it narrows from a dual actor->character+publisher goal to exclusively confirming Evan Peters portrayed Quicksilver, changing expected evidence type to filmography/cast credits and altering bridge clues and query-shape implications. Segment B mostly preserves the original dual-focus (actor->character plus publisher) and therefore is a smaller update.

**Question**

Evan Peters had a role as the fictional superhero from comic books by what publisher?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Evan Peters Quicksilver Pietro Maximoff portrayal filmography "X-Men: Days of Future Past" "X-Men: Apocalypse" Marvel Comics
- retrieved_titles: Quicksilver (comics), Days of Future Past, X-Men: Days of Future Past, All-New X-Men, Classic X-Men, Days of Future Past (disambiguation), New Canaanites
- retrieval_focus: Find an authoritative source that explicitly links Evan Peters to the character Quicksilver (Pietro Maximoff) in the X‑Men films and an explicit statement that Quicksilver is published by Marvel Comics (actor->character and character->publisher).
- anchors: Evan Peters, Quicksilver, Pietro Maximoff, X-Men: Days of Future Past, X-Men: Apocalypse, Marvel Comics
- bridge_clues: Retrieved title 'Quicksilver (comics)' — character page likely names publisher, Retrieved film titles ('X-Men: Days of Future Past', 'X-Men: Apocalypse') — link actor to role, Query already targets 'Evan Peters Quicksilver' (actor+character), summary_1 states the superhero role originates from Marvel Comics
- noisy_or_distracting_clues: All-New X-Men (comic series) — broader series noise, Classic X-Men — series-level pages not specific to the film role, Days of Future Past (disambiguation) — disambiguation pages, New Canaanites — appears unrelated to actor/character
- expected_evidence_type: A filmography or news/encyclopedic page stating 'Evan Peters portrayed Quicksilver (Pietro Maximoff)' plus a character/comics page or encyclopedic line stating 'Quicksilver is a fictional superhero appearing in American comic books published by Marvel Comics'.
- query_shape_implication: Current query mixes actor+character+film titles; next queries should be narrow, e.g. 'Evan Peters Quicksilver role', 'Evan Peters portrayed Quicksilver', and 'Quicksilver Pietro Maximoff publisher Marvel Comics' or directly open the actor filmography and the Quicksilver character page.

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
- name: R0_base
- kind: endpoint
- query: Evan Peters Quicksilver Pietro Maximoff portrayal filmography "X-Men: Days of Future Past" "X-Men: Apocalypse" Marvel Comics
- retrieved_titles: Quicksilver (comics), Days of Future Past, X-Men: Days of Future Past, All-New X-Men, Classic X-Men, Days of Future Past (disambiguation), New Canaanites
- retrieval_focus: Find an authoritative source that explicitly links Evan Peters to the character Quicksilver (Pietro Maximoff) in the X‑Men films and an explicit statement that Quicksilver is published by Marvel Comics (actor->character and character->publisher).
- anchors: Evan Peters, Quicksilver, Pietro Maximoff, X-Men: Days of Future Past, X-Men: Apocalypse, Marvel Comics
- bridge_clues: Retrieved title 'Quicksilver (comics)' — character page likely names publisher, Retrieved film titles ('X-Men: Days of Future Past', 'X-Men: Apocalypse') — link actor to role, Query already targets 'Evan Peters Quicksilver' (actor+character), summary_1 states the superhero role originates from Marvel Comics
- noisy_or_distracting_clues: All-New X-Men (comic series) — broader series noise, Classic X-Men — series-level pages not specific to the film role, Days of Future Past (disambiguation) — disambiguation pages, New Canaanites — appears unrelated to actor/character
- expected_evidence_type: A filmography or news/encyclopedic page stating 'Evan Peters portrayed Quicksilver (Pietro Maximoff)' plus a character/comics page or encyclopedic line stating 'Quicksilver is a fictional superhero appearing in American comic books published by Marvel Comics'.
- query_shape_implication: Current query mixes actor+character+film titles; next queries should be narrow, e.g. 'Evan Peters Quicksilver role', 'Evan Peters portrayed Quicksilver', and 'Quicksilver Pietro Maximoff publisher Marvel Comics' or directly open the actor filmography and the Quicksilver character page.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Confirm that Evan Peters specifically portrayed the character Quicksilver (Pietro Maximoff) in the X‑Men films/TV appearances by retrieving authoritative cast lists, the actor's filmography, and contemporary coverage linking Evan Peters to the Quicksilver role. Intentionally avoid comic-book publisher pages at this step.
- anchors: Evan Peters, Quicksilver, Pietro Maximoff, X‑Men: Days of Future Past, X‑Men: Apocalypse, filmography / cast list
- bridge_clues: Lead sentence or filmography section on an 'Evan Peters' page listing 'Quicksilver' among credited roles, Cast lists or credits for 'X‑Men: Days of Future Past' and 'X‑Men: Apocalypse' naming Evan Peters as Quicksilver, News articles/reviews or press releases from film releases that mention 'Evan Peters as Quicksilver' or 'Pietro Maximoff', Database entries (IMDb, official studio cast pages) showing Evan Peters credited as Quicksilver
- noisy_or_distracting_clues: Comic‑book character history pages and Marvel publisher articles (these relate to publisher step but are intentionally postponed), Pages about other Maximoff family members (Scarlet Witch, Luna Maximoff) or unrelated characters, General biographical details about Evan Peters (personal life, TV roles) that do not mention the Quicksilver role, Fan wikis or forum posts with unverified claims
- expected_evidence_type: Short authoritative lines: filmography/cast credits or reputable news/encyclopedic sentences explicitly stating 'Evan Peters portrayed Quicksilver (Pietro Maximoff)' or equivalent phrasing.
- query_shape_implication: Use narrow actor+role queries such as 'Evan Peters portrayed Quicksilver', 'Evan Peters filmography Quicksilver', or open 'Evan Peters' filmography and X‑Men cast pages. Defer queries like 'Quicksilver publisher' until after this actor->character link is confirmed.

---

### 247__split0__seg0__left

- idx: 247
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.86
- why_larger: B moves from a general retrieval focus to a much more specific, actionable search posture: it narrows to contemporary news/social‑media coverage that reproduces quoted hashtags/e‑petitions, adds explicit bridge clues (quoted hashtag, e‑petition, tweet embed), and prescribes concrete query construction (ORs, wildcards). This is a larger change in retrieval focus and query shape than A’s modest refinement.

**Question**

What is another name for the online protest that opposed the transfer of ex-detainees from Guantanamo Bay in 2016?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: OccupyGhana online protest name hashtag 2016 Ghana transfer Guantanamo Yemeni ex-detainees
- retrieved_titles: Gitmo detainees Ghana transfer controversy, List of Yemeni detainees at Guantanamo Bay, Timeline of the release and transfer of Guantanamo Bay detainees, Obaidullah (detainee), Guantanamo Bay hunger strikes, List of Uyghur detainees at Guantanamo Bay, Inayatullah (Guantanamo detainee 10029)
- retrieval_focus: Locate news or social-media mentions (in coverage of the Jan 2016 Ghana transfer of Yemeni ex-detainees) that explicitly name an online protest, campaign title, or hashtag opposing the transfer.
- anchors: OccupyGhana, New Patriotic Party (NPP), Ghana, January 2016 transfer, Yemeni ex-detainees, Gitmo detainees Ghana transfer controversy
- bridge_clues: online campaign, hashtag, e-petition, social media protest, named online protest, OccupyGhana online actions, coverage of public reaction
- noisy_or_distracting_clues: List of Yemeni detainees at Guantanamo Bay, Timeline of the release and transfer of Guantanamo Bay detainees, individual detainee biographies (Obaidullah, Inayatullah), Guantanamo Bay hunger strikes, general Gitmo lists and timelines
- expected_evidence_type: An explicit phrase in a news article or social-media excerpt quoting a campaign name or hashtag (e.g., a named online petition, quoted Twitter hashtag, or titled online protest) that identifies the online protest opposing the transfer.
- query_shape_implication: Queries should include terms for hashtags/online campaigns (hashtag, petition, "online protest") combined with 'Ghana', '2016', and 'Guantanamo' or 'Gitmo' and 'OccupyGhana' — likely locating news coverage or social posts rather than detainee-list pages.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Gitmo detainees Ghana transfer controversy, List of Yemeni detainees at Guantanamo Bay, Kamunting, Gitmo on the Platte, Occupy Ghana, Yemeni Revolution, Obaidullah (detainee)
- retrieval_focus: Locate a named online protest (campaign title, e‑petition name, or hashtag) that opposed Ghana's January 2016 acceptance/transfer of Yemeni ex-detainees from Guantanamo Bay; find a news or social‑media mention that gives an alternate name for the protest.
- anchors: Ghana, 2016 transfer, Gitmo, Gitmo detainees, Yemeni ex-detainees, OccupyGhana, New Patriotic Party
- bridge_clues: online protest, online campaign, hashtag, e-petition, named campaign, social media, opposed transfer, called for return
- noisy_or_distracting_clues: List of Yemeni detainees at Guantanamo Bay, Kamunting, Gitmo on the Platte, Yemeni Revolution, Obaidullah (detainee)
- expected_evidence_type: A short label or phrase (campaign title or hashtag) quoted in a news article or social‑media report that explicitly ties the name to the 2016 Ghana transfer protest.
- query_shape_implication: Use compact, token-rich queries combining actor + medium + event and year, e.g. 'OccupyGhana online campaign Guantanamo 2016 hashtag', 'Ghana Gitmo online protest name 2016', or 'online petition Ghana Gitmo detainees 2016'.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: OccupyGhana online protest name hashtag 2016 Ghana transfer Guantanamo Yemeni ex-detainees
- retrieved_titles: Gitmo detainees Ghana transfer controversy, List of Yemeni detainees at Guantanamo Bay, Timeline of the release and transfer of Guantanamo Bay detainees, Obaidullah (detainee), Guantanamo Bay hunger strikes, List of Uyghur detainees at Guantanamo Bay, Inayatullah (Guantanamo detainee 10029)
- retrieval_focus: Locate news or social-media mentions (in coverage of the Jan 2016 Ghana transfer of Yemeni ex-detainees) that explicitly name an online protest, campaign title, or hashtag opposing the transfer.
- anchors: OccupyGhana, New Patriotic Party (NPP), Ghana, January 2016 transfer, Yemeni ex-detainees, Gitmo detainees Ghana transfer controversy
- bridge_clues: online campaign, hashtag, e-petition, social media protest, named online protest, OccupyGhana online actions, coverage of public reaction
- noisy_or_distracting_clues: List of Yemeni detainees at Guantanamo Bay, Timeline of the release and transfer of Guantanamo Bay detainees, individual detainee biographies (Obaidullah, Inayatullah), Guantanamo Bay hunger strikes, general Gitmo lists and timelines
- expected_evidence_type: An explicit phrase in a news article or social-media excerpt quoting a campaign name or hashtag (e.g., a named online petition, quoted Twitter hashtag, or titled online protest) that identifies the online protest opposing the transfer.
- query_shape_implication: Queries should include terms for hashtags/online campaigns (hashtag, petition, "online protest") combined with 'Ghana', '2016', and 'Guantanamo' or 'Gitmo' and 'OccupyGhana' — likely locating news coverage or social posts rather than detainee-list pages.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow to contemporary news and social‑media coverage of the Jan 2016 Ghana transfer that explicitly quote or reproduce online campaign identifiers (hashtags, e‑petition titles, Facebook/Twitter campaign names) tied to actors opposing the transfer, especially references to OccupyGhana or NPP statements linking to online actions.
- anchors: OccupyGhana / Occupy Ghana, New Patriotic Party (NPP), Ghana, January 2016 transfer, Guantanamo / Gitmo, Yemeni ex-detainees, news articles and social media excerpts
- bridge_clues: quoted hashtag, online petition, e‑petition, Facebook campaign, Twitter campaign or tweet embed, named online protest, phrase like 'petition to' or 'hashtag' in article, coverage that links to campaign pages
- noisy_or_distracting_clues: lists of Guantanamo detainees, individual detainee biographies, general timelines of Gitmo releases, historical pieces about Guantanamo unrelated to Ghana transfer, non‑campaign blog posts
- expected_evidence_type: A short quoted label or token (e.g., a hashtag, petition title, or campaign name) reproduced in news copy or embedded social posts that explicitly ties the name to opposition to the 2016 Ghana transfer.
- query_shape_implication: Construct queries that combine actor + medium + event keywords (e.g., OccupyGhana OR NPP) + (hashtag OR 'online petition' OR 'e‑petition' OR Facebook OR Twitter) + (Ghana OR Gitmo OR Guantanamo) + 2016; allow wildcarded/substring hashtag patterns rather than exact campaign names.

---

### 262__split0__seg0__left

- idx: 262
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.84
- why_larger: Segment A shifts retrieval focus substantially from finding the game's credits page to switching to a designer-centric evidence family (Kunihiko Tanaka filmography/credits). This is a larger change in retrieval strategy and evidence type (source family and query shape) than B, which only refines the original game-credit target toward Xenoblade Chronicles X.

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
- name: Rstar_target
- kind: endpoint
- retrieved_titles: KOS-MOS, Kunihiko Tanaka, Tetsuya Takahashi, Xenosaga: The Animation, Xenoblade Chronicles 2, Xenosaga Episode III, Xenoblade Chronicles X
- retrieval_focus: {
  "retrieval_focus": "Find an authoritative credit or encyclopedia page that names the video game (developed by Monolith Soft) for which Kunihiko Tanaka is credited as a character designer — target title indicated by summary_1 (Xenoblade Chronicles X).",
  "anchors": ["Kunihiko Tanaka", "Xenoblade Chronicles X", "Monolith Soft"],
  "bridge_clues": ["Kunihiko Tanaka Xenoblade Chronicles X character designer", "Xenoblade Chronicles X credits Kunihiko Tanaka", "Kunihiko Tanaka credits list", "Monolith Soft games Xenoblade Chronicles X credits"],
  "noisy_or_distracting_clues": ["KOS-MOS", "Xenoblade Chronicles 2", "Xenosaga", "Tetsuya Takahashi", other Xeno-series pages that mention Tanaka on different titles (e.g., Xenogears)"],
  "expected_evidence_type": "Official game credits or reliable reference pages (game credits, Wikipedia filmography/credits, MobyGames, Nintendo/Monolith Soft pages) explicitly listing Kunihiko Tanaka as character designer for Xenoblade Chronicles X.",
  "query_shape_implication": "Use short exact-entity queries combining the designer name + role + game title (e.g., \"Kunihiko Tanaka character designer Xenoblade Chronicles X\") to retrieve credit pages; prioritize pages with explicit credits rather than general series summaries."
}

**Sub segment**

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

---

### 267__split0__seg0__left

- idx: 267
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: noisy_entity
- confidence: 0.87
- why_larger: Segment B makes a substantive shift away from the long, name-heavy query toward a concise, show-focused retrieval strategy: it re-anchors retrieval on the Smallville main article and the two primary creators (Alfred Gough and Miles Millar), explicitly deprioritizes noisy episode/person pages, and changes the query shape to surface series-level writing credits. Segment A only slightly refines the focus and keeps similar retrieved titles and noise. B therefore represents the larger retrieval-correction.

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
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Miles Millar, Aquaman (TV pilot), Tempest (Smallville), Smallville, Pilot (Smallville), Characters of Smallville, Chloe Sullivan
- retrieval_focus: Locate authoritative pages that list the primary writers/creators and full writing credits for the TV series Smallville (series article, episode list, or creator bios).
- anchors: Smallville, Justin Hartley, Alfred Gough, Miles Millar
- bridge_clues: creators, writers, writing credits, List of Smallville episodes, Smallville (TV series)
- noisy_or_distracting_clues: Aquaman (TV pilot), Tempest (Smallville), Pilot (Smallville), Characters of Smallville, Chloe Sullivan, Justin Hartley (actor roles)
- expected_evidence_type: Series-level or episode-list pages that explicitly name the show's creators/writers (e.g., Alfred Gough and Miles Millar) or dedicated creator biography pages.
- query_shape_implication: Use concise show-focused queries with writing keywords (e.g., 'Smallville writers', 'Smallville creators', 'Smallville writing credits', or 'Alfred Gough Miles Millar Smallville') to surface pages listing writers; avoid actor-centric queries that return cast-focused pages.

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
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Shift from a long, name-heavy retrieval that returns many person and episode pages toward concise, show-level sources that explicitly name the series creators/writers: prioritize the Smallville main article, the 'List of Smallville episodes' (writing credits section), and bios of the two primary creators (Alfred Gough and Miles Millar). This reduces noise while keeping the retrieval anchored on the core creators rather than enumerating the entire writing staff.
- anchors: Smallville, creators, writers, Alfred Gough, Miles Millar, List of Smallville episodes
- bridge_clues: Justin Hartley, Fox Crane, Passions, Oliver Queen, American TV series based on Superman, created by / developed by, series-level writing credits
- noisy_or_distracting_clues: Individual episode pages (Pilot, Tempest, Finale, specific episode credits), Individual staff/person pages for many writers (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer, etc.), Character pages (Chloe Sullivan, other cast-centric pages), Unrelated pilot pages or other DC projects (Aquaman pilot) that surface because of shared names
- expected_evidence_type: Authoritative series-level statements (Smallville main article or official credits) that explicitly identify the creators/writers (e.g., 'created by Alfred Gough and Miles Millar') and, as secondary confirmation, the episode list showing writer credits or creator biographies that state their role on the show.
- query_shape_implication: Move from long multi-name queries to concise show-focused retrieval gestures: emphasize the show plus 'creators'/'writers' and the two primary creator names as anchor terms. This shape avoids retrieving many separate person or episode pages and surfaces pages that consolidate writing credits.

---

### 55__split0__seg0__left

- idx: 55
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.8
- why_larger: A shifts the retrieval focus substantially from a conjunctive confirmation about both entities to a narrow, entity-focused lookup for the film (establishing Amsterdamned's nationality/origin). This is a clear change in query shape and retrieval strategy (and narrows anchors to film-specific metadata), whereas B mainly consolidates/validates the original joint verification with only minor anchor additions.

**Question**

What culture do both the Capital of the Netherlands and Amsterdamned have in common?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Amsterdam Dutch culture; Amsterdamned (1988) Dutch horror film Dick Maas Dutch cinema
- retrieved_titles: Amsterdamned, Sint, Huub Stapel, The Johnsons, Dick Maas, Down (film), Flodders in America
- retrieval_focus: Confirm that both Amsterdam (the capital) and the film Amsterdamned are associated with Dutch culture / are Dutch in origin.
- anchors: Amsterdam, Amsterdamned, Dick Maas, Netherlands, Dutch cinema
- bridge_clues: Dutch, capital, 1988, film, canals, director Dick Maas, Huub Stapel
- noisy_or_distracting_clues: Sint, The Johnsons, Down (film), Flodders in America
- expected_evidence_type: Short authoritative statements/page snippets that explicitly identify Amsterdam as the capital of the Netherlands and Amsterdamned as a Dutch (1988) film (e.g., encyclopedia or film pages, Dutch cinema summaries).
- query_shape_implication: Conjunctive, fact-confirmation queries: either (A) pages explicitly linking both subjects to 'Dutch' (e.g., 'Amsterdamned Dutch film', 'Amsterdam Dutch capital'), or (B) background pages on 'Culture of the Netherlands' or 'Dutch cinema' to show shared cultural origin.

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
- name: R0_base
- kind: endpoint
- query: Amsterdam Dutch culture; Amsterdamned (1988) Dutch horror film Dick Maas Dutch cinema
- retrieved_titles: Amsterdamned, Sint, Huub Stapel, The Johnsons, Dick Maas, Down (film), Flodders in America
- retrieval_focus: Confirm that both Amsterdam (the capital) and the film Amsterdamned are associated with Dutch culture / are Dutch in origin.
- anchors: Amsterdam, Amsterdamned, Dick Maas, Netherlands, Dutch cinema
- bridge_clues: Dutch, capital, 1988, film, canals, director Dick Maas, Huub Stapel
- noisy_or_distracting_clues: Sint, The Johnsons, Down (film), Flodders in America
- expected_evidence_type: Short authoritative statements/page snippets that explicitly identify Amsterdam as the capital of the Netherlands and Amsterdamned as a Dutch (1988) film (e.g., encyclopedia or film pages, Dutch cinema summaries).
- query_shape_implication: Conjunctive, fact-confirmation queries: either (A) pages explicitly linking both subjects to 'Dutch' (e.g., 'Amsterdamned Dutch film', 'Amsterdam Dutch capital'), or (B) background pages on 'Culture of the Netherlands' or 'Dutch cinema' to show shared cultural origin.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Establish the nationality/origin of the film 'Amsterdamned' (confirm it is a 1988 Dutch film set in Amsterdam), as an intermediate step toward showing both entities share Dutch culture.
- anchors: Amsterdamned, Dick Maas, 1988, Dutch film, canals of Amsterdam, Huub Stapel
- bridge_clues: 1988 horror film, directed by Dick Maas, described as Dutch, set/uses Amsterdam canals, cast includes Huub Stapel
- noisy_or_distracting_clues: Other Dutch films (Sint, The Johnsons), Films with similar Amsterdam settings but different origins, New Amsterdam (place name confusion)
- expected_evidence_type: Short film-encyclopedia or database snippets/infobox lines that explicitly state: 'Amsterdamned is a 1988 Dutch horror film directed by Dick Maas' and mention its Amsterdam setting.
- query_shape_implication: Narrow, entity-focused lookup for film metadata (film title + year/director/descriptor), e.g., searches that retrieve the Amsterdamned film page or Dutch cinema listings rather than general culture pages.

---

### 60__split0__seg0__left

- idx: 60
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: surface_form
- confidence: 0.78
- why_larger: Segment B narrows the retrieval focus from a general HST/STS search to a mission-specific target (STS-31 / NASA mission page) and explicitly emphasizes the launch/deployment date wording (e.g., 'launched 24 April 1990'). This is a clearer, more specific shift in query shape and evidence type toward the date attribute and an authoritative mission page, whereas A remains a milder refinement of the same general focus.

**Question**

The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Hubble Space Telescope STS-31 Space Shuttle Discovery launch date launch year
- retrieved_titles: STS-31, STS-82, STS-103, STS-124, STS-400, STS-51, Goddard High Resolution Spectrograph
- retrieval_focus: Locate an authoritative page (Hubble or STS-31/NASA mission page) that states the Hubble Space Telescope's launch into low Earth orbit and gives the launch year.
- anchors: Hubble Space Telescope, STS-31, Space Shuttle Discovery, launch date
- bridge_clues: launched into low Earth orbit, STS-31 mission (deployment of HST), launch year 1990, 24 April 1990 / deployed 25 April 1990
- noisy_or_distracting_clues: Other STS mission pages retrieved (STS-82, STS-103, STS-124, STS-400, STS-51) that are unrelated to HST's launch, Goddard High Resolution Spectrograph (instrument page)
- expected_evidence_type: A concise factual statement on the mission/launch date (year) from an authoritative source (Hubble overview, STS-31 or NASA mission page).
- query_shape_implication: Targeted, single-attribute lookup (entity → launch year). Expect a single best-match document (HST or STS-31) rather than multi-document synthesis; risk of false positives from similarly numbered STS pages.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: STS-31, Goddard High Resolution Spectrograph, STS-82, Hubble Space Telescope, List of Hubble anniversary images, STS-109, Space Shuttle
- retrieval_focus: Locate a reliable page that states the launch year of the Hubble Space Telescope (the year it was launched into low Earth orbit).
- anchors: Hubble Space Telescope, STS-31, Space Shuttle Discovery
- bridge_clues: launch date / launch year, launched into low Earth orbit, STS-31 mission details, deployment date of HST
- noisy_or_distracting_clues: Goddard High Resolution Spectrograph, STS-82, STS-109, List of Hubble anniversary images, ACS and NICMOS instruments (observation details)
- expected_evidence_type: HST main article or STS-31 mission page explicitly listing the launch/deployment date and year (e.g., '24 April 1990' or '1990').
- query_shape_implication: Short, factual queries combining the telescope or mission name with 'launch year' or 'launch date' — e.g. 'Hubble Space Telescope launch year', 'STS-31 launch year', or 'HST launched into low Earth orbit year'.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Hubble Space Telescope STS-31 Space Shuttle Discovery launch date launch year
- retrieved_titles: STS-31, STS-82, STS-103, STS-124, STS-400, STS-51, Goddard High Resolution Spectrograph
- retrieval_focus: Locate an authoritative page (Hubble or STS-31/NASA mission page) that states the Hubble Space Telescope's launch into low Earth orbit and gives the launch year.
- anchors: Hubble Space Telescope, STS-31, Space Shuttle Discovery, launch date
- bridge_clues: launched into low Earth orbit, STS-31 mission (deployment of HST), launch year 1990, 24 April 1990 / deployed 25 April 1990
- noisy_or_distracting_clues: Other STS mission pages retrieved (STS-82, STS-103, STS-124, STS-400, STS-51) that are unrelated to HST's launch, Goddard High Resolution Spectrograph (instrument page)
- expected_evidence_type: A concise factual statement on the mission/launch date (year) from an authoritative source (Hubble overview, STS-31 or NASA mission page).
- query_shape_implication: Targeted, single-attribute lookup (entity → launch year). Expect a single best-match document (HST or STS-31) rather than multi-document synthesis; risk of false positives from similarly numbered STS pages.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Target a mission-specific authoritative source (STS-31 / NASA mission page or Space Shuttle Discovery page) that explicitly lists the Hubble Space Telescope's launch date and year.
- anchors: STS-31, Space Shuttle Discovery, Hubble Space Telescope, launch date / launch year
- bridge_clues: STS-31 deployed HST, launched 24 April 1990, deployment 25 April 1990, mission summary / launch year 1990
- noisy_or_distracting_clues: Other STS mission pages (e.g., STS-82, STS-109) that are not STS-31, Instrument pages (ACS, NICMOS, Goddard High Resolution Spectrograph), Hubble anniversary or image gallery pages that mention HST events but may not state launch date concisely
- expected_evidence_type: A concise mission-summary line on an official NASA / STS-31 page or HST overview that states the launch date and year (e.g., '24 April 1990' or '1990').
- query_shape_implication: Short mission-focused query combining 'STS-31' or 'Space Shuttle Discovery' with 'launch date' or 'launch year' to retrieve a single authoritative mission page rather than broader HST histories.

---

### 90__split0__seg0__left

- idx: 90
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.83
- why_larger: Segment B changes the retrieval strategy more substantially: it decomposes the single combined verification into two ordered sub-queries, shifts the retrieval focus to distinct evidence families (authoritative Lumbini description vs local/gazetteer listing for Imiliya), and explicitly alters expected evidence and query shape. Segment A is mainly a modest refinement of the same combined focus.

**Question**

Imiliya is a town located in what pilgrimage site?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Imiliya Kapilvastu Lumbini Nepal Maya Devi Temple sacred garden monastic zone UNESCO coordinates proximity
- retrieved_titles: Maya Devi Temple, Lumbini, Imiliya, Basantapur, Kapilvastu, Manpur, Lumbini, Mahuwa, Lumbini, Hariharpur, Kapilvastu, Motipur, Kapilvastu
- retrieval_focus: Find authoritative sources that explicitly place Imiliya (a town in Kapilvastu District) within the Lumbini pilgrimage area (the Buddha birthplace site) or that tie Imiliya geographically to Lumbini landmarks (e.g., Mayadevi Temple / sacred garden / Rummindei).
- anchors: Imiliya, Kapilvastu District, Lumbini, Mayadevi Temple, Rummindei, Lumbini Development Trust
- bridge_clues: birthplace of Siddhartha Gautama (Gautama Buddha), Mayadevi Temple / Sacred Garden, UNESCO World Heritage designation for Lumbini, local/administrative placement linking a town to Lumbini
- noisy_or_distracting_clues: other Kapilvastu towns in retrieved list (Basantapur, Manpur, Mahuwa, Hariharpur, Motipur) that are irrelevant to pilgrimage status, purely coordinate/proximity results that don't state pilgrimage association, administrative-name confusion (Rupandehi vs Kapilvastu) that could mislead containment inference
- expected_evidence_type: Explicit textual statements or authoritative map/gazetteer entries (Wikipedia, UNESCO or Lumbini Development Trust pages, government/local sources, reputable travel guides) that directly associate Imiliya with Lumbini or its pilgrimage landmarks.
- query_shape_implication: Searches should combine the town name with pilgrimage keywords and landmarks (e.g., 'Imiliya Lumbini', 'Imiliya Mayadevi Temple', 'Imiliya sacred garden Lumbini', 'Imiliya Lumbini UNESCO') and resolve place-name variants and hierarchical containment (town → district → pilgrimage site) rather than broad district-only queries.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Imiliya, Lumbini, Taulihawa, Nepal, Basantapur, Kapilvastu, Buddhist pilgrimage sites in Nepal, Manpur, Lumbini, Mahuwa, Lumbini
- retrieval_focus: Confirm that Imiliya (a town in Kapilvastu District) is located within the pilgrimage area Lumbini and that Lumbini is identified as a major Buddhist pilgrimage site associated with the birthplace of Siddhartha Gautama (Mayadevi Temple/Rummindei).
- anchors: Imiliya, Lumbini, Kapilvastu District, Mayadevi Temple, Siddhartha Gautama / Gautama Buddha, Rummindei, Lumbini Development Trust, Ashoka pillar
- bridge_clues: Statements identifying Lumbini as the birthplace of Siddhartha Gautama and a major Buddhist pilgrimage site, References or maps linking Imiliya to Kapilvastu District within the Lumbini area, Mentions of Mayadevi Temple, Rummindei, or Ashoka pillar as pilgrimage landmarks in Lumbini, UNESCO designation or other authoritative descriptions of Lumbini as a pilgrimage site
- noisy_or_distracting_clues: Nearby town pages (Taulihawa, Basantapur, Manpur, Mahuwa) that may not mention pilgrimage context, 'Buddhist pilgrimage sites in Nepal' or other list pages that are broad and may not tie Imiliya specifically to Lumbini, Administrative/placement ambiguity between Kapilvastu District and nearby districts (e.g., Rupandehi) that could confuse location links, Local/municipal pages focused on Kapilvastu without explicit reference to Lumbini landmarks
- expected_evidence_type: Short authoritative lines: (a) a Lumbini page or UNESCO/heritage source calling Lumbini a Buddhist pilgrimage site and naming key landmarks (Mayadevi/Rummindei), and (b) a local/place or map source showing Imiliya is in Kapilvastu District within the Lumbini area.
- query_shape_implication: Use focused entity-to-site verification queries such as 'Imiliya Lumbini', 'Imiliya Kapilvastu Lumbini pilgrimage', or site-centered queries like 'Lumbini Mayadevi Temple UNESCO birthplace of Buddha' to retrieve concise confirming passages.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Imiliya Kapilvastu Lumbini Nepal Maya Devi Temple sacred garden monastic zone UNESCO coordinates proximity
- retrieved_titles: Maya Devi Temple, Lumbini, Imiliya, Basantapur, Kapilvastu, Manpur, Lumbini, Mahuwa, Lumbini, Hariharpur, Kapilvastu, Motipur, Kapilvastu
- retrieval_focus: Find authoritative sources that explicitly place Imiliya (a town in Kapilvastu District) within the Lumbini pilgrimage area (the Buddha birthplace site) or that tie Imiliya geographically to Lumbini landmarks (e.g., Mayadevi Temple / sacred garden / Rummindei).
- anchors: Imiliya, Kapilvastu District, Lumbini, Mayadevi Temple, Rummindei, Lumbini Development Trust
- bridge_clues: birthplace of Siddhartha Gautama (Gautama Buddha), Mayadevi Temple / Sacred Garden, UNESCO World Heritage designation for Lumbini, local/administrative placement linking a town to Lumbini
- noisy_or_distracting_clues: other Kapilvastu towns in retrieved list (Basantapur, Manpur, Mahuwa, Hariharpur, Motipur) that are irrelevant to pilgrimage status, purely coordinate/proximity results that don't state pilgrimage association, administrative-name confusion (Rupandehi vs Kapilvastu) that could mislead containment inference
- expected_evidence_type: Explicit textual statements or authoritative map/gazetteer entries (Wikipedia, UNESCO or Lumbini Development Trust pages, government/local sources, reputable travel guides) that directly associate Imiliya with Lumbini or its pilgrimage landmarks.
- query_shape_implication: Searches should combine the town name with pilgrimage keywords and landmarks (e.g., 'Imiliya Lumbini', 'Imiliya Mayadevi Temple', 'Imiliya sacred garden Lumbini', 'Imiliya Lumbini UNESCO') and resolve place-name variants and hierarchical containment (town → district → pilgrimage site) rather than broad district-only queries.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Split verification into two smaller, ordered checks: (A) confirm that Lumbini is explicitly described as the Buddhist pilgrimage site associated with the birthplace of Siddhartha Gautama and that key pilgrimage landmarks (Mayadevi Temple, Rummindei, Ashoka pillar, UNESCO designation) are named; (B) independently confirm that Imiliya is an administrative place in Kapilvastu District (town/VDC/ward) without yet asserting it lies inside the Lumbini sacred garden or monastic zone.
- anchors: Lumbini, Mayadevi Temple, Rummindei, UNESCO World Heritage / Lumbini Development Trust, Imiliya, Kapilvastu District
- bridge_clues: explicit sentence calling Lumbini the birthplace of Siddhartha Gautama and a major Buddhist pilgrimage site, references to Mayadevi Temple / Sacred Garden / Ashoka pillar / Rummindei as pilgrimage landmarks in Lumbini, authoritative listing of Imiliya as a town/VDC/ward in Kapilvastu District (gazetteer or local page), map or administrative source placing Imiliya within Kapilvastu (but not yet tying it to the sacred garden)
- noisy_or_distracting_clues: pages listing many Kapilvastu villages (Basantapur, Manpur, Mahuwa, Taulihawa) that don't mention pilgrimage landmarks, coordinate-only map pins that show proximity but no textual pilgrimage claim, broader 'Buddhist sites in Nepal' lists that mention Lumbini but don't name local administrative places like Imiliya, confusing district mentions (Rupandehi vs Kapilvastu) that create false containment links
- expected_evidence_type: Two short authoritative passages: (1) Lumbini/UNESCO/Lumbini Development Trust or encyclopedia lines explicitly naming Lumbini as Buddha's birthplace and a pilgrimage site with Mayadevi/Rummindei/Ashoka pillar; (2) a local/place or government/gazetteer entry (or Imiliya Wikipedia stub) listing Imiliya as a settlement in Kapilvastu District.
- query_shape_implication: Run two focused queries rather than one broad combined query: one targeting Lumbini landmarks and UNESCO/heritage language (e.g., 'Lumbini Mayadevi Temple birthplace UNESCO pilgrimage'), and one targeting the place-name administrative listing (e.g., 'Imiliya Kapilvastu town Imiliya Nepal page' or 'Imiliya village Kapilvastu District list').

---

## right_fail (10 total, showing 10)

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

### 169__split0__seg0__right

- idx: 169
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.7
- why_larger: Segment A transitions from a detailed, procedural midpoint (explicit source priorities, noise filters, anchor list and precise query-shape guidance) to the Rstar_target endpoint with finalized retrieval focus and concrete retrieved titles. That represents a bigger shift in retrieval strategy and query shape than B, which already starts as a straightforward base query/verification state and moves to the same endpoint.

**Question**

What movie did "the king of cool" play in with Bud Ekins as his stunt double?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Bud Ekins Steve McQueen stunt double Bullitt? "The Great Escape" motorcycle stunt details who performed jump stunt credits filming location
- retrieved_titles: Bud Ekins, Stunt double, Stunt coordinator, Stunt, Butch Laswell, Corey Scott, Todd Bryant
- retrieval_focus: Verify and cite which Steve McQueen film(s) Bud Ekins served as a stunt double for, with primary focus on confirming the motorcycle-stunt credit in The Great Escape and resolving the ambiguity about Bullitt.
- anchors: Bud Ekins, Steve McQueen ("The King of Cool"), The Great Escape, Bullitt
- bridge_clues: motorcycle stunt / famous motorcycle jump, stunt double credit, stunt credits in filmographies/IMDb, Stuntmen's Hall of Fame / obituary / biography entries
- noisy_or_distracting_clues: Butch Laswell, Corey Scott, Todd Bryant, generic pages titled 'Stunt' or 'Stunt coordinator' that do not mention McQueen or Ekins
- expected_evidence_type: Authoritative film-credit records or reputable secondary sources (IMDb/BFI entries, film credits, biographies, obituaries, Hall of Fame pages, production notes) explicitly stating Ekins doubled McQueen on The Great Escape and listing any other films where he doubled McQueen.
- query_shape_implication: Use narrow, factual queries and source filters (e.g., 'Bud Ekins Steve McQueen The Great Escape stunt double', 'Bud Ekins Bullitt stunt double', 'who did the motorcycle jump in The Great Escape') aimed at crediting sources rather than broad 'stunt' topic searches.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Bud Ekins, The Great Escape (film), Triumph TR6 Trophy, Steve McQueen, Stunt double, Dave Ekins, Motorcycle stunt riding
- retrieval_focus: {
  "retrieval_focus": "Verify which film(s) Bud Ekins served as Steve McQueen’s stunt double — primary candidate: The Great Escape; check whether he also doubled McQueen in Bullitt or only appears in Bullitt credits.",
  "anchors": ["Bud Ekins", "Steve McQueen (\"The King of Cool\")", "The Great Escape", "Bullitt"],
  "bridge_clues": ["stunt double", "doubled for", "motorcycle stunt", "stunt credits", "famous motorcycle jump"],
  "noisy_or_distracting_clues": ["Triumph TR6 Trophy", "Dave Ekins", "Motorcycle stunt riding (general)", "Stunt double (generic page)", empty],
  "expected_evidence_type": "Short biographical or film-credit sentences explicitly stating 'Bud Ekins served as Steve McQueen’s stunt double' on The Great Escape (and any mentions clarifying whether he doubled McQueen in Bullitt).",
  "query_shape_implication": "Use conjunctive short queries combining actor alias and stunt relation, e.g. 'Bud Ekins Steve McQueen stunt double The Great Escape' and a follow-up 'Bud Ekins Steve McQueen stunt double Bullitt' ; include alias mapping ('The King of Cool' -> Steve McQueen)."
}

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow to authoritative credit-confirmation: verify that Bud Ekins served as Steve McQueen's stunt double on The Great Escape (especially the motorcycle jump) and explicitly check primary credit sources to resolve whether he also doubled McQueen in Bullitt. Prioritize obituaries, reputable biographies, film-credit databases, and Hall-of-Fame entries rather than generic 'stunt' pages.
- anchors: Bud Ekins, Steve McQueen ("The King of Cool"), The Great Escape, Bullitt, Stuntmen's Hall of Fame / obituary
- bridge_clues: "stunt double for Steve McQueen", "performed the motorcycle jump", credited as stuntman in filmography / IMDb / BFI, obituary or Hall of Fame entry mentioning The Great Escape
- noisy_or_distracting_clues: Triumph TR6 Trophy (motorcycle model) references, Dave Ekins (relative/other rider), general pages titled 'Stunt' or 'Stunt coordinator' without film credits, motorcycling forums or fan pages that repeat claims without sourcing
- expected_evidence_type: Short, explicit credit statements from authoritative sources (IMDb/BFI entries, NYT/THR obituaries, reputable biographies, Stuntmen's Hall of Fame) that say 'Bud Ekins served as Steve McQueen's stunt double on The Great Escape' and, separately, clear statements confirming or denying a doubling credit on Bullitt.
- query_shape_implication: Use focused phrase searches and source filters (exact phrase + site filters) such as '"Bud Ekins" "stunt double" "The Great Escape"' across reputable outlets; then a narrow follow-up search for 'Bud Ekins Bullitt' to resolve that single ambiguity. Avoid broad 'stunt' or generic motorcycle-topic queries.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Bud Ekins, The Great Escape (film), Triumph TR6 Trophy, Steve McQueen, Stunt double, Dave Ekins, Motorcycle stunt riding
- retrieval_focus: {
  "retrieval_focus": "Verify which film(s) Bud Ekins served as Steve McQueen’s stunt double — primary candidate: The Great Escape; check whether he also doubled McQueen in Bullitt or only appears in Bullitt credits.",
  "anchors": ["Bud Ekins", "Steve McQueen (\"The King of Cool\")", "The Great Escape", "Bullitt"],
  "bridge_clues": ["stunt double", "doubled for", "motorcycle stunt", "stunt credits", "famous motorcycle jump"],
  "noisy_or_distracting_clues": ["Triumph TR6 Trophy", "Dave Ekins", "Motorcycle stunt riding (general)", "Stunt double (generic page)", empty],
  "expected_evidence_type": "Short biographical or film-credit sentences explicitly stating 'Bud Ekins served as Steve McQueen’s stunt double' on The Great Escape (and any mentions clarifying whether he doubled McQueen in Bullitt).",
  "query_shape_implication": "Use conjunctive short queries combining actor alias and stunt relation, e.g. 'Bud Ekins Steve McQueen stunt double The Great Escape' and a follow-up 'Bud Ekins Steve McQueen stunt double Bullitt' ; include alias mapping ('The King of Cool' -> Steve McQueen)."
}

---

### 180__split0__seg0__right

- idx: 180
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: answer_type
- confidence: 0.86
- why_larger: Segment A's from_state is a narrow midpoint focused only on confirming the 11th-album identity (no retrieved titles and explicitly defers the release date). Its to_state expands scope to the full endpoint: identifies the band, adds multiple retrieved album titles, and explicitly adds retrieval of the album's official release date. That is a larger shift (adds concrete anchors and a new answer-type/date retrieval) than B, whose from_state already contained similar retrieved titles and an endpoint-like retrieval_focus.

**Question**

What is the date of released for the eleventh studio album of the highest-selling heavy metal group from Canada?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Annihilator discography "11th studio album" release date OR "Annihilator" "11th album" release date AND "highest-selling Canadian heavy metal" confirmation
- retrieved_titles: Annihilator discography, Set the World on Fire (Annihilator album), Metal (Annihilator album), All for You (Annihilator album), Annihilator (album), Annihilator (band), The One (EP)
- retrieval_focus: Confirm that the 'highest-selling Canadian heavy metal group' refers to Annihilator, then find the name and the official release date of that band's 11th studio album.
- anchors: Annihilator, Annihilator discography, 11th studio album, Annihilator 11th album release date
- bridge_clues: summary_1 flags Annihilator as the likely target for 'highest-selling Canadian heavy metal group', 'Annihilator discography' page in retrieved_titles should list album order and links to individual album pages, Retrieved individual album pages (e.g., 'Set the World on Fire', 'Metal', 'All for You', 'Annihilator (album)') may contain release dates to verify
- noisy_or_distracting_clues: Thor mention in summary_1 — unrelated to the highest-selling Canadian heavy metal group, Multiple album titles retrieved that may not be the 11th (noise from similarly named or earlier/later albums), 'The One (EP)' — not a studio album and thus a distractor, Complex boolean operators in the visible query may reduce recall or omit simpler phrasing
- expected_evidence_type: Authoritative discography entry or official band/label page, or reputable music-database article (e.g., Wikipedia/AllMusic/Discogs) that explicitly shows the album sequence (identifies the 11th studio album) and provides the album's release date (day/month/year or month/year).
- query_shape_implication: Perform a two-step, focused search: first confirm artist identity (Annihilator = highest-selling Canadian heavy metal group), then query 'Annihilator 11th studio album' or 'Annihilator "11th" album release date' or open the discography page and the specific album page to extract the release date. Avoid generic/over-broad queries and exclude EPs and non-studio releases.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Annihilator (band), Annihilator discography, Set the World on Fire (Annihilator album), All for You (Annihilator album), Metal (Annihilator album), Schizo Deluxe, Refresh the Demon
- retrieval_focus: Identify the band referenced (likely Annihilator), find which studio album is their 11th, and retrieve that album's official release date.
- anchors: Annihilator (band), Annihilator discography, retrieved album titles (Set the World on Fire, All for You, Metal, Schizo Deluxe, Refresh the Demon)
- bridge_clues: Confirm that 'highest-selling heavy metal group from Canada' refers to Annihilator via a summary or band page, Use the discography page to determine the ordered list of studio albums and pick the 11th entry, Open the 11th-album page (or the discography entry) to read the official release date
- noisy_or_distracting_clues: Multiple album titles present that are not labeled by ordinal — risk of miscounting which is 11th, Summary mentions Thor (unrelated) and other passages with no clear link to this query, creating irrelevant context
- expected_evidence_type: Discography listing or band page that enumerates studio albums in order, and the specific album page or discography entry that gives the album's official release date (day/month/year and region/label if available).
- query_shape_implication: First query should target the band discography (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') to get album order; second query should target the identified album name plus 'release date' (e.g., '<Album Name> release date' or 'Annihilator 11th studio album release date').

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Confirm which studio album is Annihilator's 11th (identify the album title and verify its ordinal position in the band's official discography). Do not yet retrieve the album's release date.
- anchors: Annihilator discography (ordered list of studio albums), studio albums only (exclude EPs/compilations/live albums), ordinal position: 11th, album title corresponding to 11th entry
- bridge_clues: The band's discography page or a reputable music database will list studio albums in chronological order and allow unambiguous counting to the 11th entry., Some album pages include a lead sentence like 'X is the nth studio album by Annihilator' — that directly confirms ordinal without counting., Cross-checking two authoritative sources (e.g., band/Wikipedia/discography database) reduces risk of miscounting due to non-studio releases being mixed in.
- noisy_or_distracting_clues: EPs, compilations, live albums and reissues that are often shown alongside studio albums and can lead to miscounting., Self-titled album names or similarly named releases (e.g., 'Annihilator') that might be confused with other entries., Regional/label variations and deluxe editions that change listed release years but do not change album ordinal., References to other Canadian metal acts (e.g., Thor) in the supplied context — irrelevant to identifying Annihilator's 11th studio album.
- expected_evidence_type: An authoritative discography or band page that either labels the album as the band's '11th studio album' or provides a clear chronological list of studio albums from which the 11th entry (album title) can be unambiguously determined.
- query_shape_implication: Focus the next retrieval on the discography or album-listing page (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') and either open the album page that explicitly states 'X is the 11th studio album' or count studio entries on the discography to extract the 11th album title. Defer querying for the release date until after the 11th album title is confirmed.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Annihilator (band), Annihilator discography, Set the World on Fire (Annihilator album), All for You (Annihilator album), Metal (Annihilator album), Schizo Deluxe, Refresh the Demon
- retrieval_focus: Identify the band referenced (likely Annihilator), find which studio album is their 11th, and retrieve that album's official release date.
- anchors: Annihilator (band), Annihilator discography, retrieved album titles (Set the World on Fire, All for You, Metal, Schizo Deluxe, Refresh the Demon)
- bridge_clues: Confirm that 'highest-selling heavy metal group from Canada' refers to Annihilator via a summary or band page, Use the discography page to determine the ordered list of studio albums and pick the 11th entry, Open the 11th-album page (or the discography entry) to read the official release date
- noisy_or_distracting_clues: Multiple album titles present that are not labeled by ordinal — risk of miscounting which is 11th, Summary mentions Thor (unrelated) and other passages with no clear link to this query, creating irrelevant context
- expected_evidence_type: Discography listing or band page that enumerates studio albums in order, and the specific album page or discography entry that gives the album's official release date (day/month/year and region/label if available).
- query_shape_implication: First query should target the band discography (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') to get album order; second query should target the identified album name plus 'release date' (e.g., '<Album Name> release date' or 'Annihilator 11th studio album release date').

---

### 227__split0__seg0__right

- idx: 227
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: Segment A shifts retrieval focus more: its from_state intentionally avoids publisher pages and targets only confirming Evan Peters->Quicksilver, while its to_state (Rstar_target) adds the publisher/character confirmation (Marvel Comics + Quicksilver). This introduces a new entity-anchor and an added actor->character->publisher linkage that B already included in its from_state, so A requires a larger update.

**Question**

Evan Peters had a role as the fictional superhero from comic books by what publisher?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Evan Peters Quicksilver Pietro Maximoff portrayal filmography "X-Men: Days of Future Past" "X-Men: Apocalypse" Marvel Comics
- retrieved_titles: Quicksilver (comics), Days of Future Past, X-Men: Days of Future Past, All-New X-Men, Classic X-Men, Days of Future Past (disambiguation), New Canaanites
- retrieval_focus: Find an authoritative source that explicitly links Evan Peters to the character Quicksilver (Pietro Maximoff) in the X‑Men films and an explicit statement that Quicksilver is published by Marvel Comics (actor->character and character->publisher).
- anchors: Evan Peters, Quicksilver, Pietro Maximoff, X-Men: Days of Future Past, X-Men: Apocalypse, Marvel Comics
- bridge_clues: Retrieved title 'Quicksilver (comics)' — character page likely names publisher, Retrieved film titles ('X-Men: Days of Future Past', 'X-Men: Apocalypse') — link actor to role, Query already targets 'Evan Peters Quicksilver' (actor+character), summary_1 states the superhero role originates from Marvel Comics
- noisy_or_distracting_clues: All-New X-Men (comic series) — broader series noise, Classic X-Men — series-level pages not specific to the film role, Days of Future Past (disambiguation) — disambiguation pages, New Canaanites — appears unrelated to actor/character
- expected_evidence_type: A filmography or news/encyclopedic page stating 'Evan Peters portrayed Quicksilver (Pietro Maximoff)' plus a character/comics page or encyclopedic line stating 'Quicksilver is a fictional superhero appearing in American comic books published by Marvel Comics'.
- query_shape_implication: Current query mixes actor+character+film titles; next queries should be narrow, e.g. 'Evan Peters Quicksilver role', 'Evan Peters portrayed Quicksilver', and 'Quicksilver Pietro Maximoff publisher Marvel Comics' or directly open the actor filmography and the Quicksilver character page.

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

---

### 247__split0__seg0__right

- idx: 247
- split_iter: 0
- task_kind: right_recovery
- expected: A
- predicted: B
- correct: 0.0
- dominant_gap_type: query_shape
- confidence: 0.78
- why_larger: Segment B moves from a generated midpoint with no query and no retrieved titles to a focused endpoint—requiring creation of a concrete query shape and retrieval of news/social posts (hashtags, petition titles). That is a bigger shift in retrieval focus and required query formation than A, which already had a specific query and many candidate titles.

**Question**

What is another name for the online protest that opposed the transfer of ex-detainees from Guantanamo Bay in 2016?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: OccupyGhana online protest name hashtag 2016 Ghana transfer Guantanamo Yemeni ex-detainees
- retrieved_titles: Gitmo detainees Ghana transfer controversy, List of Yemeni detainees at Guantanamo Bay, Timeline of the release and transfer of Guantanamo Bay detainees, Obaidullah (detainee), Guantanamo Bay hunger strikes, List of Uyghur detainees at Guantanamo Bay, Inayatullah (Guantanamo detainee 10029)
- retrieval_focus: Locate news or social-media mentions (in coverage of the Jan 2016 Ghana transfer of Yemeni ex-detainees) that explicitly name an online protest, campaign title, or hashtag opposing the transfer.
- anchors: OccupyGhana, New Patriotic Party (NPP), Ghana, January 2016 transfer, Yemeni ex-detainees, Gitmo detainees Ghana transfer controversy
- bridge_clues: online campaign, hashtag, e-petition, social media protest, named online protest, OccupyGhana online actions, coverage of public reaction
- noisy_or_distracting_clues: List of Yemeni detainees at Guantanamo Bay, Timeline of the release and transfer of Guantanamo Bay detainees, individual detainee biographies (Obaidullah, Inayatullah), Guantanamo Bay hunger strikes, general Gitmo lists and timelines
- expected_evidence_type: An explicit phrase in a news article or social-media excerpt quoting a campaign name or hashtag (e.g., a named online petition, quoted Twitter hashtag, or titled online protest) that identifies the online protest opposing the transfer.
- query_shape_implication: Queries should include terms for hashtags/online campaigns (hashtag, petition, "online protest") combined with 'Ghana', '2016', and 'Guantanamo' or 'Gitmo' and 'OccupyGhana' — likely locating news coverage or social posts rather than detainee-list pages.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Gitmo detainees Ghana transfer controversy, List of Yemeni detainees at Guantanamo Bay, Kamunting, Gitmo on the Platte, Occupy Ghana, Yemeni Revolution, Obaidullah (detainee)
- retrieval_focus: Locate a named online protest (campaign title, e‑petition name, or hashtag) that opposed Ghana's January 2016 acceptance/transfer of Yemeni ex-detainees from Guantanamo Bay; find a news or social‑media mention that gives an alternate name for the protest.
- anchors: Ghana, 2016 transfer, Gitmo, Gitmo detainees, Yemeni ex-detainees, OccupyGhana, New Patriotic Party
- bridge_clues: online protest, online campaign, hashtag, e-petition, named campaign, social media, opposed transfer, called for return
- noisy_or_distracting_clues: List of Yemeni detainees at Guantanamo Bay, Kamunting, Gitmo on the Platte, Yemeni Revolution, Obaidullah (detainee)
- expected_evidence_type: A short label or phrase (campaign title or hashtag) quoted in a news article or social‑media report that explicitly ties the name to the 2016 Ghana transfer protest.
- query_shape_implication: Use compact, token-rich queries combining actor + medium + event and year, e.g. 'OccupyGhana online campaign Guantanamo 2016 hashtag', 'Ghana Gitmo online protest name 2016', or 'online petition Ghana Gitmo detainees 2016'.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow to contemporary news and social‑media coverage of the Jan 2016 Ghana transfer that explicitly quote or reproduce online campaign identifiers (hashtags, e‑petition titles, Facebook/Twitter campaign names) tied to actors opposing the transfer, especially references to OccupyGhana or NPP statements linking to online actions.
- anchors: OccupyGhana / Occupy Ghana, New Patriotic Party (NPP), Ghana, January 2016 transfer, Guantanamo / Gitmo, Yemeni ex-detainees, news articles and social media excerpts
- bridge_clues: quoted hashtag, online petition, e‑petition, Facebook campaign, Twitter campaign or tweet embed, named online protest, phrase like 'petition to' or 'hashtag' in article, coverage that links to campaign pages
- noisy_or_distracting_clues: lists of Guantanamo detainees, individual detainee biographies, general timelines of Gitmo releases, historical pieces about Guantanamo unrelated to Ghana transfer, non‑campaign blog posts
- expected_evidence_type: A short quoted label or token (e.g., a hashtag, petition title, or campaign name) reproduced in news copy or embedded social posts that explicitly ties the name to opposition to the 2016 Ghana transfer.
- query_shape_implication: Construct queries that combine actor + medium + event keywords (e.g., OccupyGhana OR NPP) + (hashtag OR 'online petition' OR 'e‑petition' OR Facebook OR Twitter) + (Ghana OR Gitmo OR Guantanamo) + 2016; allow wildcarded/substring hashtag patterns rather than exact campaign names.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Gitmo detainees Ghana transfer controversy, List of Yemeni detainees at Guantanamo Bay, Kamunting, Gitmo on the Platte, Occupy Ghana, Yemeni Revolution, Obaidullah (detainee)
- retrieval_focus: Locate a named online protest (campaign title, e‑petition name, or hashtag) that opposed Ghana's January 2016 acceptance/transfer of Yemeni ex-detainees from Guantanamo Bay; find a news or social‑media mention that gives an alternate name for the protest.
- anchors: Ghana, 2016 transfer, Gitmo, Gitmo detainees, Yemeni ex-detainees, OccupyGhana, New Patriotic Party
- bridge_clues: online protest, online campaign, hashtag, e-petition, named campaign, social media, opposed transfer, called for return
- noisy_or_distracting_clues: List of Yemeni detainees at Guantanamo Bay, Kamunting, Gitmo on the Platte, Yemeni Revolution, Obaidullah (detainee)
- expected_evidence_type: A short label or phrase (campaign title or hashtag) quoted in a news article or social‑media report that explicitly ties the name to the 2016 Ghana transfer protest.
- query_shape_implication: Use compact, token-rich queries combining actor + medium + event and year, e.g. 'OccupyGhana online campaign Guantanamo 2016 hashtag', 'Ghana Gitmo online protest name 2016', or 'online petition Ghana Gitmo detainees 2016'.

---

### 262__split0__seg0__right

- idx: 262
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.85
- why_larger: Segment A shifts the retrieval anchor/focus from a designer-centric search (find Kunihiko Tanaka's filmography/credits) to directly targeting the game credit that names the Monolith Soft title (game-centric verification). This is a substantive anchor/bridge change and an evidence-family shift (designer sources → game/credit page). Segment B mainly refines/cleans a noisy initial query but already targeted the same game-credit endpoint, so its update magnitude is smaller.

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
- name: Rstar_target
- kind: endpoint
- retrieved_titles: KOS-MOS, Kunihiko Tanaka, Tetsuya Takahashi, Xenosaga: The Animation, Xenoblade Chronicles 2, Xenosaga Episode III, Xenoblade Chronicles X
- retrieval_focus: {
  "retrieval_focus": "Find an authoritative credit or encyclopedia page that names the video game (developed by Monolith Soft) for which Kunihiko Tanaka is credited as a character designer — target title indicated by summary_1 (Xenoblade Chronicles X).",
  "anchors": ["Kunihiko Tanaka", "Xenoblade Chronicles X", "Monolith Soft"],
  "bridge_clues": ["Kunihiko Tanaka Xenoblade Chronicles X character designer", "Xenoblade Chronicles X credits Kunihiko Tanaka", "Kunihiko Tanaka credits list", "Monolith Soft games Xenoblade Chronicles X credits"],
  "noisy_or_distracting_clues": ["KOS-MOS", "Xenoblade Chronicles 2", "Xenosaga", "Tetsuya Takahashi", other Xeno-series pages that mention Tanaka on different titles (e.g., Xenogears)"],
  "expected_evidence_type": "Official game credits or reliable reference pages (game credits, Wikipedia filmography/credits, MobyGames, Nintendo/Monolith Soft pages) explicitly listing Kunihiko Tanaka as character designer for Xenoblade Chronicles X.",
  "query_shape_implication": "Use short exact-entity queries combining the designer name + role + game title (e.g., \"Kunihiko Tanaka character designer Xenoblade Chronicles X\") to retrieve credit pages; prioritize pages with explicit credits rather than general series summaries."
}

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Find a designer-centric, authoritative credits/filmography page for Kunihiko Tanaka that enumerates his game credits and roles (so the target title can be confirmed from the creator's side rather than the game's credits page).
- anchors: Kunihiko Tanaka, filmography, credits, works, game credits
- bridge_clues: Kunihiko Tanaka filmography or credits page, Kunihiko Tanaka Wikipedia biography, MobyGames / Giant Bomb profile for Kunihiko Tanaka, official artist portfolio or agency page listing works, lists of titles credited to Kunihiko Tanaka (look for Xenoblade Chronicles X among them)
- noisy_or_distracting_clues: KOS-MOS, Xenosaga, Xenogears, Tetsuya Takahashi, other Xenoblade titles (e.g., Xenoblade Chronicles 2), fan sites or forum mentions that are not authoritative
- expected_evidence_type: Designer-focused sources: Wikipedia filmography, official artist/agency portfolio, or reputable game-credit aggregators (MobyGames, Giant Bomb) that list per-title credits and explicitly name Kunihiko Tanaka's role on specific games.
- query_shape_implication: Use designer-focused queries (e.g., variations of 'Kunihiko Tanaka filmography' or 'Kunihiko Tanaka credits') to retrieve an authoritative list of works; once the designer's credits page confirms candidate titles, pivot to the game's official credits to verify role and developer.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: KOS-MOS, Kunihiko Tanaka, Tetsuya Takahashi, Xenosaga: The Animation, Xenoblade Chronicles 2, Xenosaga Episode III, Xenoblade Chronicles X
- retrieval_focus: {
  "retrieval_focus": "Find an authoritative credit or encyclopedia page that names the video game (developed by Monolith Soft) for which Kunihiko Tanaka is credited as a character designer — target title indicated by summary_1 (Xenoblade Chronicles X).",
  "anchors": ["Kunihiko Tanaka", "Xenoblade Chronicles X", "Monolith Soft"],
  "bridge_clues": ["Kunihiko Tanaka Xenoblade Chronicles X character designer", "Xenoblade Chronicles X credits Kunihiko Tanaka", "Kunihiko Tanaka credits list", "Monolith Soft games Xenoblade Chronicles X credits"],
  "noisy_or_distracting_clues": ["KOS-MOS", "Xenoblade Chronicles 2", "Xenosaga", "Tetsuya Takahashi", other Xeno-series pages that mention Tanaka on different titles (e.g., Xenogears)"],
  "expected_evidence_type": "Official game credits or reliable reference pages (game credits, Wikipedia filmography/credits, MobyGames, Nintendo/Monolith Soft pages) explicitly listing Kunihiko Tanaka as character designer for Xenoblade Chronicles X.",
  "query_shape_implication": "Use short exact-entity queries combining the designer name + role + game title (e.g., \"Kunihiko Tanaka character designer Xenoblade Chronicles X\") to retrieve credit pages; prioritize pages with explicit credits rather than general series summaries."
}

---

### 55__split0__seg0__right

- idx: 55
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.92
- why_larger: Segment A shifts from a narrow, film-focused intermediate (establishing Amsterdamned's nationality) to a broader verification that both the film and the city share Dutch culture — it adds new anchors (Amsterdam, Netherlands) and expands bridge clues to connect two entities rather than confirming one. Segment B shows little change (its from_state already targets both entities).

**Question**

What culture do both the Capital of the Netherlands and Amsterdamned have in common?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Amsterdam Dutch culture; Amsterdamned (1988) Dutch horror film Dick Maas Dutch cinema
- retrieved_titles: Amsterdamned, Sint, Huub Stapel, The Johnsons, Dick Maas, Down (film), Flodders in America
- retrieval_focus: Confirm that both Amsterdam (the capital) and the film Amsterdamned are associated with Dutch culture / are Dutch in origin.
- anchors: Amsterdam, Amsterdamned, Dick Maas, Netherlands, Dutch cinema
- bridge_clues: Dutch, capital, 1988, film, canals, director Dick Maas, Huub Stapel
- noisy_or_distracting_clues: Sint, The Johnsons, Down (film), Flodders in America
- expected_evidence_type: Short authoritative statements/page snippets that explicitly identify Amsterdam as the capital of the Netherlands and Amsterdamned as a Dutch (1988) film (e.g., encyclopedia or film pages, Dutch cinema summaries).
- query_shape_implication: Conjunctive, fact-confirmation queries: either (A) pages explicitly linking both subjects to 'Dutch' (e.g., 'Amsterdamned Dutch film', 'Amsterdam Dutch capital'), or (B) background pages on 'Culture of the Netherlands' or 'Dutch cinema' to show shared cultural origin.

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

---

### 77__split0__seg0__right

- idx: 77
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: A
- correct: 0.0
- dominant_gap_type: anchor
- confidence: 0.63
- why_larger: Segment A shows a bigger retrieval shift: its from_state is a generated midpoint with no retrieved titles and an explicit shift in focus from the show-winner context to the bakery entity, requiring addition of Carlo's Bake Shop / Buddy Valastro pages to resolve ownership. Segment B already starts with an owner-confirmation focus and several retrieved titles, so its transition to the same target is a smaller refinement.

**Question**

The winner of the first season of "Next Great Baker" would win an apprenticeship at the bakery owned by who?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Next Great Baker season 1 winner Carlo's Bake Shop
- retrieved_titles: Next Great Baker (season 2), Next Great Baker (season 1), Next Great Baker (season 3), Next Great Baker, The Great Australian Bake Off (season 1), The Great Australian Bake Off (season 2), Next Great Baker (season 4)
- retrieval_focus: Confirm the owner of Carlo's Bake Shop (the bakery tied to the Season 1 apprenticeship prize).
- anchors: Carlo's Bake Shop, Buddy Valastro, Next Great Baker (season 1)
- bridge_clues: Who owns Carlo's Bake Shop, Buddy Valastro owner Carlo's Bake Shop, Carlo's Bake Shop Hoboken owner, Buddy Valastro biography owner
- noisy_or_distracting_clues: Next Great Baker (season 2), Next Great Baker (season 3), Next Great Baker (season 4), The Great Australian Bake Off (season 1), The Great Australian Bake Off (season 2)
- expected_evidence_type: Short authoritative entity statements (official bakery site, Buddy Valastro bio, Wikipedia or reputable news source) naming the owner.
- query_shape_implication: Simple entity-ownership lookup expecting a single person-name answer; use exact-phrase ownership queries (e.g., "owner of Carlo's Bake Shop") to return biographical or business pages.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Next Great Baker (season 1), Next Great Baker, Carlo's Bake Shop, Next Great Baker: Latin America, List of Next Great Baker episodes, Next Great Baker (season 2), List of Cake Boss episodes
- retrieval_focus: Resolve ownership of Carlo's Bake Shop (the apprenticeship prize location named on Season 1) — identify the person who owns the bakery.
- anchors: Carlo's Bake Shop, Buddy Valastro, Next Great Baker (season 1)
- bridge_clues: owner of Carlo's Bake Shop, Carlo's Bake Shop owned by, Buddy Valastro owner Carlo's Bake Shop, Who owns Carlo's Bake Shop?, Next Great Baker apprenticeship Carlo's Bake Shop owner
- noisy_or_distracting_clues: Next Great Baker: Latin America, Next Great Baker (season 2), List of Next Great Baker episodes, List of Cake Boss episodes, Next Great Baker (general) — season overview pages
- expected_evidence_type: Short factual statement or infobox line on a bakery or biography page stating ownership (e.g., Carlo's Bake Shop page or Buddy Valastro biography noting he owns the bakery).
- query_shape_implication: Second-hop entity lookup: starting from the bakery entity (Carlo's Bake Shop) retrieve a PERSON entity as owner. Queries should be short entity-to-owner patterns ('X owner', 'owned by X') aiming for a proper name answer.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Shift from show-winner context to the bakery entity: retrieve the Carlo's Bake Shop page or Buddy Valastro biography that explicitly states who owns the bakery.
- anchors: Carlo's Bake Shop, Buddy Valastro, Next Great Baker (season 1)
- bridge_clues: Carlo's Bake Shop official site 'About' owner, Carlo's Bake Shop Wikipedia infobox owner, Buddy Valastro biography Carlo's Bake Shop owner, Carlo's Bake Shop Hoboken owner information
- noisy_or_distracting_clues: Next Great Baker (other seasons), Next Great Baker episode lists, Cake Boss episode guides, Prize details (e.g., $50,000, Chevrolet Cruze) instead of ownership
- expected_evidence_type: Direct entity-page statements (lead sentence or infobox) on the bakery's page or the owner's biography naming the proprietor, or an 'About' page on the bakery website indicating ownership.
- query_shape_implication: Entity-centered queries targeting the bakery or the person (e.g., 'Carlo's Bake Shop owner', 'Buddy Valastro biography') to return a short factual line or infobox entry linking the bakery to a PERSON name.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Next Great Baker (season 1), Next Great Baker, Carlo's Bake Shop, Next Great Baker: Latin America, List of Next Great Baker episodes, Next Great Baker (season 2), List of Cake Boss episodes
- retrieval_focus: Resolve ownership of Carlo's Bake Shop (the apprenticeship prize location named on Season 1) — identify the person who owns the bakery.
- anchors: Carlo's Bake Shop, Buddy Valastro, Next Great Baker (season 1)
- bridge_clues: owner of Carlo's Bake Shop, Carlo's Bake Shop owned by, Buddy Valastro owner Carlo's Bake Shop, Who owns Carlo's Bake Shop?, Next Great Baker apprenticeship Carlo's Bake Shop owner
- noisy_or_distracting_clues: Next Great Baker: Latin America, Next Great Baker (season 2), List of Next Great Baker episodes, List of Cake Boss episodes, Next Great Baker (general) — season overview pages
- expected_evidence_type: Short factual statement or infobox line on a bakery or biography page stating ownership (e.g., Carlo's Bake Shop page or Buddy Valastro biography noting he owns the bakery).
- query_shape_implication: Second-hop entity lookup: starting from the bakery entity (Carlo's Bake Shop) retrieve a PERSON entity as owner. Queries should be short entity-to-owner patterns ('X owner', 'owned by X') aiming for a proper name answer.

---

## tie_or_invalid_fail (0 total, showing 0)

## pass (16 total, showing 12)

### 132__split0__seg0__right

- idx: 132
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why_larger: Segment B shows a bigger narrowing and correction: it moves from a broad, multi-term biography/discography query (including birthdate, filmography, Vespertine noise) to a tightly focused target that explicitly confirms soundtrack credit and occupations. Segment A is already mid-granularity and only makes a small refinement to entity/album-centric queries.

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
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow from a broad Björk biography to authoritative soundtrack/album credit sources: find the Selmasongs (Dancer in the Dark soundtrack) album page, soundtrack credits or music-database entries that explicitly credit the soundtrack to Björk and also identify her occupations/nationality.
- anchors: Selmasongs, Dancer in the Dark (soundtrack), Björk, soundtrack credits, album liner notes
- bridge_clues: Selmasongs credits, soundtrack artist credited, performed by Björk, music from the motion picture Selmasongs, soundtrack liner notes / credits list
- noisy_or_distracting_clues: Vespertine, Vespertine World Tour, Björk (book), tríó Guðmundar Ingólfssonar, general discography lists, birthdate-focused biography searches
- expected_evidence_type: Album/soundtrack page, liner notes, or reputable music database article that names the soundtrack artist (Selmasongs) and includes a short artist descriptor (e.g., Icelandic singer/songwriter/actress/producer/DJ) tying Björk to the soundtrack.
- query_shape_implication: Use mid-granularity, album- and credit-oriented queries (film+soundtrack+credits or album-title+credits) rather than full biography dumps or single-term entity jumps; target pages with explicit 'credited to' language.

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

---

### 140__split0__seg0__left

- idx: 140
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: answer_type
- confidence: 0.85
- why_larger: Segment B moves beyond mere verification of whether George Danzer is a WPT champion (segment A) to a full answer-oriented retrieval: it must both confirm the correct WPT champion who has four WSOP bracelets and extract the person's birth date. This is a larger shift in retrieval focus and expected evidence (from checking a winners list to acquiring biographical/date information and tying together bracelet count and WPT title).

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
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Verify whether the candidate George Danzer is a World Poker Tour (WPT) champion (i.e., appears on a WPT winners/champions list or tournament-results page). If he is not, identify any WPT champion who has four World Series of Poker bracelets.
- anchors: George Danzer, List of World Poker Tour champions, World Poker Tour winner, four World Series of Poker bracelets, WPT winners list, tournament results page
- bridge_clues: Search for 'George Danzer World Poker Tour' or 'George Danzer WPT' to find any explicit link between Danzer and a WPT title, Look up 'List of World Poker Tour champions' for the presence/absence of George Danzer, If Danzer is absent, search the WPT champions list for players with 'four WSOP bracelets' to find the correct cross-over candidate
- noisy_or_distracting_clues: Pages that discuss George Danzer's WSOP bracelets and achievements but do not mention WPT results (may falsely suggest a WPT link), Other player names on WPT lists (David Chiu, John Hennigan, Alexandre Gomes, etc.) that have different bracelet counts, Articles conflating WPT event wins with WSOP bracelets or using imprecise phrasing ('World Poker Tour bracelet'), Local event reports or forums that mention wins but are not authoritative
- expected_evidence_type: A WPT champions/winners list or official tournament-results page naming the winner(s) (positive evidence that Danzer did or did not win a WPT event), or an authoritative biography that explicitly states WPT titles (or their absence).
- query_shape_implication: Single-hop verification query: 'George Danzer WPT' or 'George Danzer "World Poker Tour"'; if negative, follow-up single-hop: 'List of World Poker Tour champions + "four World Series of Poker bracelets"' to find a different matching champion.

---

### 149__split0__seg0__right

- idx: 149
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.8
- why_larger: Segment B starts from a broader R0 baseline with noisy/distraction hits (Spillaholle, Gussy Holl, 872 Holda, etc.) and an explicit multi-term query, then moves to a focused Rstar_target removing those noisy results and concentrating on authoritative Hulder/Huld/Holda pages. Segment A was already a narrowly targeted midpoint (explicitly aiming at etymology and identity claims) and its transition to the same target is minimal. Thus B requires the larger retrieval-correction (removing noisy hits and refocusing).

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
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Narrow search to authoritative etymology and comparative-mythology statements that explicitly link the Swedish hulder/skogsrå name to Huld and show Huld's identification with Holda/Frau Holle; prioritize encyclopedia/folklore/etymology entries that give short identity claims rather than broader cultural history.
- anchors: Hulder, Huld, Holda, Skogsrå, Völva, Frau Holle
- bridge_clues: etymology: huldr / huld = 'hidden/covered' as name-root connection, explicit sentence: 'the hulder is originally the same being as Huld', scholarly/encyclopedic note equating Huld with Holda/Frau Holle, regional name citations (Tallemaja, ulda) used in etymology or name-history sections
- noisy_or_distracting_clues: Coat of arms of Lardal, 872 Holda, Haugtussa, Spillaholle, Gussy Holl
- expected_evidence_type: Short definitional or etymological passages in encyclopedia/folklore/dictionary entries or comparative-mythology summaries that state name-derivation and identity (e.g., a line that directly links hulder → Huld and Huld ↔ Holda/Frau Holle).
- query_shape_implication: Concise high-precision pairwise queries combining the folkloric term and candidate divine names with relationship keywords (examples to guide retrieval: 'hulder Huld etymology', 'hulder same as Holda', 'Huld völva Holda identity'), focusing on authoritative sources.

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

---

### 150__split0__seg0__left

- idx: 150
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.86
- why_larger: Segment B moves from a general identification goal to a concrete endpoint: it adds an explicit coach page (Paul Winters (American football)), reorders retrieved titles toward final targets, and sharpens the retrieval focus to produce short authoritative affiliation lines. This is a larger, more decisive correction than A, which stays at a midpoint confirmation step with similar anchors and noise.

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

---

### 150__split0__seg0__right

- idx: 150
- split_iter: 0
- task_kind: right_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.72
- why_larger: Segment A makes a targeted anchor correction and focus refinement: the transition adds the explicit Paul Winters coach page (a direct anchor needed to link coach + team to the university) and tightens the retrieval focus/query shape by removing a verbose, noisy query. This directly increases answerability more than the more mechanical population of results in B.

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

---

### 180__split0__seg0__left

- idx: 180
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: answer_type
- confidence: 0.82
- why_larger: A advances the retrieval goal from confirming the likely band to a full endpoint: it not only anchors the entity (Annihilator) but also adds retrieving the 11th-album page and the album's official release date (a date-type answer). B only narrows the task to identifying the 11th album title (ordinal) and explicitly defers the release-date lookup, so A represents a larger change in retrieval focus and evidence-type requirements.

**Question**

What is the date of released for the eleventh studio album of the highest-selling heavy metal group from Canada?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Annihilator discography "11th studio album" release date OR "Annihilator" "11th album" release date AND "highest-selling Canadian heavy metal" confirmation
- retrieved_titles: Annihilator discography, Set the World on Fire (Annihilator album), Metal (Annihilator album), All for You (Annihilator album), Annihilator (album), Annihilator (band), The One (EP)
- retrieval_focus: Confirm that the 'highest-selling Canadian heavy metal group' refers to Annihilator, then find the name and the official release date of that band's 11th studio album.
- anchors: Annihilator, Annihilator discography, 11th studio album, Annihilator 11th album release date
- bridge_clues: summary_1 flags Annihilator as the likely target for 'highest-selling Canadian heavy metal group', 'Annihilator discography' page in retrieved_titles should list album order and links to individual album pages, Retrieved individual album pages (e.g., 'Set the World on Fire', 'Metal', 'All for You', 'Annihilator (album)') may contain release dates to verify
- noisy_or_distracting_clues: Thor mention in summary_1 — unrelated to the highest-selling Canadian heavy metal group, Multiple album titles retrieved that may not be the 11th (noise from similarly named or earlier/later albums), 'The One (EP)' — not a studio album and thus a distractor, Complex boolean operators in the visible query may reduce recall or omit simpler phrasing
- expected_evidence_type: Authoritative discography entry or official band/label page, or reputable music-database article (e.g., Wikipedia/AllMusic/Discogs) that explicitly shows the album sequence (identifies the 11th studio album) and provides the album's release date (day/month/year or month/year).
- query_shape_implication: Perform a two-step, focused search: first confirm artist identity (Annihilator = highest-selling Canadian heavy metal group), then query 'Annihilator 11th studio album' or 'Annihilator "11th" album release date' or open the discography page and the specific album page to extract the release date. Avoid generic/over-broad queries and exclude EPs and non-studio releases.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Annihilator (band), Annihilator discography, Set the World on Fire (Annihilator album), All for You (Annihilator album), Metal (Annihilator album), Schizo Deluxe, Refresh the Demon
- retrieval_focus: Identify the band referenced (likely Annihilator), find which studio album is their 11th, and retrieve that album's official release date.
- anchors: Annihilator (band), Annihilator discography, retrieved album titles (Set the World on Fire, All for You, Metal, Schizo Deluxe, Refresh the Demon)
- bridge_clues: Confirm that 'highest-selling heavy metal group from Canada' refers to Annihilator via a summary or band page, Use the discography page to determine the ordered list of studio albums and pick the 11th entry, Open the 11th-album page (or the discography entry) to read the official release date
- noisy_or_distracting_clues: Multiple album titles present that are not labeled by ordinal — risk of miscounting which is 11th, Summary mentions Thor (unrelated) and other passages with no clear link to this query, creating irrelevant context
- expected_evidence_type: Discography listing or band page that enumerates studio albums in order, and the specific album page or discography entry that gives the album's official release date (day/month/year and region/label if available).
- query_shape_implication: First query should target the band discography (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') to get album order; second query should target the identified album name plus 'release date' (e.g., '<Album Name> release date' or 'Annihilator 11th studio album release date').

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Annihilator discography "11th studio album" release date OR "Annihilator" "11th album" release date AND "highest-selling Canadian heavy metal" confirmation
- retrieved_titles: Annihilator discography, Set the World on Fire (Annihilator album), Metal (Annihilator album), All for You (Annihilator album), Annihilator (album), Annihilator (band), The One (EP)
- retrieval_focus: Confirm that the 'highest-selling Canadian heavy metal group' refers to Annihilator, then find the name and the official release date of that band's 11th studio album.
- anchors: Annihilator, Annihilator discography, 11th studio album, Annihilator 11th album release date
- bridge_clues: summary_1 flags Annihilator as the likely target for 'highest-selling Canadian heavy metal group', 'Annihilator discography' page in retrieved_titles should list album order and links to individual album pages, Retrieved individual album pages (e.g., 'Set the World on Fire', 'Metal', 'All for You', 'Annihilator (album)') may contain release dates to verify
- noisy_or_distracting_clues: Thor mention in summary_1 — unrelated to the highest-selling Canadian heavy metal group, Multiple album titles retrieved that may not be the 11th (noise from similarly named or earlier/later albums), 'The One (EP)' — not a studio album and thus a distractor, Complex boolean operators in the visible query may reduce recall or omit simpler phrasing
- expected_evidence_type: Authoritative discography entry or official band/label page, or reputable music-database article (e.g., Wikipedia/AllMusic/Discogs) that explicitly shows the album sequence (identifies the 11th studio album) and provides the album's release date (day/month/year or month/year).
- query_shape_implication: Perform a two-step, focused search: first confirm artist identity (Annihilator = highest-selling Canadian heavy metal group), then query 'Annihilator 11th studio album' or 'Annihilator "11th" album release date' or open the discography page and the specific album page to extract the release date. Avoid generic/over-broad queries and exclude EPs and non-studio releases.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Confirm which studio album is Annihilator's 11th (identify the album title and verify its ordinal position in the band's official discography). Do not yet retrieve the album's release date.
- anchors: Annihilator discography (ordered list of studio albums), studio albums only (exclude EPs/compilations/live albums), ordinal position: 11th, album title corresponding to 11th entry
- bridge_clues: The band's discography page or a reputable music database will list studio albums in chronological order and allow unambiguous counting to the 11th entry., Some album pages include a lead sentence like 'X is the nth studio album by Annihilator' — that directly confirms ordinal without counting., Cross-checking two authoritative sources (e.g., band/Wikipedia/discography database) reduces risk of miscounting due to non-studio releases being mixed in.
- noisy_or_distracting_clues: EPs, compilations, live albums and reissues that are often shown alongside studio albums and can lead to miscounting., Self-titled album names or similarly named releases (e.g., 'Annihilator') that might be confused with other entries., Regional/label variations and deluxe editions that change listed release years but do not change album ordinal., References to other Canadian metal acts (e.g., Thor) in the supplied context — irrelevant to identifying Annihilator's 11th studio album.
- expected_evidence_type: An authoritative discography or band page that either labels the album as the band's '11th studio album' or provides a clear chronological list of studio albums from which the 11th entry (album title) can be unambiguously determined.
- query_shape_implication: Focus the next retrieval on the discography or album-listing page (e.g., 'Annihilator discography' or 'Annihilator list of studio albums') and either open the album page that explicitly states 'X is the 11th studio album' or count studio entries on the discography to extract the 11th album title. Defer querying for the release date until after the 11th album title is confirmed.

---

### 267__split0__seg0__right

- idx: 267
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why_larger: Segment B shows a larger retrieval-focus shift: it moves from a long, name- and episode-heavy query that surfaces many individual person/episode pages (noisy entities) to a concise, show-focused target that should surface authoritative series-level creator/writer pages. Segment A is already a mid-step that has mostly refocused onto show-level anchors (Alfred Gough, Miles Millar, Smallville), so its remaining change to the same target is smaller.

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
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Miles Millar, Aquaman (TV pilot), Tempest (Smallville), Smallville, Pilot (Smallville), Characters of Smallville, Chloe Sullivan
- retrieval_focus: Locate authoritative pages that list the primary writers/creators and full writing credits for the TV series Smallville (series article, episode list, or creator bios).
- anchors: Smallville, Justin Hartley, Alfred Gough, Miles Millar
- bridge_clues: creators, writers, writing credits, List of Smallville episodes, Smallville (TV series)
- noisy_or_distracting_clues: Aquaman (TV pilot), Tempest (Smallville), Pilot (Smallville), Characters of Smallville, Chloe Sullivan, Justin Hartley (actor roles)
- expected_evidence_type: Series-level or episode-list pages that explicitly name the show's creators/writers (e.g., Alfred Gough and Miles Millar) or dedicated creator biography pages.
- query_shape_implication: Use concise show-focused queries with writing keywords (e.g., 'Smallville writers', 'Smallville creators', 'Smallville writing credits', or 'Alfred Gough Miles Millar Smallville') to surface pages listing writers; avoid actor-centric queries that return cast-focused pages.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Shift from a long, name-heavy retrieval that returns many person and episode pages toward concise, show-level sources that explicitly name the series creators/writers: prioritize the Smallville main article, the 'List of Smallville episodes' (writing credits section), and bios of the two primary creators (Alfred Gough and Miles Millar). This reduces noise while keeping the retrieval anchored on the core creators rather than enumerating the entire writing staff.
- anchors: Smallville, creators, writers, Alfred Gough, Miles Millar, List of Smallville episodes
- bridge_clues: Justin Hartley, Fox Crane, Passions, Oliver Queen, American TV series based on Superman, created by / developed by, series-level writing credits
- noisy_or_distracting_clues: Individual episode pages (Pilot, Tempest, Finale, specific episode credits), Individual staff/person pages for many writers (Kelly Souders, Brian Peterson, Todd Slavkin, Darren Swimmer, etc.), Character pages (Chloe Sullivan, other cast-centric pages), Unrelated pilot pages or other DC projects (Aquaman pilot) that surface because of shared names
- expected_evidence_type: Authoritative series-level statements (Smallville main article or official credits) that explicitly identify the creators/writers (e.g., 'created by Alfred Gough and Miles Millar') and, as secondary confirmation, the episode list showing writer credits or creator biographies that state their role on the show.
- query_shape_implication: Move from long multi-name queries to concise show-focused retrieval gestures: emphasize the show plus 'creators'/'writers' and the two primary creator names as anchor terms. This shape avoids retrieving many separate person or episode pages and surfaces pages that consolidate writing credits.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Miles Millar, Aquaman (TV pilot), Tempest (Smallville), Smallville, Pilot (Smallville), Characters of Smallville, Chloe Sullivan
- retrieval_focus: Locate authoritative pages that list the primary writers/creators and full writing credits for the TV series Smallville (series article, episode list, or creator bios).
- anchors: Smallville, Justin Hartley, Alfred Gough, Miles Millar
- bridge_clues: creators, writers, writing credits, List of Smallville episodes, Smallville (TV series)
- noisy_or_distracting_clues: Aquaman (TV pilot), Tempest (Smallville), Pilot (Smallville), Characters of Smallville, Chloe Sullivan, Justin Hartley (actor roles)
- expected_evidence_type: Series-level or episode-list pages that explicitly name the show's creators/writers (e.g., Alfred Gough and Miles Millar) or dedicated creator biography pages.
- query_shape_implication: Use concise show-focused queries with writing keywords (e.g., 'Smallville writers', 'Smallville creators', 'Smallville writing credits', or 'Alfred Gough Miles Millar Smallville') to surface pages listing writers; avoid actor-centric queries that return cast-focused pages.

---

### 268__split0__seg0__left

- idx: 268
- split_iter: 0
- task_kind: left_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.78
- why_larger: Segment B moves from an ambiguous, noisy multi-target start to a concrete retrieval state (explicit retrieved titles including 'Henry Green', 'Henry Yorke', and 'Party Going') and a focused retrieval goal to get occupations for both Henry Green and G. K. Chesterton. This corrects the missing-entity anchor and disambiguation in one step, whereas A mainly refines the query plan without producing the resolved entity hits.

**Question**

Between G. K. Chesterton and Henry Green, who had more diverse job experiences?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Henry Green novelist Henry Vincent Yorke biography occupations OR "Henry Green (novelist)" occupations biography; "G. K. Chesterton" biography occupations journalist novelist poet critic lay theologian
- retrieved_titles: Henry Green (disambiguation), Henry James (biographer), Henry F. Pringle, Nick Tosches, J. M. Aimot, Henry Payne (engineer), Philip Norman (author)
- retrieval_focus: Find a biographic / career summary for Henry Green (the novelist Henry Vincent Yorke) and a full list of G. K. Chesterton's occupations so the two can be compared; also disambiguate Joseph Henry Chesterton (plant collector) to avoid confusion.
- anchors: G. K. Chesterton — author of Orthodoxy (writer, Christian apologist) (present in passages), Joseph Henry Chesterton — 19th-century plant collector (present in passages), Henry Green — missing (should be Henry Vincent Yorke, novelist)
- bridge_clues: Henry Green occupations, Henry Vincent Yorke biography occupations, "Henry Green (novelist)" occupations, G. K. Chesterton biography occupations, Joseph Henry Chesterton plant collector (to confirm identity and avoid conflation)
- noisy_or_distracting_clues: Retrieved titles are largely unrelated (Henry James, Nick Tosches, Henry F. Pringle, etc.), Henry Green (disambiguation) may return many persons and add ambiguity, Presence of Joseph Henry Chesterton in passages risks name confusion with 'Henry' in query
- expected_evidence_type: Short encyclopedic/biography lead paragraphs or career sections listing occupations and notable roles (e.g., novelist, journalist, editor, poet, critic, theologian) and dates to assess diversity of jobs.
- query_shape_implication: Current multi-target query is ambiguous and returns noisy hits — perform two focused, disambiguated queries: one exact-match for "Henry Vincent Yorke" or "Henry Green (novelist)" + 'occupations/biography', and one for "G. K. Chesterton" + 'occupations/biography'. Also include a disambiguation check for Joseph Henry Chesterton to avoid conflation.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Henry Green (disambiguation), Henry Green, Party Going, Henry James (biographer), Henry Yorke, Henry F. Pringle, Bill Henry (New York Yankees pitcher)
- retrieval_focus: Locate biographical/occupation information for Henry Green (pen name of Henry Yorke) and a full occupations list for G. K. Chesterton; disambiguate Joseph Henry Chesterton (plant collector) to avoid conflation.
- anchors: Henry Green (disambiguation), Henry Green, Henry Yorke, Party Going, G. K. Chesterton, Joseph Henry Chesterton
- bridge_clues: Henry Green occupations, Henry Yorke biography occupations, Henry Green Party Going author Henry Yorke, G. K. Chesterton occupations biography, Joseph Henry Chesterton plant collector (to confirm different person)
- noisy_or_distracting_clues: Henry James (biographer), Henry F. Pringle, Bill Henry (New York Yankees pitcher)
- expected_evidence_type: Lead/infobox or biography sections that list occupations (e.g., novelist, journalist, civil servant, author, apologist, plant collector) and career summaries for Henry Green/Henry Yorke and G. K. Chesterton.
- query_shape_implication: Use short entity-centric queries ('<Name> biography' / '<Name> occupations' / '<Name> infobox') and disambiguation queries ('Henry Green vs Henry Yorke', 'Joseph Henry Chesterton') to retrieve pages that explicitly list roles to support a diversity-of-jobs comparison.

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Henry Green novelist Henry Vincent Yorke biography occupations OR "Henry Green (novelist)" occupations biography; "G. K. Chesterton" biography occupations journalist novelist poet critic lay theologian
- retrieved_titles: Henry Green (disambiguation), Henry James (biographer), Henry F. Pringle, Nick Tosches, J. M. Aimot, Henry Payne (engineer), Philip Norman (author)
- retrieval_focus: Find a biographic / career summary for Henry Green (the novelist Henry Vincent Yorke) and a full list of G. K. Chesterton's occupations so the two can be compared; also disambiguate Joseph Henry Chesterton (plant collector) to avoid confusion.
- anchors: G. K. Chesterton — author of Orthodoxy (writer, Christian apologist) (present in passages), Joseph Henry Chesterton — 19th-century plant collector (present in passages), Henry Green — missing (should be Henry Vincent Yorke, novelist)
- bridge_clues: Henry Green occupations, Henry Vincent Yorke biography occupations, "Henry Green (novelist)" occupations, G. K. Chesterton biography occupations, Joseph Henry Chesterton plant collector (to confirm identity and avoid conflation)
- noisy_or_distracting_clues: Retrieved titles are largely unrelated (Henry James, Nick Tosches, Henry F. Pringle, etc.), Henry Green (disambiguation) may return many persons and add ambiguity, Presence of Joseph Henry Chesterton in passages risks name confusion with 'Henry' in query
- expected_evidence_type: Short encyclopedic/biography lead paragraphs or career sections listing occupations and notable roles (e.g., novelist, journalist, editor, poet, critic, theologian) and dates to assess diversity of jobs.
- query_shape_implication: Current multi-target query is ambiguous and returns noisy hits — perform two focused, disambiguated queries: one exact-match for "Henry Vincent Yorke" or "Henry Green (novelist)" + 'occupations/biography', and one for "G. K. Chesterton" + 'occupations/biography'. Also include a disambiguation check for Joseph Henry Chesterton to avoid conflation.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Resolve and retrieve clear biographical/occupation information for Henry Green (pen name of Henry Vincent Yorke) — verify identity, primary occupations, and notable roles — to remove ambiguity before fetching a full occupations list for G. K. Chesterton. Also include a short disambiguation check to avoid confusing Henry Green with other Henrys.
- anchors: Henry Green — pen name of Henry Vincent Yorke (missing from R_left passages), Need for occupation list (novelist, journalist, civil servant, etc.) to compare job diversity, Avoid conflation with other 'Henry' results and with Joseph Henry Chesterton
- bridge_clues: "Henry Vincent Yorke" biography occupations, "Henry Green (novelist)" infobox occupations, "Henry Green" Party Going author Henry Yorke biography, Henry Green pen name Henry Vincent Yorke career summary
- noisy_or_distracting_clues: Henry Green (disambiguation) pages listing many unrelated Henrys, Search results for other Henrys (Henry James, Henry F. Pringle, Bill Henry), Joseph Henry Chesterton (similar name) which could distract from Henry Green identity
- expected_evidence_type: Short encyclopedic lead/infobox or biography section that explicitly lists occupations and notable roles (e.g., novelist, journalist, civil servant, editor) with brief dates/notes to assess diversity of jobs.
- query_shape_implication: Use an exact-entity query shape: 'Henry Vincent Yorke biography' or 'Henry Green (novelist) occupations' and include the pen-name mapping ('Henry Green = Henry Vincent Yorke') to return a concise lead/infobox. Avoid broad multi-entity queries in this step.

---

### 268__split0__seg0__right

- idx: 268
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: query_shape
- confidence: 0.85
- why_larger: R0_base (B) starts with a broad, multi-target and noisy query and returns largely irrelevant titles; the to_state shifts to a focused, disambiguated, entity-centric retrieval plan for Henry Green and G. K. Chesterton. This is a larger correction (resolving query-shape ambiguity and noisy results) than A, which already embodies a focused midpoint plan and only refines retrieval targets.

**Question**

Between G. K. Chesterton and Henry Green, who had more diverse job experiences?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Henry Green novelist Henry Vincent Yorke biography occupations OR "Henry Green (novelist)" occupations biography; "G. K. Chesterton" biography occupations journalist novelist poet critic lay theologian
- retrieved_titles: Henry Green (disambiguation), Henry James (biographer), Henry F. Pringle, Nick Tosches, J. M. Aimot, Henry Payne (engineer), Philip Norman (author)
- retrieval_focus: Find a biographic / career summary for Henry Green (the novelist Henry Vincent Yorke) and a full list of G. K. Chesterton's occupations so the two can be compared; also disambiguate Joseph Henry Chesterton (plant collector) to avoid confusion.
- anchors: G. K. Chesterton — author of Orthodoxy (writer, Christian apologist) (present in passages), Joseph Henry Chesterton — 19th-century plant collector (present in passages), Henry Green — missing (should be Henry Vincent Yorke, novelist)
- bridge_clues: Henry Green occupations, Henry Vincent Yorke biography occupations, "Henry Green (novelist)" occupations, G. K. Chesterton biography occupations, Joseph Henry Chesterton plant collector (to confirm identity and avoid conflation)
- noisy_or_distracting_clues: Retrieved titles are largely unrelated (Henry James, Nick Tosches, Henry F. Pringle, etc.), Henry Green (disambiguation) may return many persons and add ambiguity, Presence of Joseph Henry Chesterton in passages risks name confusion with 'Henry' in query
- expected_evidence_type: Short encyclopedic/biography lead paragraphs or career sections listing occupations and notable roles (e.g., novelist, journalist, editor, poet, critic, theologian) and dates to assess diversity of jobs.
- query_shape_implication: Current multi-target query is ambiguous and returns noisy hits — perform two focused, disambiguated queries: one exact-match for "Henry Vincent Yorke" or "Henry Green (novelist)" + 'occupations/biography', and one for "G. K. Chesterton" + 'occupations/biography'. Also include a disambiguation check for Joseph Henry Chesterton to avoid conflation.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Henry Green (disambiguation), Henry Green, Party Going, Henry James (biographer), Henry Yorke, Henry F. Pringle, Bill Henry (New York Yankees pitcher)
- retrieval_focus: Locate biographical/occupation information for Henry Green (pen name of Henry Yorke) and a full occupations list for G. K. Chesterton; disambiguate Joseph Henry Chesterton (plant collector) to avoid conflation.
- anchors: Henry Green (disambiguation), Henry Green, Henry Yorke, Party Going, G. K. Chesterton, Joseph Henry Chesterton
- bridge_clues: Henry Green occupations, Henry Yorke biography occupations, Henry Green Party Going author Henry Yorke, G. K. Chesterton occupations biography, Joseph Henry Chesterton plant collector (to confirm different person)
- noisy_or_distracting_clues: Henry James (biographer), Henry F. Pringle, Bill Henry (New York Yankees pitcher)
- expected_evidence_type: Lead/infobox or biography sections that list occupations (e.g., novelist, journalist, civil servant, author, apologist, plant collector) and career summaries for Henry Green/Henry Yorke and G. K. Chesterton.
- query_shape_implication: Use short entity-centric queries ('<Name> biography' / '<Name> occupations' / '<Name> infobox') and disambiguation queries ('Henry Green vs Henry Yorke', 'Joseph Henry Chesterton') to retrieve pages that explicitly list roles to support a diversity-of-jobs comparison.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Resolve and retrieve clear biographical/occupation information for Henry Green (pen name of Henry Vincent Yorke) — verify identity, primary occupations, and notable roles — to remove ambiguity before fetching a full occupations list for G. K. Chesterton. Also include a short disambiguation check to avoid confusing Henry Green with other Henrys.
- anchors: Henry Green — pen name of Henry Vincent Yorke (missing from R_left passages), Need for occupation list (novelist, journalist, civil servant, etc.) to compare job diversity, Avoid conflation with other 'Henry' results and with Joseph Henry Chesterton
- bridge_clues: "Henry Vincent Yorke" biography occupations, "Henry Green (novelist)" infobox occupations, "Henry Green" Party Going author Henry Yorke biography, Henry Green pen name Henry Vincent Yorke career summary
- noisy_or_distracting_clues: Henry Green (disambiguation) pages listing many unrelated Henrys, Search results for other Henrys (Henry James, Henry F. Pringle, Bill Henry), Joseph Henry Chesterton (similar name) which could distract from Henry Green identity
- expected_evidence_type: Short encyclopedic lead/infobox or biography section that explicitly lists occupations and notable roles (e.g., novelist, journalist, civil servant, editor) with brief dates/notes to assess diversity of jobs.
- query_shape_implication: Use an exact-entity query shape: 'Henry Vincent Yorke biography' or 'Henry Green (novelist) occupations' and include the pen-name mapping ('Henry Green = Henry Vincent Yorke') to return a concise lead/infobox. Avoid broad multi-entity queries in this step.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Henry Green (disambiguation), Henry Green, Party Going, Henry James (biographer), Henry Yorke, Henry F. Pringle, Bill Henry (New York Yankees pitcher)
- retrieval_focus: Locate biographical/occupation information for Henry Green (pen name of Henry Yorke) and a full occupations list for G. K. Chesterton; disambiguate Joseph Henry Chesterton (plant collector) to avoid conflation.
- anchors: Henry Green (disambiguation), Henry Green, Henry Yorke, Party Going, G. K. Chesterton, Joseph Henry Chesterton
- bridge_clues: Henry Green occupations, Henry Yorke biography occupations, Henry Green Party Going author Henry Yorke, G. K. Chesterton occupations biography, Joseph Henry Chesterton plant collector (to confirm different person)
- noisy_or_distracting_clues: Henry James (biographer), Henry F. Pringle, Bill Henry (New York Yankees pitcher)
- expected_evidence_type: Lead/infobox or biography sections that list occupations (e.g., novelist, journalist, civil servant, author, apologist, plant collector) and career summaries for Henry Green/Henry Yorke and G. K. Chesterton.
- query_shape_implication: Use short entity-centric queries ('<Name> biography' / '<Name> occupations' / '<Name> infobox') and disambiguation queries ('Henry Green vs Henry Yorke', 'Joseph Henry Chesterton') to retrieve pages that explicitly list roles to support a diversity-of-jobs comparison.

---

### 6__split0__seg0__left

- idx: 6
- split_iter: 0
- task_kind: left_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: anchor
- confidence: 0.85
- why_larger: Segment A introduces the main target entity page ('Shenandoah River') into the retrieved set and shifts the retrieval focus from many noisy local pages to an authoritative river article that can explicitly list the states (resolving the missing West Virginia linkage). This is a bigger answerability/evidence-family and entity-anchor correction than B, which only narrows toward the North Fork and downstream landmarks but does not surface the main river page or explicit interstate evidence.

**Question**

Smith Creek is a 35.5 mi tributary stream of the North Fork of a river that passes through which US states?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Shenandoah River North Fork flows through which states Virginia West Virginia Harpers Ferry
- retrieved_titles: Little Dry River, Virginius Island, West Virginia, Harpers Ferry, West Virginia, German River, Middle River (Virginia), Baltimore and Ohio Railroad, Lynch River
- retrieval_focus: Locate an authoritative page for the Shenandoah River (or the North Fork Shenandoah River) that explicitly states which U.S. states the river passes through — confirm whether the river flows through Virginia and West Virginia (look for mentions of Harpers Ferry or the river's lower course).
- anchors: Shenandoah River, North Fork Shenandoah River, Smith Creek, Harpers Ferry, Virginia, West Virginia
- bridge_clues: passes through, flows through, states, lower course toward Harpers Ferry, confluence with Potomac, Shenandoah Valley
- noisy_or_distracting_clues: other local river/place pages (Little Dry River, Middle River, Lynch River), railroad or island pages (Baltimore and Ohio Railroad, Virginius Island), titles referring to local features that don't state overall river course
- expected_evidence_type: Encyclopedic/geographic article for 'Shenandoah River' or 'North Fork Shenandoah River' that describes the river's course and explicitly lists the U.S. states traversed (mentions Virginia and West Virginia or cites Harpers Ferry in West Virginia).
- query_shape_implication: Short, place-centered query: a single precise second-hop to the main Shenandoah River page (or North Fork page) should answer the question; must avoid being misled by many local tributary/place pages with similar geographic names.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Little Dry River, Shenandoah River, German River, Cootes Store, Virginia, North River (South Fork Shenandoah River), Cedar Creek (North Fork Shenandoah River), Smith Creek (Virginia)
- retrieval_focus: Locate an authoritative page that states which US states the Shenandoah River (including its North Fork) flows through to confirm whether it passes through Virginia and West Virginia.
- anchors: Smith Creek, North Fork of the Shenandoah River, Shenandoah River, Rockingham County, Virginia, Mount Jackson, Virginia
- bridge_clues: Smith Creek is a tributary of the North Fork of the Shenandoah River, The North Fork is part of the Shenandoah River system, Need a source that lists the states traversed by the Shenandoah River (to link Smith Creek's river to states)
- noisy_or_distracting_clues: Little Dry River, German River, Cootes Store, Virginia, North River (South Fork Shenandoah River), Cedar Creek (North Fork Shenandoah River)
- expected_evidence_type: Encyclopedic or geographic source (river article, infobox, or authoritative map/state resource) explicitly listing the states the Shenandoah River flows through (e.g., Virginia; West Virginia).
- query_shape_implication: Short, entity-focused queries using the river name plus 'states' or 'flows through' (examples: 'Shenandoah River states', 'Which states does the Shenandoah River flow through?', optionally add 'North Fork Shenandoah River').

**Sub segment**

from_state:
- name: R0_base
- kind: endpoint
- query: Shenandoah River North Fork flows through which states Virginia West Virginia Harpers Ferry
- retrieved_titles: Little Dry River, Virginius Island, West Virginia, Harpers Ferry, West Virginia, German River, Middle River (Virginia), Baltimore and Ohio Railroad, Lynch River
- retrieval_focus: Locate an authoritative page for the Shenandoah River (or the North Fork Shenandoah River) that explicitly states which U.S. states the river passes through — confirm whether the river flows through Virginia and West Virginia (look for mentions of Harpers Ferry or the river's lower course).
- anchors: Shenandoah River, North Fork Shenandoah River, Smith Creek, Harpers Ferry, Virginia, West Virginia
- bridge_clues: passes through, flows through, states, lower course toward Harpers Ferry, confluence with Potomac, Shenandoah Valley
- noisy_or_distracting_clues: other local river/place pages (Little Dry River, Middle River, Lynch River), railroad or island pages (Baltimore and Ohio Railroad, Virginius Island), titles referring to local features that don't state overall river course
- expected_evidence_type: Encyclopedic/geographic article for 'Shenandoah River' or 'North Fork Shenandoah River' that describes the river's course and explicitly lists the U.S. states traversed (mentions Virginia and West Virginia or cites Harpers Ferry in West Virginia).
- query_shape_implication: Short, place-centered query: a single precise second-hop to the main Shenandoah River page (or North Fork page) should answer the question; must avoid being misled by many local tributary/place pages with similar geographic names.

to_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Target the North Fork Shenandoah River (the immediate parent watercourse of Smith Creek) or a page that connects the North Fork to the main Shenandoah River and mentions downstream landmarks (Harpers Ferry, confluence with the Potomac) that indicate the river crosses state lines.
- anchors: North Fork Shenandoah River, Shenandoah River, Smith Creek, Harpers Ferry, Potomac River, Virginia, West Virginia
- bridge_clues: North Fork is part of the Shenandoah River system, confluence near Harpers Ferry, flows into the Potomac, mentions downstream course or lower reaches, references the river crossing a state boundary
- noisy_or_distracting_clues: local tributary pages (Little Dry River, Cedar Creek, North River), county- or town-level pages (Mount Jackson, Rockingham County), pages about railroads or islands (Baltimore and Ohio Railroad, Virginius Island) that mention Harpers Ferry but not river states
- expected_evidence_type: An encyclopedic/geographic article focused on the North Fork Shenandoah River or on the Shenandoah River that explicitly connects the fork to the main river and/or names downstream locations (Harpers Ferry, Potomac) or lists the U.S. states traversed (Virginia; West Virginia).
- query_shape_implication: A fork-level, entity-specific query (e.g., 'North Fork Shenandoah River' + downstream landmark terms) that is narrower than a broad 'Shenandoah River states' query but still surfaces statements linking the fork to the main river and its interstate course.

---

### 6__split0__seg0__right

- idx: 6
- split_iter: 0
- task_kind: right_recovery
- expected: A
- predicted: A
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.85
- why_larger: Segment A moves from a noisy, local-focused retrieval state (many tributary/place pages) to actually retrieving the authoritative 'Shenandoah River' page and refocusing on the states the river passes through. This is a larger correction of retrieval focus and anchors (removing distracting local entities and picking up the main river entity) than Segment B, which is a narrower fork-to-main refinement with less noisy-entity correction.

**Question**

Smith Creek is a 35.5 mi tributary stream of the North Fork of a river that passes through which US states?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Shenandoah River North Fork flows through which states Virginia West Virginia Harpers Ferry
- retrieved_titles: Little Dry River, Virginius Island, West Virginia, Harpers Ferry, West Virginia, German River, Middle River (Virginia), Baltimore and Ohio Railroad, Lynch River
- retrieval_focus: Locate an authoritative page for the Shenandoah River (or the North Fork Shenandoah River) that explicitly states which U.S. states the river passes through — confirm whether the river flows through Virginia and West Virginia (look for mentions of Harpers Ferry or the river's lower course).
- anchors: Shenandoah River, North Fork Shenandoah River, Smith Creek, Harpers Ferry, Virginia, West Virginia
- bridge_clues: passes through, flows through, states, lower course toward Harpers Ferry, confluence with Potomac, Shenandoah Valley
- noisy_or_distracting_clues: other local river/place pages (Little Dry River, Middle River, Lynch River), railroad or island pages (Baltimore and Ohio Railroad, Virginius Island), titles referring to local features that don't state overall river course
- expected_evidence_type: Encyclopedic/geographic article for 'Shenandoah River' or 'North Fork Shenandoah River' that describes the river's course and explicitly lists the U.S. states traversed (mentions Virginia and West Virginia or cites Harpers Ferry in West Virginia).
- query_shape_implication: Short, place-centered query: a single precise second-hop to the main Shenandoah River page (or North Fork page) should answer the question; must avoid being misled by many local tributary/place pages with similar geographic names.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Little Dry River, Shenandoah River, German River, Cootes Store, Virginia, North River (South Fork Shenandoah River), Cedar Creek (North Fork Shenandoah River), Smith Creek (Virginia)
- retrieval_focus: Locate an authoritative page that states which US states the Shenandoah River (including its North Fork) flows through to confirm whether it passes through Virginia and West Virginia.
- anchors: Smith Creek, North Fork of the Shenandoah River, Shenandoah River, Rockingham County, Virginia, Mount Jackson, Virginia
- bridge_clues: Smith Creek is a tributary of the North Fork of the Shenandoah River, The North Fork is part of the Shenandoah River system, Need a source that lists the states traversed by the Shenandoah River (to link Smith Creek's river to states)
- noisy_or_distracting_clues: Little Dry River, German River, Cootes Store, Virginia, North River (South Fork Shenandoah River), Cedar Creek (North Fork Shenandoah River)
- expected_evidence_type: Encyclopedic or geographic source (river article, infobox, or authoritative map/state resource) explicitly listing the states the Shenandoah River flows through (e.g., Virginia; West Virginia).
- query_shape_implication: Short, entity-focused queries using the river name plus 'states' or 'flows through' (examples: 'Shenandoah River states', 'Which states does the Shenandoah River flow through?', optionally add 'North Fork Shenandoah River').

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Target the North Fork Shenandoah River (the immediate parent watercourse of Smith Creek) or a page that connects the North Fork to the main Shenandoah River and mentions downstream landmarks (Harpers Ferry, confluence with the Potomac) that indicate the river crosses state lines.
- anchors: North Fork Shenandoah River, Shenandoah River, Smith Creek, Harpers Ferry, Potomac River, Virginia, West Virginia
- bridge_clues: North Fork is part of the Shenandoah River system, confluence near Harpers Ferry, flows into the Potomac, mentions downstream course or lower reaches, references the river crossing a state boundary
- noisy_or_distracting_clues: local tributary pages (Little Dry River, Cedar Creek, North River), county- or town-level pages (Mount Jackson, Rockingham County), pages about railroads or islands (Baltimore and Ohio Railroad, Virginius Island) that mention Harpers Ferry but not river states
- expected_evidence_type: An encyclopedic/geographic article focused on the North Fork Shenandoah River or on the Shenandoah River that explicitly connects the fork to the main river and/or names downstream locations (Harpers Ferry, Potomac) or lists the U.S. states traversed (Virginia; West Virginia).
- query_shape_implication: A fork-level, entity-specific query (e.g., 'North Fork Shenandoah River' + downstream landmark terms) that is narrower than a broad 'Shenandoah River states' query but still surfaces statements linking the fork to the main river and its interstate course.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: Little Dry River, Shenandoah River, German River, Cootes Store, Virginia, North River (South Fork Shenandoah River), Cedar Creek (North Fork Shenandoah River), Smith Creek (Virginia)
- retrieval_focus: Locate an authoritative page that states which US states the Shenandoah River (including its North Fork) flows through to confirm whether it passes through Virginia and West Virginia.
- anchors: Smith Creek, North Fork of the Shenandoah River, Shenandoah River, Rockingham County, Virginia, Mount Jackson, Virginia
- bridge_clues: Smith Creek is a tributary of the North Fork of the Shenandoah River, The North Fork is part of the Shenandoah River system, Need a source that lists the states traversed by the Shenandoah River (to link Smith Creek's river to states)
- noisy_or_distracting_clues: Little Dry River, German River, Cootes Store, Virginia, North River (South Fork Shenandoah River), Cedar Creek (North Fork Shenandoah River)
- expected_evidence_type: Encyclopedic or geographic source (river article, infobox, or authoritative map/state resource) explicitly listing the states the Shenandoah River flows through (e.g., Virginia; West Virginia).
- query_shape_implication: Short, entity-focused queries using the river name plus 'states' or 'flows through' (examples: 'Shenandoah River states', 'Which states does the Shenandoah River flow through?', optionally add 'North Fork Shenandoah River').

---

### 60__split0__seg0__right

- idx: 60
- split_iter: 0
- task_kind: right_recovery
- expected: B
- predicted: B
- correct: 1.0
- dominant_gap_type: noisy_entity
- confidence: 0.85
- why_larger: Segment B corrects a visibly noisy/overbroad retrieval (many unrelated STS pages and noisy hits) into a focused target on the authoritative STS-31/Hubble launch page. That is a substantive change in retrieval focus and entity disambiguation. Segment A mostly rephrases a mission-focused intent to a very similar target and shows only a small refinement.

**Question**

The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

**Full segment: R_i -> R_next**

from_state:
- name: R0_base
- kind: endpoint
- query: Hubble Space Telescope STS-31 Space Shuttle Discovery launch date launch year
- retrieved_titles: STS-31, STS-82, STS-103, STS-124, STS-400, STS-51, Goddard High Resolution Spectrograph
- retrieval_focus: Locate an authoritative page (Hubble or STS-31/NASA mission page) that states the Hubble Space Telescope's launch into low Earth orbit and gives the launch year.
- anchors: Hubble Space Telescope, STS-31, Space Shuttle Discovery, launch date
- bridge_clues: launched into low Earth orbit, STS-31 mission (deployment of HST), launch year 1990, 24 April 1990 / deployed 25 April 1990
- noisy_or_distracting_clues: Other STS mission pages retrieved (STS-82, STS-103, STS-124, STS-400, STS-51) that are unrelated to HST's launch, Goddard High Resolution Spectrograph (instrument page)
- expected_evidence_type: A concise factual statement on the mission/launch date (year) from an authoritative source (Hubble overview, STS-31 or NASA mission page).
- query_shape_implication: Targeted, single-attribute lookup (entity → launch year). Expect a single best-match document (HST or STS-31) rather than multi-document synthesis; risk of false positives from similarly numbered STS pages.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: STS-31, Goddard High Resolution Spectrograph, STS-82, Hubble Space Telescope, List of Hubble anniversary images, STS-109, Space Shuttle
- retrieval_focus: Locate a reliable page that states the launch year of the Hubble Space Telescope (the year it was launched into low Earth orbit).
- anchors: Hubble Space Telescope, STS-31, Space Shuttle Discovery
- bridge_clues: launch date / launch year, launched into low Earth orbit, STS-31 mission details, deployment date of HST
- noisy_or_distracting_clues: Goddard High Resolution Spectrograph, STS-82, STS-109, List of Hubble anniversary images, ACS and NICMOS instruments (observation details)
- expected_evidence_type: HST main article or STS-31 mission page explicitly listing the launch/deployment date and year (e.g., '24 April 1990' or '1990').
- query_shape_implication: Short, factual queries combining the telescope or mission name with 'launch year' or 'launch date' — e.g. 'Hubble Space Telescope launch year', 'STS-31 launch year', or 'HST launched into low Earth orbit year'.

**Sub segment**

from_state:
- name: Rmid_iter1_split0
- kind: generated_midpoint
- retrieval_focus: Target a mission-specific authoritative source (STS-31 / NASA mission page or Space Shuttle Discovery page) that explicitly lists the Hubble Space Telescope's launch date and year.
- anchors: STS-31, Space Shuttle Discovery, Hubble Space Telescope, launch date / launch year
- bridge_clues: STS-31 deployed HST, launched 24 April 1990, deployment 25 April 1990, mission summary / launch year 1990
- noisy_or_distracting_clues: Other STS mission pages (e.g., STS-82, STS-109) that are not STS-31, Instrument pages (ACS, NICMOS, Goddard High Resolution Spectrograph), Hubble anniversary or image gallery pages that mention HST events but may not state launch date concisely
- expected_evidence_type: A concise mission-summary line on an official NASA / STS-31 page or HST overview that states the launch date and year (e.g., '24 April 1990' or '1990').
- query_shape_implication: Short mission-focused query combining 'STS-31' or 'Space Shuttle Discovery' with 'launch date' or 'launch year' to retrieve a single authoritative mission page rather than broader HST histories.

to_state:
- name: Rstar_target
- kind: endpoint
- retrieved_titles: STS-31, Goddard High Resolution Spectrograph, STS-82, Hubble Space Telescope, List of Hubble anniversary images, STS-109, Space Shuttle
- retrieval_focus: Locate a reliable page that states the launch year of the Hubble Space Telescope (the year it was launched into low Earth orbit).
- anchors: Hubble Space Telescope, STS-31, Space Shuttle Discovery
- bridge_clues: launch date / launch year, launched into low Earth orbit, STS-31 mission details, deployment date of HST
- noisy_or_distracting_clues: Goddard High Resolution Spectrograph, STS-82, STS-109, List of Hubble anniversary images, ACS and NICMOS instruments (observation details)
- expected_evidence_type: HST main article or STS-31 mission page explicitly listing the launch/deployment date and year (e.g., '24 April 1990' or '1990').
- query_shape_implication: Short, factual queries combining the telescope or mission name with 'launch year' or 'launch date' — e.g. 'Hubble Space Telescope launch year', 'STS-31 launch year', or 'HST launched into low Earth orbit year'.

---
