# Onboarding — blender-mcp in 5 minutes

You need exactly two things. Everything else is optional.

## The two things

1. **MCP server** (`blender-mcp-*.mcpb`) — [Latest release](https://github.com/sandraschi/blender-mcp/releases/latest).
   Drag it into **Claude Desktop** (Settings → MCP Servers → Install from file).
2. **Blender 3.0+** — [blender.org/download](https://www.blender.org/download/).
   Installed separately, never bundled. Tell the server where it is with
   `BLENDER_EXECUTABLE` only if it is not on PATH (see [CONFIGURATION](CONFIGURATION.md)).

Then restart Claude Desktop and try:

> Create a red cube on a gray floor with a sun lamp.

Most tools run **headless** — the server spawns `blender --background` itself.
You do **not** need to open Blender's UI.

## Pass criteria

- The server appears in Claude Desktop's MCP list with no terminal steps.
- The red-cube prompt produces MCP tool calls (`blender_mesh`, …) and a scene update.
- If Blender is missing you get a clear error naming `BLENDER_EXECUTABLE`, not a crash.

## Optional next steps (skip all of these on day one)

- **Live viewport** — install `addon/blender_bridge_addon.py` in Blender and use the
  `blender_session` start tool to watch the agent build.
  ([bridge guide](../INSTALL.md#optional-live-blender-viewport-bridge-addon))
- **Web dashboard** — run `.\start.ps1` from the repo, open http://localhost:10848.
- **Local LLM script generation** — point the dashboard Settings page at Ollama
  (`http://localhost:11434`) or LM Studio (`http://localhost:1234`).
- **Developers** — [DEVELOPMENT](DEVELOPMENT.md), [TOOLS](TOOLS.md),
  [TROUBLESHOOTING](TROUBLESHOOTING.md).

## First-run sanity check (dashboard)

Backend dot green at http://localhost:10849/api/v1/health, tool count > 0 at
http://localhost:10849/api/capabilities. If the dot is red, the dashboard retries
with backoff and offers Restart Backend — no reinstall needed.
