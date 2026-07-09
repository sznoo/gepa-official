import argparse
import json
from collections import defaultdict
from pathlib import Path


def load_jsonl(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def add(stats, key, ex):
    s = stats[key]
    s["n"] += 1
    s["support_recall_hop2"] += ex["support_recall_hop2"]
    s["missing_recovery_rate"] += ex["missing_recovery_rate"]
    s["any_support_hit"] += int(ex["support_hit_count"] > 0)
    s["any_missing_recovered"] += int(ex["missing_recovered_count"] > 0)


def render(stats, title):
    lines = [f"\n# {title}\n"]
    lines.append("| key | n | support recall hop2 | missing recovery | any support hit | any missing recovered |")
    lines.append("|---|---:|---:|---:|---:|---:|")

    for key, s in sorted(stats.items()):
        n = s["n"]
        lines.append(
            f"| {key} | {n} | "
            f"{s['support_recall_hop2'] / n:.3f} | "
            f"{s['missing_recovery_rate'] / n:.3f} | "
            f"{s['any_support_hit'] / n:.3f} | "
            f"{s['any_missing_recovered'] / n:.3f} |"
        )
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--validation", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    by_arm = defaultdict(lambda: defaultdict(float))
    by_trace_step = defaultdict(lambda: defaultdict(float))
    by_trace_edit_type = defaultdict(lambda: defaultdict(float))

    for ex in load_jsonl(args.validation):
        arm = ex["arm"]
        add(by_arm, arm, ex)

        meta = ex.get("meta") or {}
        if arm.startswith("trace_step_"):
            step = meta.get("step")
            edit_type = meta.get("edit_type")
            if step is not None:
                add(by_trace_step, f"trace_step_{step}", ex)
            if edit_type:
                add(by_trace_edit_type, edit_type, ex)

    text = []
    text.append(render(by_arm, "By raw arm"))
    text.append(render(by_trace_step, "Trace prefixes by step"))
    text.append(render(by_trace_edit_type, "Trace prefixes by edit type"))

    Path(args.out).write_text("\n\n".join(text))
    print(args.out)


if __name__ == "__main__":
    main()