#!/usr/bin/env bash
set -euo pipefail

cd /home/jinwoo/gepa-official

unset OPENAI_API_KEY

python examples/hotpotqa/scripts/run_representation_probe.py \
  --source-run outputs/hotpotqa2 \
  --output-root outputs/hotpotqa_representation_probe \
  --exp-name exp_B6_function_aware_best_retrieval_failure_n3 \
  --base-candidate best \
  --representation-group diagnostic \
  --conditions \
    bm25_contract_surface_v1 \
    bm25_lexical_diagnostic_v1 \
    function_bottleneck_transduction_v1 \
    evidence_state_machine_v1 \
    bridge_attempt_context_v1 \
    partial_context_expansion_v1 \
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
