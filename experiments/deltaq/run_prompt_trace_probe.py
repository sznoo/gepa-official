import argparse
import json
import os
import random
import time
from collections import defaultdict
from pathlib import Path

import dspy

from examples.hotpotqa.retriever import search, set_retriever_dir


try:
    from tqdm.auto import tqdm
except Exception:
    def tqdm(iterable, **kwargs):
        return iterable


DEFAULT_SRC = (
    "outputs/hotpotqa_representation_prompt_screening/"
    "rep_prompt_screening_24_dev300_final_v2/"
    "case_study_R6_best_vs_final_manual/retrieval_gain.jsonl"
)


PROMPT_TRACE = [
    {
        "arm": "p0_generic_rewrite",
        "step": 0,
        "name": "generic rewrite",
        "instruction": """
Rewrite the weak query into a better evidence-retrieval query.
""".strip(),
    },
    {
        "arm": "p1_compact_keyword",
        "step": 1,
        "name": "compact keyword",
        "instruction": """
Rewrite the weak query as a compact BM25 keyword query.
Use keywords and short phrases, not a full sentence.
Remove verbosity.
""".strip(),
    },
    {
        "arm": "p2_compact_anchor",
        "step": 2,
        "name": "compact + anchors",
        "instruction": """
Rewrite the weak query as a compact BM25 keyword query.
Preserve concrete names, titles, aliases, dates, and candidate entities.
Use keywords and short phrases, not a full sentence.
Remove verbosity.
""".strip(),
    },
    {
        "arm": "p3_candidate_set",
        "step": 3,
        "name": "compact + anchors + candidates",
        "instruction": """
Rewrite the weak query as a compact BM25 keyword query.
Preserve concrete names, titles, aliases, dates, and candidate entities.
If multiple candidates or aliases are uncertain, keep them as a compact candidate set.
Do not collapse uncertain candidates into one.
Use keywords and short phrases, not a full sentence.
Remove verbosity.
""".strip(),
    },
    {
        "arm": "p4_anchor_relation",
        "step": 4,
        "name": "candidate + relation",
        "instruction": """
Rewrite the weak query as a compact BM25 keyword query.
Preserve concrete names, titles, aliases, dates, and candidate entities.
If multiple candidates or aliases are uncertain, keep them as a compact candidate set.
Include relation words that identify the needed evidence page.
Prefer terms that connect the source entity to the missing support page.
Use keywords and short phrases, not a full sentence.
Remove verbosity.
""".strip(),
    },
    {
        "arm": "p5_noise_guard",
        "step": 5,
        "name": "candidate + relation + noise guard",
        "instruction": """
Rewrite the weak query as a compact BM25 keyword query.
Preserve concrete names, titles, aliases, dates, and candidate entities.
If multiple candidates or aliases are uncertain, keep them as a compact candidate set.
Include relation words that identify the needed evidence page.
Prefer terms that connect the source entity to the missing support page.
Remove side entities and side relations that may dominate retrieval but are not needed for the evidence page.
Avoid locking the query onto a distractor page.
Use keywords and short phrases, not a full sentence.
""".strip(),
    },
    {
        "arm": "p6_no_boolean_guard",
        "step": 6,
        "name": "full guard",
        "instruction": """
Rewrite the weak query as a compact BM25 keyword query.
Preserve concrete names, titles, aliases, dates, and candidate entities.
If multiple candidates or aliases are uncertain, keep them as a compact candidate set.
Include relation words that identify the needed evidence page.
Prefer terms that connect the source entity to the missing support page.
Remove side entities and side relations that may dominate retrieval but are not needed for the evidence page.
Avoid locking the query onto a distractor page.

Important BM25 constraints:
- BM25 treats the query as keywords, not Boolean logic.
- Do not use OR/AND-style Boolean syntax.
- Do not use long parenthesized expansions.
- Do not write a web-search-style query with many alternatives.
- Use only the most useful lexical cues.

Output only the rewritten query.
""".strip(),
    },
]


def load_env_file(path):
    path = Path(path)
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file(Path(__file__).resolve().parents[2] / ".env")


def resolve_api_key(model: str, explicit_api_key: str | None):
    if explicit_api_key:
        return explicit_api_key

    if model.startswith("openai/"):
        return os.environ.get("OPENAI_API_KEY") or os.environ.get("TASK_API_KEY") or "dummy"

    return os.environ.get("TASK_API_KEY") or os.environ.get("OPENAI_API_KEY") or "dummy"


def load_jsonl(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def title_of(passage):
    return passage.split(" | ", 1)[0]


def retrieve_titles(query, k):
    passages = search(query, k=k).passages
    return [title_of(p) for p in passages], passages


def rank_of(title, titles):
    for i, t in enumerate(titles, start=1):
        if t == title:
            return i
    return None


def random_drop(query, seed, drop_ratio=0.3):
    rng = random.Random(seed)
    toks = query.split()
    kept = [t for t in toks if rng.random() > drop_ratio]
    return " ".join(kept) if kept else query


def clean_query(raw):
    s = str(raw).strip()

    if s.startswith("```"):
        lines = s.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        s = "\n".join(lines).strip()

    prefixes = [
        "Query:",
        "Rewritten query:",
        "Search query:",
        "BM25 query:",
        "Answer:",
    ]
    for p in prefixes:
        if s.lower().startswith(p.lower()):
            s = s[len(p):].strip()

    s = s.strip().strip('"').strip("'")
    s = " ".join(s.split())
    return s


def lm_call(lm, prompt, retries=3, sleep_s=2.0):
    last_error = None
    for attempt in range(retries):
        try:
            out = lm(prompt)
            if isinstance(out, list):
                out = out[0]
            return clean_query(out), None
        except Exception as e:
            last_error = str(e)
            if attempt + 1 < retries:
                time.sleep(sleep_s * (attempt + 1))

    return None, last_error


def make_prompt(ex, spec, input_mode):
    if input_mode == "weak_query":
        return f"""
You are rewriting a second-hop retrieval query for BM25.

Task:
{spec["instruction"]}

Rules:
- Do not answer the question.
- Do not mention retrieved documents.
- Do not use gold answers.
- Output only the rewritten query.

Question:
{ex["question"]}

Weak query:
{ex["base_hop2_query"]}
""".strip()

    if input_mode == "question_only":
        return f"""
You are writing a second-hop retrieval query for BM25.

Task:
{spec["instruction"].replace("Rewrite the weak query", "Write a retrieval query for the question")}

Rules:
- Do not answer the question.
- Do not mention retrieved documents.
- Do not use gold answers.
- Output only the query.

Question:
{ex["question"]}
""".strip()

    raise ValueError(f"Unknown input_mode: {input_mode}")


def build_candidates(ex, lm, input_mode, retries):
    rows = []

    rows.append({
        "idx": ex["idx"],
        "arm": "base_query",
        "query": ex["base_hop2_query"],
        "meta": {
            "source": "given",
            "step": -2,
            "input_mode": input_mode,
        },
    })

    rows.append({
        "idx": ex["idx"],
        "arm": "target_query",
        "query": ex["cand_hop2_query"],
        "meta": {
            "source": "given",
            "step": -1,
            "input_mode": input_mode,
        },
    })

    rows.append({
        "idx": ex["idx"],
        "arm": "random_drop",
        "query": random_drop(ex["base_hop2_query"], seed=ex["idx"]),
        "meta": {
            "source": "control",
            "step": -1,
            "input_mode": input_mode,
        },
    })

    for spec in PROMPT_TRACE:
        prompt = make_prompt(ex, spec, input_mode=input_mode)
        query, error = lm_call(lm, prompt, retries=retries)

        rows.append({
            "idx": ex["idx"],
            "arm": spec["arm"],
            "query": query,
            "meta": {
                "source": "llm_prompt_trace",
                "step": spec["step"],
                "name": spec["name"],
                "instruction": spec["instruction"],
                "input_mode": input_mode,
                "prompt": prompt,
                "error": error,
            },
        })

    return rows


def validate_candidate(ex, cand, k):
    query = cand["query"]
    if not query:
        return None

    titles, passages = retrieve_titles(query, k=k)

    support = set(ex["gold_support_titles"])
    base_missing = set(ex["base_missing"])

    hit_support = sorted(support & set(titles))
    recovered_missing = sorted(base_missing & set(titles))

    return {
        "idx": ex["idx"],
        "arm": cand["arm"],
        "query": query,

        "retrieved_titles": titles,
        "hit_support_titles": hit_support,
        "recovered_missing_titles": recovered_missing,

        "support_hit_count": len(hit_support),
        "missing_recovered_count": len(recovered_missing),
        "support_recall_hop2": len(hit_support) / max(1, len(support)),
        "missing_recovery_rate": len(recovered_missing) / max(1, len(base_missing)),

        "target_ranks": {t: rank_of(t, titles) for t in ex["gold_support_titles"]},

        "gold_support_titles": ex["gold_support_titles"],
        "base_missing": ex["base_missing"],
        "base_query": ex["base_hop2_query"],
        "target_query": ex["cand_hop2_query"],
        "base_hop2_titles": ex["base_hop2_titles"],
        "target_hop2_titles": ex["cand_hop2_titles"],

        "meta": cand["meta"],
    }


def arm_sort_key(arm):
    control_order = {
        "base_query": -3,
        "random_drop": -2,
        "target_query": -1,
    }
    if arm in control_order:
        return (control_order[arm], arm)

    for spec in PROMPT_TRACE:
        if arm == spec["arm"]:
            return (spec["step"], arm)

    return (999, arm)


def summarize(rows):
    stats = defaultdict(lambda: {
        "n": 0,
        "support_recall_hop2": 0.0,
        "missing_recovery_rate": 0.0,
        "any_support_hit": 0,
        "any_missing_recovered": 0,
    })

    for r in rows:
        s = stats[r["arm"]]
        s["n"] += 1
        s["support_recall_hop2"] += r["support_recall_hop2"]
        s["missing_recovery_rate"] += r["missing_recovery_rate"]
        s["any_support_hit"] += int(r["support_hit_count"] > 0)
        s["any_missing_recovered"] += int(r["missing_recovered_count"] > 0)

    lines = []
    lines.append("| arm | n | support recall hop2 | missing recovery | any support hit | any missing recovered |")
    lines.append("|---|---:|---:|---:|---:|---:|")

    for arm, s in sorted(stats.items(), key=lambda kv: arm_sort_key(kv[0])):
        n = s["n"]
        lines.append(
            f"| {arm} | {n} | "
            f"{s['support_recall_hop2'] / n:.3f} | "
            f"{s['missing_recovery_rate'] / n:.3f} | "
            f"{s['any_support_hit'] / n:.3f} | "
            f"{s['any_missing_recovered'] / n:.3f} |"
        )

    return "\n".join(lines)


def summarize_prompt_trace(rows):
    trace_rows = [r for r in rows if r["arm"].startswith("p")]
    by_step = defaultdict(lambda: {
        "n": 0,
        "support_recall_hop2": 0.0,
        "missing_recovery_rate": 0.0,
        "any_support_hit": 0,
        "any_missing_recovered": 0,
    })

    for r in trace_rows:
        step = r.get("meta", {}).get("step")
        key = f"step_{step}_{r['arm']}"
        s = by_step[key]
        s["n"] += 1
        s["support_recall_hop2"] += r["support_recall_hop2"]
        s["missing_recovery_rate"] += r["missing_recovery_rate"]
        s["any_support_hit"] += int(r["support_hit_count"] > 0)
        s["any_missing_recovered"] += int(r["missing_recovered_count"] > 0)

    lines = []
    lines.append("# Prompt trace only")
    lines.append("")
    lines.append("| step | n | support recall hop2 | missing recovery | any support hit | any missing recovered |")
    lines.append("|---|---:|---:|---:|---:|---:|")

    for key, s in sorted(by_step.items()):
        n = s["n"]
        lines.append(
            f"| {key} | {n} | "
            f"{s['support_recall_hop2'] / n:.3f} | "
            f"{s['missing_recovery_rate'] / n:.3f} | "
            f"{s['any_support_hit'] / n:.3f} | "
            f"{s['any_missing_recovered'] / n:.3f} |"
        )

    return "\n".join(lines)


def write_case_report(validations, out_path):
    by_idx = defaultdict(dict)
    for r in validations:
        by_idx[r["idx"]][r["arm"]] = r

    lines = []
    for idx, arms in sorted(by_idx.items()):
        base = arms.get("base_query")
        if not base:
            continue

        lines.append("\n" + "=" * 100)
        lines.append(f"idx: {idx}")
        lines.append(f"gold_support_titles: {base['gold_support_titles']}")
        lines.append(f"base_missing: {base['base_missing']}")
        lines.append(f"base_query: {base['base_query']}")
        lines.append(f"target_query: {base['target_query']}")

        for arm in sorted(arms, key=arm_sort_key):
            r = arms[arm]
            lines.append("")
            lines.append(
                f"[{arm}] missing_recovery={r['missing_recovery_rate']:.3f} "
                f"support_recall={r['support_recall_hop2']:.3f}"
            )
            lines.append(f"query: {r['query']}")
            lines.append(f"hits: {r['hit_support_titles']}")
            lines.append(f"recovered: {r['recovered_missing_titles']}")
            lines.append(f"titles: {r['retrieved_titles']}")

    Path(out_path).write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=DEFAULT_SRC)
    parser.add_argument("--out-dir", default="experiments/deltaq/results_prompt_trace_gpt5mini")
    parser.add_argument("--retriever-dir", default=os.environ.get("HOTPOT_RETRIEVER_DIR"))
    parser.add_argument("--k", type=int, default=7)
    parser.add_argument("--limit", type=int, default=None)

    parser.add_argument("--input-mode", choices=["weak_query", "question_only"], default="weak_query")

    parser.add_argument("--model", default=os.environ.get("TASK_MODEL", "openai/gpt-5-mini"))
    parser.add_argument("--api-base", default=os.environ.get("TASK_API_BASE", ""))
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=16000)
    parser.add_argument("--retries", type=int, default=3)

    args = parser.parse_args()

    if "gpt-5" in args.model:
        if args.temperature not in (1.0, None):
            print(f"[warn] GPT-5 model requires temperature=1.0 or None. Overriding {args.temperature} -> 1.0")
            args.temperature = 1.0
        if args.max_tokens is not None and args.max_tokens < 16000:
            print(f"[warn] GPT-5 model requires max_tokens>=16000 or None. Overriding {args.max_tokens} -> 16000")
            args.max_tokens = 16000

    if args.retriever_dir:
        set_retriever_dir(args.retriever_dir)

    api_key = resolve_api_key(args.model, args.api_key)
    lm_kwargs = {
        "api_key": api_key,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_base:
        lm_kwargs["api_base"] = args.api_base

    lm = dspy.LM(args.model, **lm_kwargs)

    examples = list(load_jsonl(args.src))
    if args.limit is not None:
        examples = examples[:args.limit]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[info] examples: {len(examples)}")
    print(f"[info] source: {args.src}")
    print(f"[info] out_dir: {out_dir}")
    print(f"[info] k: {args.k}")
    print(f"[info] input_mode: {args.input_mode}")
    print(f"[info] model: {args.model}")
    print(f"[info] temperature: {args.temperature}")
    print(f"[info] max_tokens: {args.max_tokens}")

    all_candidates = []
    validations = []

    ex_iter = tqdm(examples, desc="Prompt-trace examples", unit="ex", dynamic_ncols=True)

    for ex in ex_iter:
        ex_iter.set_postfix({"idx": ex.get("idx")})

        cands = build_candidates(
            ex,
            lm=lm,
            input_mode=args.input_mode,
            retries=args.retries,
        )
        all_candidates.extend(cands)

        cand_iter = tqdm(
            cands,
            desc=f"BM25 validate idx={ex.get('idx')}",
            unit="cand",
            leave=False,
            dynamic_ncols=True,
        )

        for cand in cand_iter:
            cand_iter.set_postfix({"arm": cand.get("arm")})
            val = validate_candidate(ex, cand, k=args.k)
            if val is not None:
                validations.append(val)

    cand_path = out_dir / "prompt_trace_queries.jsonl"
    val_path = out_dir / "bm25_validation.jsonl"
    summary_path = out_dir / "summary.md"
    trace_summary_path = out_dir / "summary_prompt_trace.md"
    case_report_path = out_dir / "case_report.txt"

    with cand_path.open("w") as f:
        for r in all_candidates:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with val_path.open("w") as f:
        for r in validations:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    summary = summarize(validations)
    trace_summary = summarize_prompt_trace(validations)

    summary_path.write_text(summary)
    trace_summary_path.write_text(trace_summary)
    write_case_report(validations, case_report_path)

    print()
    print("queries:", cand_path)
    print("validation:", val_path)
    print("summary:", summary_path)
    print("prompt trace summary:", trace_summary_path)
    print("case report:", case_report_path)
    print()
    print(summary)
    print()
    print(trace_summary)


if __name__ == "__main__":
    main()
