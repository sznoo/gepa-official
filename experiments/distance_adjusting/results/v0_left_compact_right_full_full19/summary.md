# Distance prompt recovery eval

- tasks_path: `experiments/distance_adjusting/cache/full19_distance_tasks.jsonl`
- prompt_path: `experiments/distance_adjusting/prompts/distance_prompt_v0.txt`

- n_tasks: 152
- n_midpoint_triples: 76
- left_recovery_rate: 0.6316
- right_recovery_rate: 0.6447
- both_recovery_rate: 0.4342
- mean_recovery_rate: 0.6382
- tie_or_invalid_rate: 0.0724

## Interpretation
- left_recovery: full edge is judged larger than R_i -> R_mid.
- right_recovery: full edge is judged larger than R_mid -> R_next.
- both_recovery: both inequalities recover for the same midpoint triple.