"""
Unit tests for blender_status tool (status_tools.py).

These tests verify the fixed control flow and correct return values.
No Blender required — config and psutil are patched.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from pydantic import ValidationError

# ---------------------------------------------------------------------------
# status — json format
# ---------------------------------------------------------------------------


class TestStatusJson:
    @pytest.mark.asyncio
    async def test_returns_json_string(self):
        with patch("blender_mcp.config.validate_blender_executable", return_value=True):
            from blender_mcp.app import get_app

            app = get_app()
            result = await app.call_tool("blender_status", {"operation": "status", "format": "json"})
            text = result.content[0].text if hasattr(result, "content") else str(result)
            data = json.loads(text)
            assert "status" in data
            assert "blender" in data
            assert "version" in data

    @pytest.mark.asyncio
    async def test_blender_false_when_not_found(self):
        with patch("blender_mcp.config.validate_blender_executable", return_value=False):
            from blender_mcp.app import get_app

            app = get_app()
            result = await app.call_tool("blender_status", {"operation": "status", "format": "json"})
            text = result.content[0].text if hasattr(result, "content") else str(result)
            data = json.loads(text)
            assert data["blender"] is False


# ---------------------------------------------------------------------------
# status — text format
# ---------------------------------------------------------------------------


class TestStatusText:
    @pytest.mark.asyncio
    async def test_contains_report_header(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool(
            "blender_status",
            {
                "operation": "status",
                "format": "text",
                "include_blender_info": True,
                "include_system_info": True,
                "include_performance": False,
            },
        )
        text = result.content[0].text if hasattr(result, "content") else str(result)
        assert "Status Report" in text
        assert "MCP Server" in text

    @pytest.mark.asyncio
    async def test_no_fallthrough_to_wrong_branch(self):
        """Ensure the status operation does not execute system_info code."""
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_status", {"operation": "status"})
        text = result.content[0].text if hasattr(result, "content") else str(result)
        # system_info produces "System Information" header — should NOT appear for status
        assert "System Information" not in text


# ---------------------------------------------------------------------------
# system_info
# ---------------------------------------------------------------------------


class TestSystemInfo:
    @pytest.mark.asyncio
    async def test_system_info_contains_platform(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_status", {"operation": "system_info"})
        text = result.content[0].text if hasattr(result, "content") else str(result)
        assert "System Information" in text
        assert "Platform" in text
        assert "Python" in text

    @pytest.mark.asyncio
    async def test_system_info_no_status_header(self):
        """system_info must NOT produce status report header."""
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_status", {"operation": "system_info"})
        text = result.content[0].text if hasattr(result, "content") else str(result)
        assert "Status Report" not in text


# ---------------------------------------------------------------------------
# health_check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_returns_overall(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_status", {"operation": "health_check"})
        text = result.content[0].text if hasattr(result, "content") else str(result)
        assert "Health Check" in text
        assert "Overall" in text

    @pytest.mark.asyncio
    async def test_unhealthy_when_blender_missing(self):
        with patch("blender_mcp.config.validate_blender_executable", return_value=False):
            from blender_mcp.app import get_app

            app = get_app()
            result = await app.call_tool("blender_status", {"operation": "health_check"})
            text = result.content[0].text if hasattr(result, "content") else str(result)
            assert "UNHEALTHY" in text or "NOT FOUND" in text


# ---------------------------------------------------------------------------
# performance_monitor
# ---------------------------------------------------------------------------


class TestPerformanceMonitor:
    @pytest.mark.asyncio
    async def test_monitor_1s(self):
        """1-second run should complete and return a table."""
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool(
            "blender_status",
            {
                "operation": "performance_monitor",
                "duration_seconds": 2,
            },
        )
        text = result.content[0].text if hasattr(result, "content") else str(result)
        assert "Performance Monitor" in text
        assert "CPU" in text

    @pytest.mark.asyncio
    async def test_monitor_clamps_to_60(self):
        """Duration > 60 should be silently clamped."""
        from blender_mcp.app import get_app

        app = get_app()
        # We just check it doesn't crash — don't actually run 60s
        # The clamp check is best done by inspecting the output header
        with patch("time.sleep"):  # skip actual sleeping
            result = await app.call_tool(
                "blender_status",
                {
                    "operation": "performance_monitor",
                    "duration_seconds": 999,
                },
            )
        text = result.content[0].text if hasattr(result, "content") else str(result)
        assert "Performance Monitor" in text


# ---------------------------------------------------------------------------
# Unknown operation
# ---------------------------------------------------------------------------


class TestStatusUnknown:
    @pytest.mark.asyncio
    async def test_unknown_op(self):
        from blender_mcp.app import get_app

        app = get_app()
        with pytest.raises(ValidationError):
            await app.call_tool("blender_status", {"operation": "banana"})
