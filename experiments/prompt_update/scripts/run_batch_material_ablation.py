#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import math
import random
import re
import sys
import traceback
from collections import defaultdict
from pathlib import Path
from typing import Any

from tqdm import tqdm


# ---------------------------------------------------------------------
# Import the existing delta-granularity script and reuse its tested pieces:
# - model calling
# - query parsing
# - query writer execution
# - BM25 retrieval + summarize2 + final-answer evaluation
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

DELTA_SCRIPT = ROOT / "experiments/feedback_distance_v2/scripts/run_delta_granularity_prompt_update.py"
spec = importlib.util.spec_from_file_location("delta_granularity", DELTA_SCRIPT)
delta = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(delta)


# ---------------------------------------------------------------------
# Override the imported base.call_model.
#
# The original feedback_distance_v2 code calls LiteLLM. In this environment
# LiteLLM fails with "model does not exist" even though the OpenAI SDK can
# list and access the model. To keep the experiment stable, route all model
# calls through the official OpenAI SDK while preserving the same call_model
# signature used by the existing scripts:
#
#   call_model(model, system, user, temperature, max_tokens, retries) -> str
#
# This override is applied to delta.base.call_model, so it is also used by
# reused functions such as run_query_writer() and evaluate_query().
# ---------------------------------------------------------------------

def _openai_sdk_call_model(
    model: str,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
    retries: int,
) -> str:
    import time
    from openai import OpenAI

    client = OpenAI()
    last_err = None

    # LiteLLM accepted "openai/<model>"; OpenAI SDK expects raw model ids.
    if model.startswith("openai/"):
        model = model.split("/", 1)[1]

    for attempt in range(retries + 1):
        try:
            # Prefer Responses API for current OpenAI models.
            kwargs = {
                "model": model,
                "input": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_output_tokens": max(16, int(max_tokens)),
            }

            # Some models only accept the default temperature. Try with
            # temperature first for compatibility with prior experiments.
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
            if text is not None:
                return str(text)

            # Fallback extraction for SDK variants.
            chunks = []
            for item in getattr(resp, "output", []) or []:
                for c in getattr(item, "content", []) or []:
                    t = getattr(c, "text", None)
                    if t:
                        chunks.append(str(t))
            if chunks:
                return "\n".join(chunks)

            return str(resp)

        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(min(2 ** attempt, 8))

    raise RuntimeError(f"OpenAI SDK model call failed after {retries + 1} attempts: {last_err}")


delta.base.call_model = _openai_sdk_call_model


# ---------------------------------------------------------------------
# Prompt: generate one shared batch-level create_query_hop2 instruction.
# This is intentionally batch-level; it does not output a query.
# ---------------------------------------------------------------------

BATCH_PROMPT_UPDATER_SYSTEM = """You are updating the prompt for a HotpotQA second-hop BM25 query generator.

The target module receives:
- question
- summary_1

and must output exactly one compact second-hop BM25 query.

Your task:
Given the current query-writer prompt and a minibatch of evidence, write ONE shared updated prompt for create_query_hop2.predict.

Important:
- Output a prompt/instruction, not a query.
- The updated prompt must be reusable across the minibatch, not a separate instruction per sample.
- Preserve compact BM25 query behavior.
- Prefer behavior-level edits over memorizing sample-specific answers.
- Do not introduce web-search syntax, Boolean programs, site:, or multiple-query instructions.
- Do not use downstream scores unless they are explicitly provided in the input. In this experiment, they are not provided.
- Keep the update conservative but useful for missing-support recovery.

Return strict JSON only:
{
  "updated_prompt": "<new shared prompt for create_query_hop2.predict>",
  "rationale": "<brief rationale for the shared update>"
}
"""


# ---------------------------------------------------------------------
# Prompt: semantic-magnitude selector for local feedback segments.
# Used only to choose which local segment is fed as evidence.
# It is not an outcome-based selector.
# ---------------------------------------------------------------------

MAGNITUDE_JUDGE_SYSTEM = """You are judging semantic magnitude between two local prompt-feedback updates.

Each candidate segment contains feedback for the HotpotQA second-hop query generator.
Select the segment whose feedback text represents the larger semantic update.

Here, feedback magnitude means how much the query-generation behavior would need to change:
- which entity/title/alias anchors to preserve, add, remove, or disambiguate
- which bridge relation, comparison relation, or task relation to emphasize
- which evidence family or answer type to target
- which distractors, wrong senses, or noisy entity families to avoid
- whether the candidate set should be broadened, narrowed, preserved, or re-centered
- what kind of retrieval failure the feedback corrects

Important:
- Judge the semantic difference magnitude of the feedback itself.
- Do not judge which feedback is more correct or likely to improve retrieval.
- Do not choose a segment merely because it is longer or more detailed.
- Do not choose a segment merely because it mentions source style, infoboxes, lead sentences, cast sections, table rows, or list parsing.
- Extra detail counts only if it changes the semantic instruction to the query generator.
- A full-edge feedback update should usually be larger than a local sub-edge feedback update if the decomposition is semantically consistent.
- Return "tie" only when the two feedback updates ask for materially similar semantic changes.

Return JSON only:
{
  "larger_segment": "A" | "B" | "tie",
  "segment_index": 0 | 1 | -1,
  "why_larger": "short explanation focused on semantic feedback magnitude",
  "dominant_gap_type": "anchor|bridge_relation|surface_form|noisy_entity|answer_type|query_shape|candidate_set|evidence_family|mixed|tie",
  "confidence": 0.0
}
"""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def trunc(x: Any, n: int) -> str:
    return delta.base.truncate(str(x or ""), n)


def stderr(vals: list[float]) -> float | None:
    if not vals:
        return None
    if len(vals) == 1:
        return 0.0
    m = sum(vals) / len(vals)
    var = sum((v - m) ** 2 for v in vals) / (len(vals) - 1)
    return math.sqrt(var) / math.sqrt(len(vals))


def mean(vals: list[float]) -> float | None:
    return sum(vals) / len(vals) if vals else None


def exact_arm_edge_index(arm_id: str) -> int | None:
    m = re.match(r"edge_(\d+)_Rq$", str(arm_id))
    return int(m.group(1)) if m else None


def compact_state(s: dict[str, Any]) -> dict[str, Any]:
    """Compact one retrieval state so batch prompts do not explode."""
    docs = s.get("retrieved_docs") or []
    return {
        "state_id": s.get("state_id"),
        "kind": s.get("kind"),
        "query": s.get("query"),
        "retrieved_titles": s.get("retrieved_titles"),
        "support_recall_hop2": s.get("support_recall_hop2"),
        "missing_recovery_rate": s.get("missing_recovery_rate"),
        "summary_2": trunc(s.get("summary_2"), 500),
        "retrieved_doc_snippets": [trunc(d, 240) for d in docs[:3]],
    }


def compact_transition(trace_row: dict[str, Any], edge_index: int, trace_mode: str) -> Any:
    """Return selected local edge or full adjacent trace."""
    states = trace_row["trace"]

    if trace_mode == "full_trace":
        return [
            {
                "edge_index": i,
                "left_state": compact_state(states[i]),
                "right_state": compact_state(states[i + 1]),
            }
            for i in range(len(states) - 1)
        ]

    i = max(0, min(edge_index, len(states) - 2))
    return {
        "edge_index": i,
        "left_state": compact_state(states[i]),
        "right_state": compact_state(states[i + 1]),
    }


def make_batches(n: int, batch_size: int, num_batches: int, seed: int) -> list[list[int]]:
    """Use disjoint random batches when possible."""
    rng = random.Random(seed)
    ids = list(range(n))
    rng.shuffle(ids)

    need = batch_size * num_batches
    if need <= n:
        return [
            ids[i * batch_size : (i + 1) * batch_size]
            for i in range(num_batches)
        ]

    return [rng.sample(range(n), batch_size) for _ in range(num_batches)]


def load_samplewise_rows(path: Path) -> dict[int, list[dict[str, Any]]]:
    """Load successful edge_i_Rq rows as samplewise delta-p candidates."""
    rows = read_jsonl(path)
    by_case: dict[int, list[dict[str, Any]]] = defaultdict(list)

    for r in rows:
        if r.get("error"):
            continue
        arm_id = str(r.get("arm_id", ""))
        edge_index = r.get("edge_index")
        if edge_index is None:
            edge_index = exact_arm_edge_index(arm_id)
        if edge_index is None:
            continue
        if not arm_id.startswith("edge_") or not arm_id.endswith("_Rq"):
            continue
        if not str(r.get("updated_prompt", "")).strip():
            continue

        rr = dict(r)
        rr["edge_index"] = int(edge_index)
        by_case[int(r["case_id"])].append(rr)

    for cid in by_case:
        by_case[cid].sort(key=lambda x: int(x["edge_index"]))

    return by_case


def magnitude_compare(
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    question: str,
    summary_1: str,
    seg_a: dict[str, Any],
    seg_b: dict[str, Any],
) -> dict[str, Any]:
    segments = [
        {
            "segment_index": 0,
            "arm_id": seg_a.get("arm_id"),
            "edge_index": seg_a.get("edge_index"),
            "feedback_text": seg_a.get("prompt_update_rationale", ""),
            "updated_prompt_excerpt": trunc(seg_a.get("updated_prompt"), 900),
        },
        {
            "segment_index": 1,
            "arm_id": seg_b.get("arm_id"),
            "edge_index": seg_b.get("edge_index"),
            "feedback_text": seg_b.get("prompt_update_rationale", ""),
            "updated_prompt_excerpt": trunc(seg_b.get("updated_prompt"), 900),
        },
    ]

    user = f"""Question:
{question}

summary_1:
{summary_1}

Candidate feedback segments:
{json.dumps(segments, ensure_ascii=False, indent=2)}
"""
    raw = delta.base.call_model(
        model,
        MAGNITUDE_JUDGE_SYSTEM,
        user,
        temperature,
        max_tokens,
        retries,
    )

    obj = delta.extract_json_obj(raw)
    obj["raw"] = raw
    return obj


def select_samplewise_delta_p(
    *,
    case_id: int,
    trace_row: dict[str, Any],
    candidates: list[dict[str, Any]],
    selection: str,
    model: str,
    temperature: float,
    selector_max_tokens: int,
    retries: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Select one samplewise delta-p row per case.

    semantic selection uses pairwise magnitude judging over feedback/rationale,
    not downstream MR/EM.
    """
    if not candidates:
        raise ValueError(f"No samplewise delta-p candidates for case_id={case_id}")

    if selection == "edge0":
        return candidates[0], []

    if selection == "edge1":
        return candidates[1] if len(candidates) > 1 else candidates[0], []

    if selection != "semantic":
        raise ValueError(f"unknown selection: {selection}")

    source = trace_row["source_row"]
    winner = candidates[0]
    logs = []

    for challenger in candidates[1:]:
        verdict = magnitude_compare(
            model=model,
            temperature=temperature,
            max_tokens=selector_max_tokens,
            retries=retries,
            question=str(source.get("question") or ""),
            summary_1=str(source.get("summary_1") or ""),
            seg_a=winner,
            seg_b=challenger,
        )
        larger = verdict.get("larger_segment")
        if larger == "B" or verdict.get("segment_index") == 1:
            new_winner = challenger
        else:
            new_winner = winner

        logs.append({
            "case_id": case_id,
            "winner_before": winner.get("arm_id"),
            "challenger": challenger.get("arm_id"),
            "winner_after": new_winner.get("arm_id"),
            "verdict": verdict,
        })
        winner = new_winner

    return winner, logs


def make_batch_evidence(
    *,
    arm_id: str,
    batch_case_ids: list[int],
    trace_rows: list[dict[str, Any]],
    selected_delta_p: dict[int, dict[str, Any]],
    trace_mode: str,
) -> list[dict[str, Any]]:
    evidence = []

    for cid in batch_case_ids:
        tr = trace_rows[cid]
        source = tr["source_row"]
        dp = selected_delta_p[cid]
        edge_index = int(dp.get("edge_index", 0))

        item: dict[str, Any] = {
            "case_id": cid,
            "question": source.get("question"),
            "summary_1": trunc(source.get("summary_1"), 1400),
            "current_query": source.get("current_query"),
            "missing_after_hop1": source.get("missing_after_hop1"),
            "missing_after_hop2": source.get("missing_after_hop2"),
        }

        if arm_id in {"raw_trace_only", "raw_trace_plus_delta_p"}:
            item["retrieval_query_transition_trace"] = compact_transition(
                tr,
                edge_index=edge_index,
                trace_mode=trace_mode,
            )

        if arm_id in {"delta_p_only", "raw_trace_plus_delta_p"}:
            item["samplewise_prompt_update"] = {
                "source_arm_id": dp.get("arm_id"),
                "source_edge_index": dp.get("edge_index"),
                "updated_prompt": dp.get("updated_prompt"),
                "rationale": dp.get("prompt_update_rationale"),
            }

        evidence.append(item)

    return evidence


def generate_batch_prompt(
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    current_prompt: str,
    arm_id: str,
    batch_id: int,
    batch_case_ids: list[int],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = {
        "experiment": "batch_prompt_update_material_ablation",
        "arm_id": arm_id,
        "batch_id": batch_id,
        "batch_case_ids": batch_case_ids,
        "current_query_writer_prompt": current_prompt,
        "batch_evidence": evidence,
    }

    raw = delta.base.call_model(
        model,
        BATCH_PROMPT_UPDATER_SYSTEM,
        json.dumps(payload, ensure_ascii=False, indent=2),
        temperature,
        max_tokens,
        retries,
    )

    obj = delta.extract_json_obj(raw)
    updated_prompt = str(obj.get("updated_prompt") or "").strip()
    if not updated_prompt:
        raise ValueError("empty updated_prompt from batch updater")

    return {
        "updated_prompt": updated_prompt,
        "rationale": obj.get("rationale", ""),
        "raw": raw,
    }


def eval_one_case(task: tuple) -> dict[str, Any]:
    (
        case_id,
        trace_row,
        prompt,
        refs,
        model,
        temperature,
        query_max_tokens,
        summary_max_tokens,
        answer_max_tokens,
        retries,
        k,
    ) = task

    try:
        source = trace_row["source_row"]
        q = delta.run_query_writer(
            model=model,
            prompt=prompt,
            question=str(source.get("question") or ""),
            summary_1=str(source.get("summary_1") or ""),
            temperature=temperature,
            max_tokens=query_max_tokens,
            retries=retries,
        )
        ev = delta.evaluate_query(
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
            "question": source.get("question"),
            "gold_answer": source.get("gold_answer"),
            "generated_query": q["query"],
            "query_raw": q["raw"],
            **ev,
        }
    except Exception as e:
        return {
            "error": True,
            "case_id": case_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        }


def evaluate_prompt(
    *,
    prompt: str,
    trace_rows: list[dict[str, Any]],
    case_ids: list[int],
    refs: dict[str, Any],
    model: str,
    temperature: float,
    query_max_tokens: int,
    summary_max_tokens: int,
    answer_max_tokens: int,
    retries: int,
    k: int,
    num_threads: int,
) -> list[dict[str, Any]]:
    tasks = [
        (
            cid,
            trace_rows[cid],
            prompt,
            refs,
            model,
            temperature,
            query_max_tokens,
            summary_max_tokens,
            answer_max_tokens,
            retries,
            k,
        )
        for cid in case_ids
    ]

    rows = []
    with cf.ThreadPoolExecutor(max_workers=num_threads) as ex:
        futs = [ex.submit(eval_one_case, t) for t in tasks]
        for fut in tqdm(cf.as_completed(futs), total=len(futs), desc="eval", leave=False):
            rows.append(fut.result())

    rows.sort(key=lambda r: int(r.get("case_id", -1)))
    return rows


def current_rows_from_traces(trace_rows: list[dict[str, Any]], case_ids: list[int]) -> list[dict[str, Any]]:
    all_current = delta.baseline_rows_from_traces(trace_rows, "current")
    keep = set(case_ids)
    return [r for r in all_current if int(r["case_id"]) in keep]


def summarize_eval_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in rows if not r.get("error")]
    return {
        "n": len(ok),
        "n_error": len(rows) - len(ok),
        "mean_mr": delta.mean(ok, "missing_recovery_rate"),
        "mean_support_recall_hop2": delta.mean(ok, "support_recall_hop2"),
        "base_em": delta.mean_bool(ok, "base_score"),
        "strong_em": delta.mean_bool(ok, "strong_score"),
        "strong_correct": sum(bool(r.get("strong_score")) for r in ok),
        "base_correct": sum(bool(r.get("base_score")) for r in ok),
    }


def add_delta(summary: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    out = dict(summary)
    for key, delta_key in [
        ("mean_mr", "delta_mr_vs_current"),
        ("strong_em", "delta_strong_em_vs_current"),
        ("base_em", "delta_base_em_vs_current"),
        ("mean_support_recall_hop2", "delta_support_recall_vs_current"),
    ]:
        a = out.get(key)
        b = current.get(key)
        out[delta_key] = None if a is None or b is None else float(a) - float(b)
    return out


def aggregate_over_batches(per_batch: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate per-batch summaries into mean ± stderr."""
    out: dict[str, Any] = {}
    scopes = sorted({r["eval_scope"] for r in per_batch})
    arms = sorted({r["arm_id"] for r in per_batch})

    metrics = [
        "mean_mr",
        "strong_em",
        "base_em",
        "mean_support_recall_hop2",
        "delta_mr_vs_current",
        "delta_strong_em_vs_current",
    ]

    for scope in scopes:
        out[scope] = {}
        for arm in arms:
            rows = [r for r in per_batch if r["eval_scope"] == scope and r["arm_id"] == arm]
            out[scope][arm] = {"n_batches": len(rows)}
            for m in metrics:
                vals = [float(r[m]) for r in rows if r.get(m) is not None]
                out[scope][arm][m + "_mean"] = mean(vals)
                out[scope][arm][m + "_stderr"] = stderr(vals)

    return out


def parse_args():
    ap = argparse.ArgumentParser()

    ap.add_argument("--traces", type=Path, default=Path("experiments/prompt_update/traces/gpt/rtrace_midpoint_validity_v2_traces_hit48.jsonl"))
    ap.add_argument("--samplewise-eval", type=Path, default=Path("experiments/prompt_update/results_reference/gpt/delta_granularity_prompt_update_eval_genbias_single_rq_hit48.jsonl"))
    ap.add_argument("--fixed-prompt-config", type=Path, default=Path("experiments/prompt_update/cache/fixed_prompt_config.json"))
    ap.add_argument("--final-answerer-refs", type=Path, default=Path("experiments/prompt_update/cache/final_answerer_refs.json"))

    ap.add_argument("--out", type=Path, default=Path("experiments/prompt_update/results/batch_material_ablation_eval.jsonl"))
    ap.add_argument("--summary-out", type=Path, default=Path("experiments/prompt_update/results/batch_material_ablation_summary.json"))

    ap.add_argument("--retriever-dir", type=Path, default=Path("examples/hotpotqa"))
    ap.add_argument("--k", type=int, default=7)

    ap.add_argument("--model", type=str, default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--updater-max-tokens", type=int, default=4096)
    ap.add_argument("--selector-max-tokens", type=int, default=1024)
    ap.add_argument("--query-max-tokens", type=int, default=512)
    ap.add_argument("--summary-max-tokens", type=int, default=4096)
    ap.add_argument("--answer-max-tokens", type=int, default=2048)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--num-threads", type=int, default=8)

    ap.add_argument("--batch-size", type=int, default=6)
    ap.add_argument("--num-batches", type=int, default=3)
    ap.add_argument("--batch-seed", type=int, default=0)
    ap.add_argument(
        "--fixed-batches-json",
        type=str,
        default=None,
        help="Optional explicit batch list, e.g. '[[1,33,36,0,20,23],[14,12,7,28,44,47]]'. Overrides random batch sampling.",
    )

    ap.add_argument(
        "--selection",
        choices=["semantic", "edge0", "edge1"],
        default="semantic",
        help="How to select one samplewise delta-p / trace segment per case.",
    )
    ap.add_argument(
        "--trace-mode",
        choices=["selected_segment", "full_trace", "endpoints", "selected_plus_endpoints"],
        default="selected_segment",
        help="Trace evidence used by raw_trace arms.",
    )
    ap.add_argument(
        "--arms",
        nargs="+",
        default=["current_fixed_prompt", "delta_p_only", "raw_trace_only", "raw_trace_plus_delta_p"],
        choices=["current_fixed_prompt", "delta_p_only", "raw_trace_only", "raw_trace_plus_delta_p"],
    )
    ap.add_argument("--overwrite", action="store_true")

    return ap.parse_args()


def main():
    args = parse_args()

    delta.base.set_retriever_dir(str(args.retriever_dir))

    trace_rows = read_jsonl(args.traces)
    samplewise_by_case = load_samplewise_rows(args.samplewise_eval)

    fixed_cfg = read_json(args.fixed_prompt_config)
    final_refs = read_json(args.final_answerer_refs)
    refs = {
        **final_refs,
        "summarize2_prompt": fixed_cfg["prompt_candidate"]["prompts"]["summarize2.predict"],
        "current_query_prompt": fixed_cfg["prompt_candidate"]["prompts"]["create_query_hop2.predict"],
    }
    current_prompt = refs["current_query_prompt"]

    if args.overwrite:
        for p in [args.out, args.summary_out]:
            if p.exists():
                p.unlink()

    if args.fixed_batches_json:
        batches = json.loads(args.fixed_batches_json)
        batches = [[int(x) for x in b] for b in batches]
        if any(len(b) != args.batch_size for b in batches):
            raise ValueError(f"All fixed batches must have batch_size={args.batch_size}: {batches}")
        args.num_batches = len(batches)
    else:
        batches = make_batches(
            n=len(trace_rows),
            batch_size=args.batch_size,
            num_batches=args.num_batches,
            seed=args.batch_seed,
        )

    full_case_ids = list(range(len(trace_rows)))

    print(f"[info] traces: {len(trace_rows)}")
    print(f"[info] batch_size={args.batch_size}, num_batches={args.num_batches}, seed={args.batch_seed}")
    print(f"[info] arms={args.arms}")
    print(f"[info] selection={args.selection}, trace_mode={args.trace_mode}")

    per_batch_summaries = []
    prompt_records = []

    # Baseline current rows are derived from existing trace state R0.
    current_full_rows = current_rows_from_traces(trace_rows, full_case_ids)
    current_full_summary = summarize_eval_rows(current_full_rows)

    for batch_id, batch_case_ids in enumerate(batches):
        print(f"\n[batch {batch_id}] cases={batch_case_ids}")

        selected_delta_p: dict[int, dict[str, Any]] = {}
        selector_logs = []

        for cid in batch_case_ids:
            selected, logs = select_samplewise_delta_p(
                case_id=cid,
                trace_row=trace_rows[cid],
                candidates=samplewise_by_case.get(cid, []),
                selection=args.selection,
                model=args.model,
                temperature=args.temperature,
                selector_max_tokens=args.selector_max_tokens,
                retries=args.retries,
            )
            selected_delta_p[cid] = selected
            selector_logs.extend(logs)

        for log in selector_logs:
            append_jsonl(args.out, {
                "row_type": "selector",
                "batch_id": batch_id,
                **log,
            })

        current_batch_rows = current_rows_from_traces(trace_rows, batch_case_ids)
        current_batch_summary = summarize_eval_rows(current_batch_rows)

        if "current_fixed_prompt" in args.arms:
            for scope, rows, cur in [
                ("batch", current_batch_rows, current_batch_summary),
                ("full48", current_full_rows, current_full_summary),
            ]:
                s = add_delta(summarize_eval_rows(rows), cur)
                record = {
                    "batch_id": batch_id,
                    "arm_id": "current_fixed_prompt",
                    "eval_scope": scope,
                    **s,
                }
                per_batch_summaries.append(record)
                append_jsonl(args.out, {"row_type": "summary", **record})

        for arm_id in [a for a in args.arms if a != "current_fixed_prompt"]:
            evidence = make_batch_evidence(
                arm_id=arm_id,
                batch_case_ids=batch_case_ids,
                trace_rows=trace_rows,
                selected_delta_p=selected_delta_p,
                trace_mode=args.trace_mode,
            )

            upd = generate_batch_prompt(
                model=args.model,
                temperature=args.temperature,
                max_tokens=args.updater_max_tokens,
                retries=args.retries,
                current_prompt=current_prompt,
                arm_id=arm_id,
                batch_id=batch_id,
                batch_case_ids=batch_case_ids,
                evidence=evidence,
            )

            prompt_record = {
                "row_type": "prompt",
                "batch_id": batch_id,
                "arm_id": arm_id,
                "batch_case_ids": batch_case_ids,
                "updated_prompt": upd["updated_prompt"],
                "prompt_update_rationale": upd.get("rationale"),
                "prompt_update_raw": upd.get("raw"),
                "selection": args.selection,
                "trace_mode": args.trace_mode,
                "selected_samplewise": {
                    str(cid): {
                        "arm_id": selected_delta_p[cid].get("arm_id"),
                        "edge_index": selected_delta_p[cid].get("edge_index"),
                    }
                    for cid in batch_case_ids
                },
            }
            prompt_records.append(prompt_record)
            append_jsonl(args.out, prompt_record)

            # Evaluate once on full48; batch metrics are derived as a subset.
            full_rows = evaluate_prompt(
                prompt=upd["updated_prompt"],
                trace_rows=trace_rows,
                case_ids=full_case_ids,
                refs=refs,
                model=args.model,
                temperature=args.temperature,
                query_max_tokens=args.query_max_tokens,
                summary_max_tokens=args.summary_max_tokens,
                answer_max_tokens=args.answer_max_tokens,
                retries=args.retries,
                k=args.k,
                num_threads=args.num_threads,
            )

            for r in full_rows:
                append_jsonl(args.out, {
                    "row_type": "eval",
                    "batch_id": batch_id,
                    "arm_id": arm_id,
                    "eval_scope_source": "full48",
                    **r,
                })

            batch_set = set(batch_case_ids)
            batch_rows = [r for r in full_rows if int(r.get("case_id", -1)) in batch_set]

            for scope, rows, cur in [
                ("batch", batch_rows, current_batch_summary),
                ("full48", full_rows, current_full_summary),
            ]:
                s = add_delta(summarize_eval_rows(rows), cur)
                record = {
                    "batch_id": batch_id,
                    "arm_id": arm_id,
                    "eval_scope": scope,
                    **s,
                }
                per_batch_summaries.append(record)
                append_jsonl(args.out, {"row_type": "summary", **record})

    summary = {
        "experiment": "Experiment-Batch Prompt Update Material Ablation",
        "config": {
            "model": args.model,
            "temperature": args.temperature,
            "batch_size": args.batch_size,
            "num_batches": args.num_batches,
            "batch_seed": args.batch_seed,
            "selection": args.selection,
            "trace_mode": args.trace_mode,
            "arms": args.arms,
            "traces": str(args.traces),
            "samplewise_eval": str(args.samplewise_eval),
            "retriever_dir": str(args.retriever_dir),
            "k": args.k,
        },
        "batches": {
            str(i): batch for i, batch in enumerate(batches)
        },
        "per_batch": per_batch_summaries,
        "aggregate": aggregate_over_batches(per_batch_summaries),
        "prompt_records": prompt_records,
        "out": str(args.out),
    }

    write_json(args.summary_out, summary)

    print("\n[wrote]", args.out)
    print("[wrote]", args.summary_out)
    print(json.dumps(summary["aggregate"], ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------
# Case 1 trace-context ablation override.
#
# Adds two trace modes:
#   endpoints:
#       R0 + R* + samplewise Δp
#   selected_plus_endpoints:
#       R0 + selected local transition + R* + samplewise Δp
#
# We keep the existing arm name raw_trace_plus_delta_p so the rest of the
# evaluation pipeline is unchanged. Only the evidence text changes.
# ---------------------------------------------------------------------

_ORIG_MAKE_BATCH_EVIDENCE_CASE1 = make_batch_evidence


def _case1_get_arg(bound, names, default=None):
    for n in names:
        if n in bound.arguments:
            return bound.arguments[n]
    return default


def _case1_state_text(state, label=None):
    if state is None:
        return "None"

    sid = state.get("state_id") or state.get("id") or label or "state"
    kind = state.get("kind")
    query = state.get("query")
    titles = state.get("retrieved_titles") or []
    summary = state.get("summary_2") or state.get("summary") or ""
    sr = state.get("support_recall_hop2")
    mr = state.get("missing_recovery_rate")

    parts = []
    parts.append(f"{sid}" + (f" ({kind})" if kind else ""))
    if query:
        parts.append(f"query: {query}")
    if titles:
        parts.append("retrieved_titles: " + "; ".join(map(str, titles[:10])))
    if sr is not None or mr is not None:
        parts.append(f"support_recall_hop2={sr}, missing_recovery_rate={mr}")
    if summary:
        parts.append("summary_2: " + str(summary)[:1800])
    return "\n".join(parts)


def _case1_transition_text(trace, edge_index):
    i = int(edge_index)
    if i < 0:
        i = 0
    if i >= len(trace) - 1:
        i = max(0, len(trace) - 2)

    left = trace[i]
    right = trace[i + 1]

    return (
        f"LOCAL TRANSITION edge_index={i}\n"
        f"[FROM]\n{_case1_state_text(left, label=f'R{i}')}\n\n"
        f"[TO]\n{_case1_state_text(right, label=f'R{i+1}')}"
    )


def _case1_selected_edge_index(sel):
    if not isinstance(sel, dict):
        return 0

    for k in ["segment_index", "edge_index", "selected_edge_index", "trace_edge_index"]:
        if k in sel and sel[k] is not None:
            try:
                return int(sel[k])
            except Exception:
                pass

    arm = str(sel.get("arm_id") or sel.get("selected_arm_id") or "")
    # Common pattern: edge_2_Rq
    import re
    m = re.search(r"edge[_-](\d+)", arm)
    if m:
        return int(m.group(1))

    return 0


def _case1_delta_p_text(sel):
    if not isinstance(sel, dict):
        return "No samplewise Δp selected."

    rationale = sel.get("prompt_update_rationale") or sel.get("rationale") or ""
    updated = sel.get("updated_prompt") or sel.get("prompt") or ""
    arm = sel.get("arm_id") or ""

    return (
        f"selected_samplewise_arm: {arm}\n"
        f"samplewise_rationale: {rationale}\n\n"
        f"samplewise_updated_prompt:\n{updated}"
    )


def make_batch_evidence(*args, **kwargs):
    import inspect

    sig = inspect.signature(_ORIG_MAKE_BATCH_EVIDENCE_CASE1)
    bound = sig.bind_partial(*args, **kwargs)

    trace_mode = _case1_get_arg(bound, ["trace_mode"], None)
    arm_id = _case1_get_arg(bound, ["arm_id", "arm"], None)

    if trace_mode not in {"endpoints", "selected_plus_endpoints"}:
        return _ORIG_MAKE_BATCH_EVIDENCE_CASE1(*args, **kwargs)

    # These names cover the current script's expected arguments.
    case_ids = _case1_get_arg(
        bound,
        ["case_ids", "batch_case_ids", "batch_ids", "batch"],
        None,
    )
    trace_rows = _case1_get_arg(
        bound,
        ["trace_rows", "traces", "rows"],
        None,
    )
    selected = _case1_get_arg(
        bound,
        ["selected_samplewise", "selected", "selected_by_case", "selected_map"],
        {},
    )

    if case_ids is None or trace_rows is None:
        raise RuntimeError(
            "Case1 make_batch_evidence override could not infer argument names. "
            f"Original signature: {sig}; bound args: {list(bound.arguments.keys())}"
        )

    blocks = []
    blocks.append(f"ARM: {arm_id}")
    blocks.append(f"TRACE_MODE: {trace_mode}")
    blocks.append(
        "Goal: generate one shared create_query_hop2 prompt update from batch evidence. "
        "Use the retrieval-state evidence as context and the samplewise Δp as an update-direction anchor."
    )

    for local_j, cid in enumerate(case_ids):
        cid_int = int(cid)
        row = trace_rows[cid_int]
        trace = row.get("trace") or []
        if len(trace) < 2:
            continue

        if isinstance(selected, dict):
            sel = selected.get(cid_int, selected.get(str(cid_int), {}))
        else:
            sel = {}

        edge_i = _case1_selected_edge_index(sel)
        r0 = trace[0]
        rstar = trace[-1]

        q = row.get("question") or row.get("source_row", {}).get("question") or ""
        ans = row.get("gold_answer") or row.get("source_row", {}).get("gold_answer") or ""

        parts = []
        parts.append("=" * 80)
        parts.append(f"CASE {local_j} / case_id={cid_int}")
        if q:
            parts.append(f"question: {q}")
        if ans:
            parts.append(f"gold_answer: {ans}")

        parts.append("\n[ENDPOINT: CURRENT R0]\n" + _case1_state_text(r0, label="R0"))

        if trace_mode == "selected_plus_endpoints":
            parts.append("\n[SELECTED LOCAL TRANSITION]\n" + _case1_transition_text(trace, edge_i))

        parts.append("\n[ENDPOINT: TARGET R*]\n" + _case1_state_text(rstar, label="R_star"))

        parts.append("\n[SAMPLEWISE Δp ANCHOR]\n" + _case1_delta_p_text(sel))

        blocks.append("\n".join(parts))

    return "\n\n".join(blocks)





if __name__ == "__main__":
    main()
