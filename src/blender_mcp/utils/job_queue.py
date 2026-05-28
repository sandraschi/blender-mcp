"""In-process async job queue for long-running Blender scripts."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BlenderJob:
    id: str
    script_name: str
    status: JobStatus = JobStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    output: str = ""
    error: str | None = None
    session_used: bool = False
    mode: str | None = None
    _task: asyncio.Task | None = field(default=None, repr=False)


_jobs: dict[str, BlenderJob] = {}


def _prune_old_jobs(max_jobs: int = 100) -> None:
    if len(_jobs) <= max_jobs:
        return
    finished = sorted(
        ((jid, job) for jid, job in _jobs.items() if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)),
        key=lambda item: item[1].finished_at or 0,
    )
    for jid, _ in finished[: len(_jobs) - max_jobs]:
        _jobs.pop(jid, None)


async def submit_blender_job(
    script: str,
    *,
    script_name: str = "async_job",
    timeout: int = 600,
    prefer_session: bool = True,
) -> str:
    """Queue a Blender script and return job_id immediately."""
    from blender_mcp.utils.blender_runtime import execute_bpy_script

    job_id = str(uuid.uuid4())[:12]
    job = BlenderJob(id=job_id, script_name=script_name)
    _jobs[job_id] = job
    _prune_old_jobs()

    async def _runner() -> None:
        job.status = JobStatus.RUNNING
        job.started_at = time.time()
        try:
            result = await execute_bpy_script(
                script,
                script_name=script_name,
                timeout=timeout,
                prefer_session=prefer_session,
                headless_fallback=True,
            )
            job.output = result.get("output", "")
            job.session_used = bool(result.get("session_used"))
            job.mode = result.get("mode")
            if result.get("success"):
                job.status = JobStatus.COMPLETED
            else:
                job.status = JobStatus.FAILED
                job.error = result.get("error") or "Execution failed"
        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.error = "Job cancelled"
            raise
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error = str(exc)
            logger.exception("Blender job %s failed: %s", job_id, exc)
        finally:
            job.finished_at = time.time()

    job._task = asyncio.create_task(_runner())
    return job_id


def get_job(job_id: str) -> BlenderJob | None:
    return _jobs.get(job_id)


def job_to_dict(job: BlenderJob) -> dict[str, Any]:
    return {
        "id": job.id,
        "script_name": job.script_name,
        "status": job.status.value,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
        "output": job.output,
        "error": job.error,
        "session_used": job.session_used,
        "mode": job.mode,
    }


def list_jobs(limit: int = 20) -> list[dict[str, Any]]:
    jobs = sorted(_jobs.values(), key=lambda j: j.created_at, reverse=True)
    return [job_to_dict(j) for j in jobs[:limit]]


async def cancel_job(job_id: str) -> bool:
    job = _jobs.get(job_id)
    if not job or not job._task:
        return False
    if job.status not in (JobStatus.PENDING, JobStatus.RUNNING):
        return False
    job._task.cancel()
    try:
        await job._task
    except asyncio.CancelledError:
        pass
    job.status = JobStatus.CANCELLED
    job.finished_at = time.time()
    return True
