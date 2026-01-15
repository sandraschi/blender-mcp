from __future__ import annotations

"""
Compatibility module for Blender-MCP.

This module provides type definitions and compatibility shims to handle differences
between Python versions and FastMCP implementations.
"""

from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
)
from typing import (
    Set as TypingSet,
)

# Define JSON-compatible types
JSONPrimitive = Union[str, int, float, bool, None]
JSONType = Union[JSONPrimitive, Dict[str, Any], List[Any]]

# Re-export Set as both Set and TypingSet for compatibility
Set = TypingSet

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
                "Failed to import FastMCP components. Make sure FastMCP is installed. "
                f"Original error: {e}"
            )


# Import FastMCP components on module load
_import_fastmcp_components()

# Re-export commonly used types and components
__all__ = [
    # Basic types
    "Dict",
    "List",
    "Tuple",
    "Set",
    "Sequence",
    "Mapping",
    "Any",
    "Type",
    "Callable",
    "Awaitable",
    "TypeVar",
    "TypeAlias",
    "Optional",
    "Union",
    # Custom types
    "JSONType",
    "JSONPrimitive",
    # FastMCP components
    "Tool",
    "FunctionTool",
    "ToolManager",
    "LowLevelServer",
]
