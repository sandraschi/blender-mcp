"""Unit tests for custom exception classes."""

import pytest
from blender_mcp.exceptions import (
    BlenderMCPError, BlenderNotFoundError, BlenderScriptError,
    ValidationError, ConfigurationError, TimeoutError, OperationError
)


class TestExceptionHierarchy:
    """Test the exception class hierarchy and inheritance."""

    @pytest.mark.unit
    def test_blender_mcp_error_base(self):
        """Test the base BlenderMCPError class."""
        error = BlenderMCPError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    @pytest.mark.unit
    def test_blender_not_found_error(self):
        """Test BlenderNotFoundError."""
        error = BlenderNotFoundError("Blender not found")
        assert str(error) == "Blender not found"
        assert isinstance(error, BlenderMCPError)

    @pytest.mark.unit
    def test_blender_script_error(self):
        """Test BlenderScriptError."""
        error = BlenderScriptError("Script execution failed")
        assert str(error) == "Script execution failed"
        assert isinstance(error, BlenderMCPError)

    @pytest.mark.unit
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert isinstance(error, BlenderMCPError)

    @pytest.mark.unit
    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Configuration problem")
        assert str(error) == "Configuration problem"
        assert isinstance(error, BlenderMCPError)

    @pytest.mark.unit
    def test_timeout_error(self):
        """Test TimeoutError."""
        error = TimeoutError("Operation timed out")
        assert str(error) == "Operation timed out"
        assert isinstance(error, BlenderMCPError)

    @pytest.mark.unit
    def test_operation_error(self):
        """Test OperationError."""
        error = OperationError("Operation failed")
        assert str(error) == "Operation failed"
        assert isinstance(error, BlenderMCPError)


class TestExceptionMessages:
    """Test exception message formatting and context."""

    @pytest.mark.unit
    def test_blender_script_error_with_context(self):
        """Test BlenderScriptError with additional context."""
        error = BlenderScriptError("Script failed", script_path="/path/to/script.py", exit_code=1)
        assert "Script failed" in str(error)
        assert hasattr(error, 'script_path')
        assert hasattr(error, 'exit_code')
        assert error.script_path == "/path/to/script.py"
        assert error.exit_code == 1

    @pytest.mark.unit
    def test_validation_error_with_field(self):
        """Test ValidationError with field information."""
        error = ValidationError("Invalid value", field="timeout", value=-1, expected="positive integer")
        assert "Invalid value" in str(error)
        assert hasattr(error, 'field')
        assert hasattr(error, 'value')
        assert hasattr(error, 'expected')
        assert error.field == "timeout"
        assert error.value == -1
        assert error.expected == "positive integer"

    @pytest.mark.unit
    def test_timeout_error_with_duration(self):
        """Test TimeoutError with timeout duration."""
        error = TimeoutError("Operation timed out", timeout_seconds=300, operation="render")
        assert "Operation timed out" in str(error)
        assert hasattr(error, 'timeout_seconds')
        assert hasattr(error, 'operation')
        assert error.timeout_seconds == 300
        assert error.operation == "render"


class TestExceptionChaining:
    """Test exception chaining and cause tracking."""

    @pytest.mark.unit
    def test_exception_chaining(self):
        """Test that exceptions can be chained properly."""
        root_cause = ValueError("Root cause")
        config_error = ConfigurationError("Config failed", cause=root_cause)

        assert config_error.__cause__ == root_cause
        assert isinstance(config_error.__cause__, ValueError)

    @pytest.mark.unit
    def test_nested_exception_chain(self):
        """Test nested exception chaining."""
        original_error = OSError("File not found")
        script_error = BlenderScriptError("Script failed to load", cause=original_error)
        operation_error = OperationError("Operation completely failed", cause=script_error)

        # Check the chain
        assert operation_error.__cause__ == script_error
        assert operation_error.__cause__.__cause__ == original_error
        assert isinstance(operation_error.__cause__.__cause__, OSError)
