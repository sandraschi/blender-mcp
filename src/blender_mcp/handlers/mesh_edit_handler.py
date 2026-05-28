"""Mesh editing operations (edit mode) for Blender MCP."""

from __future__ import annotations

import json
import logging
from typing import Any

from ..decorators import blender_operation
from ..utils.blender_runtime import execute_bpy_script

logger = logging.getLogger(__name__)


def _object_setup(name: str) -> str:
    return f"""
obj = bpy.data.objects.get({name!r})
if obj is None:
    raise RuntimeError(f"Object not found: {{name!r}}")
if obj.type != 'MESH':
    raise RuntimeError(f"Object {{obj.name}} is not a mesh")
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
"""


async def _run_mesh_script(script_name: str, body: str, *, prefer_session: bool = True) -> dict[str, Any]:
    indented_body = "\n".join(f"    {line}" if line.strip() else line for line in body.splitlines())
    script = f"""
import bpy
import json
try:
{indented_body}
    print("MESH_EDIT_RESULT:" + json.dumps(result))
except Exception as e:
    print("MESH_EDIT_ERROR:" + str(e))
    raise
"""
    exec_result = await execute_bpy_script(
        script,
        script_name=script_name,
        timeout=120,
        prefer_session=prefer_session,
        headless_fallback=True,
    )
    if not exec_result.get("success"):
        return {"success": False, "error": exec_result.get("error"), **exec_result}

    output = exec_result.get("output", "")
    for line in output.splitlines():
        if line.startswith("MESH_EDIT_RESULT:"):
            try:
                payload = json.loads(line[len("MESH_EDIT_RESULT:") :])
                return {"success": True, **payload, "session_used": exec_result.get("session_used")}
            except json.JSONDecodeError:
                pass
        if line.startswith("MESH_EDIT_ERROR:"):
            return {"success": False, "error": line[len("MESH_EDIT_ERROR:") :].strip()}

    return {
        "success": True,
        "message": "Operation completed",
        "output": output,
        "session_used": exec_result.get("session_used"),
    }


@blender_operation("mesh_extrude", log_args=True)
async def mesh_extrude(object_name: str, distance: float = 0.5, prefer_session: bool = True) -> dict[str, Any]:
    body = _object_setup(object_name) + f"""
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.extrude_region()
    bpy.ops.transform.translate(value=(0, 0, {distance}))
    bpy.ops.object.mode_set(mode='OBJECT')
    result = {{"operation": "extrude", "object": obj.name, "distance": {distance}}}
"""
    return await _run_mesh_script("mesh_extrude", body, prefer_session=prefer_session)


@blender_operation("mesh_inset", log_args=True)
async def mesh_inset(object_name: str, thickness: float = 0.1, depth: float = 0.0, prefer_session: bool = True) -> dict[str, Any]:
    body = _object_setup(object_name) + f"""
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.inset(thickness={thickness}, depth={depth})
    bpy.ops.object.mode_set(mode='OBJECT')
    result = {{"operation": "inset", "object": obj.name, "thickness": {thickness}}}
"""
    return await _run_mesh_script("mesh_inset", body, prefer_session=prefer_session)


@blender_operation("mesh_bevel_modifier", log_args=True)
async def mesh_bevel_modifier(
    object_name: str, width: float = 0.1, segments: int = 2, prefer_session: bool = True
) -> dict[str, Any]:
    body = _object_setup(object_name) + f"""
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = {width}
    mod.segments = {segments}
    result = {{"operation": "bevel_modifier", "object": obj.name, "modifier": mod.name}}
"""
    return await _run_mesh_script("mesh_bevel_modifier", body, prefer_session=prefer_session)


@blender_operation("mesh_subdivide", log_args=True)
async def mesh_subdivide(object_name: str, cuts: int = 2, prefer_session: bool = True) -> dict[str, Any]:
    body = _object_setup(object_name) + f"""
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts={cuts})
    bpy.ops.object.mode_set(mode='OBJECT')
    result = {{"operation": "subdivide", "object": obj.name, "cuts": {cuts}}}
"""
    return await _run_mesh_script("mesh_subdivide", body, prefer_session=prefer_session)


@blender_operation("mesh_merge_vertices", log_args=True)
async def mesh_merge_vertices(object_name: str, merge_distance: float = 0.001, prefer_session: bool = True) -> dict[str, Any]:
    body = _object_setup(object_name) + f"""
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold={merge_distance})
    bpy.ops.object.mode_set(mode='OBJECT')
    result = {{"operation": "merge_vertices", "object": obj.name, "distance": {merge_distance}}}
"""
    return await _run_mesh_script("mesh_merge_vertices", body, prefer_session=prefer_session)


@blender_operation("mesh_delete_faces", log_args=True)
async def mesh_delete_faces(object_name: str, prefer_session: bool = True) -> dict[str, Any]:
    body = _object_setup(object_name) + """
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    result = {"operation": "delete_faces", "object": obj.name}
"""
    return await _run_mesh_script("mesh_delete_faces", body, prefer_session=prefer_session)


@blender_operation("mesh_join", log_args=True)
async def mesh_join(object_names: list[str], prefer_session: bool = True) -> dict[str, Any]:
    names_json = json.dumps(object_names)
    body = f"""
    names = {names_json}
    objs = [bpy.data.objects.get(n) for n in names]
    objs = [o for o in objs if o is not None]
    if len(objs) < 2:
        raise RuntimeError("join requires at least two valid object names")
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    result = {{"operation": "join", "object": objs[0].name, "joined": names}}
"""
    return await _run_mesh_script("mesh_join", body, prefer_session=prefer_session)


@blender_operation("mesh_separate_loose", log_args=True)
async def mesh_separate_loose(object_name: str, prefer_session: bool = True) -> dict[str, Any]:
    body = _object_setup(object_name) + """
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    result = {"operation": "separate_loose", "object": obj.name}
"""
    return await _run_mesh_script("mesh_separate_loose", body, prefer_session=prefer_session)


@blender_operation("mesh_triangulate", log_args=True)
async def mesh_triangulate(object_name: str, prefer_session: bool = True) -> dict[str, Any]:
    body = _object_setup(object_name) + """
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode='OBJECT')
    result = {"operation": "triangulate", "object": obj.name}
"""
    return await _run_mesh_script("mesh_triangulate", body, prefer_session=prefer_session)
