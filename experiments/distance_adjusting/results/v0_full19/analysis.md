# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/v0_full19/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.625 |
| tie/invalid | 0.072 |
| both recovery | 0.408 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.592 | 0.092 | 0.814 |
| right_recovery | 76 | 0.658 | 0.053 | 0.828 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.421 | 0.000 | 0.818 |
| 1 | 38 | 0.579 | 0.211 | 0.814 |
| 2 | 38 | 0.711 | 0.053 | 0.824 |
| 3 | 38 | 0.789 | 0.026 | 0.826 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 1 | 38 | 0.421 | 0.000 | 0.818 |
| 2 | 38 | 0.579 | 0.211 | 0.814 |
| 3 | 38 | 0.711 | 0.053 | 0.824 |
| 4 | 38 | 0.789 | 0.026 | 0.826 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 72 | 0.694 | 0.000 | 0.831 |
| B | 69 | 0.652 | 0.000 | 0.820 |
| tie | 11 | 0.000 | 1.000 | 0.760 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 53 | 0.660 |
| answer_type | 21 | 0.667 |
| bridge_relation | 22 | 0.727 |
| mixed | 5 | 0.400 |
| noisy_entity | 10 | 0.700 |
| query_shape | 29 | 0.621 |
| surface_form | 5 | 0.600 |
| tie | 7 | 0.000 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 72 |
| B | 69 |
| tie | 11 |
