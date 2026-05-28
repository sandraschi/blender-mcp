"""Async Blender job MCP tools."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _register_job_tools() -> None:
    from blender_mcp.app import get_app
    from blender_mcp.utils.job_queue import cancel_job, get_job, job_to_dict, list_jobs, submit_blender_job

    app = get_app()

    @app.tool
    async def blender_jobs(
        operation: str = "status",
        job_id: str = "",
        script: str = "",
        script_name: str = "async_job",
        timeout: int = 600,
        prefer_session: bool = True,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Async job queue for long-running Blender Python scripts (renders, bakes, sims).

        Operations:
        - submit: queue script, returns job_id immediately
        - status: poll job by job_id
        - list: recent jobs
        - cancel: cancel pending/running job
        """
        try:
            if operation == "submit":
                if not script.strip():
                    return {"success": False, "error": "script is required for submit"}
                new_id = await submit_blender_job(
                    script,
                    script_name=script_name,
                    timeout=timeout,
                    prefer_session=prefer_session,
                )
                return {"success": True, "job_id": new_id, "status": "pending"}

            if operation == "status":
                if not job_id:
                    return {"success": False, "error": "job_id is required for status"}
                job = get_job(job_id)
                if not job:
                    return {"success": False, "error": f"Unknown job_id: {job_id}"}
                data = job_to_dict(job)
                data["success"] = job.status.value in ("completed", "running", "pending")
                return data

            if operation == "list":
                return {"success": True, "jobs": list_jobs(limit=limit)}

            if operation == "cancel":
                if not job_id:
                    return {"success": False, "error": "job_id is required for cancel"}
                ok = await cancel_job(job_id)
                return {"success": ok, "job_id": job_id, "cancelled": ok}

            return {
                "success": False,
                "error": f"Unknown operation '{operation}'",
                "available_operations": ["submit", "status", "list", "cancel"],
            }
        except Exception as exc:
            logger.exception("blender_jobs failed: %s", exc)
            return {"success": False, "error": str(exc), "operation": operation}


_register_job_tools()
