# Positive Safety Batch0 Evaluation

- n_ok: 1365
- n_error: 7

## Scope: batch2

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 10 | 0.0000 | 0.4500 | 0.1000 | 0.3000 |
| delta_p_contrastive_raw_C | 9 | 0.0000 | 0.3889 | 0.1111 | 0.3333 |
| delta_p_custom_preserve | 10 | 0.1667 | 0.4000 | 0.1000 | 0.3000 |
| delta_p_custom_signed | 10 | 0.1667 | 0.4000 | 0.1000 | 0.4000 |
| delta_p_neg_only | 10 | 0.0000 | 0.4500 | 0.1000 | 0.3000 |
| endpoint_delta_contrastive_raw_C | 9 | 0.0000 | 0.3889 | 0.1111 | 0.4444 |
| endpoint_delta_custom_preserve | 10 | 0.2500 | 0.5000 | 0.1000 | 0.5000 |
| endpoint_delta_custom_signed | 10 | 0.1667 | 0.4000 | 0.1000 | 0.5000 |
| endpoint_delta_neg_only | 8 | 0.2000 | 0.3750 | 0.1250 | 0.6250 |

### Strong flip vs base: batch2

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 10 | 0 | 0 | 3 | 7 | 0 | 0.0000 |
| delta_p_contrastive_raw_C | 9 | 1 | 0 | 2 | 6 | 1 | 0.1111 |
| delta_p_custom_preserve | 10 | 1 | 1 | 2 | 6 | 0 | 0.2000 |
| delta_p_custom_signed | 10 | 1 | 0 | 3 | 6 | 1 | 0.1000 |
| delta_p_neg_only | 10 | 1 | 1 | 2 | 6 | 0 | 0.2000 |
| endpoint_delta_contrastive_raw_C | 9 | 1 | 0 | 3 | 5 | 1 | 0.1111 |
| endpoint_delta_custom_preserve | 10 | 2 | 0 | 3 | 5 | 2 | 0.2000 |
| endpoint_delta_custom_signed | 10 | 3 | 1 | 2 | 4 | 2 | 0.4000 |
| endpoint_delta_neg_only | 8 | 3 | 0 | 2 | 3 | 3 | 0.3750 |

### Bucket strong_EM: batch2

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 3 | 1.0000 |  |
| base | C_fragile | 1 | 0.0000 | 0.0000 |
| base | W_other | 1 | 0.0000 |  |
| base | W_retrieval | 5 | 0.0000 | 0.0000 |
| delta_p_contrastive_raw_C | C_clean | 2 | 1.0000 |  |
| delta_p_contrastive_raw_C | C_fragile | 1 | 1.0000 | 0.0000 |
| delta_p_contrastive_raw_C | W_other | 1 | 0.0000 |  |
| delta_p_contrastive_raw_C | W_retrieval | 5 | 0.0000 | 0.0000 |
| delta_p_custom_preserve | C_clean | 3 | 0.6667 |  |
| delta_p_custom_preserve | C_fragile | 1 | 1.0000 | 0.0000 |
| delta_p_custom_preserve | W_other | 1 | 0.0000 |  |
| delta_p_custom_preserve | W_retrieval | 5 | 0.0000 | 0.2000 |
| delta_p_custom_signed | C_clean | 3 | 1.0000 |  |
| delta_p_custom_signed | C_fragile | 1 | 0.0000 | 0.0000 |
| delta_p_custom_signed | W_other | 1 | 0.0000 |  |
| delta_p_custom_signed | W_retrieval | 5 | 0.2000 | 0.2000 |
| delta_p_neg_only | C_clean | 3 | 0.6667 |  |
| delta_p_neg_only | C_fragile | 1 | 1.0000 | 0.0000 |
| delta_p_neg_only | W_other | 1 | 0.0000 |  |
| delta_p_neg_only | W_retrieval | 5 | 0.0000 | 0.0000 |
| endpoint_delta_contrastive_raw_C | C_clean | 3 | 1.0000 |  |
| endpoint_delta_contrastive_raw_C | C_fragile | 1 | 1.0000 | 0.0000 |
| endpoint_delta_contrastive_raw_C | W_other | 1 | 0.0000 |  |
| endpoint_delta_contrastive_raw_C | W_retrieval | 4 | 0.0000 | 0.0000 |
| endpoint_delta_custom_preserve | C_clean | 3 | 1.0000 |  |
| endpoint_delta_custom_preserve | C_fragile | 1 | 1.0000 | 0.0000 |
| endpoint_delta_custom_preserve | W_other | 1 | 0.0000 |  |
| endpoint_delta_custom_preserve | W_retrieval | 5 | 0.2000 | 0.3000 |
| endpoint_delta_custom_signed | C_clean | 3 | 0.6667 |  |
| endpoint_delta_custom_signed | C_fragile | 1 | 1.0000 | 0.0000 |
| endpoint_delta_custom_signed | W_other | 1 | 0.0000 |  |
| endpoint_delta_custom_signed | W_retrieval | 5 | 0.4000 | 0.2000 |
| endpoint_delta_neg_only | C_clean | 2 | 1.0000 |  |
| endpoint_delta_neg_only | C_fragile | 1 | 1.0000 | 0.0000 |
| endpoint_delta_neg_only | W_other | 1 | 0.0000 |  |
| endpoint_delta_neg_only | W_retrieval | 4 | 0.5000 | 0.2500 |

## Scope: full143

| condition | n | MR | support_recall | base_EM | strong_EM |
|---|---:|---:|---:|---:|---:|
| base | 142 | 0.0938 | 0.5317 | 0.1549 | 0.4648 |
| delta_p_contrastive_raw_C | 142 | 0.2109 | 0.5704 | 0.1549 | 0.4859 |
| delta_p_custom_preserve | 142 | 0.1875 | 0.5915 | 0.1972 | 0.4789 |
| delta_p_custom_signed | 142 | 0.2500 | 0.5880 | 0.1479 | 0.5211 |
| delta_p_neg_only | 143 | 0.1692 | 0.5734 | 0.1049 | 0.4965 |
| endpoint_delta_contrastive_raw_C | 141 | 0.1905 | 0.6099 | 0.1631 | 0.4681 |
| endpoint_delta_custom_preserve | 141 | 0.1641 | 0.5603 | 0.1348 | 0.4823 |
| endpoint_delta_custom_signed | 143 | 0.1615 | 0.5524 | 0.1399 | 0.4965 |
| endpoint_delta_neg_only | 143 | 0.2000 | 0.5524 | 0.1748 | 0.4755 |

### Strong flip vs base: full143

| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 142 | 0 | 0 | 66 | 76 | 0 | 0.0000 |
| delta_p_contrastive_raw_C | 141 | 8 | 6 | 60 | 67 | 2 | 0.0993 |
| delta_p_custom_preserve | 141 | 9 | 8 | 58 | 66 | 1 | 0.1206 |
| delta_p_custom_signed | 141 | 13 | 6 | 60 | 62 | 7 | 0.1348 |
| delta_p_neg_only | 142 | 11 | 7 | 59 | 65 | 4 | 0.1268 |
| endpoint_delta_contrastive_raw_C | 140 | 6 | 6 | 59 | 69 | 0 | 0.0857 |
| endpoint_delta_custom_preserve | 140 | 10 | 8 | 57 | 65 | 2 | 0.1286 |
| endpoint_delta_custom_signed | 142 | 10 | 6 | 60 | 66 | 4 | 0.1127 |
| endpoint_delta_neg_only | 142 | 7 | 6 | 60 | 69 | 1 | 0.0915 |

### Bucket strong_EM: full143

| condition | bucket | n | strong_EM | MR |
|---|---|---:|---:|---:|
| base | C_clean | 39 | 0.8462 |  |
| base | C_fragile | 25 | 0.9600 | 0.1600 |
| base | W_other | 39 | 0.1026 |  |
| base | W_retrieval | 39 | 0.1282 | 0.0513 |
| delta_p_contrastive_raw_C | C_clean | 39 | 0.9231 |  |
| delta_p_contrastive_raw_C | C_fragile | 26 | 0.8846 | 0.1923 |
| delta_p_contrastive_raw_C | W_other | 39 | 0.0769 |  |
| delta_p_contrastive_raw_C | W_retrieval | 38 | 0.1842 | 0.2237 |
| delta_p_custom_preserve | C_clean | 39 | 0.9487 |  |
| delta_p_custom_preserve | C_fragile | 26 | 0.8846 | 0.1923 |
| delta_p_custom_preserve | W_other | 39 | 0.0513 |  |
| delta_p_custom_preserve | W_retrieval | 38 | 0.1579 | 0.1842 |
| delta_p_custom_signed | C_clean | 39 | 0.9231 |  |
| delta_p_custom_signed | C_fragile | 26 | 0.8846 | 0.2115 |
| delta_p_custom_signed | W_other | 39 | 0.1282 |  |
| delta_p_custom_signed | W_retrieval | 38 | 0.2632 | 0.2763 |
| delta_p_neg_only | C_clean | 39 | 0.9231 |  |
| delta_p_neg_only | C_fragile | 26 | 0.9615 | 0.1154 |
| delta_p_neg_only | W_other | 39 | 0.1026 |  |
| delta_p_neg_only | W_retrieval | 39 | 0.1538 | 0.2051 |
| endpoint_delta_contrastive_raw_C | C_clean | 39 | 0.8974 |  |
| endpoint_delta_contrastive_raw_C | C_fragile | 26 | 0.9231 | 0.2692 |
| endpoint_delta_contrastive_raw_C | W_other | 39 | 0.1026 |  |
| endpoint_delta_contrastive_raw_C | W_retrieval | 37 | 0.0811 | 0.1351 |
| endpoint_delta_custom_preserve | C_clean | 38 | 0.9211 |  |
| endpoint_delta_custom_preserve | C_fragile | 26 | 0.9231 | 0.1923 |
| endpoint_delta_custom_preserve | W_other | 39 | 0.1026 |  |
| endpoint_delta_custom_preserve | W_retrieval | 38 | 0.1316 | 0.1447 |
| endpoint_delta_custom_signed | C_clean | 39 | 0.8974 |  |
| endpoint_delta_custom_signed | C_fragile | 26 | 0.9615 | 0.1346 |
| endpoint_delta_custom_signed | W_other | 39 | 0.1282 |  |
| endpoint_delta_custom_signed | W_retrieval | 39 | 0.1538 | 0.1795 |
| endpoint_delta_neg_only | C_clean | 39 | 0.8974 |  |
| endpoint_delta_neg_only | C_fragile | 26 | 0.9615 | 0.2115 |
| endpoint_delta_neg_only | W_other | 39 | 0.0769 |  |
| endpoint_delta_neg_only | W_retrieval | 39 | 0.1282 | 0.1923 |
