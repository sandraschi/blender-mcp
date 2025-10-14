"""Unit tests for configuration and validation functions."""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from blender_mcp.config import (
    BLENDER_EXECUTABLE, validate_blender_executable,
    get_blender_version, validate_config
)
from blender_mcp.exceptions import BlenderNotFoundError, ValidationError


class TestBlenderValidation:
    """Test Blender executable validation functions."""

    @pytest.mark.unit
    def test_validate_blender_executable_success(self):
        """Test validation when Blender executable exists and is valid."""
        with patch('blender_mcp.config.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_file.return_value = True
            mock_path.return_value = mock_path_instance

            result = validate_blender_executable()
            assert result is True

    @pytest.mark.unit
    def test_validate_blender_executable_not_found(self):
        """Test validation when Blender executable doesn't exist."""
        with patch('blender_mcp.config.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path.return_value = mock_path_instance

            result = validate_blender_executable()
            assert result is False

    @pytest.mark.unit
    def test_validate_blender_executable_not_file(self):
        """Test validation when path exists but is not a file."""
        with patch('blender_mcp.config.Path') as mock_path:
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


class TestBlenderVersion:
    """Test Blender version detection functions."""

    @pytest.mark.unit
    def test_get_blender_version_success(self, mock_blender_executor):
        """Test successful version detection."""
        mock_blender_executor.execute_script.return_value = {
            "success": True,
            "output": "Blender 4.4.0"
        }

        with patch('blender_mcp.config.get_blender_executor') as mock_get_executor:
            mock_get_executor.return_value = mock_blender_executor

            version = get_blender_version()
            assert version == "4.4.0"

    @pytest.mark.unit
    def test_get_blender_version_no_executor(self):
        """Test version detection when executor creation fails."""
        with patch('blender_mcp.config.get_blender_executor') as mock_get_executor:
            mock_get_executor.return_value = None

            with pytest.raises(BlenderNotFoundError):
                get_blender_version()

    @pytest.mark.unit
    def test_get_blender_version_script_failure(self, mock_blender_executor):
        """Test version detection when script execution fails."""
        mock_blender_executor.execute_script.return_value = {
            "success": False,
            "error": "Script execution failed"
        }

        with patch('blender_mcp.config.get_blender_executor') as mock_get_executor:
            mock_get_executor.return_value = mock_blender_executor

            with pytest.raises(BlenderNotFoundError):
                get_blender_version()


class TestConfigValidation:
    """Test configuration validation functions."""

    @pytest.mark.unit
    def test_validate_config_valid(self):
        """Test validation of valid configuration."""
        config = {
            "blender_executable": "C:\\Program Files\\Blender\\blender.exe",
            "operation_timeout": 300,
            "max_parallel_operations": 2,
            "enable_gpu_rendering": True,
            "render_samples": 128,
            "temp_directory": "C:\\temp\\blender-mcp",
            "log_level": "INFO",
            "enable_performance_monitoring": False,
            "backup_blend_files": True,
        }

        # Should not raise any exceptions
        validate_config(config)

    @pytest.mark.unit
    def test_validate_config_invalid_timeout(self):
        """Test validation with invalid timeout value."""
        config = {
            "blender_executable": "C:\\Program Files\\Blender\\blender.exe",
            "operation_timeout": -1,  # Invalid negative timeout
        }

        with pytest.raises(ValidationError):
            validate_config(config)

    @pytest.mark.unit
    def test_validate_config_invalid_parallel_ops(self):
        """Test validation with invalid parallel operations value."""
        config = {
            "blender_executable": "C:\\Program Files\\Blender\\blender.exe",
            "max_parallel_operations": 10,  # Too many parallel operations
        }

        with pytest.raises(ValidationError):
            validate_config(config)

    @pytest.mark.unit
    def test_validate_config_invalid_log_level(self):
        """Test validation with invalid log level."""
        config = {
            "blender_executable": "C:\\Program Files\\Blender\\blender.exe",
            "log_level": "INVALID_LEVEL",
        }

        with pytest.raises(ValidationError):
            validate_config(config)

    @pytest.mark.unit
    def test_validate_config_missing_required(self):
        """Test validation with missing required fields."""
        config = {
            "operation_timeout": 300,
            # Missing blender_executable
        }

        with pytest.raises(ValidationError):
            validate_config(config)

    @pytest.mark.unit
    def test_validate_config_invalid_temp_dir(self):
        """Test validation with invalid temp directory."""
        config = {
            "blender_executable": "C:\\Program Files\\Blender\\blender.exe",
            "temp_directory": "",  # Empty temp directory
        }

        with pytest.raises(ValidationError):
            validate_config(config)
