# Trace-SGD independent one-step summary

| batch_id | selected | eligible | batch acc | batch flip | batch break | batch net | full acc | full flip | full break | full net | selected rank by actual net |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | quote_and_alternate_spellings | 1 | 0.400→0.500 | 1 | 0 | 1 | 0.476→0.476 | 3 | 3 | 0 | 2 |
| 1 | place_alias_and_date_variants | 1 | 0.500→0.600 | 1 | 0 | 1 | 0.476→0.488 | 5 | 4 | 1 | 1 |
| 2 | use_or_quotes_for_variants | 1 | 0.500→0.500 | 0 | 0 | 0 | 0.476→0.500 | 2 | 0 | 2 | 3 |

## Aggregate

- trials: 3
- mean batch Δacc: +0.067
- mean batch net gain: +0.667
- mean full Δacc: +0.012
- mean full net gain: +1.000
- positive batch net trials: 2 / 3
- nonnegative full net trials: 3 / 3