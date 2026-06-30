"""Tests for Phase 5 sculpt tools and telemetry."""

from __future__ import annotations

from unittest.mock import patch

import pytest


class TestPhase5ToolRegistration:
    @pytest.mark.asyncio
    async def test_blender_sculpt_registered(self):
        from blender_mcp.app import get_app

        app = get_app()
        tools = await app.list_tools()
        names = {t.name for t in tools}
        assert "blender_sculpt" in names

    @pytest.mark.asyncio
    async def test_blender_sculpt_list_brushes(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_sculpt", {"operation": "list_brushes"})
        text = result.content[0].text
        assert "Grab" in text


class TestTelemetry:
    def test_metrics_init_without_prometheus(self):
        from blender_mcp.utils import telemetry

        telemetry._metrics_initialized = False
        with patch.dict("sys.modules", {"prometheus_client": None}):
            telemetry.init_metrics()
        # Should not crash when optional dep missing in patched scenario

    def test_record_tool_call_noop_when_disabled(self):
        from blender_mcp.utils.telemetry import metrics_enabled, record_tool_call

        if not metrics_enabled():
            record_tool_call("test_tool", "success", 0.1)

    @pytest.mark.asyncio
    async def test_tool_wrapper_records_calls(self):
        from blender_mcp.app import get_app
        from blender_mcp.utils.telemetry import _metrics_initialized

        get_app()
        if not _metrics_initialized:
            pytest.skip("metrics not initialized in this test session")

        class FakeApp:
            def __init__(self) -> None:
                self.calls = 0

            async def call_tool(self, name: str, arguments=None, **kwargs):
                self.calls += 1
                return {"ok": True}

        from blender_mcp.utils import telemetry

        app = FakeApp()
        telemetry.install_tool_call_wrapper(app)
        await app.call_tool("blender_jobs", {"operation": "list"})
        assert app.calls == 1
