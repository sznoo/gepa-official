# Flagged updated-instruction examples


========================================================================================================================

## IDX 60 | prompt_update_onecall_R_to_q_to_p_steps_4
- MR: 0.000 → 1.000 (+1.000)
- risky_instr_title_hits: 
- suspicious: wikipedia
- query_title_hits: Hubble Space Telescope

Question: The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

Query: `Hubble Space Telescope launch year Wikipedia`

Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce a single compact BM25-style second-hop query (the `query` field) that retrieves the specific launch-year/date fact needed. Follow this ordered edit program exactly (apply steps in sequence; later steps override earlier ones when their triggers match): 1) Default — entity-first, authority-hinted (apply when the user asks for a telescope/spacecraft launch date or launch year): - Construct an entity-centric query that places the telescope ...
```

========================================================================================================================

## IDX 90 | prompt_update_onecall_R_to_q_to_p_steps_4
- MR: 1.000 → 0.000 (-1.000)
- risky_instr_title_hits: 
- suspicious: wikipedia
- query_title_hits: Imiliya; Lumbini

Question: Imiliya is a town located in what pilgrimage site?

Query: `Imiliya Kapilvastu Lumbini Mayadevi UNESCO`

Instruction excerpt:
```text
Given the fields question and summary_1, produce the single field query: one compact BM25-style query (a single line of concise, space‑separated tokens) optimized for the second hop. Goal: retrieve authoritative lines that (a) confirm Lumbini’s status as the Buddhist pilgrimage site/birthplace of Siddhartha Gautama and list its core landmarks, and (b) place Imiliya administratively in Kapilvastu or state its proximity to Lumbini landmarks. Instructions for constructing the query: - Emit ...
```

========================================================================================================================

## IDX 108 | prompt_update_onecall_R_to_q_to_p_steps_4
- MR: 0.000 → 1.000 (+1.000)
- risky_instr_title_hits: 
- suspicious: wikipedia
- query_title_hits: 

Question: Are Solo and La Croix Sparkling Water produced in the same country ?

Query: `Solo (Australian soft drink) country of origin`

Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce a single compact BM25-style `query` optimized for the second hop of a multi-hop retrieval system that will retrieve additional relevant documents not captured in the first hop. Your role is to generate one concise query (not an answer) that targets the missing entity or disambiguation needed to compare production/origin facts (e.g., to determine whether Solo and La Croix are produced in the same country). Preserve the target entity name ...
```

========================================================================================================================

## IDX 132 | prompt_update_onecall_R_to_q_to_p_steps_4
- MR: 1.000 → 0.000 (-1.000)
- risky_instr_title_hits: 
- suspicious: imdb; wikipedia
- query_title_hits: Selmasongs; Björk

Question: The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?

Query: `Selmasongs soundtrack credits Björk wikipedia`

Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce one compact BM25-style query for the second hop that will surface authoritative album/release-level pages verifying who is credited for the soundtrack (and, only if needed, confirming listed occupations). Follow these steps in order: 1. Detect soundtrack/album anchors in the inputs (tokens like "Selmasongs", "Dancer in the Dark", "soundtrack", artist name e.g. "Björk"). If such anchors are present, switch to an album-credit query shape ...
```

========================================================================================================================

## IDX 132 | prompt_update_twoturn_R_to_q_then_p_steps_4
- MR: 1.000 → 0.000 (-1.000)
- risky_instr_title_hits: 
- suspicious: site:; wikipedia
- query_title_hits: Selmasongs; Björk

Question: The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?

Query: `Selmasongs" "Dancer in the Dark" soundtrack credits Björk site:wikipedia.org`

Instruction excerpt:
```text
Given the fields question and summary_1, produce a single compact BM25-style query optimized for the second hop that will retrieve an authoritative album/release page listing who is credited for the soundtrack (not a broad biography). Follow these ordered, sample-specific steps: 1. Preserve and use the work→soundtrack→artist ordering and concrete anchors from the sample: 'Selmasongs', 'Dancer in the Dark', 'Björk', 'soundtrack'. Prefer phrase-matching the album title when possible (e.g., put ...
```

========================================================================================================================

## IDX 140 | prompt_update_onecall_R_to_q_to_p_steps_4
- MR: 1.000 → 0.000 (-1.000)
- risky_instr_title_hits: 
- suspicious: wikipedia
- query_title_hits: World Poker Tour

Question: When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

Query: `George Danzer" "World Poker Tour`

Instruction excerpt:
```text
Given the fields question and summary_1, produce a single, compact BM25 query optimized for the second hop that follows the ordered verification-and-extraction program below. Preserve the goal (confirm which World Poker Tour [WPT] champion matches the descriptor "has four World Series of Poker bracelets" and then extract that champion’s birth date) and prefer authoritative sources (wikipedia.org, worldpokertour.com, wsop.com, major news outlets). Follow these ordered steps and emit ONE ...
```

========================================================================================================================

## IDX 140 | prompt_update_twoturn_R_to_q_then_p_steps_4
- MR: 1.000 → 0.000 (-1.000)
- risky_instr_title_hits: 
- suspicious: site:; wikipedia
- query_title_hits: World Poker Tour

Question: When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

Query: `George Danzer "World Poker Tour" winner`

Instruction excerpt:
```text
Given the fields question and summary_1, produce one compact BM25 query optimized for the second hop that retrieves additional documents not captured in the first hop. Follow this ordered, sample-aware edit program (apply steps in order and pick the most appropriate shape): 1) If the summary names a candidate and you need to confirm that candidate’s association with the tournament brand, form a compact co‑occurrence query with the person’s full name first, then the exact tournament phrase. ...
```

========================================================================================================================

## IDX 150 | prompt_update_onecall_R_to_q_to_p_steps_4
- MR: 1.000 → 0.000 (-1.000)
- risky_instr_title_hits: Paul Winters (American football)
- suspicious: 
- query_title_hits: 2012 Wayne State Warriors football team; Paul Winters (American football)

Question: What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

Query: `2012 Wayne State Warriors football team" OR "Paul Winters (American football)" Wayne State University`

Instruction excerpt:
```text
Given question and summary_1, produce a single compact BM25 query optimized for the second hop that will surface the canonical season page and the coach bio and their short lead-sentence affiliation lines (to confirm the shared institution). Preserve these sample anchors: 2012 Wayne State Warriors football team, Paul Winters, Wayne State University. Avoid stadium/venue names (Tom Adams Field), conference/division tokens (GLIAC, NCAA Division II), extra season years (2011, 2016, 2017, etc.), ...
```

========================================================================================================================

## IDX 169 | prompt_update_onecall_R_to_q_to_p_steps_4
- MR: 1.000 → 0.000 (-1.000)
- risky_instr_title_hits: 
- suspicious: imdb
- query_title_hits: Bud Ekins; Steve McQueen

Question: What movie did "the king of cool" play in with Bud Ekins as his stunt double?

Query: `Bud Ekins" "Steve McQueen" "stunt double" "The Great Escape" motorcycle stunt "Stuntmen's Hall of Fame" IMDb`

Instruction excerpt:
```text
Given fields question and summary_1, produce the BM25-style second-hop query or queries optimized to retrieve authoritative film‑credit statements that confirm whether a named stunt performer served as a named actor’s stunt double for a specific film. Emit short, phrase-focused, conjunctive BM25 queries (not natural‑language questions). Keep queries compact and high‑precision; quoted anchors and exact phrases first, then a 1–2 token stunt qualifier, then 1–2 source‑type tokens to bias toward ...
```

========================================================================================================================

## IDX 247 | prompt_update_onecall_R_to_q_to_p_steps_4
- MR: 1.000 → 0.000 (-1.000)
- risky_instr_title_hits: Occupy Ghana
- suspicious: site:
- query_title_hits: Occupy Ghana

Question: What is another name for the online protest that opposed the transfer of ex-detainees from Guantanamo Bay in 2016?

Query: `site:ghanaweb.com OR site:joyonline.com OR site:change.org OR site:citinewsroom.com OR site:graphic.com.gh ("Occupy Ghana" OR OccupyGhana OR #OccupyGhana OR NPP) ("online petition" OR petition OR Change.org OR e-petition OR hashtag OR Twitter OR Facebook) (Guantanamo OR Gitmo OR "ex-detainees" OR Yemeni) ("January 2016" OR 2016)`

Instruction excerpt:
```text
Given the fields `question` and `summary_1`, produce a single compact BM25-style `query` optimized for the second hop to find an explicit named online campaign/hashtag or petition title that opposed the January 2016 transfer of Guantanamo ex‑detainees to Ghana. Preserve the anchors (OccupyGhana / "Occupy Ghana", NPP, Ghana, Guantanamo/Gitmo, Yemeni ex‑detainees) and the retrieval goal (an alternate name / hashtag / petition title). Constrain the query to local Ghana news and major ...
```

========================================================================================================================

## IDX 247 | prompt_update_twoturn_R_to_q_then_p_steps_4
- MR: 1.000 → 0.000 (-1.000)
- risky_instr_title_hits: Occupy Ghana
- suspicious: 
- query_title_hits: Occupy Ghana

Question: What is another name for the online protest that opposed the transfer of ex-detainees from Guantanamo Bay in 2016?

Query: `(OccupyGhana OR "Occupy Ghana" OR NPP OR "New Patriotic Party") AND Ghana AND (Guantanamo OR Gitmo) AND ("Jan 2016" OR "January 2016") AND (GhanaWeb OR JoyOnline OR graphic.com.gh OR citinewsroom.com OR Change.org OR Twitter OR Facebook) AND (petition OR "e-petition" OR "online petition" OR "online campaign" OR "online protest" OR hashtag OR # OR tweet OR "petition name" OR called OR "known as" OR named OR dubbed OR tagged OR "opposed transfer")`

Instruction excerpt:
```text
Given fields `question` and `summary_1`, produce one compact BM25-style query optimized for the second hop to retrieve an explicit name/alternate name/hashtag or petition title for the online protest that opposed the January 2016 transfer of ex‑detainees from Guantanamo to Ghana. Preserve the base role (one short second-hop query) and follow the ordered refinements below when composing the query: 1) Preserve core event and actor anchors up front: OccupyGhana (also allow the variant "Occupy ...
```

========================================================================================================================

## IDX 118 | prompt_update_onecall_R_to_q_to_p_steps_4
- MR: 0.500 → 1.000 (+0.500)
- risky_instr_title_hits: 
- suspicious: imdb; wikipedia
- query_title_hits: 

Question: What acress starred in both "Third Person" and "From Here to Eternity"?

Query: `Third Person 2013 cast starring actress; From Here to Eternity 1979 cast starring actress`

Instruction excerpt:
```text
Given the fields question and summary_1, produce the field query optimized for the second-hop of a multi-hop retrieval: a single compact BM25 query string (one text field) that may contain two semicolon-separated subqueries targeting authoritative title cast pages. Follow this ordered, version-aware program exactly: 1) Disambiguate Third Person first (only if necessary): if the summary or initial retrieval is ambiguous about which "Third Person" is meant, run a quick disambiguation step ...
```