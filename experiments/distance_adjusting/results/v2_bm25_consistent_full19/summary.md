# Distance prompt recovery eval

- tasks_path: `experiments/distance_adjusting/cache/full19_distance_tasks.jsonl`
- prompt_path: `experiments/distance_adjusting/prompts/distance_prompt_v2_bm25_consistent.txt`

- n_tasks: 152
- n_midpoint_triples: 76
- left_recovery_rate: 0.4868
- right_recovery_rate: 0.6184
- both_recovery_rate: 0.2895
- mean_recovery_rate: 0.5526
- tie_or_invalid_rate: 0.0987

## Interpretation
- left_recovery: full edge is judged larger than R_i -> R_mid.
- right_recovery: full edge is judged larger than R_mid -> R_next.
- both_recovery: both inequalities recover for the same midpoint triple.