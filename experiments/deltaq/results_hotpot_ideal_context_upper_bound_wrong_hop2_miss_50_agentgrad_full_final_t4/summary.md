# Ideal context upper-bound summary

Selected examples: 41


## By arm

| arm | n | EM | total recall | hop2 recall | MR | hop2 hit | new hit | retrieval fail | corrected | ret improved | ret improved final wrong |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| answer_aware_ideal_delta | 41 | 0.195 | 0.720 | 0.646 | 0.537 | 0.902 | 0.585 | 0.049 | 0.195 | 0.537 | 0.366 |
| baseline_cached | 41 | 0.000 | 0.415 | 0.305 | 0.085 | 0.610 | 0.171 | 0.171 | 0.000 | 0.000 | 0.000 |
| baseline_recomputed | 41 | 0.024 | 0.415 | 0.305 | 0.085 | 0.610 | 0.171 | 0.171 | 0.024 | 0.000 | 0.000 |
| r6_global | 41 | 0.098 | 0.488 | 0.402 | 0.232 | 0.634 | 0.293 | 0.195 | 0.098 | 0.195 | 0.122 |
| support_aware_ideal_delta | 41 | 0.146 | 0.707 | 0.634 | 0.524 | 0.854 | 0.585 | 0.049 | 0.146 | 0.463 | 0.390 |
| support_title_ceiling | 41 | 0.122 | 0.671 | 0.561 | 0.476 | 0.854 | 0.561 | 0.049 | 0.122 | 0.439 | 0.341 |

## Interpretation handles

- `corrected`: baseline cached answer was wrong, but this arm is correct.
- `ret improved`: total support recall is higher than baseline cached.
- `ret improved final wrong`: retrieval improved but final answer remains wrong.