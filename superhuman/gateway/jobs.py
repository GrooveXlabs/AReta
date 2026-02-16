from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import Lock
from uuid import uuid4

DATA_JOBS_DIR = Path(__file__).resolve().parents[2] / "data" / "jobs"


class JobState(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"
    FAILED = "FAILED"


@dataclass(slots=True)
class Job:
    id: str
    goal: str
    status: JobState
    created_at: str


class DiskJobStore:
    """Thread-safe JSON-backed job storage with per-job audit logs."""

    def __init__(self, jobs_dir: Path = DATA_JOBS_DIR) -> None:
        self._jobs_dir = jobs_dir
        self._lock = Lock()

    def create_job(self, goal: str) -> Job:
        job = Job(
            id=str(uuid4()),
            goal=goal,
            status=JobState.CREATED,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._jobs_dir.mkdir(parents=True, exist_ok=True)
            self._write_job_file(job)
            self._append_audit(
                job.id,
                "JOB_CREATED",
                f'goal="{job.goal}" status={job.status}',
            )
        return job

    def get_job(self, job_id: str) -> Job | None:
        job_file = self._job_file(job_id)
        if not job_file.exists():
            return None

        with self._lock:
            payload = json.loads(job_file.read_text(encoding="utf-8"))

        return Job(
            id=str(payload["id"]),
            goal=str(payload["goal"]),
            status=JobState(str(payload["status"])),
            created_at=str(payload["created_at"]),
        )


    def update_job_status(self, job_id: str, next_state: JobState) -> Job | None:
        job = self.get_job(job_id)
        if job is None:
            return None

        previous_state = job.status
        job.status = next_state

        with self._lock:
            self._write_job_file(job)
            self._append_audit(
                job.id,
                "JOB_UPDATED",
                f"status_transition={previous_state}->{next_state}",
            )
        return job

    def _job_file(self, job_id: str) -> Path:
        return self._jobs_dir / f"{job_id}.json"

    def _audit_file(self, job_id: str) -> Path:
        return self._jobs_dir / f"{job_id}.log"

    def _write_job_file(self, job: Job) -> None:
        self._job_file(job.id).write_text(
            json.dumps(asdict(job), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _append_audit(self, job_id: str, event_type: str, details: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        line = f"{timestamp} event={event_type} {details}\n"
        with self._audit_file(job_id).open("a", encoding="utf-8") as handle:
            handle.write(line)
