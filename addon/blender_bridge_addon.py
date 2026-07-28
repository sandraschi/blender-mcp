"""
blender_bridge_addon.py — Blender MCP Socket Bridge (v2)

Canonical location: addon/blender_bridge_addon.py
Download: https://github.com/sandraschi/blender-mcp/releases/latest/download/blender_bridge_addon.py

Installs as a Blender addon. Creates a TCP socket server inside Blender so the
blender-mcp server can send bpy scripts directly (no HTTP polling).

Install: Edit > Preferences > Add-ons > Install > pick this file > enable it.

API keys (Sketchfab, Hyper3D, Hunyuan3D) can be set in addon preferences under
Edit > Preferences > Add-ons > Blender MCP Bridge — they survive restarts.

Environment variables (all optional):
  BLENDER_BRIDGE_PORT    — TCP port (default 10850)
  BLENDER_BRIDGE_HOST    — bind address (default 127.0.0.1)
  BLENDERMCP_SKETCHFAB_API_KEY
  BLENDERMCP_HYPER3D_API_KEY
  BLENDERMCP_HUNYUAN3D_SECRET_ID / SECRET_KEY / API_URL
"""

bl_info = {
    "name": "Blender MCP Bridge",
    "author": "sandraschi",
    "version": (0, 5, 0),
    "blender": (4, 2, 0),
    "location": "Properties > Scene > Blender MCP",
    "description": "TCP socket bridge for blender-mcp — connect your MCP server to live Blender",
    "category": "System",
}

import json
import logging
import os
import socket
import struct
import threading
import traceback

import bpy

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config from env vars
# ---------------------------------------------------------------------------

BRIDGE_HOST = os.environ.get("BLENDER_BRIDGE_HOST", "127.0.0.1")
BRIDGE_PORT = int(os.environ.get("BLENDER_BRIDGE_PORT", "10850"))

_stop_event = threading.Event()
_server_thread: threading.Thread | None = None
_server_socket: socket.socket | None = None

# Main-thread task queue (thread-safe via threading.Event)
_pending_task: dict | None = None
_pending_event = threading.Event()
_result_event = threading.Event()
_result_data: dict | None = None


# ---------------------------------------------------------------------------
# Add-on Preferences — API keys that survive restarts
# ---------------------------------------------------------------------------

class MCP_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    sketchfab_api_key: bpy.props.StringProperty(
        name="Sketchfab API Key",
        description="API token for sketchfab.com (search + download models)",
        default="",
        subtype="PASSWORD",
    )
    hyper3d_api_key: bpy.props.StringProperty(
        name="Hyper3D Rodin API Key",
        description="API key for hyper3d.ai Rodin 3D generation",
        default="",
        subtype="PASSWORD",
    )
    hunyuan3d_secret_id: bpy.props.StringProperty(
        name="Hunyuan3D SecretId",
        description="Tencent Cloud SecretId for Hunyuan3D",
        default="",
        subtype="PASSWORD",
    )
    hunyuan3d_secret_key: bpy.props.StringProperty(
        name="Hunyuan3D SecretKey",
        description="Tencent Cloud SecretKey for Hunyuan3D",
        default="",
        subtype="PASSWORD",
    )
    hunyuan3d_api_url: bpy.props.StringProperty(
        name="Hunyuan3D API URL",
        description="Override Hunyuan3D API endpoint",
        default="http://localhost:8081",
    )
    bridge_port: bpy.props.IntProperty(
        name="Bridge Port",
        description="TCP port for the socket bridge",
        default=BRIDGE_PORT,
        min=1024,
        max=65535,
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="API Keys (stored in Blender preferences, survive restarts)", icon="PREFERENCES")
        box.prop(self, "sketchfab_api_key")
        box.prop(self, "hyper3d_api_key")
        box.separator()
        box.label(text="Hunyuan3D Credentials", icon="WORLD")
        box.prop(self, "hunyuan3d_secret_id")
        box.prop(self, "hunyuan3d_secret_key")
        box.prop(self, "hunyuan3d_api_url")
        box.separator()
        box.prop(self, "bridge_port")


# ---------------------------------------------------------------------------
# Socket server — runs in background thread
# ---------------------------------------------------------------------------

def _get_prefs():
    try:
        addon = bpy.context.preferences.addons.get(__name__)
        if addon and hasattr(addon, "preferences"):
            return addon.preferences
    except Exception:
        pass
    return None


def _resolve_api_key(pref_attr: str, env_var: str) -> str:
    """Read: addon prefs > env var."""
    prefs = _get_prefs()
    if prefs:
        val = getattr(prefs, pref_attr, "") or ""
        if val.strip():
            return val.strip()
    return (os.environ.get(env_var) or "").strip()


def _handle_client(client: socket.socket):
    """Handle one connected MCP server in a thread."""
    global _pending_task, _pending_event, _result_data, _result_event
    buf = b""
    header_len = struct.calcsize("!I")

    try:
        while not _stop_event.is_set():
            # Read 4-byte length prefix
            while len(buf) < header_len:
                chunk = client.recv(4096)
                if not chunk:
                    return
                buf += chunk
            body_len = struct.unpack("!I", buf[:header_len])[0]
            buf = buf[header_len:]

            # Read body
            while len(buf) < body_len:
                chunk = client.recv(4096)
                if not chunk:
                    return
                buf += chunk
            body = buf[:body_len]
            buf = buf[body_len:]

            try:
                msg = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError as e:
                _send_response(client, {"status": "error", "message": f"Invalid JSON: {e}"})
                continue

            cmd = msg.get("type", "")
            params = msg.get("params", {})

            if cmd == "ping":
                _send_response(client, {"status": "success", "result": {"pong": True}})
                continue

            if cmd == "execute_code":
                code = params.get("code", "")
                if not code.strip():
                    _send_response(client, {"status": "error", "message": "Empty code"})
                    continue

                # Hand off to main thread via timer
                _pending_task = {"code": code}
                _pending_event.set()
                _result_event.clear()
                _result_data = None

                # Wait for result (with timeout)
                if _result_event.wait(timeout=180):
                    result = _result_data or {}
                    _send_response(client, {
                        "status": "success" if result.get("success") else "error",
                        "result": result,
                    })
                else:
                    _send_response(client, {
                        "status": "error",
                        "message": "Execution timed out (180s)",
                    })
                continue

            if cmd == "get_api_keys":
                prefs = _get_prefs()
                keys = {}
                if prefs:
                    keys = {
                        "sketchfab": _resolve_api_key("sketchfab_api_key", "BLENDERMCP_SKETCHFAB_API_KEY"),
                        "hyper3d": _resolve_api_key("hyper3d_api_key", "BLENDERMCP_HYPER3D_API_KEY"),
                        "hunyuan3d": {
                            "secret_id": _resolve_api_key("hunyuan3d_secret_id", "BLENDERMCP_HUNYUAN3D_SECRET_ID"),
                            "secret_key": _resolve_api_key("hunyuan3d_secret_key", "BLENDERMCP_HUNYUAN3D_SECRET_KEY"),
                            "api_url": _resolve_api_key("hunyuan3d_api_url", "BLENDERMCP_HUNYUAN3D_API_URL"),
                        },
                    }
                _send_response(client, {"status": "success", "result": keys})
                continue

            if cmd == "get_scene_info":
                _pending_task = {"cmd": "get_scene_info"}
                _pending_event.set()
                _result_event.clear()
                _result_data = None
                if _result_event.wait(timeout=30):
                    _send_response(client, {"status": "success", "result": _result_data or {}})
                else:
                    _send_response(client, {"status": "error", "message": "Timed out"})
                continue

            if cmd == "screenshot_viewport":
                _pending_task = {"cmd": "screenshot_viewport", "params": params}
                _pending_event.set()
                _result_event.clear()
                _result_data = None
                if _result_event.wait(timeout=60):
                    _send_response(client, {"status": "success", "result": _result_data or {}})
                else:
                    _send_response(client, {"status": "error", "message": "Screenshot timed out"})
                continue

            _send_response(client, {"status": "error", "message": f"Unknown command: {cmd}"})
    except (ConnectionError, BrokenPipeError, OSError):
        pass
    finally:
        try:
            client.close()
        except Exception:
            pass


def _send_response(client: socket.socket, data: dict):
    payload = json.dumps(data).encode("utf-8")
    client.sendall(struct.pack("!I", len(payload)) + payload)


def _server_loop():
    global _server_socket
    _server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _server_socket.settimeout(1.0)
    try:
        _server_socket.bind((BRIDGE_HOST, BRIDGE_PORT))
        _server_socket.listen(5)
        _log.info("MCP Bridge socket server listening on %s:%d", BRIDGE_HOST, BRIDGE_PORT)
    except OSError as e:
        _log.error("MCP Bridge could not bind: %s", e)
        _server_socket = None
        return

    while not _stop_event.is_set():
        try:
            client, addr = _server_socket.accept()
            _log.info("MCP server connected from %s", addr)
            t = threading.Thread(target=_handle_client, args=(client,), daemon=True)
            t.start()
        except socket.timeout:
            continue
        except OSError:
            break

    _log.info("MCP Bridge socket server stopped")


# ---------------------------------------------------------------------------
# Main-thread timer — safe to call bpy here
# ---------------------------------------------------------------------------

def _process_pending():
    global _pending_task, _pending_event, _result_data, _result_event
    if _pending_task is None:
        return 0.1

    task = _pending_task
    _pending_task = None
    _pending_event.clear()

    cmd = task.get("cmd", "execute_code")
    result = None

    try:
        if cmd == "execute_code":
            code = task.get("code", "")
            output_lines = []
            error_msg = None
            import io, sys
            buf = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = buf
            try:
                exec(compile(code, "<mcp_bridge>", "exec"), {"bpy": bpy})
            except Exception as exc:
                error_msg = traceback.format_exc()
            finally:
                sys.stdout = old_stdout
            output_lines = buf.getvalue().splitlines()
            result = {
                "success": error_msg is None,
                "output": "\n".join(output_lines),
                "error": error_msg,
            }

        elif cmd == "get_scene_info":
            info = {
                "name": bpy.context.scene.name,
                "object_count": len(bpy.context.scene.objects),
                "objects": [],
                "materials_count": len(bpy.data.materials),
            }
            for i, obj in enumerate(bpy.context.scene.objects):
                if i >= 20:
                    break
                info["objects"].append({
                    "name": obj.name,
                    "type": obj.type,
                    "location": [round(float(obj.location.x), 2),
                                 round(float(obj.location.y), 2),
                                 round(float(obj.location.z), 2)],
                })
            result = info

        elif cmd == "screenshot_viewport":
            params = task.get("params", {})
            filepath = params.get("filepath", "")
            max_size = params.get("max_size", 1000)

            if not filepath:
                import tempfile
                filepath = os.path.join(tempfile.gettempdir(), f"blender_mcp_shot_{os.getpid()}.png")

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            area = None
            for a in bpy.context.screen.areas:
                if a.type == "VIEW_3D":
                    area = a
                    break

            if area:
                with bpy.context.temp_override(area=area):
                    bpy.ops.screen.screenshot_area(filepath=filepath)
            else:
                scene = bpy.context.scene
                scene.render.filepath = filepath
                scene.render.image_settings.file_format = "PNG"
                bpy.ops.render.render(write_still=True)

            if max_size > 0 and os.path.exists(filepath):
                img = bpy.data.images.load(filepath)
                w, h = img.size
                if max(w, h) > max_size:
                    scale = max_size / max(w, h)
                    img.scale(int(w * scale), int(h * scale))
                    img.file_format = "PNG"
                    img.save()
                bpy.data.images.remove(img)

            result = {
                "success": os.path.exists(filepath),
                "filepath": filepath,
            }

    except Exception as exc:
        result = {"success": False, "error": traceback.format_exc()}

    _result_data = result
    _result_event.set()
    return 0.1


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------


class MCP_OT_start_bridge(bpy.types.Operator):
    bl_idname = "mcp.start_bridge"
    bl_label = "Start MCP Bridge"

    def execute(self, context):
        global _server_thread, _stop_event, BRIDGE_PORT

        prefs = _get_prefs()
        if prefs:
            BRIDGE_PORT = prefs.bridge_port

        if _server_thread and _server_thread.is_alive():
            self.report({"WARNING"}, "Bridge already running")
            return {"CANCELLED"}

        _stop_event.clear()
        bpy.app.timers.register(_process_pending, first_interval=0.1)
        _server_thread = threading.Thread(target=_server_loop, daemon=True)
        _server_thread.start()
        self.report({"INFO"}, f"MCP Bridge started on port {BRIDGE_PORT}")
        return {"FINISHED"}


class MCP_OT_stop_bridge(bpy.types.Operator):
    bl_idname = "mcp.stop_bridge"
    bl_label = "Stop MCP Bridge"

    def execute(self, context):
        global _server_socket
        _stop_event.set()
        if _server_socket:
            try:
                _server_socket.close()
            except Exception:
                pass
            _server_socket = None
        if bpy.app.timers.is_registered(_process_pending):
            bpy.app.timers.unregister(_process_pending)
        self.report({"INFO"}, "MCP Bridge stopped")
        return {"FINISHED"}


class MCP_PT_bridge_panel(bpy.types.Panel):
    bl_label = "Blender MCP Bridge"
    bl_idname = "MCP_PT_bridge_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        prefs = _get_prefs()

        row = layout.row()
        if _server_thread and _server_thread.is_alive():
            row.operator("mcp.stop_bridge", text="Stop Bridge", icon="X")
            layout.label(text=f"Status: Connected on port {BRIDGE_PORT}", icon="CHECKMARK")
        else:
            row.operator("mcp.start_bridge", text="Start Bridge", icon="PLAY")
            layout.label(text="Status: Not running", icon="ERROR")

        layout.separator()
        if prefs:
            layout.label(text="API Keys: Edit > Preferences > Add-ons > Blender MCP Bridge", icon="PREFERENCES")
        layout.label(text="Port: " + str(BRIDGE_PORT), icon="PLUG")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_classes = [
    MCP_AddonPreferences,
    MCP_OT_start_bridge,
    MCP_OT_stop_bridge,
    MCP_PT_bridge_panel,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    global _server_socket
    _stop_event.set()
    if _server_socket:
        try:
            _server_socket.close()
        except Exception:
            pass
        _server_socket = None
    if bpy.app.timers.is_registered(_process_pending):
        bpy.app.timers.unregister(_process_pending)
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
