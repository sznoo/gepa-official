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


def pick_iteration(aux, trace_steps):
    its = aux.get("iterations") or []
    for it in its:
        if int(it.get("num_edges", -1)) == trace_steps:
            return it
    candidates = [it for it in its if int(it.get("num_edges", -1)) <= trace_steps]
    if candidates:
        return sorted(candidates, key=lambda x: int(x.get("num_edges", -1)))[-1]
    if its:
        return sorted(its, key=lambda x: int(x.get("num_edges", -1)))[-1]
    return None


def compact_state(s):
    return br.compact_state_for_prompt(s)


def parse_json_or_text(text):
    js = br.jsonish_extract(text)
    if isinstance(js, dict):
        return js
    return {"raw_text": br.clean_lm_text(text)}


def state_pair_block(left, right):
    return f"""
R_left:
{br.compact_json(compact_state(left))}

R_right:
{br.compact_json(compact_state(right))}
""".strip()


def prompt_onecall_r_to_q_to_p(question, summary_1, current_query, left, right, edge_idx):
    return f"""
You are converting one generated retrieval-state transition into a query-grounded prompt delta.

Task:
In ONE structured response, map:
  ΔR_i = R_left -> R_right
to:
  Δq_i = local query transition
then:
  Δp_i = local prompt update that would make create_query_hop2 produce q_after-like retrieval behavior.

Output JSON only:
{{
  "edge_index": {edge_idx},
  "delta_q": {{
    "q_before_behavior": "...",
    "q_after_behavior": "...",
    "candidate_q_after": "...",
    "query_edit_operations": ["..."]
  }},
  "delta_p": {{
    "trigger": "...",
    "preserve": "...",
    "add_or_restore": "...",
    "remove_or_avoid": "...",
    "bm25_query_shape": "...",
    "why_this_prompt_delta_helps": "..."
  }}
}}

Rules:
- candidate_q_after must be a concrete compact BM25 query.
- Do not output the final answer.
- Do not mention hidden metrics or gold labels.
- Preserve local step order.
- Make Δp_i executable as a prompt edit, not a query itself.

Question:
{question}

summary_1:
{summary_1}

Current baseline hop2 query:
{current_query}

{state_pair_block(left, right)}
""".strip()


def prompt_turn1_r_to_q(question, summary_1, current_query, left, right, edge_idx):
    return f"""
Convert one generated retrieval-state transition into an explicit local query transition Δq_i.

Output JSON only:
{{
  "edge_index": {edge_idx},
  "q_before_behavior": "...",
  "q_after_behavior": "...",
  "candidate_q_after": "...",
  "query_edit_operations": ["..."],
  "why_this_query_transition_matches_delta_R": "..."
}}

Rules:
- candidate_q_after must be one compact BM25 query.
- It should move from R_left toward R_right.
- It should preserve useful anchors, restore bridge/type/alias/date cues, and remove noisy distractors.
- Do not output the final answer.
- Do not mention hidden metrics or gold labels.

Question:
{question}

summary_1:
{summary_1}

Current baseline hop2 query:
{current_query}

{state_pair_block(left, right)}
""".strip()


def prompt_turn2_q_to_p(question, summary_1, current_query, delta_q_obj, edge_idx):
    return f"""
Convert an explicit local query transition Δq_i into a local prompt delta Δp_i for create_query_hop2.

Output JSON only:
{{
  "edge_index": {edge_idx},
  "delta_p": {{
    "trigger": "...",
    "preserve": "...",
    "add_or_restore": "...",
    "remove_or_avoid": "...",
    "bm25_query_shape": "...",
    "why_this_prompt_delta_helps": "..."
  }}
}}

Rules:
- Δp_i should teach the query writer to produce q_after-like behavior.
- Do not simply copy the query as an instruction.
- Keep concrete anchors and query-shape implications when useful.
- Preserve local step order.
- Do not mention hidden metrics or gold labels.

Question:
{question}

summary_1:
{summary_1}

Current baseline hop2 query:
{current_query}

Explicit Δq_i:
{br.compact_json(delta_q_obj)}
""".strip()


def call_onecall_edge(args, question, summary_1, current_query, left, right, edge_idx):
    out = br.call_lm(
        prompt_onecall_r_to_q_to_p(question, summary_1, current_query, left, right, edge_idx),
        args.retries,
    )
    obj = parse_json_or_text(out)
    delta_q = obj.get("delta_q") if isinstance(obj.get("delta_q"), dict) else {}
    delta_p = obj.get("delta_p") if isinstance(obj.get("delta_p"), dict) else {}

    if not delta_q:
        delta_q = {
            "q_before_behavior": "",
            "q_after_behavior": "",
            "candidate_q_after": "",
            "query_edit_operations": [],
            "raw_text": obj.get("raw_text", out),
        }
    if not delta_p:
        delta_p = {
            "trigger": "",
            "preserve": "",
            "add_or_restore": "",
            "remove_or_avoid": "",
            "bm25_query_shape": "",
            "why_this_prompt_delta_helps": obj.get("raw_text", out),
        }

    return {
        "edge_index": edge_idx,
        "from": left.get("name", f"R{edge_idx}"),
        "to": right.get("name", f"R{edge_idx+1}"),
        "delta_q": delta_q,
        "delta_p": delta_p,
        "raw": out,
    }


def call_twoturn_edge(args, question, summary_1, current_query, left, right, edge_idx):
    out1 = br.call_lm(
        prompt_turn1_r_to_q(question, summary_1, current_query, left, right, edge_idx),
        args.retries,
    )
    dq = parse_json_or_text(out1)
    if "candidate_q_after" not in dq:
        dq["candidate_q_after"] = ""
    if "query_edit_operations" not in dq:
        dq["query_edit_operations"] = []

    out2 = br.call_lm(
        prompt_turn2_q_to_p(question, summary_1, current_query, dq, edge_idx),
        args.retries,
    )
    dp_obj = parse_json_or_text(out2)
    dp = dp_obj.get("delta_p") if isinstance(dp_obj.get("delta_p"), dict) else dp_obj

    return {
        "edge_index": edge_idx,
        "from": left.get("name", f"R{edge_idx}"),
        "to": right.get("name", f"R{edge_idx+1}"),
        "delta_q": dq,
        "delta_p": dp,
        "raw_turn1": out1,
        "raw_turn2": out2,
    }


def format_delta_q_listing(edges):
    parts = []
    for e in edges:
        dq = e.get("delta_q") or {}
        parts.append(
            f"EDGE {e.get('edge_index')} Δq ({e.get('from')} -> {e.get('to')}):\n"
            f"q_before_behavior: {dq.get('q_before_behavior', '')}\n"
            f"q_after_behavior: {dq.get('q_after_behavior', '')}\n"
            f"candidate_q_after: {dq.get('candidate_q_after', '')}\n"
            f"query_edit_operations: {dq.get('query_edit_operations', [])}"
        )
    return "\n\n".join(parts)


def format_delta_p_listing(edges):
    parts = []
    for e in edges:
        dp = e.get("delta_p") or {}
        if isinstance(dp, str):
            dp_text = dp
        else:
            dp_text = "\n".join([
                f"trigger: {dp.get('trigger', '')}",
                f"preserve: {dp.get('preserve', '')}",
                f"add_or_restore: {dp.get('add_or_restore', '')}",
                f"remove_or_avoid: {dp.get('remove_or_avoid', '')}",
                f"bm25_query_shape: {dp.get('bm25_query_shape', '')}",
                f"why: {dp.get('why_this_prompt_delta_helps', dp.get('why', ''))}",
            ])
        parts.append(
            f"EDGE {e.get('edge_index')} Δp ({e.get('from')} -> {e.get('to')}):\n{dp_text}"
        )
    return "\n\n".join(parts)


def prompt_aggregate_delta_p(base_instruction, question, summary_1, current_query, delta_p_listing, scheme_name):
    return f"""
Aggregate the ordered local prompt deltas into ONE sample-level updated create_query_hop2 instruction p_i'.

This is a prompt update task:
  p_i' = Apply(p0, ordered {{Δp_i}})

Output only the updated instruction text.

Requirements:
- Preserve the base instruction's role: generate one compact second-hop BM25 query.
- Preserve the ordered local edit program when order matters.
- Keep concrete sample-specific anchors, bridge clues, alias/date/type cues, and noise guards.
- Do not collapse into generic retrieval advice.
- Do not output a query.
- Do not output analysis.
- Do not mention hidden metrics, gold labels, or missing supports.
- The final p_i' will be used with only question, summary_1, and current query.

Scheme:
{scheme_name}

Base instruction p0:
{base_instruction}

Question:
{question}

summary_1:
{summary_1}

Current baseline hop2 query:
{current_query}

Ordered local prompt deltas {{Δp_i}}:
{delta_p_listing}
""".strip()


def aggregate_delta_p(args, base_instruction, question, summary_1, current_query, edges, scheme_name):
    listing = format_delta_p_listing(edges)
    out = br.call_lm(
        prompt_aggregate_delta_p(base_instruction, question, summary_1, current_query, listing, scheme_name),
        args.retries,
    )
    out = br.clean_lm_text(out)
    if not out or out == "EMPTY_LLM_OUTPUT":
        out = base_instruction
    return out, listing


def build_query_prompt_with_instruction(updated_instruction, question, summary_1, current_query):
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


def build_query_prompt_with_delta_q(base_instruction, question, summary_1, current_query, delta_q_listing):
    return f"""
You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.

Base create_query_hop2 instruction:
{base_instruction}

Inputs:
Question:
{question}

summary_1:
{summary_1}

Current baseline hop2 query:
{current_query}

Ordered query-space transition program Δq:
{delta_q_listing}

Apply the ordered Δq program to produce the final second-hop BM25 query.
The Δq program is query-space guidance, not the final answer.

Output requirements:
- Output only one second-hop BM25 query.
- Keep it compact and keyword-like.
- Preserve useful anchors.
- Restore bridge/type/alias/date cues.
- Drop noisy side entities if they distract retrieval.
- Do not output explanations.
- Do not output the final answer.
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


def score_candidate_deltaq_edges(retrieve, edges, gold_support_titles, missing_titles):
    scored = []
    for e in edges:
        dq = e.get("delta_q") or {}
        q = br.clean_lm_text(dq.get("candidate_q_after", ""))
        if not q:
            scored.append({**e, "candidate_q_after_score": None})
            continue
        titles = br.normalize_titles(retrieve(q))
        sc = br.score_titles(titles, gold_support_titles, missing_titles)
        scored.append({
            **e,
            "candidate_q_after_score": {
                "query": q,
                **sc,
            }
        })
    return scored


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
    states = it.get("states") or []
    actual_steps = int(it.get("num_edges", args.trace_steps))

    log(args, f"[QG-PUPDATE] idx={idx} start steps={actual_steps}")

    onecall_edges = []
    twoturn_edges = []
    for i in range(len(states) - 1):
        onecall_edges.append(call_onecall_edge(args, question, summary_1, current_query, states[i], states[i + 1], i))
        twoturn_edges.append(call_twoturn_edge(args, question, summary_1, current_query, states[i], states[i + 1], i))
        log(args, f"[QG-PUPDATE] idx={idx} edge={i} done")

    onecall_edges_scored = score_candidate_deltaq_edges(retrieve, onecall_edges, gold_support_titles, missing_titles)
    twoturn_edges_scored = score_candidate_deltaq_edges(retrieve, twoturn_edges, gold_support_titles, missing_titles)

    onecall_instruction, onecall_dp_listing = aggregate_delta_p(
        args, base_instruction, question, summary_1, current_query,
        onecall_edges, "onecall: ΔR_i -> Δq_i -> Δp_i in one structured call"
    )
    twoturn_instruction, twoturn_dp_listing = aggregate_delta_p(
        args, base_instruction, question, summary_1, current_query,
        twoturn_edges, "twoturn: ΔR_i -> Δq_i, then Δq_i -> Δp_i"
    )

    onecall_dq_listing = format_delta_q_listing(onecall_edges)
    twoturn_dq_listing = format_delta_q_listing(twoturn_edges)

    rollouts = []

    rollouts.append(rollout_instruction(
        args, retrieve, idx,
        "prompt_current_query",
        base_instruction,
        question, summary_1, current_query,
        gold_support_titles, missing_titles,
        {"trace_steps": actual_steps},
    ))

    rollouts.append(rollout_instruction(
        args, retrieve, idx,
        f"prompt_update_onecall_R_to_q_to_p_steps_{actual_steps}",
        onecall_instruction,
        question, summary_1, current_query,
        gold_support_titles, missing_titles,
        {"trace_steps": actual_steps, "delta_p_listing": onecall_dp_listing},
    ))

    rollouts.append(rollout_instruction(
        args, retrieve, idx,
        f"prompt_update_twoturn_R_to_q_then_p_steps_{actual_steps}",
        twoturn_instruction,
        question, summary_1, current_query,
        gold_support_titles, missing_titles,
        {"trace_steps": actual_steps, "delta_p_listing": twoturn_dp_listing},
    ))

    # Diagnostic: use Δq listing directly as prompt context.
    rollouts.append(rollout_prompt(
        args, retrieve, idx,
        f"deltaq_direct_context_onecall_steps_{actual_steps}",
        build_query_prompt_with_delta_q(base_instruction, question, summary_1, current_query, onecall_dq_listing),
        gold_support_titles, missing_titles,
        {
            "question": question,
            "summary_1": summary_1,
            "current_query": current_query,
            "trace_steps": actual_steps,
            "delta_q_listing": onecall_dq_listing,
        },
    ))

    rollouts.append(rollout_prompt(
        args, retrieve, idx,
        f"deltaq_direct_context_twoturn_steps_{actual_steps}",
        build_query_prompt_with_delta_q(base_instruction, question, summary_1, current_query, twoturn_dq_listing),
        gold_support_titles, missing_titles,
        {
            "question": question,
            "summary_1": summary_1,
            "current_query": current_query,
            "trace_steps": actual_steps,
            "delta_q_listing": twoturn_dq_listing,
        },
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
        "onecall_edges": onecall_edges_scored,
        "twoturn_edges": twoturn_edges_scored,
        "onecall_delta_q_listing": onecall_dq_listing,
        "twoturn_delta_q_listing": twoturn_dq_listing,
        "onecall_delta_p_listing": onecall_dp_listing,
        "twoturn_delta_p_listing": twoturn_dp_listing,
        "updated_instruction_onecall": onecall_instruction,
        "updated_instruction_twoturn": twoturn_instruction,
    }

    best = max(safe_float(r.get("missing_recovery_rate")) for r in rollouts if "prompt_update" in r.get("arm", "") or "deltaq_direct" in r.get("arm", ""))
    log(args, f"[QG-PUPDATE] idx={idx} done best_MR={best:.3f}")
    return rollouts, aux_out


def summarize_rows(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["arm"]].append(r)

    lines = []
    lines.append("# Query-Grounded Prompt Update from Generated R-Trace\n")
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
    aux_outs = []

    with ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [
            ex.submit(process_one, args, r, aux_by_idx, qgroups, base_instruction, retrieve)
            for r in rows
        ]
        for fut in tqdm(as_completed(futs), total=len(futs), desc="query-grounded prompt update"):
            rollouts, aux = fut.result()
            all_rollouts.extend(rollouts)
            aux_outs.append(aux)
            write_jsonl(out_dir / "rows.partial.jsonl", all_rollouts)
            write_jsonl(out_dir / "query_grounded_aux.partial.jsonl", aux_outs)
            (out_dir / "summary.partial.md").write_text(summarize_rows(all_rollouts))

    write_jsonl(out_dir / "rows.jsonl", all_rollouts)
    write_jsonl(out_dir / "query_grounded_aux.jsonl", aux_outs)
    (out_dir / "summary.md").write_text(summarize_rows(all_rollouts))

    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
