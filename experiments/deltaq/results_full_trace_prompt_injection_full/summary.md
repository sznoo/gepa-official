# Full Trace Prompt Injection Probe

| arm | n | mean MR | mean hop2 recall | mean recovered |
|---|---:|---:|---:|---:|
| base_existing | 19 | 0.000 | 0.342 | 0.000 |
| last_trace_existing | 19 | 0.947 | 0.868 | 1.000 |
| prompt_base | 19 | 0.000 | 0.000 | 0.000 |
| prompt_executable_compression | 19 | 0.605 | 0.579 | 0.632 |
| prompt_minimal_compression | 19 | 0.684 | 0.711 | 0.737 |
| prompt_raw_plus_executable | 19 | 0.711 | 0.684 | 0.737 |
| prompt_raw_trace | 19 | 0.579 | 0.526 | 0.632 |
| prompt_structured_compression | 19 | 0.579 | 0.658 | 0.632 |
| target_existing | 19 | 0.947 | 0.868 | 1.000 |