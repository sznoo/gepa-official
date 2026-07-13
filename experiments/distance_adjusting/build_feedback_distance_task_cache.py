#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


PREFERRED_KEYS = [
    "trigger",
    "failure_mode",
    "keep",
    "add_or_restore",
    "remove_or_avoid",
    "query_shape",
    "why_this_moves_retrieval",
    "feedback",
    "text",
]


def read_jsonl(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def get_seg_idx(iteration):
    for k in [
        "selected_segment_for_next_split",
        "selected_segment_index",
        "selected_seg_idx",
        "seg_idx",
    ]:
        if k not in iteration:
            continue
        v = iteration[k]
        if isinstance(v, dict):
            for kk in ["segment_index", "index", "seg_idx", "selected_segment_index"]:
                if kk in v:
                    return int(v[kk])
        return int(v)
    return None


def pgrad_to_text(pg):
    if pg is None:
        return ""
    if isinstance(pg, str):
        return pg.strip()
    if isinstance(pg, list):
        return "\n".join(str(x) for x in pg).strip()
    if isinstance(pg, dict):
        lines = []

        lower_map = {str(k).lower(): k for k in pg.keys()}
        used = set()

        for lk in PREFERRED_KEYS:
            if lk in lower_map:
                k = lower_map[lk]
                v = pg.get(k)
                if v not in [None, "", [], {}]:
                    lines.append(f"{k}: {format_value(v)}")
                    used.add(k)

        for k, v in pg.items():
            if k in used:
                continue
            if v not in [None, "", [], {}]:
                lines.append(f"{k}: {format_value(v)}")

        return "\n".join(lines).strip()

    return str(pg).strip()


def format_value(v):
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def state_name(states, i):
    if not isinstance(states, list) or i < 0 or i >= len(states):
        return f"state[{i}]"
    s = states[i]
    if isinstance(s, dict):
        return s.get("name") or f"state[{i}]"
    return f"state[{i}]"


def make_feedback_segment(kind, idx, split_iter, seg_idx, edge_from, edge_to, pgrad):
    return {
        "feedback_kind": kind,
        "idx": idx,
        "split_iter": split_iter,
        "seg_idx": seg_idx,
        "edge": f"{edge_from} -> {edge_to}",
        "feedback_text": pgrad_to_text(pgrad),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rtrace-aux-path", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--prefix", default="full19_feedback")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    rows = []
    skipped = []

    for row in read_jsonl(args.rtrace_aux_path):
        idx = str(row.get("idx"))
        question = row.get("question", "")
        summary_1 = row.get("summary_1", "")
        iterations = row.get("iterations") or []

        for k in range(len(iterations) - 1):
            it = iterations[k]
            nxt = iterations[k + 1]
            seg_idx = get_seg_idx(it)

            if seg_idx is None:
                skipped.append((idx, k, "no selected segment"))
                continue

            full_pgrads = it.get("pgrads") or []
            sub_pgrads = nxt.get("pgrads") or []
            states_before = it.get("states") or []
            states_after = nxt.get("states") or []

            if seg_idx >= len(full_pgrads):
                skipped.append((idx, k, f"full pgrad missing seg={seg_idx} len={len(full_pgrads)}"))
                continue
            if seg_idx + 1 >= len(sub_pgrads):
                skipped.append((idx, k, f"sub pgrad missing seg={seg_idx} len={len(sub_pgrads)}"))
                continue

            midpoint_id = f"{idx}__split{k}__seg{seg_idx}__feedback"

            full_seg = make_feedback_segment(
                "full_edge_feedback",
                idx,
                k,
                seg_idx,
                state_name(states_before, seg_idx),
                state_name(states_before, seg_idx + 1),
                full_pgrads[seg_idx],
            )
            left_seg = make_feedback_segment(
                "left_subedge_feedback",
                idx,
                k,
                seg_idx,
                state_name(states_after, seg_idx),
                state_name(states_after, seg_idx + 1),
                sub_pgrads[seg_idx],
            )
            right_seg = make_feedback_segment(
                "right_subedge_feedback",
                idx,
                k,
                seg_idx,
                state_name(states_after, seg_idx + 1),
                state_name(states_after, seg_idx + 2),
                sub_pgrads[seg_idx + 1],
            )

            base = {
                "idx": idx,
                "question": question,
                "summary_1": summary_1,
                "split_iter": k,
                "seg_idx": seg_idx,
                "midpoint_id": midpoint_id,
                "distance_object": "prompt_feedback_pgrad",
            }

            rows.append({
                **base,
                "task_id": midpoint_id + "__left",
                "task_kind": "left_recovery",
                "full_segment": full_seg,
                "sub_segment": left_seg,
            })
            rows.append({
                **base,
                "task_id": midpoint_id + "__right",
                "task_kind": "right_recovery",
                "full_segment": full_seg,
                "sub_segment": right_seg,
            })

    tasks_path = out_dir / f"{args.prefix}_distance_tasks.jsonl"
    summary_path = out_dir / f"{args.prefix}_cache_summary.json"

    write_jsonl(tasks_path, rows)
    summary = {
        "rtrace_aux_path": args.rtrace_aux_path,
        "tasks_path": str(tasks_path),
        "n_tasks": len(rows),
        "n_midpoint_feedback_triples": len(rows) // 2,
        "n_skipped": len(skipped),
        "skipped_preview": skipped[:20],
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
