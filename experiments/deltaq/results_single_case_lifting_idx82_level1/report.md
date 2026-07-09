# Single-case Level 1 q-path lifting report

- idx: 82
- question: What type of criminals, named after a term from the Revolutionary War, were involved in the Clay County Savings Association Building robbery?
- gold_answer: bushwhackers
- gold_support_titles: ['Clay County Savings Association Building', 'Bushwhacker']
- base_missing: ['Bushwhacker']

## Query path

| path_pos | source | step | missing recovery | support recall | query |
|---:|---|---:|---:|---:|---|
| 0 | base_query | 0 | 0.000 | 0.500 | `"Clay County Savings Association robbery" 1866 Liberty Missouri Jesse James Archie Clement James–Younger Gang guerrillas bushwhackers partisans term origin Revolutionary War usage` |
| 1 | trace_step_1_compact_query | 1 | 0.000 | 0.500 | `"Clay County Savings Association robbery" Jesse James Archie Clement James–Younger Gang guerrillas bushwhackers partisans term origin Revolutionary War usage` |
| 2 | trace_step_2_remove_noisy_entity | 2 | 1.000 | 1.000 | `"Clay County Savings Association robbery" guerrillas bushwhackers partisans term origin Revolutionary War usage` |
| 3 | trace_step_3_canonicalize_surface_form | 3 | 1.000 | 1.000 | `Clay County Savings Association Building robbery guerrillas bushwhackers partisans term origin Revolutionary War usage` |
| 4 | trace_step_4_add_answer_type | 4 | 1.000 | 1.000 | `Clay County Savings Association Building robbery criminals "named after Revolutionary War" term guerrillas bushwhackers partisans` |

## Transition reproduction


---

### Transition 0_to_1: base_query → trace_step_1_compact_query

- edit_type: `compact_query`
- changed_context: Removed date and location tokens (1866, Liberty Missouri) to reduce noise while keeping the main event and candidate labels.
- intended_retrieval_effect: Broaden retrieval to documents about the robbery without restricting by date/place, focusing on actors and terms.

#### Current / oracle next / generated

current query:
```text
"Clay County Savings Association robbery" 1866 Liberty Missouri Jesse James Archie Clement James–Younger Gang guerrillas bushwhackers partisans term origin Revolutionary War usage
```
oracle next query:
```text
"Clay County Savings Association robbery" Jesse James Archie Clement James–Younger Gang guerrillas bushwhackers partisans term origin Revolutionary War usage
```
level1 generated query:
```text
Clay County Savings Association robbery" Jesse James Archie Clement James-Younger Gang guerrillas bushwhackers partisans Revolutionary War term origin usage
```

#### Retrieval metrics

| arm | missing recovery | support recall | recovered missing | support hits |
|---|---:|---:|---|---|
| current | 0.000 | 0.500 | [] | ['Clay County Savings Association Building'] |
| oracle_next | 0.000 | 0.500 | [] | ['Clay County Savings Association Building'] |
| level1 | 0.000 | 0.500 | [] | ['Clay County Savings Association Building'] |

#### Reproduction

- newly_recovered_by_oracle_next: []
- reproduced_newly_recovered: []
- first_recovery_reproduced: None
- new_recovery_reproduction_rate: None
- next_recovery_overlap: None
- gen_missing_recovery_minus_current: 0.000
- gen_missing_recovery_minus_next: 0.000

#### Retrieved titles

current:
- Clay County Savings Association Building
- Jesse James
- James–Younger Gang
- Archie Clement
- James Brothers' House and Farm
- Frank James
- The Great Northfield Minnesota Raid

oracle_next:
- Clay County Savings Association Building
- Jesse James
- Frank James
- The Great Northfield Minnesota Raid
- Wood Hite
- Quantrill's Raiders
- James–Younger Gang

level1:
- Clay County Savings Association Building
- Jesse James
- Frank James
- The Great Northfield Minnesota Raid
- Wood Hite
- Quantrill's Raiders
- James–Younger Gang


---

### Transition 1_to_2: trace_step_1_compact_query → trace_step_2_remove_noisy_entity

- edit_type: `remove_noisy_entity`
- changed_context: Removed individual names and gang (Jesse James, Archie Clement, James–Younger Gang) to avoid retrieving documents about specific people rather than the term used for the criminals.
- intended_retrieval_effect: Prioritize documents discussing the type/label of criminals involved rather than biographies of named individuals.

#### Current / oracle next / generated

current query:
```text
"Clay County Savings Association robbery" Jesse James Archie Clement James–Younger Gang guerrillas bushwhackers partisans term origin Revolutionary War usage
```
oracle next query:
```text
"Clay County Savings Association robbery" guerrillas bushwhackers partisans term origin Revolutionary War usage
```
level1 generated query:
```text
Clay County Savings Association robbery" bushwhackers guerrillas partisans term origin Revolutionary War named after label criminals
```

#### Retrieval metrics

| arm | missing recovery | support recall | recovered missing | support hits |
|---|---:|---:|---|---|
| current | 0.000 | 0.500 | [] | ['Clay County Savings Association Building'] |
| oracle_next | 1.000 | 1.000 | ['Bushwhacker'] | ['Bushwhacker', 'Clay County Savings Association Building'] |
| level1 | 1.000 | 1.000 | ['Bushwhacker'] | ['Bushwhacker', 'Clay County Savings Association Building'] |

#### Reproduction

- newly_recovered_by_oracle_next: ['Bushwhacker']
- reproduced_newly_recovered: ['Bushwhacker']
- first_recovery_reproduced: True
- new_recovery_reproduction_rate: 1.0
- next_recovery_overlap: 1.0
- gen_missing_recovery_minus_current: 1.000
- gen_missing_recovery_minus_next: 0.000

#### Retrieved titles

current:
- Clay County Savings Association Building
- Jesse James
- Frank James
- The Great Northfield Minnesota Raid
- Wood Hite
- Quantrill's Raiders
- James–Younger Gang

oracle_next:
- Clay County Savings Association Building
- Bushwhacker
- McNeill's Rangers
- Guerrilla theatre
- Guerrilla war in the Baltic states
- Donkey Squads (Korean War)
- Latvian partisans

level1:
- Clay County Savings Association Building
- Bushwhacker
- McNeill's Rangers
- Guerrilla war in the Baltic states
- Guerrilla theatre
- Latvian partisans
- Norrmalmstorg robbery


---

### Transition 2_to_3: trace_step_2_remove_noisy_entity → trace_step_3_canonicalize_surface_form

- edit_type: `canonicalize_surface_form`
- changed_context: Changed event phrasing to include 'Building' for the canonical event name and removed surrounding quotes.
- intended_retrieval_effect: Match sources that use the formal event name 'Clay County Savings Association Building robbery' to improve precision.

#### Current / oracle next / generated

current query:
```text
"Clay County Savings Association robbery" guerrillas bushwhackers partisans term origin Revolutionary War usage
```
oracle next query:
```text
Clay County Savings Association Building robbery guerrillas bushwhackers partisans term origin Revolutionary War usage
```
level1 generated query:
```text
Clay County Savings Association Building robbery guerrillas bushwhackers partisans term origin Revolutionary War usage
```

#### Retrieval metrics

| arm | missing recovery | support recall | recovered missing | support hits |
|---|---:|---:|---|---|
| current | 1.000 | 1.000 | ['Bushwhacker'] | ['Bushwhacker', 'Clay County Savings Association Building'] |
| oracle_next | 1.000 | 1.000 | ['Bushwhacker'] | ['Bushwhacker', 'Clay County Savings Association Building'] |
| level1 | 1.000 | 1.000 | ['Bushwhacker'] | ['Bushwhacker', 'Clay County Savings Association Building'] |

#### Reproduction

- newly_recovered_by_oracle_next: []
- reproduced_newly_recovered: []
- first_recovery_reproduced: None
- new_recovery_reproduction_rate: None
- next_recovery_overlap: 1.0
- gen_missing_recovery_minus_current: 0.000
- gen_missing_recovery_minus_next: 0.000

#### Retrieved titles

current:
- Clay County Savings Association Building
- Bushwhacker
- McNeill's Rangers
- Guerrilla theatre
- Guerrilla war in the Baltic states
- Donkey Squads (Korean War)
- Latvian partisans

oracle_next:
- Clay County Savings Association Building
- Bushwhacker
- McNeill's Rangers
- Guerrilla theatre
- Guerrilla war in the Baltic states
- Donkey Squads (Korean War)
- Latvian partisans

level1:
- Clay County Savings Association Building
- Bushwhacker
- McNeill's Rangers
- Guerrilla theatre
- Guerrilla war in the Baltic states
- Donkey Squads (Korean War)
- Latvian partisans


---

### Transition 3_to_4: trace_step_3_canonicalize_surface_form → trace_step_4_add_answer_type

- edit_type: `add_answer_type`
- changed_context: Added explicit answer-focus phrase 'criminals "named after Revolutionary War" term' to request the label for the perpetrators; retained candidate labels (guerrillas, bushwhackers, partisans).
- intended_retrieval_effect: Retrieve documents that identify the type/name-of-criminals involved, especially those describing a Revolutionary-War-derived term (e.g., 'bushwhackers'/'guerrillas').

#### Current / oracle next / generated

current query:
```text
Clay County Savings Association Building robbery guerrillas bushwhackers partisans term origin Revolutionary War usage
```
oracle next query:
```text
Clay County Savings Association Building robbery criminals "named after Revolutionary War" term guerrillas bushwhackers partisans
```
level1 generated query:
```text
Clay County Savings Association Building robbery criminals "named after Revolutionary War" term guerrillas bushwhackers partisans origin usage
```

#### Retrieval metrics

| arm | missing recovery | support recall | recovered missing | support hits |
|---|---:|---:|---|---|
| current | 1.000 | 1.000 | ['Bushwhacker'] | ['Bushwhacker', 'Clay County Savings Association Building'] |
| oracle_next | 1.000 | 1.000 | ['Bushwhacker'] | ['Bushwhacker', 'Clay County Savings Association Building'] |
| level1 | 1.000 | 1.000 | ['Bushwhacker'] | ['Bushwhacker', 'Clay County Savings Association Building'] |

#### Reproduction

- newly_recovered_by_oracle_next: []
- reproduced_newly_recovered: []
- first_recovery_reproduced: None
- new_recovery_reproduction_rate: None
- next_recovery_overlap: 1.0
- gen_missing_recovery_minus_current: 0.000
- gen_missing_recovery_minus_next: 0.000

#### Retrieved titles

current:
- Clay County Savings Association Building
- Bushwhacker
- McNeill's Rangers
- Guerrilla theatre
- Guerrilla war in the Baltic states
- Donkey Squads (Korean War)
- Latvian partisans

oracle_next:
- Clay County Savings Association Building
- Bushwhacker
- McNeill's Rangers
- Guerrilla war in the Baltic states
- Latvian partisans
- Soviet partisans
- Iola's fort

level1:
- Clay County Savings Association Building
- Bushwhacker
- McNeill's Rangers
- Guerrilla war in the Baltic states
- Guerrilla theatre
- Latvian partisans
- Norrmalmstorg robbery
