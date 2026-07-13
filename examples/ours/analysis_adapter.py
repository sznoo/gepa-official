# /home/jinwoo/gepa-official/examples/ours/analysis_adapter.py
import hashlib
import json
import logging
import threading
from pathlib import Path
from typing import Any

import dspy
from dspy.adapters.chat_adapter import ChatAdapter
from dspy.adapters.types import History
from dspy.adapters.types.base_type import Type
from dspy.teleprompt.bootstrap_trace import FailedPrediction

from gepa.adapters.dspy_adapter.dspy_adapter import (
    DspyAdapter,
    TOOL_MODULE_PREFIX,
)
from gepa.strategies.instruction_proposal import InstructionProposalSignature

from examples.hotpotqa.logging_utils import HotpotAnalysisLoggers

logger = logging.getLogger(__name__)


def _get(obj: Any, key: str, default=None):
    if obj is None:
        return default
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]
    except Exception:
        return default


def _to_jsonable(x: Any):
    if x is None or isinstance(x, bool | int | float | str):
        return x
    if isinstance(x, Path):
        return str(x)
    if isinstance(x, list | tuple):
        return [_to_jsonable(v) for v in x]
    if isinstance(x, set):
        return sorted(_to_jsonable(v) for v in x)
    if isinstance(x, dict):
        return {str(k): _to_jsonable(v) for k, v in x.items()}

    if hasattr(x, "items"):
        try:
            return {str(k): _to_jsonable(v) for k, v in x.items()}
        except Exception:
            pass

    if hasattr(x, "_store"):
        try:
            return _to_jsonable(x._store)
        except Exception:
            pass

    return str(x)


def _candidate_hash(candidate: dict[str, str]) -> str:
    s = json.dumps(candidate, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def _norm_title(title: str) -> str:
    return " ".join(str(title).strip().lower().split())


def _extract_titles(docs: list[str] | None) -> list[str]:
    titles = []
    for doc in docs or []:
        if not isinstance(doc, str):
            doc = str(doc)
        titles.append(doc.split(" | ", 1)[0].strip())
    return titles


def _gold_titles(example: Any) -> list[str]:
    supporting_facts = _get(example, "supporting_facts", {}) or {}
    titles = _get(supporting_facts, "title", []) or []
    return list(dict.fromkeys(str(t).strip() for t in titles))


def _gold_answer(example: Any):
    return _get(example, "answer")


def _example_id(example: Any):
    return _get(example, "_id", _get(example, "id", None))


def _compute_support_metrics(
    gold_titles: list[str],
    hop1_titles: list[str],
    hop2_titles: list[str],
) -> dict[str, Any]:
    gold_norm_to_orig = {_norm_title(t): t for t in gold_titles}
    gold = set(gold_norm_to_orig)

    hop1 = {_norm_title(t) for t in hop1_titles}
    hop2 = {_norm_title(t) for t in hop2_titles}
    total = hop1 | hop2

    hit_hop1 = gold & hop1
    hit_hop2_only = gold & hop2
    hit_total = gold & total
    new_hop2 = hit_hop2_only - hit_hop1
    missing = gold - hit_total

    denom = len(gold) if gold else 1

    return {
        "support_recall_hop1": len(hit_hop1) / denom,
        "support_recall_hop2_only": len(hit_hop2_only) / denom,
        "support_recall_total": len(hit_total) / denom,
        "new_support_titles_hop2": [gold_norm_to_orig[t] for t in sorted(new_hop2)],
        "missing_titles_after_hop2": [gold_norm_to_orig[t] for t in sorted(missing)],
        "hit_titles_hop1": [gold_norm_to_orig[t] for t in sorted(hit_hop1)],
        "hit_titles_total": [gold_norm_to_orig[t] for t in sorted(hit_total)],
    }


class HotpotLoggingDspyAdapter(DspyAdapter):
    def __init__(
        self,
        *args,
        analysis_log_dir: str | Path | None = None,
        run_id: str | None = None,
        log_rollouts: bool = True,
        log_feedback: bool = True,
        log_proposals: bool = True,
        log_instructions_in_rollout: bool = True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.analysis_log_dir = Path(analysis_log_dir) if analysis_log_dir else None
        self.analysis_loggers = (
            HotpotAnalysisLoggers(self.analysis_log_dir)
            if self.analysis_log_dir is not None
            else None
        )

        self.run_id = run_id
        self.log_rollouts = log_rollouts
        self.log_feedback = log_feedback
        self.log_proposals = log_proposals
        self.log_instructions_in_rollout = log_instructions_in_rollout

        self._eval_counter = 0
        self._eval_counter_lock = threading.Lock()

        self._context_lock = threading.Lock()
        self._context: dict[str, Any] = {}

    def set_analysis_context(self, **kwargs):
        with self._context_lock:
            self._context = dict(kwargs)

    def clear_analysis_context(self):
        with self._context_lock:
            self._context = {}

    def _next_eval_index(self) -> int:
        with self._eval_counter_lock:
            self._eval_counter += 1
            return self._eval_counter

    def _current_context(self) -> dict[str, Any]:
        with self._context_lock:
            return dict(self._context)

    def _write_rollouts(
        self,
        *,
        batch,
        candidate: dict[str, str],
        eval_batch,
        capture_traces: bool,
        eval_index: int,
    ):
        if not self.analysis_loggers or not self.log_rollouts:
            return

        context = self._current_context()
        cand_hash = _candidate_hash(candidate)

        phase = context.get(
            "phase",
            "trace_eval" if capture_traces else "eval_full",
        )

        for local_idx, (example, pred, score) in enumerate(
            zip(batch, eval_batch.outputs, eval_batch.scores, strict=False)
        ):
            hop1_docs = _get(pred, "hop1_docs", []) or []
            hop2_docs = _get(pred, "hop2_docs", []) or []
            hop1_titles = _extract_titles(hop1_docs)
            hop2_titles = _extract_titles(hop2_docs)
            gold_titles = _gold_titles(example)

            support_metrics = _compute_support_metrics(
                gold_titles=gold_titles,
                hop1_titles=hop1_titles,
                hop2_titles=hop2_titles,
            )

            record = {
                "run_id": self.run_id,
                "phase": phase,
                "split": context.get("split"),
                "iteration": context.get("iteration"),
                "candidate_id": context.get("candidate_id"),
                "parent_candidate_id": context.get("parent_candidate_id"),
                "updated_component": context.get("updated_component"),
                "candidate_hash": cand_hash,
                "eval_index": eval_index,
                "capture_traces": capture_traces,
                "local_example_idx": local_idx,
                "example_id": _example_id(example),
                "question": _get(example, "question"),
                "gold_answer": _gold_answer(example),
                "gold_support_titles": gold_titles,
                "hop1_query": _get(pred, "hop1_query", _get(example, "question")),
                "hop1_titles": hop1_titles,
                "hop1_docs": hop1_docs,
                "summary_1": _get(pred, "summary_1"),
                "hop2_query": _get(pred, "hop2_query"),
                "hop2_titles": hop2_titles,
                "hop2_docs": hop2_docs,
                "summary_2": _get(pred, "summary_2"),
                "pred_answer": _get(pred, "answer"),
                "score": score,
                **support_metrics,
            }

            if self.log_instructions_in_rollout:
                record["instructions"] = dict(candidate)

            self.analysis_loggers.write_rollout(_to_jsonable(record))

    def evaluate(self, batch, candidate, capture_traces=False):
        eval_index = self._next_eval_index()
        eval_batch = super().evaluate(batch, candidate, capture_traces=capture_traces)

        self._write_rollouts(
            batch=batch,
            candidate=candidate,
            eval_batch=eval_batch,
            capture_traces=capture_traces,
            eval_index=eval_index,
        )

        return eval_batch

    def make_reflective_dataset(self, candidate, eval_batch, components_to_update):
        program = self.build_program(candidate)
        cand_hash = _candidate_hash(candidate)
        context = self._current_context()

        ret_d: dict[str, list[dict[str, Any]]] = {}

        for pred_name in components_to_update:
            if pred_name.startswith(TOOL_MODULE_PREFIX):
                target_name = pred_name.removeprefix(f"{TOOL_MODULE_PREFIX}:")
            else:
                target_name = pred_name

            module = None
            for name, m in program.named_predictors():
                if name == target_name:
                    module = m
                    break
            assert module is not None, f"Predictor not found: {target_name}"

            items: list[dict[str, Any]] = []

            for traj_idx, data in enumerate(eval_batch.trajectories or []):
                trace = data["trace"]
                example = data["example"]
                prediction = data["prediction"]
                module_score_obj = data.get("score")
                module_score, _ = self._extract_score_and_subscores(module_score_obj)

                trace_instances = [t for t in trace if t[0].signature.equals(module.signature)]
                if not self.add_format_failure_as_feedback:
                    trace_instances = [
                        t for t in trace_instances
                        if not isinstance(t[2], FailedPrediction)
                    ]
                if len(trace_instances) == 0:
                    continue

                selected = None
                for t in trace_instances:
                    if isinstance(t[2], FailedPrediction):
                        selected = t
                        break

                if selected is None:
                    if isinstance(prediction, FailedPrediction):
                        continue
                    selected = self.rng.choice(trace_instances)

                inputs = selected[1]
                outputs = selected[2]

                new_inputs = {}
                new_outputs = {}

                contains_history = False
                history_key_name = None
                for input_key, input_val in inputs.items():
                    if isinstance(input_val, History):
                        contains_history = True
                        assert history_key_name is None
                        history_key_name = input_key

                if contains_history:
                    s = "```json\n"
                    for i, message in enumerate(inputs[history_key_name].messages):
                        s += f"  {i}: {message}\n"
                    s += "```"
                    new_inputs["Context"] = s

                for input_key, input_val in inputs.items():
                    if contains_history and input_key == history_key_name:
                        continue

                    if isinstance(input_val, Type) and self.custom_instruction_proposer is not None:
                        new_inputs[input_key] = input_val
                    else:
                        new_inputs[input_key] = str(input_val)

                feedback_score = None
                feedback_text = ""

                if isinstance(outputs, FailedPrediction):
                    s = "Couldn't parse the output as per the expected output format. The model's raw response was:\n"
                    s += "```\n"
                    s += outputs.completion_text + "\n"
                    s += "```\n\n"
                    new_outputs = s

                    adapter = ChatAdapter()
                    structure_instruction = ""
                    for dd in adapter.format(module.signature, [], {}):
                        structure_instruction += dd["role"] + ": " + dd["content"] + "\n"
                    feedback_text = "Your output failed to parse. Follow this structure:\n" + structure_instruction
                else:
                    for output_key, output_val in outputs.items():
                        new_outputs[output_key] = str(output_val)

                    feedback_fn = self.feedback_map[target_name]
                    fb = feedback_fn(
                        predictor_output=outputs,
                        predictor_inputs=inputs,
                        module_inputs=example,
                        module_outputs=prediction,
                        captured_trace=trace,
                    )

                    if isinstance(fb, dict):
                        feedback_score = fb.get("score")
                        feedback_text = fb.get("feedback", "")
                    else:
                        feedback_score = getattr(fb, "score", None)
                        feedback_text = getattr(fb, "feedback", "")

                    if module_score is not None and feedback_score is not None:
                        if abs(feedback_score - module_score) > 1e-8:
                            if self.warn_on_score_mismatch:
                                logger.warning(
                                    "The score returned by the predictor feedback differs from the module score. "
                                    "GEPA will use the module-level score for acceptance and the feedback text for reflection."
                                )
                                self.warn_on_score_mismatch = False

                reflective_item = {
                    "Inputs": new_inputs,
                    "Generated Outputs": new_outputs,
                    "Feedback": feedback_text,
                }
                items.append(reflective_item)

                if self.analysis_loggers and self.log_feedback:
                    hop1_docs = _get(prediction, "hop1_docs", []) or []
                    hop2_docs = _get(prediction, "hop2_docs", []) or []
                    hop1_titles = _extract_titles(hop1_docs)
                    hop2_titles = _extract_titles(hop2_docs)
                    gold_titles = _gold_titles(example)

                    record = {
                        "run_id": self.run_id,
                        "phase": context.get("phase", "reflective_dataset"),
                        "split": context.get("split"),
                        "iteration": context.get("iteration"),
                        "candidate_id": context.get("candidate_id"),
                        "candidate_hash": cand_hash,
                        "component": target_name,
                        "trajectory_idx": traj_idx,
                        "example_id": _example_id(example),
                        "question": _get(example, "question"),
                        "gold_answer": _gold_answer(example),
                        "gold_support_titles": gold_titles,
                        "hop1_titles": hop1_titles,
                        "hop2_titles": hop2_titles,
                        "module_score": module_score,
                        "feedback_score": feedback_score,
                        "predictor_inputs": new_inputs,
                        "predictor_outputs": new_outputs,
                        "feedback_text": feedback_text,
                        "module_outputs": {
                            "answer": _get(prediction, "answer"),
                            "hop1_query": _get(prediction, "hop1_query", _get(example, "question")),
                            "summary_1": _get(prediction, "summary_1"),
                            "hop2_query": _get(prediction, "hop2_query"),
                            "summary_2": _get(prediction, "summary_2"),
                        },
                    }
                    record.update(_compute_support_metrics(gold_titles, hop1_titles, hop2_titles))
                    self.analysis_loggers.write_feedback(_to_jsonable(record))

            if len(items) == 0:
                logger.warning(f"  No valid reflective examples found for {pred_name}")
                continue

            ret_d[pred_name] = items

        if len(ret_d) == 0:
            raise Exception("No valid predictions found for any module.")

        return ret_d

    def propose_new_texts(
        self,
        candidate: dict[str, str],
        reflective_dataset: dict[str, list[dict[str, Any]]],
        components_to_update: list[str],
    ) -> dict[str, str]:
        if any(c.startswith(TOOL_MODULE_PREFIX) for c in components_to_update):
            return super().propose_new_texts(
                candidate=candidate,
                reflective_dataset=reflective_dataset,
                components_to_update=components_to_update,
            )

        reflection_lm = self.reflection_lm or dspy.settings.lm
        if reflection_lm is None:
            raise ValueError("reflection_lm must be provided for proposal generation.")

        cand_hash = _candidate_hash(candidate)
        context = self._current_context()

        results: dict[str, str] = {}

        for name in components_to_update:
            if name not in reflective_dataset or not reflective_dataset.get(name):
                logger.warning(f"Component '{name}' is not in reflective dataset. Skipping.")
                continue

            base_instruction = candidate[name]
            dataset_with_feedback = reflective_dataset[name]

            def _single_lm_call(x):
                raw_outputs = reflection_lm(x)

                if isinstance(raw_outputs, list):
                    if not raw_outputs:
                        return ""
                    raw_output = raw_outputs[0]
                else:
                    raw_output = raw_outputs

                if isinstance(raw_output, dict):
                    if "text" not in raw_output:
                        raise KeyError("Missing 'text' field in reflection LM output.")
                    raw_output = raw_output["text"]

                return str(raw_output)


            result, prompt, raw_output = InstructionProposalSignature.run_with_metadata(
                lm=_single_lm_call,
                input_dict={
                    "current_instruction_doc": base_instruction,
                    "dataset_with_feedback": dataset_with_feedback,
                    "prompt_template": None,
                },
            )

            new_instruction = result["new_instruction"]
            results[name] = new_instruction

            if self.analysis_loggers and self.log_proposals:
                self.analysis_loggers.write_proposal(_to_jsonable({
                    "run_id": self.run_id,
                    "phase": context.get("phase", "proposal"),
                    "split": context.get("split"),
                    "iteration": context.get("iteration"),
                    "candidate_id": context.get("candidate_id"),
                    "parent_candidate_id": context.get("parent_candidate_id"),
                    "candidate_hash": cand_hash,
                    "component": name,
                    "old_instruction": base_instruction,
                    "new_instruction": new_instruction,
                    "reflection_prompt": prompt,
                    "raw_lm_output": raw_output,
                    "raw_contains_think": "<think>" in str(raw_output),
                    "new_instruction_contains_think": "<think>" in str(new_instruction),
                    "reflective_dataset": dataset_with_feedback,
                }))

        return results