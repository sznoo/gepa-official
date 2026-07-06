import json
import threading
from pathlib import Path
from typing import Any


class JsonlLogger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def write(self, record: dict[str, Any]):
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


class HotpotAnalysisLoggers:
    def __init__(self, log_dir: str | Path):
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        self.rollout = JsonlLogger(log_dir / "rollout_traces.jsonl")
        self.feedback = JsonlLogger(log_dir / "feedback_examples.jsonl")
        self.proposal = JsonlLogger(log_dir / "proposal_events.jsonl")

    def write_rollout(self, record: dict[str, Any]):
        self.rollout.write(record)

    def write_feedback(self, record: dict[str, Any]):
        self.feedback.write(record)

    def write_proposal(self, record: dict[str, Any]):
        self.proposal.write(record)