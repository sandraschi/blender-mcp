from __future__ import annotations

"""
Compatibility module for Blender-MCP.

Handles differences between Python versions and FastMCP implementations.
All FastMCP imports are done eagerly at module load with a clear error message.
"""

from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import (  # noqa: E402
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

# JSON-compatible types
JSONPrimitive = Union[str, int, float, bool, None]
JSONType = Union[JSONPrimitive, dict[str, Any], list[Any]]

# Re-export Set for compatibility
Set = set

# FastMCP 3.x component imports — fail loudly if unavailable so the problem is obvious
try:
    from fastmcp.server.low_level import LowLevelServer
    from fastmcp.tools.function_tool import FunctionTool
    from fastmcp.tools.tool import Tool
except ImportError as _fmcp_err:
    raise ImportError(
        f"FastMCP 3.1.1+ is required. Install with: pip install 'fastmcp>=3.1.1'\nOriginal error: {_fmcp_err}"
    ) from _fmcp_err

__all__ = [
    "Any",
    "Awaitable",
    "Callable",
    "Dict",
    "FunctionTool",
    "JSONPrimitive",
    "JSONType",
    "List",
    "LowLevelServer",
    "Mapping",
    "Optional",
    "Sequence",
    "Set",
    "Tool",
    "Tuple",
    "Type",
    "TypeAlias",
    "TypeVar",
    "Union",
]
