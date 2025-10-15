"""Unit tests for utility functions and helpers."""

import pytest
import json
from blender_mcp.utils.validation import (
    validate_object_exists,
    validate_vertex_group,
    validate_frame_range,
    validate_positive,
    validate_range,
)
from blender_mcp.utils.error_handling import MCPError, ValidationError, BlenderOperationError


class TestObjectValidation:
    """Test Blender object validation functions."""

    @pytest.mark.unit
    def test_validate_object_exists_success(self):
        """Test object validation when bpy is not available (should skip)."""
        # Since bpy is not available in unit tests, this should not raise
        validate_object_exists("TestObject")

    @pytest.mark.unit
    def test_validate_vertex_group_success(self):
        """Test vertex group validation when bpy is not available."""
        # Should not raise when bpy is not available
        validate_vertex_group("TestObject", "TestGroup")

    @pytest.mark.unit
    def test_validate_frame_range_valid(self):
        """Test frame range validation with valid ranges."""
        # Should not raise for valid ranges
        validate_frame_range(1, 10)
        validate_frame_range(100, 200)

    @pytest.mark.unit
    def test_validate_frame_range_invalid_start(self):
        """Test frame range validation with invalid start frame."""
        with pytest.raises(ValueError, match="Start frame must be at least 1"):
            validate_frame_range(0, 10)

    @pytest.mark.unit
    def test_validate_frame_range_invalid_end(self):
        """Test frame range validation with end before start."""
        with pytest.raises(
            ValueError, match="End frame must be greater than or equal to start frame"
        ):
            validate_frame_range(10, 5)

    @pytest.mark.unit
    def test_validate_positive_valid(self):
        """Test positive value validation."""
        # Should not raise for positive values
        validate_positive("test_param", 1.0)
        validate_positive("test_param", 0.1)
        validate_positive("test_param", 100)

    @pytest.mark.unit
    def test_validate_positive_zero(self):
        """Test positive value validation with zero."""
        with pytest.raises(ValueError):
            validate_positive("test_param", 0)

    @pytest.mark.unit
    def test_validate_positive_negative(self):
        """Test positive value validation with negative values."""
        with pytest.raises(ValueError):
            validate_positive("test_param", -1.0)

    @pytest.mark.unit
    def test_validate_range_valid(self):
        """Test range validation with valid values."""
        # Should not raise for values in range
        validate_range("test_param", 5.0, 0.0, 10.0)
        validate_range("test_param", 0.0, 0.0, 10.0)
        validate_range("test_param", 10.0, 0.0, 10.0)

    @pytest.mark.unit
    def test_validate_range_below_min(self):
        """Test range validation with value below minimum."""
        with pytest.raises(ValueError):
            validate_range("test_param", -1.0, 0.0, 10.0)

    @pytest.mark.unit
    def test_validate_range_above_max(self):
        """Test range validation with value above maximum."""
        with pytest.raises(ValueError):
            validate_range("test_param", 15.0, 0.0, 10.0)


class TestErrorHandling:
    """Test error handling utilities."""

    @pytest.mark.unit
    def test_mcp_error_creation(self):
        """Test MCPError creation."""
        error = MCPError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details == {}

    @pytest.mark.unit
    def test_mcp_error_with_details(self):
        """Test MCPError with details."""
        details = {"code": "TEST_ERROR", "operation": "test"}
        error = MCPError("Test error", details=details)
        assert error.details == details

    @pytest.mark.unit
    def test_validation_error_creation(self):
        """Test ValidationError creation."""
        error = ValidationError("Invalid input")
        assert "Validation error: Invalid input" in str(error)
        assert isinstance(error, MCPError)

    @pytest.mark.unit
    def test_blender_operation_error_creation(self):
        """Test BlenderOperationError creation."""
        error = BlenderOperationError("Failed to create object")
        assert "Blender operation failed: Failed to create object" in str(error)
        assert isinstance(error, MCPError)


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
            "object": {"nested": "value"},
        }

        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        assert parsed == data
