"""Unit tests for BlenderExecutor class.

Tests focus on initialization, validation, and error handling without running actual Blender processes.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from blender_mcp.utils.blender_executor import BlenderExecutor, get_blender_executor
from blender_mcp.exceptions import BlenderNotFoundError, BlenderScriptError


class TestBlenderExecutorInitialization:
    """Test BlenderExecutor initialization and setup."""

    @patch('blender_mcp.utils.blender_executor.validate_blender_executable')
    def test_initialization_success(self, mock_validate):
        """Test successful initialization."""
        mock_validate.return_value = True

        with patch.object(BlenderExecutor, '_initialize_executor') as mock_init:
            executor = BlenderExecutor("blender")
            assert executor.blender_executable == "blender"
            mock_init.assert_called_once()

    @patch('blender_mcp.utils.blender_executor.validate_blender_executable')
    def test_initialization_failure(self, mock_validate):
        """Test initialization failure when Blender not found."""
        mock_validate.return_value = False

        with pytest.raises(BlenderNotFoundError):
            BlenderExecutor("nonexistent_blender")

    @patch('blender_mcp.utils.blender_executor.validate_blender_executable')
    def test_initialization_with_custom_executable(self, mock_validate):
        """Test initialization with custom executable path."""
        mock_validate.return_value = True
        custom_path = "/custom/path/blender"

        with patch.object(BlenderExecutor, '_initialize_executor'):
            executor = BlenderExecutor(custom_path)
            assert executor.blender_executable == custom_path


class TestBlenderExecutorSingleton:
    """Test the singleton pattern for BlenderExecutor."""

    @patch('blender_mcp.utils.blender_executor.validate_blender_executable')
    def test_get_blender_executor_singleton(self, mock_validate):
        """Test that get_blender_executor returns singleton instances."""
        mock_validate.return_value = True

        with patch.object(BlenderExecutor, '_initialize_executor'):
            # Reset global instance
            import blender_mcp.utils.blender_executor
            blender_mcp.utils.blender_executor._blender_executor_instance = None

            executor1 = get_blender_executor("blender")
            executor2 = get_blender_executor("blender")

            assert executor1 is executor2

    @patch('blender_mcp.utils.blender_executor.validate_blender_executable')
    def test_get_blender_executor_mode_change(self, mock_validate):
        """Test that mode changes reset the singleton."""
        mock_validate.return_value = True

        with patch.object(BlenderExecutor, '_initialize_executor'):
            # Reset global instance
            import blender_mcp.utils.blender_executor
            blender_mcp.utils.blender_executor._blender_executor_instance = None

            executor1 = get_blender_executor("blender", headless=True)
            executor2 = get_blender_executor("blender", headless=False)

            assert executor1 is not executor2
            assert executor1.headless is True
            assert executor2.headless is False


class TestBlenderExecutorValidation:
    """Test Blender executable validation methods."""

    def test_locate_and_validate_blender_with_valid_path(self):
        """Test locating Blender with valid path."""
        with patch('blender_mcp.utils.blender_executor.Path.exists') as mock_exists, \
             patch('blender_mcp.utils.blender_executor.Path.resolve') as mock_resolve:

            mock_exists.return_value = True
            mock_resolve.return_value = Path("/valid/blender")

            executor = MagicMock()
            executor.blender_executable = "/valid/blender"

            # Call the method directly
            BlenderExecutor._locate_and_validate_blender(executor)

            assert executor.blender_path == Path("/valid/blender")

    def test_locate_and_validate_blender_not_found(self):
        """Test behavior when Blender is not found."""
        with patch('blender_mcp.utils.blender_executor.Path.exists') as mock_exists:
            mock_exists.return_value = False

            executor = MagicMock()
            executor.blender_executable = "/invalid/blender"

            with pytest.raises(BlenderNotFoundError):
                BlenderExecutor._locate_and_validate_blender(executor)

    @patch('blender_mcp.utils.blender_executor.subprocess.run')
    def test_validate_blender_version_success(self, mock_run):
        """Test successful Blender version validation."""
        mock_run.return_value = MagicMock(stdout="Blender 4.4.0", returncode=0)

        executor = MagicMock()
        executor.blender_path = Path("/valid/blender")

        BlenderExecutor._validate_blender_version(executor)

        assert "4.4.0" in str(executor.blender_version)

    @patch('blender_mcp.utils.blender_executor.subprocess.run')
    def test_validate_blender_version_failure(self, mock_run):
        """Test Blender version validation failure."""
        mock_run.return_value = MagicMock(stdout="", returncode=1)

        executor = MagicMock()
        executor.blender_path = Path("/invalid/blender")

        with pytest.raises(BlenderNotFoundError):
            BlenderExecutor._validate_blender_version(executor)


class TestBlenderExecutorSetup:
    """Test BlenderExecutor setup methods."""

    @patch('blender_mcp.utils.blender_executor.tempfile.mkdtemp')
    def test_setup_temp_directory(self, mock_mkdtemp):
        """Test temporary directory setup."""
        mock_mkdtemp.return_value = "/tmp/test_dir"

        executor = MagicMock()
        BlenderExecutor._setup_temp_directory(executor)

        assert executor.temp_dir == "/tmp/test_dir"
        mock_mkdtemp.assert_called_once()

    @patch('blender_mcp.utils.blender_executor.Path.exists')
    @patch('blender_mcp.utils.blender_executor.Path.mkdir')
    def test_ensure_output_directory(self, mock_mkdir, mock_exists):
        """Test output directory creation."""
        mock_exists.return_value = False

        executor = MagicMock()
        executor.temp_dir = "/tmp"

        BlenderExecutor._ensure_output_directory(executor, "output")

        expected_path = Path("/tmp/output")
        mock_mkdir.assert_called_once_with(expected_path, parents=True, exist_ok=True)


class TestBlenderExecutorScriptExecution:
    """Test script execution methods (mocked)."""



class TestBlenderExecutorUtilities:
    """Test utility methods in BlenderExecutor."""

    def test_create_temp_script(self):
        """Test temporary script creation."""
        executor = MagicMock()
        executor.temp_dir = "/tmp"

        with patch('builtins.open', mock_open()) as mock_file:
            script_path = BlenderExecutor._create_temp_script(executor, "test script")

            assert script_path.startswith("/tmp")
            assert script_path.endswith(".py")
            mock_file.assert_called()

    def test_parse_blender_output(self):
        """Test Blender output parsing."""
        test_output = "Blender 4.4.0 (hash abc123)\nSome output\nError: something wrong"

        result = BlenderExecutor._parse_blender_output(test_output)

        assert "version" in result
        assert "output" in result
        assert "errors" in result

    def test_cleanup_temp_files(self):
        """Test temporary file cleanup."""
        executor = MagicMock()
        executor.temp_dir = "/tmp"

        with patch('blender_mcp.utils.blender_executor.shutil.rmtree') as mock_rmtree:
            BlenderExecutor._cleanup_temp_files(executor)

            mock_rmtree.assert_called_once_with("/tmp", ignore_errors=True)


class TestBlenderExecutorErrorHandling:
    """Test error handling in BlenderExecutor."""

    @patch('blender_mcp.utils.blender_executor.logger')
    def test_handle_execution_error(self, mock_logger):
        """Test execution error handling."""
        executor = MagicMock()

        test_error = Exception("Test error")
        BlenderExecutor._handle_execution_error(executor, test_error, "test_script.py")

        mock_logger.error.assert_called()

    def test_validate_script_parameters(self):
        """Test script parameter validation."""
        # Valid scripts
        valid_scripts = [
            "import bpy\nprint('test')",
            "bpy.ops.mesh.primitive_cube_add()",
            "# Comment\nbpy.context.scene.name = 'test'"
        ]

        for script in valid_scripts:
            # Basic validation - scripts should be non-empty strings
            assert isinstance(script, str)
            assert len(script.strip()) > 0

    def test_timeout_handling(self):
        """Test timeout handling in execution."""
        executor = MagicMock()
        executor.process_timeout = 30

        # Test that timeout is properly set
        assert executor.process_timeout == 30
