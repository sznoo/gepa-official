# Positive Safety Batch0 Evaluation

- n_ok: 918
- n_error: 0

## Scope: full143

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 153 |  | 0.7451 | 0.2680 | 0.7647 |
| delta_p_custom_signed | 153 |  | 0.8105 | 0.2549 | 0.7843 |
| delta_p_neg_only | 153 |  | 0.7157 | 0.2549 | 0.7843 |
| endpoint_delta_contrastive_raw_C | 153 |  | 0.7190 | 0.2157 | 0.7843 |
| endpoint_delta_custom_signed | 153 |  | 0.7908 | 0.2288 | 0.7974 |
| endpoint_delta_neg_only | 153 |  | 0.7320 | 0.2418 | 0.7843 |

### Strong flip vs base: full143

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 153 | 0 | 0 | 117 | 36 | 0 | 0.0000 |
| delta_p_custom_signed | 153 | 8 | 5 | 112 | 28 | 3 | 0.0850 |
| delta_p_neg_only | 153 | 7 | 4 | 113 | 29 | 3 | 0.0719 |
| endpoint_delta_contrastive_raw_C | 153 | 6 | 3 | 114 | 30 | 3 | 0.0588 |
| endpoint_delta_custom_signed | 153 | 7 | 2 | 115 | 29 | 5 | 0.0588 |
| endpoint_delta_neg_only | 153 | 8 | 5 | 112 | 28 | 3 | 0.0850 |

### Bucket strong_EM: full143

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 121 | 0.9339 |  |
| base | W_other | 32 | 0.1250 |  |
| delta_p_custom_signed | C_clean | 121 | 0.9587 |  |
| delta_p_custom_signed | W_other | 32 | 0.1250 |  |
| delta_p_neg_only | C_clean | 121 | 0.9587 |  |
| delta_p_neg_only | W_other | 32 | 0.1250 |  |
| endpoint_delta_contrastive_raw_C | C_clean | 121 | 0.9587 |  |
| endpoint_delta_contrastive_raw_C | W_other | 32 | 0.1250 |  |
| endpoint_delta_custom_signed | C_clean | 121 | 0.9504 |  |
| endpoint_delta_custom_signed | W_other | 32 | 0.2188 |  |
| endpoint_delta_neg_only | C_clean | 121 | 0.9587 |  |
| endpoint_delta_neg_only | W_other | 32 | 0.1250 |  |
