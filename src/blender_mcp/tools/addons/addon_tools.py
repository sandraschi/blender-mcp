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
        Manage Blender addons (portmanteau). Prefer this tool over manage_blender_addons.

        Operations:
        - list_addons / list_installed: List installed addons (requires Blender).
        - install_addon: Install from local addon_path (path to .py or folder).
        - install_from_url / install_url: Download and install from addon_url (ZIP or .py).
        - install_known: Install from known registry by addon_name.
        - uninstall_addon: Uninstall addon by addon_name.
        - enable / disable: Enable or disable an installed addon module.
        - search: Return known add-on URLs for a query (e.g. gaussian splat).
        - info: Show known addons registry and addons directory.

        Args:
            operation: list_addons | list_installed | install_addon | install_from_url | install_known | ...
            addon_name: For uninstall_addon, enable, disable, install_known.
            addon_path: For install_addon (local path).
            addon_url: For install_from_url (https URL to .zip or .py).
            search_query: For search (e.g. "gaussian splat").
            enable_on_install: Enable addon after install operations.

        Returns:
            JSON string with status/result.
        """
        import json as _json

        from blender_mcp.handlers.addon_handler import (
            KNOWN_ADDONS,
            _blender_addons_dir,
            _get_executor,
            addon_search,
            install_addon,
            install_addon_from_url,
            list_addons,
            uninstall_addon,
        )

        try:
            if operation in ("list_addons", "list_installed"):
                out = await list_addons()
                return json.dumps(out)

            if operation == "install_addon":
                if not addon_path:
                    return json.dumps({"status": "ERROR", "error": "addon_path required"})
                out = await install_addon(source=addon_path, enable_on_install=enable_on_install)
                return json.dumps(out)

            if operation in ("install_from_url", "install_url"):
                if not addon_url:
                    return json.dumps({"status": "ERROR", "error": "addon_url required"})
                out = await install_addon_from_url(addon_url, enable_after=enable_on_install)
                return json.dumps(out)

            if operation == "install_known":
                if not addon_name:
                    return json.dumps({"status": "ERROR", "error": "addon_name required"})
                if addon_name not in KNOWN_ADDONS:
                    return json.dumps(
                        {
                            "status": "ERROR",
                            "error": f"Unknown addon '{addon_name}'",
                            "known": list(KNOWN_ADDONS.keys()),
                        }
                    )
                url, desc = KNOWN_ADDONS[addon_name]
                out = await install_addon_from_url(url, enable_after=enable_on_install)
                out["addon_name"] = addon_name
                out["description"] = desc
                return json.dumps(out)

            if operation == "info":
                addons_dir = _blender_addons_dir()
                return json.dumps(
                    {
                        "status": "SUCCESS",
                        "addons_directory": str(addons_dir) if addons_dir else "not found",
                        "known_addons": [
                            {"name": k, "url": v[0], "description": v[1]} for k, v in KNOWN_ADDONS.items()
                        ],
                    }
                )

            if operation == "enable":
                if not addon_name:
                    return json.dumps({"status": "ERROR", "error": "addon_name required"})
                executor = _get_executor()
                script = f"""
import bpy
try:
    bpy.ops.preferences.addon_enable(module={_json.dumps(addon_name)})
    bpy.ops.wm.save_userpref()
    print("ENABLE_OK")
except Exception as e:
    print("ENABLE_ERR:" + str(e))
"""
                output = await executor.execute_script(script, script_name="enable_addon")
                if "ENABLE_OK" in output:
                    return json.dumps({"status": "SUCCESS", "message": f"Addon '{addon_name}' enabled"})
                return json.dumps({"status": "ERROR", "error": output[-200:]})

            if operation == "disable":
                if not addon_name:
                    return json.dumps({"status": "ERROR", "error": "addon_name required"})
                executor = _get_executor()
                script = f"""
import bpy
try:
    bpy.ops.preferences.addon_disable(module={_json.dumps(addon_name)})
    bpy.ops.wm.save_userpref()
    print("DISABLE_OK")
except Exception as e:
    print("DISABLE_ERR:" + str(e))
"""
                output = await executor.execute_script(script, script_name="disable_addon")
                if "DISABLE_OK" in output:
                    return json.dumps({"status": "SUCCESS", "message": f"Addon '{addon_name}' disabled"})
                return json.dumps({"status": "ERROR", "error": output[-200:]})

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
                    "error": (
                        f"Unknown operation: {operation}. Use list_addons, list_installed, install_addon, "
                        "install_from_url, install_known, uninstall_addon, enable, disable, search, info"
                    ),
                }
            )
        except Exception as e:
            return json.dumps({"status": "ERROR", "error": str(e)})


_register_addon_tools()
