# /home/jinwoo/gepa-official/examples/hotpotqa/metric.py
import re
from typing import Any

import dspy


def _get(obj: Any, key: str, default=None):
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]
    except Exception:
        return default


def _normalize_answer(text: str) -> str:
    text = str(text).lower().strip()
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = " ".join(text.split())
    return text


def answer_match_fn(prediction, answers, frac: float = 1.0) -> bool:
    """
    Match prediction against one or more gold answers.
    Uses DSPy EM/F1 if available; falls back to normalized exact match.
    """
    if isinstance(answers, str):
        answers = [answers]

    try:
        from dspy.dsp.utils import EM, F1

        if frac >= 1.0:
            return bool(EM(prediction, answers))
        return bool(F1(prediction, answers) >= frac)
    except Exception:
        pred_norm = _normalize_answer(prediction)
        gold_norms = [_normalize_answer(a) for a in answers]
        if frac >= 1.0:
            return pred_norm in gold_norms
        return pred_norm in gold_norms


def answer_exact_match(example, pred, trace=None, frac: float = 1.0) -> float:
    gold = _get(example, "answer")
    pred_answer = _get(pred, "answer", "")

    if isinstance(gold, list):
        matched = answer_match_fn(pred_answer, gold, frac=frac)
    else:
        matched = answer_match_fn(pred_answer, [gold], frac=frac)

    return float(matched)


def get_textual_context(example) -> str:
    """
    Build a compact gold-support context from HotpotQA fields.

    Expected fields:
      example.context["title"]
      example.context["sentences"]
      example.supporting_facts["title"]
      example.supporting_facts["sent_id"]
    """
    context = _get(example, "context", {}) or {}
    supporting_facts = _get(example, "supporting_facts", {}) or {}

    titles = context.get("title", [])
    sentences = context.get("sentences", [])
    title_to_sentences = {
        title: sents for title, sents in zip(titles, sentences)
    }

    support_titles = supporting_facts.get("title", [])
    support_sent_ids = supporting_facts.get("sent_id", [])

    chunks = []
    for title, sent_id in zip(support_titles, support_sent_ids):
        sents = title_to_sentences.get(title, [])
        if isinstance(sent_id, int) and 0 <= sent_id < len(sents):
            chunks.append(f"{title} | {sents[sent_id]}")
        elif title in title_to_sentences:
            chunks.append(f"{title} | {''.join(title_to_sentences[title])}")

    if chunks:
        return "\n".join(chunks)

    # Fallback: use all documents whose titles appear in supporting facts.
    useful_titles = set(support_titles)
    for title in useful_titles:
        if title in title_to_sentences:
            chunks.append(f"{title} | {''.join(title_to_sentences[title])}")

    return "\n".join(chunks)


def answer_exact_match_with_feedback(example, pred, trace=None, frac: float = 1.0):
    score = answer_exact_match(example, pred, trace=trace, frac=frac)
    pred_answer = _get(pred, "answer", "")
    gold_answer = _get(example, "answer")

    textual_context = ""
    pred_feedback = _get(pred, "feedback_text", "")
    if pred_feedback:
        textual_context += str(pred_feedback) + "\n\n"

    textual_context += get_textual_context(example)

    if score:
        feedback = (
            f"The provided answer, '{pred_answer}', is correct. "
            f"Here is supporting context behind the answer:\n{textual_context}"
        )
    else:
        feedback = (
            f"The provided answer, '{pred_answer}', is incorrect. "
            f"The correct answer is: {gold_answer}. "
            f"Here is context that supports the correct answer:\n{textual_context}"
        )

    return dspy.Prediction(score=score, feedback=feedback)