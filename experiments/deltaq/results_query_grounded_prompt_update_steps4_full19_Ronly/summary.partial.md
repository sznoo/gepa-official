# Query-Grounded Prompt Update from Generated R-Trace

| arm | n | mean MR | mean hop2 recall | mean recovered |
|---|---:|---:|---:|---:|
| base_existing | 19 | 0.000 | 0.342 | 0.000 |
| deltaq_direct_context_onecall_steps_4 | 19 | 0.447 | 0.553 | 0.526 |
| deltaq_direct_context_twoturn_steps_4 | 19 | 0.526 | 0.579 | 0.579 |
| prompt_current_query | 19 | 0.579 | 0.579 | 0.632 |
| prompt_update_onecall_R_to_q_to_p_steps_4 | 19 | 0.447 | 0.526 | 0.526 |
| prompt_update_twoturn_R_to_q_then_p_steps_4 | 19 | 0.447 | 0.526 | 0.474 |
| target_existing | 19 | 0.947 | 0.868 | 1.000 |