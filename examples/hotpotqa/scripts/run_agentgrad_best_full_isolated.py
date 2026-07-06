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
    "summarize1.predict": ["summarize1.predict", "summarize1"],
    "create_query_hop2.predict": ["create_query_hop2.predict", "create_query_hop2"],
    "summarize2.predict": ["summarize2.predict", "summarize2"],
    "final_answer.predict": ["final_answer.predict", "final_answer"],
}

INSTRUCTION_KEYS = {
    "instruction",
    "instructions",
    "prompt",
    "system_prompt",
    "old_instruction",
    "new_instruction",
    "proposed_instruction",
}


def detect_module(x) -> str | None:
    if not isinstance(x, str):
        return None
    low = x.lower()
    for module, aliases in ALIASES.items():
        for a in aliases:
            if a.lower() in low:
                return module
    return None


def patch_instruction_container(d: dict, module: str) -> int:
    changed = 0
    found = False
    for k in list(d.keys()):
        if isinstance(k, str) and k in INSTRUCTION_KEYS and isinstance(d[k], str):
            d[k] = PROMPTS[module]
            changed += 1
            found = True
    if not found:
        d["instruction"] = PROMPTS[module]
        changed += 1
    return changed


def patch_obj(obj, inherited_module: str | None = None):
    changed = 0

    if isinstance(obj, dict):
        local_module = inherited_module

        # Detect module from record metadata.
        for k, v in obj.items():
            km = detect_module(k)
            vm = detect_module(v)
            if km:
                local_module = km
            elif vm:
                local_module = vm

        # If this dict corresponds to a module, overwrite its instruction fields.
        if local_module is not None:
            changed += patch_instruction_container(obj, local_module)

        # Recurse.
        for k in list(obj.keys()):
            v = obj[k]
            key_module = detect_module(k)

            if key_module is not None:
                if isinstance(v, str):
                    obj[k] = PROMPTS[key_module]
                    changed += 1
                else:
                    new_v, c = patch_obj(v, key_module)
                    obj[k] = new_v
                    changed += c
            else:
                new_v, c = patch_obj(v, local_module)
                obj[k] = new_v
                changed += c

        return obj, changed

    if isinstance(obj, list):
        for i, v in enumerate(obj):
            new_v, c = patch_obj(v, inherited_module)
            obj[i] = new_v
            changed += c
        return obj, changed

    return obj, changed


def patch_json_file(path: Path) -> int:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0

    patched, changed = patch_obj(obj)
    if changed:
        path.write_text(json.dumps(patched, ensure_ascii=False, indent=2), encoding="utf-8")
    return changed


def patch_jsonl_file(path: Path) -> int:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return 0

    changed_total = 0
    out = []
    touched = False

    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        try:
            obj = json.loads(line)
        except Exception:
            out.append(line)
            continue
        patched, changed = patch_obj(obj)
        if changed:
            touched = True
            changed_total += changed
            out.append(json.dumps(patched, ensure_ascii=False))
        else:
            out.append(line)

    if touched:
        path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return changed_total


def prepare_source(src: Path, prepared: Path) -> None:
    if prepared.exists():
        shutil.rmtree(prepared)
    shutil.copytree(src, prepared)

    files = []
    for pat in [
        "**/prompt_candidate.json",
        "**/prompt_candidate*.json",
        "**/proposal_event.json",
        "**/proposal_events.json",
        "**/proposal_event*.json",
        "**/proposal_events*.json",
        "**/proposal_event*.jsonl",
        "**/proposal_events*.jsonl",
    ]:
        files.extend(prepared.glob(pat))

    unique = []
    seen = set()
    for f in files:
        if f.is_file() and f not in seen:
            unique.append(f)
            seen.add(f)

    total = 0
    for f in unique:
        c = patch_jsonl_file(f) if f.suffix == ".jsonl" else patch_json_file(f)
        if c:
            print(f"[INFO] patched {c:4d} fields in {f}", file=sys.stderr)
            total += c

    if total == 0:
        raise RuntimeError(f"No prompt fields patched under {prepared}")

    print(f"[INFO] total patched fields: {total}", file=sys.stderr)


def parse_known(argv):
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--source-condition-dir", required=True)
    p.add_argument("--output-root", required=True)
    p.add_argument("--exp-name", required=True)
    p.add_argument("--overwrite", action="store_true")
    args, _ = p.parse_known_args(argv)
    return args


def replace_arg(argv, key, value):
    out = list(argv)
    if key not in out:
        out.extend([key, value])
        return out
    i = out.index(key)
    if i + 1 >= len(out):
        raise RuntimeError(f"{key} has no value")
    out[i + 1] = value
    return out


def postprocess(exp_dir: Path):
    agg = exp_dir / "aggregate_summary.json"
    if not agg.exists():
        return

    obj = json.loads(agg.read_text(encoding="utf-8"))
    conds = obj.get("conditions", {})

    # In this isolated run, gepa_best uses the prepared agentgrad full prompts.
    if "gepa_best" in conds:
        conds["agentgrad_best_full"] = copy.deepcopy(conds["gepa_best"])
        conds["agentgrad_best_full"]["condition"] = "agentgrad_best_full"

    obj["note"] = (
        "In this isolated run, condition `gepa_best` is the prepared AgentGrad-best full prompt. "
        "`agentgrad_best_full` is an alias copied from `gepa_best` for readability."
    )

    agg.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    args = parse_known(sys.argv[1:])

    src = Path(args.source_condition_dir)
    output_root = Path(args.output_root)
    exp_name = args.exp_name
    exp_dir = output_root / exp_name

    safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in exp_name)
    prepared = Path("/tmp") / f"gepa_agentgrad_best_full_prepared_{safe_name}"

    if args.overwrite and exp_dir.exists():
        shutil.rmtree(exp_dir)
    exp_dir.mkdir(parents=True, exist_ok=True)

    prepare_source(src, prepared)

    candidate = prepared / "prompt_candidate.json"
    if not candidate.exists():
        raise FileNotFoundError(f"Prepared prompt_candidate.json missing: {candidate}")

    spec = importlib.util.spec_from_file_location("_hotpot_base_runner", BASE_SCRIPT)
    base = importlib.util.module_from_spec(spec)
    sys.modules["_hotpot_base_runner"] = base
    assert spec.loader is not None
    spec.loader.exec_module(base)

    # Disable extra generated hop2 candidates. This makes the run effectively source-condition only.
    if hasattr(base, "HOP2_CANDIDATES"):
        base.HOP2_CANDIDATES = {}

    sys.argv = replace_arg(sys.argv, "--source-condition-dir", str(prepared))

    print("[INFO] output_root:", output_root, file=sys.stderr)
    print("[INFO] exp_name:", exp_name, file=sys.stderr)
    print("[INFO] prepared agentgrad source:", prepared, file=sys.stderr)
    print("[INFO] Running base evaluator.", file=sys.stderr)

    base.main()

    postprocess(exp_dir)


if __name__ == "__main__":
    main()
