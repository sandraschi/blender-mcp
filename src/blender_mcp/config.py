"""Configuration settings for the Blender MCP server."""
import os
from pathlib import Path
from typing import Optional

# Default Blender executable path
DEFAULT_BLENDER_EXECUTABLE = "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe"

# Get Blender executable from environment variable or use default
BLENDER_EXECUTABLE: str = os.environ.get("BLENDER_EXECUTABLE", DEFAULT_BLENDER_EXECUTABLE)

# Validate Blender executable
def validate_blender_executable() -> bool:
    """Check if the Blender executable exists and is accessible.
    
    Returns:
        bool: True if the Blender executable is valid, False otherwise
    """
    if not BLENDER_EXECUTABLE:
        return False
    
    blender_path = Path(BLENDER_EXECUTABLE)
    return blender_path.exists() and blender_path.is_file()

# Log the Blender executable being used
if not validate_blender_executable():
    print(f"⚠️ Warning: Blender executable not found at: {BLENDER_EXECUTABLE}")
    print("Please set the BLENDER_EXECUTABLE environment variable to the correct path.")
else:
    print(f"✅ Using Blender executable: {BLENDER_EXECUTABLE}")
