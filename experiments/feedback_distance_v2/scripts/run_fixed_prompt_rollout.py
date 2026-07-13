# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/run_fixed_prompt_rollout.py

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from tqdm.auto import tqdm

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
for _p in (str(ROOT), str(SRC)):
    if _p in sys.path:
        sys.path.remove(_p)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

import dspy  # noqa: E402

from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter  # noqa: E402
from examples.hotpotqa.data import _to_example  # noqa: E402
from examples.hotpotqa.feedback import feedback_fn_map  # noqa: E402
from examples.hotpotqa.metric import answer_exact_match  # noqa: E402
from examples.hotpotqa.program import HotpotMultiHop  # noqa: E402
from examples.hotpotqa.retriever import set_retriever_dir  # noqa: E402


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")


def norm_title(t: str) -> str:
    return " ".join(str(t).strip().lower().split())


def ordered_unique(xs):
    return list(dict.fromkeys(str(x).strip() for x in xs if str(x).strip()))


def title_set(xs):
    return {norm_title(x) for x in xs}


def missing_titles(gold_titles, *title_lists):
    gold_map = {norm_title(t): t for t in gold_titles}
    seen = set()
    for xs in title_lists:
        seen |= title_set(xs)
    return [gold_map[t] for t in sorted(set(gold_map) - seen)]


def hit_titles(gold_titles, titles):
    gold_map = {norm_title(t): t for t in gold_titles}
    hit = set(gold_map) & title_set(titles)
    return [gold_map[t] for t in sorted(hit)]


def make_lm(model, api_key, api_base, temperature, max_tokens):
    model_l = model.lower()
    if "openai/gpt-5" in model_l or model_l.startswith("gpt-5"):
        temperature = 1.0
        max_tokens = max(max_tokens or 0, 16000)

    kwargs = {
        "api_key": api_key,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if api_base:
        kwargs["api_base"] = api_base
    return dspy.LM(model, **kwargs)


def chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i+n]


def normalize_rollout_row(r: dict[str, Any]) -> dict[str, Any]:
    gold = ordered_unique(r.get("gold_support_titles") or [])
    hop1 = ordered_unique(r.get("hop1_titles") or [])
    hop2 = ordered_unique(r.get("hop2_titles") or [])

    miss_hop1 = missing_titles(gold, hop1)
    miss_hop2 = missing_titles(gold, hop1, hop2)
    recovered = hit_titles(miss_hop1, hop2)

    denom_gold = len(gold) if gold else 1
    denom_missing = len(miss_hop1)

    return {
        "idx": str(r.get("example_id")),
        "example_id": r.get("example_id"),
        "question": r.get("question"),
        "gold_answer": r.get("gold_answer"),
        "gold_support_titles": gold,

        "hop1_query": r.get("hop1_query"),
        "hop1_titles": hop1,
        "hop1_docs": r.get("hop1_docs") or [],
        "summary_1": r.get("summary_1"),

        "current_query": r.get("hop2_query"),
        "current_hop2_titles": hop2,
        "current_hop2_docs": r.get("hop2_docs") or [],
        "summary_2": r.get("summary_2"),

        "pred_answer": r.get("pred_answer"),
        "score": float(r.get("score", 0.0)),

        "missing_after_hop1": miss_hop1,
        "missing_after_hop2": miss_hop2,
        "current_support_recall_hop2": len(hit_titles(gold, hop2)) / denom_gold,
        "current_missing_recovery_rate": (
            len(recovered) / denom_missing if denom_missing else None
        ),

        "support_recall_hop1": r.get("support_recall_hop1"),
        "support_recall_hop2_only": r.get("support_recall_hop2_only"),
        "support_recall_total": r.get("support_recall_total"),
        "new_support_titles_hop2": r.get("new_support_titles_hop2") or [],
        "hit_titles_hop1": r.get("hit_titles_hop1") or [],
        "hit_titles_total": r.get("hit_titles_total") or [],
        "raw_rollout": r,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split-jsonl", type=Path, default=Path("experiments/feedback_distance_v2/cache/dev300_random_seed1.jsonl"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_config.json"))
    ap.add_argument("--analysis-dir", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_rollout_analysis"))
    ap.add_argument("--out", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_rollout_dev300.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_rollout_dev300_summary.json"))

    ap.add_argument("--task-model", default="openai/gpt-5-mini")
    ap.add_argument("--task-api-base", default=os.environ.get("TASK_API_BASE"))
    ap.add_argument("--task-api-key", default=os.environ.get("OPENAI_API_KEY") or os.environ.get("TASK_API_KEY"))
    ap.add_argument("--task-temperature", type=float, default=1.0)
    ap.add_argument("--task-max-tokens", type=int, default=16000)

    ap.add_argument("--retriever-dir", type=Path, default=Path(os.environ.get("HOTPOT_RETRIEVER_DIR", "examples/hotpotqa")))
    ap.add_argument("--retrieval-k", type=int, default=7)
    ap.add_argument("--num-threads", type=int, default=1)
    ap.add_argument("--chunk-size", type=int, default=20)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    if not args.task_api_key:
        raise EnvironmentError("OPENAI_API_KEY not found. Source .env first.")

    if args.analysis_dir.exists():
        if not args.overwrite:
            raise FileExistsError(f"{args.analysis_dir} exists. Use --overwrite.")
        shutil.rmtree(args.analysis_dir)
    args.analysis_dir.mkdir(parents=True, exist_ok=True)

    split_rows = read_jsonl(args.split_jsonl)
    dataset = [_to_example(r["raw"]) for r in split_rows]

    cfg = read_json(args.fixed_prompt_config)
    prompt_obj = cfg["prompt_candidate"]
    prompts = dict(prompt_obj["prompts"])
    fixed_prompt_name = cfg["fixed_prompt_name"]

    dspy.configure(lm=make_lm(
        args.task_model,
        args.task_api_key,
        args.task_api_base,
        args.task_temperature,
        args.task_max_tokens,
    ))

    set_retriever_dir(str(args.retriever_dir))
    program = HotpotMultiHop(k=args.retrieval_k, retriever_dir=str(args.retriever_dir))

    adapter = HotpotLoggingDspyAdapter(
        student_module=program,
        metric_fn=answer_exact_match,
        feedback_map=feedback_fn_map,
        failure_score=0.0,
        num_threads=args.num_threads,
        reflection_lm=None,
        analysis_log_dir=str(args.analysis_dir),
        run_id=str(args.analysis_dir),
        log_rollouts=True,
        log_feedback=False,
        log_proposals=False,
        log_instructions_in_rollout=True,
    )

    adapter.set_analysis_context(
        phase="feedback_distance_v2_fixed_prompt_rollout",
        split="dev300_random_seed1",
        updated_component="fixed_prompt_rollout",
        capture_traces=False,
    )

    all_scores = []
    eval_chunks = list(chunks(dataset, max(1, args.chunk_size)))
    for chunk in tqdm(eval_chunks, desc="fixed-prompt rollout", total=len(eval_chunks), dynamic_ncols=True):
        batch = adapter.evaluate(chunk, prompts, capture_traces=False)
        all_scores.extend(float(s) for s in batch.scores)

    adapter.clear_analysis_context()

    raw_rollouts = read_jsonl(args.analysis_dir / "rollout_traces.jsonl")
    out_rows = [normalize_rollout_row(r) for r in raw_rollouts]
    write_jsonl(args.out, out_rows)

    mrr = [r["current_missing_recovery_rate"] for r in out_rows if r["current_missing_recovery_rate"] is not None]
    summary = {
        "fixed_prompt_name": fixed_prompt_name,
        "split_jsonl": str(args.split_jsonl),
        "analysis_dir": str(args.analysis_dir),
        "rollout_log": str(args.analysis_dir / "rollout_traces.jsonl"),
        "out": str(args.out),
        "n": len(out_rows),
        "mean_score": sum(r["score"] for r in out_rows) / len(out_rows) if out_rows else None,
        "n_missing_after_hop1_nonempty": sum(bool(r["missing_after_hop1"]) for r in out_rows),
        "n_natural_retrieval_failures": sum(bool(r["missing_after_hop1"]) and bool(r["missing_after_hop2"]) for r in out_rows),
        "mean_current_missing_recovery_rate": sum(mrr) / len(mrr) if mrr else None,
        "task_model": args.task_model,
        "retriever_dir": str(args.retriever_dir),
        "retrieval_k": args.retrieval_k,
        "num_threads": args.num_threads,
    }
    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
