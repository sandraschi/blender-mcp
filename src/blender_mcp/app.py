"""FastMCP application instance for Blender MCP server."""

# Import from our compatibility module first
import json
import logging
import os
import subprocess
from pathlib import Path

from blender_mcp.compat import Any, Dict, List

# Logger initialization
logger = logging.getLogger(__name__)

# Initialize FastMCP application with lazy tool discovery
app = None


def get_app():
    """Get or create the FastMCP application instance with lazy initialization."""

    global app
    if app is None:
        from fastmcp import FastMCP

        from blender_mcp import __version__

        app = FastMCP(
            name="blender-mcp",
            version=__version__,
            instructions="""You are Blender MCP, a comprehensive FastMCP 3.1.1 server for 3D creation and animation using Blender.

FASTMCP 3.2.0 FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling with tools (SEP-1577) for agentic workflows and complex 3D operations
- Native Prompts for standard 3D optimization and creation templates
- Formalized Skills for autonomous modeling and pipeline automation
- Portmanteau design preventing tool explosion while maintaining full functionality
- CodeMode (BM25 tool discovery) for large tool sets

CORE CAPABILITIES:
- 3D Modeling: Create, modify, and manipulate 3D objects and meshes
- Animation: Set up keyframes, create motion paths, and manage timelines
- Rendering: Configure render settings, materials, lighting, and output
- Scene Management: Organize objects, collections, and scene hierarchies
- Materials & Textures: Create and apply materials, textures, and shaders
- Import/Export: Work with various 3D file formats and interchange standards

CONVERSATIONAL FEATURES:
- Tools return natural language responses alongside structured data
- Sampling allows autonomous orchestration of complex 3D workflows
- Agentic capabilities for intelligent content creation and management

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean and 'message' for conversational responses
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields and natural language summaries

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.
""",
        )

        # Import here to prevent circular imports
        from blender_mcp.tools import discover_tools

        # Discover and register all tools
        discover_tools()

        # Handlers are registered via discover_tools() and specific registration
        # logic within tool modules.
        from blender_mcp.tools import scene_tools

        scene_tools.register(app)

        # Register agentic workflow tools
        from blender_mcp.agentic import register_agentic_tools

        register_agentic_tools()

        # Register Prompts
        from blender_mcp.prompts import register_prompts

        register_prompts()

        # Register resources
        _register_resources(app)

        # Fleet Discovery API + Blender session bridge
        _register_fleet_api(app)

    return app


# ---------------------------------------------------------------------------
# In-process session task queue for the Blender bridge
# Maps task_id -> {"script", "result", "done"}
# ---------------------------------------------------------------------------
_session_tasks: Dict[str, Any] = {}


async def _exec_in_blender_session(script: str, script_name: str = "exec", timeout: int = 30) -> Dict[str, Any]:
    """Post a script to a connected Blender session and wait for the result.

    Returns {"success": bool, "output": str, "error": str|null, "session_used": bool}
    If no session is connected within timeout seconds, returns session_used=False.
    """
    import asyncio
    import uuid

    task_id = str(uuid.uuid4())[:8]
    _session_tasks[task_id] = {
        "id": task_id,
        "script": script,
        "script_name": script_name,
        "result": None,
        "done": False,
    }

    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        await asyncio.sleep(0.5)
        task = _session_tasks.get(task_id)
        if task and task["done"]:
            result = task["result"] or {}
            _session_tasks.pop(task_id, None)
            return {
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "error": result.get("error"),
                "session_used": True,
            }

    # Timeout — clean up
    _session_tasks.pop(task_id, None)
    return {
        "success": False,
        "output": "",
        "error": "Blender session timed out. Is the bridge addon running in Blender?",
        "session_used": False,
    }


def _register_fleet_api(app):
    """Register the fleet launch API and the Blender session bridge."""
    from pydantic import BaseModel
    from starlette.requests import Request
    from starlette.responses import JSONResponse

    from blender_mcp import __version__

    class LaunchRequest(BaseModel):
        repo_path: str
        port: int
        env: Dict[str, str] = {}

    @app.custom_route("/api/v1/fleet/launch", methods=["POST"])
    async def launch_fleet_app(request: Request):
        """Standardized endpoint to launch the Fleet UI/Backend."""
        try:
            body = await request.json()
            req = LaunchRequest.model_validate(body)

            launch_script = os.path.join(req.repo_path, "start.ps1")
            if not os.path.exists(launch_script):
                return JSONResponse({"error": f"Launch script not found: {launch_script}"}, status_code=404)

            cmd = f'conhost --pwsh -c "powershell -ExecutionPolicy Bypass -File {launch_script}"'
            subprocess.Popen(cmd, shell=True, cwd=req.repo_path, env={**os.environ, **req.env})

            return JSONResponse(
                {
                    "status": "launched",
                    "message": "Fleet launch sequence initiated",
                    "port": req.port,
                    "pid_discovery_url": f"/api/v1/fleet/status?port={req.port}",
                }
            )
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    @app.custom_route("/tool", methods=["POST"])
    async def mcp_tool_bridge(request: Request):
        """Bridge endpoint for webapp and Blender addons to call MCP tools.

        Blender session bridge usage — paste this in Blender's Script Editor
        to call save/backup operations from within the running Blender session:

            import urllib.request, json
            data = json.dumps({"tool": "manage_object_repo",
                               "params": {"operation": "save",
                                          "object_name": "Cube",
                                          "category": "general",
                                          "quality_rating": 7}}).encode()
            req = urllib.request.Request(
                "http://127.0.0.1:10849/tool",
                data=data, headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req, timeout=30)
            print(json.loads(resp.read()))
        """
        try:
            body = await request.json()
            tool_name = body.get("tool")
            params = body.get("params", {})

            if not tool_name:
                return JSONResponse({"success": False, "error": "Missing 'tool' in request"}, status_code=400)

            try:
                result = await app.call_tool(tool_name, params)
            except Exception as tool_e:
                logger.error(f"Tool {tool_name} call error: {tool_e}")
                return JSONResponse(
                    {
                        "success": False,
                        "data": None,
                        "message": f"Tool execution error: {tool_e!s}",
                        "error": str(tool_e),
                    },
                    status_code=500,
                )

            # FastMCP 3.x result unpacking
            mcp_result = result.to_mcp_result()
            is_error = False
            content_list = []

            if isinstance(mcp_result, tuple) and len(mcp_result) >= 2:
                content_list = mcp_result[0]
                is_error = mcp_result[1]
            else:
                content_list = getattr(result, "content", [])

            data = None
            if content_list:
                text = getattr(content_list[0], "text", str(content_list[0]))
                try:
                    data = json.loads(text)
                except Exception:
                    data = text

            tool_succeeded = not is_error and data is not None
            return JSONResponse(
                {
                    "success": tool_succeeded,
                    "data": data,
                    "message": "Tool execution successful" if tool_succeeded else "Tool execution failed",
                    "error": None if tool_succeeded else (str(data) if data is not None else "No content"),
                },
            )
        except Exception as e:
            logger.error(f"Bridge tool call failed: {e}")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @app.custom_route("/api/v1/blender/exec", methods=["POST"])
    async def blender_session_exec(request: Request):
        """Queue a Blender Python script for execution in a connected Blender session.

        Body: {"script": "<python code>", "script_name": "optional_label"}

        The script will be picked up by the blender_bridge_addon.py polling loop,
        executed inside the live Blender session, and the result returned via
        /api/v1/blender/result. Poll /api/v1/blender/pending to retrieve queued tasks.

        Returns: {"success": bool, "id": str, "queued": bool}
        """
        import uuid

        try:
            body = await request.json()
            script = body.get("script", "").strip()
            script_name = body.get("script_name", "exec")

            if not script:
                return JSONResponse({"success": False, "error": "Empty script"}, status_code=400)

            task_id = str(uuid.uuid4())[:8]
            _session_tasks[task_id] = {
                "id": task_id,
                "script": script,
                "script_name": script_name,
                "result": None,
                "done": False,
            }
            return JSONResponse({"success": True, "id": task_id, "queued": True})

        except Exception as e:
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @app.custom_route("/api/v1/blender/pending", methods=["GET"])
    async def blender_session_pending(request: Request):
        """Return the oldest pending Blender script task (for the bridge addon to poll).

        Returns: {"script": str, "id": str} or {} if nothing pending.
        """
        for task_id, task in _session_tasks.items():
            if not task["done"] and task["result"] is None:
                return JSONResponse({"id": task_id, "script": task["script"], "script_name": task["script_name"]})
        return JSONResponse({})

    @app.custom_route("/api/v1/blender/result", methods=["POST"])
    async def blender_session_result(request: Request):
        """Receive execution result from the bridge addon.

        Body: {"id": str, "output": str, "success": bool, "error": str|null}
        """
        try:
            body = await request.json()
            task_id = body.get("id")
            if task_id and task_id in _session_tasks:
                _session_tasks[task_id]["result"] = body
                _session_tasks[task_id]["done"] = True
            return JSONResponse({"success": True})
        except Exception as e:
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    @app.custom_route("/api/v1/health", methods=["GET"])
    async def health_check(request: Request):
        return JSONResponse({"status": "ok", "server": "blender-mcp", "version": __version__})


def _register_resources(app):
    """Register MCP resources for the Blender server."""

    @app.resource("blender://scripts/{category}")
    async def get_script_collection(category: str) -> str:
        """Get a collection of construction scripts for a specific category."""
        try:
            scripts_data = _load_script_collection(category)
            return json.dumps(
                {
                    "category": category,
                    "scripts": scripts_data,
                    "description": f"Collection of {category} construction scripts for Blender",
                    "total_scripts": len(scripts_data),
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps({"error": f"Failed to load {category} scripts", "message": str(e)})

    @app.resource("blender://scripts/{category}/{script_name}")
    async def get_specific_script(category: str, script_name: str) -> str:
        """Get a specific construction script."""
        try:
            script_data = _load_specific_script(category, script_name)
            return json.dumps(script_data, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to load script {script_name} from {category}", "message": str(e)})


def _load_script_collection(category: str) -> List[Dict[str, Any]]:
    """Load scripts for a category from data/scripts/{category}.json.

    Falls back to empty list if the file doesn't exist.
    Available categories: robots, furniture, rooms, vehicles
    """
    # data/scripts/ lives two directories above this file (src/blender_mcp/app.py)
    data_dir = Path(__file__).parent.parent.parent / "data" / "scripts"
    script_file = data_dir / f"{category}.json"
    if script_file.exists():
        try:
            with open(script_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load scripts from {script_file}: {e}")
    return []


def _load_specific_script(category: str, script_name: str) -> Dict[str, Any]:
    """Load a specific script by name from a category."""
    for script in _load_script_collection(category):
        if script.get("name") == script_name:
            return script
    raise ValueError(f"Script '{script_name}' not found in category '{category}'")


# For backward compatibility
app = get_app()
