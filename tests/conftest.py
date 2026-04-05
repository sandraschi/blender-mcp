"""
Shared pytest configuration and fixtures for blender-mcp tests.

All tests in this directory use mocked executors — no live Blender required.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure src is on the path regardless of how pytest is invoked
_SRC = Path(__file__).parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# ---------------------------------------------------------------------------
# Event loop — single session-scoped loop for all async tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def event_loop():
    """Session-scoped event loop so async fixtures can be shared."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """Set test-mode env vars before any test runs."""
    os.environ.setdefault("MCP_TEST_MODE", "true")
    os.environ.setdefault("BLENDER_EXECUTABLE", "/usr/bin/blender")  # placeholder, won't be called
    yield


# ---------------------------------------------------------------------------
# Mock executor factory
# ---------------------------------------------------------------------------

def make_mock_executor(output: str = "") -> MagicMock:
    """Return a mock BlenderExecutor whose execute_script returns *output*."""
    executor = MagicMock()
    executor.execute_script = AsyncMock(return_value=output)
    return executor


@pytest.fixture
def mock_executor():
    """Plain mock executor with empty output — override per-test as needed."""
    return make_mock_executor("")


# ---------------------------------------------------------------------------
# Mock FastMCP Context (for sampling tests)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_ctx():
    """Mock FastMCP Context that returns an empty sampling result."""
    ctx = MagicMock()
    sample_result = MagicMock()
    sample_result.content = ""
    ctx.sample = AsyncMock(return_value=sample_result)
    return ctx


# ---------------------------------------------------------------------------
# Temp repository directory
# ---------------------------------------------------------------------------

@pytest.fixture
def repo_dir(tmp_path: Path) -> Path:
    """Isolated repository base dir for each test."""
    d = tmp_path / "repository"
    d.mkdir(parents=True)
    return d


@pytest.fixture(autouse=True)
def patch_repo_paths(repo_dir: Path, monkeypatch):
    """
    Redirect REPO_BASE and INDEX_FILE in repository_tools to the temp dir.
    Applied automatically to every test that uses repo_dir (it's autouse but
    depends on repo_dir fixture so only activates when repo_dir is in scope).
    """
    try:
        import blender_mcp.tools.repository_tools as rt
        monkeypatch.setattr(rt, "REPO_BASE", repo_dir)
        monkeypatch.setattr(rt, "INDEX_FILE", repo_dir / "repository_index.json")
    except ImportError:
        pass  # module not yet importable in some test contexts


# ---------------------------------------------------------------------------
# pytest markers
# ---------------------------------------------------------------------------

def pytest_configure(config):
    config.addinivalue_line("markers", "integration: requires live Blender")
    config.addinivalue_line("markers", "slow: long-running test")
    config.addinivalue_line("markers", "sampling: requires MCP sampling-capable client")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
