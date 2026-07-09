# Q-trace order judge probe

Examples selected: 19
Total judgments: 125
Compare judgments: 87
Equal judgments: 38

## Compare accuracy by pair kind

| pair_kind | n | accuracy | expected_B_or_A_rate | tie_expected_rate |
|---|---:|---:|---:|---:|
| target | 87 | 0.851 | 0.448 | 0.552 |

## Compare prediction distribution

| predicted | n |
|---|---:|
| A | 27 |
| B | 25 |
| tie | 35 |

## Equal accuracy

| n | accuracy | expected_equiv_rate | predicted_equiv_rate |
|---:|---:|---:|---:|
| 38 | 0.921 | 0.500 | 0.474 |

## Equal relation distribution

| relation | n |
|---|---:|
| different_failure_mode | 6 |
| different_success_quality | 14 |
| same_failure | 11 |
| same_success | 7 |

## Offline q-trace monotonicity

| adjacent_edges | nondecreasing_utility_rate |
|---:|---:|
| 87 | 0.989 |