# /home/jinwoo/gepa-official/examples/hotpotqa/scripts/eval_prompt_sets.py
import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm

import dspy

from gepa.adapters.dspy_adapter.dspy_adapter import DspyAdapter

from examples.hotpotqa.data import load_hotpot_splits
from examples.hotpotqa.feedback import feedback_fn_map
from examples.hotpotqa.metric import answer_exact_match
from examples.hotpotqa.program import HotpotMultiHop
from examples.hotpotqa.retriever import DEFAULT_RETRIEVER_DIR, set_retriever_dir


REQUIRED_KEYS = {
    "summarize1.predict",
    "create_query_hop2.predict",
    "summarize2.predict",
    "final_answer.predict",
}


def make_dspy_lm(model: str, api_base: str | None, api_key: str, temperature: float, max_tokens: int):
    kwargs = {
        "api_key": api_key,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if api_base:
        kwargs["api_base"] = api_base
    return dspy.LM(model, **kwargs)


def build_seed_candidate(program: dspy.Module) -> dict[str, str]:
    return {
        name: pred.signature.instructions
        for name, pred in program.named_predictors()
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_cache_key(
    *,
    source_path: str,
    prompt_file_hash: str,
    split: str,
    num_examples: int,
    seed: int,
    retriever_dir: str,
    k: int,
    task_model: str,
    task_api_base: str | None,
    task_temperature: float,
    task_max_tokens: int,
):
    return json.dumps(
        {
            "source_path": source_path,
            "prompt_file_hash": prompt_file_hash,
            "split": split,
            "num_examples": num_examples,
            "seed": seed,
            "retriever_dir": retriever_dir,
            "k": k,
            "task_model": task_model,
            "task_api_base": task_api_base,
            "task_temperature": task_temperature,
            "task_max_tokens": task_max_tokens,
        },
        sort_keys=True,
        ensure_ascii=False,
    )


def load_cached_results(results_path: Path) -> dict[str, dict[str, Any]]:
    cache = {}
    if not results_path.exists():
        return cache

    with results_path.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            cache_key = row.get("cache_key")
            if cache_key:
                cache[cache_key] = row

    return cache


def get_attr(obj: Any, key: str, default=None):
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def title_from_doc(doc: str) -> str:
    return str(doc).split(" | ")[0].strip()


def gold_titles(example) -> list[str]:
    supporting_facts = get_attr(example, "supporting_facts", {}) or {}
    return list(dict.fromkeys([t.strip() for t in supporting_facts.get("title", [])]))


def support_metrics(example, pred) -> dict[str, Any]:
    gold = set(gold_titles(example))

    hop1_docs = get_attr(pred, "hop1_docs", []) or []
    hop2_docs = get_attr(pred, "hop2_docs", []) or []

    hop1_titles = [title_from_doc(d) for d in hop1_docs]
    hop2_titles = [title_from_doc(d) for d in hop2_docs]

    hop1_set = set(hop1_titles)
    hop2_set = set(hop2_titles)
    total_set = hop1_set | hop2_set

    denom = len(gold) if gold else 1

    return {
        "gold_titles": sorted(gold),
        "hop1_titles": hop1_titles,
        "hop2_titles": hop2_titles,
        "support_recall_hop1": len(gold & hop1_set) / denom,
        "support_recall_hop2_only": len(gold & hop2_set) / denom,
        "support_recall_total": len(gold & total_set) / denom,
        "new_support_titles_hop2": sorted((gold & hop2_set) - hop1_set),
        "missing_titles_after_hop1": sorted(gold - hop1_set),
        "missing_titles_after_hop2": sorted(gold - total_set),
    }


def load_prompt_set(path: Path, expected_keys: set[str]) -> tuple[str, dict[str, str], dict[str, Any]]:
    obj = json.loads(path.read_text())

    if not isinstance(obj, dict):
        raise ValueError(f"{path}: top-level JSON must be an object.")

    if "prompts" not in obj:
        raise ValueError(f"{path}: missing required field `prompts`.")

    prompts = obj["prompts"]
    if not isinstance(prompts, dict):
        raise ValueError(f"{path}: `prompts` must be an object.")

    keys = set(prompts.keys())
    missing = expected_keys - keys
    extra = keys - expected_keys

    if missing:
        raise ValueError(f"{path}: missing prompt keys: {sorted(missing)}")
    if extra:
        raise ValueError(f"{path}: unknown prompt keys: {sorted(extra)}")

    for key, value in prompts.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{path}: prompt for `{key}` must be a non-empty string.")

    name = obj.get("name", path.stem)
    if not isinstance(name, str) or not name.strip():
        name = path.stem

    meta = {k: v for k, v in obj.items() if k != "prompts"}

    return name, dict(prompts), meta


def iter_prompt_set_files(prompt_sets_dir: Path):
    return sorted(p for p in prompt_sets_dir.glob("*.json") if p.is_file())


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def append_jsonl(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _evaluate_one_example(program, example, idx: int):
    try:
        pred = program(**example.inputs())
        score = float(answer_exact_match(example, pred))
        return idx, example, pred, score, None
    except Exception as e:
        return idx, example, None, 0.0, f"{type(e).__name__}: {e}"


def evaluate_prompt_set(
    adapter: DspyAdapter,
    dataset,
    candidate: dict[str, str],
    prompt_set_name: str,
    output_dir: Path,
    save_per_example: bool,
    num_threads: int = 1,
):
    program = adapter.build_program(candidate)

    rows = [None] * len(dataset)
    scores = [0.0] * len(dataset)

    running_correct = 0.0
    completed = 0
    desc = f"eval:{prompt_set_name}"

    if num_threads <= 1:
        with tqdm(total=len(dataset), desc=desc, dynamic_ncols=True) as pbar:
            for idx, example in enumerate(dataset):
                idx, example, pred, score, error = _evaluate_one_example(program, example, idx)

                scores[idx] = score
                rows[idx] = (example, pred, score, error)

                completed += 1
                running_correct += score
                pbar.set_postfix(
                    acc=f"{running_correct / completed:.4f}",
                    correct=f"{running_correct:.0f}/{completed}",
                )
                pbar.update(1)
    else:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(_evaluate_one_example, program, example, idx)
                for idx, example in enumerate(dataset)
            ]

            with tqdm(total=len(dataset), desc=desc, dynamic_ncols=True) as pbar:
                for fut in as_completed(futures):
                    idx, example, pred, score, error = fut.result()

                    scores[idx] = score
                    rows[idx] = (example, pred, score, error)

                    completed += 1
                    running_correct += score
                    pbar.set_postfix(
                        acc=f"{running_correct / completed:.4f}",
                        correct=f"{running_correct:.0f}/{completed}",
                    )
                    pbar.update(1)

    num_total = len(scores)
    num_correct = float(sum(scores))
    avg_score = num_correct / num_total if num_total else 0.0

    per_example_path = output_dir / "per_example" / f"{prompt_set_name}.jsonl"

    if save_per_example:
        per_example_path.parent.mkdir(parents=True, exist_ok=True)
        with per_example_path.open("w") as f:
            for idx, row in enumerate(rows):
                if row is None:
                    continue

                example, pred, score, error = row

                record = {
                    "prompt_set": prompt_set_name,
                    "example_idx": idx,
                    "question": get_attr(example, "question"),
                    "gold_answer": get_attr(example, "answer"),
                    "pred_answer": get_attr(pred, "answer") if pred is not None else None,
                    "score": float(score),
                    "error": error,
                    "summary_1": get_attr(pred, "summary_1") if pred is not None else None,
                    "hop2_query": get_attr(pred, "hop2_query") if pred is not None else None,
                    "summary_2": get_attr(pred, "summary_2") if pred is not None else None,
                    "hop1_docs": get_attr(pred, "hop1_docs", []) if pred is not None else [],
                    "hop2_docs": get_attr(pred, "hop2_docs", []) if pred is not None else [],
                }

                if pred is not None:
                    record.update(support_metrics(example, pred))

                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "prompt_set": prompt_set_name,
        "score": avg_score,
        "num_correct": num_correct,
        "num_total": num_total,
        "per_example_path": str(per_example_path) if save_per_example else None,
    }


def parse_size(x):
    if str(x).lower() in {"all", "none", "-1"}:
        return None
    return int(x)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--prompt-sets-dir", default="examples/hotpotqa/prompt_sets")
    parser.add_argument("--output-dir", default="outputs/hotpotqa_prompt_eval")

    parser.add_argument("--split", choices=["train", "val", "test"], default="test")
    parser.add_argument("--train-size", type=parse_size, default=100)
    parser.add_argument("--val-size", type=parse_size, default=100)
    parser.add_argument("--test-size", type=parse_size, default=None)
    parser.add_argument("--seed", type=int, default=0)

    parser.add_argument("--retriever-dir", default=os.environ.get("HOTPOT_RETRIEVER_DIR", DEFAULT_RETRIEVER_DIR))
    parser.add_argument("--k", type=int, default=7)

    parser.add_argument("--task-model", default=os.environ.get("TASK_MODEL", "openai/Qwen/Qwen3-8B"))
    parser.add_argument("--task-api-base", default=os.environ.get("TASK_API_BASE", "http://localhost:8889/v1"))
    parser.add_argument("--task-api-key", default=os.environ.get("TASK_API_KEY", "dummy"))
    parser.add_argument("--task-temperature", type=float, default=0.7)
    parser.add_argument("--task-max-tokens", type=int, default=4096)

    parser.add_argument("--num-threads", type=int, default=1)
    parser.add_argument("--include-base", action="store_true")
    parser.add_argument("--save-per-example", action="store_true")

    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--overwrite", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    prompt_sets_dir = Path(args.prompt_sets_dir)
    output_dir = Path(args.output_dir)

    prompt_files = iter_prompt_set_files(prompt_sets_dir)
    if not prompt_files:
        raise FileNotFoundError(f"No .json prompt sets found in {prompt_sets_dir}")

    results_path = output_dir / "results.jsonl"

    if args.overwrite and results_path.exists():
        results_path.unlink()

    cached_results = {} if args.no_cache or args.overwrite else load_cached_results(results_path)

    print("Loading HotpotQA splits...")
    trainset, valset, testset = load_hotpot_splits(
        train_size=args.train_size,
        val_size=args.val_size,
        test_size=args.test_size,
        seed=args.seed,
    )

    dataset = {
        "train": trainset,
        "val": valset,
        "test": testset,
    }[args.split]

    print(f"Evaluating split={args.split}, n={len(dataset)}")

    print("Configuring DSPy task LM...")
    task_lm = make_dspy_lm(
        model=args.task_model,
        api_base=args.task_api_base,
        api_key=args.task_api_key,
        temperature=args.task_temperature,
        max_tokens=args.task_max_tokens,
    )
    dspy.configure(lm=task_lm)

    print(f"Using retriever dir: {args.retriever_dir}")
    set_retriever_dir(args.retriever_dir)

    program = HotpotMultiHop(
        k=args.k,
        retriever_dir=args.retriever_dir,
    )

    base_candidate = build_seed_candidate(program)
    actual_keys = set(base_candidate.keys())

    if actual_keys != REQUIRED_KEYS:
        raise ValueError(
            "Unexpected predictor keys.\n"
            f"expected={sorted(REQUIRED_KEYS)}\n"
            f"actual={sorted(actual_keys)}"
        )

    adapter = DspyAdapter(
        student_module=program,
        metric_fn=answer_exact_match,
        feedback_map=feedback_fn_map,
        num_threads=args.num_threads,
        reflection_lm=None,
        reflection_minibatch_size=1,
        warn_on_score_mismatch=False,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    save_json(output_dir / "base_candidate.json", base_candidate)

    results = []

    if args.include_base:
        base_hash = hashlib.sha256(json.dumps(base_candidate, sort_keys=True).encode()).hexdigest()
        base_cache_key = make_cache_key(
            source_path="__base__",
            prompt_file_hash=base_hash,
            split=args.split,
            num_examples=len(dataset),
            seed=args.seed,
            retriever_dir=args.retriever_dir,
            k=args.k,
            task_model=args.task_model,
            task_api_base=args.task_api_base,
            task_temperature=args.task_temperature,
            task_max_tokens=args.task_max_tokens,
        )

        if base_cache_key in cached_results:
            print("[cache] base")
            result = cached_results[base_cache_key]
        else:
            print("[eval] base")
            result = evaluate_prompt_set(
                adapter=adapter,
                dataset=dataset,
                candidate=base_candidate,
                prompt_set_name="base",
                output_dir=output_dir,
                save_per_example=args.save_per_example,
                num_threads=args.num_threads,
            )
            result.update({
                "name": "base",
                "source_path": "__base__",
                "prompt_file_hash": base_hash,
                "cache_key": base_cache_key,
                "split": args.split,
                "num_examples": len(dataset),
                "seed": args.seed,
                "retriever_dir": args.retriever_dir,
                "k": args.k,
                "task_model": args.task_model,
                "task_api_base": args.task_api_base,
                "task_temperature": args.task_temperature,
                "task_max_tokens": args.task_max_tokens,
            })
            append_jsonl(results_path, result)

        results.append(result)
        print(result)

    candidates_dir = output_dir / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)

    for path in prompt_files:
        prompt_file_hash = file_sha256(path)
        name, candidate, meta = load_prompt_set(path, actual_keys)

        cache_key = make_cache_key(
            source_path=str(path),
            prompt_file_hash=prompt_file_hash,
            split=args.split,
            num_examples=len(dataset),
            seed=args.seed,
            retriever_dir=args.retriever_dir,
            k=args.k,
            task_model=args.task_model,
            task_api_base=args.task_api_base,
            task_temperature=args.task_temperature,
            task_max_tokens=args.task_max_tokens,
        )

        cached = cached_results.get(cache_key)
        if cached and args.save_per_example:
            per_example_path = cached.get("per_example_path")
            if not per_example_path or not Path(per_example_path).exists():
                cached = None

        if cached:
            print(f"[cache] {path.name}")
            result = cached
            results.append(result)
            print(result)
            continue

        print(f"[eval] {name} ({path.name})")

        save_json(candidates_dir / f"{path.stem}.json", {
            "name": name,
            "source_path": str(path),
            "prompt_file_hash": prompt_file_hash,
            "meta": meta,
            "candidate": candidate,
        })

        result = evaluate_prompt_set(
            adapter=adapter,
            dataset=dataset,
            candidate=candidate,
            prompt_set_name=path.stem,
            output_dir=output_dir,
            save_per_example=args.save_per_example,
                num_threads=args.num_threads,
        )
        result.update({
            "name": name,
            "source_path": str(path),
            "prompt_file_hash": prompt_file_hash,
            "cache_key": cache_key,
            "split": args.split,
            "num_examples": len(dataset),
            "seed": args.seed,
            "retriever_dir": args.retriever_dir,
            "k": args.k,
            "task_model": args.task_model,
            "task_api_base": args.task_api_base,
            "task_temperature": args.task_temperature,
            "task_max_tokens": args.task_max_tokens,
            "meta": meta,
        })

        results.append(result)
        append_jsonl(results_path, result)
        print(result)

    summary = {
        "split": args.split,
        "num_examples": len(dataset),
        "prompt_sets_dir": str(prompt_sets_dir),
        "output_dir": str(output_dir),
        "retriever_dir": args.retriever_dir,
        "task_model": args.task_model,
        "task_api_base": args.task_api_base,
        "num_threads": args.num_threads,
        "cache_enabled": not args.no_cache,
        "overwrite": args.overwrite,
        "results": results,
    }

    save_json(output_dir / "summary.json", summary)

    print("\nSummary:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()