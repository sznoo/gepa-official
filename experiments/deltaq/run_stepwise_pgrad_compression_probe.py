# /home/jinwoo/gepa-official/experiments/deltaq/run_stepwise_pgrad_compression_probe.py
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


def read_jsonl(p):
    rows = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(p, rows):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def norm_title(x):
    return str(x or "").strip()


def as_set(xs):
    return {norm_title(x) for x in (xs or []) if norm_title(x)}


def arm_order(arm):
    if arm == "base_query":
        return 0
    if arm == "target_query":
        return 10_000
    m = re.search(r"trace_step_(\d+)", arm or "")
    if m:
        return int(m.group(1))
    return None


def missing_recovery_rate(row):
    return float(row.get("missing_recovery_rate") or 0.0)


def recovered_missing_count(row):
    return int(row.get("missing_recovered_count") or 0)


def support_recall_hop2(row):
    return float(row.get("support_recall_hop2") or 0.0)


def group_qtrace(rows):
    by = defaultdict(list)
    for r in rows:
        by[str(r["idx"])].append(r)

    groups = {}
    for idx, xs in by.items():
        trace = []
        for r in xs:
            o = arm_order(r.get("arm"))
            if o is not None:
                trace.append((o, r))
        trace = [r for _, r in sorted(trace, key=lambda x: x[0])]

        base = next((r for r in trace if r.get("arm") == "base_query"), None)
        target = next((r for r in trace if r.get("arm") == "target_query"), None)
        steps = [r for r in trace if str(r.get("arm", "")).startswith("trace_step_")]

        if base and steps and target:
            groups[idx] = {"idx": idx, "base": base, "steps": steps, "target": target}
    return groups


def collect_strings(obj, path=""):
    out = []
    if isinstance(obj, str):
        out.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(collect_strings(v, path + "." + str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(collect_strings(v, path + f"[{i}]"))
    return out


def find_key_subtree(obj, keyword):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if keyword in str(k):
                return v
        for v in obj.values():
            found = find_key_subtree(v, keyword)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = find_key_subtree(v, keyword)
            if found is not None:
                return found
    return None


def load_create_query_instruction(path):
    data = json.loads(Path(path).read_text())
    subtree = find_key_subtree(data, "create_query_hop2") or find_key_subtree(data, "hop2") or data

    strings = collect_strings(subtree)
    candidates = []
    for p, s in strings:
        ss = s.strip()
        if len(ss) < 40:
            continue
        low = ss.lower()
        score = 0
        for kw in ["query", "search", "question", "summary", "hop"]:
            if kw in low:
                score += 1
        candidates.append((score, len(ss), p, ss))

    if candidates:
        candidates.sort(reverse=True)
        score, length, p, instr = candidates[0]
        print(f"[create_query_hop2 instruction] extracted from {p}, chars={length}, score={score}")
        return instr

    return "Generate a compact second-hop BM25 search query from the question and first-hop summary."


def clean_lm_text(x):
    if x is None:
        return ""
    if isinstance(x, str):
        y = x.strip()
    elif isinstance(x, (list, tuple)):
        vals = [clean_lm_text(v) for v in x]
        y = next((v for v in vals if v), "")
    elif isinstance(x, dict):
        if "choices" in x and x["choices"]:
            vals = []
            for c in x["choices"]:
                if isinstance(c, dict):
                    msg = c.get("message") or {}
                    vals.append(msg.get("content") or c.get("text") or "")
            y = next((str(v).strip() for v in vals if str(v).strip()), "")
        else:
            vals = [clean_lm_text(v) for v in x.values()]
            y = next((v for v in vals if v), "")
    else:
        y = str(x).strip()

    y = re.sub(r"^```(?:text|json)?", "", y).strip()
    y = re.sub(r"```$", "", y).strip()
    return y.strip().strip('"').strip("'").strip()


def call_lm(prompt, retries=3):
    last = None
    sigs = [
        ("prompt -> response", "response"),
        ("prompt -> query", "query"),
        ("prompt -> text", "text"),
        ("prompt -> answer", "answer"),
        ("prompt -> output", "output"),
    ]
    for _ in range(retries):
        for sig, attr in sigs:
            try:
                pred = dspy.Predict(sig)(prompt=prompt)
                out = clean_lm_text(getattr(pred, attr, None))
                if out:
                    return out
            except Exception as e:
                last = e

        try:
            out = clean_lm_text(dspy.settings.lm(prompt))
            if out:
                return out
        except Exception as e:
            last = e

    if last:
        print("[warn] LLM failed:", repr(last), file=sys.stderr)
    return "EMPTY_LLM_OUTPUT"


def summarize_retrieval_delta(a, b):
    a_titles = list(a.get("retrieved_titles") or [])
    b_titles = list(b.get("retrieved_titles") or [])
    a_set = set(a_titles)
    b_set = set(b_titles)

    a_hit = as_set(a.get("recovered_missing_titles") or [])
    b_hit = as_set(b.get("recovered_missing_titles") or [])

    return {
        "from_arm": a.get("arm"),
        "to_arm": b.get("arm"),
        "from_query": a.get("query"),
        "to_query": b.get("query"),
        "from_mr": missing_recovery_rate(a),
        "to_mr": missing_recovery_rate(b),
        "newly_recovered_missing_titles": sorted([t for t in b_hit if t not in a_hit]),
        "recovered_after": sorted(b_hit),
        "retrieved_added_titles": [t for t in b_titles if t not in a_set][:8],
        "retrieved_removed_titles": [t for t in a_titles if t not in b_set][:8],
    }


def build_edges(g):
    states = [g["base"]] + g["steps"]
    return [summarize_retrieval_delta(a, b) for a, b in zip(states[:-1], states[1:])]


def compact_json(x):
    return json.dumps(x, ensure_ascii=False, indent=2)


def prompt_edge_to_pgrad(question, summary_1, edge):
    return f"""
Convert one retrieval edge into a local prompt-gradient descriptor.

This is NOT a query. This is a prompt update description that would make create_query_hop2 move from the BEFORE query toward the AFTER query.

Output exactly these fields:
TRIGGER:
KEEP:
ADD_OR_RESTORE:
REMOVE_OR_AVOID:
QUERY_SHAPE:
WHY_THIS_MOVES_RETRIEVAL:

Rules:
- Do not write a final query.
- Do not write a domain-specific rule.
- Express the update as behavior reusable inside this sample's create_query_hop2 prompt.
- Focus on BM25-relevant movement.
- Preserve useful anchors; restore missing bridge relation/type/alias/date clues; avoid noisy side entities.
- Do not say "use the gold title" or "retrieve the missing support".

Question:
{question}

summary_1:
{summary_1}

Retrieval edge:
{compact_json(edge)}
""".strip()


def prompt_compress_pgrads(question, summary_1, base_query, pgrads):
    return f"""
Compress the ordered step-level prompt gradients into ONE executable sample-level prompt update.

Output exactly these fields:
APPLY_WHEN:
KEEP:
RESTORE:
RETAIN:
DROP:
FINAL_QUERY_SHAPE:
NO_OP_IF:

Rules:
- This is a sample-specific prompt update, not a final query.
- Preserve cumulative intent across the ordered gradients.
- Do not average away decisive bridge cues.
- Prefer compact BM25 query behavior.
- Avoid generic placeholder language.
- Do not mention gold labels or evaluation metrics.
- Do not output a final query.

Question:
{question}

summary_1:
{summary_1}

Current/base query:
{base_query}

Ordered step-level prompt gradients:
{compact_json(pgrads)}
""".strip()


def prompt_direct_trace_compress(question, summary_1, base_query, edges):
    return f"""
Compress the ordered q-trace edges directly into ONE executable sample-level prompt update.

Output exactly these fields:
APPLY_WHEN:
KEEP:
RESTORE:
RETAIN:
DROP:
FINAL_QUERY_SHAPE:
NO_OP_IF:

Rules:
- This is a sample-specific prompt update, not a final query.
- Use retrieval edge behavior directly.
- Preserve stable anchors.
- Restore bridge relation/type/alias/date clues.
- Drop noisy side entities.
- Do not output a final query.

Question:
{question}

summary_1:
{summary_1}

Current/base query:
{base_query}

Ordered q-trace edges:
{compact_json(edges)}
""".strip()


def build_query_prompt(base_instruction, injection, question, summary_1, current_query):
    inj = ""
    if injection:
        inj = f"""
Sample-specific prompt update:
{injection}

Use this as an additional instruction for this sample only.
It describes how the hop2 query should move, not the final answer.
"""

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

{inj}

Output requirements:
- Output only one second-hop BM25 query.
- Keep it compact and keyword-like.
- Do not output explanations.
- Do not output the answer.
- Do not output placeholders such as missing_input, MISSING_CONTEXT, additional relevant documents, or search query.
""".strip()


def load_retriever(args):
    sys.path.insert(0, str(Path.cwd()))
    from examples.hotpotqa.retriever import search, set_retriever_dir

    retriever_dir = args.retriever_dir or os.environ.get("HOTPOT_RETRIEVER_DIR", "")
    if retriever_dir:
        set_retriever_dir(retriever_dir)

    k = int(args.retriever_k)
    print(f"[retriever] search(query, k={k})")
    if retriever_dir:
        print(f"[retriever] dir: {retriever_dir}")

    def _ret(q):
        return search(q, k)

    return _ret


def normalize_titles(out):
    if out is None:
        return []
    if hasattr(out, "passages"):
        return normalize_titles(getattr(out, "passages"))
    if hasattr(out, "docs"):
        return normalize_titles(getattr(out, "docs"))
    if hasattr(out, "titles"):
        return normalize_titles(getattr(out, "titles"))
    if isinstance(out, dict):
        for k in ["titles", "retrieved_titles", "passages", "docs", "ctxs", "contexts"]:
            if k in out:
                return normalize_titles(out[k])
        return []
    if isinstance(out, str):
        return [out.split(" | ", 1)[0].strip()]
    if isinstance(out, (list, tuple)):
        titles = []
        for x in out:
            if isinstance(x, str):
                titles.append(x.split(" | ", 1)[0].strip())
            elif isinstance(x, dict):
                t = x.get("title") or x.get("wikipedia_title") or x.get("page_title")
                if t:
                    titles.append(str(t).strip())
            elif hasattr(x, "title"):
                titles.append(str(getattr(x, "title")).strip())
            else:
                sx = str(x).strip()
                if sx:
                    titles.append(sx.split(" | ", 1)[0].strip())

        out_titles = []
        seen = set()
        for t in titles:
            if t and t not in seen:
                seen.add(t)
                out_titles.append(t)
        return out_titles
    return []


def score_titles(titles, gold_support_titles, missing_titles):
    got = as_set(titles)
    gold = as_set(gold_support_titles)
    missing = as_set(missing_titles)

    support_hit = got & gold
    missing_hit = got & missing

    return {
        "retrieved_titles": list(titles),
        "support_hit_count": len(support_hit),
        "support_recall_hop2": len(support_hit) / max(1, len(gold)),
        "recovered_missing_titles": sorted(missing_hit),
        "missing_recovered_count": len(missing_hit),
        "missing_recovery_rate": len(missing_hit) / max(1, len(missing)),
    }


def rollout(args, retrieve, base_instruction, idx, arm, injection, question, summary_1, current_query, gold_support_titles, missing_titles):
    prompt = build_query_prompt(base_instruction, injection, question, summary_1, current_query)
    query = call_lm(prompt, args.retries)
    titles = normalize_titles(retrieve(query))
    sc = score_titles(titles, gold_support_titles, missing_titles)
    return {
        "idx": idx,
        "arm": arm,
        "query": query,
        **sc,
        "meta": {
            "question": question,
            "summary_1": summary_1,
            "current_query": current_query,
            "injection": injection,
        },
    }


def process_one(args, row, qgroups, base_instruction, retrieve):
    idx = str(row["idx"])
    g = qgroups[idx]

    question = row.get("question", "")
    summary_1 = row.get("summary_1", "")
    current_query = g["base"].get("query") or row.get("qtrace_base_query") or row.get("matched_query") or ""
    gold_support_titles = g["base"].get("gold_support_titles") or row.get("gold_support_titles") or []
    missing_titles = g["base"].get("base_missing") or row.get("base_missing") or []

    edges = build_edges(g)

    pgrads = []
    for t, edge in enumerate(edges):
        pg = call_lm(prompt_edge_to_pgrad(question, summary_1, edge), args.retries)
        pgrads.append({
            "step": t,
            "edge_from": edge["from_arm"],
            "edge_to": edge["to_arm"],
            "pgrad": pg,
        })

    compressed_pgrad = call_lm(prompt_compress_pgrads(question, summary_1, current_query, pgrads), args.retries)
    direct_compressed = call_lm(prompt_direct_trace_compress(question, summary_1, current_query, edges), args.retries)

    raw_pgrad_list = "\n\n".join([f"STEP {x['step']} PROMPT_GRADIENT:\n{x['pgrad']}" for x in pgrads])

    rollouts = []
    rollouts.append(rollout(args, retrieve, base_instruction, idx, "prompt_current_query", "", question, summary_1, current_query, gold_support_titles, missing_titles))
    rollouts.append(rollout(args, retrieve, base_instruction, idx, "prompt_direct_trace_compressed", direct_compressed, question, summary_1, current_query, gold_support_titles, missing_titles))
    rollouts.append(rollout(args, retrieve, base_instruction, idx, "prompt_step_pgrad_rawlist", raw_pgrad_list, question, summary_1, current_query, gold_support_titles, missing_titles))
    rollouts.append(rollout(args, retrieve, base_instruction, idx, "prompt_step_pgrad_compressed", compressed_pgrad, question, summary_1, current_query, gold_support_titles, missing_titles))

    aux = {
        "idx": idx,
        "question": question,
        "summary_1": summary_1,
        "current_query": current_query,
        "edges": edges,
        "step_pgrads": pgrads,
        "compressed_pgrad": compressed_pgrad,
        "direct_compressed_trace": direct_compressed,
    }

    return rollouts, aux


def summarize_rows(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["arm"]].append(r)

    lines = []
    lines.append("# Stepwise P-Gradient Compression Probe\n")
    lines.append("| arm | n | mean MR | mean hop2 recall | mean recovered |")
    lines.append("|---|---:|---:|---:|---:|")
    for arm in sorted(by):
        xs = by[arm]
        n = len(xs)
        mr = sum(float(x.get("missing_recovery_rate") or 0) for x in xs) / max(1, n)
        h2 = sum(float(x.get("support_recall_hop2") or 0) for x in xs) / max(1, n)
        rec = sum(float(x.get("missing_recovered_count") or 0) for x in xs) / max(1, n)
        lines.append(f"| {arm} | {n} | {mr:.3f} | {h2:.3f} | {rec:.3f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qtrace-path", required=True)
    ap.add_argument("--meta-path", required=True)
    ap.add_argument("--base-prompt-candidate", required=True)
    ap.add_argument("--out-dir", required=True)

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

    base_instruction = load_create_query_instruction(args.base_prompt_candidate)
    (out_dir / "base_instruction.txt").write_text(base_instruction)

    qgroups = group_qtrace(read_jsonl(args.qtrace_path))
    meta_rows = read_jsonl(args.meta_path)

    rows = []
    for r in meta_rows:
        idx = str(r["idx"])
        if idx not in qgroups:
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
    print("[with summary_1]", sum(1 for r in rows if r.get("summary_1")))

    retrieve = load_retriever(args)

    all_rollouts = []
    aux_rows = []

    with ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(process_one, args, r, qgroups, base_instruction, retrieve) for r in rows]
        for fut in tqdm(as_completed(futs), total=len(futs), desc="stepwise pgrad"):
            rollouts, aux = fut.result()
            all_rollouts.extend(rollouts)
            aux_rows.append(aux)
            write_jsonl(out_dir / "rows.partial.jsonl", all_rollouts)
            write_jsonl(out_dir / "pgrad_aux.partial.jsonl", aux_rows)
            (out_dir / "summary.partial.md").write_text(summarize_rows(all_rollouts))

    write_jsonl(out_dir / "rows.jsonl", all_rollouts)
    write_jsonl(out_dir / "pgrad_aux.jsonl", aux_rows)
    (out_dir / "summary.md").write_text(summarize_rows(all_rollouts))

    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
