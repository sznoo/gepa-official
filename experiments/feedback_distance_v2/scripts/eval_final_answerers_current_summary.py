#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import string
import time
from collections import Counter
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


def get_field(row: dict[str, Any], key: str, default: Any = "") -> Any:
    if row.get(key) not in (None, ""):
        return row.get(key)
    rr = row.get("raw_rollout") or row.get("current_row", {}).get("raw_rollout") or {}
    return rr.get(key, default)


def normalize_answer(s: Any) -> str:
    s = str(s or "")

    def lower(text: str) -> str:
        return text.lower()

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

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

    # For possible DSPy-style or reasoning-block outputs.
    m = re.search(r"\[\[\s*##\s*answer\s*##\s*\]\]\s*(.*)", text, flags=re.I | re.S)
    if m:
        ans = m.group(1).strip()
        ans = re.split(r"\n\s*\[\[\s*##", ans, maxsplit=1, flags=re.I)[0].strip()
        return ans.strip().strip('"').strip("'").strip()

    # For accidental "answer:" outputs.
    m = re.search(r"(?:^|\n)\s*(?:final answer|answer)\s*:\s*(.+)$", text, flags=re.I | re.S)
    if m:
        return m.group(1).strip().splitlines()[0].strip().strip('"').strip("'").strip()

    return text.splitlines()[0].strip().strip('"').strip("'").strip()


def make_messages(instruction: str, row: dict[str, Any]) -> list[dict[str, str]]:
    question = str(get_field(row, "question", "") or "")
    summary_1 = str(get_field(row, "summary_1", "") or "")
    summary_2 = str(get_field(row, "summary_2", "") or "")

    user = f"""question:
{question}

summary_1:
{summary_1}

summary_2:
{summary_2}
"""
    return [
        {"role": "system", "content": instruction},
        {"role": "user", "content": user},
    ]


def call_model(
    model: str,
    instruction: str,
    row: dict[str, Any],
    temperature: float,
    max_tokens: int,
    retries: int,
) -> str:
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = completion(
                model=model,
                messages=make_messages(instruction, row),
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp["choices"][0]["message"]["content"] or ""
        except Exception as e:
            last_err = e
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"model call failed after {retries + 1} attempts: {last_err}")


def classify_row(row: dict[str, Any]) -> str:
    wrong = float(get_field(row, "score", 0.0) or 0.0) < 1.0
    ret_fail = bool(get_field(row, "missing_after_hop1", [])) and bool(get_field(row, "missing_after_hop2", []))
    if wrong and ret_fail:
        return "wrong_and_retrieval_failure"
    if wrong and not ret_fail:
        return "wrong_but_not_retrieval_failure"
    if (not wrong) and ret_fail:
        return "correct_but_retrieval_failure"
    return "correct_and_not_retrieval_failure"


def eval_one(args_tuple: tuple[int, dict[str, Any], dict[str, Any], str, float, int, int]) -> dict[str, Any]:
    i, row, refs, model, temperature, max_tokens, retries = args_tuple

    gold = get_field(row, "gold_answer", get_field(row, "answer", ""))
    if gold == "":
        gold = get_field(row, "raw", {}).get("answer", "")

    base_raw = call_model(
        model=model,
        instruction=refs["base_final_answerer"]["prompt"],
        row=row,
        temperature=temperature,
        max_tokens=max_tokens,
        retries=retries,
    )
    strong_raw = call_model(
        model=model,
        instruction=refs["strong_final_answerer"]["prompt"],
        row=row,
        temperature=temperature,
        max_tokens=max_tokens,
        retries=retries,
    )

    base_answer = parse_answer(base_raw)
    strong_answer = parse_answer(strong_raw)

    base_score = exact_match(base_answer, gold)
    strong_score = exact_match(strong_answer, gold)
    original_score = bool(float(get_field(row, "score", 0.0) or 0.0) >= 1.0)

    return {
        "row_id": i,
        "idx": get_field(row, "idx", i),
        "bucket": classify_row(row),

        "question": get_field(row, "question", ""),
        "gold_answer": gold,
        "summary_1": get_field(row, "summary_1", ""),
        "summary_2": get_field(row, "summary_2", ""),

        "original_pred_answer": get_field(row, "pred_answer", ""),
        "original_score": original_score,

        "base_raw_output": base_raw,
        "base_answer": base_answer,
        "base_score": base_score,

        "strong_raw_output": strong_raw,
        "strong_answer": strong_answer,
        "strong_score": strong_score,

        "strong_gain_over_base": (not base_score) and strong_score,
        "strong_loss_vs_base": base_score and (not strong_score),
        "strong_tie_with_base": base_score == strong_score,

        "missing_after_hop1": get_field(row, "missing_after_hop1", []),
        "missing_after_hop2": get_field(row, "missing_after_hop2", []),
        "current_query": get_field(row, "current_query", ""),
        "current_hop2_titles": get_field(row, "current_hop2_titles", []),
    }


def mean_bool(rows: list[dict[str, Any]], key: str) -> float | None:
    if not rows:
        return None
    return sum(bool(r.get(key)) for r in rows) / len(rows)


def summarize(rows: list[dict[str, Any]], input_path: Path, refs_path: Path, model: str) -> dict[str, Any]:
    buckets = sorted(set(r["bucket"] for r in rows))
    by_bucket = {}
    for b in buckets:
        br = [r for r in rows if r["bucket"] == b]
        by_bucket[b] = {
            "n": len(br),
            "original_em": mean_bool(br, "original_score"),
            "base_em": mean_bool(br, "base_score"),
            "strong_em": mean_bool(br, "strong_score"),
            "strong_gain_over_base": sum(bool(r["strong_gain_over_base"]) for r in br),
            "strong_loss_vs_base": sum(bool(r["strong_loss_vs_base"]) for r in br),
            "strong_tie_with_base": sum(bool(r["strong_tie_with_base"]) for r in br),
        }

    matrix = Counter(
        f"base_{int(r['base_score'])}_strong_{int(r['strong_score'])}"
        for r in rows
    )

    return {
        "input": str(input_path),
        "refs": str(refs_path),
        "model": model,
        "n": len(rows),
        "original_em": mean_bool(rows, "original_score"),
        "base_em": mean_bool(rows, "base_score"),
        "strong_em": mean_bool(rows, "strong_score"),
        "strong_gain_over_base": sum(bool(r["strong_gain_over_base"]) for r in rows),
        "strong_loss_vs_base": sum(bool(r["strong_loss_vs_base"]) for r in rows),
        "strong_tie_with_base": sum(bool(r["strong_tie_with_base"]) for r in rows),
        "base_strong_matrix": dict(matrix),
        "by_bucket": by_bucket,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_rollout_dev300.jsonl"))
    ap.add_argument("--refs", type=Path, default=Path("experiments/feedback_distance_v2/cache/final_answerer_refs.json"))
    ap.add_argument("--out", type=Path, default=Path("experiments/feedback_distance_v2/results/final_answerer_current_summary_eval.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/feedback_distance_v2/results/final_answerer_current_summary_summary.json"))
    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--num-threads", type=int, default=8)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    refs = read_json(args.refs)
    rows = read_jsonl(args.input)
    if args.limit is not None:
        rows = rows[: args.limit]

    tasks = [
        (i, row, refs, args.model, args.temperature, args.max_tokens, args.retries)
        for i, row in enumerate(rows)
    ]

    out_rows = []
    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        for r in tqdm(ex.map(eval_one, tasks), total=len(tasks), desc="final-only eval"):
            out_rows.append(r)

    out_rows.sort(key=lambda r: r["row_id"])
    write_jsonl(args.out, out_rows)

    summary = summarize(out_rows, args.input, args.refs, args.model)
    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
