import os
import re
import random
from types import SimpleNamespace

import dspy
from datasets import load_dataset
from openai import OpenAI


MODEL_NAME = os.environ.get("AIME_MODEL", "Qwen/Qwen3-8B")
API_BASE = os.environ.get("AIME_API_BASE", "http://localhost:8889/v1")
API_KEY = os.environ.get("AIME_API_KEY", "dummy")
MAX_TOKENS = int(os.environ.get("AIME_MAX_TOKENS", "4096"))

client = OpenAI(base_url=API_BASE, api_key=API_KEY)


def extract_answer(text: str) -> str:
    text = text or ""

    if "</think>" in text:
        text = text.split("</think>")[-1]

    boxed = re.findall(r"\\boxed\{(-?\d+)\}", text)
    if boxed:
        return boxed[-1]

    answer_patterns = [
        r"(?:final answer|answer)\s*(?:is|:)?\s*(-?\d+)",
        r"therefore[, ]+\s*(-?\d+)",
    ]
    for pat in answer_patterns:
        matches = re.findall(pat, text, flags=re.IGNORECASE)
        if matches:
            return matches[-1]

    nums = re.findall(r"-?\d+", text)
    return nums[-1] if nums else text.strip()


def run_llm(example, prompt: str):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": example.input},
    ]

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.7,
        max_tokens=MAX_TOKENS,
    )

    msg = resp.choices[0].message
    raw_output = msg.content or ""
    reasoning = getattr(msg, "reasoning_content", "") or ""

    return SimpleNamespace(
        answer=extract_answer(raw_output),
        raw_output=raw_output,
        reasoning=reasoning,
    )


def math_metric(example, prediction):
    correct_answer, written_solution = int(example.answer), getattr(example, "solution", "")
    solution_suffix = (
        f" Here's the full step-by-step solution:\n{written_solution}\n\n"
        "Think about what takeaways you can learn from this solution to improve your future answers and approach to similar problems"
        if written_solution
        else ""
    )

    pred_answer = getattr(prediction, "answer", "")

    try:
        llm_answer = int(str(pred_answer).strip())
    except (ValueError, TypeError):
        feedback_text = (
            f"The parsed final answer must be a valid integer. "
            f"The parsed answer was '{pred_answer}'. "
            f"The correct answer is '{correct_answer}'.{solution_suffix}"
        )
        return 0.0, feedback_text

    score = float(correct_answer == llm_answer)
    status = "correct" if score == 1.0 else "incorrect"
    feedback_text = f"Your answer is {status}. The correct answer is '{correct_answer}'.{solution_suffix}"
    return score, feedback_text


def load_math_dataset():
    train_split = []
    test_split = []

    train_load_dataset = load_dataset("AI-MO/aimo-validation-aime", "default", split="train")
    for item in train_load_dataset:
        train_split.append(
            dspy.Example(
                input=item["problem"],
                solution=item["solution"],
                answer=item["answer"],
            ).with_inputs("input")
        )

    random.Random(0).shuffle(train_split)

    test_load_dataset = load_dataset("MathArena/aime_2025", "default", split="train")
    for item in test_load_dataset:
        test_split.append(
            dspy.Example(
                input=item["problem"],
                answer=item["answer"],
            ).with_inputs("input")
        )

    train_size = len(train_split)
    trainset = train_split[: train_size // 2]
    valset = train_split[train_size // 2 :]
    testset = test_split

    return trainset, valset, testset


def evaluate_on_dataset(prompt, dataset):
    scores = []

    for i, example in enumerate(dataset):
        try:
            prediction = run_llm(example, prompt)
            score = math_metric(example, prediction)[0]
            print(f"[eval] {i + 1}/{len(dataset)} pred={prediction.answer} score={score}")
        except Exception as e:
            print(f"[eval error] example={i} error={type(e).__name__}: {e}")
            score = 0.0

        scores.append(score)
        running = sum(scores) / len(scores)
        print(f"[eval running] {i + 1}/{len(dataset)} acc={running:.4f}")

    return sum(scores) / len(scores) if scores else 0.0