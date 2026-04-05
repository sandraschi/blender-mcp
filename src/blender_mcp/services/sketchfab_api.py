"""Sketchfab REST API v3 (search + download). Requires SKETCHFAB_API_TOKEN."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

API_BASE = "https://api.sketchfab.com/v3"
DEFAULT_HEADERS = {
    "User-Agent": "blender-mcp-fleet/1.0 (+https://github.com/sandraschi/blender-mcp)",
    "Accept": "application/json",
}


class SketchfabAPI:
    def __init__(self, api_token: str | None = None, timeout: float = 60.0) -> None:
        self._token = (api_token or os.environ.get("SKETCHFAB_API_TOKEN") or "").strip()
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        if not self._token:
            raise ValueError(
                "Sketchfab API token missing. Set environment variable SKETCHFAB_API_TOKEN "
                "(see https://sketchfab.com/settings/password → API token)."
            )
        h = dict(DEFAULT_HEADERS)
        h["Authorization"] = f"Token {self._token}"
        return h

    async def search_models(
        self,
        query: str,
        categories: str | None = None,
        count: int = 24,
        downloadable: bool = True,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "type": "models",
            "q": query,
            "count": min(max(1, count), 100),
            "downloadable": int(downloadable),
        }
        if categories:
            params["categories"] = categories
        async with httpx.AsyncClient(timeout=self._timeout, headers=self._headers()) as client:
            r = await client.get(f"{API_BASE}/search", params=params)
            r.raise_for_status()
            return r.json()

    async def download_info(self, uid: str) -> dict[str, Any]:
        """GET /models/{uid}/download — signed URLs for glTF/OBJ sources."""
        async with httpx.AsyncClient(timeout=self._timeout, headers=self._headers()) as client:
            r = await client.get(f"{API_BASE}/models/{uid}/download")
            r.raise_for_status()
            return r.json()


__all__ = ["SketchfabAPI"]
