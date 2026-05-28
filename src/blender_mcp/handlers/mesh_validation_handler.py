"""Mesh geometry audit (polycount, manifold, topology)."""

from __future__ import annotations

import json
import logging
import textwrap
from typing import Any

from ..decorators import blender_operation
from ..utils.blender_runtime import execute_bpy_script

logger = logging.getLogger(__name__)


async def _run_audit_script(script_name: str, body: str) -> dict[str, Any]:
    normalized = textwrap.dedent(body).strip("\n")
    indented = "\n".join(f"    {line}" for line in normalized.splitlines())
    script = f"""
import bpy
import json
try:
{indented}
    print("MESH_AUDIT:" + json.dumps(result))
except Exception as e:
    print("MESH_AUDIT_ERROR:" + str(e))
    raise
"""
    exec_result = await execute_bpy_script(
        script,
        script_name=script_name,
        timeout=120,
        prefer_session=True,
        headless_fallback=True,
    )
    if not exec_result.get("success"):
        return {"success": False, "error": exec_result.get("error"), **exec_result}

    for line in (exec_result.get("output") or "").splitlines():
        if line.startswith("MESH_AUDIT:"):
            try:
                payload = json.loads(line[len("MESH_AUDIT:") :])
                return {"success": True, **payload, "session_used": exec_result.get("session_used")}
            except json.JSONDecodeError:
                pass
        if line.startswith("MESH_AUDIT_ERROR:"):
            return {"success": False, "error": line[len("MESH_AUDIT_ERROR:") :].strip()}

    return {"success": False, "error": "No audit output from Blender"}


@blender_operation("validate_mesh_geometry", log_args=True)
async def validate_mesh_geometry(object_name: str = "") -> dict[str, Any]:
    """Audit mesh topology: polycount, loose geometry, non-manifold edges, degenerate faces."""
    target = object_name or "__ACTIVE__"
    body = f"""
    import bmesh
    obj = bpy.data.objects.get({object_name!r}) if {object_name!r} else bpy.context.active_object
    if obj is None and {target!r} == "__ACTIVE__":
        obj = bpy.context.active_object
    if obj is None:
        raise RuntimeError("No mesh object found; pass object_name or select a mesh")
    if obj.type != 'MESH':
        raise RuntimeError(f"Object {{obj.name}} is not a mesh")

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    loose_verts = [v.index for v in bm.verts if not v.link_edges]
    loose_edges = [e.index for e in bm.edges if not e.link_faces]
    non_manifold = [e.index for e in bm.edges if not e.is_manifold]
    degenerate = [f.index for f in bm.faces if f.calc_area() <= 1e-12]

    result = {{
        "operation": "validate_geometry",
        "object": obj.name,
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "triangles": sum(len(f.verts) - 2 for f in bm.faces),
        "loose_vertices": len(loose_verts),
        "loose_edges": len(loose_edges),
        "non_manifold_edges": len(non_manifold),
        "degenerate_faces": len(degenerate),
        "issues": [],
    }}
    if result["loose_vertices"]:
        result["issues"].append(f"{{result['loose_vertices']}} loose vertices")
    if result["loose_edges"]:
        result["issues"].append(f"{{result['loose_edges']}} loose edges")
    if result["non_manifold_edges"]:
        result["issues"].append(f"{{result['non_manifold_edges']}} non-manifold edges")
    if result["degenerate_faces"]:
        result["issues"].append(f"{{result['degenerate_faces']}} degenerate faces")
    result["status"] = "PASS" if not result["issues"] else "WARNING"
    bm.free()
"""
    return await _run_audit_script("validate_mesh_geometry", body)


@blender_operation("check_mesh_manifold", log_args=True)
async def check_mesh_manifold(object_name: str = "") -> dict[str, Any]:
    """Check whether mesh is manifold (watertight-friendly)."""
    body = f"""
    import bmesh
    obj = bpy.data.objects.get({object_name!r}) if {object_name!r} else bpy.context.active_object
    if obj is None:
        raise RuntimeError("No mesh object found")
    if obj.type != 'MESH':
        raise RuntimeError(f"Object {{obj.name}} is not a mesh")

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    non_manifold = [e.index for e in bm.edges if not e.is_manifold]
    boundary = [e.index for e in bm.edges if e.is_boundary]
    is_manifold = len(non_manifold) == 0 and len(boundary) == 0
    result = {{
        "operation": "check_manifold",
        "object": obj.name,
        "is_manifold": is_manifold,
        "non_manifold_edges": len(non_manifold),
        "boundary_edges": len(boundary),
        "status": "PASS" if is_manifold else "FAIL",
    }}
    bm.free()
"""
    return await _run_audit_script("check_mesh_manifold", body)
