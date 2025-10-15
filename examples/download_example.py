#!/usr/bin/env python3
"""
Example usage of Blender MCP download tools.

This example demonstrates how to use the blender_download tool to download
and import assets into Blender scenes.
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from blender_mcp.tools.download_tools import blender_download_info


async def demo_download_tools():
    """Demonstrate the download tools functionality."""

    print("=== Blender MCP Download Tools Demo ===\n")

    # Show supported formats
    print("1. Getting information about supported download formats:")
    info = await blender_download_info()
    print(info)
    print("\n" + "=" * 60 + "\n")

    # Example download URLs (these are examples - replace with real URLs)
    example_urls = [
        # 3D Models
        ("https://example.com/katana.obj", "OBJ model file"),
        ("https://example.com/character.fbx", "FBX character model"),
        ("https://example.com/scene.gltf", "glTF scene file"),
        # Textures
        ("https://example.com/texture.png", "PNG texture"),
        ("https://example.com/normal.jpg", "Normal map texture"),
        # Other formats
        ("https://example.com/model.stl", "STL 3D print file"),
        ("https://example.com/data.abc", "Alembic animation cache"),
    ]

    print("2. Example download commands:")
    for url, description in example_urls:
        print(f"# Download and import: {description}")
        print(f'# blender_download(url="{url}")')
        print()

    print("3. Advanced usage examples:")
    print("# Download without importing")
    print('# blender_download(url="https://example.com/texture.png", import_into_scene=False)')
    print()
    print("# Download with custom filename")
    print(
        '# blender_download(url="https://example.com/model.obj", custom_filename="my_custom_model")'
    )
    print()
    print("# Download with longer timeout for large files")
    print('# blender_download(url="https://example.com/large_model.fbx", timeout=120)')
    print()

    print("4. Katana-specific usage:")
    print("# For Katana models or assets:")
    print('# blender_download(url="https://katana-assets.example.com/sword.obj")')
    print('# blender_download(url="https://katana-assets.example.com/armor.fbx")')
    print()
    print("# Download from freebie sites:")
    print('# blender_download(url="https://freebie-site.com/katana-texture.png")')
    print('# blender_download(url="https://asset-site.com/katana-model.gltf")')
    print()

    print("NOTE: Replace example URLs with actual download links.")
    print("The tool will automatically detect file type and import appropriately.")


if __name__ == "__main__":
    asyncio.run(demo_download_tools())
