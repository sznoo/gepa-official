#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import string
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

import dspy  # noqa: E402

from examples.hotpotqa.retriever import search, set_retriever_dir  # noqa: E402


DEFAULT_RETRIEVER_DIR = ROOT / "examples/hotpotqa"

PROMPT_KEY_TO_ATTR = {
    "summarize1.predict": "summarize1",
    "create_query_hop2.predict": "create_query_hop2",
    "summarize2.predict": "summarize2",
    "final_answer.predict": "final_answer",
}


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)

    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSONL: path={path}, line={line_number}"
                ) from exc

            rows.append(row)

    if not rows:
        raise ValueError(f"No rows found in {path}")

    return rows


def load_prompt_snapshot(path: str | Path) -> dict[str, str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    if isinstance(data, dict) and isinstance(data.get("prompts"), dict):
        data = data["prompts"]

    if not isinstance(data, dict):
        raise ValueError("Prompt snapshot must be a JSON object.")

    prompts = {}
    for key, value in data.items():
        if key in PROMPT_KEY_TO_ATTR and isinstance(value, str):
            prompts[key] = value

    if not prompts:
        raise ValueError(
            "No supported predictor prompts found. Expected keys such as "
            "'create_query_hop2.predict'."
        )

    return prompts


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _unique_strings(values: Iterable[Any]) -> list[str]:
    output = []
    seen = set()

    for value in values:
        text = _clean_text(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)

    return output


def passages_from_search_result(result: Any) -> list[str]:
    if result is None:
        return []

    if hasattr(result, "passages"):
        result = result.passages
    elif isinstance(result, Mapping):
        result = (
            result.get("passages")
            or result.get("docs")
            or result.get("contexts")
            or []
        )

    if isinstance(result, str):
        return [result]

    if not isinstance(result, (list, tuple)):
        raise TypeError(
            f"Unsupported retriever output type: {type(result).__name__}"
        )

    return [_clean_text(item) for item in result if _clean_text(item)]


def title_from_passage(passage: str) -> str:
    return passage.split(" | ", 1)[0].strip()


def titles_from_passages(passages: Iterable[str]) -> list[str]:
    return _unique_strings(title_from_passage(p) for p in passages)


def gold_support_titles(row: Mapping[str, Any]) -> list[str]:
    supporting_facts = row.get("supporting_facts") or {}
    return _unique_strings(supporting_facts.get("title") or [])


def normalize_answer(text: Any) -> str:
    """Standard HotpotQA-style answer normalization."""

    text = _clean_text(text).lower()

    text = "".join(
        char for char in text
        if char not in set(string.punctuation)
    )

    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = " ".join(text.split())

    return text


def exact_match(prediction: Any, gold: Any) -> int:
    return int(normalize_answer(prediction) == normalize_answer(gold))


def compute_retrieval_metrics(
    *,
    gold_titles: Iterable[str],
    hop1_titles: Iterable[str],
    hop2_titles: Iterable[str],
) -> dict[str, Any]:
    gold = set(_unique_strings(gold_titles))
    hop1 = set(_unique_strings(hop1_titles))
    hop2 = set(_unique_strings(hop2_titles))
    total = hop1 | hop2

    hit_after_hop1 = gold & hop1
    hit_after_hop2 = gold & total

    missing_after_hop1 = gold - hop1
    recovered_in_hop2 = missing_after_hop1 & hop2
    missing_after_hop2 = missing_after_hop1 - hop2

    denominator = len(gold)

    support_recall_hop1 = (
        len(hit_after_hop1) / denominator
        if denominator
        else None
    )
    support_recall_hop2_only = (
        len(gold & hop2) / denominator
        if denominator
        else None
    )
    support_recall_total = (
        len(hit_after_hop2) / denominator
        if denominator
        else None
    )

    # None means that hop1 already retrieved all gold support titles, so
    # missing-recovery is not applicable rather than a zero-valued failure.
    missing_recovery_rate = (
        len(recovered_in_hop2) / len(missing_after_hop1)
        if missing_after_hop1
        else None
    )

    return {
        "hit_support_titles_hop1": sorted(hit_after_hop1),
        "hit_support_titles_hop2": sorted(gold & hop2),
        "hit_support_titles_total": sorted(hit_after_hop2),
        "new_support_titles_hop2": sorted(recovered_in_hop2),
        "missing_after_hop1": sorted(missing_after_hop1),
        "recovered_missing_titles": sorted(recovered_in_hop2),
        "missing_after_hop2": sorted(missing_after_hop2),
        "support_recall_hop1": support_recall_hop1,
        "support_recall_hop2_only": support_recall_hop2_only,
        "support_recall_total": support_recall_total,
        "missing_recovery_rate": missing_recovery_rate,
        "missing_recovery_applicable": bool(missing_after_hop1),
        "natural_retrieval_failure": bool(missing_after_hop2),
    }


def _set_predictor_instruction(module: Any, instruction: str) -> None:
    predictor = getattr(module, "predict", module)
    signature = getattr(predictor, "signature", None)

    if signature is None:
        raise AttributeError(
            f"Cannot find DSPy signature on {type(module).__name__}"
        )

    if not hasattr(signature, "with_instructions"):
        raise AttributeError(
            "DSPy signature does not support with_instructions()."
        )

    predictor.signature = signature.with_instructions(instruction)


class HotpotRuntime:
    """
    Minimal two-hop HotpotQA runtime.

    Pipeline:
      question
      -> BM25 hop1
      -> summarize1
      -> create_query_hop2
      -> BM25 hop2
      -> summarize2
      -> final_answer
    """

    def __init__(
        self,
        *,
        retrieval_k: int = 7,
        retriever_dir: str | Path = DEFAULT_RETRIEVER_DIR,
        prompts: Optional[Mapping[str, str]] = None,
    ):
        if retrieval_k <= 0:
            raise ValueError("retrieval_k must be positive.")

        self.retrieval_k = int(retrieval_k)
        self.retriever_dir = Path(retriever_dir).resolve()

        set_retriever_dir(str(self.retriever_dir))

        self.summarize1 = dspy.ChainOfThought(
            "question,passages->summary"
        )
        self.create_query_hop2 = dspy.ChainOfThought(
            "question,summary_1->query"
        )
        self.summarize2 = dspy.ChainOfThought(
            "question,context,passages->summary"
        )
        self.final_answer = dspy.ChainOfThought(
            "question,summary_1,summary_2->answer"
        )

        if prompts:
            self.apply_prompts(prompts)

    def apply_prompts(self, prompts: Mapping[str, str]) -> None:
        for prompt_key, instruction in prompts.items():
            attr_name = PROMPT_KEY_TO_ATTR.get(prompt_key)
            if attr_name is None:
                raise KeyError(f"Unsupported prompt key: {prompt_key}")

            if not isinstance(instruction, str) or not instruction.strip():
                raise ValueError(f"Empty instruction for {prompt_key}")

            module = getattr(self, attr_name)
            _set_predictor_instruction(module, instruction.strip())

    def retrieve(self, query: str) -> list[str]:
        query = _clean_text(query)
        if not query:
            raise ValueError("Retriever query is empty.")

        result = search(query, self.retrieval_k)
        return passages_from_search_result(result)

    def run(self, row: Mapping[str, Any]) -> dict[str, Any]:
        sample_id = _clean_text(row.get("sample_id") or row.get("id"))
        question = _clean_text(row.get("question"))
        gold_answer = _clean_text(row.get("answer"))

        if not sample_id:
            raise ValueError("Row has no sample_id or id.")
        if not question:
            raise ValueError(f"Row {sample_id} has an empty question.")

        gold_titles = gold_support_titles(row)

        # Hop 1 is fixed as the original question.
        hop1_query = question
        hop1_docs = self.retrieve(hop1_query)
        hop1_titles = titles_from_passages(hop1_docs)

        summary1_pred = self.summarize1(
            question=question,
            passages=hop1_docs,
        )
        summary_1 = _clean_text(summary1_pred.summary)

        query_pred = self.create_query_hop2(
            question=question,
            summary_1=summary_1,
        )
        hop2_query = _clean_text(query_pred.query)

        hop2_docs = self.retrieve(hop2_query)
        hop2_titles = titles_from_passages(hop2_docs)

        summary2_pred = self.summarize2(
            question=question,
            context=hop1_docs,
            passages=hop2_docs,
        )
        summary_2 = _clean_text(summary2_pred.summary)

        answer_pred = self.final_answer(
            question=question,
            summary_1=summary_1,
            summary_2=summary_2,
        )
        pred_answer = _clean_text(answer_pred.answer)

        retrieval_metrics = compute_retrieval_metrics(
            gold_titles=gold_titles,
            hop1_titles=hop1_titles,
            hop2_titles=hop2_titles,
        )

        return {
            "sample_id": sample_id,
            "split": row.get("split"),
            "split_index": row.get("split_index"),
            "question": question,
            "gold_answer": gold_answer,
            "gold_support_titles": gold_titles,
            "hop1_query": hop1_query,
            "hop1_titles": hop1_titles,
            "hop1_docs": hop1_docs,
            "summary_1": summary_1,
            "hop2_query": hop2_query,
            "hop2_titles": hop2_titles,
            "hop2_docs": hop2_docs,
            "summary_2": summary_2,
            "pred_answer": pred_answer,
            "score": exact_match(pred_answer, gold_answer),
            **retrieval_metrics,
        }


    def run_from_hop2_query(
        self,
        row: Mapping[str, Any],
        *,
        hop1_docs: Iterable[str],
        summary_1: str,
        hop2_query: str,
        hop1_query: Optional[str] = None,
        hop1_titles: Optional[Iterable[str]] = None,
    ) -> dict[str, Any]:
        """
        Re-run the downstream Hotpot pipeline from an externally supplied
        second-hop query.

        This is used to materialize oracle and midpoint query endpoints:

            supplied hop2 query
            -> BM25 hop2 retrieval
            -> summarize2
            -> final answer
            -> retrieval/downstream metrics
        """

        sample_id = _clean_text(
            row.get("sample_id") or row.get("id")
        )
        question = _clean_text(row.get("question"))
        gold_answer = _clean_text(row.get("answer"))
        summary_1 = _clean_text(summary_1)
        hop2_query = _clean_text(hop2_query)

        if not sample_id:
            raise ValueError("Row has no sample_id or id.")
        if not question:
            raise ValueError(
                f"Row {sample_id} has an empty question."
            )
        if not summary_1:
            raise ValueError(
                f"Row {sample_id} has an empty summary_1."
            )
        if not hop2_query:
            raise ValueError(
                f"Row {sample_id} has an empty hop2 query."
            )

        hop1_docs = passages_from_search_result(list(hop1_docs))

        if hop1_titles is None:
            normalized_hop1_titles = titles_from_passages(
                hop1_docs
            )
        else:
            normalized_hop1_titles = _unique_strings(
                hop1_titles
            )

        normalized_hop1_query = (
            _clean_text(hop1_query)
            if hop1_query is not None
            else question
        )

        gold_titles = gold_support_titles(row)

        hop2_docs = self.retrieve(hop2_query)
        hop2_titles = titles_from_passages(hop2_docs)

        summary2_pred = self.summarize2(
            question=question,
            context=hop1_docs,
            passages=hop2_docs,
        )
        summary_2 = _clean_text(summary2_pred.summary)

        answer_pred = self.final_answer(
            question=question,
            summary_1=summary_1,
            summary_2=summary_2,
        )
        pred_answer = _clean_text(answer_pred.answer)

        retrieval_metrics = compute_retrieval_metrics(
            gold_titles=gold_titles,
            hop1_titles=normalized_hop1_titles,
            hop2_titles=hop2_titles,
        )

        return {
            "sample_id": sample_id,
            "split": row.get("split"),
            "split_index": row.get("split_index"),
            "question": question,
            "gold_answer": gold_answer,
            "gold_support_titles": gold_titles,
            "hop1_query": normalized_hop1_query,
            "hop1_titles": normalized_hop1_titles,
            "hop1_docs": hop1_docs,
            "summary_1": summary_1,
            "hop2_query": hop2_query,
            "hop2_titles": hop2_titles,
            "hop2_docs": hop2_docs,
            "summary_2": summary_2,
            "pred_answer": pred_answer,
            "score": exact_match(
                pred_answer,
                gold_answer,
            ),
            "partial_rerun": True,
            **retrieval_metrics,
        }


def configure_lm(
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    api_base: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Any:
    kwargs: dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if api_base:
        kwargs["api_base"] = api_base
    if api_key:
        kwargs["api_key"] = api_key

    lm = dspy.LM(**kwargs)
    dspy.configure(lm=lm)
    return lm


def atomic_write_json(path: str | Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one method_probe HotpotQA rollout."
    )

    parser.add_argument("--data", required=True)
    parser.add_argument("--index", type=int, default=0)

    parser.add_argument("--model", default="openai/gpt-5-mini")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=16000)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None)

    parser.add_argument(
        "--retriever-dir",
        default=str(DEFAULT_RETRIEVER_DIR),
    )
    parser.add_argument("--retrieval-k", type=int, default=7)
    parser.add_argument("--prompt-json", default=None)
    parser.add_argument("--out", default=None)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    rows = load_jsonl(args.data)

    if args.index < 0 or args.index >= len(rows):
        raise IndexError(
            f"index={args.index} is outside [0, {len(rows) - 1}]"
        )

    configure_lm(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        api_base=args.api_base,
        api_key=args.api_key,
    )

    prompts = (
        load_prompt_snapshot(args.prompt_json)
        if args.prompt_json
        else None
    )

    runtime = HotpotRuntime(
        retrieval_k=args.retrieval_k,
        retriever_dir=args.retriever_dir,
        prompts=prompts,
    )

    result = runtime.run(rows[args.index])

    if args.out:
        atomic_write_json(args.out, result)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Full candidate execution
# ---------------------------------------------------------------------------

CANDIDATE_PREDICTOR_BASES = (
    "summarize1",
    "create_query_hop2",
    "summarize2",
    "final_answer",
)


def _candidate_base_name(name: str) -> str:
    name = str(name).strip()

    if name.endswith(".predict"):
        return name[: -len(".predict")]

    return name


def _unwrap_candidate(
    candidate: Mapping[str, Any],
) -> dict[str, str]:
    if isinstance(
        candidate.get("prompts"),
        Mapping,
    ):
        candidate = candidate["prompts"]
    elif isinstance(
        candidate.get("candidate"),
        Mapping,
    ):
        candidate = candidate["candidate"]

    output: dict[str, str] = {}

    for key, value in candidate.items():
        text = str(value or "").strip()

        if text:
            output[str(key)] = text

    return output


def apply_candidate_prompts(
    program: Any,
    candidate: Mapping[str, Any],
) -> dict[str, str]:
    """
    Apply candidate instructions to a fresh HotpotMultiHop instance.

    Both:
        create_query_hop2
    and:
        create_query_hop2.predict

    are accepted. The actual program predictor names determine application.
    """

    candidate = _unwrap_candidate(candidate)

    candidate_by_base: dict[str, str] = {}

    for key, instruction in candidate.items():
        base_name = _candidate_base_name(key)

        if base_name in candidate_by_base:
            raise ValueError(
                f"Duplicate candidate aliases for {base_name}."
            )

        candidate_by_base[base_name] = instruction

    expected = set(CANDIDATE_PREDICTOR_BASES)
    actual_candidate = set(candidate_by_base)

    missing = expected - actual_candidate
    extra = actual_candidate - expected

    if missing:
        raise ValueError(
            "Candidate is missing predictors: "
            + ", ".join(sorted(missing))
        )

    if extra:
        raise ValueError(
            "Candidate has unknown predictors: "
            + ", ".join(sorted(extra))
        )

    actual_named_predictors = {
        name: predictor
        for name, predictor
        in program.named_predictors()
    }

    actual_by_base = {
        _candidate_base_name(name): (
            name,
            predictor,
        )
        for name, predictor
        in actual_named_predictors.items()
    }

    missing_program = expected - set(actual_by_base)
    if missing_program:
        raise ValueError(
            "Program is missing predictors: "
            + ", ".join(sorted(missing_program))
        )

    applied: dict[str, str] = {}

    for base_name in CANDIDATE_PREDICTOR_BASES:
        actual_name, predictor = (
            actual_by_base[base_name]
        )
        instruction = candidate_by_base[
            base_name
        ]

        signature = getattr(
            predictor,
            "signature",
            None,
        )

        if signature is None:
            raise AttributeError(
                f"Predictor {actual_name} has no signature."
            )

        if hasattr(
            signature,
            "with_instructions",
        ):
            predictor.signature = (
                signature.with_instructions(
                    instruction
                )
            )
        elif hasattr(
            signature,
            "instructions",
        ):
            signature.instructions = instruction
        else:
            raise AttributeError(
                f"Cannot replace instructions for "
                f"{actual_name}."
            )

        applied[actual_name] = instruction

    return applied


def build_seed_prompt_candidate(
    *,
    k: int = 7,
    retriever_dir: str | None = None,
) -> dict[str, str]:
    from examples.hotpotqa.program import (
        HotpotMultiHop,
    )

    program = HotpotMultiHop(
        k=k,
        retriever_dir=retriever_dir,
    )

    return {
        name: predictor.signature.instructions
        for name, predictor
        in program.named_predictors()
    }


def build_candidate_program(
    *,
    candidate: Mapping[str, Any],
    k: int = 7,
    retriever_dir: str | None = None,
):
    from examples.hotpotqa.program import (
        HotpotMultiHop,
    )

    program = HotpotMultiHop(
        k=k,
        retriever_dir=retriever_dir,
    )

    apply_candidate_prompts(
        program,
        candidate,
    )

    return program


def _candidate_normalize_answer(
    value: Any,
) -> str:
    import string

    text = str(value or "").lower()

    text = "".join(
        char
        for char in text
        if char not in set(string.punctuation)
    )
    text = re.sub(
        r"\b(a|an|the)\b",
        " ",
        text,
    )

    return " ".join(text.split())


def _candidate_exact_match(
    prediction: Any,
    gold: Any,
) -> bool:
    if isinstance(gold, list):
        return any(
            _candidate_normalize_answer(prediction)
            == _candidate_normalize_answer(answer)
            for answer in gold
        )

    return (
        _candidate_normalize_answer(prediction)
        == _candidate_normalize_answer(gold)
    )


def _candidate_gold_answer(
    row: Mapping[str, Any],
) -> Any:
    for key in (
        "gold_answer",
        "answer",
        "answers",
    ):
        value = row.get(key)

        if value is not None:
            return value

    return ""


def _candidate_gold_support_titles(
    row: Mapping[str, Any],
) -> list[str]:
    direct = row.get("gold_support_titles")

    if isinstance(direct, list):
        return _unique_strings(direct)

    supporting_facts = (
        row.get("supporting_facts")
        or row.get("supporting_facts_titles")
        or []
    )

    titles: list[str] = []

    if isinstance(supporting_facts, list):
        for item in supporting_facts:
            if isinstance(item, str):
                titles.append(item)
            elif (
                isinstance(item, (list, tuple))
                and item
            ):
                titles.append(str(item[0]))
            elif isinstance(item, Mapping):
                title = (
                    item.get("title")
                    or item.get("page")
                )

                if title:
                    titles.append(str(title))

    return _unique_strings(titles)


def _candidate_norm_title(
    value: Any,
) -> str:
    return " ".join(
        str(value or "").strip().lower().split()
    )


def _candidate_title_subset(
    reference_titles: Sequence[str],
    observed_titles: Sequence[str],
) -> list[str]:
    observed_norm = {
        _candidate_norm_title(title)
        for title in observed_titles
    }

    return [
        title
        for title in reference_titles
        if _candidate_norm_title(title)
        in observed_norm
    ]


def run_program_rollout(
    *,
    program: Any,
    row: Mapping[str, Any],
    candidate_id: str | None = None,
) -> dict[str, Any]:
    question = str(
        row.get("question") or ""
    ).strip()

    if not question:
        raise ValueError(
            "Row has no question."
        )

    sample_id = str(
        row.get("sample_id")
        or row.get("id")
        or ""
    ).strip()

    if not sample_id:
        raise ValueError(
            "Row has no sample_id or id."
        )

    prediction = program(
        question=question
    )

    hop1_docs = list(
        getattr(
            prediction,
            "hop1_docs",
            [],
        )
        or []
    )
    hop2_docs = list(
        getattr(
            prediction,
            "hop2_docs",
            [],
        )
        or []
    )

    hop1_titles = titles_from_passages(
        hop1_docs
    )
    hop2_titles = titles_from_passages(
        hop2_docs
    )

    gold_support_titles = (
        _candidate_gold_support_titles(row)
    )
    gold_answer = _candidate_gold_answer(row)

    hit_hop1 = _candidate_title_subset(
        gold_support_titles,
        hop1_titles,
    )
    hit_hop2 = _candidate_title_subset(
        gold_support_titles,
        hop2_titles,
    )
    hit_total = _candidate_title_subset(
        gold_support_titles,
        [
            *hop1_titles,
            *hop2_titles,
        ],
    )

    missing_after_hop1 = [
        title
        for title in gold_support_titles
        if title not in hit_hop1
    ]

    recovered_missing_titles = (
        _candidate_title_subset(
            missing_after_hop1,
            hop2_titles,
        )
    )

    missing_after_hop2 = [
        title
        for title in gold_support_titles
        if title not in hit_total
    ]

    gold_count = len(
        gold_support_titles
    )
    missing_hop1_count = len(
        missing_after_hop1
    )

    pred_answer = str(
        getattr(
            prediction,
            "answer",
            "",
        )
        or ""
    ).strip()

    score = int(
        _candidate_exact_match(
            pred_answer,
            gold_answer,
        )
    )

    return {
        "sample_id": sample_id,
        "question": question,
        "gold_answer": gold_answer,
        "gold_support_titles": (
            gold_support_titles
        ),
        "pred_answer": pred_answer,
        "score": score,
        "hop1_query": str(
            getattr(
                prediction,
                "hop1_query",
                question,
            )
            or question
        ),
        "hop1_docs": hop1_docs,
        "hop1_titles": hop1_titles,
        "summary_1": str(
            getattr(
                prediction,
                "summary_1",
                "",
            )
            or ""
        ),
        "hop2_query": str(
            getattr(
                prediction,
                "hop2_query",
                "",
            )
            or ""
        ),
        "hop2_docs": hop2_docs,
        "hop2_titles": hop2_titles,
        "summary_2": str(
            getattr(
                prediction,
                "summary_2",
                "",
            )
            or ""
        ),
        "hit_support_titles_hop1": hit_hop1,
        "hit_support_titles_hop2": hit_hop2,
        "hit_support_titles_total": hit_total,
        "missing_after_hop1": (
            missing_after_hop1
        ),
        "recovered_missing_titles": (
            recovered_missing_titles
        ),
        "missing_after_hop2": (
            missing_after_hop2
        ),
        "support_recall_hop1": (
            len(hit_hop1) / gold_count
            if gold_count
            else None
        ),
        "support_recall_hop2_only": (
            len(hit_hop2) / gold_count
            if gold_count
            else None
        ),
        "support_recall_total": (
            len(hit_total) / gold_count
            if gold_count
            else None
        ),
        "missing_recovery_rate": (
            len(recovered_missing_titles)
            / missing_hop1_count
            if missing_hop1_count
            else 1.0
        ),
        "natural_retrieval_failure": bool(
            missing_after_hop2
        ),
        "candidate_id": candidate_id,
    }


def evaluate_candidate_rows(
    *,
    rows: Sequence[Mapping[str, Any]],
    candidate: Mapping[str, Any],
    k: int = 7,
    retriever_dir: str | None = None,
    candidate_id: str | None = None,
) -> dict[str, Any]:
    import hashlib
    import json

    normalized_candidate = _unwrap_candidate(
        candidate
    )

    candidate_hash = hashlib.sha256(
        json.dumps(
            normalized_candidate,
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()

    program = build_candidate_program(
        candidate=normalized_candidate,
        k=k,
        retriever_dir=retriever_dir,
    )

    rollouts: list[dict[str, Any]] = []

    for row in rows:
        rollouts.append(
            run_program_rollout(
                program=program,
                row=row,
                candidate_id=(
                    candidate_id
                    or candidate_hash
                ),
            )
        )

    scores = [
        int(rollout["score"])
        for rollout in rollouts
    ]

    return {
        "candidate_id": (
            candidate_id
            or candidate_hash
        ),
        "candidate_hash": candidate_hash,
        "num_rows": len(rollouts),
        "score_sum": sum(scores),
        "score": (
            sum(scores) / len(scores)
            if scores
            else 0.0
        ),
        "rollouts": rollouts,
    }
