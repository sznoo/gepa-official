# Rq-Grounded DeltaP Aggregation

| arm | n | mean MR | mean hop2 recall | mean recovered |
|---|---:|---:|---:|---:|
| base_existing | 19 | 0.000 | 0.342 | 0.000 |
| delta_p_direct_context_Rq_grounded_steps_4 | 19 | 0.632 | 0.632 | 0.684 |
| prompt_current_query | 19 | 0.316 | 0.474 | 0.368 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | 19 | 0.474 | 0.579 | 0.526 |
| prompt_update_Rq_full_context_aggregate_steps_4 | 19 | 0.526 | 0.605 | 0.579 |
| target_existing | 19 | 0.947 | 0.868 | 1.000 |