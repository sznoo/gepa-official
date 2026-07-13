#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/jinwoo/gepa-official"

cd "${ROOT}"

python "${ROOT}/experiments/method_probe/data/build_splits.py" \
  --train-size 150 \
  --val-size 150 \
  --test-size 150 \
  --seed 0 \
  --hf-split train \
  --out-dir "${ROOT}/experiments/method_probe/data"
