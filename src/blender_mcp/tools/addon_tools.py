"""
Addon management tools for Blender MCP.

Exposes addon_handler functionality as FastMCP tools:
- list known addons
- search addons
- install from URL or by name
- list installed Blender addons
- enable / disable addons
"""

import logging
from typing import Any

from blender_mcp.app import get_app
from blender_mcp.handlers.addon_handler import (
    KNOWN_ADDONS,
    _blender_addons_dir,
    _get_executor,
    addon_search,
    install_addon_from_url,
)

logger = logging.getLogger(__name__)


def _register_addon_tools() -> None:
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
        Blender addon management: search known addons, install, enable, disable, list.

        Operations:
        - search: search the known-addons registry by keyword (e.g. "gaussian", "splat", "gis")
        - install_known: install a known addon by name (see 'search' for names)
        - install_url: install addon from an arbitrary URL (zip or .py)
        - list_installed: list addons currently visible to Blender (via bpy preferences)
        - enable: enable an installed addon by module name
        - disable: disable an installed addon by module name
        - info: show known addons registry and addons directory

        Known addon names (use with install_known):
          gaussian_splat, 3dgs_blender, openscatter, asset_bridge, blender_gis,
          blender_tools_collection

        Args:
            operation: Operation to perform (see above)
            query: Search query for 'search' operation
            addon_name: Addon name for install_known / enable / disable
            url: URL for install_url operation
            enable_after: Enable addon after installation (default True)
            enabled_only: For list_installed, only show enabled addons

        Returns:
            Dict with success, message, and operation-specific data
        """
        try:
            if operation == "search":
                return addon_search(query)

            elif operation == "info":
                addons_dir = _blender_addons_dir()
                return {
                    "success": True,
                    "addons_directory": str(addons_dir) if addons_dir else "not found",
                    "known_addons": [{"name": k, "url": v[0], "description": v[1]} for k, v in KNOWN_ADDONS.items()],
                    "hint": "Use operation='install_known' with addon_name to install.",
                }

            elif operation == "install_known":
                if not addon_name:
                    return {"success": False, "error": "addon_name required for install_known"}
                if addon_name not in KNOWN_ADDONS:
                    close = [k for k in KNOWN_ADDONS if addon_name.lower() in k.lower()]
                    return {
                        "success": False,
                        "error": f"Unknown addon '{addon_name}'",
                        "suggestions": close,
                        "known": list(KNOWN_ADDONS.keys()),
                    }
                addon_url, description = KNOWN_ADDONS[addon_name]
                result = await install_addon_from_url(addon_url, enable_after=enable_after)
                result["addon_name"] = addon_name
                result["description"] = description
                if result.get("status") == "SUCCESS":
                    result["success"] = True
                    result["message"] = (
                        f"Installed '{addon_name}' from GitHub. Restart Blender or use enable operation to activate."
                    )
                    if addon_name in ("gaussian_splat", "3dgs_blender"):
                        result["splat_note"] = (
                            "After enabling in Blender, use blender_splatting('import_gs') "
                            "to import .ply Gaussian Splat files from WorldLabs or other sources."
                        )
                else:
                    result["success"] = False
                return result

            elif operation == "install_url":
                if not url:
                    return {"success": False, "error": "url required for install_url"}
                result = await install_addon_from_url(url, enable_after=enable_after)
                result["success"] = result.get("status") == "SUCCESS"
                return result

            elif operation == "list_installed":
                executor = _get_executor()
                import json as _json

                script = f"""
import bpy, json
enabled_only = {enabled_only!s}
addons = []
for mod_name in bpy.context.preferences.addons.keys():
    if not enabled_only or mod_name:  # all enabled addons are already in preferences.addons
        addons.append({{"module": mod_name, "enabled": True}})
print("ADDONS:" + json.dumps(addons))
"""
                output = await executor.execute_script(script, script_name="list_addons")
                addons = []
                for line in output.splitlines():
                    if line.startswith("ADDONS:"):
                        addons = _json.loads(line[len("ADDONS:") :])
                return {"success": True, "addons": addons, "count": len(addons)}

            elif operation == "enable":
                if not addon_name:
                    return {"success": False, "error": "addon_name required for enable"}
                executor = _get_executor()
                import json as _json2

                en_script = f"""
import bpy
try:
    bpy.ops.preferences.addon_enable(module={_json2.dumps(addon_name)})
    bpy.ops.wm.save_userpref()
    print("ENABLE_OK")
except Exception as e:
    print("ENABLE_ERR:" + str(e))
"""
                output = await executor.execute_script(en_script, script_name="enable_addon")
                if "ENABLE_OK" in output:
                    return {"success": True, "message": f"Addon '{addon_name}' enabled"}
                err = next(
                    (l[len("ENABLE_ERR:") :] for l in output.splitlines() if l.startswith("ENABLE_ERR:")), output[-200:]
                )
                return {"success": False, "error": err}

            elif operation == "disable":
                if not addon_name:
                    return {"success": False, "error": "addon_name required for disable"}
                executor = _get_executor()
                import json as _json3

                dis_script = f"""
import bpy
try:
    bpy.ops.preferences.addon_disable(module={_json3.dumps(addon_name)})
    bpy.ops.wm.save_userpref()
    print("DISABLE_OK")
except Exception as e:
    print("DISABLE_ERR:" + str(e))
"""
                output = await executor.execute_script(dis_script, script_name="disable_addon")
                if "DISABLE_OK" in output:
                    return {"success": True, "message": f"Addon '{addon_name}' disabled"}
                err = next(
                    (l[len("DISABLE_ERR:") :] for l in output.splitlines() if l.startswith("DISABLE_ERR:")),
                    output[-200:],
                )
                return {"success": False, "error": err}

            else:
                return {
                    "success": False,
                    "error": f"Unknown operation '{operation}'",
                    "available_operations": [
                        "search",
                        "info",
                        "install_known",
                        "install_url",
                        "list_installed",
                        "enable",
                        "disable",
                    ],
                }

        except Exception as e:
            logger.exception(f"manage_blender_addons '{operation}' failed: {e}")
            return {"success": False, "error": str(e), "operation": operation}


_register_addon_tools()
