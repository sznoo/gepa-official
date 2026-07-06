#!/usr/bin/env bash
set -e

cd /home/jinwoo/gepa-official

export PYTHONPATH=/home/jinwoo/gepa-official/src:/home/jinwoo/gepa-official:${PYTHONPATH}

python - <<'PY'
import gepa
import gepa.adapters.dspy_adapter.dspy_adapter as d

print("gepa:", gepa.__file__)
print("dspy_adapter:", d.__file__)
print("has TOOL_MODULE_PREFIX:", hasattr(d, "TOOL_MODULE_PREFIX"))
PY

python -m examples.hotpotqa.run_hotpot \
  --train-size 100 \
  --val-size 100 \
  --test-size 100 \
  --max-metric-calls 1500 \
  --num-threads 20 \
  --run-dir outputs/hotpotqa2 \
  --analysis-log-dir outputs/hotpotqa2/analysis \
  --reflection-minibatch-size 3 \
  --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa