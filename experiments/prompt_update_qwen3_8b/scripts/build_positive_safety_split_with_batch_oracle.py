#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import math
import os
import random
import re
import shutil
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

CONDITIONS = [
    "base",
    "delta_p_neg_only",
    "delta_p_custom_preserve",
    "delta_p_custom_signed",
    "endpoint_delta_neg_only",
    "endpoint_delta_custom_preserve",
    "endpoint_delta_custom_signed",
]

BATCH_BUCKET_COUNTS = {
    "W_retrieval": 5,
    "C_clean": 3,
    "C_fragile": 1,
    "W_other": 1,
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def as_list(x: Any) -> list[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return list(x)


def strip_qwen_thinking(text: str) -> str:
    text = str(text or "").strip()
    text = re.sub(r"^```(?:json|text)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    text = re.sub(r"(?is)^\s*<think>.*?</think>\s*", "", text).strip()
    text = re.sub(r"(?is)<think>.*?</think>\s*", "", text).strip()
    if text.lower().startswith("<think>"):
        return ""
    text = re.sub(r"(?i)</?think>", "", text).strip()
    return text


def extract_queries(raw: str) -> list[str]:
    clean = strip_qwen_thinking(raw)
    queries: list[str] = []

    if clean:
        try:
            obj = json.loads(clean)
            if isinstance(obj, dict):
                qv = obj.get("queries") or obj.get("query_candidates") or obj.get("query")
                if isinstance(qv, list):
                    queries.extend(str(q).strip() for q in qv if str(q).strip())
                elif isinstance(qv, str) and qv.strip():
                    queries.append(qv.strip())
            elif isinstance(obj, list):
                queries.extend(str(q).strip() for q in obj if str(q).strip())
        except Exception:
            pass

        if not queries:
            m = re.search(r"\{.*\}", clean, flags=re.S)
            if m:
                try:
                    obj = json.loads(m.group(0))
                    qv = obj.get("queries") or obj.get("query_candidates") or obj.get("query")
                    if isinstance(qv, list):
                        queries.extend(str(q).strip() for q in qv if str(q).strip())
                    elif isinstance(qv, str) and qv.strip():
                        queries.append(qv.strip())
                except Exception:
                    pass

        if not queries:
            for line in clean.splitlines():
                line = line.strip()
                line = re.sub(r"^\s*[-*]\s+", "", line)
                line = re.sub(r"^\s*\d+[.)]\s+", "", line)
                line = re.sub(r"^(query|candidate|bm25 query)\s*[:：]\s*", "", line, flags=re.I).strip()
                line = line.strip('"').strip("'").strip()
                if len(line.split()) >= 2:
                    queries.append(line)

    # Deduplicate while preserving order.
    out = []
    seen = set()
    for q in queries:
        q = re.sub(r"\s+", " ", q).strip()
        if not q or q in seen:
            continue
        if len(q) > 300:
            q = q[:300].strip()
        seen.add(q)
        out.append(q)
    return out


def chat_query_candidates(
    *,
    client: OpenAI,
    model: str,
    base_url: str,
    question: str,
    gold_answer: str,
    gold_support_titles: list[str],
    missing_after_hop1: list[str],
    current_query: str,
    current_titles: list[str],
    summary_1: str,
    summary_2: str,
    max_tokens: int,
    temperature: float,
    retries: int,
) -> dict[str, Any]:
    system = """You generate oracle-style second-hop BM25 queries for HotpotQA.

Goal:
- Produce compact lexical BM25 query candidates that can retrieve the missing gold support page(s).
- Use the given gold support titles as privileged oracle hints.
- Keep each query short. Do not explain.
- Return JSON only: {"queries": ["...", "...", "..."]}.
"""

    user = f"""Question:
{question}

Gold answer:
{gold_answer}

Gold support titles:
{json.dumps(gold_support_titles, ensure_ascii=False)}

Missing after hop1:
{json.dumps(missing_after_hop1, ensure_ascii=False)}

Current hop2 query:
{current_query}

Current hop2 retrieved titles:
{json.dumps(current_titles, ensure_ascii=False)}

Summary 1:
{summary_1}

Summary 2:
{summary_2}

Generate 4 compact BM25 query candidates for retrieving the missing gold support page(s).
Return JSON only.
"""

    last_err = None
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
            qs = extract_queries(raw)
            return {
                "raw": raw,
                "queries": qs,
                "attempt": attempt + 1,
                "base_url": base_url,
            }
        except Exception as e:
            last_err = e
            time.sleep(min(2 * (attempt + 1), 8))
    raise last_err


def support_metrics(titles: list[str], gold_support_titles: list[str], missing_after_hop1: list[str]) -> dict[str, Any]:
    title_set = set(titles)
    gold = list(gold_support_titles or [])
    missing = list(missing_after_hop1 or [])

    hit_gold = [t for t in gold if t in title_set]
    hit_missing = [t for t in missing if t in title_set]

    return {
        "support_recall_total": len(hit_gold) / len(gold) if gold else None,
        "missing_recovery_rate": len(hit_missing) / len(missing) if missing else 1.0,
        "hit_gold_titles": hit_gold,
        "hit_missing_titles": hit_missing,
        "hit_gold_count": len(hit_gold),
        "hit_missing_count": len(hit_missing),
    }


def search_eval_query(query: str, *, k: int, gold_support_titles: list[str], missing_after_hop1: list[str]) -> dict[str, Any]:
    docs = list(base.search(query, k=k).passages)
    titles = base.extract_titles(docs)
    m = support_metrics(titles, gold_support_titles, missing_after_hop1)
    return {
        "query": query,
        "retrieved_docs": docs,
        "retrieved_titles": titles,
        **m,
    }


def deterministic_oracle_queries(r: dict[str, Any]) -> list[str]:
    q = str(r.get("question") or "")
    gold_answer = str(r.get("gold_answer") or "")
    gold_support_titles = [str(x) for x in as_list(r.get("gold_support_titles"))]
    missing_after_hop1 = [str(x) for x in as_list(r.get("missing_after_hop1"))]
    summary_1 = str(r.get("summary_1") or "")

    cands = []

    if missing_after_hop1:
        cands.append(" ".join(missing_after_hop1))
        cands.append(" ".join(missing_after_hop1 + [gold_answer]))

    if gold_support_titles:
        cands.append(" ".join(gold_support_titles))
        cands.append(" ".join(gold_support_titles + [gold_answer]))

    # Compact question/title hybrid.
    important = []
    important.extend(missing_after_hop1[:2])
    important.extend(gold_support_titles[:2])
    if gold_answer:
        important.append(gold_answer)
    if important:
        cands.append(" ".join(important))

    # Last resort: question plus answer.
    if q and gold_answer:
        cands.append(f"{q} {gold_answer}")

    # summary lexical fallback
    if summary_1:
        toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9'._-]+", summary_1)
        if toks:
            cands.append(" ".join(toks[:25]))

    out = []
    seen = set()
    for x in cands:
        x = re.sub(r"\s+", " ", str(x or "")).strip()
        if x and x not in seen:
            seen.add(x)
            out.append(x[:300])
    return out


def choose_best_oracle(candidates: list[str], *, k: int, gold_support_titles: list[str], missing_after_hop1: list[str]) -> dict[str, Any]:
    scored = []
    for q in candidates:
        try:
            row = search_eval_query(q, k=k, gold_support_titles=gold_support_titles, missing_after_hop1=missing_after_hop1)
            scored.append(row)
        except Exception as e:
            scored.append({"query": q, "error": True, "error_message": str(e)})

    valid = [r for r in scored if not r.get("error")]
    if not valid:
        return {
            "error": True,
            "error_message": "all candidate searches failed",
            "candidate_results": scored,
        }

    def key(r: dict[str, Any]):
        return (
            float(r.get("missing_recovery_rate") or 0.0),
            float(r.get("support_recall_total") or 0.0),
            int(r.get("hit_missing_count") or 0),
            int(r.get("hit_gold_count") or 0),
            -len(str(r.get("query") or "")),
        )

    best = max(valid, key=key)
    return {
        **best,
        "candidate_results": scored,
    }


def current_bucket(r: dict[str, Any]) -> str:
    score = float(r.get("score") or 0.0)
    missing_after_hop2 = as_list(r.get("missing_after_hop2"))
    is_correct = score >= 0.5
    retrieval_fail = bool(missing_after_hop2)

    if (not is_correct) and retrieval_fail:
        return "W_retrieval"
    if is_correct and (not retrieval_fail):
        return "C_clean"
    if is_correct and retrieval_fail:
        return "C_fragile"
    return "W_other"


def current_mr(r: dict[str, Any]) -> float:
    v = r.get("current_missing_recovery_rate")
    if v is not None:
        return float(v)
    return support_metrics(
        as_list(r.get("current_hop2_titles")),
        as_list(r.get("gold_support_titles")),
        as_list(r.get("missing_after_hop1")),
    )["missing_recovery_rate"]


def build_cases_from_rollout(rollout: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    cases = {}
    for cid, r in enumerate(rollout):
        case = {
            "case_id": cid,
            "idx": r.get("idx", r.get("example_id", cid)),
            "example_id": r.get("example_id", r.get("idx", cid)),

            "question": r.get("question"),
            "gold_answer": r.get("gold_answer"),
            "gold_support_titles": as_list(r.get("gold_support_titles")),

            "hop1_query": r.get("hop1_query", ""),
            "hop1_titles": as_list(r.get("hop1_titles")),
            "hop1_docs": as_list(r.get("hop1_docs")),

            "current_query": r.get("current_query", ""),
            "current_hop2_titles": as_list(r.get("current_hop2_titles")),
            "current_hop2_docs": as_list(r.get("current_hop2_docs")),

            # Compatibility aliases for existing prompt-update scripts.
            "hop2_query": r.get("current_query", ""),
            "hop2_titles": as_list(r.get("current_hop2_titles")),
            "hop2_docs": as_list(r.get("current_hop2_docs")),
            "missing_titles_after_hop1": as_list(r.get("missing_after_hop1")),
            "missing_titles_after_hop2": as_list(r.get("missing_after_hop2")),

            "missing_after_hop1": as_list(r.get("missing_after_hop1")),
            "missing_after_hop2": as_list(r.get("missing_after_hop2")),

            "new_support_titles_hop2": as_list(r.get("new_support_titles_hop2")),
            "hit_titles_hop1": as_list(r.get("hit_titles_hop1")),
            "hit_titles_total": as_list(r.get("hit_titles_total")),

            "summary_1": r.get("summary_1"),
            "summary_2": r.get("summary_2"),
            "pred_answer": r.get("pred_answer"),
            "score": float(r.get("score") or 0.0),

            "support_recall_hop1": r.get("support_recall_hop1"),
            "support_recall_hop2_only": r.get("support_recall_hop2_only"),
            "support_recall_total": r.get("support_recall_total"),
            "current_support_recall_hop2": r.get("current_support_recall_hop2", r.get("support_recall_hop2_only")),
            "current_missing_recovery_rate": current_mr(r),

            "bucket": current_bucket(r),
            "source_row": r,
        }
        cases[str(cid)] = case
    return cases


def unique_ints(xs: list[Any]) -> list[int]:
    out = []
    seen = set()
    for x in xs:
        i = int(x)
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def quarantine_existing(paths: list[Path], root: Path) -> Path | None:
    existing = [p for p in paths if p.exists()]
    if not existing:
        return None
    qdir = root / f"split_oracle_rebuild_{time.strftime('%Y%m%d_%H%M%S')}"
    qdir.mkdir(parents=True, exist_ok=False)
    for p in existing:
        shutil.move(str(p), str(qdir / p.name))
    return qdir


def oracle_one(task: dict[str, Any]) -> dict[str, Any]:
    try:
        r = task["case"]
        client = task["client"]

        llm = chat_query_candidates(
            client=client,
            model=task["model"],
            base_url=task["base_url"],
            question=str(r.get("question") or ""),
            gold_answer=str(r.get("gold_answer") or ""),
            gold_support_titles=[str(x) for x in as_list(r.get("gold_support_titles"))],
            missing_after_hop1=[str(x) for x in as_list(r.get("missing_after_hop1"))],
            current_query=str(r.get("current_query") or ""),
            current_titles=[str(x) for x in as_list(r.get("current_hop2_titles"))],
            summary_1=str(r.get("summary_1") or ""),
            summary_2=str(r.get("summary_2") or ""),
            max_tokens=task["max_tokens"],
            temperature=task["temperature"],
            retries=task["retries"],
        )

        candidates = []
        candidates.extend(llm["queries"])
        candidates.extend(deterministic_oracle_queries(r))

        # Deduplicate.
        dedup = []
        seen = set()
        for q in candidates:
            q = re.sub(r"\s+", " ", str(q or "")).strip()
            if q and q not in seen:
                seen.add(q)
                dedup.append(q)

        best = choose_best_oracle(
            dedup,
            k=task["k"],
            gold_support_titles=as_list(r.get("gold_support_titles")),
            missing_after_hop1=as_list(r.get("missing_after_hop1")),
        )

        current = {
            "query": r.get("current_query"),
            "titles": as_list(r.get("current_hop2_titles")),
            "missing_recovery_rate": r.get("current_missing_recovery_rate"),
            "support_recall_total": r.get("support_recall_total"),
        }

        return {
            "case_id": r["case_id"],
            "bucket": r["bucket"],
            "question": r.get("question"),
            "gold_answer": r.get("gold_answer"),
            "gold_support_titles": as_list(r.get("gold_support_titles")),
            "missing_after_hop1": as_list(r.get("missing_after_hop1")),
            "current": current,
            "llm_raw": llm["raw"],
            "llm_queries": llm["queries"],
            "deterministic_queries": deterministic_oracle_queries(r),
            "all_candidates": dedup,
            "best": best,
            "error": False,
        }
    except Exception as e:
        return {
            "case_id": task["case"].get("case_id"),
            "bucket": task["case"].get("bucket"),
            "error": True,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollout", type=Path, required=True)
    ap.add_argument("--out-index", type=Path, required=True)
    ap.add_argument("--out-split", type=Path, required=True)
    ap.add_argument("--summary-out", type=Path, required=True)
    ap.add_argument("--oracle-out", type=Path, required=True)

    ap.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    ap.add_argument("--k", type=int, default=7)

    ap.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
    ap.add_argument("--base-url", type=str, default=None)
    ap.add_argument("--api-key", type=str, default="EMPTY")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--num-threads", type=int, default=4)
    ap.add_argument("--retries", type=int, default=4)

    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--num-batches", type=int, default=3)
    ap.add_argument("--full-size", type=int, default=143)
    ap.add_argument("--quarantine-root", type=Path, default=Path("experiments/prompt_update_qwen3_8b/cache/bad_runs"))
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    base_url = args.base_url or os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
    if not base_url:
        raise EnvironmentError("Set --base-url or OPENAI_BASE_URL/OPENAI_API_BASE")

    base.set_retriever_dir(str(args.retriever_dir))

    qdir = quarantine_existing([args.out_index, args.out_split, args.summary_out, args.oracle_out], args.quarantine_root)
    if qdir:
        print("[quarantined existing outputs to]", qdir)

    rollout = read_jsonl(args.rollout)
    cases = build_cases_from_rollout(rollout)

    by_bucket: dict[str, list[int]] = {b: [] for b in BATCH_BUCKET_COUNTS}
    for cid_s, c in cases.items():
        by_bucket[c["bucket"]].append(int(cid_s))

    rng = random.Random(args.seed)
    for b in by_bucket:
        rng.shuffle(by_bucket[b])

    for b, n_per_batch in BATCH_BUCKET_COUNTS.items():
        need = n_per_batch * args.num_batches
        have = len(by_bucket[b])
        if have < need:
            raise ValueError(f"bucket {b} has {have}; need {need}")

    # Build 3×10 update batches current-only.
    offsets = {b: 0 for b in BATCH_BUCKET_COUNTS}
    batches = []
    batch_used = set()
    for bid in range(args.num_batches):
        case_ids_by_bucket = {}
        case_ids = []
        for b, n in BATCH_BUCKET_COUNTS.items():
            start = offsets[b]
            end = start + n
            picked = by_bucket[b][start:end]
            offsets[b] = end
            case_ids_by_bucket[b] = picked
            case_ids.extend(picked)
            batch_used.update(picked)
        batches.append({
            "batch_id": bid,
            "case_ids_by_bucket": case_ids_by_bucket,
            "case_ids": case_ids,
            "bucket_counts": {k: len(v) for k, v in case_ids_by_bucket.items()},
        })

    oracle_target_case_ids = []
    for b in batches:
        oracle_target_case_ids.extend(b["case_ids"])
    oracle_target_case_ids = unique_ints(oracle_target_case_ids)

    print("[info] bucket counts:", {b: len(v) for b, v in by_bucket.items()})
    print("[info] oracle target cases:", len(oracle_target_case_ids), oracle_target_case_ids)

    client = OpenAI(api_key=args.api_key, base_url=base_url)

    tasks = []
    for cid in oracle_target_case_ids:
        tasks.append({
            "case": cases[str(cid)],
            "client": client,
            "model": args.model,
            "base_url": base_url,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "retries": args.retries,
            "k": args.k,
        })

    oracle_rows = []
    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(oracle_one, t) for t in tasks]
        for fut in tqdm(cf.as_completed(futs), total=len(futs), desc="oracle target generation"):
            oracle_rows.append(fut.result())

    oracle_by_id = {int(r["case_id"]): r for r in oracle_rows}

    args.oracle_out.parent.mkdir(parents=True, exist_ok=True)
    with args.oracle_out.open("w", encoding="utf-8") as f:
        for r in sorted(oracle_rows, key=lambda x: int(x["case_id"])):
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")

    # Attach oracle fields to batch cases.
    invalid_oracle = []
    for cid in oracle_target_case_ids:
        c = cases[str(cid)]
        o = oracle_by_id.get(cid)
        if not o or o.get("error") or o.get("best", {}).get("error"):
            invalid_oracle.append(cid)
            continue

        best = o["best"]
        cur_mr = float(c.get("current_missing_recovery_rate") or 0.0)
        oracle_mr = float(best.get("missing_recovery_rate") or 0.0)
        oracle_sr = best.get("support_recall_total")

        c.update({
            "oracle_target_query": best.get("query"),
            "oracle_target_titles": best.get("retrieved_titles", []),
            "oracle_target_retrieved_titles": best.get("retrieved_titles", []),
            "oracle_target_retrieved_docs": best.get("retrieved_docs", []),
            "oracle_target_missing_recovery_rate": oracle_mr,
            "oracle_target_support_recall_total": oracle_sr,
            "oracle_target_hit_missing_titles": best.get("hit_missing_titles", []),
            "oracle_target_hit_gold_titles": best.get("hit_gold_titles", []),
            "oracle_target_generation": o,
        })

        # Only W_retrieval and C_fragile require oracle improvement for transition quality.
        if c["bucket"] in {"W_retrieval", "C_fragile"} and oracle_mr < cur_mr:
            invalid_oracle.append(cid)

    # Build full143 eval split from all non-batch cases; oracle not required.
    eligible = [int(cid) for cid in cases if int(cid) not in batch_used]
    rng.shuffle(eligible)
    full143 = eligible[:args.full_size]
    if len(full143) != args.full_size:
        raise ValueError(f"full143 got {len(full143)}")

    case_meta = {}
    for cid_s, c in cases.items():
        cid = int(cid_s)
        case_meta[cid_s] = {
            "bucket": c["bucket"],
            "score": c.get("score"),
            "question": c.get("question"),
            "current_missing_recovery_rate": c.get("current_missing_recovery_rate"),
            "current_support_recall_hop2": c.get("current_support_recall_hop2"),
            "has_oracle_target": bool(c.get("oracle_target_query")),
            "oracle_target_missing_recovery_rate": c.get("oracle_target_missing_recovery_rate"),
            "in_update_batch": cid in batch_used,
            "in_full143": cid in set(full143),
        }

    split = {
        "name": "qwen3_8b_positive_safety_b10_split_seed0_batch_oracle",
        "seed": args.seed,
        "source_rollout": str(args.rollout),
        "conditions": CONDITIONS,
        "bucket_definitions": {
            "W_retrieval": "score=0 and missing_after_hop2 nonempty; oracle target generated only for update-batch cases.",
            "C_clean": "score=1 and missing_after_hop2 empty.",
            "C_fragile": "score=1 and missing_after_hop2 nonempty; oracle target generated only for update-batch cases.",
            "W_other": "score=0 and missing_after_hop2 empty.",
        },
        "bucket_case_ids": {b: ids for b, ids in by_bucket.items()},
        "original_bucket_counts": {b: len(ids) for b, ids in by_bucket.items()},
        "case_meta": case_meta,
        "update_batches": {
            "compositions": {
                "mixed_custom": {
                    "description": "Per batch: 5 W_retrieval, 3 C_clean, 1 C_fragile, 1 W_other.",
                    "batch_bucket_counts": BATCH_BUCKET_COUNTS,
                    "batches": batches,
                }
            }
        },
        "eval_split": {
            "full143": full143,
            "full143_excludes_update_batches": True,
        },
        "oracle_target_scope": {
            "strategy": "Generate oracle targets only for 30 update-batch cases.",
            "case_ids": oracle_target_case_ids,
            "oracle_out": str(args.oracle_out),
        },
    }

    index = {
        **cases,
        "cases": cases,
        "case_state_index": cases,
        "_meta": {
            "source_rollout": str(args.rollout),
            "n_cases": len(cases),
            "bucket_counts": {b: len(ids) for b, ids in by_bucket.items()},
            "oracle_target_case_ids": oracle_target_case_ids,
            "invalid_oracle_case_ids": invalid_oracle,
            "oracle_out": str(args.oracle_out),
            "notes": [
                "Oracle targets are generated only for update-batch cases.",
                "Eval full143 does not require oracle target states.",
                "current_* fields are Qwen fixed rollout states.",
            ],
        },
    }

    summary = {
        "out_index": str(args.out_index),
        "out_split": str(args.out_split),
        "oracle_out": str(args.oracle_out),
        "n_rollout": len(rollout),
        "bucket_counts": {b: len(ids) for b, ids in by_bucket.items()},
        "batches": [b["case_ids_by_bucket"] for b in batches],
        "batch_used_n": len(batch_used),
        "oracle_target_n": len(oracle_target_case_ids),
        "oracle_errors": sum(bool(r.get("error")) for r in oracle_rows),
        "invalid_oracle_case_ids": invalid_oracle,
        "full143_n": len(full143),
        "full143_overlap_with_update_batches": len(set(full143) & batch_used),
    }

    args.out_index.parent.mkdir(parents=True, exist_ok=True)
    args.out_split.parent.mkdir(parents=True, exist_ok=True)

    write_json(args.out_index, index)
    write_json(args.out_split, split)
    write_json(args.summary_out, summary)

    print("[wrote]", args.oracle_out)
    print("[wrote]", args.out_index)
    print("[wrote]", args.out_split)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if invalid_oracle:
        print("[warn] invalid oracle cases:", invalid_oracle)
        print("[warn] You can inspect oracle_out before continuing to prompt artifact generation.")


if __name__ == "__main__":
    main()
