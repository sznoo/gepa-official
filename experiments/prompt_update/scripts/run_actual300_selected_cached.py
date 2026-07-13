import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from collections import Counter

SELECTED_CONDITIONS = [
    "base",
    "delta_p_custom_signed",
    "endpoint_delta_custom_signed",
    "delta_p_neg_only",
    "endpoint_delta_neg_only",
    "endpoint_delta_contrastive_raw_C",
]

def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    with path.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")

def read_json(path):
    with open(path) as f:
        return json.load(f)

def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)

def extract_ids_from_obj(obj):
    found = set()

    def maybe_add(v):
        try:
            if isinstance(v, bool):
                return
            iv = int(v)
            if 0 <= iv < 100000:
                found.add(iv)
        except Exception:
            pass

    def rec(x, key_hint=""):
        if isinstance(x, dict):
            # Common record forms.
            if "case_id" in x:
                maybe_add(x["case_id"])
            if "id" in x and ("case" in key_hint.lower() or "bucket" in key_hint.lower()):
                maybe_add(x["id"])

            for k, v in x.items():
                kl = str(k).lower()

                # If dict key itself is numeric under a case-ish container, treat as case id.
                if any(t in kl for t in ["case", "bucket", "clean", "fragile", "retrieval", "other", "dev300", "split"]):
                    try:
                        if isinstance(v, (dict, list)):
                            maybe_add(k)
                    except Exception:
                        pass

                rec(v, key_hint=str(k))

        elif isinstance(x, list):
            for v in x:
                if isinstance(v, int):
                    maybe_add(v)
                elif isinstance(v, str) and v.isdigit():
                    maybe_add(v)
                else:
                    rec(v, key_hint=key_hint)

    rec(obj)
    return sorted(found)

def extract_dev300_case_ids(split_path, case_state_index_path):
    """
    actual300 should come from the split file buckets, not from the evaluator's full143 scope.
    Expected prior: C_clean 163 + C_fragile 26 + W_retrieval 39 + W_other 72 = 300.
    """
    split = read_json(split_path)

    # First: targeted bucket extraction.
    wanted_buckets = {"C_clean", "C_fragile", "W_retrieval", "W_other"}
    bucket_ids = set()

    def rec_bucket(x, key=None):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in wanted_buckets:
                    ids = extract_ids_from_obj(v)
                    bucket_ids.update(ids)
                rec_bucket(v, k)
        elif isinstance(x, list):
            for v in x:
                rec_bucket(v, key)

    rec_bucket(split)

    if len(bucket_ids) == 300:
        return sorted(bucket_ids)

    # Second: explicit dev300-like fields.
    for key in [
        "dev300", "dev300_ids", "dev300_case_ids",
        "all300", "all300_ids", "case_ids", "all_case_ids",
    ]:
        if isinstance(split, dict) and key in split:
            ids = extract_ids_from_obj(split[key])
            if len(ids) >= 250:
                return sorted(ids)

    # Third: broad split extraction.
    ids = extract_ids_from_obj(split)
    if len(ids) >= 300:
        # Keep all if exactly 300. If more, prefer first 300 sorted only as last resort.
        if len(ids) == 300:
            return sorted(ids)
        print(f"WARNING: broad split extraction found {len(ids)} ids; using all extracted ids, not truncating.")
        return sorted(ids)

    # Diagnostic fallback: show structure before failing.
    print("Could not find 300 ids from split.")
    if isinstance(split, dict):
        print("top-level split keys:", sorted(split.keys()))
        for k, v in split.items():
            if isinstance(v, list):
                print("list key:", k, "len:", len(v), "head:", v[:3])
            elif isinstance(v, dict):
                print("dict key:", k, "keys head:", list(v.keys())[:10])

    # Old behavior as fallback, but this is likely full143-only.
    csi = read_json(case_state_index_path)
    ids = extract_ids_from_obj(csi)
    if len(ids) >= 250:
        return sorted(ids)

    raise RuntimeError(
        f"Could not extract actual300 ids. From split buckets got {len(bucket_ids)} ids; "
        f"from broad split got {len(extract_ids_from_obj(split))} ids; "
        f"from case_state_index got {len(ids)} ids."
    )

def select_prompts(batch_id, results_dir, out_path):
    main_p = results_dir / f"positive_safety_b10_batch{batch_id}_prompts.jsonl"
    rawc_p = results_dir / f"positive_safety_b10_batch{batch_id}_contrastive_raw_c_prompts.jsonl"

    rows = read_jsonl(main_p) + read_jsonl(rawc_p)
    by_cond = {}
    for r in rows:
        c = r.get("condition")
        if c in SELECTED_CONDITIONS:
            by_cond[c] = r

    missing = [c for c in SELECTED_CONDITIONS if c not in by_cond]
    if missing:
        raise RuntimeError(f"Missing selected prompt rows for batch {batch_id}: {missing}")

    selected = [by_cond[c] for c in SELECTED_CONDITIONS]
    write_jsonl(out_path, selected)
    return selected

def patch_split_full143_ids(split_obj, ids):
    """
    Existing evaluator already knows --scopes full143.
    We reuse that path by replacing full143 ids with the target missing ids.
    This keeps evaluator internals unchanged.
    """
    obj = copy.deepcopy(split_obj)

    common_top_keys = [
        "full143",
        "full143_ids",
        "full143_case_ids",
        "eval_full143_ids",
        "full_eval_ids",
        "full_eval_case_ids",
    ]
    for k in common_top_keys:
        obj[k] = ids

    common_maps = [
        "scopes",
        "eval_scopes",
        "scope_to_case_ids",
        "case_ids_by_scope",
        "eval_case_ids_by_scope",
        "ids_by_scope",
    ]
    for k in common_maps:
        if isinstance(obj.get(k), dict):
            obj[k]["full143"] = ids

    # Recursive conservative replacement:
    # any key explicitly named full143 and whose value is list-like gets replaced.
    def rec(x):
        if isinstance(x, dict):
            for k, v in list(x.items()):
                if k == "full143" and isinstance(v, list):
                    x[k] = ids
                else:
                    rec(v)
        elif isinstance(x, list):
            for v in x:
                rec(v)

    rec(obj)
    return obj

def normalize_to_actual300(row, source):
    r = dict(row)
    r["source_eval_scope"] = r.get("eval_scope")
    r["eval_scope"] = "actual300"
    r["actual300_cache_source"] = source
    return r

def case_key(row):
    return (row.get("condition"), int(row.get("case_id")))

def valid_result_row(row):
    if row.get("condition") not in SELECTED_CONDITIONS:
        return False
    if row.get("case_id") is None:
        return False
    if row.get("error"):
        return False
    return True

def build_initial_cache(batch_id, results_dir, actual_out):
    cache = {}

    # Lower priority: previous b10 eval rows. Reuse both batch10 and full143 rows.
    old_p = results_dir / f"positive_safety_b10_batch{batch_id}_eval.jsonl"
    for r in read_jsonl(old_p):
        if not valid_result_row(r):
            continue
        cache[case_key(r)] = normalize_to_actual300(r, source="positive_safety_b10_eval")

    # Higher priority: previous actual300 rows, so rerun is resumable.
    for r in read_jsonl(actual_out):
        if not valid_result_row(r):
            continue
        cache[case_key(r)] = normalize_to_actual300(r, source=r.get("actual300_cache_source", "actual300_previous"))

    return cache

def help_text(script_path):
    try:
        p = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        return p.stdout or ""
    except Exception:
        return ""

def maybe_timeout_args(script_path, request_timeout):
    """
    Add timeout flag only if the evaluator exposes one.
    Otherwise rely on env variables + retries.
    """
    h = help_text(script_path)
    candidates = [
        "--request-timeout",
        "--timeout",
        "--api-timeout",
        "--task-timeout",
    ]
    for flag in candidates:
        if flag in h:
            return [flag, str(request_timeout)]
    return []


def force_replace_full143_like_lists(split_obj, target_ids):
    """
    The evaluator may read a nested 143-list rather than top-level full143.
    Replace all full143-like lists of length 143 with target_ids.
    Handles int lists and dict lists with case_id/id.
    """
    target_ids = [int(x) for x in target_ids]
    replaced_paths = []

    def looks_like_case_id_list(xs):
        if not isinstance(xs, list) or len(xs) != 143:
            return False
        ok = 0
        for x in xs:
            if isinstance(x, bool):
                continue
            if isinstance(x, int):
                ok += 1
            elif isinstance(x, str) and x.isdigit():
                ok += 1
        return ok >= 100

    def looks_like_case_dict_list(xs):
        if not isinstance(xs, list) or len(xs) != 143:
            return False
        ok = 0
        for x in xs:
            if isinstance(x, dict) and ("case_id" in x or "id" in x):
                ok += 1
        return ok >= 100

    # Build id -> representative dict from the whole split.
    id_to_obj = {}

    def collect_objs(x):
        if isinstance(x, dict):
            cid = None
            if "case_id" in x:
                cid = x.get("case_id")
            elif "id" in x:
                cid = x.get("id")
            try:
                if cid is not None:
                    id_to_obj[int(cid)] = x
            except Exception:
                pass
            for v in x.values():
                collect_objs(v)
        elif isinstance(x, list):
            for v in x:
                collect_objs(v)

    collect_objs(split_obj)

    def rec(x, path=""):
        if isinstance(x, dict):
            for k, v in list(x.items()):
                kp = f"{path}.{k}" if path else str(k)

                if looks_like_case_id_list(v):
                    x[k] = target_ids
                    replaced_paths.append((kp, "id_list", 143, len(target_ids)))

                elif looks_like_case_dict_list(v):
                    new_list = []
                    missing_obj = False
                    for cid in target_ids:
                        if cid in id_to_obj:
                            new_list.append(id_to_obj[cid])
                        else:
                            missing_obj = True
                            new_list.append({"case_id": cid})
                    x[k] = new_list
                    replaced_paths.append((kp, "dict_list", 143, len(target_ids), "fallback_obj" if missing_obj else "mapped_obj"))

                else:
                    rec(v, kp)

        elif isinstance(x, list):
            for i, v in enumerate(x):
                rec(v, f"{path}[{i}]")

    rec(split_obj)

    # Also force common fields.
    if isinstance(split_obj, dict):
        split_obj["full143"] = target_ids
        split_obj["full143_ids"] = target_ids
        split_obj["full143_case_ids"] = target_ids

        if "scopes" not in split_obj or not isinstance(split_obj.get("scopes"), dict):
            split_obj["scopes"] = {}
        split_obj["scopes"]["full143"] = target_ids

        if "eval_scopes" not in split_obj or not isinstance(split_obj.get("eval_scopes"), dict):
            split_obj["eval_scopes"] = {}
        split_obj["eval_scopes"]["full143"] = target_ids

    return split_obj, replaced_paths

def run_eval_for_missing(args, batch_id, missing_ids, selected_prompts_path, tmp_dir):
    if not missing_ids:
        return []

    split_obj = read_json(args.split)
    tmp_split = tmp_dir / f"actual300_missing_batch{batch_id}_split.json"
    tmp_out = tmp_dir / f"actual300_missing_batch{batch_id}_eval.jsonl"
    tmp_summary = tmp_dir / f"actual300_missing_batch{batch_id}_summary.json"
    tmp_summary_md = tmp_dir / f"actual300_missing_batch{batch_id}_summary.md"

    patched_split = patch_split_full143_ids(split_obj, missing_ids)
    patched_split, replaced_paths = force_replace_full143_like_lists(patched_split, missing_ids)
    print("force replaced full143-like lists:")
    for item in replaced_paths:
        print("  ", item)

    write_json(tmp_split, patched_split)

    # Verify the temp split before launching evaluator.
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
        "--prompts", str(selected_prompts_path),
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
    print(f"RUN missing actual300 eval / batch={batch_id} / missing_ids={len(missing_ids)}")
    print("timeout_extra:", timeout_extra if timeout_extra else "(no evaluator timeout flag found; using env timeout variables)")
    print("tmp_split:", tmp_split)
    print("tmp_out:", tmp_out)
    print("cmd:")
    print(" ".join(cmd))
    print("=" * 100)

    subprocess.run(cmd, env=env, check=True)

    rows = read_jsonl(tmp_out)
    ok = [r for r in rows if valid_result_row(r)]
    err = [r for r in rows if r.get("error")]

    print(f"batch={batch_id} temp rows={len(rows)} ok={len(ok)} err={len(err)}")
    if err:
        print("error conditions:", Counter(r.get("condition") for r in err))

    return [normalize_to_actual300(r, source="new_missing_eval") for r in ok]

def write_sorted_actual_out(path, cache, all_ids):
    rows = []
    cond_order = {c: i for i, c in enumerate(SELECTED_CONDITIONS)}
    all_set = set(all_ids)

    for (cond, cid), r in cache.items():
        if cond in SELECTED_CONDITIONS and cid in all_set:
            rows.append(r)

    rows.sort(key=lambda r: (cond_order.get(r.get("condition"), 99), int(r.get("case_id", -1))))
    write_jsonl(path, rows)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="experiments/prompt_update/data/positive_safety_b10_split_seed0.json")
    ap.add_argument("--case-state-index", default="experiments/prompt_update/cache/positive_safety/case_state_index.json")
    ap.add_argument("--fixed-prompt-config", default="experiments/prompt_update/cache/fixed_prompt_config.json")
    ap.add_argument("--final-answerer-refs", default="experiments/prompt_update/cache/final_answerer_refs.json")
    ap.add_argument("--results-dir", default="experiments/prompt_update/results")
    ap.add_argument("--out-dir", default="experiments/prompt_update/results/actual300_selected")
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
    print("dev300 case ids:", len(all_ids), "min:", min(all_ids), "max:", max(all_ids))
    if len(all_ids) != 300:
        print(f"WARNING: extracted {len(all_ids)} case ids, not exactly 300")

    for B in args.batches:
        selected_prompts_path = args.tmp_dir / f"selected6_batch{B}_prompts.jsonl"
        select_prompts(B, args.results_dir, selected_prompts_path)

        actual_out = args.out_dir / f"positive_safety_actual300_selected_batch{B}_eval.jsonl"
        cache = build_initial_cache(B, args.results_dir, actual_out)

        # Determine missing ids. Since selected prompts are all evaluated over the same actual300 ids,
        # use condition-wise missing and run one evaluator call on the union.
        missing_by_cond = {}
        for cond in SELECTED_CONDITIONS:
            have = {cid for (c, cid) in cache.keys() if c == cond}
            missing = [cid for cid in all_ids if cid not in have]
            missing_by_cond[cond] = missing

        missing_union = sorted(set(x for xs in missing_by_cond.values() for x in xs))

        print("\n" + "=" * 100)
        print("BATCH", B)
        print("selected prompts:", selected_prompts_path)
        print("actual_out:", actual_out)
        for cond in SELECTED_CONDITIONS:
            have_n = len(all_ids) - len(missing_by_cond[cond])
            print(f"  {cond:36s} have={have_n:3d}/{len(all_ids)} missing={len(missing_by_cond[cond]):3d}")
        print("missing union:", len(missing_union))

        if missing_union:
            new_rows = run_eval_for_missing(args, B, missing_union, selected_prompts_path, args.tmp_dir)
            for r in new_rows:
                if valid_result_row(r):
                    cache[case_key(r)] = r

        rows = write_sorted_actual_out(actual_out, cache, all_ids)

        final_counts = Counter(r.get("condition") for r in rows)
        print("\nFINAL BATCH", B)
        print("written rows:", len(rows), "/ expected", len(SELECTED_CONDITIONS) * len(all_ids))
        for cond in SELECTED_CONDITIONS:
            print(f"  {cond:36s} {final_counts.get(cond,0):3d}/{len(all_ids)}")

        still_missing = []
        for cond in SELECTED_CONDITIONS:
            have = {int(r["case_id"]) for r in rows if r.get("condition") == cond}
            miss = [cid for cid in all_ids if cid not in have]
            if miss:
                still_missing.append((cond, len(miss), miss[:10]))

        if still_missing:
            print("\nSTILL MISSING after this pass:")
            for cond, n, head in still_missing:
                print(f"  {cond:36s} missing={n} head={head}")
            print("Rerun the same command; existing successful rows will be reused.")

if __name__ == "__main__":
    main()
