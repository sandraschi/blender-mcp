"""Configuration settings for the Blender MCP server."""

import logging
import os
import sys
from pathlib import Path

from blender_mcp.compat import *

logger = logging.getLogger(__name__)

# Default Blender executable path
DEFAULT_BLENDER_EXECUTABLE = "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe"

# Get Blender executable from environment variable or use default
BLENDER_EXECUTABLE: str = os.environ.get("BLENDER_EXECUTABLE", DEFAULT_BLENDER_EXECUTABLE)


# Validate Blender executable
def validate_blender_executable() -> bool:
    """Check if the Blender executable exists and is accessible.

from ..compat import *

    Returns:
        bool: True if the Blender executable is valid, False otherwise
    """
    if not BLENDER_EXECUTABLE:
        return False

    blender_path = Path(BLENDER_EXECUTABLE)
    return blender_path.exists() and blender_path.is_file()


# Configuration validation
def validate_config(config: dict) -> None:
    """Validate configuration parameters.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If configuration is invalid
    """
    required_keys = ["blender_executable", "operation_timeout", "max_parallel_operations"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

    # Validate operation_timeout
    if config.get("operation_timeout", 0) <= 0:
        raise ValueError("operation_timeout must be positive")

    # Validate max_parallel_operations
    if config.get("max_parallel_operations", 0) <= 0:
        raise ValueError("max_parallel_operations must be positive")

    # Validate blender_executable if provided
    if "blender_executable" in config:
        blender_path = Path(config["blender_executable"])
        if not blender_path.exists():
            raise ValueError(f"Blender executable not found at: {config['blender_executable']}")


# Log the Blender executable being used - use stderr to avoid Claude Desktop JSON parsing issues
if not validate_blender_executable():
    print(f"WARNING: Blender executable not found at: {BLENDER_EXECUTABLE}", file=sys.stderr)
    print(
        "Please set the BLENDER_EXECUTABLE environment variable to the correct path.",
        file=sys.stderr,
    )
else:
    print(f"Using Blender executable: {BLENDER_EXECUTABLE}", file=sys.stderr)
