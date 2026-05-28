"""Execute Blender Python with live GUI session preferred over headless subprocess."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def execute_bpy_script(
    script: str,
    *,
    script_name: str = "exec",
    timeout: int = 60,
    prefer_session: bool = True,
    headless_fallback: bool = True,
) -> dict[str, Any]:
    """Run a bpy script in a live Blender session when the bridge is connected.

    Falls back to headless ``BlenderExecutor`` when no session is available and
    ``headless_fallback`` is True.

    Returns a dict with keys: success, output, error, session_used, mode
    (``session`` | ``headless`` | ``unavailable``).
    """
    if prefer_session:
        try:
            from blender_mcp.app import _exec_in_blender_session

            session_result = await _exec_in_blender_session(
                script, script_name=script_name, timeout=timeout
            )
            if session_result.get("session_used"):
                return {
                    "success": session_result.get("success", False),
                    "output": session_result.get("output", ""),
                    "error": session_result.get("error"),
                    "session_used": True,
                    "mode": "session",
                }
            if not headless_fallback:
                return {
                    "success": False,
                    "output": "",
                    "error": session_result.get(
                        "error",
                        "No live Blender session. Start blender_session and enable the bridge addon.",
                    ),
                    "session_used": False,
                    "mode": "unavailable",
                }
            logger.info(
                "Live Blender session not connected; falling back to headless execution for %s",
                script_name,
            )
        except Exception as exc:
            if not headless_fallback:
                return {
                    "success": False,
                    "output": "",
                    "error": str(exc),
                    "session_used": False,
                    "mode": "unavailable",
                }
            logger.warning("Session bridge error (%s); using headless fallback", exc)

    try:
        from blender_mcp.utils.blender_executor import get_blender_executor

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
