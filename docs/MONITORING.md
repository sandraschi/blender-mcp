# Monitoring — Blender MCP

Observability for **blender-mcp** follows [mcp-central-docs monitoring standards](https://github.com/sandraschi/mcp-central-docs/tree/main/monitoring).

For fleet-wide Grafana/Loki/Prometheus, prefer the **unified stack** in `mcp-central-docs/monitoring/` rather than running duplicate containers per repo.

## What is instrumented

| Signal | Endpoint / format | Notes |
|--------|-------------------|-------|
| **Metrics** | `http://127.0.0.1:9091/metrics` (standalone) | `PROMETHEUS_PORT` (default 9091) |
| **Metrics** | `http://127.0.0.1:10849/metrics` | Same registry on HTTP MCP app |
| **Health** | `http://127.0.0.1:10849/api/v1/health` | Fleet health probe |
| **Logs** | JSON lines when `BLENDER_MCP_LOG_FORMAT=json` | Loki-friendly via Promtail |

### Prometheus metrics

- `blender_mcp_tool_calls_total{tool,status}`
- `blender_mcp_tool_duration_seconds_bucket{tool,...}`
- `blender_mcp_jobs_active`
- `blender_mcp_session_connected`
- `blender_mcp_info{version,service}`

## Local development

```powershell
uv sync --extra monitoring
$env:BLENDER_MCP_METRICS_ENABLED = "true"
$env:PROMETHEUS_PORT = "9091"
$env:BLENDER_MCP_LOG_FORMAT = "json"
uv run python -m blender_mcp.cli --http --port 10849
```

Verify metrics:

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:9091/metrics -UseBasicParsing
Invoke-WebRequest -Uri http://127.0.0.1:10849/metrics -UseBasicParsing
```

## Optional Docker stack (repo-local)

Includes MCP server + Prometheus + Grafana + Loki + Promtail:

```powershell
docker compose --profile monitoring up -d --build
```

| Service | URL |
|---------|-----|
| MCP HTTP | http://localhost:10849/mcp |
| Grafana | http://localhost:3000 (admin / admin) |
| Prometheus | http://localhost:9090 |
| Loki | http://localhost:3100/ready |

MCP only (no monitoring profile):

```powershell
docker compose up blender-mcp --build
```

## GHCR images

Published on `main` via `.github/workflows/ci-cd.yml`:

```
ghcr.io/sandraschi/blender-mcp:latest
ghcr.io/sandraschi/blender-mcp:<version>
```

Pull and run:

```powershell
docker pull ghcr.io/sandraschi/blender-mcp:latest
docker run --rm -p 10849:10849 -p 9091:9091 ghcr.io/sandraschi/blender-mcp:latest
```

## Connect to unified fleet monitoring

Add to `mcp-central-docs/monitoring/prometheus/prometheus.yml`:

```yaml
- job_name: 'blender-mcp'
  metrics_path: /metrics
  static_configs:
    - targets: ['host.docker.internal:9091']
```

Filter logs in Grafana: `{job="blender-mcp"}`

See also: [docs/DOCKER.md](DOCKER.md)
