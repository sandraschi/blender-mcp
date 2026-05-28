"""Shader node graph MCP tools."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _register_shader_tools() -> None:
    from blender_mcp.app import get_app
    from blender_mcp.handlers.shader_handler import (
        ShaderOperationResult,
        connect_shader_nodes,
        create_shader_material,
        create_shader_node,
    )

    app = get_app()

    @app.tool
    async def blender_shaders(
        operation: str = "create_material",
        material_name: str = "",
        node_type: str = "ShaderNodeBsdfPrincipled",
        node_name: str = "",
        from_node: str = "",
        from_socket: str = "",
        to_node: str = "",
        to_socket: str = "",
        shader_type: str = "ShaderNodeBsdfPrincipled",
        location_x: float = 0.0,
        location_y: float = 0.0,
        node_properties: dict[str, Any] | None = None,
        clear_nodes: bool = True,
    ) -> dict[str, Any]:
        """
        Shader node graph operations for materials.

        Operations:
        - create_material: create a node-based material
        - create_node: add a shader node to an existing material
        - connect_nodes: wire two shader nodes together
        - list_node_types: return common ShaderNode type names
        """
        try:
            if operation == "create_material":
                if not material_name:
                    return {"success": False, "error": "material_name is required"}
                result: ShaderOperationResult = await create_shader_material(
                    name=material_name,
                    shader_type=shader_type,
                    clear_nodes=clear_nodes,
                )
                return {"success": result.status == "SUCCESS", "result": result.to_dict()}

            if operation == "create_node":
                if not material_name:
                    return {"success": False, "error": "material_name is required"}
                result = await create_shader_node(
                    material_name=material_name,
                    node_type=node_type,
                    node_name=node_name or None,
                    location=(location_x, location_y),
                    node_properties=node_properties,
                )
                return {"success": result.status == "SUCCESS", "result": result.to_dict()}

            if operation == "connect_nodes":
                if not all([material_name, from_node, from_socket, to_node, to_socket]):
                    return {
                        "success": False,
                        "error": "material_name, from_node, from_socket, to_node, to_socket are required",
                    }
                result = await connect_shader_nodes(
                    material_name=material_name,
                    from_node=from_node,
                    from_socket=from_socket,
                    to_node=to_node,
                    to_socket=to_socket,
                )
                return {"success": result.status == "SUCCESS", "result": result.to_dict()}

            if operation == "list_node_types":
                return {
                    "success": True,
                    "node_types": [
                        "ShaderNodeBsdfPrincipled",
                        "ShaderNodeEmission",
                        "ShaderNodeMixShader",
                        "ShaderNodeTexImage",
                        "ShaderNodeTexNoise",
                        "ShaderNodeTexCoord",
                        "ShaderNodeMapping",
                        "ShaderNodeNormalMap",
                        "ShaderNodeBump",
                        "ShaderNodeValue",
                        "ShaderNodeRGB",
                    ],
                }

            return {
                "success": False,
                "error": f"Unknown operation '{operation}'",
                "available_operations": [
                    "create_material",
                    "create_node",
                    "connect_nodes",
                    "list_node_types",
                ],
            }
        except Exception as exc:
            logger.exception("blender_shaders failed: %s", exc)
            return {"success": False, "error": str(exc), "operation": operation}


_register_shader_tools()
