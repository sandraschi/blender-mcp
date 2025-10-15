"""Custom exceptions for Blender MCP operations."""

from typing import Optional
from blender_mcp.compat import *


class BlenderMCPError(Exception):
    """Base exception for all Blender MCP operations."""

from ..compat import *

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class BlenderNotFoundError(BlenderMCPError):
    """Raised when Blender executable is not found."""

    def __init__(self, path: str):
        super().__init__(f"Blender executable not found at: {path}", "BLENDER_NOT_FOUND")


class BlenderScriptError(BlenderMCPError):
    """Raised when Blender script execution fails."""

    def __init__(self, script: str, error: str):
        super().__init__(f"Blender script failed: {error}", "SCRIPT_ERROR")
        self.script = script
        self.error = error


class BlenderExportError(BlenderMCPError):
    """Raised when asset export operations fail."""

    def __init__(self, format: str, path: str, error: str):
        super().__init__(f"Export to {format} failed at {path}: {error}", "EXPORT_ERROR")
        self.format = format
        self.path = path


class BlenderImportError(BlenderMCPError):
    """Raised when asset import operations fail."""

    def __init__(self, path: str, error: str):
        super().__init__(f"Import from {path} failed: {error}", "IMPORT_ERROR")
        self.path = path


class BlenderMaterialError(BlenderMCPError):
    """Raised when material operations fail."""

    def __init__(self, material_name: str, operation: str, error: str):
        super().__init__(
            f"Material '{material_name}' {operation} failed: {error}", "MATERIAL_ERROR"
        )
        self.material_name = material_name
        self.operation = operation


class BlenderRenderError(BlenderMCPError):
    """Raised when render operations fail."""

    def __init__(self, output_path: str, error: str):
        super().__init__(f"Render to {output_path} failed: {error}", "RENDER_ERROR")
        self.output_path = output_path


class BlenderMeshError(BlenderMCPError):
    """Raised when mesh operations fail."""

    def __init__(self, operation: str, error: str):
        super().__init__(f"Mesh operation '{operation}' failed: {error}", "MESH_ERROR")
        self.operation = operation


class BlenderAnimationError(BlenderMCPError):
    """Raised when animation operations fail."""

    def __init__(self, operation: str, error: str):
        super().__init__(f"Animation operation '{operation}' failed: {error}", "ANIMATION_ERROR")
        self.operation = operation


class BlenderLightingError(BlenderMCPError):
    """Raised when lighting operations fail."""

    def __init__(self, operation: str, error: str):
        super().__init__(f"Lighting operation '{operation}' failed: {error}", "LIGHTING_ERROR")
        self.operation = operation
