#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional


CACHE_SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def to_jsonable(value: Any) -> Any:
    """Convert common Python objects into deterministic JSON-compatible values."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, Mapping):
        return {
            str(key): to_jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]

    if isinstance(value, set):
        converted = [to_jsonable(item) for item in value]
        return sorted(
            converted,
            key=lambda item: json.dumps(
                item,
                ensure_ascii=False,
                sort_keys=True,
            ),
        )

    if hasattr(value, "model_dump"):
        return to_jsonable(value.model_dump())

    if hasattr(value, "to_dict"):
        return to_jsonable(value.to_dict())

    try:
        return to_jsonable(dict(value))
    except (TypeError, ValueError):
        pass

    return str(value)


def canonical_json(value: Any) -> str:
    return json.dumps(
        to_jsonable(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def make_input_hash(
    *,
    stage: str,
    request: Any,
    model: Optional[str] = None,
    generation: Optional[Mapping[str, Any]] = None,
    prompt_version: Optional[int | str] = None,
    cache_version: int = CACHE_SCHEMA_VERSION,
) -> str:
    """
    Create the cache key.

    Run ID, iteration, timestamps, and other execution metadata are intentionally
    excluded. They do not change the semantic external call.
    """

    payload = {
        "cache_version": cache_version,
        "stage": stage,
        "model": model,
        "generation": generation or {},
        "prompt_version": prompt_version,
        "request": request,
    }

    return hashlib.sha256(
        canonical_json(payload).encode("utf-8")
    ).hexdigest()


def safe_stage_name(stage: str) -> str:
    stage = stage.strip()
    if not stage:
        raise ValueError("stage must not be empty.")

    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", stage)
    return safe.strip("._") or "unknown"


def atomic_write_json(path: str | Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.parent / (
        f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    )

    with tmp.open("w", encoding="utf-8") as f:
        json.dump(
            to_jsonable(data),
            f,
            ensure_ascii=False,
            indent=2,
        )
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())

    os.replace(tmp, path)


def append_jsonl(path: str | Path, row: Any) -> None:
    """
    Append one complete JSON record and fsync it immediately.

    flock prevents multiple worker processes from interleaving JSONL lines.
    """

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    line = json.dumps(
        to_jsonable(row),
        ensure_ascii=False,
        separators=(",", ":"),
    )

    with path.open("a", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


class CallCache:
    """
    File-based call cache with append-only attempt records.

    Layout:

        <root>/<stage>/<input_hash>.json
            Successful result used for cache lookup.

        <root>/<stage>/_attempts/<input_hash>.<attempt_id>.json
            Immutable record for every actual external call attempt.

        <root>/<stage>/_locks/<input_hash>.lock
            Cross-process lock preventing duplicate concurrent calls.
    """

    def __init__(
        self,
        root: str | Path,
        *,
        events_path: Optional[str | Path] = None,
    ):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

        self.events_path = (
            Path(events_path)
            if events_path is not None
            else None
        )

    def success_path(self, stage: str, input_hash: str) -> Path:
        return (
            self.root
            / safe_stage_name(stage)
            / f"{input_hash}.json"
        )

    def attempt_path(
        self,
        stage: str,
        input_hash: str,
        attempt_id: str,
    ) -> Path:
        return (
            self.root
            / safe_stage_name(stage)
            / "_attempts"
            / f"{input_hash}.{attempt_id}.json"
        )

    def lock_path(self, stage: str, input_hash: str) -> Path:
        return (
            self.root
            / safe_stage_name(stage)
            / "_locks"
            / f"{input_hash}.lock"
        )

    def load_success(
        self,
        *,
        stage: str,
        input_hash: str,
    ) -> Optional[dict[str, Any]]:
        path = self.success_path(stage, input_hash)

        if not path.exists():
            return None

        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # An invalid file is treated as a cache miss.
            return None

        if record.get("status") != "success":
            return None

        if record.get("input_hash") != input_hash:
            return None

        return record

    def append_event(self, event: Mapping[str, Any]) -> None:
        if self.events_path is None:
            return

        append_jsonl(
            self.events_path,
            {
                "timestamp": utc_now(),
                **to_jsonable(event),
            },
        )

    def cached_call(
        self,
        *,
        stage: str,
        request: Any,
        call_fn: Callable[[], Any],
        parse_fn: Optional[Callable[[Any], Any]] = None,
        model: Optional[str] = None,
        generation: Optional[Mapping[str, Any]] = None,
        prompt_version: Optional[int | str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        retry_index: int = 0,
        reuse: bool = True,
    ) -> tuple[Any, bool, dict[str, Any]]:
        """
        Execute or reuse one external call.

        Returns:
            parsed_response, cache_hit, cache_record

        `call_fn` performs the actual model/tool call.
        `parse_fn`, when provided, converts the raw response into the structured
        object that downstream code consumes.
        """

        stage = safe_stage_name(stage)
        request_json = to_jsonable(request)
        generation_json = to_jsonable(generation or {})
        metadata_json = to_jsonable(metadata or {})

        input_hash = make_input_hash(
            stage=stage,
            request=request_json,
            model=model,
            generation=generation_json,
            prompt_version=prompt_version,
        )

        if reuse:
            cached = self.load_success(
                stage=stage,
                input_hash=input_hash,
            )
            if cached is not None:
                self.append_event({
                    "event": "call_cache_hit",
                    "stage": stage,
                    "input_hash": input_hash,
                    "model": model,
                    "metadata": metadata_json,
                })

                return (
                    cached.get("parsed_response"),
                    True,
                    cached,
                )

        lock_path = self.lock_path(stage, input_hash)
        lock_path.parent.mkdir(parents=True, exist_ok=True)

        # Hold the lock through the external call. A second process requesting
        # the same input waits and then reuses the first process's result.
        with lock_path.open("a+", encoding="utf-8") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

            try:
                if reuse:
                    cached = self.load_success(
                        stage=stage,
                        input_hash=input_hash,
                    )
                    if cached is not None:
                        self.append_event({
                            "event": "call_cache_hit_after_wait",
                            "stage": stage,
                            "input_hash": input_hash,
                            "model": model,
                            "metadata": metadata_json,
                        })

                        return (
                            cached.get("parsed_response"),
                            True,
                            cached,
                        )

                attempt_id = (
                    f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
                    f"-{os.getpid()}-{uuid.uuid4().hex[:8]}"
                )
                started_at = utc_now()
                started_perf = time.perf_counter()
                raw_response: Any = None

                self.append_event({
                    "event": "call_started",
                    "stage": stage,
                    "input_hash": input_hash,
                    "attempt_id": attempt_id,
                    "model": model,
                    "retry_index": retry_index,
                    "metadata": metadata_json,
                })

                try:
                    raw_response = call_fn()
                    parsed_response = (
                        parse_fn(raw_response)
                        if parse_fn is not None
                        else raw_response
                    )

                    finished_at = utc_now()
                    duration_seconds = (
                        time.perf_counter() - started_perf
                    )

                    record = {
                        "schema_version": CACHE_SCHEMA_VERSION,
                        "status": "success",
                        "stage": stage,
                        "input_hash": input_hash,
                        "attempt_id": attempt_id,
                        "model": model,
                        "generation": generation_json,
                        "prompt_version": prompt_version,
                        "retry_index": retry_index,
                        "request": request_json,
                        "raw_response": to_jsonable(raw_response),
                        "parsed_response": to_jsonable(parsed_response),
                        "metadata": metadata_json,
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "duration_seconds": duration_seconds,
                        "error": None,
                    }

                    # Append-only call attempt record.
                    atomic_write_json(
                        self.attempt_path(
                            stage,
                            input_hash,
                            attempt_id,
                        ),
                        record,
                    )

                    # Canonical successful lookup record.
                    atomic_write_json(
                        self.success_path(stage, input_hash),
                        record,
                    )

                    self.append_event({
                        "event": "call_succeeded",
                        "stage": stage,
                        "input_hash": input_hash,
                        "attempt_id": attempt_id,
                        "model": model,
                        "duration_seconds": duration_seconds,
                        "metadata": metadata_json,
                    })

                    return parsed_response, False, record

                except Exception as exc:
                    finished_at = utc_now()
                    duration_seconds = (
                        time.perf_counter() - started_perf
                    )

                    error_record = {
                        "schema_version": CACHE_SCHEMA_VERSION,
                        "status": "error",
                        "stage": stage,
                        "input_hash": input_hash,
                        "attempt_id": attempt_id,
                        "model": model,
                        "generation": generation_json,
                        "prompt_version": prompt_version,
                        "retry_index": retry_index,
                        "request": request_json,
                        "raw_response": to_jsonable(raw_response),
                        "parsed_response": None,
                        "metadata": metadata_json,
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "duration_seconds": duration_seconds,
                        "error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                            "traceback": traceback.format_exc(),
                        },
                    }

                    # Error attempts remain persisted, but are never reused.
                    atomic_write_json(
                        self.attempt_path(
                            stage,
                            input_hash,
                            attempt_id,
                        ),
                        error_record,
                    )

                    self.append_event({
                        "event": "call_failed",
                        "stage": stage,
                        "input_hash": input_hash,
                        "attempt_id": attempt_id,
                        "model": model,
                        "duration_seconds": duration_seconds,
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                        "metadata": metadata_json,
                    })

                    raise

            finally:
                fcntl.flock(
                    lock_file.fileno(),
                    fcntl.LOCK_UN,
                )
