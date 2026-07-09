# Full Trace Prompt Injection Probe

| arm | n | mean MR | mean hop2 recall | mean recovered |
|---|---:|---:|---:|---:|
| base_existing | 4 | 0.000 | 0.250 | 0.000 |
| last_trace_existing | 4 | 1.000 | 0.875 | 1.000 |
| prompt_base | 4 | 0.250 | 0.375 | 0.250 |
| prompt_current_plus_executable | 4 | 0.750 | 0.625 | 0.750 |
| prompt_current_plus_minimal | 4 | 0.750 | 0.625 | 0.750 |
| prompt_current_query | 4 | 0.500 | 0.500 | 0.500 |
| prompt_executable_compression | 4 | 0.750 | 0.625 | 0.750 |
| prompt_minimal_compression | 4 | 0.750 | 0.625 | 0.750 |
| prompt_raw_plus_executable | 4 | 1.000 | 0.875 | 1.000 |
| prompt_raw_trace | 4 | 1.000 | 0.875 | 1.000 |
| prompt_structured_compression | 4 | 0.500 | 0.500 | 0.500 |
| target_existing | 4 | 1.000 | 0.875 | 1.000 |