"""Geometry Nodes MCP tools."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _register_geonodes_tools() -> None:
    from blender_mcp.app import get_app
    from blender_mcp.handlers.geonodes_handler import (
        geonodes_add_input,
        geonodes_add_node,
        geonodes_assign_modifier,
        geonodes_connect_nodes,
        geonodes_create_group,
        list_common_geonode_types,
    )

    app = get_app()

    @app.tool
    async def blender_geonodes(
        operation: str = "create_group",
        group_name: str = "GeoNodes",
        object_name: str = "",
        node_type: str = "GeometryNodeMeshCube",
        node_name: str = "",
        from_node: str = "",
        from_socket: str = "",
        to_node: str = "",
        to_socket: str = "",
        modifier_name: str = "",
        location_x: float = 0.0,
        location_y: float = 0.0,
        input_name: str = "Input",
        socket_type: str = "NodeSocketFloat",
        default_value: float = 0.0,
    ) -> dict[str, Any]:
        """
        Geometry Nodes graph operations (procedural modeling).

        Operations:
        - create_group: create or reuse a GeometryNodeTree
        - add_node: add a node to the group
        - connect_nodes: wire two nodes in the group
        - assign_modifier: attach node group to an object as Geometry Nodes modifier
        - add_input: expose a group input socket
        - list_node_types: common GeometryNode types for agents
        """
        try:
            if operation == "create_group":
                if not group_name:
                    return {"success": False, "error": "group_name is required"}
                return await geonodes_create_group(group_name=group_name)

            if operation == "add_node":
                if not group_name:
                    return {"success": False, "error": "group_name is required"}
                return await geonodes_add_node(
                    group_name=group_name,
                    node_type=node_type,
                    node_name=node_name,
                    location_x=location_x,
                    location_y=location_y,
                )

            if operation == "connect_nodes":
                if not all([group_name, from_node, from_socket, to_node, to_socket]):
                    return {
                        "success": False,
                        "error": "group_name, from_node, from_socket, to_node, to_socket are required",
                    }
                return await geonodes_connect_nodes(
                    group_name=group_name,
                    from_node=from_node,
                    from_socket=from_socket,
                    to_node=to_node,
                    to_socket=to_socket,
                )

            if operation == "assign_modifier":
                if not object_name or not group_name:
                    return {"success": False, "error": "object_name and group_name are required"}
                return await geonodes_assign_modifier(
                    object_name=object_name,
                    group_name=group_name,
                    modifier_name=modifier_name,
                )

            if operation == "add_input":
                if not group_name:
                    return {"success": False, "error": "group_name is required"}
                return await geonodes_add_input(
                    group_name=group_name,
                    socket_type=socket_type,
                    input_name=input_name,
                    default_value=default_value,
                )

            if operation == "list_node_types":
                return {"success": True, "node_types": list_common_geonode_types()}

            return {
                "success": False,
                "error": f"Unknown operation '{operation}'",
                "available_operations": [
                    "create_group",
                    "add_node",
                    "connect_nodes",
                    "assign_modifier",
                    "add_input",
                    "list_node_types",
                ],
            }
        except Exception as exc:
            logger.exception("blender_geonodes failed: %s", exc)
            return {"success": False, "error": str(exc), "operation": operation}


_register_geonodes_tools()
