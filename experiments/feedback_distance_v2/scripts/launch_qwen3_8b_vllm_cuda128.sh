#!/usr/bin/env bash
set -euo pipefail

cd /home/jinwoo/gepa-official

export CUDA_HOME=/usr/local/cuda-12.8
export CUDA_PATH=/usr/local/cuda-12.8
export CUDACXX=/usr/local/cuda-12.8/bin/nvcc
export NVCC=/usr/local/cuda-12.8/bin/nvcc
export CUDA_NVCC_EXECUTABLE=/usr/local/cuda-12.8/bin/nvcc
export PATH=/usr/local/cuda-12.8/bin:$(echo "$PATH" | tr ':' '\n' | grep -v '^/usr/local/cuda' | grep -v '/cuda-13' | paste -sd: -)
export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:${LD_LIBRARY_PATH:-}
export TORCH_EXTENSIONS_DIR=/tmp/torch_extensions_jinwoo_cuda128
export VLLM_CACHE_ROOT=/tmp/vllm_cache_jinwoo_cuda128
export VLLM_DISABLE_COMPILE_CACHE=1

echo "CUDA_HOME=$CUDA_HOME"
echo "CUDACXX=$CUDACXX"
which -a nvcc
nvcc --version

CUDA_VISIBLE_DEVICES=0,1,2,3 \
HF_HOME=/hub_data2/jinwoo/hf_cache \
HF_HUB_CACHE=/hub_data2/jinwoo/hf_cache/hub \
TRANSFORMERS_CACHE=/hub_data2/jinwoo/hf_cache/transformers \
HF_DATASETS_CACHE=/hub_data2/jinwoo/hf_cache/datasets \
HF_XET_CACHE=/hub_data2/jinwoo/hf_cache/xet \
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-8B \
  --served-model-name Qwen/Qwen3-8B \
  --tensor-parallel-size 4 \
  --host 0.0.0.0 \
  --port 8123 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 32768 \
  --enforce-eager
