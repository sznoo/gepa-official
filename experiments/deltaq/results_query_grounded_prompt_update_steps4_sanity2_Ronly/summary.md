# Query-Grounded Prompt Update from Generated R-Trace

| arm | n | mean MR | mean hop2 recall | mean recovered |
|---|---:|---:|---:|---:|
| base_existing | 2 | 0.000 | 0.250 | 0.000 |
| deltaq_direct_context_onecall_steps_4 | 2 | 0.500 | 0.500 | 0.500 |
| deltaq_direct_context_twoturn_steps_4 | 2 | 0.500 | 0.500 | 0.500 |
| prompt_current_query | 2 | 0.000 | 0.250 | 0.000 |
| prompt_update_onecall_R_to_q_to_p_steps_4 | 2 | 1.000 | 0.750 | 1.000 |
| prompt_update_twoturn_R_to_q_then_p_steps_4 | 2 | 0.500 | 0.500 | 0.500 |
| target_existing | 2 | 1.000 | 1.000 | 1.000 |