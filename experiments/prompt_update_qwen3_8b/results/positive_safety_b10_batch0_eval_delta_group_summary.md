# Qwen positive-safety eval summary

- n_ok: 612
- n_error: 0

## batch0

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| base | 10 | 0.2857 | -0.1143 | 0.5000 | 0.2000 | 0.6000 |
| delta_p_custom_preserve | 10 | 0.3571 | -0.0429 | 0.4000 | 0.1000 | 0.6000 |
| delta_p_custom_signed | 10 | 0.5714 | 0.1714 | 0.4000 | 0.2000 | 0.6500 |
| delta_p_neg_only | 10 | 0.2857 | -0.1143 | 0.5000 | 0.2000 | 0.6500 |

## full143

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| base | 143 | 0.5169 | -0.1929 | 0.5524 | 0.2028 | 0.6853 |
| delta_p_custom_preserve | 143 | 0.5225 | -0.1873 | 0.5874 | 0.2168 | 0.7343 |
| delta_p_custom_signed | 143 | 0.5618 | -0.1480 | 0.5944 | 0.1818 | 0.6713 |
| delta_p_neg_only | 143 | 0.5843 | -0.1255 | 0.5874 | 0.1958 | 0.6923 |
