# Configuration

Environment variables and Claude Desktop config for blender-mcp.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BLENDER_EXECUTABLE` | Auto-detected common paths | Path to `blender.exe` or `blender` binary |
| `BLENDER_PATH` | — | Legacy alias checked by CLI status |
| `BLENDER_ADDONS_PATH` | User addons folder | Override Blender addons directory |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama API (script generation, model list) |
| `OPENAI_API_BASE` | — | Cloud or vLLM OpenAI-compatible endpoint (Tier B weak-PC path) |
| `OPENAI_API_KEY` | — | API key for cloud / vLLM when required |
| `MCP_TRANSPORT` | `stdio` | `stdio`, `http`, or `sse` |
| `MCP_HOST` | `127.0.0.1` | HTTP/SSE bind address |
| `MCP_PORT` | `10849` | HTTP MCP port (fleet range 10700+) |
| `MCP_PATH` | `/mcp` | HTTP endpoint path |
| `BLENDER_MCP_LOG_LEVEL` | `INFO` | Python log level |
| `BLENDER_MCP_LOG_FORMAT` | text | Set to `json` for Loki-friendly logs |
| `BLENDER_MCP_METRICS_ENABLED` | `true` | Prometheus metrics on HTTP mode |
| `PROMETHEUS_PORT` | `9091` | Metrics scrape port when enabled |
| `SKETCHFAB_API_TOKEN` | — | Sketchfab mesh download (optional) |
| `PYTHONUNBUFFERED` | — | Set to `1` in Claude Desktop config |

AI mesh backends (optional): see `src/blender_mcp/utils/ai_mesh_backends.py` for
provider-specific keys (`RODIN_*`, `TRIPO_*`, etc.).

## Setting Variables in Claude Desktop

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
        "PYTHONUNBUFFERED": "1",
        "BLENDER_EXECUTABLE": "C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe"
      }
    }
  }
}
```

Config file locations:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

## Shell Examples

**Windows (PowerShell):**

```powershell
$env:BLENDER_EXECUTABLE = "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
$env:BLENDER_MCP_LOG_FORMAT = "json"
```

**Linux / macOS:**

```bash
export BLENDER_EXECUTABLE=/usr/bin/blender
export BLENDER_MCP_LOG_FORMAT=json
```

## Docker

**Not required** for Claude Desktop or Tauri install. Optional for developers and homelab observability (Prometheus/Grafana/Loki).

Container defaults and overrides: [DOCKER.md](DOCKER.md). Fleet rule: [mcp-central-docs — LLM and Install Tiers](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/LLM_AND_INSTALL_TIERS.md).

## LLM settings (webapp)

The dashboard persists provider choice under **Settings → LLM**:

| Provider | Fields |
|----------|--------|
| Ollama | `ollama_url` (default `http://localhost:11434`), selected model |
| LM Studio | `lmstudio_url` (default `http://localhost:1234`), selected model |
| Cloud | `openai_api_key`, `openai_model`, optional custom base URL via env |

Cloud examples: DeepSeek API, OpenRouter, or an OpenCode `serve` gateway pointing at a cheap model.

## Related Docs

- [INSTALL.md](../INSTALL.md) — install paths
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Blender path and port issues
- [MONITORING.md](MONITORING.md) — Prometheus / Grafana / Loki
