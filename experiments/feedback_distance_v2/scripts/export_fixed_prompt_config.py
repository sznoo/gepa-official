# /home/jinwoo/gepa-official/experiments/feedback_distance_v2/scripts/export_fixed_prompt_config.py
#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


DEFAULT_CONDITION_DIR = Path(
    "outputs/hotpotqa_representation_prompt_screening/"
    "rep_prompt_screening_24_dev300_final_v2/"
    "conditions/"
    "R6_hybrid_edit_script__MB1_retrieval_gain_recover__S1_conservative_reversible"
)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition-dir", default=str(DEFAULT_CONDITION_DIR))
    ap.add_argument("--out-dir", default="experiments/feedback_distance_v2/cache")
    args = ap.parse_args()

    condition_dir = Path(args.condition_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = condition_dir / "prompt_candidate.json"
    summary_path = condition_dir / "summary.json"
    rollout_preview_path = condition_dir / "analysis" / "rollout_traces.jsonl"

    missing = [str(p) for p in [prompt_path, summary_path] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required files: {missing}")

    prompt_obj = load_json(prompt_path)
    summary_obj = load_json(summary_path)

    config = {
        "condition_dir": str(condition_dir),
        "prompt_candidate_path": str(prompt_path),
        "summary_path": str(summary_path),
        "rollout_preview_path": str(rollout_preview_path),
        "fixed_prompt_name": condition_dir.name,
        "prompt_candidate": prompt_obj,
        "condition_summary": summary_obj,
        "notes": [
            "Use this fixed prompt to generate the natural failure distribution.",
            "Do not use old retrieval_gain/retrieval_loss pairs as the new split.",
            "The actual current state must come from a fresh fixed-prompt rollout."
        ],
    }

    out_path = out_dir / "fixed_prompt_config.json"
    out_path.write_text(json.dumps(config, ensure_ascii=False, indent=2))

    print("[wrote]", out_path)
    print("[condition]", condition_dir)
    print("[prompt_candidate keys]", sorted(prompt_obj.keys()) if isinstance(prompt_obj, dict) else type(prompt_obj).__name__)
    print("[summary keys]", sorted(summary_obj.keys()) if isinstance(summary_obj, dict) else type(summary_obj).__name__)
    print(json.dumps(config, ensure_ascii=False, indent=2)[:4000])


if __name__ == "__main__":
    main()
