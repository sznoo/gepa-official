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

DEFAULT_TRACE_VALIDATION = (
    "experiments/deltaq/results_retrieval_gain_gpt5mini_full/"
    "bm25_validation.jsonl"
)


ARMS = [
    "generic",
    "type_only",
    "effect_only",
    "type_effect",
    "context_only",
    "type_context",
    "full",
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
        "Output:",
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


def validate_query(ex, query, k):
    titles, passages = retrieve_titles(query, k=k)

    support = set(ex["gold_support_titles"])
    base_missing = set(ex["base_missing"])

    hit_support = sorted(support & set(titles))
    recovered_missing = sorted(base_missing & set(titles))

    return {
        "query": query,
        "retrieved_titles": titles,
        "hit_support_titles": hit_support,
        "recovered_missing_titles": recovered_missing,
        "support_hit_count": len(hit_support),
        "missing_recovered_count": len(recovered_missing),
        "support_recall_hop2": len(hit_support) / max(1, len(support)),
        "missing_recovery_rate": len(recovered_missing) / max(1, len(base_missing)),
        "target_ranks": {t: rank_of(t, titles) for t in ex["gold_support_titles"]},
    }


def load_examples(src, idxs=None, limit=None):
    examples = {}
    wanted = None
    if idxs:
        wanted = {int(x) for x in idxs}

    for ex in load_jsonl(src):
        idx = int(ex["idx"])
        if wanted is not None and idx not in wanted:
            continue
        examples[idx] = ex
        if limit is not None and len(examples) >= limit:
            break

    return examples


def load_trace_validation_by_idx(path):
    by_idx = defaultdict(list)
    for r in load_jsonl(path):
        by_idx[int(r["idx"])].append(r)
    return by_idx


def build_q_path(rows):
    by_arm = {r["arm"]: r for r in rows}

    base = by_arm.get("base_query")
    target = by_arm.get("target_query")

    if base is None:
        raise ValueError("base_query missing")
    if target is None:
        raise ValueError("target_query missing")

    trace_rows = [
        r for r in rows
        if r["arm"].startswith("trace_step_")
    ]

    trace_rows = sorted(
        trace_rows,
        key=lambda r: (
            r.get("meta", {}).get("step", 999),
            r["arm"],
        ),
    )

    path = []
    path.append({
        "source": "base_query",
        "step": 0,
        "query": base["query"],
        "validation": base,
        "meta": {
            "edit_type": "START",
            "changed_context": "",
            "intended_retrieval_effect": "",
        },
    })

    seen_queries = {base["query"]}

    for r in trace_rows:
        q = r.get("query")
        if not q:
            continue
        if q in seen_queries:
            continue

        meta = r.get("meta") or {}
        path.append({
            "source": r["arm"],
            "step": meta.get("step"),
            "query": q,
            "validation": r,
            "meta": meta,
        })
        seen_queries.add(q)

    if target["query"] not in seen_queries:
        path.append({
            "source": "target_query",
            "step": "target",
            "query": target["query"],
            "validation": target,
            "meta": {
                "edit_type": "TARGET_COMPLETION",
                "changed_context": "Complete the remaining edit toward the target retrieval behavior.",
                "intended_retrieval_effect": "Recover the missing support evidence while preserving useful evidence.",
                "synthetic": True,
            },
        })

    return path


def build_transition_specs(examples, trace_by_idx, include_final_target_edge=False, only_recovery_edges=True):
    specs = []
    skipped = []

    for idx, ex in sorted(examples.items()):
        if idx not in trace_by_idx:
            skipped.append({"idx": idx, "reason": "no trace rows"})
            continue

        try:
            path = build_q_path(trace_by_idx[idx])
        except Exception as e:
            skipped.append({"idx": idx, "reason": str(e)})
            continue

        for j in range(len(path) - 1):
            current = path[j]
            next_node = path[j + 1]

            if next_node["source"] == "target_query" and not include_final_target_edge:
                continue

            current_val = current["validation"]
            next_val = next_node["validation"]
            edit_meta = next_node["meta"] or {}

            current_rec = set(current_val["recovered_missing_titles"])
            next_rec = set(next_val["recovered_missing_titles"])
            is_recovery_edge = len(next_rec - current_rec) > 0

            if only_recovery_edges and not is_recovery_edge:
                continue

            specs.append({
                "idx": idx,
                "question": ex["question"],
                "gold_answer": ex.get("gold_answer"),
                "gold_support_titles": ex["gold_support_titles"],
                "base_missing": ex["base_missing"],

                "transition_id": f"{j}_to_{j+1}",
                "current_source": current["source"],
                "next_source": next_node["source"],
                "current_step": current["step"],
                "next_step": next_node["step"],
                "is_recovery_edge": is_recovery_edge,

                "current_query": current["query"],
                "oracle_next_query": next_node["query"],
                "current_val": current_val,
                "next_val": next_val,

                "edit_type": edit_meta.get("edit_type", ""),
                "changed_context": edit_meta.get("changed_context", ""),
                "intended_retrieval_effect": edit_meta.get("intended_retrieval_effect", ""),
            })

    return specs, skipped


def descriptor_block(arm, spec):
    edit_type = spec["edit_type"]
    changed_context = spec["changed_context"]
    intended_effect = spec["intended_retrieval_effect"]

    if arm == "generic":
        return """Task:
Improve the query by one small local edit so that it retrieves better evidence."""

    if arm == "type_only":
        return f"""Edit descriptor:
- edit_type: {edit_type}"""

    if arm == "effect_only":
        return f"""Edit descriptor:
- intended_retrieval_effect: {intended_effect}"""

    if arm == "type_effect":
        return f"""Edit descriptor:
- edit_type: {edit_type}
- intended_retrieval_effect: {intended_effect}"""

    if arm == "context_only":
        return f"""Edit descriptor:
- changed_context: {changed_context}"""

    if arm == "type_context":
        return f"""Edit descriptor:
- edit_type: {edit_type}
- changed_context: {changed_context}"""

    if arm == "full":
        return f"""Edit descriptor:
- edit_type: {edit_type}
- changed_context: {changed_context}
- intended_retrieval_effect: {intended_effect}"""

    raise ValueError(f"Unknown arm: {arm}")


def make_example_block(arm, spec):
    desc = descriptor_block(arm, spec)
    return f"""
Example:
Question:
{spec["question"]}

Current query:
{spec["current_query"]}

{desc}

Rewritten query:
{spec["oracle_next_query"]}
""".strip()


def select_fewshots(specs, target_spec, arm, k, seed=0, same_edit_type_first=True):
    if k <= 0:
        return []

    rng = random.Random(seed + int(target_spec["idx"]) * 1009)

    candidates = [
        s for s in specs
        if not (
            int(s["idx"]) == int(target_spec["idx"])
            and s["transition_id"] == target_spec["transition_id"]
        )
    ]

    if same_edit_type_first:
        same = [s for s in candidates if s["edit_type"] == target_spec["edit_type"]]
        other = [s for s in candidates if s["edit_type"] != target_spec["edit_type"]]
        rng.shuffle(same)
        rng.shuffle(other)
        ordered = same + other
    else:
        ordered = candidates[:]
        rng.shuffle(ordered)

    return ordered[:k]


def make_prompt(arm, spec, fewshots=None):
    fewshots = fewshots or []
    fewshot_text = ""

    if fewshots:
        blocks = [make_example_block(arm, fs) for fs in fewshots]
        fewshot_text = "\n\nFew-shot examples:\n\n" + "\n\n---\n\n".join(blocks) + "\n\n"

    desc = descriptor_block(arm, spec)

    return f"""
You are applying one local edit to a BM25 retrieval query.

The output should be a retrieval query, not an answer.
Use compact BM25 keyword-query style.

{fewshot_text}
Now rewrite the current query.

Question:
{spec["question"]}

Current query:
{spec["current_query"]}

{desc}

Rules:
- Output only the rewritten query.
- Do not answer the question.
- Do not mention retrieved documents, gold support titles, or evaluation.
- Do not copy a target query; no target query is provided for the current item.
- Apply only one local edit.
- Preserve useful concrete anchors unless the descriptor implies removing them.
- Keep uncertain candidate entities or aliases when they help the retrieval direction.
- Avoid long explanatory sentences.
""".strip()


def reproduction_stats(current_val, next_val, gen_val):
    current_rec = set(current_val["recovered_missing_titles"])
    next_rec = set(next_val["recovered_missing_titles"])
    gen_rec = set(gen_val["recovered_missing_titles"])

    newly_recovered_by_next = sorted(next_rec - current_rec)
    reproduced_new = sorted(gen_rec & set(newly_recovered_by_next))

    if newly_recovered_by_next:
        first_recovery_reproduced = len(reproduced_new) > 0
        new_recovery_reproduction_rate = len(reproduced_new) / len(newly_recovered_by_next)
    else:
        first_recovery_reproduced = None
        new_recovery_reproduction_rate = None

    next_recovered_reproduced = sorted(gen_rec & next_rec)
    if next_rec:
        next_recovery_overlap = len(next_recovered_reproduced) / len(next_rec)
    else:
        next_recovery_overlap = None

    return {
        "newly_recovered_by_oracle_next": newly_recovered_by_next,
        "reproduced_newly_recovered": reproduced_new,
        "first_recovery_reproduced": first_recovery_reproduced,
        "new_recovery_reproduction_rate": new_recovery_reproduction_rate,
        "next_recovered_reproduced": next_recovered_reproduced,
        "next_recovery_overlap": next_recovery_overlap,
        "gen_improves_over_current": gen_val["missing_recovery_rate"] > current_val["missing_recovery_rate"],
        "gen_matches_or_exceeds_next": gen_val["missing_recovery_rate"] >= next_val["missing_recovery_rate"],
        "gen_missing_recovery_minus_current": (
            gen_val["missing_recovery_rate"] - current_val["missing_recovery_rate"]
        ),
        "gen_missing_recovery_minus_next": (
            gen_val["missing_recovery_rate"] - next_val["missing_recovery_rate"]
        ),
        "gen_support_recall_minus_current": (
            gen_val["support_recall_hop2"] - current_val["support_recall_hop2"]
        ),
        "gen_support_recall_minus_next": (
            gen_val["support_recall_hop2"] - next_val["support_recall_hop2"]
        ),
    }


def run_generation_arm(lm, ex, spec, arm, prompt_arm_name, prompt, retries, k):
    query, error = lm_call(lm, prompt, retries=retries)

    if query:
        val = validate_query(ex, query, k=k)
    else:
        val = {
            "query": None,
            "retrieved_titles": [],
            "hit_support_titles": [],
            "recovered_missing_titles": [],
            "support_hit_count": 0,
            "missing_recovered_count": 0,
            "support_recall_hop2": 0.0,
            "missing_recovery_rate": 0.0,
            "target_ranks": {},
        }

    rep = reproduction_stats(
        current_val=spec["current_val"],
        next_val=spec["next_val"],
        gen_val=val,
    )

    row = {
        "idx": spec["idx"],
        "question": spec["question"],
        "gold_answer": spec["gold_answer"],
        "gold_support_titles": spec["gold_support_titles"],
        "base_missing": spec["base_missing"],

        "transition_id": spec["transition_id"],
        "current_source": spec["current_source"],
        "next_source": spec["next_source"],
        "current_step": spec["current_step"],
        "next_step": spec["next_step"],
        "is_recovery_edge": spec["is_recovery_edge"],

        "arm": arm,
        "prompt_arm_name": prompt_arm_name,
        "edit_type": spec["edit_type"],
        "changed_context": spec["changed_context"],
        "intended_retrieval_effect": spec["intended_retrieval_effect"],

        "current_query": spec["current_query"],
        "oracle_next_query": spec["oracle_next_query"],
        "generated_query": query,
        "prompt": prompt,
        "error": error,

        "current_missing_recovery_rate": spec["current_val"]["missing_recovery_rate"],
        "oracle_next_missing_recovery_rate": spec["next_val"]["missing_recovery_rate"],
        "generated_missing_recovery_rate": val["missing_recovery_rate"],

        "current_support_recall_hop2": spec["current_val"]["support_recall_hop2"],
        "oracle_next_support_recall_hop2": spec["next_val"]["support_recall_hop2"],
        "generated_support_recall_hop2": val["support_recall_hop2"],

        "current_recovered_missing_titles": spec["current_val"]["recovered_missing_titles"],
        "oracle_next_recovered_missing_titles": spec["next_val"]["recovered_missing_titles"],
        "generated_recovered_missing_titles": val["recovered_missing_titles"],

        "current_hit_support_titles": spec["current_val"]["hit_support_titles"],
        "oracle_next_hit_support_titles": spec["next_val"]["hit_support_titles"],
        "generated_hit_support_titles": val["hit_support_titles"],

        "generated_retrieved_titles": val["retrieved_titles"],

        **rep,
    }

    return row


def add_metric(stats, key, tr):
    s = stats[key]
    s["n"] += 1

    for prefix in ["current", "oracle_next", "generated"]:
        s[f"{prefix}_missing_recovery"] += tr[f"{prefix}_missing_recovery_rate"]
        s[f"{prefix}_support_recall"] += tr[f"{prefix}_support_recall_hop2"]

    s["gen_improves_over_current"] += int(tr["gen_improves_over_current"])
    s["gen_matches_or_exceeds_next"] += int(tr["gen_matches_or_exceeds_next"])

    if tr["is_recovery_edge"]:
        s["n_recovery_edges"] += 1
        s["first_recovery_reproduced"] += int(bool(tr["first_recovery_reproduced"]))
        if tr["new_recovery_reproduction_rate"] is not None:
            s["new_recovery_reproduction_rate_sum"] += tr["new_recovery_reproduction_rate"]

    if tr["next_recovery_overlap"] is not None:
        s["n_next_recovery_nonempty"] += 1
        s["next_recovery_overlap_sum"] += tr["next_recovery_overlap"]

    s["delta_missing_vs_current"] += tr["gen_missing_recovery_minus_current"]
    s["delta_missing_vs_next"] += tr["gen_missing_recovery_minus_next"]
    s["delta_support_vs_current"] += tr["gen_support_recall_minus_current"]
    s["delta_support_vs_next"] += tr["gen_support_recall_minus_next"]


def render_summary(stats, title):
    lines = [f"# {title}", ""]
    lines.append(
        "| key | n | recovery edges | current MR | next MR | generated MR | "
        "ΔMR vs current | ΔMR vs next | gen>current | gen>=next | "
        "first recovery reproduced | next recovery overlap |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

    def sort_key(k):
        if k == "ALL":
            return ("", -999, k)
        return (str(k), 0, k)

    for key, s in sorted(stats.items(), key=lambda kv: sort_key(kv[0])):
        n = s["n"]
        rec_edges = s["n_recovery_edges"]

        first_repr = (
            s["first_recovery_reproduced"] / rec_edges
            if rec_edges else 0.0
        )
        next_overlap = (
            s["next_recovery_overlap_sum"] / s["n_next_recovery_nonempty"]
            if s["n_next_recovery_nonempty"] else 0.0
        )

        lines.append(
            f"| {key} | {n} | {rec_edges} | "
            f"{s['current_missing_recovery'] / n:.3f} | "
            f"{s['oracle_next_missing_recovery'] / n:.3f} | "
            f"{s['generated_missing_recovery'] / n:.3f} | "
            f"{s['delta_missing_vs_current'] / n:.3f} | "
            f"{s['delta_missing_vs_next'] / n:.3f} | "
            f"{s['gen_improves_over_current'] / n:.3f} | "
            f"{s['gen_matches_or_exceeds_next'] / n:.3f} | "
            f"{first_repr:.3f} | "
            f"{next_overlap:.3f} |"
        )

    return "\n".join(lines)


def write_summary(out_path, rows):
    make_stats = lambda: defaultdict(lambda: {
        "n": 0,
        "n_recovery_edges": 0,
        "current_missing_recovery": 0.0,
        "oracle_next_missing_recovery": 0.0,
        "generated_missing_recovery": 0.0,
        "current_support_recall": 0.0,
        "oracle_next_support_recall": 0.0,
        "generated_support_recall": 0.0,
        "gen_improves_over_current": 0,
        "gen_matches_or_exceeds_next": 0,
        "first_recovery_reproduced": 0,
        "new_recovery_reproduction_rate_sum": 0.0,
        "n_next_recovery_nonempty": 0,
        "next_recovery_overlap_sum": 0.0,
        "delta_missing_vs_current": 0.0,
        "delta_missing_vs_next": 0.0,
        "delta_support_vs_current": 0.0,
        "delta_support_vs_next": 0.0,
    })

    by_arm = make_stats()
    by_prompt_arm = make_stats()
    by_edit = make_stats()
    by_arm_edit = make_stats()
    by_idx = make_stats()

    for r in rows:
        add_metric(by_arm, r["arm"], r)
        add_metric(by_arm, "ALL", r)

        add_metric(by_prompt_arm, r["prompt_arm_name"], r)
        add_metric(by_prompt_arm, "ALL", r)

        add_metric(by_edit, r["edit_type"], r)
        add_metric(by_edit, "ALL", r)

        add_metric(by_arm_edit, f"{r['arm']}::{r['edit_type']}", r)
        add_metric(by_idx, str(r["idx"]), r)

    text = "\n\n".join([
        render_summary(by_arm, "By arm"),
        render_summary(by_prompt_arm, "By prompt arm name"),
        render_summary(by_edit, "By edit type"),
        render_summary(by_arm_edit, "By arm and edit type"),
        render_summary(by_idx, "By idx"),
    ])

    Path(out_path).write_text(text)


def write_case_report(out_path, rows):
    by_idx = defaultdict(list)
    for r in rows:
        by_idx[r["idx"]].append(r)

    lines = []

    for idx, rs in sorted(by_idx.items()):
        lines.append("\n" + "=" * 120)
        lines.append(f"idx: {idx}")
        lines.append(f"question: {rs[0]['question']}")
        lines.append(f"gold_support_titles: {rs[0]['gold_support_titles']}")
        lines.append(f"base_missing: {rs[0]['base_missing']}")

        for r in rs:
            lines.append("\n" + "-" * 100)
            lines.append(
                f"transition: {r['transition_id']} "
                f"{r['current_source']} -> {r['next_source']} | "
                f"arm={r['arm']} | edit_type={r['edit_type']}"
            )
            lines.append(f"changed_context: {r['changed_context']}")
            lines.append(f"intended_retrieval_effect: {r['intended_retrieval_effect']}")
            lines.append("")
            lines.append(
                f"current MR={r['current_missing_recovery_rate']:.3f}, "
                f"next MR={r['oracle_next_missing_recovery_rate']:.3f}, "
                f"generated MR={r['generated_missing_recovery_rate']:.3f}"
            )
            lines.append(
                f"first_recovery_reproduced={r['first_recovery_reproduced']} "
                f"gen_improves_over_current={r['gen_improves_over_current']} "
                f"gen_matches_or_exceeds_next={r['gen_matches_or_exceeds_next']}"
            )
            lines.append("")
            lines.append("current query:")
            lines.append(r["current_query"])
            lines.append("")
            lines.append("oracle next query:")
            lines.append(r["oracle_next_query"])
            lines.append("")
            lines.append("generated query:")
            lines.append(str(r["generated_query"]))
            lines.append("")
            lines.append(f"current recovered: {r['current_recovered_missing_titles']}")
            lines.append(f"next recovered: {r['oracle_next_recovered_missing_titles']}")
            lines.append(f"generated recovered: {r['generated_recovered_missing_titles']}")
            lines.append("")
            lines.append(f"generated titles: {r['generated_retrieved_titles']}")

    Path(out_path).write_text("\n".join(lines))


def parse_idxs(s):
    if not s or s == "all":
        return None
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def parse_arms(s):
    if not s or s == "all":
        return ARMS
    arms = [x.strip() for x in s.split(",") if x.strip()]
    bad = [a for a in arms if a not in ARMS]
    if bad:
        raise ValueError(f"Unknown arms: {bad}. Valid arms: {ARMS}")
    return arms


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=DEFAULT_SRC)
    parser.add_argument("--trace-validation", default=DEFAULT_TRACE_VALIDATION)
    parser.add_argument("--idxs", default="all")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out-dir", default="experiments/deltaq/results_lifting_component_ablation")
    parser.add_argument("--retriever-dir", default=os.environ.get("HOTPOT_RETRIEVER_DIR"))
    parser.add_argument("--k", type=int, default=7)

    parser.add_argument("--arms", default="all")
    parser.add_argument("--include-fewshot", action="store_true")
    parser.add_argument("--fewshot-k", type=int, default=3)
    parser.add_argument("--fewshot-seed", type=int, default=0)
    parser.add_argument("--fewshot-same-edit-first", action="store_true")
    parser.add_argument("--include-final-target-edge", action="store_true")
    parser.add_argument("--only-recovery-edges", action="store_true")

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

    selected_arms = parse_arms(args.arms)
    idxs = parse_idxs(args.idxs)

    examples = load_examples(args.src, idxs=idxs, limit=args.limit)
    trace_by_idx = load_trace_validation_by_idx(args.trace_validation)

    specs, skipped = build_transition_specs(
        examples=examples,
        trace_by_idx=trace_by_idx,
        include_final_target_edge=args.include_final_target_edge,
        only_recovery_edges=args.only_recovery_edges,
    )

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

    print(f"[info] examples: {len(examples)}")
    print(f"[info] transitions: {len(specs)}")
    print(f"[info] trace_validation: {args.trace_validation}")
    print(f"[info] out_dir: {out_dir}")
    print(f"[info] k: {args.k}")
    print(f"[info] model: {args.model}")
    print(f"[info] arms: {selected_arms}")
    print(f"[info] include_fewshot: {args.include_fewshot}")
    print(f"[info] fewshot_k: {args.fewshot_k}")
    print(f"[info] only_recovery_edges: {args.only_recovery_edges}")

    rows = []

    job_list = []
    for spec in specs:
        for arm in selected_arms:
            job_list.append((spec, arm, False))
            if args.include_fewshot:
                job_list.append((spec, arm, True))

    job_iter = tqdm(job_list, desc="Component ablation jobs", unit="job", dynamic_ncols=True)

    for spec, arm, use_fewshot in job_iter:
        job_iter.set_postfix({
            "idx": spec["idx"],
            "arm": arm,
            "fs": int(use_fewshot),
        })

        fewshots = []
        prompt_arm_name = arm

        if use_fewshot:
            fewshots = select_fewshots(
                specs=specs,
                target_spec=spec,
                arm=arm,
                k=args.fewshot_k,
                seed=args.fewshot_seed,
                same_edit_type_first=args.fewshot_same_edit_first,
            )
            prompt_arm_name = f"{arm}_fs{args.fewshot_k}"

        prompt = make_prompt(
            arm=arm,
            spec=spec,
            fewshots=fewshots,
        )

        ex = examples[int(spec["idx"])]

        row = run_generation_arm(
            lm=lm,
            ex=ex,
            spec=spec,
            arm=arm,
            prompt_arm_name=prompt_arm_name,
            prompt=prompt,
            retries=args.retries,
            k=args.k,
        )

        row["use_fewshot"] = use_fewshot
        row["fewshot_k"] = len(fewshots)
        row["fewshot_ids"] = [
            {
                "idx": fs["idx"],
                "transition_id": fs["transition_id"],
                "edit_type": fs["edit_type"],
            }
            for fs in fewshots
        ]

        rows.append(row)

    result_path = out_dir / "component_ablation_transitions.jsonl"
    summary_path = out_dir / "summary.md"
    case_report_path = out_dir / "case_report.txt"
    skipped_path = out_dir / "skipped.jsonl"

    with result_path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with skipped_path.open("w") as f:
        for r in skipped:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    write_summary(summary_path, rows)
    write_case_report(case_report_path, rows)

    print()
    print("results:", result_path)
    print("summary:", summary_path)
    print("case report:", case_report_path)
    print("skipped:", skipped_path)
    print()
    print(summary_path.read_text())


if __name__ == "__main__":
    main()
