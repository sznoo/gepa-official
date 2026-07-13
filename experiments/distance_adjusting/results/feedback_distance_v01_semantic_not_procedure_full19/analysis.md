# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/feedback_distance_v01_semantic_not_procedure_full19/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.434 |
| tie/invalid | 0.316 |
| both recovery | 0.184 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.553 | 0.171 | 0.851 |
| right_recovery | 76 | 0.316 | 0.461 | 0.821 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.500 | 0.316 | 0.835 |
| 1 | 38 | 0.316 | 0.316 | 0.842 |
| 2 | 38 | 0.500 | 0.211 | 0.842 |
| 3 | 38 | 0.421 | 0.421 | 0.823 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| None | 152 | 0.434 | 0.316 | 0.836 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 57 | 0.614 | 0.000 | 0.837 |
| B | 47 | 0.660 | 0.000 | 0.860 |
| tie | 48 | 0.000 | 1.000 | 0.810 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 42 | 0.476 |
| answer_type | 3 | 0.667 |
| bridge_relation | 21 | 0.571 |
| candidate_set | 16 | 0.438 |
| evidence_family | 43 | 0.488 |
| mixed | 11 | 0.182 |
| query_shape | 2 | 0.500 |
| surface_form | 2 | 0.500 |
| tie | 12 | 0.000 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 57 |
| B | 47 |
| tie | 48 |
