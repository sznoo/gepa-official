import argparse
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import dspy

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from examples.hotpotqa.program import HotpotMultiHop
from examples.hotpotqa.retriever import set_retriever_dir

from experiments.deltaq.run_hotpot_ideal_context_upper_bound import (
    DEFAULT_TRACE,
    DEFAULT_FIXED_PROMPT,
    DEFAULT_R6_PROMPT,
    parse_arms,
    read_jsonl,
    write_jsonl,
    safe_float,
    clean_query,
    lm_raw_call,
    apply_prompt_candidate,
    load_eval_examples,
    support_evidence_from_example,
    baseline_cached_row,
    make_support_aware_delta_prompt,
    make_answer_aware_delta_prompt,
    make_query_rewrite_prompt,
    run_downstream,
    retrieval_metrics,
    support_title_ceiling_query,
    write_summary,
)

try:
    from tqdm.auto import tqdm
except Exception:
    def tqdm(x, **kwargs):
        return x


_tls = threading.local()


def make_lm(args):
    lm_kwargs = {
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_key:
        lm_kwargs["api_key"] = args.api_key
    if args.api_base:
        lm_kwargs["api_base"] = args.api_base
    return dspy.LM(args.model, **lm_kwargs)


def get_thread_state(args):
    """
    Thread-local LM/programs.
    Avoids sharing DSPy module state across workers.
    """
    if not hasattr(_tls, "state"):
        lm = make_lm(args)

        fixed_program = HotpotMultiHop(k=args.k, retriever_dir=args.retriever_dir)
        apply_prompt_candidate(fixed_program, args.fixed_prompt_candidate)

        r6_program = HotpotMultiHop(k=args.k, retriever_dir=args.retriever_dir)
        apply_prompt_candidate(r6_program, args.r6_prompt_candidate)

        _tls.state = {
            "lm": lm,
            "fixed_program": fixed_program,
            "r6_program": r6_program,
        }
    return _tls.state


def support_titles_from_trace(t):
    return set(str(x).strip() for x in t.get("gold_support_titles", []) if str(x).strip())


def select_traces(traces, subset):
    selected = []
    for t in traces:
        score = safe_float(t.get("score", 0.0))
        missing_after_hop2 = set(t.get("missing_titles_after_hop2", []) or [])
        hop1_titles = set(t.get("hop1_titles", []) or [])
        gold_titles = support_titles_from_trace(t)
        missing_after_hop1 = gold_titles - hop1_titles

        if subset == "all":
            keep = True
        elif subset == "wrong":
            keep = score < 1.0
        elif subset == "hop2_miss":
            keep = len(missing_after_hop2) > 0
        elif subset == "wrong_hop2_miss":
            keep = score < 1.0 and len(missing_after_hop2) > 0
        elif subset == "wrong_missing_after_hop1":
            keep = score < 1.0 and len(missing_after_hop1) > 0
        else:
            raise ValueError(f"Unknown subset: {subset}")

        if keep:
            selected.append(t)
    return selected


def process_one(args, arms, q_to_ex, t):
    state = get_thread_state(args)
    lm = state["lm"]
    fixed_program = state["fixed_program"]
    r6_program = state["r6_program"]

    question = t["question"]
    ex = q_to_ex.get(question)
    support_evidence = support_evidence_from_example(ex)

    base = baseline_cached_row(t)
    meta = {
        "eval_index": t.get("eval_index"),
        "example_id": t.get("example_id"),
        "question": question,
        "gold_answer": t.get("gold_answer"),
        "baseline_score": base["score"],
        "baseline_support_recall_total": base["support_recall_total"],
        "baseline_missing_titles_after_hop2": base["missing_titles_after_hop2"],
    }

    local_rows = []

    with dspy.context(lm=lm):
        for arm in arms:
            error = None
            delta_context = None

            try:
                if arm == "baseline_cached":
                    result = base

                elif arm == "baseline_recomputed":
                    result = run_downstream(
                        fixed_program,
                        t,
                        t.get("hop2_query", ""),
                        retriever_k=args.k,
                    )

                elif arm == "r6_global":
                    q = r6_program.create_query_hop2(
                        question=question,
                        summary_1=t.get("summary_1", ""),
                    ).query
                    q = clean_query(q)
                    result = run_downstream(fixed_program, t, q, retriever_k=args.k)

                elif arm == "support_aware_ideal_delta":
                    delta_prompt = make_support_aware_delta_prompt(t, support_evidence)
                    delta_context, error = lm_raw_call(lm, delta_prompt, retries=args.retries)
                    rewrite_prompt = make_query_rewrite_prompt(t, delta_context)
                    q_raw, err2 = lm_raw_call(lm, rewrite_prompt, retries=args.retries)
                    if err2:
                        error = (error or "") + "\n" + err2
                    q = clean_query(q_raw)
                    result = run_downstream(fixed_program, t, q, retriever_k=args.k)
                    result["delta_prompt"] = delta_prompt
                    result["rewrite_prompt"] = rewrite_prompt

                elif arm == "answer_aware_ideal_delta":
                    delta_prompt = make_answer_aware_delta_prompt(t, support_evidence)
                    delta_context, error = lm_raw_call(lm, delta_prompt, retries=args.retries)
                    rewrite_prompt = make_query_rewrite_prompt(t, delta_context)
                    q_raw, err2 = lm_raw_call(lm, rewrite_prompt, retries=args.retries)
                    if err2:
                        error = (error or "") + "\n" + err2
                    q = clean_query(q_raw)
                    result = run_downstream(fixed_program, t, q, retriever_k=args.k)
                    result["delta_prompt"] = delta_prompt
                    result["rewrite_prompt"] = rewrite_prompt

                elif arm == "support_title_ceiling":
                    q = support_title_ceiling_query(t)
                    result = run_downstream(fixed_program, t, q, retriever_k=args.k)

                else:
                    raise ValueError(f"unknown arm: {arm}")

            except Exception as e:
                error = str(e)
                result = {
                    "hop2_query": "",
                    "hop2_docs": [],
                    "summary_2": "",
                    "pred_answer": "",
                    "score": 0.0,
                    **retrieval_metrics(t, []),
                }

            row = {
                "arm": arm,
                "eval_index": t.get("eval_index"),
                "example_id": t.get("example_id"),
                "question": question,
                "gold_answer": t.get("gold_answer"),
                "baseline_hop2_query": t.get("hop2_query", ""),
                "delta_context": delta_context,
                "error": error,

                "baseline_score": base["score"],
                "baseline_support_recall_total": base["support_recall_total"],
                "baseline_support_recall_hop2_only": base["support_recall_hop2_only"],
                "baseline_missing_recovery_rate": base["missing_recovery_rate"],

                **result,
            }

            row["final_corrected_vs_baseline"] = float(
                base["score"] < 1.0 and row["score"] >= 1.0
            )
            row["retrieval_improved_vs_baseline"] = float(
                row["support_recall_total"] > base["support_recall_total"]
            )
            row["retrieval_improved_but_final_wrong"] = float(
                row["support_recall_total"] > base["support_recall_total"]
                and row["score"] < 1.0
            )
            local_rows.append(row)

    return meta, local_rows


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--trace-path", default=DEFAULT_TRACE)
    parser.add_argument("--fixed-prompt-candidate", default=DEFAULT_FIXED_PROMPT)
    parser.add_argument("--r6-prompt-candidate", default=DEFAULT_R6_PROMPT)
    parser.add_argument("--out-dir", default="experiments/deltaq/results_hotpot_ideal_context_upper_bound_parallel")

    parser.add_argument("--retriever-dir", default=os.environ.get("HOTPOT_RETRIEVER_DIR"))
    parser.add_argument("--k", type=int, default=7)

    parser.add_argument("--subset", default="wrong_hop2_miss",
                        choices=["all", "wrong", "hop2_miss", "wrong_hop2_miss", "wrong_missing_after_hop1"])
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--arms", default="all")
    parser.add_argument("--num-threads", type=int, default=1)

    parser.add_argument("--model", default=os.environ.get("TASK_MODEL", "openai/gpt-5-mini"))
    parser.add_argument("--api-base", default=os.environ.get("TASK_API_BASE", ""))
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=16000)
    parser.add_argument("--retries", type=int, default=3)

    # Split reconstruction only for support evidence.
    parser.add_argument("--hf-split", default="train")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-size", type=int, default=100)
    parser.add_argument("--val-size", type=int, default=100)
    parser.add_argument("--test-size", type=int, default=500)
    parser.add_argument("--eval-split", default="test", choices=["train", "val", "test"])
    parser.add_argument("--eval-offset", type=int, default=100)
    parser.add_argument("--eval-limit", type=int, default=300)

    args = parser.parse_args()

    if "gpt-5" in args.model:
        if args.temperature not in (1.0, None):
            print(f"[warn] GPT-5 model requires temperature=1.0 or None; overriding {args.temperature} -> 1.0")
            args.temperature = 1.0
        if args.max_tokens is not None and args.max_tokens < 16000:
            print(f"[warn] GPT-5 model requires max_tokens>=16000 or None; overriding {args.max_tokens} -> 16000")
            args.max_tokens = 16000

    if args.retriever_dir:
        set_retriever_dir(args.retriever_dir)

    # Configure a main-thread LM for any fallback DSPy calls.
    main_lm = make_lm(args)
    dspy.settings.configure(lm=main_lm)

    traces_all = read_jsonl(args.trace_path)
    traces = select_traces(traces_all, args.subset)
    traces = traces[args.offset:]
    if args.limit is not None:
        traces = traces[:args.limit]

    arms = parse_arms(args.arms)
    q_to_ex = load_eval_examples(args)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[info] trace_path: {args.trace_path}")
    print(f"[info] total traces: {len(traces_all)}")
    print(f"[info] selected subset={args.subset}: {len(traces)}")
    print(f"[info] arms: {arms}")
    print(f"[info] num_threads: {args.num_threads}")
    print(f"[info] fixed_prompt_candidate: {args.fixed_prompt_candidate}")
    print(f"[info] out_dir: {out_dir}")

    rows = []
    selected_meta = []

    if args.num_threads <= 1:
        for t in tqdm(traces, desc="ideal-context upper bound", unit="ex", dynamic_ncols=True):
            meta, local_rows = process_one(args, arms, q_to_ex, t)
            selected_meta.append(meta)
            rows.extend(local_rows)
    else:
        with ThreadPoolExecutor(max_workers=args.num_threads) as pool:
            futs = [pool.submit(process_one, args, arms, q_to_ex, t) for t in traces]
            for fut in tqdm(as_completed(futs), total=len(futs), desc="ideal-context upper bound", unit="ex", dynamic_ncols=True):
                meta, local_rows = fut.result()
                selected_meta.append(meta)
                rows.extend(local_rows)

    rows.sort(key=lambda r: (str(r.get("eval_index")), r.get("arm", "")))
    selected_meta.sort(key=lambda r: str(r.get("eval_index")))

    write_jsonl(out_dir / "rows.jsonl", rows)
    write_jsonl(out_dir / "selected_examples.jsonl", selected_meta)
    write_summary(out_dir / "summary.md", rows, selected_count=len(traces))

    config = vars(args)
    config["arms"] = arms
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False))

    print()
    print("[wrote]", out_dir / "rows.jsonl")
    print("[wrote]", out_dir / "selected_examples.jsonl")
    print("[wrote]", out_dir / "summary.md")
    print()
    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
