# /home/jinwoo/gepa-official/experiments/prompt_update/scripts/generate_contrastive_raw_c_prompts.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

from tqdm import tqdm


# Generate paper-style raw-C contrastive controls:
#
#   delta_p_contrastive_raw_C
#   endpoint_delta_contrastive_raw_C
#
# Evidence:
#   W_retrieval repair rows
#   + raw successful C rows from C_clean/C_fragile
#
# Difference from custom_preserve/custom_signed:
#   No transported R_C^-.
#   No C-side synthetic transition.
#   C rows are used as successful current behavior to preserve.


CONDITIONS = [
    "delta_p_contrastive_raw_C",
    "endpoint_delta_contrastive_raw_C",
]


BATCH_PROMPT_UPDATER_SYSTEM = """You are generating one shared prompt for a HotpotQA second-hop BM25 query writer.

The target module receives:
- question
- summary_1

and must output one compact second-hop BM25 query string.

You are given contrastive batch-level evidence:
- W_repair rows: failed or weak retrieval behavior with samplewise prompt-update anchors.
- raw_C_success rows: nearby successful current retrieval/query behavior that should be preserved as a safety boundary.

Your task:
Write a single updated prompt for create_query_hop2.predict that improves W-side repair behavior while preserving the successful C-side behavior.

Important constraints:
- Output a prompt/instruction, not a query.
- The prompt must still ask for exactly one compact BM25 query string.
- W_repair rows should be converted into positive query-writing guidance.
- raw_C_success rows should be converted into preservation/safety constraints, not new target answers to hard-code.
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
  "absorbed_patterns": ["<short W-side repair pattern>", "..."],
  "preserved_patterns": ["<short C-side success boundary>", "..."],
  "avoided_patterns": ["<short anti-pattern>", "..."]
}
"""


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
            if attempt < retries:
                time.sleep(min(2 ** attempt, 8))

    raise RuntimeError(f"model call failed after {retries + 1} attempts: {last_err}")


def sort_key(r: dict[str, Any]) -> tuple:
    bucket_order = {
        "W_retrieval": 0,
        "C_fragile": 1,
        "C_clean": 2,
    }
    return (
        bucket_order.get(r.get("bucket"), 99),
        int(r.get("case_id") or 0),
        str(r.get("transition_family")),
    )


def select_w_repair(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        r for r in rows
        if not r.get("error")
        and r.get("transition_family") == "w_retrieval_repair"
    ]


def select_raw_c_success(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Use only preserve rows to get one raw success state per C case.

    C_clean preserve row:
      source_R = transported damaged
      target_R = current successful reference

    C_fragile preserve row:
      source_R = current fragile but answer-correct state
      target_R = oracle target

    Raw C success should use:
      C_clean   -> target_R
      C_fragile -> source_R
    """
    out = []
    seen = set()

    for r in rows:
        if r.get("error"):
            continue
        if r.get("bucket") not in {"C_clean", "C_fragile"}:
            continue
        fam = str(r.get("transition_family") or "")
        if not fam.endswith("_preserve"):
            continue

        cid = int(r["case_id"])
        if cid in seen:
            continue
        seen.add(cid)
        out.append(r)

    return out


def compact_state(s: dict[str, Any] | None, *, max_titles: int, max_summary_chars: int) -> dict[str, Any]:
    s = s or {}
    return {
        "query": s.get("query"),
        "retrieved_titles": (s.get("retrieved_titles") or s.get("expected_retrieved_titles") or [])[:max_titles],
        "summary_2": truncate(s.get("summary_2"), max_summary_chars),
        "support_recall_hop2": s.get("support_recall_hop2"),
        "missing_recovery_rate": s.get("missing_recovery_rate"),
        "strong_score": s.get("strong_score"),
    }


def raw_c_success_state(r: dict[str, Any]) -> dict[str, Any]:
    if r.get("bucket") == "C_clean":
        return r.get("target_R") or {}
    if r.get("bucket") == "C_fragile":
        return r.get("source_R") or {}
    return {}


def make_w_evidence(
    r: dict[str, Any],
    *,
    include_endpoint: bool,
    max_prompt_chars: int,
    max_rationale_chars: int,
    max_summary_chars: int,
    max_titles: int,
) -> dict[str, Any]:
    e = {
        "evidence_kind": "W_repair",
        "case_id": r.get("case_id"),
        "bucket": r.get("bucket"),
        "question": r.get("question"),
        "delta_q": r.get("delta_q"),
        "samplewise_prompt_update": {
            "updated_prompt": truncate(r.get("samplewise_updated_prompt"), max_prompt_chars),
            "rationale": truncate(r.get("samplewise_prompt_rationale"), max_rationale_chars),
        },
        "instructional_role": "absorb this repair behavior",
    }

    if include_endpoint:
        e["endpoint_contrast"] = {
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
        }

    return e


def make_c_evidence(
    r: dict[str, Any],
    *,
    include_endpoint: bool,
    max_summary_chars: int,
    max_titles: int,
) -> dict[str, Any]:
    st = raw_c_success_state(r)
    e = {
        "evidence_kind": "raw_C_success",
        "case_id": r.get("case_id"),
        "bucket": r.get("bucket"),
        "question": r.get("question"),
        "successful_query": st.get("query"),
        "successful_retrieved_titles": (st.get("retrieved_titles") or st.get("expected_retrieved_titles") or [])[:max_titles],
        "successful_summary_2": truncate(st.get("summary_2"), max_summary_chars),
        "instructional_role": "preserve this successful retrieval/query behavior as a safety boundary",
    }

    if include_endpoint:
        e["success_endpoint"] = compact_state(
            st,
            max_titles=max_titles,
            max_summary_chars=max_summary_chars,
        )

    return e


def make_user_payload(
    *,
    condition: str,
    current_prompt: str,
    rows: list[dict[str, Any]],
    max_prompt_chars: int,
    max_rationale_chars: int,
    max_summary_chars: int,
    max_titles: int,
) -> tuple[str, list[dict[str, Any]]]:
    include_endpoint = condition.startswith("endpoint_delta_")

    w_rows = sorted(select_w_repair(rows), key=sort_key)
    c_rows = sorted(select_raw_c_success(rows), key=sort_key)

    evidence = []
    for r in w_rows:
        evidence.append(make_w_evidence(
            r,
            include_endpoint=include_endpoint,
            max_prompt_chars=max_prompt_chars,
            max_rationale_chars=max_rationale_chars,
            max_summary_chars=max_summary_chars,
            max_titles=max_titles,
        ))
    for r in c_rows:
        evidence.append(make_c_evidence(
            r,
            include_endpoint=include_endpoint,
            max_summary_chars=max_summary_chars,
            max_titles=max_titles,
        ))

    payload = {
        "condition": condition,
        "evidence_mode": "contrastive_raw_C_endpoint" if include_endpoint else "contrastive_raw_C_delta_p",
        "current_query_writer_prompt": current_prompt,
        "condition_semantics": {
            "W_repair": "repair behavior to absorb",
            "raw_C_success": "nearby successful behavior to preserve; not a synthetic damaged transition",
            "C_success_definition": "C_clean + C_fragile only; W_other is excluded",
        },
        "evidence_rows": evidence,
        "output_requirement": "Return one shared prompt for create_query_hop2.predict.",
    }

    return json.dumps(payload, ensure_ascii=False, indent=2), evidence


def generate_prompt(
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
    user, evidence = make_user_payload(
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
            "evidence_mode": "contrastive_raw_C_endpoint" if condition.startswith("endpoint_delta_") else "contrastive_raw_C_delta_p",
            "updated_prompt": prompt,
            "rationale": obj.get("rationale", ""),
            "absorbed_patterns": obj.get("absorbed_patterns", []),
            "preserved_patterns": obj.get("preserved_patterns", []),
            "avoided_patterns": obj.get("avoided_patterns", []),
            "raw": raw,
            "parse_failed": False,
            "n_evidence_rows": len(evidence),
            "evidence_case_ids": [e.get("case_id") for e in evidence],
            "evidence_kinds": [e.get("evidence_kind") for e in evidence],
        }
    except Exception as e:
        fallback = current_prompt + "\n\nAdditional contrastive guidance: repair failed retrieval by preserving answer-bearing anchors and relation/type cues, while avoiding edits that would obscure the successful C-side query/retrieval behavior. Output one compact BM25 query string."
        return {
            "condition": condition,
            "evidence_mode": "contrastive_raw_C_endpoint" if condition.startswith("endpoint_delta_") else "contrastive_raw_C_delta_p",
            "updated_prompt": fallback,
            "rationale": f"JSON parse failed; fallback used. error={type(e).__name__}: {e}",
            "absorbed_patterns": [],
            "preserved_patterns": [],
            "avoided_patterns": [],
            "raw": raw,
            "parse_failed": True,
            "n_evidence_rows": len(evidence),
            "evidence_case_ids": [e.get("case_id") for e in evidence],
            "evidence_kinds": [e.get("evidence_kind") for e in evidence],
        }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-id", type=int, required=True)
    ap.add_argument("--delta-qp", type=Path, required=True)
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/prompt_update/cache/fixed_prompt_config.json"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--summary-out", type=Path, required=True)
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

    for c in args.conditions:
        if c not in CONDITIONS:
            raise ValueError(f"unknown condition: {c}")

    rows = read_jsonl(args.delta_qp)
    fixed_cfg = read_json(args.fixed_prompt_config)
    current_prompt = fixed_cfg["prompt_candidate"]["prompts"]["create_query_hop2.predict"]

    if args.overwrite and args.out.exists():
        args.out.unlink()

    existing = []
    done = set()
    if args.out.exists():
        # Resume only from successful rows. Drop stale error rows from previous quota/runtime failures.
        existing_all = read_jsonl(args.out)
        existing = [r for r in existing_all if not r.get("error")]
        for r in existing:
            done.add(r.get("condition"))

    print("[info] batch_id:", args.batch_id)
    print("[info] input rows:", len(rows))
    print("[info] conditions:", args.conditions)
    print("[info] existing:", len(existing))

    result_rows = list(existing)

    for condition in tqdm(args.conditions, desc="contrastive raw-C prompts"):
        if condition in done:
            continue

        try:
            row = generate_prompt(
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
                "row_type": "contrastive_raw_c_batch_prompt",
                "batch_id": args.batch_id,
                "model": args.model,
            })
        except Exception as e:
            row = {
                "row_type": "contrastive_raw_c_batch_prompt",
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
        "script": "generate_contrastive_raw_c_prompts.py",
        "batch_id": args.batch_id,
        "delta_qp": str(args.delta_qp),
        "out": str(args.out),
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
                "evidence_kinds": r.get("evidence_kinds"),
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
