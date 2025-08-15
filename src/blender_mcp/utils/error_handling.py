"""
Error handling utilities for Blender MCP.

This module provides common error handling patterns and decorators.
"""
from functools import wraps
from typing import Any, Callable, Dict, Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError
from fastmcp.types import JSONType
import logging

logger = logging.getLogger(__name__)

class MCPError(Exception):
    """Base exception for all MCP-related errors."""
    def __init__(self, message: str, code: int = 400, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ValidationError(MCPError):
    """Raised when input validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Validation error: {message}", code=400, details=details)

class BlenderOperationError(MCPError):
    """Raised when a Blender operation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Blender operation failed: {message}", code=500, details=details)

def handle_errors(func: Callable) -> Callable:
    """Decorator to handle common errors in tool functions.
    
    This decorator:
    1. Validates input parameters against a Pydantic model if specified
    2. Handles common exceptions
    3. Returns a standardized response format
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> JSONType:
        try:
            # If the function has a _model attribute, validate inputs
            if hasattr(func, '_model'):
                try:
                    # For tool functions, the first argument is the params dict
                    if args and isinstance(args[0], dict):
                        validated_params = func._model(**args[0])
                        # Replace the params dict with the validated model
                        args = (validated_params.dict(),) + args[1:]
                except ValidationError as e:
                    error_details = {}
                    for error in e.errors():
                        field = ".".join(str(loc) for loc in error['loc'])
                        error_details[field] = error['msg']
                    raise ValidationError("Invalid parameters", details=error_details)
            
            # Call the original function
            result = await func(*args, **kwargs)
            return result
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "error": e.message,
                "code": e.code,
                "details": e.details
            }
        except BlenderOperationError as e:
            logger.error(f"Blender operation failed: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "error": e.message,
                "code": e.code,
                "details": e.details
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {
                "status": "ERROR",
                "error": "An unexpected error occurred",
                "code": 500,
                "details": {"exception": str(e), "type": type(e).__name__}
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
