"""
Addon management compatibility alias for Blender MCP.

Prefer blender_addons (tools/addons/addon_tools.py) for new integrations.
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _register_addon_tools() -> None:
    from blender_mcp.app import get_app

    app = get_app()

    @app.tool
    async def manage_blender_addons(
        operation: str = "search",
        query: str = "",
        addon_name: str = "",
        url: str = "",
        enable_after: bool = True,
        enabled_only: bool = False,
    ) -> dict[str, Any]:
        """
        Blender addon management (compatibility alias — prefer blender_addons).

        Operations mirror blender_addons: search, install_known, install_url,
        list_installed, enable, disable, info.
        """
        del enabled_only  # list_installed via blender_addons ignores this legacy flag
        op_map = {
            "install_url": "install_from_url",
            "list_installed": "list_installed",
        }
        mapped = op_map.get(operation, operation)
        try:
            result = await app.call_tool(
                "blender_addons",
                {
                    "operation": mapped,
                    "addon_name": addon_name,
                    "addon_url": url,
                    "search_query": query,
                    "enable_on_install": enable_after,
                },
            )
            payload = json.loads(result.content[0].text)
            if isinstance(payload, dict):
                payload.setdefault("success", payload.get("status") == "SUCCESS")
                payload["deprecated"] = "Use blender_addons instead of manage_blender_addons"
                return payload
            return {
                "success": True,
                "message": str(payload),
                "deprecated": "Use blender_addons instead of manage_blender_addons",
            }
        except Exception as exc:
            logger.exception("manage_blender_addons '%s' failed: %s", operation, exc)
            return {"success": False, "error": str(exc), "operation": operation}


_register_addon_tools()
