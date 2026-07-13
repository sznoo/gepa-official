# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/run_rtrace_midpoint_validity.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import string
import sys
import time
from pathlib import Path
from typing import Any

from litellm import completion
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

from examples.hotpotqa.retriever import search, set_retriever_dir  # noqa: E402


DISTANCE_SPEC = """You are working with a tool-oriented semantic distance over retrieval states in a multi-hop QA pipeline.

A retrieval state R contains:
- the second-hop retrieval query,
- retrieved document titles and passages,
- summary_2 generated from those passages,
- final answers produced from summary_1 and summary_2.

The intended distance is not surface text edit distance. It is a task/tool-oriented semantic distance based on:
1. Query intent: what missing bridge/support evidence the query is trying to retrieve.
2. Retrieved evidence: whether the retrieved titles/passages move toward the support facts needed for the question.
3. Answerability: whether the retrieved evidence and summary_2 make the final answer easier to derive.
4. State transition utility: whether the state is an intermediate retrieval/answering state between two endpoint states.

A midpoint R_mid between R_left and R_right should be a minimal, meaningful intermediate state:
- closer to R_left than R_right is to R_left;
- closer to R_right than R_left is to R_right;
- not just a copy of either endpoint;
- preserving useful evidence from the left endpoint while moving toward the missing evidence/retrieval intent of the right endpoint.
"""


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


def truncate(s: Any, n: int) -> str:
    s = str(s or "")
    return s if len(s) <= n else s[:n] + " ...[truncated]"


def extract_titles(docs: list[str]) -> list[str]:
    return [str(d).split(" | ", 1)[0].strip() for d in docs]


def norm_title(t: Any) -> str:
    return " ".join(str(t or "").strip().lower().split())


def normalize_answer(s: Any) -> str:
    s = str(s or "")

    def remove_punc(text: str) -> str:
        return "".join(ch for ch in text if ch not in set(string.punctuation))

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text.lower())

    return " ".join(remove_articles(remove_punc(s)).split())


def exact_match(pred: Any, gold: Any) -> bool:
    if isinstance(gold, list):
        return any(normalize_answer(pred) == normalize_answer(g) for g in gold)
    return normalize_answer(pred) == normalize_answer(gold)


def parse_answer(raw: str) -> str:
    text = str(raw or "").strip()

    m = re.search(r"\[\[\s*##\s*answer\s*##\s*\]\]\s*(.*)", text, flags=re.I | re.S)
    if m:
        ans = m.group(1).strip()
        ans = re.split(r"\n\s*\[\[\s*##", ans, maxsplit=1, flags=re.I)[0].strip()
        return ans.strip().strip('"').strip("'").strip()

    m = re.search(r"(?:^|\n)\s*(?:final answer|answer)\s*:\s*(.+)$", text, flags=re.I | re.S)
    if m:
        return m.group(1).strip().splitlines()[0].strip().strip('"').strip("'").strip()

    return text.splitlines()[0].strip().strip('"').strip("'").strip()


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


def call_model(
    model: str,
    system: str,
    user: str,
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
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp["choices"][0]["message"]["content"] or ""
        except Exception as e:
            last_err = e
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"model call failed after {retries + 1} attempts: {last_err}")


def make_summary2_user(question: str, summary_1: str, docs: list[str]) -> str:
    return f"""question:
{question}

context:
{summary_1}

passages:
{chr(10).join(str(d) for d in docs)}
"""


def make_final_user(question: str, summary_1: str, summary_2: str) -> str:
    return f"""question:
{question}

summary_1:
{summary_1}

summary_2:
{summary_2}
"""


def get_nested(row: dict[str, Any], path: list[str], default: Any = None) -> Any:
    cur: Any = row
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def get_current_docs(row: dict[str, Any]) -> list[str]:
    candidates = [
        get_nested(row, ["oracle_target_row", "current_row", "current_hop2_docs"], None),
        get_nested(row, ["oracle_target_row", "current_row", "hop2_docs"], None),
        get_nested(row, ["current_eval_row", "current_hop2_docs"], None),
        row.get("current_hop2_docs"),
    ]
    for c in candidates:
        if isinstance(c, list):
            return c
    return []


def get_gold_support_titles(row: dict[str, Any]) -> list[str]:
    candidates = [
        row.get("gold_support_titles"),
        get_nested(row, ["oracle_target_row", "gold_support_titles"], None),
        get_nested(row, ["oracle_target_row", "current_row", "gold_support_titles"], None),
        get_nested(row, ["current_eval_row", "gold_support_titles"], None),
    ]
    for c in candidates:
        if isinstance(c, list):
            return c
    return []


def support_metrics(titles: list[str], row: dict[str, Any]) -> dict[str, Any]:
    gold = {norm_title(t) for t in get_gold_support_titles(row)}
    missing_after_hop1 = {norm_title(t) for t in (row.get("missing_after_hop1") or [])}
    got = {norm_title(t) for t in titles}

    hit_gold = gold & got
    recovered_missing = missing_after_hop1 & got

    return {
        "support_recall_hop2": len(hit_gold) / len(gold) if gold else None,
        "missing_recovery_rate": len(recovered_missing) / len(missing_after_hop1) if missing_after_hop1 else None,
        "hit_gold_count": len(hit_gold),
        "recovered_missing_count": len(recovered_missing),
    }


def build_state(
    *,
    state_id: str,
    kind: str,
    query: str,
    titles: list[str],
    docs: list[str],
    summary_2: str,
    base_answer: str | None,
    base_score: bool | None,
    strong_answer: str | None,
    strong_score: bool | None,
    row: dict[str, Any],
) -> dict[str, Any]:
    return {
        "state_id": state_id,
        "kind": kind,
        "query": query,
        "retrieved_titles": titles,
        "retrieved_docs": docs,
        "summary_2": summary_2,
        "base_answer": base_answer,
        "base_score": base_score,
        "strong_answer": strong_answer,
        "strong_score": strong_score,
        **support_metrics(titles, row),
    }


def state_for_prompt(s: dict[str, Any], max_doc_chars: int = 500) -> dict[str, Any]:
    docs = s.get("retrieved_docs") or []
    doc_snips = [truncate(d, max_doc_chars) for d in docs[:7]]

    return {
        "state_id": s.get("state_id"),
        "kind": s.get("kind"),
        "query": s.get("query"),
        "retrieved_titles": s.get("retrieved_titles"),
        "support_recall_hop2": s.get("support_recall_hop2"),
        "missing_recovery_rate": s.get("missing_recovery_rate"),
        "strong_answer": s.get("strong_answer"),
        "strong_score": s.get("strong_score"),
        "base_answer": s.get("base_answer"),
        "base_score": s.get("base_score"),
        "summary_2": truncate(s.get("summary_2"), 1200),
        "retrieved_doc_snippets": doc_snips,
    }


def make_initial_states(row: dict[str, Any]) -> list[dict[str, Any]]:
    cur_docs = get_current_docs(row)
    cur_titles = row.get("current_hop2_titles") or extract_titles(cur_docs)

    target_docs = row.get("oracle_target_retrieved_docs") or []
    target_titles = row.get("oracle_target_retrieved_titles") or extract_titles(target_docs)

    current_summary_2 = get_nested(row, ["current_eval_row", "summary_2"], "") or ""
    target_summary_2 = row.get("oracle_summary_2") or ""

    current = build_state(
        state_id="R0",
        kind="current",
        query=str(row.get("current_query") or ""),
        titles=list(cur_titles),
        docs=list(cur_docs),
        summary_2=str(current_summary_2),
        base_answer=row.get("current_base_answer"),
        base_score=bool(row.get("current_base_score")),
        strong_answer=row.get("current_strong_answer"),
        strong_score=bool(row.get("current_strong_score")),
        row=row,
    )

    target = build_state(
        state_id="R_star",
        kind="oracle_target",
        query=str(row.get("oracle_target_query") or ""),
        titles=list(target_titles),
        docs=list(target_docs),
        summary_2=str(target_summary_2),
        base_answer=row.get("oracle_base_answer"),
        base_score=bool(row.get("oracle_base_score")),
        strong_answer=row.get("oracle_strong_answer"),
        strong_score=bool(row.get("oracle_strong_score")),
        row=row,
    )

    return [current, target]


def select_longest_edge(
    *,
    trace: list[dict[str, Any]],
    row: dict[str, Any],
    model: str,
    temperature: float,
    max_tokens: int,
    retries: int,
) -> dict[str, Any]:
    edges = []
    for i in range(len(trace) - 1):
        edges.append({
            "edge_index": i,
            "left": state_for_prompt(trace[i]),
            "right": state_for_prompt(trace[i + 1]),
        })

    system = DISTANCE_SPEC + """

Select the single adjacent edge with the largest tool-oriented retrieval-state distance.
Return strict JSON only:
{
  "edge_index": <integer>,
  "rationale": "<brief reason>"
}
"""

    user = json.dumps({
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "missing_after_hop1": row.get("missing_after_hop1"),
        "missing_after_hop2": row.get("missing_after_hop2"),
        "edges": edges,
    }, ensure_ascii=False, indent=2)

    raw = call_model(model, system, user, temperature, max_tokens, retries)
    try:
        obj = extract_json_obj(raw)
        edge_index = int(obj.get("edge_index", 0))
    except Exception:
        obj = {"edge_index": 0, "rationale": "JSON parse failed; defaulted to first edge.", "raw": raw}
        edge_index = 0

    edge_index = max(0, min(edge_index, len(trace) - 2))
    obj["edge_index"] = edge_index
    return obj


def generate_midpoint_query(
    *,
    left: dict[str, Any],
    right: dict[str, Any],
    row: dict[str, Any],
    model: str,
    temperature: float,
    max_tokens: int,
    retries: int,
) -> dict[str, Any]:
    system = DISTANCE_SPEC + """

Generate a midpoint retrieval query R_mid between R_left and R_right.

The query should be a minimal transformation from R_left toward R_right. It should preserve useful intent/evidence from R_left while targeting evidence that makes it closer to R_right. Do not simply copy either endpoint query.

Return strict JSON only:
{
  "mid_query": "<second-hop retrieval query>",
  "rationale": "<why this query is between the endpoints under the distance specification>"
}
"""

    user = json.dumps({
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "summary_1": row.get("summary_1"),
        "missing_after_hop1": row.get("missing_after_hop1"),
        "missing_after_hop2": row.get("missing_after_hop2"),
        "R_left": state_for_prompt(left),
        "R_right": state_for_prompt(right),
    }, ensure_ascii=False, indent=2)

    raw = call_model(model, system, user, temperature, max_tokens, retries)
    try:
        obj = extract_json_obj(raw)
        q = str(obj.get("mid_query") or "").strip()
        if not q:
            raise ValueError("empty mid_query")
        return {"mid_query": q, "rationale": obj.get("rationale", ""), "raw": raw}
    except Exception:
        fallback = f"{left.get('query', '')} {right.get('query', '')}".strip()
        return {
            "mid_query": fallback,
            "rationale": "JSON parse failed; fallback concatenated endpoint queries.",
            "raw": raw,
            "parse_failed": True,
        }


def evaluate_query_state(
    *,
    state_id: str,
    kind: str,
    query: str,
    row: dict[str, Any],
    summarize2_prompt: str,
    base_prompt: str,
    strong_prompt: str,
    model: str,
    temperature: float,
    summary_max_tokens: int,
    answer_max_tokens: int,
    retries: int,
    k: int,
) -> dict[str, Any]:
    docs = list(search(query, k=k).passages)
    titles = extract_titles(docs)
    question = str(row.get("question") or "")
    summary_1 = str(row.get("summary_1") or "")
    gold = row.get("gold_answer")

    summary_2 = call_model(
        model,
        summarize2_prompt,
        make_summary2_user(question, summary_1, docs),
        temperature,
        summary_max_tokens,
        retries,
    )

    final_user = make_final_user(question, summary_1, summary_2)

    base_raw = call_model(
        model,
        base_prompt,
        final_user,
        temperature,
        answer_max_tokens,
        retries,
    )
    strong_raw = call_model(
        model,
        strong_prompt,
        final_user,
        temperature,
        answer_max_tokens,
        retries,
    )

    base_answer = parse_answer(base_raw)
    strong_answer = parse_answer(strong_raw)

    return build_state(
        state_id=state_id,
        kind=kind,
        query=query,
        titles=titles,
        docs=docs,
        summary_2=summary_2,
        base_answer=base_answer,
        base_score=exact_match(base_answer, gold),
        strong_answer=strong_answer,
        strong_score=exact_match(strong_answer, gold),
        row=row,
    ) | {
        "base_raw_output": base_raw,
        "strong_raw_output": strong_raw,
    }


def verify_midpoint(
    *,
    left: dict[str, Any],
    right: dict[str, Any],
    mid: dict[str, Any],
    row: dict[str, Any],
    model: str,
    temperature: float,
    max_tokens: int,
    retries: int,
) -> dict[str, Any]:
    system = DISTANCE_SPEC + """

Verify whether R_mid satisfies the intended midpoint inequalities under this same distance specification.

Check:
- left_valid: d(R_left, R_mid) < d(R_left, R_right)
- right_valid: d(R_right, R_mid) < d(R_left, R_right)
- both_valid: left_valid AND right_valid

Use the tool-oriented retrieval-state distance from the specification. Do not use only query string overlap.

Return strict JSON only:
{
  "left_valid": true/false,
  "right_valid": true/false,
  "both_valid": true/false,
  "left_reason": "<brief reason>",
  "right_reason": "<brief reason>",
  "confidence": <number between 0 and 1>
}
"""

    user = json.dumps({
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "missing_after_hop1": row.get("missing_after_hop1"),
        "missing_after_hop2": row.get("missing_after_hop2"),
        "R_left": state_for_prompt(left),
        "R_right": state_for_prompt(right),
        "R_mid": state_for_prompt(mid),
    }, ensure_ascii=False, indent=2)

    raw = call_model(model, system, user, temperature, max_tokens, retries)
    try:
        obj = extract_json_obj(raw)
        left_valid = bool(obj.get("left_valid"))
        right_valid = bool(obj.get("right_valid"))
        obj["left_valid"] = left_valid
        obj["right_valid"] = right_valid
        obj["both_valid"] = bool(left_valid and right_valid)
        obj["raw"] = raw
        return obj
    except Exception:
        return {
            "left_valid": False,
            "right_valid": False,
            "both_valid": False,
            "left_reason": "JSON parse failed.",
            "right_reason": "JSON parse failed.",
            "confidence": 0.0,
            "raw": raw,
            "parse_failed": True,
        }


def run_case(
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
    ) = task

    trace = make_initial_states(row)
    attempts = []

    for it in range(max_iter):
        selected = select_longest_edge(
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

        gen = generate_midpoint_query(
            left=left,
            right=right,
            row=row,
            model=model,
            temperature=temperature,
            max_tokens=generator_max_tokens,
            retries=retries,
        )

        mid_state = evaluate_query_state(
            state_id=f"R_mid_{it}",
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

        judge = verify_midpoint(
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
        }
        attempts.append(attempt)

        # Insert every generated midpoint to keep the trace-generation process moving.
        # Validity is measured separately and never hidden.
        trace.insert(edge_index + 1, mid_state)

    return {
        "case_id": case_id,
        "idx": row.get("idx"),
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "oracle_target_hit": bool(row.get("oracle_target_hit")),
        "trace": trace,
        "attempts": attempts,
        "source_row": row,
    }


def mean_bool(rows: list[dict[str, Any]], key: str) -> float | None:
    if not rows:
        return None
    return sum(bool(r.get(key)) for r in rows) / len(rows)


def build_summary(case_rows: list[dict[str, Any]]) -> dict[str, Any]:
    attempts = [a for c in case_rows for a in c["attempts"]]
    by_iter = {}
    for it in sorted({a["iter"] for a in attempts}):
        ar = [a for a in attempts if a["iter"] == it]
        by_iter[str(it)] = {
            "attempts": len(ar),
            "left_valid_rate": mean_bool(ar, "left_valid"),
            "right_valid_rate": mean_bool(ar, "right_valid"),
            "both_valid_rate": mean_bool(ar, "both_valid"),
            "both_valid_count": sum(bool(a["both_valid"]) for a in ar),
        }

    return {
        "n_cases": len(case_rows),
        "n_attempts": len(attempts),
        "left_valid_rate": mean_bool(attempts, "left_valid"),
        "right_valid_rate": mean_bool(attempts, "right_valid"),
        "both_valid_rate": mean_bool(attempts, "both_valid"),
        "left_valid_count": sum(bool(a["left_valid"]) for a in attempts),
        "right_valid_count": sum(bool(a["right_valid"]) for a in attempts),
        "both_valid_count": sum(bool(a["both_valid"]) for a in attempts),
        "by_iter": by_iter,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("experiments/feedback_distance_v2/results/oracle_query_downstream_eval.repaired.jsonl"))
    ap.add_argument("--final-answerer-refs", type=Path, default=Path("experiments/feedback_distance_v2/cache/final_answerer_refs.json"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/feedback_distance_v2/cache/fixed_prompt_config.json"))
    ap.add_argument("--out-traces", type=Path, default=Path("experiments/feedback_distance_v2/results/rtrace_midpoint_validity_traces.jsonl"))
    ap.add_argument("--out-attempts", type=Path, default=Path("experiments/feedback_distance_v2/results/rtrace_midpoint_validity_attempts.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/feedback_distance_v2/results/rtrace_midpoint_validity_summary.json"))
    ap.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--selector-max-tokens", type=int, default=1024)
    ap.add_argument("--generator-max-tokens", type=int, default=2048)
    ap.add_argument("--judge-max-tokens", type=int, default=2048)
    ap.add_argument("--summary-max-tokens", type=int, default=4096)
    ap.add_argument("--answer-max-tokens", type=int, default=2048)
    ap.add_argument("--num-threads", type=int, default=4)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--max-iter", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--include-oracle-target-miss", action="store_true")
    args = ap.parse_args()

    set_retriever_dir(str(args.retriever_dir))

    rows = read_jsonl(args.input)
    if not args.include_oracle_target_miss:
        rows = [r for r in rows if bool(r.get("oracle_target_hit"))]
    if args.limit is not None:
        rows = rows[: args.limit]

    final_refs = read_json(args.final_answerer_refs)
    fixed_cfg = read_json(args.fixed_prompt_config)

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
        )
        for i, r in enumerate(rows)
    ]

    case_rows = []
    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        for r in tqdm(ex.map(run_case, tasks), total=len(tasks), desc="rtrace midpoint"):
            case_rows.append(r)

    case_rows.sort(key=lambda r: r["case_id"])
    attempts = [a for c in case_rows for a in c["attempts"]]

    write_jsonl(args.out_traces, case_rows)
    write_jsonl(args.out_attempts, attempts)

    summary = {
        "input": str(args.input),
        "out_traces": str(args.out_traces),
        "out_attempts": str(args.out_attempts),
        "subset": "all_65" if args.include_oracle_target_miss else "oracle_target_hit_48",
        "model": args.model,
        "retriever_dir": str(args.retriever_dir),
        "k": args.k,
        "max_iter": args.max_iter,
        "metrics": build_summary(case_rows),
        "distance_spec": DISTANCE_SPEC,
    }
    write_json(args.summary_out, summary)

    print("[wrote]", args.out_traces)
    print("[wrote]", args.out_attempts)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary["metrics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
