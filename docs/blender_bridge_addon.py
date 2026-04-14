"""
blender_bridge_addon.py — Blender MCP Session Bridge

Install: Edit > Preferences > Add-ons > Install > pick this file > enable it.

What it does
------------
Connects the running Blender session to the blender-mcp HTTP server so that
tools like `manage_object_repo save` can export real objects from your current
scene instead of getting the "session required" placeholder.

How it works
------------
1. On registration it starts a background thread that polls the MCP server
   for pending scripts at GET /api/v1/blender/pending.
2. When a script arrives (posted by the MCP tool via /api/v1/blender/exec) the
   addon executes it inside Blender using a bpy.app.timers callback (safe from
   the main thread) and POSTs the result back to /api/v1/blender/result.
3. The MCP server tool waits up to 30 s for the result, then returns it to the
   caller.

Quick manual use (no addon needed)
------------------------------------
You can also just paste this in Blender's Script Editor to call any MCP tool
from the current session:

    import urllib.request, json
    data = json.dumps({
        "tool": "manage_object_repo",
        "params": {
            "operation": "save",
            "object_name": "Cube",        # exact name of object in your scene
            "category":    "general",
            "quality_rating": 7,
        }
    }).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:10849/tool",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=30)
    print(json.loads(resp.read()))

Server address: matches MCP_HOST / MCP_PORT env vars (default 127.0.0.1:10849).
"""

bl_info = {
    "name": "Blender MCP Session Bridge",
    "author": "sandraschi",
    "version": (0, 4, 1),
    "blender": (4, 2, 0),
    "location": "Properties > Scene > Blender MCP",
    "description": "Connects running Blender session to the blender-mcp HTTP server",
    "category": "System",
}

import json
import threading
import time
import urllib.error
import urllib.request

import bpy

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MCP_BASE_URL = "http://127.0.0.1:10849"
POLL_INTERVAL = 1.0  # seconds between polls
_stop_event = threading.Event()
_poll_thread: threading.Thread | None = None


# ---------------------------------------------------------------------------
# Result queue (thread → main thread)
# ---------------------------------------------------------------------------

_pending_exec: dict | None = None  # set by poll thread
_pending_result: dict | None = None  # set by main-thread timer


def _post_json(path: str, payload: dict, timeout: int = 10) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{MCP_BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _get_json(path: str, timeout: int = 5) -> dict:
    req = urllib.request.Request(f"{MCP_BASE_URL}{path}")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Poll thread — runs outside main thread, only reads/writes _pending_exec
# ---------------------------------------------------------------------------


def _poll_loop():
    global _pending_exec
    while not _stop_event.is_set():
        try:
            result = _get_json("/api/v1/blender/pending")
            if result.get("script"):
                _pending_exec = result
        except Exception:
            pass  # server not running or not reachable — silent
        time.sleep(POLL_INTERVAL)


# ---------------------------------------------------------------------------
# Main-thread timer — safe to call bpy here
# ---------------------------------------------------------------------------


def _execute_pending():
    global _pending_exec, _pending_result
    task = _pending_exec
    if task is None:
        return POLL_INTERVAL

    _pending_exec = None
    script = task.get("script", "")
    task_id = task.get("id", "unknown")

    output_lines = []
    error_msg = None

    try:
        import io
        import sys

        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            exec(compile(script, f"<mcp_task_{task_id}>", "exec"), {"bpy": bpy})
        finally:
            sys.stdout = old_stdout
        output_lines = buf.getvalue().splitlines()
    except Exception as exc:
        error_msg = str(exc)

    # Post result back asynchronously (done in a thread to avoid blocking)
    def _post():
        try:
            _post_json(
                "/api/v1/blender/result",
                {
                    "id": task_id,
                    "output": "\n".join(output_lines),
                    "success": error_msg is None,
                    "error": error_msg,
                },
            )
        except Exception:
            pass

    threading.Thread(target=_post, daemon=True).start()
    return POLL_INTERVAL


# ---------------------------------------------------------------------------
# Blender UI panel
# ---------------------------------------------------------------------------


class MCP_PT_bridge_panel(bpy.types.Panel):
    bl_label = "Blender MCP Bridge"
    bl_idname = "MCP_PT_bridge_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        props = context.scene.mcp_bridge

        layout.prop(props, "server_url")
        row = layout.row()
        if _poll_thread and _poll_thread.is_alive():
            row.operator("mcp.stop_bridge", text="Stop Bridge", icon="X")
            layout.label(text="Status: Connected", icon="CHECKMARK")
        else:
            row.operator("mcp.start_bridge", text="Start Bridge", icon="PLAY")
            layout.label(text="Status: Not running", icon="ERROR")


class MCP_OT_start_bridge(bpy.types.Operator):
    bl_idname = "mcp.start_bridge"
    bl_label = "Start MCP Bridge"

    def execute(self, context):
        global _poll_thread, MCP_BASE_URL
        MCP_BASE_URL = context.scene.mcp_bridge.server_url
        _stop_event.clear()
        _poll_thread = threading.Thread(target=_poll_loop, daemon=True)
        _poll_thread.start()
        bpy.app.timers.register(_execute_pending, first_interval=POLL_INTERVAL)
        self.report({"INFO"}, f"MCP bridge started → {MCP_BASE_URL}")
        return {"FINISHED"}


class MCP_OT_stop_bridge(bpy.types.Operator):
    bl_idname = "mcp.stop_bridge"
    bl_label = "Stop MCP Bridge"

    def execute(self, context):
        _stop_event.set()
        if bpy.app.timers.is_registered(_execute_pending):
            bpy.app.timers.unregister(_execute_pending)
        self.report({"INFO"}, "MCP bridge stopped")
        return {"FINISHED"}


class MCP_PG_props(bpy.types.PropertyGroup):
    server_url: bpy.props.StringProperty(  # type: ignore
        name="Server URL",
        default="http://127.0.0.1:10849",
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_classes = [MCP_PG_props, MCP_PT_bridge_panel, MCP_OT_start_bridge, MCP_OT_stop_bridge]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mcp_bridge = bpy.props.PointerProperty(type=MCP_PG_props)


def unregister():
    _stop_event.set()
    if bpy.app.timers.is_registered(_execute_pending):
        bpy.app.timers.unregister(_execute_pending)
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mcp_bridge
