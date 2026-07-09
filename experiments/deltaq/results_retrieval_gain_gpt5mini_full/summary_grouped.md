# Trace prefixes by step

| key | n | support recall hop2 | missing recovery | any support hit | any missing recovered |
|---|---:|---:|---:|---:|---:|
| trace_step_1 | 19 | 0.474 | 0.289 | 0.737 | 0.316 |
| trace_step_2 | 19 | 0.684 | 0.684 | 0.895 | 0.737 |
| trace_step_3 | 18 | 0.806 | 0.833 | 1.000 | 0.889 |
| trace_step_4 | 12 | 0.833 | 0.917 | 1.000 | 1.000 |

# Trace prefixes by edit type

| key | n | support recall hop2 | missing recovery | any support hit | any missing recovered |
|---|---:|---:|---:|---:|---:|
| add_answer_type | 9 | 0.611 | 0.667 | 0.889 | 0.778 |
| canonicalize_surface_form | 14 | 0.679 | 0.643 | 0.786 | 0.643 |
| compact_query | 12 | 0.625 | 0.583 | 0.833 | 0.667 |
| keep_anchor | 1 | 1.000 | 1.000 | 1.000 | 1.000 |
| remove_noisy_entity | 13 | 0.654 | 0.538 | 0.923 | 0.615 |
| remove_noisy_relation | 8 | 0.812 | 0.875 | 1.000 | 0.875 |
| replace_wrong_focus | 1 | 0.500 | 0.000 | 1.000 | 0.000 |
| restore_missing_anchor | 5 | 0.900 | 0.800 | 1.000 | 0.800 |
| restore_missing_relation | 5 | 0.600 | 0.700 | 1.000 | 0.800 |