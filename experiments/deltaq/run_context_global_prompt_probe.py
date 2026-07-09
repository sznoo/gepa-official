import argparse
import json
import os
import sys
import time
from pathlib import Path

import dspy

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from examples.hotpotqa.retriever import set_retriever_dir
from experiments.deltaq.run_lifting_component_ablation import (
    DEFAULT_SRC,
    DEFAULT_TRACE_VALIDATION,
    load_examples,
    load_trace_validation_by_idx,
    build_transition_specs,
    resolve_api_key,
    lm_call,
    validate_query,
    reproduction_stats,
    write_summary,
    write_case_report,
)


try:
    from tqdm.auto import tqdm
except Exception:
    def tqdm(iterable, **kwargs):
        return iterable


ARMS = [
    "distilled_global",
    "raw_context_bank",
]


MANUAL_DISTILLED_GLOBAL = """\
Rewrite the current second-hop BM25 query using general principles distilled from successful query updates.

Use a compact evidence-retrieval query, not a full sentence.

General rewrite principles:
1. Preserve concrete anchors from the question and current query when they identify the main entity, work, person, place, organization, event, or candidate page.
2. Do not collapse uncertain candidates too early. If multiple aliases, candidate entities, or possible referents are useful, keep them as a compact candidate set.
3. Add or restore relation cues that specify the missing evidence relation, such as produced by, owned by, named after, founded by, location, origin, cast, role, author, director, capital, birthplace, or occupation.
4. Add answer-type cues when they help BM25 retrieve the evidence page, such as person, organization, country, river, film, song, album, actor, character, owner, manufacturer, or location.
5. Remove or downweight side entities, side relations, franchise/background details, or source-page-specific clutter that can dominate BM25 and pull retrieval to a distractor page.
6. Prefer exact lexical anchors over broad paraphrases. Include canonical names, aliases, and relation words likely to appear in Wikipedia abstracts.
7. The output should be a short BM25 keyword query containing the most useful anchors and relation cues only.
"""


def parse_arms(s):
    if not s or s == "all":
        return ARMS
    arms = [x.strip() for x in s.split(",") if x.strip()]
    bad = [a for a in arms if a not in ARMS]
    if bad:
        raise ValueError(f"Unknown arms: {bad}. Valid arms: {ARMS}")
    return arms


def parse_idxs(s):
    if not s or s == "all":
        return None
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def lm_text_call(lm, prompt, retries=3, sleep_s=2.0):
    last_error = None
    for attempt in range(retries):
        try:
            out = lm(prompt)
            if isinstance(out, list):
                out = out[0]
            return str(out).strip(), None
        except Exception as e:
            last_error = str(e)
            if attempt + 1 < retries:
                time.sleep(sleep_s * (attempt + 1))
    return None, last_error


def bank_entry(spec, include_effect=False, include_oracle_next=False):
    lines = [
        f"[idx={spec['idx']} transition={spec['transition_id']}]",
        f"Question: {spec['question']}",
        f"Current query: {spec['current_query']}",
        f"Edit type: {spec['edit_type']}",
        f"Local query delta: {spec['changed_context']}",
    ]
    if include_effect:
        lines.append(f"Intended retrieval effect: {spec['intended_retrieval_effect']}")
    if include_oracle_next:
        lines.append(f"Rewritten query: {spec['oracle_next_query']}")
    return "\n".join(lines)


def build_context_bank(specs, heldout=None, include_effect=False, include_oracle_next=False):
    entries = []
    for s in specs:
        if heldout is not None:
            same = (
                int(s["idx"]) == int(heldout["idx"])
                and s["transition_id"] == heldout["transition_id"]
            )
            if same:
                continue
        entries.append(bank_entry(
            s,
            include_effect=include_effect,
            include_oracle_next=include_oracle_next,
        ))
    return "\n\n---\n\n".join(entries)


def build_distill_source(specs, include_effect=False):
    entries = []
    for i, s in enumerate(specs, start=1):
        lines = [
            f"{i}. edit_type: {s['edit_type']}",
            f"   changed_context: {s['changed_context']}",
        ]
        if include_effect:
            lines.append(f"   intended_retrieval_effect: {s['intended_retrieval_effect']}")
        entries.append("\n".join(lines))
    return "\n".join(entries)


def generate_distilled_global_prompt(lm, specs, include_effect=False, retries=3):
    source = build_distill_source(specs, include_effect=include_effect)
    prompt = f"""\
You are distilling successful local BM25 query edits into one reusable global prompt.

Below are oracle-derived local query deltas from successful HotpotQA second-hop retrieval transitions.
Your job is to compress them into general rewrite rules for future current queries.

Important constraints:
- Do NOT include specific named entities, titles, people, places, organizations, dates, or works from the examples.
- Do NOT mention the examples.
- Do NOT assume gold support titles or oracle next queries.
- Preserve only abstract, reusable BM25-facing rewrite principles.
- The final prompt should instruct a model how to rewrite a current second-hop query.
- The final prompt should be concise but operational.
- Output only the final reusable prompt text.

Local query deltas:
{source}
"""
    text, error = lm_text_call(lm, prompt, retries=retries)
    if not text:
        text = MANUAL_DISTILLED_GLOBAL
    return text.strip(), error, prompt


def make_distilled_global_eval_prompt(spec, distilled_prompt):
    return f"""\
You are rewriting a HotpotQA second-hop BM25 query.

Reusable global rewrite prompt:
{distilled_prompt}

Now apply the reusable prompt to the current item.

Question:
{spec['question']}

Current query:
{spec['current_query']}

Rules:
- Output only the rewritten BM25 query.
- Do not answer the question.
- Do not mention retrieved documents, gold support titles, or evaluation.
- Use compact keyword-query style.
- Preserve useful concrete anchors.
- Add relation/answer-type cues only when they help retrieval.
- Remove distractor or side-context terms that may dominate BM25.
""".strip()


def make_raw_context_bank_eval_prompt(spec, bank_text):
    return f"""\
You are rewriting a HotpotQA second-hop BM25 query.

You are given a bank of successful local query deltas from recovery-producing query transitions.
Use the bank as prompt memory.

How to use the bank:
- If a bank entry matches the current question/current query, apply that entry's Local query delta.
- If no exact match is available, infer the most relevant reusable rewrite pattern from the bank.
- Do not copy irrelevant entities from unrelated bank entries.
- Output a compact BM25 keyword query, not an answer.

Context bank:
{bank_text}

Now rewrite the current item.

Question:
{spec['question']}

Current query:
{spec['current_query']}

Rules:
- Output only the rewritten BM25 query.
- Do not answer the question.
- Do not mention retrieved documents, gold support titles, or evaluation.
- Preserve useful concrete anchors.
- Add relation/answer-type cues only when they help retrieval.
- Remove distractor or side-context terms that may dominate BM25.
""".strip()


def evaluate_prompt(lm, ex, spec, arm, prompt, k, retries):
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

    return {
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
        "prompt_arm_name": arm,
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=DEFAULT_SRC)
    parser.add_argument("--trace-validation", default=DEFAULT_TRACE_VALIDATION)
    parser.add_argument("--idxs", default="all")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out-dir", default="experiments/deltaq/results_context_global_prompt_probe")
    parser.add_argument("--retriever-dir", default=os.environ.get("HOTPOT_RETRIEVER_DIR"))
    parser.add_argument("--k", type=int, default=7)

    parser.add_argument("--arms", default="all")
    parser.add_argument("--only-recovery-edges", action="store_true")
    parser.add_argument("--include-final-target-edge", action="store_true")

    parser.add_argument("--distill-mode", choices=["manual", "llm"], default="llm")
    parser.add_argument("--distill-include-effect", action="store_true")
    parser.add_argument("--raw-bank-include-effect", action="store_true")
    parser.add_argument("--raw-bank-include-oracle-next", action="store_true")
    parser.add_argument("--raw-bank-loo", action="store_true")

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
    print(f"[info] arms: {selected_arms}")
    print(f"[info] distill_mode: {args.distill_mode}")
    print(f"[info] raw_bank_loo: {args.raw_bank_loo}")
    print(f"[info] out_dir: {out_dir}")

    distilled_prompt = None
    distill_error = None
    distill_source_prompt = None

    if "distilled_global" in selected_arms:
        if args.distill_mode == "manual":
            distilled_prompt = MANUAL_DISTILLED_GLOBAL
        else:
            distilled_prompt, distill_error, distill_source_prompt = generate_distilled_global_prompt(
                lm=lm,
                specs=specs,
                include_effect=args.distill_include_effect,
                retries=args.retries,
            )

        (out_dir / "distilled_global_prompt.txt").write_text(distilled_prompt)
        if distill_source_prompt:
            (out_dir / "distill_source_prompt.txt").write_text(distill_source_prompt)
        if distill_error:
            (out_dir / "distill_error.txt").write_text(str(distill_error))

    if "raw_context_bank" in selected_arms and not args.raw_bank_loo:
        bank_text = build_context_bank(
            specs,
            heldout=None,
            include_effect=args.raw_bank_include_effect,
            include_oracle_next=args.raw_bank_include_oracle_next,
        )
        (out_dir / "raw_context_bank_prompt_bank.txt").write_text(bank_text)

    rows = []
    jobs = [(spec, arm) for spec in specs for arm in selected_arms]

    for spec, arm in tqdm(jobs, desc="Context global prompt jobs", unit="job", dynamic_ncols=True):
        ex = examples[int(spec["idx"])]

        if arm == "distilled_global":
            prompt = make_distilled_global_eval_prompt(spec, distilled_prompt)
        elif arm == "raw_context_bank":
            if args.raw_bank_loo:
                bank_text = build_context_bank(
                    specs,
                    heldout=spec,
                    include_effect=args.raw_bank_include_effect,
                    include_oracle_next=args.raw_bank_include_oracle_next,
                )
            else:
                bank_text = (out_dir / "raw_context_bank_prompt_bank.txt").read_text()
            prompt = make_raw_context_bank_eval_prompt(spec, bank_text)
        else:
            raise ValueError(f"Unknown arm: {arm}")

        row = evaluate_prompt(
            lm=lm,
            ex=ex,
            spec=spec,
            arm=arm,
            prompt=prompt,
            k=args.k,
            retries=args.retries,
        )
        row["distill_mode"] = args.distill_mode
        row["raw_bank_loo"] = args.raw_bank_loo
        rows.append(row)

    result_path = out_dir / "context_global_prompt_transitions.jsonl"
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
    if "distilled_global" in selected_arms:
        print("distilled prompt:", out_dir / "distilled_global_prompt.txt")
    if "raw_context_bank" in selected_arms and not args.raw_bank_loo:
        print("raw bank:", out_dir / "raw_context_bank_prompt_bank.txt")
    print()
    print(summary_path.read_text())


if __name__ == "__main__":
    main()
