# Qwen positive-safety eval summary

- n_ok: 459
- n_error: 0

## batch2

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| endpoint_delta_custom_preserve | 10 | 0.5556 | 0.1556 | 0.5000 | 0.0000 | 0.5000 |
| endpoint_delta_custom_signed | 10 | 0.4444 | 0.0444 | 0.4000 | 0.1000 | 0.4500 |
| endpoint_delta_neg_only | 10 | 0.4444 | 0.0444 | 0.4000 | 0.1000 | 0.5000 |

## full143

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| endpoint_delta_custom_preserve | 143 | 0.5225 | -0.1873 | 0.5944 | 0.2308 | 0.6573 |
| endpoint_delta_custom_signed | 143 | 0.5337 | -0.1761 | 0.5944 | 0.1958 | 0.6364 |
| endpoint_delta_neg_only | 143 | 0.5000 | -0.2098 | 0.5734 | 0.1958 | 0.6503 |
