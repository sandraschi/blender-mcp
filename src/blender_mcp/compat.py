from __future__ import annotations

"""
Compatibility module for Blender-MCP.

Handles differences between Python versions and FastMCP implementations.
All FastMCP imports are done eagerly at module load with a clear error message.
"""

from typing import (  # noqa: E402
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
from typing import Set as TypingSet  # noqa: E402

# JSON-compatible types
JSONPrimitive = Union[str, int, float, bool, None]
JSONType = Union[JSONPrimitive, Dict[str, Any], List[Any]]

# Re-export Set for compatibility
Set = TypingSet

# FastMCP 3.x component imports — fail loudly if unavailable so the problem is obvious
try:
    from fastmcp.server.low_level import LowLevelServer
    from fastmcp.tools.function_tool import FunctionTool
    from fastmcp.tools.tool import Tool
except ImportError as _fmcp_err:
    raise ImportError(
        "FastMCP 3.1.1+ is required. Install with: pip install 'fastmcp>=3.1.1'\n"
        f"Original error: {_fmcp_err}"
    ) from _fmcp_err

__all__ = [
    "Dict", "List", "Tuple", "Set", "Sequence", "Mapping",
    "Any", "Type", "Callable", "Awaitable", "TypeVar", "TypeAlias",
    "Optional", "Union",
    "JSONType", "JSONPrimitive",
    "Tool", "FunctionTool", "LowLevelServer",
]
