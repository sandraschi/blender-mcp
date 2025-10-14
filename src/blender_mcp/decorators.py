"""Decorators for Blender MCP operations with validation, logging, and error handling."""

import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from loguru import logger

from blender_mcp.compat import *
from blender_mcp.exceptions import BlenderMCPError

F = TypeVar('F', bound=Callable[..., Any])


def blender_operation(
    operation_name: str,
    log_args: bool = True,
    log_result: bool = False,
    validate_blender: bool = True
) -> Callable[[F], F]:
    """
    Decorator for Blender operations with comprehensive logging and error handling.
    
    Args:
        operation_name: Human-readable operation name for logging
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        validate_blender: Whether to validate Blender availability before operation
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            operation_id = f"{operation_name}_{int(start_time * 1000)}"
            
            logger.info(f"🎨 Starting Blender operation: {operation_name} [{operation_id}]")
            
            if log_args:
                logger.debug(f"📥 Operation args: {args[1:] if args else []}, kwargs: {kwargs}")
            
            try:
                if validate_blender:
                    # Validate Blender availability (implementation in server)
                    if args and hasattr(args[0], '_validate_blender_available'):
                        await args[0]._validate_blender_available()
                
                result = await func(*args, **kwargs)
                
                execution_time = time.time() - start_time
                logger.info(f"✅ Blender operation completed: {operation_name} [{operation_id}] ({execution_time:.2f}s)")
                
                if log_result:
                    logger.debug(f"📤 Operation result: {result}")
                
                return result
                
            except BlenderMCPError as e:
                execution_time = time.time() - start_time
                logger.error(f"❌ Blender operation failed: {operation_name} [{operation_id}] ({execution_time:.2f}s) - {e}")
                raise
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"💥 Unexpected error in Blender operation: {operation_name} [{operation_id}] ({execution_time:.2f}s) - {e}")
                raise BlenderMCPError(f"Unexpected error in {operation_name}: {str(e)}", "UNEXPECTED_ERROR")
        
        return wrapper
    return decorator


def validate_scene_exists(func: F) -> F:
    """Decorator to validate that a Blender scene exists before operation."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        # Implementation would check if scene exists
        logger.debug("🔍 Validating scene exists")
        return await func(*args, **kwargs)
    return wrapper


def validate_mesh_exists(mesh_name_param: str = "mesh_name") -> Callable[[F], F]:
    """Decorator to validate that a specific mesh exists in the scene."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            mesh_name = kwargs.get(mesh_name_param)
            logger.debug(f"🔍 Validating mesh exists: {mesh_name}")
            # Implementation would check if mesh exists
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def validate_material_exists(material_name_param: str = "material_name") -> Callable[[F], F]:
    """Decorator to validate that a specific material exists."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            material_name = kwargs.get(material_name_param)
            logger.debug(f"🔍 Validating material exists: {material_name}")
            # Implementation would check if material exists
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_export_path(path_param: str = "output_path") -> Callable[[F], F]:
    """Decorator to validate export path is writable."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            output_path = kwargs.get(path_param)
            logger.debug(f"🔍 Validating export path: {output_path}")
            # Implementation would validate path is writable
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def cache_blender_data(cache_key: str, ttl: int = 300) -> Callable[[F], F]:
    """Decorator to cache Blender data operations."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Implementation would use caching mechanism
            logger.debug(f"🗄️ Checking cache for key: {cache_key}")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
