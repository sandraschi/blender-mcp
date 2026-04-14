"""
System status and monitoring portmanteau for Blender MCP.

Exposes blender_status: status, system_info, health_check, performance_monitor.
"""

import json
import os
import platform
import sys
import time
from datetime import datetime
from typing import Literal

import psutil

from ..compat import *


def _register_status_tools():
    """Register the blender_status portmanteau tool."""
    from blender_mcp.app import get_app

    app = get_app()

    @app.tool
    async def blender_status(
        operation: Literal["status", "system_info", "health_check", "performance_monitor"] = "status",
        include_blender_info: bool = True,
        include_system_info: bool = True,
        include_performance: bool = True,
        duration_seconds: int = 10,
        limit: Optional[int] = 50,
        format: Literal["text", "json"] = "text",
    ) -> str:
        """
        System status and monitoring (portmanteau).

        Operations:
        - status: MCP server, Blender, system, and performance summary
        - system_info: Detailed OS, Python, env, and resources
        - health_check: Blender availability, resources, tool registration
        - performance_monitor: Sample CPU/memory/disk over duration_seconds (max 60)

        Args:
            operation: status | system_info | health_check | performance_monitor
            include_blender_info: For status — include Blender section
            include_system_info: For status — include system section
            include_performance: For status — include performance section
            duration_seconds: For performance_monitor — sampling duration (1–60)
            format: "json" for webapp dict (status only); "text" for report string
        """

        # ------------------------------------------------------------------
        if operation == "status":
            if format == "json":
                try:
                    from blender_mcp.config import validate_blender_executable

                    blender_ok = validate_blender_executable()
                    from blender_mcp import __version__

                    version = __version__
                except Exception:
                    blender_ok = False
                    version = "unknown"
                return json.dumps({"status": "ok", "blender": blender_ok, "version": version})

            parts = []
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            parts.append(f"Blender MCP Status Report — {ts}")
            parts.append("=" * 50)

            try:
                from blender_mcp.app import get_app as _ga

                _ga()
                parts.append("MCP Server: Running")
            except Exception as e:
                parts.append(f"MCP Server: Error — {e}")

            if include_blender_info:
                parts.append("\nBlender:")
                try:
                    from blender_mcp.config import BLENDER_EXECUTABLE, validate_blender_executable

                    if validate_blender_executable():
                        parts.append(f"  Available: {BLENDER_EXECUTABLE}")
                    else:
                        parts.append(f"  Not found: {BLENDER_EXECUTABLE}")
                except Exception as e:
                    parts.append(f"  Check failed: {e}")

            if include_system_info:
                parts.append("\nSystem:")
                parts.append(f"  Platform: {platform.system()} {platform.release()}")
                parts.append(f"  Python: {sys.version.split()[0]}")
                try:
                    mem = psutil.virtual_memory()
                    parts.append(f"  Memory: {mem.total / 1024**3:.1f} GB total")
                except Exception:
                    pass

            if include_performance:
                parts.append("\nPerformance:")
                try:
                    cpu = psutil.cpu_percent(interval=1)
                    mem = psutil.virtual_memory()
                    disk = psutil.disk_usage("/")
                    parts.append(f"  CPU: {cpu:.1f}%")
                    parts.append(f"  Memory: {mem.percent:.1f}% ({mem.available // 1024**2:,} MB free)")
                    parts.append(f"  Disk: {disk.percent:.1f}% ({disk.free // 1024**3:.1f} GB free)")
                except Exception as e:
                    parts.append(f"  Unavailable: {e}")

            return "\n".join(parts)

        # ------------------------------------------------------------------
        elif operation == "system_info":
            parts = []
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            parts.append(f"Blender MCP System Information — {ts}")
            parts.append("=" * 50)
            parts.append(f"Platform: {platform.system()} {platform.version()}")
            parts.append(f"Architecture: {platform.machine()}")
            parts.append(f"Processor: {platform.processor()}")
            parts.append(f"\nPython: {sys.version}")
            parts.append(f"Executable: {sys.executable}")
            parts.append(f"CWD: {os.getcwd()}")

            parts.append("\nEnvironment:")
            for var in ("BLENDER_EXECUTABLE", "PYTHONPATH"):
                val = os.environ.get(var)
                parts.append(f"  {var}: {val or 'Not set'}")

            parts.append("\nResources:")
            try:
                mem = psutil.virtual_memory()
                parts.append(f"  Memory total: {mem.total // 1024**3:.1f} GB")
                parts.append(f"  Memory available: {mem.available // 1024**3:.1f} GB")
                parts.append(f"  CPU cores: {psutil.cpu_count()} physical, {psutil.cpu_count(logical=True)} logical")
                disk = psutil.disk_usage("/")
                parts.append(f"  Disk: {disk.total // 1024**3:.1f} GB total, {disk.free // 1024**3:.1f} GB free")
            except Exception as e:
                parts.append(f"  Unavailable: {e}")

            return "\n".join(parts)

        # ------------------------------------------------------------------
        elif operation == "health_check":
            checks = []
            status = "HEALTHY"

            try:
                from blender_mcp.app import get_app as _ga

                _ga()
                checks.append("MCP Server: OK")
            except Exception as e:
                checks.append(f"MCP Server: FAIL — {e}")
                status = "UNHEALTHY"

            try:
                from blender_mcp.config import validate_blender_executable

                if validate_blender_executable():
                    checks.append("Blender: Available")
                else:
                    checks.append("Blender: NOT FOUND")
                    status = "UNHEALTHY"
            except Exception as e:
                checks.append(f"Blender: FAIL — {e}")
                status = "UNHEALTHY"

            try:
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage("/")
                issues = []
                if mem.percent > 90:
                    issues.append(f"high memory ({mem.percent:.0f}%)")
                if disk.percent > 95:
                    issues.append(f"low disk ({disk.percent:.0f}%)")
                if issues:
                    checks.append(f"Resources: WARNING — {', '.join(issues)}")
                    if status == "HEALTHY":
                        status = "WARNING"
                else:
                    checks.append("Resources: OK")
            except Exception as e:
                checks.append(f"Resources: FAIL — {e}")

            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines = [f"Blender MCP Health Check — {ts}", "=" * 50, f"Overall: {status}", "", *checks]
            return "\n".join(lines)

        # ------------------------------------------------------------------
        elif operation == "performance_monitor":
            duration_seconds = min(max(1, duration_seconds), 60)
            samples = []
            start = datetime.now()
            try:
                for _ in range(0, duration_seconds, 2):
                    t = datetime.now()
                    samples.append(
                        {
                            "n": len(samples) + 1,
                            "time": t.strftime("%H:%M:%S"),
                            "cpu": psutil.cpu_percent(interval=1),
                            "mem": psutil.virtual_memory().percent,
                            "disk": psutil.disk_usage("/").percent,
                        }
                    )
                    if len(samples) * 2 < duration_seconds:
                        time.sleep(1)
            except Exception as e:
                return f"Performance monitoring failed: {e}"

            lines = [
                f"Blender MCP Performance Monitor — {start.strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 60,
                f"Duration: {duration_seconds}s  Samples: {len(samples)}",
                "",
                f"{'#':<5} {'Time':<12} {'CPU%':<8} {'Mem%':<8} {'Disk%'}",
                "-" * 50,
            ]
            for s in samples:
                lines.append(f"{s['n']:<5} {s['time']:<12} {s['cpu']:<8.1f} {s['mem']:<8.1f} {s['disk']:.1f}")

            if samples:
                cpu_v = [s["cpu"] for s in samples]
                mem_v = [s["mem"] for s in samples]
                lines += [
                    "",
                    "Summary:",
                    f"  CPU:    avg {sum(cpu_v) / len(cpu_v):.1f}%  max {max(cpu_v):.1f}%  min {min(cpu_v):.1f}%",
                    f"  Memory: avg {sum(mem_v) / len(mem_v):.1f}%  max {max(mem_v):.1f}%  min {min(mem_v):.1f}%",
                ]
            return "\n".join(lines)

        # ------------------------------------------------------------------
        else:
            return f"Unknown operation '{operation}'. Use: status, system_info, health_check, performance_monitor"

    @app.tool
    async def server_info() -> str:
        """Return Blender MCP server information, version, and status."""
        try:
            from blender_mcp import __version__
            from blender_mcp.config import BLENDER_EXECUTABLE, validate_blender_executable

            blender_ok = validate_blender_executable()
            return json.dumps(
                {
                    "name": "blender-mcp",
                    "version": __version__,
                    "status": "connected",
                    "blender_executable": str(BLENDER_EXECUTABLE),
                    "blender_status": "ok" if blender_ok else "error",
                    "platform": platform.system(),
                    "python_version": sys.version.split()[0],
                }
            )
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})


_register_status_tools()
