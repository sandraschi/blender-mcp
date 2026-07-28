# Installing blender-mcp

Control Blender from Claude Desktop (or Cursor) via MCP.

## Downloads

| Artifact | Link | Required? |
|----------|------|-----------|
| **MCP server** (`blender-mcp-*.mcpb`) | [Latest release](https://github.com/sandraschi/blender-mcp/releases/latest) | Yes |
| **Blender 3.0+** | [blender.org/download](https://www.blender.org/download/) | Yes (for 3D tools) |
| **Bridge addon** (`blender_bridge_addon.py`) | [Download from release](https://github.com/sandraschi/blender-mcp/releases/latest/download/blender_bridge_addon.py) | No — live viewport only |

---

## Quick Start (recommended)

1. Open [Releases](https://github.com/sandraschi/blender-mcp/releases/latest)
2. Download `blender-mcp-*.mcpb`
3. Open Claude Desktop
4. Drag the `.mcpb` onto the window, or **Settings → MCP Servers → Install from file**
5. Install [Blender](https://www.blender.org/download/) if you have not already
6. Restart Claude Desktop if prompted

**Pass criteria:** server appears in the MCP list with no terminal steps.

### Verify

In Claude Desktop, try:

> Create a red cube in Blender and tell me what you built.

You should see MCP tool calls (`blender_mesh`, `blender_materials`, etc.) and a scene update.
If Blender is missing, set `BLENDER_EXECUTABLE` ([Configuration](docs/CONFIGURATION.md)) and retry.

---

## Optional: Live Blender viewport (bridge addon)

**Skip this section** if headless use is fine — most tools work without opening Blender's UI.

The bridge addon lets you **watch** the agent build in Blender and enables viewport screenshots via a live session.

1. Download [blender_bridge_addon.py](https://github.com/sandraschi/blender-mcp/releases/latest/download/blender_bridge_addon.py) (also in [addon/](addon/blender_bridge_addon.py) in this repo)
2. Start HTTP MCP: `.\start.ps1` or `uv run blender-mcp --http --port 10849`
3. MCP tool `blender_session` → `start` (opens Blender GUI)
4. In Blender:
   - **Edit → Preferences → Add-ons → Install** → select `blender_bridge_addon.py`
   - Enable **Blender MCP Bridge**
   - **Properties → Scene → Blender MCP Bridge → Start Bridge**
5. Use `blender_render` → `screenshot_viewport` for vision feedback

Without the bridge, tools fall back to headless Blender execution.

---

## Other install methods

### Option B — mcpb CLI

Requires Node.js. `mcpb` is **not** on PyPI — `uvx mcpb` will fail.

```powershell
winget install OpenJS.NodeJS --accept-source-agreements --accept-package-agreements
# Close and reopen terminal, then:
npx @anthropic-ai/mcpb install https://github.com/sandraschi/blender-mcp
```

Restart Claude Desktop after install completes.

### Option C — Manual configuration

For running from a cloned repo (stdio MCP in Claude Desktop):

```powershell
winget install astral-sh.uv --accept-source-agreements --accept-package-agreements
winget install Git.Git --accept-source-agreements --accept-package-agreements
# Close and reopen terminal

git clone https://github.com/sandraschi/blender-mcp
cd blender-mcp
uv sync --all-extras
```

Edit Claude Desktop config:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add (replace the path with your clone location):

```json
{
  "mcpServers": {
    "blender-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\blender-mcp",
        "run",
        "blender-mcp",
        "--stdio"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

Restart Claude Desktop.

**Windows note:** if `blender-mcp` is not on PATH outside uv, use `python -m blender_mcp.cli --stdio`
as the args tail instead of `blender-mcp --stdio`.

### Option D — Developer mode

Contributors and webapp/dashboard users: clone, sync, and use `just` recipes.

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for winget dev-tool setup, lint/test/build, and mcpb packaging.

Quick path:

```powershell
winget install astral-sh.uv
winget install Git.Git
winget install Casey.Just
git clone https://github.com/sandraschi/blender-mcp
cd blender-mcp
uv sync --all-extras
just
```

---

## Webapp dashboard (optional)

React dashboard on **http://localhost:10848** (API on **10849**):

```powershell
.\start.ps1
```

Flags: `-Headless`, `-BackendOnly`, `-NoBrowser`. Requires Option D setup (`uv sync`, webapp deps via `just`).

---

## Other MCP clients (Cursor, VS Code)

Same invocation as Option C — stdio via `uv run blender-mcp --stdio` or
`python -m blender_mcp.cli --stdio`.

---

## Prerequisites

### Required

| Tool | Purpose | Install |
|------|---------|---------|
| **Claude Desktop** (or MCP client) | Host app | [claude.ai/download](https://claude.ai/download) |
| **Blender 3.0+** | Mesh, materials, render, export | [blender.org/download](https://www.blender.org/download/) |

Blender is **never bundled** in `.mcpb`, Tauri installer, or release assets.

Set path if auto-detection fails ([docs/CONFIGURATION.md](docs/CONFIGURATION.md)):

```powershell
$env:BLENDER_EXECUTABLE = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
```

### Optional — dev / alternate install paths

| Tool | Required for | Install |
|------|--------------|---------|
| **Git** | Options C, D | `winget install Git.Git` |
| **Python + uv** | Options C, D | `winget install astral-sh.uv` |
| **Node.js** | Option B | `winget install OpenJS.NodeJS` |
| **just** | Option D | `winget install Casey.Just` |

> **Windows:** install CLI tools with [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/).  
> **macOS:** use `brew install git uv node` equivalents.  
> After any winget install, **close and reopen PowerShell** so PATH updates apply.

> **Docker:** not required for normal install. Optional observability: [docs/DOCKER.md](docs/DOCKER.md) and [docs/MONITORING.md](docs/MONITORING.md).

### Optional — LLM (script generation only)

Script generation (`generate_blender_script`, Agent Lab) needs **one** inference path. Models are **never** bundled.

| Path | When | Install |
|------|------|---------|
| **Ollama** (local) | Normal PC | `winget install Ollama.Ollama` then `ollama pull llama3.2` |
| **LM Studio** (local) | GUI model browser | [lmstudio.ai](https://lmstudio.ai/) |
| **Cloud API** | Weak PC / no GPU | Webapp **Settings → LLM → Cloud** |
| **vLLM** (advanced) | Homelab server | Base URL in Settings — [docs/CONFIGURATION.md](docs/CONFIGURATION.md) |

MCP tools work without any LLM (direct mesh/material/scene ops). LLM is only for natural-language **script generation**.

Configure in the webapp dashboard (**Settings → LLM**) or env vars in [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

---

## Terminal health checks (Options C/D)

```powershell
uv run blender-mcp --check-blender
uv run python -c "import blender_mcp; print('OK')"
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Server missing in Claude Desktop | Validate JSON at jsonlint.com; restart Claude Desktop |
| `command not found: uv` | `winget install astral-sh.uv`; reopen terminal |
| `uvx mcpb` fails | Expected — use Quick Start or `npx @anthropic-ai/mcpb` |
| Blender not found | Set `BLENDER_EXECUTABLE` — [CONFIGURATION.md](docs/CONFIGURATION.md) |
| Script generation fails | Install Ollama **or** set cloud API in Settings → LLM → Cloud |
| No local models listed | Start Ollama/LM Studio, or switch to Cloud provider in Settings |
| Port 10848/10849 in use | Re-run `.\start.ps1` or stop the conflicting process |
| `just` not found | Dev-only — `winget install Casey.Just` or use Quick Start |
| Cannot find bridge addon | [Download from release](https://github.com/sandraschi/blender-mcp/releases/latest/download/blender_bridge_addon.py) |

Full diagnostics: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

*Feature overview: [README.md](README.md)*
