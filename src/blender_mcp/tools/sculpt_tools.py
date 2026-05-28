"""Sculpt mode MCP tools."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _register_sculpt_tools() -> None:
    from blender_mcp.app import get_app
    from blender_mcp.handlers.sculpt_handler import (
        list_sculpt_brushes,
        sculpt_dynotopo,
        sculpt_enter,
        sculpt_exit,
        sculpt_mask_clear,
        sculpt_remesh_voxel,
        sculpt_set_brush,
        sculpt_symmetrize,
    )

    app = get_app()

    @app.tool
    async def blender_sculpt(
        operation: str = "enter",
        object_name: str = "",
        brush_name: str = "Grab",
        strength: float = 0.5,
        radius: float = 50.0,
        enable_dynotopo: bool = True,
        detail_resolution: float = 6.0,
        symmetrize_direction: str = "NEGATIVE_X",
        voxel_size: float = 0.1,
        adaptivity: float = 0.0,
        target_mode: str = "OBJECT",
        prefer_session: bool = True,
    ) -> dict[str, Any]:
        """
        Sculpt mode operations for organic mesh editing.

        Operations:
        - enter: switch object to sculpt mode
        - exit: leave sculpt mode (default back to OBJECT)
        - set_brush: assign brush with strength and radius
        - dynotopo: enable/disable dynamic topology
        - symmetrize: mirror sculpt along an axis
        - mask_clear: clear sculpt mask
        - remesh_voxel: apply voxel remesh modifier
        - list_brushes: common sculpt brush names
        """
        try:
            if operation == "list_brushes":
                return {"success": True, "brushes": list_sculpt_brushes()}

            if not object_name:
                return {"success": False, "error": "object_name is required"}

            if operation == "enter":
                return await sculpt_enter(object_name, prefer_session=prefer_session)

            if operation == "exit":
                return await sculpt_exit(object_name, target_mode=target_mode, prefer_session=prefer_session)

            if operation == "set_brush":
                return await sculpt_set_brush(
                    object_name,
                    brush_name=brush_name,
                    strength=strength,
                    radius=radius,
                    prefer_session=prefer_session,
                )

            if operation == "dynotopo":
                return await sculpt_dynotopo(
                    object_name,
                    enable=enable_dynotopo,
                    detail_resolution=detail_resolution,
                    prefer_session=prefer_session,
                )

            if operation == "symmetrize":
                return await sculpt_symmetrize(
                    object_name,
                    direction=symmetrize_direction,
                    prefer_session=prefer_session,
                )

            if operation == "mask_clear":
                return await sculpt_mask_clear(object_name, prefer_session=prefer_session)

            if operation == "remesh_voxel":
                return await sculpt_remesh_voxel(
                    object_name,
                    voxel_size=voxel_size,
                    adaptivity=adaptivity,
                    prefer_session=prefer_session,
                )

            return {
                "success": False,
                "error": f"Unknown operation '{operation}'",
                "available_operations": [
                    "enter",
                    "exit",
                    "set_brush",
                    "dynotopo",
                    "symmetrize",
                    "mask_clear",
                    "remesh_voxel",
                    "list_brushes",
                ],
            }
        except Exception as exc:
            logger.exception("blender_sculpt failed: %s", exc)
            return {"success": False, "error": str(exc), "operation": operation}


_register_sculpt_tools()
