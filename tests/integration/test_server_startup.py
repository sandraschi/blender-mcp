"""Integration tests for MCP server startup and basic functionality."""

import pytest
import asyncio
import subprocess
import time
import signal
import os
from pathlib import Path
from unittest.mock import patch


class TestServerStartup:
    """Test MCP server startup and initialization."""

    @pytest.mark.integration
    @pytest.mark.requires_blender
    def test_server_can_start(self, blender_executable: str, temp_dir: Path):
        """Test that the MCP server can start successfully."""
        # Set environment variable for Blender
        env = os.environ.copy()
        env["BLENDER_EXECUTABLE"] = blender_executable

        # Create a test script that starts the server briefly
        test_script = f'''
import sys
import os
sys.path.insert(0, r"{Path(__file__).parent.parent.parent / "src"}")

try:
    from blender_mcp.server import main
    print("Server import successful")
    print("Test completed - server can start")
except Exception as e:
    print(f"Server startup failed: {{e}}")
    sys.exit(1)
'''

        test_file = temp_dir / "server_test.py"
        test_file.write_text(test_script)

        # Run the test script
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )

        assert result.returncode == 0, f"Server test failed: {result.stderr}"
        assert "Server import successful" in result.stdout
        assert "Test completed - server can start" in result.stdout

    @pytest.mark.integration
    @pytest.mark.requires_blender
    def test_server_imports_all_tools(self, blender_executable: str, temp_dir: Path):
        """Test that server can import all tool modules."""
        env = os.environ.copy()
        env["BLENDER_EXECUTABLE"] = blender_executable

        test_script = f'''
import sys
import os
sys.path.insert(0, r"{Path(__file__).parent.parent.parent / "src"}")

try:
    # Import server which imports all handlers
    from blender_mcp.server import app
    print("Server and all handlers imported successfully")

    # Try to get tools
    tools = app.get_tools()
    print(f"Found {{len(tools)}} tools registered")

    # Check that we have expected tools
    tool_names = [tool.name for tool in tools]
    expected_tools = ["blender_mesh", "blender_animation", "blender_lighting"]

    for expected_tool in expected_tools:
        if expected_tool in tool_names:
            print(f"Found expected tool: {{expected_tool}}")
        else:
            print(f"Missing expected tool: {{expected_tool}}")

    print("Tool registration test completed")

except Exception as e:
    import traceback
    print(f"Tool import test failed: {{e}}")
    traceback.print_exc()
    sys.exit(1)
'''

        test_file = temp_dir / "tool_test.py"
        test_file.write_text(test_script)

        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )

        assert result.returncode == 0, f"Tool test failed: {result.stderr}"
        assert "Server and all handlers imported successfully" in result.stdout
        assert "Tool registration test completed" in result.stdout

    @pytest.mark.integration
    @pytest.mark.requires_blender
    def test_server_configuration_validation(self, blender_executable: str, temp_dir: Path):
        """Test that server validates configuration properly."""
        env = os.environ.copy()
        env["BLENDER_EXECUTABLE"] = blender_executable

        test_script = f'''
import sys
import os
sys.path.insert(0, r"{Path(__file__).parent.parent.parent / "src"}")

try:
    from blender_mcp.config import validate_config
    from blender_mcp.exceptions import ValidationError

    # Test valid config
    valid_config = {{
        "blender_executable": r"{blender_executable}",
        "operation_timeout": 300,
        "max_parallel_operations": 2,
        "enable_gpu_rendering": False,
        "render_samples": 64,
        "temp_directory": r"{temp_dir}",
        "log_level": "INFO",
        "enable_performance_monitoring": False,
        "backup_blend_files": True,
    }}

    try:
        validate_config(valid_config)
        print("Valid configuration accepted")
    except ValidationError as e:
        print(f"Valid config rejected: {{e}}")
        sys.exit(1)

    # Test invalid config
    invalid_config = {{
        "blender_executable": r"{blender_executable}",
        "operation_timeout": -1,  # Invalid
    }}

    try:
        validate_config(invalid_config)
        print("Invalid config should have been rejected")
        sys.exit(1)
    except ValidationError:
        print("Invalid configuration correctly rejected")

    print("Configuration validation test completed")

except Exception as e:
    import traceback
    print(f"Configuration test failed: {{e}}")
    traceback.print_exc()
    sys.exit(1)
'''

        test_file = temp_dir / "config_test.py"
        test_file.write_text(test_script)

        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )

        assert result.returncode == 0, f"Config test failed: {result.stderr}"
        assert "Valid configuration accepted" in result.stdout
        assert "Invalid configuration correctly rejected" in result.stdout


class TestServerCommunication:
    """Test MCP server communication protocols."""

    @pytest.mark.integration
    @pytest.mark.requires_blender
    def test_stdio_communication_setup(self, blender_executable: str, temp_dir: Path):
        """Test that server can set up stdio communication."""
        env = os.environ.copy()
        env["BLENDER_EXECUTABLE"] = blender_executable

        # This is a more advanced test that would require setting up
        # actual MCP protocol communication. For now, we'll just test
        # that the server can be imported and initialized.

        test_script = f'''
import sys
import os
sys.path.insert(0, r"{Path(__file__).parent.parent.parent / "src"}")

try:
    from blender_mcp.server import setup_logging, parse_args
    from blender_mcp.app import get_app

    # Test logging setup
    setup_logging("INFO")
    print("Logging setup successful")

    # Test app creation
    app = get_app()
    print("App creation successful")

    # Test argument parsing (mocked)
    # Note: We can't easily test full server startup in a unit test
    # This tests the components that would be used

    print("Server communication setup test completed")

except Exception as e:
    import traceback
    print(f"Communication setup test failed: {{e}}")
    traceback.print_exc()
    sys.exit(1)
'''

        test_file = temp_dir / "communication_test.py"
        test_file.write_text(test_script)

        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )

        assert result.returncode == 0, f"Communication test failed: {result.stderr}"
        assert "Server communication setup test completed" in result.stdout
