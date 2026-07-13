# Distance prompt recovery eval

- tasks_path: `experiments/distance_adjusting/cache/tmp_2_feedback_distance_tasks.jsonl`
- prompt_path: `experiments/distance_adjusting/prompts/feedback_distance_prompt_v0.txt`

- n_tasks: 2
- n_midpoint_triples: 1
- left_recovery_rate: 1.0000
- right_recovery_rate: 1.0000
- both_recovery_rate: 1.0000
- mean_recovery_rate: 1.0000
- tie_or_invalid_rate: 0.0000

## Interpretation
- left_recovery: full edge is judged larger than R_i -> R_mid.
- right_recovery: full edge is judged larger than R_mid -> R_next.
- both_recovery: both inequalities recover for the same midpoint triple.