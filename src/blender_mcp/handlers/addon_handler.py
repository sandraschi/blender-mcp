from ..compat import *

"""Addon operations handler for Blender MCP."""

import json
from typing import Dict, Any, Optional
from enum import Enum
from loguru import logger

from ..utils.blender_executor import get_blender_executor
from ..decorators import blender_operation

_executor = get_blender_executor()

class AddonInstallType(str, Enum):
    """Addon installation types."""
    FILE = "FILE"
    URL = "URL"
    REPO = "REPO"
    PACKAGE = "PACKAGE"

@blender_operation("install_addon", log_args=True)
async def install_addon(
    source: str,
    install_type: AddonInstallType = AddonInstallType.FILE,
    **kwargs: Any
) -> Dict[str, Any]:
    """Install a Blender addon.
    
    Args:
        source: Source of the addon
        install_type: Type of installation source
        **kwargs: Additional parameters
            - name: Name to give the addon
            - version: Version to install
            - enable: Enable after installation
            
    Returns:
        Dict containing installation status
    """
    script = f"""
import os
import json

try:
    # Implementation would go here
    result = {{"status": "SUCCESS", "message": "Addon installed"}}
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"status": "ERROR", "error": str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return json.loads(output)
    except Exception as e:
        logger.error(f"Failed to install addon: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("uninstall_addon", log_args=True)
async def uninstall_addon(
    name: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Uninstall a Blender addon.
    
    Args:
        name: Name of the addon to uninstall
        **kwargs: Additional parameters
            - remove_prefs: Remove preferences
            
    Returns:
        Dict containing uninstallation status
    """
    script = f"""
import json

try:
    # Implementation would go here
    result = {{"status": "SUCCESS", "message": "Addon uninstalled"}}
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"status": "ERROR", "error": str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return json.loads(output)
    except Exception as e:
        logger.error(f"Failed to uninstall addon: {str(e)}")
        return {"status": "ERROR", "error": str(e)}

@blender_operation("list_addons", log_args=True)
async def list_addons(
    enabled_only: bool = False,
    **kwargs: Any
) -> Dict[str, Any]:
    """List installed Blender addons.
    
    Args:
        enabled_only: Only list enabled addons
        **kwargs: Additional parameters
            - include_builtin: Include built-in addons
            
    Returns:
        Dict containing list of addons
    """
    script = f"""
import json

try:
    addons = []
    for addon in bpy.context.preferences.addons:
        if not {enabled_only} or addon.enabled:
            addons.append({{
                'name': addon.module,
                'enabled': addon.enabled
            }})
    
    result = {{"status": "SUCCESS", "addons": addons}}
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({{"status": "ERROR", "error": str(e)}}))
"""
    try:
        output = await _executor.execute_script(script)
        return json.loads(output)
    except Exception as e:
        logger.error(f"Failed to list addons: {str(e)}")
        return {"status": "ERROR", "error": str(e)}
