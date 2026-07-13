# /home/jinwoo/gepa-official/experiments/prompt_update/scripts/evaluate_positive_safety_prompts.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any

from tqdm import tqdm


# Evaluate positive-safety batch prompts on:
#   1) batch0 custom update set
#   2) full flip_eval_stratified_143 set
#
# Metrics:
#   - MR / missing_recovery_rate
#   - support_recall_hop2
#   - base_EM
#   - strong_EM
#   - flip decomposition vs base condition
#
# This script uses rtrace_base only for evaluation runtime:
#   BM25 search, summarize2, final answerer calls, support metrics, EM parsing.


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

BASE_SCRIPT = Path("experiments/feedback_distance_v2/scripts/run_rtrace_midpoint_validity.py").resolve()
spec = importlib.util.spec_from_file_location("rtrace_base", BASE_SCRIPT)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

# Avoid LiteLLM noisy failures in this experiment path.
# Override rtrace_base.call_model with a local OpenAI Responses API wrapper.
def _normalize_model_name(model: str) -> str:
    return model.split("/", 1)[1] if str(model).startswith("openai/") else str(model)


def _openai_call_model(model, system, user, temperature, max_tokens, retries):
    import time
    from openai import OpenAI

    client = OpenAI()
    model = _normalize_model_name(model)
    last_err = None

    for attempt in range(int(retries) + 1):
        try:
            kwargs = {
                "model": model,
                "input": [
                    {"role": "system", "content": str(system or "")},
                    {"role": "user", "content": str(user or "")},
                ],
                "max_output_tokens": max(16, int(max_tokens)),
            }
            if temperature is not None:
                kwargs["temperature"] = temperature

            try:
                resp = client.responses.create(**kwargs)
            except Exception as e:
                msg = str(e).lower()
                if "temperature" in msg or "unsupported" in msg:
                    kwargs.pop("temperature", None)
                    resp = client.responses.create(**kwargs)
                else:
                    raise

            text = getattr(resp, "output_text", None)
            if text is not None and str(text).strip():
                return str(text)

            chunks = []
            for item in getattr(resp, "output", []) or []:
                for c in getattr(item, "content", []) or []:
                    t = getattr(c, "text", None)
                    if t:
                        chunks.append(str(t))

            if chunks and "\n".join(chunks).strip():
                return "\n".join(chunks)

            raise RuntimeError("empty model output")

        except Exception as e:
            last_err = e
            if attempt < int(retries):
                time.sleep(min(2 ** attempt, 8))

    raise RuntimeError(f"OpenAI Responses call failed after {int(retries) + 1} attempts: {last_err}")


base.call_model = _openai_call_model



def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.open("r", encoding="utf-8") if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def parse_query(raw: str) -> str:
    """Robustly parse a query-writer output into one BM25 query string."""
    text = str(raw or "").strip()
    text = re.sub(r"^```(?:json|text)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    if not text:
        return ""

    text_no_think = re.sub(r"(?is)<think>.*?</think>", "", text).strip()
    if text_no_think.lower().startswith("<think>"):
        inner = re.sub(r"(?is)^\s*<think>\s*", "", text, count=1).strip()
        candidates = []
        for line in inner.splitlines():
            line = line.strip()
            if not line:
                continue
            low = line.lower()
            if low in {"<think>", "</think>"}:
                continue
            if low.startswith((
                "okay", "first", "now", "the user", "i need", "looking",
                "wait", "so,", "therefore", "putting", "another point",
                "the constraints", "the summary", "let me", "also,"
            )):
                continue
            if len(line.split()) >= 3:
                candidates.append(line.strip().strip('"').strip("'"))
        return candidates[-1] if candidates else ""

    text = re.sub(r"(?i)</?think>", "", text_no_think).strip()
    if not text:
        return ""

    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            for k in ["query", "q", "search_query", "bm25_query", "hop2_query", "answer"]:
                if k in obj and str(obj[k]).strip():
                    lines = [l.strip().strip('"').strip("'") for l in str(obj[k]).splitlines() if l.strip()]
                    return lines[-1] if lines else ""
    except Exception:
        pass

    m = re.search(
        r"(?:^|\n)\s*(?:final\s+)?(?:bm25\s+|search\s+|second-hop\s+|hop2\s+)?(?:query|answer)\s*[:：]\s*(.+)$",
        text,
        flags=re.I | re.S,
    )
    if m:
        lines = [l.strip().strip('"').strip("'") for l in m.group(1).splitlines() if l.strip()]
        return lines[-1] if lines else ""

    lines = []
    for line in text.splitlines():
        line = line.strip().strip("`").strip()
        if not line:
            continue
        low = line.lower()
        if low in {"<think>", "</think>"}:
            continue
        if low.startswith(("rationale:", "explanation:", "reasoning:", "note:")):
            continue
        line = re.sub(r"^\s*[-*]\s+", "", line).strip()
        line = re.sub(r"^\s*\d+[.)]\s+", "", line).strip()
        line = line.strip('"').strip("'").strip()
        if line:
            lines.append(line)

    if not lines:
        return ""

    q = lines[-1]
    if q.lower().startswith("<think>") or q.lower() == "</think>":
        return ""

    return q


def make_query_user(question: str, summary_1: str) -> str:
    return f"""question:
{question}

summary_1:
{summary_1}

Return only the second-hop BM25 query string.
"""


def run_query_writer(
    *,
    model: str,
    prompt: str,
    question: str,
    summary_1: str,
    temperature: float,
    max_tokens: int,
    retries: int,
) -> dict[str, Any]:
    raw = base.call_model(
        model,
        prompt + "\n\nOutput only the query string.",
        make_query_user(question, summary_1),
        temperature,
        max_tokens,
        retries,
    )
    query = parse_query(raw)

    if query:
        return {"query": query, "raw": raw}

    retry_raw = base.call_model(
        model,
        prompt + "\n\nYou previously returned an empty output. Return exactly one non-empty compact BM25 query string. No explanation.",
        make_query_user(question, summary_1),
        temperature,
        max_tokens,
        retries,
    )
    retry_query = parse_query(retry_raw)

    if retry_query:
        return {
            "query": retry_query,
            "raw": retry_raw,
            "empty_first_raw": raw,
            "empty_query_retry_used": True,
        }

    fallback = f"{question} {summary_1}"
    fallback = " ".join(fallback.split())[:300]
    return {
        "query": fallback,
        "raw": retry_raw,
        "empty_first_raw": raw,
        "empty_query_retry_used": True,
        "empty_query_fallback_used": True,
    }


def flatten_case_ids(obj: Any) -> list[int]:
    """Robustly collect case ids from split structures."""
    ids: list[int] = []

    if obj is None:
        return ids

    if isinstance(obj, int):
        return [int(obj)]

    if isinstance(obj, str):
        if obj.isdigit():
            return [int(obj)]
        return []

    if isinstance(obj, list):
        for x in obj:
            ids.extend(flatten_case_ids(x))
        return ids

    if isinstance(obj, dict):
        # Prefer explicit fields when present.
        for key in ["case_ids", "ids"]:
            if key in obj:
                return flatten_case_ids(obj[key])
        if "case_ids_by_bucket" in obj:
            return flatten_case_ids(obj["case_ids_by_bucket"])
        if "by_bucket" in obj:
            return flatten_case_ids(obj["by_bucket"])

        # Fallback for dict like {"C_clean": [...], ...}
        for v in obj.values():
            ids.extend(flatten_case_ids(v))
        return ids

    return ids


def unique_preserve_order(xs: list[int]) -> list[int]:
    seen = set()
    out = []
    for x in xs:
        x = int(x)
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def get_scope_case_ids(split: dict[str, Any], *, scope: str, composition: str, batch_id: int) -> list[int]:
    if scope in {"batch", "update_batch", "batch0"}:
        batch = split["update_batches"]["compositions"][composition]["batches"][batch_id]
        return unique_preserve_order(flatten_case_ids(batch.get("case_ids_by_bucket", batch)))

    if scope in {"full143", "eval143", "flip_eval_stratified_143"}:
        ev = split.get("eval_split")
        return unique_preserve_order(flatten_case_ids(ev))

    raise ValueError(f"unknown eval scope: {scope}")


def compact_current_reference(rec: dict[str, Any]) -> dict[str, Any]:
    s = rec.get("current_state") or {}
    return {
        "current_query": s.get("query"),
        "current_titles": s.get("retrieved_titles") or [],
        "current_missing_titles_after_hop2": s.get("missing_titles_after_hop2") or [],
        "current_support_recall_total": s.get("support_recall_total"),
        "current_score": s.get("score"),
    }



def _norm_title(x: Any) -> str:
    return " ".join(str(x or "").lower().strip().split())


def direct_retrieval_metrics(titles: list[str], rec: dict[str, Any]) -> dict[str, Any]:
    """Compute support recall and MR directly from case_state_index schema.

    MR is defined over the support titles missing from the fixed current hop2 state:
        recovered_missing_count / len(current_missing_titles_after_hop2)

    For C_clean/W_other with no current missing support titles, MR is left as None.
    """
    title_set = {_norm_title(t) for t in titles if str(t or "").strip()}

    gold_titles = rec.get("gold_support_titles") or []
    gold_norm = [_norm_title(t) for t in gold_titles if str(t or "").strip()]
    hit_gold = sum(1 for t in gold_norm if t in title_set)

    current_state = rec.get("current_state") or {}
    missing = (
        current_state.get("missing_titles_after_hop2")
        or current_state.get("missing_after_hop2")
        or rec.get("missing_after_hop2")
        or []
    )
    missing_norm = [_norm_title(t) for t in missing if str(t or "").strip()]
    recovered_missing = sum(1 for t in missing_norm if t in title_set)

    return {
        "support_recall_hop2": hit_gold / len(gold_norm) if gold_norm else None,
        "hit_gold_count": hit_gold,
        "missing_recovery_rate": recovered_missing / len(missing_norm) if missing_norm else None,
        "recovered_missing_count": recovered_missing,
        "missing_count_for_mr": len(missing_norm),
    }



def evaluate_query(
    *,
    query: str,
    rec: dict[str, Any],
    refs: dict[str, Any],
    model: str,
    temperature: float,
    k: int,
    summary_max_tokens: int,
    answer_max_tokens: int,
    retries: int,
) -> dict[str, Any]:
    question = str(rec.get("question") or "")
    summary_1 = str(rec.get("summary_1") or "")
    gold = rec.get("gold_answer")

    docs = list(base.search(query, k=k).passages)
    titles = base.extract_titles(docs)

    summary_2 = base.call_model(
        model,
        refs["summarize2_prompt"],
        base.make_summary2_user(question, summary_1, docs),
        temperature,
        summary_max_tokens,
        retries,
    )

    final_user = base.make_final_user(question, summary_1, summary_2)

    base_raw = base.call_model(
        model,
        refs["base_final_answerer"]["prompt"],
        final_user,
        temperature,
        answer_max_tokens,
        retries,
    )
    strong_raw = base.call_model(
        model,
        refs["strong_final_answerer"]["prompt"],
        final_user,
        temperature,
        answer_max_tokens,
        retries,
    )

    base_answer = base.parse_answer(base_raw)
    strong_answer = base.parse_answer(strong_raw)

    # support_metrics expects a source-row-like dict.
    source_like = {
        "gold_support_titles": rec.get("gold_support_titles") or [],
        "missing_after_hop2": (rec.get("current_state") or {}).get("missing_titles_after_hop2") or [],
        "missing_titles_after_hop2": (rec.get("current_state") or {}).get("missing_titles_after_hop2") or [],
    }
    source_like.update(rec)

    metrics = base.support_metrics(titles, source_like)
    direct_metrics = direct_retrieval_metrics(titles, rec)

    support_recall_hop2 = (
        direct_metrics.get("support_recall_hop2")
        if direct_metrics.get("support_recall_hop2") is not None
        else metrics.get("support_recall_hop2")
    )
    missing_recovery_rate = (
        direct_metrics.get("missing_recovery_rate")
        if direct_metrics.get("missing_recovery_rate") is not None
        else metrics.get("missing_recovery_rate")
    )

    return {
        "generated_query": query,
        "retrieved_titles": titles,
        "retrieved_docs": docs,
        "summary_2": summary_2,
        "support_recall_hop2": support_recall_hop2,
        "missing_recovery_rate": missing_recovery_rate,
        "hit_gold_count": direct_metrics.get("hit_gold_count", metrics.get("hit_gold_count")),
        "recovered_missing_count": direct_metrics.get("recovered_missing_count", metrics.get("recovered_missing_count")),
        "missing_count_for_mr": direct_metrics.get("missing_count_for_mr"),
        "base_raw_output": base_raw,
        "base_answer": base_answer,
        "base_score": bool(base.exact_match(base_answer, gold)),
        "strong_raw_output": strong_raw,
        "strong_answer": strong_answer,
        "strong_score": bool(base.exact_match(strong_answer, gold)),
    }


def run_one(task: tuple) -> dict[str, Any]:
    (
        scope,
        condition_row,
        rec,
        refs,
        model,
        temperature,
        query_max_tokens,
        summary_max_tokens,
        answer_max_tokens,
        retries,
        k,
    ) = task

    condition = condition_row["condition"]
    prompt = condition_row["updated_prompt"]

    q = run_query_writer(
        model=model,
        prompt=prompt,
        question=str(rec.get("question") or ""),
        summary_1=str(rec.get("summary_1") or ""),
        temperature=temperature,
        max_tokens=query_max_tokens,
        retries=retries,
    )

    ev = evaluate_query(
        query=q["query"],
        rec=rec,
        refs=refs,
        model=model,
        temperature=temperature,
        k=k,
        summary_max_tokens=summary_max_tokens,
        answer_max_tokens=answer_max_tokens,
        retries=retries,
    )

    return {
        "row_type": "positive_safety_eval",
        "eval_scope": scope,
        "condition": condition,
        "condition_evidence_mode": condition_row.get("evidence_mode"),
        "case_id": int(rec["case_id"]),
        "bucket": rec.get("bucket"),
        "question": rec.get("question"),
        "gold_answer": rec.get("gold_answer"),
        "gold_support_titles": rec.get("gold_support_titles") or [],
        **compact_current_reference(rec),
        "query_raw": q.get("raw"),
        "empty_first_raw": q.get("empty_first_raw"),
        "empty_query_retry_used": q.get("empty_query_retry_used", False),
        "empty_query_fallback_used": q.get("empty_query_fallback_used", False),
        **ev,
    }


def run_one_safe(task: tuple) -> dict[str, Any]:
    # Optional last tuple element is task_retries.
    if len(task) >= 12 and isinstance(task[-1], int):
        task_retries = int(task[-1])
        base_task = task[:-1]
    else:
        task_retries = 0
        base_task = task

    scope, condition_row, rec, *_ = base_task
    last_e = None
    last_tb = None

    for attempt in range(task_retries + 1):
        try:
            row = run_one(base_task)
            row["task_attempt"] = attempt + 1
            return row
        except Exception as e:
            last_e = e
            last_tb = traceback.format_exc()
            if attempt < task_retries:
                import time
                time.sleep(min(2 ** attempt, 8))

    return {
        "row_type": "positive_safety_eval",
        "error": True,
        "eval_scope": scope,
        "condition": condition_row.get("condition"),
        "case_id": int(rec.get("case_id")),
        "bucket": rec.get("bucket"),
        "task_attempts": task_retries + 1,
        "error_type": type(last_e).__name__,
        "error_message": str(last_e),
        "traceback": last_tb,
    }


def mean(rows: list[dict[str, Any]], key: str) -> float | None:
    vals = [r.get(key) for r in rows if r.get(key) is not None]
    if not vals:
        return None
    return sum(float(v) for v in vals) / len(vals)


def mean_bool(rows: list[dict[str, Any]], key: str) -> float | None:
    if not rows:
        return None
    return sum(bool(r.get(key)) for r in rows) / len(rows)


def summarize_subset(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "n": len(rows),
        "mean_mr": mean(rows, "missing_recovery_rate"),
        "mean_support_recall_hop2": mean(rows, "support_recall_hop2"),
        "base_em": mean_bool(rows, "base_score"),
        "strong_em": mean_bool(rows, "strong_score"),
        "base_correct": sum(bool(r.get("base_score")) for r in rows),
        "strong_correct": sum(bool(r.get("strong_score")) for r in rows),
    }


def flip_summary(rows: list[dict[str, Any]], *, score_key: str) -> dict[str, Any]:
    """Compare each condition against base within the same eval scope."""
    base_rows = [r for r in rows if r.get("condition") == "base"]
    base_by_case = {int(r["case_id"]): bool(r.get(score_key)) for r in base_rows}

    out = {}
    for cond in sorted({r.get("condition") for r in rows}):
        cond_rows = [r for r in rows if r.get("condition") == cond]
        wr = rw = rr = ww = missing = 0

        for r in cond_rows:
            cid = int(r["case_id"])
            if cid not in base_by_case:
                missing += 1
                continue
            before = base_by_case[cid]
            after = bool(r.get(score_key))

            if not before and after:
                wr += 1
            elif before and not after:
                rw += 1
            elif before and after:
                rr += 1
            else:
                ww += 1

        n = wr + rw + rr + ww
        out[cond] = {
            "n": n,
            "W_to_R": wr,
            "R_to_W": rw,
            "stable_right": rr,
            "stable_wrong": ww,
            "missing_base": missing,
            "net": wr - rw,
            "flip_rate": (wr + rw) / n if n else None,
            "W_to_R_rate": wr / n if n else None,
            "R_to_W_rate": rw / n if n else None,
        }

    return out


def build_summary(rows: list[dict[str, Any]], split: dict[str, Any]) -> dict[str, Any]:
    ok = [r for r in rows if not r.get("error")]
    err = [r for r in rows if r.get("error")]

    summary: dict[str, Any] = {
        "n_rows": len(rows),
        "n_ok": len(ok),
        "n_error": len(err),
        "by_scope_condition": {},
        "by_scope_condition_bucket": {},
        "flip_vs_base": {
            "strong": {},
            "base": {},
        },
    }

    for scope in sorted({r.get("eval_scope") for r in ok}):
        scope_rows = [r for r in ok if r.get("eval_scope") == scope]
        summary["by_scope_condition"][scope] = {}

        for cond in sorted({r.get("condition") for r in scope_rows}):
            cr = [r for r in scope_rows if r.get("condition") == cond]
            summary["by_scope_condition"][scope][cond] = summarize_subset(cr)

        summary["by_scope_condition_bucket"][scope] = {}
        for cond in sorted({r.get("condition") for r in scope_rows}):
            summary["by_scope_condition_bucket"][scope][cond] = {}
            cr = [r for r in scope_rows if r.get("condition") == cond]
            for b in sorted({r.get("bucket") for r in cr}):
                br = [r for r in cr if r.get("bucket") == b]
                summary["by_scope_condition_bucket"][scope][cond][b] = summarize_subset(br)

        summary["flip_vs_base"]["strong"][scope] = flip_summary(scope_rows, score_key="strong_score")
        summary["flip_vs_base"]["base"][scope] = flip_summary(scope_rows, score_key="base_score")

    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    lines = []
    lines.append("# Positive Safety Batch0 Evaluation")
    lines.append("")
    lines.append(f"- n_ok: {summary['n_ok']}")
    lines.append(f"- n_error: {summary['n_error']}")
    lines.append("")

    for scope, by_cond in summary["by_scope_condition"].items():
        lines.append(f"## Scope: {scope}")
        lines.append("")
        lines.append("| condition | n | MR | support_recall | base_EM | strong_EM |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for cond, s in by_cond.items():
            lines.append(
                f"| {cond} | {s['n']} | "
                f"{fmt(s['mean_mr'])} | {fmt(s['mean_support_recall_hop2'])} | "
                f"{fmt(s['base_em'])} | {fmt(s['strong_em'])} |"
            )
        lines.append("")

        lines.append(f"### Strong flip vs base: {scope}")
        lines.append("")
        lines.append("| condition | n | W→R | R→W | stable R | stable W | net | flip_rate |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for cond, s in summary["flip_vs_base"]["strong"][scope].items():
            lines.append(
                f"| {cond} | {s['n']} | {s['W_to_R']} | {s['R_to_W']} | "
                f"{s['stable_right']} | {s['stable_wrong']} | {s['net']} | {fmt(s['flip_rate'])} |"
            )
        lines.append("")

        lines.append(f"### Bucket strong_EM: {scope}")
        lines.append("")
        lines.append("| condition | bucket | n | strong_EM | MR |")
        lines.append("|---|---|---:|---:|---:|")
        for cond, by_bucket in summary["by_scope_condition_bucket"][scope].items():
            for bucket, s in by_bucket.items():
                lines.append(
                    f"| {cond} | {bucket} | {s['n']} | {fmt(s['strong_em'])} | {fmt(s['mean_mr'])} |"
                )
        lines.append("")

    return "\n".join(lines)


def fmt(x: Any) -> str:
    if x is None:
        return ""
    try:
        return f"{float(x):.4f}"
    except Exception:
        return str(x)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()

    ap.add_argument("--split", type=Path, default=Path("experiments/prompt_update/data/positive_safety_b10_split_seed0.json"))
    ap.add_argument("--case-state-index", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/case_state_index.json"))
    ap.add_argument("--prompts", type=Path, default=Path("experiments/prompt_update/results/positive_safety_b10_batch0_prompts.jsonl"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/prompt_update/cache/fixed_prompt_config.json"))
    ap.add_argument("--final-answerer-refs", type=Path, default=Path("experiments/prompt_update/cache/final_answerer_refs.json"))

    ap.add_argument("--out", type=Path, default=Path("experiments/prompt_update/results/positive_safety_b10_batch0_eval.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/prompt_update/results/positive_safety_b10_batch0_eval_summary.json"))
    ap.add_argument("--summary-md", type=Path, default=Path("experiments/prompt_update/results/positive_safety_b10_batch0_eval_summary.md"))

    ap.add_argument("--composition", type=str, default="mixed_custom")
    ap.add_argument("--batch-id", type=int, default=0)
    ap.add_argument("--scopes", nargs="+", default=["batch0", "full143"])
    ap.add_argument("--conditions", nargs="+", default=None)

    ap.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--query-max-tokens", type=int, default=512)
    ap.add_argument("--summary-max-tokens", type=int, default=4096)
    ap.add_argument("--answer-max-tokens", type=int, default=2048)
    ap.add_argument("--num-threads", type=int, default=12)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--task-retries", type=int, default=2)

    ap.add_argument("--overwrite", action="store_true")

    return ap.parse_args()


def main() -> None:
    args = parse_args()

    base.set_retriever_dir(str(args.retriever_dir))

    split = read_json(args.split)
    index = read_json(args.case_state_index)
    prompt_rows = [r for r in read_jsonl(args.prompts) if not r.get("error")]

    if args.conditions:
        keep = set(args.conditions)
        prompt_rows = [r for r in prompt_rows if r.get("condition") in keep]

    fixed_cfg = read_json(args.fixed_prompt_config)
    final_refs = read_json(args.final_answerer_refs)
    refs = {
        **final_refs,
        "summarize2_prompt": fixed_cfg["prompt_candidate"]["prompts"]["summarize2.predict"],
    }

    if args.overwrite and args.out.exists():
        args.out.unlink()

    existing = []
    done = set()
    if args.out.exists():
        existing = read_jsonl(args.out)
        for r in existing:
            if not r.get("error"):
                done.add((r.get("eval_scope"), r.get("condition"), int(r.get("case_id"))))

    tasks = []
    scope_case_ids = {}

    for scope in args.scopes:
        case_ids = get_scope_case_ids(
            split,
            scope=scope,
            composition=args.composition,
            batch_id=args.batch_id,
        )
        scope_label = f"batch{args.batch_id}" if scope in {"batch", "update_batch", "batch0"} else scope
        scope_case_ids[scope_label] = case_ids

        for cond in prompt_rows:
            for cid in case_ids:
                rec = dict(index["cases"][str(int(cid))])
                rec["case_id"] = int(cid)

                key = (scope_label, cond["condition"], int(cid))
                if key in done:
                    continue

                tasks.append((
                    scope_label,
                    cond,
                    rec,
                    refs,
                    args.model,
                    args.temperature,
                    args.query_max_tokens,
                    args.summary_max_tokens,
                    args.answer_max_tokens,
                    args.retries,
                    args.k,
                    args.task_retries,
                ))

    print("[info] conditions:", [r["condition"] for r in prompt_rows])
    print("[info] scopes:", {k: len(v) for k, v in scope_case_ids.items()})
    print("[info] pending eval rows:", len(tasks))
    print("[info] existing rows:", len(existing))

    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(run_one_safe, t) for t in tasks]
        for fut in tqdm(cf.as_completed(futs), total=len(futs), desc="positive safety eval"):
            append_jsonl(args.out, fut.result())

    all_rows = read_jsonl(args.out)
    summary = build_summary(all_rows, split)
    summary.update({
        "script": "evaluate_positive_safety_prompts.py",
        "split": str(args.split),
        "case_state_index": str(args.case_state_index),
        "prompts": str(args.prompts),
        "out": str(args.out),
        "scopes": scope_case_ids,
        "model": args.model,
        "k": args.k,
        "retriever_dir": str(args.retriever_dir),
    })

    write_json(args.summary_out, summary)
    write_text(args.summary_md, render_markdown(summary))

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print("[wrote]", args.summary_md)
    print(json.dumps({
        "n_ok": summary["n_ok"],
        "n_error": summary["n_error"],
        "scopes": {k: len(v) for k, v in scope_case_ids.items()},
        "by_scope_condition": summary["by_scope_condition"],
    }, ensure_ascii=False, indent=2)[:5000])


if __name__ == "__main__":
    main()
