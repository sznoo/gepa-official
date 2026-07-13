# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/v2_bm25_consistent_full19/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.553 |
| tie/invalid | 0.099 |
| both recovery | 0.289 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.487 | 0.145 | 0.827 |
| right_recovery | 76 | 0.618 | 0.053 | 0.837 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.316 | 0.158 | 0.823 |
| 1 | 38 | 0.447 | 0.158 | 0.828 |
| 2 | 38 | 0.658 | 0.079 | 0.834 |
| 3 | 38 | 0.789 | 0.000 | 0.844 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 1 | 38 | 0.316 | 0.158 | 0.823 |
| 2 | 38 | 0.447 | 0.158 | 0.828 |
| 3 | 38 | 0.658 | 0.079 | 0.834 |
| 4 | 38 | 0.789 | 0.000 | 0.844 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 70 | 0.643 | 0.000 | 0.845 |
| B | 67 | 0.582 | 0.000 | 0.823 |
| tie | 15 | 0.000 | 1.000 | 0.811 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 35 | 0.600 |
| answer_type | 7 | 0.714 |
| bridge_relation | 23 | 0.435 |
| mixed | 2 | 0.000 |
| noisy_entity | 6 | 0.833 |
| query_shape | 65 | 0.631 |
| surface_form | 7 | 0.286 |
| tie | 7 | 0.000 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 70 |
| B | 67 |
| tie | 15 |
