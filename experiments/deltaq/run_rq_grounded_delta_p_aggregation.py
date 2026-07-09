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


def log(args, msg):
    if getattr(args, "log_progress", False):
        print(msg, flush=True)


def norm_text(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def parse_json_or_text(text):
    js = br.jsonish_extract(text)
    if isinstance(js, dict):
        return js
    return {"raw_text": br.clean_lm_text(text)}


def compact_state(s):
    return br.compact_state_for_prompt(s)


def state_pair_block(left, right):
    return f"""
R_left:
{br.compact_json(compact_state(left))}

R_right:
{br.compact_json(compact_state(right))}
""".strip()


def load_qg_aux(path):
    rows = read_jsonl(path)
    out = {}
    for r in rows:
        out[str(r["idx"])] = r
    return out


def load_meta_rows(meta_path, qgroups, qg_aux, limit=0, require_summary1=False):
    rows = read_jsonl(meta_path)
    usable = []
    for r in rows:
        idx = str(r["idx"])
        if idx not in qgroups:
            continue
        if idx not in qg_aux:
            continue
        if not r.get("question"):
            continue
        if require_summary1 and not r.get("summary_1"):
            continue
        usable.append(r)

    usable = sorted(usable, key=lambda x: int(x["idx"]) if str(x["idx"]).isdigit() else str(x["idx"]))
    if limit:
        usable = usable[:limit]
    return usable


def get_trace_states_and_edges(qg_aux_row, trace_steps):
    states = qg_aux_row.get("states") or []
    edges = qg_aux_row.get("twoturn_edges") or []

    if not states or not edges:
        raise RuntimeError("missing states or twoturn_edges in query_grounded_aux row")

    # Keep only requested number of edges.
    edges = sorted(edges, key=lambda e: int(e.get("edge_index", 0)))[:trace_steps]
    states = states[:len(edges) + 1]
    return states, edges


def visible_input_block(question, summary_1, current_query):
    return f"""
Visible inputs available to create_query_hop2:
Question:
{question}

summary_1:
{summary_1}

Current baseline hop2 query:
{current_query}
""".strip()


def prompt_rq_to_guarded_delta_p(question, summary_1, current_query, left, right, delta_q_obj, edge_idx):
    return f"""
You are deriving a LOCAL PROMPT DELTA Δp_i for create_query_hop2.

Goal:
Use BOTH:
  1. ΔR_i = R_left -> R_right as the retrieval-state target / semantic constraint.
  2. Δq_i as the executable query-space mechanism.

Produce a self-contained prompt-delta unit that can later be aggregated without seeing ΔR_i or Δq_i again.

Output JSON only:
{{
  "edge_index": {edge_idx},
  "delta_p": {{
    "trigger": "...",
    "preserve_rule": "...",
    "restore_rule": "...",
    "drop_or_avoid_rule": "...",
    "query_shape_rule": "...",
    "bm25_interface_guard": "...",
    "why_this_delta_is_retrieval_grounded": "..."
  }}
}}

Strict rules:
- Δp_i must be a PROMPT EDIT, not a query.
- Do NOT output candidate queries as the prompt delta.
- Do NOT tell the prompt to copy a support title, answer literal, or page title that appears only in R_left/R_right.
- Sample-specific anchors may appear only as examples if they already appear in the visible inputs.
- Prefer rule-like language: relation cue, answer type, entity role, alias/date/type cue, noisy side entity, candidate set.
- No web-search syntax: do not use or recommend site:, IMDb, Wikipedia, OR-heavy, AND-heavy, multi-site, search-engine style.
- Preserve the interface: create_query_hop2 must output exactly one compact BM25 query.
- No semicolon-separated multi-query programs.
- No final answer.
- No hidden metrics, gold labels, oracle labels, or missing-support terminology.
- If Δq_i is noisy or too specific, correct the prompt delta using ΔR_i as a retrieval-context constraint.

{visible_input_block(question, summary_1, current_query)}

Original retrieval-state transition ΔR_i:
{state_pair_block(left, right)}

Explicit query-space transition Δq_i:
{br.compact_json(delta_q_obj)}
""".strip()


def call_guarded_delta_p(args, question, summary_1, current_query, left, right, delta_q_obj, edge_idx):
    out = br.call_lm(
        prompt_rq_to_guarded_delta_p(question, summary_1, current_query, left, right, delta_q_obj, edge_idx),
        args.retries,
    )
    obj = parse_json_or_text(out)

    dp = obj.get("delta_p") if isinstance(obj.get("delta_p"), dict) else obj
    if not isinstance(dp, dict):
        dp = {"raw_text": str(dp)}

    # Normalize required keys.
    keys = [
        "trigger",
        "preserve_rule",
        "restore_rule",
        "drop_or_avoid_rule",
        "query_shape_rule",
        "bm25_interface_guard",
        "why_this_delta_is_retrieval_grounded",
    ]
    for k in keys:
        dp.setdefault(k, "")

    return {
        "edge_index": edge_idx,
        "from": left.get("name", f"R{edge_idx}"),
        "to": right.get("name", f"R{edge_idx+1}"),
        "delta_q": delta_q_obj,
        "delta_p": dp,
        "raw_delta_p_generation": out,
    }


def format_delta_p_only_listing(edges):
    parts = []
    for e in edges:
        dp = e.get("delta_p") or {}
        parts.append(
            f"EDGE {e.get('edge_index')} Δp ({e.get('from')} -> {e.get('to')}):\n"
            f"TRIGGER: {dp.get('trigger', '')}\n"
            f"PRESERVE_RULE: {dp.get('preserve_rule', '')}\n"
            f"RESTORE_RULE: {dp.get('restore_rule', '')}\n"
            f"DROP_OR_AVOID_RULE: {dp.get('drop_or_avoid_rule', '')}\n"
            f"QUERY_SHAPE_RULE: {dp.get('query_shape_rule', '')}\n"
            f"BM25_INTERFACE_GUARD: {dp.get('bm25_interface_guard', '')}\n"
            f"WHY_RETRIEVAL_GROUNDED: {dp.get('why_this_delta_is_retrieval_grounded', '')}"
        )
    return "\n\n".join(parts)


def format_full_context_listing(states, edges):
    parts = []
    for e in edges:
        i = int(e.get("edge_index", 0))
        left = states[i]
        right = states[i + 1]
        dq = e.get("delta_q") or {}
        dp = e.get("delta_p") or {}

        parts.append(
            f"EDGE {i}: ΔR + Δq + Δp\n\n"
            f"ΔR_i:\n{state_pair_block(left, right)}\n\n"
            f"Δq_i:\n{br.compact_json(dq)}\n\n"
            f"Δp_i:\n"
            f"TRIGGER: {dp.get('trigger', '')}\n"
            f"PRESERVE_RULE: {dp.get('preserve_rule', '')}\n"
            f"RESTORE_RULE: {dp.get('restore_rule', '')}\n"
            f"DROP_OR_AVOID_RULE: {dp.get('drop_or_avoid_rule', '')}\n"
            f"QUERY_SHAPE_RULE: {dp.get('query_shape_rule', '')}\n"
            f"BM25_INTERFACE_GUARD: {dp.get('bm25_interface_guard', '')}\n"
            f"WHY_RETRIEVAL_GROUNDED: {dp.get('why_this_delta_is_retrieval_grounded', '')}"
        )
    return "\n\n" + ("-" * 80 + "\n\n").join(parts)


def prompt_delta_p_direct_context(base_instruction, question, summary_1, current_query, delta_p_listing):
    return f"""
You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.

Base create_query_hop2 instruction:
{base_instruction}

Additional ordered local prompt deltas Δp_i:
{delta_p_listing}

Apply the ordered Δp_i list as prompt-update guidance for this sample.

Important:
- Use only the Δp_i rules, not the original ΔR_i or Δq_i.
- Output exactly one compact BM25 query.
- Do not output explanations.
- Do not output the final answer.
- Do not output multiple semicolon-separated queries.
- Do not use site:, IMDb, Wikipedia, OR-heavy, or web-search syntax.
- Do not copy hidden support titles or answer literals.

{visible_input_block(question, summary_1, current_query)}
""".strip()


def prompt_aggregate_delta_p_only(base_instruction, question, summary_1, current_query, delta_p_listing):
    return f"""
Aggregate the ordered local prompt deltas into ONE sample-level updated create_query_hop2 instruction p_i'.

This is the main Δp-only aggregation arm:
  p_i' = Apply(p0, ordered {{Δp_i}})

Output only the updated instruction text.

Requirements:
- Use ONLY the ordered Δp_i list as update evidence.
- Do NOT ask for or reconstruct ΔR_i or Δq_i.
- Preserve create_query_hop2's role: produce exactly one compact second-hop BM25 query.
- Keep the instruction rule-like, not query-like.
- Do not include final queries.
- Do not include support titles or answer literals unless they are present in question/summary_1/current query.
- Avoid sample-specific retrieval scripts.
- Avoid site:, IMDb, Wikipedia, OR-heavy, AND-heavy, semicolon multi-query, or search-engine syntax.
- Prefer reusable local rules: preserve source anchor, restore relation/type/alias/date cue, keep candidate set when uncertain, drop noisy side entities.
- Output no analysis.

Base instruction p0:
{base_instruction}

{visible_input_block(question, summary_1, current_query)}

Ordered Δp_i list:
{delta_p_listing}
""".strip()


def prompt_aggregate_full_context(base_instruction, question, summary_1, current_query, full_listing):
    return f"""
Aggregate the ordered local trace into ONE sample-level updated create_query_hop2 instruction p_i'.

This is an ablation / upper-bound aggregation arm:
  p_i' = Apply(p0, ordered {{ΔR_i, Δq_i, Δp_i}})

Output only the updated instruction text.

Requirements:
- You may use ΔR_i and Δq_i to interpret Δp_i, but the final p_i' must still be a prompt instruction, not a query.
- Preserve create_query_hop2's role: produce exactly one compact second-hop BM25 query.
- Keep the instruction rule-like, not query-like.
- Do not include final queries.
- Do not include support titles or answer literals unless they are present in question/summary_1/current query.
- Avoid sample-specific retrieval scripts.
- Avoid site:, IMDb, Wikipedia, OR-heavy, AND-heavy, semicolon multi-query, or search-engine syntax.
- Prefer reusable local rules: preserve source anchor, restore relation/type/alias/date cue, keep candidate set when uncertain, drop noisy side entities.
- Output no analysis.

Base instruction p0:
{base_instruction}

{visible_input_block(question, summary_1, current_query)}

Ordered full trace context:
{full_listing}
""".strip()


def aggregate_instruction(args, prompt, fallback_instruction):
    out = br.call_lm(prompt, args.retries)
    out = br.clean_lm_text(out)
    if not out or out == "EMPTY_LLM_OUTPUT":
        return fallback_instruction
    return out


def build_query_prompt_with_instruction(updated_instruction, question, summary_1, current_query):
    return f"""
You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.

create_query_hop2 instruction:
{updated_instruction}

{visible_input_block(question, summary_1, current_query)}

Output requirements:
- Output only one second-hop BM25 query.
- Keep it compact and keyword-like.
- Do not output explanations.
- Do not output the final answer.
- Do not output placeholders.
- Do not output multiple semicolon-separated queries.
- Do not use site:, IMDb, Wikipedia, OR-heavy, AND-heavy, or web-search syntax.
""".strip()


def rollout_prompt(args, retrieve, idx, arm, prompt, gold_support_titles, missing_titles, meta):
    query = br.call_lm(prompt, args.retries)
    titles = br.normalize_titles(retrieve(query))
    sc = br.score_titles(titles, gold_support_titles, missing_titles)
    return {
        "idx": idx,
        "arm": arm,
        "query": query,
        **sc,
        "meta": meta,
    }


def rollout_instruction(args, retrieve, idx, arm, instruction, question, summary_1, current_query, gold_support_titles, missing_titles, meta_extra=None):
    prompt = build_query_prompt_with_instruction(instruction, question, summary_1, current_query)
    meta = {
        "question": question,
        "summary_1": summary_1,
        "current_query": current_query,
        "updated_instruction": instruction,
    }
    if meta_extra:
        meta.update(meta_extra)
    return rollout_prompt(args, retrieve, idx, arm, prompt, gold_support_titles, missing_titles, meta)


def process_one(args, meta_row, qgroups, qg_aux_by_idx, base_instruction, retrieve):
    idx = str(meta_row["idx"])
    g = qgroups[idx]
    base = g["base"]
    target = g["target"]
    qg_aux = qg_aux_by_idx[idx]

    question = meta_row.get("question") or qg_aux.get("question") or ""
    summary_1 = meta_row.get("summary_1") or qg_aux.get("summary_1") or ""
    current_query = qg_aux.get("current_query") or base.get("query") or ""

    gold_support_titles = base.get("gold_support_titles") or meta_row.get("gold_support_titles") or []
    missing_titles = base.get("base_missing") or meta_row.get("base_missing") or []

    states, q_edges = get_trace_states_and_edges(qg_aux, args.trace_steps)
    actual_steps = len(q_edges)

    log(args, f"[RQ-DP] idx={idx} start steps={actual_steps}")

    rq_edges = []
    for i, qe in enumerate(q_edges):
        dq = qe.get("delta_q") or {}
        edge_idx = int(qe.get("edge_index", i))
        dp_edge = call_guarded_delta_p(
            args,
            question, summary_1, current_query,
            states[i], states[i + 1],
            dq,
            edge_idx,
        )
        rq_edges.append(dp_edge)
        log(args, f"[RQ-DP] idx={idx} edge={edge_idx} delta_p_done")

    delta_p_listing = format_delta_p_only_listing(rq_edges)
    full_context_listing = format_full_context_listing(states, rq_edges)

    instr_delta_p_only = aggregate_instruction(
        args,
        prompt_aggregate_delta_p_only(base_instruction, question, summary_1, current_query, delta_p_listing),
        base_instruction,
    )

    instr_full_context = aggregate_instruction(
        args,
        prompt_aggregate_full_context(base_instruction, question, summary_1, current_query, full_context_listing),
        base_instruction,
    )

    rollouts = []

    rollouts.append(rollout_instruction(
        args, retrieve, idx,
        "prompt_current_query",
        base_instruction,
        question, summary_1, current_query,
        gold_support_titles, missing_titles,
        {"trace_steps": actual_steps},
    ))

    rollouts.append(rollout_prompt(
        args, retrieve, idx,
        f"delta_p_direct_context_Rq_grounded_steps_{actual_steps}",
        prompt_delta_p_direct_context(base_instruction, question, summary_1, current_query, delta_p_listing),
        gold_support_titles, missing_titles,
        {
            "question": question,
            "summary_1": summary_1,
            "current_query": current_query,
            "trace_steps": actual_steps,
            "delta_p_listing": delta_p_listing,
        },
    ))

    rollouts.append(rollout_instruction(
        args, retrieve, idx,
        f"prompt_update_Rq_delta_p_only_aggregate_steps_{actual_steps}",
        instr_delta_p_only,
        question, summary_1, current_query,
        gold_support_titles, missing_titles,
        {
            "trace_steps": actual_steps,
            "delta_p_listing": delta_p_listing,
            "aggregate_mode": "delta_p_only",
        },
    ))

    rollouts.append(rollout_instruction(
        args, retrieve, idx,
        f"prompt_update_Rq_full_context_aggregate_steps_{actual_steps}",
        instr_full_context,
        question, summary_1, current_query,
        gold_support_titles, missing_titles,
        {
            "trace_steps": actual_steps,
            "delta_p_listing": delta_p_listing,
            "full_context_listing": full_context_listing,
            "aggregate_mode": "full_context",
        },
    ))

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
        "question": question,
        "summary_1": summary_1,
        "current_query": current_query,
        "trace_steps": actual_steps,
        "states": states,
        "source_twoturn_delta_q_edges": q_edges,
        "rq_grounded_delta_p_edges": rq_edges,
        "delta_p_listing": delta_p_listing,
        "full_context_listing": full_context_listing,
        "updated_instruction_delta_p_only": instr_delta_p_only,
        "updated_instruction_full_context": instr_full_context,
    }

    best = max(
        safe_float(r.get("missing_recovery_rate"))
        for r in rollouts
        if r["arm"].startswith("delta_p_") or r["arm"].startswith("prompt_update_Rq_")
    )
    log(args, f"[RQ-DP] idx={idx} done best_MR={best:.3f}")
    return rollouts, aux_out


def summarize_rows(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["arm"]].append(r)

    lines = []
    lines.append("# Rq-Grounded DeltaP Aggregation\n")
    lines.append("| arm | n | mean MR | mean hop2 recall | mean recovered |")
    lines.append("|---|---:|---:|---:|---:|")
    for arm in sorted(by):
        xs = by[arm]
        n = len(xs)
        mean_mr = sum(safe_float(x.get("missing_recovery_rate")) for x in xs) / max(1, n)
        mean_h2 = sum(safe_float(x.get("support_recall_hop2")) for x in xs) / max(1, n)
        mean_rec = sum(safe_float(x.get("missing_recovered_count")) for x in xs) / max(1, n)
        lines.append(f"| {arm} | {n} | {mean_mr:.3f} | {mean_h2:.3f} | {mean_rec:.3f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qtrace-path", required=True)
    ap.add_argument("--meta-path", required=True)
    ap.add_argument("--query-grounded-aux-path", required=True)
    ap.add_argument("--base-prompt-candidate", required=True)
    ap.add_argument("--out-dir", required=True)

    ap.add_argument("--trace-steps", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--require-summary1", action="store_true")
    ap.add_argument("--num-threads", type=int, default=4)
    ap.add_argument("--log-progress", action="store_true")

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
    qg_aux_by_idx = load_qg_aux(args.query_grounded_aux_path)
    meta_rows = load_meta_rows(
        args.meta_path,
        qgroups,
        qg_aux_by_idx,
        limit=args.limit,
        require_summary1=args.require_summary1,
    )

    print("[rows]", len(meta_rows))
    print("[trace_steps]", args.trace_steps)
    print("[with summary_1]", sum(1 for r in meta_rows if r.get("summary_1")))

    retrieve = br.load_retriever(args)

    all_rows = []
    aux_rows = []

    with ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [
            ex.submit(process_one, args, r, qgroups, qg_aux_by_idx, base_instruction, retrieve)
            for r in meta_rows
        ]
        for fut in tqdm(as_completed(futs), total=len(futs), desc="rq-grounded delta-p aggregation"):
            rows, aux = fut.result()
            all_rows.extend(rows)
            aux_rows.append(aux)
            write_jsonl(out_dir / "rows.partial.jsonl", all_rows)
            write_jsonl(out_dir / "rq_delta_p_aux.partial.jsonl", aux_rows)
            (out_dir / "summary.partial.md").write_text(summarize_rows(all_rows))

    write_jsonl(out_dir / "rows.jsonl", all_rows)
    write_jsonl(out_dir / "rq_delta_p_aux.jsonl", aux_rows)
    (out_dir / "summary.md").write_text(summarize_rows(all_rows))

    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
