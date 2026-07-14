# /home/jinwoo/gepa-official/src/ours/analyze_attribute.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import traceback
from collections import Counter
from datetime import datetime
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv
from gepa.proposer.reflective_mutation.base import LanguageModel, Signature
from tqdm.auto import tqdm

from ours.lm import run_signature
from ours.prompts import (
    AGENTGRAD_PROMPT_SET,
    BASELINE_PROMPT_SET,
    validate_candidate,
)
from ours.runtime import OursRuntime
from ours.utils.destination import build_agent_destination
from ours.utils.materialize import (
    compute_local_metric,
    evaluate_endpoint_solvability,
    materialize_agent_state,
    materialize_destination,
    state_from_trace,
)
from ours.utils.midpoint import generate_midpoint, select_largest_edge

from examples.ours.adapter import HotpotAdapter
from examples.ours.metric import answer_exact_match
from examples.ours.program import HotpotMultiHop
from examples.ours.retriever import DEFAULT_RETRIEVER_DIR, set_retriever_dir


AGENT_ORDER = (
    "final",
    "summary2",
    "query",
    "summary1",
)

DEFAULT_AGENT_MAX_ITERS = {
    "final": 0,
    "summary2": 0,
    "query": 1,
    "summary1": 1,
}

AGENT_TO_PROMPT_KEY = {
    "summary1": "summarize1.predict",
    "query": "create_query_hop2.predict",
    "summary2": "summarize2.predict",
    "final": "final_answer.predict",
}

AGENT_ROLES = {
    "summary1": (
        "Summarize first-hop evidence and expose the bridge entity, "
        "missing fact, or retrieval direction needed for the next hop."
    ),
    "query": (
        "Produce one compact second-hop retrieval query targeting the "
        "missing bridge or supporting evidence."
    ),
    "summary2": (
        "Integrate second-hop evidence with first-hop context and retain "
        "the facts needed to answer the question."
    ),
    "final": (
        "Follow the base prompt's native final-answer output contract. "
        "Ensure the [[ ## answer ## ]] block contains only the minimal "
        "answer string supported by the visible summaries."
    ),
}

DEFAULT_EVAL_ROWS = (
    "examples/ours/runs/"
    "gpt5mini_agentgrad_best_test150/eval_rows.json"
)
DEFAULT_RUN_DIR = (
    "examples/ours/runs/"
    "gpt5mini_agentgrad_best_test150/backward_attribution_v2"
)
DEFAULT_ENV_FILE = "/home/jinwoo/gepa-official/.env"

MAX_STATE_DOCS = 7
MAX_STATE_DOC_CHARS = 500
MAX_VISIBLE_TEXT_CHARS = 12000

SCRIPT_VERSION = "2026-07-14-v4-candidate-log-input"


def _log(enabled: bool, message: str) -> None:
    """Emit a timestamped progress line without corrupting tqdm output."""
    if not enabled:
        return
    stamp = datetime.now().strftime("%H:%M:%S")
    tqdm.write(f"[{stamp}] {message}")


def _preview(value: Any, limit: int = 180) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[:limit] + " ..."


def _metric_preview(metric: Mapping[str, Any] | None) -> dict[str, Any]:
    metric = metric or {}
    keep = (
        "name",
        "value",
        "missing_recovery_rate",
        "hit_titles",
        "recovered_missing_titles",
        "score",
    )
    return {key: metric.get(key) for key in keep if key in metric}


# ---------------------------------------------------------------------------
# JSON / filesystem helpers
# ---------------------------------------------------------------------------


def _json_dumps(value: Any, *, indent: int | None = 2) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=indent,
        default=str,
        sort_keys=False,
    )


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def read_rows_file(path: str | Path) -> list[dict[str, Any]]:
    """Read either a JSON list or a JSONL row log."""
    path = Path(path)
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        value = [
            json.loads(line)
            for line in text.splitlines()
            if line.strip()
        ]

    if isinstance(value, Mapping):
        rows = value.get("rows")
        value = rows if isinstance(rows, list) else [value]

    if not isinstance(value, list):
        raise TypeError(
            f"{path} must contain a JSON list or JSONL rows."
        )
    if not all(isinstance(row, Mapping) for row in value):
        raise TypeError(f"{path} contains a non-object row.")

    return [dict(row) for row in value]


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_candidate_file(
    path: str | Path,
) -> tuple[dict[str, str], str]:
    """Load update_prompt candidate.json or a direct prompt mapping."""
    path = Path(path)
    value = read_json(path)
    if not isinstance(value, Mapping):
        raise TypeError(
            f"{path} must contain a JSON object."
        )

    candidate_value: Any = value
    for key in ("candidate", "prompts"):
        nested = value.get(key)
        if isinstance(nested, Mapping):
            candidate_value = nested
            break

    required = set(AGENT_TO_PROMPT_KEY.values())
    if not isinstance(candidate_value, Mapping):
        raise TypeError(
            f"{path} does not contain a prompt candidate mapping."
        )

    candidate = {
        str(key): str(prompt)
        for key, prompt in candidate_value.items()
        if str(key) in required
    }
    missing = required - set(candidate)
    if missing:
        raise ValueError(
            f"{path} is missing prompt keys: {sorted(missing)}"
        )

    candidate_name = str(
        value.get("candidate_name")
        or value.get("condition")
        or path.stem
    )
    return candidate, candidate_name


def normalize_eval_rows(
    *,
    eval_rows_path: str | Path,
    source_eval_rows_path: str | Path | None,
    expected_candidate_hash: str | None,
) -> list[dict[str, Any]]:
    """
    Accept legacy flat eval rows or update_prompt eval_rows.jsonl.

    For update_prompt logs, merge each nested trace over the corresponding
    source eval row so gold/context fields remain available.
    """
    raw_rows = read_rows_file(eval_rows_path)
    source_rows = (
        read_rows_file(source_eval_rows_path)
        if source_eval_rows_path
        else []
    )

    is_rollout_log = any(
        isinstance(row.get("trace"), Mapping)
        or "eval_position" in row
        for row in raw_rows
    )

    if not is_rollout_log:
        normalized = [dict(row) for row in raw_rows]
        row_hashes = {
            str(row.get("candidate_hash"))
            for row in normalized
            if row.get("candidate_hash")
        }
        if (
            expected_candidate_hash is not None
            and row_hashes
            and row_hashes != {expected_candidate_hash}
        ):
            raise ValueError(
                "Flat eval rows candidate_hash does not match "
                "--candidate-path."
            )

        if expected_candidate_hash is not None:
            for row in normalized:
                row.setdefault(
                    "candidate_hash",
                    expected_candidate_hash,
                )

        return normalized

    successful = [
        row
        for row in raw_rows
        if not row.get("error")
    ]

    if expected_candidate_hash is not None:
        logged_hashes = {
            str(row.get("candidate_hash"))
            for row in successful
            if row.get("candidate_hash")
        }
        if (
            logged_hashes
            and expected_candidate_hash not in logged_hashes
        ):
            raise ValueError(
                "No successful eval row matches the candidate loaded "
                "from --candidate-path."
            )

        successful = [
            row
            for row in successful
            if (
                not row.get("candidate_hash")
                or str(row.get("candidate_hash"))
                == expected_candidate_hash
            )
        ]

    latest_by_position: dict[int, dict[str, Any]] = {}
    for ordinal, row in enumerate(successful):
        position = int(
            row.get("eval_position", ordinal)
        )
        latest_by_position[position] = dict(row)

    normalized = []
    for position in sorted(latest_by_position):
        logged = latest_by_position[position]
        source = (
            dict(source_rows[position])
            if position < len(source_rows)
            else {}
        )

        trace = logged.get("trace")
        trace = (
            dict(trace)
            if isinstance(trace, Mapping)
            else {}
        )

        row = {
            **source,
            **trace,
        }
        row["index"] = logged.get(
            "row_index",
            row.get("index", position),
        )
        row["sample_id"] = logged.get(
            "sample_id",
            row.get("sample_id"),
        )
        row["score"] = float(
            logged.get(
                "score",
                row.get("score") or 0.0,
            )
        )
        row["candidate_hash"] = (
            logged.get("candidate_hash")
            or expected_candidate_hash
        )
        row["eval_position"] = position
        row["original_baseline_score"] = logged.get(
            "original_baseline_score"
        )

        normalized.append(row)

    required = (
        "question",
        "gold_answer",
        "summary_1",
        "hop2_query",
        "summary_2",
        "answer",
    )
    missing_rows = [
        {
            "position": int(
                row.get("eval_position", index)
            ),
            "missing": [
                key
                for key in required
                if row.get(key) is None
            ],
        }
        for index, row in enumerate(normalized)
        if any(
            row.get(key) is None
            for key in required
        )
    ]

    if missing_rows:
        raise ValueError(
            "Normalized rollout rows are missing attribution fields. "
            "Pass the original flat rows with --source-eval-rows. "
            f"Examples: {missing_rows[:5]}"
        )

    return normalized


def write_json(path: str | Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _json_dumps(value, indent=2),
        encoding="utf-8",
    )


def append_jsonl(path: str | Path, row: Mapping[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(_json_dumps(dict(row), indent=None) + "\n")


def _extract_json_object(text: str) -> dict[str, Any]:
    text = str(text or "").strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except Exception:
        pass

    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value

    raise ValueError(
        "Could not extract a JSON object from LM output: "
        f"{text[:800]}"
    )


def _require_text(value: Any, *, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} cannot be empty.")
    return text


# ---------------------------------------------------------------------------
# Prompt / state views
# ---------------------------------------------------------------------------


def _truncate(value: Any, limit: int) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[:limit] + " ...[truncated]"


def _doc_snippets(docs: Any) -> list[str]:
    snippets = []
    for doc in list(docs or [])[:MAX_STATE_DOCS]:
        snippets.append(
            _truncate(" ".join(str(doc).split()), MAX_STATE_DOC_CHARS)
        )
    return snippets


def _state_output(agent: str, state: Mapping[str, Any]) -> Any:
    output = state.get("output")
    if agent == "query":
        if isinstance(output, Mapping):
            query = output.get("query")
        else:
            query = output
        if query is None:
            query = state.get("hop2_query")
        return {"query": str(query or "").strip()}

    if output is not None:
        return output
    if agent == "summary1":
        return state.get("summary_1")
    if agent == "summary2":
        return state.get("summary_2")
    if agent == "final":
        return state.get("answer")
    raise ValueError(f"Unknown agent {agent!r}.")


def compact_state(agent: str, state: Mapping[str, Any]) -> dict[str, Any]:
    """Compact state used only for guarded edge-to-delta inversion."""
    common = {
        "state_kind": state.get("state_kind"),
        "state_origin": state.get("state_origin"),
        "output": _state_output(agent, state),
        "score": state.get("score"),
    }

    if agent == "summary1":
        return {
            **common,
            "generated_query": state.get("hop2_query"),
            "retrieved_titles": list(state.get("hop2_titles") or []),
            "summary_2": _truncate(state.get("summary_2"), 1200),
            "answer": state.get("answer"),
            "missing_recovery_rate": state.get("missing_recovery_rate"),
            "recovered_missing_titles": list(
                state.get("recovered_missing_titles_hop2") or []
            ),
            "missing_titles_after_hop2": list(
                state.get("missing_titles_after_hop2") or []
            ),
        }

    if agent == "query":
        return {
            **common,
            "retrieved_titles": list(state.get("hop2_titles") or []),
            "retrieved_doc_snippets": _doc_snippets(state.get("hop2_docs")),
            "summary_2": _truncate(state.get("summary_2"), 1200),
            "answer": state.get("answer"),
            "missing_recovery_rate": state.get("missing_recovery_rate"),
            "recovered_missing_titles": list(
                state.get("recovered_missing_titles_hop2") or []
            ),
            "missing_titles_after_hop2": list(
                state.get("missing_titles_after_hop2") or []
            ),
        }

    if agent == "summary2":
        return {
            **common,
            "answer": state.get("answer"),
        }

    return common


def build_agent_inputs(agent: str, row: Mapping[str, Any]) -> dict[str, Any]:
    """Return only inputs visible at the selected agent boundary."""
    if agent == "summary1":
        return {
            "question": row.get("question"),
            "passages": list(row.get("hop1_docs") or []),
            "current_output": row.get("summary_1"),
        }
    if agent == "query":
        return {
            "question": row.get("question"),
            "summary_1": row.get("summary_1"),
            "current_output": {"query": row.get("hop2_query")},
        }
    if agent == "summary2":
        return {
            "question": row.get("question"),
            "context": row.get("summary_1"),
            "passages": list(row.get("hop2_docs") or []),
            "current_output": row.get("summary_2"),
        }
    if agent == "final":
        return {
            "question": row.get("question"),
            "summary_1": row.get("summary_1"),
            "summary_2": row.get("summary_2"),
            "current_output": row.get("answer"),
        }
    raise ValueError(f"Unknown agent {agent!r}.")


def build_task_context(agent: str, row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "question": row.get("question"),
        "agent": agent,
        "agent_role": AGENT_ROLES[agent],
    }

def _extract_dspy_field(text: str, field: str) -> str | None:
    pattern = re.compile(
        rf"\[\[\s*##\s*{re.escape(field)}\s*##\s*\]\]"
        rf"\s*(.*?)"
        rf"(?=\[\[\s*##|\Z)",
        flags=re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def normalize_direct_output(agent: str, output: Any) -> str | dict[str, str]:
    if agent == "query":
        if isinstance(output, Mapping):
            output = output.get("query", output)

        text = str(output or "").strip()
        parsed = _extract_dspy_field(text, "query")
        return {
            "query": _require_text(
                parsed or text,
                field="query output",
            )
        }

    if isinstance(output, Mapping):
        preferred_key = "answer" if agent == "final" else "summary"
        for key in (preferred_key, "output", "text", "value"):
            value = output.get(key)
            if str(value or "").strip():
                output = value
                break

    text = _require_text(
        output,
        field=f"{agent} output",
    )

    if agent == "final":
        parsed = _extract_dspy_field(text, "answer")
        return _require_text(
            parsed or text,
            field="final answer",
        )

    if agent in {"summary1", "summary2"}:
        parsed = _extract_dspy_field(text, "summary")
        return _require_text(
            parsed or text,
            field=f"{agent} summary",
        )

    raise ValueError(f"Unknown agent: {agent}")

def _validate_agent_output(agent: str, output: Any) -> str | dict[str, str]:
    if agent == "query":
        if isinstance(output, Mapping):
            query = output.get("query")
        else:
            query = output
        return {"query": _require_text(query, field="query output")}

    if isinstance(output, Mapping):
        for key in ("answer", "summary", "text", "value"):
            if key in output and str(output[key] or "").strip():
                output = output[key]
                break
    return _require_text(output, field=f"{agent} output")


def make_intermediate_state(
    *,
    agent: str,
    mid_output: Any,
    rationale: str,
    bisection_round: int,
) -> dict[str, Any]:
    return {
        "agent": agent,
        "output": _validate_agent_output(agent, mid_output),
        "materialized": False,
        "forced_agent": None,
        "state_kind": "intermediate",
        "state_origin": "generated_midpoint",
        "midpoint_rationale": str(rationale or "").strip(),
        "bisection_round": int(bisection_round),
    }


# ---------------------------------------------------------------------------
# Guarded edge -> delta-p inversion
# ---------------------------------------------------------------------------


DELTA_P_FIELDS = (
    "trigger",
    "preserve_rule",
    "change_rule",
    "drop_or_avoid_rule",
    "output_contract",
    "why_local_transition",
)


class GuardedEdgeDeltaPSignature(Signature):
    input_keys = [
        "agent",
        "agent_role",
        "task_context",
        "visible_agent_inputs",
        "current_prompt",
        "edge_index",
        "source_state",
        "target_state",
        "repair_feedback",
    ]
    output_keys = [
        "delta_p",
        "rationale",
    ]

    @classmethod
    def prompt_renderer(cls, input_dict: Mapping[str, Any]) -> str:
        return f"""
You are deriving one LOCAL PROMPT DELTA Δp_i for an agent in a fixed
multi-agent HotpotQA pipeline.

The source and target states describe one local functional transition.
Produce a prompt-update rule that helps the unchanged base prompt move
through this edge. The delta will later be placed in an ORDERED list with
all other edge deltas and executed directly as supplemental context.

Return JSON only:
{{
  "delta_p": {{
    "trigger": "...",
    "preserve_rule": "...",
    "change_rule": "...",
    "drop_or_avoid_rule": "...",
    "output_contract": "...",
    "why_local_transition": "..."
  }},
  "rationale": "..."
}}

Strict anti-cheating rules:
- Δp_i is a PROMPT EDIT / behavior rule, never the target output.
- Do not output a candidate answer, summary, or query as Δp_i.
- Do not instruct the agent to copy the target state.
- Do not copy the gold answer, hidden support title, target-only entity,
  or a long literal span that appears only in the target state.
- Sample-specific anchors may appear only when they already occur in the
  visible agent inputs below.
- Do not mention gold labels, oracle labels, evaluation metrics, missing
  support, target state, source state, or endpoint reconstruction.
- Preserve the agent's original input/output interface.
- Express the smallest coherent behavioral change for this edge.
- Preserve useful behavior and evidence already present at the source.
- Each edge is inverted independently from the same current prompt.

Agent:
{input_dict["agent"]}

Agent role:
{input_dict["agent_role"]}

Task context:
{_json_dumps(input_dict["task_context"])}

Visible agent inputs:
{_truncate(_json_dumps(input_dict["visible_agent_inputs"]), MAX_VISIBLE_TEXT_CHARS)}

Current/base prompt p:
{input_dict["current_prompt"]}

Edge index:
{input_dict["edge_index"]}

Source state:
{_json_dumps(input_dict["source_state"])}

Target state:
{_json_dumps(input_dict["target_state"])}

Repair feedback from a rejected previous attempt:
{_json_dumps(input_dict.get("repair_feedback") or {})}
""".strip()

    @classmethod
    def output_extractor(cls, lm_out: str) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        delta_p = obj.get("delta_p")
        if not isinstance(delta_p, Mapping):
            raise TypeError("delta_p must be a JSON object.")

        normalized = {
            key: str(delta_p.get(key) or "").strip()
            for key in DELTA_P_FIELDS
        }
        if not any(normalized.values()):
            raise ValueError("delta_p cannot be empty.")

        return {
            "delta_p": normalized,
            "rationale": str(obj.get("rationale") or "").strip(),
        }


def _normalize_for_leak_check(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _candidate_secret_literals(
    *,
    row: Mapping[str, Any],
    destination: Mapping[str, Any],
    visible_inputs: Mapping[str, Any],
) -> list[str]:
    visible = _normalize_for_leak_check(_json_dumps(visible_inputs))
    candidates: list[str] = []

    gold_answer = row.get("gold_answer")
    if gold_answer is not None:
        if isinstance(gold_answer, (list, tuple)):
            candidates.extend(str(x) for x in gold_answer)
        else:
            candidates.append(str(gold_answer))

    candidates.extend(str(x) for x in destination.get("target_titles", []) or [])

    output = destination.get("output")
    if isinstance(output, Mapping):
        candidates.extend(str(v) for v in output.values())
    elif output is not None:
        candidates.append(str(output))

    hidden = []
    seen = set()
    for literal in candidates:
        normalized = _normalize_for_leak_check(literal)
        if len(normalized) < 4 or normalized in seen:
            continue
        seen.add(normalized)
        if normalized not in visible:
            hidden.append(literal)
    return hidden


def detect_delta_leaks(
    *,
    delta_p: Mapping[str, Any],
    hidden_literals: Sequence[str],
) -> list[str]:
    delta_text = _normalize_for_leak_check(_json_dumps(delta_p))
    leaks = []
    for literal in hidden_literals:
        normalized = _normalize_for_leak_check(literal)
        if normalized and normalized in delta_text:
            leaks.append(str(literal))
    return leaks


def generate_guarded_delta_p(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent: str,
    current_prompt: str,
    task_context: Mapping[str, Any],
    visible_inputs: Mapping[str, Any],
    source_state: Mapping[str, Any],
    target_state: Mapping[str, Any],
    edge_index: int,
    hidden_literals: Sequence[str],
    metadata: Mapping[str, Any],
    max_attempts: int,
    verbose: bool = False,
) -> dict[str, Any]:
    repair_feedback: dict[str, Any] = {}
    last_error: Exception | None = None

    sample_index = metadata.get("sample_index", "?")
    round_index = metadata.get("bisection_round", "?")

    for attempt in range(max_attempts):
        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}][round={round_index}] "
            f"delta-p edge={edge_index} attempt={attempt + 1}/{max_attempts} start",
        )
        try:
            parsed, prompt, raw, cache_hit = run_signature(
                runtime=runtime,
                operation=(
                    "backward_attribution.edge_delta_p."
                    f"attempt_{attempt}"
                ),
                lm=lm,
                signature_cls=GuardedEdgeDeltaPSignature,
                input_dict={
                    "agent": agent,
                    "agent_role": AGENT_ROLES[agent],
                    "task_context": dict(task_context),
                    "visible_agent_inputs": dict(visible_inputs),
                    "current_prompt": current_prompt,
                    "edge_index": int(edge_index),
                    "source_state": compact_state(agent, source_state),
                    "target_state": compact_state(agent, target_state),
                    "repair_feedback": repair_feedback,
                },
                lm_config=lm_config,
                metadata={
                    **dict(metadata),
                    "agent": agent,
                    "edge_index": int(edge_index),
                    "delta_attempt": attempt,
                },
                return_cache_hit=True,
            )

            leaks = detect_delta_leaks(
                delta_p=parsed["delta_p"],
                hidden_literals=hidden_literals,
            )
            if leaks:
                _log(
                    verbose,
                    f"[sample={sample_index}][agent={agent}][round={round_index}] "
                    f"delta-p edge={edge_index} rejected: literal leakage {leaks}",
                )
                repair_feedback = {
                    "rejected": True,
                    "reason": "literal leakage",
                    "leaked_literals": leaks,
                    "instruction": (
                        "Rewrite the delta as abstract behavior and remove "
                        "all listed literals."
                    ),
                }
                last_error = ValueError(
                    f"Delta-p leaked hidden literals: {leaks}"
                )
                continue

            _log(
                verbose,
                f"[sample={sample_index}][agent={agent}][round={round_index}] "
                f"delta-p edge={edge_index} done cache_hit={cache_hit} "
                f"change={_preview(parsed['delta_p'].get('change_rule'))}",
            )
            return {
                "edge_index": int(edge_index),
                "source_output": _state_output(agent, source_state),
                "target_output": _state_output(agent, target_state),
                "delta_p": parsed["delta_p"],
                "rationale": parsed["rationale"],
                "leak_check": {
                    "passed": True,
                    "hidden_literal_count": len(hidden_literals),
                },
                "lm_trace": {
                    "rendered_prompt": prompt,
                    "raw_output": raw,
                    "cache_hit": cache_hit,
                    "attempt": attempt,
                },
            }
        except Exception as exc:
            last_error = exc
            _log(
                verbose,
                f"[sample={sample_index}][agent={agent}][round={round_index}] "
                f"delta-p edge={edge_index} attempt failed: "
                f"{type(exc).__name__}: {exc}",
            )
            repair_feedback = {
                "rejected": True,
                "reason": type(exc).__name__,
                "message": str(exc),
                "instruction": (
                    "Return strict JSON and express only an abstract local "
                    "prompt behavior change."
                ),
            }

    assert last_error is not None
    raise RuntimeError(
        f"Failed to generate guarded delta-p after {max_attempts} attempts: "
        f"{last_error}"
    ) from last_error


def build_delta_p_trace(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent: str,
    current_prompt: str,
    task_context: Mapping[str, Any],
    visible_inputs: Mapping[str, Any],
    states: Sequence[Mapping[str, Any]],
    destination: Mapping[str, Any],
    row: Mapping[str, Any],
    metadata: Mapping[str, Any],
    max_attempts: int,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    hidden_literals = _candidate_secret_literals(
        row=row,
        destination=destination,
        visible_inputs=visible_inputs,
    )

    sample_index = metadata.get("sample_index", "?")
    round_index = metadata.get("bisection_round", "?")
    n_edges = len(states) - 1
    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}][round={round_index}] "
        f"building ordered delta-p trace for {n_edges} edge(s)",
    )

    trace = []
    for edge_index in range(n_edges):
        trace.append(
            generate_guarded_delta_p(
                runtime=runtime,
                lm=lm,
                lm_config=lm_config,
                agent=agent,
                current_prompt=current_prompt,
                task_context=task_context,
                visible_inputs=visible_inputs,
                source_state=states[edge_index],
                target_state=states[edge_index + 1],
                edge_index=edge_index,
                hidden_literals=hidden_literals,
                metadata=metadata,
                max_attempts=max_attempts,
                verbose=verbose,
            )
        )

    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}][round={round_index}] "
        f"ordered delta-p trace complete ({len(trace)} edge(s))",
    )
    return trace


# ---------------------------------------------------------------------------
# Direct base-prompt + ordered-delta execution
# ---------------------------------------------------------------------------


OUTPUT_REQUIREMENTS = {
    "summary1": (
        "Return one summary_1 string. Summarize the visible hop1 passages "
        "and expose a useful second-hop retrieval direction."
    ),
    "query": (
        'Return exactly {"query": "<one compact second-hop BM25 query>"}. '
        "Do not return explanations or multiple queries."
    ),
    "summary2": (
        "Return one summary_2 string integrating only the visible summary_1 "
        "and hop2 passages."
    ),
    "final": (
        "Return only the minimal final answer string derivable from the "
        "visible summaries."
    ),
}


class DirectDeltaExecutionSignature(Signature):
    input_keys = [
        "agent",
        "agent_role",
        "base_prompt",
        "ordered_delta_p_trace",
        "visible_agent_inputs",
        "output_requirement",
    ]
    output_keys = [
        "output",
        "rationale",
    ]

    @classmethod
    def prompt_renderer(cls, input_dict: Mapping[str, Any]) -> str:
        return f"""
You are executing one agent in a fixed HotpotQA multi-agent pipeline.

Use the unchanged base instruction p together with the complete ORDERED
list of local prompt deltas. The deltas are supplemental behavior guidance
for this sample; they are not outputs and must not be quoted mechanically.

This is a direct delta-context execution probe:
- Do not rewrite, aggregate, or synthesize a new prompt p'.
- Apply every delta in order to the visible inputs.
- Judge success only by producing the endpoint agent output.
- Do not attempt to reproduce or discuss intermediate states.
- Do not infer hidden information from the existence of the deltas.
- Use only the visible agent inputs as factual evidence.
- Never output gold/oracle labels, evaluation metrics, or hidden support.
- Preserve the agent's normal input/output contract.

Agent:
{input_dict["agent"]}

Agent role:
{input_dict["agent_role"]}

Base prompt p:
{input_dict["base_prompt"]}

Ordered local prompt deltas:
{_json_dumps(input_dict["ordered_delta_p_trace"])}

Visible agent inputs:
{_truncate(_json_dumps(input_dict["visible_agent_inputs"]), MAX_VISIBLE_TEXT_CHARS)}

Required parsed output:
{input_dict["output_requirement"]}

Return strict JSON only:
{{
  "output": <the parsed agent output in the required form>,
  "rationale": "brief statement of how the ordered rules were applied; do not reveal hidden reasoning"
}}
""".strip()

    @classmethod
    def output_extractor(cls, lm_out: str) -> dict[str, Any]:
        obj = _extract_json_object(lm_out)
        if "output" not in obj:
            raise ValueError("Direct execution output is missing `output`.")
        return {
            "output": obj["output"],
            "rationale": str(obj.get("rationale") or "").strip(),
        }


def execute_direct_delta_context(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent: str,
    base_prompt: str,
    delta_p_trace: Sequence[Mapping[str, Any]],
    visible_inputs: Mapping[str, Any],
    metadata: Mapping[str, Any],
    verbose: bool = False,
) -> dict[str, Any]:
    delta_listing = [
        {
            "edge_index": int(item["edge_index"]),
            "delta_p": dict(item["delta_p"]),
        }
        for item in delta_p_trace
    ]

    sample_index = metadata.get("sample_index", "?")
    round_index = metadata.get("bisection_round", "?")
    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}][round={round_index}] "
        f"direct endpoint execution start with {len(delta_listing)} ordered delta(s)",
    )

    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation="backward_attribution.direct_delta_execution",
        lm=lm,
        signature_cls=DirectDeltaExecutionSignature,
        input_dict={
            "agent": agent,
            "agent_role": AGENT_ROLES[agent],
            "base_prompt": base_prompt,
            "ordered_delta_p_trace": delta_listing,
            "visible_agent_inputs": dict(visible_inputs),
            "output_requirement": OUTPUT_REQUIREMENTS[agent],
        },
        lm_config=lm_config,
        metadata={
            **dict(metadata),
            "agent": agent,
            "n_edges": len(delta_listing),
        },
        return_cache_hit=True,
    )

    validated_output = normalize_direct_output(agent, parsed["output"])
    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}][round={round_index}] "
        f"direct endpoint execution done cache_hit={cache_hit} "
        f"output={_preview(validated_output)}",
    )

    return {
        "output": validated_output,
        "rationale": parsed["rationale"],
        "ordered_delta_p_trace": delta_listing,
        "lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    }


# ---------------------------------------------------------------------------
# Summary2-local semantic metric
# ---------------------------------------------------------------------------


class Summary2LocalJudgeSignature(Signature):
    input_keys = [
        "question",
        "source_summary",
        "target_summary",
        "candidate_summary",
    ]
    output_keys = [
        "target_reconstructed",
        "preserves_source",
        "meaningful_gain",
        "rationale",
    ]

    @classmethod
    def prompt_renderer(cls, input_dict: Mapping[str, Any]) -> str:
        return f"""
You are evaluating the LOCAL output quality of the summary2 agent in a
multi-agent HotpotQA pipeline.

Do not evaluate the downstream final answerer and do not use final-answer
exact match. Compare semantic information states, not lexical overlap.

Definitions:
- target_reconstructed: the candidate summary preserves the target
  summary's task-relevant evidence, entities, relations, and conclusions
  needed for the question. Paraphrases are allowed. Incidental details in
  the target need not be copied.
- preserves_source: the candidate does not remove or contradict useful
  task-relevant information already present in the source summary.
- meaningful_gain: relative to the source summary, the candidate adds at
  least one task-relevant fact, relation, disambiguation, or answer-bearing
  detail represented in the target summary.

Judge only the summaries shown below. Do not reward verbosity. Additional
facts are acceptable only when they do not contradict the source or target.

Question:
{input_dict["question"]}

Source summary2:
{input_dict["source_summary"]}

Target summary2:
{input_dict["target_summary"]}

Candidate summary2:
{input_dict["candidate_summary"]}

Return strict JSON only:
{{
  "target_reconstructed": true or false,
  "preserves_source": true or false,
  "meaningful_gain": true or false,
  "rationale": "brief evidence-based explanation"
}}
""".strip()

    @classmethod
    def output_extractor(cls, raw_output: str) -> dict[str, Any]:
        value = _extract_json_object(raw_output)
        required = {
            "target_reconstructed",
            "preserves_source",
            "meaningful_gain",
            "rationale",
        }
        missing = required - set(value)
        if missing:
            raise ValueError(
                "Summary2 local judge response missing keys: "
                f"{sorted(missing)}"
            )
        return value


def _strict_bool(value: Any, *, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    raise ValueError(f"{field} must be a JSON boolean, got {value!r}")


def judge_summary2_local(
    *,
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    question: str,
    source_state: Mapping[str, Any],
    target_state: Mapping[str, Any],
    candidate_state: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    source_summary = str(source_state.get("output") or "").strip()
    target_summary = str(target_state.get("output") or "").strip()
    candidate_summary = str(candidate_state.get("output") or "").strip()

    parsed, prompt, raw, cache_hit = run_signature(
        runtime=runtime,
        operation="backward_attribution.summary2_local_judge",
        lm=lm,
        signature_cls=Summary2LocalJudgeSignature,
        input_dict={
            "question": question,
            "source_summary": source_summary,
            "target_summary": target_summary,
            "candidate_summary": candidate_summary,
        },
        lm_config=lm_config,
        metadata={**dict(metadata), "agent": "summary2"},
        return_cache_hit=True,
    )

    target_reconstructed = _strict_bool(
        parsed["target_reconstructed"],
        field="target_reconstructed",
    )
    preserves_source = _strict_bool(
        parsed["preserves_source"],
        field="preserves_source",
    )
    meaningful_gain = _strict_bool(
        parsed["meaningful_gain"],
        field="meaningful_gain",
    )
    target_solved = target_reconstructed and preserves_source

    return {
        "metric_name": "summary2_semantic_target",
        "target_solved": target_solved,
        "no_regression": preserves_source,
        "target_reconstructed": target_reconstructed,
        "meaningful_gain": meaningful_gain,
        "source_metric": {
            "metric_name": "summary2_semantic_target",
            "value": 0.0,
            "available": True,
            "summary": source_summary,
        },
        "target_metric": {
            "metric_name": "summary2_semantic_target",
            "value": 1.0,
            "available": True,
            "summary": target_summary,
        },
        "realized_metric": {
            "metric_name": "summary2_semantic_target",
            "value": 1.0 if target_solved else 0.0,
            "available": True,
            "summary": candidate_summary,
        },
        "source_value": 0.0,
        "target_value": 1.0,
        "realized_value": 1.0 if target_solved else 0.0,
        "rationale": str(parsed["rationale"]),
        "judge_lm_trace": {
            "rendered_prompt": prompt,
            "raw_output": raw,
            "cache_hit": cache_hit,
        },
    }


# ---------------------------------------------------------------------------
# Attribution workflow
# ---------------------------------------------------------------------------


def assess_destination_operational(
    *,
    agent: str,
    source_state: Mapping[str, Any],
    target_state: Mapping[str, Any],
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    question: str,
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """Check that the constructed destination is a meaningful local target."""
    if agent == "summary2":
        judged = judge_summary2_local(
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            question=question,
            source_state=source_state,
            target_state=target_state,
            candidate_state=target_state,
            metadata={**dict(metadata), "judge_phase": "destination_gate"},
        )
        operational = bool(
            judged["target_reconstructed"]
            and judged["no_regression"]
            and judged["meaningful_gain"]
        )
        return {
            "operational": operational,
            "source_metric": judged["source_metric"],
            "target_metric": judged["target_metric"],
            "summary2_local_judge": judged,
            "reason": (
                "destination adds task-relevant summary2 information "
                "without semantic regression"
                if operational
                else "destination lacks meaningful task-relevant gain or "
                "regresses useful source-summary information"
            ),
        }

    source_metric = compute_local_metric(
        agent=agent,
        state=source_state,
    )
    target_metric = compute_local_metric(
        agent=agent,
        state=target_state,
    )

    if agent in {"query", "summary1"}:
        source_hits = set(source_metric.get("hit_titles") or [])
        target_hits = set(target_metric.get("hit_titles") or [])
        new_target_hits = target_hits - source_hits
        lost_source_hits = source_hits - target_hits
        operational = bool(new_target_hits) and not lost_source_hits
        return {
            "operational": operational,
            "source_metric": source_metric,
            "target_metric": target_metric,
            "new_target_hits": sorted(new_target_hits),
            "lost_source_hits": sorted(lost_source_hits),
            "reason": (
                "destination adds missing-support recovery without regression"
                if operational
                else "destination does not add a new recoverable support hit "
                "or loses a source hit"
            ),
        }

    source_value = float(source_metric.get("value") or 0.0)
    target_value = float(target_metric.get("value") or 0.0)
    operational = target_value > source_value and target_value >= 1.0
    return {
        "operational": operational,
        "source_metric": source_metric,
        "target_metric": target_metric,
        "reason": (
            "destination improves the answer metric to exact match"
            if operational
            else "destination does not improve the answer metric to exact match"
        ),
    }


def _destination_result(
    *,
    agent: str,
    row: Mapping[str, Any],
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    destination, prompt, raw, cache_hit = build_agent_destination(
        agent=agent,
        row=row,
        runtime=runtime,
        lm=lm,
        lm_config=lm_config,
        summary_1=str(row.get("summary_1") or ""),
        metadata=metadata,
        return_metadata=True,
    )
    return destination, {
        "rendered_prompt": prompt,
        "raw_output": raw,
        "cache_hit": cache_hit,
    }


def attempt_agent_attribution(
    *,
    row: Mapping[str, Any],
    sample_index: int,
    agent: str,
    program: Any,
    candidate: Mapping[str, str],
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    max_iter: int,
    delta_attempts: int,
    verbose: bool = False,
) -> dict[str, Any]:
    metadata = {
        "sample_index": int(sample_index),
        "row_index": row.get("index", sample_index),
    }
    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}] start attribution attempt "
        f"question={_preview(row.get('question'))}",
    )
    base_prompt = candidate[AGENT_TO_PROMPT_KEY[agent]]
    visible_inputs = build_agent_inputs(agent, row)
    task_context = build_task_context(agent, row)

    _log(verbose, f"[sample={sample_index}][agent={agent}] build source endpoint")
    source_state = state_from_trace(
        agent=agent,
        row=row,
        state_kind="endpoint",
        state_origin="baseline_rollout",
    )
    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}] source endpoint ready "
        f"output={_preview(_state_output(agent, source_state))}",
    )

    _log(verbose, f"[sample={sample_index}][agent={agent}] build destination")
    destination, destination_lm_trace = _destination_result(
        agent=agent,
        row=row,
        runtime=runtime,
        lm=lm,
        lm_config=lm_config,
        metadata=metadata,
    )

    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}] destination generated "
        f"available={destination.get('available', True)} "
        f"cache_hit={destination_lm_trace.get('cache_hit')} "
        f"output={_preview(destination.get('output'))}",
    )

    if destination.get("available") is False:
        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}] destination unavailable: "
            f"{destination.get('reason')} -> move upstream",
        )
        return {
            "agent": agent,
            "status": "destination_unavailable",
            "attributed": False,
            "reason": destination.get("reason"),
            "destination": destination,
            "destination_lm_trace": destination_lm_trace,
            "probes": [],
        }

    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}] materialize destination endpoint",
    )
    target_state = materialize_destination(
        program=program,
        row=row,
        destination=destination,
        summary_1=str(row.get("summary_1") or ""),
    )
    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}] destination endpoint materialized "
        f"output={_preview(_state_output(agent, target_state))}",
    )

    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}] evaluate destination operational gate",
    )
    destination_gate = assess_destination_operational(
        agent=agent,
        source_state=source_state,
        target_state=target_state,
        runtime=runtime,
        lm=lm,
        lm_config=lm_config,
        question=str(row.get("question") or ""),
        metadata=metadata,
    )
    _log(
        verbose,
        f"[sample={sample_index}][agent={agent}] destination gate "
        f"operational={destination_gate['operational']} "
        f"source_metric={_json_dumps(_metric_preview(destination_gate.get('source_metric')), indent=None)} "
        f"target_metric={_json_dumps(_metric_preview(destination_gate.get('target_metric')), indent=None)}",
    )
    if not destination_gate["operational"]:
        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}] destination rejected: "
            f"{destination_gate['reason']} -> move upstream",
        )
        return {
            "agent": agent,
            "status": "destination_not_operational",
            "attributed": False,
            "reason": destination_gate["reason"],
            "source_state": source_state,
            "destination": destination,
            "destination_state": target_state,
            "destination_gate": destination_gate,
            "destination_lm_trace": destination_lm_trace,
            "probes": [],
        }

    states: list[dict[str, Any]] = [source_state, target_state]
    probes = []

    # Probe 0 is the unsplit endpoint edge. Each failed probe may be
    # followed by one bisection; max_iter therefore means at most
    # max_iter bisection rounds and max_iter + 1 endpoint probes.
    for bisection_round in range(max_iter + 1):
        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}][round={bisection_round}] "
            f"endpoint probe start states={len(states)} edges={len(states) - 1}",
        )
        delta_p_trace = build_delta_p_trace(
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            agent=agent,
            current_prompt=base_prompt,
            task_context=task_context,
            visible_inputs=visible_inputs,
            states=states,
            destination=destination,
            row=row,
            metadata={
                **metadata,
                "bisection_round": bisection_round,
            },
            max_attempts=delta_attempts,
            verbose=verbose,
        )

        execution = execute_direct_delta_context(
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            agent=agent,
            base_prompt=base_prompt,
            delta_p_trace=delta_p_trace,
            visible_inputs=visible_inputs,
            metadata={
                **metadata,
                "bisection_round": bisection_round,
            },
            verbose=verbose,
        )

        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}][round={bisection_round}] "
            "materialize generated output downstream",
        )
        realized_state = materialize_agent_state(
            agent=agent,
            program=program,
            row=row,
            output=execution["output"],
            summary_1=str(row.get("summary_1") or ""),
            state_kind="endpoint",
            state_origin="prompt_intervention",
        )

        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}][round={bisection_round}] "
            "evaluate endpoint solvability",
        )
        if agent == "summary2":
            solvability = judge_summary2_local(
                runtime=runtime,
                lm=lm,
                lm_config=lm_config,
                question=str(row.get("question") or ""),
                source_state=source_state,
                target_state=target_state,
                candidate_state=realized_state,
                metadata={
                    **metadata,
                    "judge_phase": "endpoint_probe",
                    "bisection_round": bisection_round,
                },
            )
        else:
            solvability = evaluate_endpoint_solvability(
                agent=agent,
                source_state=source_state,
                target_state=target_state,
                realized_state=realized_state,
            )

        probe = {
            "bisection_round": bisection_round,
            "n_states": len(states),
            "n_edges": len(states) - 1,
            "states": states,
            "delta_p_trace": delta_p_trace,
            "execution": execution,
            "realized_state": realized_state,
            "endpoint_solvability": solvability,
        }
        probes.append(probe)

        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}][round={bisection_round}] "
            f"endpoint result target_solved={solvability.get('target_solved')} "
            f"source={_json_dumps(_metric_preview(solvability.get('source_metric')), indent=None)} "
            f"target={_json_dumps(_metric_preview(solvability.get('target_metric')), indent=None)} "
            f"realized={_json_dumps(_metric_preview(solvability.get('realized_metric')), indent=None)}",
        )

        if solvability["target_solved"]:
            _log(
                verbose,
                f"[sample={sample_index}][agent={agent}] ATTRIBUTED at round={bisection_round}",
            )
            return {
                "agent": agent,
                "status": "attributed",
                "attributed": True,
                "base_prompt_key": AGENT_TO_PROMPT_KEY[agent],
                "base_prompt": base_prompt,
                "source_state": source_state,
                "destination": destination,
                "destination_state": target_state,
                "destination_lm_trace": destination_lm_trace,
                "successful_bisection_round": bisection_round,
                "endpoint_verified": True,
                "edge_individually_verified": False,
                "probes": probes,
            }

        if bisection_round == max_iter:
            _log(
                verbose,
                f"[sample={sample_index}][agent={agent}] max_iter reached without endpoint reconstruction",
            )
            break

        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}][round={bisection_round}] "
            "probe failed -> select largest edge",
        )
        selected, select_prompt, select_raw, select_cache_hit = (
            select_largest_edge(
                runtime=runtime,
                lm=lm,
                lm_config=lm_config,
                agent=agent,
                task_context=task_context,
                states=states,
                metadata={
                    **metadata,
                    "bisection_round": bisection_round + 1,
                },
                return_metadata=True,
            )
        )

        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}][round={bisection_round}] "
            f"largest edge={selected['edge_index']} cache_hit={select_cache_hit} -> generate midpoint",
        )
        midpoint, mid_prompt, mid_raw, mid_cache_hit = generate_midpoint(
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            agent=agent,
            task_context=task_context,
            left_state=selected["source_state"],
            right_state=selected["target_state"],
            metadata={
                **metadata,
                "bisection_round": bisection_round + 1,
                "selected_edge_index": selected["edge_index"],
            },
            return_metadata=True,
        )

        mid_state = make_intermediate_state(
            agent=agent,
            mid_output=midpoint["mid_output"],
            rationale=midpoint["rationale"],
            bisection_round=bisection_round + 1,
        )
        insertion_index = int(selected["edge_index"]) + 1
        states = states[:insertion_index] + [mid_state] + states[insertion_index:]
        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}][round={bisection_round + 1}] "
            f"midpoint inserted at state_index={insertion_index} cache_hit={mid_cache_hit} "
            f"output={_preview(mid_state['output'])}; new_edges={len(states) - 1}",
        )

        probe["bisection_after_failure"] = {
            "selected_edge": selected,
            "selection_lm_trace": {
                "rendered_prompt": select_prompt,
                "raw_output": select_raw,
                "cache_hit": select_cache_hit,
            },
            "midpoint": midpoint,
            "midpoint_lm_trace": {
                "rendered_prompt": mid_prompt,
                "raw_output": mid_raw,
                "cache_hit": mid_cache_hit,
            },
            "inserted_state": mid_state,
        }

    return {
        "agent": agent,
        "status": "max_iter_unsolved",
        "attributed": False,
        "base_prompt_key": AGENT_TO_PROMPT_KEY[agent],
        "base_prompt": base_prompt,
        "source_state": source_state,
        "destination": destination,
        "destination_state": target_state,
        "destination_lm_trace": destination_lm_trace,
        "endpoint_verified": False,
        "edge_individually_verified": False,
        "probes": probes,
    }


def analyze_wrong_sample(
    *,
    row: Mapping[str, Any],
    sample_index: int,
    program: Any,
    candidate: Mapping[str, str],
    runtime: OursRuntime,
    lm: LanguageModel,
    lm_config: Mapping[str, Any],
    agent_max_iters: Mapping[str, int],
    delta_attempts: int,
    verbose: bool = False,
) -> dict[str, Any]:
    attempts = []
    attributed_agent = None

    _log(
        verbose,
        f"[sample={sample_index}] START wrong sample row_index={row.get('index', sample_index)} "
        f"baseline={_preview(row.get('answer'))} gold={_preview(row.get('gold_answer'))}",
    )

    for agent in AGENT_ORDER:
        _log(
            verbose,
            f"[sample={sample_index}] move attribution scope to agent={agent}",
        )
        try:
            attempt = attempt_agent_attribution(
                row=row,
                sample_index=sample_index,
                agent=agent,
                program=program,
                candidate=candidate,
                runtime=runtime,
                lm=lm,
                lm_config=lm_config,
                max_iter=agent_max_iters[agent],
                delta_attempts=delta_attempts,
                verbose=verbose,
            )
        except Exception as exc:
            _log(
                verbose,
                f"[sample={sample_index}][agent={agent}] ERROR "
                f"{type(exc).__name__}: {exc}",
            )
            attempt = {
                "agent": agent,
                "status": "error",
                "attributed": False,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "traceback": traceback.format_exc(),
            }

        attempts.append(attempt)
        _log(
            verbose,
            f"[sample={sample_index}][agent={agent}] attempt finished status={attempt.get('status')}",
        )
        if attempt.get("attributed") is True:
            attributed_agent = agent
            break

    _log(
        verbose,
        f"[sample={sample_index}] DONE attributed_agent={attributed_agent or 'none'}",
    )

    return {
        "sample_index": int(sample_index),
        "row_index": row.get("index", sample_index),
        "sample_id": row.get("sample_id"),
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "baseline_answer": row.get("answer"),
        "baseline_score": float(row.get("score") or 0.0),
        "candidate_hash": (
            row.get("candidate_hash")
            or canonical_hash(candidate)
        ),
        "source_candidate_hash": (
            row.get("candidate_hash")
            or canonical_hash(candidate)
        ),
        "attributed": attributed_agent is not None,
        "attributed_agent": attributed_agent,
        "attempts": attempts,
    }


def endpoint_verified_edge_rows(
    attribute_row: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if not attribute_row.get("attributed"):
        return []

    successful_attempt = next(
        (
            attempt
            for attempt in attribute_row.get("attempts", [])
            if attempt.get("attributed") is True
        ),
        None,
    )
    if successful_attempt is None:
        return []

    successful_probe = successful_attempt["probes"][-1]
    states = successful_probe["states"]
    deltas = successful_probe["delta_p_trace"]

    rows = []
    for edge_index, delta in enumerate(deltas):
        rows.append({
            "sample_index": attribute_row["sample_index"],
            "row_index": attribute_row.get("row_index"),
            "question": attribute_row.get("question"),
            "agent": successful_attempt["agent"],
            "trace_endpoint_solved": True,
            "edge_individually_verified": False,
            "bisection_round": successful_probe["bisection_round"],
            "n_edges": successful_probe["n_edges"],
            "edge_index": edge_index,
            "source_state": states[edge_index],
            "target_state": states[edge_index + 1],
            "delta_p": delta,
            "endpoint_solvability": successful_probe[
                "endpoint_solvability"
            ],
        })
    return rows


def build_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    wrong_rows = len(rows)
    attributed = [row for row in rows if row.get("attributed")]
    agent_counts = Counter(
        row.get("attributed_agent")
        for row in attributed
        if row.get("attributed_agent")
    )

    status_counts = Counter()
    destination_unavailable = Counter()
    error_counts = Counter()
    successful_rounds = Counter()

    for row in rows:
        for attempt in row.get("attempts", []):
            agent = str(attempt.get("agent") or "unknown")
            status = str(attempt.get("status") or "unknown")
            status_counts[f"{agent}:{status}"] += 1
            if status == "destination_unavailable":
                destination_unavailable[agent] += 1
            if status == "error":
                error_counts[agent] += 1
            if attempt.get("attributed"):
                successful_rounds[
                    str(attempt.get("successful_bisection_round", 0))
                ] += 1

    return {
        "num_wrong_rows_processed": wrong_rows,
        "num_attributed": len(attributed),
        "num_unattributed": wrong_rows - len(attributed),
        "attribution_rate": (
            len(attributed) / wrong_rows if wrong_rows else 0.0
        ),
        "attributed_by_agent": dict(agent_counts),
        "successful_bisection_rounds": dict(successful_rounds),
        "destination_unavailable_by_agent": dict(destination_unavailable),
        "errors_by_agent": dict(error_counts),
        "attempt_status_counts": dict(status_counts),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_indices(text: str | None) -> set[int] | None:
    if text is None:
        return None
    values = set()
    for part in text.split(","):
        part = part.strip()
        if part:
            values.add(int(part))
    return values


def make_dspy_lm(
    *,
    model: str,
    api_base: str | None,
    api_key: str,
    temperature: float,
    max_tokens: int,
):
    kwargs: dict[str, Any] = {
        "api_key": api_key,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if api_base:
        kwargs["api_base"] = api_base
    return dspy.LM(model, **kwargs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Backward agent attribution using direct ordered delta-p "
            "endpoint reconstruction."
        )
    )
    parser.add_argument("--eval-rows", default=DEFAULT_EVAL_ROWS)
    parser.add_argument(
        "--source-eval-rows",
        default=None,
        help=(
            "Optional original flat eval_rows JSON used to supplement "
            "nested update_prompt eval_rows.jsonl traces."
        ),
    )
    parser.add_argument(
        "--candidate-path",
        default=None,
        help=(
            "Optional candidate.json from a previous prompt-update "
            "iteration. If omitted, BASELINE_PROMPT_SET is used."
        ),
    )
    parser.add_argument("--run-dir", default=DEFAULT_RUN_DIR)
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    parser.add_argument("--cache-dir", default="examples/ours/cache/backward_attribution_v2")
    parser.add_argument("--retriever-dir", default=DEFAULT_RETRIEVER_DIR)
    parser.add_argument("--k", type=int, default=7)

    parser.add_argument("--model", default="openai/gpt-5-mini")
    parser.add_argument("--api-base", default="https://api.openai.com/v1")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=16000)

    for agent, default in DEFAULT_AGENT_MAX_ITERS.items():
        parser.add_argument(
            f"--{agent}-max-iter",
            type=int,
            default=default,
            help=(
                f"Maximum midpoint generations for {agent}. "
                "The number of endpoint probes is max_iter + 1."
            ),
        )
    parser.add_argument(
        "--delta-attempts",
        type=int,
        default=3,
        help="Maximum guarded delta-p generation attempts per edge.",
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        default=4,
    )
    parser.add_argument("--indices", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument(
        "--verbose",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Print sample/agent/round/edge progress logs. "
            "Use --no-verbose to disable."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    agent_max_iters = {
        agent: getattr(args, f"{agent}_max_iter")
        for agent in AGENT_ORDER
    }

    print(
        f"[startup] script={Path(__file__).resolve()} "
        f"version={SCRIPT_VERSION} verbose={args.verbose}",
        flush=True,
    )

    for agent, max_iter in agent_max_iters.items():
        if max_iter < 0:
            raise ValueError(
                f"--{agent}-max-iter must be non-negative."
            )
    if args.delta_attempts < 1:
        raise ValueError("--delta-attempts must be at least 1.")
    if args.num_threads < 1:
        raise ValueError("--num-threads must be at least 1.")
    if args.limit is not None and args.limit < 0:
        raise ValueError("--limit must be non-negative.")

    load_dotenv(args.env_file)
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError(
            f"OPENAI_API_KEY is missing after loading {args.env_file}."
        )
    _log(args.verbose, f"[setup] loaded environment from {args.env_file}")

    if args.candidate_path:
        candidate, candidate_name = load_candidate_file(
            args.candidate_path
        )
        candidate_path = str(
            Path(args.candidate_path)
        )
    else:
        candidate = dict(
            BASELINE_PROMPT_SET["prompts"]
        )
        candidate_name = (
            BASELINE_PROMPT_SET["name"]
        )
        candidate_path = None

    candidate_hash = canonical_hash(candidate)

    eval_rows = normalize_eval_rows(
        eval_rows_path=args.eval_rows,
        source_eval_rows_path=args.source_eval_rows,
        expected_candidate_hash=(
            candidate_hash
            if args.candidate_path
            else None
        ),
    )
    if not eval_rows:
        raise ValueError(
            "No usable evaluation rows were loaded."
        )

    if args.candidate_path:
        for row in eval_rows:
            row.setdefault(
                "candidate_hash",
                candidate_hash,
            )

    _log(
        args.verbose,
        f"[setup] candidate={candidate_name} "
        f"candidate_hash={candidate_hash[:12]} "
        f"candidate_path={candidate_path or 'builtin'}",
    )

    selected_indices = parse_indices(args.indices)
    wrong_items = [
        (position, row)
        for position, row in enumerate(eval_rows)
        if float(row.get("score") or 0.0) != 1.0
        and (
            selected_indices is None
            or int(row.get("index", position)) in selected_indices
        )
    ]
    if args.limit is not None:
        wrong_items = wrong_items[: args.limit]

    _log(
        args.verbose,
        f"[setup] eval_rows={args.eval_rows} total={len(eval_rows)} "
        f"wrong_selected={len(wrong_items)} model={args.model} "
        f"agent_max_iters={agent_max_iters}",
    )

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    attribute_path = run_dir / "attribute_rows.jsonl"
    edge_path = run_dir / "endpoint_verified_edges.jsonl"
    summary_path = run_dir / "summary.json"
    config_path = run_dir / "config.json"

    if args.overwrite:
        for path in (attribute_path, edge_path, summary_path, config_path):
            if path.exists():
                path.unlink()

    existing_rows = read_jsonl(attribute_path)

    if args.candidate_path and existing_rows:
        existing_hashes = {
            str(
                row.get("source_candidate_hash")
                or row.get("candidate_hash")
            )
            for row in existing_rows
            if (
                row.get("source_candidate_hash")
                or row.get("candidate_hash")
            )
        }
        if (
            existing_hashes
            and existing_hashes != {candidate_hash}
        ):
            raise ValueError(
                "Existing attribution rows were produced from a "
                "different candidate. Use a new --run-dir or --overwrite."
            )

    done = {
        int(row["sample_index"])
        for row in existing_rows
    }

    _log(args.verbose, f"[setup] initialize LM model={args.model}")
    lm = make_dspy_lm(
        model=args.model,
        api_base=args.api_base,
        api_key=api_key,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    dspy.configure(lm=lm)

    lm_config = {
        "model": args.model,
        "api_base": args.api_base,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }

    _log(args.verbose, f"[setup] initialize retriever dir={args.retriever_dir} k={args.k}")
    set_retriever_dir(args.retriever_dir)
    base_program = HotpotMultiHop(
        k=args.k,
        retriever_dir=args.retriever_dir,
    )
    validate_candidate(
        candidate,
        program=base_program,
    )
    adapter = HotpotAdapter(
        program=base_program,
        metric_fn=answer_exact_match,
        runtime_config={
            "task_model": args.model,
            "task_api_base": args.api_base,
            "task_temperature": args.temperature,
            "task_max_tokens": args.max_tokens,
            "retriever_dir": args.retriever_dir,
            "k": args.k,
        },
    )
    _log(
        args.verbose,
        f"[setup] apply candidate={candidate_name} to HotpotMultiHop",
    )
    program = adapter.build_program(candidate)
    _log(args.verbose, "[setup] program ready")

    runtime = OursRuntime(
        cache_dir=args.cache_dir,
        cache_enabled=not args.no_cache,
    )
    _log(
        args.verbose,
        f"[setup] runtime ready cache_enabled={not args.no_cache} cache_dir={args.cache_dir}",
    )

    write_json(config_path, {
        "eval_rows": str(args.eval_rows),
        "run_dir": str(args.run_dir),
        "candidate_name": candidate_name,
        "candidate_path": candidate_path,
        "candidate_hash": candidate_hash,
        "source_eval_rows": (
            str(args.source_eval_rows)
            if args.source_eval_rows
            else None
        ),
        "candidate": candidate,
        "agent_order": list(AGENT_ORDER),
        "model": lm_config,
        "retriever_dir": str(args.retriever_dir),
        "k": args.k,
        "agent_max_iters": agent_max_iters,
        "agent_probe_counts": {
            agent: max_iter + 1
            for agent, max_iter in agent_max_iters.items()
        },
        "delta_attempts": args.delta_attempts,
        "success_definition": (
            "All ordered adjacent-edge delta-p items are supplied directly "
            "with the unchanged base prompt; only final endpoint "
            "reconstruction is evaluated."
        ),
        "intermediate_reconstruction_required": False,
        "individual_edge_atomicity_claimed": False,
    })

    pending = [item for item in wrong_items if item[0] not in done]
    _log(
        args.verbose,
        f"[setup] completed={len(done)} pending={len(pending)} "
        f"cache_enabled={not args.no_cache} run_dir={run_dir}",
    )
    completed_rows = list(existing_rows)

    def run_one(
        item: tuple[int, Mapping[str, Any]],
    ) -> dict[str, Any]:
        sample_position, row = item
        worker_program = (
            program
            if args.num_threads == 1
            else adapter.build_program(candidate)
        )
        return analyze_wrong_sample(
            row=row,
            sample_index=sample_position,
            program=worker_program,
            candidate=candidate,
            runtime=runtime,
            lm=lm,
            lm_config=lm_config,
            agent_max_iters=agent_max_iters,
            delta_attempts=args.delta_attempts,
            verbose=args.verbose,
        )

    def persist_result(result: Mapping[str, Any]) -> None:
        append_jsonl(attribute_path, result)

        verified_edges = endpoint_verified_edge_rows(result)
        for edge_row in verified_edges:
            append_jsonl(edge_path, edge_row)

        completed_rows.append(dict(result))
        summary = build_summary(completed_rows)
        summary.update({
            "num_eval_rows": len(eval_rows),
            "num_wrong_rows_selected": len(wrong_items),
            "attribute_rows": str(attribute_path),
            "endpoint_verified_edges": str(edge_path),
        })
        write_json(summary_path, summary)

        _log(
            args.verbose,
            f"[sample={result['sample_index']}] persisted attribute row; "
            f"endpoint_verified_edges_added={len(verified_edges)}",
        )

    if args.num_threads == 1:
        progress = tqdm(
            pending,
            desc="Backward attribution",
            unit="sample",
        )
        for item in progress:
            result = run_one(item)
            persist_result(result)
            progress.set_postfix(
                attributed=result.get("attributed_agent") or "none",
                refresh=False,
            )
    else:
        with cf.ThreadPoolExecutor(
            max_workers=args.num_threads,
        ) as executor:
            futures = [
                executor.submit(run_one, item)
                for item in pending
            ]
            progress = tqdm(
                total=len(futures),
                desc="Backward attribution",
                unit="sample",
            )
            for future in cf.as_completed(futures):
                result = future.result()
                persist_result(result)
                progress.set_postfix(
                    attributed=result.get("attributed_agent") or "none",
                    refresh=False,
                )
                progress.update(1)
            progress.close()

    all_rows = read_jsonl(attribute_path)
    summary = build_summary(all_rows)
    summary.update({
        "num_eval_rows": len(eval_rows),
        "num_wrong_rows_selected": len(wrong_items),
        "attribute_rows": str(attribute_path),
        "endpoint_verified_edges": str(edge_path),
    })
    write_json(summary_path, summary)
    _log(args.verbose, f"[done] summary written to {summary_path}")
    print(_json_dumps(summary))


if __name__ == "__main__":
    main()
