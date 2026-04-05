# Gaussian Splats in Vanilla Blender

Vanilla Blender cannot load Gaussian splat files without an **add-on**. Blender MCP can install add-ons from URL (no Blender open required).

- **Search**: `blender_addons(operation="search", search_query="gaussian splat")` — returns FastGS, 3dgs_blender and other known entries.
- **Install**: `blender_addons(operation="install_from_url", addon_url="<zip_url>", enable_on_install=True)`.
- **Enable**: Blender → Edit → Preferences → Add-ons → enable the add-on.
- **Import**: `blender_splatting(operation="import_gs", file_path="...")` after add-on is enabled.

Full documentation: [ADDONS_MESH_SPLAT.md](ADDONS_MESH_SPLAT.md) (addons, mesh download, splat, webapp Mesh/Collider/Splat page).
