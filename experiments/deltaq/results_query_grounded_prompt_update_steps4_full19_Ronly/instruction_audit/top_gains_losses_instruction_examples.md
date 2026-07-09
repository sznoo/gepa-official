# Top gains and losses


## TOP GAINS

### IDX 6 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR +1.000
Q: Smith Creek is a 35.5 mi tributary stream of the North Fork of a river that passes through which US states?
Query: `Shenandoah River infobox states Harpers Ferry Potomac Virginia West Virginia`
Risky titles: 
Instruction excerpt:
```text
Given the fields question and summary_1, produce the field query optimized for the second hop. Generate one compact, entity-first BM25-style keyword query (single-line, minimal stopwords, no natural-language question phrasing) that retrieves an authoritative river-level article or fork-level lead/infobox that explicitly lists the U.S. states the river passes through. Instructions: - Use the summary to detect the missing link: connect Smith Creek → North Fork of the Shenandoah → Shenandoah ...
```

### IDX 55 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR +1.000
Q: What culture do both the Capital of the Netherlands and Amsterdamned have in common?
Query: `Amsterdam capital Netherlands Amsterdamned 1988 Dutch film`
Risky titles: 
Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop of a multi‑hop retrieval system. Your goal is one compact BM25-style query (single bag-of-words / short ordered token set) that retrieves authoritative metadata/lede/infobox lines to confirm whether two entities share the same national/cultural label. Follow these ordered rules (apply in sequence): 1) Primary film-metadata step (use when you need to verify the film’s nationality as an ...
```

### IDX 55 | prompt_update_twoturn_R_to_q_then_p_steps_4 | ΔMR +1.000
Q: What culture do both the Capital of the Netherlands and Amsterdamned have in common?
Query: `Amsterdam capital Netherlands Amsterdamned Dutch film`
Risky titles: 
Instruction excerpt:
```text
Given the fields question and summary_1, produce the field query optimized for the second hop of a multi-hop retrieval system. Generate one compact BM25-style query that retrieves short lede/infobox lines confirming the shared culture/national label between the two named entities in the summary. Preserve sample-specific anchors and the ordered local edit program: place the Amsterdam anchor first with an adjacent role/country token, then the Amsterdamned anchor with an adjacent ...
```

### IDX 60 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR +1.000
Q: The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?
Query: `Hubble Space Telescope launch year Wikipedia`
Risky titles: 
Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce a single compact BM25-style second-hop query (the `query` field) that retrieves the specific launch-year/date fact needed. Follow this ordered edit program exactly (apply steps in sequence; later steps override earlier ones when their triggers match): 1) Default — entity-first, authority-hinted (apply when the user asks for a telescope/spacecraft launch date or launch year): - Construct an entity-centric query that places the telescope ...
```

### IDX 108 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR +1.000
Q: Are Solo and La Croix Sparkling Water produced in the same country ?
Query: `Solo (Australian soft drink) country of origin`
Risky titles: 
Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce a single compact BM25-style `query` optimized for the second hop of a multi-hop retrieval system that will retrieve additional relevant documents not captured in the first hop. Your role is to generate one concise query (not an answer) that targets the missing entity or disambiguation needed to compare production/origin facts (e.g., to determine whether Solo and La Croix are produced in the same country). Preserve the target entity name ...
```

### IDX 108 | prompt_update_twoturn_R_to_q_then_p_steps_4 | ΔMR +1.000
Q: Are Solo and La Croix Sparkling Water produced in the same country ?
Query: `Solo (soft drink) Australian origin infobox`
Risky titles: 
Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce one compact BM25-style second-hop query optimized to retrieve a short lead/infobox statement about the production country for the missing entity. Follow the ordered edits below when constructing the query: 1) Anchor on the canonical, disambiguated product title (e.g., Solo or Solo (soft drink)) and a geographic sense token (Australian / Australian soft drink). 2) Remove manufacturer and global-brand tokens that cause company pages to ...
```

### IDX 267 | prompt_update_twoturn_R_to_q_then_p_steps_4 | ΔMR +1.000
Q: Who were the writers of an American television series based on the DC Comics character Superman, which starred an American actor known for his television roles that include Fox Crane on the NBC daytime soap opera "Passions"?
Query: `Smallville "created by" Alfred Gough Miles Millar Justin Hartley`
Risky titles: 
Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce the field `query` optimized for the second hop. Generate one compact BM25-style query (do not output a full answer). Follow these sample-specific constraints and the ordered edit program exactly: - Keep the show anchor first: use the series title "Smallville" (show title goes first). - Immediately follow the show title with a short quoted credit cue to force series-level authorship language, e.g., "created by" (or the single token: ...
```

### IDX 118 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR +0.500
Q: What acress starred in both "Third Person" and "From Here to Eternity"?
Query: `Third Person 2013 cast starring actress; From Here to Eternity 1979 cast starring actress`
Risky titles: 
Instruction excerpt:
```text
Given the fields question and summary_1, produce the field query optimized for the second-hop of a multi-hop retrieval: a single compact BM25 query string (one text field) that may contain two semicolon-separated subqueries targeting authoritative title cast pages. Follow this ordered, version-aware program exactly: 1) Disambiguate Third Person first (only if necessary): if the summary or initial retrieval is ambiguous about which "Third Person" is meant, run a quick disambiguation step ...
```


## WORST LOSSES

### IDX 82 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR -1.000
Q: What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?
Query: `Clay County Savings Association Building robbers Liberty Missouri 1866 former Confederate guerrillas bushwhackers
guerrilla definition Civil War Missouri`
Risky titles: 
Instruction excerpt:
```text
Given fields question, summary_1, and the current_query, produce a second‑hop BM25 query (or, when the summary requests confirmation of the exact one‑word label used for the perpetrators, emit two compact BM25 queries in strict sequence) optimized to retrieve short, authoritative lead/definition lines needed to close gaps from the first hop. Primary role (default): generate one compact, title‑anchored second‑hop BM25 query that refines the original retrieval to fetch additional relevant ...
```

### IDX 82 | prompt_update_twoturn_R_to_q_then_p_steps_4 | ΔMR -1.000
Q: What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?
Query: `Clay County Savings robbery" Liberty Missouri 1866 robbers "former Confederate guerrillas" bushwhackers partisans lead`
Risky titles: 
Instruction excerpt:
```text
Given the fields question and summary_1, produce a single compact second‑hop BM25 query (roughly 6–12 tokens) that prioritizes the robbery article lead and short definition/usage lines rather than long biographies. Follow this ordered shape: 1) event anchor first — "Clay County Savings Association Building robbery" (or "Clay County Savings Association robbery"); 2) place/state/date as short tokens (Liberty Missouri 1866) to prefer the local article; 3) an explicit label cue such as robbers ...
```

### IDX 90 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR -1.000
Q: Imiliya is a town located in what pilgrimage site?
Query: `Imiliya Kapilvastu Lumbini Mayadevi UNESCO`
Risky titles: 
Instruction excerpt:
```text
Given the fields question and summary_1, produce the single field query: one compact BM25-style query (a single line of concise, space‑separated tokens) optimized for the second hop. Goal: retrieve authoritative lines that (a) confirm Lumbini’s status as the Buddhist pilgrimage site/birthplace of Siddhartha Gautama and list its core landmarks, and (b) place Imiliya administratively in Kapilvastu or state its proximity to Lumbini landmarks. Instructions for constructing the query: - Emit ...
```

### IDX 132 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR -1.000
Q: The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?
Query: `Selmasongs soundtrack credits Björk wikipedia`
Risky titles: 
Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce one compact BM25-style query for the second hop that will surface authoritative album/release-level pages verifying who is credited for the soundtrack (and, only if needed, confirming listed occupations). Follow these steps in order: 1. Detect soundtrack/album anchors in the inputs (tokens like "Selmasongs", "Dancer in the Dark", "soundtrack", artist name e.g. "Björk"). If such anchors are present, switch to an album-credit query shape ...
```

### IDX 132 | prompt_update_twoturn_R_to_q_then_p_steps_4 | ΔMR -1.000
Q: The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?
Query: `Selmasongs" "Dancer in the Dark" soundtrack credits Björk site:wikipedia.org`
Risky titles: 
Instruction excerpt:
```text
Given the fields question and summary_1, produce a single compact BM25-style query optimized for the second hop that will retrieve an authoritative album/release page listing who is credited for the soundtrack (not a broad biography). Follow these ordered, sample-specific steps: 1. Preserve and use the work→soundtrack→artist ordering and concrete anchors from the sample: 'Selmasongs', 'Dancer in the Dark', 'Björk', 'soundtrack'. Prefer phrase-matching the album title when possible (e.g., put ...
```

### IDX 140 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR -1.000
Q: When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?
Query: `George Danzer" "World Poker Tour`
Risky titles: 
Instruction excerpt:
```text
Given the fields question and summary_1, produce a single, compact BM25 query optimized for the second hop that follows the ordered verification-and-extraction program below. Preserve the goal (confirm which World Poker Tour [WPT] champion matches the descriptor "has four World Series of Poker bracelets" and then extract that champion’s birth date) and prefer authoritative sources (wikipedia.org, worldpokertour.com, wsop.com, major news outlets). Follow these ordered steps and emit ONE ...
```

### IDX 140 | prompt_update_twoturn_R_to_q_then_p_steps_4 | ΔMR -1.000
Q: When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?
Query: `George Danzer "World Poker Tour" winner`
Risky titles: 
Instruction excerpt:
```text
Given the fields question and summary_1, produce one compact BM25 query optimized for the second hop that retrieves additional documents not captured in the first hop. Follow this ordered, sample-aware edit program (apply steps in order and pick the most appropriate shape): 1) If the summary names a candidate and you need to confirm that candidate’s association with the tournament brand, form a compact co‑occurrence query with the person’s full name first, then the exact tournament phrase. ...
```

### IDX 150 | prompt_update_onecall_R_to_q_to_p_steps_4 | ΔMR -1.000
Q: What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?
Query: `2012 Wayne State Warriors football team" OR "Paul Winters (American football)" Wayne State University`
Risky titles: Paul Winters (American football)
Instruction excerpt:
```text
Given question and summary_1, produce a single compact BM25 query optimized for the second hop that will surface the canonical season page and the coach bio and their short lead-sentence affiliation lines (to confirm the shared institution). Preserve these sample anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State University. Avoid stadium/venue names (Tom Adams Field), conference/division tokens (GLIAC, NCAA Division II), extra season years (2011, 2016, 2017, etc.), ...
```
