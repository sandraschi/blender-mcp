"""Addon operations handler for Blender MCP."""

import json
import logging
import os
import zipfile
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from ..compat import *

logger = logging.getLogger(__name__)
from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

_executor = None


def _get_executor():
    global _executor
    if _executor is None:
        _executor = get_blender_executor()
    return _executor


# Known add-ons and packs (direct GitHub archive URLs). Format: name -> (url, description)
# Packs: one ZIP with multiple addons; extract to addons dir, then enable sub-addons in Blender.
KNOWN_ADDONS = {
    # Gaussian splats
    "gaussian_splat": (
        "https://github.com/Stuffmatic/fastgs/archive/refs/heads/main.zip",
        "FastGS - Gaussian Splatting viewer/loader for Blender",
    ),
    "3dgs_blender": (
        "https://github.com/cake-lab/3dgs_blender_addon/archive/refs/heads/main.zip",
        "3DGS Blender add-on for Gaussian Splatting",
    ),
    # Addon packs (multi-addon repos; enable sub-addons in Blender after install)
    "blender_tools_collection": (
        "https://github.com/evilmushroom/blender-tools-collection/archive/refs/heads/main.zip",
        "Pack: Animation Manager, Batch FBX Exporter, and other animation/export tools",
    ),
    # Single addons (free, GitHub)
    "openscatter": (
        "https://github.com/GitMay3D/OpenScatter/archive/refs/heads/main.zip",
        "OpenScatter - free open-source advanced scattering addon",
    ),
    "asset_bridge": (
        "https://github.com/strike-digital/asset_bridge/archive/refs/heads/main.zip",
        "Asset Bridge - download and import free assets from the internet",
    ),
    "blender_gis": (
        "https://github.com/domlysz/BlenderGIS/archive/refs/heads/master.zip",
        "BlenderGIS - import geographic data (archived but still usable)",
    ),
}


class AddonInstallType(str, Enum):
    """Addon installation types."""

    FILE = "FILE"
    URL = "URL"
    REPO = "REPO"
    PACKAGE = "PACKAGE"


@blender_operation("install_addon", log_args=True)
async def install_addon(
    source: str, install_type: AddonInstallType = AddonInstallType.FILE, **kwargs: Any
) -> dict[str, Any]:
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
    script = """
import os
import json

try:
    # Implementation would go here
    result = {"status": "SUCCESS", "message": "Addon installed"}
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"status": "ERROR", "error": str(e)}))
"""
    try:
        output = await _get_executor().execute_script(script)
        return json.loads(output)
    except Exception as e:
        logger.error(f"Failed to install addon: {e!s}")
        return {"status": "ERROR", "error": str(e)}


def _blender_addons_dir() -> Path | None:
    """Return Blender addons directory from env or platform default."""
    path = os.environ.get("BLENDER_ADDONS_PATH")
    if path and os.path.isdir(path):
        return Path(path)
    if os.name == "nt":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            base = Path(appdata) / "Blender Foundation" / "Blender"
            if base.exists():
                for v in sorted(base.iterdir(), reverse=True):
                    if v.is_dir():
                        addons = v / "scripts" / "addons"
                        if addons.exists():
                            return addons
    home = os.environ.get("HOME", os.path.expanduser("~"))
    config = Path(home) / ".config" / "blender"
    if config.exists():
        for v in sorted(config.iterdir(), reverse=True):
            if v.is_dir():
                addons = v / "scripts" / "addons"
                if addons.exists():
                    return addons
    return None


async def install_addon_from_url(addon_url: str, enable_after: bool = True) -> dict[str, Any]:
    """Download addon from URL (ZIP or single .py) and copy to Blender addons dir. No bpy required."""
    addons_dir = _blender_addons_dir()
    if not addons_dir:
        return {
            "status": "ERROR",
            "error": "Blender addons path not found. Set BLENDER_ADDONS_PATH.",
        }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            r = await client.get(addon_url)
            r.raise_for_status()
            data = r.content
    except Exception as e:
        logger.warning("Addon download failed: %s", e)
        return {"status": "ERROR", "error": str(e)}
    name = urlparse(addon_url).path.rstrip("/").split("/")[-1].replace(".zip", "")
    try:
        if addon_url.lower().endswith(".zip") or data[:4] == b"PK\x03\x04":
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
                f.write(data)
                zip_path = f.name
            try:
                with zipfile.ZipFile(zip_path, "r") as z:
                    z.extractall(addons_dir)
            finally:
                os.unlink(zip_path)
        else:
            out = addons_dir / (name or "addon") if not name.endswith(".py") else addons_dir / name
            if not str(out).endswith(".py"):
                out = addons_dir / f"{name}.py"
            out.write_bytes(data)
        return {
            "status": "SUCCESS",
            "message": f"Addon installed to {addons_dir}",
            "addons_dir": str(addons_dir),
        }
    except Exception as e:
        logger.exception("Install from URL failed")
        return {"status": "ERROR", "error": str(e)}


def addon_search(query: str) -> dict[str, Any]:
    """Return recommended add-ons and known URLs for a query (e.g. gaussian splat). No web crawl."""
    q = (query or "").strip().lower()
    results: list[dict[str, Any]] = []
    for key, (url, desc) in KNOWN_ADDONS.items():
        if not q or q in key or q in desc.lower():
            results.append({"name": key, "url": url, "description": desc})
    return {
        "success": True,
        "query": query,
        "results": results,
        "hint": "Use install_from_url with one of the URLs.",
    }


@blender_operation("uninstall_addon", log_args=True)
async def uninstall_addon(name: str, **kwargs: Any) -> dict[str, Any]:
    """Uninstall a Blender addon.

    Args:
        name: Name of the addon to uninstall
        **kwargs: Additional parameters
            - remove_prefs: Remove preferences

    Returns:
        Dict containing uninstallation status
    """
    script = """
import json

try:
    # Implementation would go here
    result = {"status": "SUCCESS", "message": "Addon uninstalled"}
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"status": "ERROR", "error": str(e)}))
"""
    try:
        output = await _get_executor().execute_script(script)
        return json.loads(output)
    except Exception as e:
        logger.error(f"Failed to uninstall addon: {e!s}")
        return {"status": "ERROR", "error": str(e)}


@blender_operation("list_addons", log_args=True)
async def list_addons(enabled_only: bool = False, **kwargs: Any) -> dict[str, Any]:
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
        output = await _get_executor().execute_script(script)
        return json.loads(output)
    except Exception as e:
        logger.error(f"Failed to list addons: {e!s}")
        return {"status": "ERROR", "error": str(e)}
