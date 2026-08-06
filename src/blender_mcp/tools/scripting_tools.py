"""
Script execution tool for Blender MCP webapp.

Exposes script_execute (webapp calls with { code }) so the bridge can invoke it.
"""

import json
import logging

from blender_mcp.app import get_app
from blender_mcp.compat import *
from blender_mcp.exceptions import BlenderNotFoundError, BlenderScriptError

logger = logging.getLogger(__name__)

_READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
_MUTATING = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}
_DESTRUCTIVE = {"readOnlyHint": False, "destructiveHint": True, "idempotentHint": False, "openWorldHint": False}


def _register_scripting_tools():
    app = get_app()

    @app.tool(annotations=_MUTATING)
    async def script_execute(code: str) -> str:
        """
        Execute Python script in Blender (headless).

        Args:
            code: Python script source (Blender/bpy API).

        Returns:
            JSON string with keys: output (str), success (bool).

        ## Return Format
        Standard dict with keys: success, message, data

        ## Examples
        ```python
        await call_tool("script_execute", {"code": "import bpy; ..."})
        ```
        """
        if not code or not code.strip():
            return json.dumps({"output": "Empty script.", "success": False})

        try:
            from blender_mcp.utils.blender_executor import get_blender_executor

            executor = get_blender_executor()
            output = await executor.execute_script(code)
            return json.dumps({"output": output or "Script completed.", "success": True})
        except BlenderNotFoundError as e:
            logger.warning("script_execute: Blender not found: %s", e)
            return json.dumps({"output": str(e), "success": False})
        except BlenderScriptError as e:
            logger.warning("script_execute: script error: %s", e)
            return json.dumps({"output": getattr(e, "error", str(e)), "success": False})
        except Exception as e:
            logger.exception("script_execute: unexpected error")
            return json.dumps({"output": str(e), "success": False})


_register_scripting_tools()
