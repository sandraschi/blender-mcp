"""Integration tests for Blender executor functionality."""

import pytest
import json
from pathlib import Path
from blender_mcp.utils.blender_executor import BlenderExecutor
from blender_mcp.exceptions import BlenderNotFoundError, BlenderScriptError


class TestBlenderExecutorIntegration:
    """Integration tests for BlenderExecutor with real Blender."""

    @pytest.mark.integration
    @pytest.mark.requires_blender
    def test_executor_creation(self, blender_executable: str):
        """Test that BlenderExecutor can be created with real Blender."""
        executor = BlenderExecutor(blender_executable)
        assert executor is not None
        assert str(executor.blender_path) == blender_executable

    @pytest.mark.integration
    @pytest.mark.requires_blender
    @pytest.mark.asyncio
    async def test_basic_script_execution(self, blender_executable: str):
        """Test basic script execution in Blender."""
        executor = BlenderExecutor(blender_executable)

        script = """
import bpy
print("Hello from Blender integration test")
"""

        result = await executor.execute_script(script)

        assert isinstance(result, str)
        assert "Hello from Blender integration test" in result

    @pytest.mark.integration
    @pytest.mark.requires_blender
    @pytest.mark.asyncio
    async def test_scene_creation_script(self, blender_executable: str):
        """Test scene creation script execution."""
        executor = BlenderExecutor(blender_executable)

        script = """
import bpy

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create objects
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TestCube"

bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3, 0, 0))
sphere = bpy.context.active_object
sphere.name = "TestSphere"

print(f"Created {len(bpy.data.objects)} objects")
"""

        result = await executor.execute_script(script)

        assert isinstance(result, str)
        assert "Created 2 objects" in result

    @pytest.mark.integration
    @pytest.mark.requires_blender
    @pytest.mark.asyncio
    async def test_material_creation(self, blender_executable: str):
        """Test material creation and assignment."""
        executor = BlenderExecutor(blender_executable)

        script = """
import bpy

# Clear scene and create object
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object

# Create material
material = bpy.data.materials.new(name="TestMaterial")
material.use_nodes = True

# Set base color
nodes = material.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs["Base Color"].default_value = (1, 0, 0, 1)  # Red

# Assign material
cube.data.materials.append(material)

print(f"Created material: {material.name}")
print(f"Assigned to object: {cube.name}")
"""

        result = await executor.execute_script(script)

        assert isinstance(result, str)
        assert "Created material: TestMaterial" in result

    @pytest.mark.integration
    @pytest.mark.requires_blender
    @pytest.mark.asyncio
    async def test_script_error_handling(self, blender_executable: str):
        """Test error handling when script has syntax errors."""
        executor = BlenderExecutor(blender_executable)

        # Script with syntax error
        script = """
import bpy
# This will cause a syntax error
print("This is fine"
print("This won't execute")
"""

        # Should raise BlenderScriptError due to syntax error
        with pytest.raises(BlenderScriptError):
            await executor.execute_script(script)

    @pytest.mark.integration
    @pytest.mark.requires_blender
    @pytest.mark.asyncio
    async def test_complex_scene_operations(self, blender_executable: str):
        """Test complex scene operations."""
        executor = BlenderExecutor(blender_executable)

        script = """
import bpy
import json

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create multiple objects in a pattern
objects_created = []
for x in range(-1, 2):
    for y in range(-1, 2):
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=(x*2, y*2, 0))
        cube = bpy.context.active_object
        cube.name = f"Cube_{x}_{y}"
        objects_created.append(cube.name)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
light = bpy.context.active_object
light.name = "SunLight"

# Add camera
bpy.ops.object.camera_add(location=(8, -8, 6))
camera = bpy.context.active_object
camera.name = "MainCamera"

# Create materials
for i, obj_name in enumerate(objects_created[:3]):  # Just first 3 for speed
    obj = bpy.data.objects[obj_name]
    material = bpy.data.materials.new(name=f"Material_{i}")
    material.use_nodes = True

    # Set different colors
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        colors = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)]  # RGB
        principled.inputs["Base Color"].default_value = colors[i % len(colors)]

    obj.data.materials.append(material)

scene_info = {
    "total_objects": len(bpy.data.objects),
    "meshes": len([obj for obj in bpy.data.objects if obj.type == 'MESH']),
    "lights": len([obj for obj in bpy.data.objects if obj.type == 'LIGHT']),
    "cameras": len([obj for obj in bpy.data.objects if obj.type == 'CAMERA']),
    "materials": len(bpy.data.materials)
}

print(json.dumps(scene_info))
"""

        result = await executor.execute_script(script)

        assert isinstance(result, str)

        # Parse the JSON output from the result string
        output_lines = result.strip().split("\n")
        json_line = None
        for line in output_lines:
            if line.strip().startswith("{"):
                json_line = line.strip()
                break

        assert json_line is not None, "Expected JSON output not found"

        scene_info = json.loads(json_line)
        assert scene_info["total_objects"] >= 11  # 9 cubes + light + camera
        assert scene_info["meshes"] >= 9  # 9 cubes
        assert scene_info["lights"] >= 1
        assert scene_info["cameras"] >= 1

    @pytest.mark.integration
    @pytest.mark.requires_blender
    @pytest.mark.asyncio
    async def test_timeout_handling(self, blender_executable: str):
        """Test timeout handling for long-running scripts."""
        executor = BlenderExecutor(blender_executable)

        # Script that should take longer than timeout
        script = """
import bpy
import time

# Simulate long operation
time.sleep(10)  # This should timeout
print("This should not print")
"""

        # Should raise BlenderScriptError due to timeout
        with pytest.raises(BlenderScriptError):
            await executor.execute_script(script, timeout=5)  # Short timeout

    @pytest.mark.integration
    @pytest.mark.requires_blender
    @pytest.mark.asyncio
    async def test_file_output_operations(self, blender_executable: str, temp_dir: Path):
        """Test operations that create file outputs."""
        executor = BlenderExecutor(blender_executable)

        output_path = temp_dir / "test_render.png"

        script = (
            '''
import bpy

# Clear scene and create simple object
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Add material
material = bpy.data.materials.new(name="TestMaterial")
material.use_nodes = True
bpy.context.active_object.data.materials.append(material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))

# Add camera
bpy.ops.object.camera_add(location=(7, -7, 5))
camera = bpy.context.active_object
camera.rotation_euler = (1.0, 0.0, 0.8)
bpy.context.scene.camera = camera

# Set render settings
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 600
bpy.context.scene.render.filepath = r"'''
            + str(output_path)
            + """"
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Render
bpy.ops.render.render(write_still=True)

print(f"Rendered to: {output_path}")
"""
        )

        result = await executor.execute_script(script)

        assert isinstance(result, str)
        assert "Rendered to:" in result

        # Check if file was actually created
        assert output_path.exists(), "Render output file was not created"
        assert output_path.stat().st_size > 0, "Render output file is empty"


class TestBlenderExecutorErrorCases:
    """Test error cases for BlenderExecutor."""

    @pytest.mark.integration
    def test_executor_creation_no_blender(self):
        """Test executor creation when Blender is not available."""
        with pytest.raises(BlenderNotFoundError):
            BlenderExecutor("nonexistent_blender_path")

    @pytest.mark.integration
    @pytest.mark.requires_blender
    @pytest.mark.asyncio
    async def test_invalid_script_execution(self, blender_executable: str):
        """Test execution of invalid Python script."""
        executor = BlenderExecutor(blender_executable)

        # Script that will cause a runtime error
        script = """
import bpy
# This will cause an AttributeError
nonexistent_object.some_method()
"""

        # Should raise BlenderScriptError due to invalid script
        with pytest.raises(BlenderScriptError):
            await executor.execute_script(script)
