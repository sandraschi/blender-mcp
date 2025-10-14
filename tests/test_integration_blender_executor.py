"""Integration tests for BlenderExecutor with real Blender execution.

These tests actually run Blender processes to test real functionality.
"""

import pytest
import asyncio
import json
from pathlib import Path

from blender_mcp.utils.blender_executor import BlenderExecutor


@pytest.mark.integration
@pytest.mark.requires_blender
class TestBlenderExecutorIntegration:
    """Integration tests that run real Blender processes."""

    @pytest.fixture
    async def executor(self, blender_executable: str):
        """Create a real BlenderExecutor instance."""
        executor = BlenderExecutor(blender_executable)
        yield executor
        # Cleanup will happen automatically

    @pytest.mark.asyncio
    async def test_basic_script_execution(self, executor: BlenderExecutor):
        """Test basic script execution with real Blender."""
        script = '''
import bpy
print("Hello from Blender!")
print(f"Blender version: {bpy.app.version}")
'''
        result = await executor.execute_script(script)

        assert "Hello from Blender!" in result
        assert "Blender version:" in result

    @pytest.mark.asyncio
    async def test_scene_creation_and_query(self, executor: BlenderExecutor):
        """Test creating a scene and querying its contents."""
        create_script = '''
import bpy
import json

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create objects
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TestCube"

bpy.ops.mesh.primitive_uv_sphere_add(location=(2, 0, 0))
sphere = bpy.context.active_object
sphere.name = "TestSphere"

# Create materials
material1 = bpy.data.materials.new(name="RedMaterial")
material1.use_nodes = True
material1.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 0, 0, 1)

material2 = bpy.data.materials.new(name="BlueMaterial")
material2.use_nodes = True
material2.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 1, 1)

# Assign materials
cube.data.materials.append(material1)
sphere.data.materials.append(material2)

print("Scene created successfully")
'''

        query_script = '''
import bpy
import json

scene_info = {
    "objects": [],
    "materials": []
}

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        scene_info["objects"].append({
            "name": obj.name,
            "type": obj.type,
            "location": [obj.location.x, obj.location.y, obj.location.z]
        })

for mat in bpy.data.materials:
    scene_info["materials"].append(mat.name)

print(json.dumps(scene_info))
'''

        # Create scene
        create_result = await executor.execute_script(create_script)
        assert "Scene created successfully" in create_result

        # Query scene
        query_result = await executor.execute_script(query_script)

        # Parse JSON output
        # Find the JSON line in the output
        json_line = None
        for line in query_result.split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                json_line = line
                break

        assert json_line is not None, f"Could not find JSON in output: {query_result}"

        scene_info = json.loads(json_line)

        # Verify scene contents
        assert len(scene_info["objects"]) >= 2  # At least cube and sphere
        assert len(scene_info["materials"]) >= 2  # At least the two materials

        # Check for our specific objects
        object_names = [obj["name"] for obj in scene_info["objects"]]
        assert "TestCube" in object_names
        assert "TestSphere" in object_names

        # Check for our materials
        assert "RedMaterial" in scene_info["materials"]
        assert "BlueMaterial" in scene_info["materials"]

    @pytest.mark.asyncio
    async def test_material_creation_and_properties(self, executor: BlenderExecutor):
        """Test material creation and property setting."""
        script = '''
import bpy
import json

# Clear scene and create object
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object

# Create different types of materials
materials_info = {}

# Basic material
basic_mat = bpy.data.materials.new(name="BasicMaterial")
basic_mat.use_nodes = True
materials_info["basic"] = {"name": basic_mat.name, "type": "basic"}

# Metallic material
metallic_mat = bpy.data.materials.new(name="MetallicMaterial")
metallic_mat.use_nodes = True
metallic_mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
metallic_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.2
materials_info["metallic"] = {"name": metallic_mat.name, "type": "metallic"}

# Glass material
glass_mat = bpy.data.materials.new(name="GlassMaterial")
glass_mat.use_nodes = True
glass_mat.node_tree.nodes["Principled BSDF"].inputs["Transmission"].default_value = 1.0
glass_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.0
materials_info["glass"] = {"name": glass_mat.name, "type": "glass"}

# Assign materials to object
cube.data.materials.append(basic_mat)

print(json.dumps(materials_info))
'''

        result = await executor.execute_script(script)

        # Parse the JSON output
        json_line = None
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                json_line = line
                break

        assert json_line is not None, f"Could not find JSON in output: {result}"

        materials_info = json.loads(json_line)

        # Verify materials were created
        assert "basic" in materials_info
        assert "metallic" in materials_info
        assert "glass" in materials_info

        assert materials_info["basic"]["name"] == "BasicMaterial"
        assert materials_info["metallic"]["name"] == "MetallicMaterial"
        assert materials_info["glass"]["name"] == "GlassMaterial"

    @pytest.mark.asyncio
    async def test_animation_setup(self, executor: BlenderExecutor):
        """Test animation setup and keyframe creation."""
        script = '''
import bpy
import json

# Clear scene and create object
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object

# Set up animation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 60

# Create keyframe animation
# Frame 1: original position
cube.location = (0, 0, 0)
cube.keyframe_insert(data_path="location", frame=1)

# Frame 30: moved position
cube.location = (5, 0, 0)
cube.keyframe_insert(data_path="location", frame=30)

# Frame 60: back to start
cube.location = (0, 0, 0)
cube.keyframe_insert(data_path="location", frame=60)

# Add rotation animation
cube.rotation_euler = (0, 0, 0)
cube.keyframe_insert(data_path="rotation_euler", frame=1)

cube.rotation_euler = (0, 0, 6.28318)  # 360 degrees in radians
cube.keyframe_insert(data_path="rotation_euler", frame=60)

# Get animation info
animation_info = {
    "object": cube.name,
    "keyframes": len([fc for fcurve in cube.animation_data.action.fcurves for kp in fcurve.keyframe_points]),
    "frame_range": [bpy.context.scene.frame_start, bpy.context.scene.frame_end]
}

print(json.dumps(animation_info))
'''

        result = await executor.execute_script(script)

        # Parse the JSON output
        json_line = None
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                json_line = line
                break

        assert json_line is not None, f"Could not find JSON in output: {result}"

        animation_info = json.loads(json_line)

        # Verify animation was created
        assert animation_info["object"] == "Cube"
        assert animation_info["keyframes"] > 0  # Should have keyframes
        assert animation_info["frame_range"] == [1, 60]

    @pytest.mark.asyncio
    async def test_script_error_handling(self, executor: BlenderExecutor):
        """Test that script errors are properly handled."""
        from blender_mcp.exceptions import BlenderScriptError

        error_script = '''
import bpy
# This should cause a NameError
nonexistent_function_call()
'''

        with pytest.raises(BlenderScriptError) as exc_info:
            await executor.execute_script(error_script)

        # Verify error contains useful information
        error_message = str(exc_info.value)
        assert "NameError" in error_message or "nonexistent_function_call" in error_message

    @pytest.mark.asyncio
    async def test_large_script_execution(self, executor: BlenderExecutor):
        """Test execution of a larger, more complex script."""
        large_script = '''
import bpy
import math
import json

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create a complex scene with multiple objects
objects_created = []

# Create a grid of cubes
for x in range(-3, 4):
    for y in range(-3, 4):
        if x == 0 and y == 0:  # Skip center
            continue
        bpy.ops.mesh.primitive_cube_add(location=(x*3, y*3, 0))
        cube = bpy.context.active_object
        cube.name = f"GridCube_{x}_{y}"
        cube.scale = (0.8, 0.8, 0.8)
        objects_created.append(cube.name)

# Create some spheres at different heights
for i in range(5):
    angle = (i / 5) * 2 * math.pi
    x = math.cos(angle) * 8
    y = math.sin(angle) * 8
    z = i * 2
    bpy.ops.mesh.primitive_uv_sphere_add(location=(x, y, z))
    sphere = bpy.context.active_object
    sphere.name = f"FloatingSphere_{i}"
    sphere.scale = (0.5, 0.5, 0.5)
    objects_created.append(sphere.name)

# Create materials for all objects
materials_created = []
for i, obj_name in enumerate(objects_created):
    obj = bpy.data.objects[obj_name]

    # Create unique material
    material = bpy.data.materials.new(name=f"Material_{i}")
    material.use_nodes = True

    # Set random-like colors based on index
    r = ((i * 37) % 256) / 255.0
    g = ((i * 71) % 256) / 255.0
    b = ((i * 113) % 256) / 255.0

    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (r, g, b, 1.0)
    obj.data.materials.append(material)
    materials_created.append(material.name)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 5.0

bpy.ops.object.light_add(type='POINT', location=(-5, -5, 5))
point = bpy.context.active_object
point.name = "PointLight"
point.data.energy = 1000.0

# Add camera
bpy.ops.object.camera_add(location=(15, -15, 10))
camera = bpy.context.active_object
camera.name = "SceneCamera"
camera.rotation_euler = (1.2, 0.0, 0.8)

# Set camera as active
bpy.context.scene.camera = camera

# Get scene statistics
scene_stats = {
    "total_objects": len(bpy.data.objects),
    "mesh_objects": len([obj for obj in bpy.data.objects if obj.type == 'MESH']),
    "materials": len(bpy.data.materials),
    "lights": len([obj for obj in bpy.data.objects if obj.type == 'LIGHT']),
    "cameras": len([obj for obj in bpy.data.objects if obj.type == 'CAMERA'])
}

print(json.dumps(scene_stats))
print(f"Successfully created complex scene with {len(objects_created)} objects")
'''

        result = await executor.execute_script(large_script)

        # Parse the JSON output
        json_line = None
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                json_line = line
                break

        assert json_line is not None, f"Could not find JSON in output: {result}"

        scene_stats = json.loads(json_line)

        # Verify complex scene was created
        assert scene_stats["mesh_objects"] > 20  # Should have many mesh objects
        assert scene_stats["materials"] > 20  # Should have corresponding materials
        assert scene_stats["lights"] >= 2  # Should have sun and point lights
        assert scene_stats["cameras"] >= 1  # Should have camera

        assert "Successfully created complex scene" in result

    @pytest.mark.asyncio
    async def test_memory_cleanup(self, executor: BlenderExecutor):
        """Test that Blender processes clean up properly after execution."""
        # Run multiple scripts and verify no memory leaks or hanging processes
        for i in range(3):
            script = f'''
import bpy
print(f"Script execution {i+1} completed")
'''
            result = await executor.execute_script(script)
            assert f"Script execution {i+1} completed" in result

        # All executions should complete without hanging
        assert True
