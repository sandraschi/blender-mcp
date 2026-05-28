"""Geometry Nodes operations for Blender MCP."""

from __future__ import annotations

import json
import logging
from typing import Any

from ..decorators import blender_operation
from ..utils.blender_runtime import execute_bpy_script

logger = logging.getLogger(__name__)


async def _run_geonodes_script(script_name: str, body: str, *, prefer_session: bool = True) -> dict[str, Any]:
    indented = "\n".join(f"    {line}" if line.strip() else line for line in body.splitlines())
    script = f"""
import bpy
import json
try:
{indented}
    print("GEONODES_RESULT:" + json.dumps(result))
except Exception as e:
    print("GEONODES_ERROR:" + str(e))
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
        if line.startswith("GEONODES_RESULT:"):
            try:
                payload = json.loads(line[len("GEONODES_RESULT:") :])
                return {"success": True, **payload, "session_used": exec_result.get("session_used")}
            except json.JSONDecodeError:
                pass
        if line.startswith("GEONODES_ERROR:"):
            return {"success": False, "error": line[len("GEONODES_ERROR:") :].strip()}

    return {
        "success": True,
        "message": "Operation completed",
        "output": exec_result.get("output"),
        "session_used": exec_result.get("session_used"),
    }


@blender_operation("geonodes_create_group", log_args=True)
async def geonodes_create_group(
    group_name: str,
    prefer_session: bool = True,
) -> dict[str, Any]:
    body = f"""
    if {group_name!r} in bpy.data.node_groups:
        ng = bpy.data.node_groups[{group_name!r}]
    else:
        ng = bpy.data.node_groups.new({group_name!r}, 'GeometryNodeTree')
    result = {{"operation": "create_group", "group_name": ng.name, "node_count": len(ng.nodes)}}
"""
    return await _run_geonodes_script("geonodes_create_group", body, prefer_session=prefer_session)


@blender_operation("geonodes_add_node", log_args=True)
async def geonodes_add_node(
    group_name: str,
    node_type: str,
    node_name: str = "",
    location_x: float = 0.0,
    location_y: float = 0.0,
    prefer_session: bool = True,
) -> dict[str, Any]:
    body = f"""
    ng = bpy.data.node_groups.get({group_name!r})
    if ng is None:
        raise RuntimeError(f"Node group not found: {{group_name!r}}")
    node = ng.nodes.new({node_type!r})
    if {node_name!r}:
        node.name = {node_name!r}
    node.location = ({location_x}, {location_y})
    result = {{"operation": "add_node", "group_name": ng.name, "node_name": node.name, "node_type": node.type}}
"""
    return await _run_geonodes_script("geonodes_add_node", body, prefer_session=prefer_session)


@blender_operation("geonodes_connect_nodes", log_args=True)
async def geonodes_connect_nodes(
    group_name: str,
    from_node: str,
    from_socket: str,
    to_node: str,
    to_socket: str,
    prefer_session: bool = True,
) -> dict[str, Any]:
    body = f"""
    ng = bpy.data.node_groups.get({group_name!r})
    if ng is None:
        raise RuntimeError(f"Node group not found: {{group_name!r}}")
    src = ng.nodes.get({from_node!r})
    dst = ng.nodes.get({to_node!r})
    if src is None or dst is None:
        raise RuntimeError("Source or destination node not found")
    ng.links.new(src.outputs[{from_socket!r}], dst.inputs[{to_socket!r}])
    result = {{
        "operation": "connect_nodes",
        "group_name": ng.name,
        "from_node": src.name,
        "to_node": dst.name,
    }}
"""
    return await _run_geonodes_script("geonodes_connect_nodes", body, prefer_session=prefer_session)


@blender_operation("geonodes_assign_modifier", log_args=True)
async def geonodes_assign_modifier(
    object_name: str,
    group_name: str,
    modifier_name: str = "",
    prefer_session: bool = True,
) -> dict[str, Any]:
    mod_name = modifier_name or f"GeoNodes_{group_name}"
    body = f"""
    obj = bpy.data.objects.get({object_name!r})
    if obj is None:
        raise RuntimeError(f"Object not found: {{object_name!r}}")
    ng = bpy.data.node_groups.get({group_name!r})
    if ng is None:
        raise RuntimeError(f"Node group not found: {{group_name!r}}")
    mod = obj.modifiers.get({mod_name!r})
    if mod is None:
        mod = obj.modifiers.new({mod_name!r}, 'NODES')
    mod.node_group = ng
    result = {{
        "operation": "assign_modifier",
        "object": obj.name,
        "modifier": mod.name,
        "group_name": ng.name,
    }}
"""
    return await _run_geonodes_script("geonodes_assign_modifier", body, prefer_session=prefer_session)


@blender_operation("geonodes_add_input", log_args=True)
async def geonodes_add_input(
    group_name: str,
    socket_type: str = "NodeSocketFloat",
    input_name: str = "Input",
    default_value: float = 0.0,
    prefer_session: bool = True,
) -> dict[str, Any]:
    body = f"""
    ng = bpy.data.node_groups.get({group_name!r})
    if ng is None:
        raise RuntimeError(f"Node group not found: {{group_name!r}}")
    iface = ng.interface
    item = iface.new_socket(name={input_name!r}, in_out='INPUT', socket_type={socket_type!r})
    if hasattr(item, 'default_value'):
        item.default_value = {default_value}
    result = {{"operation": "add_input", "group_name": ng.name, "input_name": {input_name!r}}}
"""
    return await _run_geonodes_script("geonodes_add_input", body, prefer_session=prefer_session)


def list_common_geonode_types() -> list[str]:
    return [
        "GeometryNodeGroupInput",
        "GeometryNodeGroupOutput",
        "GeometryNodeMeshCube",
        "GeometryNodeMeshUVSphere",
        "GeometryNodeMeshCylinder",
        "GeometryNodeSubdivideMesh",
        "GeometryNodeExtrudeMesh",
        "GeometryNodeSetPosition",
        "GeometryNodeInstanceOnPoints",
        "GeometryNodeDistributePointsOnFaces",
        "GeometryNodeJoinGeometry",
        "GeometryNodeRealizeInstances",
        "GeometryNodeMeshToCurve",
        "GeometryNodeCurveToMesh",
        "GeometryNodeStoreNamedAttribute",
    ]
