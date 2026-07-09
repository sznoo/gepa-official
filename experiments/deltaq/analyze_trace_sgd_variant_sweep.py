import argparse
import csv
import json
from pathlib import Path
from statistics import mean

def read_jsonl(p):
    rows = []
    if not p.exists():
        return rows
    with p.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def fmt(x):
    if x is None:
        return ""
    if isinstance(x, float):
        return f"{x:.3f}"
    return str(x)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--variants", nargs="+", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)

    by_trial_rows = []
    aggregate_rows = []
    selected_patch_lines = ["# Selected patches by variant\n"]

    for variant in args.variants:
        out = root / variant
        trials = read_jsonl(out / "trial_summary.jsonl")
        patches = read_jsonl(out / "patches.jsonl")

        if not trials:
            aggregate_rows.append({
                "variant": variant,
                "status": "missing_or_incomplete",
            })
            continue

        selected_patch_lines.append(f"\n## {variant}\n")

        for r in trials:
            row = {
                "variant": variant,
                "batch_id": r.get("batch_id"),
                "selected_patch_name": r.get("selected_patch_name"),
                "wrong_gain_by_compare": r.get("wrong_gain_by_compare"),
                "correct_preserve_by_equal": r.get("correct_preserve_by_equal"),
                "selected_rank_by_actual_net_gain": r.get("selected_rank_by_actual_net_gain"),
                "batch_acc_before": r.get("batch_acc_before"),
                "batch_acc_after": r.get("batch_acc_after"),
                "batch_delta": (r.get("batch_acc_after", 0) - r.get("batch_acc_before", 0)),
                "batch_flip": r.get("batch_flip"),
                "batch_break": r.get("batch_break"),
                "batch_net_gain": r.get("batch_net_gain"),
                "full_acc_before": r.get("full_acc_before"),
                "full_acc_after": r.get("full_acc_after"),
                "full_delta": (r.get("full_acc_after", 0) - r.get("full_acc_before", 0)),
                "full_flip": r.get("full_flip"),
                "full_break": r.get("full_break"),
                "full_net_gain": r.get("full_net_gain"),
                "fail_pool_acc_before": r.get("fail_pool_acc_before"),
                "fail_pool_acc_after": r.get("fail_pool_acc_after"),
                "fail_pool_delta": (r.get("fail_pool_acc_after", 0) - r.get("fail_pool_acc_before", 0)),
                "correct_pool_acc_before": r.get("correct_pool_acc_before"),
                "correct_pool_acc_after": r.get("correct_pool_acc_after"),
                "correct_pool_delta": (r.get("correct_pool_acc_after", 0) - r.get("correct_pool_acc_before", 0)),
            }
            by_trial_rows.append(row)

            selected_patch_lines.append(f"### batch {r.get('batch_id')} — {r.get('selected_patch_name')}\n")
            selected_patch_lines.append(
                f"- batch net: {r.get('batch_net_gain')}, full net: {r.get('full_net_gain')}, "
                f"wrong_gain: {r.get('wrong_gain_by_compare')}, "
                f"correct_preserve: {r.get('correct_preserve_by_equal')}/{r.get('correct_preserve_threshold', 4) + 1}, "
                f"rank: {r.get('selected_rank_by_actual_net_gain')}\n"
            )
            selected_patch_lines.append("```text\n")
            selected_patch_lines.append(str(r.get("selected_patch", "")).strip() + "\n")
            selected_patch_lines.append("```\n")

        n = len(trials)
        aggregate_rows.append({
            "variant": variant,
            "status": "ok",
            "n": n,
            "mean_batch_delta": mean(r.get("batch_acc_after", 0) - r.get("batch_acc_before", 0) for r in trials),
            "mean_batch_net": mean(r.get("batch_net_gain", 0) for r in trials),
            "positive_batch_net": sum(r.get("batch_net_gain", 0) > 0 for r in trials),
            "nonnegative_batch_net": sum(r.get("batch_net_gain", 0) >= 0 for r in trials),
            "mean_full_delta": mean(r.get("full_acc_after", 0) - r.get("full_acc_before", 0) for r in trials),
            "mean_full_net": mean(r.get("full_net_gain", 0) for r in trials),
            "positive_full_net": sum(r.get("full_net_gain", 0) > 0 for r in trials),
            "nonnegative_full_net": sum(r.get("full_net_gain", 0) >= 0 for r in trials),
            "mean_fail_pool_delta": mean(r.get("fail_pool_acc_after", 0) - r.get("fail_pool_acc_before", 0) for r in trials),
            "mean_correct_pool_delta": mean(r.get("correct_pool_acc_after", 0) - r.get("correct_pool_acc_before", 0) for r in trials),
            "mean_selected_rank": mean(r.get("selected_rank_by_actual_net_gain", 0) for r in trials),
            "mean_wrong_gain": mean(r.get("wrong_gain_by_compare", 0) for r in trials),
            "mean_correct_preserve": mean(r.get("correct_preserve_by_equal", 0) for r in trials),
        })

    # CSV by trial
    by_trial_csv = root / "by_trial.csv"
    if by_trial_rows:
        fieldnames = list(by_trial_rows[0].keys())
        with by_trial_csv.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(by_trial_rows)

    # Aggregate markdown
    lines = []
    lines.append("# Trace-SGD variant sweep summary\n")
    lines.append("| variant | n | mean batch Δacc | mean batch net | batch net >0 | mean full Δacc | mean full net | full net >0 | full net >=0 | mean fail Δacc | mean correct Δacc | mean rank | mean wrong gain | mean correct preserve |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    for r in aggregate_rows:
        if r.get("status") != "ok":
            lines.append(f"| {r['variant']} | 0 | missing | missing | missing | missing | missing | missing | missing | missing | missing | missing | missing | missing |")
            continue
        lines.append(
            f"| {r['variant']} | {r['n']} | "
            f"{r['mean_batch_delta']:+.3f} | {r['mean_batch_net']:+.3f} | {r['positive_batch_net']}/{r['n']} | "
            f"{r['mean_full_delta']:+.3f} | {r['mean_full_net']:+.3f} | {r['positive_full_net']}/{r['n']} | {r['nonnegative_full_net']}/{r['n']} | "
            f"{r['mean_fail_pool_delta']:+.3f} | {r['mean_correct_pool_delta']:+.3f} | "
            f"{r['mean_selected_rank']:.2f} | {r['mean_wrong_gain']:.2f} | {r['mean_correct_preserve']:.2f} |"
        )

    lines.append("\n## Output files\n")
    lines.append(f"- by-trial CSV: `{by_trial_csv}`")
    lines.append(f"- selected patches: `{root / 'selected_patches.md'}`")

    (root / "sweep_summary.md").write_text("\n".join(lines))
    (root / "selected_patches.md").write_text("\n".join(selected_patch_lines))

    print((root / "sweep_summary.md").read_text())

if __name__ == "__main__":
    main()
