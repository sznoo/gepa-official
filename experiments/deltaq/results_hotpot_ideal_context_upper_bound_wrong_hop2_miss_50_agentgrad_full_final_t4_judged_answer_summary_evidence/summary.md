# LLM judge summary

Judged rows: 246
Scopes: answer, summary, evidence

| arm | n | strict EM | relaxed EM | LLM ans | LLM corrected | sum2 gold str | summary suff | summary partial+ | summary suff but EM0 | evidence suff | evidence partial+ | evidence suff but EM0 | total recall | MR | ret improved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| answer_aware_ideal_delta | 41 | 0.195 | 0.220 | 0.659 | 0.293 | 0.707 | 0.817 | 0.854 | 0.585 | 0.866 | 0.927 | 0.634 | 0.720 | 0.537 | 0.537 |
| baseline_cached | 41 | 0.000 | 0.000 | 0.366 | 0.000 | 0.366 | 0.537 | 0.610 | 0.463 | 0.537 | 0.634 | 0.439 | 0.415 | 0.085 | 0.000 |
| baseline_recomputed | 41 | 0.024 | 0.024 | 0.390 | 0.049 | 0.366 | 0.524 | 0.585 | 0.463 | 0.561 | 0.683 | 0.415 | 0.415 | 0.085 | 0.000 |
| r6_global | 41 | 0.098 | 0.098 | 0.463 | 0.122 | 0.439 | 0.573 | 0.610 | 0.439 | 0.598 | 0.634 | 0.488 | 0.488 | 0.232 | 0.195 |
| support_aware_ideal_delta | 41 | 0.146 | 0.171 | 0.561 | 0.195 | 0.634 | 0.756 | 0.829 | 0.537 | 0.829 | 0.878 | 0.659 | 0.707 | 0.524 | 0.463 |
| support_title_ceiling | 41 | 0.122 | 0.122 | 0.512 | 0.146 | 0.683 | 0.695 | 0.732 | 0.537 | 0.780 | 0.878 | 0.561 | 0.671 | 0.476 | 0.439 |

## Summary judge failure types

| arm | failure_type | n |
|---|---|---:|
| answer_aware_ideal_delta | answer_string_present_but_relation_missing | 2 |
| answer_aware_ideal_delta | not_supported | 5 |
| answer_aware_ideal_delta | partial_bridge_missing | 1 |
| answer_aware_ideal_delta | sufficient | 32 |
| answer_aware_ideal_delta | wrong_granularity | 1 |
| baseline_cached | answer_string_present_but_relation_missing | 3 |
| baseline_cached | not_supported | 15 |
| baseline_cached | partial_bridge_missing | 4 |
| baseline_cached | sufficient | 19 |
| baseline_recomputed | answer_string_present_but_relation_missing | 2 |
| baseline_recomputed | not_supported | 17 |
| baseline_recomputed | partial_bridge_missing | 3 |
| baseline_recomputed | sufficient | 19 |
| r6_global | not_supported | 16 |
| r6_global | partial_bridge_missing | 3 |
| r6_global | sufficient | 22 |
| support_aware_ideal_delta | answer_string_present_but_relation_missing | 3 |
| support_aware_ideal_delta | not_supported | 6 |
| support_aware_ideal_delta | partial_bridge_missing | 4 |
| support_aware_ideal_delta | sufficient | 28 |
| support_title_ceiling | answer_string_present_but_relation_missing | 4 |
| support_title_ceiling | not_supported | 8 |
| support_title_ceiling | partial_bridge_missing | 2 |
| support_title_ceiling | sufficient | 27 |

## Answer judge categories

| arm | category | n |
|---|---|---:|
| answer_aware_ideal_delta | alias | 8 |
| answer_aware_ideal_delta | exact_or_format | 19 |
| answer_aware_ideal_delta | insufficient_information | 8 |
| answer_aware_ideal_delta | related_but_wrong | 1 |
| answer_aware_ideal_delta | too_broad | 1 |
| answer_aware_ideal_delta | wrong | 4 |
| baseline_cached | alias | 6 |
| baseline_cached | exact_or_format | 9 |
| baseline_cached | insufficient_information | 12 |
| baseline_cached | related_but_wrong | 1 |
| baseline_cached | too_broad | 1 |
| baseline_cached | wrong | 12 |
| baseline_recomputed | alias | 6 |
| baseline_recomputed | exact_or_format | 10 |
| baseline_recomputed | insufficient_information | 15 |
| baseline_recomputed | related_but_wrong | 2 |
| baseline_recomputed | too_broad | 2 |
| baseline_recomputed | wrong | 6 |
| r6_global | alias | 5 |
| r6_global | exact_or_format | 14 |
| r6_global | insufficient_information | 13 |
| r6_global | related_but_wrong | 3 |
| r6_global | too_broad | 1 |
| r6_global | wrong | 5 |
| support_aware_ideal_delta | alias | 7 |
| support_aware_ideal_delta | exact_or_format | 16 |
| support_aware_ideal_delta | insufficient_information | 10 |
| support_aware_ideal_delta | related_but_wrong | 2 |
| support_aware_ideal_delta | too_broad | 1 |
| support_aware_ideal_delta | wrong | 5 |
| support_title_ceiling | alias | 7 |
| support_title_ceiling | exact_or_format | 14 |
| support_title_ceiling | insufficient_information | 15 |
| support_title_ceiling | related_but_wrong | 2 |
| support_title_ceiling | too_broad | 1 |
| support_title_ceiling | wrong | 2 |