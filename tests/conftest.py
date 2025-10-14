"""Pytest configuration and fixtures for Blender MCP tests.

This module provides fixtures and configuration for running tests in both local development
environments (with Blender available) and CI/CD environments (without Blender).

Test Categories:
- unit: Pure unit tests that don't require external dependencies
- integration: Tests that require Blender to be installed and available
- slow: Tests that take longer to run (may be skipped in fast CI runs)
- performance: Performance benchmark tests

Usage:
    # Run all unit tests (works in CI)
    pytest tests/unit/ -m "not slow"

    # Run all integration tests (requires Blender)
    pytest tests/integration/ -m "requires_blender"

    # Run all tests except slow ones
    pytest tests/ -m "not slow"
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Optional, Dict, Any
from unittest.mock import MagicMock


# Constants
BLENDER_EXECUTABLE_ENV = "BLENDER_EXECUTABLE"
DEFAULT_BLENDER_PATHS = [
    "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
    "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
    "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
    "/usr/bin/blender",
    "/usr/local/bin/blender",
    "/opt/blender/blender",
    "/Applications/Blender.app/Contents/MacOS/Blender",
]
TEST_TIMEOUT = 60  # seconds


def is_blender_available() -> bool:
    """Check if Blender is available on this system."""
    # Check environment variable first
    env_path = os.environ.get(BLENDER_EXECUTABLE_ENV)
    if env_path and Path(env_path).exists() and Path(env_path).is_file():
        return True

    # Try default paths
    for path in DEFAULT_BLENDER_PATHS:
        if Path(path).exists() and Path(path).is_file():
            return True

    return False


def find_blender_executable() -> Optional[str]:
    """Find a working Blender executable."""
    # Check environment variable first
    env_path = os.environ.get(BLENDER_EXECUTABLE_ENV)
    if env_path and Path(env_path).exists() and Path(env_path).is_file():
        return env_path

    # Try default paths
    for path in DEFAULT_BLENDER_PATHS:
        if Path(path).exists() and Path(path).is_file():
            return str(path)

    return None


@pytest.fixture(scope="session")
def blender_available() -> bool:
    """Check if Blender is available for testing."""
    return is_blender_available()


@pytest.fixture(scope="session")
def blender_executable(blender_available: bool) -> Optional[str]:
    """Find and return the Blender executable path."""
    if not blender_available:
        return None
    return find_blender_executable()


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for the test session."""
    temp_path = Path(tempfile.mkdtemp(prefix="blender_mcp_test_"))
    yield temp_path
    # Cleanup - only in local environment, not CI
    if not os.environ.get("CI"):
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file for individual tests."""
    def _temp_file(suffix: str = "") -> Path:
        fd, path = tempfile.mkstemp(dir=temp_dir, suffix=suffix)
        os.close(fd)
        return Path(path)
    return _temp_file


@pytest.fixture(scope="session")
def test_config(blender_executable: Optional[str], temp_dir: Path) -> Dict[str, Any]:
    """Test configuration dictionary."""
    return {
        "blender_executable": blender_executable,
        "temp_dir": temp_dir,
        "timeout": TEST_TIMEOUT,
        "headless": True,
        "test_data_dir": temp_dir / "test_data",
        "output_dir": temp_dir / "output",
        "ci_mode": bool(os.environ.get("CI")),
        "blender_available": blender_executable is not None,
    }


@pytest.fixture(autouse=True)
def setup_test_environment(test_config: Dict[str, Any]):
    """Setup test environment before each test."""
    # Ensure output directories exist
    test_config["test_data_dir"].mkdir(exist_ok=True)
    test_config["output_dir"].mkdir(exist_ok=True)

    # Set environment variables for tests
    if test_config["blender_executable"]:
        os.environ["BLENDER_EXECUTABLE"] = test_config["blender_executable"]

    yield

    # Cleanup after test if needed
    pass


# Custom pytest markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: pure unit tests that don't require external dependencies")
    config.addinivalue_line("markers", "integration: integration tests that test full workflows")
    config.addinivalue_line("markers", "slow: marks tests as slow (may take >5 seconds)")
    config.addinivalue_line("markers", "performance: performance benchmark tests")
    config.addinivalue_line("markers", "requires_blender: tests that require Blender to be installed")
    config.addinivalue_line("markers", "ci_skip: tests to skip in CI environment")
    config.addinivalue_line("markers", "local_only: tests that only run in local development")


@pytest.fixture
def skip_if_no_blender(blender_available: bool):
    """Skip test if Blender is not available."""
    if not blender_available:
        pytest.skip("Blender not available - install Blender or set BLENDER_EXECUTABLE env var")


@pytest.fixture
def skip_in_ci():
    """Skip test if running in CI environment."""
    if os.environ.get("CI"):
        pytest.skip("Test skipped in CI environment")


@pytest.fixture
def mock_blender_executor():
    """Mock BlenderExecutor for unit testing without Blender."""
    mock_executor = MagicMock()
    mock_executor.execute_script.return_value = {"success": True, "output": "Mock output"}
    return mock_executor


@pytest.fixture
def sample_blender_script():
    """Sample Blender Python script for testing."""
    return '''
import bpy
import sys

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TestCube"

# Add material
material = bpy.data.materials.new(name="TestMaterial")
material.use_nodes = True
cube.data.materials.append(material)

print("Test scene created successfully")
'''


@pytest.fixture
def sample_scene_data():
    """Sample scene data for testing."""
    return {
        "objects": [
            {"name": "Cube", "type": "MESH", "location": [0, 0, 0]},
            {"name": "Light", "type": "LIGHT", "location": [5, 5, 5]},
            {"name": "Camera", "type": "CAMERA", "location": [10, -10, 5]},
        ],
        "materials": ["Material1", "Material2"],
        "lights": ["Light"],
        "cameras": ["Camera"],
    }


# Test utilities
class TestHelper:
    """Helper class for common test operations."""

    @staticmethod
    def create_test_blend_file(temp_dir: Path, script: str = None) -> Path:
        """Create a test .blend file."""
        blend_path = temp_dir / "test_scene.blend"

        if script:
            # In a real implementation, this would create a blend file with the script
            # For now, just return the path
            pass

        return blend_path

    @staticmethod
    def create_test_script_file(temp_dir: Path, script: str) -> Path:
        """Create a test Python script file."""
        script_path = temp_dir / "test_script.py"
        script_path.write_text(script, encoding="utf-8")
        return script_path

    @staticmethod
    def assert_scene_structure(result: Dict[str, Any], expected_objects: int = 0):
        """Assert that scene has expected structure."""
        assert "objects" in result
        assert isinstance(result["objects"], list)
        if expected_objects > 0:
            assert len(result["objects"]) >= expected_objects

    @staticmethod
    def assert_success_response(result: Dict[str, Any]):
        """Assert that result indicates success."""
        assert "success" in result
        assert result["success"] is True


@pytest.fixture
def test_helper():
    """Fixture providing TestHelper instance."""
    return TestHelper()
