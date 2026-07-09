import argparse
import csv
import json
import re
import textwrap
from pathlib import Path
from collections import defaultdict, Counter

AGG_ARMS = [
    "prompt_update_Rq_delta_p_only_aggregate_steps_4",
    "prompt_update_Rq_full_context_aggregate_steps_4",
]

DIRECT_ARM = "delta_p_direct_context_Rq_grounded_steps_4"
CURRENT_ARM = "prompt_current_query"

PATTERNS = {
    "preserve_anchor": [
        r"\bpreserve\b", r"\bkeep\b", r"\bretain\b", r"\banchor\b", r"source anchor"
    ],
    "restore_relation_or_type": [
        r"\brestore\b", r"\badd\b", r"\binclude\b", r"relation", r"type cue", r"answer type",
        r"role cue", r"date cue", r"alias", r"bridge"
    ],
    "drop_noisy_entity": [
        r"\bdrop\b", r"\bavoid\b", r"\bremove\b", r"\bdemote\b", r"\bsuppress\b",
        r"noisy", r"distractor", r"side entit"
    ],
    "candidate_uncertainty": [
        r"candidate", r"uncertain", r"ambiguous", r"variant", r"disambiguat", r"alternative"
    ],
    "wrong_candidate_relaxation": [
        r"wrong candidate", r"current candidate", r"relax", r"replace", r"do not preserve.*candidate",
        r"if.*candidate.*distractor"
    ],
    "entity_level_over_location_event": [
        r"entity-level", r"main article", r"higher-level", r"river-level", r"page-level",
        r"not.*location", r"not.*event", r"demote.*location", r"demote.*event"
    ],
    "bm25_interface_guard": [
        r"BM25", r"compact", r"keyword", r"no natural-language", r"bag-of-words",
        r"minimal stopwords"
    ],
    "single_query_guard": [
        r"exactly one", r"single compact", r"one compact", r"one .*query", r"do not output multiple"
    ],
    "web_search_drift": [
        r"site:", r"wikipedia", r"imdb", r"google", r"search-engine", r"web search",
        r"OR-heavy", r"AND-heavy"
    ],
    "multi_query_drift": [
        r"semicolon", r"semi-colon", r"multiple queries", r"two compact", r"query or queries",
        r"subqueries", r";"
    ],
    "query_string_like_delta": [
        r"query should be", r"final query", r"emit.*tokens", r"place .* first",
        r"exact token", r"exact phrase"
    ],
    "leakage_language": [
        r"gold", r"oracle", r"missing support", r"support title", r"answer literal",
        r"final answer", r"answer is"
    ],
}

BAD_PATTERNS = {
    "web_syntax": [r"site:", r"imdb", r"wikipedia", r"google", r"web search"],
    "boolean_heavy": [r"\bOR\b", r"\bAND\b", r"OR-heavy", r"AND-heavy"],
    "multi_query": [r";", r"multiple queries", r"two compact", r"subqueries", r"query or queries"],
    "leakage_language": [r"gold", r"oracle", r"missing support", r"support title", r"answer literal", r"final answer"],
}

def read_jsonl(path):
    return [json.loads(l) for l in Path(path).open()]

def norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()

def lower(s):
    return norm(s).lower()

def contains(text, phrase):
    return bool(norm(phrase)) and lower(phrase) in lower(text)

def regex_any(text, patterns):
    return any(re.search(p, text, flags=re.I) for p in patterns)

def short(s, n=700):
    return textwrap.shorten(norm(s), width=n, placeholder=" ...")

def mr(r):
    return float(r.get("missing_recovery_rate") or 0)

def h2(r):
    return float(r.get("support_recall_hop2") or 0)

def get_qtrace_meta(qtrace_path):
    qrows = read_jsonl(qtrace_path)
    out = defaultdict(dict)
    for r in qrows:
        idx = str(r.get("idx"))
        arm = r.get("arm")
        if arm == "base_query":
            out[idx]["base"] = r
        elif arm == "target_query":
            out[idx]["target"] = r
    return out

def title_leak_info(idx, text, visible_input, qmeta):
    base = qmeta.get(idx, {}).get("base", {})
    target = qmeta.get(idx, {}).get("target", {})

    titles = []
    titles += base.get("gold_support_titles") or []
    titles += target.get("gold_support_titles") or []
    titles += base.get("base_missing") or []
    titles = list(dict.fromkeys(titles))

    hits = [t for t in titles if contains(text, t)]
    risky = [t for t in hits if not contains(visible_input, t)]
    return hits, risky

def pattern_hits(text):
    return [name for name, pats in PATTERNS.items() if regex_any(text, pats)]

def bad_hits(text):
    return [name for name, pats in BAD_PATTERNS.items() if regex_any(text, pats)]

def generality_score(text, risky_titles):
    # heuristic score, not a metric. Higher means more rule-like / less suspicious.
    score = 5
    if regex_any(text, BAD_PATTERNS["web_syntax"]): score -= 1
    if regex_any(text, BAD_PATTERNS["boolean_heavy"]): score -= 1
    if regex_any(text, BAD_PATTERNS["multi_query"]): score -= 1
    if regex_any(text, BAD_PATTERNS["leakage_language"]): score -= 2
    if risky_titles: score -= 2
    if regex_any(text, PATTERNS["bm25_interface_guard"]): score += 1
    if regex_any(text, PATTERNS["restore_relation_or_type"]): score += 1
    if regex_any(text, PATTERNS["drop_noisy_entity"]): score += 1
    if regex_any(text, PATTERNS["wrong_candidate_relaxation"]): score += 1
    return max(0, min(10, score))

def locality_score(text, visible_input):
    # heuristic: concrete sample-anchor dependence. Higher means more local.
    score = 0
    if "sample-specific" in lower(text): score += 2
    if "for this sample" in lower(text): score += 2
    if regex_any(text, PATTERNS["query_string_like_delta"]): score += 1
    # count visible named-ish anchors that appear in text
    caps = re.findall(r"\b[A-Z][A-Za-z0-9'’().-]*(?:\s+[A-Z][A-Za-z0-9'’().-]*){0,4}\b", visible_input or "")
    caps = [c for c in caps if len(c) >= 4 and c.lower() not in {"question", "current", "summary"}]
    hits = sum(1 for c in set(caps) if contains(text, c))
    score += min(4, hits // 2)
    return max(0, min(10, score))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result-dir", required=True)
    ap.add_argument("--qtrace-path", default="experiments/deltaq/results_retrieval_gain_gpt5mini_full/bm25_validation.jsonl")
    ap.add_argument("--out-dir", default="")
    args = ap.parse_args()

    D = Path(args.result_dir)
    OUT = Path(args.out_dir) if args.out_dir else D / "prompt_quality_audit"
    OUT.mkdir(parents=True, exist_ok=True)

    rows = read_jsonl(D / "rows.jsonl")
    aux_rows = read_jsonl(D / "rq_delta_p_aux.jsonl")
    qmeta = get_qtrace_meta(args.qtrace_path)

    by_idx = defaultdict(dict)
    for r in rows:
        by_idx[str(r["idx"])][r["arm"]] = r

    # ------------------------------------------------------------
    # 1) Updated instruction records
    # ------------------------------------------------------------
    inst_records = []
    for idx, xs in by_idx.items():
        cur = xs.get(CURRENT_ARM)
        if not cur:
            continue
        question = cur.get("meta", {}).get("question", "")
        summary_1 = cur.get("meta", {}).get("summary_1", "")
        current_query = cur.get("meta", {}).get("current_query", cur.get("query", ""))
        visible = "\n".join([question, summary_1, current_query])

        for arm in AGG_ARMS:
            if arm not in xs:
                continue
            r = xs[arm]
            instr = r.get("meta", {}).get("updated_instruction", "")
            query = r.get("query", "")

            instr_title_hits, instr_risky_titles = title_leak_info(idx, instr, visible, qmeta)
            query_title_hits, query_risky_titles = title_leak_info(idx, query, visible, qmeta)

            ph = pattern_hits(instr)
            bh = bad_hits(instr + "\n" + query)

            inst_records.append({
                "idx": idx,
                "arm": arm,
                "current_mr": mr(cur),
                "mr": mr(r),
                "delta_mr": mr(r) - mr(cur),
                "current_h2": h2(cur),
                "h2": h2(r),
                "instr_len": len(instr),
                "query_len": len(query),
                "generality_score": generality_score(instr + "\n" + query, instr_risky_titles + query_risky_titles),
                "locality_score": locality_score(instr, visible),
                "patterns": "; ".join(ph),
                "bad_patterns": "; ".join(bh),
                "instr_title_hits": "; ".join(instr_title_hits),
                "instr_risky_titles": "; ".join(instr_risky_titles),
                "query_title_hits": "; ".join(query_title_hits),
                "query_risky_titles": "; ".join(query_risky_titles),
                "question": question,
                "current_query": current_query,
                "query": query,
                "instruction_excerpt": short(instr, 1000),
            })

    # ------------------------------------------------------------
    # 2) Delta-p listing records
    # ------------------------------------------------------------
    dp_records = []
    for a in aux_rows:
        idx = str(a["idx"])
        question = a.get("question", "")
        summary_1 = a.get("summary_1", "")
        current_query = a.get("current_query", "")
        visible = "\n".join([question, summary_1, current_query])
        listing = a.get("delta_p_listing", "")

        title_hits, risky_titles = title_leak_info(idx, listing, visible, qmeta)
        ph = pattern_hits(listing)
        bh = bad_hits(listing)

        # Join performance from rows.
        xs = by_idx.get(idx, {})
        direct = xs.get(DIRECT_ARM, {})
        cur = xs.get(CURRENT_ARM, {})

        dp_records.append({
            "idx": idx,
            "current_mr": mr(cur),
            "direct_delta_p_mr": mr(direct),
            "direct_delta_p_delta_mr": mr(direct) - mr(cur),
            "listing_len": len(listing),
            "generality_score": generality_score(listing, risky_titles),
            "locality_score": locality_score(listing, visible),
            "patterns": "; ".join(ph),
            "bad_patterns": "; ".join(bh),
            "title_hits": "; ".join(title_hits),
            "risky_titles": "; ".join(risky_titles),
            "question": question,
            "current_query": current_query,
            "delta_p_excerpt": short(listing, 1200),
        })

    # ------------------------------------------------------------
    # Write CSVs
    # ------------------------------------------------------------
    inst_csv = OUT / "updated_instruction_quality.csv"
    with inst_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(inst_records[0].keys()))
        w.writeheader()
        w.writerows(inst_records)

    dp_csv = OUT / "delta_p_quality.csv"
    with dp_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dp_records[0].keys()))
        w.writeheader()
        w.writerows(dp_records)

    # ------------------------------------------------------------
    # Pattern frequency report
    # ------------------------------------------------------------
    md = []
    md.append("# Prompt quality pattern report\n")

    md.append("## Updated instruction summary\n")
    md.append("| arm | n | mean MR | mean ΔMR | avg generality | avg locality | avg instr len | bad cases | risky-title cases |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for arm in AGG_ARMS:
        xs = [r for r in inst_records if r["arm"] == arm]
        md.append(
            f"| {arm} | {len(xs)} | "
            f"{sum(r['mr'] for r in xs)/len(xs):.3f} | "
            f"{sum(r['delta_mr'] for r in xs)/len(xs):+.3f} | "
            f"{sum(r['generality_score'] for r in xs)/len(xs):.2f} | "
            f"{sum(r['locality_score'] for r in xs)/len(xs):.2f} | "
            f"{sum(r['instr_len'] for r in xs)/len(xs):.0f} | "
            f"{sum(bool(r['bad_patterns']) for r in xs)} | "
            f"{sum(bool(r['instr_risky_titles'] or r['query_risky_titles']) for r in xs)} |"
        )

    md.append("\n## Δp listing summary\n")
    xs = dp_records
    md.append("| n | mean direct Δp MR | mean direct ΔMR | avg generality | avg locality | avg listing len | bad cases | risky-title cases |")
    md.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
    md.append(
        f"| {len(xs)} | "
        f"{sum(r['direct_delta_p_mr'] for r in xs)/len(xs):.3f} | "
        f"{sum(r['direct_delta_p_delta_mr'] for r in xs)/len(xs):+.3f} | "
        f"{sum(r['generality_score'] for r in xs)/len(xs):.2f} | "
        f"{sum(r['locality_score'] for r in xs)/len(xs):.2f} | "
        f"{sum(r['listing_len'] for r in xs)/len(xs):.0f} | "
        f"{sum(bool(r['bad_patterns']) for r in xs)} | "
        f"{sum(bool(r['risky_titles']) for r in xs)} |"
    )

    md.append("\n## Pattern frequency in updated instructions\n")
    md.append("| arm | pattern | count | mean ΔMR when present |")
    md.append("|---|---|---:|---:|")
    for arm in AGG_ARMS:
        xs = [r for r in inst_records if r["arm"] == arm]
        for p in PATTERNS:
            present = [r for r in xs if p in r["patterns"]]
            if present:
                md.append(f"| {arm} | {p} | {len(present)} | {sum(r['delta_mr'] for r in present)/len(present):+.3f} |")

    md.append("\n## Pattern frequency in Δp listings\n")
    md.append("| pattern | count | mean direct ΔMR when present |")
    md.append("|---|---:|---:|")
    for p in PATTERNS:
        present = [r for r in dp_records if p in r["patterns"]]
        if present:
            md.append(f"| {p} | {len(present)} | {sum(r['direct_delta_p_delta_mr'] for r in present)/len(present):+.3f} |")

    (OUT / "pattern_report.md").write_text("\n".join(md))

    # ------------------------------------------------------------
    # Case cards: top gains/losses and flagged
    # ------------------------------------------------------------
    cards = []
    cards.append("# Prompt quality case cards\n")

    def add_inst_card(r):
        cards.append("\n" + "=" * 120)
        cards.append(f"\n## IDX {r['idx']} | {r['arm']}")
        cards.append(f"- MR: {r['current_mr']:.3f} → {r['mr']:.3f} ({r['delta_mr']:+.3f})")
        cards.append(f"- generality/locality: {r['generality_score']}/{r['locality_score']}")
        cards.append(f"- patterns: {r['patterns']}")
        cards.append(f"- bad_patterns: {r['bad_patterns']}")
        cards.append(f"- risky titles: instr=[{r['instr_risky_titles']}], query=[{r['query_risky_titles']}]")
        cards.append(f"\nQuestion: {r['question']}")
        cards.append(f"\nCurrent query: `{r['current_query']}`")
        cards.append(f"\nNew query: `{r['query']}`")
        cards.append("\nUpdated instruction excerpt:")
        cards.append("```text")
        cards.append(r["instruction_excerpt"])
        cards.append("```")

    cards.append("\n## Top updated-instruction gains\n")
    for r in sorted(inst_records, key=lambda x: x["delta_mr"], reverse=True)[:10]:
        add_inst_card(r)

    cards.append("\n## Worst updated-instruction losses\n")
    for r in sorted(inst_records, key=lambda x: x["delta_mr"])[:10]:
        add_inst_card(r)

    flagged = [
        r for r in inst_records
        if r["bad_patterns"] or r["instr_risky_titles"] or r["query_risky_titles"] or r["generality_score"] <= 3
    ]
    cards.append("\n## Flagged updated instructions\n")
    for r in sorted(flagged, key=lambda x: (x["generality_score"], -abs(x["delta_mr"])))[:14]:
        add_inst_card(r)

    (OUT / "updated_instruction_case_cards.md").write_text("\n".join(cards))

    # Delta-p cards
    dp_cards = ["# Delta-p listing case cards\n"]

    def add_dp_card(r):
        dp_cards.append("\n" + "=" * 120)
        dp_cards.append(f"\n## IDX {r['idx']}")
        dp_cards.append(f"- direct Δp MR: {r['current_mr']:.3f} → {r['direct_delta_p_mr']:.3f} ({r['direct_delta_p_delta_mr']:+.3f})")
        dp_cards.append(f"- generality/locality: {r['generality_score']}/{r['locality_score']}")
        dp_cards.append(f"- patterns: {r['patterns']}")
        dp_cards.append(f"- bad_patterns: {r['bad_patterns']}")
        dp_cards.append(f"- risky titles: {r['risky_titles']}")
        dp_cards.append(f"\nQuestion: {r['question']}")
        dp_cards.append(f"\nCurrent query: `{r['current_query']}`")
        dp_cards.append("\nΔp listing excerpt:")
        dp_cards.append("```text")
        dp_cards.append(r["delta_p_excerpt"])
        dp_cards.append("```")

    dp_cards.append("\n## Top direct-Δp gains\n")
    for r in sorted(dp_records, key=lambda x: x["direct_delta_p_delta_mr"], reverse=True)[:10]:
        add_dp_card(r)

    dp_cards.append("\n## Worst direct-Δp losses\n")
    for r in sorted(dp_records, key=lambda x: x["direct_delta_p_delta_mr"])[:10]:
        add_dp_card(r)

    dp_cards.append("\n## Flagged Δp listings\n")
    flagged_dp = [
        r for r in dp_records
        if r["bad_patterns"] or r["risky_titles"] or r["generality_score"] <= 3
    ]
    for r in sorted(flagged_dp, key=lambda x: (x["generality_score"], -abs(x["direct_delta_p_delta_mr"])))[:14]:
        add_dp_card(r)

    (OUT / "delta_p_case_cards.md").write_text("\n".join(dp_cards))

    print("Wrote:")
    print(" ", inst_csv)
    print(" ", dp_csv)
    print(" ", OUT / "pattern_report.md")
    print(" ", OUT / "updated_instruction_case_cards.md")
    print(" ", OUT / "delta_p_case_cards.md")
    print()
    print((OUT / "pattern_report.md").read_text())

if __name__ == "__main__":
    main()
