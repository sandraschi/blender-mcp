"""Pytest configuration and fixtures for Blender MCP tests.

This module provides fixtures and configuration for running tests with real Blender instances.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Optional

# Import test utilities
from . import DEFAULT_BLENDER_PATHS, BLENDER_EXECUTABLE_ENV, TEST_TIMEOUT


def find_blender_executable() -> Optional[str]:
    """Find a working Blender executable."""
    # Check environment variable first
    env_path = os.environ.get(BLENDER_EXECUTABLE_ENV)
    if env_path and Path(env_path).exists():
        return env_path

    # Try default paths
    for path in DEFAULT_BLENDER_PATHS:
        if Path(path).exists():
            return path
        # Try without .exe extension on Windows
        if path.endswith('.exe') and Path(path[:-4]).exists():
            return path[:-4]

    return None


@pytest.fixture(scope="session")
def blender_executable() -> str:
    """Find and return the Blender executable path."""
    executable = find_blender_executable()
    if not executable:
        pytest.skip("Blender executable not found. Please install Blender or set BLENDER_EXECUTABLE environment variable.")
    return executable


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for the test session."""
    temp_path = Path(tempfile.mkdtemp(prefix="blender_mcp_test_"))
    yield temp_path
    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file for individual tests."""
    def _temp_file(suffix: str = "") -> Path:
        return Path(tempfile.mktemp(dir=temp_dir, suffix=suffix))
    return _temp_file


@pytest.fixture(scope="session")
def test_config(blender_executable: str, temp_dir: Path) -> dict:
    """Test configuration dictionary."""
    return {
        "blender_executable": blender_executable,
        "temp_dir": temp_dir,
        "timeout": TEST_TIMEOUT,
        "headless": True,
        "test_data_dir": temp_dir / "test_data",
        "output_dir": temp_dir / "output"
    }


@pytest.fixture(autouse=True)
def setup_test_environment(test_config: dict):
    """Setup test environment before each test."""
    # Ensure output directories exist
    test_config["test_data_dir"].mkdir(exist_ok=True)
    test_config["output_dir"].mkdir(exist_ok=True)

    # Set environment variables for tests
    os.environ["BLENDER_EXECUTABLE"] = test_config["blender_executable"]

    yield

    # Cleanup after test
    pass


# Custom markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "requires_blender: marks tests that require a real Blender installation")


@pytest.fixture
def skip_if_no_blender(blender_executable: str):
    """Skip test if Blender is not available."""
    if not blender_executable:
        pytest.skip("Blender not available")


# Test utilities
class BlenderTestHelper:
    """Helper class for Blender-related test operations."""

    @staticmethod
    def create_basic_scene_script() -> str:
        """Create a basic Blender scene setup script."""
        return '''
import bpy
import sys

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create a basic scene
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TestCube"

# Add a material
material = bpy.data.materials.new(name="TestMaterial")
material.use_nodes = True
cube.data.materials.append(material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))

# Add camera
bpy.ops.object.camera_add(location=(7, -7, 5))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0.0, 0.8)

print("Basic scene created successfully")
'''

    @staticmethod
    def create_complex_scene_script() -> str:
        """Create a complex scene with multiple objects."""
        return '''
import bpy
import sys

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create multiple objects
objects_created = []

# Create cubes in a grid
for x in range(-2, 3):
    for y in range(-2, 3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x*3, y*3, 0))
        cube = bpy.context.active_object
        cube.name = f"Cube_{x}_{y}"
        objects_created.append(cube.name)

# Create spheres
for i in range(3):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(i*2-2, 5, 1))
    sphere = bpy.context.active_object
    sphere.name = f"Sphere_{i}"
    objects_created.append(sphere.name)

# Create materials for each object
for obj_name in objects_created:
    obj = bpy.data.objects[obj_name]
    material = bpy.data.materials.new(name=f"Material_{obj_name}")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (
        (hash(obj_name) % 256) / 255.0,
        (hash(obj_name + "r") % 256) / 255.0,
        (hash(obj_name + "g") % 256) / 255.0,
        1.0
    )
    obj.data.materials.append(material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
bpy.ops.object.light_add(type='POINT', location=(-5, -5, 5))

# Add camera with better positioning
bpy.ops.object.camera_add(location=(15, -15, 10))
camera = bpy.context.active_object
camera.rotation_euler = (1.2, 0.0, 0.8)

print(f"Complex scene created with {len(objects_created)} objects")
'''

    @staticmethod
    def get_scene_info_script() -> str:
        """Script to get information about the current scene."""
        return '''
import bpy
import json

scene_info = {
    "objects": [],
    "materials": [],
    "lights": [],
    "cameras": []
}

for obj in bpy.data.objects:
    obj_info = {
        "name": obj.name,
        "type": obj.type,
        "location": [obj.location.x, obj.location.y, obj.location.z]
    }
    scene_info["objects"].append(obj_info)

    if obj.type == 'LIGHT':
        scene_info["lights"].append(obj.name)
    elif obj.type == 'CAMERA':
        scene_info["cameras"].append(obj.name)

for mat in bpy.data.materials:
    scene_info["materials"].append(mat.name)

print(json.dumps(scene_info))
'''

    @staticmethod
    def render_scene_script(output_path: str, resolution_x: int = 1920, resolution_y: int = 1080) -> str:
        """Script to render the current scene."""
        return f'''
import bpy

# Set render settings
bpy.context.scene.render.resolution_x = {resolution_x}
bpy.context.scene.render.resolution_y = {resolution_y}
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.filepath = r"{output_path}"
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Set camera as active camera if available
cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
if cameras:
    bpy.context.scene.camera = cameras[0]

# Render
bpy.ops.render.render(write_still=True)
print(f"Rendered scene to: {output_path}")
'''


@pytest.fixture
def blender_test_helper():
    """Fixture providing BlenderTestHelper instance."""
    return BlenderTestHelper()
