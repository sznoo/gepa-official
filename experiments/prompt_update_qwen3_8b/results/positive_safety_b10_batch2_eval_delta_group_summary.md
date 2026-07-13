# Qwen positive-safety eval summary

- n_ok: 612
- n_error: 0

## batch2

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| base | 10 | 0.4444 | 0.0444 | 0.3000 | 0.0000 | 0.5500 |
| delta_p_custom_preserve | 10 | 0.4444 | 0.0444 | 0.4000 | 0.0000 | 0.4500 |
| delta_p_custom_signed | 10 | 0.5556 | 0.1556 | 0.4000 | 0.0000 | 0.6000 |
| delta_p_neg_only | 10 | 0.4444 | 0.0444 | 0.3000 | 0.1000 | 0.4500 |

## full143

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| base | 143 | 0.5393 | -0.1705 | 0.6154 | 0.1888 | 0.7098 |
| delta_p_custom_preserve | 143 | 0.5000 | -0.2098 | 0.6014 | 0.1678 | 0.6783 |
| delta_p_custom_signed | 143 | 0.5787 | -0.1311 | 0.6084 | 0.2238 | 0.7133 |
| delta_p_neg_only | 143 | 0.5618 | -0.1480 | 0.5944 | 0.1818 | 0.7203 |
