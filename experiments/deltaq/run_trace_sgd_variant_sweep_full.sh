#!/usr/bin/env bash
set -euo pipefail

cd /home/jinwoo/gepa-official

set -a
source .env
set +a

export HOTPOT_RETRIEVER_DIR=/home/jinwoo/gepa-official/examples/hotpotqa

BATCH_IDS="${BATCH_IDS:-0,1,2,3,4,5,6,7,8,9}"
NUM_PATCHES="${NUM_PATCHES:-4}"
NUM_THREADS="${NUM_THREADS:-4}"
MODEL="${MODEL:-openai/gpt-5-mini}"

OUT_ROOT="${OUT_ROOT:-experiments/deltaq/results_trace_sgd_variant_sweep_supportaware_b0to9_k4_full}"
CACHE_DIR="${OUT_ROOT}/cache"
BASE_FULL_CACHE="${CACHE_DIR}/base_full_states_final_manual_agentgrad.jsonl"

mkdir -p "${OUT_ROOT}" "${CACHE_DIR}"

VARIANTS=(
  "edit_script_bridge"
  "gated_variant_expansion"
  "counterfactual_preservation"
)

for V in "${VARIANTS[@]}"; do
  OUT_DIR="${OUT_ROOT}/${V}"
  echo
  echo "================================================================================"
  echo "[variant] ${V}"
  echo "[out]     ${OUT_DIR}"
  echo "================================================================================"

  if [[ -f "${OUT_DIR}/trial_summary.jsonl" && "${FORCE:-0}" != "1" ]]; then
    echo "[skip] final trial_summary.jsonl already exists. Set FORCE=1 to rerun."
    continue
  fi

  python experiments/deltaq/run_trace_sgd_onestep.py \
    --model "${MODEL}" \
    --api-base "" \
    --temperature 1.0 \
    --max-tokens 16000 \
    --pool-dir experiments/deltaq/trace_sgd_pool_seed13_random_correct \
    --minibatch-path experiments/deltaq/trace_sgd_pool_seed13_random_correct/minibatches.jsonl \
    --batch-ids "${BATCH_IDS}" \
    --oracle-rows-path experiments/deltaq/results_hotpot_ideal_context_upper_bound_wrong_hop2_miss_50_agentgrad_full_final_t4/rows.jsonl \
    --oracle-arm support_aware_ideal_delta \
    --base-prompt-candidate outputs/hotpotqa_representation_prompt_screening/rep_prompt_screening_24_dev300_final_v2/conditions/final_manual_only/prompt_candidate.json \
    --fixed-prompt-candidate experiments/deltaq/prompt_candidates/final_manual_with_agentgrad_best_full_final_answer.json \
    --num-patches "${NUM_PATCHES}" \
    --patch-generator-variant "${V}" \
    --select-mode equal_compare \
    --eval-full-pool \
    --base-full-cache-path "${BASE_FULL_CACHE}" \
    --num-threads "${NUM_THREADS}" \
    --out-dir "${OUT_DIR}"

  echo
  echo "[done variant] ${V}"
  cat "${OUT_DIR}/summary.md"
done

python experiments/deltaq/analyze_trace_sgd_variant_sweep.py \
  --root "${OUT_ROOT}" \
  --variants "${VARIANTS[@]}"

echo
echo "================================================================================"
echo "[sweep summary]"
echo "================================================================================"
cat "${OUT_ROOT}/sweep_summary.md"

echo
echo "================================================================================"
echo "[selected patches]"
echo "================================================================================"
cat "${OUT_ROOT}/selected_patches.md"
