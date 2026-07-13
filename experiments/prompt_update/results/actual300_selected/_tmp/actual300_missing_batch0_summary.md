# Positive Safety Batch0 Evaluation

- n_ok: 924
- n_error: 0

## Scope: full143

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 154 |  | 0.7370 | 0.2208 | 0.7987 |
| delta_p_custom_signed | 154 |  | 0.7630 | 0.2143 | 0.7922 |
| delta_p_neg_only | 154 |  | 0.7273 | 0.2468 | 0.7922 |
| endpoint_delta_contrastive_raw_C | 154 |  | 0.6981 | 0.2273 | 0.7987 |
| endpoint_delta_custom_signed | 154 |  | 0.7240 | 0.2338 | 0.7857 |
| endpoint_delta_neg_only | 154 |  | 0.7305 | 0.2532 | 0.7987 |

### Strong flip vs base: full143

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 154 | 0 | 0 | 123 | 31 | 0 | 0.0000 |
| delta_p_custom_signed | 154 | 3 | 4 | 119 | 28 | -1 | 0.0455 |
| delta_p_neg_only | 154 | 3 | 4 | 119 | 28 | -1 | 0.0455 |
| endpoint_delta_contrastive_raw_C | 154 | 3 | 3 | 120 | 28 | 0 | 0.0390 |
| endpoint_delta_custom_signed | 154 | 2 | 4 | 119 | 29 | -2 | 0.0390 |
| endpoint_delta_neg_only | 154 | 6 | 6 | 117 | 25 | 0 | 0.0779 |

### Bucket strong_EM: full143

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 122 | 0.9754 |  |
| base | W_other | 32 | 0.1250 |  |
| delta_p_custom_signed | C_clean | 122 | 0.9590 |  |
| delta_p_custom_signed | W_other | 32 | 0.1562 |  |
| delta_p_neg_only | C_clean | 122 | 0.9508 |  |
| delta_p_neg_only | W_other | 32 | 0.1875 |  |
| endpoint_delta_contrastive_raw_C | C_clean | 122 | 0.9754 |  |
| endpoint_delta_contrastive_raw_C | W_other | 32 | 0.1250 |  |
| endpoint_delta_custom_signed | C_clean | 122 | 0.9590 |  |
| endpoint_delta_custom_signed | W_other | 32 | 0.1250 |  |
| endpoint_delta_neg_only | C_clean | 122 | 0.9508 |  |
| endpoint_delta_neg_only | W_other | 32 | 0.2188 |  |
