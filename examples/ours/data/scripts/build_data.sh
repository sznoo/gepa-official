cd /home/jinwoo/gepa-official


python experiments/method_probe/data/build_splits.py \
  --train-size 150 \
  --val-size 150 \
  --test-size 150 \
  --seed 0 \
  --hf-split train \
  --out-dir experiments/method_probe/data \
  --overwrite