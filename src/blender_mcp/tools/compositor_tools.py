"""Compositor node graph MCP tools."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _register_compositor_tools() -> None:
    from blender_mcp.app import get_app
    from blender_mcp.handlers.compositor_handler import (
        add_compositor_node,
        connect_compositor_nodes,
        create_glow_effect,
        enable_compositor,
    )

    app = get_app()

    @app.tool
    async def blender_compositor(
        operation: str = "enable",
        node_type: str = "CompositorNodeBlur",
        node_name: str = "",
        from_node: str = "",
        from_socket: str = "",
        to_node: str = "",
        to_socket: str = "",
        location_x: float = 0.0,
        location_y: float = 0.0,
        use_sequencer: bool = False,
        glow_threshold: float = 0.8,
        glow_size: int = 10,
        glow_quality: int = 2,
    ) -> dict[str, Any]:
        """
        Compositor graph operations for post-processing.

        Operations:
        - enable: turn on compositor nodes with render layers -> composite wiring
        - add_node: add a compositor node
        - connect_nodes: connect two compositor nodes
        - glow: add a glow/glare effect chain
        """
        try:
            if operation == "enable":
                result = await enable_compositor(use_nodes=True, use_sequencer=use_sequencer)
                return {"success": result.get("status") == "SUCCESS", **result}

            if operation == "add_node":
                result = await add_compositor_node(
                    node_type=node_type,
                    node_name=node_name or None,
                    location=(location_x, location_y),
                )
                return {"success": result.get("status") == "SUCCESS", **result}

            if operation == "connect_nodes":
                if not all([from_node, from_socket, to_node, to_socket]):
                    return {
                        "success": False,
                        "error": "from_node, from_socket, to_node, to_socket are required",
                    }
                result = await connect_compositor_nodes(
                    from_node=from_node,
                    from_socket=from_socket,
                    to_node=to_node,
                    to_socket=to_socket,
                )
                return {"success": result.get("status") == "SUCCESS", **result}

            if operation == "glow":
                result = await create_glow_effect(
                    threshold=glow_threshold,
                    size=glow_size,
                    quality=glow_quality,
                )
                return {"success": result.get("status") == "SUCCESS", **result}

            return {
                "success": False,
                "error": f"Unknown operation '{operation}'",
                "available_operations": ["enable", "add_node", "connect_nodes", "glow"],
            }
        except Exception as exc:
            logger.exception("blender_compositor failed: %s", exc)
            return {"success": False, "error": str(exc), "operation": operation}


_register_compositor_tools()
