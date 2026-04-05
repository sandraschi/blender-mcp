"""Download asset bundles (URL + relative path) to a directory."""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "blender-mcp-fleet/1.0 (+https://github.com/sandraschi/blender-mcp)",
}


async def download_entry_list(entries: list[tuple[str, str]], dest_dir: Path) -> Path:
    """Download each (url, relative_path) under dest_dir, creating subfolders as needed."""
    dest_dir = dest_dir.resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=120.0, headers=HEADERS, follow_redirects=True) as client:
        for url, rel in entries:
            target = dest_dir / rel.replace("\\", "/")
            target.parent.mkdir(parents=True, exist_ok=True)
            r = await client.get(url)
            r.raise_for_status()
            target.write_bytes(r.content)
            logger.debug("Downloaded %s -> %s", url[:80], target)
    return dest_dir


async def download_single(url: str, dest_file: Path) -> Path:
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=120.0, headers=HEADERS, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        dest_file.write_bytes(r.content)
    return dest_file
