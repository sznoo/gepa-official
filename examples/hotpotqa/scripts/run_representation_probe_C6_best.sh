#!/usr/bin/env bash
set -euo pipefail

cd /home/jinwoo/gepa-official

unset OPENAI_API_KEY

python examples/hotpotqa/scripts/run_representation_probe.py \
  --source-run outputs/hotpotqa2 \
  --output-root outputs/hotpotqa_representation_probe \
  --exp-name exp_C6_gradient_skeleton_best_retrieval_failure_n3 \
  --base-candidate best \
  --representation-group gradient \
  --conditions \
    bm25_missing_target_mainness_v1 \
    bm25_manual_clause_violation_v1 \
    missing_target_slot_gradient_v1 \
    known_vs_missing_query_allocation_v1 \
    query_compression_violation_v1 \
    canonical_anchor_preservation_v1 \
  --pair-filter retrieval_failure \
  --num-pairs 3 \
  --env-file /home/jinwoo/gepa-official/.env \
  --proposer-model gpt-5-mini \
  --proposer-max-tokens 16000 \
  --task-model openai/gpt-5-mini \
  --task-temperature 1.0 \
  --task-max-tokens 16000 \
  --eval-split test \
  --train-size 100 \
  --val-size 100 \
  --test-size 100 \
  --seed 0 \
  --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \
  --num-threads 20 \
  --show-eval-progress \
  --eval-progress-chunk-size 20 \
  --overwrite
