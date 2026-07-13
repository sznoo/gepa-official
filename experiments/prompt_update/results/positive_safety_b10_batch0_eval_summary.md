# Positive Safety Batch0 Evaluation

- n_ok: 1376
- n_error: 1

## Scope: batch0

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 10 | 0.0000 | 0.5500 | 0.2000 | 0.5000 |
| delta_p_contrastive_raw_C | 10 | 0.0000 | 0.5500 | 0.2000 | 0.5000 |
| delta_p_custom_preserve | 10 | 0.1667 | 0.6500 | 0.1000 | 0.5000 |
| delta_p_custom_signed | 10 | 0.0000 | 0.5500 | 0.2000 | 0.4000 |
| delta_p_neg_only | 10 | 0.0000 | 0.5500 | 0.1000 | 0.6000 |
| endpoint_delta_contrastive_raw_C | 10 | 0.1667 | 0.5000 | 0.1000 | 0.4000 |
| endpoint_delta_custom_preserve | 10 | 0.3333 | 0.5000 | 0.1000 | 0.5000 |
| endpoint_delta_custom_signed | 10 | 0.3333 | 0.6000 | 0.2000 | 0.5000 |
| endpoint_delta_neg_only | 10 | 0.1667 | 0.4500 | 0.2000 | 0.5000 |

### Strong flip vs base: batch0

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |
| delta_p_contrastive_raw_C | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |
| delta_p_custom_preserve | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |
| delta_p_custom_signed | 10 | 0 | 1 | 4 | 5 | -1 | 0.1000 |
| delta_p_neg_only | 10 | 1 | 0 | 5 | 4 | 1 | 0.1000 |
| endpoint_delta_contrastive_raw_C | 10 | 0 | 1 | 4 | 5 | -1 | 0.1000 |
| endpoint_delta_custom_preserve | 10 | 1 | 1 | 4 | 4 | 0 | 0.2000 |
| endpoint_delta_custom_signed | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |
| endpoint_delta_neg_only | 10 | 0 | 0 | 5 | 5 | 0 | 0.0000 |

### Bucket strong_EM: batch0

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 3 | 1.0000 |  |
| base | C_fragile | 1 | 1.0000 | 0.0000 |
| base | W_other | 1 | 0.0000 |  |
| base | W_retrieval | 5 | 0.2000 | 0.0000 |
| delta_p_contrastive_raw_C | C_clean | 3 | 1.0000 |  |
| delta_p_contrastive_raw_C | C_fragile | 1 | 1.0000 | 0.0000 |
| delta_p_contrastive_raw_C | W_other | 1 | 0.0000 |  |
| delta_p_contrastive_raw_C | W_retrieval | 5 | 0.2000 | 0.0000 |
| delta_p_custom_preserve | C_clean | 3 | 1.0000 |  |
| delta_p_custom_preserve | C_fragile | 1 | 1.0000 | 1.0000 |
| delta_p_custom_preserve | W_other | 1 | 0.0000 |  |
| delta_p_custom_preserve | W_retrieval | 5 | 0.2000 | 0.0000 |
| delta_p_custom_signed | C_clean | 3 | 1.0000 |  |
| delta_p_custom_signed | C_fragile | 1 | 1.0000 | 0.0000 |
| delta_p_custom_signed | W_other | 1 | 0.0000 |  |
| delta_p_custom_signed | W_retrieval | 5 | 0.0000 | 0.0000 |
| delta_p_neg_only | C_clean | 3 | 1.0000 |  |
| delta_p_neg_only | C_fragile | 1 | 1.0000 | 0.0000 |
| delta_p_neg_only | W_other | 1 | 0.0000 |  |
| delta_p_neg_only | W_retrieval | 5 | 0.4000 | 0.0000 |
| endpoint_delta_contrastive_raw_C | C_clean | 3 | 0.6667 |  |
| endpoint_delta_contrastive_raw_C | C_fragile | 1 | 1.0000 | 0.0000 |
| endpoint_delta_contrastive_raw_C | W_other | 1 | 0.0000 |  |
| endpoint_delta_contrastive_raw_C | W_retrieval | 5 | 0.2000 | 0.2000 |
| endpoint_delta_custom_preserve | C_clean | 3 | 1.0000 |  |
| endpoint_delta_custom_preserve | C_fragile | 1 | 1.0000 | 1.0000 |
| endpoint_delta_custom_preserve | W_other | 1 | 0.0000 |  |
| endpoint_delta_custom_preserve | W_retrieval | 5 | 0.2000 | 0.2000 |
| endpoint_delta_custom_signed | C_clean | 3 | 1.0000 |  |
| endpoint_delta_custom_signed | C_fragile | 1 | 1.0000 | 1.0000 |
| endpoint_delta_custom_signed | W_other | 1 | 0.0000 |  |
| endpoint_delta_custom_signed | W_retrieval | 5 | 0.2000 | 0.2000 |
| endpoint_delta_neg_only | C_clean | 3 | 1.0000 |  |
| endpoint_delta_neg_only | C_fragile | 1 | 1.0000 | 0.0000 |
| endpoint_delta_neg_only | W_other | 1 | 0.0000 |  |
| endpoint_delta_neg_only | W_retrieval | 5 | 0.2000 | 0.2000 |

## Scope: full143

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 143 | 0.0923 | 0.5769 | 0.1469 | 0.4615 |
| delta_p_contrastive_raw_C | 143 | 0.1846 | 0.6154 | 0.1259 | 0.4685 |
| delta_p_custom_preserve | 143 | 0.2000 | 0.5944 | 0.1888 | 0.4965 |
| delta_p_custom_signed | 143 | 0.1538 | 0.5699 | 0.1888 | 0.4825 |
| delta_p_neg_only | 143 | 0.2077 | 0.5769 | 0.1399 | 0.4965 |
| endpoint_delta_contrastive_raw_C | 143 | 0.1154 | 0.5140 | 0.1748 | 0.4965 |
| endpoint_delta_custom_preserve | 142 | 0.2891 | 0.5599 | 0.1620 | 0.4930 |
| endpoint_delta_custom_signed | 143 | 0.1923 | 0.5490 | 0.1259 | 0.4895 |
| endpoint_delta_neg_only | 143 | 0.2615 | 0.5944 | 0.1329 | 0.4685 |

### Strong flip vs base: full143

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 143 | 0 | 0 | 66 | 77 | 0 | 0.0000 |
| delta_p_contrastive_raw_C | 143 | 7 | 6 | 60 | 70 | 1 | 0.0909 |
| delta_p_custom_preserve | 143 | 9 | 4 | 62 | 68 | 5 | 0.0909 |
| delta_p_custom_signed | 143 | 8 | 5 | 61 | 69 | 3 | 0.0909 |
| delta_p_neg_only | 143 | 11 | 6 | 60 | 66 | 5 | 0.1189 |
| endpoint_delta_contrastive_raw_C | 143 | 8 | 3 | 63 | 69 | 5 | 0.0769 |
| endpoint_delta_custom_preserve | 142 | 11 | 7 | 59 | 65 | 4 | 0.1268 |
| endpoint_delta_custom_signed | 143 | 7 | 3 | 63 | 70 | 4 | 0.0699 |
| endpoint_delta_neg_only | 143 | 7 | 6 | 60 | 70 | 1 | 0.0909 |

### Bucket strong_EM: full143

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 39 | 0.9231 |  |
| base | C_fragile | 26 | 0.9231 | 0.1154 |
| base | W_other | 39 | 0.0769 |  |
| base | W_retrieval | 39 | 0.0769 | 0.0769 |
| delta_p_contrastive_raw_C | C_clean | 39 | 0.8462 |  |
| delta_p_contrastive_raw_C | C_fragile | 26 | 1.0000 | 0.2692 |
| delta_p_contrastive_raw_C | W_other | 39 | 0.1282 |  |
| delta_p_contrastive_raw_C | W_retrieval | 39 | 0.0769 | 0.1282 |
| delta_p_custom_preserve | C_clean | 39 | 0.9744 |  |
| delta_p_custom_preserve | C_fragile | 26 | 1.0000 | 0.2692 |
| delta_p_custom_preserve | W_other | 39 | 0.0513 |  |
| delta_p_custom_preserve | W_retrieval | 39 | 0.1282 | 0.1538 |
| delta_p_custom_signed | C_clean | 39 | 0.9487 |  |
| delta_p_custom_signed | C_fragile | 26 | 0.9231 | 0.1923 |
| delta_p_custom_signed | W_other | 39 | 0.1282 |  |
| delta_p_custom_signed | W_retrieval | 39 | 0.0769 | 0.1282 |
| delta_p_neg_only | C_clean | 39 | 0.9231 |  |
| delta_p_neg_only | C_fragile | 26 | 0.9615 | 0.2692 |
| delta_p_neg_only | W_other | 39 | 0.0769 |  |
| delta_p_neg_only | W_retrieval | 39 | 0.1795 | 0.1667 |
| endpoint_delta_contrastive_raw_C | C_clean | 39 | 0.9231 |  |
| endpoint_delta_contrastive_raw_C | C_fragile | 26 | 1.0000 | 0.1154 |
| endpoint_delta_contrastive_raw_C | W_other | 39 | 0.1282 |  |
| endpoint_delta_contrastive_raw_C | W_retrieval | 39 | 0.1026 | 0.1154 |
| endpoint_delta_custom_preserve | C_clean | 39 | 0.8974 |  |
| endpoint_delta_custom_preserve | C_fragile | 26 | 0.9615 | 0.2885 |
| endpoint_delta_custom_preserve | W_other | 39 | 0.0513 |  |
| endpoint_delta_custom_preserve | W_retrieval | 38 | 0.2105 | 0.2895 |
| endpoint_delta_custom_signed | C_clean | 39 | 0.9487 |  |
| endpoint_delta_custom_signed | C_fragile | 26 | 0.9231 | 0.2885 |
| endpoint_delta_custom_signed | W_other | 39 | 0.1026 |  |
| endpoint_delta_custom_signed | W_retrieval | 39 | 0.1282 | 0.1282 |
| endpoint_delta_neg_only | C_clean | 39 | 0.8974 |  |
| endpoint_delta_neg_only | C_fragile | 26 | 0.9231 | 0.2308 |
| endpoint_delta_neg_only | W_other | 39 | 0.1026 |  |
| endpoint_delta_neg_only | W_retrieval | 39 | 0.1026 | 0.2821 |
