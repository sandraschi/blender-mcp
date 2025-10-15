"""
Scene Tools for Blender-MCP.

This module provides tools for scene management and organization in Blender.
The actual tool functions are defined in the handlers and registered with @app.tool decorators.
This module provides parameter models and enums for documentation and validation purposes.
"""

from ..compat import *

from typing import List, Tuple
from enum import Enum
from pydantic import BaseModel, Field

# Note: The actual tool functions are defined in the handlers and registered with @app.tool decorators.
# This module provides parameter models and enums for documentation and validation purposes.
# We don't import from handlers to avoid circular imports.


# Enums for scene settings
class RenderEngine(str, Enum):
    """Render engine types."""

    EEVEE = "BLENDER_EEVEE"
    WORKBENCH = "BLENDER_WORKBENCH"
    CYCLES = "CYCLES"


class DeviceType(str, Enum):
    """Device types for rendering."""

    CPU = "CPU"
    CUDA = "CUDA"
    OPTIX = "OPTIX"


class LightType(str, Enum):
    """Light types."""

    SUN = "SUN"
    POINT = "POINT"
    SPOT = "SPOT"
    AREA = "AREA"


class UnitSystem(str, Enum):
    """Unit systems."""

    NONE = "NONE"
    METRIC = "METRIC"
    IMPERIAL = "IMPERIAL"


class UnitLength(str, Enum):
    """Unit length types."""

    ADAPTIVE = "ADAPTIVE"
    KILOMETERS = "KILOMETERS"
    METERS = "METERS"
    CENTIMETERS = "CENTIMETERS"
    MILLIMETERS = "MILLIMETERS"
    MICROMETERS = "MICROMETERS"
    MILES = "MILES"
    FEET = "FEET"
    INCHES = "INCHES"
    THOU = "THOU"


class UnitMass(str, Enum):
    """Unit mass types."""

    ADAPTIVE = "ADAPTIVE"
    TONNES = "TONNES"
    KILOGRAMS = "KILOGRAMS"
    GRAMS = "GRAMS"
    POUNDS = "POUNDS"
    OUNCES = "OUNCES"


class UnitTime(str, Enum):
    """Unit time types."""

    ADAPTIVE = "ADAPTIVE"
    YEARS = "YEARS"
    MONTHS = "MONTHS"
    DAYS = "DAYS"
    HOURS = "HOURS"
    MINUTES = "MINUTES"
    SECONDS = "SECONDS"
    MILLISECONDS = "MILLISECONDS"


class UnitTemperature(str, Enum):
    """Unit temperature types."""

    KELVIN = "KELVIN"
    CELSIUS = "CELSIUS"
    FAHRENHEIT = "FAHRENHEIT"


class FileFormat(str, Enum):
    """File formats for rendering."""

    PNG = "PNG"
    JPEG = "JPEG"
    TIFF = "TIFF"
    OPEN_EXR = "OPEN_EXR"
    HDR = "HDR"


class ColorMode(str, Enum):
    """Color modes for rendering."""

    RGB = "RGB"
    RGBA = "RGBA"
    BW = "BW"


class ColorDepth(str, Enum):
    """Color depth for rendering."""

    U8 = "8"
    U16 = "16"
    FLOAT = "32"


# Parameter Models for validation and documentation
class CreateSceneParams(BaseModel):
    """Parameters for creating a new scene."""

    name: str = Field(..., description="Name of the scene")
    use_nodes: bool = Field(False, description="Use compositing nodes")
    use_gravity: bool = Field(True, description="Use gravity")
    gravity: Tuple[float, float, float] = Field((0, 0, -9.81), description="Gravity vector")
    unit_system: UnitSystem = Field(UnitSystem.METRIC, description="Unit system")
    unit_length: UnitLength = Field(UnitLength.METERS, description="Unit length")
    unit_mass: UnitMass = Field(UnitMass.KILOGRAMS, description="Unit mass")
    unit_time: UnitTime = Field(UnitTime.SECONDS, description="Unit time")
    unit_temperature: UnitTemperature = Field(
        UnitTemperature.CELSIUS, description="Unit temperature"
    )


class SetActiveSceneParams(BaseModel):
    """Parameters for setting the active scene."""

    scene_name: str = Field(..., description="Name of the scene to activate")


class LinkObjectToSceneParams(BaseModel):
    """Parameters for linking an object to a scene."""

    object_name: str = Field(..., description="Name of the object to link")
    scene_name: str = Field(..., description="Name of the scene to link to")


class CreateCollectionParams(BaseModel):
    """Parameters for creating a collection."""

    collection_name: str = Field(..., description="Name of the collection")


class AddToCollectionParams(BaseModel):
    """Parameters for adding an object to a collection."""

    collection_name: str = Field(..., description="Name of the collection")
    object_name: str = Field(..., description="Name of the object to add")


class SetActiveCollectionParams(BaseModel):
    """Parameters for setting the active collection."""

    collection_name: str = Field(..., description="Name of the collection to activate")


class SetViewLayerParams(BaseModel):
    """Parameters for setting the view layer."""

    layer_name: str = Field(..., description="Name of the view layer")


class SetupLightingParams(BaseModel):
    """Parameters for setting up lighting."""

    light_type: LightType = Field(LightType.SUN, description="Type of light")
    location: Tuple[float, float, float] = Field((0, 0, 5), description="Light location")
    rotation: Tuple[float, float, float] = Field((0, 0, 0), description="Light rotation")
    energy: float = Field(1.0, gt=0.0, description="Light energy")
    color: Tuple[float, float, float] = Field((1, 1, 1), description="Light color")
    use_shadow: bool = Field(True, description="Use shadows")
    shadow_soft_size: float = Field(0.25, gt=0.0, description="Shadow soft size")


class SetupCameraParams(BaseModel):
    """Parameters for setting up a camera."""

    location: Tuple[float, float, float] = Field((0, -5, 2), description="Camera location")
    rotation: Tuple[float, float, float] = Field((1.0, 0, 0), description="Camera rotation")
    focal_length: float = Field(50.0, gt=0.0, description="Focal length")
    sensor_width: float = Field(32.0, gt=0.0, description="Sensor width")
    sensor_height: float = Field(18.0, gt=0.0, description="Sensor height")
    use_dof: bool = Field(False, description="Use depth of field")
    focus_distance: float = Field(10.0, gt=0.0, description="Focus distance")
    aperture_fstop: float = Field(2.8, gt=0.0, description="Aperture f-stop")


class SetRenderSettingsParams(BaseModel):
    """Parameters for setting render settings."""

    resolution_x: int = Field(1920, gt=0, description="Resolution X")
    resolution_y: int = Field(1080, gt=0, description="Resolution Y")
    resolution_percentage: int = Field(100, ge=1, le=100, description="Resolution percentage")
    render_engine: RenderEngine = Field(RenderEngine.EEVEE, description="Render engine")
    device: DeviceType = Field(DeviceType.CPU, description="Device type")
    samples: int = Field(64, gt=0, description="Number of samples")
    use_denoising: bool = Field(True, description="Use denoising")
    use_motion_blur: bool = Field(False, description="Use motion blur")
    use_transparent: bool = Field(False, description="Use transparent background")
    file_format: FileFormat = Field(FileFormat.PNG, description="File format")
    color_mode: ColorMode = Field(ColorMode.RGBA, description="Color mode")
    color_depth: ColorDepth = Field(ColorDepth.U8, description="Color depth")
    compression: int = Field(15, ge=0, le=100, description="Compression")


class SetWorldSettingsParams(BaseModel):
    """Parameters for setting world settings."""

    use_nodes: bool = Field(True, description="Use world nodes")
    background_color: Tuple[float, float, float] = Field(
        (0.05, 0.05, 0.05), description="Background color"
    )
    strength: float = Field(1.0, gt=0.0, description="World strength")
    use_ambient_occlusion: bool = Field(True, description="Use ambient occlusion")
    ao_factor: float = Field(1.0, gt=0.0, description="AO factor")
    ao_distance: float = Field(1.0, gt=0.0, description="AO distance")
    use_environment_lighting: bool = Field(True, description="Use environment lighting")
    environment_energy: float = Field(1.0, gt=0.0, description="Environment energy")
    environment_color: Tuple[float, float, float] = Field(
        (1, 1, 1), description="Environment color"
    )


class SetUnitsParams(BaseModel):
    """Parameters for setting units."""

    unit_system: UnitSystem = Field(UnitSystem.METRIC, description="Unit system")
    unit_length: UnitLength = Field(UnitLength.METERS, description="Unit length")
    unit_mass: UnitMass = Field(UnitMass.KILOGRAMS, description="Unit mass")
    unit_time: UnitTime = Field(UnitTime.SECONDS, description="Unit time")
    unit_temperature: UnitTemperature = Field(
        UnitTemperature.CELSIUS, description="Unit temperature"
    )


class SetGravityParams(BaseModel):
    """Parameters for setting gravity."""

    gravity: Tuple[float, float, float] = Field((0, 0, -9.81), description="Gravity vector")
    use_gravity: bool = Field(True, description="Use gravity")


class SetFrameRangeParams(BaseModel):
    """Parameters for setting frame range."""

    start_frame: int = Field(1, description="Start frame")
    end_frame: int = Field(250, description="End frame")
    current_frame: int = Field(1, description="Current frame")


class SetActiveObjectParams(BaseModel):
    """Parameters for setting the active object."""

    object_name: str = Field(..., description="Name of the object to activate")


class SelectObjectsParams(BaseModel):
    """Parameters for selecting objects."""

    object_names: List[str] = Field(..., description="Names of objects to select")
    extend: bool = Field(False, description="Extend selection")
    deselect_all: bool = Field(False, description="Deselect all first")


class FrameRangeParams(BaseModel):
    """Parameters for frame range settings."""

    frame_start: int = Field(1, description="Start frame")
    frame_end: int = Field(250, description="End frame")
    frame_step: int = Field(1, description="Frame step")
    fps: int = Field(24, description="Frames per second")
    fps_base: float = Field(1.0, description="FPS base")


# Tool Definitions
# Note: The actual tool functions are defined in the handlers and registered with @app.tool decorators.
# This module provides parameter models and enums for documentation and validation purposes.

# The following tools are available (registered in handlers):
# - create_scene: Create a new scene
# - list_scenes: List all scenes
# - clear_scene: Clear all objects from current scene
# - set_active_scene: Set the active scene
# - link_object_to_scene: Link an object to a scene
# - create_collection: Create a new collection
# - add_to_collection: Add an object to a collection
# - set_active_collection: Set the active collection
# - set_view_layer: Set the active view layer
# - setup_lighting: Setup lighting for the scene
# - setup_camera: Setup camera for the scene
# - set_render_settings: Configure render settings


def register() -> None:
    """Register all scene tools."""
    # Tools are already registered via @app.tool decorators in handlers
    pass


# Auto-register tools when module is imported
register()
