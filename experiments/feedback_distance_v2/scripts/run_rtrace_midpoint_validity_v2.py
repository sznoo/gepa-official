# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/run_rtrace_midpoint_validity_v2.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
from pathlib import Path
from typing import Any

from tqdm import tqdm


BASE_SCRIPT = Path("experiments/feedback_distance_v2/scripts/run_rtrace_midpoint_validity.py").resolve()
spec = importlib.util.spec_from_file_location("rtrace_base", BASE_SCRIPT)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)


def generate_midpoint_query_v2(
    *,
    left: dict[str, Any],
    right: dict[str, Any],
    row: dict[str, Any],
    model: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    retry_feedback: dict[str, Any] | None = None,
    attempt_no: int = 0,
) -> dict[str, Any]:
    feedback_block = ""
    if retry_feedback:
        feedback_block = f"""

Previous midpoint candidate was judged invalid under the same distance specification.

Verifier feedback:
{json.dumps({
    "left_valid": retry_feedback.get("left_valid"),
    "right_valid": retry_feedback.get("right_valid"),
    "left_reason": retry_feedback.get("left_reason"),
    "right_reason": retry_feedback.get("right_reason"),
}, ensure_ascii=False, indent=2)}

Revise the midpoint query to fix the verifier failure.
If right_valid was false, make more concrete progress toward R_right.
If left_valid was false, avoid jumping too close to R_right or changing the retrieval intent too abruptly.
"""

    system = base.DISTANCE_SPEC + f"""

Generate a midpoint retrieval query R_mid between R_left and R_right.

The query should be a minimal transformation from R_left toward R_right. It should preserve useful intent/evidence from R_left while targeting evidence that makes it closer to R_right. Do not simply copy either endpoint query.

Additional constraint:
- The midpoint must make concrete progress toward R_right.
- It should target at least one retrieval intent, entity, relation, or evidence cluster that is present in R_right but weak or absent in R_left.
- Do not produce a midpoint that only paraphrases R_left.

{feedback_block}

Return strict JSON only:
{{
  "mid_query": "<second-hop retrieval query>",
  "rationale": "<why this query is between the endpoints under the distance specification>"
}}
"""

    user = json.dumps({
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "summary_1": row.get("summary_1"),
        "missing_after_hop1": row.get("missing_after_hop1"),
        "missing_after_hop2": row.get("missing_after_hop2"),
        "attempt_no": attempt_no,
        "R_left": base.state_for_prompt(left),
        "R_right": base.state_for_prompt(right),
    }, ensure_ascii=False, indent=2)

    raw = base.call_model(model, system, user, temperature, max_tokens, retries)
    try:
        obj = base.extract_json_obj(raw)
        q = str(obj.get("mid_query") or "").strip()
        if not q:
            raise ValueError("empty mid_query")
        return {
            "mid_query": q,
            "rationale": obj.get("rationale", ""),
            "raw": raw,
            "attempt_no": attempt_no,
        }
    except Exception:
        fallback = f"{left.get('query', '')} {right.get('query', '')}".strip()
        return {
            "mid_query": fallback,
            "rationale": "JSON parse failed; fallback concatenated endpoint queries.",
            "raw": raw,
            "parse_failed": True,
            "attempt_no": attempt_no,
        }


def run_case_v2(
    task: tuple[
        int,
        dict[str, Any],
        dict[str, Any],
        str,
        float,
        int,
        int,
        int,
        int,
        int,
        int,
        int,
        int,
        int,
    ]
) -> dict[str, Any]:
    (
        case_id,
        row,
        refs,
        model,
        temperature,
        selector_max_tokens,
        generator_max_tokens,
        judge_max_tokens,
        summary_max_tokens,
        answer_max_tokens,
        retries,
        max_iter,
        k,
        max_retries_per_edge,
    ) = task

    trace = base.make_initial_states(row)
    attempts = []
    iterations = []

    for it in range(max_iter):
        selected = base.select_longest_edge(
            trace=trace,
            row=row,
            model=model,
            temperature=temperature,
            max_tokens=selector_max_tokens,
            retries=retries,
        )
        edge_index = int(selected["edge_index"])
        left = trace[edge_index]
        right = trace[edge_index + 1]

        inserted = False
        inserted_state_id = None
        retry_feedback = None
        iter_attempts = []

        for attempt_no in range(max_retries_per_edge + 1):
            gen = generate_midpoint_query_v2(
                left=left,
                right=right,
                row=row,
                model=model,
                temperature=temperature,
                max_tokens=generator_max_tokens,
                retries=retries,
                retry_feedback=retry_feedback,
                attempt_no=attempt_no,
            )

            mid_state = base.evaluate_query_state(
                state_id=f"R_mid_{it}_try{attempt_no}",
                kind="midpoint",
                query=gen["mid_query"],
                row=row,
                summarize2_prompt=refs["summarize2_prompt"],
                base_prompt=refs["base_final_answerer"]["prompt"],
                strong_prompt=refs["strong_final_answerer"]["prompt"],
                model=model,
                temperature=temperature,
                summary_max_tokens=summary_max_tokens,
                answer_max_tokens=answer_max_tokens,
                retries=retries,
                k=k,
            )

            judge = base.verify_midpoint(
                left=left,
                right=right,
                mid=mid_state,
                row=row,
                model=model,
                temperature=temperature,
                max_tokens=judge_max_tokens,
                retries=retries,
            )

            attempt = {
                "case_id": case_id,
                "idx": row.get("idx"),
                "iter": it,
                "attempt_no": attempt_no,
                "selected_edge_index": edge_index,
                "left_state_id": left.get("state_id"),
                "right_state_id": right.get("state_id"),
                "mid_state_id": mid_state.get("state_id"),
                "edge_selector": selected,
                "midpoint_generation": gen,
                "left_state": left,
                "right_state": right,
                "mid_state": mid_state,
                "judge": judge,
                "left_valid": bool(judge.get("left_valid")),
                "right_valid": bool(judge.get("right_valid")),
                "both_valid": bool(judge.get("both_valid")),
                "inserted": False,
            }
            attempts.append(attempt)
            iter_attempts.append(attempt)

            if bool(judge.get("both_valid")):
                trace.insert(edge_index + 1, mid_state)
                attempt["inserted"] = True
                inserted = True
                inserted_state_id = mid_state.get("state_id")
                break

            retry_feedback = judge

        iterations.append({
            "case_id": case_id,
            "idx": row.get("idx"),
            "iter": it,
            "selected_edge_index": edge_index,
            "left_state_id": left.get("state_id"),
            "right_state_id": right.get("state_id"),
            "n_attempts": len(iter_attempts),
            "inserted": inserted,
            "inserted_state_id": inserted_state_id,
            "first_pass_valid": bool(iter_attempts[0]["both_valid"]) if iter_attempts else False,
            "final_valid": inserted,
            "recovered_by_retry": (
                len(iter_attempts) > 1
                and not bool(iter_attempts[0]["both_valid"])
                and inserted
            ),
            "attempt_state_ids": [a["mid_state_id"] for a in iter_attempts],
        })

    return {
        "case_id": case_id,
        "idx": row.get("idx"),
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "oracle_target_hit": bool(row.get("oracle_target_hit")),
        "trace": trace,
        "iterations": iterations,
        "attempts": attempts,
        "source_row": row,
    }


def mean_bool(rows: list[dict[str, Any]], key: str) -> float | None:
    if not rows:
        return None
    return sum(bool(r.get(key)) for r in rows) / len(rows)


def build_summary_v2(case_rows: list[dict[str, Any]]) -> dict[str, Any]:
    attempts = [a for c in case_rows for a in c["attempts"]]
    iterations = [it for c in case_rows for it in c["iterations"]]
    first_attempts = [a for a in attempts if int(a.get("attempt_no", 0)) == 0]
    retry_attempts = [a for a in attempts if int(a.get("attempt_no", 0)) > 0]

    by_iter = {}
    for it in sorted({x["iter"] for x in iterations}):
        iter_rows = [x for x in iterations if x["iter"] == it]
        first_rows = [a for a in first_attempts if a["iter"] == it]
        retry_rows = [a for a in retry_attempts if a["iter"] == it]
        by_iter[str(it)] = {
            "iterations": len(iter_rows),
            "candidate_attempts": len([a for a in attempts if a["iter"] == it]),
            "first_pass_both_valid_rate": mean_bool(first_rows, "both_valid"),
            "final_insert_rate": mean_bool(iter_rows, "inserted"),
            "retry_recovered_rate": mean_bool(iter_rows, "recovered_by_retry"),
            "retry_attempt_both_valid_rate": mean_bool(retry_rows, "both_valid"),
            "inserted_count": sum(bool(x["inserted"]) for x in iter_rows),
            "recovered_by_retry_count": sum(bool(x["recovered_by_retry"]) for x in iter_rows),
        }

    invalid_first = [x for x in iterations if not bool(x["first_pass_valid"])]
    return {
        "n_cases": len(case_rows),
        "n_case_iterations": len(iterations),
        "n_candidate_attempts": len(attempts),

        "first_pass_left_valid_rate": mean_bool(first_attempts, "left_valid"),
        "first_pass_right_valid_rate": mean_bool(first_attempts, "right_valid"),
        "first_pass_both_valid_rate": mean_bool(first_attempts, "both_valid"),
        "first_pass_both_valid_count": sum(bool(a["both_valid"]) for a in first_attempts),

        "final_insert_rate": mean_bool(iterations, "inserted"),
        "final_insert_count": sum(bool(x["inserted"]) for x in iterations),

        "invalid_first_pass_count": len(invalid_first),
        "retry_recovered_count": sum(bool(x["recovered_by_retry"]) for x in iterations),
        "retry_recovered_rate_among_invalid_first": (
            sum(bool(x["recovered_by_retry"]) for x in iterations) / len(invalid_first)
            if invalid_first else None
        ),

        "all_candidate_left_valid_rate": mean_bool(attempts, "left_valid"),
        "all_candidate_right_valid_rate": mean_bool(attempts, "right_valid"),
        "all_candidate_both_valid_rate": mean_bool(attempts, "both_valid"),

        "by_iter": by_iter,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("experiments/feedback_distance_v2/results/oracle_query_downstream_eval.repaired.jsonl"))
    ap.add_argument("--final-answerer-refs", type=Path, default=Path("experiments/feedback_distance_v2/cache/final_answerer_refs.json"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_config.json"))
    ap.add_argument("--out-traces", type=Path, default=Path("experiments/feedback_distance_v2/results/rtrace_midpoint_validity_v2_traces_hit48.jsonl"))
    ap.add_argument("--out-attempts", type=Path, default=Path("experiments/feedback_distance_v2/results/rtrace_midpoint_validity_v2_attempts_hit48.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/feedback_distance_v2/results/rtrace_midpoint_validity_v2_summary_hit48.json"))
    ap.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--selector-max-tokens", type=int, default=1024)
    ap.add_argument("--generator-max-tokens", type=int, default=2048)
    ap.add_argument("--judge-max-tokens", type=int, default=2048)
    ap.add_argument("--summary-max-tokens", type=int, default=4096)
    ap.add_argument("--answer-max-tokens", type=int, default=2048)
    ap.add_argument("--num-threads", type=int, default=12)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--max-iter", type=int, default=4)
    ap.add_argument("--max-retries-per-edge", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--include-oracle-target-miss", action="store_true")
    args = ap.parse_args()

    base.set_retriever_dir(str(args.retriever_dir))

    rows = base.read_jsonl(args.input)
    if not args.include_oracle_target_miss:
        rows = [r for r in rows if bool(r.get("oracle_target_hit"))]
    if args.limit is not None:
        rows = rows[: args.limit]

    final_refs = base.read_json(args.final_answerer_refs)
    fixed_cfg = base.read_json(args.fixed_prompt_config)

    refs = {
        **final_refs,
        "summarize2_prompt": fixed_cfg["prompt_candidate"]["prompts"]["summarize2.predict"],
    }

    tasks = [
        (
            i,
            r,
            refs,
            args.model,
            args.temperature,
            args.selector_max_tokens,
            args.generator_max_tokens,
            args.judge_max_tokens,
            args.summary_max_tokens,
            args.answer_max_tokens,
            args.retries,
            args.max_iter,
            args.k,
            args.max_retries_per_edge,
        )
        for i, r in enumerate(rows)
    ]

    case_rows = []
    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        for r in tqdm(ex.map(run_case_v2, tasks), total=len(tasks), desc="rtrace midpoint v2"):
            case_rows.append(r)

    case_rows.sort(key=lambda r: r["case_id"])
    attempts = [a for c in case_rows for a in c["attempts"]]

    base.write_jsonl(args.out_traces, case_rows)
    base.write_jsonl(args.out_attempts, attempts)

    summary = {
        "input": str(args.input),
        "out_traces": str(args.out_traces),
        "out_attempts": str(args.out_attempts),
        "subset": "all_65" if args.include_oracle_target_miss else "oracle_target_hit_48",
        "model": args.model,
        "retriever_dir": str(args.retriever_dir),
        "k": args.k,
        "max_iter": args.max_iter,
        "max_retries_per_edge": args.max_retries_per_edge,
        "strict_insert": True,
        "metrics": build_summary_v2(case_rows),
        "distance_spec": base.DISTANCE_SPEC,
    }
    base.write_json(args.summary_out, summary)

    print("[wrote]", args.out_traces)
    print("[wrote]", args.out_attempts)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary["metrics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
