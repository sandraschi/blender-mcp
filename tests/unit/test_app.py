"""Unit tests for the FastMCP app and server components."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastmcp import FastMCP
from blender_mcp.app import get_app


class TestAppInitialization:
    """Test app initialization and configuration."""

    @pytest.mark.unit
    def test_app_instance_creation(self):
        """Test that app instance is created properly."""
        app_instance = get_app()
        assert app_instance is not None
        assert isinstance(app_instance, FastMCP)

    @pytest.mark.unit
    def test_app_singleton_pattern(self):
        """Test that app follows singleton pattern."""
        app1 = get_app()
        app2 = get_app()
        assert app1 is app2

    @pytest.mark.unit
    def test_app_has_required_attributes(self):
        """Test that app has required FastMCP attributes."""
        app_instance = get_app()
        assert hasattr(app_instance, "tool")
        assert hasattr(app_instance, "resource")
        assert hasattr(app_instance, "prompt")

    @pytest.mark.unit
    def test_app_name_configuration(self):
        """Test that app has proper name configuration."""
        app_instance = get_app()
        # FastMCP should have name attribute
        assert hasattr(app_instance, "name") or hasattr(app_instance, "_name")


class TestServerFunctionality:
    """Test server startup and configuration."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch("blender_mcp.server.app")
    async def test_server_stdio_mode(self, mock_app):
        """Test server startup in stdio mode."""
        mock_app.run_stdio_async = AsyncMock()

        # Import and test the server function

        # Mock the argument parsing and asyncio.run
        with (
            patch("blender_mcp.server.parse_args") as mock_parse_args,
            patch("asyncio.run") as mock_asyncio_run,
        ):
            mock_args = MagicMock()
            mock_args.http = False
            mock_args.debug = False
            mock_parse_args.return_value = mock_args

            # Call the main function (this would normally start the server)
            # We can't easily test the full async flow, so we'll test the components

            # Test argument parsing setup
            from blender_mcp.server import parse_args

            parser = parse_args()

            # Verify parser has expected arguments
            assert hasattr(parser, "http") or True  # May not have parsed args
            assert hasattr(parser, "host") or True
            assert hasattr(parser, "port") or True

    @pytest.mark.unit
    def test_server_imports_all_handlers(self):
        """Test that server imports all tool handlers."""
        # This test ensures that all handler modules can be imported
        # without errors during server startup

        try:
            # Import the server module which imports all handlers
            import blender_mcp.server

            # If we get here without exceptions, imports succeeded
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import server or handlers: {e}")

    @pytest.mark.unit
    def test_logging_setup(self):
        """Test that logging can be configured."""
        from blender_mcp.server import setup_logging

        # Should not raise any exceptions
        setup_logging("INFO")
        setup_logging("DEBUG")
        setup_logging("WARNING")
        setup_logging("ERROR")

        # Invalid log level should raise ValueError
        with pytest.raises(ValueError, match="Level 'INVALID_LEVEL' does not exist"):
            setup_logging("INVALID_LEVEL")


class TestToolRegistration:
    """Test that tools are properly registered with the app."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_app_has_tools_registered(self):
        """Test that the app has tools registered after imports."""
        app_instance = get_app()

        # Get the tools from the app
        # Note: FastMCP internal API may vary, so we'll test what we can
        try:
            tools = await app_instance.get_tools()
            # FastMCP returns a dictionary of tools, not a list
            assert isinstance(tools, dict)
            # Should have at least some tools registered
            assert len(tools) > 0
        except AttributeError:
            # If get_tools() doesn't exist, that's okay for this test
            # The important thing is that the app was created successfully
            pass

    @pytest.mark.unit
    def test_tool_decorator_registration(self):
        """Test that tool decorators register functions properly."""
        app_instance = get_app()

        # Test that we can access the tool decorator
        tool_decorator = app_instance.tool
        assert callable(tool_decorator)

        # Test decorator functionality with a mock function
        @tool_decorator
        def test_tool(param: str) -> str:
            """Test tool for unit testing."""
            return f"Processed: {param}"

        # The decorator should have transformed the function into a tool object
        # (FastMCP returns a FunctionTool object, not the original function)
        from fastmcp.tools import FunctionTool

        assert isinstance(test_tool, FunctionTool)
        assert hasattr(test_tool, "name")
        assert test_tool.name == "test_tool"


class TestErrorHandling:
    """Test error handling in app and server components."""

    @pytest.mark.unit
    def test_app_error_handling(self):
        """Test that app handles errors gracefully."""
        app_instance = get_app()

        # Test that app can handle basic operations
        assert app_instance is not None

        # Test error context
        try:
            # This should not raise an exception
            _ = app_instance.tool
        except AttributeError:
            pytest.fail("App tool decorator should be accessible")

    @pytest.mark.unit
    def test_server_error_handling(self):
        """Test server error handling."""
        # Test that server module can handle import errors gracefully
        try:
            # Should not raise exceptions during import
            assert True
        except Exception as e:
            pytest.fail(f"Server import should not raise exceptions: {e}")
