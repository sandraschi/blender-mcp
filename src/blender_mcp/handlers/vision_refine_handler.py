"""Vision refinement loop helpers for agent review cycles."""

from __future__ import annotations

import json
import logging
from typing import Any

from ..decorators import blender_operation
from ..handlers.render_handler import render_multi_angle, screenshot_viewport
from ..utils.blender_runtime import execute_bpy_script

logger = logging.getLogger(__name__)


@blender_operation("vision_capture", log_args=True)
async def vision_capture(
    output_path: str,
    resolution_x: int = 1280,
    resolution_y: int = 720,
    prefer_session: bool = True,
) -> dict[str, Any]:
    """Capture viewport screenshot for vision model review."""
    return await screenshot_viewport(
        output_path=output_path,
        resolution_x=resolution_x,
        resolution_y=resolution_y,
        prefer_session=prefer_session,
    )


@blender_operation("vision_review_bundle", log_args=True)
async def vision_review_bundle(
    output_dir: str,
    goal: str = "",
    include_multi_angle: bool = True,
    angles: int = 4,
    prefer_session: bool = True,
) -> dict[str, Any]:
    """Build a review package: screenshot, optional multi-angle stills, scene summary."""
    from pathlib import Path

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    screenshot_path = str(out / "review_viewport.png")

    capture = await screenshot_viewport(
        output_path=screenshot_path,
        prefer_session=prefer_session,
    )

    multi: dict[str, Any] | None = None
    if include_multi_angle:
        multi = await render_multi_angle(
            output_dir=str(out / "angles"),
            angles=angles,
            prefer_session=prefer_session,
        )

    scene_summary = await _scene_summary(prefer_session=prefer_session)

    refinement_prompt = _build_refinement_prompt(goal, scene_summary)

    return {
        "success": True,
        "screenshot": capture,
        "multi_angle": multi,
        "scene_summary": scene_summary,
        "refinement_prompt": refinement_prompt,
        "message": (
            "Review bundle ready. Send screenshot (base64 in screenshot payload) to your vision "
            "model, then call blender_vision_refine operation=apply_script with corrective bpy."
        ),
    }


@blender_operation("vision_apply_script", log_args=True)
async def vision_apply_script(
    script: str,
    script_name: str = "vision_refine",
    prefer_session: bool = True,
) -> dict[str, Any]:
    """Apply agent-generated corrective bpy script after vision review."""
    if not script.strip():
        return {"success": False, "error": "script is required"}

    result = await execute_bpy_script(
        script,
        script_name=script_name,
        timeout=120,
        prefer_session=prefer_session,
        headless_fallback=True,
    )
    return {
        "success": result.get("success", False),
        "output": result.get("output", ""),
        "error": result.get("error"),
        "session_used": result.get("session_used"),
        "execution_mode": result.get("mode"),
        "message": "Refinement script applied" if result.get("success") else "Refinement script failed",
    }


async def _scene_summary(*, prefer_session: bool) -> dict[str, Any]:
    script = """
import bpy
import json

objects = []
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        objects.append({
            "name": obj.name,
            "verts": len(obj.data.vertices) if obj.data else 0,
            "location": list(obj.location),
        })

summary = {
    "scene": bpy.context.scene.name,
    "object_count": len(bpy.context.scene.objects),
    "mesh_objects": objects[:20],
}
print("SCENE_SUMMARY:" + json.dumps(summary))
"""
    result = await execute_bpy_script(
        script,
        script_name="scene_summary",
        timeout=30,
        prefer_session=prefer_session,
        headless_fallback=True,
    )
    for line in (result.get("output") or "").splitlines():
        if line.startswith("SCENE_SUMMARY:"):
            try:
                return json.loads(line[len("SCENE_SUMMARY:") :])
            except json.JSONDecodeError:
                pass
    return {"object_count": 0, "mesh_objects": []}


def _build_refinement_prompt(goal: str, scene_summary: dict[str, Any]) -> str:
    goal_line = goal.strip() or "Improve the 3D scene toward the user's stated goal."
    mesh_list = scene_summary.get("mesh_objects") or []
    mesh_names = ", ".join(o.get("name", "?") for o in mesh_list[:8]) or "(none)"
    return (
        f"Goal: {goal_line}\n"
        f"Scene '{scene_summary.get('scene', 'Scene')}' has "
        f"{scene_summary.get('object_count', 0)} object(s). "
        f"Meshes: {mesh_names}.\n"
        "Inspect the attached viewport image. List concrete fixes (scale, materials, "
        "topology, lighting, composition). Then emit a bpy script and call "
        "blender_vision_refine operation=apply_script."
    )
