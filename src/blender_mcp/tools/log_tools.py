"""
Log viewing portmanteau for Blender MCP.

Single tool: view logs or log buffer statistics.
"""

import logging
from typing import Literal, Optional

from ..app import app
from ..compat import *
from ..utils.error_handling import MCPError

logger = logging.getLogger(__name__)


@app.tool
async def blender_logs(
    operation: Literal["view", "stats"] = "view",
    level_filter: Optional[str] = None,
    module_filter: Optional[str] = None,
    limit: int = 20,
    since_minutes: Optional[int] = None,
    include_details: bool = False,
) -> str:
    """
    View recent logs or log buffer statistics (portmanteau).

    Operations:
    - view: Recent log entries with optional filters (level_filter, module_filter, limit, since_minutes, include_details)
    - stats: Log buffer statistics (total entries, time range, level distribution)

    Args:
        operation: One of view, stats
        level_filter: For view - DEBUG, INFO, WARNING, ERROR, CRITICAL
        module_filter: For view - partial module name match
        limit: For view - max entries (1-100)
        since_minutes: For view - logs from last N minutes
        include_details: For view - include function/line in output

    Returns:
        Formatted log view or statistics string
    """
    from ..server import _memory_logs, get_recent_logs

    if operation == "stats":
        logger.info("Getting log statistics")
        try:
            if not _memory_logs:
                return "No logs in memory buffer. The server may have just started."
            total_logs = len(_memory_logs)
            oldest = _memory_logs[0]["timestamp"]
            newest = _memory_logs[-1]["timestamp"]
            time_span = newest - oldest
            levels = {}
            modules = {}
            for log in _memory_logs:
                levels[log["level"]] = levels.get(log["level"], 0) + 1
                modules[log["name"]] = modules.get(log["name"], 0) + 1
            result_lines = [
                "Log Buffer Statistics",
                "=" * 40,
                f"Total entries: {total_logs}",
                f"Time span: {time_span}",
                f"Oldest: {oldest.strftime('%H:%M:%S')}",
                f"Newest: {newest.strftime('%H:%M:%S')}",
                "",
                "Log Levels:",
            ]
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

    # operation == "view"
    logger.info(
        f"Viewing logs - level: {level_filter}, module: {module_filter}, limit: {limit}, since: {since_minutes}min"
    )
    try:
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

        result_lines = [f"Recent Logs ({len(logs)} entries)", "=" * 60]
        for log in logs:
            timestamp = log["timestamp"].strftime("%H:%M:%S")
            if include_details:
                location = f"{log['name']}:{log['function']}:{log['line']}"
                result_lines.append(
                    f"{timestamp} | {log['level']:<8} | {location} | {log['message']}"
                )
            else:
                result_lines.append(f"{timestamp} | {log['level']:<8} | {log['message']}")

        total_logs = len(logs)
        levels = {}
        for log in logs:
            levels[log["level"]] = levels.get(log["level"], 0) + 1
        result_lines.append("")
        result_lines.append(f"Summary: {total_logs} logs shown")
        if levels:
            result_lines.append(f"Levels: {', '.join(f'{k}: {v}' for k, v in levels.items())}")
        return "\n".join(result_lines)

    except Exception as e:
        logger.error(f"Error viewing logs: {str(e)}")
        return f"Error retrieving logs: {str(e)}"
