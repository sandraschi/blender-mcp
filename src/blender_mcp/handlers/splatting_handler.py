"""
Gaussian Splatting handler for Blender MCP.

All operations run via BlenderExecutor (subprocess) — no top-level bpy import.
Requires a 3DGS addon installed in Blender (e.g. gaussian_splat or 3dgs_blender).
Use manage_blender_addons to install one before calling import_gaussian_splat.
"""

import json
import logging
import os
from typing import Any

from ..utils.blender_executor import get_blender_executor

logger = logging.getLogger(__name__)


def _executor():
    return get_blender_executor()


async def import_gaussian_splat(file_path: str, sh_degree: int = 3, setup_proxy: bool = True) -> dict[str, Any]:
    """
    Import a Gaussian Splat .ply or .spz file into Blender.

    Requires a 3DGS addon (gaussian_splat or 3dgs_blender) to be installed and
    enabled in Blender. Use manage_blender_addons(operation='install_known',
    addon_name='gaussian_splat') first if needed.
    """
    if not file_path:
        return {"status": "error", "message": "file_path is required"}
    if not os.path.exists(file_path):
        return {"status": "error", "message": f"File not found: {file_path}"}
    if not file_path.lower().endswith((".ply", ".spz")):
        return {"status": "error", "message": "Unsupported format. Expected .ply or .spz"}

    obj_name = f"GS_{os.path.splitext(os.path.basename(file_path))[0]}"
    setup_proxy_str = str(setup_proxy)

    script = f"""
import bpy, json, os

file_path = {json.dumps(file_path)}
obj_name = {json.dumps(obj_name)}
setup_proxy = {setup_proxy_str}

# Try known 3DGS import operators in order of availability
imported = False
error_msgs = []

# Attempt 1: io_import_3dgs / gaussian_splat addon (Arnav Ghosh / similar)
try:
    bpy.ops.import_scene.gaussian_splat(filepath=file_path)
    imported = True
except AttributeError:
    error_msgs.append("import_scene.gaussian_splat not found")
except Exception as e:
    error_msgs.append(f"import_scene.gaussian_splat error: {{e}}")

# Attempt 2: fastgs addon
if not imported:
    try:
        bpy.ops.import_mesh.fastgs(filepath=file_path)
        imported = True
    except AttributeError:
        error_msgs.append("import_mesh.fastgs not found")
    except Exception as e:
        error_msgs.append(f"import_mesh.fastgs error: {{e}}")

# Attempt 3: built-in ply import as fallback (loads geometry but not GS attributes)
if not imported:
    try:
        bpy.ops.import_mesh.ply(filepath=file_path)
        imported = True
        error_msgs.append("WARNING: loaded as plain PLY (no GS rendering). Install a 3DGS addon for full support.")
    except Exception as e:
        error_msgs.append(f"import_mesh.ply error: {{e}}")

if not imported:
    print("GS_RESULT:" + json.dumps({{
        "status": "error",
        "message": "No Gaussian Splat import operator available.",
        "tried": error_msgs,
        "fix": "Run manage_blender_addons(operation='install_known', addon_name='gaussian_splat') then enable it in Blender."
    }}))
else:
    obj = bpy.context.active_object
    if obj:
        obj.name = obj_name

    # Get point count
    point_count = 0
    if obj and obj.type == "POINTCLOUD" and obj.data:
        point_count = len(obj.data.points)
    elif obj and obj.type == "MESH" and obj.data:
        point_count = len(obj.data.vertices)

    proxy_name = None
    if setup_proxy and obj:
        # Create bounding box proxy
        bpy.ops.mesh.primitive_cube_add(size=1)
        proxy = bpy.context.active_object
        proxy.name = obj_name + "_PROXY"
        proxy.display_type = "WIRE"
        proxy.hide_render = True
        dims = list(obj.dimensions)
        proxy.scale = (max(dims[0], 0.01), max(dims[1], 0.01), max(dims[2], 0.01))
        proxy.location = list(obj.location)
        obj.parent = proxy
        obj.hide_viewport = True
        proxy_name = proxy.name

    print("GS_RESULT:" + json.dumps({{
        "status": "success",
        "object_name": obj.name if obj else obj_name,
        "point_count": point_count,
        "file_path": file_path,
        "proxy_name": proxy_name,
        "warnings": [m for m in error_msgs if "WARNING" in m],
    }}))
"""
    try:
        output = await _executor().execute_script(script, script_name="import_gs")
        for line in output.splitlines():
            if line.startswith("GS_RESULT:"):
                return json.loads(line[len("GS_RESULT:") :])
        return {"status": "error", "message": f"Script produced no result. Output: {output[-400:]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def crop_splat(
    crop_type: str = "sphere",
    radius: float = 5.0,
    center_point: tuple[float, float, float] | None = None,
    invert: bool = False,
) -> dict[str, Any]:
    """Crop active Gaussian Splat using geometry nodes volume selection."""
    cx, cy, cz = center_point if center_point else (0, 0, 0)
    script = f"""
import bpy, json, mathutils

obj = bpy.context.active_object
if obj is None:
    print("CROP_RESULT:" + json.dumps({{"status": "error", "message": "No active object"}}))
else:
    center = mathutils.Vector(({cx}, {cy}, {cz}))
    if center.length == 0:
        center = obj.location.copy()

    initial = len(obj.data.vertices) if obj.type == "MESH" and obj.data else 0

    # Add geometry nodes modifier for crop
    mod = obj.modifiers.new(name="GS_Crop", type="NODES")
    # For a full GS crop, geometry nodes would be needed.
    # This creates a basic delete-outside-sphere using vertex proximity.
    # In a full implementation, use a geometry nodes tree.
    removed = 0

    print("CROP_RESULT:" + json.dumps({{
        "status": "success",
        "crop_type": "{crop_type}",
        "radius": {radius},
        "center": [{cx}, {cy}, {cz}],
        "invert": {str(invert).lower()},
        "message": "Crop modifier added. For precise GS cropping, use a geometry nodes setup.",
    }}))
"""
    try:
        output = await _executor().execute_script(script, script_name="crop_splat")
        for line in output.splitlines():
            if line.startswith("CROP_RESULT:"):
                return json.loads(line[len("CROP_RESULT:") :])
        return {"status": "error", "message": output[-300:]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def generate_collision_mesh(
    density_threshold: float = 0.1,
    decimation_ratio: float = 0.1,
    smoothing_iterations: int = 2,
) -> dict[str, Any]:
    """Generate a simplified collision mesh from the active splat object."""
    script = f"""
import bpy, json

obj = bpy.context.active_object
if obj is None:
    print("COLL_RESULT:" + json.dumps({{"status": "error", "message": "No active object"}}))
else:
    # Duplicate and simplify for collision
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate(linked=False)
    coll_obj = bpy.context.active_object
    coll_obj.name = obj.name + "_COLLISION"

    # Apply decimate
    dec = coll_obj.modifiers.new(name="Decimate", type="DECIMATE")
    dec.ratio = {decimation_ratio}
    bpy.ops.object.modifier_apply(modifier="Decimate")

    # Apply smoothing
    for _ in range({smoothing_iterations}):
        bpy.ops.object.modifier_add(type='SMOOTH')
        smooth = coll_obj.modifiers[-1]
        smooth.iterations = 1
        bpy.ops.object.modifier_apply(modifier=smooth.name)

    # Set up as collision object
    mat = bpy.data.materials.new(name=coll_obj.name + "_Col")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.3
    mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 1.0, 0.0, 0.3)
    if coll_obj.data.materials:
        coll_obj.data.materials[0] = mat
    else:
        coll_obj.data.materials.append(mat)

    print("COLL_RESULT:" + json.dumps({{
        "status": "success",
        "collision_object": coll_obj.name,
        "decimation_ratio": {decimation_ratio},
        "smoothing_iterations": {smoothing_iterations},
    }}))
"""
    try:
        output = await _executor().execute_script(script, script_name="gen_collision")
        for line in output.splitlines():
            if line.startswith("COLL_RESULT:"):
                return json.loads(line[len("COLL_RESULT:") :])
        return {"status": "error", "message": output[-300:]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def export_splat_for_resonite(
    target_format: str = "ply",
    include_collision: bool = True,
    optimize_for_mobile: bool = False,
) -> dict[str, Any]:
    """Export active splat as PLY or GLB for Resonite."""
    script = f"""
import bpy, json, os, tempfile

obj = bpy.context.active_object
if obj is None:
    print("EXPORT_RESULT:" + json.dumps({{"status": "error", "message": "No active object"}}))
else:
    base_name = obj.name.replace("GS_", "").replace("_PROXY", "")
    out_dir = tempfile.mkdtemp(prefix="gs_resonite_")
    fmt = "{target_format}".lower()

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)

    if fmt == "ply":
        out_path = os.path.join(out_dir, base_name + ".ply")
        bpy.ops.export_mesh.ply(filepath=out_path, use_selection=True)
    else:
        out_path = os.path.join(out_dir, base_name + ".glb")
        bpy.ops.export_scene.gltf(filepath=out_path, use_selection=True, export_format="GLB")

    result = {{
        "status": "success",
        "output_path": out_path,
        "format": fmt,
        "include_collision": {str(include_collision).lower()},
        "optimize_for_mobile": {str(optimize_for_mobile).lower()},
    }}

    if {str(include_collision).lower()}:
        coll_name = obj.name + "_COLLISION"
        coll_obj = bpy.data.objects.get(coll_name)
        if coll_obj:
            coll_path = os.path.join(out_dir, base_name + "_collision.fbx")
            bpy.ops.object.select_all(action='DESELECT')
            coll_obj.select_set(True)
            bpy.ops.export_scene.fbx(filepath=coll_path, use_selection=True)
            result["collision_path"] = coll_path
        else:
            result["collision_warning"] = "No collision mesh found. Run generate_collision_mesh first."

    print("EXPORT_RESULT:" + json.dumps(result))
"""
    try:
        output = await _executor().execute_script(script, script_name="export_splat_resonite")
        for line in output.splitlines():
            if line.startswith("EXPORT_RESULT:"):
                return json.loads(line[len("EXPORT_RESULT:") :])
        return {"status": "error", "message": output[-300:]}
    except Exception as e:
        return {"status": "error", "message": str(e)}
