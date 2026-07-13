import argparse
import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from collections import Counter

# Reuse helpers from the selected6 runner.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from run_actual300_selected_cached import (
    read_jsonl,
    write_jsonl,
    read_json,
    write_json,
    extract_dev300_case_ids,
    patch_split_full143_ids,
    maybe_timeout_args,
)

COND = "manual_best"

def valid_result_row(row):
    return (
        row.get("condition") == COND
        and row.get("case_id") is not None
        and not row.get("error")
    )

def normalize_to_actual300(row, source):
    r = dict(row)
    r["source_eval_scope"] = r.get("eval_scope")
    r["eval_scope"] = "actual300"
    r["actual300_cache_source"] = source
    return r

def case_key(row):
    return int(row["case_id"])

def replace_prompt_fields(obj, manual_prompt, path=""):
    """
    Clone a base prompt row and replace the create_query_hop2 instruction.
    This is intentionally conservative: it modifies only likely prompt-bearing fields.
    """
    changed = []

    def rec(x, p):
        if isinstance(x, dict):
            for k, v in list(x.items()):
                kp = f"{p}.{k}" if p else str(k)
                kl = str(k).lower()

                if isinstance(v, str):
                    is_target_key = (
                        kl in {
                            "prompt",
                            "instruction",
                            "instructions",
                            "updated_prompt",
                            "new_prompt",
                            "candidate_prompt",
                            "create_query_hop2",
                            "create_query_hop2_prompt",
                            "create_query_hop2_instruction",
                        }
                        or ("create_query_hop2" in kp.lower() and any(t in kl for t in ["prompt", "instruction", "text"]))
                    )

                    looks_like_hop2_prompt = (
                        "summary_1" in v
                        and "question" in v
                        and ("BM25" in v or "second-hop" in v or "second hop" in v or "query" in v)
                    )

                    if is_target_key or looks_like_hop2_prompt:
                        x[k] = manual_prompt
                        changed.append(kp)
                else:
                    rec(v, kp)

        elif isinstance(x, list):
            for i, v in enumerate(x):
                rec(v, f"{p}[{i}]")

    rec(obj, path)
    return changed

def make_manual_prompt_row(batch_id, results_dir, manual_prompt_path, out_path):
    manual_prompt = Path(manual_prompt_path).read_text()

    base_prompt_file = results_dir / f"positive_safety_b10_batch{batch_id}_prompts.jsonl"
    rows = read_jsonl(base_prompt_file)
    base_rows = [r for r in rows if r.get("condition") == "base"]
    if not base_rows:
        raise RuntimeError(f"No base row found in {base_prompt_file}")

    row = copy.deepcopy(base_rows[0])
    row["condition"] = COND
    row["manual_best_source"] = str(manual_prompt_path)

    changed = replace_prompt_fields(row, manual_prompt)
    if not changed:
        print("base row keys:", sorted(row.keys()))
        raise RuntimeError(
            "Could not find a prompt field to replace. "
            "Inspect the base prompt row structure."
        )

    row["manual_best_replaced_fields"] = changed

    write_jsonl(out_path, [row])

    print("\nmanual_best prompt row")
    print(" batch:", batch_id)
    print(" source base file:", base_prompt_file)
    print(" output:", out_path)
    print(" replaced fields:")
    for c in changed:
        print("  -", c)

def build_cache(actual_out):
    cache = {}
    for r in read_jsonl(actual_out):
        if valid_result_row(r):
            cache[case_key(r)] = normalize_to_actual300(r, source=r.get("actual300_cache_source", "manual_best_previous"))
    return cache

def run_eval_for_missing(args, batch_id, missing_ids, prompt_path, tmp_dir):
    if not missing_ids:
        return []

    split_obj = read_json(args.split)
    tmp_split = tmp_dir / f"manual_best_actual300_missing_batch{batch_id}_split.json"
    tmp_out = tmp_dir / f"manual_best_actual300_missing_batch{batch_id}_eval.jsonl"
    tmp_summary = tmp_dir / f"manual_best_actual300_missing_batch{batch_id}_summary.json"
    tmp_summary_md = tmp_dir / f"manual_best_actual300_missing_batch{batch_id}_summary.md"

    patched_split = patch_split_full143_ids(split_obj, missing_ids)

    # Hard override full143 fields, same as selected6 runner.
    if isinstance(patched_split, dict):
        patched_split["full143"] = missing_ids
        patched_split["full143_ids"] = missing_ids
        patched_split["full143_case_ids"] = missing_ids

        if "scopes" not in patched_split or not isinstance(patched_split.get("scopes"), dict):
            patched_split["scopes"] = {}
        patched_split["scopes"]["full143"] = missing_ids

        if "eval_scopes" not in patched_split or not isinstance(patched_split.get("eval_scopes"), dict):
            patched_split["eval_scopes"] = {}
        patched_split["eval_scopes"]["full143"] = missing_ids

    write_json(tmp_split, patched_split)

    tmp_obj = read_json(tmp_split)
    probe_lengths = {}
    if isinstance(tmp_obj, dict):
        for k in ["full143", "full143_ids", "full143_case_ids"]:
            if isinstance(tmp_obj.get(k), list):
                probe_lengths[k] = len(tmp_obj[k])
        for k in ["scopes", "eval_scopes"]:
            if isinstance(tmp_obj.get(k), dict) and isinstance(tmp_obj[k].get("full143"), list):
                probe_lengths[f"{k}.full143"] = len(tmp_obj[k]["full143"])
    print("tmp split full143 probe lengths:", probe_lengths)

    if tmp_out.exists():
        tmp_out.unlink()

    env = os.environ.copy()
    env.setdefault("LITELLM_LOG", "ERROR")
    env.setdefault("LITELLM_SET_VERBOSE", "False")
    env.setdefault("LITELLM_TIMEOUT", str(args.request_timeout))
    env.setdefault("LITELLM_REQUEST_TIMEOUT", str(args.request_timeout))
    env.setdefault("OPENAI_TIMEOUT", str(args.request_timeout))
    env.setdefault("HTTPX_TIMEOUT", str(args.request_timeout))

    timeout_extra = maybe_timeout_args(args.evaluator, args.request_timeout)

    cmd = [
        sys.executable, str(args.evaluator),
        "--split", str(tmp_split),
        "--case-state-index", str(args.case_state_index),
        "--prompts", str(prompt_path),
        "--fixed-prompt-config", str(args.fixed_prompt_config),
        "--final-answerer-refs", str(args.final_answerer_refs),
        "--out", str(tmp_out),
        "--summary-out", str(tmp_summary),
        "--summary-md", str(tmp_summary_md),
        "--composition", args.composition,
        "--batch-id", str(batch_id),
        "--scopes", "full143",
        "--retriever-dir", str(args.retriever_dir),
        "--k", str(args.k),
        "--model", args.model,
        "--temperature", str(args.temperature),
        "--query-max-tokens", str(args.query_max_tokens),
        "--summary-max-tokens", str(args.summary_max_tokens),
        "--answer-max-tokens", str(args.answer_max_tokens),
        "--num-threads", str(args.num_threads),
        "--retries", str(args.retries),
        "--task-retries", str(args.task_retries),
    ] + timeout_extra

    print("\n" + "=" * 100)
    print(f"RUN manual_best actual300 / batch={batch_id} / missing_ids={len(missing_ids)}")
    print("tmp_split:", tmp_split)
    print("tmp_out:", tmp_out)
    print("timeout_extra:", timeout_extra if timeout_extra else "(env timeout only)")
    print(" ".join(cmd))
    print("=" * 100)

    subprocess.run(cmd, env=env, check=True)

    rows = read_jsonl(tmp_out)
    ok = [r for r in rows if valid_result_row(r)]
    err = [r for r in rows if r.get("error")]
    print(f"manual_best batch={batch_id} temp rows={len(rows)} ok={len(ok)} err={len(err)}")
    if err:
        print("error types:", Counter(r.get("error_type") for r in err))

    return [normalize_to_actual300(r, source="new_manual_best_eval") for r in ok]

def write_final(path, cache, all_ids):
    rows = []
    for cid in all_ids:
        if cid in cache:
            rows.append(cache[cid])
    rows.sort(key=lambda r: int(r.get("case_id", -1)))
    write_jsonl(path, rows)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="experiments/prompt_update/data/positive_safety_b10_split_seed0.json")
    ap.add_argument("--case-state-index", default="experiments/prompt_update/cache/positive_safety/case_state_index.json")
    ap.add_argument("--fixed-prompt-config", default="experiments/prompt_update/cache/fixed_prompt_config.json")
    ap.add_argument("--final-answerer-refs", default="experiments/prompt_update/cache/final_answerer_refs.json")
    ap.add_argument("--results-dir", default="experiments/prompt_update/results")
    ap.add_argument("--out-dir", default="experiments/prompt_update/results/actual300_manual_best")
    ap.add_argument("--manual-prompt", default="experiments/prompt_update/prompts/manual_best_create_query_hop2.txt")
    ap.add_argument("--evaluator", default="experiments/prompt_update/scripts/evaluate_positive_safety_prompts.py")
    ap.add_argument("--retriever-dir", default="examples/hotpotqa")
    ap.add_argument("--composition", default="mixed_custom")
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--model", default="openai/gpt-5-mini")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--query-max-tokens", type=int, default=512)
    ap.add_argument("--summary-max-tokens", type=int, default=4096)
    ap.add_argument("--answer-max-tokens", type=int, default=2048)
    ap.add_argument("--num-threads", type=int, default=12)
    ap.add_argument("--retries", type=int, default=10)
    ap.add_argument("--task-retries", type=int, default=10)
    ap.add_argument("--request-timeout", type=int, default=300)
    ap.add_argument("--batches", type=int, nargs="+", default=[0, 1, 2])
    args = ap.parse_args()

    args.results_dir = Path(args.results_dir)
    args.out_dir = Path(args.out_dir)
    args.tmp_dir = args.out_dir / "_tmp"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.tmp_dir.mkdir(parents=True, exist_ok=True)

    all_ids = extract_dev300_case_ids(args.split, args.case_state_index)
    print("actual300 case ids:", len(all_ids), "min:", min(all_ids), "max:", max(all_ids))
    if len(all_ids) != 300:
        print("WARNING: actual id count is not 300:", len(all_ids))

    for B in args.batches:
        prompt_path = args.tmp_dir / f"manual_best_batch{B}_prompts.jsonl"
        make_manual_prompt_row(B, args.results_dir, args.manual_prompt, prompt_path)

        out = args.out_dir / f"positive_safety_actual300_manual_best_batch{B}_eval.jsonl"
        cache = build_cache(out)

        have = set(cache.keys())
        missing = [cid for cid in all_ids if cid not in have]

        print("\n" + "=" * 100)
        print("BATCH", B)
        print(f"manual_best have={len(have)}/{len(all_ids)} missing={len(missing)}")
        print("out:", out)

        if missing:
            new_rows = run_eval_for_missing(args, B, missing, prompt_path, args.tmp_dir)
            for r in new_rows:
                if valid_result_row(r):
                    cache[case_key(r)] = r

        rows = write_final(out, cache, all_ids)
        print("\nFINAL manual_best BATCH", B)
        print("written rows:", len(rows), "/ expected", len(all_ids))
        still_missing = [cid for cid in all_ids if cid not in {int(r["case_id"]) for r in rows}]
        if still_missing:
            print("STILL MISSING:", len(still_missing), still_missing[:20])
            print("Rerun the same command; completed rows will be reused.")

if __name__ == "__main__":
    main()
