from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Literal
from uuid import uuid4


JobStatus = Literal["queued"]


@dataclass(slots=True)
class Job:
    id: str
    goal: str
    status: JobStatus
    created_at: str


class InMemoryJobStore:
    """Thread-safe in-memory store for job metadata."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = Lock()

    def create_job(self, goal: str) -> Job:
        job = Job(
            id=str(uuid4()),
            goal=goal,
            status="queued",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get_job(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)
