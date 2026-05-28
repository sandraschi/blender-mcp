# Installing blender-mcp

Control Blender from Claude Desktop (or Cursor) via MCP. Most users need only Option A.

## Prerequisites

| Tool | Required for | Install |
|------|--------------|---------|
| **Claude Desktop** | All options | [claude.ai/download](https://claude.ai/download) |
| **Blender 3.0+** | Running 3D operations | [blender.org/download](https://www.blender.org/download/) |
| **Git** | Options C, D only | `winget install Git.Git` |
| **Python + uv** | Options C, D only | `winget install astral-sh.uv` |
| **Node.js** | Option B only | `winget install OpenJS.NodeJS` |

> **Windows:** install CLI tools with [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/).  
> **macOS:** use `brew install git uv node` equivalents.  
> After any winget install, **close and reopen PowerShell** so PATH updates apply.

Set Blender path if auto-detection fails (see [docs/CONFIGURATION.md](docs/CONFIGURATION.md)):

```powershell
$env:BLENDER_EXECUTABLE = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
```

---

## Option A — Drag and Drop (Recommended)

1. Open [Releases](https://github.com/sandraschi/blender-mcp/releases/latest)
2. Download `blender-mcp-*.mcpb`
3. Open Claude Desktop
4. Drag the `.mcpb` file onto the Claude Desktop window  
   Or: **Settings → MCP Servers → Install from file**

Restart Claude Desktop if prompted.

**Pass criteria:** server appears in the MCP list with no terminal steps.

---

## Option B — mcpb CLI

Requires Node.js (see Prerequisites). `mcpb` is **not** on PyPI — `uvx mcpb` will fail.

```powershell
winget install OpenJS.NodeJS --accept-source-agreements --accept-package-agreements
# Close and reopen terminal, then:
npx @anthropic-ai/mcpb install https://github.com/sandraschi/blender-mcp
```

Restart Claude Desktop after install completes.

---

## Option C — Manual Configuration

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

---

## Option D — Developer Mode

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

## Webapp Dashboard (optional)

React dashboard on **http://localhost:10848** (API on **10849**):

```powershell
.\start.ps1
```

Flags: `-Headless`, `-BackendOnly`, `-NoBrowser`. Requires Option D setup (`uv sync`, webapp deps via `just`).

---

## Live Blender GUI (session bridge)

Watch the agent build in Blender instead of headless subprocess mode:

1. Start HTTP MCP: `.\start.ps1` or `uv run blender-mcp --http --port 10849`
2. MCP tool `blender_session` → `start` (opens Blender GUI)
3. In Blender: install **docs/blender_bridge_addon.py** → enable → **Start Bridge**
4. Use `blender_render` → `screenshot_viewport` for vision feedback

Without the bridge, tools fall back to headless Blender execution.

---

## Other MCP Clients (Cursor, VS Code)

Same invocation as Option C — stdio via `uv run blender-mcp --stdio` or
`python -m blender_mcp.cli --stdio`.

---

## Verify Installation

In Claude Desktop, try:

> Create a red cube in Blender and tell me what you built.

You should see MCP tool calls (`blender_mesh`, `blender_materials`, etc.) and a scene update.
If Blender is missing, set `BLENDER_EXECUTABLE` and retry.

Health checks from a terminal (Option C/D):

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
| `uvx mcpb` fails | Expected — use Option A or `npx @anthropic-ai/mcpb` |
| Blender not found | Set `BLENDER_EXECUTABLE` — [CONFIGURATION.md](docs/CONFIGURATION.md) |
| Port 10848/10849 in use | Re-run `.\start.ps1` or stop the conflicting process |
| `just` not found | Dev-only — `winget install Casey.Just` or use Option A |

Full diagnostics: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

*Feature overview: [README.md](README.md)*
