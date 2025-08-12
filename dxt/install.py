"""Installation script for Blender MCP server.

This script handles the installation of the Blender MCP server and its dependencies.
It ensures that all required Python packages are installed and performs any necessary
setup for the Blender integration.
"""

import os
import sys
import subprocess
import json
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List

# Constants
PACKAGE_NAME = "blender-mcp"
REQUIRED_PYTHON = (3, 8)
REQUIRED_BLENDER = (3, 0, 0)


def check_python_version() -> None:
    """Verify that the Python version meets the minimum requirements."""
    if sys.version_info < REQUIRED_PYTHON:
        print(f"Error: {PACKAGE_NAME} requires Python {'.'.join(map(str, REQUIRED_PYTHON))} or higher")
        sys.exit(1)


def check_blender_installed() -> Optional[str]:
    """Check if Blender is installed and return the path to the executable."""
    # First check if BLENDER_EXECUTABLE is set in environment
    blender_executable = os.environ.get("BLENDER_EXECUTABLE")
    if blender_executable and Path(blender_executable).exists():
        return blender_executable
    
    # Check common installation paths
    common_paths = []
    
    if platform.system() == "Windows":
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        
        common_paths.extend([
            f"{program_files}\\Blender Foundation\\Blender {REQUIRED_BLENDER[0]}.{REQUIRED_BLENDER[1]}\\blender.exe",
            f"{program_files_x86}\\Blender Foundation\\Blender {REQUIRED_BLENDER[0]}.{REQUIRED_BLENDER[1]}\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
            "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe"
        ])
    elif platform.system() == "Darwin":  # macOS
        common_paths.extend([
            "/Applications/Blender.app/Contents/MacOS/Blender",
            f"/Applications/Blender {REQUIRED_BLENDER[0]}.{REQUIRED_BLENDER[1]}/Blender.app/Contents/MacOS/Blender"
        ])
    else:  # Linux
        common_paths.extend([
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/opt/blender/blender"
        ])
    
    # Check each path
    for path in common_paths:
        if Path(path).exists():
            return path
    
    return None


def install_dependencies() -> bool:
    """Install required Python dependencies using pip."""
    try:
        # Read requirements from dxt.json
        with open(Path(__file__).parent / "dxt.json") as f:
            config = json.load(f)
        
        # Install each dependency
        for dep in config.get("dependencies", []):
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False


def setup_environment(blender_path: str) -> None:
    """Set up environment variables and configuration."""
    # Set BLENDER_EXECUTABLE in environment
    os.environ["BLENDER_EXECUTABLE"] = blender_path
    
    # Create a simple script to verify Blender integration
    verify_script = """
import bpy
print(f"Blender version: {bpy.app.version_string}")
print("Blender integration test successful!")
"""
    
    try:
        # Test Blender integration
        print("Testing Blender integration...")
        result = subprocess.run(
            [blender_path, "--background", "--python-expr", verify_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Blender integration test passed")
            print(result.stdout)
        else:
            print("❌ Blender integration test failed")
            print(result.stderr)
    except Exception as e:
        print(f"Error testing Blender integration: {e}")


def main() -> None:
    """Main installation function."""
    print(f"🚀 Installing {PACKAGE_NAME}...")
    
    # Check Python version
    check_python_version()
    
    # Check if Blender is installed
    blender_path = check_blender_installed()
    if not blender_path:
        print(f"❌ Blender {'.'.join(map(str, REQUIRED_BLENDER))} or later is required but not found.")
        print("Please install Blender and ensure it's in your PATH or set the BLENDER_EXECUTABLE environment variable.")
        sys.exit(1)
    
    print(f"✅ Found Blender at: {blender_path}")
    
    # Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Set up environment
    print("\n⚙️  Setting up environment...")
    setup_environment(blender_path)
    
    print("\n✨ Installation complete!")
    print(f"\nTo start the {PACKAGE_NAME} server, run:")
    print("  python -m blender_mcp.server")
    print("\nFor HTTP mode, use:")
    print("  python -m blender_mcp.server --http --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    main()
