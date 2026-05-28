"""Batch file operations (images, exports)."""

from __future__ import annotations

import json
import logging
import textwrap
from typing import Any

from ..decorators import blender_operation
from ..utils.blender_runtime import execute_bpy_script

logger = logging.getLogger(__name__)


async def _run_batch_script(script_name: str, body: str) -> dict[str, Any]:
    normalized = textwrap.dedent(body).strip("\n")
    indented = "\n".join(f"    {line}" for line in normalized.splitlines())
    script = f"""
import bpy
import json
try:
{indented}
    print("BATCH_RESULT:" + json.dumps(result))
except Exception as e:
    print("BATCH_ERROR:" + str(e))
    raise
"""
    exec_result = await execute_bpy_script(
        script,
        script_name=script_name,
        timeout=300,
        prefer_session=False,
        headless_fallback=True,
    )
    if not exec_result.get("success"):
        return {"success": False, "error": exec_result.get("error"), **exec_result}

    for line in (exec_result.get("output") or "").splitlines():
        if line.startswith("BATCH_RESULT:"):
            try:
                payload = json.loads(line[len("BATCH_RESULT:") :])
                return {"success": True, **payload}
            except json.JSONDecodeError:
                pass
        if line.startswith("BATCH_ERROR:"):
            return {"success": False, "error": line[len("BATCH_ERROR:") :].strip()}

    return {"success": False, "error": "No batch output from Blender"}


@blender_operation("batch_resize_images", log_args=True)
async def batch_resize_images(
    input_dir: str,
    pattern: str = "*.png",
    width: int = 1024,
    height: int = 1024,
    output_dir: str = "",
) -> dict[str, Any]:
    """Resize images in a directory using Blender image API."""
    out = output_dir or input_dir
    body = f"""
    import glob
    import os
    from pathlib import Path

    input_dir = {input_dir!r}
    output_dir = {out!r}
    pattern = {pattern!r}
    os.makedirs(output_dir, exist_ok=True)
    files = glob.glob(os.path.join(input_dir, pattern))
    processed = []
    for fp in files:
        img = bpy.data.images.load(fp, check_existing=True)
        img.scale({width}, {height})
        name = Path(fp).stem + "_resized.png"
        out_path = os.path.join(output_dir, name)
        img.filepath_raw = out_path
        img.file_format = 'PNG'
        img.save()
        processed.append(out_path)
    result = {{"operation": "resize", "count": len(processed), "files": processed, "width": {width}, "height": {height}}}
"""
    return await _run_batch_script("batch_resize_images", body)


@blender_operation("batch_convert_images", log_args=True)
async def batch_convert_images(
    input_dir: str,
    source_format: str = "jpg",
    target_format: str = "png",
    output_dir: str = "",
) -> dict[str, Any]:
    """Convert images between formats (jpg, png, tiff, exr, etc.)."""
    out = output_dir or input_dir
    src = source_format.lower().lstrip(".")
    tgt = target_format.upper().lstrip(".")
    body = f"""
    import glob
    import os
    from pathlib import Path

    input_dir = {input_dir!r}
    output_dir = {out!r}
    os.makedirs(output_dir, exist_ok=True)
    files = glob.glob(os.path.join(input_dir, "*.{src}"))
    processed = []
    for fp in files:
        img = bpy.data.images.load(fp, check_existing=True)
        name = Path(fp).stem + ".{target_format.lower()}"
        out_path = os.path.join(output_dir, name)
        img.filepath_raw = out_path
        img.file_format = {tgt!r}
        img.save()
        processed.append(out_path)
    result = {{"operation": "convert", "count": len(processed), "files": processed, "target_format": {tgt!r}}}
"""
    return await _run_batch_script("batch_convert_images", body)


@blender_operation("batch_export_objects", log_args=True)
async def batch_export_objects(
    output_dir: str,
    name_pattern: str = "",
    export_format: str = "glb",
) -> dict[str, Any]:
    """Export mesh objects matching name pattern to files."""
    fmt = export_format.lower()
    body = f"""
    import json
    import os

    output_dir = {output_dir!r}
    pattern = {name_pattern!r}.lower()
    os.makedirs(output_dir, exist_ok=True)
    exported = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        if pattern and pattern not in obj.name.lower():
            continue
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        out_path = os.path.join(output_dir, obj.name + ".{fmt}")
        if {fmt!r} == 'glb':
            bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=True)
        elif {fmt!r} == 'gltf':
            bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLTF_SEPARATE', use_selection=True)
        elif {fmt!r} == 'fbx':
            bpy.ops.export_scene.fbx(filepath=out_path, use_selection=True)
        elif {fmt!r} == 'obj':
            bpy.ops.export_scene.obj(filepath=out_path, use_selection=True)
        else:
            raise RuntimeError("Unsupported export_format: {fmt}")
        exported.append(out_path)
    result = {{"operation": "export", "count": len(exported), "files": exported, "format": {fmt!r}}}
"""
    return await _run_batch_script("batch_export_objects", body)
