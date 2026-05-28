"""Fetch Blender Python API documentation snippets for agent lookup."""

from __future__ import annotations

import logging
import re
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

_DOCS_BASE = "https://docs.blender.org/api/current"


def normalize_identifier(identifier: str) -> str:
    """Normalize user input to a bpy docs identifier (e.g. Mesh -> bpy.types.Mesh)."""
    ident = identifier.strip()
    if not ident:
        raise ValueError("identifier is required")
    if ident.startswith("bpy."):
        return ident
    if ident.startswith("types."):
        return f"bpy.{ident}"
    if ident.startswith("ops."):
        return f"bpy.{ident}"
    return f"bpy.types.{ident}"


def docs_url(identifier: str) -> str:
    """Build the blender.org API HTML URL for an identifier."""
    ident = normalize_identifier(identifier)
    return f"{_DOCS_BASE}/{ident}.html"


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = unescape(re.sub(r"\s+", " ", text)).strip()
    return text


def fetch_api_doc(identifier: str, *, max_chars: int = 12000) -> dict[str, str]:
    """Download and extract plain text from the Blender API docs page."""
    ident = normalize_identifier(identifier)
    url = docs_url(ident)
    request = Request(url, headers={"User-Agent": "blender-mcp/1.0 (api-docs)"})
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        if exc.code == 404:
            return {
                "identifier": ident,
                "url": url,
                "found": "false",
                "content": f"No documentation page found for {ident}. Try bpy.types.* or bpy.ops.* identifiers.",
            }
        raise
    except URLError as exc:
        logger.error("Failed to fetch API docs from %s: %s", url, exc)
        raise RuntimeError(f"Could not reach Blender API docs: {exc}") from exc

    content = _strip_html(raw)
    if len(content) > max_chars:
        content = content[:max_chars] + "\n\n[truncated — open URL for full page]"

    return {
        "identifier": ident,
        "url": url,
        "found": "true",
        "content": content,
    }
