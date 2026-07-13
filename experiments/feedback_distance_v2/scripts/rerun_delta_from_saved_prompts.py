# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/rerun_delta_from_saved_prompts.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import traceback
from pathlib import Path

from tqdm import tqdm

BASE = Path("experiments/feedback_distance_v2/scripts/run_delta_granularity_prompt_update.py").resolve()
spec = importlib.util.spec_from_file_location("delta", BASE)
delta = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(delta)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def append_jsonl(path: Path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def task_safe(task):
    (
        row,
        trace_row,
        refs,
        model,
        temperature,
        query_max_tokens,
        summary_max_tokens,
        answer_max_tokens,
        retries,
        k,
    ) = task

    try:
        source = trace_row["source_row"]

        q = delta.run_query_writer(
            model=model,
            prompt=row["updated_prompt"],
            question=str(source.get("question") or ""),
            summary_1=str(source.get("summary_1") or ""),
            temperature=temperature,
            max_tokens=query_max_tokens,
            retries=retries,
        )

        ev = delta.evaluate_query(
            query=q["query"],
            trace_row=trace_row,
            refs=refs,
            model=model,
            temperature=temperature,
            k=k,
            summary_max_tokens=summary_max_tokens,
            answer_max_tokens=answer_max_tokens,
            retries=retries,
        )

        out = dict(row)

        for bad_key in [
            "generated_query", "query_raw", "query",
            "retrieved_titles", "retrieved_docs", "summary_2",
            "support_recall_hop2", "missing_recovery_rate",
            "hit_gold_count", "recovered_missing_count",
            "base_raw_output", "base_answer", "base_score",
            "strong_raw_output", "strong_answer", "strong_score",
        ]:
            out.pop(bad_key, None)

        out.update({
            "generated_query": q["query"],
            "query_raw": q["raw"],
            "reused_updated_prompt": True,
            **ev,
        })
        return out

    except Exception as e:
        return {
            "error": True,
            "case_id": row.get("case_id"),
            "idx": row.get("idx"),
            "arm_id": row.get("arm_id"),
            "arm_family": row.get("arm_family"),
            "info_mode": row.get("info_mode"),
            "edge_index": row.get("edge_index"),
            "prefix_k": row.get("prefix_k"),
            "edge_pairs": row.get("edge_pairs"),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saved-eval", type=Path, required=True)
    ap.add_argument("--traces", type=Path, required=True)
    ap.add_argument("--fixed-prompt-config", type=Path, required=True)
    ap.add_argument("--final-answerer-refs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary-out", type=Path, required=True)
    ap.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--model", type=str, default="openai/Qwen/Qwen3-8B")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--query-max-tokens", type=int, default=512)
    ap.add_argument("--summary-max-tokens", type=int, default=4096)
    ap.add_argument("--answer-max-tokens", type=int, default=2048)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--num-threads", type=int, default=12)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    delta.base.set_retriever_dir(str(args.retriever_dir))

    saved_rows = read_jsonl(args.saved_eval)
    trace_rows = read_jsonl(args.traces)

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
                done.add((int(r["case_id"]), str(r["arm_id"])))

    tasks = []
    for r in saved_rows:
        if r.get("error"):
            continue
        key = (int(r["case_id"]), str(r["arm_id"]))
        if key in done:
            continue
        tasks.append((
            r,
            trace_rows[int(r["case_id"])],
            refs,
            args.model,
            args.temperature,
            args.query_max_tokens,
            args.summary_max_tokens,
            args.answer_max_tokens,
            args.retries,
            args.k,
        ))

    print(f"[info] saved rows: {len(saved_rows)}")
    print(f"[info] pending rows: {len(tasks)}")
    print(f"[info] existing rows: {len(existing)}")

    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(task_safe, t) for t in tasks]
        for fut in tqdm(cf.as_completed(futs), total=len(futs), desc="rerun saved prompts"):
            append_jsonl(args.out, fut.result())

    all_rows = read_jsonl(args.out)
    error_rows = [r for r in all_rows if r.get("error")]
    result_rows = [r for r in all_rows if not r.get("error")]

    summary = delta.build_summary(result_rows, trace_rows)
    summary.update({
        "rerun_from_saved_prompts": True,
        "saved_eval": str(args.saved_eval),
        "traces": str(args.traces),
        "out": str(args.out),
        "n_error_rows": len(error_rows),
        "n_eval_rows": len(result_rows),
        "model": args.model,
        "k": args.k,
    })
    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps({
        "baselines": summary["baselines"],
        "best_single_edge": summary["best_single_edge"],
        "selected_arms": {
            k: v for k, v in summary["by_arm_id"].items()
            if k in ["endpoint_R_only", "endpoint_Rq", "full_trace_Rq", "full_trace_R_only"]
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
