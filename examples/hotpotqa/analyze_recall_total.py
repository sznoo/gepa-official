# /home/jinwoo/gepa-official/examples/hotpotqa/analyze_recall_total.py
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def candidate_hash(candidate: dict[str, str]) -> str:
    s = json.dumps(candidate, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def example_key(row: dict[str, Any]) -> str:
    exid = row.get("example_id")
    if exid not in (None, "", "None"):
        return f"id::{exid}"
    return "q::" + str(row.get("question", "")).strip()


def short(x: Any, n: int = 500) -> str:
    s = "" if x is None else str(x)
    s = s.replace("\n", " ").strip()
    return s if len(s) <= n else s[:n] + " ..."


def as_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def f3(x: Any) -> str:
    try:
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


def md_escape(x: Any) -> str:
    return short(x, 160).replace("|", "\\|")


def fenced_text(text: Any) -> str:
    # Four-backtick fence prevents nested triple-backtick instructions from breaking markdown.
    return "````text\n" + ("" if text is None else str(text)) + "\n````"


def bucket_name(delta_recall: float, delta_em: float) -> str:
    eps = 1e-9
    if delta_recall > eps and delta_em > eps:
        return "recall_up_em_up"
    if delta_recall > eps and abs(delta_em) <= eps:
        return "recall_up_em_same"
    if delta_recall > eps and delta_em < -eps:
        return "recall_up_em_down"
    if abs(delta_recall) <= eps and delta_em > eps:
        return "recall_same_em_up"
    if abs(delta_recall) <= eps and abs(delta_em) <= eps:
        return "recall_same_em_same"
    if abs(delta_recall) <= eps and delta_em < -eps:
        return "recall_same_em_down"
    if delta_recall < -eps and delta_em > eps:
        return "recall_down_em_up"
    if delta_recall < -eps and abs(delta_em) <= eps:
        return "recall_down_em_same"
    return "recall_down_em_down"


def recall_direction(delta_recall: float) -> str:
    eps = 1e-9
    if delta_recall > eps:
        return "↑"
    if delta_recall < -eps:
        return "↓"
    return "="


def em_direction(delta_em: float) -> str:
    eps = 1e-9
    if delta_em > eps:
        return "↑"
    if delta_em < -eps:
        return "↓"
    return "="


def get_rollout_map(rollouts: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    """
    Keep one rollout per (candidate_hash, example_key).
    If duplicates exist, keep the last one in log order.
    """
    out = {}
    for i, row in enumerate(rollouts):
        h = row.get("candidate_hash")
        if not h:
            continue
        if not row.get("instructions"):
            continue
        key = (h, example_key(row))
        rr = dict(row)
        rr["_line_idx"] = i
        out[key] = rr
    return out


def get_old_rows_for_hash(
    rollout_map: dict[tuple[str, str], dict[str, Any]],
    old_hash: str,
) -> list[dict[str, Any]]:
    return [row for (h, _), row in rollout_map.items() if h == old_hash and row.get("instructions")]


def infer_new_candidate(old_candidate: dict[str, str], component: str, new_instruction: str) -> dict[str, str]:
    new_candidate = dict(old_candidate)
    new_candidate[component] = new_instruction
    return new_candidate


def build_case(
    proposal_idx: int,
    proposal: dict[str, Any],
    old: dict[str, Any],
    new: dict[str, Any],
    old_candidate: dict[str, str],
    new_hash: str,
) -> dict[str, Any]:
    component = proposal.get("component")
    old_recall = as_float(old.get("support_recall_total"))
    new_recall = as_float(new.get("support_recall_total"))
    old_em = as_float(old.get("score"))
    new_em = as_float(new.get("score"))

    delta_recall = new_recall - old_recall
    delta_em = new_em - old_em

    return {
        "proposal_idx": proposal_idx,
        "component": component,
        "old_hash": proposal.get("candidate_hash"),
        "new_hash": new_hash,
        "example_key": example_key(old),
        "bucket": bucket_name(delta_recall, delta_em),
        "recall_dir": recall_direction(delta_recall),
        "em_dir": em_direction(delta_em),
        "old_recall": old_recall,
        "new_recall": new_recall,
        "delta_recall": delta_recall,
        "old_em": old_em,
        "new_em": new_em,
        "delta_em": delta_em,
        "question": old.get("question"),
        "gold_answer": old.get("gold_answer"),
        "gold_support_titles": old.get("gold_support_titles"),
        "old_hop1_titles": old.get("hop1_titles"),
        "old_hop2_titles": old.get("hop2_titles"),
        "new_hop1_titles": new.get("hop1_titles"),
        "new_hop2_titles": new.get("hop2_titles"),
        "old_new_support_titles_hop2": old.get("new_support_titles_hop2"),
        "new_new_support_titles_hop2": new.get("new_support_titles_hop2"),
        "old_missing_titles_after_hop2": old.get("missing_titles_after_hop2"),
        "new_missing_titles_after_hop2": new.get("missing_titles_after_hop2"),
        "old_summary_1": old.get("summary_1"),
        "new_summary_1": new.get("summary_1"),
        "old_hop2_query": old.get("hop2_query"),
        "new_hop2_query": new.get("hop2_query"),
        "old_summary_2": old.get("summary_2"),
        "new_summary_2": new.get("summary_2"),
        "old_pred_answer": old.get("pred_answer"),
        "new_pred_answer": new.get("pred_answer"),
        "old_instruction": old_candidate.get(component),
        "new_instruction": proposal.get("new_instruction"),
    }


def build_updates(
    proposals: list[dict[str, Any]],
    rollout_map: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    updates = []

    for proposal_idx, proposal in enumerate(proposals):
        component = proposal.get("component")
        old_hash = proposal.get("candidate_hash")
        new_instruction = proposal.get("new_instruction")

        if not component or not old_hash or new_instruction is None:
            continue

        old_rows = get_old_rows_for_hash(rollout_map, old_hash)
        if not old_rows:
            updates.append({
                "proposal_idx": proposal_idx,
                "component": component,
                "old_hash": old_hash,
                "new_hash": None,
                "status": "unmatched_old_hash",
                "cases": [],
                "proposal": proposal,
            })
            continue

        old_candidate = dict(old_rows[0]["instructions"])
        if component not in old_candidate:
            updates.append({
                "proposal_idx": proposal_idx,
                "component": component,
                "old_hash": old_hash,
                "new_hash": None,
                "status": "component_not_in_candidate",
                "cases": [],
                "proposal": proposal,
            })
            continue

        new_candidate = infer_new_candidate(old_candidate, component, new_instruction)
        new_hash = candidate_hash(new_candidate)

        old_by_ex = {example_key(row): row for row in old_rows}
        new_by_ex = {
            ex_key: row
            for (h, ex_key), row in rollout_map.items()
            if h == new_hash
        }

        shared_keys = sorted(set(old_by_ex) & set(new_by_ex))
        cases = [
            build_case(
                proposal_idx=proposal_idx,
                proposal=proposal,
                old=old_by_ex[ex_key],
                new=new_by_ex[ex_key],
                old_candidate=old_candidate,
                new_hash=new_hash,
            )
            for ex_key in shared_keys
        ]

        updates.append({
            "proposal_idx": proposal_idx,
            "component": component,
            "old_hash": old_hash,
            "new_hash": new_hash,
            "status": "matched" if cases else "no_shared_rollouts",
            "old_instruction": old_candidate.get(component),
            "new_instruction": new_instruction,
            "proposal": proposal,
            "cases": cases,
        })

    return updates


def summarize_update(update: dict[str, Any]) -> dict[str, Any]:
    cases = update.get("cases", [])
    n = len(cases)
    if not cases:
        return {
            "proposal_idx": update.get("proposal_idx"),
            "component": update.get("component"),
            "old_hash": update.get("old_hash"),
            "new_hash": update.get("new_hash"),
            "status": update.get("status"),
            "num_pairs": 0,
            "mean_delta_recall": "",
            "mean_delta_em": "",
            "recall_up": 0,
            "recall_same": 0,
            "recall_down": 0,
            "em_up": 0,
            "em_same": 0,
            "em_down": 0,
        }

    return {
        "proposal_idx": update.get("proposal_idx"),
        "component": update.get("component"),
        "old_hash": update.get("old_hash"),
        "new_hash": update.get("new_hash"),
        "status": update.get("status"),
        "num_pairs": n,
        "mean_delta_recall": sum(c["delta_recall"] for c in cases) / n,
        "mean_delta_em": sum(c["delta_em"] for c in cases) / n,
        "recall_up": sum(c["delta_recall"] > 1e-9 for c in cases),
        "recall_same": sum(abs(c["delta_recall"]) <= 1e-9 for c in cases),
        "recall_down": sum(c["delta_recall"] < -1e-9 for c in cases),
        "em_up": sum(c["delta_em"] > 1e-9 for c in cases),
        "em_same": sum(abs(c["delta_em"]) <= 1e-9 for c in cases),
        "em_down": sum(c["delta_em"] < -1e-9 for c in cases),
    }


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._\n"

    lines = []
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(columns)) + " |")

    for row in rows:
        vals = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append(f"{val:.3f}")
            else:
                vals.append(md_escape(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def render_case_table(cases: list[dict[str, Any]]) -> str:
    rows = []
    for i, c in enumerate(cases, 1):
        rows.append({
            "#": i,
            "bucket": c["bucket"],
            "R": f'{c["old_recall"]:.1f}->{c["new_recall"]:.1f} ({c["recall_dir"]})',
            "EM": f'{c["old_em"]:.1f}->{c["new_em"]:.1f} ({c["em_dir"]})',
            "gold": c.get("gold_support_titles"),
            "new_support_hop2": c.get("new_new_support_titles_hop2"),
            "missing_after": c.get("new_missing_titles_after_hop2"),
            "old_query": c.get("old_hop2_query"),
            "new_query": c.get("new_hop2_query"),
            "question": c.get("question"),
        })

    return md_table(
        rows,
        ["#", "bucket", "R", "EM", "gold", "new_support_hop2", "missing_after", "old_query", "new_query", "question"],
    )


def render_case_detail(case: dict[str, Any], idx: int) -> str:
    return f"""
#### Case {idx}: {case["bucket"]}

- Recall: `{case["old_recall"]:.3f} -> {case["new_recall"]:.3f}` / Δ `{case["delta_recall"]:.3f}`
- EM: `{case["old_em"]:.3f} -> {case["new_em"]:.3f}` / Δ `{case["delta_em"]:.3f}`

**Question:** {case["question"]}

**Gold answer:** `{case["gold_answer"]}`

**Gold support titles:** `{case["gold_support_titles"]}`

**Old hop2 query:**  
> {short(case["old_hop2_query"], 700)}

**New hop2 query:**  
> {short(case["new_hop2_query"], 700)}

**Old hop2 titles:** `{case["old_hop2_titles"]}`

**New hop2 titles:** `{case["new_hop2_titles"]}`

**Old new-support-titles-hop2:** `{case["old_new_support_titles_hop2"]}`

**New new-support-titles-hop2:** `{case["new_new_support_titles_hop2"]}`

**Old missing after hop2:** `{case["old_missing_titles_after_hop2"]}`

**New missing after hop2:** `{case["new_missing_titles_after_hop2"]}`

**Old summary_1:**  
> {short(case["old_summary_1"], 900)}

**New summary_1:**  
> {short(case["new_summary_1"], 900)}

**Old summary_2:**  
> {short(case["old_summary_2"], 900)}

**New summary_2:**  
> {short(case["new_summary_2"], 900)}

**Old answer:** `{case["old_pred_answer"]}`

**New answer:** `{case["new_pred_answer"]}`
"""


def sort_cases_for_update(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Show changed examples first, then stable examples.
    # Within changed examples, prioritize recall-up, recall-down, then EM-only.
    def key(c: dict[str, Any]):
        changed = abs(c["delta_recall"]) > 1e-9 or abs(c["delta_em"]) > 1e-9
        return (
            0 if changed else 1,
            -c["delta_recall"],
            -c["delta_em"],
            str(c.get("question", "")),
        )

    return sorted(cases, key=key)


def render_update(update: dict[str, Any], max_cases_per_update: int | None) -> str:
    cases = sort_cases_for_update(update.get("cases", []))
    summary = summarize_update(update)
    bucket_counts = Counter(c["bucket"] for c in cases)

    lines = []
    lines.append(
        f'## Update {update["proposal_idx"]}: `{update["component"]}`\n'
    )
    lines.append(f'- status: `{update.get("status")}`')
    lines.append(f'- old_hash: `{update.get("old_hash")}`')
    lines.append(f'- new_hash: `{update.get("new_hash")}`')
    lines.append(f'- pairs: `{summary["num_pairs"]}`')
    lines.append(f'- mean Δrecall: `{f3(summary["mean_delta_recall"])}`')
    lines.append(f'- mean ΔEM: `{f3(summary["mean_delta_em"])}`')
    lines.append(
        f'- recall up/same/down: `{summary["recall_up"]}/{summary["recall_same"]}/{summary["recall_down"]}`'
    )
    lines.append(
        f'- EM up/same/down: `{summary["em_up"]}/{summary["em_same"]}/{summary["em_down"]}`\n'
    )

    lines.append("### Bucket counts within this update\n")
    bucket_rows = [{"bucket": k, "count": v} for k, v in sorted(bucket_counts.items())]
    lines.append(md_table(bucket_rows, ["bucket", "count"]))

    lines.append("<details>")
    lines.append("<summary>Instruction diff source</summary>\n")
    lines.append("**Old instruction**\n")
    lines.append(fenced_text(update.get("old_instruction")))
    lines.append("\n**New instruction**\n")
    lines.append(fenced_text(update.get("new_instruction")))
    lines.append("\n</details>\n")

    if cases:
        lines.append("### Batch-level comparison table\n")
        shown_cases = cases if max_cases_per_update is None else cases[:max_cases_per_update]
        lines.append(render_case_table(shown_cases))

        if max_cases_per_update is not None and len(cases) > max_cases_per_update:
            lines.append(
                f"\n_Only first {max_cases_per_update} / {len(cases)} cases shown. "
                "Increase `--max-cases-per-update` to show more._\n"
            )

        lines.append("### Case details\n")
        for i, case in enumerate(shown_cases, 1):
            lines.append(render_case_detail(case, i))
    else:
        lines.append("_No matched before/after rollout pairs for this update._\n")

    return "\n".join(lines)


def render_markdown(updates: list[dict[str, Any]], max_cases_per_update: int | None) -> str:
    summaries = [summarize_update(u) for u in updates]

    total_cases = sum(len(u.get("cases", [])) for u in updates)
    global_bucket_counts = Counter()
    for u in updates:
        global_bucket_counts.update(c["bucket"] for c in u.get("cases", []))

    lines = []
    lines.append("# HotpotQA GEPA Support Recall Comparison by Update\n")
    lines.append(
        "This report reconstructs old/new candidate pairs from `proposal_events.jsonl` "
        "and `rollout_traces.jsonl`, then groups all paired rollout cases by proposal/update.\n"
    )
    lines.append(
        "Current status: all proposals are included. Accepted/rejected filtering is not applied unless the log contains such metadata.\n"
    )

    lines.append("## Global summary\n")
    lines.append(f"- updates: `{len(updates)}`")
    lines.append(f"- matched rollout cases: `{total_cases}`\n")

    lines.append("### Global bucket counts\n")
    bucket_rows = [
        {"bucket": k, "count": v, "ratio": v / total_cases if total_cases else 0.0}
        for k, v in sorted(global_bucket_counts.items())
    ]
    lines.append(md_table(bucket_rows, ["bucket", "count", "ratio"]))

    lines.append("## Update-level overview\n")
    lines.append(
        md_table(
            summaries,
            [
                "proposal_idx",
                "component",
                "old_hash",
                "new_hash",
                "status",
                "num_pairs",
                "mean_delta_recall",
                "mean_delta_em",
                "recall_up",
                "recall_same",
                "recall_down",
                "em_up",
                "em_same",
                "em_down",
            ],
        )
    )

    for update in updates:
        lines.append(render_update(update, max_cases_per_update=max_cases_per_update))

    return "\n".join(lines)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="/home/jinwoo/gepa-official/outputs/hotpotqa_smoke")
    parser.add_argument("--output", default=None)
    parser.add_argument(
        "--max-cases-per-update",
        type=int,
        default=50,
        help="Max detailed cases shown per update. Use -1 to show all cases.",
    )
    parser.add_argument(
        "--write-cases-jsonl",
        action="store_true",
        help="Also save flattened per-case comparison JSONL.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    analysis_dir = run_dir / "analysis"

    proposal_path = analysis_dir / "proposal_events.jsonl"
    rollout_path = analysis_dir / "rollout_traces.jsonl"

    proposals = load_jsonl(proposal_path)
    rollouts = load_jsonl(rollout_path)

    rollout_map = get_rollout_map(rollouts)
    updates = build_updates(proposals, rollout_map)

    max_cases = None if args.max_cases_per_update < 0 else args.max_cases_per_update

    output_path = Path(args.output) if args.output else analysis_dir / "recall_total_by_update.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    md = render_markdown(updates, max_cases_per_update=max_cases)
    output_path.write_text(md, encoding="utf-8")

    updates_dir = analysis_dir / "updates"
    updates_dir.mkdir(parents=True, exist_ok=True)

    index_rows = []
    for update in updates:
        proposal_idx = update.get("proposal_idx")
        component = str(update.get("component", "unknown"))
        component_slug = (
            component.replace(".", "_")
            .replace("/", "_")
            .replace(":", "_")
            .replace(" ", "_")
        )
        fname = f"update_{int(proposal_idx):03d}_{component_slug}.md"
        update_path = updates_dir / fname

        update_md = (
            f"# Update {proposal_idx}: `{component}`\\n\\n"
            + render_update(update, max_cases_per_update=max_cases)
        )
        update_path.write_text(update_md, encoding="utf-8")

        row = summarize_update(update)
        row["file"] = f"updates/{fname}"
        index_rows.append(row)

    index_md = "# HotpotQA GEPA Update Index\\n\\n"
    index_md += md_table(
        index_rows,
        [
            "proposal_idx",
            "component",
            "file",
            "status",
            "num_pairs",
            "mean_delta_recall",
            "mean_delta_em",
            "recall_up",
            "recall_same",
            "recall_down",
            "em_up",
            "em_same",
            "em_down",
        ],
    )
    (analysis_dir / "updates_index.md").write_text(index_md, encoding="utf-8")

    if args.write_cases_jsonl:
        all_cases = []
        for update in updates:
            all_cases.extend(update.get("cases", []))
        write_jsonl(analysis_dir / "recall_total_cases_by_update.jsonl", all_cases)

    print(f"Saved markdown: {output_path}")
    print(f"Updates: {len(updates)}")
    print(f"Matched cases: {sum(len(u.get('cases', [])) for u in updates)}")
    for s in [summarize_update(u) for u in updates]:
        print(
            f"proposal={s['proposal_idx']} component={s['component']} "
            f"pairs={s['num_pairs']} ΔR={f3(s['mean_delta_recall'])} ΔEM={f3(s['mean_delta_em'])} "
            f"R(up/same/down)={s['recall_up']}/{s['recall_same']}/{s['recall_down']}"
        )


if __name__ == "__main__":
    main()
