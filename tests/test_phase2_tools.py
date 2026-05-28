"""Tests for Phase 2 async jobs and mesh edit registration."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestJobQueue:
    @pytest.mark.asyncio
    async def test_submit_and_complete(self):
        from blender_mcp.utils.job_queue import JobStatus, get_job, submit_blender_job

        with patch(
            "blender_mcp.utils.blender_runtime.execute_bpy_script",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "output": "done",
                    "error": None,
                    "session_used": True,
                    "mode": "session",
                }
            ),
        ):
            job_id = await submit_blender_job("print('x')", script_name="test")
            job = get_job(job_id)
            assert job is not None
            # Wait for background task
            if job._task:
                await job._task
            assert job.status == JobStatus.COMPLETED
            assert job.output == "done"


class TestPhase2ToolRegistration:
    @pytest.mark.asyncio
    async def test_blender_jobs_registered(self):
        from blender_mcp.app import get_app

        app = get_app()
        tools = await app.list_tools()
        names = {t.name for t in tools}
        assert "blender_jobs" in names

    @pytest.mark.asyncio
    async def test_blender_jobs_list_operation(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_jobs", {"operation": "list"})
        text = result.content[0].text
        assert "jobs" in text
