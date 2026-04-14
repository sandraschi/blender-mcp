from __future__ import annotations

"""
Compatibility module for Blender-MCP.

This module provides type definitions and compatibility shims to handle differences
between Python versions and FastMCP implementations.
"""

from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
)

# Define JSON-compatible types
JSONPrimitive = Union[str, int, float, bool, None]
JSONType = Union[JSONPrimitive, dict[str, Any], list[Any]]

# Re-export Set as both Set and TypingSet for compatibility
Set = set

# Initialize FastMCP components as None
Tool = None
FunctionTool = None
ToolManager = None
LowLevelServer = None


def _import_fastmcp_components():
    """Lazy import of FastMCP components to prevent circular imports."""
    global Tool, FunctionTool, ToolManager, LowLevelServer

    if Tool is None:
        try:
            # Import FastMCP components
            from fastmcp.server.low_level import LowLevelServer as _LowLevelServer
            from fastmcp.tools.tool import FunctionTool as _FunctionTool
            from fastmcp.tools.tool import Tool as _Tool
            from fastmcp.tools.tool_manager import ToolManager as _ToolManager

            # Assign to global variables
            Tool = _Tool
            FunctionTool = _FunctionTool
            ToolManager = _ToolManager
            LowLevelServer = _LowLevelServer

        except ImportError as e:
            raise ImportError(
                f"Failed to import FastMCP components. Make sure FastMCP is installed. Original error: {e}"
            )


# Import FastMCP components on module load
_import_fastmcp_components()

# Re-export commonly used types and components
__all__ = [
    "Any",
    "Awaitable",
    "Callable",
    # Basic types
    "Dict",
    "FunctionTool",
    "JSONPrimitive",
    # Custom types
    "JSONType",
    "List",
    "LowLevelServer",
    "Mapping",
    "Optional",
    "Sequence",
    "Set",
    # FastMCP components
    "Tool",
    "ToolManager",
    "Tuple",
    "Type",
    "TypeAlias",
    "TypeVar",
    "Union",
]
