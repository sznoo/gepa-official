# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/eval_oracle_query_downstream.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import string
import time
from pathlib import Path
from typing import Any

from litellm import completion
from tqdm import tqdm


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


def normalize_answer(s: Any) -> str:
    s = str(s or "")

    def lower(text: str) -> str:
        return text.lower()

    def remove_punc(text: str) -> str:
        return "".join(ch for ch in text if ch not in set(string.punctuation))

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def exact_match(pred: Any, gold: Any) -> bool:
    if isinstance(gold, list):
        return any(normalize_answer(pred) == normalize_answer(g) for g in gold)
    return normalize_answer(pred) == normalize_answer(gold)


def parse_answer(raw: str) -> str:
    text = str(raw or "").strip()

    # DSPy / reasoning-block style.
    m = re.search(r"\[\[\s*##\s*answer\s*##\s*\]\]\s*(.*)", text, flags=re.I | re.S)
    if m:
        ans = m.group(1).strip()
        ans = re.split(r"\n\s*\[\[\s*##", ans, maxsplit=1, flags=re.I)[0].strip()
        return ans.strip().strip('"').strip("'").strip()

    # Plain "answer:" style.
    m = re.search(r"(?:^|\n)\s*(?:final answer|answer)\s*:\s*(.+)$", text, flags=re.I | re.S)
    if m:
        return m.group(1).strip().splitlines()[0].strip().strip('"').strip("'").strip()

    return text.splitlines()[0].strip().strip('"').strip("'").strip()


def call_model(
    model: str,
    instruction: str,
    user_content: str,
    temperature: float,
    max_tokens: int,
    retries: int,
) -> str:
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = completion(
                model=model,
                messages=[
                    {"role": "system", "content": instruction},
                    {"role": "user", "content": user_content},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp["choices"][0]["message"]["content"] or ""
        except Exception as e:
            last_err = e
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"model call failed after {retries + 1} attempts: {last_err}")


def make_summary2_user(row: dict[str, Any]) -> str:
    question = str(row.get("question") or "")
    context = str(row.get("summary_1") or "")
    passages = row.get("oracle_target_retrieved_docs") or []
    passages_text = "\n\n".join(str(p) for p in passages)

    return f"""question:
{question}

context:
{context}

passages:
{passages_text}
"""


def make_final_user(question: str, summary_1: str, summary_2: str) -> str:
    return f"""question:
{question}

summary_1:
{summary_1}

summary_2:
{summary_2}
"""


def get_current_eval_by_idx(current_eval_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for r in current_eval_rows:
        out[str(r.get("idx"))] = r
    return out


def eval_one(
    task: tuple[
        int,
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        str,
        float,
        int,
        int,
        int,
    ]
) -> dict[str, Any]:
    (
        row_id,
        oracle_row,
        current_eval,
        refs,
        model,
        temperature,
        summary_max_tokens,
        answer_max_tokens,
        retries,
    ) = task

    question = str(oracle_row.get("question") or "")
    summary_1 = str(oracle_row.get("summary_1") or "")
    gold = oracle_row.get("gold_answer")

    summarize2_prompt = refs["summarize2_prompt"]
    base_prompt = refs["base_final_answerer"]["prompt"]
    strong_prompt = refs["strong_final_answerer"]["prompt"]

    oracle_summary_2 = call_model(
        model=model,
        instruction=summarize2_prompt,
        user_content=make_summary2_user(oracle_row),
        temperature=temperature,
        max_tokens=summary_max_tokens,
        retries=retries,
    )

    final_user = make_final_user(question, summary_1, oracle_summary_2)

    oracle_base_raw = call_model(
        model=model,
        instruction=base_prompt,
        user_content=final_user,
        temperature=temperature,
        max_tokens=answer_max_tokens,
        retries=retries,
    )
    oracle_strong_raw = call_model(
        model=model,
        instruction=strong_prompt,
        user_content=final_user,
        temperature=temperature,
        max_tokens=answer_max_tokens,
        retries=retries,
    )

    oracle_base_answer = parse_answer(oracle_base_raw)
    oracle_strong_answer = parse_answer(oracle_strong_raw)

    oracle_base_score = exact_match(oracle_base_answer, gold)
    oracle_strong_score = exact_match(oracle_strong_answer, gold)

    current_base_score = bool(current_eval.get("base_score", False))
    current_strong_score = bool(current_eval.get("strong_score", False))

    return {
        "row_id": row_id,
        "idx": oracle_row.get("idx"),
        "question": question,
        "gold_answer": gold,

        "oracle_target_hit": bool(oracle_row.get("oracle_target_hit")),
        "oracle_target_missing_recovery_rate": oracle_row.get("oracle_target_missing_recovery_rate"),
        "oracle_target_query": oracle_row.get("oracle_target_query"),
        "oracle_target_titles": oracle_row.get("oracle_target_titles"),
        "oracle_target_retrieved_titles": oracle_row.get("oracle_target_retrieved_titles"),
        "oracle_target_hit_titles": oracle_row.get("oracle_target_hit_titles"),

        "current_query": oracle_row.get("current_query"),
        "current_hop2_titles": oracle_row.get("current_hop2_titles"),
        "missing_after_hop1": oracle_row.get("missing_after_hop1"),
        "missing_after_hop2": oracle_row.get("missing_after_hop2"),

        "summary_1": summary_1,
        "oracle_summary_2": oracle_summary_2,

        "current_base_answer": current_eval.get("base_answer"),
        "current_base_score": current_base_score,
        "current_strong_answer": current_eval.get("strong_answer"),
        "current_strong_score": current_strong_score,

        "oracle_base_raw_output": oracle_base_raw,
        "oracle_base_answer": oracle_base_answer,
        "oracle_base_score": oracle_base_score,
        "oracle_base_gain": (not current_base_score) and oracle_base_score,
        "oracle_base_loss": current_base_score and (not oracle_base_score),

        "oracle_strong_raw_output": oracle_strong_raw,
        "oracle_strong_answer": oracle_strong_answer,
        "oracle_strong_score": oracle_strong_score,
        "oracle_strong_gain": (not current_strong_score) and oracle_strong_score,
        "oracle_strong_loss": current_strong_score and (not oracle_strong_score),

        "current_eval_row": current_eval,
        "oracle_target_row": oracle_row,
    }


def mean_bool(rows: list[dict[str, Any]], key: str) -> float | None:
    if not rows:
        return None
    return sum(bool(r.get(key)) for r in rows) / len(rows)


def count_bool(rows: list[dict[str, Any]], key: str) -> int:
    return sum(bool(r.get(key)) for r in rows)


def summarize_subset(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    n = len(rows)

    base_default_em = mean_bool(rows, "current_base_score")
    base_oracle_em = mean_bool(rows, "oracle_base_score")
    strong_default_em = mean_bool(rows, "current_strong_score")
    strong_oracle_em = mean_bool(rows, "oracle_strong_score")

    return {
        "name": name,
        "n": n,
        "base": {
            "default_hop2_em": base_default_em,
            "oracle_query_em": base_oracle_em,
            "oracle_gap": None if base_default_em is None or base_oracle_em is None else base_oracle_em - base_default_em,
            "default_hop2_correct": count_bool(rows, "current_base_score"),
            "oracle_query_correct": count_bool(rows, "oracle_base_score"),
            "oracle_gain_count": count_bool(rows, "oracle_base_gain"),
            "oracle_loss_count": count_bool(rows, "oracle_base_loss"),
        },
        "strong": {
            "default_hop2_em": strong_default_em,
            "oracle_query_em": strong_oracle_em,
            "oracle_gap": None if strong_default_em is None or strong_oracle_em is None else strong_oracle_em - strong_default_em,
            "default_hop2_correct": count_bool(rows, "current_strong_score"),
            "oracle_query_correct": count_bool(rows, "oracle_strong_score"),
            "oracle_gain_count": count_bool(rows, "oracle_strong_gain"),
            "oracle_loss_count": count_bool(rows, "oracle_strong_loss"),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--oracle-targets", type=Path, default=Path("experiments/feedback_distance_v2/cache/oracle_targets.jsonl"))
    ap.add_argument("--current-final-eval", type=Path, default=Path("experiments/feedback_distance_v2/results/final_answerer_current_summary_eval.jsonl"))
    ap.add_argument("--final-answerer-refs", type=Path, default=Path("experiments/feedback_distance_v2/cache/final_answerer_refs.json"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_config.json"))
    ap.add_argument("--out", type=Path, default=Path("experiments/feedback_distance_v2/results/oracle_query_downstream_eval.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/feedback_distance_v2/results/oracle_query_downstream_summary.json"))
    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--summary-max-tokens", type=int, default=4096)
    ap.add_argument("--answer-max-tokens", type=int, default=2048)
    ap.add_argument("--num-threads", type=int, default=8)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    oracle_rows = read_jsonl(args.oracle_targets)
    if args.limit is not None:
        oracle_rows = oracle_rows[: args.limit]

    current_eval_rows = read_jsonl(args.current_final_eval)
    current_by_idx = get_current_eval_by_idx(current_eval_rows)

    final_refs = read_json(args.final_answerer_refs)
    fixed_cfg = read_json(args.fixed_prompt_config)
    summarize2_prompt = fixed_cfg["prompt_candidate"]["prompts"]["summarize2.predict"]

    refs = {
        **final_refs,
        "summarize2_prompt": summarize2_prompt,
    }

    tasks = []
    for i, row in enumerate(oracle_rows):
        idx = str(row.get("idx"))
        if idx not in current_by_idx:
            raise KeyError(f"idx={idx} not found in current final eval: {args.current_final_eval}")
        tasks.append((
            i,
            row,
            current_by_idx[idx],
            refs,
            args.model,
            args.temperature,
            args.summary_max_tokens,
            args.answer_max_tokens,
            args.retries,
        ))

    out_rows = []
    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        for r in tqdm(ex.map(eval_one, tasks), total=len(tasks), desc="oracle downstream"):
            out_rows.append(r)

    out_rows.sort(key=lambda r: r["row_id"])
    write_jsonl(args.out, out_rows)

    hit_rows = [r for r in out_rows if r.get("oracle_target_hit")]
    fail_rows = [r for r in out_rows if not r.get("oracle_target_hit")]

    summary = {
        "oracle_targets": str(args.oracle_targets),
        "current_final_eval": str(args.current_final_eval),
        "final_answerer_refs": str(args.final_answerer_refs),
        "fixed_prompt_config": str(args.fixed_prompt_config),
        "model": args.model,
        "n": len(out_rows),
        "main_table": summarize_subset(out_rows, "all_oracle_targets_65"),
        "by_oracle_target_hit": {
            "hit": summarize_subset(hit_rows, "oracle_target_hit"),
            "miss": summarize_subset(fail_rows, "oracle_target_miss"),
        },
    }
    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary["main_table"], ensure_ascii=False, indent=2))
    print("\n[by_oracle_target_hit]")
    print(json.dumps(summary["by_oracle_target_hit"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
