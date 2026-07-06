cd /home/jinwoo/gepa-official
export PYTHONPATH=/home/jinwoo/gepa-official/src:/home/jinwoo/gepa-official:${PYTHONPATH}

PROMPT_DIR=/home/jinwoo/gepa-official/examples/hotpotqa/prompt_sets
RUN_DIR=/home/jinwoo/gepa-official/outputs/hotpotqa

declare -a NAMES=(
  "optimized_baseline"
  "optimized_baseline_hop2_A_concise_bm25"
  "optimized_baseline_hop2_B_short"
  "optimized_baseline_hop2_C_retrieval_state"
  "optimized_baseline_hop2_D_anchor_preservation"
)

for NAME in "${NAMES[@]}"; do
  echo "===== Running ${NAME} ====="

  python -m examples.hotpotqa.run_hotpot \
    --train-size 100 \
    --val-size 100 \
    --test-size 100 \
    --seed 0 \
    --k 7 \
    --num-threads 20 \
    --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \
    --task-model openai/Qwen/Qwen3-8B \
    --task-api-base http://localhost:8889/v1 \
    --task-api-key dummy \
    --task-temperature 0.7 \
    --task-max-tokens 4096 \
    --run-dir ${RUN_DIR} \
    --eval-only \
    --prompt-json ${PROMPT_DIR}/${NAME}.json \
    --analysis-name ${NAME} \
    --overwrite-analysis

done