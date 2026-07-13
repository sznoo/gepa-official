# Positive Safety Batch0 Evaluation

- n_ok: 70
- n_error: 0

## Scope: batch0

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 10 |  | 0.5500 | 0.2000 | 0.5000 |
| delta_p_custom_preserve | 10 |  | 0.5500 | 0.2000 | 0.5000 |
| delta_p_custom_signed | 10 |  | 0.6500 | 0.1000 | 0.5000 |
| delta_p_neg_only | 10 |  | 0.6000 | 0.2000 | 0.5000 |
| endpoint_delta_custom_preserve | 10 |  | 0.5500 | 0.2000 | 0.6000 |
| endpoint_delta_custom_signed | 10 |  | 0.6000 | 0.2000 | 0.5000 |
| endpoint_delta_neg_only | 10 |  | 0.5500 | 0.0000 | 0.6000 |

### Strong flip vs base: batch0

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |
| delta_p_custom_preserve | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |
| delta_p_custom_signed | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |
| delta_p_neg_only | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |
| endpoint_delta_custom_preserve | 10 | 1 | 0 | 5 | 4 | 1 | 0.1000 |
| endpoint_delta_custom_signed | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |
| endpoint_delta_neg_only | 10 | 1 | 0 | 5 | 4 | 1 | 0.1000 |

### Bucket strong_EM: batch0

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 3 | 1.0000 |  |
| base | C_fragile | 1 | 1.0000 |  |
| base | W_other | 1 | 0.0000 |  |
| base | W_retrieval | 5 | 0.2000 |  |
| delta_p_custom_preserve | C_clean | 3 | 1.0000 |  |
| delta_p_custom_preserve | C_fragile | 1 | 1.0000 |  |
| delta_p_custom_preserve | W_other | 1 | 0.0000 |  |
| delta_p_custom_preserve | W_retrieval | 5 | 0.2000 |  |
| delta_p_custom_signed | C_clean | 3 | 1.0000 |  |
| delta_p_custom_signed | C_fragile | 1 | 1.0000 |  |
| delta_p_custom_signed | W_other | 1 | 0.0000 |  |
| delta_p_custom_signed | W_retrieval | 5 | 0.2000 |  |
| delta_p_neg_only | C_clean | 3 | 1.0000 |  |
| delta_p_neg_only | C_fragile | 1 | 1.0000 |  |
| delta_p_neg_only | W_other | 1 | 0.0000 |  |
| delta_p_neg_only | W_retrieval | 5 | 0.2000 |  |
| endpoint_delta_custom_preserve | C_clean | 3 | 1.0000 |  |
| endpoint_delta_custom_preserve | C_fragile | 1 | 1.0000 |  |
| endpoint_delta_custom_preserve | W_other | 1 | 0.0000 |  |
| endpoint_delta_custom_preserve | W_retrieval | 5 | 0.4000 |  |
| endpoint_delta_custom_signed | C_clean | 3 | 1.0000 |  |
| endpoint_delta_custom_signed | C_fragile | 1 | 1.0000 |  |
| endpoint_delta_custom_signed | W_other | 1 | 0.0000 |  |
| endpoint_delta_custom_signed | W_retrieval | 5 | 0.2000 |  |
| endpoint_delta_neg_only | C_clean | 3 | 1.0000 |  |
| endpoint_delta_neg_only | C_fragile | 1 | 1.0000 |  |
| endpoint_delta_neg_only | W_other | 1 | 0.0000 |  |
| endpoint_delta_neg_only | W_retrieval | 5 | 0.4000 |  |
