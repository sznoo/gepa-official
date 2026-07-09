import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import dspy
from tqdm import tqdm

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

import run_biggest_step_rtrace_decomposition as br


def safe_float(x):
    try:
        return float(x or 0)
    except Exception:
        return 0.0


def read_jsonl(p):
    return br.read_jsonl(p)


def write_jsonl(p, rows):
    return br.write_jsonl(p, rows)


def fmt_pgrad_list(pgrads):
    return "\n\n".join([
        f"STEP {x.get('step')} PROMPT_GRADIENT ({x.get('from')} -> {x.get('to')}):\n{x.get('pgrad', '')}"
        for x in pgrads
    ])


def compact_state(s):
    return br.compact_state_for_prompt(s)


def pick_iteration(aux, trace_steps):
    its = aux.get("iterations") or []
    for it in its:
        if int(it.get("num_edges", -1)) == trace_steps:
            return it
    # fallback: closest smaller, then largest
    candidates = [it for it in its if int(it.get("num_edges", -1)) <= trace_steps]
    if candidates:
        return sorted(candidates, key=lambda x: int(x.get("num_edges", -1)))[-1]
    if its:
        return sorted(its, key=lambda x: int(x.get("num_edges", -1)))[-1]
    return None


def prompt_context_delta(question, summary_1, left, right, step_idx):
    return f"""
Convert one adjacent retrieval-state transition into a local CONTEXT-DELTA descriptor.

This is not a query and not a prompt-gradient. It describes how the retrieval context should change from R_left toward R_right.

Output exactly these fields:
TRIGGER:
KEEP_CONTEXT:
SHIFT_CONTEXT_TO:
ADD_CONTEXT_CUES:
DROP_CONTEXT_CUES:
QUERY_IMPLICATION:
WHY_THIS_CONTEXT_DELTA_HELPS:

Rules:
- Preserve local step order.
- Focus on retrieval context movement, not final answer wording.
- Use BM25-relevant anchors, bridge relations, type/alias/date clues, and noisy entity removal.
- Do not mention gold labels, hidden metrics, or missing support titles.
- Do not output a final query.

Step index: {step_idx}

Question:
{question}

summary_1:
{summary_1}

R_left:
{br.compact_json(compact_state(left))}

R_right:
{br.compact_json(compact_state(right))}
""".strip()


def make_context_delta_listing(args, question, summary_1, states):
    deltas = []
    for i in range(len(states) - 1):
        out = br.call_lm(prompt_context_delta(question, summary_1, states[i], states[i + 1], i), args.retries)
        deltas.append({
            "step": i,
            "from": states[i].get("name", f"R{i}"),
            "to": states[i + 1].get("name", f"R{i+1}"),
            "context_delta": out,
        })

    return "\n\n".join([
        f"STEP {x['step']} CONTEXT_DELTA ({x['from']} -> {x['to']}):\n{x['context_delta']}"
        for x in deltas
    ]), deltas


def prompt_update_from_listing(kind, base_instruction, question, summary_1, current_query, listing_text):
    if kind == "gradient_listing":
        listing_name = "ordered prompt-gradient listing"
        extra = """
The listing already describes local prompt-gradient edits. Absorb it into the instruction as an executable sample-level query-writing policy.
"""
    elif kind == "context_delta_listing":
        listing_name = "ordered context-delta listing"
        extra = """
The listing describes local retrieval-context changes. Convert them into an executable sample-level query-writing policy.
"""
    else:
        raise ValueError(kind)

    return f"""
Rewrite the create_query_hop2 instruction for THIS SAMPLE ONLY.

Goal:
Produce an updated instruction p_i' that absorbs the {listing_name}.
The updated instruction will later be used by the query writer with only question, summary_1, and current query.
Therefore, the updated instruction itself must carry the useful update signal.

Important:
- Output only the updated instruction text.
- Do not output a query.
- Do not output analysis.
- Do not mention evaluation metrics.
- Do not say "retrieve missing support".
- Because this is sample-level, it may include sample-specific anchors, aliases, relation hints, and noise guards.
- Preserve the base instruction's purpose: generate a compact second-hop BM25 query.
- Keep the updated instruction concise but executable.
- Preserve ordered local edits when order matters.

{extra}

Base create_query_hop2 instruction:
{base_instruction}

Question:
{question}

summary_1:
{summary_1}

Current baseline hop2 query:
{current_query}

{listing_name}:
{listing_text}
""".strip()


def generate_prompt_update(args, kind, base_instruction, question, summary_1, current_query, listing_text):
    out = br.call_lm(
        prompt_update_from_listing(kind, base_instruction, question, summary_1, current_query, listing_text),
        args.retries,
    )
    out = br.clean_lm_text(out)
    if not out or out == "EMPTY_LLM_OUTPUT":
        out = base_instruction
    return out


def build_query_prompt(updated_instruction, question, summary_1, current_query):
    return f"""
You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.

create_query_hop2 instruction:
{updated_instruction}

Inputs:
Question:
{question}

summary_1:
{summary_1}

Current baseline hop2 query:
{current_query}

Output requirements:
- Output only one second-hop BM25 query.
- Keep it compact and keyword-like.
- Do not output explanations.
- Do not output the final answer.
- Do not output placeholders such as missing_input, MISSING_CONTEXT, additional relevant documents, or search query.
""".strip()


def rollout_instruction(args, retrieve, idx, arm, updated_instruction, question, summary_1, current_query, gold_support_titles, missing_titles):
    prompt = build_query_prompt(updated_instruction, question, summary_1, current_query)
    query = br.call_lm(prompt, args.retries)
    titles = br.normalize_titles(retrieve(query))
    sc = br.score_titles(titles, gold_support_titles, missing_titles)
    return {
        "idx": idx,
        "arm": arm,
        "query": query,
        **sc,
        "meta": {
            "question": question,
            "summary_1": summary_1,
            "current_query": current_query,
            "updated_instruction": updated_instruction,
        },
    }


def process_one(args, meta_row, aux_by_idx, qgroups, base_instruction, retrieve):
    idx = str(meta_row["idx"])
    aux = aux_by_idx[idx]
    g = qgroups[idx]
    base = g["base"]
    target = g["target"]

    question = meta_row.get("question") or aux.get("question") or ""
    summary_1 = meta_row.get("summary_1") or aux.get("summary_1") or ""
    current_query = aux.get("current_query") or base.get("query") or ""

    gold_support_titles = base.get("gold_support_titles") or meta_row.get("gold_support_titles") or []
    missing_titles = base.get("base_missing") or meta_row.get("base_missing") or []

    it = pick_iteration(aux, args.trace_steps)
    if it is None:
        raise RuntimeError(f"idx={idx}: no iteration found")

    actual_steps = int(it.get("num_edges", args.trace_steps))
    states = it.get("states") or []
    pgrads = it.get("pgrads") or []

    gradient_listing = fmt_pgrad_list(pgrads)
    context_delta_listing, context_deltas = make_context_delta_listing(args, question, summary_1, states)

    upd_grad = generate_prompt_update(
        args,
        "gradient_listing",
        base_instruction,
        question,
        summary_1,
        current_query,
        gradient_listing,
    )
    upd_ctx = generate_prompt_update(
        args,
        "context_delta_listing",
        base_instruction,
        question,
        summary_1,
        current_query,
        context_delta_listing,
    )

    rollouts = []

    # Re-run current prompt baseline under the same script.
    rollouts.append(rollout_instruction(
        args, retrieve, idx,
        "prompt_current_query",
        base_instruction,
        question, summary_1, current_query,
        gold_support_titles, missing_titles,
    ))

    rollouts.append(rollout_instruction(
        args, retrieve, idx,
        f"prompt_update_gradient_listing_steps_{actual_steps}",
        upd_grad,
        question, summary_1, current_query,
        gold_support_titles, missing_titles,
    ))

    rollouts.append(rollout_instruction(
        args, retrieve, idx,
        f"prompt_update_context_delta_listing_steps_{actual_steps}",
        upd_ctx,
        question, summary_1, current_query,
        gold_support_titles, missing_titles,
    ))

    # Endpoint diagnostics.
    rollouts.append({
        "idx": idx,
        "arm": "base_existing",
        "query": base.get("query"),
        "retrieved_titles": base.get("retrieved_titles") or [],
        "support_hit_count": base.get("support_hit_count"),
        "support_recall_hop2": safe_float(base.get("support_recall_hop2")),
        "recovered_missing_titles": base.get("recovered_missing_titles") or [],
        "missing_recovered_count": int(base.get("missing_recovered_count") or 0),
        "missing_recovery_rate": safe_float(base.get("missing_recovery_rate")),
        "meta": {"question": question, "summary_1": summary_1, "current_query": current_query},
    })
    rollouts.append({
        "idx": idx,
        "arm": "target_existing",
        "query": target.get("query"),
        "retrieved_titles": target.get("retrieved_titles") or [],
        "support_hit_count": target.get("support_hit_count"),
        "support_recall_hop2": safe_float(target.get("support_recall_hop2")),
        "recovered_missing_titles": target.get("recovered_missing_titles") or [],
        "missing_recovered_count": int(target.get("missing_recovered_count") or 0),
        "missing_recovery_rate": safe_float(target.get("missing_recovery_rate")),
        "meta": {"question": question, "summary_1": summary_1, "current_query": current_query},
    })

    aux_out = {
        "idx": idx,
        "trace_steps_requested": args.trace_steps,
        "trace_steps_used": actual_steps,
        "question": question,
        "summary_1": summary_1,
        "current_query": current_query,
        "states": states,
        "gradient_listing": gradient_listing,
        "context_delta_listing": context_delta_listing,
        "context_deltas": context_deltas,
        "updated_instruction_gradient_listing": upd_grad,
        "updated_instruction_context_delta_listing": upd_ctx,
    }

    return rollouts, aux_out


def summarize_rows(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["arm"]].append(r)

    lines = []
    lines.append("# Sample-Level Prompt Update from R-Trace\n")
    lines.append("| arm | n | mean MR | mean hop2 recall | mean recovered |")
    lines.append("|---|---:|---:|---:|---:|")
    for arm in sorted(by):
        xs = by[arm]
        n = len(xs)
        mr = sum(safe_float(x.get("missing_recovery_rate")) for x in xs) / max(1, n)
        h2 = sum(safe_float(x.get("support_recall_hop2")) for x in xs) / max(1, n)
        rec = sum(safe_float(x.get("missing_recovered_count")) for x in xs) / max(1, n)
        lines.append(f"| {arm} | {n} | {mr:.3f} | {h2:.3f} | {rec:.3f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qtrace-path", required=True)
    ap.add_argument("--meta-path", required=True)
    ap.add_argument("--rtrace-aux-path", required=True)
    ap.add_argument("--base-prompt-candidate", required=True)
    ap.add_argument("--out-dir", required=True)

    ap.add_argument("--trace-steps", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--require-summary1", action="store_true")
    ap.add_argument("--num-threads", type=int, default=4)

    ap.add_argument("--model", default="openai/gpt-5-mini")
    ap.add_argument("--api-base", default="")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--retries", type=int, default=3)

    ap.add_argument("--retriever-dir", default="")
    ap.add_argument("--retriever-k", type=int, default=7)
    args = ap.parse_args()

    if args.retriever_dir:
        os.environ["HOTPOT_RETRIEVER_DIR"] = args.retriever_dir

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lm_kwargs = {
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_base:
        lm_kwargs["api_base"] = args.api_base
    dspy.settings.configure(lm=dspy.LM(**lm_kwargs))

    base_instruction = br.load_create_query_instruction(args.base_prompt_candidate)
    (out_dir / "base_instruction.txt").write_text(base_instruction)

    qgroups = br.group_qtrace(read_jsonl(args.qtrace_path))
    meta_rows = read_jsonl(args.meta_path)
    aux_rows = read_jsonl(args.rtrace_aux_path)
    aux_by_idx = {str(r["idx"]): r for r in aux_rows}

    rows = []
    for r in meta_rows:
        idx = str(r["idx"])
        if idx not in qgroups or idx not in aux_by_idx:
            continue
        if not r.get("question"):
            continue
        if args.require_summary1 and not r.get("summary_1"):
            continue
        rows.append(r)

    rows = sorted(rows, key=lambda r: int(r["idx"]) if str(r["idx"]).isdigit() else str(r["idx"]))
    if args.limit:
        rows = rows[:args.limit]

    print("[rows]", len(rows))
    print("[trace_steps]", args.trace_steps)
    print("[with summary_1]", sum(1 for r in rows if r.get("summary_1")))

    retrieve = br.load_retriever(args)

    all_rollouts = []
    update_aux = []

    with ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [
            ex.submit(process_one, args, r, aux_by_idx, qgroups, base_instruction, retrieve)
            for r in rows
        ]
        for fut in tqdm(as_completed(futs), total=len(futs), desc="sample prompt update"):
            rollouts, aux = fut.result()
            all_rollouts.extend(rollouts)
            update_aux.append(aux)
            write_jsonl(out_dir / "rows.partial.jsonl", all_rollouts)
            write_jsonl(out_dir / "prompt_update_aux.partial.jsonl", update_aux)
            (out_dir / "summary.partial.md").write_text(summarize_rows(all_rollouts))

    write_jsonl(out_dir / "rows.jsonl", all_rollouts)
    write_jsonl(out_dir / "prompt_update_aux.jsonl", update_aux)
    (out_dir / "summary.md").write_text(summarize_rows(all_rollouts))

    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
