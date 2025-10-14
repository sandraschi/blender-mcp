# 📊 Log Tools Documentation

Access and analyze Blender MCP server logs with powerful filtering and search capabilities.

## Overview

Blender MCP provides comprehensive logging tools to help debug issues, monitor performance, and understand system behavior. All logs are captured in memory and can be accessed programmatically.

## Available Log Tools

### `blender_view_logs`
View recent Blender MCP logs with advanced filtering options.

#### Parameters
- `level_filter` (Optional[str]): Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `module_filter` (Optional[str]): Filter by module name (partial match, case-insensitive)
- `limit` (int): Maximum entries to return (1-100, default: 20)
- `since_minutes` (Optional[int]): Show logs from last N minutes
- `include_details` (bool): Include function name and line number (default: false)

#### Examples
```python
# View last 20 logs
blender_view_logs()

# Show only errors from last hour
blender_view_logs(level_filter="ERROR", since_minutes=60)

# Find mesh-related logs
blender_view_logs(module_filter="mesh", limit=50)

# Debug with full details
blender_view_logs(include_details=True, level_filter="DEBUG")
```

### `blender_log_stats`
Get comprehensive statistics about the in-memory log buffer.

#### Returns
- Total log entries
- Time range covered
- Distribution by log level
- Memory buffer capacity

#### Example
```python
blender_log_stats()
# Output: Blender MCP Log Statistics (Max Capacity: 1000 entries)
# Total Log Entries: 456
# Oldest Log: 2025-10-14 14:30:15
# Newest Log: 2025-10-14 16:45:22
# Time Range Covered: 2:15:07
# Log Level Distribution:
#   INFO: 234
#   DEBUG: 145
#   WARNING: 67
#   ERROR: 10
```

## Log Levels

### DEBUG
Detailed diagnostic information for development and troubleshooting.
```
- Parameter values and conversions
- Function entry/exit points
- Intermediate calculation results
- Low-level system information
```

### INFO
General information about normal operations.
```
- Tool execution start/completion
- Asset download progress
- Scene operations summary
- Configuration loading
```

### WARNING
Potentially harmful situations that don't prevent operation.
```
- Deprecated feature usage
- Performance warnings
- Resource limitations
- Recovery actions taken
```

### ERROR
Error conditions that may affect single operations.
```
- Tool execution failures
- File access problems
- Network timeouts
- Validation errors
```

### CRITICAL
Severe error conditions that may affect system stability.
```
- Blender subprocess crashes
- Memory exhaustion
- Configuration corruption
- System resource failures
```

## Log Format

Each log entry contains:
```
TIMESTAMP | LEVEL | MODULE:FUNCTION:LINE - MESSAGE
```

### Example Log Entries
```
2025-10-14 14:30:15.123 | INFO | blender_mcp.tools.mesh.mesh_tools:45 - blender_mesh called with operation='create_cube', name='TestCube'
2025-10-14 14:30:15.245 | DEBUG | blender_mcp.handlers.mesh_handler:78 - Creating cube 'TestCube' at (0, 0, 0) with scale (1, 1, 1)
2025-10-14 14:30:15.456 | INFO | blender_mcp.handlers.mesh_handler:89 - Successfully created cube 'TestCube'
2025-10-14 14:30:16.789 | WARNING | blender_mcp.utils.blender_executor:234 - Blend file not found, using factory startup
```

## Memory Buffer

### Buffer Capacity
- **Maximum entries**: 1000 (configurable)
- **Circular buffer**: Oldest entries automatically removed
- **Persistent**: Survives server restarts
- **Thread-safe**: Safe for concurrent access

### Buffer Management
```python
# Check current buffer status
stats = blender_log_stats()

# Clear buffer (if needed for testing)
# Note: Buffer clears automatically on server restart
```

## Filtering Techniques

### Level-Based Filtering
```python
# Show only errors and warnings
blender_view_logs(level_filter="ERROR")
blender_view_logs(level_filter="WARNING")

# Show all issues
blender_view_logs(level_filter="WARNING")  # Includes ERROR
```

### Module-Based Filtering
```python
# Blender operation logs
blender_view_logs(module_filter="blender_mcp.handlers")

# Tool execution logs
blender_view_logs(module_filter="blender_mcp.tools")

# Specific tool logs
blender_view_logs(module_filter="mesh_handler")
```

### Time-Based Filtering
```python
# Last 5 minutes
blender_view_logs(since_minutes=5)

# Last hour
blender_view_logs(since_minutes=60)

# Last 24 hours
blender_view_logs(since_minutes=1440)
```

### Combined Filtering
```python
# Recent errors in mesh operations
blender_view_logs(
    level_filter="ERROR",
    module_filter="mesh",
    since_minutes=30
)

# Debug information with details
blender_view_logs(
    level_filter="DEBUG",
    include_details=True,
    limit=100
)
```

## Common Debugging Scenarios

### Operation Failures
```python
# Find what went wrong
blender_view_logs(level_filter="ERROR", since_minutes=10)

# See the full context
blender_view_logs(module_filter="mesh", since_minutes=5, include_details=True)
```

### Performance Issues
```python
# Check for warnings
blender_view_logs(level_filter="WARNING", since_minutes=60)

# Monitor operation timing
blender_view_logs(module_filter="executor", since_minutes=30)
```

### Asset Download Problems
```python
# Download-related logs
blender_view_logs(module_filter="download", since_minutes=15)

# Network issues
blender_view_logs(module_filter="requests", level_filter="ERROR")
```

### Configuration Issues
```python
# Startup logs
blender_view_logs(module_filter="server", since_minutes=1)

# Configuration loading
blender_view_logs(module_filter="config", level_filter="WARNING")
```

## Log Analysis Tips

### Pattern Recognition
- Look for repeated error messages
- Check timing patterns for performance issues
- Identify modules with high error rates

### Context Building
- Use `include_details=True` for function traces
- Combine time and module filters
- Check logs before and after failures

### Proactive Monitoring
- Regular stats checks: `blender_log_stats()`
- Monitor error rates over time
- Set up alerts for critical errors

## Log Storage and Persistence

### In-Memory Only
- Logs exist only during server runtime
- Lost on server restart
- Not persisted to disk by default

### External Logging
For persistent logging, configure external log file:
```bash
export LOG_FILE="/path/to/blender_mcp.log"
```

### Log Rotation
External logs can be rotated using system tools:
```bash
# Linux/macOS
logrotate /etc/logrotate.d/blender_mcp

# Windows (scheduled task)
# Use log rotation utilities
```

## Performance Considerations

### Memory Usage
- Each log entry: ~200-500 bytes
- 1000 entries: ~200KB maximum
- Minimal performance impact

### Search Performance
- In-memory filtering: Instantaneous
- Time-based filtering: Fast (indexed)
- Text search: Linear scan (acceptable for <1000 entries)

### Recommendations
- Use specific filters to reduce output
- Limit results with `limit` parameter
- Use time filters for recent issues
- Combine filters strategically

## Integration with Claude

### Automatic Log Analysis
When you report issues to Claude, it can automatically:
```python
# Claude can suggest this when you mention problems
blender_view_logs(level_filter="ERROR", since_minutes=30)

# Or analyze specific operations
blender_view_logs(module_filter="mesh", since_minutes=10)
```

### Log-Based Debugging
Claude can help interpret logs:
```
"I got an error when creating a sphere"
→ Claude: Let me check the logs...
→ blender_view_logs(module_filter="mesh", since_minutes=5)
→ Analysis of the error and suggested fix
```

## Troubleshooting Log Tools

### No Logs Available
```python
# Check server is running
blender_status()

# Check log level configuration
# LOG_LEVEL should be INFO or DEBUG
```

### Empty Results
```python
# Try broader filters
blender_view_logs()  # No filters

# Check time range
blender_view_logs(since_minutes=120)  # Longer time
```

### Performance Issues
```python
# Use smaller limits
blender_view_logs(limit=10)

# Use more specific filters
blender_view_logs(module_filter="specific_module")
```

---

**Effective logging is key to successful debugging and monitoring!** 🔍📊

*For more advanced log analysis, check the [development logging guide](../development/LOGURU_LOGGING_GUIDE.md).* 🚀
