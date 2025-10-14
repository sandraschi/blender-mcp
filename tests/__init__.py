"""Test package for Blender MCP with real Blender execution.

This package contains comprehensive tests that actually run Blender instances
to ensure all functionality works correctly in real scenarios.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

# Test constants
TEST_TIMEOUT = 300  # 5 minutes
BLENDER_EXECUTABLE_ENV = "BLENDER_EXECUTABLE"
DEFAULT_BLENDER_PATHS = [
    "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
    "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
    "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
    "/usr/bin/blender",
    "/usr/local/bin/blender",
    "/opt/blender/blender",
    "blender"  # PATH lookup
]
