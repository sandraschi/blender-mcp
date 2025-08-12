"""Comprehensive test suite for Blender MCP server."""

import pytest
import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from blender_mcp.server import BlenderMCPServer
from blender_mcp.utils.blender_executor import BlenderExecutor
from blender_mcp.handlers import SceneHandler, MeshHandler, MaterialHandler, ExportHandler, RenderHandler
from blender_mcp.exceptions import BlenderNotFoundError, BlenderScriptError


class TestBlenderExecutor:
    """Test the core Blender executor functionality."""
    
    @pytest.fixture
    def executor(self):
        return BlenderExecutor("blender")
    
    @pytest.mark.asyncio
    async def test_simple_script_execution(self, executor):
        """Test basic script execution."""
        script = '''
import bpy
print("Test script executed successfully")
'''
        result = await executor.execute_script(script)
        assert "Test script executed successfully" in result
    
    @pytest.mark.asyncio
    async def test_scene_object_creation(self, executor):
        """Test creating objects in Blender scene."""
        script = '''
import bpy
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TestCube"
print(f"Created cube: {cube.name}")
'''
        result = await executor.execute_script(script)
        assert "Created cube: TestCube" in result
    
    @pytest.mark.asyncio
    async def test_script_error_handling(self, executor):
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


class TestSceneHandler:
    """Test scene operations."""
    
    @pytest.fixture
    def scene_handler(self):
        return SceneHandler("blender")
    
    @pytest.mark.asyncio
    async def test_create_scene(self, scene_handler):
        """Test scene creation."""
        result = await scene_handler.create_scene("TestScene")
        assert "Created scene: TestScene" in result
    
    @pytest.mark.asyncio
    async def test_clear_scene(self, scene_handler):
        """Test scene clearing."""
        result = await scene_handler.clear_scene()
        assert "Scene cleared successfully" in result


class TestMeshHandler:
    """Test mesh generation operations."""
    
    @pytest.fixture
    def mesh_handler(self):
        return MeshHandler("blender")
    
    @pytest.mark.asyncio
    async def test_create_chaiselongue(self, mesh_handler):
        """Test chaiselongue creation."""
        result = await mesh_handler.create_chaiselongue("TestChaise")
        assert "Created elegant victorian chaiselongue: TestChaise" in result
    
    @pytest.mark.asyncio
    async def test_create_candle_set(self, mesh_handler):
        """Test candle set creation."""
        result = await mesh_handler.create_candle_set(count=3)
        assert "Created 3 elegant candles" in result
    
    @pytest.mark.asyncio
    async def test_create_ornate_mirror(self, mesh_handler):
        """Test ornate mirror creation."""
        result = await mesh_handler.create_ornate_mirror("TestMirror")
        assert "Created ornate baroque mirror: TestMirror" in result
    
    @pytest.mark.asyncio
    async def test_create_feather_duster(self, mesh_handler):
        """Test feather duster creation."""
        result = await mesh_handler.create_feather_duster("TestDuster")
        assert "Created vintage feather duster: TestDuster" in result


class TestMaterialHandler:
    """Test material creation operations."""
    
    @pytest.fixture
    def material_handler(self):
        return MaterialHandler("blender")
    
    @pytest.mark.asyncio
    async def test_create_fabric_material(self, material_handler):
        """Test fabric material creation."""
        result = await material_handler.create_fabric_material("TestFabric", fabric_type="velvet")
        assert "Created velvet fabric material: TestFabric" in result
    
    @pytest.mark.asyncio
    async def test_create_metal_material(self, material_handler):
        """Test metal material creation."""
        result = await material_handler.create_metal_material("TestMetal", metal_type="gold")
        assert "Created gold metal material: TestMetal" in result
    
    @pytest.mark.asyncio
    async def test_create_wood_material(self, material_handler):
        """Test wood material creation."""
        result = await material_handler.create_wood_material("TestWood", wood_type="oak")
        assert "Created oak wood material: TestWood" in result


class TestExportHandler:
    """Test export operations."""
    
    @pytest.fixture
    def export_handler(self):
        return ExportHandler("blender")
    
    @pytest.mark.asyncio
    async def test_export_for_unity(self, export_handler):
        """Test Unity export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_unity.fbx")
            result = await export_handler.export_for_unity(output_path)
            assert "Exported Unity-optimized scene" in result
    
    @pytest.mark.asyncio
    async def test_export_for_vrchat(self, export_handler):
        """Test VRChat export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_vrchat.fbx")
            result = await export_handler.export_for_vrchat(output_path, performance_rank="Good")
            assert "Exported VRChat-optimized scene" in result


class TestRenderHandler:
    """Test render operations."""
    
    @pytest.fixture
    def render_handler(self):
        return RenderHandler("blender")
    
    @pytest.mark.asyncio
    async def test_render_preview(self, render_handler):
        """Test preview rendering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_preview.png")
            result = await render_handler.render_preview(output_path, resolution_x=640, resolution_y=480, samples=16)
            assert "Rendered professional preview" in result


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def server(self):
        return BlenderMCPServer("blender")
    
    @pytest.mark.asyncio
    async def test_complete_boudoir_workflow(self):
        """Test complete boudoir creation workflow."""
        scene_handler = SceneHandler("blender")
        mesh_handler = MeshHandler("blender")
        material_handler = MaterialHandler("blender")
        
        # Create scene
        await scene_handler.create_scene("BoudoirScene")
        
        # Create furniture
        await mesh_handler.create_chaiselongue("ElegantChaise")
        await mesh_handler.create_candle_set(count=3)
        await mesh_handler.create_ornate_mirror("VictorianMirror")
        await mesh_handler.create_feather_duster("VintageDuster")
        
        # Create materials
        await material_handler.create_fabric_material("VelvetUpholstery", fabric_type="velvet")
        await material_handler.create_metal_material("GoldFrame", metal_type="gold")
        await material_handler.create_wood_material("MahoganyHandle", wood_type="mahogany")
        
        # This workflow should complete without errors
        assert True
    
    @pytest.mark.asyncio
    async def test_export_workflow(self):
        """Test complete export workflow."""
        export_handler = ExportHandler("blender")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            unity_path = os.path.join(temp_dir, "boudoir_unity.fbx")
            vrchat_path = os.path.join(temp_dir, "boudoir_vrchat.fbx")
            
            # Export for both platforms
            unity_result = await export_handler.export_for_unity(unity_path)
            vrchat_result = await export_handler.export_for_vrchat(vrchat_path)
            
            assert "Unity-optimized" in unity_result
            assert "VRChat-optimized" in vrchat_result


# Performance and stress tests
class TestPerformance:
    """Performance and stress tests."""
    
    @pytest.mark.asyncio
    async def test_multiple_objects_creation(self):
        """Test creating multiple objects rapidly."""
        mesh_handler = MeshHandler("blender")
        
        # Create multiple candle sets
        for i in range(3):
            result = await mesh_handler.create_candle_set(count=5, base_x=i * 3)
            assert "Created 5 elegant candles" in result
    
    @pytest.mark.asyncio
    async def test_material_batch_creation(self):
        """Test batch material creation."""
        material_handler = MaterialHandler("blender")
        
        fabric_types = ["velvet", "silk", "cotton", "linen"]
        for fabric_type in fabric_types:
            result = await material_handler.create_fabric_material(f"{fabric_type.title()}Material", fabric_type=fabric_type)
            assert f"Created {fabric_type} fabric material" in result


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
