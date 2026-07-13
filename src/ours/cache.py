# /home/jinwoo/gepa-official/src/ours/cache.py
import hashlib
import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


def _to_jsonable(value: Any):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]

    if isinstance(value, set):
        items = [_to_jsonable(item) for item in value]
        return sorted(
            items,
            key=lambda item: json.dumps(
                item,
                sort_keys=True,
                ensure_ascii=False,
            ),
        )

    if isinstance(value, dict):
        return {
            str(key): _to_jsonable(item)
            for key, item in value.items()
        }

    if hasattr(value, "_store"):
        return _to_jsonable(value._store)

    if hasattr(value, "items"):
        try:
            return {
                str(key): _to_jsonable(item)
                for key, item in value.items()
            }
        except Exception:
            pass

    return str(value)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _to_jsonable(value),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _normalize_namespace(namespace: str) -> str:
    namespace = re.sub(
        r"[^a-zA-Z0-9_.-]+",
        "_",
        namespace.strip(),
    )
    if not namespace:
        raise ValueError("Cache namespace cannot be empty.")
    return namespace


class CallCache:
    """
    File-based call-level cache.

    Each unique (namespace, request) pair is stored as one JSON file:

        <root>/<namespace>/<sha256>.json

    The caller must include all behavior-changing values in request:
      - model
      - prompt
      - inputs
      - generation parameters
      - candidate
      - runtime configuration
    """

    def __init__(
        self,
        root_dir: str | Path,
        enabled: bool = True,
    ):
        self.root_dir = Path(root_dir)
        self.enabled = enabled

        self._locks: dict[str, threading.RLock] = {}
        self._locks_guard = threading.Lock()

        if self.enabled:
            self.root_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

    def make_key(
        self,
        namespace: str,
        request: Any,
    ) -> str:
        namespace = _normalize_namespace(namespace)

        payload = _canonical_json({
            "namespace": namespace,
            "request": request,
        })

        return hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

    def path_for(
        self,
        namespace: str,
        request: Any,
    ) -> Path:
        namespace = _normalize_namespace(namespace)
        key = self.make_key(namespace, request)

        return self.root_dir / namespace / f"{key}.json"

    def _lock_for(self, path: Path) -> threading.RLock:
        key = str(path)

        with self._locks_guard:
            if key not in self._locks:
                self._locks[key] = threading.RLock()
            return self._locks[key]

    def get(
        self,
        namespace: str,
        request: Any,
    ) -> tuple[bool, Any]:
        if not self.enabled:
            return False, None

        path = self.path_for(namespace, request)

        if not path.exists():
            return False, None

        record = json.loads(path.read_text())
        return True, record["response"]

    def put(
        self,
        namespace: str,
        request: Any,
        response: Any,
        metadata: dict[str, Any] | None = None,
    ) -> Path | None:
        if not self.enabled:
            return None

        namespace = _normalize_namespace(namespace)
        path = self.path_for(namespace, request)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        key = self.make_key(namespace, request)

        record = {
            "schema_version": 1,
            "namespace": namespace,
            "key": key,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "request": _to_jsonable(request),
            "response": _to_jsonable(response),
            "metadata": _to_jsonable(metadata or {}),
        }

        lock = self._lock_for(path)

        with lock:
            temp_path = path.with_suffix(
                f".{os.getpid()}.{threading.get_ident()}.tmp"
            )
            temp_path.write_text(
                json.dumps(
                    record,
                    indent=2,
                    ensure_ascii=False,
                )
            )
            os.replace(temp_path, path)

        return path

    def call(
        self,
        namespace: str,
        request: Any,
        fn: Callable[[], Any],
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Any, bool]:
        """
        Return:
            response, cache_hit
        """
        if not self.enabled:
            return fn(), False

        path = self.path_for(namespace, request)
        lock = self._lock_for(path)

        with lock:
            hit, response = self.get(
                namespace,
                request,
            )
            if hit:
                return response, True

            response = fn()

            self.put(
                namespace=namespace,
                request=request,
                response=response,
                metadata=metadata,
            )

            return _to_jsonable(response), False
