#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from openai import OpenAI
from tqdm import tqdm


DEFAULT_NAMES = [
    "optimized_baseline",
    "optimized_baseline_hop2_A_concise_bm25",
    "optimized_baseline_hop2_B_short",
    "optimized_baseline_hop2_C_retrieval_state",
    "optimized_baseline_hop2_D_anchor_preservation",
]

DIAGNOSIS_PROMPT_VERSION = "hotpot_wrong_diagnosis_v2"

DIAGNOSIS_INSTRUCTIONS = """You are diagnosing a failed HotpotQA multi-hop RAG prediction.

Classify the main failure cause using only the provided trace.

Major category:
- retrieval_failure
- summary_failure
- final_answer_failure
- ambiguous_or_gold_issue

Retrieval subtypes:
- retrieval_missing_target: hop2 query does not target the missing support/evidence.
- known_entity_dominance: already-known entity/comparison target dominates retrieval.
- context_stuffing: too much context dilutes the target.
- lexical_anchor_loss: canonical entity/title/domain phrase is dropped or weakened.
- domain_qualifier_missing: target name is ambiguous because domain qualifier is missing.
- category_term_dominance: category/condition term dominates the actual target.
- alias_or_surface_mismatch: target is conceptually right but surface form is poor.
- retriever_limit: query is reasonable but BM25/top-k fails.

Summary subtypes:
- summary1_missing_signal_failure
- summary1_premature_answer
- summary1_distractor_overemphasis
- summary2_evidence_ignored
- summary2_wrong_inference

Final answer subtypes:
- answer_extraction_failure
- canonicalization_failure
- answer_type_mismatch
- insufficient_evidence_refusal

Return JSON only:
{
  "major_category": "...",
  "primary_subtype": "...",
  "secondary_subtypes": ["..."],
  "failure_stage": "...",
  "is_retrieval_support_missing": true,
  "is_gold_evidence_present_after_hop2": false,
  "short_reason": "...",
  "key_bad_query_terms": ["..."],
  "missing_or_weakened_terms": ["..."],
  "suggested_better_query": "..."
}

Rules:
- If support_recall_total < 1, prefer retrieval_failure unless the trace clearly shows otherwise.
- If support_recall_total = 1 but answer is wrong, diagnose summary2 or final_answer.
- Focus on hop2_query, hop2_titles, summary_1, summary_2, pred_answer.
- Do not invent external facts.
- Keep short_reason concise.
"""


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def stable_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_cache_key(model: str, trace: dict[str, Any]) -> str:
    payload = {
        "prompt_version": DIAGNOSIS_PROMPT_VERSION,
        "model": model,
        "instructions": DIAGNOSIS_INSTRUCTIONS,
        "trace": trace,
    }
    return sha256_text(stable_json(payload))


def is_wrong(row: dict[str, Any]) -> bool:
    return float(row.get("score", 0.0)) < 1.0


def compact_trace(row: dict[str, Any], candidate: str, wrong_index: int) -> dict[str, Any]:
    return {
        "candidate": candidate,
        "wrong_index": wrong_index,
        "example_id": row.get("example_id"),
        "qid": row.get("qid") or row.get("_id"),
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "pred_answer": row.get("pred_answer"),
        "score": row.get("score"),
        "gold_support_titles": row.get("gold_support_titles"),
        "hop1_query": row.get("hop1_query"),
        "hop1_titles": row.get("hop1_titles"),
        "summary_1": row.get("summary_1"),
        "hop2_query": row.get("hop2_query"),
        "hop2_titles": row.get("hop2_titles"),
        "summary_2": row.get("summary_2"),
        "support_recall_hop1": row.get("support_recall_hop1"),
        "support_recall_hop2_only": row.get("support_recall_hop2_only"),
        "support_recall_total": row.get("support_recall_total"),
        "new_support_titles_hop2": row.get("new_support_titles_hop2"),
        "missing_titles_after_hop2": row.get("missing_titles_after_hop2"),
    }


def case_key(row: dict[str, Any]) -> str:
    qid = row.get("qid") or row.get("example_id")
    if qid is not None:
        return str(qid)
    return f"{row.get('wrong_index')}::{row.get('question', '')[:120]}"


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))

    obj = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not obj:
        raise ValueError(f"No JSON object found in model output: {text[:500]}")

    return json.loads(obj.group(0))


def normalize_diagnosis(d: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    support_recall = trace.get("support_recall_total")
    try:
        support_recall_float = float(support_recall)
    except Exception:
        support_recall_float = 0.0

    defaults = {
        "major_category": "retrieval_failure" if support_recall_float < 1.0 else "final_answer_failure",
        "primary_subtype": "retriever_limit" if support_recall_float < 1.0 else "answer_extraction_failure",
        "secondary_subtypes": [],
        "failure_stage": "hop2_retrieval" if support_recall_float < 1.0 else "final_answer",
        "is_retrieval_support_missing": support_recall_float < 1.0,
        "is_gold_evidence_present_after_hop2": support_recall_float >= 1.0,
        "short_reason": "",
        "key_bad_query_terms": [],
        "missing_or_weakened_terms": [],
        "suggested_better_query": "",
    }

    out = {**defaults, **(d or {})}

    if not isinstance(out.get("secondary_subtypes"), list):
        out["secondary_subtypes"] = []
    if not isinstance(out.get("key_bad_query_terms"), list):
        out["key_bad_query_terms"] = []
    if not isinstance(out.get("missing_or_weakened_terms"), list):
        out["missing_or_weakened_terms"] = []

    return out


def diagnose_worker(task: dict[str, Any]) -> dict[str, Any]:
    """
    Runs in a separate process.
    Creates its own OpenAI client to avoid pickling client objects.
    """
    model = task["model"]
    trace = task["trace"]
    cache_key = task["cache_key"]
    max_retries = task["max_retries"]
    sleep_s = task["sleep_s"]
    timeout = task["timeout"]

    client = OpenAI(timeout=timeout)

    user_input = stable_json(trace)
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.responses.create(
                model=model,
                instructions=DIAGNOSIS_INSTRUCTIONS,
                input=user_input,
            )

            raw_text = response.output_text
            diagnosis = normalize_diagnosis(extract_json(raw_text), trace)

            usage = None
            try:
                usage = response.usage.model_dump()
            except Exception:
                try:
                    usage = response.usage.to_dict()
                except Exception:
                    usage = None

            return {
                "ok": True,
                "cache_key": cache_key,
                "trace": trace,
                "diagnosis": diagnosis,
                "diagnosis_model": model,
                "prompt_version": DIAGNOSIS_PROMPT_VERSION,
                "raw_response_text": raw_text,
                "usage": usage,
                "error": None,
            }

        except Exception as e:
            last_error = repr(e)
            time.sleep(sleep_s * (attempt + 1))

    support_recall = trace.get("support_recall_total")
    try:
        support_recall_float = float(support_recall)
    except Exception:
        support_recall_float = 0.0

    diagnosis = {
        "major_category": "diagnosis_error",
        "primary_subtype": "diagnosis_error",
        "secondary_subtypes": [],
        "failure_stage": "unknown",
        "is_retrieval_support_missing": support_recall_float < 1.0,
        "is_gold_evidence_present_after_hop2": support_recall_float >= 1.0,
        "short_reason": f"Diagnosis failed after retries: {last_error}",
        "key_bad_query_terms": [],
        "missing_or_weakened_terms": [],
        "suggested_better_query": "",
    }

    return {
        "ok": False,
        "cache_key": cache_key,
        "trace": trace,
        "diagnosis": diagnosis,
        "diagnosis_model": model,
        "prompt_version": DIAGNOSIS_PROMPT_VERSION,
        "raw_response_text": "",
        "usage": None,
        "error": last_error,
    }


def load_cache(cache_path: Path) -> dict[str, dict[str, Any]]:
    cache = {}
    for row in read_jsonl(cache_path):
        key = row.get("cache_key")
        if key:
            cache[key] = row
    return cache


def to_diagnosed_row(result: dict[str, Any]) -> dict[str, Any]:
    trace = result["trace"]
    return {
        **trace,
        "diagnosis": result["diagnosis"],
        "diagnosis_model": result["diagnosis_model"],
        "prompt_version": result["prompt_version"],
        "cache_key": result["cache_key"],
        "api_error": result.get("error"),
        "usage": result.get("usage"),
    }


def to_api_log_row(result: dict[str, Any]) -> dict[str, Any]:
    trace = result["trace"]
    return {
        "cache_key": result["cache_key"],
        "prompt_version": result["prompt_version"],
        "diagnosis_model": result["diagnosis_model"],
        "candidate": trace.get("candidate"),
        "wrong_index": trace.get("wrong_index"),
        "qid": trace.get("qid"),
        "example_id": trace.get("example_id"),
        "question": trace.get("question"),
        "request": {
            "instructions": DIAGNOSIS_INSTRUCTIONS,
            "input": trace,
        },
        "raw_response_text": result.get("raw_response_text", ""),
        "diagnosis": result.get("diagnosis"),
        "usage": result.get("usage"),
        "error": result.get("error"),
        "ok": result.get("ok"),
    }


def summarize_diagnoses(rows: list[dict[str, Any]]) -> dict[str, Any]:
    major = Counter()
    subtype = Counter()
    stage = Counter()
    recall_values = []
    usage_totals = Counter()
    examples_by_subtype = defaultdict(list)

    for row in rows:
        d = row.get("diagnosis", {})
        major[d.get("major_category", "unknown")] += 1
        subtype[d.get("primary_subtype", "unknown")] += 1
        stage[d.get("failure_stage", "unknown")] += 1

        recall = row.get("support_recall_total")
        if recall is not None:
            try:
                recall_values.append(float(recall))
            except Exception:
                pass

        usage = row.get("usage") or {}
        for k, v in usage.items():
            if isinstance(v, (int, float)):
                usage_totals[k] += v

        st = d.get("primary_subtype", "unknown")
        if len(examples_by_subtype[st]) < 3:
            examples_by_subtype[st].append({
                "question": row.get("question"),
                "gold_answer": row.get("gold_answer"),
                "pred_answer": row.get("pred_answer"),
                "hop2_query": row.get("hop2_query"),
                "hop2_titles": row.get("hop2_titles"),
                "support_recall_total": row.get("support_recall_total"),
                "short_reason": d.get("short_reason"),
                "suggested_better_query": d.get("suggested_better_query"),
            })

    return {
        "num_wrong": len(rows),
        "mean_support_recall_total_wrong": (
            sum(recall_values) / len(recall_values) if recall_values else None
        ),
        "major_category_counts": dict(major.most_common()),
        "primary_subtype_counts": dict(subtype.most_common()),
        "failure_stage_counts": dict(stage.most_common()),
        "usage_totals": dict(usage_totals),
        "representative_cases_by_subtype": dict(examples_by_subtype),
    }


def write_markdown_summary(path: Path, candidate: str, summary: dict[str, Any]) -> None:
    lines = []
    lines.append(f"# Wrong-case diagnosis summary: `{candidate}`\n")
    lines.append(f"- wrong cases: `{summary['num_wrong']}`")
    lines.append(f"- mean support recall among wrong cases: `{summary['mean_support_recall_total_wrong']}`\n")

    if summary.get("usage_totals"):
        lines.append("## Usage totals\n")
        lines.append("| field | value |")
        lines.append("| --- | ---: |")
        for k, v in summary["usage_totals"].items():
            lines.append(f"| `{k}` | {v} |")
        lines.append("")

    def add_counts(title: str, counts: dict[str, int]):
        lines.append(f"## {title}\n")
        lines.append("| label | count |")
        lines.append("| --- | ---: |")
        for k, v in counts.items():
            lines.append(f"| `{k}` | {v} |")
        lines.append("")

    add_counts("Major categories", summary["major_category_counts"])
    add_counts("Primary subtypes", summary["primary_subtype_counts"])
    add_counts("Failure stages", summary["failure_stage_counts"])

    lines.append("## Representative cases\n")
    for subtype, cases in summary["representative_cases_by_subtype"].items():
        lines.append(f"### `{subtype}`\n")
        for i, c in enumerate(cases, 1):
            lines.append(f"**Case {i}**")
            lines.append(f"- Question: {c.get('question')}")
            lines.append(f"- Gold: `{c.get('gold_answer')}`")
            lines.append(f"- Pred: `{c.get('pred_answer')}`")
            lines.append(f"- Hop2 query: `{c.get('hop2_query')}`")
            lines.append(f"- Support recall: `{c.get('support_recall_total')}`")
            lines.append(f"- Reason: {c.get('short_reason')}")
            if c.get("suggested_better_query"):
                lines.append(f"- Suggested query: `{c.get('suggested_better_query')}`")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def collect_wrong_rows(run_dir: Path, candidate: str, limit: int | None) -> tuple[Path, list[dict[str, Any]]]:
    analysis_dir = run_dir / f"analysis_{candidate}"
    rollout_path = analysis_dir / "rollout_traces.jsonl"

    if not rollout_path.exists():
        return analysis_dir, []

    rollouts = read_jsonl(rollout_path)

    wrong_rows = []
    for i, row in enumerate(rollouts):
        if is_wrong(row):
            wrong_rows.append(compact_trace(row, candidate, i))

    if limit is not None:
        wrong_rows = wrong_rows[:limit]

    return analysis_dir, wrong_rows


def process_candidate(
    run_dir: Path,
    candidate: str,
    model: str,
    limit: int | None,
    overwrite: bool,
    cache: dict[str, dict[str, Any]],
    cache_path: Path,
    max_workers: int,
    max_retries: int,
    sleep_s: float,
    timeout: float,
) -> None:
    analysis_dir, wrong_rows = collect_wrong_rows(run_dir, candidate, limit)
    if not wrong_rows and not analysis_dir.exists():
        print(f"[SKIP] Missing analysis dir: {analysis_dir}")
        return

    analysis_dir.mkdir(parents=True, exist_ok=True)

    wrong_path = analysis_dir / "wrong_traces.jsonl"
    diag_path = analysis_dir / "wrong_diagnoses.jsonl"
    api_log_path = analysis_dir / "diagnosis_api_calls.jsonl"
    summary_json_path = analysis_dir / "wrong_diagnosis_summary.json"
    summary_md_path = analysis_dir / "wrong_diagnosis_summary.md"

    write_jsonl(wrong_path, wrong_rows)

    if overwrite:
        for p in [diag_path, api_log_path, summary_json_path, summary_md_path]:
            if p.exists():
                p.unlink()

    existing_rows = read_jsonl(diag_path)
    done_case_keys = {case_key(r) for r in existing_rows}

    tasks = []
    cached_results = []

    for trace in wrong_rows:
        ck = make_cache_key(model, trace)
        trace["cache_key"] = ck

        if case_key(trace) in done_case_keys:
            continue

        if ck in cache:
            cached = cache[ck]
            cached_result = {
                "ok": cached.get("ok", True),
                "cache_key": ck,
                "trace": trace,
                "diagnosis": cached["diagnosis"],
                "diagnosis_model": cached.get("diagnosis_model", model),
                "prompt_version": cached.get("prompt_version", DIAGNOSIS_PROMPT_VERSION),
                "raw_response_text": cached.get("raw_response_text", ""),
                "usage": cached.get("usage"),
                "error": cached.get("error"),
            }
            cached_results.append(cached_result)
        else:
            tasks.append({
                "model": model,
                "trace": trace,
                "cache_key": ck,
                "max_retries": max_retries,
                "sleep_s": sleep_s,
                "timeout": timeout,
            })

    print(
        f"[{candidate}] wrong={len(wrong_rows)} "
        f"existing={len(existing_rows)} cached_pending={len(cached_results)} api_pending={len(tasks)}"
    )

    for result in cached_results:
        diagnosed_row = to_diagnosed_row(result)
        append_jsonl(diag_path, diagnosed_row)
        append_jsonl(api_log_path, {**to_api_log_row(result), "from_cache": True})
        done_case_keys.add(case_key(diagnosed_row))

    if tasks:
        with ProcessPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(diagnose_worker, task) for task in tasks]

            with tqdm(
                total=len(futures),
                desc=f"Diagnosing {candidate}",
                unit="case",
                dynamic_ncols=True,
            ) as pbar:
                for fut in as_completed(futures):
                    result = fut.result()

                    cache_row = {
                        "cache_key": result["cache_key"],
                        "prompt_version": result["prompt_version"],
                        "diagnosis_model": result["diagnosis_model"],
                        "diagnosis": result["diagnosis"],
                        "raw_response_text": result.get("raw_response_text", ""),
                        "usage": result.get("usage"),
                        "error": result.get("error"),
                        "ok": result.get("ok"),
                    }
                    append_jsonl(cache_path, cache_row)
                    cache[result["cache_key"]] = cache_row

                    diagnosed_row = to_diagnosed_row(result)
                    append_jsonl(diag_path, diagnosed_row)
                    append_jsonl(api_log_path, {**to_api_log_row(result), "from_cache": False})
                    done_case_keys.add(case_key(diagnosed_row))

                    pbar.update(1)

    all_diags = read_jsonl(diag_path)
    summary = {
        "candidate": candidate,
        "model": model,
        "prompt_version": DIAGNOSIS_PROMPT_VERSION,
        **summarize_diagnoses(all_diags),
    }

    summary_json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown_summary(summary_md_path, candidate, summary)

    print(f"[{candidate}] saved:")
    print(f"  {wrong_path}")
    print(f"  {diag_path}")
    print(f"  {api_log_path}")
    print(f"  {summary_json_path}")
    print(f"  {summary_md_path}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default="/home/jinwoo/gepa-official/outputs/hotpotqa")
    parser.add_argument("--env-file", default="/home/jinwoo/gepa-official/.env")
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--names", nargs="+", default=DEFAULT_NAMES)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--max-workers", type=int, default=8)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--sleep-s", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument(
        "--cache-path",
        default=None,
        help="Global diagnosis cache JSONL. Default: <run-dir>/diagnosis_cache_<model>.jsonl",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    load_dotenv(Path(args.env_file))
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(f"OPENAI_API_KEY not found. Check {args.env_file}")

    run_dir = Path(args.run_dir)
    safe_model = args.model.replace("/", "_").replace(":", "_")
    cache_path = Path(args.cache_path) if args.cache_path else run_dir / f"diagnosis_cache_{safe_model}.jsonl"
    cache = load_cache(cache_path)

    print(f"Model: {args.model}")
    print(f"Run dir: {run_dir}")
    print(f"Cache: {cache_path}")
    print(f"Loaded cache entries: {len(cache)}")
    print(f"Max workers: {args.max_workers}")

    for name in args.names:
        process_candidate(
            run_dir=run_dir,
            candidate=name,
            model=args.model,
            limit=args.limit,
            overwrite=args.overwrite,
            cache=cache,
            cache_path=cache_path,
            max_workers=args.max_workers,
            max_retries=args.max_retries,
            sleep_s=args.sleep_s,
            timeout=args.timeout,
        )


if __name__ == "__main__":
    main()