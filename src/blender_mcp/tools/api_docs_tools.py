"""Blender Python API documentation lookup tool."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def _register_api_docs_tools() -> None:
    from blender_mcp.app import get_app
    from blender_mcp.utils.bpy_api_docs import fetch_api_doc, normalize_identifier

    app = get_app()

    @app.tool
    async def blender_api_docs(
        identifier: str = "bpy.types.Object",
        search: str = "",
    ) -> dict[str, str | bool]:
        """
        Look up Blender Python API documentation for an identifier.

        Examples: ``Mesh``, ``bpy.types.Mesh``, ``bpy.ops.mesh.primitive_cube_add``.

        Use before writing bpy scripts to reduce hallucinated API calls.
        """
        try:
            if search.strip():
                # Simple discovery hint — full search would need an index
                guess = normalize_identifier(search.strip())
                doc = fetch_api_doc(guess)
                doc["search_term"] = search
                doc["success"] = doc.get("found") == "true"
                return doc

            doc = fetch_api_doc(identifier)
            doc["success"] = doc.get("found") == "true"
            return doc
        except Exception as exc:
            logger.exception("blender_api_docs failed: %s", exc)
            return {"success": False, "error": str(exc), "identifier": identifier}


_register_api_docs_tools()
