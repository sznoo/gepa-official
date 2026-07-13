#!/usr/bin/env bash
set -euo pipefail

cd /home/jinwoo/gepa-official
set -a
source .env
set +a

export LITELLM_LOG=ERROR
export LITELLM_SET_VERBOSE=False

BATCHES="${BATCHES:-1 2}"
MODEL="${MODEL:-openai/gpt-5-mini}"
THREADS="${THREADS:-4}"
OVERWRITE="${OVERWRITE:---overwrite}"

for B in $BATCHES; do
  echo
  echo "=============================="
  echo "[prepare] batch ${B}"
  echo "=============================="

  python experiments/prompt_update/scripts/match_transportable_pairs.py \
    --batch-id "${B}" \
    --composition mixed_custom \
    --candidate-bucket W_retrieval \
    --target-buckets C_clean W_other \
    --out "experiments/prompt_update/cache/positive_safety/batch${B}_c_failure_matches.jsonl" \
    --summary-out "experiments/prompt_update/cache/positive_safety/batch${B}_c_failure_matches.summary.json" \
    --model "${MODEL}" \
    --temperature 1.0 \
    --max-output-tokens 4096 \
    --num-threads "${THREADS}" \
    ${OVERWRITE}

  python experiments/prompt_update/scripts/generate_transported_endpoints.py \
    --batch-id "${B}" \
    --case-state-index experiments/prompt_update/cache/positive_safety/case_state_index.json \
    --matches "experiments/prompt_update/cache/positive_safety/batch${B}_c_failure_matches.jsonl" \
    --out "experiments/prompt_update/cache/positive_safety/batch${B}_c_transported_endpoints.jsonl" \
    --summary-out "experiments/prompt_update/cache/positive_safety/batch${B}_c_transported_endpoints.summary.json" \
    --model "${MODEL}" \
    --temperature 1.0 \
    --max-output-tokens 4096 \
    --num-threads "${THREADS}" \
    ${OVERWRITE}

  python experiments/prompt_update/scripts/build_directional_transitions.py \
    --batch-id "${B}" \
    --composition mixed_custom \
    --split experiments/prompt_update/data/positive_safety_b10_split_seed0.json \
    --case-state-index experiments/prompt_update/cache/positive_safety/case_state_index.json \
    --transported-endpoints "experiments/prompt_update/cache/positive_safety/batch${B}_c_transported_endpoints.jsonl" \
    --out "experiments/prompt_update/cache/positive_safety/batch${B}_directional_transitions.jsonl" \
    --summary-out "experiments/prompt_update/cache/positive_safety/batch${B}_directional_transitions.summary.json"

  python experiments/prompt_update/scripts/generate_directional_delta_qp.py \
    --directional-transitions "experiments/prompt_update/cache/positive_safety/batch${B}_directional_transitions.jsonl" \
    --fixed-prompt-config experiments/prompt_update/cache/fixed_prompt_config.json \
    --out "experiments/prompt_update/cache/positive_safety/batch${B}_directional_delta_qp.jsonl" \
    --summary-out "experiments/prompt_update/cache/positive_safety/batch${B}_directional_delta_qp.summary.json" \
    --model "${MODEL}" \
    --temperature 1.0 \
    --info-mode Rq \
    --updater-max-tokens 4096 \
    --num-threads "${THREADS}" \
    ${OVERWRITE}

  python experiments/prompt_update/scripts/generate_positive_safety_batch_prompts.py \
    --batch-id "${B}" \
    --delta-qp "experiments/prompt_update/cache/positive_safety/batch${B}_directional_delta_qp.jsonl" \
    --fixed-prompt-config experiments/prompt_update/cache/fixed_prompt_config.json \
    --out "experiments/prompt_update/results/positive_safety_b10_batch${B}_prompts.jsonl" \
    --summary-out "experiments/prompt_update/results/positive_safety_b10_batch${B}_prompts.summary.json" \
    --model "${MODEL}" \
    --temperature 1.0 \
    --max-output-tokens 4096 \
    ${OVERWRITE}

  echo "[done prepare] batch ${B}"
done
