CUDA_VISIBLE_DEVICES=0,1,2,3 \
VLLM_USE_FLASHINFER_SAMPLER=0 \
vllm serve Qwen/Qwen3-8B \
  --host 0.0.0.0 \
  --port 8889 \
  --tensor-parallel-size 4 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 8192 \
  --served-model-name Qwen/Qwen3-8B