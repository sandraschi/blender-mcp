# Docker Deployment

Optional containerized deployment for headless MCP + metrics. Live GUI sculpting still requires a local Blender session with the bridge addon.

## Quick start

```powershell
docker compose up blender-mcp --build
```

HTTP MCP: `http://localhost:10849/mcp`  
Metrics: `http://localhost:9091/metrics`

## With monitoring profile

```powershell
docker compose --profile monitoring up -d --build
```

See [MONITORING.md](MONITORING.md) for Grafana/Prometheus/Loki URLs.

## GHCR (GitHub Container Registry)

Images are built and pushed by CI on `main`:

| Tag | Description |
|-----|-------------|
| `ghcr.io/sandraschi/blender-mcp:latest` | Latest main build |
| `ghcr.io/sandraschi/blender-mcp:<semver>` | Release version |

```powershell
docker pull ghcr.io/sandraschi/blender-mcp:latest
docker run --rm -p 10849:10849 -p 9091:9091 `
  -e BLENDER_MCP_LOG_FORMAT=json `
  ghcr.io/sandraschi/blender-mcp:latest
```

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MCP_TRANSPORT` | `http` | Transport mode in container |
| `MCP_PORT` | `10849` | HTTP MCP port |
| `PROMETHEUS_PORT` | `9091` | Metrics scrape port |
| `BLENDER_MCP_METRICS_ENABLED` | `true` | Enable Prometheus metrics |
| `BLENDER_MCP_LOG_FORMAT` | `json` | JSON logs for Loki |
| `BLENDER_EXECUTABLE` | `/opt/blender/blender` | Headless Blender path |

## Limitations

- Container includes Linux Blender 4.2 for **headless** bpy execution.
- **Sculpt live preview** and viewport screenshots need host Blender + bridge addon.
- Windows host: use Docker Desktop; bind mounts for logs use named volume `blender-mcp-logs`.

## Build locally

```powershell
docker build --target production -t ghcr.io/sandraschi/blender-mcp:local .
```
