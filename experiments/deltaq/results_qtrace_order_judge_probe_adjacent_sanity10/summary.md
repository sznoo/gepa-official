# Q-trace order judge probe

Examples selected: 10
Total judgments: 67
Compare judgments: 47
Equal judgments: 20

## Compare accuracy by pair kind

| pair_kind | n | accuracy | expected_B_or_A_rate | tie_expected_rate |
|---|---:|---:|---:|---:|
| adjacent | 47 | 0.766 | 0.213 | 0.787 |

## Compare prediction distribution

| predicted | n |
|---|---:|
| (empty) | 1 |
| A | 10 |
| B | 10 |
| tie | 26 |

## Equal accuracy

| n | accuracy | expected_equiv_rate | predicted_equiv_rate |
|---:|---:|---:|---:|
| 20 | 1.000 | 0.500 | 0.500 |

## Equal relation distribution

| relation | n |
|---|---:|
| different_failure_mode | 2 |
| different_success_quality | 8 |
| same_failure | 8 |
| same_success | 2 |

## Offline q-trace monotonicity

| adjacent_edges | nondecreasing_utility_rate |
|---:|---:|
| 47 | 1.000 |