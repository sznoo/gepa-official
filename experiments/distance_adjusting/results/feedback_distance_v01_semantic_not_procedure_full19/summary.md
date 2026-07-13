# Distance prompt recovery eval

- tasks_path: `experiments/distance_adjusting/cache/full19_feedback_distance_tasks.jsonl`
- prompt_path: `experiments/distance_adjusting/prompts/feedback_distance_prompt_v01_semantic_not_procedure.txt`

- n_tasks: 152
- n_midpoint_triples: 76
- left_recovery_rate: 0.5526
- right_recovery_rate: 0.3158
- both_recovery_rate: 0.1842
- mean_recovery_rate: 0.4342
- tie_or_invalid_rate: 0.3158

## Interpretation
- left_recovery: full edge is judged larger than R_i -> R_mid.
- right_recovery: full edge is judged larger than R_mid -> R_next.
- both_recovery: both inequalities recover for the same midpoint triple.