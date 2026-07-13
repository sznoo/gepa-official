# Positive Safety Batch0 Evaluation

- n_ok: 924
- n_error: 0

## Scope: full143

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 154 |  | 0.7370 | 0.2468 | 0.7857 |
| delta_p_custom_signed | 154 |  | 0.6851 | 0.2208 | 0.7727 |
| delta_p_neg_only | 154 |  | 0.7370 | 0.2727 | 0.7922 |
| endpoint_delta_contrastive_raw_C | 154 |  | 0.7208 | 0.2338 | 0.7857 |
| endpoint_delta_custom_signed | 154 |  | 0.7143 | 0.2338 | 0.8052 |
| endpoint_delta_neg_only | 154 |  | 0.6558 | 0.2338 | 0.7792 |

### Strong flip vs base: full143

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 154 | 0 | 0 | 121 | 33 | 0 | 0.0000 |
| delta_p_custom_signed | 154 | 5 | 7 | 114 | 28 | -2 | 0.0779 |
| delta_p_neg_only | 154 | 3 | 2 | 119 | 30 | 1 | 0.0325 |
| endpoint_delta_contrastive_raw_C | 154 | 4 | 4 | 117 | 29 | 0 | 0.0519 |
| endpoint_delta_custom_signed | 154 | 4 | 1 | 120 | 29 | 3 | 0.0325 |
| endpoint_delta_neg_only | 154 | 4 | 5 | 116 | 29 | -1 | 0.0584 |

### Bucket strong_EM: full143

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 121 | 0.9669 |  |
| base | W_other | 33 | 0.1212 |  |
| delta_p_custom_signed | C_clean | 121 | 0.9339 |  |
| delta_p_custom_signed | W_other | 33 | 0.1818 |  |
| delta_p_neg_only | C_clean | 121 | 0.9752 |  |
| delta_p_neg_only | W_other | 33 | 0.1212 |  |
| endpoint_delta_contrastive_raw_C | C_clean | 121 | 0.9752 |  |
| endpoint_delta_contrastive_raw_C | W_other | 33 | 0.0909 |  |
| endpoint_delta_custom_signed | C_clean | 121 | 0.9752 |  |
| endpoint_delta_custom_signed | W_other | 33 | 0.1818 |  |
| endpoint_delta_neg_only | C_clean | 121 | 0.9504 |  |
| endpoint_delta_neg_only | W_other | 33 | 0.1515 |  |
