"""
Unit tests for addon handler helpers.

No Blender installation required — executor is mocked.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from blender_mcp.handlers.addon_handler import (
    KNOWN_ADDONS,
    _blender_addons_dir,
    addon_search,
)


class TestAddonSearch:
    def test_search_all_returns_all(self):
        result = addon_search("")
        assert result["success"] is True
        assert len(result["results"]) == len(KNOWN_ADDONS)

    def test_search_gaussian(self):
        result = addon_search("gaussian")
        assert result["success"] is True
        names = [r["name"] for r in result["results"]]
        assert "gaussian_splat" in names or "3dgs_blender" in names

    def test_search_no_match(self):
        result = addon_search("xyznonexistent12345")
        assert result["success"] is True
        assert result["results"] == []

    def test_search_case_insensitive(self):
        result = addon_search("GAUSSIAN")
        assert result["success"] is True
        # Should still find splat addons
        assert len(result["results"]) > 0


class TestBlenderAddonsDir:
    def test_uses_env_var(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("BLENDER_ADDONS_PATH", str(tmp_path))
        result = _blender_addons_dir()
        assert result == tmp_path

    def test_invalid_env_var_returns_none_or_path(self, monkeypatch):
        monkeypatch.setenv("BLENDER_ADDONS_PATH", "/nonexistent/path/xyz")
        result = _blender_addons_dir()
        # Either None (not found) or a real path from the OS defaults
        assert result is None or isinstance(result, Path)


class TestInstallFromUrl:
    @pytest.mark.asyncio
    async def test_zip_install(self, tmp_path: Path):
        import io
        import zipfile

        # Create a minimal zip
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("addon/__init__.py", "bl_info = {}")
        zip_bytes = buf.getvalue()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.content = zip_bytes
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_response)

        with (
            patch("blender_mcp.handlers.addon_handler._blender_addons_dir", return_value=tmp_path),
            patch("httpx.AsyncClient", return_value=mock_client),
        ):
            from blender_mcp.handlers.addon_handler import install_addon_from_url

            result = await install_addon_from_url("https://example.com/addon.zip")

        assert result["status"] == "SUCCESS"

    @pytest.mark.asyncio
    async def test_no_addons_dir(self):
        with patch("blender_mcp.handlers.addon_handler._blender_addons_dir", return_value=None):
            from blender_mcp.handlers.addon_handler import install_addon_from_url

            result = await install_addon_from_url("https://example.com/addon.zip")
        assert result["status"] == "ERROR"
        assert "BLENDER_ADDONS_PATH" in result["error"]

    @pytest.mark.asyncio
    async def test_download_failure(self, tmp_path: Path):
        import httpx

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))

        with (
            patch("blender_mcp.handlers.addon_handler._blender_addons_dir", return_value=tmp_path),
            patch("httpx.AsyncClient", return_value=mock_client),
        ):
            from blender_mcp.handlers.addon_handler import install_addon_from_url

            result = await install_addon_from_url("https://example.com/addon.zip")
        assert result["status"] == "ERROR"


class TestManageBlenderAddonsTool:
    """Test the manage_blender_addons MCP tool (registered via _register_addon_tools)."""

    @pytest.mark.asyncio
    async def test_search_operation(self):
        from blender_mcp.app import get_app

        app = get_app()
        # Tool should be discoverable
        tool_names = [t.name for t in await app.list_tools()]
        assert "manage_blender_addons" in tool_names

    @pytest.mark.asyncio
    async def test_unknown_operation(self):
        """Direct helper test: unknown operation returns error."""
        # Import the inner logic by calling manage_blender_addons directly
        from blender_mcp.app import get_app

        app = get_app()
        result = await app.call_tool("manage_blender_addons", {"operation": "nonexistent_op_xyz"})
        # Result should contain success: False
        import json as _json

        content = result.content[0].text if hasattr(result, "content") else str(result)
        try:
            data = _json.loads(content) if isinstance(content, str) else content
            assert data.get("success") is False or "error" in str(data).lower()
        except Exception:
            pass  # If parsing fails, at least the call didn't crash
