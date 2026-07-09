# LLM judge summary

Judged rows: 30
Scopes: answer, summary, evidence

| arm | n | strict EM | relaxed EM | LLM ans | LLM corrected | sum2 gold str | summary suff | summary partial+ | summary suff but EM0 | evidence suff | evidence partial+ | evidence suff but EM0 | total recall | MR | ret improved |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| answer_aware_ideal_delta | 5 | 0.000 | 0.200 | 0.600 | 0.200 | 0.800 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.800 | 0.600 | 0.600 |
| baseline_cached | 5 | 0.000 | 0.000 | 0.400 | 0.000 | 0.200 | 0.600 | 0.600 | 0.600 | 0.600 | 0.600 | 0.600 | 0.500 | 0.000 | 0.000 |
| baseline_recomputed | 5 | 0.000 | 0.000 | 0.400 | 0.000 | 0.200 | 0.600 | 0.600 | 0.600 | 0.600 | 0.600 | 0.600 | 0.500 | 0.000 | 0.000 |
| r6_global | 5 | 0.000 | 0.000 | 0.400 | 0.000 | 0.200 | 0.600 | 0.600 | 0.600 | 0.700 | 0.800 | 0.600 | 0.500 | 0.000 | 0.000 |
| support_aware_ideal_delta | 5 | 0.000 | 0.200 | 0.600 | 0.200 | 0.600 | 0.800 | 0.800 | 0.800 | 0.800 | 0.800 | 0.800 | 0.700 | 0.400 | 0.400 |
| support_title_ceiling | 5 | 0.000 | 0.000 | 0.400 | 0.000 | 0.400 | 0.800 | 0.800 | 0.800 | 0.800 | 0.800 | 0.800 | 0.800 | 0.600 | 0.600 |

## Summary judge failure types

| arm | failure_type | n |
|---|---|---:|
| answer_aware_ideal_delta | sufficient | 5 |
| baseline_cached | not_supported | 2 |
| baseline_cached | sufficient | 3 |
| baseline_recomputed | not_supported | 2 |
| baseline_recomputed | sufficient | 3 |
| r6_global | not_supported | 2 |
| r6_global | sufficient | 3 |
| support_aware_ideal_delta | not_supported | 1 |
| support_aware_ideal_delta | sufficient | 4 |
| support_title_ceiling | not_supported | 1 |
| support_title_ceiling | sufficient | 4 |

## Answer judge categories

| arm | category | n |
|---|---|---:|
| answer_aware_ideal_delta | alias | 1 |
| answer_aware_ideal_delta | exact_or_format | 2 |
| answer_aware_ideal_delta | insufficient_information | 1 |
| answer_aware_ideal_delta | too_broad | 1 |
| baseline_cached | alias | 1 |
| baseline_cached | exact_or_format | 1 |
| baseline_cached | insufficient_information | 1 |
| baseline_cached | too_broad | 1 |
| baseline_cached | wrong | 1 |
| baseline_recomputed | alias | 1 |
| baseline_recomputed | exact_or_format | 1 |
| baseline_recomputed | insufficient_information | 1 |
| baseline_recomputed | too_broad | 1 |
| baseline_recomputed | wrong | 1 |
| r6_global | alias | 1 |
| r6_global | exact_or_format | 1 |
| r6_global | insufficient_information | 1 |
| r6_global | too_broad | 1 |
| r6_global | wrong | 1 |
| support_aware_ideal_delta | alias | 1 |
| support_aware_ideal_delta | exact_or_format | 2 |
| support_aware_ideal_delta | too_broad | 1 |
| support_aware_ideal_delta | wrong | 1 |
| support_title_ceiling | alias | 1 |
| support_title_ceiling | exact_or_format | 1 |
| support_title_ceiling | insufficient_information | 2 |
| support_title_ceiling | too_broad | 1 |