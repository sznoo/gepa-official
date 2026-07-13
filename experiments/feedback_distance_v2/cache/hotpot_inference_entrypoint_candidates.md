# Candidate HotpotQA / GEPA inference entrypoints


## score=10 experiments/feedback_distance_v2/scripts/find_hotpot_inference_entrypoints.py
6: Path("examples/hotpotqa"),
8: Path("outputs/hotpotqa_representation_prompt_screening"),
12: "create_query_hop2",
13: "summarize1",
14: "summarize2",
15: "final_answer",
16: "rollout_traces",
17: "prompt_candidate",

## score=8 experiments/deltaq/run_hotpot_ideal_context_upper_bound.py
15: from examples.hotpotqa.program import HotpotMultiHop
16: from examples.hotpotqa.retriever import set_retriever_dir
17: from examples.hotpotqa.metric import answer_match_fn
20: from examples.hotpotqa.data import load_hotpot_splits
32: "outputs/hotpotqa_representation_prompt_screening/"
33: "rep_prompt_screening_24_dev300_final_v2/conditions"
37: DEFAULT_ROOT + "/final_manual_only/prompt_candidate.json"
43: + "/prompt_candidate.json"

## score=6 examples/hotpotqa/scripts/eval_prompt_sets.py
1: # /home/jinwoo/gepa-official/examples/hotpotqa/scripts/eval_prompt_sets.py
16: from examples.hotpotqa.data import load_hotpot_splits
17: from examples.hotpotqa.feedback import feedback_fn_map
18: from examples.hotpotqa.metric import answer_exact_match
19: from examples.hotpotqa.program import HotpotMultiHop
20: from examples.hotpotqa.retriever import DEFAULT_RETRIEVER_DIR, set_retriever_dir
24: "summarize1.predict",
25: "create_query_hop2.predict",

## score=6 examples/hotpotqa/scripts/run_agentgrad_best_full_isolated.py
14: BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"
103: "summarize1.predict": AGENTGRAD_SUMMARIZE1,
104: "create_query_hop2.predict": AGENTGRAD_CREATE_QUERY_HOP2,
105: "summarize2.predict": AGENTGRAD_SUMMARIZE2,
106: "final_answer.predict": AGENTGRAD_FINAL,
110: "summarize1.predict": ["summarize1.predict", "summarize1"],
111: "create_query_hop2.predict": ["create_query_hop2.predict", "create_query_hop2"],
112: "summarize2.predict": ["summarize2.predict", "summarize2"],

## score=6 examples/hotpotqa/scripts/run_agentgrad_full_comparison_dev300.py
13: BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"
158: "summarize1.predict": AGENTGRAD_SUMMARIZE1,
159: "create_query_hop2.predict": AGENTGRAD_CREATE_QUERY_HOP2,
160: "summarize2.predict": AGENTGRAD_SUMMARIZE2,
161: "final_answer.predict": AGENTGRAD_FINAL,
323: # Direct module-key style: {"summarize1.predict": "..."}
331: # Record style: {"module": "summarize1.predict", "instruction": "..."}
374: # Patch json serialization, because the base runner usually writes prompt_candidate.json.

## score=6 examples/hotpotqa/scripts/run_agentgrad_full_only_dev300.py
14: BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"
103: "summarize1.predict": AGENTGRAD_SUMMARIZE1,
104: "create_query_hop2.predict": AGENTGRAD_CREATE_QUERY_HOP2,
105: "summarize2.predict": AGENTGRAD_SUMMARIZE2,
106: "final_answer.predict": AGENTGRAD_FINAL,
110: "summarize1.predict": [
111: "summarize1.predict",
112: "summarize1",

## score=6 experiments/deltaq/run_trace_sgd_onestep.py
19: from examples.hotpotqa.program import HotpotMultiHop
22: from examples.hotpotqa.metric import answer_match_fn
244: # keys look like "create_query_hop2.predict"
253: fixed = load_json(args.fixed_prompt_candidate)
256: if args.base_prompt_candidate:
257: base = load_json(args.base_prompt_candidate)
258: if "create_query_hop2.predict" in base["prompts"]:
259: prompts["create_query_hop2.predict"] = base["prompts"]["create_query_hop2.predict"]

## score=5 examples/hotpotqa/feedback.py
1: # /home/jinwoo/gepa-official/examples/hotpotqa/feedback.py
2: from examples.hotpotqa.metric import answer_match_fn, answer_exact_match_with_feedback
173: def provide_feedback_to_summarize1_module(
241: "create_query_hop2.predict": provide_feedback_to_query_module,
242: "final_answer.predict": provide_feedback_to_answer_module,
243: "summarize1.predict": provide_feedback_to_summarize1_module,
244: "summarize2.predict": provide_feedback_to_summary2_module,

## score=5 examples/hotpotqa/program.py
1: # /home/jinwoo/gepa-official/examples/hotpotqa/program.py
6: from examples.hotpotqa.retriever import search, set_retriever_dir
28: self.summarize1 = dspy.ChainOfThought("question,passages->summary")
29: self.create_query_hop2 = dspy.ChainOfThought("question,summary_1->query")
30: self.summarize2 = dspy.ChainOfThought("question,context,passages->summary")
31: self.final_answer = dspy.ChainOfThought("question,summary_1,summary_2->answer")
37: summary_1 = self.summarize1(
43: hop2_query = self.create_query_hop2(

## score=5 examples/hotpotqa/scripts/run_C_top2_large_probe.py
26: from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter  # noqa: E402
27: from examples.hotpotqa.data import load_hotpot_splits  # noqa: E402
28: from examples.hotpotqa.feedback import feedback_fn_map  # noqa: E402
29: from examples.hotpotqa.metric import answer_exact_match  # noqa: E402
30: from examples.hotpotqa.program import HotpotMultiHop  # noqa: E402
31: from examples.hotpotqa.retriever import set_retriever_dir  # noqa: E402
34: HOP2_COMPONENT = "create_query_hop2.predict"
35: FINAL_COMPONENT = "final_answer.predict"

## score=5 examples/hotpotqa/scripts/run_R6_v2_representation_17_dev300.py
9: BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"
200: - summarize1.predict: reasoning+summary format with passage mapping, missing fact diagnosis, prioritized next-hop retrieval plan.
201: - create_query_hop2.predict: Given question and summary_1, produce query.
202: - summarize2.predict: Given question, context, passages, produce summary.
203: - final_answer.predict: reasoning+answer blocks with strict hygiene and normalization.
206: For a true agentgrad_best_full condition, the base runner must support per-condition overrides for summarize1, summarize2, and final_answer.
224: # Reference condition: agentgrad create_query_hop2 only, under the same final_v2-fixed runner.

## score=5 examples/hotpotqa/scripts/run_bm_aware_hop2_large_probe.py
26: from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter  # noqa: E402
27: from examples.hotpotqa.data import load_hotpot_splits  # noqa: E402
28: from examples.hotpotqa.feedback import feedback_fn_map  # noqa: E402
29: from examples.hotpotqa.metric import answer_exact_match  # noqa: E402
30: from examples.hotpotqa.program import HotpotMultiHop  # noqa: E402
31: from examples.hotpotqa.retriever import set_retriever_dir  # noqa: E402
34: HOP2_COMPONENT = "create_query_hop2.predict"
35: FINAL_COMPONENT = "final_answer.predict"

## score=5 examples/hotpotqa/scripts/run_final_prompt_probe.py
26: from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter  # noqa: E402
27: from examples.hotpotqa.data import load_hotpot_splits  # noqa: E402
28: from examples.hotpotqa.feedback import feedback_fn_map  # noqa: E402
29: from examples.hotpotqa.metric import answer_exact_match  # noqa: E402
30: from examples.hotpotqa.program import HotpotMultiHop  # noqa: E402
31: from examples.hotpotqa.retriever import set_retriever_dir  # noqa: E402
34: TARGET_COMPONENT = "final_answer.predict"
316: rollout_summary = summarize_rollouts(analysis_dir / "rollout_traces.jsonl")

## score=5 examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py
26: from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter  # noqa: E402
27: from examples.hotpotqa.data import load_hotpot_splits  # noqa: E402
28: from examples.hotpotqa.feedback import feedback_fn_map  # noqa: E402
29: from examples.hotpotqa.metric import answer_exact_match  # noqa: E402
30: from examples.hotpotqa.program import HotpotMultiHop  # noqa: E402
31: from examples.hotpotqa.retriever import set_retriever_dir  # noqa: E402
34: HOP2_COMPONENT = "create_query_hop2.predict"
35: FINAL_COMPONENT = "final_answer.predict"

## score=5 examples/hotpotqa/scripts/run_large_manual_probe.py
26: from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter  # noqa: E402
27: from examples.hotpotqa.data import load_hotpot_splits  # noqa: E402
28: from examples.hotpotqa.feedback import feedback_fn_map  # noqa: E402
29: from examples.hotpotqa.metric import answer_exact_match  # noqa: E402
30: from examples.hotpotqa.program import HotpotMultiHop  # noqa: E402
31: from examples.hotpotqa.retriever import set_retriever_dir  # noqa: E402
34: HOP2_COMPONENT = "create_query_hop2.predict"
35: FINAL_COMPONENT = "final_answer.predict"

## score=5 examples/hotpotqa/scripts/run_representation_probe.py
3: Representation probe for HotpotQA GEPA traces.
6: 1. Reads an existing GEPA run, e.g. outputs/hotpotqa2.
7: 2. Selects create_query_hop2.predict feedback pairs from analysis/feedback_examples.jsonl.
11: 6. Evaluates the resulting candidate on the fixed HotpotQA split.
16: python examples/hotpotqa/scripts/run_representation_probe.py \
17: --source-run outputs/hotpotqa2 \
18: --output-root outputs/hotpotqa_representation_probe \
32: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \

## score=4 examples/hotpotqa/run_hotpot.py
1: # /home/jinwoo/gepa-official/examples/hotpotqa/run_hotpot.py
12: from examples.hotpotqa.analysis_adapter import HotpotLoggingDspyAdapter
13: from examples.hotpotqa.data import load_hotpot_splits
14: from examples.hotpotqa.feedback import feedback_fn_map
15: from examples.hotpotqa.metric import answer_exact_match
16: from examples.hotpotqa.program import HotpotMultiHop
17: from examples.hotpotqa.retriever import DEFAULT_RETRIEVER_DIR, set_retriever_dir
21: "rollout_traces.jsonl",

## score=4 experiments/deltaq/fill_qtrace_summary1.py
60: def load_summarize1_instruction(path):
64: find_key_subtree(data, "summarize1")
86: print(f"[summarize1 instruction] extracted from {p}, chars={length}, score={score}")
89: print("[warn] summarize1 instruction not found; using generic fallback")
154: from examples.hotpotqa.retriever import search, set_retriever_dir
209: You are the summarize1 module in a two-hop HotpotQA BM25 pipeline.
211: Base summarize1 instruction:
257: instruction = load_summarize1_instruction(args.base_prompt_candidate)

## score=4 experiments/deltaq/judge_hotpot_upper_bound_rows.py
172: You are judging answer equivalence for HotpotQA.
213: You are judging whether the summaries contain enough evidence to answer a HotpotQA question with the gold answer.
253: You are judging whether the retrieved passages contain enough evidence to answer a HotpotQA question with the gold answer.
455: "outputs/hotpotqa_representation_prompt_screening/"
456: "rep_prompt_screening_24_dev300_final_v2/conditions/"
457: "final_manual_only/analysis/rollout_traces.jsonl"

## score=4 experiments/deltaq/run_biggest_step_rtrace_decomposition.py
94: subtree = find_key_subtree(data, "create_query_hop2") or find_key_subtree(data, "hop2") or data
112: print(f"[create_query_hop2 instruction] extracted from {p}, chars={length}, score={score}")
115: print("[warn] create_query_hop2 instruction not found; using fallback")
194: from examples.hotpotqa.retriever import search, set_retriever_dir
314: Describe this retrieval state as a compact R-state for second-hop HotpotQA retrieval.
362: You are judging retrieval-context update magnitude for HotpotQA BM25.
482: Convert one adjacent R-state transition into a local prompt-gradient descriptor for create_query_hop2.
550: You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.

## score=4 experiments/deltaq/run_full_trace_prompt_injection_probe.py
206: find_key_subtree(data, "create_query_hop2")
225: print("[warn] could not extract create_query_hop2 instruction; using fallback")
384: Compress the retrieval trace into an executable query-edit plan for create_query_hop2.
471: You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.
473: Base create_query_hop2 instruction:
500: from examples.hotpotqa.retriever import search, set_retriever_dir
507: print(f"[retriever] using examples.hotpotqa.retriever.search(query, k={k})")
738: base_instruction = load_create_query_instruction(args.base_prompt_candidate)

## score=4 experiments/deltaq/run_stepwise_pgrad_compression_probe.py
118: subtree = find_key_subtree(data, "create_query_hop2") or find_key_subtree(data, "hop2") or data
136: print(f"[create_query_hop2 instruction] extracted from {p}, chars={length}, score={score}")
236: This is NOT a query. This is a prompt update description that would make create_query_hop2 move from the BEFORE query toward the AFTER query.
249: - Express the update as behavior reusable inside this sample's create_query_hop2 prompt.
348: You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.
350: Base create_query_hop2 instruction:
376: from examples.hotpotqa.retriever import search, set_retriever_dir
574: base_instruction = load_create_query_instruction(args.base_prompt_candidate)

## score=4 experiments/deltaq/run_trace_sgd_variant_sweep_full.sh
10: export HOTPOT_RETRIEVER_DIR=/home/jinwoo/gepa-official/examples/hotpotqa
52: --base-prompt-candidate outputs/hotpotqa_representation_prompt_screening/rep_prompt_screening_24_dev300_final_v2/conditions/final_manual_only/prompt_candidate.json \
53: --fixed-prompt-candidate experiments/deltaq/prompt_candidates/final_manual_with_agentgrad_best_full_final_answer.json \

## score=4 experiments/feedback_distance_v2/scripts/export_fixed_prompt_config.py
8: "outputs/hotpotqa_representation_prompt_screening/"
9: "rep_prompt_screening_24_dev300_final_v2/"
30: prompt_path = condition_dir / "prompt_candidate.json"
32: rollout_preview_path = condition_dir / "analysis" / "rollout_traces.jsonl"
43: "prompt_candidate_path": str(prompt_path),
47: "prompt_candidate": prompt_obj,
61: print("[prompt_candidate keys]", sorted(prompt_obj.keys()) if isinstance(prompt_obj, dict) else type(prompt_obj).__name__)

## score=4 scripts/diagnose_hotpot_wrong_cases.py
27: DIAGNOSIS_INSTRUCTIONS = """You are diagnosing a failed HotpotQA multi-hop RAG prediction.
34: - final_answer_failure
76: - If support_recall_total = 1 but answer is wrong, diagnose summary2 or final_answer.
205: "major_category": "retrieval_failure" if support_recall_float < 1.0 else "final_answer_failure",
208: "failure_stage": "hop2_retrieval" if support_recall_float < 1.0 else "final_answer",
457: rollout_path = analysis_dir / "rollout_traces.jsonl"
610: parser.add_argument("--run-dir", default="/home/jinwoo/gepa-official/outputs/hotpotqa")

## score=3 examples/hotpotqa/analyze_recall_total.py
1: # /home/jinwoo/gepa-official/examples/hotpotqa/analyze_recall_total.py
476: lines.append("# HotpotQA GEPA Support Recall Comparison by Update\n")
479: "and `rollout_traces.jsonl`, then groups all paired rollout cases by proposal/update.\n"
534: parser.add_argument("--run-dir", default="/home/jinwoo/gepa-official/outputs/hotpotqa_smoke")
553: rollout_path = analysis_dir / "rollout_traces.jsonl"
595: index_md = "# HotpotQA GEPA Update Index\\n\\n"

## score=3 experiments/deltaq/build_trace_sgd_pool.py
119: "outputs/hotpotqa_representation_prompt_screening/"
120: "rep_prompt_screening_24_dev300_final_v2/conditions/"
121: "final_manual_only/analysis/rollout_traces.jsonl"

## score=3 experiments/deltaq/run_deltaq_probe.py
10: from examples.hotpotqa.retriever import search, set_retriever_dir
21: "outputs/hotpotqa_representation_prompt_screening/"
22: "rep_prompt_screening_24_dev300_final_v2/"
23: "case_study_R6_best_vs_final_manual/retrieval_gain.jsonl"

## score=3 experiments/deltaq/run_hotpot_ideal_context_upper_bound_parallel.py
14: from examples.hotpotqa.program import HotpotMultiHop
15: from examples.hotpotqa.retriever import set_retriever_dir
27: apply_prompt_candidate,
71: apply_prompt_candidate(fixed_program, args.fixed_prompt_candidate)
74: apply_prompt_candidate(r6_program, args.r6_prompt_candidate)
156: q = r6_program.create_query_hop2(
307: print(f"[info] fixed_prompt_candidate: {args.fixed_prompt_candidate}")

## score=3 experiments/deltaq/run_lifting_component_ablation.py
11: from examples.hotpotqa.retriever import search, set_retriever_dir
22: "outputs/hotpotqa_representation_prompt_screening/"
23: "rep_prompt_screening_24_dev300_final_v2/"
24: "case_study_R6_best_vs_final_manual/retrieval_gain.jsonl"

## score=3 experiments/deltaq/run_multicase_lifting_probe.py
10: from examples.hotpotqa.retriever import search, set_retriever_dir
21: "outputs/hotpotqa_representation_prompt_screening/"
22: "rep_prompt_screening_24_dev300_final_v2/"
23: "case_study_R6_best_vs_final_manual/retrieval_gain.jsonl"

## score=3 experiments/deltaq/run_prompt_trace_probe.py
11: from examples.hotpotqa.retriever import search, set_retriever_dir
22: "outputs/hotpotqa_representation_prompt_screening/"
23: "rep_prompt_screening_24_dev300_final_v2/"
24: "case_study_R6_best_vs_final_manual/retrieval_gain.jsonl"

## score=3 experiments/deltaq/run_query_grounded_prompt_update_from_rtrace.py
83: Δp_i = local prompt update that would make create_query_hop2 produce q_after-like retrieval behavior.
160: Convert an explicit local query transition Δq_i into a local prompt delta Δp_i for create_query_hop2.
299: Aggregate the ordered local prompt deltas into ONE sample-level updated create_query_hop2 instruction p_i'.
350: You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.
352: create_query_hop2 instruction:
376: You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.
378: Base create_query_hop2 instruction:
663: base_instruction = br.load_create_query_instruction(args.base_prompt_candidate)

## score=3 experiments/deltaq/run_rq_grounded_delta_p_aggregation.py
108: Visible inputs available to create_query_hop2:
122: You are deriving a LOCAL PROMPT DELTA Δp_i for create_query_hop2.
152: - Preserve the interface: create_query_hop2 must output exactly one compact BM25 query.
246: You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.
248: Base create_query_hop2 instruction:
271: Aggregate the ordered local prompt deltas into ONE sample-level updated create_query_hop2 instruction p_i'.
281: - Preserve create_query_hop2's role: produce exactly one compact second-hop BM25 query.
302: Aggregate the ordered local trace into ONE sample-level updated create_query_hop2 instruction p_i'.

## score=3 experiments/deltaq/run_sample_level_prompt_update_from_rtrace.py
129: Rewrite the create_query_hop2 instruction for THIS SAMPLE ONLY.
149: Base create_query_hop2 instruction:
179: You are the create_query_hop2 module in a two-hop HotpotQA BM25 pipeline.
181: create_query_hop2 instruction:
394: base_instruction = br.load_create_query_instruction(args.base_prompt_candidate)

## score=2 examples/hotpotqa/data.py
1: # /home/jinwoo/gepa-official/examples/hotpotqa/data.py
36: Load HotpotQA fullwiki and create deterministic train/val/test splits.

## score=2 examples/hotpotqa/metric.py
1: # /home/jinwoo/gepa-official/examples/hotpotqa/metric.py
63: Build a compact gold-support context from HotpotQA fields.

## score=2 experiments/deltaq/run_context_global_prompt_probe.py
13: from examples.hotpotqa.retriever import set_retriever_dir
140: Below are oracle-derived local query deltas from successful HotpotQA second-hop retrieval transitions.
163: You are rewriting a HotpotQA second-hop BM25 query.
189: You are rewriting a HotpotQA second-hop BM25 query.

## score=2 experiments/deltaq/run_qtrace_accumulation_probe.py
167: You are rewriting the second-hop BM25 query for a two-hop HotpotQA retriever.
199: You are rewriting the second-hop BM25 query for a two-hop HotpotQA retriever.
259: You are rewriting the second-hop BM25 query for a two-hop HotpotQA retriever.
291: Use the HotpotQA BM25 retriever directly.
294: from examples.hotpotqa.retriever import search, set_retriever_dir
303: from examples.hotpotqa.retriever import search, set_retriever_dir
310: print(f"[retriever] using examples.hotpotqa.retriever.search(query, k={k})")

## score=1 examples/hotpotqa/analysis_adapter.py
1: # /home/jinwoo/gepa-official/examples/hotpotqa/analysis_adapter.py
21: from examples.hotpotqa.logging_utils import HotpotAnalysisLoggers

## score=1 examples/hotpotqa/logging_utils.py
24: self.rollout = JsonlLogger(log_dir / "rollout_traces.jsonl")

## score=1 examples/hotpotqa/retriever.py
1: # /home/jinwoo/gepa-official/examples/hotpotqa/retriever.py

## score=1 examples/hotpotqa/scripts/eval.sh
1: python -m examples.hotpotqa.scripts.eval_prompt_sets \
2: --prompt-sets-dir examples/hotpotqa/prompt_sets \
3: --output-dir outputs/hotpotqa_prompt_eval \
4: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \

## score=1 examples/hotpotqa/scripts/run_hop2_candidate_search_v2_dev300.py
9: BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"

## score=1 examples/hotpotqa/scripts/run_hop2_candidate_search_v3_dev300.py
9: BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"

## score=1 examples/hotpotqa/scripts/run_no_lockin_final_v2_dev300.py
9: BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"

## score=1 examples/hotpotqa/scripts/run_representation_probe.sh
8: python examples/hotpotqa/scripts/run_representation_probe.py \
9: --source-run outputs/hotpotqa2 \
10: --output-root outputs/hotpotqa_representation_probe \
27: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \

## score=1 examples/hotpotqa/scripts/run_representation_probe_A4.sh
8: python examples/hotpotqa/scripts/run_representation_probe.py \
9: --source-run outputs/hotpotqa2 \
10: --output-root outputs/hotpotqa_representation_probe \
27: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \

## score=1 examples/hotpotqa/scripts/run_representation_probe_A4_vs_gepa.sh
8: python examples/hotpotqa/scripts/run_representation_probe.py \
9: --source-run outputs/hotpotqa2 \
10: --output-root outputs/hotpotqa_representation_probe \
33: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \

## score=1 examples/hotpotqa/scripts/run_representation_probe_B6_best.sh
8: python examples/hotpotqa/scripts/run_representation_probe.py \
9: --source-run outputs/hotpotqa2 \
10: --output-root outputs/hotpotqa_representation_probe \
34: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \

## score=1 examples/hotpotqa/scripts/run_representation_probe_C6_best.sh
8: python examples/hotpotqa/scripts/run_representation_probe.py \
9: --source-run outputs/hotpotqa2 \
10: --output-root outputs/hotpotqa_representation_probe \
34: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \

## score=1 examples/hotpotqa/scripts/run_representation_probe_D6_best.sh
8: python examples/hotpotqa/scripts/run_representation_probe.py \
9: --source-run outputs/hotpotqa2 \
10: --output-root outputs/hotpotqa_representation_probe \
34: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \

## score=1 examples/hotpotqa/scripts/run_representation_prompt_screening_dev300.py
9: BASE_SCRIPT = ROOT / "examples/hotpotqa/scripts/run_hop2_candidate_search_dev300.py"

## score=1 examples/hotpotqa/test.sh
17: python -m examples.hotpotqa.run_hotpot \
23: --run-dir outputs/hotpotqa2 \
24: --analysis-log-dir outputs/hotpotqa2/analysis \
26: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa

## score=1 experiments/deltaq/run_qtrace_order_judge_probe.py
289: You are a local tool-aware distance comparison judge for a HotpotQA hop2 BM25 query state.
343: You are a metric-aware equivalence judge for a HotpotQA hop2 BM25 query state.

## score=1 experiments/deltaq/run_rtrace_midpoint_distance_judge.py
99: You are judging retrieval-context update magnitude for HotpotQA BM25.

## score=1 scripts/diagnose_hotpot_wrong_cases.sh
7: RUN_DIR=/home/jinwoo/gepa-official/outputs/hotpotqa

## score=1 scripts/run_optimized_baseline.sh
4: PROMPT_DIR=/home/jinwoo/gepa-official/examples/hotpotqa/prompt_sets
5: RUN_DIR=/home/jinwoo/gepa-official/outputs/hotpotqa
18: python -m examples.hotpotqa.run_hotpot \
25: --retriever-dir /home/jinwoo/gepa-official/examples/hotpotqa \
