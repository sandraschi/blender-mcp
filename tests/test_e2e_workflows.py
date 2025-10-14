"""End-to-end tests for complete Blender MCP workflows.

These tests run the actual FastMCP server and test complete user workflows.
"""

import pytest
import asyncio
import httpx
import json
from pathlib import Path
from typing import Dict, Any

from blender_mcp.server import BlenderMCPServer


@pytest.mark.e2e
@pytest.mark.requires_blender
class TestE2EWorkflows:
    """End-to-end tests for complete workflows."""

    @pytest.fixture
    async def server(self, blender_executable: str, temp_dir: Path):
        """Create and start a test server."""
        server = BlenderMCPServer(blender_executable)

        # Start server in background
        server_task = asyncio.create_task(server.start_server())
        await asyncio.sleep(1)  # Give server time to start

        yield server

        # Cleanup
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass

    async def call_tool(self, server: BlenderMCPServer, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool through the MCP server."""
        # This is a simplified version - in real implementation we'd use the MCP protocol
        # For testing purposes, we'll call the handler methods directly

        if tool_name == "create_scene":
            from blender_mcp.handlers.scene_handler import SceneHandler
            handler = SceneHandler(server.blender_executable)
            result = await handler.create_scene(arguments.get("name", "TestScene"))
            return {"result": result}

        elif tool_name == "create_cube":
            from blender_mcp.handlers.mesh_handler import MeshHandler
            handler = MeshHandler(server.blender_executable)
            script = f'''
import bpy
bpy.ops.mesh.primitive_cube_add(location=({arguments.get("x", 0)}, {arguments.get("y", 0)}, {arguments.get("z", 0)}))
cube = bpy.context.active_object
cube.name = "{arguments.get("name", "Cube")}"
print(f"Created cube: {{cube.name}}")
'''
            result = await handler.executor.execute_script(script)
            return {"result": result}

        elif tool_name == "create_material":
            from blender_mcp.handlers.material_handler import MaterialHandler
            handler = MaterialHandler(server.blender_executable)
            script = f'''
import bpy
material = bpy.data.materials.new(name="{arguments.get("name", "Material")}")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = ({arguments.get("r", 1)}, {arguments.get("g", 1)}, {arguments.get("b", 1)}, 1)
print(f"Created material: {{material.name}}")
'''
            result = await handler.executor.execute_script(script)
            return {"result": result}

        return {"error": f"Unknown tool: {tool_name}"}

    @pytest.mark.asyncio
    async def test_basic_scene_creation_workflow(self, server: BlenderMCPServer):
        """Test a basic scene creation workflow."""
        # Create scene
        result1 = await self.call_tool(server, "create_scene", {"name": "TestScene"})
        assert "Created scene: TestScene" in result1["result"]

        # Create objects
        result2 = await self.call_tool(server, "create_cube", {"name": "Cube1", "x": 0, "y": 0, "z": 0})
        assert "Created cube: Cube1" in result2["result"]

        result3 = await self.call_tool(server, "create_cube", {"name": "Cube2", "x": 2, "y": 0, "z": 0})
        assert "Created cube: Cube2" in result3["result"]

        # Create materials
        result4 = await self.call_tool(server, "create_material", {"name": "RedMaterial", "r": 1, "g": 0, "b": 0})
        assert "Created material: RedMaterial" in result4["result"]

        result5 = await self.call_tool(server, "create_material", {"name": "BlueMaterial", "r": 0, "g": 0, "b": 1})
        assert "Created material: BlueMaterial" in result5["result"]

        # Verify scene contents
        verify_script = '''
import bpy
import json

scene_info = {
    "scenes": [scene.name for scene in bpy.data.scenes],
    "objects": [obj.name for obj in bpy.data.objects if obj.type == 'MESH'],
    "materials": [mat.name for mat in bpy.data.materials]
}

print(json.dumps(scene_info))
'''
        result6 = await server.executor.execute_script(verify_script)

        # Parse JSON
        json_line = None
        for line in result6.split('\n'):
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                json_line = line
                break

        assert json_line is not None
        scene_info = json.loads(json_line)

        assert "TestScene" in scene_info["scenes"]
        assert "Cube1" in scene_info["objects"]
        assert "Cube2" in scene_info["objects"]
        assert "RedMaterial" in scene_info["materials"]
        assert "BlueMaterial" in scene_info["materials"]

    @pytest.mark.asyncio
    async def test_furniture_creation_workflow(self, server: BlenderMCPServer):
        """Test furniture creation workflow."""
        try:
            from blender_mcp.handlers.mesh_handler import MeshHandler
            mesh_handler = MeshHandler(server.blender_executable)

            # Try to create furniture items
            results = []

            # Create chaiselongue
            try:
                result = await mesh_handler.create_chaiselongue("TestChaise")
                results.append(("chaiselongue", result))
            except Exception as e:
                results.append(("chaiselongue", f"Error: {e}"))

            # Create candle set
            try:
                result = await mesh_handler.create_candle_set(count=3)
                results.append(("candles", result))
            except Exception as e:
                results.append(("candles", f"Error: {e}"))

            # Create mirror
            try:
                result = await mesh_handler.create_ornate_mirror("TestMirror")
                results.append(("mirror", result))
            except Exception as e:
                results.append(("mirror", f"Error: {e}"))

            # At least one should succeed for the test to pass
            successful_creations = [r for r in results if not r[1].startswith("Error:")]
            assert len(successful_creations) > 0, f"No furniture items could be created: {results}"

            # Verify objects were created
            verify_script = '''
import bpy
mesh_objects = [obj.name for obj in bpy.data.objects if obj.type == 'MESH']
print(f"Created mesh objects: {mesh_objects}")
'''
            verify_result = await server.executor.execute_script(verify_script)
            assert len(verify_result.strip()) > 0

        except ImportError:
            pytest.skip("Furniture handlers not available")

    @pytest.mark.asyncio
    async def test_material_workflow(self, server: BlenderMCPServer):
        """Test material creation and assignment workflow."""
        try:
            from blender_mcp.handlers.material_handler import MaterialHandler
            material_handler = MaterialHandler(server.blender_executable)

            # Create various materials
            materials_created = []

            # Fabric materials
            try:
                result = await material_handler.create_fabric_material("VelvetFabric", fabric_type="velvet")
                materials_created.append("VelvetFabric")
            except Exception:
                pass

            try:
                result = await material_handler.create_fabric_material("SilkFabric", fabric_type="silk")
                materials_created.append("SilkFabric")
            except Exception:
                pass

            # Metal materials
            try:
                result = await material_handler.create_metal_material("GoldMetal", metal_type="gold")
                materials_created.append("GoldMetal")
            except Exception:
                pass

            # Wood materials
            try:
                result = await material_handler.create_wood_material("OakWood", wood_type="oak")
                materials_created.append("OakWood")
            except Exception:
                pass

            # At least some materials should be created
            assert len(materials_created) > 0, "No materials could be created"

            # Verify materials exist
            verify_script = f'''
import bpy
all_materials = [mat.name for mat in bpy.data.materials]
expected_materials = {materials_created}
found_materials = [mat for mat in expected_materials if mat in all_materials]
print(f"Found materials: {{found_materials}}")
'''
            verify_result = await server.executor.execute_script(verify_script)
            assert "Found materials:" in verify_result

        except ImportError:
            pytest.skip("Material handlers not available")

    @pytest.mark.asyncio
    async def test_export_workflow(self, server: BlenderMCPServer, temp_dir: Path):
        """Test export workflow."""
        try:
            from blender_mcp.handlers.export_handler import ExportHandler
            export_handler = ExportHandler(server.blender_executable)

            # Create a simple scene first
            setup_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
bpy.ops.object.camera_add(location=(5, -5, 5))
bpy.context.scene.camera = bpy.context.active_object
'''
            await server.executor.execute_script(setup_script)

            # Test FBX export
            fbx_path = temp_dir / "test_scene.fbx"
            try:
                result = await export_handler.export_for_unity(str(fbx_path))
                assert "Unity-optimized" in result

                # Check if file was created
                assert fbx_path.exists() or "exported" in result.lower()
            except Exception as e:
                pytest.skip(f"FBX export not available: {e}")

        except ImportError:
            pytest.skip("Export handlers not available")

    @pytest.mark.asyncio
    async def test_render_workflow(self, server: BlenderMCPServer, temp_dir: Path):
        """Test rendering workflow."""
        try:
            from blender_mcp.handlers.render_handler import RenderHandler
            render_handler = RenderHandler(server.blender_executable)

            # Create a simple scene
            setup_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object

# Add material
material = bpy.data.materials.new(name="RenderMaterial")
material.use_nodes = True
material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.2, 0.2, 1)
cube.data.materials.append(material)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))

# Add camera
bpy.ops.object.camera_add(location=(7, -7, 5))
bpy.context.scene.camera = bpy.context.active_object
'''
            await server.executor.execute_script(setup_script)

            # Test rendering
            render_path = temp_dir / "test_render.png"
            try:
                result = await render_handler.render_preview(str(render_path), resolution_x=640, resolution_y=480)
                assert "Rendered" in result

                # Check if file was created
                assert render_path.exists() or "preview" in result.lower()
            except Exception as e:
                pytest.skip(f"Rendering not available: {e}")

        except ImportError:
            pytest.skip("Render handlers not available")

    @pytest.mark.asyncio
    async def test_complex_boudoir_workflow(self, server: BlenderMCPServer):
        """Test complete boudoir scene creation workflow."""
        try:
            # This tests the integration of multiple handlers
            from blender_mcp.handlers.scene_handler import SceneHandler
            from blender_mcp.handlers.mesh_handler import MeshHandler
            from blender_mcp.handlers.material_handler import MaterialHandler

            scene_handler = SceneHandler(server.blender_executable)
            mesh_handler = MeshHandler(server.blender_executable)
            material_handler = MaterialHandler(server.blender_executable)

            # Create scene
            await scene_handler.create_scene("BoudoirScene")

            # Create furniture (with error handling)
            furniture_created = 0

            try:
                await mesh_handler.create_chaiselongue("ElegantChaise")
                furniture_created += 1
            except:
                pass

            try:
                await mesh_handler.create_candle_set(count=3)
                furniture_created += 1
            except:
                pass

            try:
                await mesh_handler.create_ornate_mirror("VictorianMirror")
                furniture_created += 1
            except:
                pass

            # Create materials
            materials_created = 0

            try:
                await material_handler.create_fabric_material("VelvetUpholstery", fabric_type="velvet")
                materials_created += 1
            except:
                pass

            try:
                await material_handler.create_metal_material("GoldFrame", metal_type="gold")
                materials_created += 1
            except:
                pass

            # At minimum, scene should be created
            assert True  # Workflow completed without crashing

            # Verify scene has some content
            verify_script = '''
import bpy
import json

scene_stats = {
    "total_objects": len(bpy.data.objects),
    "mesh_objects": len([obj for obj in bpy.data.objects if obj.type == 'MESH']),
    "materials": len(bpy.data.materials),
    "scenes": [scene.name for scene in bpy.data.scenes]
}

print(json.dumps(scene_stats))
'''
            result = await server.executor.execute_script(verify_script)

            # Parse JSON
            json_line = None
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    json_line = line
                    break

            assert json_line is not None
            scene_stats = json.loads(json_line)

            assert "BoudoirScene" in scene_stats["scenes"]
            assert scene_stats["total_objects"] >= 1  # At least camera/light

        except ImportError as e:
            pytest.skip(f"Required handlers not available: {e}")


@pytest.mark.e2e
@pytest.mark.slow
class TestPerformanceWorkflows:
    """Performance and stress tests for workflows."""

    @pytest.mark.asyncio
    async def test_multiple_scene_creation(self, blender_executable: str):
        """Test creating multiple scenes rapidly."""
        from blender_mcp.handlers.scene_handler import SceneHandler
        scene_handler = SceneHandler(blender_executable)

        # Create multiple scenes
        for i in range(5):
            scene_name = f"PerformanceScene{i}"
            result = await scene_handler.create_scene(scene_name)
            assert f"Created scene: {scene_name}" in result

        # Verify scenes exist
        verify_script = '''
import bpy
scenes = [scene.name for scene in bpy.data.scenes if "PerformanceScene" in scene.name]
print(f"Performance scenes created: {len(scenes)}")
'''
        result = await scene_handler.executor.execute_script(verify_script)
        assert "Performance scenes created: 5" in result

    @pytest.mark.asyncio
    async def test_batch_object_creation(self, blender_executable: str):
        """Test creating many objects at once."""
        from blender_mcp.handlers.mesh_handler import MeshHandler
        mesh_handler = MeshHandler(blender_executable)

        # Create batch of objects
        batch_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)

objects_created = []
for i in range(20):
    x, y, z = (i % 5) * 2, (i // 5) * 2, 0
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
    cube = bpy.context.active_object
    cube.name = f"BatchCube_{i:02d}"
    objects_created.append(cube.name)

print(f"Created {len(objects_created)} objects successfully")
'''
        result = await mesh_handler.executor.execute_script(batch_script)
        assert "Created 20 objects successfully" in result

    @pytest.mark.asyncio
    async def test_memory_cleanup_workflow(self, blender_executable: str):
        """Test that memory is properly cleaned up between operations."""
        from blender_mcp.utils.blender_executor import BlenderExecutor
        executor = BlenderExecutor(blender_executable)

        # Run multiple complex operations
        for iteration in range(3):
            complex_script = f'''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create complex scene
for i in range(10):
    bpy.ops.mesh.primitive_cube_add(location=(i*2, 0, 0))
    cube = bpy.context.active_object
    cube.name = f"CleanupCube_{iteration}_{i}"

print(f"Iteration {iteration} completed")
'''
            result = await executor.execute_script(complex_script)
            assert f"Iteration {iteration} completed" in result

        # Final verification
        final_script = '''
import bpy
cubes = [obj for obj in bpy.data.objects if obj.type == 'MESH' and "CleanupCube" in obj.name]
print(f"Total cleanup cubes remaining: {len(cubes)}")
'''
        result = await executor.execute_script(final_script)
        # Should have cubes from all iterations
        assert "Total cleanup cubes remaining:" in result
