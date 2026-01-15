"""
Addon management tools for Blender MCP.

Provides tools for installing, enabling, and managing Blender addons.
"""

from blender_mcp.compat import *

from blender_mcp.app import get_app


def _register_addon_tools():
    """Register all addon-related tools."""
    app = get_app()

    @app.tool
    async def blender_addons(
        operation: str = "list_addons",
        addon_name: str = "",
        addon_path: str = "",
        enable_on_install: bool = True,
    ) -> str:
        """
        Manage Blender addons.

        Supports multiple operations through the operation parameter:
        - list_addons: List all available addons
        - install_addon: Install addon from file
        - uninstall_addon: Uninstall an addon

        Args:
            operation: Addon operation type
            addon_name: Name of the addon
            addon_path: Path to addon file for installation
            enable_on_install: Auto-enable after installation

        Returns:
            Success message with addon details
        """
        from blender_mcp.handlers.addon_handler import install_addon, uninstall_addon, list_addons

        try:
            if operation == "list_addons":
                return await list_addons()

            elif operation == "install_addon":
                if not addon_path:
                    return "addon_path parameter required"
                return await install_addon(
                    addon_path=addon_path, enable_on_install=enable_on_install
                )

            elif operation == "uninstall_addon":
                if not addon_name:
                    return "addon_name parameter required"
                return await uninstall_addon(addon_name=addon_name)

            else:
                return f"Unknown addon operation: {operation}. Available: list_addons, install_addon, uninstall_addon"

        except Exception as e:
            return f"Error in addon operation '{operation}': {str(e)}"


_register_addon_tools()
