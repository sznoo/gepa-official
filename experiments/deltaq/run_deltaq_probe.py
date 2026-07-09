import argparse
import json
import os
import random
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


EDIT_TYPES = [
    "keep_anchor",
    "restore_missing_anchor",
    "restore_missing_relation",
    "add_answer_type",
    "retain_candidate_set",
    "remove_noisy_entity",
    "remove_noisy_relation",
    "replace_wrong_focus",
    "canonicalize_surface_form",
    "compact_query",
    "STOP",
]


ARMS = {
    "generic_good": "Rewrite the weak query into a better evidence-retrieval query.",
    "compact_only": "Make the weak query shorter. Keep only central concrete keywords.",
    "expansion_only": "Expand the weak query with useful entities, aliases, relation words, and answer-type cues.",
    "relation_only": "Keep named entities mostly fixed. Modify only relation, action, or type words.",
    "anchor_only": "Keep only concrete names, titles, dates, aliases, and candidate entities. Remove abstract phrasing.",
    "candidate_set": "If multiple candidates appear, keep them as an uncertain candidate set. Do not collapse to one.",
    "wrong_focus_relax": "If the query is locked onto one interpretation, relax that focus while preserving the original intent.",
    "paraphrase": "Paraphrase the query without adding or removing major entities or relations.",
}


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


def lm_call(lm, prompt):
    out = lm(prompt)
    if isinstance(out, list):
        out = out[0]
    return str(out).strip()


def rewrite_prompt(ex, arm):
    return f"""
You are given a question and a weak retrieval query.

{ARMS[arm]}

Rules:
- Output only the rewritten query.
- Do not answer the question.
- Do not mention retriever-specific scoring rules.
- Do not use gold answers or retrieved document titles.

Question:
{ex["question"]}

Weak query:
{ex["base_hop2_query"]}
""".strip()


def trace_prompt(ex):
    return f"""
You are given a question, a weak retrieval query, and a stronger target retrieval query.

Decompose the change from the weak query to the target query into at most 4 minimal, interpretable query edits.

The query is used to retrieve evidence documents. Do not answer the question. Do not use or mention retriever-specific scoring rules.

Return valid JSON only with this schema:
{{
  "trace": [
    {{
      "step": 1,
      "edit_type": "...",
      "query_after": "...",
      "changed_context": "...",
      "intended_retrieval_effect": "..."
    }},
    {{
      "step": 2,
      "edit_type": "...",
      "query_after": "...",
      "changed_context": "...",
      "intended_retrieval_effect": "..."
    }},
    {{
      "step": 3,
      "edit_type": "...",
      "query_after": "...",
      "changed_context": "...",
      "intended_retrieval_effect": "..."
    }},
    {{
      "step": 4,
      "edit_type": "...",
      "query_after": "...",
      "changed_context": "...",
      "intended_retrieval_effect": "..."
    }}
  ]
}}

Rules:
- Output exactly 4 trace slots.
- The final active query_after must exactly match the target query.
- Use STOP for unused steps.
- Preserve the original question intent.
- Prefer minimal edits.
- Do not claim that an entity or fact is confirmed unless it is already present in the weak or target query.
- edit_type must be one of: {", ".join(EDIT_TYPES)}.

Question:
{ex["question"]}

Weak query:
{ex["base_hop2_query"]}

Target query:
{ex["cand_hop2_query"]}
""".strip()


def strip_json_fence(raw):
    s = raw.strip()

    if s.startswith("```json"):
        s = s[len("```json"):].strip()
        if s.endswith("```"):
            s = s[:-3].strip()
        return s

    if s.startswith("```"):
        s = s[3:].strip()
        if s.endswith("```"):
            s = s[:-3].strip()
        return s

    return s


def parse_trace(raw):
    s = strip_json_fence(raw)
    obj = json.loads(s)
    return obj["trace"]


def build_candidates(ex, lm, use_llm):
    rows = []

    rows.append({
        "idx": ex["idx"],
        "arm": "base_query",
        "query": ex["base_hop2_query"],
        "meta": {},
    })

    rows.append({
        "idx": ex["idx"],
        "arm": "target_query",
        "query": ex["cand_hop2_query"],
        "meta": {},
    })

    rows.append({
        "idx": ex["idx"],
        "arm": "random_drop",
        "query": random_drop(ex["base_hop2_query"], seed=ex["idx"]),
        "meta": {},
    })

    if not use_llm:
        return rows

    raw_trace = lm_call(lm, trace_prompt(ex))
    rows.append({
        "idx": ex["idx"],
        "arm": "target_trace_raw",
        "query": None,
        "meta": {"raw_trace": raw_trace},
    })

    try:
        trace = parse_trace(raw_trace)
        for step in trace:
            if step.get("edit_type") == "STOP":
                continue

            q = step.get("query_after")
            if not q:
                continue

            rows.append({
                "idx": ex["idx"],
                "arm": f"trace_step_{step.get('step')}_{step.get('edit_type')}",
                "query": q,
                "meta": {
                    "step": step.get("step"),
                    "edit_type": step.get("edit_type"),
                    "changed_context": step.get("changed_context"),
                    "intended_retrieval_effect": step.get("intended_retrieval_effect"),
                },
            })
    except Exception as e:
        rows.append({
            "idx": ex["idx"],
            "arm": "target_trace_parse_error",
            "query": None,
            "meta": {"error": str(e), "raw_trace": raw_trace},
        })

    for arm in ARMS:
        q = lm_call(lm, rewrite_prompt(ex, arm))
        rows.append({
            "idx": ex["idx"],
            "arm": arm,
            "query": q.strip(),
            "meta": {},
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

    for arm, s in sorted(stats.items()):
        n = s["n"]
        lines.append(
            f"| {arm} | {n} | "
            f"{s['support_recall_hop2'] / n:.3f} | "
            f"{s['missing_recovery_rate'] / n:.3f} | "
            f"{s['any_support_hit'] / n:.3f} | "
            f"{s['any_missing_recovered'] / n:.3f} |"
        )

    return "\n".join(lines)


def summarize_grouped(rows):
    by_trace_step = defaultdict(lambda: {
        "n": 0,
        "support_recall_hop2": 0.0,
        "missing_recovery_rate": 0.0,
        "any_support_hit": 0,
        "any_missing_recovered": 0,
    })

    by_trace_edit_type = defaultdict(lambda: {
        "n": 0,
        "support_recall_hop2": 0.0,
        "missing_recovery_rate": 0.0,
        "any_support_hit": 0,
        "any_missing_recovered": 0,
    })

    def add(bucket, key, r):
        s = bucket[key]
        s["n"] += 1
        s["support_recall_hop2"] += r["support_recall_hop2"]
        s["missing_recovery_rate"] += r["missing_recovery_rate"]
        s["any_support_hit"] += int(r["support_hit_count"] > 0)
        s["any_missing_recovered"] += int(r["missing_recovered_count"] > 0)

    for r in rows:
        arm = r["arm"]
        meta = r.get("meta") or {}

        if not arm.startswith("trace_step_"):
            continue

        step = meta.get("step")
        edit_type = meta.get("edit_type")

        if step is not None:
            add(by_trace_step, f"trace_step_{step}", r)
        if edit_type:
            add(by_trace_edit_type, edit_type, r)

    def render(bucket, title):
        lines = [f"# {title}", ""]
        lines.append("| key | n | support recall hop2 | missing recovery | any support hit | any missing recovered |")
        lines.append("|---|---:|---:|---:|---:|---:|")

        for key, s in sorted(bucket.items()):
            n = s["n"]
            lines.append(
                f"| {key} | {n} | "
                f"{s['support_recall_hop2'] / n:.3f} | "
                f"{s['missing_recovery_rate'] / n:.3f} | "
                f"{s['any_support_hit'] / n:.3f} | "
                f"{s['any_missing_recovered'] / n:.3f} |"
            )
        return "\n".join(lines)

    return "\n\n".join([
        render(by_trace_step, "Trace prefixes by step"),
        render(by_trace_edit_type, "Trace prefixes by edit type"),
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=DEFAULT_SRC)
    parser.add_argument("--out-dir", default="experiments/deltaq/results_retrieval_gain")
    parser.add_argument("--retriever-dir", default=os.environ.get("HOTPOT_RETRIEVER_DIR"))
    parser.add_argument("--k", type=int, default=7)
    parser.add_argument("--limit", type=int, default=None)

    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument("--model", default=os.environ.get("TASK_MODEL", "openai/gpt-5-mini"))
    parser.add_argument("--api-base", default=os.environ.get("TASK_API_BASE", ""))
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=16000)

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

    lm = None
    if args.use_llm:
        api_key = resolve_api_key(args.model, args.api_key)
        lm_kwargs = {
            "api_key": api_key,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
        }
        if args.api_base:
            lm_kwargs["api_base"] = args.api_base

        lm = dspy.LM(args.model, **lm_kwargs)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    examples = list(load_jsonl(args.src))
    if args.limit is not None:
        examples = examples[:args.limit]

    print(f"[info] examples: {len(examples)}")
    print(f"[info] source: {args.src}")
    print(f"[info] out_dir: {out_dir}")
    print(f"[info] k: {args.k}")
    print(f"[info] use_llm: {args.use_llm}")
    if args.use_llm:
        print(f"[info] model: {args.model}")
        print(f"[info] temperature: {args.temperature}")
        print(f"[info] max_tokens: {args.max_tokens}")

    all_candidates = []
    validations = []

    ex_iter = tqdm(
        examples,
        desc="Generating candidates",
        unit="ex",
        dynamic_ncols=True,
    )

    for ex in ex_iter:
        ex_iter.set_postfix({"idx": ex.get("idx")})
        cands = build_candidates(ex, lm=lm, use_llm=args.use_llm)
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

    cand_path = out_dir / "candidate_queries.jsonl"
    val_path = out_dir / "bm25_validation.jsonl"
    summary_path = out_dir / "summary.md"
    grouped_summary_path = out_dir / "summary_grouped.md"

    with cand_path.open("w") as f:
        for r in all_candidates:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with val_path.open("w") as f:
        for r in validations:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    summary = summarize(validations)
    grouped_summary = summarize_grouped(validations)

    summary_path.write_text(summary)
    grouped_summary_path.write_text(grouped_summary)

    print()
    print("candidates:", cand_path)
    print("validation:", val_path)
    print("summary:", summary_path)
    print("grouped summary:", grouped_summary_path)
    print()
    print(summary)
    print()
    print(grouped_summary)


if __name__ == "__main__":
    main()