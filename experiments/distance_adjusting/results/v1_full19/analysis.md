# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/v1_full19/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.520 |
| tie/invalid | 0.138 |
| both recovery | 0.303 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.539 | 0.171 | 0.820 |
| right_recovery | 76 | 0.500 | 0.105 | 0.843 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.211 | 0.211 | 0.828 |
| 1 | 38 | 0.500 | 0.211 | 0.831 |
| 2 | 38 | 0.684 | 0.105 | 0.829 |
| 3 | 38 | 0.684 | 0.026 | 0.837 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 1 | 38 | 0.211 | 0.211 | 0.828 |
| 2 | 38 | 0.500 | 0.211 | 0.831 |
| 3 | 38 | 0.684 | 0.105 | 0.829 |
| 4 | 38 | 0.684 | 0.026 | 0.837 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 65 | 0.662 | 0.000 | 0.838 |
| B | 66 | 0.545 | 0.000 | 0.827 |
| tie | 21 | 0.000 | 1.000 | 0.823 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 39 | 0.641 |
| answer_type | 17 | 0.824 |
| bridge_relation | 22 | 0.500 |
| mixed | 32 | 0.469 |
| noisy_entity | 1 | 0.000 |
| query_shape | 22 | 0.636 |
| tie | 19 | 0.000 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 65 |
| B | 66 |
| tie | 21 |
