# Distance prompt recovery analysis

- judgments_path: `experiments/distance_adjusting/results/v0_compact_runtime_full19/judgments.jsonl`
- n_tasks: 152

## Overall

| metric | value |
|---|---:|
| task recovery | 0.638 |
| tie/invalid | 0.053 |
| both recovery | 0.395 |

## Breakdown by task_kind

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| left_recovery | 76 | 0.711 | 0.053 | 0.820 |
| right_recovery | 76 | 0.566 | 0.053 | 0.834 |

## Breakdown by split_iter

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 0 | 38 | 0.447 | 0.000 | 0.822 |
| 1 | 38 | 0.632 | 0.132 | 0.823 |
| 2 | 38 | 0.711 | 0.053 | 0.827 |
| 3 | 38 | 0.763 | 0.026 | 0.835 |

## Breakdown by num_edges_before_split

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| 1 | 38 | 0.447 | 0.000 | 0.822 |
| 2 | 38 | 0.632 | 0.132 | 0.823 |
| 3 | 38 | 0.711 | 0.053 | 0.827 |
| 4 | 38 | 0.763 | 0.026 | 0.835 |

## Breakdown by predicted

| key | n | recovery | tie/invalid | mean confidence |
|---|---:|---:|---:|---:|
| A | 81 | 0.679 | 0.000 | 0.837 |
| B | 63 | 0.667 | 0.000 | 0.821 |
| tie | 8 | 0.000 | 1.000 | 0.771 |

## Breakdown by dominant_gap_type

| gap_type | n | recovery |
|---|---:|---:|
| anchor | 63 | 0.714 |
| answer_type | 25 | 0.760 |
| bridge_relation | 30 | 0.567 |
| noisy_entity | 5 | 0.200 |
| query_shape | 22 | 0.591 |
| surface_form | 3 | 0.667 |
| tie | 4 | 0.000 |

## Prediction distribution

| predicted | n |
|---|---:|
| A | 81 |
| B | 63 |
| tie | 8 |
