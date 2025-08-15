"""
Validation utilities for Blender MCP.

This module provides common validation functions for MCP tools.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel, validator, root_validator
import bpy
import numpy as np

T = TypeVar('T', bound=BaseModel)

def validate_object_exists(object_name: str) -> None:
    """Validate that a Blender object with the given name exists."""
    if object_name not in bpy.data.objects:
        raise ValueError(f"Object '{object_name}' not found")

def validate_vertex_group(object_name: str, group_name: str) -> None:
    """Validate that a vertex group exists on the specified object."""
    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")
    if group_name and group_name not in obj.vertex_groups:
        raise ValueError(f"Vertex group '{group_name}' not found on object '{object_name}'")

def validate_frame_range(frame_start: int, frame_end: int) -> None:
    """Validate that the frame range is valid."""
    if frame_start < 1:
        raise ValueError("Start frame must be at least 1")
    if frame_end < frame_start:
        raise ValueError("End frame must be greater than or equal to start frame")

def validate_positive(name: str, value: float) -> None:
    """Validate that a value is positive."""
    if value <= 0:
        raise ValueError(f"{name} must be positive")

def validate_range(name: str, value: float, min_val: float, max_val: float) -> None:
    """Validate that a value is within a specified range."""
    if not (min_val <= value <= max_val):
        raise ValueError(f"{name} must be between {min_val} and {max_val}")

class BaseValidator(BaseModel):
    """Base validator with common validation methods."""
    
    class Config:
        extra = 'forbid'  # Forbid extra fields
        validate_assignment = True  # Validate on attribute assignment
        arbitrary_types_allowed = True  # Allow non-pydantic types
    
    @root_validator(pre=True)
    def check_extra_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Check for extra fields in the input."""
        extra_fields = set(values.keys()) - set(cls.__fields__.keys())
        if extra_fields:
            raise ValueError(f"Unexpected fields: {', '.join(extra_fields)}")
        return values

class ObjectValidator(BaseValidator):
    """Validator for object-related parameters."""
    object_name: str
    
    @validator('object_name')
    def object_exists(cls, v: str) -> str:
        validate_object_exists(v)
        return v

class FrameRangeValidator(BaseValidator):
    """Validator for frame range parameters."""
    frame_start: int = 1
    frame_end: int = 250
    
    @validator('frame_start', 'frame_end')
    def validate_frames(cls, v: int, field) -> int:
        if field.name == 'frame_start' and v < 1:
            raise ValueError("Start frame must be at least 1")
        if field.name == 'frame_end' and v < 1:
            raise ValueError("End frame must be at least 1")
        return v
    
    @root_validator
    def validate_frame_range(cls, values):
        if values['frame_end'] < values['frame_start']:
            raise ValueError("End frame must be greater than or equal to start frame")
        return values

def validate_with_model(model: Type[BaseModel]) -> callable:
    """Decorator to validate function parameters with a Pydantic model."""
    def decorator(func: callable) -> callable:
        def wrapper(*args, **kwargs):
            # For tool functions, the first argument is the params dict
            if args and isinstance(args[0], dict):
                validated = model(**args[0])
                return func(validated.dict(), *args[1:], **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator
