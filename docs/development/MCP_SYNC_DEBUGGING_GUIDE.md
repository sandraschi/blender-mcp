# MCP File Sync Debugging Guide

**Created:** 2025-10-10  
**Context:** Advanced-memory-mcp sync stuck at 242/1896 files - watchdog failed silently

---

## The Problem

MCP servers with file watching (like advanced-memory-mcp, basic-memory-mcp) can fail silently:
- ✅ Server starts successfully
- ✅ Tools register properly
- ❌ File watcher never starts
- ❌ Database doesn't grow
- ❌ **NO ERROR MESSAGES**

---

## Root Cause Analysis

### What Happened

1. **Fresh database created** (152 KB)
2. **Server loaded** and tools registered
3. **Watchdog initialized** but never started scanning
4. **No logging** to indicate failure
5. User waited 10+ minutes for "sync" that never happened

### Why It Failed Silently

```python
# BAD: Silent failure
def start_file_watcher(self):
    try:
        self.watcher = FileWatcher(self.project_path)
        # If watcher.start() fails, no one knows!
    except Exception:
        pass  # ❌ Swallowed exception
```

---

## Solution: Robust Error Handling

### 1. **Structured Logging**

```python
import logging
import structlog

logger = structlog.get_logger(__name__)

class FileSyncManager:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.watcher = None
        self.sync_state = "INITIALIZING"
        self.files_scanned = 0
        self.files_total = 0
        self.errors = []
        
        logger.info("file_sync_initialized", 
                   project_path=project_path,
                   state=self.sync_state)
    
    def start_sync(self):
        """Start file synchronization with detailed logging."""
        try:
            logger.info("sync_starting", path=self.project_path)
            
            # Count files first
            self.files_total = self._count_files()
            logger.info("file_count_complete", 
                       total=self.files_total,
                       path=self.project_path)
            
            # Start watcher
            self.watcher = FileWatcher(self.project_path)
            self.watcher.start()
            
            self.sync_state = "SCANNING"
            logger.info("sync_started", 
                       state=self.sync_state,
                       total_files=self.files_total)
            
            return True
            
        except PermissionError as e:
            self.sync_state = "ERROR_PERMISSION"
            logger.error("sync_permission_denied",
                        path=self.project_path,
                        error=str(e))
            self.errors.append(f"Permission denied: {e}")
            return False
            
        except FileNotFoundError as e:
            self.sync_state = "ERROR_NOT_FOUND"
            logger.error("sync_path_not_found",
                        path=self.project_path,
                        error=str(e))
            self.errors.append(f"Path not found: {e}")
            return False
            
        except Exception as e:
            self.sync_state = "ERROR_UNKNOWN"
            logger.error("sync_failed",
                        error=str(e),
                        error_type=type(e).__name__,
                        traceback=traceback.format_exc())
            self.errors.append(f"Sync failed: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get detailed sync status for debugging."""
        return {
            "state": self.sync_state,
            "files_scanned": self.files_scanned,
            "files_total": self.files_total,
            "progress_percent": (self.files_scanned / self.files_total * 100) 
                               if self.files_total > 0 else 0,
            "errors": self.errors,
            "watcher_alive": self.watcher.is_alive() if self.watcher else False,
        }
```

### 2. **Health Check Tool**

```python
@mcp_server.tool()
async def sync_health_check() -> str:
    """
    Comprehensive sync health check with diagnostics.
    
    Returns detailed status including:
    - Watcher process state
    - Database growth rate
    - Scan progress
    - Error logs
    - Performance metrics
    """
    status = sync_manager.get_status()
    
    # Check if stuck
    if status["state"] == "SCANNING" and status["files_scanned"] == 0:
        logger.warning("sync_appears_stuck",
                      state=status["state"],
                      duration=sync_manager.get_runtime())
    
    # Format output
    output = f"""
# Sync Health Check

**State:** {status['state']}
**Progress:** {status['files_scanned']} / {status['files_total']} ({status['progress_percent']:.1f}%)
**Watcher:** {'ALIVE' if status['watcher_alive'] else 'DEAD ❌'}

## Errors
{chr(10).join(status['errors']) if status['errors'] else 'None'}

## Diagnostics
- Database size: {get_db_size()} KB
- Growth rate: {calculate_growth_rate()} KB/sec
- Memory usage: {get_memory_usage()} MB
- CPU usage: {get_cpu_usage()}%

## Recommendations
{generate_recommendations(status)}
"""
    
    return output

def generate_recommendations(status: dict) -> str:
    """Generate actionable recommendations based on status."""
    recs = []
    
    if not status["watcher_alive"]:
        recs.append("⚠️  Watcher is dead - restart server required")
    
    if status["state"] == "ERROR_PERMISSION":
        recs.append("🔒 Permission error - check folder permissions")
    
    if status["files_scanned"] == 0 and status["state"] == "SCANNING":
        recs.append("🐛 Scan appears stuck - check logs for errors")
    
    if status["progress_percent"] < 50 and get_runtime() > 300:
        recs.append("⏱️  Slow scan - consider reducing file count or checking disk I/O")
    
    return "\n".join(recs) if recs else "✅ All systems healthy"
```

### 3. **Progress Monitoring**

```python
class ProgressMonitor:
    """Monitor sync progress and detect stalls."""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.last_progress = 0
        self.stall_count = 0
        self.max_stalls = 3
        
    async def monitor(self):
        """Background monitoring task."""
        while True:
            await asyncio.sleep(self.check_interval)
            
            current_progress = sync_manager.files_scanned
            
            if current_progress == self.last_progress:
                self.stall_count += 1
                logger.warning("sync_stalled",
                              progress=current_progress,
                              stall_count=self.stall_count)
                
                if self.stall_count >= self.max_stalls:
                    logger.error("sync_stuck",
                                progress=current_progress,
                                duration=self.stall_count * self.check_interval)
                    # Attempt recovery
                    await self.attempt_recovery()
            else:
                self.stall_count = 0  # Reset on progress
                logger.debug("sync_progress",
                            scanned=current_progress,
                            remaining=sync_manager.files_total - current_progress)
            
            self.last_progress = current_progress
    
    async def attempt_recovery(self):
        """Try to recover from stuck sync."""
        logger.info("attempting_sync_recovery")
        
        # Kill stuck watcher
        if sync_manager.watcher:
            sync_manager.watcher.stop()
        
        # Restart sync
        await sync_manager.start_sync()
```

---

## Testing Strategy

### 1. **Unit Tests for Sync Manager**

```python
# tests/test_file_sync.py
import pytest
import tempfile
from pathlib import Path
from file_sync import FileSyncManager

@pytest.fixture
def temp_project():
    """Create temporary project with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create test files
        for i in range(100):
            (project_path / f"test_{i}.md").write_text(f"# Test {i}")
        
        yield project_path

def test_sync_counts_files_correctly(temp_project):
    """Test that file counting works."""
    sync = FileSyncManager(str(temp_project))
    sync.start_sync()
    
    assert sync.files_total == 100
    assert sync.sync_state == "SCANNING"

def test_sync_handles_missing_directory():
    """Test handling of non-existent directory."""
    sync = FileSyncManager("/nonexistent/path")
    result = sync.start_sync()
    
    assert result is False
    assert sync.sync_state == "ERROR_NOT_FOUND"
    assert len(sync.errors) > 0

def test_sync_handles_permission_error(temp_project):
    """Test handling of permission errors."""
    # Make directory read-only
    temp_project.chmod(0o444)
    
    sync = FileSyncManager(str(temp_project))
    result = sync.start_sync()
    
    assert result is False
    assert "Permission" in sync.errors[0]

@pytest.mark.timeout(60)
def test_sync_completes_in_reasonable_time(temp_project):
    """Test that sync doesn't hang."""
    sync = FileSyncManager(str(temp_project))
    sync.start_sync()
    
    # Wait for completion
    import time
    start = time.time()
    while sync.sync_state == "SCANNING" and time.time() - start < 30:
        time.sleep(0.5)
    
    assert sync.sync_state == "COMPLETED"
    assert sync.files_scanned == sync.files_total

def test_watcher_stays_alive(temp_project):
    """Test that watcher doesn't die silently."""
    sync = FileSyncManager(str(temp_project))
    sync.start_sync()
    
    import time
    time.sleep(5)
    
    status = sync.get_status()
    assert status["watcher_alive"] is True
```

### 2. **Integration Tests**

```python
# tests/test_mcp_sync.py
import pytest
from mcp.client import ClientSession
from mcp import StdioServerParameters

@pytest.mark.asyncio
async def test_sync_status_reports_progress():
    """Test that sync_status tool works and reports progress."""
    server = StdioServerParameters(
        command="python",
        args=["-m", "advanced_memory.mcp.server"]
    )
    
    async with ClientSession(server) as client:
        # Call sync_status
        result = await client.call_tool("sync_status")
        
        assert "files_scanned" in result
        assert "files_total" in result
        assert "state" in result

@pytest.mark.asyncio
async def test_sync_health_check_detects_stuck_sync():
    """Test that health check detects stuck syncs."""
    # This would require mocking a stuck watcher
    # Implementation depends on your architecture
    pass
```

### 3. **Performance Tests**

```python
# tests/test_sync_performance.py
import pytest
import time
from file_sync import FileSyncManager

@pytest.mark.performance
def test_sync_speed_baseline(benchmark, temp_project_1000_files):
    """Benchmark sync speed for 1000 files."""
    def run_sync():
        sync = FileSyncManager(str(temp_project_1000_files))
        sync.start_sync()
        while sync.sync_state == "SCANNING":
            time.sleep(0.1)
        return sync
    
    result = benchmark(run_sync)
    assert result.files_scanned == 1000

@pytest.mark.performance
def test_database_growth_rate(temp_project):
    """Test that database grows at reasonable rate."""
    sync = FileSyncManager(str(temp_project))
    initial_size = get_db_size()
    
    sync.start_sync()
    time.sleep(10)
    
    final_size = get_db_size()
    growth_rate = (final_size - initial_size) / 10  # KB/sec
    
    assert growth_rate > 0, "Database should grow during sync"
    assert growth_rate < 1000, "Growth rate seems suspiciously high"
```

---

## Monitoring in Production

### 1. **Structured Logs**

Use structured logging (structlog) for parseable output:

```json
{
  "event": "sync_progress",
  "timestamp": "2025-10-10T08:52:03Z",
  "files_scanned": 150,
  "files_total": 1896,
  "progress_percent": 7.9,
  "elapsed_seconds": 45,
  "estimated_remaining_seconds": 525
}
```

### 2. **Metrics Export**

Export metrics for monitoring tools:

```python
from prometheus_client import Counter, Gauge, Histogram

files_scanned = Counter('mcp_files_scanned_total', 'Total files scanned')
files_total = Gauge('mcp_files_total', 'Total files to scan')
scan_duration = Histogram('mcp_scan_duration_seconds', 'Time to scan files')
sync_errors = Counter('mcp_sync_errors_total', 'Sync errors', ['error_type'])
```

### 3. **Health Endpoint**

```python
@mcp_server.resource("health://sync")
async def sync_health():
    """Health check endpoint for monitoring."""
    status = sync_manager.get_status()
    
    return {
        "healthy": status["state"] not in ["ERROR_UNKNOWN", "ERROR_PERMISSION"],
        "state": status["state"],
        "progress": f"{status['files_scanned']}/{status['files_total']}",
        "errors": status["errors"]
    }
```

---

## Debugging Checklist

When sync appears stuck:

1. ✅ **Check logs** for errors
2. ✅ **Verify watcher is alive** (`sync_health_check()`)
3. ✅ **Monitor database growth** (should grow steadily)
4. ✅ **Check file permissions** on project directory
5. ✅ **Verify file count** matches expectation
6. ✅ **Look for resource exhaustion** (CPU, memory, disk I/O)
7. ✅ **Check for file lock conflicts** (antivirus, backup software)
8. ✅ **Review recent changes** to codebase

---

## Prevention

### Code Review Checklist

- [ ] All exceptions are logged with context
- [ ] Background tasks have monitoring
- [ ] Progress is reported regularly
- [ ] Stalled operations have timeouts
- [ ] Health checks exist for critical paths
- [ ] Tests cover failure scenarios
- [ ] Performance tests catch regressions

### CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Run sync tests
  run: |
    pytest tests/test_file_sync.py -v
    pytest tests/test_sync_performance.py --benchmark-only

- name: Check for silent failures
  run: |
    # Run server and check logs
    python -m server &
    sleep 10
    grep -q "ERROR" logs/ && exit 1 || exit 0
```

---

## Lessons Learned

1. **Silent failures are deadly** - Always log, even success
2. **Progress monitoring is essential** - Users need feedback
3. **Health checks catch bugs** - Test tools should exist
4. **Timeouts prevent hangs** - All long operations need limits
5. **Metrics enable debugging** - Instrument everything

---

## Related Issues

- Advanced-memory-mcp sync stuck (2025-10-10)
- Similar issue in basic-memory-mcp (resolved with better logging)
- Watchdog library issues on Windows (known bug)

---

## References

- [MCP Best Practices](https://modelcontextprotocol.io/docs/best-practices)
- [Structlog Documentation](https://www.structlog.org/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)

