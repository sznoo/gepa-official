#!/usr/bin/env bash
set -euo pipefail

cd /home/jinwoo/gepa-official
export PYTHONPATH=/home/jinwoo/gepa-official/src:/home/jinwoo/gepa-official:${PYTHONPATH}

RUN_DIR=/home/jinwoo/gepa-official/outputs/hotpotqa
ENV_FILE=/home/jinwoo/gepa-official/.env
CACHE_PATH=${RUN_DIR}/diagnosis_cache_gpt-5-mini.jsonl

python /home/jinwoo/gepa-official/scripts/diagnose_hotpot_wrong_cases.py \
  --run-dir "${RUN_DIR}" \
  --env-file "${ENV_FILE}" \
  --model gpt-5-mini \
  --cache-path "${CACHE_PATH}" \
  --max-workers 8 \
  --max-retries 3 \
  --timeout 120 \
  --names \
    optimized_baseline \
    optimized_baseline_hop2_A_concise_bm25 \
    optimized_baseline_hop2_B_short \
    optimized_baseline_hop2_C_retrieval_state \
    optimized_baseline_hop2_D_anchor_preservation