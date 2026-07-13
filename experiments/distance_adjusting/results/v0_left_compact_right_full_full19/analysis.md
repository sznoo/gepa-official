# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/v0_left_compact_right_full_full19/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.638 |
| tie/invalid | 0.072 |
| both recovery | 0.434 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.632 | 0.092 | 0.797 |
| right_recovery | 76 | 0.645 | 0.053 | 0.821 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.316 | 0.000 | 0.816 |
| 1 | 38 | 0.684 | 0.184 | 0.789 |
| 2 | 38 | 0.763 | 0.079 | 0.817 |
| 3 | 38 | 0.789 | 0.026 | 0.815 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 1 | 38 | 0.316 | 0.000 | 0.816 |
| 2 | 38 | 0.684 | 0.184 | 0.789 |
| 3 | 38 | 0.763 | 0.079 | 0.817 |
| 4 | 38 | 0.789 | 0.026 | 0.815 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 79 | 0.696 | 0.000 | 0.823 |
| B | 62 | 0.677 | 0.000 | 0.812 |
| tie | 11 | 0.000 | 1.000 | 0.690 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 66 | 0.652 |
| answer_type | 20 | 0.650 |
| bridge_relation | 26 | 0.654 |
| mixed | 1 | 1.000 |
| noisy_entity | 3 | 0.667 |
| query_shape | 26 | 0.731 |
| surface_form | 2 | 1.000 |
| tie | 8 | 0.000 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 79 |
| B | 62 |
| tie | 11 |
