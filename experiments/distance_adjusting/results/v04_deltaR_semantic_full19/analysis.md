# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/v04_deltaR_semantic_full19/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.599 |
| tie/invalid | 0.086 |
| both recovery | 0.368 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.605 | 0.092 | 0.842 |
| right_recovery | 76 | 0.592 | 0.079 | 0.850 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.368 | 0.053 | 0.836 |
| 1 | 38 | 0.526 | 0.132 | 0.843 |
| 2 | 38 | 0.684 | 0.132 | 0.860 |
| 3 | 38 | 0.816 | 0.026 | 0.846 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 1 | 38 | 0.368 | 0.053 | 0.836 |
| 2 | 38 | 0.526 | 0.132 | 0.843 |
| 3 | 38 | 0.684 | 0.132 | 0.860 |
| 4 | 38 | 0.816 | 0.026 | 0.846 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 77 | 0.649 | 0.000 | 0.858 |
| B | 62 | 0.661 | 0.000 | 0.840 |
| tie | 13 | 0.000 | 1.000 | 0.806 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 54 | 0.519 |
| answer_type | 4 | 0.750 |
| breadth | 23 | 0.957 |
| bridge_relation | 22 | 0.545 |
| evidence_family | 32 | 0.594 |
| mixed | 3 | 0.333 |
| noisy_entity | 4 | 1.000 |
| query_shape | 3 | 0.333 |
| surface_form | 1 | 1.000 |
| tie | 6 | 0.000 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 77 |
| B | 62 |
| tie | 13 |
