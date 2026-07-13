# Qwen positive-safety eval summary

- n_ok: 459
- n_error: 0

## batch1

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| endpoint_delta_custom_preserve | 10 | 0.3333 | -0.0667 | 0.5000 | 0.2000 | 0.5500 |
| endpoint_delta_custom_signed | 10 | 0.3333 | -0.0667 | 0.5000 | 0.2000 | 0.5000 |
| endpoint_delta_neg_only | 10 | 0.4444 | 0.0444 | 0.4000 | 0.0000 | 0.6000 |

## full143

| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |
|---|---:|---:|---:|---:|---:|---:|
| endpoint_delta_custom_preserve | 143 | 0.5562 | -0.1536 | 0.5804 | 0.2308 | 0.7063 |
| endpoint_delta_custom_signed | 143 | 0.5506 | -0.1592 | 0.5804 | 0.2308 | 0.7028 |
| endpoint_delta_neg_only | 143 | 0.5449 | -0.1648 | 0.5874 | 0.2098 | 0.6958 |
