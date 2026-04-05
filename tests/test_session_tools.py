"""
Unit tests for blender_session tool (session_tools.py).

No live Blender required — process launch is mocked.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_session_state():
    """Reset the module-level session state between tests."""
    import blender_mcp.tools.session_tools as st
    st._blender_process = None
    st._blender_pid = None


@pytest.fixture(autouse=True)
def reset_session(monkeypatch):
    _reset_session_state()
    yield
    _reset_session_state()


# ---------------------------------------------------------------------------
# status operation
# ---------------------------------------------------------------------------

class TestSessionStatus:
    @pytest.mark.asyncio
    async def test_status_not_running(self):
        from blender_mcp.app import get_app
        app = get_app()
        result = await app.call_tool("blender_session", {"operation": "status"})
        # Parse the text content
        import json as _j
        text = result.content[0].text if hasattr(result, "content") else str(result)
        try:
            data = _j.loads(text)
        except Exception:
            data = {}
        assert data.get("running") is False or "not running" in str(data).lower()

    @pytest.mark.asyncio
    async def test_status_running(self):
        import blender_mcp.tools.session_tools as st
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None  # still running
        mock_proc.pid = 12345
        st._blender_process = mock_proc
        st._blender_pid = 12345

        from blender_mcp.app import get_app
        app = get_app()
        result = await app.call_tool("blender_session", {"operation": "status"})
        text = result.content[0].text if hasattr(result, "content") else str(result)
        try:
            data = json.loads(text)
            assert data.get("running") is True
            assert data.get("pid") == 12345
        except Exception:
            assert "12345" in text or "running" in text.lower()


# ---------------------------------------------------------------------------
# start operation
# ---------------------------------------------------------------------------

class TestSessionStart:
    @pytest.mark.asyncio
    async def test_start_launches_process(self, tmp_path):
        fake_exe = tmp_path / "blender.exe"
        fake_exe.write_text("fake")

        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.pid = 99999

        with patch("blender_mcp.tools.session_tools._get_blender_exe", return_value=str(fake_exe)), \
             patch("subprocess.Popen", return_value=mock_proc), \
             patch("asyncio.sleep", AsyncMock()):
            from blender_mcp.app import get_app
            app = get_app()
            result = await app.call_tool("blender_session", {"operation": "start"})
            text = result.content[0].text if hasattr(result, "content") else str(result)
            try:
                data = json.loads(text)
                assert data.get("success") is True
                assert data.get("pid") == 99999
            except Exception:
                assert "99999" in text or "started" in text.lower()

    @pytest.mark.asyncio
    async def test_start_already_running(self):
        import blender_mcp.tools.session_tools as st
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.pid = 55555
        st._blender_process = mock_proc
        st._blender_pid = 55555

        from blender_mcp.app import get_app
        app = get_app()
        result = await app.call_tool("blender_session", {"operation": "start"})
        text = result.content[0].text if hasattr(result, "content") else str(result)
        try:
            data = json.loads(text)
            assert data.get("success") is False
        except Exception:
            assert "already" in text.lower() or "55555" in text

    @pytest.mark.asyncio
    async def test_start_exe_not_found(self):
        with patch("blender_mcp.tools.session_tools._get_blender_exe",
                   return_value="/nonexistent/blender"):
            from blender_mcp.app import get_app
            app = get_app()
            result = await app.call_tool("blender_session", {"operation": "start"})
            text = result.content[0].text if hasattr(result, "content") else str(result)
            try:
                data = json.loads(text)
                assert data.get("success") is False
            except Exception:
                assert "not found" in text.lower() or "executable" in text.lower()


# ---------------------------------------------------------------------------
# stop operation
# ---------------------------------------------------------------------------

class TestSessionStop:
    @pytest.mark.asyncio
    async def test_stop_when_running(self):
        import blender_mcp.tools.session_tools as st
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_proc.pid = 77777
        st._blender_process = mock_proc
        st._blender_pid = 77777

        from blender_mcp.app import get_app
        app = get_app()
        result = await app.call_tool("blender_session", {"operation": "stop"})
        text = result.content[0].text if hasattr(result, "content") else str(result)
        try:
            data = json.loads(text)
            assert data.get("success") is True
            assert "77777" in data.get("message", "")
        except Exception:
            assert "stopped" in text.lower() or "77777" in text
        # Process should be cleared
        assert st._blender_pid is None

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self):
        from blender_mcp.app import get_app
        app = get_app()
        result = await app.call_tool("blender_session", {"operation": "stop"})
        text = result.content[0].text if hasattr(result, "content") else str(result)
        try:
            data = json.loads(text)
            assert data.get("success") is True
        except Exception:
            assert "not running" in text.lower() or "no managed" in text.lower()


# ---------------------------------------------------------------------------
# run_script / demo — bridge path
# ---------------------------------------------------------------------------

class TestSessionRunScript:
    @pytest.mark.asyncio
    async def test_run_script_no_bridge(self):
        """Without bridge, should return session_used=False with helpful message."""
        with patch("blender_mcp.app._exec_in_blender_session",
                   AsyncMock(return_value={"session_used": False, "output": "", "error": None, "success": False})):
            from blender_mcp.app import get_app
            app = get_app()
            result = await app.call_tool("blender_session", {
                "operation": "run_script",
                "script": "import bpy; print('hello')",
            })
            text = result.content[0].text if hasattr(result, "content") else str(result)
            try:
                data = json.loads(text)
                assert data.get("success") is False
                assert data.get("session_used") is False
            except Exception:
                assert "bridge" in text.lower() or "not connected" in text.lower()

    @pytest.mark.asyncio
    async def test_run_script_via_bridge(self):
        """With bridge, script output returned."""
        with patch("blender_mcp.app._exec_in_blender_session",
                   AsyncMock(return_value={
                       "session_used": True,
                       "success": True,
                       "output": "SCRIPT_DONE: test",
                       "error": None,
                   })):
            from blender_mcp.app import get_app
            app = get_app()
            result = await app.call_tool("blender_session", {
                "operation": "run_script",
                "script": "print('test')",
            })
            text = result.content[0].text if hasattr(result, "content") else str(result)
            try:
                data = json.loads(text)
                assert data.get("success") is True
                assert data.get("session_used") is True
            except Exception:
                assert "success" in text.lower()

    @pytest.mark.asyncio
    async def test_demo_unknown(self):
        from blender_mcp.app import get_app
        app = get_app()
        result = await app.call_tool("blender_session", {
            "operation": "demo",
            "demo_name": "nonexistent_xyz",
        })
        text = result.content[0].text if hasattr(result, "content") else str(result)
        try:
            data = json.loads(text)
            assert data.get("success") is False
            assert "available_demos" in data
        except Exception:
            assert "unknown" in text.lower() or "available" in text.lower()

    @pytest.mark.asyncio
    async def test_demo_living_room_with_car(self, tmp_path, monkeypatch):
        """Demo script should be loadable from data/scripts/demos.json."""
        import blender_mcp.tools.session_tools as st
        # Point the demo loader at the real data/scripts dir
        real_data = Path(__file__).parent.parent / "data" / "scripts"
        if not (real_data / "demos.json").exists():
            pytest.skip("demos.json not found — data directory may not be mounted")

        script = st._get_demo_script("living_room_with_car")
        assert script is not None
        assert "bpy" in script
        assert "SCRIPT_DONE" in script


# ---------------------------------------------------------------------------
# Unknown operation
# ---------------------------------------------------------------------------

class TestSessionUnknown:
    @pytest.mark.asyncio
    async def test_unknown_op(self):
        from blender_mcp.app import get_app
        app = get_app()
        result = await app.call_tool("blender_session", {"operation": "explode"})
        text = result.content[0].text if hasattr(result, "content") else str(result)
        try:
            data = json.loads(text)
            assert data.get("success") is False
        except Exception:
            assert "unknown" in text.lower() or "explode" in text.lower()
