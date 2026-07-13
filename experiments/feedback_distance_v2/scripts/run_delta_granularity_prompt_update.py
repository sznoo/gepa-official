# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/run_delta_granularity_prompt_update.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from tqdm import tqdm

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


PROMPT_UPDATER_SYSTEM = """You are converting retrieval/query delta observations into a local update for a second-hop BM25 query-writer prompt.

The target module receives:
- question
- summary_1

and must output one compact second-hop BM25 query.

Your task:
Given the current query-writer prompt and one or more local delta observations, write a locally updated prompt that would make the query writer produce a better second-hop BM25 query for this sample.

Important constraints:
- The output must be a prompt/instruction, not the query itself.
- The prompt should preserve reusable retrieval-facing behavior where possible: preserve core anchors, restore relation/type cues, drop noisy side entities, keep compact BM25 query shape, preserve uncertainty when candidates are unresolved, and prefer answer-bearing entity pages over noisy event/mission/location pages.
- It may use the sample's entities as examples, since this is a sample-level diagnostic, but it should phrase the update as query-writing behavior rather than simply hard-coding one query.
- Prefer behavior-level prompt edits over literal entity memorization. Treat the sample-specific entities as evidence for a reusable retrieval failure pattern, not as content to hard-code.
- The updated prompt should still be meaningful for nearby multi-hop questions with different entities but similar retrieval failures.
- Make the smallest generalizable behavior change needed to improve the observed retrieval transition.
- Do not ask for multiple queries.
- Do not use web-search syntax such as site:, OR-heavy syntax, quoted Boolean programs, or natural-language search instructions.
- The query writer must output only one compact BM25 query string.

Return strict JSON only:
{
  "updated_prompt": "<new prompt for create_query_hop2.predict>",
  "rationale": "<brief explanation of the prompt update>"
}
"""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def extract_json_obj(text: str) -> dict[str, Any]:
    text = str(text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError(f"could not find JSON object in: {text[:500]}")
    return json.loads(m.group(0))


def parse_query(raw: str) -> str:
    """Parse a query-writer response into one compact BM25 query.

    Qwen3 often emits reasoning before the final query:
        <think>
        ...
        </think>
        final query

    The old fallback returned the first line, which became "<think>".
    """
    text = str(raw or "").strip()
    text = re.sub(r"^```(?:json|text)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    if not text:
        return ""

    # 1) Remove complete Qwen thinking blocks.
    text_no_think = re.sub(r"(?is)<think>.*?</think>", "", text).strip()

    # 2) If the model produced an unterminated <think> block, recover from
    # query-like lines near the end of the reasoning instead of returning "<think>".
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
            # Keep plausible keyword-query lines.
            if len(line.split()) >= 3:
                candidates.append(line.strip().strip('"').strip("'"))
        return candidates[-1] if candidates else ""

    text = text_no_think
    text = re.sub(r"(?i)</?think>", "", text).strip()

    if not text:
        return ""

    # 3) JSON object case.
    try:
        obj = extract_json_obj(text)
        for k in ["query", "q", "search_query", "bm25_query", "hop2_query", "answer"]:
            if k in obj and str(obj[k]).strip():
                lines = [
                    l.strip().strip('"').strip("'")
                    for l in str(obj[k]).strip().splitlines()
                    if l.strip()
                ]
                return lines[-1] if lines else ""
    except Exception:
        pass

    # 4) Label case: Query: ...
    m = re.search(
        r"(?:^|\n)\s*(?:final\s+)?(?:bm25\s+|search\s+|second-hop\s+|hop2\s+)?(?:query|answer)\s*[:：]\s*(.+)$",
        text,
        flags=re.I | re.S,
    )
    if m:
        lines = [
            l.strip().strip('"').strip("'")
            for l in m.group(1).strip().splitlines()
            if l.strip()
        ]
        return lines[-1] if lines else ""

    # 5) Plain text case. Prefer the last non-empty line, since Qwen may put the
    # final query after explanatory text.
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

def state_compact(s: dict[str, Any], include_query: bool) -> dict[str, Any]:
    docs = s.get("retrieved_docs") or []
    out = {
        "state_id": s.get("state_id"),
        "kind": s.get("kind"),
        "retrieved_titles": s.get("retrieved_titles"),
        "support_recall_hop2": s.get("support_recall_hop2"),
        "missing_recovery_rate": s.get("missing_recovery_rate"),
        "summary_2": base.truncate(s.get("summary_2"), 900),
        "strong_answer": s.get("strong_answer"),
        "strong_score": s.get("strong_score"),
        "retrieved_doc_snippets": [base.truncate(d, 350) for d in docs[:7]],
    }
    if include_query:
        out["query"] = s.get("query")
    return out


def build_delta_items(states: list[dict[str, Any]], edge_pairs: list[tuple[int, int]], info_mode: str) -> list[dict[str, Any]]:
    include_query = info_mode == "Rq"
    items = []
    for pos, (i, j) in enumerate(edge_pairs):
        items.append({
            "delta_index": pos,
            "left_index": i,
            "right_index": j,
            "left_state": state_compact(states[i], include_query=include_query),
            "right_state": state_compact(states[j], include_query=include_query),
        })
    return items


def make_prompt_update_user(
    *,
    current_prompt: str,
    trace_row: dict[str, Any],
    arm: dict[str, Any],
    delta_items: list[dict[str, Any]],
) -> str:
    source = trace_row["source_row"]
    payload = {
        "arm_id": arm["arm_id"],
        "arm_family": arm["arm_family"],
        "info_mode": arm["info_mode"],
        "question": source.get("question"),
        "summary_1": source.get("summary_1"),
        "missing_after_hop1": source.get("missing_after_hop1"),
        "missing_after_hop2": source.get("missing_after_hop2"),
        "current_query_writer_prompt": current_prompt,
        "delta_observations": delta_items,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def generate_updated_prompt(
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    current_prompt: str,
    trace_row: dict[str, Any],
    arm: dict[str, Any],
) -> dict[str, Any]:
    states = trace_row["trace"]
    delta_items = build_delta_items(states, arm["edge_pairs"], arm["info_mode"])
    user = make_prompt_update_user(
        current_prompt=current_prompt,
        trace_row=trace_row,
        arm=arm,
        delta_items=delta_items,
    )

    raw = base.call_model(
        model,
        PROMPT_UPDATER_SYSTEM,
        user,
        temperature,
        max_tokens,
        retries,
    )

    try:
        obj = extract_json_obj(raw)
        p = str(obj.get("updated_prompt") or "").strip()
        if not p:
            raise ValueError("empty updated_prompt")
        return {
            "updated_prompt": p,
            "rationale": obj.get("rationale", ""),
            "raw": raw,
        }
    except Exception:
        fallback = current_prompt + "\n\nAdditional local guidance: use the provided retrieval delta to preserve core anchors, restore missing relation/type cues, remove noisy side entities, and output one compact BM25 query."
        return {
            "updated_prompt": fallback,
            "rationale": "JSON parse failed; fallback appended generic local guidance.",
            "raw": raw,
            "parse_failed": True,
        }


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

    if not query:
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

        # Last-resort deterministic fallback. This keeps the arm evaluable and makes
        # the failure visible without dropping the row.
        fallback = f"{question} {summary_1}"
        fallback = " ".join(fallback.split())[:300]
        return {
            "query": fallback,
            "raw": retry_raw,
            "empty_first_raw": raw,
            "empty_query_retry_used": True,
            "empty_query_fallback_used": True,
        }

    return {
        "query": query,
        "raw": raw,
    }


def evaluate_query(
    *,
    query: str,
    trace_row: dict[str, Any],
    refs: dict[str, Any],
    model: str,
    temperature: float,
    k: int,
    summary_max_tokens: int,
    answer_max_tokens: int,
    retries: int,
) -> dict[str, Any]:
    source = trace_row["source_row"]
    question = str(source.get("question") or "")
    summary_1 = str(source.get("summary_1") or "")
    gold = source.get("gold_answer")

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

    metrics = base.support_metrics(titles, source)

    return {
        "query": query,
        "retrieved_titles": titles,
        "retrieved_docs": docs,
        "summary_2": summary_2,
        "support_recall_hop2": metrics.get("support_recall_hop2"),
        "missing_recovery_rate": metrics.get("missing_recovery_rate"),
        "hit_gold_count": metrics.get("hit_gold_count"),
        "recovered_missing_count": metrics.get("recovered_missing_count"),
        "base_raw_output": base_raw,
        "base_answer": base_answer,
        "base_score": base.exact_match(base_answer, gold),
        "strong_raw_output": strong_raw,
        "strong_answer": strong_answer,
        "strong_score": base.exact_match(strong_answer, gold),
    }


def build_arms(trace_row: dict[str, Any], include_prefix: bool, max_prefix: int, include_full_r_only: bool) -> list[dict[str, Any]]:
    states = trace_row["trace"]
    n_edges = len(states) - 1
    if n_edges < 1:
        return []

    arms = [
        {
            "arm_id": "endpoint_R_only",
            "arm_family": "endpoint",
            "info_mode": "R_only",
            "edge_pairs": [(0, len(states) - 1)],
        },
        {
            "arm_id": "endpoint_Rq",
            "arm_family": "endpoint",
            "info_mode": "Rq",
            "edge_pairs": [(0, len(states) - 1)],
        },
    ]

    for i in range(n_edges):
        arms.append({
            "arm_id": f"edge_{i}_R_only",
            "arm_family": "single_edge",
            "info_mode": "R_only",
            "edge_index": i,
            "edge_pairs": [(i, i + 1)],
        })
        arms.append({
            "arm_id": f"edge_{i}_Rq",
            "arm_family": "single_edge",
            "info_mode": "Rq",
            "edge_index": i,
            "edge_pairs": [(i, i + 1)],
        })

    if include_prefix:
        for k in range(1, min(max_prefix, n_edges) + 1):
            pairs = [(i, i + 1) for i in range(k)]
            arms.append({
                "arm_id": f"prefix_{k}_Rq",
                "arm_family": "prefix",
                "info_mode": "Rq",
                "prefix_k": k,
                "edge_pairs": pairs,
            })

    full_pairs = [(i, i + 1) for i in range(n_edges)]
    arms.append({
        "arm_id": "full_trace_Rq",
        "arm_family": "full_trace",
        "info_mode": "Rq",
        "edge_pairs": full_pairs,
    })

    if include_full_r_only:
        arms.append({
            "arm_id": "full_trace_R_only",
            "arm_family": "full_trace",
            "info_mode": "R_only",
            "edge_pairs": full_pairs,
        })

    return arms


def run_task(task: tuple[int, dict[str, Any], dict[str, Any], dict[str, Any], str, float, int, int, int, int, int, int]) -> dict[str, Any]:
    (
        case_id,
        trace_row,
        arm,
        refs,
        model,
        temperature,
        updater_max_tokens,
        query_max_tokens,
        summary_max_tokens,
        answer_max_tokens,
        retries,
        k,
    ) = task

    source = trace_row["source_row"]
    current_prompt = refs["current_query_prompt"]

    upd = generate_updated_prompt(
        model=model,
        temperature=temperature,
        max_tokens=updater_max_tokens,
        retries=retries,
        current_prompt=current_prompt,
        trace_row=trace_row,
        arm=arm,
    )

    q = run_query_writer(
        model=model,
        prompt=upd["updated_prompt"],
        question=str(source.get("question") or ""),
        summary_1=str(source.get("summary_1") or ""),
        temperature=temperature,
        max_tokens=query_max_tokens,
        retries=retries,
    )

    ev = evaluate_query(
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

    return {
        "case_id": case_id,
        "idx": trace_row.get("idx"),
        "arm_id": arm["arm_id"],
        "arm_family": arm["arm_family"],
        "info_mode": arm["info_mode"],
        "edge_index": arm.get("edge_index"),
        "prefix_k": arm.get("prefix_k"),
        "edge_pairs": arm["edge_pairs"],

        "question": source.get("question"),
        "gold_answer": source.get("gold_answer"),
        "missing_after_hop1": source.get("missing_after_hop1"),
        "missing_after_hop2": source.get("missing_after_hop2"),

        "updated_prompt": upd["updated_prompt"],
        "prompt_update_rationale": upd.get("rationale"),
        "prompt_update_raw": upd.get("raw"),

        "generated_query": q["query"],
        "query_raw": q["raw"],

        **ev,
    }



def filter_arms(arms: list[dict[str, Any]], arm_set: str) -> list[dict[str, Any]]:
    if arm_set == "all":
        return arms

    if arm_set == "core":
        keep = {"endpoint_R_only", "endpoint_Rq", "full_trace_Rq"}
        return [a for a in arms if a.get("arm_id") in keep]

    if arm_set == "endpoint":
        return [a for a in arms if a.get("arm_family") == "endpoint"]

    if arm_set == "single_rq":
        return [
            a for a in arms
            if a.get("arm_family") == "single_edge" and a.get("info_mode") == "Rq"
        ]

    if arm_set == "single_all":
        return [a for a in arms if a.get("arm_family") == "single_edge"]

    if arm_set == "rq_only":
        return [a for a in arms if a.get("info_mode") == "Rq"]

    raise ValueError(f"unknown arm_set: {arm_set}")


def run_task_safe(task):
    case_id = task[0]
    trace_row = task[1]
    arm = task[2]
    try:
        return run_task(task)
    except Exception as e:
        return {
            "error": True,
            "case_id": case_id,
            "idx": trace_row.get("idx"),
            "arm_id": arm.get("arm_id"),
            "arm_family": arm.get("arm_family"),
            "info_mode": arm.get("info_mode"),
            "edge_index": arm.get("edge_index"),
            "prefix_k": arm.get("prefix_k"),
            "edge_pairs": arm.get("edge_pairs"),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
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


def summarize_rows(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    return {
        "name": name,
        "n": len(rows),
        "mean_mr": mean(rows, "missing_recovery_rate"),
        "mean_support_recall_hop2": mean(rows, "support_recall_hop2"),
        "base_em": mean_bool(rows, "base_score"),
        "strong_em": mean_bool(rows, "strong_score"),
        "strong_correct": sum(bool(r.get("strong_score")) for r in rows),
        "base_correct": sum(bool(r.get("base_score")) for r in rows),
    }


def baseline_rows_from_traces(trace_rows: list[dict[str, Any]], which: str) -> list[dict[str, Any]]:
    out = []
    for i, tr in enumerate(trace_rows):
        source = tr["source_row"]
        s = tr["trace"][0] if which == "current" else tr["trace"][-1]
        out.append({
            "case_id": i,
            "arm_id": which,
            "arm_family": which,
            "info_mode": "existing",
            "generated_query": s.get("query"),
            "retrieved_titles": s.get("retrieved_titles"),
            "missing_recovery_rate": s.get("missing_recovery_rate"),
            "support_recall_hop2": s.get("support_recall_hop2"),
            "base_score": bool(s.get("base_score")),
            "strong_score": bool(s.get("strong_score")),
            "question": source.get("question"),
            "gold_answer": source.get("gold_answer"),
        })
    return out


def pick_best_per_case(rows: list[dict[str, Any]], family: str, info_mode: str, metric: str = "missing_recovery_rate") -> list[dict[str, Any]]:
    selected = []
    case_ids = sorted({r["case_id"] for r in rows if r.get("arm_family") == family and r.get("info_mode") == info_mode})
    for cid in case_ids:
        rs = [r for r in rows if r.get("case_id") == cid and r.get("arm_family") == family and r.get("info_mode") == info_mode]
        if not rs:
            continue
        rs = sorted(
            rs,
            key=lambda r: (
                -float(r.get(metric) if r.get(metric) is not None else -1),
                -int(bool(r.get("strong_score"))),
                str(r.get("arm_id")),
            ),
        )
        selected.append(rs[0])
    return selected


def build_summary(result_rows: list[dict[str, Any]], trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    current_rows = baseline_rows_from_traces(trace_rows, "current")
    target_rows = baseline_rows_from_traces(trace_rows, "target")

    summary: dict[str, Any] = {
        "baselines": {
            "current": summarize_rows(current_rows, "current"),
            "target": summarize_rows(target_rows, "target"),
        },
        "by_arm_id": {},
        "by_family": {},
        "best_single_edge": {},
        "edge_index_breakdown": {},
        "pairwise_vs_current_mr": {},
    }

    for arm_id in sorted({r["arm_id"] for r in result_rows}):
        rs = [r for r in result_rows if r["arm_id"] == arm_id]
        summary["by_arm_id"][arm_id] = summarize_rows(rs, arm_id)

    for fam in sorted({r["arm_family"] for r in result_rows}):
        rs = [r for r in result_rows if r["arm_family"] == fam]
        summary["by_family"][fam] = summarize_rows(rs, fam)

    for info_mode in ["R_only", "Rq"]:
        best = pick_best_per_case(result_rows, "single_edge", info_mode)
        summary["best_single_edge"][info_mode] = summarize_rows(best, f"best_single_edge_{info_mode}")

    for info_mode in ["R_only", "Rq"]:
        mode_rows = [r for r in result_rows if r.get("arm_family") == "single_edge" and r.get("info_mode") == info_mode]
        edge_indices = sorted({r.get("edge_index") for r in mode_rows if r.get("edge_index") is not None})
        summary["edge_index_breakdown"][info_mode] = {
            str(e): summarize_rows([r for r in mode_rows if r.get("edge_index") == e], f"edge_{e}_{info_mode}")
            for e in edge_indices
        }

    current_by_case = {r["case_id"]: r for r in current_rows}
    for name, rs in {
        **{k: [r for r in result_rows if r["arm_id"] == k] for k in sorted({r["arm_id"] for r in result_rows})},
        "best_single_edge_R_only": summary_best_rows(result_rows, "R_only"),
        "best_single_edge_Rq": summary_best_rows(result_rows, "Rq"),
    }.items():
        wins = ties = losses = 0
        diffs = []
        for r in rs:
            c = current_by_case.get(r["case_id"])
            if not c:
                continue
            a = r.get("missing_recovery_rate")
            b = c.get("missing_recovery_rate")
            if a is None or b is None:
                continue
            d = float(a) - float(b)
            diffs.append(d)
            if d > 1e-9:
                wins += 1
            elif d < -1e-9:
                losses += 1
            else:
                ties += 1
        summary["pairwise_vs_current_mr"][name] = {
            "n": len(diffs),
            "mean_delta_mr": sum(diffs) / len(diffs) if diffs else None,
            "win": wins,
            "tie": ties,
            "lose": losses,
        }

    return summary


def summary_best_rows(result_rows: list[dict[str, Any]], info_mode: str) -> list[dict[str, Any]]:
    return pick_best_per_case(result_rows, "single_edge", info_mode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", type=Path, default=Path("experiments/feedback_distance_v2/results/rtrace_midpoint_validity_v2_traces_hit48.jsonl"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_config.json"))
    ap.add_argument("--final-answerer-refs", type=Path, default=Path("experiments/feedback_distance_v2/cache/final_answerer_refs.json"))
    ap.add_argument("--out", type=Path, default=Path("experiments/feedback_distance_v2/results/delta_granularity_prompt_update_eval.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/feedback_distance_v2/results/delta_granularity_prompt_update_summary.json"))
    ap.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--updater-max-tokens", type=int, default=4096)
    ap.add_argument("--query-max-tokens", type=int, default=512)
    ap.add_argument("--summary-max-tokens", type=int, default=4096)
    ap.add_argument("--answer-max-tokens", type=int, default=2048)
    ap.add_argument("--num-threads", type=int, default=12)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--include-prefix", action="store_true")
    ap.add_argument("--max-prefix", type=int, default=4)
    ap.add_argument("--include-full-r-only", action="store_true")
    ap.add_argument("--arm-set", type=str, default="all", choices=["all", "core", "endpoint", "single_rq", "single_all", "rq_only"])
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    base.set_retriever_dir(str(args.retriever_dir))

    trace_rows = read_jsonl(args.traces)
    if args.limit is not None:
        trace_rows = trace_rows[: args.limit]

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
    existing_rows = []
    if args.out.exists():
        existing_rows = read_jsonl(args.out)
        # Only successful rows are considered done.
        # Error rows remain retryable when the script is resumed without --overwrite.
        for r in existing_rows:
            if r.get("error"):
                continue
            done.add((int(r["case_id"]), str(r["arm_id"])))

    tasks = []
    for case_id, tr in enumerate(trace_rows):
        arms = build_arms(
            tr,
            include_prefix=args.include_prefix,
            max_prefix=args.max_prefix,
            include_full_r_only=args.include_full_r_only,
        )
        arms = filter_arms(arms, args.arm_set)
        for arm in arms:
            key = (case_id, arm["arm_id"])
            if key in done:
                continue
            tasks.append((
                case_id,
                tr,
                arm,
                refs,
                args.model,
                args.temperature,
                args.updater_max_tokens,
                args.query_max_tokens,
                args.summary_max_tokens,
                args.answer_max_tokens,
                args.retries,
                args.k,
            ))

    print(f"[info] trace cases: {len(trace_rows)}")
    print(f"[info] pending eval arms: {len(tasks)}")
    print(f"[info] existing rows: {len(existing_rows)}")

    result_rows = list(existing_rows)

    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(run_task_safe, t) for t in tasks]
        for fut in tqdm(cf.as_completed(futs), total=len(futs), desc="delta granularity"):
            row = fut.result()
            append_jsonl(args.out, row)
            result_rows.append(row)

    all_result_rows = read_jsonl(args.out)
    error_rows = [r for r in all_result_rows if r.get("error")]
    result_rows = [r for r in all_result_rows if not r.get("error")]

    if error_rows:
        print(f"[warn] error rows: {len(error_rows)}")
        print(json.dumps(error_rows[0], ensure_ascii=False, indent=2)[:3000])

    summary = build_summary(result_rows, trace_rows)
    summary.update({
        "arm_set": args.arm_set,
        "n_error_rows": len(error_rows),
        "traces": str(args.traces),
        "out": str(args.out),
        "n_trace_cases": len(trace_rows),
        "n_eval_rows": len(result_rows),
        "model": args.model,
        "retriever_dir": str(args.retriever_dir),
        "k": args.k,
        "include_prefix": args.include_prefix,
        "include_full_r_only": args.include_full_r_only,
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
