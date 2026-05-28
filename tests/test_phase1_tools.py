"""Tests for Phase 1 utilities and tool registration."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestBpyApiDocs:
    def test_normalize_identifier(self):
        from blender_mcp.utils.bpy_api_docs import docs_url, normalize_identifier

        assert normalize_identifier("Mesh") == "bpy.types.Mesh"
        assert normalize_identifier("bpy.ops.mesh.primitive_cube_add") == "bpy.ops.mesh.primitive_cube_add"
        assert docs_url("Mesh").endswith("bpy.types.Mesh.html")

    def test_fetch_api_doc_parses_html(self):
        from blender_mcp.utils.bpy_api_docs import fetch_api_doc

        html = "<html><head><title>Mesh</title></head><body><h1>class Mesh</h1><p>Blender mesh type.</p></body></html>"
        with patch("blender_mcp.utils.bpy_api_docs.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__.return_value.read.return_value = html.encode("utf-8")
            doc = fetch_api_doc("bpy.types.Mesh")
        assert doc["found"] == "true"
        assert "Mesh" in doc["content"]


class TestBlenderRuntime:
    @pytest.mark.asyncio
    async def test_prefers_session_when_connected(self):
        from blender_mcp.utils.blender_runtime import execute_bpy_script

        with patch(
            "blender_mcp.app._exec_in_blender_session",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "output": "OK",
                    "error": None,
                    "session_used": True,
                }
            ),
        ):
            result = await execute_bpy_script("print('hi')", script_name="test")
        assert result["mode"] == "session"
        assert result["session_used"] is True

    @pytest.mark.asyncio
    async def test_headless_fallback(self):
        from blender_mcp.utils.blender_runtime import execute_bpy_script

        with patch(
            "blender_mcp.app._exec_in_blender_session",
            new=AsyncMock(return_value={"success": False, "output": "", "error": "timeout", "session_used": False}),
        ), patch(
            "blender_mcp.utils.blender_executor.get_blender_executor",
        ) as mock_get_executor:
            mock_executor = mock_get_executor.return_value
            mock_executor.execute_script = AsyncMock(return_value="done")
            result = await execute_bpy_script("print('hi')", script_name="test")
        assert result["mode"] == "headless"
        assert result["success"] is True


class TestPhase1ToolRegistration:
    @pytest.mark.asyncio
    async def test_new_tools_registered(self):
        from blender_mcp.app import get_app

        app = get_app()
        tools = await app.list_tools()
        tool_names = {tool.name for tool in tools}
        assert "blender_shaders" in tool_names
        assert "blender_compositor" in tool_names
        assert "blender_api_docs" in tool_names

    @pytest.mark.asyncio
    async def test_blender_export_lists_new_operations(self):
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool(
            "blender_export",
            {"operation": "export_not_real", "output_path": "D:/Temp/blender_mcp_test/x.glb"},
        )
        text = result.content[0].text
        assert "export_glb" in text
        assert "export_unreal" in text
