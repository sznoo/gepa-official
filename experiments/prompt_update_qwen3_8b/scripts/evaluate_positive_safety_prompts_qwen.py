# /home/jinwoo/gepa-official/experiments/prompt_update_qwen3_8b/scripts/evaluate_positive_safety_prompts_qwen.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import math
import os
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from openai import OpenAI
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

BASE_SCRIPT = (ROOT / "experiments/feedback_distance_v2/scripts/run_rtrace_midpoint_validity.py").resolve()
spec = importlib.util.spec_from_file_location("rtrace_base", BASE_SCRIPT)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)


HOP2_COMPONENT = "create_query_hop2.predict"
SUMMARIZE2_COMPONENT = "summarize2.predict"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def truncate(x: Any, n: int) -> str:
    try:
        return base.truncate(str(x or ""), n)
    except Exception:
        s = str(x or "")
        return s if len(s) <= n else s[:n]


def strip_qwen_thinking(text: str) -> str:
    text = str(text or "").strip()
    if not text:
        return ""

    text = re.sub(r"^```(?:json|text)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    # Complete Qwen thinking block.
    text = re.sub(r"(?is)^\s*<think>.*?</think>\s*", "", text).strip()
    text = re.sub(r"(?is)<think>.*?</think>\s*", "", text).strip()

    # Unclosed thinking block: no reliable final answer.
    if text.lower().startswith("<think>"):
        return ""

    text = re.sub(r"(?i)</?think>", "", text).strip()
    return text


def extract_json_obj(text: str) -> dict[str, Any]:
    text = strip_qwen_thinking(text)
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError(f"could not find JSON object in: {text[:500]}")
    return json.loads(m.group(0))


def parse_query(raw: str) -> str:
    """Parse one compact BM25 query from Qwen output."""
    text = str(raw or "").strip()
    text = re.sub(r"^```(?:json|text)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    if not text:
        return ""

    text_no_think = re.sub(r"(?is)<think>.*?</think>", "", text).strip()

    # If thinking block is unclosed, try to recover the last plausible query-like line.
    if text_no_think.lower().startswith("<think>"):
        inner = re.sub(r"(?is)^\s*<think>\s*", "", text, count=1).strip()
        candidates = []
        for line in inner.splitlines():
            line = line.strip().strip("`").strip()
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
        obj = extract_json_obj(text)
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


def chat_call(
    *,
    client: OpenAI,
    model: str,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    strip_think: bool = True,
) -> str:
    last_err: Exception | None = None

    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            raw = resp.choices[0].message.content or ""
            if not strip_think:
                return raw

            clean = strip_qwen_thinking(raw)
            if clean:
                return clean

            # If Qwen spent the whole budget inside <think>, retry.
            if "<think>" in raw.lower():
                raise RuntimeError("empty final content after stripping Qwen thinking block")

            return clean
        except Exception as e:
            last_err = e
            time.sleep(min(2.0 * (attempt + 1), 8.0))

    assert last_err is not None
    raise last_err


def make_query_user(question: str, summary_1: str) -> str:
    return f"""question:
{question}

summary_1:
{summary_1}

Return only the second-hop BM25 query string.
"""


def run_query_writer(
    *,
    client: OpenAI,
    model: str,
    prompt: str,
    question: str,
    summary_1: str,
    temperature: float,
    max_tokens: int,
    retries: int,
) -> dict[str, Any]:
    raw = chat_call(
        client=client,
        model=model,
        system=prompt + "\n\nOutput only one compact BM25 query string. No explanation.",
        user=make_query_user(question, summary_1),
        temperature=temperature,
        max_tokens=max_tokens,
        retries=retries,
        strip_think=False,
    )
    query = parse_query(raw)

    if query:
        return {"query": query, "raw": raw}

    retry_raw = chat_call(
        client=client,
        model=model,
        system=prompt + "\n\nYou previously returned an empty output. Return exactly one non-empty compact BM25 query string. No explanation.",
        user=make_query_user(question, summary_1),
        temperature=temperature,
        max_tokens=max_tokens,
        retries=retries,
        strip_think=False,
    )
    retry_query = parse_query(retry_raw)
    if retry_query:
        return {
            "query": retry_query,
            "raw": retry_raw,
            "empty_first_raw": raw,
            "empty_query_retry_used": True,
        }

    fallback = " ".join(f"{question} {summary_1}".split())[:300]
    return {
        "query": fallback,
        "raw": retry_raw,
        "empty_first_raw": raw,
        "empty_query_retry_used": True,
        "empty_query_fallback_used": True,
    }


def normalize_case_index(case_state_index: Any) -> dict[int, dict[str, Any]]:
    if isinstance(case_state_index, dict):
        if isinstance(case_state_index.get("cases"), dict):
            return {int(k): v for k, v in case_state_index["cases"].items()}
        if isinstance(case_state_index.get("case_state_index"), dict):
            return {int(k): v for k, v in case_state_index["case_state_index"].items()}
        if all(str(k).isdigit() for k in case_state_index.keys()):
            return {int(k): v for k, v in case_state_index.items()}
        if isinstance(case_state_index.get("rows"), list):
            return {int(r.get("case_id", r.get("idx", i))): r for i, r in enumerate(case_state_index["rows"])}

    if isinstance(case_state_index, list):
        return {int(r.get("case_id", r.get("idx", i))): r for i, r in enumerate(case_state_index)}

    raise ValueError("Unsupported case_state_index format")


def unwrap_source(case: dict[str, Any]) -> dict[str, Any]:
    for k in ["source_row", "source", "rollout", "rollout_row", "current", "current_state"]:
        v = case.get(k)
        if isinstance(v, dict) and v.get("question"):
            merged = dict(case)
            merged.update(v)
            return merged
    return case


def get_case_field(case: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in case and case.get(k) is not None:
            return case.get(k)
    for nested in ["source_row", "source", "rollout", "rollout_row", "current", "current_state"]:
        obj = case.get(nested)
        if isinstance(obj, dict):
            for k in keys:
                if k in obj and obj.get(k) is not None:
                    return obj.get(k)
    return default


def get_prompt_text(prompt_row: dict[str, Any], fixed_cfg: dict[str, Any]) -> str:
    condition = str(prompt_row.get("condition") or "")

    if condition == "base":
        try:
            return fixed_cfg["prompt_candidate"]["prompts"][HOP2_COMPONENT]
        except Exception:
            pass

    for k in ["updated_prompt", "prompt", "instruction", "new_prompt"]:
        if str(prompt_row.get(k) or "").strip():
            return str(prompt_row[k]).strip()

    pc = prompt_row.get("prompt_candidate")
    if isinstance(pc, dict):
        prompts = pc.get("prompts", pc)
        if isinstance(prompts, dict) and str(prompts.get(HOP2_COMPONENT) or "").strip():
            return str(prompts[HOP2_COMPONENT]).strip()

    try:
        return fixed_cfg["prompt_candidate"]["prompts"][HOP2_COMPONENT]
    except Exception as e:
        raise KeyError(f"Cannot find prompt text for condition={condition}") from e


def get_summarize2_prompt(fixed_cfg: dict[str, Any]) -> str:
    return fixed_cfg["prompt_candidate"]["prompts"][SUMMARIZE2_COMPONENT]


def get_final_prompt(final_refs: dict[str, Any], name: str) -> str:
    candidates = [
        name,
        f"{name}_prompt",
        f"{name}.prompt",
    ]
    for k in candidates:
        v = final_refs.get(k)
        if isinstance(v, str) and v.strip():
            return v
        if isinstance(v, dict):
            for kk in ["prompt", "instruction", "system"]:
                if isinstance(v.get(kk), str) and v.get(kk).strip():
                    return v[kk]

    # Common names from previous scripts.
    if name == "base_final_answerer":
        for k in ["base_final_answerer", "final_answerer", "answerer"]:
            v = final_refs.get(k)
            if isinstance(v, dict) and isinstance(v.get("prompt"), str):
                return v["prompt"]

    if name == "strong_final_answerer":
        for k in ["strong_final_answerer", "final_answerer", "answerer"]:
            v = final_refs.get(k)
            if isinstance(v, dict) and isinstance(v.get("prompt"), str):
                return v["prompt"]

    raise KeyError(f"Cannot find final prompt: {name}")


def support_metrics(titles: list[str], source: dict[str, Any]) -> dict[str, Any]:
    try:
        return base.support_metrics(titles, source)
    except Exception:
        gold = list(source.get("gold_support_titles") or [])
        missing = list(
            source.get("missing_after_hop1")
            or source.get("missing_titles_after_hop1")
            or source.get("missing_after_hop2")
            or source.get("missing_titles_after_hop2")
            or gold
        )
        title_set = set(titles)
        gold_hit = [t for t in gold if t in title_set]
        missing_hit = [t for t in missing if t in title_set]
        return {
            "support_recall_hop2": len(gold_hit) / len(gold) if gold else None,
            "missing_recovery_rate": len(missing_hit) / len(missing) if missing else 1.0,
            "hit_gold_count": len(gold_hit),
            "recovered_missing_count": len(missing_hit),
        }


def exact_match(pred: str, gold: Any) -> bool:
    try:
        return bool(base.exact_match(pred, gold))
    except Exception:
        def norm(x: Any) -> str:
            x = str(x or "").lower()
            x = re.sub(r"[^a-z0-9가-힣 ]+", " ", x)
            x = re.sub(r"\s+", " ", x).strip()
            return x
        return norm(pred) == norm(gold)


def evaluate_one(
    *,
    client: OpenAI,
    model: str,
    temperature: float,
    prompt_row: dict[str, Any],
    prompt_text: str,
    case_id: int,
    source: dict[str, Any],
    refs: dict[str, str],
    k: int,
    query_max_tokens: int,
    summary_max_tokens: int,
    answer_max_tokens: int,
    retries: int,
    eval_scope: str,
) -> dict[str, Any]:
    question = str(get_case_field(source, "question", default="") or "")
    summary_1 = str(get_case_field(source, "summary_1", default="") or "")
    gold_answer = get_case_field(source, "gold_answer", "answer", default=None)

    q = run_query_writer(
        client=client,
        model=model,
        prompt=prompt_text,
        question=question,
        summary_1=summary_1,
        temperature=temperature,
        max_tokens=query_max_tokens,
        retries=retries,
    )

    docs = list(base.search(q["query"], k=k).passages)
    titles = base.extract_titles(docs)

    summary_2 = chat_call(
        client=client,
        model=model,
        system=refs["summarize2_prompt"],
        user=base.make_summary2_user(question, summary_1, docs),
        temperature=temperature,
        max_tokens=summary_max_tokens,
        retries=retries,
        strip_think=True,
    )

    final_user = base.make_final_user(question, summary_1, summary_2)

    base_raw = chat_call(
        client=client,
        model=model,
        system=refs["base_final_answerer_prompt"],
        user=final_user,
        temperature=temperature,
        max_tokens=answer_max_tokens,
        retries=retries,
        strip_think=True,
    )
    strong_raw = chat_call(
        client=client,
        model=model,
        system=refs["strong_final_answerer_prompt"],
        user=final_user,
        temperature=temperature,
        max_tokens=answer_max_tokens,
        retries=retries,
        strip_think=True,
    )

    base_answer = base.parse_answer(base_raw)
    strong_answer = base.parse_answer(strong_raw)
    metrics = support_metrics(titles, source)

    return {
        "condition": prompt_row.get("condition"),
        "eval_scope": eval_scope,
        "case_id": case_id,
        "idx": get_case_field(source, "idx", "example_id", default=case_id),

        "question": question,
        "gold_answer": gold_answer,
        "gold_support_titles": get_case_field(source, "gold_support_titles", default=[]),
        "missing_after_hop1": get_case_field(source, "missing_after_hop1", "missing_titles_after_hop1", default=[]),
        "missing_after_hop2": get_case_field(source, "missing_after_hop2", "missing_titles_after_hop2", default=[]),

        "updated_prompt": prompt_text,
        "prompt_rationale": prompt_row.get("rationale") or prompt_row.get("prompt_update_rationale"),

        "generated_query": q["query"],
        "query_raw": q.get("raw"),
        "empty_query_retry_used": q.get("empty_query_retry_used", False),
        "empty_query_fallback_used": q.get("empty_query_fallback_used", False),

        "retrieved_titles": titles,
        "retrieved_docs": docs,
        "summary_2": summary_2,

        "support_recall_hop2": metrics.get("support_recall_hop2"),
        "missing_recovery_rate": metrics.get("missing_recovery_rate"),
        "hit_gold_count": metrics.get("hit_gold_count"),
        "recovered_missing_count": metrics.get("recovered_missing_count"),

        "base_raw_output": base_raw,
        "base_answer": base_answer,
        "base_score": exact_match(base_answer, gold_answer),

        "strong_raw_output": strong_raw,
        "strong_answer": strong_answer,
        "strong_score": exact_match(strong_answer, gold_answer),

        "current_missing_recovery_rate": get_case_field(source, "current_missing_recovery_rate", "missing_recovery_rate", default=None),
        "current_support_recall_hop2": get_case_field(source, "current_support_recall_hop2", "support_recall_hop2_only", "support_recall_hop2", default=None),
        "current_score": get_case_field(source, "score", default=None),
    }


def run_task_safe(task: dict[str, Any]) -> dict[str, Any]:
    task_retries = int(task.pop("task_retries"))
    for attempt in range(task_retries):
        try:
            return evaluate_one(**task)
        except Exception as e:
            last = {
                "error": True,
                "condition": task["prompt_row"].get("condition"),
                "eval_scope": task["eval_scope"],
                "case_id": task["case_id"],
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "attempt": attempt + 1,
            }
            time.sleep(min(2.0 * (attempt + 1), 8.0))
    return last


def unique_ints(xs: list[Any]) -> list[int]:
    out = []
    seen = set()
    for x in xs:
        i = int(x)
        if i not in seen:
            out.append(i)
            seen.add(i)
    return out


def batch_case_ids(split: dict[str, Any], composition: str, batch_id: int) -> list[int]:
    comp = split["update_batches"]["compositions"][composition]
    b = comp["batches"][batch_id]

    if isinstance(b, dict) and "case_ids_by_bucket" in b:
        ids = []
        for vs in b["case_ids_by_bucket"].values():
            ids.extend(vs)
        return unique_ints(ids)

    if isinstance(b, dict) and "case_ids" in b:
        return unique_ints(b["case_ids"])

    if isinstance(b, list):
        return unique_ints(b)

    raise KeyError(f"Cannot parse batch case ids for composition={composition} batch_id={batch_id}")


def eval_scope_case_ids(split: dict[str, Any], scope: str, composition: str, batch_id: int) -> tuple[str, list[int]]:
    if scope == "batch":
        return f"batch{batch_id}", batch_case_ids(split, composition, batch_id)

    if scope.startswith("batch") and scope[5:].isdigit():
        bid = int(scope[5:])
        return scope, batch_case_ids(split, composition, bid)

    ev = split.get("eval_split")

    if isinstance(ev, dict):
        if scope in ev:
            v = ev[scope]
            if isinstance(v, dict):
                for kk in ["case_ids", "ids", "cases"]:
                    if kk in v:
                        return scope, unique_ints(v[kk])
            if isinstance(v, list):
                return scope, unique_ints(v)

        for kk in ["case_ids", "ids", "cases"]:
            if kk in ev and isinstance(ev[kk], list):
                return scope, unique_ints(ev[kk])

    if isinstance(ev, list):
        return scope, unique_ints(ev)

    # Fallback for common positive-safety split.
    if scope == "full143" and isinstance(split.get("case_meta"), dict):
        return scope, unique_ints(split["case_meta"].keys())

    raise KeyError(f"Cannot parse eval scope case ids: {scope}")


def mean(vals: list[Any]) -> float | None:
    xs = [float(v) for v in vals if v is not None]
    return sum(xs) / len(xs) if xs else None


def mean_bool(vals: list[Any]) -> float | None:
    xs = [bool(v) for v in vals]
    return sum(xs) / len(xs) if xs else None


def stderr(vals: list[Any]) -> float | None:
    xs = [float(v) for v in vals if v is not None]
    if not xs:
        return None
    if len(xs) == 1:
        return 0.0
    m = sum(xs) / len(xs)
    var = sum((v - m) ** 2 for v in xs) / (len(xs) - 1)
    return math.sqrt(var) / math.sqrt(len(xs))


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in rows if not r.get("error")]
    errors = [r for r in rows if r.get("error")]

    out: dict[str, Any] = {
        "n_rows": len(rows),
        "n_ok": len(ok),
        "n_error": len(errors),
        "by_scope_condition": {},
    }

    scopes = sorted({str(r.get("eval_scope")) for r in ok})
    conds = sorted({str(r.get("condition")) for r in ok})

    for scope in scopes:
        out["by_scope_condition"][scope] = {}
        for cond in conds:
            rs = [r for r in ok if str(r.get("eval_scope")) == scope and str(r.get("condition")) == cond]
            if not rs:
                continue
            mr = [r.get("missing_recovery_rate") for r in rs]
            sr = [r.get("support_recall_hop2") for r in rs]
            strong = [r.get("strong_score") for r in rs]
            base_score = [r.get("base_score") for r in rs]
            cur_mr = [r.get("current_missing_recovery_rate") for r in rs]
            cur_score = [r.get("current_score") for r in rs if r.get("current_score") is not None]

            out["by_scope_condition"][scope][cond] = {
                "n": len(rs),
                "mean_mr": mean(mr),
                "mean_mr_stderr": stderr(mr),
                "mean_support_recall_hop2": mean(sr),
                "strong_em": mean_bool(strong),
                "base_em": mean_bool(base_score),
                "strong_correct": sum(bool(x) for x in strong),
                "base_correct": sum(bool(x) for x in base_score),
                "mean_current_mr": mean(cur_mr),
                "delta_mr_vs_current": None if mean(mr) is None or mean(cur_mr) is None else mean(mr) - mean(cur_mr),
                "current_em": mean_bool(cur_score) if cur_score else None,
                "delta_strong_em_vs_current": None if not cur_score else mean_bool(strong) - mean_bool(cur_score),
            }

    if errors:
        out["first_error"] = errors[0]

    return out


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = []
    lines.append("# Qwen positive-safety eval summary\n")
    lines.append(f"- n_ok: {summary.get('n_ok')}")
    lines.append(f"- n_error: {summary.get('n_error')}")
    lines.append("")
    for scope, conds in summary.get("by_scope_condition", {}).items():
        lines.append(f"## {scope}\n")
        lines.append("| condition | n | MR | ΔMR vs current | strong_EM | base_EM | support_recall |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for cond, m in conds.items():
            def fmt(x):
                return "NA" if x is None else f"{float(x):.4f}"
            lines.append(
                f"| {cond} | {m['n']} | {fmt(m.get('mean_mr'))} | "
                f"{fmt(m.get('delta_mr_vs_current'))} | {fmt(m.get('strong_em'))} | "
                f"{fmt(m.get('base_em'))} | {fmt(m.get('mean_support_recall_hop2'))} |"
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()

    ap.add_argument("--split", type=Path, required=True)
    ap.add_argument("--case-state-index", type=Path, required=True)
    ap.add_argument("--prompts", type=Path, required=True)
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/prompt_update/cache/fixed_prompt_config.json"))
    ap.add_argument("--final-answerer-refs", type=Path, default=Path("experiments/prompt_update/cache/final_answerer_refs.json"))

    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary-out", type=Path, required=True)
    ap.add_argument("--summary-md", type=Path, default=None)

    ap.add_argument("--composition", type=str, default="mixed_custom")
    ap.add_argument("--batch-id", type=int, default=0)
    ap.add_argument("--scopes", nargs="+", default=["batch", "full143"])
    ap.add_argument("--conditions", nargs="+", default=None)

    ap.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    ap.add_argument("--k", type=int, default=7)

    ap.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    ap.add_argument("--base-url", "--api-base", dest="base_url", type=str, default=None)
    ap.add_argument("--api-key", type=str, default=None)
    ap.add_argument("--temperature", type=float, default=0.7)

    ap.add_argument("--query-max-tokens", type=int, default=2048)
    ap.add_argument("--summary-max-tokens", type=int, default=8192)
    ap.add_argument("--answer-max-tokens", type=int, default=4096)

    ap.add_argument("--num-threads", type=int, default=8)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--task-retries", type=int, default=5)

    ap.add_argument("--overwrite", action="store_true")

    return ap.parse_args()


def main() -> None:
    args = parse_args()

    base.set_retriever_dir(str(args.retriever_dir))

    split = read_json(args.split)
    case_index = normalize_case_index(read_json(args.case_state_index))
    prompt_rows = [r for r in read_jsonl(args.prompts) if not r.get("error")]

    if args.conditions:
        keep = set(args.conditions)
        prompt_rows = [r for r in prompt_rows if r.get("condition") in keep]

    fixed_cfg = read_json(args.fixed_prompt_config)
    final_refs = read_json(args.final_answerer_refs)

    refs = {
        "summarize2_prompt": get_summarize2_prompt(fixed_cfg),
        "base_final_answerer_prompt": get_final_prompt(final_refs, "base_final_answerer"),
        "strong_final_answerer_prompt": get_final_prompt(final_refs, "strong_final_answerer"),
    }

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or "EMPTY"
    base_url = args.base_url or os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
    if not base_url:
        raise EnvironmentError("Set --base-url or OPENAI_BASE_URL/OPENAI_API_BASE")

    client = OpenAI(api_key=api_key, base_url=base_url)

    if args.overwrite:
        for p in [args.out, args.summary_out, args.summary_md]:
            if p and Path(p).exists():
                Path(p).unlink()

    existing = read_jsonl(args.out)
    done = {
        (str(r.get("condition")), str(r.get("eval_scope")), int(r.get("case_id")))
        for r in existing
        if not r.get("error") and r.get("case_id") is not None
    }

    tasks = []
    for scope in args.scopes:
        eval_scope, case_ids = eval_scope_case_ids(split, scope, args.composition, args.batch_id)
        for pr in prompt_rows:
            cond = str(pr.get("condition"))
            prompt_text = get_prompt_text(pr, fixed_cfg)
            for cid in case_ids:
                key = (cond, eval_scope, int(cid))
                if key in done:
                    continue
                case = unwrap_source(case_index[int(cid)])
                tasks.append({
                    "client": client,
                    "model": args.model,
                    "temperature": args.temperature,
                    "prompt_row": pr,
                    "prompt_text": prompt_text,
                    "case_id": int(cid),
                    "source": case,
                    "refs": refs,
                    "k": args.k,
                    "query_max_tokens": args.query_max_tokens,
                    "summary_max_tokens": args.summary_max_tokens,
                    "answer_max_tokens": args.answer_max_tokens,
                    "retries": args.retries,
                    "task_retries": args.task_retries,
                    "eval_scope": eval_scope,
                })

    print("[info] prompts:", len(prompt_rows), [r.get("condition") for r in prompt_rows])
    print("[info] existing rows:", len(existing))
    print("[info] pending rows:", len(tasks))
    print("[info] model:", args.model)
    print("[info] base_url:", base_url)

    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(run_task_safe, dict(t)) for t in tasks]
        for fut in tqdm(cf.as_completed(futs), total=len(futs), desc="qwen positive-safety eval"):
            row = fut.result()
            append_jsonl(args.out, row)

    all_rows = read_jsonl(args.out)
    summary = summarize(all_rows)
    summary.update({
        "split": str(args.split),
        "case_state_index": str(args.case_state_index),
        "prompts": str(args.prompts),
        "out": str(args.out),
        "model": args.model,
        "base_url": base_url,
        "composition": args.composition,
        "batch_id": args.batch_id,
        "scopes": args.scopes,
        "conditions": args.conditions,
        "retriever_dir": str(args.retriever_dir),
        "k": args.k,
    })
    write_json(args.summary_out, summary)
    if args.summary_md:
        write_summary_md(args.summary_md, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    if args.summary_md:
        print("[wrote]", args.summary_md)
    print(json.dumps({
        "n_ok": summary.get("n_ok"),
        "n_error": summary.get("n_error"),
        "by_scope_condition": summary.get("by_scope_condition"),
    }, ensure_ascii=False, indent=2)[:5000])


if __name__ == "__main__":
    main()
