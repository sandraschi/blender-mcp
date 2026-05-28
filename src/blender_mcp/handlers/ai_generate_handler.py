"""AI mesh generation and Blender import."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..decorators import blender_operation
from ..utils.ai_mesh_backends import GenerationJob, MeshBackend, list_backends, submit_generation
from ..utils.blender_runtime import execute_bpy_script

logger = logging.getLogger(__name__)

_FORMAT_IMPORTERS = {
    ".glb": ("import_scene.gltf", {"filepath": None}),
    ".gltf": ("import_scene.gltf", {"filepath": None}),
    ".fbx": ("import_scene.fbx", {"filepath": None}),
    ".obj": ("import_scene.obj", {"filepath": None}),
    ".stl": ("import_mesh.stl", {"filepath": None}),
}


@blender_operation("ai_generate_mesh", log_args=True)
async def ai_generate_mesh(
    prompt: str,
    backend: str = "tripo",
    image_path: str | None = None,
    object_name: str | None = None,
    output_format: str = "glb",
    poll_timeout: int = 600,
    prefer_session: bool = True,
) -> dict[str, Any]:
    """Generate a mesh via external AI backend and import into Blender."""
    try:
        job: GenerationJob = await submit_generation(
            backend=MeshBackend(backend.lower()),
            prompt=prompt,
            image_path=image_path,
            output_format=output_format,
            poll_timeout=poll_timeout,
        )
    except Exception as exc:
        logger.error("AI mesh generation failed: %s", exc)
        return {"success": False, "error": str(exc), "backend": backend}

    if not job.local_path:
        return {"success": False, "error": "Generation completed but no local file path", "job_id": job.job_id}

    import_result = await _import_mesh_file(job.local_path, object_name, prefer_session=prefer_session)
    return {
        "success": import_result.get("success", False),
        "backend": job.backend.value,
        "job_id": job.job_id,
        "local_path": job.local_path,
        "prompt": prompt,
        **import_result,
    }


async def _import_mesh_file(
    file_path: str,
    object_name: str | None,
    *,
    prefer_session: bool,
) -> dict[str, Any]:
    path = Path(file_path)
    ext = path.suffix.lower()
    importer = _FORMAT_IMPORTERS.get(ext)
    if not importer:
        return {"success": False, "error": f"Unsupported generated format: {ext}"}

    op_path, _ = importer
    rename_block = ""
    if object_name:
        rename_block = f"""
for obj in bpy.context.selected_objects:
    obj.name = {object_name!r}
"""

    script = f"""
import bpy
import json

filepath = {str(path.absolute())!r}
bpy.ops.{op_path}(filepath=filepath)
imported = [o.name for o in bpy.context.selected_objects]
{rename_block}
print("AI_IMPORT_OBJECTS:" + json.dumps(imported))
"""

    result = await execute_bpy_script(
        script,
        script_name="ai_import_mesh",
        timeout=120,
        prefer_session=prefer_session,
        headless_fallback=True,
    )
    if not result.get("success"):
        return {"success": False, "error": result.get("error"), "session_used": result.get("session_used")}

    imported: list[str] = []
    for line in (result.get("output") or "").splitlines():
        if line.startswith("AI_IMPORT_OBJECTS:"):
            import json as _json

            try:
                imported = _json.loads(line[len("AI_IMPORT_OBJECTS:") :])
            except Exception:
                pass

    return {
        "success": True,
        "imported_objects": imported,
        "session_used": result.get("session_used"),
        "execution_mode": result.get("mode"),
        "message": f"Imported {len(imported)} object(s) from AI generation",
    }


def get_backend_status() -> dict[str, Any]:
    """Return backend configuration for agents."""
    return {"backends": list_backends()}
