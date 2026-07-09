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
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
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


def is_trace_arm(arm):
    return arm == "base_query" or arm == "target_query" or str(arm).startswith("trace_step_")


def group_qtrace(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["idx"]].append(r)

    groups = []
    for idx, xs in sorted(by.items()):
        trace = []
        for r in xs:
            o = arm_order(r.get("arm"))
            if o is not None:
                trace.append((o, r))
        trace = [r for _, r in sorted(trace, key=lambda x: x[0])]

        # remove target from normal trace states
        base = next((r for r in trace if r.get("arm") == "base_query"), None)
        target = next((r for r in trace if r.get("arm") == "target_query"), None)
        steps = [r for r in trace if str(r.get("arm", "")).startswith("trace_step_")]

        if base and steps and target:
            groups.append({
                "idx": idx,
                "base": base,
                "steps": steps,
                "target": target,
            })
    return groups


def recovered_missing_count(row):
    return int(row.get("missing_recovered_count") or 0)


def missing_recovery_rate(row):
    return float(row.get("missing_recovery_rate") or 0.0)


def support_recall_hop2(row):
    return float(row.get("support_recall_hop2") or 0.0)


def metric_score(row):
    # Primary: missing recovery. Secondary: hop2 support recall.
    return (
        missing_recovery_rate(row),
        support_recall_hop2(row),
        recovered_missing_count(row),
    )


def summarize_retrieval_delta(a, b):
    a_titles = list(a.get("retrieved_titles") or [])
    b_titles = list(b.get("retrieved_titles") or [])
    a_hit = as_set(a.get("recovered_missing_titles") or [])
    b_hit = as_set(b.get("recovered_missing_titles") or [])

    added_titles = [t for t in b_titles if t not in set(a_titles)]
    removed_titles = [t for t in a_titles if t not in set(b_titles)]
    newly_recovered = [t for t in b_hit if t not in a_hit]

    return {
        "from_arm": a.get("arm"),
        "to_arm": b.get("arm"),
        "from_query": a.get("query"),
        "to_query": b.get("query"),
        "from_mr": missing_recovery_rate(a),
        "to_mr": missing_recovery_rate(b),
        "from_recovered": list(a_hit),
        "to_recovered": list(b_hit),
        "newly_recovered": newly_recovered,
        "retrieved_added_titles": added_titles[:8],
        "retrieved_removed_titles": removed_titles[:8],
        "gold_support_titles": b.get("gold_support_titles") or a.get("gold_support_titles") or [],
        "missing_titles": b.get("base_missing") or a.get("base_missing") or [],
    }


def best_single_edge(base, steps):
    states = [base] + steps
    best = None
    for a, b in zip(states[:-1], states[1:]):
        delta = missing_recovery_rate(b) - missing_recovery_rate(a)
        rec_delta = recovered_missing_count(b) - recovered_missing_count(a)
        key = (delta, rec_delta, missing_recovery_rate(b), support_recall_hop2(b))
        if best is None or key > best[0]:
            best = (key, a, b)
    return best[1], best[2]


def compact_json(x):
    return json.dumps(x, ensure_ascii=False, indent=2)


def call_lm(prompt, max_retries=3):
    last = None
    for _ in range(max_retries):
        try:
            pred = dspy.Predict("prompt -> query")(prompt=prompt)
            q = str(pred.query).strip()
            q = re.sub(r"^```(?:text|json)?", "", q).strip()
            q = re.sub(r"```$", "", q).strip()
            q = q.strip('"').strip("'").strip()
            if q:
                return q
        except Exception as e:
            last = e
    if last:
        raise last
    raise RuntimeError("empty LLM output")


def prompt_single_edge(question, summary_1, current_query, edge):
    return f"""
You are rewriting the second-hop BM25 query for a two-hop HotpotQA retriever.

Goal:
Apply one local retrieval edge to the current query.

Rules:
- Output only one compact BM25 query.
- Preserve source anchors from the current query unless the edge clearly shows they are noise.
- Restore the missing bridge relation or discriminating clue implied by the edge.
- Do not output the answer.
- Do not output a sentence.
- Prefer compact entity/relation/title keywords.
- Avoid broad synonym expansion.

Question:
{question}

First-hop summary:
{summary_1}

Current query:
{current_query}

Local retrieval edge:
{compact_json(edge)}

Write the updated BM25 query only.
""".strip()


def prompt_full_trace_all(question, summary_1, base_query, edges):
    return f"""
You are rewriting the second-hop BM25 query for a two-hop HotpotQA retriever.

Goal:
Use the full retrieval trace to produce one final compact BM25 query.

Rules:
- Output only one compact BM25 query.
- Treat the trace as a sequence of local movements toward better missing-support recovery.
- Preserve stable source anchors.
- Restore bridge relations, aliases, title-type clues, or discriminating attributes that repeatedly help.
- Drop noisy side entities that the trace moves away from.
- Do not concatenate every trace token.
- Do not output the answer.
- Avoid verbose natural language.

Question:
{question}

First-hop summary:
{summary_1}

Base query:
{base_query}

Full retrieval trace edges:
{compact_json(edges)}

Write the final BM25 query only.
""".strip()


def prompt_compress_trace(question, summary_1, base_query, edges):
    return f"""
Compress this retrieval trace into a short query-edit descriptor.

Output only a compact descriptor, not a query.

Descriptor should mention:
- KEEP anchors
- RESTORE bridge/relation clues
- RETAIN candidate set if useful
- DROP noise
- STYLE constraints for BM25

Question:
{question}

First-hop summary:
{summary_1}

Base query:
{base_query}

Trace edges:
{compact_json(edges)}
""".strip()


def prompt_apply_compressed(question, summary_1, base_query, descriptor):
    return f"""
You are rewriting the second-hop BM25 query for a two-hop HotpotQA retriever.

Goal:
Apply the compressed trace descriptor to the base query.

Rules:
- Output only one compact BM25 query.
- Use the descriptor as a query-edit instruction.
- Do not output the answer.
- Avoid verbose natural language.

Question:
{question}

First-hop summary:
{summary_1}

Base query:
{base_query}

Compressed trace descriptor:
{descriptor}

Write the final BM25 query only.
""".strip()


# ---- retrieval loading ----


def load_retriever(args):
    """
    Use the HotpotQA BM25 retriever directly.

    Expected project interface:
      from examples.hotpotqa.retriever import search, set_retriever_dir
      search(query, k).passages

    Passage strings usually look like:
      "Title | passage text"
    """
    repo = Path.cwd()
    sys.path.insert(0, str(repo))

    from examples.hotpotqa.retriever import search, set_retriever_dir

    retriever_dir = args.retriever_dir or os.environ.get("HOTPOT_RETRIEVER_DIR", "")
    if retriever_dir:
        set_retriever_dir(retriever_dir)

    k = int(getattr(args, "retriever_k", 7))
    print(f"[retriever] using examples.hotpotqa.retriever.search(query, k={k})")
    if retriever_dir:
        print(f"[retriever] dir: {retriever_dir}")

    def _ret(q):
        out = search(q, k)
        return normalize_retrieval_output(out)

    return _ret



def normalize_retrieval_output(out):
    """
    Return list of titles.

    Handles:
    - search(query, k).passages
    - object.passages
    - dict with passages/docs/titles
    - list[str] passage strings like "title | text"
    - list[dict] with title/page_title/wikipedia_title
    """
    if out is None:
        return []

    # bm25s SearchResult-like object
    if hasattr(out, "passages"):
        return normalize_retrieval_output(getattr(out, "passages"))

    if hasattr(out, "docs"):
        return normalize_retrieval_output(getattr(out, "docs"))

    if hasattr(out, "titles"):
        return normalize_retrieval_output(getattr(out, "titles"))

    if isinstance(out, dict):
        for k in ["titles", "retrieved_titles", "passages", "docs", "ctxs", "contexts"]:
            if k in out:
                return normalize_retrieval_output(out[k])
        return []

    if isinstance(out, str):
        # Passage format: "Title | text"
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

        # preserve order, remove duplicates
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


def run_group(args, g, retrieve_fn):
    idx = g["idx"]
    base = g["base"]
    steps = g["steps"]
    target = g["target"]

    question = base.get("meta", {}).get("question") or base.get("question") or ""
    summary_1 = base.get("meta", {}).get("summary_1") or base.get("summary_1") or ""
    base_query = base.get("query")

    states = [base] + steps
    edges = [summarize_retrieval_delta(a, b) for a, b in zip(states[:-1], states[1:])]

    best_a, best_b = best_single_edge(base, steps)
    best_edge = summarize_retrieval_delta(best_a, best_b)

    outputs = []

    def add_existing(name, row):
        outputs.append({
            "idx": idx,
            "arm": name,
            "query": row.get("query"),
            "source": "existing",
            "missing_recovery_rate": missing_recovery_rate(row),
            "missing_recovered_count": recovered_missing_count(row),
            "support_recall_hop2": support_recall_hop2(row),
            "retrieved_titles": row.get("retrieved_titles") or [],
            "recovered_missing_titles": row.get("recovered_missing_titles") or [],
            "gold_support_titles": row.get("gold_support_titles") or [],
            "missing_titles": row.get("base_missing") or [],
            "meta": {
                "question": question,
                "summary_1": summary_1,
            },
        })

    add_existing("base_existing", base)
    add_existing("best_single_existing", best_b)
    add_existing("last_trace_existing", steps[-1])
    add_existing("target_existing", target)

    generated = []

    # LLM single best edge
    q_single = call_lm(prompt_single_edge(question, summary_1, base_query, best_edge), args.retries)
    generated.append(("llm_single_best_edge", q_single, {"best_edge": best_edge}))

    # LLM sequential trace
    q_seq = base_query
    seq_queries = []
    for t, e in enumerate(edges):
        q_seq = call_lm(prompt_single_edge(question, summary_1, q_seq, e), args.retries)
        seq_queries.append(q_seq)
    generated.append(("llm_seq_trace", q_seq, {"seq_queries": seq_queries, "edges": edges}))

    # LLM all trace single-turn
    q_all = call_lm(prompt_full_trace_all(question, summary_1, base_query, edges), args.retries)
    generated.append(("llm_all_trace", q_all, {"edges": edges}))

    # compressed descriptor
    desc = call_lm(prompt_compress_trace(question, summary_1, base_query, edges), args.retries)
    q_comp = call_lm(prompt_apply_compressed(question, summary_1, base_query, desc), args.retries)
    generated.append(("llm_compressed_trace", q_comp, {"compressed_descriptor": desc, "edges": edges}))

    for arm, q, extra in generated:
        titles = retrieve_fn(q)
        sc = score_titles(
            titles,
            base.get("gold_support_titles") or target.get("gold_support_titles") or [],
            base.get("base_missing") or target.get("base_missing") or [],
        )
        outputs.append({
            "idx": idx,
            "arm": arm,
            "query": q,
            "source": "generated",
            **sc,
            "meta": {
                "question": question,
                "summary_1": summary_1,
                **extra,
            },
        })

    return outputs


def summarize(rows):
    by_arm = defaultdict(list)
    for r in rows:
        by_arm[r["arm"]].append(r)

    lines = []
    lines.append("# Q-trace accumulation probe\n")
    lines.append("| arm | n | mean MR | mean hop2 recall | mean recovered count |")
    lines.append("|---|---:|---:|---:|---:|")

    for arm in sorted(by_arm):
        xs = by_arm[arm]
        n = len(xs)
        mean_mr = sum(float(x.get("missing_recovery_rate") or 0) for x in xs) / max(1, n)
        mean_rec = sum(float(x.get("missing_recovered_count") or 0) for x in xs) / max(1, n)
        mean_hop2 = sum(float(x.get("support_recall_hop2") or 0) for x in xs) / max(1, n)
        lines.append(f"| {arm} | {n} | {mean_mr:.3f} | {mean_hop2:.3f} | {mean_rec:.3f} |")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qtrace-path", default="experiments/deltaq/results_retrieval_gain_gpt5mini_full/bm25_validation.jsonl")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--limit", type=int, default=0)
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

    rows = read_jsonl(args.qtrace_path)
    groups = group_qtrace(rows)
    if args.limit:
        groups = groups[:args.limit]

    print("[groups]", len(groups))

    lm_kwargs = {
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_base:
        lm_kwargs["api_base"] = args.api_base

    dspy.settings.configure(lm=dspy.LM(**lm_kwargs))

    retrieve_fn = load_retriever(args)

    all_rows = []
    with ThreadPoolExecutor(max_workers=args.num_threads) as ex:
        futs = [ex.submit(run_group, args, g, retrieve_fn) for g in groups]
        for fut in tqdm(as_completed(futs), total=len(futs), desc="qtrace groups"):
            outs = fut.result()
            all_rows.extend(outs)
            write_jsonl(out_dir / "rows.partial.jsonl", all_rows)
            (out_dir / "summary.partial.md").write_text(summarize(all_rows))

    write_jsonl(out_dir / "rows.jsonl", all_rows)
    (out_dir / "summary.md").write_text(summarize(all_rows))

    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
