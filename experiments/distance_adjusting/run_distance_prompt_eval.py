#!/usr/bin/env python3
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
from collections import defaultdict

import dspy

try:
    from dotenv import load_dotenv
    load_dotenv("/home/jinwoo/gepa-official/.env")
except Exception:
    pass

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
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def clean_lm_text(x):
    if x is None:
        return ""
    if isinstance(x, list):
        x = x[0] if x else ""
    x = str(x).strip()
    x = re.sub(r"^```(?:json|text)?", "", x, flags=re.I).strip()
    x = re.sub(r"```$", "", x).strip()
    return x.strip("` \n")


def extract_json_obj(text):
    text = clean_lm_text(text)
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


def lm_call(args, prompt):
    lm = get_lm(args)
    last_error = None
    for i in range(args.retries):
        try:
            # print(f"[DEBUG_LM_CALL] retry={i+1}/{args.retries} prompt_chars={len(prompt)}", flush=True)
            out = lm(prompt)

            text = clean_lm_text(out)
            # print("[DEBUG_CLEAN_TEXT_REPR]", repr(text)[:3000], flush=True)

            if text:
                return text, None
            last_error = "empty output"

        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"

        if i + 1 < args.retries:
            time.sleep(2.0 * (i + 1))

    return "", last_error


def compact_json(x):
    return json.dumps(x, ensure_ascii=False, indent=2)


def filter_state(s, view):
    if view == "full":
        return s
    keep = {
        "compact": {
            "name", "kind", "query", "retrieved_titles",
            "retrieval_focus", "anchors", "bridge_clues",
        },
        "minimal": {
            "name", "kind", "query", "retrieved_titles",
            "retrieval_focus", "anchors",
        },
    }[view]
    return {k: v for k, v in (s or {}).items() if k in keep}


def filter_segment(seg, view):
    if view == "full":
        return seg
    return {
        "from_state": filter_state(seg.get("from_state"), view),
        "to_state": filter_state(seg.get("to_state"), view),
    }


def resolve_state_view(task, state_view):
    if state_view == "left_compact_right_full":
        return "compact" if task.get("task_kind") == "left_recovery" else "full"
    if state_view == "left_minimal_right_full":
        return "minimal" if task.get("task_kind") == "left_recovery" else "full"
    return state_view


def render_prompt(template, task, segment_a, segment_b, state_view, cache_bust_tag):
    state_view = resolve_state_view(task, state_view)
    segment_a = filter_segment(segment_a, state_view)
    segment_b = filter_segment(segment_b, state_view)

    segments = [
        {
            "segment_index": 0,
            "segment_label": "A",
            **segment_a,
        },
        {
            "segment_index": 1,
            "segment_label": "B",
            **segment_b,
        },
    ]

    prompt = (
        template
        .replace("{question}", str(task.get("question", "")))
        .replace("{summary_1}", str(task.get("summary_1", "")))
        .replace("{segments_json}", compact_json(segments))
    )

    if cache_bust_tag:
        prompt = f"Run tag: {cache_bust_tag}\nState view: {state_view}\n\n" + prompt
    return prompt


def parse_larger_segment(raw):
    obj = extract_json_obj(raw)
    if isinstance(obj, dict):
        val = str(obj.get("larger_segment", "")).strip().upper()
        if val in {"A", "B", "TIE"}:
            return "tie" if val == "TIE" else val, obj

        try:
            idx = int(obj.get("segment_index"))
            if idx == 0:
                return "A", obj
            if idx == 1:
                return "B", obj
            if idx < 0:
                return "tie", obj
        except Exception:
            pass

    text = str(raw).upper()
    if re.search(r"\b(TIE|EQUAL|SIMILAR)\b", text):
        return "tie", obj or {"raw": raw}
    if re.search(r"\bA\b", text):
        return "A", obj or {"raw": raw}
    if re.search(r"\bB\b", text):
        return "B", obj or {"raw": raw}
    return "invalid", obj or {"raw": raw}


def run_task(args, template, task, rng_seed):
    rng = random.Random(rng_seed)

    sub = task["sub_segment"]
    full = task["full_segment"]

    if args.shuffle_pair_order and rng.random() < 0.5:
        segment_a, segment_b = full, sub
        expected = "A"
        shuffled = True
    else:
        segment_a, segment_b = sub, full
        expected = "B"
        shuffled = False

    prompt = render_prompt(template, task, segment_a, segment_b, args.state_view, args.cache_bust_tag)
    raw, err = lm_call(args, prompt)
    pred, obj = parse_larger_segment(raw)
    correct = pred == expected

    return {
        "task_id": task["task_id"],
        "triple_id": task.get("triple_id") or task.get("midpoint_id") or task.get("task_id"),
        "idx": task["idx"],
        "split_iter": task.get("split_iter"),
        "num_edges_before_split": task.get("num_edges_before_split"),
        "selected_segment_for_next_split": task.get("selected_segment_for_next_split"),
        "task_kind": task["task_kind"],
        "definition": task.get("definition", task.get("distance_object", "prompt_feedback_pgrad")),
        "R_i_name": task.get("R_i_name"),
        "R_mid_name": task.get("R_mid_name"),
        "R_next_name": task.get("R_next_name"),
        "expected": expected,
        "predicted": pred,
        "correct": float(correct),
        "shuffled": shuffled,
        "error": err,
        "judge_obj": obj,
        "raw": raw,
        "prompt": prompt if args.save_prompts else None,
    }


def rate(xs):
    return sum(xs) / len(xs) if xs else 0.0


def summarize(rows):
    left = [r for r in rows if r["task_kind"] == "left_recovery"]
    right = [r for r in rows if r["task_kind"] == "right_recovery"]

    by_triple = defaultdict(dict)
    for r in rows:
        by_triple[r["triple_id"]][r["task_kind"]] = bool(r["correct"])

    both = []
    for d in by_triple.values():
        if "left_recovery" in d and "right_recovery" in d:
            both.append(float(d["left_recovery"] and d["right_recovery"]))

    return {
        "n_tasks": len(rows),
        "n_midpoint_triples": len(by_triple),
        "left_recovery_rate": rate([float(r["correct"]) for r in left]),
        "right_recovery_rate": rate([float(r["correct"]) for r in right]),
        "both_recovery_rate": rate(both),
        "mean_recovery_rate": rate([float(r["correct"]) for r in rows]),
        "tie_or_invalid_rate": rate([float(r["predicted"] in {"tie", "invalid"}) for r in rows]),
    }


def write_summary_md(path, args, summary):
    lines = []
    lines.append("# Distance prompt recovery eval")
    lines.append("")
    lines.append(f"- tasks_path: `{args.tasks_path}`")
    lines.append(f"- prompt_path: `{args.prompt_path}`")
    lines.append("")
    for k, v in summary.items():
        if isinstance(v, float):
            lines.append(f"- {k}: {v:.4f}")
        else:
            lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("- left_recovery: full edge is judged larger than R_i -> R_mid.")
    lines.append("- right_recovery: full edge is judged larger than R_mid -> R_next.")
    lines.append("- both_recovery: both inequalities recover for the same midpoint triple.")
    Path(path).write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-path", required=True)
    ap.add_argument("--prompt-path", required=True)
    ap.add_argument("--out-dir", required=True)

    ap.add_argument("--model", default=os.environ.get("TASK_MODEL", "openai/gpt-5-mini"))
    ap.add_argument("--api-base", default=os.environ.get("TASK_API_BASE", ""))
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--num-threads", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--shuffle-pair-order", action="store_true")
    ap.add_argument("--save-prompts", action="store_true")
    ap.add_argument(
        "--state-view",
        choices=["full", "compact", "minimal", "left_compact_right_full", "left_minimal_right_full"],
        default="full",
    )
    ap.add_argument("--cache-bust-tag", default="")
    args = ap.parse_args()

    if "gpt-5" in args.model:
        args.temperature = 1.0
        args.max_tokens = max(args.max_tokens, 16000)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    template = Path(args.prompt_path).read_text()
    tasks = read_jsonl(args.tasks_path)
    if args.limit:
        tasks = tasks[:args.limit]

    config = vars(args)
    config["num_tasks"] = len(tasks)
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False))

    dspy.settings.configure(lm=make_lm(args))

    results = []
    if args.num_threads <= 1:
        for i, task in enumerate(tqdm(tasks, desc="distance prompt eval", unit="task")):
            results.append(run_task(args, template, task, args.seed + i))
    else:
        with ThreadPoolExecutor(max_workers=args.num_threads) as pool:
            futs = [
                pool.submit(run_task, args, template, task, args.seed + i)
                for i, task in enumerate(tasks)
            ]
            for fut in tqdm(as_completed(futs), total=len(futs), desc="distance prompt eval", unit="task"):
                results.append(fut.result())

    results.sort(key=lambda r: (str(r["idx"]), str(r["split_iter"]), r["task_kind"]))

    write_jsonl(out_dir / "judgments.jsonl", results)

    summary = summarize(results)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    write_summary_md(out_dir / "summary.md", args, summary)

    print((out_dir / "summary.md").read_text())


if __name__ == "__main__":
    main()
