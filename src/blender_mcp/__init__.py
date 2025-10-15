"""Blender MCP Server - Avatar Ecosystem Integration

A comprehensive MCP server for Blender automation, specifically designed for
avatar ecosystem workflows including Unity3D and VRChat integration.

Features:
- Scene management and manipulation
- Procedural mesh generation (furniture, props)
- PBR material system
- Asset export pipeline (FBX/glTF)
- Render operations
- Avatar-relative scaling
- VRChat optimization tools
"""

# Import only specific types from typing to avoid circular imports
from typing import (
    Dict,
    List,
    Tuple,
    Any,
    Type,
    Callable,
    Awaitable,
    Optional,
    Union,
    TypeVar,
    TypeAlias,
    Mapping,
    Sequence,
)

# Import custom types from compat
from .compat import JSONType, JSONPrimitive

# Import exceptions first to prevent circular imports
from .exceptions import *

# Lazy imports for modules that might cause circular imports
app = None


def get_app():
    """Get the FastMCP application instance with lazy initialization."""
    global app
    if app is None:
        from .app import app as _app

        app = _app
    return app


__version__ = "1.0.0"
__author__ = "Sandra"
__email__ = "sandra@sandraschi.dev"

__all__ = [
    "get_app",
    "__version__",
    "__author__",
    "__email__",
]
