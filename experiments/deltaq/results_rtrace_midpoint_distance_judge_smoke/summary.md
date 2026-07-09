# R-trace midpoint distance utility judge

- rtrace_aux_path: `experiments/deltaq/results_biggest_step_rtrace_full19_Ronly/rtrace_aux.jsonl`
- judge criterion: same update-magnitude criterion as biggest-step R-trace decomposition
- evaluated condition:

```latex
\begin{aligned}
d_T(R_i, R_{\mathrm{mid}}) &< d_T(R_i, R_{i+1}) \\
d_T(R_{\mathrm{mid}}, R_{i+1}) &< d_T(R_i, R_{i+1})
\end{aligned}
```

- n_tasks: 6
- n_midpoint_triples: 3
- left_pass_rate: 0.3333
- right_pass_rate: 1.0000
- both_pass_rate: 0.3333
- mean_shrink_score: 0.6667
- tie_or_invalid_rate: 0.0000

## Definitions

- left_pass: original edge \(R_i \to R_{i+1}\) is judged larger than \(R_i \to R_{mid}\).
- right_pass: original edge \(R_i \to R_{i+1}\) is judged larger than \(R_{mid} \to R_{i+1}\).
- both_pass: both midpoint inequalities hold for the same generated midpoint.