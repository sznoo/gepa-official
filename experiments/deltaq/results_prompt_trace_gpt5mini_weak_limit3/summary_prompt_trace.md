# Prompt trace only

| step | n | support recall hop2 | missing recovery | any support hit | any missing recovered |
|---|---:|---:|---:|---:|---:|
| step_0_p0_generic_rewrite | 3 | 0.000 | 0.000 | 0.000 | 0.000 |
| step_1_p1_compact_keyword | 3 | 0.333 | 0.333 | 0.667 | 0.333 |
| step_2_p2_compact_anchor | 3 | 0.667 | 0.667 | 0.667 | 0.667 |
| step_3_p3_candidate_set | 3 | 0.667 | 0.667 | 1.000 | 0.667 |
| step_4_p4_anchor_relation | 3 | 0.833 | 0.667 | 1.000 | 0.667 |
| step_5_p5_noise_guard | 3 | 0.667 | 1.000 | 1.000 | 1.000 |
| step_6_p6_no_boolean_guard | 3 | 0.500 | 0.333 | 1.000 | 0.333 |