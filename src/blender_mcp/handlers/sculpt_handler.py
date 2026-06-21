"""Sculpt mode operations for Blender MCP."""

from __future__ import annotations

import json
import logging
import textwrap
from typing import Any

from ..decorators import blender_operation
from ..utils.blender_runtime import execute_bpy_script

logger = logging.getLogger(__name__)


async def _run_sculpt_script(script_name: str, body: str, *, prefer_session: bool = True) -> dict[str, Any]:
    normalized = textwrap.dedent(body).strip("\n")
    indented = "\n".join(f"    {line}" for line in normalized.splitlines())
    script = f"""
import bpy
import json
try:
{indented}
    print("SCULPT_RESULT:" + json.dumps(result))
except Exception as e:
    print("SCULPT_ERROR:" + str(e))
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

    for line in (exec_result.get("output") or "").splitlines():
        if line.startswith("SCULPT_RESULT:"):
            try:
                payload = json.loads(line[len("SCULPT_RESULT:") :])
                return {"success": True, **payload, "session_used": exec_result.get("session_used")}
            except json.JSONDecodeError:
                pass
        if line.startswith("SCULPT_ERROR:"):
            return {"success": False, "error": line[len("SCULPT_ERROR:") :].strip()}

    return {"success": False, "error": "No sculpt output from Blender"}


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


@blender_operation("sculpt_enter", log_args=True)
async def sculpt_enter(object_name: str, prefer_session: bool = True) -> dict[str, Any]:
    body = (
        _object_setup(object_name)
        + """
    bpy.ops.object.mode_set(mode='SCULPT')
    result = {"operation": "enter_sculpt", "object": obj.name, "mode": obj.mode}
"""
    )
    return await _run_sculpt_script("sculpt_enter", body, prefer_session=prefer_session)


@blender_operation("sculpt_exit", log_args=True)
async def sculpt_exit(object_name: str, target_mode: str = "OBJECT", prefer_session: bool = True) -> dict[str, Any]:
    body = (
        _object_setup(object_name)
        + f"""
    bpy.ops.object.mode_set(mode={target_mode!r})
    result = {{"operation": "exit_sculpt", "object": obj.name, "mode": obj.mode}}
"""
    )
    return await _run_sculpt_script("sculpt_exit", body, prefer_session=prefer_session)


@blender_operation("sculpt_set_brush", log_args=True)
async def sculpt_set_brush(
    object_name: str,
    brush_name: str = "Grab",
    strength: float = 0.5,
    radius: float = 50.0,
    prefer_session: bool = True,
) -> dict[str, Any]:
    body = (
        _object_setup(object_name)
        + f"""
    bpy.ops.object.mode_set(mode='SCULPT')
    brush = bpy.data.brushes.get({brush_name!r})
    if brush is None:
        raise RuntimeError(f"Brush not found: {{brush_name!r}}")
    bpy.context.tool_settings.sculpt.brush = brush
    brush.strength = {strength}
    brush.size = {radius}
    result = {{
        "operation": "set_brush",
        "object": obj.name,
        "brush": brush.name,
        "strength": brush.strength,
        "radius": brush.size,
    }}
"""
    )
    return await _run_sculpt_script("sculpt_set_brush", body, prefer_session=prefer_session)


@blender_operation("sculpt_dynotopo", log_args=True)
async def sculpt_dynotopo(
    object_name: str,
    enable: bool = True,
    detail_type: str = "CONSTANT",
    detail_resolution: float = 6.0,
    prefer_session: bool = True,
) -> dict[str, Any]:
    body = (
        _object_setup(object_name)
        + f"""
    bpy.ops.object.mode_set(mode='SCULPT')
    active = bpy.context.active_object
    if active is None:
        raise RuntimeError("No active object")
    if {enable!r}:
        bpy.ops.sculpt.dynamic_topology_toggle()
        if active.use_dynamic_topology_sculpting:
            active.dynamic_topology_sculpting_detail_type = {detail_type!r}
            active.dynamic_topology_sculpting_detail_resolution = {detail_resolution}
    elif active.use_dynamic_topology_sculpting:
        bpy.ops.sculpt.dynamic_topology_toggle()
    result = {{
        "operation": "dynotopo",
        "object": obj.name,
        "dynotopo_enabled": active.use_dynamic_topology_sculpting,
        "detail_resolution": active.dynamic_topology_sculpting_detail_resolution,
    }}
"""
    )
    return await _run_sculpt_script("sculpt_dynotopo", body, prefer_session=prefer_session)


@blender_operation("sculpt_symmetrize", log_args=True)
async def sculpt_symmetrize(
    object_name: str,
    direction: str = "NEGATIVE_X",
    prefer_session: bool = True,
) -> dict[str, Any]:
    body = (
        _object_setup(object_name)
        + f"""
    bpy.ops.object.mode_set(mode='SCULPT')
    bpy.ops.sculpt.symmetrize(direction={direction!r})
    result = {{"operation": "symmetrize", "object": obj.name, "direction": {direction!r}}}
"""
    )
    return await _run_sculpt_script("sculpt_symmetrize", body, prefer_session=prefer_session)


@blender_operation("sculpt_mask_clear", log_args=True)
async def sculpt_mask_clear(object_name: str, prefer_session: bool = True) -> dict[str, Any]:
    body = (
        _object_setup(object_name)
        + """
    bpy.ops.object.mode_set(mode='SCULPT')
    bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0.0)
    result = {"operation": "mask_clear", "object": obj.name}
"""
    )
    return await _run_sculpt_script("sculpt_mask_clear", body, prefer_session=prefer_session)


@blender_operation("sculpt_remesh_voxel", log_args=True)
async def sculpt_remesh_voxel(
    object_name: str,
    voxel_size: float = 0.1,
    adaptivity: float = 0.0,
    prefer_session: bool = True,
) -> dict[str, Any]:
    body = (
        _object_setup(object_name)
        + f"""
    mod = obj.modifiers.get('Remesh') or obj.modifiers.new('Remesh', 'REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = {voxel_size}
    mod.adaptivity = {adaptivity}
    bpy.ops.object.modifier_apply(modifier=mod.name)
    result = {{
        "operation": "remesh_voxel",
        "object": obj.name,
        "voxel_size": {voxel_size},
        "adaptivity": {adaptivity},
    }}
"""
    )
    return await _run_sculpt_script("sculpt_remesh_voxel", body, prefer_session=prefer_session)


def list_sculpt_brushes() -> list[str]:
    return [
        "Grab",
        "Draw",
        "Clay",
        "Clay Strips",
        "Inflate",
        "Blob",
        "Crease",
        "Smooth",
        "Flatten",
        "Scrape",
        "Fill",
        "Pinch",
        "Nudge",
        "Snake Hook",
        "Thumb",
        "Layer",
        "Mask",
    ]
