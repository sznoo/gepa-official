# Ideal context upper-bound summary

Selected examples: 5


## By arm

| arm | n | EM | total recall | hop2 recall | MR | hop2 hit | new hit | retrieval fail | corrected | ret improved | ret improved final wrong |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| answer_aware_ideal_delta | 5 | 0.000 | 0.800 | 0.500 | 0.600 | 0.800 | 0.600 | 0.000 | 0.000 | 0.600 | 0.600 |
| baseline_cached | 5 | 0.000 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| r6_global | 5 | 0.000 | 0.500 | 0.100 | 0.000 | 0.200 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| support_aware_ideal_delta | 5 | 0.000 | 0.700 | 0.500 | 0.400 | 0.800 | 0.400 | 0.000 | 0.000 | 0.400 | 0.400 |
| support_title_ceiling | 5 | 0.000 | 0.800 | 0.300 | 0.600 | 0.600 | 0.600 | 0.000 | 0.000 | 0.600 | 0.600 |

## Interpretation handles

- `corrected`: baseline cached answer was wrong, but this arm is correct.
- `ret improved`: total support recall is higher than baseline cached.
- `ret improved final wrong`: retrieval improved but final answer remains wrong.