# Qwen positive-safety eval summary

- n_ok: 612
- n_error: 0

## batch1

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| base | 10 | 0.3333 | -0.0667 | 0.4000 | 0.0000 | 0.5000 |
| delta_p_custom_preserve | 10 | 0.3889 | -0.0111 | 0.4000 | 0.0000 | 0.5500 |
| delta_p_custom_signed | 10 | 0.5000 | 0.1000 | 0.4000 | 0.0000 | 0.6000 |
| delta_p_neg_only | 10 | 0.6111 | 0.2111 | 0.4000 | 0.1000 | 0.6500 |

## full143

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| base | 143 | 0.5056 | -0.2042 | 0.6154 | 0.1958 | 0.6993 |
| delta_p_custom_preserve | 143 | 0.5000 | -0.2098 | 0.5874 | 0.2028 | 0.6818 |
| delta_p_custom_signed | 143 | 0.4775 | -0.2323 | 0.5734 | 0.1818 | 0.6469 |
| delta_p_neg_only | 143 | 0.5281 | -0.1817 | 0.5804 | 0.1329 | 0.6678 |
