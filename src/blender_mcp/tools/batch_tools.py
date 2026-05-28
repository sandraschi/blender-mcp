"""Batch processing MCP tools."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _register_batch_tools() -> None:
    from blender_mcp.app import get_app
    from blender_mcp.handlers.batch_handler import (
        batch_convert_images,
        batch_export_objects,
        batch_resize_images,
    )

    app = get_app()

    @app.tool
    async def blender_batch(
        operation: str = "resize",
        input_dir: str = "",
        output_dir: str = "",
        pattern: str = "*.png",
        width: int = 1024,
        height: int = 1024,
        source_format: str = "jpg",
        target_format: str = "png",
        name_pattern: str = "",
        export_format: str = "glb",
    ) -> dict[str, Any]:
        """
        Batch image and mesh export operations.

        Operations:
        - resize: resize images matching pattern (default *.png)
        - convert: convert image formats in input_dir
        - export: export mesh objects whose names contain name_pattern
        """
        try:
            if operation == "resize":
                if not input_dir:
                    return {"success": False, "error": "input_dir is required"}
                return await batch_resize_images(
                    input_dir=input_dir,
                    pattern=pattern,
                    width=width,
                    height=height,
                    output_dir=output_dir,
                )

            if operation == "convert":
                if not input_dir:
                    return {"success": False, "error": "input_dir is required"}
                return await batch_convert_images(
                    input_dir=input_dir,
                    source_format=source_format,
                    target_format=target_format,
                    output_dir=output_dir,
                )

            if operation == "export":
                if not output_dir:
                    return {"success": False, "error": "output_dir is required"}
                return await batch_export_objects(
                    output_dir=output_dir,
                    name_pattern=name_pattern,
                    export_format=export_format,
                )

            return {
                "success": False,
                "error": f"Unknown operation '{operation}'",
                "available_operations": ["resize", "convert", "export"],
            }
        except Exception as exc:
            logger.exception("blender_batch failed: %s", exc)
            return {"success": False, "error": str(exc), "operation": operation}


_register_batch_tools()
