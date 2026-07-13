# /home/jinwoo/gepa-official/experiments/prompt_update/scripts/match_transportable_pairs.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import time
import traceback
from pathlib import Path
from typing import Any

from tqdm import tqdm


SYSTEM = """You are judging semantic transferability between W-side retrieval repair transitions.

Each candidate transition is a W-side repair-candidate transition for the HotpotQA second-hop BM25 query generator:
- R_minus: current failed retrieval state
- R_plus: oracle/repaired retrieval state

Given one target reference sample with a current/reference retrieval state R_ref, select which W-side transition is most semantically transferable as a plausible damaged-endpoint operator for the target sample.

Transferability means that applying the W-side failure pattern to the target reference retrieval state would create a plausible local retrieval degradation, considering:
- which entity/title/alias anchors would be removed, blurred, replaced, or over-emphasized
- which bridge relation, comparison relation, or task relation would be damaged
- which evidence family or answer type would be shifted
- which distractors, wrong senses, or noisy entity families would become more likely
- whether the candidate set would be broadened, narrowed, preserved, or re-centered
- what kind of retrieval failure the W-side transition corrects

Important:
- Select exactly one candidate unless all candidates are genuinely unusable.
- Do not judge which W transition is more correct or larger in isolation.
- Judge which W transition is most applicable to the given target reference sample.
- Do not require a bijection. Multiple target samples may select the same W transition.
- Do not claim the transported endpoint will necessarily flip the answer; it may become wrong or remain answerable after evaluation.
- Focus on retrieval/query behavior, not final answer correctness.
- Return strict JSON only.
- Keep every string field short: at most 35 words.
- Do not include newline characters inside JSON string values.
- Prefer concise phrases over long explanations.

Return schema:
{
  "selected_candidate_id": <integer W-side case_id>,
  "selected_candidate_index": <integer 0-based index in candidates>,
  "why_selected": "<short explanation focused on semantic transferability>",
  "dominant_gap_type": "anchor|bridge_relation|entity_disambiguation|missing_qualifier|surface_form|noisy_entity|answer_type|query_shape|candidate_set|evidence_family|mixed",
  "transported_damage_hypothesis": "<what retrieval damage would be induced in the target reference state>",
  "expected_damaged_query_behavior": "<how the target query behavior would change if this failure were transported>",
  "expected_damaged_retrieval_focus": "<what titles/entities/evidence family would become over- or under-emphasized>",
  "confidence": 0.0
}
"""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


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
        raise ValueError(f"could not find JSON object in: {text[:800]}")
    return json.loads(m.group(0))


def normalize_model(model: str) -> str:
    if model.startswith("openai/"):
        return model.split("/", 1)[1]
    return model


def call_openai(
    *,
    model: str,
    system: str,
    user: str,
    temperature: float,
    max_output_tokens: int,
    retries: int,
) -> str:
    from openai import OpenAI

    client = OpenAI()
    model = normalize_model(model)
    last_err = None

    for attempt in range(retries + 1):
        try:
            kwargs = {
                "model": model,
                "input": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_output_tokens": max(16, int(max_output_tokens)),
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
            if text is not None and not str(text).strip():
                raise RuntimeError("empty model output")

            chunks = []
            for item in getattr(resp, "output", []) or []:
                for c in getattr(item, "content", []) or []:
                    t = getattr(c, "text", None)
                    if t:
                        chunks.append(str(t))
            if chunks and "\n".join(chunks).strip():
                return "\n".join(chunks)

            fallback = str(resp)
            if not fallback.strip():
                raise RuntimeError("empty model output")
            return fallback

        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(min(2 ** attempt, 8))

    raise RuntimeError(f"OpenAI call failed after {retries + 1} attempts: {last_err}")


def trunc(x: Any, n: int) -> str:
    s = str(x or "")
    return s if len(s) <= n else s[:n] + "..."


def compact_docs(docs: list[dict[str, Any]] | None, max_docs: int, max_chars: int) -> list[dict[str, str]]:
    out = []
    for d in (docs or [])[:max_docs]:
        if isinstance(d, dict):
            out.append({
                "title": str(d.get("title") or "")[:160],
                "text": trunc(d.get("text"), max_chars),
            })
        else:
            text = str(d or "")
            title = text.split("|", 1)[0].strip() if "|" in text else text[:120]
            out.append({
                "title": title,
                "text": trunc(text, max_chars),
            })
    return out


def compact_state(state: dict[str, Any] | None, *, max_docs: int, max_doc_chars: int, max_summary_chars: int) -> dict[str, Any]:
    state = state or {}
    return {
        "state_role": state.get("state_role"),
        "query": state.get("query"),
        "retrieved_titles": state.get("retrieved_titles") or [],
        "missing_titles_after_hop2": state.get("missing_titles_after_hop2") or [],
        "new_support_titles_hop2": state.get("new_support_titles_hop2") or [],
        "support_recall_total": state.get("support_recall_total"),
        "support_recall_hop2_only": state.get("support_recall_hop2_only"),
        "missing_recovery_rate": state.get("missing_recovery_rate"),
        "summary_2": trunc(state.get("summary_2"), max_summary_chars),
        "retrieved_doc_snippets": compact_docs(state.get("retrieved_docs") or [], max_docs, max_doc_chars),
    }


def build_w_candidate(
    *,
    rec: dict[str, Any],
    candidate_index: int,
    max_docs: int,
    max_doc_chars: int,
    max_summary_chars: int,
) -> dict[str, Any]:
    current = rec["current_state"]
    oracle = rec["oracle_state"]

    return {
        "candidate_index": candidate_index,
        "candidate_id": int(rec["case_id"]),
        "candidate_role": "W-side repair candidate transition",
        "question": rec.get("question"),
        "gold_answer": rec.get("gold_answer"),
        "gold_support_titles": rec.get("gold_support_titles") or [],
        "missing_titles_after_hop2": current.get("missing_titles_after_hop2") or [],
        "R_minus_current_failed": compact_state(
            current,
            max_docs=max_docs,
            max_doc_chars=max_doc_chars,
            max_summary_chars=max_summary_chars,
        ),
        "R_plus_oracle_target": compact_state(
            oracle,
            max_docs=max_docs,
            max_doc_chars=max_doc_chars,
            max_summary_chars=max_summary_chars,
        ),
    }


def build_target_sample(
    *,
    rec: dict[str, Any],
    max_docs: int,
    max_doc_chars: int,
    max_summary_chars: int,
) -> dict[str, Any]:
    return {
        "target_case_id": int(rec["case_id"]),
        "target_bucket": rec.get("bucket"),
        "target_role": "reference retrieval state to be damaged by transported failure",
        "question": rec.get("question"),
        "gold_answer": rec.get("gold_answer"),
        "gold_support_titles": rec.get("gold_support_titles") or [],
        "summary_1": trunc(rec.get("summary_1"), 1400),
        "current_correct": rec.get("current_correct"),
        "current_retrieval_failure": rec.get("current_retrieval_failure"),
        "R_ref_current_state": compact_state(
            rec.get("current_state"),
            max_docs=max_docs,
            max_doc_chars=max_doc_chars,
            max_summary_chars=max_summary_chars,
        ),
        "endpoint_plan": rec.get("endpoint_plan"),
    }


def make_user_payload(
    *,
    target_rec: dict[str, Any],
    candidate_recs: list[dict[str, Any]],
    max_docs: int,
    max_doc_chars: int,
    max_summary_chars: int,
) -> str:
    candidates = [
        build_w_candidate(
            rec=r,
            candidate_index=i,
            max_docs=max_docs,
            max_doc_chars=max_doc_chars,
            max_summary_chars=max_summary_chars,
        )
        for i, r in enumerate(candidate_recs)
    ]

    payload = {
        "task": "select_most_transportable_W_side_transition_for_target_reference_sample",
        "target_reference_sample": build_target_sample(
            rec=target_rec,
            max_docs=max_docs,
            max_doc_chars=max_doc_chars,
            max_summary_chars=max_summary_chars,
        ),
        "candidate_W_side_transitions": candidates,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def validate_selection(obj: dict[str, Any], candidate_ids: list[int]) -> dict[str, Any]:
    out = dict(obj)

    selected_id = out.get("selected_candidate_id")
    selected_index = out.get("selected_candidate_index")

    valid_by_id = None
    valid_by_index = None

    try:
        sid = int(selected_id)
        if sid in candidate_ids:
            valid_by_id = sid
    except Exception:
        pass

    try:
        idx = int(selected_index)
        if 0 <= idx < len(candidate_ids):
            valid_by_index = candidate_ids[idx]
    except Exception:
        pass

    if valid_by_id is None and valid_by_index is None:
        raise ValueError(f"invalid selected_candidate_id/index: {obj}; valid candidate_ids={candidate_ids}")

    if valid_by_id is None:
        valid_by_id = valid_by_index
        out["selected_candidate_id"] = valid_by_id

    if valid_by_index is None or valid_by_index != valid_by_id:
        out["selected_candidate_index"] = candidate_ids.index(valid_by_id)

    out["selected_candidate_id"] = int(out["selected_candidate_id"])
    out["selected_candidate_index"] = int(out["selected_candidate_index"])

    return out


def match_one(task: tuple) -> dict[str, Any]:
    (
        batch_id,
        target_case_id,
        target_rec,
        candidate_recs,
        model,
        temperature,
        max_output_tokens,
        retries,
        max_docs,
        max_doc_chars,
        max_summary_chars,
    ) = task

    candidate_ids = [int(r["case_id"]) for r in candidate_recs]
    user = make_user_payload(
        target_rec=target_rec,
        candidate_recs=candidate_recs,
        max_docs=max_docs,
        max_doc_chars=max_doc_chars,
        max_summary_chars=max_summary_chars,
    )

    raw = call_openai(
        model=model,
        system=SYSTEM,
        user=user,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        retries=retries,
    )
    obj = validate_selection(extract_json_obj(raw), candidate_ids)

    matched = next(r for r in candidate_recs if int(r["case_id"]) == int(obj["selected_candidate_id"]))

    return {
        "row_type": "transportable_pair_match",
        "batch_id": batch_id,
        "target_case_id": int(target_case_id),
        "target_bucket": target_rec.get("bucket"),
        "target_question": target_rec.get("question"),
        "candidate_case_ids": candidate_ids,
        "matched_w_case_id": int(obj["selected_candidate_id"]),
        "matched_w_candidate_index": int(obj["selected_candidate_index"]),
        "matched_w_question": matched.get("question"),
        "match_method": "single_call_top1_over_candidate_set",
        "why_selected": obj.get("why_selected"),
        "dominant_gap_type": obj.get("dominant_gap_type"),
        "transported_damage_hypothesis": obj.get("transported_damage_hypothesis"),
        "expected_damaged_query_behavior": obj.get("expected_damaged_query_behavior"),
        "expected_damaged_retrieval_focus": obj.get("expected_damaged_retrieval_focus"),
        "confidence": obj.get("confidence"),
        "raw": raw,
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()

    ap.add_argument("--split", type=Path, default=Path("experiments/prompt_update/data/positive_safety_b10_split_seed0.json"))
    ap.add_argument("--case-state-index", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/case_state_index.json"))
    ap.add_argument("--out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_c_failure_matches.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_c_failure_matches.summary.json"))

    ap.add_argument("--batch-id", type=int, default=0)
    ap.add_argument("--composition", type=str, default="mixed_custom")
    ap.add_argument("--candidate-bucket", type=str, default="W_retrieval")
    ap.add_argument("--target-buckets", nargs="+", default=["C_clean", "W_other"])

    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-output-tokens", type=int, default=2048)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--num-threads", type=int, default=4)

    ap.add_argument("--max-docs", type=int, default=4)
    ap.add_argument("--max-doc-chars", type=int, default=450)
    ap.add_argument("--max-summary-chars", type=int, default=700)

    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    split = read_json(args.split)
    index = read_json(args.case_state_index)

    comp = split["update_batches"]["compositions"][args.composition]
    batch = comp["batches"][args.batch_id]
    by_bucket = batch["case_ids_by_bucket"]

    candidate_ids = [int(x) for x in by_bucket.get(args.candidate_bucket, [])]
    target_ids = []
    for b in args.target_buckets:
        target_ids.extend(int(x) for x in by_bucket.get(b, []))

    if not candidate_ids:
        raise ValueError(f"No candidates found for bucket={args.candidate_bucket} in composition={args.composition}, batch_id={args.batch_id}")
    if not target_ids:
        raise ValueError(f"No target ids found for target_buckets={args.target_buckets}")

    candidate_recs = []
    for cid in candidate_ids:
        rec = dict(index["cases"][str(cid)])
        rec["case_id"] = cid
        if not rec.get("oracle_available"):
            raise ValueError(f"candidate W-side case {cid} has no oracle target")
        candidate_recs.append(rec)

    target_recs = []
    for cid in target_ids:
        rec = dict(index["cases"][str(cid)])
        rec["case_id"] = cid
        target_recs.append(rec)

    if args.overwrite:
        for p in [args.out, args.summary_out]:
            if p.exists():
                p.unlink()

    done = set()
    existing_rows = []
    if args.out.exists():
        with args.out.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                existing_rows.append(r)
                if not r.get("error"):
                    done.add(int(r["target_case_id"]))

    tasks = []
    for rec in target_recs:
        cid = int(rec["case_id"])
        if cid in done:
            continue
        tasks.append((
            args.batch_id,
            cid,
            rec,
            candidate_recs,
            args.model,
            args.temperature,
            args.max_output_tokens,
            args.retries,
            args.max_docs,
            args.max_doc_chars,
            args.max_summary_chars,
        ))

    print("[info] composition:", args.composition)
    print("[info] batch_id:", args.batch_id)
    print("[info] candidate_bucket:", args.candidate_bucket, candidate_ids)
    print("[info] target_buckets:", args.target_buckets, target_ids)
    print("[info] pending:", len(tasks), "existing:", len(existing_rows))

    new_rows = []

    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        fut_to_task = {ex.submit(match_one, t): t for t in tasks}
        for fut in tqdm(cf.as_completed(fut_to_task), total=len(fut_to_task), desc="match transportable pairs"):
            t = fut_to_task[fut]
            _, target_case_id, target_rec, candidate_recs, *_ = t
            try:
                row = fut.result()
            except Exception as e:
                row = {
                    "row_type": "transportable_pair_match",
                    "error": True,
                    "batch_id": args.batch_id,
                    "target_case_id": int(target_case_id),
                    "target_bucket": target_rec.get("bucket"),
                    "target_question": target_rec.get("question"),
                    "candidate_case_ids": [int(r["case_id"]) for r in candidate_recs],
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc(),
                }
            append_jsonl(args.out, row)
            new_rows.append(row)

    all_rows = []
    if args.out.exists():
        with args.out.open("r", encoding="utf-8") as f:
            all_rows = [json.loads(l) for l in f if l.strip()]

    ok = [r for r in all_rows if not r.get("error")]
    summary = {
        "script": "match_transportable_pairs.py",
        "split": str(args.split),
        "case_state_index": str(args.case_state_index),
        "out": str(args.out),
        "batch_id": args.batch_id,
        "composition": args.composition,
        "candidate_bucket": args.candidate_bucket,
        "candidate_case_ids": candidate_ids,
        "target_buckets": args.target_buckets,
        "target_case_ids": target_ids,
        "n_rows": len(all_rows),
        "n_ok": len(ok),
        "n_error": len(all_rows) - len(ok),
        "matches": [
            {
                "target_case_id": r.get("target_case_id"),
                "target_bucket": r.get("target_bucket"),
                "matched_w_case_id": r.get("matched_w_case_id"),
                "dominant_gap_type": r.get("dominant_gap_type"),
                "confidence": r.get("confidence"),
            }
            for r in ok
        ],
    }
    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary["matches"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
