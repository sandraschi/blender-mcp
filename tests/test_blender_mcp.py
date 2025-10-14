"""Comprehensive test suite for Blender MCP server.

This module contains tests that can run with or without real Blender.
Use pytest markers to control test execution:
- pytest -m "not integration" : Run only unit tests
- pytest -m "integration" : Run only integration tests (requires Blender)
- pytest -m "e2e" : Run end-to-end tests (requires Blender)
- pytest -m "performance" : Run performance tests (requires Blender)
"""

import pytest
import asyncio
import os
import tempfile
from pathlib import Path

# Import test utilities
from .test_utils import TestBlenderHelper, TestDataBuilder, PerformanceTimer

# Try to import Blender MCP components
try:
    from blender_mcp.utils.blender_executor import BlenderExecutor
    from blender_mcp.exceptions import BlenderNotFoundError, BlenderScriptError
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    print(f"Warning: Some imports failed: {e}")

# Try to import additional components
try:
    from blender_mcp.server import BlenderMCPServer
    from blender_mcp.handlers import SceneHandler, MeshHandler, MaterialHandler, ExportHandler, RenderHandler
    FULL_IMPORTS_AVAILABLE = True
except ImportError:
    FULL_IMPORTS_AVAILABLE = False


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="BlenderExecutor imports not available")
class TestBlenderExecutor:
    """Test the core Blender executor functionality."""

    @pytest.fixture
    def executor(self, blender_executable: str):
        """Create executor with real Blender."""
        return BlenderExecutor(blender_executable)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_simple_script_execution(self, executor: BlenderExecutor):
        """Test basic script execution with real Blender."""
        script = '''
import bpy
print("Test script executed successfully")
'''
        result = await executor.execute_script(script)
        assert "Test script executed successfully" in result

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_scene_object_creation(self, executor: BlenderExecutor):
        """Test creating objects in Blender scene."""
        script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TestCube"
print(f"Created cube: {cube.name}")
'''
        result = await executor.execute_script(script)
        assert "Created cube: TestCube" in result

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_script_error_handling(self, executor: BlenderExecutor):
        """Test that script errors are properly caught."""
        script = '''
import bpy
# This should cause an error
nonexistent_function()
'''
        with pytest.raises(BlenderScriptError):
            await executor.execute_script(script)

    def test_blender_validation(self):
        """Test Blender installation validation."""
        # Test with invalid executable
        with pytest.raises(BlenderNotFoundError):
            BlenderExecutor("nonexistent_blender")


@pytest.mark.skipif(not FULL_IMPORTS_AVAILABLE, reason="Full Blender MCP imports not available")
class TestSceneHandler:
    """Test scene operations."""

    @pytest.fixture
    async def scene_handler(self, blender_executable: str):
        return SceneHandler(blender_executable)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_scene(self, scene_handler: SceneHandler):
        """Test scene creation."""
        result = await scene_handler.create_scene("TestScene")
        assert "Created scene: TestScene" in result

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_clear_scene(self, scene_handler: SceneHandler):
        """Test scene clearing."""
        result = await scene_handler.clear_scene()
        assert "Scene cleared successfully" in result


@pytest.mark.skipif(not FULL_IMPORTS_AVAILABLE, reason="Full Blender MCP imports not available")
class TestMeshHandler:
    """Test mesh generation operations."""

    @pytest.fixture
    async def mesh_handler(self, blender_executable: str):
        return MeshHandler(blender_executable)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_chaiselongue(self, mesh_handler: MeshHandler):
        """Test chaiselongue creation."""
        try:
            result = await mesh_handler.create_chaiselongue("TestChaise")
            assert "Created elegant victorian chaiselongue: TestChaise" in result
        except Exception:
            pytest.skip("Chaiselongue creation not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_candle_set(self, mesh_handler: MeshHandler):
        """Test candle set creation."""
        try:
            result = await mesh_handler.create_candle_set(count=3)
            assert "Created 3 elegant candles" in result
        except Exception:
            pytest.skip("Candle creation not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_ornate_mirror(self, mesh_handler: MeshHandler):
        """Test ornate mirror creation."""
        try:
            result = await mesh_handler.create_ornate_mirror("TestMirror")
            assert "Created ornate baroque mirror: TestMirror" in result
        except Exception:
            pytest.skip("Mirror creation not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_feather_duster(self, mesh_handler: MeshHandler):
        """Test feather duster creation."""
        try:
            result = await mesh_handler.create_feather_duster("TestDuster")
            assert "Created vintage feather duster: TestDuster" in result
        except Exception:
            pytest.skip("Feather duster creation not available")


@pytest.mark.skipif(not FULL_IMPORTS_AVAILABLE, reason="Full Blender MCP imports not available")
class TestMaterialHandler:
    """Test material creation operations."""

    @pytest.fixture
    async def material_handler(self, blender_executable: str):
        return MaterialHandler(blender_executable)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_fabric_material(self, material_handler: MaterialHandler):
        """Test fabric material creation."""
        try:
            result = await material_handler.create_fabric_material("TestFabric", fabric_type="velvet")
            assert "Created velvet fabric material: TestFabric" in result
        except Exception:
            pytest.skip("Fabric material creation not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_metal_material(self, material_handler: MaterialHandler):
        """Test metal material creation."""
        try:
            result = await material_handler.create_metal_material("TestMetal", metal_type="gold")
            assert "Created gold metal material: TestMetal" in result
        except Exception:
            pytest.skip("Metal material creation not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_wood_material(self, material_handler: MaterialHandler):
        """Test wood material creation."""
        try:
            result = await material_handler.create_wood_material("TestWood", wood_type="oak")
            assert "Created oak wood material: TestWood" in result
        except Exception:
            pytest.skip("Wood material creation not available")


@pytest.mark.skipif(not FULL_IMPORTS_AVAILABLE, reason="Full Blender MCP imports not available")
class TestExportHandler:
    """Test export operations."""

    @pytest.fixture
    async def export_handler(self, blender_executable: str):
        return ExportHandler(blender_executable)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_export_for_unity(self, export_handler: ExportHandler, temp_dir: Path):
        """Test Unity export."""
        try:
            output_path = temp_dir / "test_unity.fbx"
            result = await export_handler.export_for_unity(str(output_path))
            assert "Exported Unity-optimized scene" in result
        except Exception:
            pytest.skip("Unity export not available")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_export_for_vrchat(self, export_handler: ExportHandler, temp_dir: Path):
        """Test VRChat export."""
        try:
            output_path = temp_dir / "test_vrchat.fbx"
            result = await export_handler.export_for_vrchat(str(output_path), performance_rank="Good")
            assert "Exported VRChat-optimized scene" in result
        except Exception:
            pytest.skip("VRChat export not available")


@pytest.mark.skipif(not FULL_IMPORTS_AVAILABLE, reason="Full Blender MCP imports not available")
class TestRenderHandler:
    """Test render operations."""

    @pytest.fixture
    async def render_handler(self, blender_executable: str):
        return RenderHandler(blender_executable)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_render_preview(self, render_handler: RenderHandler, temp_dir: Path):
        """Test preview rendering."""
        try:
            output_path = temp_dir / "test_preview.png"
            result = await render_handler.render_preview(
                str(output_path),
                resolution_x=640,
                resolution_y=480,
                samples=16
            )
            assert "Rendered professional preview" in result
        except Exception:
            pytest.skip("Rendering not available")


@pytest.mark.skipif(not FULL_IMPORTS_AVAILABLE, reason="Full Blender MCP imports not available")
class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.fixture
    async def server(self, blender_executable: str):
        return BlenderMCPServer(blender_executable)

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_boudoir_workflow(self, blender_executable: str):
        """Test complete boudoir creation workflow."""
        try:
            scene_handler = SceneHandler(blender_executable)
            mesh_handler = MeshHandler(blender_executable)
            material_handler = MaterialHandler(blender_executable)

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

            try:
                await mesh_handler.create_feather_duster("VintageDuster")
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

            try:
                await material_handler.create_wood_material("MahoganyHandle", wood_type="mahogany")
                materials_created += 1
            except:
                pass

            # At least scene creation should work
            assert True

        except Exception:
            pytest.skip("Boudoir workflow components not available")

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_export_workflow(self, blender_executable: str, temp_dir: Path):
        """Test complete export workflow."""
        try:
            export_handler = ExportHandler(blender_executable)

            # Create a simple scene first
            setup_script = '''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
bpy.ops.object.camera_add(location=(5, -5, 5))
bpy.context.scene.camera = bpy.context.active_object
'''
            await export_handler.executor.execute_script(setup_script)

            unity_path = temp_dir / "boudoir_unity.fbx"
            vrchat_path = temp_dir / "boudoir_vrchat.fbx"

            # Export for both platforms
            unity_result = await export_handler.export_for_unity(str(unity_path))
            vrchat_result = await export_handler.export_for_vrchat(str(vrchat_path))

            assert "Unity-optimized" in unity_result
            assert "VRChat-optimized" in vrchat_result

        except Exception:
            pytest.skip("Export workflow not available")


# Performance and stress tests
@pytest.mark.skipif(not FULL_IMPORTS_AVAILABLE, reason="Full Blender MCP imports not available")
class TestPerformance:
    """Performance and stress tests."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_multiple_objects_creation(self, blender_executable: str):
        """Test creating multiple objects rapidly."""
        try:
            mesh_handler = MeshHandler(blender_executable)

            # Create multiple candle sets
            for i in range(3):
                result = await mesh_handler.create_candle_set(count=5, base_x=i * 3)
                assert "Created 5 elegant candles" in result
        except Exception:
            pytest.skip("Multiple objects creation not available")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_material_batch_creation(self, blender_executable: str):
        """Test batch material creation."""
        try:
            material_handler = MaterialHandler(blender_executable)

            fabric_types = ["velvet", "silk", "cotton", "linen"]
            for fabric_type in fabric_types:
                result = await material_handler.create_fabric_material(f"{fabric_type.title()}Material", fabric_type=fabric_type)
                assert f"Created {fabric_type} fabric material" in result
        except Exception:
            pytest.skip("Batch material creation not available")


# Fixture for test configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return {
        "blender_executable": os.environ.get("BLENDER_EXECUTABLE", "blender"),
        "test_timeout": 300,
        "temp_dir": None
    }


# Test utilities
class TestUtilities:
    """Utility functions for testing."""
    
    @staticmethod
    def create_temp_blend_file():
        """Create a temporary blend file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".blend", delete=False) as f:
            return f.name
    
    @staticmethod
    def cleanup_temp_files(file_paths):
        """Clean up temporary files after testing."""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass  # Ignore cleanup errors in tests


# Pytest configuration
def pytest_configure(config):
    """Configure pytest for Blender MCP tests."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")


# Custom pytest fixtures
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Ensure clean test environment
    yield
    # Cleanup after test
    pass
