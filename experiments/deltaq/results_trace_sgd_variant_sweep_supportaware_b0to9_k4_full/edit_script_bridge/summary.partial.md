# Trace-SGD independent one-step summary

| batch_id | selected | eligible | batch acc | batch flip | batch break | batch net | full acc | full flip | full break | full net | selected rank by actual net |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | ordinal_release_discography_bridge | 1 | 0.400→0.500 | 1 | 0 | 1 | 0.476→0.512 | 3 | 0 | 3 | 1 |
| 1 | restore_bridge_relation_tokens | 1 | 0.500→0.500 | 0 | 0 | 0 | 0.476→0.500 | 3 | 1 | 2 | 1 |
| 2 | last_assignment_station_bridge | 1 | 0.500→0.500 | 0 | 0 | 0 | 0.476→0.488 | 1 | 0 | 1 | 2 |
| 3 | restore_term_etymology_bridge | 1 | 0.500→0.500 | 0 | 0 | 0 | 0.476→0.488 | 2 | 1 | 1 | 1 |
| 4 | promote_list_page_candidates_for_name_requests | 1 | 0.500→0.500 | 0 | 0 | 0 | 0.476→0.476 | 3 | 3 | 0 | 3 |
| 5 | restore_usage_and_credit_cues_for_type_of_used_item | 1 | 0.500→0.400 | 0 | 1 | -1 | 0.476→0.476 | 2 | 2 | 0 | 2 |
| 6 | conjoin_entities_with_relation_token_for_shared_attribute | 1 | 0.500→0.500 | 0 | 0 | 0 | 0.476→0.488 | 2 | 1 | 1 | 3 |
| 7 | restore_missing_bridge_relation | 1 | 0.400→0.400 | 0 | 0 | 0 | 0.476→0.476 | 2 | 2 | 0 | 1 |
| 8 | drop_noisy_side_entities | 1 | 0.400→0.300 | 0 | 1 | -1 | 0.476→0.451 | 1 | 3 | -2 | 3 |
| 9 | work_title_bridge_tag | 1 | 0.500→0.600 | 1 | 0 | 1 | 0.476→0.488 | 2 | 1 | 1 | 1 |

## Aggregate

- trials: 10
- mean batch Δacc: -0.000
- mean batch net gain: +0.000
- mean full Δacc: +0.009
- mean full net gain: +0.700
- positive batch net trials: 2 / 10
- nonnegative full net trials: 9 / 10