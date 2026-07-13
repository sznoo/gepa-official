# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/v02_semantic_feedback_full19/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.599 |
| tie/invalid | 0.046 |
| both recovery | 0.382 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.592 | 0.039 | 0.842 |
| right_recovery | 76 | 0.605 | 0.053 | 0.854 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.316 | 0.053 | 0.842 |
| 1 | 38 | 0.579 | 0.053 | 0.842 |
| 2 | 38 | 0.658 | 0.053 | 0.848 |
| 3 | 38 | 0.842 | 0.026 | 0.861 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 1 | 38 | 0.316 | 0.053 | 0.842 |
| 2 | 38 | 0.579 | 0.053 | 0.842 |
| 3 | 38 | 0.658 | 0.053 | 0.848 |
| 4 | 38 | 0.842 | 0.026 | 0.861 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 81 | 0.642 | 0.000 | 0.851 |
| B | 64 | 0.609 | 0.000 | 0.854 |
| tie | 7 | 0.000 | 1.000 | 0.764 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 49 | 0.612 |
| answer_type | 15 | 0.733 |
| bridge_relation | 28 | 0.571 |
| mixed | 15 | 0.467 |
| noisy_entity | 2 | 0.000 |
| query_shape | 42 | 0.643 |
| tie | 1 | 0.000 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 81 |
| B | 64 |
| tie | 7 |
