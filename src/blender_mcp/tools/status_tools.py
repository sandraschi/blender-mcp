"""
System status and monitoring tools for Blender MCP.

Provides comprehensive system information, health checks, and monitoring
capabilities for the Blender MCP server and Blender environment.
"""

from ..compat import *

import os
import sys
import psutil
import platform
from datetime import datetime


# Import app lazily to avoid circular imports
def get_app():
    from blender_mcp.app import app

    return app


def _register_status_tools():
    """Register status tools with the app."""
    app = get_app()

    @app.tool
    async def blender_status(
        include_blender_info: bool = True,
        include_system_info: bool = True,
        include_performance: bool = True,
    ) -> str:
        """
        Get comprehensive system status and health information.

        Returns detailed information about the Blender MCP server, system resources,
        Blender availability, and performance metrics.

        Args:
            include_blender_info: Include Blender-specific information
            include_system_info: Include general system information
            include_performance: Include performance metrics

        Returns:
            Formatted status report with all requested information

        Examples:
            - blender_status() - Complete status
            - blender_status(include_performance=False) - Status without performance
        """
        status_parts = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        status_parts.append(f"Blender MCP Status Report - {timestamp}")
        status_parts.append("=" * 50)

        # MCP Server status
        try:
            from blender_mcp.app import get_app

            get_app()
            status_parts.append("✅ MCP Server: Running")
        except Exception as e:
            status_parts.append(f"❌ MCP Server: Error - {str(e)}")

        if include_blender_info:
            status_parts.append("")
            status_parts.append("Blender Information:")
            status_parts.append("-" * 20)

            from blender_mcp.config import BLENDER_EXECUTABLE, validate_blender_executable

            if validate_blender_executable():
                status_parts.append(f"✅ Blender Available: {BLENDER_EXECUTABLE}")
                # Try to get version
                try:
                    from blender_mcp.config import get_blender_version

                    version = get_blender_version()
                    if version:
                        status_parts.append(f"📦 Version: {version}")
                    else:
                        status_parts.append("📦 Version: Unknown")
                except Exception:
                    status_parts.append("📦 Version: Unable to detect")
            else:
                status_parts.append(f"❌ Blender Not Found: {BLENDER_EXECUTABLE}")

        if include_system_info:
            status_parts.append("")
            status_parts.append("System Information:")
            status_parts.append("-" * 20)

            status_parts.append(f"🖥️  Platform: {platform.system()} {platform.release()}")
            status_parts.append(f"🧠 Processor: {platform.processor()}")
            status_parts.append(f"🐍 Python: {sys.version.split()[0]}")

            # Memory info
            try:
                memory = psutil.virtual_memory()
                memory_gb = memory.total / (1024**3)
                status_parts.append(f"💾 Memory: {memory_gb:.1f} GB total")
            except Exception:
                status_parts.append("💾 Memory: Unable to detect")

        if include_performance:
            status_parts.append("")
            status_parts.append("Performance Metrics:")
            status_parts.append("-" * 20)

            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                status_parts.append(f"⚡ CPU Usage: {cpu_percent:.1f}%")

                # Memory usage
                memory = psutil.virtual_memory()
                status_parts.append(
                    f"💾 Memory Usage: {memory.percent:.1f}% ({memory.available // (1024**2):,} MB free)"
                )

                # Disk usage
                disk = psutil.disk_usage("/")
                status_parts.append(
                    f"💿 Disk Usage: {disk.percent:.1f}% ({disk.free // (1024**3):.1f} GB free)"
                )

            except Exception as e:
                status_parts.append(f"⚠️  Performance monitoring unavailable: {str(e)}")

        return "\n".join(status_parts)

    @app.tool
    async def blender_system_info() -> str:
        """
        Get detailed system and environment information.

        Returns comprehensive information about the operating system, Python environment,
        available resources, and configuration.

        Returns:
            Detailed system information report

        Examples:
            - blender_system_info() - Get all system details
        """
        info_parts = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        info_parts.append(f"Blender MCP System Information - {timestamp}")
        info_parts.append("=" * 50)

        # Basic system info
        info_parts.append("Operating System:")
        info_parts.append(f"  • Platform: {platform.system()} {platform.version()}")
        info_parts.append(f"  • Architecture: {platform.machine()}")
        info_parts.append(f"  • Processor: {platform.processor()}")

        # Python info
        info_parts.append("")
        info_parts.append("Python Environment:")
        info_parts.append(f"  • Version: {sys.version}")
        info_parts.append(f"  • Executable: {sys.executable}")
        info_parts.append(f"  • Current Directory: {os.getcwd()}")

        # Environment variables
        info_parts.append("")
        info_parts.append("Key Environment Variables:")
        env_vars = ["BLENDER_EXECUTABLE", "PYTHONPATH", "PATH"]
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                if var == "PATH":
                    # Show just the first path element for brevity
                    display_value = value.split(os.pathsep)[0] + "..."
                else:
                    display_value = value
                info_parts.append(f"  • {var}: {display_value}")
            else:
                info_parts.append(f"  • {var}: Not set")

        # Resource information
        info_parts.append("")
        info_parts.append("System Resources:")
        try:
            # Memory
            memory = psutil.virtual_memory()
            info_parts.append(f"  • Total Memory: {memory.total // (1024**3):.1f} GB")
            info_parts.append(f"  • Available Memory: {memory.available // (1024**3):.1f} GB")

            # CPU
            info_parts.append(
                f"  • CPU Cores: {psutil.cpu_count()} physical, {psutil.cpu_count(logical=True)} logical"
            )

            # Disk
            disk = psutil.disk_usage("/")
            info_parts.append(
                f"  • Disk Space: {disk.total // (1024**3):.1f} GB total, {disk.free // (1024**3):.1f} GB free"
            )

        except Exception as e:
            info_parts.append(f"  • Resource info unavailable: {str(e)}")

        return "\n".join(info_parts)

    @app.tool
    async def blender_health_check() -> str:
        """
        Perform a comprehensive health check of the Blender MCP system.

        Checks Blender availability, system resources, tool registration,
        and overall system health.

        Returns:
            Health check results with status indicators

        Examples:
            - blender_health_check() - Run complete health check
        """
        checks = []
        overall_status = "✅ HEALTHY"

        # Check 1: MCP Server
        try:
            from blender_mcp.app import get_app

            get_app()
            checks.append("✅ MCP Server: Running and accessible")
        except Exception as e:
            checks.append(f"❌ MCP Server: Failed - {str(e)}")
            overall_status = "❌ UNHEALTHY"

        # Check 2: Blender Availability
        try:
            from blender_mcp.config import validate_blender_executable

            if validate_blender_executable():
                checks.append("✅ Blender: Available and validated")
            else:
                checks.append("❌ Blender: Not found or inaccessible")
                overall_status = "❌ UNHEALTHY"
        except Exception as e:
            checks.append(f"❌ Blender: Check failed - {str(e)}")
            overall_status = "❌ UNHEALTHY"

        # Check 3: System Resources
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            resource_issues = []
            if memory.percent > 90:
                resource_issues.append(f"high memory usage ({memory.percent:.1f}%)")
            if disk.percent > 95:
                resource_issues.append(f"low disk space ({disk.percent:.1f}% used)")

            if resource_issues:
                checks.append(
                    f"⚠️  System Resources: Issues detected - {', '.join(resource_issues)}"
                )
                if overall_status == "✅ HEALTHY":
                    overall_status = "⚠️  WARNING"
            else:
                checks.append("✅ System Resources: Adequate levels")

        except Exception as e:
            checks.append(f"⚠️  System Resources: Monitoring unavailable - {str(e)}")

        # Check 4: Tool Registration
        try:
            from blender_mcp.help import list_functions, get_categories

            categories = get_categories()
            total_tools = sum(len(list_functions(cat)) for cat in categories)

            if total_tools > 0:
                checks.append(
                    f"✅ Tool Registration: {total_tools} tools across {len(categories)} categories"
                )
            else:
                checks.append("❌ Tool Registration: No tools registered")
                overall_status = "❌ UNHEALTHY"

        except Exception as e:
            checks.append(f"❌ Tool Registration: Check failed - {str(e)}")
            overall_status = "❌ UNHEALTHY"

        # Format the response
        result = f"Blender MCP Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += "=" * 60 + "\n"
        result += f"Overall Status: {overall_status}\n\n"
        result += "Detailed Checks:\n"
        result += "\n".join(checks)

        return result

    @app.tool
    async def blender_performance_monitor(duration_seconds: int = 10) -> str:
        """
        Monitor system performance over a specified duration.

        Collects performance metrics at regular intervals to identify
        performance patterns and potential issues.

        Args:
            duration_seconds: How long to monitor (max 60 seconds)

        Returns:
            Performance monitoring report with samples and summary

        Examples:
            - blender_performance_monitor() - Monitor for 10 seconds
            - blender_performance_monitor(30) - Monitor for 30 seconds
        """
        import time

        if duration_seconds > 60:
            duration_seconds = 60  # Cap at 60 seconds

        samples = []
        start_time = datetime.now()

        result = f"Blender MCP Performance Monitor - {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += "=" * 70 + "\n"
        result += f"Monitoring Duration: {duration_seconds} seconds\n"
        result += "Sample Interval: 2 seconds\n"
        result += f"Number of Samples: {max(1, duration_seconds // 2)}\n\n"

        try:
            for i in range(0, duration_seconds, 2):
                sample_time = datetime.now()
                perf_data = {}

                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                perf_data["cpu"] = cpu_percent

                # Memory usage
                memory = psutil.virtual_memory()
                perf_data["memory"] = memory.percent

                # Disk usage
                disk = psutil.disk_usage("/")
                perf_data["disk"] = disk.percent

                samples.append(
                    {
                        "sample": len(samples) + 1,
                        "timestamp": sample_time.strftime("%H:%M:%S"),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "disk_percent": disk.percent,
                    }
                )

                if i + 2 < duration_seconds:  # Don't sleep after last sample
                    time.sleep(2)

            # Calculate summary statistics
            cpu_values = [s["cpu_percent"] for s in samples]
            memory_values = [s["memory_percent"] for s in samples]
            disk_values = [s["disk_percent"] for s in samples]

            result += "Performance Samples:\n"
            result += f"{'Sample':<8} {'Time':<12} {'CPU%':<8} {'Mem%':<8} {'Disk%':<8}\n"
            result += "-" * 60 + "\n"

            for sample in samples:
                result += f"{sample['sample']:<8} {sample['timestamp']:<12} {sample['cpu_percent']:<8.1f} {sample['memory_percent']:<8.1f} {sample['disk_percent']:<8.1f}\n"

            result += "\nSummary Statistics:\n"
            result += "-" * 20 + "\n"
            result += f"CPU Usage:    Avg {sum(cpu_values) / len(cpu_values):5.1f}% | Max {max(cpu_values):5.1f}% | Min {min(cpu_values):5.1f}%\n"
            result += f"Memory Usage: Avg {sum(memory_values) / len(memory_values):5.1f}% | Max {max(memory_values):5.1f}% | Min {min(memory_values):5.1f}%\n"
            result += f"Disk Usage:   Avg {sum(disk_values) / len(disk_values):5.1f}% | Max {max(disk_values) / len(disk_values):5.1f}% | Min {min(disk_values):5.1f}%\n"

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            result += f"\nMonitoring completed in {duration:.1f} seconds"

        except Exception as e:
            result += f"❌ Performance monitoring failed: {str(e)}\n"
            result += "This may be due to system permissions or psutil not being available."

        return result


# Register the tools when this module is imported
_register_status_tools()
