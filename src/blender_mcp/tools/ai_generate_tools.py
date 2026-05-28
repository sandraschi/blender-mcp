"""AI mesh generation MCP tools."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _register_ai_generate_tools() -> None:
    from blender_mcp.app import get_app
    from blender_mcp.handlers.ai_generate_handler import ai_generate_mesh, get_backend_status

    app = get_app()

    @app.tool
    async def blender_ai_generate(
        operation: str = "generate",
        prompt: str = "",
        backend: str = "tripo",
        image_path: str = "",
        object_name: str = "",
        output_format: str = "glb",
        poll_timeout: int = 600,
    ) -> dict[str, Any]:
        """
        Generate 3D meshes via external AI backends and import into Blender.

        Backends (set API keys in environment):
        - tripo: TRIPO_API_KEY
        - rodin: RODIN_API_KEY or HYPER3D_API_KEY
        - hunyuan: HUNYUAN3D_API_KEY (+ optional HUNYUAN3D_API_URL)

        Operations:
        - generate: text/image-to-3D, poll, download, import
        - list_backends: show configured backends and env var names
        """
        try:
            if operation == "list_backends":
                status = get_backend_status()
                configured = [b["backend"] for b in status["backends"] if b["configured"]]
                return {
                    "success": True,
                    "backends": status["backends"],
                    "configured": configured,
                    "message": (
                        f"{len(configured)} backend(s) configured"
                        if configured
                        else "No AI backends configured. Set TRIPO_API_KEY, RODIN_API_KEY, or HUNYUAN3D_API_KEY."
                    ),
                }

            if operation == "generate":
                if not prompt.strip() and not image_path.strip():
                    return {"success": False, "error": "prompt or image_path is required"}
                return await ai_generate_mesh(
                    prompt=prompt,
                    backend=backend,
                    image_path=image_path or None,
                    object_name=object_name or None,
                    output_format=output_format,
                    poll_timeout=poll_timeout,
                )

            return {
                "success": False,
                "error": f"Unknown operation '{operation}'",
                "available_operations": ["generate", "list_backends"],
            }
        except Exception as exc:
            logger.exception("blender_ai_generate failed: %s", exc)
            return {"success": False, "error": str(exc), "operation": operation}


_register_ai_generate_tools()
