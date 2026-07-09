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


def missing_recovery_rate(row):
    return float(row.get("missing_recovery_rate") or 0.0)


def recovered_missing_count(row):
    return int(row.get("missing_recovered_count") or 0)


def support_recall_hop2(row):
    return float(row.get("support_recall_hop2") or 0.0)


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



def load_meta_maps(paths):
    meta = {}
    if not paths:
        return meta

    for raw_path in str(paths).split(","):
        raw_path = raw_path.strip()
        if not raw_path:
            continue
        p = Path(raw_path)
        if not p.exists():
            print(f"[meta] skip missing: {p}")
            continue

        n = 0
        with p.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue

                q = (
                    r.get("question")
                    or r.get("input_question")
                    or r.get("x")
                    or r.get("meta", {}).get("question")
                    or ""
                )
                s1 = (
                    r.get("summary_1")
                    or r.get("summary1")
                    or r.get("hop1_summary")
                    or r.get("meta", {}).get("summary_1")
                    or ""
                )

                if not q and not s1:
                    continue

                keys = []
                for k in ["idx", "eval_index", "example_index", "example_id", "_id", "id"]:
                    if k in r and r[k] is not None:
                        keys.append(str(r[k]))

                # Some qtrace idx values are eval_index-like.
                if "idx" not in r and "eval_index" in r:
                    keys.append(str(r["eval_index"]))

                for key in keys:
                    meta[key] = {
                        "question": q,
                        "summary_1": s1,
                        "source_path": str(p),
                    }
                    n += 1

        print(f"[meta] loaded {n} keyed entries from {p}")

    print(f"[meta] total keys: {len(meta)}")
    return meta


def lookup_meta(meta_map, idx, base):
    keys = [str(idx)]
    for k in ["idx", "eval_index", "example_index", "example_id", "_id", "id"]:
        if k in base and base[k] is not None:
            keys.append(str(base[k]))
        if isinstance(base.get("meta"), dict) and k in base["meta"] and base["meta"][k] is not None:
            keys.append(str(base["meta"][k]))

    for key in keys:
        if key in meta_map:
            return meta_map[key]

    return {}


def load_create_query_instruction(path):
    data = json.loads(Path(path).read_text())

    subtree = (
        find_key_subtree(data, "create_query_hop2")
        or find_key_subtree(data, "hop2")
        or data
    )

    strings = collect_strings(subtree)
    candidates = []
    for p, s in strings:
        ss = s.strip()
        if len(ss) < 40:
            continue
        score = 0
        low = ss.lower()
        for kw in ["query", "search", "question", "summary", "hop"]:
            if kw in low:
                score += 1
        candidates.append((score, len(ss), p, ss))

    if not candidates:
        print("[warn] could not extract create_query_hop2 instruction; using fallback")
        return "Generate a compact second-hop BM25 search query from the question and first-hop summary."

    candidates.sort(reverse=True)
    score, length, p, instr = candidates[0]
    print(f"[instruction] extracted from {p}, chars={length}, score={score}")
    return instr


def summarize_retrieval_delta(a, b):
    a_titles = list(a.get("retrieved_titles") or [])
    b_titles = list(b.get("retrieved_titles") or [])
    a_title_set = set(a_titles)
    b_title_set = set(b_titles)

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
        "retrieved_added_titles": [t for t in b_titles if t not in a_title_set][:8],
        "retrieved_removed_titles": [t for t in a_titles if t not in b_title_set][:8],
    }


def compact_json(x):
    return json.dumps(x, ensure_ascii=False, indent=2)


def raw_trace_block(edges):
    lines = []
    lines.append("Full retrieval trace hint:")
    lines.append("The following edges describe how better BM25 queries changed retrieval behavior.")
    lines.append("Use them as retrieval-behavior hints, not as gold answers.")
    for i, e in enumerate(edges):
        lines.append(f"\nEDGE {i}: {e['from_arm']} -> {e['to_arm']}")
        lines.append(f"- query before: {e['from_query']}")
        lines.append(f"- query after: {e['to_query']}")
        lines.append(f"- MR: {e['from_mr']:.3f} -> {e['to_mr']:.3f}")
        if e["newly_recovered_missing_titles"]:
            lines.append(f"- newly recovered missing titles: {e['newly_recovered_missing_titles']}")
        if e["retrieved_added_titles"]:
            lines.append(f"- added retrieved titles: {e['retrieved_added_titles']}")
        if e["retrieved_removed_titles"]:
            lines.append(f"- removed retrieved titles: {e['retrieved_removed_titles']}")
    return "\n".join(lines)



def _clean_lm_text(x):
    if x is None:
        return ""

    if isinstance(x, str):
        y = x.strip()
    elif isinstance(x, (list, tuple)):
        vals = [_clean_lm_text(v) for v in x]
        y = next((v for v in vals if v), "")
    elif isinstance(x, dict):
        # LiteLLM/OpenAI-like shapes
        if "choices" in x and x["choices"]:
            vals = []
            for c in x["choices"]:
                if isinstance(c, dict):
                    msg = c.get("message") or {}
                    vals.append(msg.get("content") or c.get("text") or "")
            y = next((str(v).strip() for v in vals if str(v).strip()), "")
        else:
            vals = [_clean_lm_text(v) for v in x.values()]
            y = next((v for v in vals if v), "")
    else:
        y = str(x).strip()

    y = re.sub(r"^```(?:text|json)?", "", y).strip()
    y = re.sub(r"```$", "", y).strip()
    y = y.strip('"').strip("'").strip()
    return y


def call_lm(prompt, max_retries=3):
    last = None

    # DSPy structured fallback signatures.
    sig_attrs = [
        ("prompt -> response", "response"),
        ("prompt -> query", "query"),
        ("prompt -> text", "text"),
        ("prompt -> answer", "answer"),
        ("prompt -> output", "output"),
    ]

    for _ in range(max_retries):
        for sig, attr in sig_attrs:
            try:
                pred = dspy.Predict(sig)(prompt=prompt)
                out = _clean_lm_text(getattr(pred, attr, None))
                if out:
                    return out
            except Exception as e:
                last = e

        # Direct LM fallback, bypassing DSPy output-field parsing.
        try:
            lm = dspy.settings.lm
            out = _clean_lm_text(lm(prompt))
            if out:
                return out
        except Exception as e:
            last = e

    # Last-resort debug aid: return a compact safe fallback rather than crashing.
    # This keeps the run alive; bad outputs will show up as low MR.
    print("[warn] empty LLM output after retries; returning fallback empty-query marker", file=sys.stderr)
    return "EMPTY_LLM_OUTPUT"


def prompt_structured_compress(question, summary_1, base_query, edges):
    return f"""
Compress the retrieval trace into a structured query-edit descriptor.

Output exactly these fields:
KEEP:
RESTORE:
RETAIN:
DROP:
STYLE:

Rules:
- KEEP should list stable anchors that should remain in the hop2 query.
- RESTORE should list bridge relations, aliases, title-type clues, or discriminating attributes needed for recovery.
- RETAIN should mention candidate sets or ambiguity that should not be collapsed too early.
- DROP should mention noisy side entities or overly broad context.
- STYLE should describe compact BM25 query form.
- Do not output a final query.
- Do not reveal gold answers as instructions.

Question:
{question}

First-hop summary:
{summary_1}

Base query:
{base_query}

Trace:
{compact_json(edges)}
""".strip()


def prompt_executable_compress(question, summary_1, base_query, edges):
    return f"""
Compress the retrieval trace into an executable query-edit plan for create_query_hop2.

Output exactly these fields:
TRIGGER:
PRESERVE:
ADD:
REMOVE:
FINAL_QUERY_SHAPE:
NO_OP_IF:

Rules:
- TRIGGER: when the edit should apply.
- PRESERVE: words/entities/relations to keep from question and summary.
- ADD: bridge/relation/title-type/candidate clues licensed by the trace.
- REMOVE: noisy terms to avoid.
- FINAL_QUERY_SHAPE: compact BM25 query shape, not a full sentence.
- NO_OP_IF: when the current query behavior should be preserved.
- Do not output a final query.
- Do not output answer literals.

Question:
{question}

First-hop summary:
{summary_1}

Base query:
{base_query}

Trace:
{compact_json(edges)}
""".strip()


def prompt_minimal_compress(question, summary_1, base_query, edges):
    return f"""
Compress the retrieval trace into the shortest useful retrieval hint.

Output exactly three lines:
STABLE_ANCHORS:
MISSING_BRIDGE:
QUERY_HINT:

Rules:
- Be minimal.
- Prefer 3 to 12 tokens per field.
- Focus only on what changes retrieval.
- Do not output a final query.
- Do not include answer literals unless they are already explicit in the question or first-hop summary.

Question:
{question}

First-hop summary:
{summary_1}

Base query:
{base_query}

Trace:
{compact_json(edges)}
""".strip()


def build_query_prompt(base_instruction, question, summary_1, injection, current_query=""):
    inj = injection.strip()
    cur = ""
    if current_query:
        cur = f"""
Current baseline hop2 query:
{current_query}

Use the current query as the starting point. Preserve useful anchors unless the guidance says they are noisy.
"""

    if inj:
        inj = f"""
Additional sample-specific retrieval guidance:
{inj}

Important:
- The guidance describes retrieval behavior, not the answer.
- Use it only to choose a better second-hop BM25 query.
- Do not copy recovered titles as answers.
- Do not output generic placeholders such as missing_input, MISSING_CONTEXT, additional relevant documents, or search query.
"""
    return f"""
You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.

Base create_query_hop2 instruction:
{base_instruction}

Inputs:
Question:
{question}

First-hop summary:
{summary_1}

{cur}

{inj}

Output requirements:
- Output only one second-hop BM25 query.
- Keep it compact and keyword-like.
- Do not output explanations.
- Do not output the answer.
- Do not output placeholders.
""".strip()


def load_retriever(args):
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
    if out is None:
        return []

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


def add_existing(outputs, idx, arm, row, question, summary_1):
    outputs.append({
        "idx": idx,
        "arm": arm,
        "source": "existing",
        "query": row.get("query"),
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


def run_group(args, g, base_instruction, retrieve_fn, meta_map):
    idx = g["idx"]
    base = g["base"]
    steps = g["steps"]
    target = g["target"]

    m = lookup_meta(meta_map, idx, base)
    question = (
        base.get("meta", {}).get("question")
        or base.get("question")
        or m.get("question")
        or ""
    )
    summary_1 = (
        base.get("meta", {}).get("summary_1")
        or base.get("summary_1")
        or m.get("summary_1")
        or ""
    )
    base_query = base.get("query")

    if not question:
        print(f"[warn] missing question for idx={idx}")
    if not summary_1:
        print(f"[warn] missing summary_1 for idx={idx}")

    states = [base] + steps
    edges = [summarize_retrieval_delta(a, b) for a, b in zip(states[:-1], states[1:])]

    outputs = []
    add_existing(outputs, idx, "base_existing", base, question, summary_1)
    add_existing(outputs, idx, "last_trace_existing", steps[-1], question, summary_1)
    add_existing(outputs, idx, "target_existing", target, question, summary_1)

    raw = raw_trace_block(edges)

    desc_structured = call_lm(prompt_structured_compress(question, summary_1, base_query, edges), args.retries)
    desc_executable = call_lm(prompt_executable_compress(question, summary_1, base_query, edges), args.retries)
    desc_minimal = call_lm(prompt_minimal_compress(question, summary_1, base_query, edges), args.retries)

    arms = [
        ("prompt_base", ""),
        ("prompt_current_query", "Use the current baseline query as the starting point. Improve it only if the input question and summary license a better compact BM25 query."),
        ("prompt_raw_trace", raw),
        ("prompt_structured_compression", desc_structured),
        ("prompt_executable_compression", desc_executable),
        ("prompt_minimal_compression", desc_minimal),
        ("prompt_raw_plus_executable", raw + "\n\nExecutable compressed plan:\n" + desc_executable),
        ("prompt_current_plus_minimal", "Use the current baseline query as the starting point. Apply this compressed trace hint:\n" + desc_minimal),
        ("prompt_current_plus_executable", "Use the current baseline query as the starting point. Apply this executable trace plan:\n" + desc_executable),
    ]

    for arm, injection in arms:
        prompt = build_query_prompt(base_instruction, question, summary_1, injection, current_query=base_query)
        q = call_lm(prompt, args.retries)
        titles = retrieve_fn(q)
        sc = score_titles(
            titles,
            base.get("gold_support_titles") or target.get("gold_support_titles") or [],
            base.get("base_missing") or target.get("base_missing") or [],
        )
        outputs.append({
            "idx": idx,
            "arm": arm,
            "source": "prompt_injection",
            "query": q,
            **sc,
            "meta": {
                "question": question,
                "summary_1": summary_1,
                "raw_trace": raw,
                "structured_descriptor": desc_structured,
                "executable_descriptor": desc_executable,
                "minimal_descriptor": desc_minimal,
            },
        })

    return outputs


def summarize(rows):
    by_arm = defaultdict(list)
    for r in rows:
        by_arm[r["arm"]].append(r)

    lines = []
    lines.append("# Full Trace Prompt Injection Probe\n")
    lines.append("| arm | n | mean MR | mean hop2 recall | mean recovered |")
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
    ap.add_argument("--base-prompt-candidate", required=True)
    ap.add_argument("--meta-rows-path", default="", help="comma-separated jsonl files containing question/summary_1 keyed by idx/eval_index")
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

    base_instruction = load_create_query_instruction(args.base_prompt_candidate)
    meta_map = load_meta_maps(args.meta_rows_path)
    (out_dir / "base_instruction.txt").write_text(base_instruction)

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
        futs = [ex.submit(run_group, args, g, base_instruction, retrieve_fn, meta_map) for g in groups]
        for fut in tqdm(as_completed(futs), total=len(futs), desc="prompt-injection groups"):
            outs = fut.result()
            all_rows.extend(outs)
            write_jsonl(out_dir / "rows.partial.jsonl", all_rows)
            (out_dir / "summary.partial.md").write_text(summarize(all_rows))

    write_jsonl(out_dir / "rows.jsonl", all_rows)
    (out_dir / "summary.md").write_text(summarize(all_rows))

    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
