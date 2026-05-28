"""Tests for Phase 4 validation, rendering, batch, and addon dedupe."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestPhase4ToolRegistration:
    @pytest.mark.asyncio
    async def test_phase4_tools_registered(self):
        from blender_mcp.app import get_app

        app = get_app()
        tools = await app.list_tools()
        names = {t.name for t in tools}
        assert "blender_batch" in names
        assert "blender_addons" in names
        assert "manage_blender_addons" in names

    @pytest.mark.asyncio
    async def test_blender_batch_lists_operations(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_batch", {"operation": "nope"})
        text = result.content[0].text
        assert "resize" in text
        assert "convert" in text

    @pytest.mark.asyncio
    async def test_validation_geometry_operation_exists(self):
        from blender_mcp.app import get_app

        app = get_app()
        with patch(
            "blender_mcp.handlers.mesh_validation_handler.execute_bpy_script",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "output": 'MESH_AUDIT:{"operation":"validate_geometry","status":"PASS","vertices":8}',
                    "session_used": False,
                    "mode": "headless",
                }
            ),
        ):
            result = await app.call_tool(
                "blender_validation",
                {"operation": "validate_geometry", "object_name": "Cube"},
            )
        text = result.content[0].text
        assert "validate_geometry" in text or "vertices" in text
