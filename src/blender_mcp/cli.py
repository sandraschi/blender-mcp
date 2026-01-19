"""Command-line interface for Blender MCP."""

import argparse
import sys
import logging
from pathlib import Path

from blender_mcp.server import create_server, main_stdio


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Blender MCP - AI-Powered 3D Creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  blender-mcp --stdio                    # Run in stdio mode (for MCP clients)
  blender-mcp --http --host 0.0.0.0     # Run HTTP server
  blender-mcp --install-config          # Install Claude Desktop config
  blender-mcp --check-blender           # Check Blender installation
        """
    )

    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Run in stdio mode for MCP clients (default)"
    )

    parser.add_argument(
        "--http",
        action="store_true",
        help="Run in HTTP mode for web clients"
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind HTTP server to (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind HTTP server to (default: 8000)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    parser.add_argument(
        "--install-config",
        action="store_true",
        help="Install Claude Desktop configuration"
    )

    parser.add_argument(
        "--check-blender",
        action="store_true",
        help="Check Blender installation and compatibility"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    try:
        if args.install_config:
            install_claude_config()
            return

        if args.check_blender:
            check_blender_installation()
            return

        if args.http:
            # Run HTTP server
            logger.info(f"Starting HTTP server on {args.host}:{args.port}")
            import uvicorn
            from blender_mcp.server import app

            uvicorn.run(
                app,
                host=args.host,
                port=args.port,
                log_level="debug" if args.debug else "info"
            )
        else:
            # Run stdio mode (default for MCP clients)
            logger.info("Starting MCP server in stdio mode")
            main_stdio()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def install_claude_config():
    """Install Claude Desktop configuration."""
    import platform
    import json
    from pathlib import Path

    system = platform.system().lower()

    if system == "windows":
        config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
    elif system == "darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif system == "linux":
        config_dir = Path.home() / ".config" / "Claude"
    else:
        logger.warning(f"Unsupported platform: {system}")
        return

    config_file = config_dir / "claude_desktop_config.json"

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Load existing config or create new one
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            logger.warning("Existing config file is corrupted, creating new one")
            config = {"mcpServers": {}}
    else:
        config = {"mcpServers": {}}

    # Add Blender MCP configuration
    import sys
    python_executable = sys.executable

    config["mcpServers"]["blender-mcp"] = {
        "command": python_executable,
        "args": ["-c", "from blender_mcp.server import main_stdio; main_stdio()"],
        "env": {
            "PYTHONPATH": str(Path(__file__).parent.parent)
        }
    }

    # Write config file
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print("✅ Claude Desktop configuration installed!")
    print(f"📁 Config file: {config_file}")
    print("🔄 Restart Claude Desktop to load the new MCP server")
    print()
    print("To verify installation:")
    print("1. Open Claude Desktop")
    print("2. Ask: 'What Blender operations can you perform?'")


def check_blender_installation():
    """Check Blender installation and compatibility."""
    import subprocess
    import shutil

    print("🔍 Checking Blender installation...")

    # Check if blender command is available
    blender_path = shutil.which("blender")
    if blender_path:
        print(f"✅ Blender found at: {blender_path}")

        # Try to get version
        try:
            result = subprocess.run(
                [blender_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Extract version from first line
                version_line = result.stdout.strip().split('\n')[0]
                print(f"📦 {version_line}")

                # Check if version is compatible
                if "Blender 3." in version_line or "Blender 4." in version_line:
                    print("✅ Compatible version detected")
                else:
                    print("⚠️  Version might not be fully compatible (recommended: 3.0+)")
            else:
                print("⚠️  Could not determine Blender version")

        except subprocess.TimeoutExpired:
            print("⚠️  Blender command timed out")
        except Exception as e:
            print(f"⚠️  Error checking version: {e}")
    else:
        print("❌ Blender not found in PATH")
        print()
        print("To install Blender:")
        print("1. Download from: https://www.blender.org/download/")
        print("2. Add Blender to your system PATH")
        print("3. Or set BLENDER_PATH environment variable")

    # Check Python integration
    try:
        import bpy
        print("✅ Blender Python API (bpy) available")
    except ImportError:
        print("ℹ️  Blender Python API not available (normal for external MCP usage)")

    print()
    print("🎯 Blender MCP is ready to use with external Blender installations!")


if __name__ == "__main__":
    main()