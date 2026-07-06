#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"

if not BASE_SCRIPT.exists():
    raise FileNotFoundError(f"Base script not found: {BASE_SCRIPT}")


AGENTGRAD_SUMMARIZE1 = """Given inputs question (string) and passages (list of strings), produce a single textual output to populate the field "summary". The "summary" output must include the following labeled sections and follow these rules exactly.

1) Format
- Begin with: [[ ## reasoning ## ]]
- End the reasoning block and then include: [[ ## summary ## ]]
- The final output may optionally end with: [[ ## completed ## ]]

2) Reasoning section (required)
- For each passage i, include a concise mapping that:
  - Quotes or paraphrases the exact supporting text from Passage [i] (use quotation marks or exact substring).
  - Explicitly maps each quoted fact to the entity and scope it supports (e.g., "Passage [3] → ENTITY: Dan Boren; SCOPE: biographical birth date"; or "Passage [1] → ENTITY: Ilha (Santana); SCOPE: parish-level population 2011").
  - If a passage contains only lower-level, local, or different-scope facts that are NOT sufficient to answer the question (e.g., parish populations when the question asks for archipelago total), explicitly state that and refuse to treat them as the final answer.

- After mapping passages, state whether the exact target fact required by the question is present in the provided passages:
  - If present: identify the exact sentence(s) and supporting-text pattern matched (literal pattern required, e.g., "ENTITY_NAME (born <date>)" or "The population in 2011 was <number>"). Cite passage indices that contain that exact supporting text.
  - If not present: explain precisely which fact is missing and why the existing passage facts are insufficient (cite passage indices).

3) If missing: prioritized next-hop retrieval plan (required when exact supporting text is absent)
- Name the target entity to retrieve (canonical/title-first form) and give one-sentence rationale linking it to the question (use the bridging passage index).
- Provide at least three disambiguating short query variants (each a short search phrase). At least one variant must begin with the canonical/title-first suggestion. Include scope/context tokens (e.g., "birth date", "2011 population", "archipelago", "U.S. Representative", "politician", location).
- Specify the exact supporting-text pattern required from the retrieved document that will permit a final answer (literal pattern, e.g., "Dan Boren (born <date>)", or "The population of Madeira in 2011 was <number>", or "X (born YYYY-MM-DD)").
- Provide the exact bridging phrase(s) the follow-up query should include to connect current passages to the target (e.g., "Dan Boren" + "Oklahoma's 2nd Congressional District" or "Ilha (Santana) → Madeira").
- Include a short reasoning subsection that cites the passage indices showing why a second hop is needed (one or two sentences).

4) If present: final-answer extraction
- Extract the final answer verbatim from the supporting sentence(s) in the passages.
- State the exact supporting-text pattern matched.
- Cite the passage index(es) that contain the supporting text.

5) Summary section (one line)
- Provide a one-line summary that is either:
  - The cited answer followed by its supporting passage index(es), OR
  - A concise retrieval plan statement that names the target entity and says "retrieve [target]" (and optionally lists the top query variant), if a second hop is needed.
- Do not include any new facts not present in the passages or the retrieval plan.

6) Constraints and behavior
- Never answer from memory. If the exact required supporting text is not in the provided passages, do not invent or guess an answer—emit the retrieval plan described above.
- Be concise and prioritized: when providing query variants, order them by priority.
- Always include passage indices in reasoning to justify conclusions.
- Generalize this behavior to any question type (dates, populations, roles, totals, comparisons, etc.).
"""

AGENTGRAD_CREATE_QUERY_HOP2 = """Given the fields `question`, `summary_1`, produce the fields `query`."""

AGENTGRAD_SUMMARIZE2 = """Given the fields `question`, `context`, `passages`, produce the fields `summary`."""

AGENTGRAD_FINAL = """You are given three fields as input: question, summary_1, summary_2. Produce output containing exactly two blocks in this order and exact format (no other text, blocks, or commentary):

[[ ## reasoning ## ]]
[[ ## answer ## ]]

Rules for [[ ## reasoning ## ]]:
- Use only the contents of summary_1 and summary_2 to support premises and the final answer, except for one allowed metadata line: you must include a single numbered item that documents the detected question type and the chosen output form (see "Question type detection" below). All other numbered items must attribute their content to a summary.
- Present a short, numbered sequence of concise premises and a brief derivation, or a statement that the conclusion cannot be reached. Keep the reasoning to one or two lines per numbered item where possible while still numbered and sufficient to show the inference.
- Each numbered item that cites a summary must explicitly attribute its content using one of these exact phrasings: "summary_1 states: \\"...\\"" or "summary_2 states: \\"...\\"" (you may paraphrase the quoted text but must include the exact label). If both summaries supply the same premise, you may combine it and indicate both sources as "(summary_1, summary_2)".
- If you remove any parenthetical content or editorial qualifiers from a name/title to create a canonical form for the answer, list each removed parenthetical or qualifier in the reasoning block and attribute it to the summary that contained it using the exact phrasing above (e.g. summary_2 states: "X (the Mighty Handful)"; removed: "(the Mighty Handful)").
- The reasoning must show which premises were used and how the conclusion follows, or why it cannot be reached (conflict or silence). Keep steps concise and numbered.
- Question type detection: before applying normalization or selecting the output token, determine whether the question is a confirmation (yes/no), a request for a category/label, or another type. Include exactly one numbered reasoning item that states the detected question type and the chosen output form. This metadata item need not quote a summary; phrase it clearly, e.g. "Detected question type: confirmation. Chosen output form: yes/no/insufficient information." Place this metadata item as the first or last numbered item in the reasoning.

Normalization and selection rule (Generalized Update Direction):
- If the detected question type is confirmation, answer exactly "yes", "no", or "insufficient information" as supported by the summaries.
- When the required answer is an occupation or category label, normalize it to a single canonical noun phrase in singular form and lowercase (unless the label is a proper noun). Prefer the more specific supported label when the summaries differ (for example, prefer "professional wrestler" over "wrestler" if one summary supplies the more specific form). If neither summary clearly supports a more specific label (conflict or different incompatible categories), return "insufficient information".
- Provide the normalization in the reasoning (cite which summary supports the chosen normalized label). The reasoning should be one or two concise numbered items that cite summary_1 and/or summary_2 for the normalization.

Rules for [[ ## answer ## ]]:
- The answer block must contain only the minimal required token or short label derived solely from the reasoning block and nothing else (no punctuation, no extra words, no capitalization beyond the canonicalization rule).
- If the question is a confirmation, the answer must be exactly one of: yes, no, insufficient information.
- If the answer is a name/title, return the cleaned canonical string by stripping nonessential parenthetical content and editorial qualifiers (do not include the removed parentheticals or qualifiers in this field). Prefer the base token exactly as present in the summaries where possible.
- For occupation/category outputs follow the normalization rule: singular noun phrase, lowercase (unless proper noun), and choose the more specific supported label when summaries differ.
- If the summaries do not provide enough information or they conflict on the needed point(s), return exactly: insufficient information
- Do not add any extra text, salutations, or sections. The answer block must be a single minimal token or short label only.

Strict hygiene:
- Emit exactly the two blocks shown above and nothing else.
- The reasoning must be numbered and cite which summary supplied each premise using the exact phrasings required, except for the one permitted question-type metadata item.
- Use only summary_1 and summary_2 to derive the answer (aside from the required question-type metadata line).
- The reasoning must include the detected question type and the chosen output form as specified.

Follow these rules for every input.
"""


PROMPTS = {
    "summarize1.predict": AGENTGRAD_SUMMARIZE1,
    "create_query_hop2.predict": AGENTGRAD_CREATE_QUERY_HOP2,
    "summarize2.predict": AGENTGRAD_SUMMARIZE2,
    "final_answer.predict": AGENTGRAD_FINAL,
}

ALIASES = {
    "summarize1.predict": [
        "summarize1.predict",
        "summarize1",
        "summary1",
        "summarize_1",
    ],
    "create_query_hop2.predict": [
        "create_query_hop2.predict",
        "create_query_hop2",
        "query_hop2",
        "hop2",
    ],
    "summarize2.predict": [
        "summarize2.predict",
        "summarize2",
        "summary2",
        "summarize_2",
    ],
    "final_answer.predict": [
        "final_answer.predict",
        "final_answer",
        "answer",
    ],
}

INSTRUCTION_KEYS = {
    "instruction",
    "instructions",
    "prompt",
    "system_prompt",
    "old_instruction",
    "new_instruction",
    "proposed_instruction",
    "program_instruction",
    "description",
}


def detect_module(text: object) -> str | None:
    if not isinstance(text, str):
        return None
    low = text.lower()
    for module, aliases in ALIASES.items():
        for a in aliases:
            if a.lower() in low:
                return module
    return None


def set_instruction_fields(d: dict, module: str) -> int:
    n = 0
    for k in list(d.keys()):
        if isinstance(k, str) and k in INSTRUCTION_KEYS and isinstance(d[k], str):
            d[k] = PROMPTS[module]
            n += 1
    if n == 0:
        d["instruction"] = PROMPTS[module]
        n += 1
    return n


def patch_obj(obj, current_module: str | None = None) -> tuple[object, int]:
    changed = 0

    if isinstance(obj, dict):
        local_module = current_module

        for k, v in obj.items():
            mk = detect_module(k)
            mv = detect_module(v)
            if mk:
                local_module = mk
            elif mv:
                local_module = mv

        if local_module is not None:
            changed += set_instruction_fields(obj, local_module)

        for k in list(obj.keys()):
            v = obj[k]
            mk = detect_module(k)

            if mk is not None:
                if isinstance(v, str):
                    obj[k] = PROMPTS[mk]
                    changed += 1
                else:
                    new_v, c = patch_obj(v, mk)
                    obj[k] = new_v
                    changed += c
            else:
                new_v, c = patch_obj(v, local_module)
                obj[k] = new_v
                changed += c

        return obj, changed

    if isinstance(obj, list):
        for i, v in enumerate(obj):
            new_v, c = patch_obj(v, current_module)
            obj[i] = new_v
            changed += c
        return obj, changed

    return obj, changed


def patch_json_file(path: Path) -> int:
    try:
        obj = json.loads(path.read_text())
    except Exception:
        return 0

    patched, changed = patch_obj(obj)
    if changed:
        path.write_text(json.dumps(patched, ensure_ascii=False, indent=2))
    return changed


def patch_jsonl_file(path: Path) -> int:
    changed_total = 0
    new_lines = []
    touched = False

    try:
        lines = path.read_text().splitlines()
    except Exception:
        return 0

    for line in lines:
        if not line.strip():
            new_lines.append(line)
            continue
        try:
            obj = json.loads(line)
        except Exception:
            new_lines.append(line)
            continue

        patched, changed = patch_obj(obj)
        changed_total += changed
        if changed:
            touched = True
            new_lines.append(json.dumps(patched, ensure_ascii=False))
        else:
            new_lines.append(line)

    if touched:
        path.write_text("\n".join(new_lines) + "\n")

    return changed_total


def prepare_agentgrad_source(src: Path, dst: Path, overwrite: bool = True) -> None:
    if overwrite and dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)

    changed = 0
    target_files = []

    for pat in [
        "**/prompt_candidate.json",
        "**/prompt_candidate*.json",
        "**/proposal_event*.json",
        "**/proposal_events*.json",
    ]:
        target_files.extend(dst.glob(pat))

    # jsonl may contain old_instruction/new_instruction used by some runners.
    for pat in [
        "**/proposal_event*.jsonl",
        "**/proposal_events*.jsonl",
    ]:
        target_files.extend(dst.glob(pat))

    seen = set()
    unique_files = []
    for p in target_files:
        if p not in seen and p.is_file():
            seen.add(p)
            unique_files.append(p)

    for p in unique_files:
        if p.suffix == ".jsonl":
            c = patch_jsonl_file(p)
        else:
            c = patch_json_file(p)
        if c:
            print(f"[INFO] patched {c:4d} fields in {p}", file=sys.stderr)
            changed += c

    if changed == 0:
        raise RuntimeError(
            f"No prompt fields were patched under {dst}. "
            "Check prompt_candidate/proposal_event structure."
        )

    print(f"[INFO] total patched fields: {changed}", file=sys.stderr)


def parse_known_source_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--source-condition-dir", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--exp-name", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args, _ = parser.parse_known_args(argv)
    return args


def replace_arg(argv: list[str], key: str, value: str) -> list[str]:
    out = list(argv)
    if key not in out:
        out.extend([key, value])
        return out
    i = out.index(key)
    if i + 1 >= len(out):
        raise RuntimeError(f"Argument {key} has no value.")
    out[i + 1] = value
    return out


def postprocess_summary(exp_dir: Path) -> None:
    agg = exp_dir / "aggregate_summary.json"
    if not agg.exists():
        return

    obj = json.loads(agg.read_text())
    conds = obj.get("conditions", {})

    if "gepa_best" in conds and "agentgrad_best_full" not in conds:
        conds["agentgrad_best_full"] = copy.deepcopy(conds["gepa_best"])
        conds["agentgrad_best_full"]["condition"] = "agentgrad_best_full"

    if "final_manual_only" in conds and "agentgrad_full_with_final_v2_mixed" not in conds:
        conds["agentgrad_full_with_final_v2_mixed"] = copy.deepcopy(conds["final_manual_only"])
        conds["agentgrad_full_with_final_v2_mixed"]["condition"] = "agentgrad_full_with_final_v2_mixed"

    agg.write_text(json.dumps(obj, ensure_ascii=False, indent=2))


def main() -> None:
    outer_args = parse_known_source_args(sys.argv[1:])

    source = Path(outer_args.source_condition_dir)
    output_root = Path(outer_args.output_root)
    exp_name = outer_args.exp_name
    exp_dir = output_root / exp_name
    prepared = exp_dir / "_prepared_agentgrad_source_condition"

    if outer_args.overwrite and exp_dir.exists():
        shutil.rmtree(exp_dir)
    exp_dir.mkdir(parents=True, exist_ok=True)

    prepare_agentgrad_source(source, prepared, overwrite=True)

    # Import base runner only after preparation.
    spec = importlib.util.spec_from_file_location("_hotpot_base_runner", BASE_SCRIPT)
    base = importlib.util.module_from_spec(spec)
    sys.modules["_hotpot_base_runner"] = base
    assert spec.loader is not None
    spec.loader.exec_module(base)

    # Disable generated hop2 candidates. We only need the prepared source condition.
    if hasattr(base, "HOP2_CANDIDATES"):
        base.HOP2_CANDIDATES = {}

    # Replace source condition with prepared agentgrad source.
    new_argv = replace_arg(sys.argv, "--source-condition-dir", str(prepared))
    sys.argv = new_argv

    print("[INFO] Running base evaluator with prepared agentgrad full source:", prepared, file=sys.stderr)
    base.main()

    postprocess_summary(exp_dir)


if __name__ == "__main__":
    main()
