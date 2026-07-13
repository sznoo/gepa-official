# /home/jinwoo/gepa-official/examples/ours/adapter.py
import copy
import hashlib
import json
from typing import Any, Callable

import dspy


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


def _to_jsonable(value: Any):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, set):
        return sorted(_to_jsonable(v) for v in value)
    if isinstance(value, dict):
        return {
            str(k): _to_jsonable(v)
            for k, v in value.items()
        }
    if hasattr(value, "_store"):
        return _to_jsonable(value._store)
    if hasattr(value, "items"):
        return {
            str(k): _to_jsonable(v)
            for k, v in value.items()
        }
    return str(value)


def _candidate_hash(candidate: dict[str, str]) -> str:
    payload = json.dumps(
        candidate,
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha1(
        payload.encode("utf-8")
    ).hexdigest()[:12]


def _normalize_title(title: str) -> str:
    return " ".join(
        str(title).strip().lower().split()
    )


def _extract_titles(docs: list[str] | None) -> list[str]:
    return [
        str(doc).split(" | ", 1)[0].strip()
        for doc in docs or []
    ]


def _gold_titles(example: Any) -> list[str]:
    supporting_facts = (
        _get(example, "supporting_facts", {}) or {}
    )
    titles = _get(
        supporting_facts,
        "title",
        [],
    ) or []

    return list(
        dict.fromkeys(
            str(title).strip()
            for title in titles
        )
    )


def _example_id(example: Any):
    return _get(
        example,
        "_id",
        _get(example, "id"),
    )


def _compute_support_metrics(
    gold_titles: list[str],
    hop1_titles: list[str],
    hop2_titles: list[str],
) -> dict[str, Any]:
    gold_map = {
        _normalize_title(title): title
        for title in gold_titles
    }

    gold = set(gold_map)
    hop1 = {
        _normalize_title(title)
        for title in hop1_titles
    }
    hop2 = {
        _normalize_title(title)
        for title in hop2_titles
    }

    total = hop1 | hop2

    hit_hop1 = gold & hop1
    hit_hop2 = gold & hop2
    hit_total = gold & total

    new_hop2 = hit_hop2 - hit_hop1
    missing = gold - hit_total

    denominator = len(gold) if gold else 1

    return {
        "support_recall_hop1": (
            len(hit_hop1) / denominator
        ),
        "support_recall_hop2_only": (
            len(hit_hop2) / denominator
        ),
        "support_recall_total": (
            len(hit_total) / denominator
        ),
        "new_support_titles_hop2": [
            gold_map[title]
            for title in sorted(new_hop2)
        ],
        "missing_titles_after_hop2": [
            gold_map[title]
            for title in sorted(missing)
        ],
        "hit_titles_hop1": [
            gold_map[title]
            for title in sorted(hit_hop1)
        ],
        "hit_titles_total": [
            gold_map[title]
            for title in sorted(hit_total)
        ],
    }


class HotpotAdapter:
    """
    HotpotQA execution adapter.

    Responsibilities:
      - apply a prompt candidate to the DSPy program
      - execute a full forward pass
      - rerun from a selected agent
      - produce a structured trace
      - evaluate end-to-end answer EM

    Cache arguments are accepted for runner compatibility, but caching is
    intentionally not implemented here.
    """

    def __init__(
        self,
        program: dspy.Module,
        metric_fn: Callable,
        cache_dir: str | None = None,
        runtime_config: dict[str, Any] | None = None,
    ):
        self.program = program
        self.metric_fn = metric_fn
        self.cache_dir = cache_dir
        self.runtime_config = runtime_config or {}

    def predictor_names(self) -> list[str]:
        return [
            name
            for name, _ in self.program.named_predictors()
        ]

    def validate_candidate(
        self,
        candidate: dict[str, str],
    ):
        predictor_names = set(self.predictor_names())
        candidate_names = set(candidate)

        missing = predictor_names - candidate_names
        extra = candidate_names - predictor_names

        if missing:
            raise ValueError(
                "Prompt candidate is missing predictor keys: "
                f"{sorted(missing)}"
            )

        if extra:
            raise ValueError(
                "Prompt candidate has unknown predictor keys: "
                f"{sorted(extra)}"
            )

        for name, instruction in candidate.items():
            if not isinstance(name, str):
                raise TypeError(
                    "Candidate keys must be strings."
                )
            if not isinstance(instruction, str):
                raise TypeError(
                    f"Instruction for {name!r} must be a string."
                )

    def build_program(
        self,
        candidate: dict[str, str],
    ) -> dspy.Module:
        self.validate_candidate(candidate)

        program = copy.deepcopy(self.program)

        for name, predictor in program.named_predictors():
            predictor.signature = (
                predictor.signature.with_instructions(
                    candidate[name]
                )
            )

        return program

    def _score(
        self,
        example,
        prediction,
    ) -> float:
        result = self.metric_fn(
            example,
            prediction,
        )

        score = _get(result, "score", result)
        return float(score)

    def _build_trace(
        self,
        example,
        prediction,
        candidate: dict[str, str],
        rerun_from: str | None = None,
    ) -> dict[str, Any]:
        hop1_docs = list(
            _get(prediction, "hop1_docs", []) or []
        )
        hop2_docs = list(
            _get(prediction, "hop2_docs", []) or []
        )

        hop1_titles = _extract_titles(hop1_docs)
        hop2_titles = _extract_titles(hop2_docs)
        gold_titles = _gold_titles(example)

        trace = {
            "sample_id": _example_id(example),
            "candidate_hash": _candidate_hash(candidate),
            "rerun_from": rerun_from,
            "question": _get(example, "question"),
            "gold_answer": _get(example, "answer"),
            "context": _to_jsonable(
                _get(example, "context", {})
            ),
            "supporting_facts": _to_jsonable(
                _get(example, "supporting_facts", {})
            ),
            "gold_support_titles": gold_titles,
            "hop1_query": _get(
                prediction,
                "hop1_query",
                _get(example, "question"),
            ),
            "hop1_docs": _to_jsonable(hop1_docs),
            "hop1_titles": hop1_titles,
            "summary_1": _get(
                prediction,
                "summary_1",
            ),
            "hop2_query": _get(
                prediction,
                "hop2_query",
            ),
            "hop2_docs": _to_jsonable(hop2_docs),
            "hop2_titles": hop2_titles,
            "summary_2": _get(
                prediction,
                "summary_2",
            ),
            "answer": _get(
                prediction,
                "answer",
                "",
            ),
            "score": self._score(
                example,
                prediction,
            ),
        }

        trace.update(
            _compute_support_metrics(
                gold_titles=gold_titles,
                hop1_titles=hop1_titles,
                hop2_titles=hop2_titles,
            )
        )

        return trace

    def forward(
        self,
        example,
        candidate: dict[str, str],
    ) -> dict[str, Any]:
        program = self.build_program(candidate)

        prediction = program(
            question=_get(example, "question")
        )

        return self._build_trace(
            example=example,
            prediction=prediction,
            candidate=candidate,
            rerun_from=None,
        )

    def rerun(
        self,
        example,
        candidate: dict[str, str],
        start_agent: str,
        baseline_trace: dict[str, Any],
    ) -> dict[str, Any]:
        program = self.build_program(candidate)

        prediction = program.rerun_from(
            question=_get(example, "question"),
            baseline_trace=baseline_trace,
            start_agent=start_agent,
        )

        return self._build_trace(
            example=example,
            prediction=prediction,
            candidate=candidate,
            rerun_from=start_agent,
        )

    def evaluate(
        self,
        dataset,
        candidate: dict[str, str],
        return_traces: bool = False,
    ) -> dict[str, Any]:
        traces = [
            self.forward(
                example=example,
                candidate=candidate,
            )
            for example in dataset
        ]

        scores = [
            float(trace["score"])
            for trace in traces
        ]

        result = {
            "score": (
                sum(scores) / len(scores)
                if scores
                else 0.0
            ),
            "num_examples": len(scores),
            "num_correct": int(sum(scores)),
            "scores": scores,
        }

        if return_traces:
            result["traces"] = traces

        return result
