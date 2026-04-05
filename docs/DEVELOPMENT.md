# Development

## Code quality

- **Lint**: `ruff check src` (from repo root). Config in `pyproject.toml`: `[tool.ruff]`, `[tool.ruff.lint]`.
- **Format**: `ruff format src`.
- **Auto-fix**: `ruff check src --fix` (fixes import order, unused imports, etc.).

Excluded from ruff: `mcpb`, `examples`, `_llm_test_scripts`, `check_result.py`. Ignored rules include E402 (import not at top in handlers), E722 (bare except in cleanup), B904 (raise from), F403/F405 (star imports and re-exports).

## Addons, Mesh, Splat

See [ADDONS_MESH_SPLAT.md](ADDONS_MESH_SPLAT.md) for addon install/search, mesh download, and Gaussian splat import. Webapp route: `/mesh`.

## Server entry points

- **Primary**: `blender_mcp.server` (stdio/HTTP via transport). CLI: `blender-mcp --stdio` or `--http`.
- **Alternative**: `blender_mcp.server_fixed` — manual tool registration; run via `run_server(app, server_name="blender-mcp")` when `__name__ == "__main__"`.

## References

- [ADDONS_MESH_SPLAT.md](ADDONS_MESH_SPLAT.md) — Addons, mesh download, splats, webapp Mesh page.
- [GAUSSIAN_SPLATS_ADDON.md](GAUSSIAN_SPLATS_ADDON.md) — Splat add-on install.
- [TOOLS_AND_REALTIME.md](TOOLS_AND_REALTIME.md) — Tool design, realtime limits.
