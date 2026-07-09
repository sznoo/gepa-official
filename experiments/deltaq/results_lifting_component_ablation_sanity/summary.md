# By arm

| key | n | recovery edges | current MR | next MR | generated MR | ΔMR vs current | ΔMR vs next | gen>current | gen>=next | first recovery reproduced | next recovery overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ALL | 21 | 21 | 0.000 | 1.000 | 0.476 | 0.476 | -0.524 | 0.476 | 0.476 | 0.476 | 0.476 |
| context_only | 3 | 3 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| effect_only | 3 | 3 | 0.000 | 1.000 | 0.333 | 0.333 | -0.667 | 0.333 | 0.333 | 0.333 | 0.333 |
| full | 3 | 3 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| generic | 3 | 3 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| type_context | 3 | 3 | 0.000 | 1.000 | 0.667 | 0.667 | -0.333 | 0.667 | 0.667 | 0.667 | 0.667 |
| type_effect | 3 | 3 | 0.000 | 1.000 | 0.333 | 0.333 | -0.667 | 0.333 | 0.333 | 0.333 | 0.333 |
| type_only | 3 | 3 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |

# By prompt arm name

| key | n | recovery edges | current MR | next MR | generated MR | ΔMR vs current | ΔMR vs next | gen>current | gen>=next | first recovery reproduced | next recovery overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ALL | 21 | 21 | 0.000 | 1.000 | 0.476 | 0.476 | -0.524 | 0.476 | 0.476 | 0.476 | 0.476 |
| context_only | 3 | 3 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| effect_only | 3 | 3 | 0.000 | 1.000 | 0.333 | 0.333 | -0.667 | 0.333 | 0.333 | 0.333 | 0.333 |
| full | 3 | 3 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| generic | 3 | 3 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| type_context | 3 | 3 | 0.000 | 1.000 | 0.667 | 0.667 | -0.333 | 0.667 | 0.667 | 0.667 | 0.667 |
| type_effect | 3 | 3 | 0.000 | 1.000 | 0.333 | 0.333 | -0.667 | 0.333 | 0.333 | 0.333 | 0.333 |
| type_only | 3 | 3 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |

# By edit type

| key | n | recovery edges | current MR | next MR | generated MR | ΔMR vs current | ΔMR vs next | gen>current | gen>=next | first recovery reproduced | next recovery overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ALL | 21 | 21 | 0.000 | 1.000 | 0.476 | 0.476 | -0.524 | 0.476 | 0.476 | 0.476 | 0.476 |
| remove_noisy_entity | 14 | 14 | 0.000 | 1.000 | 0.500 | 0.500 | -0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| remove_noisy_relation | 7 | 7 | 0.000 | 1.000 | 0.429 | 0.429 | -0.571 | 0.429 | 0.429 | 0.429 | 0.429 |

# By arm and edit type

| key | n | recovery edges | current MR | next MR | generated MR | ΔMR vs current | ΔMR vs next | gen>current | gen>=next | first recovery reproduced | next recovery overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| context_only::remove_noisy_entity | 2 | 2 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| context_only::remove_noisy_relation | 1 | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| effect_only::remove_noisy_entity | 2 | 2 | 0.000 | 1.000 | 0.500 | 0.500 | -0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| effect_only::remove_noisy_relation | 1 | 1 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| full::remove_noisy_entity | 2 | 2 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| full::remove_noisy_relation | 1 | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| generic::remove_noisy_entity | 2 | 2 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| generic::remove_noisy_relation | 1 | 1 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| type_context::remove_noisy_entity | 2 | 2 | 0.000 | 1.000 | 0.500 | 0.500 | -0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| type_context::remove_noisy_relation | 1 | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| type_effect::remove_noisy_entity | 2 | 2 | 0.000 | 1.000 | 0.500 | 0.500 | -0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| type_effect::remove_noisy_relation | 1 | 1 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| type_only::remove_noisy_entity | 2 | 2 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| type_only::remove_noisy_relation | 1 | 1 | 0.000 | 1.000 | 0.000 | 0.000 | -1.000 | 0.000 | 0.000 | 0.000 | 0.000 |

# By idx

| key | n | recovery edges | current MR | next MR | generated MR | ΔMR vs current | ΔMR vs next | gen>current | gen>=next | first recovery reproduced | next recovery overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 108 | 7 | 7 | 0.000 | 1.000 | 0.429 | 0.429 | -0.571 | 0.429 | 0.429 | 0.429 | 0.429 |
| 227 | 7 | 7 | 0.000 | 1.000 | 0.429 | 0.429 | -0.571 | 0.429 | 0.429 | 0.429 | 0.429 |
| 82 | 7 | 7 | 0.000 | 1.000 | 0.571 | 0.571 | -0.429 | 0.571 | 0.571 | 0.571 | 0.571 |