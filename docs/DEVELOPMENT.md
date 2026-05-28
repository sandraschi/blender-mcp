# Development Setup

Contributors and webapp users. End users should use [INSTALL.md](../INSTALL.md) Option A or B.

## Tools Required

Install all of these before continuing:

| Tool | Windows | macOS | Verify |
|------|---------|-------|--------|
| uv (Python) | `winget install astral-sh.uv` | `brew install uv` | `uv --version` |
| Git | `winget install Git.Git` | `brew install git` | `git --version` |
| Node.js | `winget install OpenJS.NodeJS` | `brew install node` | `node --version` |
| Just | `winget install Casey.Just` | `brew install just` | `just --version` |
| Ruff (via uv) | `uv tool install ruff` | `uv tool install ruff` | `ruff --version` |
| Biome | `npm install -g @biomejs/biome` | `npm install -g @biomejs/biome` | `biome --version` |

After winget installs, close and reopen the terminal so PATH updates apply.

Ruff, Biome, and Just are **dev-only** — not required for `.mcpb` end-user install.

## Setup

```powershell
git clone https://github.com/sandraschi/blender-mcp
cd blender-mcp
uv sync --all-extras
just
```

The interactive recipe dashboard lists lint, test, serve, webapp, and mcpb build targets.

## Common Tasks

```powershell
just lint       # ruff + biome
just test       # pytest
just format     # ruff format
just serve      # stdio MCP (local testing)
just mcpb-pack  # dist/blender-mcp-*.mcpb
just build-native  # Tauri installer pipeline
```

Or without `just`:

```powershell
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mypy src
uv run blender-mcp --stdio
```

## Code Quality

- **Lint:** `ruff check src` — config in `pyproject.toml`
- **Format:** `ruff format src`
- **Webapp:** Biome in `webapp/` — strict `noConsoleLog`
- **Security:** `bandit`, `safety` via just recipes

Excluded from ruff: `mcpb`, `examples`, `_llm_test_scripts`. See existing ruff ignore rules in `pyproject.toml`.

## Server Entry Points

| Entry | Use |
|-------|-----|
| `uv run blender-mcp --stdio` | Claude Desktop / MCP clients |
| `uv run blender-mcp --http --port 10849` | HTTP MCP + webapp API |
| `uv run python -m blender_mcp.cli` | Module form (Windows PATH fallback) |
| `.\start.ps1` | Webapp dashboard (10848/10849) |

## MCPB Packaging

```powershell
just mcpb-pack
# or: npx @anthropic-ai/mcpb pack . dist/blender-mcp.mcpb
```

Do not use `uvx mcpb` — mcpb is npm, not PyPI.

## Code Standards

Fleet MCP standards: `D:\Dev\repos\mcp-central-docs\standards\`

- [README_STRUCTURE.md](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/README_STRUCTURE.md)
- Tool registration: `mcp-central-docs/standards/rules/mcp_registration.md`

## References

- [CONFIGURATION.md](CONFIGURATION.md) — env vars
- [ADDONS_MESH_SPLAT.md](ADDONS_MESH_SPLAT.md) — addons, mesh, splats
- [TOOLS_AND_REALTIME.md](TOOLS_AND_REALTIME.md) — tool design limits
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — debug paths
