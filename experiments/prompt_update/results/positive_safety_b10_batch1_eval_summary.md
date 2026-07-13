# Positive Safety Batch0 Evaluation

- n_ok: 1375
- n_error: 1

## Scope: batch1

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 9 | 0.0000 | 0.5556 | 0.0000 | 0.3333 |
| delta_p_contrastive_raw_C | 10 | 0.3333 | 0.6500 | 0.0000 | 0.4000 |
| delta_p_custom_preserve | 10 | 0.1667 | 0.6500 | 0.0000 | 0.5000 |
| delta_p_custom_signed | 10 | 0.1667 | 0.6500 | 0.0000 | 0.4000 |
| delta_p_neg_only | 10 | 0.1667 | 0.6000 | 0.0000 | 0.4000 |
| endpoint_delta_contrastive_raw_C | 10 | 0.3333 | 0.7000 | 0.0000 | 0.4000 |
| endpoint_delta_custom_preserve | 10 | 0.3333 | 0.6500 | 0.1000 | 0.5000 |
| endpoint_delta_custom_signed | 10 | 0.1667 | 0.6500 | 0.1000 | 0.6000 |
| endpoint_delta_neg_only | 10 | 0.3333 | 0.7000 | 0.0000 | 0.5000 |

### Strong flip vs base: batch1

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 9 | 0 | 0 | 3 | 6 | 0 | 0.0000 |
| delta_p_contrastive_raw_C | 9 | 0 | 0 | 3 | 6 | 0 | 0.0000 |
| delta_p_custom_preserve | 9 | 1 | 0 | 3 | 5 | 1 | 0.1111 |
| delta_p_custom_signed | 9 | 0 | 0 | 3 | 6 | 0 | 0.0000 |
| delta_p_neg_only | 9 | 0 | 0 | 3 | 6 | 0 | 0.0000 |
| endpoint_delta_contrastive_raw_C | 9 | 0 | 0 | 3 | 6 | 0 | 0.0000 |
| endpoint_delta_custom_preserve | 9 | 1 | 0 | 3 | 5 | 1 | 0.1111 |
| endpoint_delta_custom_signed | 9 | 2 | 0 | 3 | 4 | 2 | 0.2222 |
| endpoint_delta_neg_only | 9 | 1 | 0 | 3 | 5 | 1 | 0.1111 |

### Bucket strong_EM: batch1

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 3 | 1.0000 |  |
| base | W_other | 1 | 0.0000 |  |
| base | W_retrieval | 5 | 0.0000 | 0.0000 |
| delta_p_contrastive_raw_C | C_clean | 3 | 1.0000 |  |
| delta_p_contrastive_raw_C | C_fragile | 1 | 1.0000 | 1.0000 |
| delta_p_contrastive_raw_C | W_other | 1 | 0.0000 |  |
| delta_p_contrastive_raw_C | W_retrieval | 5 | 0.0000 | 0.2000 |
| delta_p_custom_preserve | C_clean | 3 | 1.0000 |  |
| delta_p_custom_preserve | C_fragile | 1 | 1.0000 | 1.0000 |
| delta_p_custom_preserve | W_other | 1 | 0.0000 |  |
| delta_p_custom_preserve | W_retrieval | 5 | 0.2000 | 0.0000 |
| delta_p_custom_signed | C_clean | 3 | 1.0000 |  |
| delta_p_custom_signed | C_fragile | 1 | 1.0000 | 1.0000 |
| delta_p_custom_signed | W_other | 1 | 0.0000 |  |
| delta_p_custom_signed | W_retrieval | 5 | 0.0000 | 0.0000 |
| delta_p_neg_only | C_clean | 3 | 1.0000 |  |
| delta_p_neg_only | C_fragile | 1 | 1.0000 | 1.0000 |
| delta_p_neg_only | W_other | 1 | 0.0000 |  |
| delta_p_neg_only | W_retrieval | 5 | 0.0000 | 0.0000 |
| endpoint_delta_contrastive_raw_C | C_clean | 3 | 1.0000 |  |
| endpoint_delta_contrastive_raw_C | C_fragile | 1 | 1.0000 | 1.0000 |
| endpoint_delta_contrastive_raw_C | W_other | 1 | 0.0000 |  |
| endpoint_delta_contrastive_raw_C | W_retrieval | 5 | 0.0000 | 0.2000 |
| endpoint_delta_custom_preserve | C_clean | 3 | 1.0000 |  |
| endpoint_delta_custom_preserve | C_fragile | 1 | 1.0000 | 1.0000 |
| endpoint_delta_custom_preserve | W_other | 1 | 0.0000 |  |
| endpoint_delta_custom_preserve | W_retrieval | 5 | 0.2000 | 0.2000 |
| endpoint_delta_custom_signed | C_clean | 3 | 1.0000 |  |
| endpoint_delta_custom_signed | C_fragile | 1 | 1.0000 | 0.0000 |
| endpoint_delta_custom_signed | W_other | 1 | 0.0000 |  |
| endpoint_delta_custom_signed | W_retrieval | 5 | 0.4000 | 0.2000 |
| endpoint_delta_neg_only | C_clean | 3 | 1.0000 |  |
| endpoint_delta_neg_only | C_fragile | 1 | 1.0000 | 1.0000 |
| endpoint_delta_neg_only | W_other | 1 | 0.0000 |  |
| endpoint_delta_neg_only | W_retrieval | 5 | 0.2000 | 0.2000 |

## Scope: full143

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 143 | 0.0231 | 0.5315 | 0.1538 | 0.4825 |
| delta_p_contrastive_raw_C | 143 | 0.1769 | 0.5699 | 0.1678 | 0.4615 |
| delta_p_custom_preserve | 143 | 0.1923 | 0.6049 | 0.1608 | 0.4615 |
| delta_p_custom_signed | 143 | 0.1692 | 0.6049 | 0.1469 | 0.4825 |
| delta_p_neg_only | 143 | 0.1692 | 0.5524 | 0.1469 | 0.4825 |
| endpoint_delta_contrastive_raw_C | 142 | 0.1250 | 0.5669 | 0.1338 | 0.4859 |
| endpoint_delta_custom_preserve | 143 | 0.1385 | 0.5944 | 0.1329 | 0.4895 |
| endpoint_delta_custom_signed | 143 | 0.1077 | 0.5874 | 0.1469 | 0.4755 |
| endpoint_delta_neg_only | 143 | 0.2000 | 0.5979 | 0.1678 | 0.4755 |

### Strong flip vs base: full143

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 143 | 0 | 0 | 69 | 74 | 0 | 0.0000 |
| delta_p_contrastive_raw_C | 143 | 3 | 6 | 63 | 71 | -3 | 0.0629 |
| delta_p_custom_preserve | 143 | 3 | 6 | 63 | 71 | -3 | 0.0629 |
| delta_p_custom_signed | 143 | 7 | 7 | 62 | 67 | 0 | 0.0979 |
| delta_p_neg_only | 143 | 7 | 7 | 62 | 67 | 0 | 0.0979 |
| endpoint_delta_contrastive_raw_C | 142 | 8 | 8 | 61 | 65 | 0 | 0.1127 |
| endpoint_delta_custom_preserve | 143 | 7 | 6 | 63 | 67 | 1 | 0.0909 |
| endpoint_delta_custom_signed | 143 | 5 | 6 | 63 | 69 | -1 | 0.0769 |
| endpoint_delta_neg_only | 143 | 3 | 4 | 65 | 71 | -1 | 0.0490 |

### Bucket strong_EM: full143

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 39 | 0.8974 |  |
| base | C_fragile | 26 | 0.9615 | 0.0000 |
| base | W_other | 39 | 0.1282 |  |
| base | W_retrieval | 39 | 0.1026 | 0.0385 |
| delta_p_contrastive_raw_C | C_clean | 39 | 0.8974 |  |
| delta_p_contrastive_raw_C | C_fragile | 26 | 0.9615 | 0.2308 |
| delta_p_contrastive_raw_C | W_other | 39 | 0.0256 |  |
| delta_p_contrastive_raw_C | W_retrieval | 39 | 0.1282 | 0.1410 |
| delta_p_custom_preserve | C_clean | 39 | 0.8974 |  |
| delta_p_custom_preserve | C_fragile | 26 | 1.0000 | 0.2692 |
| delta_p_custom_preserve | W_other | 39 | 0.0513 |  |
| delta_p_custom_preserve | W_retrieval | 39 | 0.0769 | 0.1410 |
| delta_p_custom_signed | C_clean | 39 | 0.9231 |  |
| delta_p_custom_signed | C_fragile | 26 | 0.9231 | 0.2308 |
| delta_p_custom_signed | W_other | 39 | 0.1282 |  |
| delta_p_custom_signed | W_retrieval | 39 | 0.1026 | 0.1282 |
| delta_p_neg_only | C_clean | 39 | 0.9744 |  |
| delta_p_neg_only | C_fragile | 26 | 0.8846 | 0.2692 |
| delta_p_neg_only | W_other | 39 | 0.1026 |  |
| delta_p_neg_only | W_retrieval | 39 | 0.1026 | 0.1026 |
| endpoint_delta_contrastive_raw_C | C_clean | 39 | 0.8718 |  |
| endpoint_delta_contrastive_raw_C | C_fragile | 26 | 0.9615 | 0.1923 |
| endpoint_delta_contrastive_raw_C | W_other | 39 | 0.1282 |  |
| endpoint_delta_contrastive_raw_C | W_retrieval | 38 | 0.1316 | 0.0789 |
| endpoint_delta_custom_preserve | C_clean | 39 | 0.8718 |  |
| endpoint_delta_custom_preserve | C_fragile | 26 | 1.0000 | 0.1923 |
| endpoint_delta_custom_preserve | W_other | 39 | 0.1026 |  |
| endpoint_delta_custom_preserve | W_retrieval | 39 | 0.1538 | 0.1026 |
| endpoint_delta_custom_signed | C_clean | 39 | 0.8974 |  |
| endpoint_delta_custom_signed | C_fragile | 26 | 1.0000 | 0.1154 |
| endpoint_delta_custom_signed | W_other | 39 | 0.0513 |  |
| endpoint_delta_custom_signed | W_retrieval | 39 | 0.1282 | 0.1026 |
| endpoint_delta_neg_only | C_clean | 39 | 0.9487 |  |
| endpoint_delta_neg_only | C_fragile | 26 | 0.9615 | 0.1923 |
| endpoint_delta_neg_only | W_other | 39 | 0.0769 |  |
| endpoint_delta_neg_only | W_retrieval | 39 | 0.0769 | 0.2051 |
