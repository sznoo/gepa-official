# /home/jinwoo/gepa-official/experiments/prompt_update/scripts/generate_directional_delta_p.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import sys
import traceback
from pathlib import Path
from typing import Any

from tqdm import tqdm


# This script intentionally reuses the old delta-granularity prompt-update path:
#   directional_transition -> synthetic trace_row/arm
#   -> old generate_updated_prompt(...)
#
# Therefore the prompt updater system and payload style remain aligned with:
#   experiments/feedback_distance_v2/scripts/run_delta_granularity_prompt_update.py


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))


DELTA_SCRIPT = Path("experiments/feedback_distance_v2/scripts/run_delta_granularity_prompt_update.py").resolve()
spec = importlib.util.spec_from_file_location("delta_granularity", DELTA_SCRIPT)
delta = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(delta)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.open("r", encoding="utf-8") if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def truncate(x: Any, n: int) -> str:
    s = str(x or "")
    return s if len(s) <= n else s[:n] + "..."


def docs_to_old_format(state: dict[str, Any]) -> list[str]:
    """Old state_compact expects retrieved_docs as list[str]."""
    docs = state.get("retrieved_docs") or []
    out = []

    for d in docs[:7]:
        if isinstance(d, dict):
            title = str(d.get("title") or "")
            text = str(d.get("text") or "")
            out.append((title + "\n" + text).strip())
        else:
            out.append(str(d))

    # Semantic damaged endpoints do not have actual docs.
    # Keep a short pseudo-doc list so old state_compact can still carry endpoint semantics.
    if not out and state.get("expected_retrieved_titles"):
        for t in state.get("expected_retrieved_titles")[:7]:
            out.append(f"EXPECTED_TITLE: {t}")

    return out


def normalize_state_for_old_delta(
    *,
    state: dict[str, Any],
    state_id: str,
    kind: str,
) -> dict[str, Any]:
    """Convert our directional endpoint schema into old delta trace state schema."""
    titles = (
        state.get("retrieved_titles")
        or state.get("expected_retrieved_titles")
        or []
    )

    return {
        "state_id": state_id,
        "kind": kind,
        "query": state.get("query"),
        "retrieved_titles": titles,
        "retrieved_docs": docs_to_old_format(state),
        "summary_2": state.get("summary_2"),
        "support_recall_hop2": state.get("support_recall_hop2"),
        "missing_recovery_rate": state.get("missing_recovery_rate"),
        "strong_answer": state.get("strong_answer"),
        "strong_score": state.get("strong_score"),
        "is_semantic_endpoint": bool(state.get("is_semantic_endpoint")),
        "is_actual_bm25_result": state.get("is_actual_bm25_result", True),
    }


def make_synthetic_trace_row(t: dict[str, Any]) -> dict[str, Any]:
    """Make a trace_row compatible with old generate_updated_prompt()."""
    source = {
        "question": t.get("question"),
        "summary_1": t.get("summary_1"),
        "gold_answer": t.get("gold_answer"),
        "gold_support_titles": t.get("gold_support_titles") or [],
        "missing_after_hop1": None,
        "missing_after_hop2": None,
    }

    left = normalize_state_for_old_delta(
        state=t["source_R"],
        state_id=f"{t['transition_id']}:source",
        kind=t.get("source_R_role") or "source",
    )
    right = normalize_state_for_old_delta(
        state=t["target_R"],
        state_id=f"{t['transition_id']}:target",
        kind=t.get("target_R_role") or "target",
    )

    return {
        "idx": t.get("case_id"),
        "case_id": t.get("case_id"),
        "source_row": source,
        "trace": [left, right],
        "directional_transition": t,
    }


def make_old_arm(t: dict[str, Any], info_mode: str) -> dict[str, Any]:
    """Single endpoint edge arm, matching old arm schema."""
    return {
        "arm_id": f"{t['transition_family']}_{info_mode}",
        "arm_family": "directional_endpoint",
        "info_mode": info_mode,
        "edge_pairs": [(0, 1)],
        "transition_id": t["transition_id"],
        "direction_label": t.get("direction_label"),
        "polarity": t.get("polarity"),
    }


def make_delta_q(t: dict[str, Any]) -> dict[str, Any]:
    """Materialize the directional query delta used inside Rq mode."""
    return {
        "source_query": t.get("source_R", {}).get("query"),
        "target_query": t.get("target_R", {}).get("query"),
        "direction_label": t.get("direction_label"),
        "polarity": t.get("polarity"),
        "note": "This is the directional q-pair inside the old Rq delta observation; not an additive vector.",
    }


def run_one(task: tuple) -> dict[str, Any]:
    (
        t,
        refs,
        model,
        temperature,
        updater_max_tokens,
        retries,
        info_mode,
    ) = task

    trace_row = make_synthetic_trace_row(t)
    arm = make_old_arm(t, info_mode=info_mode)

    upd = delta.generate_updated_prompt(
        model=model,
        temperature=temperature,
        max_tokens=updater_max_tokens,
        retries=retries,
        current_prompt=refs["current_query_prompt"],
        trace_row=trace_row,
        arm=arm,
    )

    return {
        "row_type": "directional_delta_p",
        "transition_id": t["transition_id"],
        "batch_id": t.get("batch_id"),
        "case_id": t.get("case_id"),
        "bucket": t.get("bucket"),
        "transition_family": t.get("transition_family"),
        "direction_label": t.get("direction_label"),
        "polarity": t.get("polarity"),
        "info_mode": info_mode,
        "arm_id": arm["arm_id"],
        "arm_family": arm["arm_family"],
        "edge_pairs": arm["edge_pairs"],

        # Directional Δq material is the source/target query pair.
        "delta_q": make_delta_q(t),

        # Directional Δp material is the old updater's updated prompt.
        # For polarity=avoid, this is a harmful/downhill prompt-update anchor to avoid later.
        "samplewise_updated_prompt": upd["updated_prompt"],
        "samplewise_prompt_rationale": upd.get("rationale"),
        "prompt_update_raw": upd.get("raw"),
        "parse_failed": upd.get("parse_failed", False),

        # Keep enough endpoint metadata for later batch evidence assembly.
        "source_R_role": t.get("source_R_role"),
        "target_R_role": t.get("target_R_role"),
        "source_R": t.get("source_R"),
        "target_R": t.get("target_R"),
        "delta_R_prime": t.get("delta_R_prime"),
        "matched_w_case_id": t.get("matched_w_case_id"),
        "question": t.get("question"),
        "summary_1": t.get("summary_1"),
        "gold_answer": t.get("gold_answer"),
        "gold_support_titles": t.get("gold_support_titles") or [],
    }


def run_one_safe(task: tuple) -> dict[str, Any]:
    t = task[0]
    info_mode = task[-1]
    try:
        return run_one(task)
    except Exception as e:
        return {
            "row_type": "directional_delta_p",
            "error": True,
            "transition_id": t.get("transition_id"),
            "batch_id": t.get("batch_id"),
            "case_id": t.get("case_id"),
            "bucket": t.get("bucket"),
            "transition_family": t.get("transition_family"),
            "direction_label": t.get("direction_label"),
            "polarity": t.get("polarity"),
            "info_mode": info_mode,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()

    ap.add_argument("--directional-transitions", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_directional_transitions.jsonl"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/prompt_update/cache/fixed_prompt_config.json"))
    ap.add_argument("--final-answerer-refs", type=Path, default=Path("experiments/prompt_update/cache/final_answerer_refs.json"))
    ap.add_argument("--out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_directional_delta_p.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_directional_delta_p.summary.json"))

    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--updater-max-tokens", type=int, default=4096)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--num-threads", type=int, default=8)

    # Keep Rq by default because this is the closest to old single_edge_Rq / endpoint_Rq.
    ap.add_argument("--info-mode", type=str, default="Rq", choices=["Rq", "R_only"])
    ap.add_argument("--overwrite", action="store_true")

    return ap.parse_args()


def main() -> None:
    args = parse_args()

    transitions = read_jsonl(args.directional_transitions)
    fixed_cfg = read_json(args.fixed_prompt_config)
    final_refs = read_json(args.final_answerer_refs)

    refs = {
        **final_refs,
        "summarize2_prompt": fixed_cfg["prompt_candidate"]["prompts"]["summarize2.predict"],
        "current_query_prompt": fixed_cfg["prompt_candidate"]["prompts"]["create_query_hop2.predict"],
    }

    if args.overwrite and args.out.exists():
        args.out.unlink()

    done = set()
    existing = []
    if args.out.exists():
        existing = read_jsonl(args.out)
        for r in existing:
            if not r.get("error"):
                done.add((r.get("transition_id"), r.get("info_mode")))

    tasks = []
    for t in transitions:
        key = (t.get("transition_id"), args.info_mode)
        if key in done:
            continue
        tasks.append((
            t,
            refs,
            args.model,
            args.temperature,
            args.updater_max_tokens,
            args.retries,
            args.info_mode,
        ))

    print("[info] directional transitions:", len(transitions))
    print("[info] pending:", len(tasks))
    print("[info] existing:", len(existing))
    print("[info] info_mode:", args.info_mode)

    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(run_one_safe, t) for t in tasks]
        for fut in tqdm(cf.as_completed(futs), total=len(futs), desc="directional delta_p"):
            append_jsonl(args.out, fut.result())

    rows = read_jsonl(args.out)
    ok = [r for r in rows if not r.get("error")]
    err = [r for r in rows if r.get("error")]

    summary = {
        "script": "generate_directional_delta_p.py",
        "old_delta_script": str(DELTA_SCRIPT),
        "directional_transitions": str(args.directional_transitions),
        "out": str(args.out),
        "info_mode": args.info_mode,
        "n_rows": len(rows),
        "n_ok": len(ok),
        "n_error": len(err),
        "counts_by_bucket": {},
        "counts_by_transition_family": {},
        "counts_by_polarity": {},
        "rows": [
            {
                "transition_id": r.get("transition_id"),
                "case_id": r.get("case_id"),
                "bucket": r.get("bucket"),
                "transition_family": r.get("transition_family"),
                "polarity": r.get("polarity"),
                "info_mode": r.get("info_mode"),
                "parse_failed": r.get("parse_failed", False),
                "error": r.get("error", False),
            }
            for r in rows
        ],
    }

    for r in ok:
        summary["counts_by_bucket"][r["bucket"]] = summary["counts_by_bucket"].get(r["bucket"], 0) + 1
        summary["counts_by_transition_family"][r["transition_family"]] = summary["counts_by_transition_family"].get(r["transition_family"], 0) + 1
        summary["counts_by_polarity"][r["polarity"]] = summary["counts_by_polarity"].get(r["polarity"], 0) + 1

    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps({
        "n_ok": summary["n_ok"],
        "n_error": summary["n_error"],
        "counts_by_bucket": summary["counts_by_bucket"],
        "counts_by_transition_family": summary["counts_by_transition_family"],
        "counts_by_polarity": summary["counts_by_polarity"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
