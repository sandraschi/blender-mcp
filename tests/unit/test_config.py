"""Unit tests for configuration and validation functions."""

import pytest
import os
from unittest.mock import patch, MagicMock
from blender_mcp.config import BLENDER_EXECUTABLE, validate_blender_executable


class TestBlenderValidation:
    """Test Blender executable validation functions."""

    @pytest.mark.unit
    def test_validate_blender_executable_success(self):
        """Test validation when Blender executable exists and is valid."""
        with patch("blender_mcp.config.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_file.return_value = True
            mock_path.return_value = mock_path_instance

            result = validate_blender_executable()
            assert result is True

    @pytest.mark.unit
    def test_validate_blender_executable_not_found(self):
        """Test validation when Blender executable doesn't exist."""
        with patch("blender_mcp.config.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path.return_value = mock_path_instance

            result = validate_blender_executable()
            assert result is False

    @pytest.mark.unit
    def test_validate_blender_executable_not_file(self):
        """Test validation when path exists but is not a file."""
        with patch("blender_mcp.config.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_file.return_value = False
            mock_path.return_value = mock_path_instance

            result = validate_blender_executable()
            assert result is False

    @pytest.mark.unit
    def test_blender_executable_constant(self):
        """Test that BLENDER_EXECUTABLE constant is properly set."""
        assert isinstance(BLENDER_EXECUTABLE, str)
        assert len(BLENDER_EXECUTABLE) > 0
        # Should be a reasonable default path
        assert "blender" in BLENDER_EXECUTABLE.lower()


class TestBlenderExecutableConstant:
    """Test Blender executable constant."""

    @pytest.mark.unit
    def test_blender_executable_constant(self):
        """Test that BLENDER_EXECUTABLE constant is set."""
        assert isinstance(BLENDER_EXECUTABLE, str)
        assert len(BLENDER_EXECUTABLE) > 0
        # Should contain 'blender' in the path
        assert "blender" in BLENDER_EXECUTABLE.lower()

    @pytest.mark.unit
    def test_blender_executable_from_env(self):
        """Test that BLENDER_EXECUTABLE uses environment variable when set."""
        with patch.dict(os.environ, {"BLENDER_EXECUTABLE": "/custom/blender/path"}):
            # Need to reload the module to pick up new env var
            from importlib import reload
            import blender_mcp.config

            reload(blender_mcp.config)
            assert blender_mcp.config.BLENDER_EXECUTABLE == "/custom/blender/path"
