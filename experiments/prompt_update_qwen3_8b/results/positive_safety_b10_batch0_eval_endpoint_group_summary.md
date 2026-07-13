# Qwen positive-safety eval summary

- n_ok: 459
- n_error: 0

## batch0

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| endpoint_delta_custom_preserve | 10 | 0.4286 | 0.0286 | 0.4000 | 0.2000 | 0.6500 |
| endpoint_delta_custom_signed | 10 | 0.2857 | -0.1143 | 0.5000 | 0.2000 | 0.5500 |
| endpoint_delta_neg_only | 10 | 0.4286 | 0.0286 | 0.5000 | 0.2000 | 0.6000 |

## full143

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| endpoint_delta_custom_preserve | 143 | 0.5337 | -0.1761 | 0.6084 | 0.2238 | 0.7028 |
| endpoint_delta_custom_signed | 143 | 0.5000 | -0.2098 | 0.6014 | 0.1818 | 0.6573 |
| endpoint_delta_neg_only | 143 | 0.5000 | -0.2098 | 0.5944 | 0.2028 | 0.6713 |
