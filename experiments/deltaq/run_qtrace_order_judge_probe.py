# /home/jinwoo/gepa-official/experiments/deltaq/run_qtrace_order_judge_probe.py
import argparse
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean

import dspy

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    from tqdm.auto import tqdm
except Exception:
    def tqdm(x, **kwargs):
        return x


_tls = threading.local()


def read_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def as_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, set):
        return list(x)
    if isinstance(x, tuple):
        return list(x)
    return [x]


def title_from_doc(doc):
    return str(doc).split(" | ", 1)[0].strip()


def safe_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default


def get_first(row, keys, default=None):
    for k in keys:
        if k in row and row[k] is not None:
            return row[k]
    return default


def get_group_key(row):
    for k in ["example_id", "_id", "id", "case_id", "idx", "example_index", "question"]:
        v = row.get(k)
        if v is not None:
            return str(v)
    return str(row.get("question", ""))


def get_question(row):
    return str(get_first(row, ["question", "input_question"], ""))


def get_state_id(row):
    for k in ["arm", "key", "candidate_key", "query_key", "name", "candidate_type"]:
        v = row.get(k)
        if v is not None:
            return str(v)
    return "UNKNOWN"


def get_query(row):
    return str(get_first(row, [
        "query",
        "candidate_query",
        "hop2_query",
        "rewritten_query",
        "generated_query",
        "q",
    ], ""))


def get_docs(row):
    docs = get_first(row, [
        "docs",
        "passages",
        "retrieved_docs",
        "retrieved_passages",
        "hop2_docs",
        "bm25_docs",
    ], [])
    return [str(x) for x in as_list(docs)]


def get_titles(row):
    titles = get_first(row, [
        "titles",
        "retrieved_titles",
        "hop2_titles",
        "doc_titles",
        "bm25_titles",
    ], None)

    if titles is not None:
        return [str(x).strip() for x in as_list(titles) if str(x).strip()]

    docs = get_docs(row)
    return [title_from_doc(d) for d in docs if str(d).strip()]


def get_gold_titles(row):
    titles = get_first(row, [
        "gold_support_titles",
        "gold_titles",
        "support_titles",
        "oracle_support_titles",
    ], [])
    return [str(x).strip() for x in as_list(titles) if str(x).strip()]


def get_missing_after_hop1(row):
    titles = get_first(row, [
        "missing_titles_after_hop1",
        "remaining_gold_titles_after_hop1",
        "missing_support_titles_after_hop1",
        "missing_titles",
    ], None)
    if titles is not None:
        return [str(x).strip() for x in as_list(titles) if str(x).strip()]

    gold = set(get_gold_titles(row))
    hop1 = set(as_list(get_first(row, ["hop1_titles"], [])))
    if gold:
        return sorted(gold - hop1)
    return []


def state_order(state_id):
    s = str(state_id)

    if s == "base_query" or s == "baseline" or s == "current_query":
        return 0

    m = re.search(r"trace[_-]?step[_-]?(\d+)", s)
    if m:
        return int(m.group(1))

    if s in {"target_query", "oracle_next", "oracle_target", "target"}:
        return 10_000

    # Keep random/drop controls available for equal checks, but exclude from ordered trace.
    return None


def get_hit_titles(row):
    titles = set(get_titles(row))
    gold = set(get_gold_titles(row))
    return sorted(titles & gold)


def get_recovered_missing_titles(row):
    titles = set(get_titles(row))
    missing = set(get_missing_after_hop1(row))
    if missing:
        return sorted(titles & missing)
    return get_hit_titles(row)


def get_utility(row):
    # Prefer missing-recovery style metrics if present.
    for k in [
        "missing_recovery_rate",
        "mr",
        "missing_recovery",
        "support_recall",
        "support_recall_total",
        "recall",
        "support_hit_rate",
    ]:
        v = safe_float(row.get(k), None)
        if v is not None:
            return v

    missing = set(get_missing_after_hop1(row))
    titles = set(get_titles(row))
    gold = set(get_gold_titles(row))

    if missing:
        return len(titles & missing) / max(1, len(missing))
    if gold:
        return len(titles & gold) / max(1, len(gold))

    return 0.0


def metric_signature(row):
    # Metric-aware equivalence target for offline evaluation.
    recovered = tuple(sorted(get_recovered_missing_titles(row)))
    hit = tuple(sorted(get_hit_titles(row)))
    util = round(get_utility(row), 3)
    return {
        "recovered_missing_titles": recovered,
        "hit_gold_titles": hit,
        "utility_rounded": util,
        "any_hit": bool(hit),
        "any_recovered": bool(recovered),
    }


def equivalent_by_metric(a, b, tol):
    sa = metric_signature(a)
    sb = metric_signature(b)

    # If title signatures are available, use them.
    if sa["hit_gold_titles"] or sb["hit_gold_titles"] or sa["recovered_missing_titles"] or sb["recovered_missing_titles"]:
        return (
            sa["recovered_missing_titles"] == sb["recovered_missing_titles"]
            and sa["hit_gold_titles"] == sb["hit_gold_titles"]
        )

    return abs(get_utility(a) - get_utility(b)) <= tol


def expected_compare(a, b, tol):
    ua = get_utility(a)
    ub = get_utility(b)
    if ua > ub + tol:
        return "A"
    if ub > ua + tol:
        return "B"
    return "tie"


def truncate(s, n):
    s = str(s)
    if len(s) <= n:
        return s
    return s[:n] + "\n...[truncated]"


def format_state(label, row, max_doc_chars):
    docs = get_docs(row)
    docs_text = "\n".join(f"- {truncate(d, 600)}" for d in docs[:7])

    return f"""\
State {label}
state_id: {get_state_id(row)}
query: {get_query(row)}
retrieved_titles: {get_titles(row)}
retrieved_passages:
{truncate(docs_text, max_doc_chars)}
observed_pred_answer: {row.get("pred_answer", "")}
observed_summary_2: {truncate(row.get("summary_2", ""), 1000)}
""".strip()


def make_compare_prompt(a, b, max_doc_chars):
    # Use oracle diagnostic fields, but do not expose numeric utility.
    question = get_question(a) or get_question(b)
    summary_1 = get_first(a, ["summary_1"], get_first(b, ["summary_1"], ""))
    gold_titles = get_gold_titles(a) or get_gold_titles(b)
    missing_after_hop1 = get_missing_after_hop1(a) or get_missing_after_hop1(b)
    gold_answer = get_first(a, ["gold_answer", "answer"], get_first(b, ["gold_answer", "answer"], ""))

    return f"""\
You are a local tool-aware distance comparison judge for a HotpotQA hop2 BM25 query state.

You do NOT assign an absolute distance.
You compare two query states and decide which one is closer to the sample's success equivalence class.

A query state is closer if it better satisfies the local retrieval/answerability objective while preserving task-relevant anchors:
- retrieves missing support or answer-sufficient evidence
- preserves necessary entities, aliases, dates, and relations
- removes distractors that cause topic drift
- does not overfit to irrelevant titles or answer strings
- yields evidence more compatible with the gold support information when oracle diagnostics are provided

Tie-first calibration rule:
- If both states retrieve the same gold support titles and recover the same missing support titles, return "tie" unless one state clearly provides more answer-sufficient evidence or avoids a clear task-relevant distractor.
- Do not prefer a query merely because it is more fluent, more compact, more canonical, or semantically more plausible.
- BM25-relevant evidence behavior dominates textual query quality.
- A local wording improvement is not a distance improvement unless it changes retrieved support, answerability, or a clear retrieval failure mode.

If both states are metric-equivalent, return "tie".
If they improve incompatible aspects and no local order is justified, return "incomparable".

Question:
{question}

First-hop summary:
{truncate(summary_1, 1800)}

Oracle diagnostics for this calibration experiment:
gold_answer: {gold_answer}
gold_support_titles: {gold_titles}
missing_support_titles_after_hop1: {missing_after_hop1}

{format_state("A", a, max_doc_chars)}

{format_state("B", b, max_doc_chars)}

Return only JSON:
{{
  "closer": "A" | "B" | "tie" | "incomparable",
  "comparison_basis": ["short reason 1", "short reason 2"],
  "minimality_basis": ["what task-relevant behavior is preserved or minimally changed"],
  "confidence": 0.0
}}
""".strip()


def make_equal_prompt(a, b, max_doc_chars):
    question = get_question(a) or get_question(b)
    summary_1 = get_first(a, ["summary_1"], get_first(b, ["summary_1"], ""))
    gold_titles = get_gold_titles(a) or get_gold_titles(b)
    missing_after_hop1 = get_missing_after_hop1(a) or get_missing_after_hop1(b)
    gold_answer = get_first(a, ["gold_answer", "answer"], get_first(b, ["gold_answer", "answer"], ""))

    return f"""\
You are a metric-aware equivalence judge for a HotpotQA hop2 BM25 query state.

You are NOT judging whether two queries are textually similar.
You are judging whether two query states belong to the same local metric behavior class for this sample.

Two states are equivalent if:
- both recover the same task-relevant support/evidence, or
- both are successful in the same task-relevant way, or
- both fail in materially the same way.

They are NOT equivalent if one state recovers missing support or answer-sufficient evidence and the other does not, or if they fail for materially different retrieval reasons.

Question:
{question}

First-hop summary:
{truncate(summary_1, 1800)}

Oracle diagnostics for this calibration experiment:
gold_answer: {gold_answer}
gold_support_titles: {gold_titles}
missing_support_titles_after_hop1: {missing_after_hop1}

{format_state("A", a, max_doc_chars)}

{format_state("B", b, max_doc_chars)}

Return only JSON:
{{
  "equivalent": true or false,
  "relation": "same_success" | "same_failure" | "different_success_quality" | "different_failure_mode",
  "metric_basis": ["short reason 1", "short reason 2"],
  "material_difference": "none or short description",
  "confidence": 0.0
}}
""".strip()


def clean_lm_text(x):
    if isinstance(x, list):
        x = x[0] if x else ""
    x = str(x).strip()
    x = x.strip("` \n")
    if x.lower().startswith("json"):
        x = x[4:].strip()
    return x


def extract_json_obj(text):
    text = clean_lm_text(text)
    text = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.I).strip()
    text = re.sub(r"```$", "", text.strip()).strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            pass
    return None


def make_lm(args):
    kwargs = {
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_base:
        kwargs["api_base"] = args.api_base
    if args.api_key:
        kwargs["api_key"] = args.api_key
    return dspy.LM(args.model, **kwargs)


def get_lm(args):
    if not hasattr(_tls, "lm"):
        _tls.lm = make_lm(args)
    return _tls.lm


def lm_json_call(args, prompt):
    lm = get_lm(args)
    last_error = None
    for i in range(args.retries):
        try:
            out = lm(prompt)
            text = clean_lm_text(out)
            obj = extract_json_obj(text)
            if isinstance(obj, dict):
                return obj, text, None
            last_error = f"JSON parse failed: {text[:500]}"
        except Exception as e:
            last_error = str(e)
        if i + 1 < args.retries:
            time.sleep(2.0 * (i + 1))
    return {}, "", last_error


def build_groups(rows):
    groups = {}
    for r in rows:
        groups.setdefault(get_group_key(r), []).append(r)
    return groups


def choose_examples(groups, max_examples):
    keys = []
    for k, rs in groups.items():
        ordered = [r for r in rs if state_order(get_state_id(r)) is not None]
        ids = {get_state_id(r) for r in ordered}
        if len(ordered) >= 2 and any(state_order(s) == 0 for s in ids):
            keys.append(k)
    keys = sorted(keys)
    if max_examples is not None:
        keys = keys[:max_examples]
    return keys


def build_compare_tasks(groups, keys, pair_mode, shuffle_pair_order, rng, tol):
    tasks = []

    for gk in keys:
        states = [r for r in groups[gk] if state_order(get_state_id(r)) is not None]
        states = sorted(states, key=lambda r: state_order(get_state_id(r)))

        if len(states) < 2:
            continue

        pairs = []

        if pair_mode in {"adjacent", "all"}:
            for i in range(len(states) - 1):
                pairs.append(("adjacent", states[i], states[i + 1]))

        if pair_mode in {"target", "all"}:
            target = None
            for s in states:
                if state_order(get_state_id(s)) == 10_000:
                    target = s
                    break
            if target is not None:
                for s in states:
                    if s is not target:
                        pairs.append(("target", s, target))

        if pair_mode == "all_pairs":
            for i in range(len(states)):
                for j in range(i + 1, len(states)):
                    pairs.append(("all_pairs", states[i], states[j]))

        for kind, a, b in pairs:
            orig_a, orig_b = a, b
            swapped = False
            if shuffle_pair_order and rng.random() < 0.5:
                a, b = b, a
                swapped = True

            exp = expected_compare(a, b, tol)
            tasks.append({
                "task_type": "compare",
                "pair_kind": kind,
                "group_key": gk,
                "a_state_id": get_state_id(a),
                "b_state_id": get_state_id(b),
                "a_order": state_order(get_state_id(a)),
                "b_order": state_order(get_state_id(b)),
                "a_utility": get_utility(a),
                "b_utility": get_utility(b),
                "expected": exp,
                "swapped": swapped,
                "row_a": a,
                "row_b": b,
                "orig_left_state_id": get_state_id(orig_a),
                "orig_right_state_id": get_state_id(orig_b),
            })

    return tasks


def build_equal_tasks(groups, keys, max_equal_pairs_per_example, rng, tol):
    tasks = []

    for gk in keys:
        rs = groups[gk]
        # Use all available states, including controls such as random_drop.
        states = [r for r in rs if get_query(r)]
        if len(states) < 2:
            continue

        eq_pairs = []
        neq_pairs = []

        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                a, b = states[i], states[j]
                if equivalent_by_metric(a, b, tol):
                    eq_pairs.append((a, b))
                else:
                    neq_pairs.append((a, b))

        rng.shuffle(eq_pairs)
        rng.shuffle(neq_pairs)

        selected = []
        # Try to include both positive and negative equality cases.
        half = max(1, max_equal_pairs_per_example // 2)
        selected.extend(eq_pairs[:half])
        selected.extend(neq_pairs[:max_equal_pairs_per_example - len(selected)])

        # If no metric-equivalent non-identical pairs exist, add one self-pair as a sanity positive.
        if not selected and states:
            selected.append((states[0], states[0]))

        for a, b in selected[:max_equal_pairs_per_example]:
            tasks.append({
                "task_type": "equal",
                "pair_kind": "equal_probe",
                "group_key": gk,
                "a_state_id": get_state_id(a),
                "b_state_id": get_state_id(b),
                "a_order": state_order(get_state_id(a)),
                "b_order": state_order(get_state_id(b)),
                "a_utility": get_utility(a),
                "b_utility": get_utility(b),
                "expected_equivalent": equivalent_by_metric(a, b, tol),
                "row_a": a,
                "row_b": b,
            })

    return tasks


def run_task(args, task):
    a, b = task["row_a"], task["row_b"]

    if task["task_type"] == "compare":
        prompt = make_compare_prompt(a, b, args.max_doc_chars)
        obj, raw, err = lm_json_call(args, prompt)
        pred = obj.get("closer", "")
        ok = (pred == task["expected"]) or (task["expected"] == "tie" and pred in {"tie", "incomparable"})

        out = {
            **{k: v for k, v in task.items() if k not in {"row_a", "row_b"}},
            "prompt": prompt if args.save_prompts else None,
            "raw": raw,
            "error": err,
            "predicted": pred,
            "correct": float(ok),
            "comparison_basis": obj.get("comparison_basis", []),
            "minimality_basis": obj.get("minimality_basis", []),
            "confidence": obj.get("confidence", None),
        }
        return out

    if task["task_type"] == "equal":
        prompt = make_equal_prompt(a, b, args.max_doc_chars)
        obj, raw, err = lm_json_call(args, prompt)
        pred = bool(obj.get("equivalent", False))
        ok = pred == bool(task["expected_equivalent"])

        out = {
            **{k: v for k, v in task.items() if k not in {"row_a", "row_b"}},
            "prompt": prompt if args.save_prompts else None,
            "raw": raw,
            "error": err,
            "predicted_equivalent": pred,
            "correct": float(ok),
            "relation": obj.get("relation", ""),
            "metric_basis": obj.get("metric_basis", []),
            "material_difference": obj.get("material_difference", ""),
            "confidence": obj.get("confidence", None),
        }
        return out

    raise ValueError(task["task_type"])


def write_summary(path, results, groups, keys):
    compare = [r for r in results if r["task_type"] == "compare"]
    equal = [r for r in results if r["task_type"] == "equal"]

    lines = []
    lines.append("# Q-trace order judge probe\n")
    lines.append(f"Examples selected: {len(keys)}")
    lines.append(f"Total judgments: {len(results)}")
    lines.append(f"Compare judgments: {len(compare)}")
    lines.append(f"Equal judgments: {len(equal)}\n")

    if compare:
        lines.append("## Compare accuracy by pair kind\n")
        lines.append("| pair_kind | n | accuracy | expected_B_or_A_rate | tie_expected_rate |")
        lines.append("|---|---:|---:|---:|---:|")
        kinds = sorted(set(r["pair_kind"] for r in compare))
        for k in kinds:
            rs = [r for r in compare if r["pair_kind"] == k]
            acc = mean(r["correct"] for r in rs)
            non_tie = mean(float(r["expected"] in {"A", "B"}) for r in rs)
            tie = mean(float(r["expected"] == "tie") for r in rs)
            lines.append(f"| {k} | {len(rs)} | {acc:.3f} | {non_tie:.3f} | {tie:.3f} |")

        lines.append("\n## Compare prediction distribution\n")
        lines.append("| predicted | n |")
        lines.append("|---|---:|")
        counts = {}
        for r in compare:
            counts[r["predicted"]] = counts.get(r["predicted"], 0) + 1
        for k, v in sorted(counts.items()):
            lines.append(f"| {k or '(empty)'} | {v} |")

    if equal:
        lines.append("\n## Equal accuracy\n")
        lines.append("| n | accuracy | expected_equiv_rate | predicted_equiv_rate |")
        lines.append("|---:|---:|---:|---:|")
        acc = mean(r["correct"] for r in equal)
        exp = mean(float(r["expected_equivalent"]) for r in equal)
        pred = mean(float(r["predicted_equivalent"]) for r in equal)
        lines.append(f"| {len(equal)} | {acc:.3f} | {exp:.3f} | {pred:.3f} |")

        lines.append("\n## Equal relation distribution\n")
        lines.append("| relation | n |")
        lines.append("|---|---:|")
        counts = {}
        for r in equal:
            counts[r["relation"]] = counts.get(r["relation"], 0) + 1
        for k, v in sorted(counts.items()):
            lines.append(f"| {k or '(empty)'} | {v} |")

    # Actual trace monotonicity according to offline utility.
    monotonic_edges = []
    for gk in keys:
        states = [r for r in groups[gk] if state_order(get_state_id(r)) is not None]
        states = sorted(states, key=lambda r: state_order(get_state_id(r)))
        for i in range(len(states) - 1):
            monotonic_edges.append(float(get_utility(states[i + 1]) >= get_utility(states[i])))

    if monotonic_edges:
        lines.append("\n## Offline q-trace monotonicity\n")
        lines.append("| adjacent_edges | nondecreasing_utility_rate |")
        lines.append("|---:|---:|")
        lines.append(f"| {len(monotonic_edges)} | {mean(monotonic_edges):.3f} |")

    path.write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qtrace-path", default="experiments/deltaq/results_retrieval_gain_gpt5mini_full/bm25_validation.jsonl")
    ap.add_argument("--out-dir", default="experiments/deltaq/results_qtrace_order_judge_probe")
    ap.add_argument("--max-examples", type=int, default=20)

    ap.add_argument("--pair-mode", default="adjacent", choices=["adjacent", "target", "all", "all_pairs"])
    ap.add_argument("--include-equal", action="store_true")
    ap.add_argument("--max-equal-pairs-per-example", type=int, default=2)
    ap.add_argument("--shuffle-pair-order", action="store_true")
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--tol", type=float, default=1e-6)

    ap.add_argument("--model", default=os.environ.get("TASK_MODEL", "openai/gpt-5-mini"))
    ap.add_argument("--api-base", default=os.environ.get("TASK_API_BASE", ""))
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--num-threads", type=int, default=4)
    ap.add_argument("--max-doc-chars", type=int, default=5000)
    ap.add_argument("--save-prompts", action="store_true")

    args = ap.parse_args()

    if "gpt-5" in args.model:
        args.temperature = 1.0
        if args.max_tokens < 16000:
            args.max_tokens = 16000

    rng = random.Random(args.seed)

    rows = read_jsonl(args.qtrace_path)
    groups = build_groups(rows)
    keys = choose_examples(groups, args.max_examples)

    compare_tasks = build_compare_tasks(
        groups=groups,
        keys=keys,
        pair_mode=args.pair_mode,
        shuffle_pair_order=args.shuffle_pair_order,
        rng=rng,
        tol=args.tol,
    )

    equal_tasks = []
    if args.include_equal:
        equal_tasks = build_equal_tasks(
            groups=groups,
            keys=keys,
            max_equal_pairs_per_example=args.max_equal_pairs_per_example,
            rng=rng,
            tol=args.tol,
        )

    tasks = compare_tasks + equal_tasks

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / "tasks.jsonl", [
        {k: v for k, v in t.items() if k not in {"row_a", "row_b"}}
        for t in tasks
    ])

    print("[qtrace path]", args.qtrace_path)
    print("[rows]", len(rows))
    print("[groups]", len(groups))
    print("[selected examples]", len(keys))
    print("[compare tasks]", len(compare_tasks))
    print("[equal tasks]", len(equal_tasks))
    print("[out dir]", out_dir)

    # Main thread LM config for DSPy fallback.
    dspy.settings.configure(lm=make_lm(args))

    results = []
    if args.num_threads <= 1:
        for t in tqdm(tasks, desc="judging q-trace order", unit="pair", dynamic_ncols=True):
            results.append(run_task(args, t))
    else:
        with ThreadPoolExecutor(max_workers=args.num_threads) as pool:
            futs = [pool.submit(run_task, args, t) for t in tasks]
            for fut in tqdm(as_completed(futs), total=len(futs), desc="judging q-trace order", unit="pair", dynamic_ncols=True):
                results.append(fut.result())

    results.sort(key=lambda r: (
        str(r.get("group_key", "")),
        str(r.get("task_type", "")),
        str(r.get("pair_kind", "")),
        str(r.get("a_order", "")),
        str(r.get("b_order", "")),
    ))

    write_jsonl(out_dir / "judgments.jsonl", results)
    write_summary(out_dir / "summary.md", results, groups, keys)

    config = vars(args)
    config["selected_examples"] = len(keys)
    config["num_tasks"] = len(tasks)
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False))

    print()
    print("[wrote]", out_dir / "summary.md")
    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
