"""Test utilities and helpers for Blender MCP tests.

This module provides utilities for test setup, teardown, and common test operations.
"""

import os
import sys
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator
from contextlib import contextmanager


class TestBlenderHelper:
    """Helper class for Blender-related test operations."""

    def __init__(self, blender_executable: str):
        self.blender_executable = blender_executable
        from blender_mcp.utils.blender_executor import BlenderExecutor
        self.executor = BlenderExecutor(blender_executable)

    async def execute_script_safe(self, script: str, timeout: int = 60) -> str:
        """Execute a script with error handling."""
        try:
            return await asyncio.wait_for(
                self.executor.execute_script(script),
                timeout=timeout
            )
        except Exception as e:
            return f"ERROR: {str(e)}"

    async def create_test_scene(self, scene_name: str = "TestScene") -> bool:
        """Create a basic test scene."""
        script = f'''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.name = "{scene_name}"
print(f"Created test scene: {scene_name}")
'''
        result = await self.execute_script_safe(script)
        return "Created test scene" in result

    async def clear_scene(self) -> bool:
        """Clear the current scene."""
        script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
print("Scene cleared")
'''
        result = await self.execute_script_safe(script)
        return "Scene cleared" in result

    async def get_scene_info(self) -> Dict[str, Any]:
        """Get information about the current scene."""
        script = '''
import bpy
import json

scene_info = {
    "scene_name": bpy.context.scene.name,
    "objects": len(bpy.data.objects),
    "meshes": len(bpy.data.meshes),
    "materials": len(bpy.data.materials),
    "lights": len([obj for obj in bpy.data.objects if obj.type == 'LIGHT']),
    "cameras": len([obj for obj in bpy.data.objects if obj.type == 'CAMERA']),
    "object_names": [obj.name for obj in bpy.data.objects if obj.type in ['MESH', 'LIGHT', 'CAMERA']]
}

print(json.dumps(scene_info))
'''
        result = await self.execute_script_safe(script)

        try:
            # Extract JSON from result
            import json
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return {"error": "Could not parse scene info", "raw_result": result}

    async def create_basic_cube(self, name: str = "TestCube", location: tuple = (0, 0, 0)) -> bool:
        """Create a basic cube."""
        script = f'''
import bpy
bpy.ops.mesh.primitive_cube_add(location={location})
cube = bpy.context.active_object
cube.name = "{name}"
print(f"Created cube: {name}")
'''
        result = await self.execute_script_safe(script)
        return f"Created cube: {name}" in result

    async def create_basic_material(self, name: str = "TestMaterial", color: tuple = (1, 0, 0, 1)) -> bool:
        """Create a basic material."""
        script = f'''
import bpy
material = bpy.data.materials.new(name="{name}")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = {color}
print(f"Created material: {name}")
'''
        result = await self.execute_script_safe(script)
        return f"Created material: {name}" in result


@contextmanager
def temp_directory(prefix: str = "blender_test_") -> Generator[Path, None, None]:
    """Context manager for temporary directories."""
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@contextmanager
def temp_file(suffix: str = "", prefix: str = "blender_test_") -> Generator[Path, None, None]:
    """Context manager for temporary files."""
    temp_file = Path(tempfile.mktemp(suffix=suffix, prefix=prefix))
    try:
        yield temp_file
    finally:
        if temp_file.exists():
            temp_file.unlink(missing_ok=True)


def find_blender_executable() -> Optional[str]:
    """Find a Blender executable in common locations."""
    from .conftest import DEFAULT_BLENDER_PATHS

    # Check environment variable
    env_path = os.environ.get('BLENDER_EXECUTABLE')
    if env_path and Path(env_path).exists():
        return env_path

    # Check common paths
    for path in DEFAULT_BLENDER_PATHS:
        if Path(path).exists():
            return path

        # Try without .exe on Windows
        if path.endswith('.exe') and Path(path[:-4]).exists():
            return path[:-4]

    return None


def is_blender_available() -> bool:
    """Check if Blender is available for testing."""
    return find_blender_executable() is not None


def skip_if_no_blender():
    """Skip test if Blender is not available."""
    if not is_blender_available():
        import pytest
        pytest.skip("Blender executable not found")


class TestDataBuilder:
    """Builder for creating test data and scenes."""

    def __init__(self, blender_helper: TestBlenderHelper):
        self.helper = blender_helper
        self.created_objects: List[str] = []
        self.created_materials: List[str] = []

    async def create_grid_of_cubes(self, width: int = 5, height: int = 5, spacing: float = 2.0) -> bool:
        """Create a grid of cubes."""
        script = f'''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)

created_objects = []
for x in range({width}):
    for y in range({height}):
        location = (x * {spacing}, y * {spacing}, 0)
        bpy.ops.mesh.primitive_cube_add(location=location)
        cube = bpy.context.active_object
        cube.name = f"GridCube_{x}_{y}"
        created_objects.append(cube.name)

print(f"Created grid of {{len(created_objects)}} cubes")
'''
        result = await self.helper.execute_script_safe(script)
        success = f"Created grid of {width * height} cubes" in result

        if success:
            for x in range(width):
                for y in range(height):
                    self.created_objects.append(f"GridCube_{x}_{y}")

        return success

    async def create_material_set(self, count: int = 5) -> bool:
        """Create a set of different materials."""
        script = f'''
import bpy
import random

materials_created = []
for i in range({count}):
    material = bpy.data.materials.new(name=f"TestMaterial_{{i:02d}}")
    material.use_nodes = True

    # Random color
    color = (
        random.random(),
        random.random(),
        random.random(),
        1.0
    )
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = color
    materials_created.append(material.name)

print(f"Created {{len(materials_created)}} materials")
'''
        result = await self.helper.execute_script_safe(script)
        success = f"Created {count} materials" in result

        if success:
            for i in range(count):
                self.created_materials.append(f"TestMaterial_{i:02d}")

        return success

    async def assign_materials_to_objects(self) -> bool:
        """Assign created materials to created objects."""
        if not self.created_materials or not self.created_objects:
            return False

        script = f'''
import bpy

objects = {self.created_objects}
materials = {self.created_materials}

assignments = 0
for i, obj_name in enumerate(objects):
    if obj_name in bpy.data.objects:
        obj = bpy.data.objects[obj_name]
        mat_name = materials[i % len(materials)]
        if mat_name in bpy.data.materials:
            material = bpy.data.materials[mat_name]
            obj.data.materials.append(material)
            assignments += 1

print(f"Assigned materials to {{assignments}} objects")
'''
        result = await self.helper.execute_script_safe(script)
        return "Assigned materials to" in result

    async def cleanup(self) -> bool:
        """Clean up created test data."""
        result = await self.helper.clear_scene()
        self.created_objects.clear()
        self.created_materials.clear()
        return result


class PerformanceTimer:
    """Timer for measuring performance."""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.measurements: List[float] = []

    def start(self):
        """Start timing."""
        self.start_time = asyncio.get_event_loop().time()

    async def stop(self) -> float:
        """Stop timing and return duration."""
        self.end_time = asyncio.get_event_loop().time()
        duration = self.end_time - self.start_time
        self.measurements.append(duration)
        return duration

    def reset(self):
        """Reset the timer."""
        self.start_time = None
        self.end_time = None
        self.measurements.clear()

    def get_average(self) -> float:
        """Get average duration."""
        if not self.measurements:
            return 0.0
        return sum(self.measurements) / len(self.measurements)

    def get_total(self) -> float:
        """Get total duration of all measurements."""
        return sum(self.measurements)

    def get_min(self) -> float:
        """Get minimum duration."""
        return min(self.measurements) if self.measurements else 0.0

    def get_max(self) -> float:
        """Get maximum duration."""
        return max(self.measurements) if self.measurements else 0.0


async def run_with_timeout(coro, timeout: float = 30.0):
    """Run a coroutine with a timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")


def get_test_resource_path(resource_name: str) -> Path:
    """Get path to a test resource file."""
    test_dir = Path(__file__).parent
    return test_dir / "resources" / resource_name


def create_test_resources_dir():
    """Create test resources directory if it doesn't exist."""
    test_dir = Path(__file__).parent
    resources_dir = test_dir / "resources"
    resources_dir.mkdir(exist_ok=True)
    return resources_dir
