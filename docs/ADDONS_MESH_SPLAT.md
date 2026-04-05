# Addons, Mesh, and Gaussian Splats

This document describes Blender MCP support for **addon management** (install/uninstall/search, including addon packs), **mesh download and import**, and **Gaussian splat** import. The webapp exposes these on the **Mesh / Collider / Splat** page.

## Addon system

Blender uses an add-on system (scripts in the addons directory). Vanilla Blender does **not** load Gaussian splat files without an add-on. The MCP server can install add-ons from URLs (ZIP or single `.py`) without opening Blender.

### MCP tool: `blender_addons`

Portmanteau tool for addon operations. Call via MCP or from the webapp **Add-ons** tab.

| Operation | Description |
|-----------|-------------|
| `list_addons` | List installed addons (requires Blender running). Returns JSON with `addons` list (`name`, `enabled`). |
| `install_from_url` | Download from `addon_url` (ZIP or .py) and extract/copy into Blender addons dir. No Blender needed. |
| `install_addon` | Install from local `addon_path` (file or folder). Uses Blender executor. |
| `uninstall_addon` | Uninstall by `addon_name`. |
| `search` | Return known add-on entries for a query (e.g. "gaussian splat"). No web crawl; uses curated list. |

Parameters: `operation`, `addon_name`, `addon_path`, `addon_url`, `search_query`, `enable_on_install`.

### Addons path

- Set `BLENDER_ADDONS_PATH` to override.
- Default: Windows `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons`; Linux `~/.config/blender/<version>/scripts/addons`. Latest version is chosen when not set.

### Known add-ons and packs

The server ships with a curated list (see `KNOWN_ADDONS` in `handlers/addon_handler.py`). Search returns these so users can install with one click (webapp: Search → Use this URL → Install).

- **Gaussian splats**: FastGS, 3dgs_blender (install one for splat import).
- **Packs** (multi-addon repos): blender_tools_collection (animation/export tools). After install, enable the sub-addons you need in Blender Preferences.
- **Single addons**: OpenScatter (scattering), Asset Bridge (download/import free assets), BlenderGIS (geographic data).

Adding more: append entries to `KNOWN_ADDONS` as `(url, description)`. Use GitHub archive URLs (e.g. `https://github.com/org/repo/archive/refs/heads/main.zip`).

See [GAUSSIAN_SPLATS_ADDON.md](GAUSSIAN_SPLATS_ADDON.md) for splat-specific install steps.

---

## Mesh download and import

### MCP tool: `blender_download`

Download a file from a URL and optionally import it into the current Blender scene.

- **Operations**: `download` (requires `url`), `info` (returns supported formats and usage).
- **Parameters**: `operation`, `url`, `import_into_scene`, `custom_filename`, `timeout`.

Supported formats (examples): OBJ, FBX, GLTF/GLB, STL, PLY, DAE, 3DS, X3D, Alembic, USD, images (PNG, JPG, EXR, HDR), .blend. File type is detected from the URL path; the file is downloaded to a temp dir and, if `import_into_scene` is true, imported via the appropriate Blender operator.

### Alternative: `blender_import`

For files already on disk: `blender_import(operation="import_fbx", filepath="/path/to/file.fbx", ...)`. Supports FBX, OBJ, GLTF, STL, PLY, CAD (STEP/IGES with conversion), etc.

---

## Gaussian splat import

### MCP tool: `blender_splatting`

Portmanteau for 3DGS operations. For import:

- **Operation**: `import_gs`.
- **Parameter**: `file_path` — path to a .ply or add-on-supported splat file (local path on the machine running the MCP server/Blender).

Other operations: `crop_and_clean`, `generate_collision_mesh`, `export_for_resonite`, `create_proxy`, `optimize_for_vr`. See tool docstring or `blender_help(operation='tool_info', tool_name='blender_splatting')`.

**Requirement**: A Gaussian splat add-on (e.g. FastGS or 3dgs_blender) must be installed and enabled in Blender. Use `blender_addons(operation='install_from_url', addon_url='...')` or the webapp Add-ons tab.

---

## Webapp: Mesh / Collider / Splat page

Route: `/mesh`. Tabs:

1. **Mesh** — URL input; "Download & import" calls `blender_download`. Use for mesh sites or any direct URL to OBJ, FBX, GLB, etc.
2. **Collider** — Short guidance: create collision geometry via Construct or Script Console (e.g. convex hull, box, sphere).
3. **Splat** — Local file path input; "Import splat" calls `blender_splatting(operation='import_gs', file_path=...)`. Requires a 3DGS add-on.
4. **Add-ons** — Install from URL, Search (known add-ons/packs), List add-ons (from Blender).

Backend health is shown; ensure the webapp backend and Blender (when listing/importing) are running as needed.

---

## References

- [GAUSSIAN_SPLATS_ADDON.md](GAUSSIAN_SPLATS_ADDON.md) — Splat add-on install summary.
- [TOOLS_AND_REALTIME.md](TOOLS_AND_REALTIME.md) — Tool design and realtime limits.
- [DEVELOPMENT.md](DEVELOPMENT.md) — Ruff, code quality, server entry points.
- Source: `handlers/addon_handler.py`, `tools/addons/addon_tools.py`, `tools/download_tools.py`, `tools/splatting_tools.py`, `webapp/frontend/src/pages/mesh-collider-splat.tsx`.
