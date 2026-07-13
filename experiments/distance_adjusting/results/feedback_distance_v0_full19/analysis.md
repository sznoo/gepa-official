# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/feedback_distance_v0_full19/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.717 |
| tie/invalid | 0.039 |
| both recovery | 0.526 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.737 | 0.026 | 0.841 |
| right_recovery | 76 | 0.697 | 0.053 | 0.832 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.763 | 0.026 | 0.839 |
| 1 | 38 | 0.658 | 0.026 | 0.833 |
| 2 | 38 | 0.684 | 0.079 | 0.838 |
| 3 | 38 | 0.763 | 0.026 | 0.834 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| None | 152 | 0.717 | 0.039 | 0.836 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 93 | 0.720 | 0.000 | 0.837 |
| B | 53 | 0.792 | 0.000 | 0.834 |
| tie | 6 | 0.000 | 1.000 | 0.843 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 62 | 0.855 |
| answer_type | 1 | 0.000 |
| bridge_relation | 10 | 0.800 |
| candidate_set | 22 | 0.682 |
| evidence_family | 8 | 0.625 |
| mixed | 3 | 0.667 |
| query_shape | 40 | 0.600 |
| surface_form | 4 | 0.500 |
| tie | 2 | 0.000 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 93 |
| B | 53 |
| tie | 6 |
