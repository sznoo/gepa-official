# Trace-SGD independent one-step summary

| batch_id | selected | eligible | batch acc | batch flip | batch break | batch net | full acc | full flip | full break | full net | selected rank by actual net |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | combined_shared_cast_clause_for_pairwise_comparisons | 1 | 0.400→0.500 | 1 | 0 | 1 | 0.476→0.476 | 2 | 2 | 0 | 2 |
| 1 | explicit_alias_or_quote_on_alias_request | 1 | 0.500→0.500 | 0 | 0 | 0 | 0.476→0.488 | 4 | 3 | 1 | 2 |
| 2 | numeric_unit_exact_and_abbrev_gate | 1 | 0.500→0.500 | 0 | 0 | 0 | 0.476→0.476 | 1 | 1 | 0 | 3 |

## Aggregate

- trials: 3
- mean batch Δacc: +0.033
- mean batch net gain: +0.333
- mean full Δacc: +0.004
- mean full net gain: +0.333
- positive batch net trials: 1 / 3
- nonnegative full net trials: 3 / 3