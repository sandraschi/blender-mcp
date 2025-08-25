"""
Error handling utilities for Blender-MCP.

This module provides decorators and utilities for consistent error handling
across the Blender-MCP application.
"""
from functools import wraps
from typing import Any, Callable, Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError
from ..compat import JSONType
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class MCPError(Exception):
    """Base exception for all MCP-related errors."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(MCPError):
    """Raised when input validation fails."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(f"Validation error: {message}", details)

class BlenderOperationError(MCPError):
    """Raised when a Blender operation fails."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(f"Blender operation failed: {message}", details)

def handle_errors(func: Callable[..., T]) -> Callable[..., dict[str, Any]]:
    """
    Decorator to handle errors and return a consistent error response.
    
    Args:
        func: The function to wrap with error handling.
        
    Returns:
        A wrapped function that returns a consistent response format.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        try:
            result = await func(*args, **kwargs)
            return {
                "success": True,
                "result": result
            }
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "message": str(e),
                    "details": e.details
                }
            }
        except BlenderOperationError as e:
            logger.error(f"Blender operation error: {e}")
            return {
                "success": False,
                "error": {
                    "type": "blender_error",
                    "message": str(e),
                    "details": e.details
                }
            }
        except Exception as e:
            logger.exception("Unexpected error in MCP handler")
            return {
                "success": False,
                "error": {
                    "type": "internal_error",
                    "message": f"An unexpected error occurred: {str(e)}",
                    "details": {}
                }
            }
    
    return wrapper

def validate_with(model: Type[BaseModel]) -> Callable:
    """Decorator to validate function parameters with a Pydantic model.
    
    This decorator should be used on tool functions to validate their parameters.
    The model will be used to validate the input parameters before the function is called.
    """
    def decorator(func: Callable) -> Callable:
        # Store the model on the function for the error handler to use
        func._model = model
        return func
    return decorator

def validate_blender_object_exists(object_name: str) -> None:
    """Validate that a Blender object with the given name exists."""
    import bpy
    if object_name not in bpy.data.objects:
        raise BlenderOperationError(f"Object '{object_name}' not found")

def validate_vertex_group_exists(object_name: str, group_name: str) -> None:
    """Validate that a vertex group exists on the specified object."""
    import bpy
    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise BlenderOperationError(f"Object '{object_name}' not found")
    if group_name and group_name not in obj.vertex_groups:
        raise ValidationError(f"Vertex group '{group_name}' not found on object '{object_name}'")
