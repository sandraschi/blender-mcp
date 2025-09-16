"""
Tool definitions for Blender-MCP.

This module provides decorators and utilities for registering and managing FastMCP tools.
Tools can be registered using the @app.tool decorator from the FastMCP application instance.
"""
from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
import functools
from pathlib import Path

# Import from our compatibility module
from ..compat import (
    JSONType, Dict, Any, Type, TypeVar, Callable, 
    Awaitable, Optional, Union, List, TypeAlias, Type,
    Tool, FunctionTool, ToolManager, LowLevelServer
)

# Import error handling utilities
from blender_mcp.utils.error_handling import (
    handle_errors,
    MCPError,
    ValidationError as MCPValidationError,
    BlenderOperationError
)

# Type alias for tool functions
ToolFunction: TypeAlias = Callable[..., Awaitable[JSONType]]

# Type variable for tool classes
T = TypeVar('T')

# Logger
logger = logging.getLogger(__name__)

# Global tool registration
_tools: Dict[str, Any] = {}

class ToolRegistrationError(Exception):
    """Exception raised for errors in tool registration."""
    pass

def register_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    require_validation: bool = True,
    **kwargs
) -> Callable[[ToolFunction], ToolFunction]:
    """
    Decorator to register a function as an MCP tool with enhanced error handling.
    
    Note: This is a compatibility layer. New code should use @app.tool decorator instead.
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        parameters: JSON Schema for tool parameters
        require_validation: Whether to enable parameter validation
        **kwargs: Additional tool parameters
        
    Returns:
        Decorator function that returns a wrapped tool function
    """
    def decorator(func: ToolFunction) -> ToolFunction:
        nonlocal name, description, parameters
        
        # Use function name if name not provided
        if name is None:
            name = func.__name__
            
        # Use docstring as description if not provided
        if description is None and func.__doc__:
            description = inspect.cleandoc(func.__doc__)
        
        # Get the validation model if available
        validation_model = getattr(func, '_validation_model', None)
        
        # If we have a validation model, use its schema
        if validation_model is not None and parameters is None:
            parameters = validation_model.schema()
        
        # Create the tool with the wrapped function
        @functools.wraps(func)
        async def wrapped_func(**params):
            try:
                # Validate parameters if a model is provided
                if require_validation and validation_model is not None:
                    try:
                        validated = validation_model(**params)
                        # Convert model to dict for the function
                        params = validated.dict()
                    except ValidationError as e:
                        error_details = {}
                        for error in e.errors():
                            field = ".".join(str(loc) for loc in error['loc'])
                            error_details[field] = error['msg']
                        raise MCPValidationError("Invalid parameters", details=error_details)
                
                # Call the original function
                return await func(**params)
                
            except MCPValidationError as e:
                # Re-raise validation errors
                raise
            except BlenderOperationError as e:
                # Re-raise Blender operation errors
                raise
            except Exception as e:
                # Wrap other exceptions
                raise MCPError(f"Tool execution failed: {str(e)}")
        
        # Create the tool
        tool = FunctionTool(
            name=name,
            description=description or "",
            parameters=parameters or {"type": "object", "properties": {}},
            execute=handle_errors(wrapped_func),
            **kwargs
        )
        
        # Register the tool
        if tool.name in _tools:
            logger.warning(f"Tool '{tool.name}' is already registered. Overwriting.")
        
        _tools[tool.name] = tool
        
        # Return the original function to allow chaining decorators
        return func
        
    return decorator

def validate_with(model: Type[BaseModel]) -> Callable[[ToolFunction], ToolFunction]:
    """
    Decorator to associate a Pydantic model with a tool for parameter validation.
    
    Args:
        model: Pydantic model to use for validation
        
    Returns:
        Decorator that adds validation to the function
    """
    def decorator(func: ToolFunction) -> ToolFunction:
        # Store the model on the function
        func._validation_model = model
        return func
    return decorator

def get_tool(name: str) -> Optional[Any]:
    """
    Get a registered tool by name.
    
    Args:
        name: Name of the tool to retrieve
        
    Returns:
        The Tool instance or None if not found
    """
    return _tools.get(name)

def get_toolset() -> Any:
    """
    Get the MCP toolset with all registered tools.
    
    Returns:
        ToolManager containing all registered tools
    """
    return ToolManager(tools=list(_tools.values()))

def register_tools(server: Any) -> None:
    """
    Register all tools with an MCP server.
    
    Args:
        server: The MCP server instance
    """
    for tool in _tools.values():
        server.register_tool(tool)

def discover_tools(package: str = 'blender_mcp.tools') -> None:
    """
    Discover and import all modules in the tools package.
    
    This will cause all @register_tool decorators to be executed.
    
    Args:
        package: The package to search for tool modules
    """
    try:
        package_mod = importlib.import_module(package)
        package_path = Path(package_mod.__file__).parent if hasattr(package_mod, '__file__') else None
        
        if not package_path:
            raise ToolRegistrationError(f"Could not find package path for {package}")
            
        # Import all modules in the package
        problematic_modules = {
            'export_tools', 'physics_advanced', 'physics_tools_enhanced', 
            'render_tools', 'scene_tools', 'rendering_tools', 'material_tools', 'animation_tools'
        }
        
        for _, modname, _ in pkgutil.iter_modules([str(package_path)]):
            if modname != '__init__' and not modname.startswith('_'):
                if modname in problematic_modules:
                    logger.warning(f"Skipping problematic tool module: {modname}")
                    continue
                    
                try:
                    full_module_name = f"{package}.{modname}"
                    logger.debug(f"Importing tool module: {full_module_name}")
                    importlib.import_module(full_module_name)
                    logger.info(f"Successfully imported tool module: {full_module_name}")
                except ImportError as e:
                    logger.error(f"Failed to import tool module {modname}: {e}", exc_info=True)
                    # Don't raise, continue with other modules
                except Exception as e:
                    logger.error(f"Error initializing tool module {modname}: {e}", exc_info=True)
                    # Don't raise, continue with other modules
                    
    except Exception as e:
        logger.error(f"Error discovering tools: {e}", exc_info=True)
        raise ToolRegistrationError(f"Failed to discover tools: {e}")

# Re-export commonly used types and functions
__all__ = [
    'register_tool',
    'validate_with',
    'get_tool',
    'get_toolset',
    'register_tools',
    'discover_tools',
    'MCPError',
    'MCPValidationError',
    'BlenderOperationError',
    'ToolFunction'
]

# Import all tool modules when this package is imported
# This ensures tools are registered when the package is imported
discover_tools()
