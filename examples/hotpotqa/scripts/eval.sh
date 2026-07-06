python -m examples.hotpotqa.scripts.eval_prompt_sets \
  --prompt-sets-dir examples/hotpotqa/prompt_sets \
  --output-dir outputs/hotpotqa_prompt_eval \
  --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \
  --split test \
  --test-size 150 \
  --num-threads 20 \
  --include-base \
  --save-per-example