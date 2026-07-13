export CUDA_VISIBLE_DEVICES=0,1,2,3t && \
cd /home/jinwoo/gepa-official && \
set -a && \
source .env && \
set +a && \
export QWEN_MODEL="openai/Qwen/Qwen3-8B" && \
python experiments/feedback_distance_v2/scripts/run_rtrace_midpoint_validity_v2.py \
  --input experiments/feedback_distance_v2/results/oracle_query_downstream_eval.repaired.jsonl \
  --final-answerer-refs experiments/feedback_distance_v2/cache/final_answerer_refs.json \
  --fixed-prompt-config experiments/feedback_distance_v2/cache/fixed_prompt_config.json \
  --out-traces experiments/feedback_distance_v2/results/rtrace_midpoint_validity_v2_traces_hit48_qwen_smoke8.jsonl \
  --out-attempts experiments/feedback_distance_v2/results/rtrace_midpoint_validity_v2_attempts_hit48_qwen_smoke8.jsonl \
  --summary-out experiments/feedback_distance_v2/results/rtrace_midpoint_validity_v2_summary_hit48_qwen_smoke8.json \
  --retriever-dir examples/hotpotqa \
  --k 7 \
  --model "$QWEN_MODEL" \
  --temperature 1.0 \
  --max-iter 4 \
  --max-retries-per-edge 1 \
  --num-threads 4 \
  --limit 8