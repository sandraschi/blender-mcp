"""
Addon management tools for Blender MCP.

Provides tools for installing (local path or URL), uninstall, list, and search (known add-ons).
"""

import json

from blender_mcp.app import get_app
from blender_mcp.compat import *


def _register_addon_tools():
    """Register all addon-related tools."""
    app = get_app()

    @app.tool
    async def blender_addons(
        operation: str = "list_addons",
        addon_name: str = "",
        addon_path: str = "",
        addon_url: str = "",
        search_query: str = "",
        enable_on_install: bool = True,
    ) -> str:
        """
        Manage Blender addons (portmanteau).

        Operations:
        - list_addons: List installed addons (requires Blender).
        - install_addon: Install from local addon_path (path to .py or folder).
        - install_from_url: Download and install from addon_url (ZIP or .py). No Blender needed.
        - uninstall_addon: Uninstall addon by addon_name.
        - search: Return known add-on URLs for a query (e.g. gaussian splat). No web crawl.

        Args:
            operation: list_addons | install_addon | install_from_url | uninstall_addon | search
            addon_name: For uninstall_addon.
            addon_path: For install_addon (local path).
            addon_url: For install_from_url (https URL to .zip or .py).
            search_query: For search (e.g. "gaussian splat").
            enable_on_install: For install_addon.

        Returns:
            JSON string or message with status/result.
        """
        from blender_mcp.handlers.addon_handler import (
            addon_search,
            install_addon,
            install_addon_from_url,
            list_addons,
            uninstall_addon,
        )

        try:
            if operation == "list_addons":
                out = await list_addons()
                return json.dumps(out)

            if operation == "install_addon":
                if not addon_path:
                    return json.dumps({"status": "ERROR", "error": "addon_path required"})
                out = await install_addon(source=addon_path, enable_on_install=enable_on_install)
                return json.dumps(out)

            if operation == "install_from_url":
                if not addon_url:
                    return json.dumps({"status": "ERROR", "error": "addon_url required"})
                out = await install_addon_from_url(addon_url, enable_after=enable_on_install)
                return json.dumps(out)

            if operation == "uninstall_addon":
                if not addon_name:
                    return json.dumps({"status": "ERROR", "error": "addon_name required"})
                out = await uninstall_addon(name=addon_name)
                return json.dumps(out)

            if operation == "search":
                out = addon_search(search_query)
                return json.dumps(out)

            return json.dumps(
                {
                    "status": "ERROR",
                    "error": f"Unknown operation: {operation}. Use list_addons, install_addon, install_from_url, uninstall_addon, search",
                }
            )
        except Exception as e:
            return json.dumps({"status": "ERROR", "error": str(e)})


_register_addon_tools()
