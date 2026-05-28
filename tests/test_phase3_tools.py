"""Tests for Phase 3 generative, geonodes, and vision refine tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestAiMeshBackends:
    def test_list_backends_structure(self):
        from blender_mcp.utils.ai_mesh_backends import list_backends

        rows = list_backends()
        names = {r["backend"] for r in rows}
        assert names == {"rodin", "tripo", "hunyuan"}
        assert all("configured" in r and "env_vars" in r for r in rows)


class TestPhase3ToolRegistration:
    @pytest.mark.asyncio
    async def test_phase3_tools_registered(self):
        from blender_mcp.app import get_app

        app = get_app()
        tools = await app.list_tools()
        names = {t.name for t in tools}
        assert "blender_ai_generate" in names
        assert "blender_geonodes" in names
        assert "blender_vision_refine" in names

    @pytest.mark.asyncio
    async def test_blender_ai_generate_list_backends(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_ai_generate", {"operation": "list_backends"})
        text = result.content[0].text
        assert "tripo" in text
        assert "rodin" in text

    @pytest.mark.asyncio
    async def test_blender_geonodes_list_node_types(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_geonodes", {"operation": "list_node_types"})
        text = result.content[0].text
        assert "GeometryNodeMeshCube" in text

    @pytest.mark.asyncio
    async def test_blender_vision_refine_unknown_operation(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("blender_vision_refine", {"operation": "nope"})
        text = result.content[0].text
        assert "review_bundle" in text


class TestVisionRefineHandler:
    @pytest.mark.asyncio
    async def test_apply_script_requires_body(self):
        from blender_mcp.handlers.vision_refine_handler import vision_apply_script

        result = await vision_apply_script(script="")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_apply_script_success(self):
        from blender_mcp.handlers.vision_refine_handler import vision_apply_script

        with patch(
            "blender_mcp.handlers.vision_refine_handler.execute_bpy_script",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "output": "ok",
                    "error": None,
                    "session_used": True,
                    "mode": "session",
                }
            ),
        ):
            result = await vision_apply_script(script="import bpy")
        assert result["success"] is True
