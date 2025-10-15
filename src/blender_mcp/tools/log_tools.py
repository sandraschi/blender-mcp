"""
Log viewing tools for Blender MCP.

Provides tools to view and filter recent logs for debugging purposes.
"""

from typing import Optional
from loguru import logger
from ..app import app
from ..utils.error_handling import MCPError


@app.tool
async def blender_view_logs(
    level_filter: Optional[str] = None,
    module_filter: Optional[str] = None,
    limit: int = 20,
    since_minutes: Optional[int] = None,
    include_details: bool = False,
) -> str:
    """
    View recent Blender MCP logs with filtering options.

    This tool allows you to inspect recent log entries to help debug issues.
    Logs are kept in memory and include the last 1000 entries.

    Args:
        level_filter: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        module_filter: Filter by module name (partial match, case-insensitive)
        limit: Maximum number of log entries to return (1-100, default: 20)
        since_minutes: Show logs from the last N minutes (optional)
        include_details: Include function name and line number in output

    Returns:
        Formatted string with recent log entries

    Examples:
        - blender_view_logs() - Show last 20 logs
        - blender_view_logs(level_filter="ERROR") - Show only errors
        - blender_view_logs(module_filter="mesh") - Show mesh-related logs
        - blender_view_logs(limit=50, since_minutes=5) - Show last 5 minutes
        - blender_view_logs(include_details=True) - Include file details
    """
    from ..server import get_recent_logs

    logger.info(
        f"Viewing logs - level: {level_filter}, module: {module_filter}, limit: {limit}, since: {since_minutes}min"
    )

    try:
        # Validate inputs
        if limit < 1 or limit > 100:
            raise MCPError(f"limit must be between 1 and 100, got {limit}")

        if since_minutes is not None and since_minutes < 0:
            raise MCPError(f"since_minutes must be positive, got {since_minutes}")

        if level_filter and level_filter.upper() not in [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]:
            raise MCPError(
                f"level_filter must be DEBUG, INFO, WARNING, ERROR, or CRITICAL, got '{level_filter}'"
            )

        # Get filtered logs
        logs = get_recent_logs(
            level_filter=level_filter,
            module_filter=module_filter,
            limit=limit,
            since_minutes=since_minutes,
        )

        if not logs:
            criteria = []
            if level_filter:
                criteria.append(f"level={level_filter}")
            if module_filter:
                criteria.append(f"module={module_filter}")
            if since_minutes:
                criteria.append(f"since={since_minutes}min")

            filter_desc = f" ({', '.join(criteria)})" if criteria else ""
            return f"No logs found{filter_desc}. Try adjusting your filters or check if the server has been running long enough."

        # Format logs
        result_lines = []
        result_lines.append(f"Recent Logs ({len(logs)} entries)")
        result_lines.append("=" * 60)

        for log in logs:
            timestamp = log["timestamp"].strftime("%H:%M:%S")

            if include_details:
                location = f"{log['name']}:{log['function']}:{log['line']}"
                line = f"{timestamp} | {log['level']:<8} | {location} | {log['message']}"
            else:
                line = f"{timestamp} | {log['level']:<8} | {log['message']}"

            result_lines.append(line)

        # Add summary info
        total_logs = len(logs)
        levels = {}
        for log in logs:
            levels[log["level"]] = levels.get(log["level"], 0) + 1

        result_lines.append("")
        result_lines.append(f"Summary: {total_logs} logs shown")
        if levels:
            level_summary = ", ".join([f"{level}: {count}" for level, count in levels.items()])
            result_lines.append(f"Levels: {level_summary}")

        return "\n".join(result_lines)

    except Exception as e:
        logger.error(f"Error viewing logs: {str(e)}")
        return f"Error retrieving logs: {str(e)}"


@app.tool
async def blender_log_stats() -> str:
    """
    Get statistics about current log buffer.

    Shows information about the log buffer including total entries,
    time range, and level distribution.

    Returns:
        Statistics about the log buffer

    Examples:
        - blender_log_stats() - Show log buffer statistics
    """
    from ..server import _memory_logs

    logger.info("Getting log statistics")

    try:
        if not _memory_logs:
            return "No logs in memory buffer. The server may have just started."

        total_logs = len(_memory_logs)
        oldest = _memory_logs[0]["timestamp"]
        newest = _memory_logs[-1]["timestamp"]
        time_span = newest - oldest

        # Count by level
        levels = {}
        modules = {}

        for log in _memory_logs:
            levels[log["level"]] = levels.get(log["level"], 0) + 1
            modules[log["name"]] = modules.get(log["name"], 0) + 1

        # Format results
        result_lines = []
        result_lines.append("Log Buffer Statistics")
        result_lines.append("=" * 40)
        result_lines.append(f"Total entries: {total_logs}")
        result_lines.append(f"Time span: {time_span}")
        result_lines.append(f"Oldest: {oldest.strftime('%H:%M:%S')}")
        result_lines.append(f"Newest: {newest.strftime('%H:%M:%S')}")

        result_lines.append("")
        result_lines.append("Log Levels:")
        for level, count in sorted(levels.items()):
            result_lines.append(f"  {level}: {count}")

        result_lines.append("")
        result_lines.append("Top Modules:")
        for module, count in sorted(modules.items(), key=lambda x: x[1], reverse=True)[:5]:
            result_lines.append(f"  {module}: {count}")

        return "\n".join(result_lines)

    except Exception as e:
        logger.error(f"Error getting log stats: {str(e)}")
        return f"Error retrieving log statistics: {str(e)}"
