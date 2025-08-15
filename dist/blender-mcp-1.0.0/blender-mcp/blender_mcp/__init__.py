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

from .server import BlenderMCPServer
from .tools import *
from .decorators import *
from .exceptions import *

__version__ = "1.0.0"
__author__ = "Sandra"
__email__ = "sandra@sandraschi.dev"

__all__ = [
    "BlenderMCPServer",
    "__version__",
    "__author__",
    "__email__",
]
