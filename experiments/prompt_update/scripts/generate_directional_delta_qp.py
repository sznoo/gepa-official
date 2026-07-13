# /home/jinwoo/gepa-official/experiments/prompt_update/scripts/generate_directional_delta_qp.py
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


# Self-contained directional Δq/Δp generator.
#
# This file does NOT import run_delta_granularity_prompt_update.py.
# It only mirrors the old prompt-update interface:
#   current_prompt + delta_observations -> updated_prompt/rationale
#
# Input:
#   batch0_directional_transitions.jsonl
#
# Output:
#   one row per directional transition:
#     delta_q = source/target query pair
#     delta_p = samplewise updated prompt from the old-style updater prompt


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
        raise ValueError(f"could not find JSON object in: {text[:500]}")
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
    """Local OpenAI Responses API wrapper.

    Kept self-contained so this script does not depend on feedback_distance_v2 code.
    """
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


def state_compact(s: dict[str, Any], include_query: bool) -> dict[str, Any]:
    """Mirror old state_compact field names as closely as possible."""
    docs = s.get("retrieved_docs") or []

    out = {
        "state_id": s.get("state_id"),
        "kind": s.get("kind"),
        "retrieved_titles": s.get("retrieved_titles"),
        "support_recall_hop2": s.get("support_recall_hop2"),
        "missing_recovery_rate": s.get("missing_recovery_rate"),
        "summary_2": truncate(s.get("summary_2"), 900),
        "strong_answer": s.get("strong_answer"),
        "strong_score": s.get("strong_score"),
        "retrieved_doc_snippets": [truncate(d, 350) for d in docs[:7]],
    }

    if include_query:
        out["query"] = s.get("query")

    return out


def build_delta_items(states: list[dict[str, Any]], edge_pairs: list[tuple[int, int]], info_mode: str) -> list[dict[str, Any]]:
    """Mirror old build_delta_items: left_state/right_state delta observations."""
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
    """Mirror old make_prompt_update_user payload schema."""
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
    """Mirror old generate_updated_prompt without importing old code."""
    states = trace_row["trace"]
    delta_items = build_delta_items(states, arm["edge_pairs"], arm["info_mode"])

    user = make_prompt_update_user(
        current_prompt=current_prompt,
        trace_row=trace_row,
        arm=arm,
        delta_items=delta_items,
    )

    raw = call_model(
        model=model,
        system=PROMPT_UPDATER_SYSTEM,
        user=user,
        temperature=temperature,
        max_tokens=max_tokens,
        retries=retries,
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


def docs_to_old_format(state: dict[str, Any]) -> list[str]:
    """Convert actual or semantic endpoint docs into old list[str] doc snippets."""
    docs = state.get("retrieved_docs") or []
    out = []

    for d in docs[:7]:
        if isinstance(d, dict):
            title = str(d.get("title") or "")
            text = str(d.get("text") or "")
            out.append((title + "\n" + text).strip())
        else:
            out.append(str(d))

    # Generated R_C^- endpoints have expected titles, not actual BM25 docs.
    if not out and state.get("expected_retrieved_titles"):
        for t in state.get("expected_retrieved_titles")[:7]:
            out.append(f"EXPECTED_TITLE: {t}")

    return out


def support_recall_for_old_state(state: dict[str, Any]) -> Any:
    if state.get("support_recall_hop2") is not None:
        return state.get("support_recall_hop2")
    if state.get("support_recall_hop2_only") is not None:
        return state.get("support_recall_hop2_only")
    return state.get("support_recall_total")


def normalize_state_for_old_delta(
    *,
    state: dict[str, Any],
    state_id: str,
    kind: str,
) -> dict[str, Any]:
    """Convert directional endpoint schema into old trace-state schema."""
    titles = state.get("retrieved_titles") or state.get("expected_retrieved_titles") or []

    return {
        "state_id": state_id,
        "kind": kind,
        "query": state.get("query"),
        "retrieved_titles": titles,
        "retrieved_docs": docs_to_old_format(state),
        "summary_2": state.get("summary_2"),
        "support_recall_hop2": support_recall_for_old_state(state),
        "missing_recovery_rate": state.get("missing_recovery_rate"),
        "strong_answer": state.get("strong_answer"),
        "strong_score": state.get("strong_score"),
    }


def make_synthetic_trace_row(t: dict[str, Any]) -> dict[str, Any]:
    """Create the old trace_row shape from one directional transition."""
    source = {
        "question": t.get("question"),
        "summary_1": t.get("summary_1"),
        "gold_answer": t.get("gold_answer"),
        "gold_support_titles": t.get("gold_support_titles") or [],
        "missing_after_hop1": None,
        "missing_after_hop2": (
            t.get("source_R", {}).get("missing_titles_after_hop2")
            or t.get("target_R", {}).get("expected_missing_or_weakened_support_titles")
            or None
        ),
    }

    left = normalize_state_for_old_delta(
        state=t["source_R"],
        state_id=f"{t['transition_id']}:source",
        kind=t.get("source_R_role") or "source",
    )
    right = normalize_state_for_old_delta(
        state=t["target_R"],
        state_id=f"{t['transition_id']}:target",
        kind=t.get("target_R_role") or "target",
    )

    return {
        "idx": t.get("case_id"),
        "case_id": t.get("case_id"),
        "source_row": source,
        "trace": [left, right],
    }


def make_arm(t: dict[str, Any], info_mode: str) -> dict[str, Any]:
    """Single endpoint edge arm in old arm schema."""
    return {
        "arm_id": f"{t['transition_family']}_{info_mode}",
        "arm_family": "directional_endpoint",
        "info_mode": info_mode,
        "edge_pairs": [(0, 1)],
    }


def make_delta_q(t: dict[str, Any]) -> dict[str, Any]:
    """Directional query-pair material. Not an additive vector."""
    return {
        "source_query": t.get("source_R", {}).get("query"),
        "target_query": t.get("target_R", {}).get("query"),
        "direction_label": t.get("direction_label"),
        "polarity": t.get("polarity"),
    }


def run_one(task: tuple) -> dict[str, Any]:
    (
        transition,
        refs,
        model,
        temperature,
        updater_max_tokens,
        retries,
        info_mode,
    ) = task

    trace_row = make_synthetic_trace_row(transition)
    arm = make_arm(transition, info_mode)

    upd = generate_updated_prompt(
        model=model,
        temperature=temperature,
        max_tokens=updater_max_tokens,
        retries=retries,
        current_prompt=refs["current_query_prompt"],
        trace_row=trace_row,
        arm=arm,
    )

    return {
        "row_type": "directional_delta_qp",
        "transition_id": transition["transition_id"],
        "batch_id": transition.get("batch_id"),
        "case_id": transition.get("case_id"),
        "bucket": transition.get("bucket"),
        "transition_family": transition.get("transition_family"),
        "direction_label": transition.get("direction_label"),
        "polarity": transition.get("polarity"),
        "info_mode": info_mode,
        "arm_id": arm["arm_id"],
        "arm_family": arm["arm_family"],
        "edge_pairs": arm["edge_pairs"],

        "question": transition.get("question"),
        "summary_1": transition.get("summary_1"),
        "gold_answer": transition.get("gold_answer"),
        "gold_support_titles": transition.get("gold_support_titles") or [],

        "source_R_role": transition.get("source_R_role"),
        "target_R_role": transition.get("target_R_role"),
        "source_R": transition.get("source_R"),
        "target_R": transition.get("target_R"),
        "delta_R_prime": transition.get("delta_R_prime"),
        "matched_w_case_id": transition.get("matched_w_case_id"),

        "delta_q": make_delta_q(transition),
        "samplewise_updated_prompt": upd["updated_prompt"],
        "samplewise_prompt_rationale": upd.get("rationale"),
        "prompt_update_raw": upd.get("raw"),
        "parse_failed": upd.get("parse_failed", False),
    }


def run_one_safe(task: tuple) -> dict[str, Any]:
    transition = task[0]
    info_mode = task[-1]
    try:
        return run_one(task)
    except Exception as e:
        return {
            "row_type": "directional_delta_qp",
            "error": True,
            "transition_id": transition.get("transition_id"),
            "batch_id": transition.get("batch_id"),
            "case_id": transition.get("case_id"),
            "bucket": transition.get("bucket"),
            "transition_family": transition.get("transition_family"),
            "direction_label": transition.get("direction_label"),
            "polarity": transition.get("polarity"),
            "info_mode": info_mode,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()

    ap.add_argument("--directional-transitions", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_directional_transitions.jsonl"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/prompt_update/cache/fixed_prompt_config.json"))
    ap.add_argument("--out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_directional_delta_qp.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/prompt_update/cache/positive_safety/batch0_directional_delta_qp.summary.json"))

    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--updater-max-tokens", type=int, default=4096)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--num-threads", type=int, default=8)

    ap.add_argument("--info-mode", type=str, default="Rq", choices=["Rq", "R_only"])
    ap.add_argument("--overwrite", action="store_true")

    return ap.parse_args()


def main() -> None:
    args = parse_args()

    transitions = read_jsonl(args.directional_transitions)
    fixed_cfg = read_json(args.fixed_prompt_config)

    refs = {
        "current_query_prompt": fixed_cfg["prompt_candidate"]["prompts"]["create_query_hop2.predict"],
    }

    if args.overwrite and args.out.exists():
        args.out.unlink()

    done = set()
    existing_rows = []
    if args.out.exists():
        existing_rows = read_jsonl(args.out)
        for r in existing_rows:
            if not r.get("error"):
                done.add((r.get("transition_id"), r.get("info_mode")))

    tasks = []
    for t in transitions:
        key = (t.get("transition_id"), args.info_mode)
        if key in done:
            continue
        tasks.append((
            t,
            refs,
            args.model,
            args.temperature,
            args.updater_max_tokens,
            args.retries,
            args.info_mode,
        ))

    print("[info] directional transitions:", len(transitions))
    print("[info] pending:", len(tasks))
    print("[info] existing rows:", len(existing_rows))
    print("[info] info_mode:", args.info_mode)

    with cf.ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(run_one_safe, t) for t in tasks]
        for fut in tqdm(cf.as_completed(futs), total=len(futs), desc="directional delta_qp"):
            append_jsonl(args.out, fut.result())

    rows = read_jsonl(args.out)
    ok = [r for r in rows if not r.get("error")]
    err = [r for r in rows if r.get("error")]

    summary = {
        "script": "generate_directional_delta_qp.py",
        "directional_transitions": str(args.directional_transitions),
        "fixed_prompt_config": str(args.fixed_prompt_config),
        "out": str(args.out),
        "info_mode": args.info_mode,
        "n_rows": len(rows),
        "n_ok": len(ok),
        "n_error": len(err),
        "n_parse_failed": sum(bool(r.get("parse_failed")) for r in ok),
        "counts_by_bucket": {},
        "counts_by_transition_family": {},
        "counts_by_polarity": {},
        "rows": [
            {
                "transition_id": r.get("transition_id"),
                "case_id": r.get("case_id"),
                "bucket": r.get("bucket"),
                "transition_family": r.get("transition_family"),
                "polarity": r.get("polarity"),
                "info_mode": r.get("info_mode"),
                "parse_failed": r.get("parse_failed", False),
                "error": r.get("error", False),
            }
            for r in rows
        ],
    }

    for r in ok:
        summary["counts_by_bucket"][r["bucket"]] = summary["counts_by_bucket"].get(r["bucket"], 0) + 1
        summary["counts_by_transition_family"][r["transition_family"]] = summary["counts_by_transition_family"].get(r["transition_family"], 0) + 1
        summary["counts_by_polarity"][r["polarity"]] = summary["counts_by_polarity"].get(r["polarity"], 0) + 1

    write_json(args.summary_out, summary)

    print("[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps({
        "n_ok": summary["n_ok"],
        "n_error": summary["n_error"],
        "n_parse_failed": summary["n_parse_failed"],
        "counts_by_bucket": summary["counts_by_bucket"],
        "counts_by_transition_family": summary["counts_by_transition_family"],
        "counts_by_polarity": summary["counts_by_polarity"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
