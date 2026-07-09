import argparse
import json
import re
from pathlib import Path
from difflib import SequenceMatcher


QUERY_KEYS = {
    "query",
    "base_query",
    "hop2_query",
    "base_hop2_query",
    "cand_hop2_query",
    "target_query",
    "current_query",
}


def read_jsonl(path):
    rows = []
    p = Path(path)
    if not p.exists():
        return rows
    with p.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def norm_query(x):
    x = str(x or "")
    x = x.replace("“", '"').replace("”", '"').replace("’", "'")
    x = re.sub(r"\s+", " ", x).strip().lower()
    x = x.strip('"').strip("'").strip()
    return x


def get_question(row):
    return (
        row.get("question")
        or row.get("input_question")
        or row.get("x")
        or row.get("meta", {}).get("question")
        or ""
    )


def get_summary_1(row):
    return (
        row.get("summary_1")
        or row.get("summary1")
        or row.get("hop1_summary")
        or row.get("meta", {}).get("summary_1")
        or ""
    )


def collect_query_fields(obj, path=""):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            kp = f"{path}.{k}" if path else str(k)
            if k in QUERY_KEYS and isinstance(v, str) and len(v.strip()) >= 8:
                out.append((kp, v))
            out.extend(collect_query_fields(v, kp))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(collect_query_fields(v, f"{path}[{i}]"))
    return out


def load_qtrace_groups(path):
    rows = read_jsonl(path)
    by = {}
    for r in rows:
        if r.get("arm") != "base_query":
            continue
        idx = str(r["idx"])
        q = r.get("query") or r.get("base_query") or ""
        by[idx] = {
            "idx": idx,
            "base_query": q,
            "gold_support_titles": r.get("gold_support_titles") or [],
            "base_missing": r.get("base_missing") or [],
        }
    return by


def iter_candidate_paths(paths):
    out = []
    for raw in paths:
        p = Path(raw)
        if not p.exists():
            print("[skip missing]", p)
            continue
        if p.is_file():
            out.append(p)
        else:
            out.extend(sorted(p.rglob("*.jsonl")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qtrace-path", required=True)
    ap.add_argument("--search-path", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-fuzzy", type=float, default=0.94)
    args = ap.parse_args()

    qtrace = load_qtrace_groups(args.qtrace_path)
    qnorm_to_idx = {norm_query(v["base_query"]): idx for idx, v in qtrace.items()}

    exact = {}
    fuzzy_candidates = []

    paths = iter_candidate_paths(args.search_path)
    print("[qtrace groups]", len(qtrace))
    print("[candidate jsonl files]", len(paths))

    scanned_rows = 0
    usable_rows = 0

    for p in paths:
        # skip outputs from the prompt injection experiment itself
        ps = str(p)
        if "results_full_trace_prompt_injection" in ps:
            continue
        if "results_qtrace_accumulation_probe" in ps:
            continue

        for row in read_jsonl(p):
            scanned_rows += 1
            question = get_question(row)
            summary_1 = get_summary_1(row)

            if not question:
                continue

            qfields = collect_query_fields(row)
            if not qfields:
                continue

            usable_rows += 1

            for qpath, qval in qfields:
                nq = norm_query(qval)
                if not nq:
                    continue

                if nq in qnorm_to_idx:
                    idx = qnorm_to_idx[nq]
                    score = 2 if summary_1 else 1
                    cur = exact.get(idx)
                    if cur is None or score > cur["score"]:
                        exact[idx] = {
                            "idx": idx,
                            "question": question,
                            "summary_1": summary_1,
                            "source_path": str(p),
                            "source_query_field": qpath,
                            "matched_query": qval,
                            "match_type": "exact_query",
                            "score": score,
                        }

                # keep fuzzy candidates only for rows with summary or strong q field
                if summary_1 or qpath.split(".")[-1] in {"base_hop2_query", "hop2_query", "base_query"}:
                    fuzzy_candidates.append((p, row, qpath, qval, nq, question, summary_1))

    missing = [idx for idx in qtrace if idx not in exact]
    fuzzy = {}

    for idx in missing:
        target = norm_query(qtrace[idx]["base_query"])
        best = None
        for p, row, qpath, qval, nq, question, summary_1 in fuzzy_candidates:
            sim = SequenceMatcher(None, target, nq).ratio()
            if sim < args.min_fuzzy:
                continue
            score = (sim, 1 if summary_1 else 0, len(nq))
            if best is None or score > best[0]:
                best = (score, p, row, qpath, qval, question, summary_1)

        if best:
            score, p, row, qpath, qval, question, summary_1 = best
            fuzzy[idx] = {
                "idx": idx,
                "question": question,
                "summary_1": summary_1,
                "source_path": str(p),
                "source_query_field": qpath,
                "matched_query": qval,
                "match_type": f"fuzzy_query_{score[0]:.3f}",
                "score": score[0],
            }

    joined = []
    for idx in sorted(qtrace, key=lambda x: int(x) if str(x).isdigit() else str(x)):
        if idx in exact:
            r = exact[idx]
        elif idx in fuzzy:
            r = fuzzy[idx]
        else:
            r = {
                "idx": idx,
                "question": "",
                "summary_1": "",
                "source_path": "",
                "source_query_field": "",
                "matched_query": "",
                "match_type": "missing",
                "score": 0,
            }

        r["qtrace_base_query"] = qtrace[idx]["base_query"]
        r["gold_support_titles"] = qtrace[idx]["gold_support_titles"]
        r["base_missing"] = qtrace[idx]["base_missing"]
        joined.append(r)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for r in joined:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    report = []
    report.append("# Qtrace Meta Join Report\n")
    report.append(f"- qtrace groups: {len(qtrace)}")
    report.append(f"- candidate jsonl files: {len(paths)}")
    report.append(f"- scanned rows: {scanned_rows}")
    report.append(f"- usable rows with question and query fields: {usable_rows}")
    report.append(f"- exact query matches: {len(exact)}")
    report.append(f"- fuzzy query matches: {len(fuzzy)}")
    report.append(f"- total joined with question: {sum(1 for r in joined if r.get('question'))}")
    report.append("\n| idx | match_type | has_summary_1 | source | field |")
    report.append("|---:|---|---:|---|---|")
    for r in joined:
        report.append(
            f"| {r['idx']} | {r['match_type']} | {1 if r.get('summary_1') else 0} | "
            f"{r.get('source_path','')} | {r.get('source_query_field','')} |"
        )

    report_path = out.with_suffix(".report.md")
    report_path.write_text("\n".join(report))

    print(report_path.read_text())
    print("[wrote]", out)


if __name__ == "__main__":
    main()
