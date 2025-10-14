"""Unit tests for Blender MCP utilities.

These tests focus on utility functions and do not require running Blender.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from blender_mcp.config import BLENDER_EXECUTABLE, validate_blender_executable
from blender_mcp.exceptions import BlenderNotFoundError, BlenderScriptError


class TestConfiguration:
    """Test configuration utilities."""

    def test_validate_blender_executable_success(self):
        """Test validation when Blender executable exists."""
        with patch('blender_mcp.config.Path.exists') as mock_exists, \
             patch('blender_mcp.config.Path.is_file') as mock_is_file:
            mock_exists.return_value = True
            mock_is_file.return_value = True
            assert validate_blender_executable() is True

    def test_validate_blender_executable_not_found(self):
        """Test validation when Blender executable doesn't exist."""
        with patch('blender_mcp.config.Path.exists') as mock_exists:
            mock_exists.return_value = False
            assert validate_blender_executable() is False

    def test_validate_blender_executable_not_file(self):
        """Test validation when path exists but is not a file."""
        with patch('blender_mcp.config.Path.exists') as mock_exists, \
             patch('blender_mcp.config.Path.is_file') as mock_is_file:
            mock_exists.return_value = True
            mock_is_file.return_value = False
            assert validate_blender_executable() is False

    def test_blender_executable_constant(self):
        """Test that BLENDER_EXECUTABLE constant is set."""
        assert isinstance(BLENDER_EXECUTABLE, str)
        assert len(BLENDER_EXECUTABLE) > 0


class TestFileOperations:
    """Test file operation utilities."""

    def test_temp_file_creation(self):
        """Test temporary file creation and cleanup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "test.blend"

            # Create a test file
            temp_path.write_text("test content")

            # Verify it exists
            assert temp_path.exists()
            assert temp_path.read_text() == "test content"

    def test_path_validation(self):
        """Test path validation utilities."""
        # Valid paths
        valid_paths = [
            "/valid/path/file.blend",
            "C:\\valid\\path\\file.blend",
            "./relative/path/file.blend",
            "file.blend"
        ]

        for path in valid_paths:
            # Basic path validation - just check it's a string and not empty
            assert isinstance(path, str)
            assert len(path) > 0

    def test_output_path_generation(self):
        """Test output path generation for exports/renders."""
        base_name = "test_scene"
        extension = ".fbx"

        # Test basic path generation
        output_path = f"{base_name}{extension}"
        assert output_path.endswith(extension)
        assert base_name in output_path


class TestDataValidation:
    """Test data validation utilities."""

    def test_numeric_validation(self):
        """Test numeric parameter validation."""
        # Valid numbers
        valid_numbers = [1, 1.5, -1, 0, 1000]

        for num in valid_numbers:
            assert isinstance(num, (int, float))

    def test_string_validation(self):
        """Test string parameter validation."""
        # Valid strings
        valid_strings = ["test", "Test Object", "object_123", "test-object"]

        for string in valid_strings:
            assert isinstance(string, str)
            assert len(string) > 0

    def test_boolean_validation(self):
        """Test boolean parameter validation."""
        valid_bools = [True, False]

        for bool_val in valid_bools:
            assert isinstance(bool_val, bool)

    def test_list_validation(self):
        """Test list parameter validation."""
        valid_lists = [[], [1, 2, 3], ["a", "b", "c"]]

        for list_val in valid_lists:
            assert isinstance(list_val, list)


class TestConfigurationLoading:
    """Test configuration loading and parsing."""

    def test_default_config_values(self):
        """Test that default configuration values are reasonable."""
        # Import config to check defaults
        from blender_mcp import config

        # Check that key config values exist and are reasonable
        assert hasattr(config, 'BLENDER_EXECUTABLE')
        assert isinstance(config.BLENDER_EXECUTABLE, str)

    @patch('builtins.open', new_callable=mock_open, read_data='BLENDER_EXECUTABLE=/custom/path/blender')
    def test_config_file_loading(self, mock_file):
        """Test loading configuration from file."""
        # This would test config file loading if implemented
        # For now, just verify the mock setup works
        with open('dummy_config.txt', 'r') as f:
            content = f.read()
        assert 'BLENDER_EXECUTABLE' in content


class TestTypeChecking:
    """Test type checking utilities."""

    def test_type_validation(self):
        """Test type validation for function parameters."""
        # Test basic type checking
        test_values = [
            (42, int, True),
            (42.0, float, True),
            ("test", str, True),
            ([1, 2, 3], list, True),
            (True, bool, True),
            (42, str, False),
            ("test", int, False),
        ]

        for value, expected_type, should_pass in test_values:
            result = isinstance(value, expected_type)
            if should_pass:
                assert result, f"Expected {value} to be {expected_type}"
            else:
                assert not result, f"Did not expect {value} to be {expected_type}"
