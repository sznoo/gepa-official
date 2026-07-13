#!/usr/bin/env bash
set -euo pipefail

cd /home/jinwoo/gepa-official
set -a
source .env
set +a

export LITELLM_LOG=ERROR
export LITELLM_SET_VERBOSE=False

BATCHES="${BATCHES:-0 1 2}"
MODEL="${MODEL:-openai/gpt-5-mini}"
THREADS="${THREADS:-12}"
TASK_RETRIES="${TASK_RETRIES:-3}"
OVERWRITE="${OVERWRITE:---overwrite}"

for B in $BATCHES; do
  echo
  echo "=============================="
  echo "[eval] batch ${B}"
  echo "=============================="

  python experiments/prompt_update/scripts/evaluate_positive_safety_prompts.py \
    --split experiments/prompt_update/data/positive_safety_b10_split_seed0.json \
    --case-state-index experiments/prompt_update/cache/positive_safety/case_state_index.json \
    --prompts "experiments/prompt_update/results/positive_safety_b10_batch${B}_prompts.jsonl" \
    --fixed-prompt-config experiments/prompt_update/cache/fixed_prompt_config.json \
    --final-answerer-refs experiments/prompt_update/cache/final_answerer_refs.json \
    --out "experiments/prompt_update/results/positive_safety_b10_batch${B}_eval.jsonl" \
    --summary-out "experiments/prompt_update/results/positive_safety_b10_batch${B}_eval_summary.json" \
    --summary-md "experiments/prompt_update/results/positive_safety_b10_batch${B}_eval_summary.md" \
    --composition mixed_custom \
    --batch-id "${B}" \
    --scopes batch full143 \
    --retriever-dir examples/hotpotqa \
    --k 7 \
    --model "${MODEL}" \
    --temperature 1.0 \
    --query-max-tokens 512 \
    --summary-max-tokens 4096 \
    --answer-max-tokens 2048 \
    --num-threads "${THREADS}" \
    --retries 4 \
    --task-retries "${TASK_RETRIES}" \
    ${OVERWRITE}

  echo "[done eval] batch ${B}"
done
