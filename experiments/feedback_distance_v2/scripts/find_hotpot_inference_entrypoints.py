#!/usr/bin/env python3
from pathlib import Path

ROOTS = [
    Path("experiments"),
    Path("examples/hotpotqa"),
    Path("scripts"),
    Path("outputs/hotpotqa_representation_prompt_screening"),
]

PATTERNS = [
    "create_query_hop2",
    "summarize1",
    "summarize2",
    "final_answer",
    "rollout_traces",
    "prompt_candidate",
    "case_study_R6_best_vs_final_manual",
    "rep_prompt_screening",
    "HotpotQA",
    "hotpotqa",
]

SKIP_SUFFIXES = {
    ".jsonl",
    ".json",
    ".md",
    ".txt",
    ".partial",
    ".log",
    ".csv",
}


def should_read(p):
    if not p.is_file():
        return False
    if p.suffix in SKIP_SUFFIXES:
        return False
    if "__pycache__" in p.parts or ".git" in p.parts:
        return False
    return p.suffix in {".py", ".sh", ".yaml", ".yml", ".toml"}


def main():
    hits = []
    for root in ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not should_read(p):
                continue
            try:
                text = p.read_text(errors="ignore")
            except Exception:
                continue

            score = sum(1 for pat in PATTERNS if pat in text)
            if not score:
                continue

            lines = []
            for i, line in enumerate(text.splitlines(), start=1):
                if any(pat in line for pat in PATTERNS):
                    lines.append((i, line.strip()))
                if len(lines) >= 8:
                    break

            hits.append((score, str(p), lines))

    hits.sort(key=lambda x: (-x[0], x[1]))

    print("# Candidate HotpotQA / GEPA inference entrypoints")
    print()
    for score, path, lines in hits[:80]:
        print(f"\n## score={score} {path}")
        for ln, line in lines:
            print(f"{ln}: {line[:220]}")


if __name__ == "__main__":
    main()
