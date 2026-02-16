from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from gateway.jobs import DiskJobStore, Job

app = FastAPI(title="superhuman-gateway", version="0.1.0")
store = DiskJobStore()


class CreateJobRequest(BaseModel):
    goal: str = Field(min_length=1, description="High-level goal for this job")


class JobResponse(BaseModel):
    id: str
    goal: str
    status: str
    created_at: str

    @classmethod
    def from_job(cls, job: Job) -> "JobResponse":
        return cls(id=job.id, goal=job.goal, status=job.status, created_at=job.created_at)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/jobs", response_model=JobResponse, status_code=201)
def create_job(payload: CreateJobRequest) -> JobResponse:
    try:
        job = store.create_job(payload.goal)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Unable to persist job") from exc
    return JobResponse.from_job(job)


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    try:
        job = store.get_job(job_id)
    except (OSError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=500, detail="Unable to load job") from exc

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.from_job(job)
