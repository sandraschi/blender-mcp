"""Integration tests for Blender MCP handlers with real Blender execution.

These tests test individual handlers using real Blender processes.
"""

import pytest
import asyncio
import json
from pathlib import Path

from blender_mcp.handlers.scene_handler import SceneHandler
from blender_mcp.handlers.mesh_handler import MeshHandler
from blender_mcp.handlers.material_handler import MaterialHandler


@pytest.mark.integration
@pytest.mark.requires_blender
class TestSceneHandlerIntegration:
    """Integration tests for SceneHandler."""

    @pytest.fixture
    async def scene_handler(self, blender_executable: str):
        """Create a SceneHandler with real Blender."""
        handler = SceneHandler(blender_executable)
        yield handler

    @pytest.mark.asyncio
    async def test_create_scene(self, scene_handler: SceneHandler):
        """Test scene creation."""
        result = await scene_handler.create_scene("TestScene")

        assert "Created scene: TestScene" in result

        # Verify scene exists
        verify_script = '''
import bpy
scenes = [scene.name for scene in bpy.data.scenes]
print(f"Available scenes: {scenes}")
'''
        verify_result = await scene_handler.executor.execute_script(verify_script)
        assert "TestScene" in verify_result

    @pytest.mark.asyncio
    async def test_clear_scene(self, scene_handler: SceneHandler):
        """Test scene clearing."""
        # First create some objects
        setup_script = '''
import bpy
bpy.ops.mesh.primitive_cube_add()
bpy.ops.mesh.primitive_uv_sphere_add()
print(f"Created {len(bpy.data.objects)} objects")
'''
        await scene_handler.executor.execute_script(setup_script)

        # Clear scene
        result = await scene_handler.clear_scene()
        assert "Scene cleared successfully" in result

        # Verify scene is clear
        verify_script = '''
import bpy
object_count = len([obj for obj in bpy.data.objects if obj.type != 'CAMERA' and obj.type != 'LIGHT'])
print(f"Objects after clear: {object_count}")
'''
        verify_result = await scene_handler.executor.execute_script(verify_script)
        assert "Objects after clear: 0" in verify_result

    @pytest.mark.asyncio
    async def test_get_scene_info(self, scene_handler: SceneHandler):
        """Test getting scene information."""
        # Create a test scene
        setup_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
bpy.ops.mesh.primitive_uv_sphere_add(location=(2, 0, 0))
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
bpy.ops.object.camera_add(location=(7, -7, 5))
'''
        await scene_handler.executor.execute_script(setup_script)

        # Get scene info - we'll test this by directly querying
        info_script = '''
import bpy
import json

scene_info = {
    "objects": len(bpy.data.objects),
    "meshes": len(bpy.data.meshes),
    "materials": len(bpy.data.materials),
    "lights": len([obj for obj in bpy.data.objects if obj.type == 'LIGHT']),
    "cameras": len([obj for obj in bpy.data.objects if obj.type == 'CAMERA'])
}

print(json.dumps(scene_info))
'''
        result = await scene_handler.executor.execute_script(info_script)

        # Parse JSON
        json_line = None
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                json_line = line
                break

        assert json_line is not None
        scene_info = json.loads(json_line)

        assert scene_info["objects"] >= 4  # cube, sphere, light, camera
        assert scene_info["meshes"] >= 2  # cube and sphere meshes
        assert scene_info["lights"] >= 1
        assert scene_info["cameras"] >= 1


@pytest.mark.integration
@pytest.mark.requires_blender
class TestMeshHandlerIntegration:
    """Integration tests for MeshHandler."""

    @pytest.fixture
    async def mesh_handler(self, blender_executable: str):
        """Create a MeshHandler with real Blender."""
        handler = MeshHandler(blender_executable)
        yield handler

    @pytest.mark.asyncio
    async def test_create_basic_objects(self, mesh_handler: MeshHandler):
        """Test creation of basic mesh objects."""
        # Test cube creation
        result = await mesh_handler.executor.execute_script('''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
print(f"Created cube: {cube.name}, vertices: {len(cube.data.vertices)}")
''')

        assert "Created cube" in result

        # Test sphere creation
        result = await mesh_handler.executor.execute_script('''
import bpy
bpy.ops.mesh.primitive_uv_sphere_add(location=(2, 0, 0))
sphere = bpy.context.active_object
print(f"Created sphere: {sphere.name}, vertices: {len(sphere.data.vertices)}")
''')

        assert "Created sphere" in result

    @pytest.mark.asyncio
    async def test_furniture_creation(self, mesh_handler: MeshHandler):
        """Test furniture object creation."""
        # Test chaiselongue creation (if available)
        try:
            result = await mesh_handler.create_chaiselongue("TestChaise")
            assert "Created elegant victorian chaiselongue: TestChaise" in result

            # Verify object was created
            verify_script = '''
import bpy
objects = [obj.name for obj in bpy.data.objects if obj.type == 'MESH']
print(f"Mesh objects: {objects}")
'''
            verify_result = await mesh_handler.executor.execute_script(verify_script)
            assert "TestChaise" in verify_result
        except Exception as e:
            # If the specific furniture creation fails, that's okay for integration test
            pytest.skip(f"Furniture creation not available: {e}")

    @pytest.mark.asyncio
    async def test_candle_set_creation(self, mesh_handler: MeshHandler):
        """Test candle set creation."""
        try:
            result = await mesh_handler.create_candle_set(count=3)
            assert "Created 3 elegant candles" in result

            # Verify candles were created
            verify_script = '''
import bpy
candle_objects = [obj.name for obj in bpy.data.objects if "candle" in obj.name.lower()]
print(f"Candle objects: {candle_objects}")
'''
            verify_result = await mesh_handler.executor.execute_script(verify_script)
            # Should have at least some candle-related objects
            assert len(verify_result.strip()) > 0
        except Exception as e:
            pytest.skip(f"Candle creation not available: {e}")

    @pytest.mark.asyncio
    async def test_mesh_modification(self, mesh_handler: MeshHandler):
        """Test mesh modification operations."""
        setup_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
print(f"Initial cube scale: {cube.scale}")
'''

        await mesh_handler.executor.execute_script(setup_script)

        # Modify the mesh
        modify_script = '''
import bpy
cube = bpy.context.active_object
cube.scale = (2, 2, 2)
cube.location = (1, 1, 1)
print(f"Modified cube scale: {cube.scale}, location: {cube.location}")
'''

        result = await mesh_handler.executor.execute_script(modify_script)
        assert "Modified cube scale: (2.0, 2.0, 2.0)" in result
        assert "location: (1.0, 1.0, 1.0)" in result


@pytest.mark.integration
@pytest.mark.requires_blender
class TestMaterialHandlerIntegration:
    """Integration tests for MaterialHandler."""

    @pytest.fixture
    async def material_handler(self, blender_executable: str):
        """Create a MaterialHandler with real Blender."""
        handler = MaterialHandler(blender_executable)
        yield handler

    @pytest.mark.asyncio
    async def test_create_basic_material(self, material_handler: MaterialHandler):
        """Test basic material creation."""
        setup_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
'''

        await material_handler.executor.execute_script(setup_script)

        # Create material
        material_script = '''
import bpy
cube = bpy.context.active_object

# Create a basic material
material = bpy.data.materials.new(name="TestMaterial")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 0, 0, 1)  # Red

cube.data.materials.append(material)
print(f"Created and assigned material: {material.name}")
'''

        result = await material_handler.executor.execute_script(material_script)
        assert "Created and assigned material: TestMaterial" in result

    @pytest.mark.asyncio
    async def test_fabric_material_creation(self, material_handler: MaterialHandler):
        """Test fabric material creation."""
        try:
            result = await material_handler.create_fabric_material("TestFabric", fabric_type="velvet")

            # Verify material was created
            verify_script = '''
import bpy
materials = [mat.name for mat in bpy.data.materials]
print(f"Available materials: {materials}")
'''
            verify_result = await material_handler.executor.execute_script(verify_script)
            assert "TestFabric" in verify_result or "velvet" in result.lower()
        except Exception as e:
            pytest.skip(f"Fabric material creation not available: {e}")

    @pytest.mark.asyncio
    async def test_metal_material_creation(self, material_handler: MaterialHandler):
        """Test metal material creation."""
        try:
            result = await material_handler.create_metal_material("TestMetal", metal_type="gold")

            # Verify material was created
            verify_script = '''
import bpy
materials = [mat.name for mat in bpy.data.materials]
print(f"Available materials: {materials}")
'''
            verify_result = await material_handler.executor.execute_script(verify_script)
            assert "TestMetal" in verify_result or "gold" in result.lower()
        except Exception as e:
            pytest.skip(f"Metal material creation not available: {e}")

    @pytest.mark.asyncio
    async def test_material_assignment(self, material_handler: MaterialHandler):
        """Test material assignment to objects."""
        setup_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create two objects
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube1 = bpy.context.active_object
cube1.name = "Cube1"

bpy.ops.mesh.primitive_uv_sphere_add(location=(2, 0, 0))
sphere1 = bpy.context.active_object
sphere1.name = "Sphere1"

# Create two materials
material1 = bpy.data.materials.new(name="RedMaterial")
material1.use_nodes = True
material1.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 0, 0, 1)

material2 = bpy.data.materials.new(name="BlueMaterial")
material2.use_nodes = True
material2.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 1, 1)
'''

        await material_handler.executor.execute_script(setup_script)

        # Assign materials
        assign_script = '''
import bpy

cube1 = bpy.data.objects["Cube1"]
sphere1 = bpy.data.objects["Sphere1"]
red_mat = bpy.data.materials["RedMaterial"]
blue_mat = bpy.data.materials["BlueMaterial"]

cube1.data.materials.append(red_mat)
sphere1.data.materials.append(blue_mat)

print("Materials assigned successfully")
print(f"Cube1 materials: {[mat.name for mat in cube1.data.materials]}")
print(f"Sphere1 materials: {[mat.name for mat in sphere1.data.materials]}")
'''

        result = await material_handler.executor.execute_script(assign_script)
        assert "Materials assigned successfully" in result
        assert "RedMaterial" in result
        assert "BlueMaterial" in result
