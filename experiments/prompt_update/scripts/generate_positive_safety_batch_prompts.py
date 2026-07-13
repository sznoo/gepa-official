#!/usr/bin/env python3
# /home/jinwoo/gepa-official/experiments/prompt_update/scripts/generate_positive_safety_batch_prompts.py
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

from tqdm import tqdm


# Generate one shared create_query_hop2 prompt per positive-safety condition.
#
# Input:
#   batch0_directional_delta_qp.jsonl
#
# Conditions:
#   base
#   delta_p_neg_only
#   delta_p_custom_preserve
#   delta_p_custom_signed
#   endpoint_delta_neg_only
#   endpoint_delta_custom_preserve
#   endpoint_delta_custom_signed
#
# Rule:
#   encourage rows = behavior to absorb
#   avoid rows     = downhill/signed anchor to avoid, not to apply


BATCH_PROMPT_UPDATER_SYSTEM = """You are generating one shared prompt for a HotpotQA second-hop BM25 query writer.

The target module receives:
- question
- summary_1

and must output one compact second-hop BM25 query string.

You are given batch-level evidence from samplewise directional retrieval/query/prompt updates.
Some evidence rows have polarity="encourage"; these describe behavior to absorb.
Some evidence rows have polarity="avoid"; these describe downhill or damaging behavior to avoid.

Your task:
Write a single updated prompt for create_query_hop2.predict that generalizes across the batch.

Important constraints:
- Output a prompt/instruction, not a query.
- The prompt must still ask for exactly one compact BM25 query string.
- Preserve the useful behavior of the current prompt unless evidence strongly indicates a local update.
- Encourage rows should be converted into positive query-writing guidance.
- Avoid rows should be converted into safety constraints or anti-patterns, not copied as positive instructions.
- Do not hard-code the batch answers.
- You may mention sample entities as examples only if phrased as behavior-level guidance.
- Prefer compact retrieval-facing guidance: preserve core anchors, restore relation/type/qualifier cues, avoid noisy side entities, keep answer-bearing title/entity pages in focus.
- Do not ask for multiple queries.
- Do not use web-search syntax such as site:, OR-heavy syntax, or quoted Boolean programs.
- The final prompt should be directly usable as the system/developer prompt for the query writer.

Return strict JSON only:
{
  "updated_prompt": "<shared prompt for create_query_hop2.predict>",
  "rationale": "<brief explanation of the batch-level update>",
  "absorbed_patterns": ["<short pattern>", "..."],
  "avoided_patterns": ["<short pattern>", "..."]
}
"""


CONDITIONS = [
    "base",
    "delta_p_neg_only",
    "delta_p_custom_preserve",
    "delta_p_custom_signed",
    "endpoint_delta_neg_only",
    "endpoint_delta_custom_preserve",
    "endpoint_delta_custom_signed",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.open("r", encoding="utf-8") if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def truncate(x: Any, n: int) -> str:
    s = str(x or "")
    return s if len(s) <= n else s[:n] + "..."


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


def call_model(
    *,
    model: str,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
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

    raise RuntimeError(f"model call failed after {retries + 1} attempts: {last_err}")


def condition_evidence_mode(condition: str) -> str:
    if condition.startswith("delta_p_"):
        return "delta_p_only"
    if condition.startswith("endpoint_delta_"):
        return "endpoint_delta"
    if condition == "base":
        return "base"
    raise ValueError(condition)


def select_rows(rows: list[dict[str, Any]], condition: str) -> list[dict[str, Any]]:
    """Deterministic evidence subset for each condition."""
    ok = [r for r in rows if not r.get("error")]

    if condition == "base":
        return []

    if condition.endswith("neg_only"):
        return [
            r for r in ok
            if r.get("transition_family") == "w_retrieval_repair"
        ]

    if condition.endswith("custom_preserve"):
        return [
            r for r in ok
            if r.get("transition_family") == "w_retrieval_repair"
            or str(r.get("transition_family", "")).endswith("_preserve")
        ]

    if condition.endswith("custom_signed"):
        return [
            r for r in ok
            if r.get("transition_family") == "w_retrieval_repair"
            or str(r.get("transition_family", "")).endswith("_signed")
        ]

    raise ValueError(f"unknown condition: {condition}")


def sort_key(r: dict[str, Any]) -> tuple:
    bucket_order = {
        "W_retrieval": 0,
        "C_fragile": 1,
        "C_clean": 2,
        "W_other": 3,
    }
    pol_order = {"encourage": 0, "avoid": 1}
    return (
        bucket_order.get(r.get("bucket"), 99),
        int(r.get("case_id") or 0),
        pol_order.get(r.get("polarity"), 99),
        str(r.get("transition_family")),
    )


def compact_state(s: dict[str, Any] | None, *, max_titles: int, max_summary_chars: int) -> dict[str, Any]:
    s = s or {}
    return {
        "role": s.get("state_role"),
        "query": s.get("query"),
        "retrieved_titles": (s.get("retrieved_titles") or s.get("expected_retrieved_titles") or [])[:max_titles],
        "summary_2": truncate(s.get("summary_2"), max_summary_chars),
        "expected_missing_or_weakened_support_titles": s.get("expected_missing_or_weakened_support_titles"),
        "expected_effect": s.get("expected_effect"),
        "is_semantic_endpoint": s.get("is_semantic_endpoint"),
        "is_actual_bm25_result": s.get("is_actual_bm25_result"),
    }


def compact_evidence_row(
    r: dict[str, Any],
    *,
    evidence_mode: str,
    max_prompt_chars: int,
    max_rationale_chars: int,
    max_summary_chars: int,
    max_titles: int,
) -> dict[str, Any]:
    base = {
        "case_id": r.get("case_id"),
        "bucket": r.get("bucket"),
        "transition_family": r.get("transition_family"),
        "direction_label": r.get("direction_label"),
        "polarity": r.get("polarity"),
        "question": r.get("question"),
        "delta_q": r.get("delta_q"),
        "samplewise_prompt_update": {
            "updated_prompt": truncate(r.get("samplewise_updated_prompt"), max_prompt_chars),
            "rationale": truncate(r.get("samplewise_prompt_rationale"), max_rationale_chars),
        },
    }

    if evidence_mode == "endpoint_delta":
        base["endpoint_contrast"] = {
            "source_R_role": r.get("source_R_role"),
            "target_R_role": r.get("target_R_role"),
            "source_R": compact_state(
                r.get("source_R"),
                max_titles=max_titles,
                max_summary_chars=max_summary_chars,
            ),
            "target_R": compact_state(
                r.get("target_R"),
                max_titles=max_titles,
                max_summary_chars=max_summary_chars,
            ),
            "delta_R_prime": r.get("delta_R_prime"),
            "matched_w_case_id": r.get("matched_w_case_id"),
        }

    return base


def make_user_payload(
    *,
    condition: str,
    current_prompt: str,
    rows: list[dict[str, Any]],
    max_prompt_chars: int,
    max_rationale_chars: int,
    max_summary_chars: int,
    max_titles: int,
) -> str:
    evidence_mode = condition_evidence_mode(condition)
    selected = sorted(select_rows(rows, condition), key=sort_key)

    evidence = [
        compact_evidence_row(
            r,
            evidence_mode=evidence_mode,
            max_prompt_chars=max_prompt_chars,
            max_rationale_chars=max_rationale_chars,
            max_summary_chars=max_summary_chars,
            max_titles=max_titles,
        )
        for r in selected
    ]

    payload = {
        "condition": condition,
        "evidence_mode": evidence_mode,
        "current_query_writer_prompt": current_prompt,
        "condition_semantics": {
            "base": "no update; keep current prompt",
            "neg_only": "use only W-side repair transitions",
            "custom_preserve": "use W-side repair plus C-side preserve/recovery transitions as positive constraints",
            "custom_signed": "use W-side repair plus C-side downhill/signed transitions as avoid constraints",
            "delta_p_only": "use samplewise prompt-update anchors only",
            "endpoint_delta": "use endpoint contrast plus samplewise prompt-update anchors",
        },
        "evidence_rows": evidence,
        "output_requirement": "Return one shared prompt for create_query_hop2.predict.",
    }

    return json.dumps(payload, ensure_ascii=False, indent=2)


def generate_condition_prompt(
    *,
    condition: str,
    current_prompt: str,
    rows: list[dict[str, Any]],
    model: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    max_prompt_chars: int,
    max_rationale_chars: int,
    max_summary_chars: int,
    max_titles: int,
) -> dict[str, Any]:
    selected = sorted(select_rows(rows, condition), key=sort_key)
    evidence_mode = condition_evidence_mode(condition)

    if condition == "base":
        return {
            "condition": condition,
            "evidence_mode": evidence_mode,
            "updated_prompt": current_prompt,
            "rationale": "Base condition; current fixed prompt is used unchanged.",
            "absorbed_patterns": [],
            "avoided_patterns": [],
            "raw": None,
            "n_evidence_rows": 0,
            "evidence_case_ids": [],
        }

    user = make_user_payload(
        condition=condition,
        current_prompt=current_prompt,
        rows=rows,
        max_prompt_chars=max_prompt_chars,
        max_rationale_chars=max_rationale_chars,
        max_summary_chars=max_summary_chars,
        max_titles=max_titles,
    )

    raw = call_model(
        model=model,
        system=BATCH_PROMPT_UPDATER_SYSTEM,
        user=user,
        temperature=temperature,
        max_tokens=max_tokens,
        retries=retries,
    )

    try:
        obj = extract_json_obj(raw)
        prompt = str(obj.get("updated_prompt") or "").strip()
        if not prompt:
            raise ValueError("empty updated_prompt")

        return {
            "condition": condition,
            "evidence_mode": evidence_mode,
            "updated_prompt": prompt,
            "rationale": obj.get("rationale", ""),
            "absorbed_patterns": obj.get("absorbed_patterns", []),
            "avoided_patterns": obj.get("avoided_patterns", []),
            "raw": raw,
            "parse_failed": False,
            "n_evidence_rows": len(selected),
            "evidence_case_ids": [r.get("case_id") for r in selected],
        }

    except Exception as e:
        fallback = current_prompt + "\n\nAdditional batch guidance: preserve answer-bearing entity/title anchors, retain required relation/type/qualifier cues, avoid noisy side-entity drift, and treat signed/downhill evidence as behavior to avoid. Output one compact BM25 query string."
        return {
            "condition": condition,
            "evidence_mode": evidence_mode,
            "updated_prompt": fallback,
            "rationale": f"JSON parse failed; fallback appended generic batch guidance. error={type(e).__name__}: {e}",
            "absorbed_patterns": [],
            "avoided_patterns": [],
            "raw": raw,
            "parse_failed": True,
            "n_evidence_rows": len(selected),
            "evidence_case_ids": [r.get("case_id") for r in selected],
        }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()

    ap.add_argument("--delta-qp", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_directional_delta_qp.jsonl"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/prompt_update/cache/fixed_prompt_config.json"))
    ap.add_argument("--out", type=Path, default=Path("experiments/prompt_update/results/positive_safety_b10_batch0_prompts.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/prompt_update/results/positive_safety_b10_batch0_prompts.summary.json"))

    ap.add_argument("--batch-id", type=int, default=0)
    ap.add_argument("--conditions", nargs="+", default=CONDITIONS)

    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-output-tokens", type=int, default=4096)
    ap.add_argument("--retries", type=int, default=4)

    ap.add_argument("--max-prompt-chars", type=int, default=1800)
    ap.add_argument("--max-rationale-chars", type=int, default=700)
    ap.add_argument("--max-summary-chars", type=int, default=550)
    ap.add_argument("--max-titles", type=int, default=7)

    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    rows = read_jsonl(args.delta_qp)
    fixed_cfg = read_json(args.fixed_prompt_config)
    current_prompt = fixed_cfg["prompt_candidate"]["prompts"]["create_query_hop2.predict"]

    for c in args.conditions:
        if c not in CONDITIONS:
            raise ValueError(f"unknown condition: {c}")

    if args.overwrite and args.out.exists():
        args.out.unlink()

    done = set()
    existing = []
    if args.out.exists():
        existing = read_jsonl(args.out)
        for r in existing:
            if not r.get("error"):
                done.add(r.get("condition"))

    print("[info] input delta_qp rows:", len(rows))
    print("[info] conditions:", args.conditions)
    print("[info] existing:", len(existing))

    result_rows = list(existing)

    for condition in tqdm(args.conditions, desc="batch prompt conditions"):
        if condition in done:
            continue

        try:
            row = generate_condition_prompt(
                condition=condition,
                current_prompt=current_prompt,
                rows=rows,
                model=args.model,
                temperature=args.temperature,
                max_tokens=args.max_output_tokens,
                retries=args.retries,
                max_prompt_chars=args.max_prompt_chars,
                max_rationale_chars=args.max_rationale_chars,
                max_summary_chars=args.max_summary_chars,
                max_titles=args.max_titles,
            )
            row.update({
                "row_type": "positive_safety_batch_prompt",
                "batch_id": args.batch_id,
                "model": args.model,
            })
        except Exception as e:
            row = {
                "row_type": "positive_safety_batch_prompt",
                "error": True,
                "batch_id": args.batch_id,
                "condition": condition,
                "model": args.model,
                "error_type": type(e).__name__,
                "error_message": str(e),
            }

        append_jsonl(args.out, row)
        result_rows.append(row)

    all_rows = read_jsonl(args.out)
    ok = [r for r in all_rows if not r.get("error")]
    err = [r for r in all_rows if r.get("error")]

    summary = {
        "script": "generate_positive_safety_batch_prompts.py",
        "delta_qp": str(args.delta_qp),
        "fixed_prompt_config": str(args.fixed_prompt_config),
        "out": str(args.out),
        "batch_id": args.batch_id,
        "n_rows": len(all_rows),
        "n_ok": len(ok),
        "n_error": len(err),
        "n_parse_failed": sum(bool(r.get("parse_failed")) for r in ok),
        "conditions": [
            {
                "condition": r.get("condition"),
                "evidence_mode": r.get("evidence_mode"),
                "n_evidence_rows": r.get("n_evidence_rows"),
                "evidence_case_ids": r.get("evidence_case_ids"),
                "parse_failed": r.get("parse_failed", False),
                "prompt_chars": len(str(r.get("updated_prompt") or "")),
                "error": r.get("error", False),
            }
            for r in all_rows
        ],
    }

    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps({
        "n_ok": summary["n_ok"],
        "n_error": summary["n_error"],
        "n_parse_failed": summary["n_parse_failed"],
        "conditions": summary["conditions"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
