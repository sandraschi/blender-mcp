"""Unit tests for utility functions and helpers."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from blender_mcp.utils.validation import (
    validate_file_path, validate_directory_path, validate_timeout,
    validate_parallel_operations, validate_render_samples, sanitize_filename
)
from blender_mcp.utils.error_handling import ErrorHandler, ErrorContext


class TestPathValidation:
    """Test path validation utility functions."""

    @pytest.mark.unit
    def test_validate_file_path_valid(self):
        """Test validation of valid file path."""
        with patch('blender_mcp.utils.validation.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_file.return_value = True
            mock_path.return_value = mock_path_instance

            result = validate_file_path("/valid/path/file.txt")
            assert result is True

    @pytest.mark.unit
    def test_validate_file_path_not_exists(self):
        """Test validation of non-existent file path."""
        with patch('blender_mcp.utils.validation.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path.return_value = mock_path_instance

            result = validate_file_path("/invalid/path/file.txt")
            assert result is False

    @pytest.mark.unit
    def test_validate_file_path_is_directory(self):
        """Test validation when path is a directory instead of file."""
        with patch('blender_mcp.utils.validation.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_file.return_value = False
            mock_path.return_value = mock_path_instance

            result = validate_file_path("/path/to/directory")
            assert result is False

    @pytest.mark.unit
    def test_validate_directory_path_valid(self):
        """Test validation of valid directory path."""
        with patch('blender_mcp.utils.validation.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_dir.return_value = True
            mock_path.return_value = mock_path_instance

            result = validate_directory_path("/valid/directory")
            assert result is True

    @pytest.mark.unit
    def test_validate_directory_path_creates_if_missing(self):
        """Test directory validation with auto-creation."""
        with patch('blender_mcp.utils.validation.Path') as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path_instance.mkdir = MagicMock()
            mock_path.return_value = mock_path_instance

            result = validate_directory_path("/new/directory", create_if_missing=True)
            assert result is True
            mock_path_instance.mkdir.assert_called_once()

    @pytest.mark.unit
    def test_validate_timeout_valid(self):
        """Test timeout validation with valid values."""
        assert validate_timeout(30) is True
        assert validate_timeout(300) is True
        assert validate_timeout(3600) is True

    @pytest.mark.unit
    def test_validate_timeout_invalid(self):
        """Test timeout validation with invalid values."""
        assert validate_timeout(10) is False  # Too low
        assert validate_timeout(4000) is False  # Too high
        assert validate_timeout(-1) is False  # Negative
        assert validate_timeout("300") is False  # Wrong type

    @pytest.mark.unit
    def test_validate_parallel_operations_valid(self):
        """Test parallel operations validation with valid values."""
        assert validate_parallel_operations(1) is True
        assert validate_parallel_operations(2) is True
        assert validate_parallel_operations(4) is True

    @pytest.mark.unit
    def test_validate_parallel_operations_invalid(self):
        """Test parallel operations validation with invalid values."""
        assert validate_parallel_operations(0) is False  # Too low
        assert validate_parallel_operations(5) is False  # Too high
        assert validate_parallel_operations(-1) is False  # Negative
        assert validate_parallel_operations("2") is False  # Wrong type

    @pytest.mark.unit
    def test_validate_render_samples_valid(self):
        """Test render samples validation with valid values."""
        assert validate_render_samples(1) is True
        assert validate_render_samples(128) is True
        assert validate_render_samples(4096) is True

    @pytest.mark.unit
    def test_validate_render_samples_invalid(self):
        """Test render samples validation with invalid values."""
        assert validate_render_samples(0) is False  # Too low
        assert validate_render_samples(5000) is False  # Too high
        assert validate_render_samples(-1) is False  # Negative
        assert validate_render_samples("128") is False  # Wrong type


class TestFilenameSanitization:
    """Test filename sanitization functions."""

    @pytest.mark.unit
    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        result = sanitize_filename("normal_filename.txt")
        assert result == "normal_filename.txt"

    @pytest.mark.unit
    def test_sanitize_filename_special_chars(self):
        """Test filename sanitization with special characters."""
        result = sanitize_filename("file:with*chars?.txt")
        assert result == "file_with_chars_.txt"

    @pytest.mark.unit
    def test_sanitize_filename_whitespace(self):
        """Test filename sanitization with whitespace."""
        result = sanitize_filename("file with spaces.txt")
        assert result == "file_with_spaces.txt"

    @pytest.mark.unit
    def test_sanitize_filename_empty(self):
        """Test filename sanitization with empty string."""
        result = sanitize_filename("")
        assert result == "untitled"

    @pytest.mark.unit
    def test_sanitize_filename_too_long(self):
        """Test filename sanitization with overly long names."""
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith("a")


class TestErrorHandling:
    """Test error handling utilities."""

    @pytest.mark.unit
    def test_error_handler_initialization(self):
        """Test ErrorHandler initialization."""
        handler = ErrorHandler()
        assert handler is not None
        assert hasattr(handler, 'handle_error')

    @pytest.mark.unit
    def test_error_context_creation(self):
        """Test ErrorContext creation and properties."""
        context = ErrorContext(
            operation="test_operation",
            parameters={"key": "value"},
            start_time=1234567890.0
        )

        assert context.operation == "test_operation"
        assert context.parameters == {"key": "value"}
        assert context.start_time == 1234567890.0

    @pytest.mark.unit
    def test_error_context_duration(self):
        """Test ErrorContext duration calculation."""
        context = ErrorContext(start_time=1000.0)
        # Mock end_time
        context.end_time = 1005.0

        assert context.duration == 5.0

    @pytest.mark.unit
    def test_error_context_to_dict(self):
        """Test ErrorContext serialization."""
        context = ErrorContext(
            operation="test_op",
            parameters={"param": "value"},
            start_time=1000.0
        )
        context.end_time = 1002.0
        context.success = True

        data = context.to_dict()
        assert data["operation"] == "test_op"
        assert data["parameters"] == {"param": "value"}
        assert data["duration"] == 2.0
        assert data["success"] is True


class TestJSONHandling:
    """Test JSON handling utilities."""

    @pytest.mark.unit
    def test_parse_json_valid(self):
        """Test parsing valid JSON."""
        json_str = '{"key": "value", "number": 42}'
        result = json.loads(json_str)
        assert result["key"] == "value"
        assert result["number"] == 42

    @pytest.mark.unit
    def test_parse_json_invalid(self):
        """Test parsing invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            json.loads("invalid json")

    @pytest.mark.unit
    def test_json_serialization(self):
        """Test JSON serialization of complex objects."""
        data = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }

        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        assert parsed == data
