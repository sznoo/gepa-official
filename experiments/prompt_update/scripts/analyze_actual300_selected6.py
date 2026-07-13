import json, math
from pathlib import Path
from collections import Counter
import pandas as pd
import numpy as np

ROOT = Path("experiments/prompt_update/results/actual300_selected")
OUT_PREFIX = ROOT / "positive_safety_actual300_selected6_batch012_analysis"

BATCHES = [0, 1, 2]
CONDS = [
    "base",
    "delta_p_custom_signed",
    "endpoint_delta_custom_signed",
    "delta_p_neg_only",
    "endpoint_delta_neg_only",
    "endpoint_delta_contrastive_raw_C",
]

def read_jsonl(p):
    rows = []
    if not p.exists():
        return rows
    with p.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def stderr(xs):
    xs = pd.Series(xs).dropna().astype(float)
    if len(xs) <= 1:
        return float("nan")
    return float(xs.std(ddof=1) / math.sqrt(len(xs)))

def safe_bool(x):
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        return bool(x)
    if isinstance(x, str):
        return x.lower() in {"true", "1", "yes", "y"}
    return False

def title_set(xs):
    if not isinstance(xs, list):
        return set()
    out = set()
    for x in xs:
        if isinstance(x, str):
            out.add(x)
        elif isinstance(x, dict):
            t = x.get("title") or x.get("page_title")
            if t:
                out.add(str(t))
    return out

def support_recall(row):
    # Prefer evaluator-computed support recall.
    for k in ["support_recall_hop2", "current_support_recall_total", "current_support_recall_hop2"]:
        v = row.get(k)
        if v is not None:
            try:
                return float(v)
            except Exception:
                pass

    gold = row.get("gold_support_titles") or []
    got = title_set(row.get("retrieved_titles") or row.get("retrieved_docs") or [])
    if not gold:
        return np.nan
    return len(set(gold) & got) / len(set(gold))

def missing_recovery(row):
    # Some GPT rows have null missing_recovery_rate. Recompute if possible.
    v = row.get("missing_recovery_rate")
    if v is not None:
        try:
            return float(v)
        except Exception:
            pass

    missing = (
        row.get("missing_after_hop1")
        or row.get("missing_titles_after_hop1")
        or row.get("missing_after_hop2")
        or row.get("missing_titles_after_hop2")
        or []
    )
    if not missing:
        return np.nan

    got = title_set(row.get("retrieved_titles") or row.get("retrieved_docs") or [])
    miss = set(missing)
    return len(miss & got) / len(miss)

rows = []
for B in BATCHES:
    p = ROOT / f"positive_safety_actual300_selected_batch{B}_eval.jsonl"
    if not p.exists():
        print("MISSING:", p)
        continue

    for r in read_jsonl(p):
        if r.get("condition") not in CONDS:
            continue
        rr = dict(r)
        rr["batch"] = B
        rr["error"] = bool(rr.get("error"))
        rr["case_id"] = int(rr["case_id"])
        rr["base_answerer_score"] = safe_bool(rr.get("base_score"))
        rr["strong_answerer_score"] = safe_bool(rr.get("strong_score"))
        rr["support_recall"] = support_recall(rr)
        rr["missing_recovery"] = missing_recovery(rr)
        rows.append(rr)

if not rows:
    raise SystemExit("No rows loaded.")

df_all = pd.DataFrame(rows)
err = df_all[df_all["error"]].copy()
df = df_all[~df_all["error"]].copy()

print("=" * 120)
print("ROW SANITY")
print("loaded rows:", len(df_all), "ok:", len(df), "err:", len(err), "/ expected", len(BATCHES) * len(CONDS) * 300)
if len(err):
    print("error types:", dict(Counter(err.get("error_type", pd.Series(dtype=str)).fillna("NA"))))

for B in BATCHES:
    sub = df[df["batch"].eq(B)]
    print("\nBATCH", B)
    print("  rows:", len(sub), "/ expected", len(CONDS) * 300)
    print("  scope:", dict(Counter(sub.get("eval_scope", pd.Series(dtype=str)))))
    print("  source:", dict(Counter(sub.get("actual300_cache_source", pd.Series(dtype=str)))))
    cnt = Counter(sub["condition"])
    for c in CONDS:
        print(f"  {c:38s} {cnt.get(c,0):3d}/300")

def summarize_abs(x):
    return pd.Series({
        "n": len(x),
        "support_recall": x["support_recall"].mean(),
        "missing_recovery": x["missing_recovery"].mean(),
        "base_answerer_EM": x["base_answerer_score"].astype(float).mean(),
        "strong_answerer_EM": x["strong_answerer_score"].astype(float).mean(),
        "answerer_delta_EM": (
            x["strong_answerer_score"].astype(float).mean()
            - x["base_answerer_score"].astype(float).mean()
        ),
    })

per_batch_abs = (
    df.groupby(["batch", "condition"], dropna=False)
      .apply(summarize_abs)
      .reset_index()
)

abs_summary = (
    per_batch_abs.groupby("condition", dropna=False)
      .agg(
          batches=("batch", "nunique"),
          n_mean=("n", "mean"),
          support_recall_mean=("support_recall", "mean"),
          support_recall_se=("support_recall", stderr),
          missing_recovery_mean=("missing_recovery", "mean"),
          missing_recovery_se=("missing_recovery", stderr),
          base_answerer_EM_mean=("base_answerer_EM", "mean"),
          base_answerer_EM_se=("base_answerer_EM", stderr),
          strong_answerer_EM_mean=("strong_answerer_EM", "mean"),
          strong_answerer_EM_se=("strong_answerer_EM", stderr),
          answerer_delta_EM_mean=("answerer_delta_EM", "mean"),
          answerer_delta_EM_se=("answerer_delta_EM", stderr),
      )
      .reset_index()
      .sort_values("strong_answerer_EM_mean", ascending=False)
)

# Paired condition-vs-base prompt comparison.
paired_rows = []
for B in BATCHES:
    sub = df[df["batch"].eq(B)].copy()
    base_rows = sub[sub["condition"].eq("base")].set_index("case_id")

    for cond in CONDS:
        crows = sub[sub["condition"].eq(cond)].set_index("case_id")
        common = sorted(set(base_rows.index) & set(crows.index))
        if not common:
            continue

        b = base_rows.loc[common]
        c = crows.loc[common]

        b_strong = b["strong_answerer_score"].astype(bool)
        c_strong = c["strong_answerer_score"].astype(bool)
        b_baseans = b["base_answerer_score"].astype(bool)
        c_baseans = c["base_answerer_score"].astype(bool)

        strong_w2r = ((~b_strong) & c_strong)
        strong_r2w = (b_strong & (~c_strong))
        baseans_w2r = ((~b_baseans) & c_baseans)
        baseans_r2w = (b_baseans & (~c_baseans))

        paired_rows.append({
            "batch": B,
            "condition": cond,
            "n": len(common),

            # Prompt effect under strong final answerer.
            "prompt_delta_strong_EM_vs_base": c_strong.astype(float).mean() - b_strong.astype(float).mean(),
            "prompt_strong_W_to_R": int(strong_w2r.sum()),
            "prompt_strong_R_to_W": int(strong_r2w.sum()),
            "prompt_strong_net": int(strong_w2r.sum() - strong_r2w.sum()),
            "prompt_strong_gain_freq": strong_w2r.mean(),
            "prompt_strong_loss_freq": strong_r2w.mean(),
            "prompt_strong_net_freq": strong_w2r.mean() - strong_r2w.mean(),

            # Prompt effect under base final answerer.
            "prompt_delta_base_answerer_EM_vs_base": c_baseans.astype(float).mean() - b_baseans.astype(float).mean(),
            "prompt_baseans_W_to_R": int(baseans_w2r.sum()),
            "prompt_baseans_R_to_W": int(baseans_r2w.sum()),
            "prompt_baseans_net": int(baseans_w2r.sum() - baseans_r2w.sum()),
            "prompt_baseans_gain_freq": baseans_w2r.mean(),
            "prompt_baseans_loss_freq": baseans_r2w.mean(),
            "prompt_baseans_net_freq": baseans_w2r.mean() - baseans_r2w.mean(),

            # Retrieval-side prompt effect.
            "prompt_delta_support_recall_vs_base": c["support_recall"].astype(float).mean() - b["support_recall"].astype(float).mean(),
            "prompt_delta_missing_recovery_vs_base": c["missing_recovery"].astype(float).mean() - b["missing_recovery"].astype(float).mean(),
            "support_recall_base": b["support_recall"].astype(float).mean(),
            "support_recall_cond": c["support_recall"].astype(float).mean(),
            "missing_recovery_base": b["missing_recovery"].astype(float).mean(),
            "missing_recovery_cond": c["missing_recovery"].astype(float).mean(),
        })

paired = pd.DataFrame(paired_rows)

paired_summary = (
    paired.groupby("condition", dropna=False)
      .agg(
          batches=("batch", "nunique"),
          n_mean=("n", "mean"),

          prompt_delta_strong_EM_vs_base_mean=("prompt_delta_strong_EM_vs_base", "mean"),
          prompt_delta_strong_EM_vs_base_se=("prompt_delta_strong_EM_vs_base", stderr),
          prompt_strong_W_to_R_mean=("prompt_strong_W_to_R", "mean"),
          prompt_strong_R_to_W_mean=("prompt_strong_R_to_W", "mean"),
          prompt_strong_net_mean=("prompt_strong_net", "mean"),
          prompt_strong_gain_freq_mean=("prompt_strong_gain_freq", "mean"),
          prompt_strong_gain_freq_se=("prompt_strong_gain_freq", stderr),
          prompt_strong_loss_freq_mean=("prompt_strong_loss_freq", "mean"),
          prompt_strong_loss_freq_se=("prompt_strong_loss_freq", stderr),
          prompt_strong_net_freq_mean=("prompt_strong_net_freq", "mean"),
          prompt_strong_net_freq_se=("prompt_strong_net_freq", stderr),

          prompt_delta_base_answerer_EM_vs_base_mean=("prompt_delta_base_answerer_EM_vs_base", "mean"),
          prompt_delta_base_answerer_EM_vs_base_se=("prompt_delta_base_answerer_EM_vs_base", stderr),
          prompt_baseans_W_to_R_mean=("prompt_baseans_W_to_R", "mean"),
          prompt_baseans_R_to_W_mean=("prompt_baseans_R_to_W", "mean"),
          prompt_baseans_net_mean=("prompt_baseans_net", "mean"),

          prompt_delta_support_recall_vs_base_mean=("prompt_delta_support_recall_vs_base", "mean"),
          prompt_delta_support_recall_vs_base_se=("prompt_delta_support_recall_vs_base", stderr),
          prompt_delta_missing_recovery_vs_base_mean=("prompt_delta_missing_recovery_vs_base", "mean"),
          prompt_delta_missing_recovery_vs_base_se=("prompt_delta_missing_recovery_vs_base", stderr),
          support_recall_base_mean=("support_recall_base", "mean"),
          support_recall_cond_mean=("support_recall_cond", "mean"),
          missing_recovery_base_mean=("missing_recovery_base", "mean"),
          missing_recovery_cond_mean=("missing_recovery_cond", "mean"),
      )
      .reset_index()
      .sort_values("prompt_delta_strong_EM_vs_base_mean", ascending=False)
)

def pm(m, s):
    if pd.isna(m):
        return "NA"
    if pd.isna(s):
        return f"{m:.4f}"
    return f"{m:.4f} ± {s:.4f}"

abs_view = abs_summary.copy()
for name in [
    "support_recall",
    "missing_recovery",
    "base_answerer_EM",
    "strong_answerer_EM",
    "answerer_delta_EM",
]:
    abs_view[name] = [
        pm(m, s)
        for m, s in zip(abs_view[f"{name}_mean"], abs_view[f"{name}_se"])
    ]

paired_view = paired_summary.copy()
rename_specs = {
    "prompt_delta_strong_EM_vs_base": "Δstrong_EM_vs_base_prompt",
    "prompt_strong_gain_freq": "strong_W2R_freq",
    "prompt_strong_loss_freq": "strong_R2W_freq",
    "prompt_strong_net_freq": "strong_net_freq",
    "prompt_delta_base_answerer_EM_vs_base": "Δbase_answerer_EM_vs_base_prompt",
    "prompt_delta_support_recall_vs_base": "Δsupport_recall_vs_base_prompt",
    "prompt_delta_missing_recovery_vs_base": "Δmissing_recovery_vs_base_prompt",
}
for raw, pretty in rename_specs.items():
    paired_view[pretty] = [
        pm(m, s)
        for m, s in zip(paired_view[f"{raw}_mean"], paired_view[f"{raw}_se"])
    ]

print("\n" + "=" * 120)
print("ABSOLUTE ACTUAL300 METRICS, MEAN ± STDERR OVER BATCHES")
abs_cols = [
    "condition",
    "batches",
    "n_mean",
    "support_recall",
    "missing_recovery",
    "base_answerer_EM",
    "strong_answerer_EM",
    "answerer_delta_EM",
]
print(abs_view[abs_cols].to_string(index=False))

print("\n" + "=" * 120)
print("PAIRED PROMPT EFFECT VS condition=base, MEAN ± STDERR OVER BATCHES")
paired_cols = [
    "condition",
    "batches",
    "n_mean",
    "Δstrong_EM_vs_base_prompt",
    "prompt_strong_W_to_R_mean",
    "prompt_strong_R_to_W_mean",
    "prompt_strong_net_mean",
    "strong_W2R_freq",
    "strong_R2W_freq",
    "strong_net_freq",
    "Δbase_answerer_EM_vs_base_prompt",
    "prompt_baseans_W_to_R_mean",
    "prompt_baseans_R_to_W_mean",
    "prompt_baseans_net_mean",
    "Δsupport_recall_vs_base_prompt",
    "Δmissing_recovery_vs_base_prompt",
]
print(paired_view[paired_cols].to_string(index=False))

# Save outputs.
per_batch_abs.to_csv(f"{OUT_PREFIX}_absolute_per_batch.csv", index=False)
abs_summary.to_csv(f"{OUT_PREFIX}_absolute_summary.csv", index=False)
paired.to_csv(f"{OUT_PREFIX}_paired_vs_base_per_batch.csv", index=False)
paired_summary.to_csv(f"{OUT_PREFIX}_paired_vs_base_summary.csv", index=False)

with open(f"{OUT_PREFIX}_summary.md", "w", encoding="utf-8") as f:
    f.write("# GPT Actual300 Selected6 Analysis\n\n")
    f.write("## Definitions\n\n")
    f.write("- `condition`: create_query_hop2 prompt condition.\n")
    f.write("- `support_recall`: fraction of gold support titles retrieved by hop2 query.\n")
    f.write("- `missing_recovery`: fraction of missing-after-hop1 titles recovered by hop2 query, recomputed when evaluator field is null.\n")
    f.write("- `base_answerer_EM`: downstream EM using `base_final_answerer_prompt` on the retrieved context.\n")
    f.write("- `strong_answerer_EM`: downstream EM using `strong_final_answerer_prompt` on the retrieved context.\n")
    f.write("- `answerer_delta_EM`: `strong_answerer_EM - base_answerer_EM`; this is answerer-side delta, not prompt-condition gain.\n")
    f.write("- Paired prompt deltas compare each condition to `condition=base` on the same `(batch, case_id)`.\n\n")

    f.write("## Absolute Actual300 Metrics\n\n")
    f.write(abs_view[abs_cols].to_markdown(index=False, floatfmt=".4f"))
    f.write("\n\n")

    f.write("## Paired Prompt Effect vs condition=base\n\n")
    f.write(paired_view[paired_cols].to_markdown(index=False, floatfmt=".4f"))
    f.write("\n\n")

    f.write("## Absolute Per-Batch Metrics\n\n")
    f.write(per_batch_abs.sort_values(["batch", "condition"]).to_markdown(index=False, floatfmt=".4f"))
    f.write("\n\n")

    f.write("## Paired Per-Batch Metrics\n\n")
    f.write(paired.sort_values(["batch", "condition"]).to_markdown(index=False, floatfmt=".4f"))
    f.write("\n")

print("\n" + "=" * 120)
print("WROTE")
print(f"{OUT_PREFIX}_absolute_per_batch.csv")
print(f"{OUT_PREFIX}_absolute_summary.csv")
print(f"{OUT_PREFIX}_paired_vs_base_per_batch.csv")
print(f"{OUT_PREFIX}_paired_vs_base_summary.csv")
print(f"{OUT_PREFIX}_summary.md")
