"""
Poly Haven public JSON API (https://api.polyhaven.com).

Used for categories, search, and resolving CDN URLs from /files/{id}.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://api.polyhaven.com"
DEFAULT_HEADERS = {
    "User-Agent": "blender-mcp-fleet/1.0 (+https://github.com/sandraschi/blender-mcp)",
    "Accept": "application/json",
}

VALID_RESOLUTIONS = ("1k", "2k", "4k", "8k", "16k")


class PolyHavenAPI:
    """Thin async client for Poly Haven API endpoints."""

    def __init__(self, timeout: float = 60.0) -> None:
        self._timeout = timeout

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{BASE_URL}{path}" if path.startswith("/") else f"{BASE_URL}/{path}"
        async with httpx.AsyncClient(timeout=self._timeout, headers=DEFAULT_HEADERS) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def categories(self, asset_type: str) -> dict[str, Any]:
        """GET /categories/{hdris|textures|models}."""
        t = asset_type.lower().strip()
        if t == "all":
            t = "hdris"
        return await self._get(f"/categories/{t}")

    async def search_assets(
        self,
        asset_type: str = "hdris",
        categories: str | None = None,
        page: int = 1,
    ) -> dict[str, Any]:
        """
        GET /assets — returns a large dict of asset_id -> metadata.
        `t` is hdris | textures | models | all
        """
        tmap = {
            "hdri": "hdris",
            "hdris": "hdris",
            "texture": "textures",
            "textures": "textures",
            "model": "models",
            "models": "models",
            "all": "all",
        }
        key = asset_type.lower().strip()
        t = tmap.get(key, asset_type)
        params: dict[str, Any] = {"t": t, "page": max(1, page)}
        if categories:
            params["categories"] = categories
        return await self._get("/assets", params=params)

    async def files(self, asset_id: str) -> dict[str, Any]:
        """GET /files/{asset_id} — file tree with CDN URLs."""
        return await self._get(f"/files/{asset_id}")


def _pick_resolution(resolution: str, available: list[str]) -> str:
    r = resolution.lower().strip()
    if r in available:
        return r
    for fallback in ("4k", "2k", "1k", "8k"):
        if fallback in available:
            logger.info("Poly Haven: resolution %s not found, using %s", resolution, fallback)
            return fallback
    return available[0] if available else "4k"


def resolve_hdri_url(files_data: dict[str, Any], resolution: str, fmt: str) -> str | None:
    """Return a single .hdr or .exr URL from files JSON."""
    hdri = files_data.get("hdri") or {}
    if not hdri:
        return None
    res_keys = [k for k in hdri if isinstance(hdri[k], dict)]
    res = _pick_resolution(resolution, res_keys)
    block = hdri.get(res) or {}
    fmt = (fmt or "hdr").lower().lstrip(".")
    if fmt not in ("hdr", "exr"):
        fmt = "hdr"
    slot = block.get(fmt) or block.get("hdr") or block.get("exr")
    if isinstance(slot, dict) and slot.get("url"):
        return str(slot["url"])
    return None


def collect_bundle_entries(node: dict[str, Any]) -> list[tuple[str, str]]:
    """From a format node (e.g. gltf/fbx/blend inner dict), list all URLs + relative paths."""
    out: list[tuple[str, str]] = []
    u = node.get("url")
    if isinstance(u, str) and u.startswith("http"):
        name = u.split("/")[-1].split("?")[0] or "root"
        out.append((u, name))
    inc = node.get("include")
    if isinstance(inc, dict):
        for rel, sub in inc.items():
            if isinstance(sub, dict) and sub.get("url"):
                out.append((str(sub["url"]), rel))
    return out


def resolve_texture_blend_bundle(files_data: dict[str, Any], resolution: str) -> tuple[list[tuple[str, str]], str | None]:
    """Texture: prefer packed .blend + texture includes."""
    blend_root = files_data.get("blend") or {}
    res_keys = [k for k in blend_root if isinstance(blend_root[k], dict)]
    res = _pick_resolution(resolution, res_keys)
    block = (blend_root.get(res) or {}).get("blend") or {}
    if not block.get("url"):
        return [], None
    entries = collect_bundle_entries(block)
    primary = block.get("url")
    if not isinstance(primary, str):
        return [], None
    return entries, primary


def resolve_model_import_bundle(
    files_data: dict[str, Any],
    resolution: str,
    prefer: str = "gltf",
) -> tuple[list[tuple[str, str]], str | None]:
    """
    Model: prefer glTF (main .gltf + includes) or FBX as fallback.
    Returns download list and primary file path hint (basename of main import file).
    """
    prefer = prefer.lower().strip()
    if prefer not in ("gltf", "fbx", "blend"):
        prefer = "gltf"

    root = files_data.get(prefer) or {}
    res_keys = [k for k in root if isinstance(root[k], dict)]
    res = _pick_resolution(resolution, res_keys)
    inner = root.get(res) or {}
    fmt_key = {"gltf": "gltf", "fbx": "fbx", "blend": "blend"}[prefer]
    block = inner.get(fmt_key) or {}
    if not block.get("url"):
        if prefer == "gltf" and files_data.get("fbx"):
            return resolve_model_import_bundle(files_data, resolution, "fbx")
        if prefer == "fbx" and files_data.get("blend"):
            return resolve_model_import_bundle(files_data, resolution, "blend")
        return [], None

    entries = collect_bundle_entries(block)
    primary = block.get("url")
    if not isinstance(primary, str):
        return [], None
    return entries, primary


__all__ = [
    "PolyHavenAPI",
    "VALID_RESOLUTIONS",
    "resolve_hdri_url",
    "resolve_texture_blend_bundle",
    "resolve_model_import_bundle",
    "collect_bundle_entries",
]
