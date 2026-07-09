# Prompt quality pattern report

## Updated instruction summary

| arm | n | mean MR | mean ΔMR | avg generality | avg locality | avg instr len | bad cases | risky-title cases |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | 19 | 0.474 | +0.158 | 3.95 | 3.11 | 1889 | 19 | 1 |
| prompt_update_Rq_full_context_aggregate_steps_4 | 19 | 0.526 | +0.211 | 3.68 | 3.32 | 2019 | 19 | 1 |

## Δp listing summary

| n | mean direct Δp MR | mean direct ΔMR | avg generality | avg locality | avg listing len | bad cases | risky-title cases |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 19 | 0.632 | +0.316 | 3.58 | 4.58 | 10034 | 19 | 1 |

## Pattern frequency in updated instructions

| arm | pattern | count | mean ΔMR when present |
|---|---|---:|---:|
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | preserve_anchor | 18 | +0.167 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | restore_relation_or_type | 19 | +0.158 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | drop_noisy_entity | 19 | +0.158 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | candidate_uncertainty | 13 | +0.231 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | entity_level_over_location_event | 1 | +0.000 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | bm25_interface_guard | 19 | +0.158 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | single_query_guard | 19 | +0.158 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | web_search_drift | 15 | +0.133 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | multi_query_drift | 19 | +0.158 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | query_string_like_delta | 8 | +0.125 |
| prompt_update_Rq_delta_p_only_aggregate_steps_4 | leakage_language | 13 | +0.077 |
| prompt_update_Rq_full_context_aggregate_steps_4 | preserve_anchor | 19 | +0.211 |
| prompt_update_Rq_full_context_aggregate_steps_4 | restore_relation_or_type | 19 | +0.211 |
| prompt_update_Rq_full_context_aggregate_steps_4 | drop_noisy_entity | 19 | +0.211 |
| prompt_update_Rq_full_context_aggregate_steps_4 | candidate_uncertainty | 17 | +0.235 |
| prompt_update_Rq_full_context_aggregate_steps_4 | wrong_candidate_relaxation | 1 | +0.000 |
| prompt_update_Rq_full_context_aggregate_steps_4 | entity_level_over_location_event | 1 | +0.000 |
| prompt_update_Rq_full_context_aggregate_steps_4 | bm25_interface_guard | 19 | +0.211 |
| prompt_update_Rq_full_context_aggregate_steps_4 | single_query_guard | 19 | +0.211 |
| prompt_update_Rq_full_context_aggregate_steps_4 | web_search_drift | 17 | +0.118 |
| prompt_update_Rq_full_context_aggregate_steps_4 | multi_query_drift | 19 | +0.211 |
| prompt_update_Rq_full_context_aggregate_steps_4 | query_string_like_delta | 11 | +0.091 |
| prompt_update_Rq_full_context_aggregate_steps_4 | leakage_language | 15 | +0.267 |

## Pattern frequency in Δp listings

| pattern | count | mean direct ΔMR when present |
|---|---:|---:|
| preserve_anchor | 19 | +0.316 |
| restore_relation_or_type | 19 | +0.316 |
| drop_noisy_entity | 19 | +0.316 |
| candidate_uncertainty | 19 | +0.316 |
| wrong_candidate_relaxation | 3 | +0.000 |
| entity_level_over_location_event | 5 | +0.400 |
| bm25_interface_guard | 19 | +0.316 |
| single_query_guard | 19 | +0.316 |
| web_search_drift | 19 | +0.316 |
| multi_query_drift | 19 | +0.316 |
| query_string_like_delta | 14 | +0.286 |
| leakage_language | 15 | +0.267 |