# Flagged Δp_i listings


========================================================================================================================

## IDX 55
- suspicious: site:; OR ;  AND ; ;

Question: What culture do both the Capital of the Netherlands and Amsterdamned have in common?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter1_split0): TRIGGER: Question mentions both the city 'Amsterdam' (capital) and the film 'Amsterdamned' and asks what culture they share. PRESERVE_RULE: Keep the main entity anchors intact as retrieval seeds: the film title anchor (e.g., 'Amsterdamned') and the place anchor ('Amsterdam' / capital). Do not broaden these anchors into generic culture phrases at this stage. RESTORE_RULE: Reintroduce tight, disambiguating film metadata cues as retrieval signals: year token (e.g., 1988), nationality token ('Dutch' or 'Netherlands'), genre cue ('horror film' or 'film'), director name (e.g., 'Dick Maas'), and setting cue ('canals' or 'set in Amsterdam'). These cues ...
```

========================================================================================================================

## IDX 60
- suspicious: site:; OR ;  AND ; ;

Question: The telescope that observed the debris disk of HD 92945 was launched into low Earth orbit in what year?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter2_split0): TRIGGER: Apply when the follow-up step must retrieve the launch year/date of a named space telescope (entity-centric attribute lookup: e.g., “which year was [TELESCOPE] launched?”). PRESERVE_RULE: Keep the canonical telescope name tokens (entity tokens such as 'Hubble Space Telescope' or the provided telescope name) and a single clear date-attribute token such as 'launch', 'launch date', or 'launch year'. Optionally keep a short contextual locator token like 'overview' or 'infobox' to favor summary pages. RESTORE_RULE: If initial retrieval returns many mission pages or instrument pages (e.g., pages listing multiple STS missions or instrument ...
```

========================================================================================================================

## IDX 77
- suspicious: site:; wikipedia; OR ;  AND ; ;

Question: The winner of the first season of "Next Great Baker" would win an apprenticeship at the bakery owned by who?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter3_split0): TRIGGER: Apply when the question asks who owns (or is the owner of) a bakery that was offered as an apprenticeship prize for a specific season of a TV show. PRESERVE_RULE: Keep four retrieval anchors: the show title, the explicit season marker (e.g., 'season 1'), the bakery's proper name, and a prize relation token (words like 'apprenticeship', 'prize', 'grand prize'). Specify expected answer type: a single person-name (owner). RESTORE_RULE: If retrieval drifts to general series pages or bakery menus, reintroduce the prize phrasing and season constraint: demand season-level show sources (season page, episode/press release, news article) that ...
```

========================================================================================================================

## IDX 6
- suspicious: final answer; OR ;  AND ; ;

Question: Smith Creek is a 35.5 mi tributary stream of the North Fork of a river that passes through which US states?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter1_split0): TRIGGER: When the question asks which U.S. states a parent river passes through and the current context supplies a tributary (e.g., 'Smith Creek' -> parent 'North Fork Shenandoah River'), apply this edit to produce the second-hop retrieval query. PRESERVE_RULE: Keep the precise parent-watercourse entity phrase (the fork-level name that identifies the immediate parent river) as a primary anchor token in the query (example form appears in the available inputs). RESTORE_RULE: Restore a downstream/confluence landmark token that links the fork to the river's lower course (use a well-known downstream place such as Harpers Ferry or the Potomac as a ...
```

========================================================================================================================

## IDX 90
- suspicious: site:; final answer; OR ;  AND ; ;

Question: Imiliya is a town located in what pilgrimage site?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter2_split0): TRIGGER: Question asks which pilgrimage site a named town is located in (town→pilgrimage containment question). PRESERVE_RULE: Keep the requirement that create_query_hop2 returns exactly one compact BM25 query string. Preserve the retrieval intent: obtain authoritative statements that identify the pilgrimage site and name its core landmarks/authority (answer type: pilgrimage site; role: Lumbini as pilgrimage/birthplace). RESTORE_RULE: Restore authoritative landmark and authority tokens and relation cues to the query: include terms that signal 'birthplace' relation and established authorities/landmarks (examples: birthplace, Siddhartha Gautama, ...
```

========================================================================================================================

## IDX 108
- suspicious: site:; final answer; OR ;  AND ; ;

Question: Are Solo and La Croix Sparkling Water produced in the same country ?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter1_split0): TRIGGER: When the next retrieval hop must resolve the production/origin country for a named beverage (a single-entity disambiguation used to compare countries), e.g., a follow-up asking whether 'Solo' and 'La Croix' are produced in the same country. PRESERVE_RULE: Keep the core entity name tokens and any tight regional disambiguator or parenthetical cue that resolves ambiguity (for example, the token indicating 'Australian' or a short parenthetical like '(Australian soft drink)'). Also retain the target country keyword as an anchor if present (e.g., 'Australia'). RESTORE_RULE: Reintroduce a concise evidence-type token such as 'country of origin', ...
```

========================================================================================================================

## IDX 82
- suspicious: site:; final answer; support title; OR ;  AND ; ;

Question: What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter3_split0): TRIGGER: Apply when the baseline query mixes the event title with many personal names, gang names, dates, and long etymology phrases and retrieval returns biography- or gang-heavy pages instead of a short label/definition for the perpetrators. PRESERVE_RULE: Keep compact event anchors and location tokens (the robbery name as an event anchor and the place 'Liberty, Missouri' or equivalent location token) and preserve a small candidate set of one-word perpetrator-label tokens (e.g., guerrillas, bushwhackers, partisans). RESTORE_RULE: If the upstream query removed the event anchor or candidate labels, restore: (1) the event anchor token(s) (robbery- ...
```

========================================================================================================================

## IDX 118
- suspicious: site:; imdb; wikipedia; OR ;  AND ; ;

Question: What acress starred in both "Third Person" and "From Here to Eternity"?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter1_split0): TRIGGER: If the question asks which performer (actress) ‘starred in both’ two named works (two title entities given) and prior retrieval lacked authoritative cast lists or disambiguation. PRESERVE_RULE: Keep the relation cue ('starred in both' / overlap-of-cast) and answer type (person — actress). Treat the two named works as distinct entity roles: SOURCE_TITLE and TARGET_TITLE to be compared. RESTORE_RULE: Force disambiguation and versioning tokens for ambiguous titles and require 'cast' evidence: instruct the generator to append a disambiguation cue for any ambiguous title (example: treat 'Third Person' as 'Third Person' + ...
```

========================================================================================================================

## IDX 132
- suspicious: site:; wikipedia; final answer; support title; OR ;  AND ; ;

Question: The soundtrack to 'Dancer in the Dark' is by what Icelandic singer, songwriter, actress, record producer, and DJ?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter3_split0): TRIGGER: Apply when the question asks who performed or who is credited for a film soundtrack (contains words like 'soundtrack', 'soundtrack to', film title, or album title). PRESERVE_RULE: Preserve entity anchors and relation cues already present in the input: album title (e.g., 'Selmasongs'), film title (e.g., 'Dancer in the Dark'), artist name (e.g., 'Björk'), and the relation cue 'soundtrack' or 'soundtrack by'. RESTORE_RULE: Reintroduce compact album-level bridge cues that point to an album/soundtrack page: prefer tokens such as 'soundtrack credits', 'credits', 'performed by', 'album', 'soundtrack listing', or 'credited to' alongside the ...
```

========================================================================================================================

## IDX 140
- suspicious: site:; wikipedia; final answer; OR ;  AND ; ;

Question: When was the winner of the series of international poker tournaments started in 2002 by Steven Lipscomb who has also won four World Series of Poker bracelets born?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter1_split0): TRIGGER: When the next query must verify whether a named candidate person is a winner/champion of a named tournament series before extracting biographical details. PRESERVE_RULE: Keep the candidate-person anchor token(s) (the person's full name) and the entity role 'candidate person' in the prompt so the produced query pairs that person with an event-series anchor. RESTORE_RULE: Restore an explicit event-series anchor: require the canonical series name phrase and optional short-form acronym (e.g., 'World Poker Tour' and 'WPT') as retrieval cues to force pages that explicitly link the person to the series. DROP_OR_AVOID_RULE: Drop list-oriented or ...
```

========================================================================================================================

## IDX 149
- suspicious: site:; final answer; OR ;  AND ; ;

Question: A mythical forest creature that is seductive and from Sweden has the same being as what divine figure?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter2_split0): TRIGGER: Apply when the question asks which divine/older figure is 'the same being as' or original identity of a named Swedish seductive forest-creature (mentions hulder / skogsrå or regional names). PRESERVE_RULE: Preserve core folkloric and name anchors and role cues: hulder, skogsrå, Huld, regional name examples (e.g., Tallemaja, ulda) and the role-token völva; preserve philological cue words such as etymology, origin, root, and the root-form variant huldr/huld as examples to guide retrieval focus. RESTORE_RULE: If the generated query omits philological role cues, reinsert at least one etymology marker (e.g., 'etymology' or 'origin') and the ...
```

========================================================================================================================

## IDX 150
- suspicious: site:; final answer; OR ;  AND ; ;

Question: What institution does 2012 Wayne State Warriors football team and Paul Winters have in common?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter2_split0): TRIGGER: Apply when the goal is to identify a shared institutional affiliation between a specific team-season page and a named person (i.e., mapping a season/team entity and a coach/person to their university). PRESERVE_RULE: Keep only the core anchors: the season+team identifier (year + team name) and the person name. Preserve canonical program alias tokens (e.g., program nickname) only if they are identical to the anchors. RESTORE_RULE: Ensure the explicit full institution token (the university name) appears in the generated query when available. Add the institution token to reintroduce the bridge cue that ties team pages and coach bios to a ...
```

========================================================================================================================

## IDX 169
- suspicious: site:; imdb; wikipedia; final answer; OR ;  AND ; ;

Question: What movie did "the king of cool" play in with Bud Ekins as his stunt double?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter2_split0): TRIGGER: Question asks which movie the actor nicknamed "the king of cool" appeared in with Bud Ekins as his stunt double (mentions Steve McQueen / Bud Ekins / motorcycle stunt). PRESERVE_RULE: Keep the core retrieval anchors intact: the stunt-performer (Bud Ekins), the principal actor (Steve McQueen / 'the king of cool'), and the specific film anchor present in the question (The Great Escape). Preserve the target relation: 'stunt double' relationship tying Ekins to McQueen and to a motorcycle-stunt sequence. RESTORE_RULE: Restore focused bridge cues that guide authoritative confirmation: include a compact phrase for the stunt type ('motorcycle' ...
```

========================================================================================================================

## IDX 180
- suspicious: site:; wikipedia; final answer; OR ;  AND ; ;

Question: What is the date of released for the eleventh studio album of the highest-selling heavy metal group from Canada?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter1_split0): TRIGGER: This step must identify which studio album is the artist's 11th (confirm the album title/ordinal) before attempting any release-date lookup. PRESERVE_RULE: Keep the artist anchor (e.g., the band name appearing in the visible inputs) and a 'discography' / 'studio albums' cue. Preserve the explicit ordinal intention (11th / eleventh) so retrieval targets an ordered list or an album page that states '11th studio album.' RESTORE_RULE: If the outgoing prompt removed ordinal or discography anchors, restore an explicit ordinal token ('11th' or 'eleventh' or numeric '11') together with a 'discography' or 'studio albums' cue and an explicit ...
```

========================================================================================================================

## IDX 227
- suspicious: site:; final answer; OR ;  AND ; ;

Question: Evan Peters had a role as the fictional superhero from comic books by what publisher?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter1_split0): TRIGGER: When the next query should confirm an actor->character link (actor portrayed X) before retrieving publisher/comic pages. PRESERVE_RULE: Keep the core entity tokens: actor name (e.g., 'Evan Peters') and character name(s)/aliases (e.g., 'Quicksilver', 'Pietro Maximoff'). Do not drop these anchors or replace them with generic descriptions. RESTORE_RULE: Restore role-link and evidence-type cues that elicit cast/filmography lines: include role-verbs/phrases such as 'portrayed', 'portrayer', 'credited', or 'cast' and terms signaling authoritative film-credit sources such as 'filmography', 'cast list', or 'credited as'. These tokens must appear ...
```

========================================================================================================================

## IDX 247
- suspicious: site:; final answer; OR ;  AND ; ;

Question: What is another name for the online protest that opposed the transfer of ex-detainees from Guantanamo Bay in 2016?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter3_split0): TRIGGER: When the question asks for an alternate name, campaign title, or hashtag for an online protest opposing the Jan 2016 transfer of ex-detainees to Ghana (e.g., 'another name for the online protest that opposed the transfer...'). PRESERVE_RULE: Keep core event and actor anchors as ordinary tokens: OccupyGhana, Ghana, Guantanamo (or Gitmo), 2016, Yemeni (ex-)detainees. These must remain in the query to maintain event specificity. RESTORE_RULE: Restore digital-campaign bridge cues to bias retrieval toward local news and petition pages: include one bridge token such as petition OR hashtag OR online OR 'e-petition' and optionally one or two ...
```

========================================================================================================================

## IDX 267
- suspicious: site:; final answer; OR ;  AND ; ;

Question: Who were the writers of an American television series based on the DC Comics character Superman, which starred an American actor known for his television roles that include Fox Crane on the NBC daytime soap opera "Passions"?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter3_split0): TRIGGER: Apply when the question requests the writers/creators of a TV show (named) and mentions an actor as a casting/bridge clue (actor role or credits). PRESERVE_RULE: Keep the show title and the actor anchor; preserve a show-type cue ('TV series') and a credit-seeking cue ('created by' / 'writing credits' / 'writers') and retain primary creator names if they already appear in inputs. RESTORE_RULE: If prior queries or instructions list many individual staff names or episode pages, restore focus to series-level evidence by instructing: emphasize 'TV series' + credit cue, consolidate to primary creators (max two names) rather than enumerating ...
```

========================================================================================================================

## IDX 262
- suspicious: site:; wikipedia; final answer; OR ;  AND ; ;

Question: Kunihiko Tanaka designed the characters for which video game developed by Monolith Soft ?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter2_split0): TRIGGER: applies when the question asks which game a named character designer (person) worked on for a named developer or series PRESERVE_RULE: Always preserve the designer's full name token (e.g., 'Kunihiko Tanaka') as an anchor in the query. RESTORE_RULE: Restore or insert the precise target game title (if present in the task context) plus a bridge cue indicating staff/credits (use tokens like 'credits' or 'character designer' or 'staff'). If the exact title is not present, combine the developer name (e.g., 'Monolith Soft') with the bridge cue and the designer name. DROP_OR_AVOID_RULE: Remove noisy series- or character-specific tokens that pull ...
```

========================================================================================================================

## IDX 268
- suspicious: final answer; OR ;  AND ; ;

Question: Between G. K. Chesterton and Henry Green, who had more diverse job experiences?

Δp excerpt:
```text
EDGE 0 Δp (R0_base -> Rmid_iter3_split0): TRIGGER: When a comparison question asks which of two people had more diverse jobs but one person (the second named individual) is missing or ambiguous in current retrievals (e.g., comparing G. K. Chesterton vs Henry Green and Henry Green is not resolved). PRESERVE_RULE: Keep the hop's retrieval intent framed as a comparison: this hop must fetch biographical/occupation evidence only for the missing subject so the overall task can compare job diversity; retain the other person (G. K. Chesterton) as the comparison endpoint in the surrounding context but do not query for that person in this hop. RESTORE_RULE: Restore explicit disambiguation cues for ...
```