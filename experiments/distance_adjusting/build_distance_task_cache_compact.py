#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def read_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def state_name(s):
    if isinstance(s, dict):
        return str(s.get("name") or s.get("state_id") or s.get("kind") or "UNKNOWN")
    return "UNKNOWN"


def compact_state_for_prompt(s):
    if not isinstance(s, dict):
        return {}
    return {
        "name": s.get("name"),
        "kind": s.get("kind"),
        "query": s.get("query") if s.get("query_visible") else "",
        "retrieved_titles": s.get("retrieved_titles") or [],
        "retrieval_focus": s.get("retrieval_focus") or "",
        "anchors": s.get("anchors") or [],
        "bridge_clues": s.get("bridge_clues") or [],
        "noisy_or_distracting_clues": s.get("noisy_or_distracting_clues") or [],
        "expected_evidence_type": s.get("expected_evidence_type") or "",
        "query_shape_implication": s.get("query_shape_implication") or "",
    }


def extract_triples(aux_rows):
    triples = []

    for row in aux_rows:
        idx = str(row["idx"])
        question = row.get("question", "")
        summary_1 = row.get("summary_1", "")

        for it in row.get("iterations", []):
            if "selected_segment_for_next_split" not in it:
                continue
            if "inserted_mid_state" not in it:
                continue

            states = it.get("states") or []
            seg_idx = safe_int(it.get("selected_segment_for_next_split"), 0)
            if seg_idx < 0 or seg_idx + 1 >= len(states):
                continue

            left = states[seg_idx]
            mid = it["inserted_mid_state"]
            right = states[seg_idx + 1]

            triple_id = f"{idx}__split{it.get('split_iter')}__seg{seg_idx}"

            triples.append({
                "triple_id": triple_id,
                "idx": idx,
                "question": question,
                "summary_1": summary_1,
                "split_iter": it.get("split_iter"),
                "num_edges_before_split": it.get("num_edges"),
                "selected_segment_for_next_split": seg_idx,
                "R_i_name": state_name(left),
                "R_mid_name": state_name(mid),
                "R_next_name": state_name(right),
                "R_i": compact_state_for_prompt(left),
                "R_mid": compact_state_for_prompt(mid),
                "R_next": compact_state_for_prompt(right),
                "max_info": it.get("max_info", {}),
            })

    return triples


def build_tasks(triples):
    tasks = []

    for t in triples:
        full_segment = {
            "from_state": t["R_i"],
            "to_state": t["R_next"],
        }

        left_sub = {
            "from_state": t["R_i"],
            "to_state": t["R_mid"],
        }

        right_sub = {
            "from_state": t["R_mid"],
            "to_state": t["R_next"],
        }

        base = {
            "triple_id": t["triple_id"],
            "idx": t["idx"],
            "question": t["question"],
            "summary_1": t["summary_1"],
            "split_iter": t["split_iter"],
            "num_edges_before_split": t["num_edges_before_split"],
            "selected_segment_for_next_split": t["selected_segment_for_next_split"],
            "R_i_name": t["R_i_name"],
            "R_mid_name": t["R_mid_name"],
            "R_next_name": t["R_next_name"],
        }

        tasks.append({
            **base,
            "task_id": f"{t['triple_id']}__left",
            "task_kind": "left_recovery",
            "definition": "full edge R_i -> R_next should be larger than sub-edge R_i -> R_mid",
            "sub_segment": left_sub,
            "full_segment": full_segment,
        })

        tasks.append({
            **base,
            "task_id": f"{t['triple_id']}__right",
            "task_kind": "right_recovery",
            "definition": "full edge R_i -> R_next should be larger than sub-edge R_mid -> R_next",
            "sub_segment": right_sub,
            "full_segment": full_segment,
        })

    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rtrace-aux-path", required=True)
    ap.add_argument("--out-dir", default="experiments/distance_adjusting/cache")
    ap.add_argument("--prefix", default="full19")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    aux_rows = read_jsonl(args.rtrace_aux_path)
    triples = extract_triples(aux_rows)
    tasks = build_tasks(triples)

    triples_path = out_dir / f"{args.prefix}_midpoint_triples.jsonl"
    tasks_path = out_dir / f"{args.prefix}_distance_tasks.jsonl"
    summary_path = out_dir / f"{args.prefix}_cache_summary.json"

    write_jsonl(triples_path, triples)
    write_jsonl(tasks_path, tasks)

    summary = {
        "rtrace_aux_path": args.rtrace_aux_path,
        "n_aux_rows": len(aux_rows),
        "n_midpoint_triples": len(triples),
        "n_distance_tasks": len(tasks),
        "triples_path": str(triples_path),
        "tasks_path": str(tasks_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
