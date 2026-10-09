"""Execute Blender Python with live GUI session preferred over headless subprocess.

Connection priority:
1. TCP socket bridge (new v2 addon - fastest, bidirectional)
2. HTTP poll bridge (legacy v1 addon)
3. Headless subprocess (blender --background, always works)
"""

from __future__ import annotations

import json
import logging
import os
import socket
import struct
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config - env vars
# ---------------------------------------------------------------------------

BRIDGE_HOST = os.environ.get("BLENDER_BRIDGE_HOST", os.environ.get("BLENDER_HOST", "127.0.0.1"))
BRIDGE_PORT = int(os.environ.get("BLENDER_BRIDGE_PORT", "10850"))
BRIDGE_TIMEOUT = int(os.environ.get("BLENDER_BRIDGE_TIMEOUT", "180"))


# ---------------------------------------------------------------------------
# v2 - TCP socket bridge (unidirectional: MCP server → Blender addon)
# ---------------------------------------------------------------------------


def _send_socket_cmd(host: str, port: int, cmd: dict, timeout: int = BRIDGE_TIMEOUT) -> dict[str, Any]:
    """Connect to the Blender bridge addon's TCP socket, send a command, and read the response.

    Wire format: 4-byte big-endian length prefix + UTF-8 JSON payload.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        payload = json.dumps(cmd).encode("utf-8")
        sock.sendall(struct.pack("!I", len(payload)) + payload)

        # Read response: 4-byte length prefix + body
        header = b""
        while len(header) < 4:
            chunk = sock.recv(4 - len(header))
            if not chunk:
                raise ConnectionError("Bridge closed connection mid-header")
            header += chunk
        body_len = struct.unpack("!I", header)[0]

        body = b""
        while len(body) < body_len:
            chunk = sock.recv(body_len - len(body))
            if not chunk:
                raise ConnectionError("Bridge closed connection mid-body")
            body += chunk

        return json.loads(body.decode("utf-8"))
    finally:
        try:
            sock.close()
        except Exception as e:
            logger.debug("Bridge socket close failed: %s", e)


async def exec_via_socket_bridge(script: str, timeout: int = BRIDGE_TIMEOUT) -> dict[str, Any] | None:
    """Try to execute via TCP socket bridge. Returns None if bridge is unreachable."""
    try:
        import asyncio

        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _send_socket_cmd(
                BRIDGE_HOST,
                BRIDGE_PORT,
                {"type": "execute_code", "params": {"code": script}},
                timeout=timeout,
            ),
        )
        inner = result.get("result", result)
        if result.get("status") == "success":
            return {
                "success": inner.get("success", True),
                "output": inner.get("output", ""),
                "error": inner.get("error"),
                "session_used": True,
                "mode": "socket",
            }
        return {
            "success": False,
            "output": "",
            "error": inner.get("error", inner.get("message", "Unknown bridge error")),
            "session_used": True,
            "mode": "socket",
        }
    except (ConnectionRefusedError, OSError) as e:
        logger.debug("Socket bridge unreachable (%s); trying next transport", e)
        return None
    except Exception as e:
        logger.warning("Socket bridge error (%s); trying next transport", e)
        return None


# ---------------------------------------------------------------------------
# v1 - HTTP poll bridge (legacy)
# ---------------------------------------------------------------------------


async def _exec_via_http_poll(script: str, script_name: str = "exec", timeout: int = 30) -> dict[str, Any] | None:
    """Try the legacy HTTP poll bridge. Returns None if unreachable."""
    try:
        from blender_mcp.app import _exec_in_blender_session

        result = await _exec_in_blender_session(script, script_name=script_name, timeout=timeout)
        if result:
            result["mode"] = "session"
        return result
    except Exception as e:
        logger.debug("HTTP poll bridge error (%s)", e)
        return None


# ---------------------------------------------------------------------------
# Fallback - headless subprocess
# ---------------------------------------------------------------------------


async def _exec_headless(script: str, script_name: str = "exec", timeout: int = 60) -> dict[str, Any]:
    from blender_mcp.utils.blender_executor import get_blender_executor

    try:
        executor = get_blender_executor()
        output = await executor.execute_script(script, script_name=script_name, timeout=timeout)
        return {
            "success": True,
            "output": output or "",
            "error": None,
            "session_used": False,
            "mode": "headless",
        }
    except Exception as exc:
        logger.error("Headless Blender execution failed for %s: %s", script_name, exc)
        return {
            "success": False,
            "output": "",
            "error": str(exc),
            "session_used": False,
            "mode": "headless",
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def execute_bpy_script(
    script: str,
    *,
    script_name: str = "exec",
    timeout: int = 60,
    prefer_session: bool = True,
    headless_fallback: bool = True,
) -> dict[str, Any]:
    """Run a bpy script preferring a live Blender session over headless subprocess.

    Connection priority:
    1. TCP socket bridge (v2 addon, default bridge port 10850)
    2. HTTP poll bridge (legacy v1 addon, /api/v1/blender/pending)
    3. Headless subprocess (blender --background)

    Returns a dict with keys: success, output, error, session_used, mode
    (``socket`` | ``session`` | ``headless`` | ``unavailable``).
    """
    if not prefer_session:
        if not headless_fallback:
            return {
                "success": False,
                "output": "",
                "error": "Session execution disabled and no fallback requested",
                "session_used": False,
                "mode": "unavailable",
            }
        return await _exec_headless(script, script_name=script_name, timeout=timeout)

    # 1. Try TCP socket bridge (fastest)
    result = await exec_via_socket_bridge(script, timeout=timeout)
    if result is not None:
        return result

    # 2. Try legacy HTTP poll bridge
    result = await _exec_via_http_poll(script, script_name=script_name, timeout=timeout)
    if result is not None:
        if result.get("session_used"):
            return result
        if not headless_fallback:
            return result

    # 3. Fall back to headless
    if not headless_fallback:
        return {
            "success": False,
            "output": "",
            "error": "No live Blender session. Start the bridge addon in Blender.",
            "session_used": False,
            "mode": "unavailable",
        }
    return await _exec_headless(script, script_name=script_name, timeout=timeout)
