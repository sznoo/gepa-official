#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict, Counter
from pathlib import Path


def read_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def rate(xs):
    return sum(xs) / len(xs) if xs else 0.0


def get_gap_type(r):
    obj = r.get("judge_obj") or {}
    return str(obj.get("dominant_gap_type") or "UNKNOWN")


def get_conf(r):
    obj = r.get("judge_obj") or {}
    try:
        return float(obj.get("confidence"))
    except Exception:
        return None


def summarize_group(rows, key):
    by = defaultdict(list)
    for r in rows:
        by[r.get(key)].append(r)

    lines = []
    lines.append(f"## Breakdown by {key}")
    lines.append("")
    lines.append("| key | n | recovery | tie/invalid | mean confidence |")
    lines.append("|---|---:|---:|---:|---:|")

    for k in sorted(by, key=lambda x: str(x)):
        xs = by[k]
        confs = [get_conf(r) for r in xs if get_conf(r) is not None]
        lines.append(
            f"| {k} | {len(xs)} | "
            f"{rate([float(r['correct']) for r in xs]):.3f} | "
            f"{rate([float(r['predicted'] in {'tie', 'invalid'}) for r in xs]):.3f} | "
            f"{rate(confs):.3f} |"
        )
    lines.append("")
    return lines


def both_by_triple(rows):
    by = defaultdict(dict)
    meta = {}
    for r in rows:
        by[r["triple_id"]][r["task_kind"]] = bool(r["correct"])
        meta[r["triple_id"]] = r

    out = []
    for tid, d in by.items():
        if "left_recovery" not in d or "right_recovery" not in d:
            continue
        m = meta[tid]
        out.append({
            "triple_id": tid,
            "idx": m["idx"],
            "split_iter": m.get("split_iter"),
            "num_edges_before_split": m.get("num_edges_before_split"),
            "left": d["left_recovery"],
            "right": d["right_recovery"],
            "both": d["left_recovery"] and d["right_recovery"],
        })
    return out


def failure_audit(rows, max_cases):
    by_task = {r["task_id"]: r for r in rows}
    triples = both_by_triple(rows)

    failed = [t for t in triples if not t["both"]]
    failed = sorted(failed, key=lambda x: (str(x["idx"]), str(x["split_iter"])))[:max_cases]

    lines = []
    lines.append("# Failure audit")
    lines.append("")
    lines.append(f"- failed triples shown: {len(failed)}")
    lines.append("")

    for t in failed:
        left = by_task.get(f"{t['triple_id']}__left")
        right = by_task.get(f"{t['triple_id']}__right")

        lines.append(f"## {t['triple_id']}")
        lines.append("")
        lines.append(f"- idx: {t['idx']}")
        lines.append(f"- split_iter: {t['split_iter']}")
        lines.append(f"- num_edges_before_split: {t['num_edges_before_split']}")
        lines.append(f"- left_recovery: {t['left']}")
        lines.append(f"- right_recovery: {t['right']}")
        lines.append("")

        for name, r in [("left", left), ("right", right)]:
            if not r:
                continue
            obj = r.get("judge_obj") or {}
            lines.append(f"### {name}")
            lines.append("")
            lines.append(f"- predicted: {r.get('predicted')}")
            lines.append(f"- expected: {r.get('expected')}")
            lines.append(f"- correct: {r.get('correct')}")
            lines.append(f"- dominant_gap_type: {obj.get('dominant_gap_type')}")
            lines.append(f"- confidence: {obj.get('confidence')}")
            why = obj.get("why_larger") or obj.get("why") or r.get("raw", "")
            lines.append(f"- why: {str(why).strip()[:800]}")
            lines.append("")

    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgments-path", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-failures", type=int, default=30)
    args = ap.parse_args()

    rows = read_jsonl(args.judgments_path)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Distance prompt recovery analysis")
    lines.append("")
    lines.append(f"- judgments_path: `{args.judgments_path}`")
    lines.append(f"- n_tasks: {len(rows)}")
    lines.append("")

    triples = both_by_triple(rows)
    lines.append("## Overall")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    lines.append(f"| task recovery | {rate([float(r['correct']) for r in rows]):.3f} |")
    lines.append(f"| tie/invalid | {rate([float(r['predicted'] in {'tie', 'invalid'}) for r in rows]):.3f} |")
    lines.append(f"| both recovery | {rate([float(t['both']) for t in triples]):.3f} |")
    lines.append("")

    for key in ["task_kind", "split_iter", "num_edges_before_split", "predicted"]:
        lines.extend(summarize_group(rows, key))

    by_gap = defaultdict(list)
    for r in rows:
        by_gap[get_gap_type(r)].append(r)

    lines.append("## Breakdown by dominant_gap_type")
    lines.append("")
    lines.append("| gap_type | n | recovery |")
    lines.append("|---|---:|---:|")
    for k, xs in sorted(by_gap.items()):
        lines.append(f"| {k} | {len(xs)} | {rate([float(r['correct']) for r in xs]):.3f} |")
    lines.append("")

    pred_counts = Counter(r["predicted"] for r in rows)
    lines.append("## Prediction distribution")
    lines.append("")
    lines.append("| predicted | n |")
    lines.append("|---|---:|")
    for k, v in sorted(pred_counts.items()):
        lines.append(f"| {k} | {v} |")
    lines.append("")

    analysis_path = out_dir / "analysis.md"
    analysis_path.write_text("\n".join(lines))

    audit_path = out_dir / "failure_audit.md"
    audit_path.write_text("\n".join(failure_audit(rows, args.max_failures)))

    print("[wrote]", analysis_path)
    print("[wrote]", audit_path)
    print(analysis_path.read_text())


if __name__ == "__main__":
    main()
