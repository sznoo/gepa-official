import argparse
import json
import os
import re
import sys
from pathlib import Path

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
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


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


def load_summarize1_instruction(path):
    data = json.loads(Path(path).read_text())

    subtree = (
        find_key_subtree(data, "summarize1")
        or find_key_subtree(data, "summary_1")
        or find_key_subtree(data, "summarize")
        or data
    )

    strings = collect_strings(subtree)
    candidates = []
    for p, s in strings:
        ss = s.strip()
        if len(ss) < 40:
            continue
        low = ss.lower()
        score = 0
        for kw in ["summary", "question", "passage", "document", "retrieved"]:
            if kw in low:
                score += 1
        candidates.append((score, len(ss), p, ss))

    if candidates:
        candidates.sort(reverse=True)
        score, length, p, instr = candidates[0]
        print(f"[summarize1 instruction] extracted from {p}, chars={length}, score={score}")
        return instr

    print("[warn] summarize1 instruction not found; using generic fallback")
    return (
        "Given a question and first-hop retrieved passages, write a concise factual summary "
        "containing only information useful for generating a second-hop search query."
    )


def clean_lm_text(x):
    if x is None:
        return ""
    if isinstance(x, str):
        y = x.strip()
    elif isinstance(x, (list, tuple)):
        vals = [clean_lm_text(v) for v in x]
        y = next((v for v in vals if v), "")
    elif isinstance(x, dict):
        if "choices" in x and x["choices"]:
            vals = []
            for c in x["choices"]:
                if isinstance(c, dict):
                    msg = c.get("message") or {}
                    vals.append(msg.get("content") or c.get("text") or "")
            y = next((str(v).strip() for v in vals if str(v).strip()), "")
        else:
            vals = [clean_lm_text(v) for v in x.values()]
            y = next((v for v in vals if v), "")
    else:
        y = str(x).strip()

    y = re.sub(r"^```(?:text|json)?", "", y).strip()
    y = re.sub(r"```$", "", y).strip()
    return y.strip().strip('"').strip("'").strip()


def call_lm(prompt, retries=3):
    last = None
    sigs = [
        ("prompt -> summary_1", "summary_1"),
        ("prompt -> summary", "summary"),
        ("prompt -> response", "response"),
        ("prompt -> text", "text"),
    ]
    for _ in range(retries):
        for sig, attr in sigs:
            try:
                pred = dspy.Predict(sig)(prompt=prompt)
                out = clean_lm_text(getattr(pred, attr, None))
                if out:
                    return out
            except Exception as e:
                last = e
        try:
            out = clean_lm_text(dspy.settings.lm(prompt))
            if out:
                return out
        except Exception as e:
            last = e

    if last:
        print("[warn] LLM failed:", repr(last), file=sys.stderr)
    return ""


def load_retriever(args):
    sys.path.insert(0, str(Path.cwd()))
    from examples.hotpotqa.retriever import search, set_retriever_dir

    retriever_dir = args.retriever_dir or os.environ.get("HOTPOT_RETRIEVER_DIR", "")
    if retriever_dir:
        set_retriever_dir(retriever_dir)

    k = int(args.retriever_k)
    print(f"[retriever] search(question, k={k})")
    if retriever_dir:
        print(f"[retriever] dir: {retriever_dir}")

    def _ret(q):
        return search(q, k)

    return _ret


def normalize_passages(out):
    if out is None:
        return []

    if hasattr(out, "passages"):
        return normalize_passages(getattr(out, "passages"))

    if hasattr(out, "docs"):
        return normalize_passages(getattr(out, "docs"))

    if isinstance(out, dict):
        for k in ["passages", "docs", "ctxs", "contexts", "retrieved"]:
            if k in out:
                return normalize_passages(out[k])
        return []

    if isinstance(out, str):
        return [out]

    if isinstance(out, (list, tuple)):
        vals = []
        for x in out:
            if isinstance(x, str):
                vals.append(x)
            elif isinstance(x, dict):
                title = x.get("title") or x.get("page_title") or x.get("wikipedia_title") or ""
                text = x.get("text") or x.get("passage") or x.get("contents") or ""
                vals.append((str(title) + " | " + str(text)).strip(" |"))
            else:
                vals.append(str(x))
        return [v for v in vals if v.strip()]

    return [str(out)]


def make_summary_prompt(instruction, question, passages):
    docs = "\n".join([f"[{i+1}] {p}" for i, p in enumerate(passages)])
    return f"""
You are the summarize1 module in a two-hop HotpotQA BM25 pipeline.

Base summarize1 instruction:
{instruction}

Question:
{question}

First-hop retrieved passages:
{docs}

Output requirements:
- Write summary_1 only.
- Include entities, relations, aliases, dates, titles, and bridge clues useful for the second-hop query.
- Do not use any gold answer, gold support title, q-trace target, or missing-support metadata.
- Be concise but specific.
""".strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta-in", required=True)
    ap.add_argument("--meta-out", required=True)
    ap.add_argument("--base-prompt-candidate", required=True)

    ap.add_argument("--model", default="openai/gpt-5-mini")
    ap.add_argument("--api-base", default="")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--retries", type=int, default=3)

    ap.add_argument("--retriever-dir", default="")
    ap.add_argument("--retriever-k", type=int, default=7)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.retriever_dir:
        os.environ["HOTPOT_RETRIEVER_DIR"] = args.retriever_dir

    lm_kwargs = {
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    if args.api_base:
        lm_kwargs["api_base"] = args.api_base
    dspy.settings.configure(lm=dspy.LM(**lm_kwargs))

    instruction = load_summarize1_instruction(args.base_prompt_candidate)
    retrieve = load_retriever(args)

    rows = read_jsonl(args.meta_in)

    out = []
    generated = 0
    kept = 0

    for r in tqdm(rows, desc="fill summary_1"):
        r = dict(r)
        if r.get("summary_1") and not args.force:
            r["summary_1_source"] = r.get("summary_1_source") or "existing"
            kept += 1
            out.append(r)
            continue

        q = r.get("question", "").strip()
        if not q:
            r["summary_1_source"] = "missing_question"
            out.append(r)
            continue

        passages = normalize_passages(retrieve(q))
        prompt = make_summary_prompt(instruction, q, passages)
        s1 = call_lm(prompt, args.retries)

        r["summary_1"] = s1
        r["summary_1_source"] = "regenerated_question_hop1_bm25_summarize1"
        r["hop1_passages_for_summary_1"] = passages
        generated += 1
        out.append(r)

        write_jsonl(Path(args.meta_out).with_suffix(".partial.jsonl"), out)

    write_jsonl(args.meta_out, out)

    print("[done]")
    print("rows:", len(out))
    print("kept:", kept)
    print("generated:", generated)
    print("with question:", sum(1 for r in out if r.get("question")))
    print("with summary_1:", sum(1 for r in out if r.get("summary_1")))
    print("out:", args.meta_out)


if __name__ == "__main__":
    main()
