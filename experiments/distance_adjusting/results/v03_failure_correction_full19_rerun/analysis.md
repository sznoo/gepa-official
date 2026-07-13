# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/v03_failure_correction_full19_rerun/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.559 |
| tie/invalid | 0.112 |
| both recovery | 0.342 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.553 | 0.132 | 0.846 |
| right_recovery | 76 | 0.566 | 0.092 | 0.861 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.184 | 0.184 | 0.846 |
| 1 | 38 | 0.526 | 0.105 | 0.849 |
| 2 | 38 | 0.658 | 0.053 | 0.858 |
| 3 | 38 | 0.868 | 0.105 | 0.861 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 1 | 38 | 0.184 | 0.184 | 0.846 |
| 2 | 38 | 0.526 | 0.105 | 0.849 |
| 3 | 38 | 0.658 | 0.053 | 0.858 |
| 4 | 38 | 0.868 | 0.105 | 0.861 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 92 | 0.620 | 0.000 | 0.860 |
| B | 43 | 0.651 | 0.000 | 0.863 |
| tie | 17 | 0.000 | 1.000 | 0.794 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 74 | 0.595 |
| answer_type | 4 | 1.000 |
| bridge_relation | 26 | 0.577 |
| candidate_set | 1 | 0.000 |
| mixed | 2 | 0.000 |
| noisy_entity | 2 | 0.500 |
| query_shape | 39 | 0.487 |
| surface_form | 4 | 0.500 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 92 |
| B | 43 |
| tie | 17 |
