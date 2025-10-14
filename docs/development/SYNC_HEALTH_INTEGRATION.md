# Sync Health Monitoring - Integration Guide

**How to integrate robust sync monitoring into any MCP server**

---

## Quick Start

### 1. Add Health Monitoring to Your Server

```python
# server.py
from fastmcp import FastMCP
from sync_health import SyncHealthMonitor, SyncState

mcp = FastMCP("My MCP Server")

# Initialize health monitor
sync_monitor = SyncHealthMonitor(
    project_path="/path/to/files",
    stall_timeout=60,        # Alert if no progress for 60 seconds
    check_interval=10,       # Check health every 10 seconds
    max_recovery_attempts=3  # Try to recover 3 times
)

@mcp.tool()
async def sync_status() -> str:
    """Get detailed sync status with health diagnostics."""
    return sync_monitor.format_health_report()

@mcp.tool()
async def sync_health_check() -> dict:
    """Machine-readable health check for monitoring."""
    return sync_monitor.get_health_report()
```

### 2. Start Monitoring on Server Init

```python
@mcp.on_startup()
async def initialize():
    """Initialize server and start file sync."""
    # Start file scan
    if not sync_monitor.start_scan():
        logger.error("Failed to start file scan")
        return
    
    # Start background health monitoring
    await sync_monitor.start_monitoring()
    
    logger.info("Server initialized successfully")
```

### 3. Update Progress During Scan

```python
async def scan_files():
    """Scan files and update progress."""
    files = list(Path(sync_monitor.project_path).rglob("*.md"))
    
    for i, file_path in enumerate(files):
        # Process file...
        await process_file(file_path)
        
        # Update progress every file (or every N files)
        if i % 10 == 0:  # Update every 10 files
            sync_monitor.update_scan_progress(i)
        
        # Yield to event loop
        await asyncio.sleep(0)
    
    # Mark complete
    sync_monitor.update_scan_progress(len(files))
```

---

## Advanced Usage

### Custom Health Checks

```python
from sync_health import SyncHealthMonitor

class CustomSyncMonitor(SyncHealthMonitor):
    """Extended monitor with custom checks."""
    
    async def _check_health(self):
        """Override with custom health checks."""
        # Call parent checks
        await super()._check_health()
        
        # Add custom checks
        if self.metrics.bytes_processed > 1_000_000_000:  # 1GB
            self._log("large_scan_warning", level="warning",
                     bytes=self.metrics.bytes_processed)
        
        # Check database size
        db_size = get_database_size()
        if db_size == 0 and self.metrics.files_scanned > 0:
            self._log("database_not_growing", level="error")
            await self._attempt_recovery()
```

### Integration with Prometheus

```python
from prometheus_client import Counter, Gauge, Histogram

# Define metrics
files_scanned_total = Counter(
    'mcp_files_scanned_total',
    'Total files scanned'
)
files_total_gauge = Gauge(
    'mcp_files_total',
    'Total files to scan'
)
scan_duration = Histogram(
    'mcp_scan_duration_seconds',
    'Time to scan files'
)

def update_prometheus_metrics():
    """Update Prometheus metrics from sync monitor."""
    report = sync_monitor.get_health_report()
    
    files_scanned_total.inc(report['metrics']['files_scanned'])
    files_total_gauge.set(report['metrics']['files_total'])
    scan_duration.observe(report['metrics']['runtime_seconds'])
```

### Integration with Health Endpoint

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    """Health check endpoint for load balancers."""
    report = sync_monitor.get_health_report()
    
    return {
        "status": "healthy" if report['healthy'] else "unhealthy",
        "checks": {
            "sync": {
                "status": report['state'],
                "progress": f"{report['metrics']['files_scanned']}/{report['metrics']['files_total']}",
            },
            "watcher": {
                "alive": report['watcher']['alive'],
            },
        }
    }
```

---

## Testing Your Integration

### Unit Tests

```python
# test_my_server_sync.py
import pytest
from my_server import sync_monitor

@pytest.mark.asyncio
async def test_sync_monitor_starts():
    """Test that sync monitor initializes."""
    assert sync_monitor is not None
    assert sync_monitor.state != SyncState.ERROR_UNKNOWN

@pytest.mark.asyncio
async def test_health_check_tool_works():
    """Test that health check tool returns data."""
    from my_server import sync_health_check
    
    result = await sync_health_check()
    
    assert "healthy" in result
    assert "state" in result
    assert "metrics" in result
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_sync_completes_successfully(temp_project):
    """Test end-to-end sync."""
    monitor = SyncHealthMonitor(str(temp_project))
    monitor.start_scan()
    
    # Simulate scan
    await scan_files()
    
    report = monitor.get_health_report()
    assert report['healthy']
    assert report['state'] == 'completed'
    assert report['metrics']['files_scanned'] == report['metrics']['files_total']
```

---

## Monitoring in Production

### Log Analysis

Use structured logs for easy parsing:

```bash
# Find stalled syncs
grep "sync_stalled" logs/mcp-server.log

# Check error rate
grep "error" logs/mcp-server.log | wc -l

# Monitor progress
grep "scan_progress" logs/mcp-server.log | tail -f
```

### Alerting Rules

Example Prometheus alerts:

```yaml
groups:
  - name: mcp_sync
    rules:
      - alert: MCPSyncStalled
        expr: mcp_files_scanned_total == 0 and time() - mcp_scan_start_time > 300
        for: 5m
        annotations:
          summary: "MCP sync appears stalled"
          
      - alert: MCPWatcherDead
        expr: mcp_watcher_alive == 0
        for: 1m
        annotations:
          summary: "MCP file watcher is dead"
```

---

## Troubleshooting

### Sync Won't Start

1. Check logs for errors
2. Verify path exists and is readable
3. Check file permissions
4. Run `sync_health_check()` tool

### Sync Stuck at Zero

1. Check if watcher is alive
2. Look for errors in health report
3. Try manual recovery
4. Restart server if needed

### Slow Sync

1. Check `files_per_second` metric
2. Monitor disk I/O
3. Reduce file count if possible
4. Consider batching

---

## Best Practices

### DO:
- ✅ Log all state transitions
- ✅ Update progress regularly (every 10-100 files)
- ✅ Monitor in background
- ✅ Implement timeouts
- ✅ Test recovery mechanisms
- ✅ Expose health check tools

### DON'T:
- ❌ Swallow exceptions silently
- ❌ Skip progress updates
- ❌ Ignore stalls
- ❌ Forget to test with large datasets
- ❌ Hard-code timeouts

---

## Real-World Example

Complete working example from notepadpp-mcp:

```python
from fastmcp import FastMCP
from sync_health import SyncHealthMonitor
from pathlib import Path
import asyncio

mcp = FastMCP("notepadpp-mcp")

# Global sync monitor
sync_monitor = None

@mcp.on_startup()
async def initialize():
    """Initialize server with health monitoring."""
    global sync_monitor
    
    project_path = Path.cwd()
    sync_monitor = SyncHealthMonitor(
        project_path=str(project_path),
        stall_timeout=60,
        check_interval=10,
    )
    
    # Start scan
    if sync_monitor.start_scan():
        # Start monitoring
        await sync_monitor.start_monitoring()
        
        # Start background scan task
        asyncio.create_task(perform_initial_scan())
    else:
        logger.error("Failed to initialize file sync")

async def perform_initial_scan():
    """Perform initial file scan with progress updates."""
    files = list(Path(sync_monitor.project_path).rglob("*.md"))
    
    for i, file_path in enumerate(files):
        # Process file
        await index_file(file_path)
        
        # Update progress
        sync_monitor.update_scan_progress(i + 1)
        
        # Yield to event loop
        await asyncio.sleep(0)

@mcp.tool()
async def sync_status() -> str:
    """Get detailed sync status."""
    if sync_monitor is None:
        return "Sync monitor not initialized"
    return sync_monitor.format_health_report()

@mcp.tool()
async def force_rescan() -> str:
    """Force a full rescan of files."""
    if sync_monitor is None:
        return "Sync monitor not initialized"
    
    sync_monitor.state = SyncState.INITIALIZING
    if sync_monitor.start_scan():
        asyncio.create_task(perform_initial_scan())
        return "Rescan started"
    return "Rescan failed to start"
```

---

## Next Steps

1. **Integrate into your server** - Copy `sync_health.py` and add to your project
2. **Add health check tools** - Expose `sync_status()` and `sync_health_check()`
3. **Write tests** - Use provided test suite as template
4. **Set up monitoring** - Add to your observability stack
5. **Test thoroughly** - Especially with large file counts

---

## Related Documentation

- [MCP Sync Debugging Guide](./MCP_SYNC_DEBUGGING_GUIDE.md)
- [Test Suite](../../tests/test_sync_health.py)
- [Sync Health Module](../../src/notepadpp_mcp/sync_health.py)

