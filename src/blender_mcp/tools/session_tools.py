"""
Blender session management tools for Blender MCP.

Exposes a `blender_session` portmanteau tool for:
- start: launch Blender GUI (with optional .blend file)
- stop: kill the managed Blender GUI process
- status: check if a managed session is running
- run_script: send a Python script to the running GUI via the bridge
- demo: run a built-in demo scene in Blender

The session bridge addon (docs/blender_bridge_addon.py) is required for
run_script and demo operations — the addon provides the /api/v1/blender/exec
endpoint that allows the MCP server to execute code inside the live session.
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Single managed Blender GUI process (one at a time)
_blender_process: Optional[subprocess.Popen] = None
_blender_pid: Optional[int] = None


def _get_blender_exe() -> str:
    from blender_mcp.config import BLENDER_EXECUTABLE
    return BLENDER_EXECUTABLE


def _is_running() -> bool:
    global _blender_process
    if _blender_process is None:
        return False
    return _blender_process.poll() is None


def _register_session_tools() -> None:
    from blender_mcp.app import get_app
    app = get_app()

    @app.tool
    async def blender_session(
        operation: str = "status",
        blend_file: str = "",
        script: str = "",
        script_name: str = "mcp_script",
        demo_name: str = "living_room_with_car",
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Manage a Blender GUI session from the MCP server.

        Operations:
        - status: check whether a Blender GUI is running under MCP control
        - start: launch Blender GUI (optionally opening a .blend file)
        - stop: kill the managed Blender GUI process
        - run_script: execute a Python snippet in the running Blender session
          (requires the bridge addon to be enabled in Blender)
        - demo: run a named built-in demo in Blender via the bridge
          Available demos: living_room_with_car, driver_training, garden, house_interior

        Args:
            operation: status | start | stop | run_script | demo
            blend_file: for start — path to a .blend file to open (optional)
            script: for run_script — Python code to execute in Blender
            script_name: for run_script — label for the script
            demo_name: for demo — which demo to run
            timeout: for run_script/demo — seconds to wait for bridge response

        Returns:
            Dict with success, message, and operation-specific fields.
        """
        global _blender_process, _blender_pid

        try:
            if operation == "status":
                running = _is_running()
                return {
                    "success": True,
                    "running": running,
                    "pid": _blender_pid if running else None,
                    "message": f"Blender GUI {'is running' if running else 'is not running'}"
                               + (f" (PID {_blender_pid})" if running else ""),
                    "bridge_hint": (
                        "Enable the bridge addon in Blender (Properties > Scene > Blender MCP Bridge > Start) "
                        "to allow run_script and demo operations."
                        if running else ""
                    ),
                }

            elif operation == "start":
                if _is_running():
                    return {
                        "success": False,
                        "message": f"Blender GUI is already running (PID {_blender_pid}). "
                                   "Use operation='stop' first, or operation='status' to check.",
                    }

                exe = _get_blender_exe()
                if not Path(exe).exists():
                    return {
                        "success": False,
                        "message": f"Blender executable not found: {exe}. "
                                   "Set BLENDER_EXECUTABLE env var to the correct path.",
                    }

                cmd = [exe, "--enable-autoexec"]
                if blend_file and Path(blend_file).exists():
                    cmd.append(blend_file)

                # Launch detached (no --background = opens GUI)
                _blender_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                _blender_pid = _blender_process.pid

                await asyncio.sleep(1)  # brief yield to let process start
                if not _is_running():
                    return {"success": False, "message": "Blender process exited immediately."}

                return {
                    "success": True,
                    "pid": _blender_pid,
                    "message": (
                        f"Blender GUI started (PID {_blender_pid})."
                        + (f" Opened: {blend_file}" if blend_file else "")
                        + "\n\nNext: enable the bridge addon in Blender:\n"
                        "  1. Edit > Preferences > Add-ons > Install > select docs/blender_bridge_addon.py\n"
                        "  2. Enable 'Blender MCP Session Bridge'\n"
                        "  3. Properties > Scene > Blender MCP Bridge > Start Bridge\n"
                        "  4. Then use operation='demo' or operation='run_script'."
                    ),
                }

            elif operation == "stop":
                if not _is_running():
                    return {"success": True, "message": "No managed Blender GUI was running."}

                pid = _blender_pid
                try:
                    _blender_process.terminate()
                    try:
                        _blender_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        _blender_process.kill()
                        _blender_process.wait(timeout=5)
                except Exception as e:
                    return {"success": False, "message": f"Failed to stop Blender: {e}"}

                _blender_process = None
                _blender_pid = None
                return {"success": True, "message": f"Blender GUI (PID {pid}) stopped."}

            elif operation == "run_script":
                if not script.strip():
                    return {"success": False, "message": "script is required for run_script"}

                result = await _exec_via_bridge(script, script_name, timeout)
                return result

            elif operation == "demo":
                demo_script = _get_demo_script(demo_name)
                if demo_script is None:
                    available = ["living_room_with_car", "driver_training", "garden", "house_interior"]
                    return {
                        "success": False,
                        "message": f"Unknown demo '{demo_name}'",
                        "available_demos": available,
                    }

                result = await _exec_via_bridge(demo_script, f"demo_{demo_name}", timeout)
                if result["success"]:
                    result["message"] = f"Demo '{demo_name}' executed in Blender. " + result.get("message", "")
                return result

            else:
                return {
                    "success": False,
                    "message": f"Unknown operation '{operation}'",
                    "available_operations": ["status", "start", "stop", "run_script", "demo"],
                }

        except Exception as e:
            logger.exception(f"blender_session '{operation}' failed: {e}")
            return {"success": False, "message": f"Operation failed: {e}", "operation": operation}


async def _exec_via_bridge(script: str, script_name: str, timeout: int) -> Dict[str, Any]:
    """Send a script to the Blender bridge and wait for the result."""
    try:
        from blender_mcp.app import _exec_in_blender_session
        result = await _exec_in_blender_session(script, script_name=script_name, timeout=timeout)
        if result["session_used"]:
            return {
                "success": result["success"],
                "message": result.get("error") or "Script executed successfully.",
                "output": result.get("output", ""),
                "session_used": True,
            }
        else:
            return {
                "success": False,
                "message": (
                    "Bridge not connected. Start Blender with operation='start', "
                    "then enable the bridge addon (docs/blender_bridge_addon.py) "
                    "and click 'Start Bridge' in Properties > Scene."
                ),
                "session_used": False,
            }
    except Exception as e:
        return {"success": False, "message": str(e), "session_used": False}


def _get_demo_script(demo_name: str) -> Optional[str]:
    """Return the bpy script for the named demo."""
    data_dir = Path(__file__).parent.parent.parent.parent / "data" / "scripts"
    demo_file = data_dir / "demos.json"
    if demo_file.exists():
        try:
            with open(demo_file, encoding="utf-8") as f:
                demos = json.load(f)
            for d in demos:
                if d.get("name") == demo_name:
                    return d.get("script")
        except Exception as e:
            logger.warning(f"Could not load demos.json: {e}")
    return None


_register_session_tools()
