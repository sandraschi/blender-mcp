"""Vision refinement loop MCP tools."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _register_vision_refine_tools() -> None:
    from blender_mcp.app import get_app
    from blender_mcp.handlers.vision_refine_handler import (
        vision_apply_script,
        vision_capture,
        vision_review_bundle,
    )

    app = get_app()

    @app.tool
    async def blender_vision_refine(
        operation: str = "capture",
        output_path: str = "",
        output_dir: str = "",
        goal: str = "",
        script: str = "",
        resolution_x: int = 1280,
        resolution_y: int = 720,
        include_multi_angle: bool = True,
        angles: int = 4,
    ) -> dict[str, Any]:
        """
        Agent vision refinement loop: capture, review bundle, apply fixes.

        Operations:
        - capture: viewport PNG + base64 for vision models
        - review_bundle: screenshot + multi-angle stills + scene summary + refinement prompt
        - apply_script: run corrective bpy script after vision model feedback
        """
        try:
            if operation == "capture":
                if not output_path:
                    return {"success": False, "error": "output_path is required"}
                return await vision_capture(
                    output_path=output_path,
                    resolution_x=resolution_x,
                    resolution_y=resolution_y,
                )

            if operation == "review_bundle":
                if not output_dir:
                    return {"success": False, "error": "output_dir is required"}
                return await vision_review_bundle(
                    output_dir=output_dir,
                    goal=goal,
                    include_multi_angle=include_multi_angle,
                    angles=angles,
                )

            if operation == "apply_script":
                if not script.strip():
                    return {"success": False, "error": "script is required"}
                return await vision_apply_script(script=script)

            return {
                "success": False,
                "error": f"Unknown operation '{operation}'",
                "available_operations": ["capture", "review_bundle", "apply_script"],
            }
        except Exception as exc:
            logger.exception("blender_vision_refine failed: %s", exc)
            return {"success": False, "error": str(exc), "operation": operation}


_register_vision_refine_tools()
