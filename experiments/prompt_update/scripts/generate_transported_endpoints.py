# /home/jinwoo/gepa-official/experiments/prompt_update/scripts/generate_transported_endpoints.py
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


# Build C-side damaged endpoint as:
#   R_minus = R_plus + transported_delta_R_prime
#
# R_plus is the target sample's current/reference retrieval state.
# delta_R_prime is inferred from the matched W-side repair transition.
# R_minus is a semantic retrieval-state endpoint, not an actual BM25 run result.

SYSTEM = """You are constructing a transported damaged retrieval endpoint for HotpotQA second-hop BM25 retrieval.

You are given:
1. A target reference retrieval state R_plus.
2. A matched W-side repair-candidate transition:
   - W_R_minus: current failed retrieval
   - W_R_plus: oracle/repaired retrieval
3. A match explanation describing why this W transition is transferable to the target sample.

Your task:
Construct a target-specific damaged retrieval endpoint R_minus by applying the transported failure edit delta_R_prime to R_plus.

Interpretation:
- R_minus = R_plus + transported delta_R_prime.
- delta_R_prime is not a vector addition. It is a semantic retrieval-state edit.
- The edit should be inferred from the W-side transition's failure pattern and applied to the target sample's own anchors, relations, qualifiers, and distractors.
- Do not copy W-side entities into the target endpoint unless they are already relevant to the target sample.
- Do not create an unrelated bad retrieval state.
- Preserve enough of the target context that R_minus is a plausible local neighbor of R_plus.
- Damage should be specific: weaken/remove/blur the relevant anchor, relation, qualifier, evidence family, or candidate-set focus.
- The endpoint may or may not cause answer failure. Do not claim C->W is guaranteed.
- This is a semantic endpoint for later prompt-update material, not an actual BM25 retrieval result.

Return strict JSON only.
Keep all string fields concise.

Schema:
{
  "applied_failure_summary": "<one-sentence summary of the transported failure>",
  "delta_R_prime": {
    "edit_type": "anchor|bridge_relation|entity_disambiguation|missing_qualifier|surface_form|noisy_entity|answer_type|query_shape|candidate_set|evidence_family|mixed",
    "weakened_or_removed_cues": ["<target-specific cue>", "..."],
    "overemphasized_or_distractor_cues": ["<target-specific cue>", "..."],
    "query_behavior_change": "<how a query would change under this damage>",
    "retrieval_focus_change": "<how retrieved evidence focus would shift>"
  },
  "R_minus": {
    "state_role": "transported_damaged",
    "damaged_query": "<one compact BM25-style query that reflects the damaged behavior>",
    "expected_retrieved_titles": ["<plausible title>", "..."],
    "expected_missing_or_weakened_support_titles": ["<support title/cue likely weakened>", "..."],
    "damaged_retrieval_summary": "<short description of the damaged retrieval state>",
    "expected_effect": "<short caveat; answer flip is not assumed>"
  },
  "locality_check": {
    "is_local_neighbor_of_R_plus": true,
    "preserved_context": ["<cue preserved from R_plus>", "..."],
    "why_not_unrelated": "<brief reason>"
  },
  "confidence": 0.0
}
"""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.open("r", encoding="utf-8") if l.strip()]


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
    return model.split("/", 1)[1] if model.startswith("openai/") else model


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


def compact_state(state: dict[str, Any] | None, *, max_docs: int, max_doc_chars: int, max_summary_chars: int) -> dict[str, Any]:
    state = state or {}
    docs = state.get("retrieved_docs") or []

    compact_docs = []
    for d in docs[:max_docs]:
        if isinstance(d, dict):
            compact_docs.append({
                "title": d.get("title"),
                "text": trunc(d.get("text"), max_doc_chars),
            })
        else:
            text = str(d or "")
            title = text.split("|", 1)[0].strip() if "|" in text else text[:120]
            compact_docs.append({
                "title": title,
                "text": trunc(text, max_doc_chars),
            })

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
        "retrieved_doc_snippets": compact_docs,
    }


def make_payload(
    *,
    target_rec: dict[str, Any],
    matched_w_rec: dict[str, Any],
    match_row: dict[str, Any],
    max_docs: int,
    max_doc_chars: int,
    max_summary_chars: int,
) -> str:
    # Target R_plus: the reference state to be damaged.
    target_R_plus = compact_state(
        target_rec["current_state"],
        max_docs=max_docs,
        max_doc_chars=max_doc_chars,
        max_summary_chars=max_summary_chars,
    )

    # W transition: repair candidate used to infer the transported failure edit.
    w_R_minus = compact_state(
        matched_w_rec["current_state"],
        max_docs=max_docs,
        max_doc_chars=max_doc_chars,
        max_summary_chars=max_summary_chars,
    )
    w_R_plus = compact_state(
        matched_w_rec["oracle_state"],
        max_docs=max_docs,
        max_doc_chars=max_doc_chars,
        max_summary_chars=max_summary_chars,
    )

    payload = {
        "task": "generate_R_minus_as_R_plus_plus_transported_delta_R_prime",
        "target_sample": {
            "case_id": int(target_rec["case_id"]),
            "bucket": target_rec.get("bucket"),
            "question": target_rec.get("question"),
            "gold_answer": target_rec.get("gold_answer"),
            "gold_support_titles": target_rec.get("gold_support_titles") or [],
            "summary_1": trunc(target_rec.get("summary_1"), 1400),
            "R_plus_reference": target_R_plus,
        },
        "matched_W_side_transition": {
            "case_id": int(matched_w_rec["case_id"]),
            "question": matched_w_rec.get("question"),
            "gold_answer": matched_w_rec.get("gold_answer"),
            "gold_support_titles": matched_w_rec.get("gold_support_titles") or [],
            "W_R_minus_current_failed": w_R_minus,
            "W_R_plus_oracle_target": w_R_plus,
        },
        "match_judgment": {
            "dominant_gap_type": match_row.get("dominant_gap_type"),
            "why_selected": match_row.get("why_selected"),
            "transported_damage_hypothesis": match_row.get("transported_damage_hypothesis"),
            "expected_damaged_query_behavior": match_row.get("expected_damaged_query_behavior"),
            "expected_damaged_retrieval_focus": match_row.get("expected_damaged_retrieval_focus"),
            "confidence": match_row.get("confidence"),
        },
        "construction_requirement": {
            "formula": "R_minus = R_plus + transported_delta_R_prime",
            "do_not": [
                "do not generate an unrelated bad state",
                "do not copy W-side entities into the target unless already relevant",
                "do not claim answer flip is guaranteed",
                "do not describe this as actual BM25 output"
            ],
        },
    }

    return json.dumps(payload, ensure_ascii=False, indent=2)


def validate_obj(obj: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(obj.get("delta_R_prime"), dict):
        raise ValueError("missing delta_R_prime object")
    if not isinstance(obj.get("R_minus"), dict):
        raise ValueError("missing R_minus object")

    rminus = obj["R_minus"]
    if not str(rminus.get("damaged_query") or "").strip():
        raise ValueError("empty R_minus.damaged_query")
    if not isinstance(rminus.get("expected_retrieved_titles"), list):
        raise ValueError("R_minus.expected_retrieved_titles must be list")

    return obj


def generate_one(task: tuple) -> dict[str, Any]:
    (
        batch_id,
        match_row,
        target_rec,
        matched_w_rec,
        model,
        temperature,
        max_output_tokens,
        retries,
        max_docs,
        max_doc_chars,
        max_summary_chars,
    ) = task

    user = make_payload(
        target_rec=target_rec,
        matched_w_rec=matched_w_rec,
        match_row=match_row,
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
    obj = validate_obj(extract_json_obj(raw))

    return {
        "row_type": "transported_damaged_endpoint",
        "batch_id": batch_id,
        "case_id": int(target_rec["case_id"]),
        "bucket": target_rec.get("bucket"),
        "matched_w_case_id": int(matched_w_rec["case_id"]),
        "matched_w_dominant_gap_type": match_row.get("dominant_gap_type"),
        "match_confidence": match_row.get("confidence"),

        # R_plus is the reference endpoint from the target sample.
        "R_plus_role": "current_reference",
        "R_plus": compact_state(
            target_rec["current_state"],
            max_docs=max_docs,
            max_doc_chars=max_doc_chars,
            max_summary_chars=max_summary_chars,
        ),

        # delta_R_prime is the transported semantic damage edit.
        "delta_R_prime": obj["delta_R_prime"],

        # R_minus is semantic, expected, and local to R_plus.
        "R_minus_role": "transported_damaged",
        "R_minus": obj["R_minus"],

        "applied_failure_summary": obj.get("applied_failure_summary"),
        "locality_check": obj.get("locality_check"),
        "confidence": obj.get("confidence"),
        "raw": raw,
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()

    ap.add_argument("--case-state-index", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/case_state_index.json"))
    ap.add_argument("--matches", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_c_failure_matches.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_c_transported_endpoints.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_c_transported_endpoints.summary.json"))

    ap.add_argument("--batch-id", type=int, default=0)
    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-output-tokens", type=int, default=4096)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--num-threads", type=int, default=4)

    ap.add_argument("--max-docs", type=int, default=4)
    ap.add_argument("--max-doc-chars", type=int, default=450)
    ap.add_argument("--max-summary-chars", type=int, default=700)

    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    index = read_json(args.case_state_index)
    matches = [r for r in read_jsonl(args.matches) if not r.get("error")]

    if args.overwrite:
        for p in [args.out, args.summary_out]:
            if p.exists():
                p.unlink()

    done = set()
    existing_rows = []
    if args.out.exists():
        existing_rows = read_jsonl(args.out)
        for r in existing_rows:
            if not r.get("error"):
                done.add(int(r["case_id"]))

    tasks = []
    for m in matches:
        cid = int(m["target_case_id"])
        if cid in done:
            continue

        target_rec = dict(index["cases"][str(cid)])
        target_rec["case_id"] = cid

        wid = int(m["matched_w_case_id"])
        matched_w_rec = dict(index["cases"][str(wid)])
        matched_w_rec["case_id"] = wid

        tasks.append((
            args.batch_id,
            m,
            target_rec,
            matched_w_rec,
            args.model,
            args.temperature,
            args.max_output_tokens,
            args.retries,
            args.max_docs,
            args.max_doc_chars,
            args.max_summary_chars,
        ))

    print("[info] batch_id:", args.batch_id)
    print("[info] matches:", len(matches))
    print("[info] pending:", len(tasks), "existing:", len(existing_rows))

    new_rows = []

    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        fut_to_task = {ex.submit(generate_one, t): t for t in tasks}
        for fut in tqdm(cf.as_completed(fut_to_task), total=len(fut_to_task), desc="generate transported endpoints"):
            t = fut_to_task[fut]
            _, match_row, target_rec, matched_w_rec, *_ = t
            try:
                row = fut.result()
            except Exception as e:
                row = {
                    "row_type": "transported_damaged_endpoint",
                    "error": True,
                    "batch_id": args.batch_id,
                    "case_id": int(target_rec["case_id"]),
                    "bucket": target_rec.get("bucket"),
                    "matched_w_case_id": int(matched_w_rec["case_id"]),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc(),
                }

            append_jsonl(args.out, row)
            new_rows.append(row)

    all_rows = read_jsonl(args.out) if args.out.exists() else []
    ok = [r for r in all_rows if not r.get("error")]

    summary = {
        "script": "generate_transported_endpoints.py",
        "case_state_index": str(args.case_state_index),
        "matches": str(args.matches),
        "out": str(args.out),
        "batch_id": args.batch_id,
        "n_rows": len(all_rows),
        "n_ok": len(ok),
        "n_error": len(all_rows) - len(ok),
        "rows": [
            {
                "case_id": r.get("case_id"),
                "bucket": r.get("bucket"),
                "matched_w_case_id": r.get("matched_w_case_id"),
                "edit_type": (r.get("delta_R_prime") or {}).get("edit_type"),
                "damaged_query": (r.get("R_minus") or {}).get("damaged_query"),
                "expected_retrieved_titles": (r.get("R_minus") or {}).get("expected_retrieved_titles"),
                "confidence": r.get("confidence"),
                "error": r.get("error", False),
            }
            for r in all_rows
        ],
    }
    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary["rows"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
