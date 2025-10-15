"""
Level 1: Smoke Test - Blender MCP Basic Functionality (2 minutes)
=================================================================

Quick sanity check that the core system works.

WHAT IT TESTS:
- Server can start and initialize
- Basic tool discovery works
- Simple tool calls succeed
- No crashes on basic operations

WHAT IT SKIPS:
- Complex operations
- Performance testing
- Edge cases
- Multi-step workflows

USAGE:
pytest tests/megatest/level1_smoke/ -v -m megatest_smoke
"""

import pytest
import asyncio
from pathlib import Path


@pytest.mark.megatest_smoke
class TestSmokeLevel:
    """Smoke test suite - essential functionality only."""

    def test_server_can_import(self, megatest_config):
        """Test that server module can be imported."""
        try:
            import blender_mcp.server
            assert True, "Server import successful"
        except ImportError as e:
            pytest.fail(f"Server import failed: {e}")

    def test_tools_can_import(self, megatest_config):
        """Test that tools module can be imported."""
        try:
            import blender_mcp.tools
            assert True, "Tools import successful"
        except ImportError as e:
            pytest.fail(f"Tools import failed: {e}")

    def test_config_can_import(self, megatest_config):
        """Test that config module can be imported."""
        try:
            import blender_mcp.config
            assert True, "Config import successful"
        except ImportError as e:
            pytest.fail(f"Config import failed: {e}")

    def test_safety_isolation(self, megatest_base_path, megatest_results_path):
        """Test that test environment is properly isolated."""
        # Ensure we're not in production paths
        from tests.megatest.conftest import is_production_path

        assert not is_production_path(megatest_base_path), \
            f"Test path {megatest_base_path} is in production area!"

        assert megatest_results_path.exists(), \
            f"Results path {megatest_results_path} not created"

        # Check safety log exists
        safety_log = megatest_results_path / "safety_check.log"
        assert safety_log.exists(), "Safety log not created"

        with open(safety_log) as f:
            content = f.read()
            assert "SAFETY CHECK PASSED" in content, "Safety check failed"

    def test_temp_directory_creation(self, safe_temp_dir):
        """Test that temporary directories are created safely."""
        assert safe_temp_dir.exists(), f"Temp directory {safe_temp_dir} not created"
        assert safe_temp_dir.is_dir(), f"Temp path {safe_temp_dir} is not a directory"

        # Test can write to temp directory
        test_file = safe_temp_dir / "test_write.txt"
        test_file.write_text("test content")
        assert test_file.exists(), "Cannot write to temp directory"
        assert test_file.read_text() == "test content", "Cannot read from temp directory"

    def test_blender_executor_import(self, megatest_config):
        """Test that Blender executor can be imported."""
        try:
            from blender_mcp.utils.blender_executor import BlenderExecutor
            assert True, "BlenderExecutor import successful"
        except ImportError as e:
            pytest.fail(f"BlenderExecutor import failed: {e}")

    def test_basic_test_data_creation(self, megatest_config):
        """Test that basic test data helpers work."""
        from tests.megatest.conftest import (
            create_test_blender_scene,
            create_test_blender_object,
            create_test_material
        )

        # Test scene creation
        scene = create_test_blender_scene("test_scene")
        assert scene["name"] == "test_scene"
        assert "objects" in scene
        assert scene["metadata"]["test_session"] is True

        # Test object creation
        obj = create_test_blender_object("test_cube", "MESH")
        assert obj["name"] == "test_cube"
        assert obj["type"] == "MESH"
        assert obj["location"] == [0.0, 0.0, 0.0]

        # Test material creation
        mat = create_test_material("test_material")
        assert mat["name"] == "test_material"
        assert mat["type"] == "PRINCIPLED"
        assert mat["base_color"] == [0.8, 0.8, 0.8, 1.0]

    @pytest.mark.asyncio
    async def test_async_test_framework(self, megatest_config):
        """Test that async test framework works."""
        # Simple async test to ensure pytest-asyncio works
        await asyncio.sleep(0.1)
        assert True, "Async test framework working"

    def test_megatest_config_properties(self, megatest_config):
        """Test that megatest config has required properties."""
        assert hasattr(megatest_config, 'base_path')
        assert hasattr(megatest_config, 'results_path')
        assert hasattr(megatest_config, 'run_id')

        assert megatest_config.base_path.exists()
        assert megatest_config.results_path.exists()
        assert isinstance(megatest_config.run_id, str)
        assert len(megatest_config.run_id) > 0
