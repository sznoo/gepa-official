#!/usr/bin/env bash
set -euo pipefail

cd /home/jinwoo/gepa-official

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"
export LD_PRELOAD="$CONDA_PREFIX/lib/libstdc++.so.6${LD_PRELOAD:+:$LD_PRELOAD}"

export VLLM_CACHE_ROOT=/tmp/vllm_cache_jinwoo_cuda128

echo "CONDA_PREFIX=$CONDA_PREFIX"
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
echo "LD_PRELOAD=$LD_PRELOAD"
echo "VLLM_CACHE_ROOT=$VLLM_CACHE_ROOT"

CUDA_VISIBLE_DEVICES=0,1,2,3 \
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-8B \
  --served-model-name Qwen/Qwen3-8B \
  --tensor-parallel-size 4 \
  --enforce-eager
