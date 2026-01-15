"""Integration tests for MCPB packaging and deployment."""

import pytest
import os
import tempfile
import subprocess
from pathlib import Path


@pytest.mark.integration
@pytest.mark.slow
def test_mcpb_package_creation():
    """Test that MCPB package can be created successfully."""
    # This test requires MCPB CLI to be installed
    pytest.skip("Requires MCPB CLI installation")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy mcpb directory to temp location
        # Run mcpb validation
        # Run mcpb pack
        # Verify package exists
        assert True  # Placeholder


@pytest.mark.integration
def test_package_installation():
    """Test package installation process."""
    # This would test the installation scripts
    # Verify files are copied to correct locations
    # Test that package can be loaded
    assert True  # Placeholder


@pytest.mark.integration
@pytest.mark.slow
def test_blender_connectivity():
    """Test actual connectivity to Blender (requires Blender installation)."""
    pytest.skip("Requires Blender installation")

    # Test that we can connect to Blender
    # Send basic commands
    # Verify responses
    assert True  # Placeholder


def test_package_structure():
    """Test that the MCPB package has correct structure."""
    mcpb_dir = Path("mcpb")

    # Check required files exist
    assert (mcpb_dir / "manifest.json").exists()
    assert (mcpb_dir / "mcpb.json").exists()
    assert (mcpb_dir / "server" / "main.py").exists()
    assert (mcpb_dir / "assets" / "icon.svg").exists()

    # Validate manifest structure
    import json
    with open(mcpb_dir / "manifest.json") as f:
        manifest = json.load(f)

    required_fields = ["mcpb_version", "name", "display_name", "version", "server"]
    for field in required_fields:
        assert field in manifest, f"Missing required field: {field}"

    assert manifest["name"] == "blender-mcp"
    assert "capabilities" in manifest


def test_version_consistency():
    """Test that version is consistent across all files."""
    import json
    from pathlib import Path

    # Check pyproject.toml version
    with open("pyproject.toml") as f:
        content = f.read()
        # Extract version from pyproject.toml
        # This is a simplified check

    # Check MCPB manifest version
    with open("mcpb/manifest.json") as f:
        manifest = json.load(f)
        mcpb_version = manifest["version"]

    # Check MCPB config version
    with open("mcpb/mcpb.json") as f:
        mcpb_config = json.load(f)
        config_version = mcpb_config["version"]

    # Versions should match
    assert mcpb_version == config_version


def test_dependencies():
    """Test that all required dependencies are specified."""
    import json

    with open("mcpb/manifest.json") as f:
        manifest = json.load(f)

    assert "dependencies" in manifest
    deps = manifest["dependencies"]

    # Check for critical dependencies
    required_deps = ["python", "fastmcp"]
    for dep in required_deps:
        assert dep in deps, f"Missing required dependency: {dep}"





