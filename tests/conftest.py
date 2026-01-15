"""Pytest configuration and fixtures for Blender MCP tests."""

import pytest
import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_blender_process():
    """Mock Blender process for testing."""
    with pytest.mock.patch('subprocess.Popen') as mock_popen:
        mock_process = pytest.mock.MagicMock()
        mock_process.poll.return_value = None
        mock_process.wait.return_value = 0
        mock_process.communicate.return_value = (b'', b'')
        mock_process.stdout.readline.return_value = b'Blender 3.6.0'
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def sample_3d_scene():
    """Sample 3D scene data for testing."""
    return {
        "objects": [
            {
                "name": "Cube",
                "type": "MESH",
                "location": [0, 0, 0],
                "scale": [1, 1, 1]
            }
        ],
        "materials": [
            {
                "name": "Default",
                "color": [0.8, 0.8, 0.8, 1.0]
            }
        ]
    }


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing."""
    client = pytest.mock.AsyncMock()
    client.call_tool = pytest.mock.AsyncMock()
    client.read_resource = pytest.mock.AsyncMock()
    return client


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ.setdefault('BLENDER_PATH', '/usr/bin/blender')
    os.environ.setdefault('MCP_TEST_MODE', 'true')
    yield
    # Cleanup after all tests


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark slow tests
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)