import argparse
import json
import os
import re
import sys
import time
import threading
from pathlib import Path
from statistics import mean
from concurrent.futures import ThreadPoolExecutor, as_completed

import dspy

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


try:
    from tqdm.auto import tqdm
except Exception:
    def tqdm(x, **kwargs):
        return x


_tls = threading.local()


def read_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def norm_relaxed(x):
    x = str(x).lower().strip()
    x = re.sub(r"\b(about|approximately|around|roughly|nearly)\b", " ", x)
    x = re.sub(r"\b(a|an|the)\b", " ", x)
    x = re.sub(r"[^a-z0-9]+", " ", x)
    x = " ".join(x.split())

    # Numeric comma/space equivalence: "150 000" -> "150000".
    toks = x.split()
    if toks and all(t.isdigit() for t in toks):
        x = "".join(toks)

    return x


def relaxed_match(pred, gold):
    return norm_relaxed(pred) == norm_relaxed(gold)


def make_lm(args):
    kwargs = {
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_key:
        kwargs["api_key"] = args.api_key
    if args.api_base:
        kwargs["api_base"] = args.api_base
    return dspy.LM(args.model, **kwargs)


def get_lm(args):
    if not hasattr(_tls, "lm"):
        _tls.lm = make_lm(args)
    return _tls.lm


def clean_lm_text(x):
    if isinstance(x, list):
        x = x[0] if x else ""
    x = str(x).strip()
    x = x.strip("` \n")
    if x.lower().startswith("json"):
        x = x[4:].strip()
    return x.strip()


def extract_json_obj(text):
    text = clean_lm_text(text)

    try:
        return json.loads(text)
    except Exception:
        pass

    # Strip fenced code block if present.
    text2 = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.I).strip()
    text2 = re.sub(r"```$", "", text2.strip()).strip()
    try:
        return json.loads(text2)
    except Exception:
        pass

    # Last-resort: first {...} span.
    start = text2.find("{")
    end = text2.rfind("}")
    if start >= 0 and end > start:
        frag = text2[start:end + 1]
        try:
            return json.loads(frag)
        except Exception:
            pass

    return None


def lm_json_call(args, prompt, retries=3, sleep_s=2.0):
    lm = get_lm(args)
    last_error = None

    for i in range(retries):
        try:
            out = lm(prompt)
            text = clean_lm_text(out)
            obj = extract_json_obj(text)
            if isinstance(obj, dict):
                return obj, text, None
            last_error = f"Could not parse JSON from: {text[:500]}"
        except Exception as e:
            last_error = str(e)

        if i + 1 < retries:
            time.sleep(sleep_s * (i + 1))

    return {}, "", last_error


def truncate(s, max_chars):
    s = str(s)
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + "\n...[truncated]"


def format_docs(docs, max_chars=12000):
    chunks = []
    total = 0
    for i, d in enumerate(docs or [], 1):
        text = f"[doc {i}] {d}"
        if total + len(text) > max_chars:
            remaining = max(0, max_chars - total)
            if remaining > 200:
                chunks.append(text[:remaining] + "\n...[truncated]")
            break
        chunks.append(text)
        total += len(text)
    return "\n\n".join(chunks)


def make_answer_judge_prompt(row):
    return f"""\
You are judging answer equivalence for HotpotQA.

Decide whether the predicted answer should be counted as correct for the question, given the gold answer.

Use semantic equivalence, not strict string matching.
Accept:
- punctuation/case differences
- comma formatting in numbers, e.g. 150,000 vs 150000
- harmless leading words such as "about" when the quantity is otherwise the same
- common aliases/nicknames if they unambiguously refer to the same entity

Reject:
- broader/narrower geographic answers, e.g. United Kingdom vs Northern Ireland
- related but different occupations/entities
- partial answers that miss the requested specificity
- "insufficient information"

Return only JSON with this schema:
{{
  "equivalent": true or false,
  "score": 1.0 or 0.0,
  "category": "exact_or_format" | "alias" | "too_broad" | "too_narrow" | "related_but_wrong" | "wrong" | "insufficient_information",
  "reason": "short reason"
}}

Question:
{row.get("question")}

Gold answer:
{row.get("gold_answer")}

Predicted answer:
{row.get("pred_answer")}
""".strip()


def make_summary_judge_prompt(row, trace):
    summary_1 = trace.get("summary_1", "")
    summary_2 = row.get("summary_2", "")

    return f"""\
You are judging whether the summaries contain enough evidence to answer a HotpotQA question with the gold answer.

Use ONLY summary_1 and summary_2. Do not use outside knowledge.
The gold answer is provided only for judging whether the summaries support it.

Return only JSON with this schema:
{{
  "sufficient": true or false,
  "score": 1.0 or 0.5 or 0.0,
  "supporting_quotes": ["short quote from summary_1 or summary_2"],
  "failure_type": "sufficient" | "partial_bridge_missing" | "answer_string_present_but_relation_missing" | "wrong_granularity" | "not_supported",
  "reason": "short reason"
}}

Scoring:
- 1.0: summaries contain enough explicit information to derive the gold answer.
- 0.5: summaries contain partial evidence or the answer string, but the needed relation/bridge is ambiguous or incomplete.
- 0.0: summaries do not support the gold answer.
- If there is no supporting quote from the summaries, score must be 0.0.

Question:
{row.get("question")}

Gold answer:
{row.get("gold_answer")}

summary_1:
{truncate(summary_1, 5000)}

summary_2:
{truncate(summary_2, 7000)}
""".strip()


def make_evidence_judge_prompt(row, trace, max_doc_chars):
    hop1_docs = trace.get("hop1_docs", []) or []
    hop2_docs = row.get("hop2_docs", []) or []
    docs_text = format_docs(hop1_docs + hop2_docs, max_chars=max_doc_chars)

    return f"""\
You are judging whether the retrieved passages contain enough evidence to answer a HotpotQA question with the gold answer.

Use ONLY the retrieved passages below. Do not use outside knowledge.
The gold answer is provided only for judging whether the retrieved context supports it.

Return only JSON with this schema:
{{
  "sufficient": true or false,
  "score": 1.0 or 0.5 or 0.0,
  "supporting_quotes": ["short quote from retrieved passages"],
  "failure_type": "sufficient" | "partial_bridge_missing" | "answer_string_present_but_relation_missing" | "wrong_granularity" | "not_supported",
  "reason": "short reason"
}}

Scoring:
- 1.0: retrieved passages contain enough explicit evidence to derive the gold answer.
- 0.5: retrieved passages contain partial evidence or the answer string, but the needed relation/bridge is ambiguous or incomplete.
- 0.0: retrieved passages do not support the gold answer.
- If there is no supporting quote from the retrieved passages, score must be 0.0.

Question:
{row.get("question")}

Gold answer:
{row.get("gold_answer")}

Retrieved passages:
{docs_text}
""".strip()


def trace_key_from_row(row):
    # Question is safest here because eval_index was not unique in the sanity printout.
    return str(row.get("question", ""))


def trace_key_from_trace(trace):
    return str(trace.get("question", ""))


def judge_one(args, scopes, trace_by_question, row):
    out = dict(row)
    trace = trace_by_question.get(trace_key_from_row(row), {})

    pred = out.get("pred_answer", "")
    gold = out.get("gold_answer", "")
    summary_2 = out.get("summary_2", "")

    out["strict_em_existing"] = safe_float(out.get("score", 0.0))
    out["relaxed_em"] = float(relaxed_match(pred, gold))
    out["summary2_contains_gold_string"] = float(str(gold).lower() in str(summary_2).lower())

    if "answer" in scopes:
        prompt = make_answer_judge_prompt(out)
        obj, raw, err = lm_json_call(args, prompt, retries=args.retries)
        out["llm_answer_judge_raw"] = raw
        out["llm_answer_judge_error"] = err
        out["llm_answer_equivalent"] = float(bool(obj.get("equivalent", False)))
        out["llm_answer_score"] = safe_float(obj.get("score", out["llm_answer_equivalent"]))
        out["llm_answer_category"] = obj.get("category", "")
        out["llm_answer_reason"] = obj.get("reason", "")

    if "summary" in scopes:
        prompt = make_summary_judge_prompt(out, trace)
        obj, raw, err = lm_json_call(args, prompt, retries=args.retries)
        out["llm_summary_judge_raw"] = raw
        out["llm_summary_judge_error"] = err
        out["llm_summary_sufficient"] = float(bool(obj.get("sufficient", False)))
        out["llm_summary_score"] = safe_float(obj.get("score", out["llm_summary_sufficient"]))
        out["llm_summary_partial_or_sufficient"] = float(out["llm_summary_score"] >= 0.5)
        out["llm_summary_failure_type"] = obj.get("failure_type", "")
        out["llm_summary_reason"] = obj.get("reason", "")
        out["llm_summary_supporting_quotes"] = obj.get("supporting_quotes", [])

    if "evidence" in scopes:
        prompt = make_evidence_judge_prompt(out, trace, args.max_doc_chars)
        obj, raw, err = lm_json_call(args, prompt, retries=args.retries)
        out["llm_evidence_judge_raw"] = raw
        out["llm_evidence_judge_error"] = err
        out["llm_evidence_sufficient"] = float(bool(obj.get("sufficient", False)))
        out["llm_evidence_score"] = safe_float(obj.get("score", out["llm_evidence_sufficient"]))
        out["llm_evidence_partial_or_sufficient"] = float(out["llm_evidence_score"] >= 0.5)
        out["llm_evidence_failure_type"] = obj.get("failure_type", "")
        out["llm_evidence_reason"] = obj.get("reason", "")
        out["llm_evidence_supporting_quotes"] = obj.get("supporting_quotes", [])

    return out


def add_corrected_vs_baseline(rows):
    # Baseline by question.
    baseline_by_q = {}
    for r in rows:
        if r.get("arm") == "baseline_cached":
            baseline_by_q[trace_key_from_row(r)] = r

    for r in rows:
        b = baseline_by_q.get(trace_key_from_row(r), {})
        r["relaxed_corrected_vs_baseline"] = float(
            safe_float(b.get("relaxed_em", 0.0)) < 1.0 and safe_float(r.get("relaxed_em", 0.0)) >= 1.0
        )
        r["llm_answer_corrected_vs_baseline"] = float(
            safe_float(b.get("llm_answer_score", 0.0)) < 1.0 and safe_float(r.get("llm_answer_score", 0.0)) >= 1.0
        )
        r["summary_sufficient_but_strict_wrong"] = float(
            safe_float(r.get("llm_summary_score", 0.0)) >= 1.0 and safe_float(r.get("strict_em_existing", 0.0)) < 1.0
        )
        r["evidence_sufficient_but_strict_wrong"] = float(
            safe_float(r.get("llm_evidence_score", 0.0)) >= 1.0 and safe_float(r.get("strict_em_existing", 0.0)) < 1.0
        )
    return rows


def write_summary(path, rows, scopes):
    groups = {}
    for r in rows:
        groups.setdefault(r.get("arm", "UNKNOWN"), []).append(r)

    cols = [
        ("strict_em_existing", "strict EM"),
        ("relaxed_em", "relaxed EM"),
    ]

    if "answer" in scopes:
        cols += [
            ("llm_answer_score", "LLM ans"),
            ("llm_answer_corrected_vs_baseline", "LLM corrected"),
        ]

    cols += [
        ("summary2_contains_gold_string", "sum2 gold str"),
    ]

    if "summary" in scopes:
        cols += [
            ("llm_summary_score", "summary suff"),
            ("llm_summary_partial_or_sufficient", "summary partial+"),
            ("summary_sufficient_but_strict_wrong", "summary suff but EM0"),
        ]

    if "evidence" in scopes:
        cols += [
            ("llm_evidence_score", "evidence suff"),
            ("llm_evidence_partial_or_sufficient", "evidence partial+"),
            ("evidence_sufficient_but_strict_wrong", "evidence suff but EM0"),
        ]

    # Existing retrieval diagnostic fields from upper-bound run.
    cols += [
        ("support_recall_total", "total recall"),
        ("missing_recovery_rate", "MR"),
        ("retrieval_improved_vs_baseline", "ret improved"),
    ]

    lines = []
    lines.append("# LLM judge summary\n")
    lines.append(f"Judged rows: {len(rows)}")
    lines.append(f"Scopes: {', '.join(scopes)}\n")

    header = ["arm", "n"] + [label for _, label in cols]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] + ["---:"] * (len(header) - 1)) + "|")

    for arm, rs in sorted(groups.items()):
        vals = []
        for key, _ in cols:
            vals.append(mean(safe_float(r.get(key, 0.0)) for r in rs))
        line = f"| {arm} | {len(rs)} | " + " | ".join(f"{v:.3f}" for v in vals) + " |"
        lines.append(line)

    # Failure-type breakdown.
    if "summary" in scopes:
        lines.append("\n## Summary judge failure types\n")
        lines.append("| arm | failure_type | n |")
        lines.append("|---|---|---:|")
        for arm, rs in sorted(groups.items()):
            counts = {}
            for r in rs:
                ft = r.get("llm_summary_failure_type", "")
                counts[ft] = counts.get(ft, 0) + 1
            for ft, c in sorted(counts.items()):
                lines.append(f"| {arm} | {ft or '(empty)'} | {c} |")

    if "answer" in scopes:
        lines.append("\n## Answer judge categories\n")
        lines.append("| arm | category | n |")
        lines.append("|---|---|---:|")
        for arm, rs in sorted(groups.items()):
            counts = {}
            for r in rs:
                cat = r.get("llm_answer_category", "")
                counts[cat] = counts.get(cat, 0) + 1
            for cat, c in sorted(counts.items()):
                lines.append(f"| {arm} | {cat or '(empty)'} | {c} |")

    path.write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows-path", required=True)
    ap.add_argument("--trace-path", default=(
        "outputs/hotpotqa_representation_prompt_screening/"
        "rep_prompt_screening_24_dev300_final_v2/conditions/"
        "final_manual_only/analysis/rollout_traces.jsonl"
    ))
    ap.add_argument("--out-dir", required=True)

    ap.add_argument("--judge-scopes", default="answer,summary,evidence",
                    help="comma-separated subset of: answer,summary,evidence")
    ap.add_argument("--num-threads", type=int, default=4)

    ap.add_argument("--model", default=os.environ.get("TASK_MODEL", "openai/gpt-5-mini"))
    ap.add_argument("--api-base", default=os.environ.get("TASK_API_BASE", ""))
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--max-doc-chars", type=int, default=12000)

    args = ap.parse_args()

    if "gpt-5" in args.model:
        if args.temperature not in (1.0, None):
            print(f"[warn] GPT-5 model requires temperature=1.0 or None; overriding {args.temperature} -> 1.0")
            args.temperature = 1.0
        if args.max_tokens is not None and args.max_tokens < 16000:
            print(f"[warn] GPT-5 model requires max_tokens>=16000 or None; overriding {args.max_tokens} -> 16000")
            args.max_tokens = 16000

    scopes = [s.strip() for s in args.judge_scopes.split(",") if s.strip()]
    valid = {"answer", "summary", "evidence"}
    bad = [s for s in scopes if s not in valid]
    if bad:
        raise ValueError(f"Bad judge scopes: {bad}. Valid: {sorted(valid)}")

    rows = read_jsonl(args.rows_path)
    traces = read_jsonl(args.trace_path)
    trace_by_question = {trace_key_from_trace(t): t for t in traces}

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[info] rows: {len(rows)}")
    print(f"[info] traces: {len(traces)}")
    print(f"[info] scopes: {scopes}")
    print(f"[info] num_threads: {args.num_threads}")
    print(f"[info] out_dir: {out_dir}")

    judged = []

    if args.num_threads <= 1:
        for r in tqdm(rows, desc="judging rows", unit="row", dynamic_ncols=True):
            judged.append(judge_one(args, scopes, trace_by_question, r))
    else:
        with ThreadPoolExecutor(max_workers=args.num_threads) as pool:
            futs = [
                pool.submit(judge_one, args, scopes, trace_by_question, r)
                for r in rows
            ]
            for fut in tqdm(as_completed(futs), total=len(futs), desc="judging rows", unit="row", dynamic_ncols=True):
                judged.append(fut.result())

    judged = add_corrected_vs_baseline(judged)
    judged.sort(key=lambda r: (str(r.get("question", "")), str(r.get("arm", ""))))

    write_jsonl(out_dir / "judged_rows.jsonl", judged)
    write_summary(out_dir / "summary.md", judged, scopes)

    config = vars(args)
    config["judge_scopes"] = scopes
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False))

    print()
    print("[wrote]", out_dir / "judged_rows.jsonl")
    print("[wrote]", out_dir / "summary.md")
    print()
    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
