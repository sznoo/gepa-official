# /home/jinwoo/gepa-official/src/ours/runtime.py
from pathlib import Path
from typing import Any, Callable

from ours.cache import CallCache


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


def _example_payload(example: Any) -> dict[str, Any]:
    """
    Cache identity for a task example.

    Include task-relevant fields rather than relying only on sample_id,
    since some examples may not have a stable ID.
    """
    return {
        "sample_id": _get(
            example,
            "_id",
            _get(example, "id"),
        ),
        "question": _get(example, "question"),
        "answer": _get(example, "answer"),
        "context": _get(example, "context"),
        "supporting_facts": _get(
            example,
            "supporting_facts",
        ),
    }


class OursRuntime:
    """
    Single execution surface for all expensive calls.

    The optimizer and helper modules should call:
      - runtime.forward(...)
      - runtime.rerun(...)
      - runtime.call(...)

    instead of invoking adapters or LMs directly.
    """

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        cache_enabled: bool = True,
    ):
        self.cache = (
            CallCache(
                root_dir=cache_dir,
                enabled=cache_enabled,
            )
            if cache_dir is not None
            else None
        )

    def _execute(
        self,
        namespace: str,
        request: dict[str, Any],
        fn: Callable[[], Any],
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, bool]:
        if self.cache is None:
            return fn(), False

        return self.cache.call(
            namespace=namespace,
            request=request,
            fn=fn,
            metadata=metadata,
        )

    def forward(
        self,
        adapter,
        example,
        candidate: dict[str, str],
        return_cache_hit: bool = False,
    ):
        request = {
            **_example_payload(example),
            "candidate": candidate,
            "runtime_config": adapter.runtime_config,
        }

        response, cache_hit = self._execute(
            namespace="forward",
            request=request,
            fn=lambda: adapter.forward(
                example=example,
                candidate=candidate,
            ),
            metadata={
                "call_type": "forward",
            },
        )

        if return_cache_hit:
            return response, cache_hit
        return response

    def rerun(
        self,
        adapter,
        example,
        candidate: dict[str, str],
        start_agent: str,
        baseline_trace: dict[str, Any],
        return_cache_hit: bool = False,
    ):
        request = {
            **_example_payload(example),
            "candidate": candidate,
            "start_agent": start_agent,
            "baseline_trace": baseline_trace,
            "runtime_config": adapter.runtime_config,
        }

        response, cache_hit = self._execute(
            namespace="rerun",
            request=request,
            fn=lambda: adapter.rerun(
                example=example,
                candidate=candidate,
                start_agent=start_agent,
                baseline_trace=baseline_trace,
            ),
            metadata={
                "call_type": "rerun",
                "start_agent": start_agent,
            },
        )

        if return_cache_hit:
            return response, cache_hit
        return response

    def call(
        self,
        operation: str,
        request: dict[str, Any],
        fn: Callable[[], Any],
        metadata: dict[str, Any] | None = None,
        return_cache_hit: bool = False,
    ):
        """
        Generic cached operation for future method helpers.

        The request must explicitly contain every value that can change
        the result, such as:
          - model
          - rendered prompt
          - inputs
          - generation parameters
          - current candidate or prompt
        """
        if not operation.strip():
            raise ValueError("Operation name cannot be empty.")

        if not isinstance(request, dict):
            raise TypeError("Runtime request must be a dict.")

        response, cache_hit = self._execute(
            namespace=operation,
            request=request,
            fn=fn,
            metadata=metadata,
        )

        if return_cache_hit:
            return response, cache_hit
        return response
