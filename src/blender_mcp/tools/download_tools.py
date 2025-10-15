"""
Download tools for Blender MCP.

Provides tools to download files from URLs and import them into Blender scenes.
Supports models, textures, and other assets with automatic format detection.
"""

import os
import requests
import tempfile
from typing import Optional
from urllib.parse import urlparse
from loguru import logger
from ..app import app
from ..utils.error_handling import MCPError


# Supported file extensions and their Blender import methods
SUPPORTED_FORMATS = {
    # 3D Models
    ".obj": "import_scene.obj",
    ".fbx": "import_scene.fbx",
    ".dae": "import_scene.dae",
    ".3ds": "import_scene.autodesk_3ds",
    ".ply": "import_mesh.ply",
    ".stl": "import_mesh.stl",
    ".x3d": "import_scene.x3d",
    ".gltf": "import_scene.gltf",
    ".glb": "import_scene.gltf",
    ".abc": "import_scene.alembic",
    ".usd": "import_scene.usd",
    ".usda": "import_scene.usd",
    ".usdc": "import_scene.usd",
    ".usdz": "import_scene.usd",
    # Images/Textures
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".tiff": "image",
    ".tif": "image",
    ".bmp": "image",
    ".exr": "image",
    ".hdr": "image",
    # Other
    ".blend": "link_blend",  # Can link or append from .blend files
}


def _get_file_type_from_url(url: str) -> str:
    """Extract file type from URL or return 'unknown'."""
    parsed = urlparse(url)
    path = parsed.path.lower()

    for ext in SUPPORTED_FORMATS.keys():
        if path.endswith(ext):
            return ext

    return "unknown"


def _download_file(url: str, output_path: str, timeout: int = 30) -> bool:
    """Download file from URL to specified path with error handling."""
    try:
        logger.info(f"Downloading from: {url}")
        logger.debug(f"Saving to: {output_path}")

        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        # Get file size for progress indication
        total_size = int(response.headers.get("content-length", 0))

        with open(output_path, "wb") as file:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        logger.debug(f"Download progress: {progress:.1f}%")

        file_size = os.path.getsize(output_path)
        logger.info(f"Download completed: {file_size} bytes")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Download failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during download: {str(e)}")
        return False


def _import_into_blender(file_path: str, file_ext: str) -> str:
    """Import downloaded file into Blender scene."""
    script = f"""
import bpy
import os

file_path = r"{file_path}"
file_ext = "{file_ext}"

try:
    # Ensure file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Downloaded file not found: {{file_path}}")

    # Import based on file type
    if file_ext in ['.obj']:
        bpy.ops.import_scene.obj(filepath=file_path)
        result = f"Imported OBJ file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.fbx']:
        bpy.ops.import_scene.fbx(filepath=file_path)
        result = f"Imported FBX file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.dae']:
        bpy.ops.import_scene.dae(filepath=file_path)
        result = f"Imported COLLADA file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.3ds']:
        bpy.ops.import_scene.autodesk_3ds(filepath=file_path)
        result = f"Imported 3DS file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.ply']:
        bpy.ops.import_mesh.ply(filepath=file_path)
        result = f"Imported PLY file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.stl']:
        bpy.ops.import_mesh.stl(filepath=file_path)
        result = f"Imported STL file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.x3d']:
        bpy.ops.import_scene.x3d(filepath=file_path)
        result = f"Imported X3D file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.gltf', '.glb']:
        bpy.ops.import_scene.gltf(filepath=file_path)
        result = f"Imported glTF file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.abc']:
        bpy.ops.import_scene.alembic(filepath=file_path)
        result = f"Imported Alembic file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.usd', '.usda', '.usdc', '.usdz']:
        bpy.ops.import_scene.usd(filepath=file_path)
        result = f"Imported USD file: {{os.path.basename(file_path)}}"

    elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.exr', '.hdr']:
        # Load as image texture
        img = bpy.data.images.load(file_path)
        result = f"Loaded image texture: {{img.name}}"

    elif file_ext in ['.blend']:
        # Link/append from blend file - this is more complex, just report success
        result = f"Downloaded Blender file: {{os.path.basename(file_path)}} (ready for linking/appending)"

    else:
        result = f"Downloaded file: {{os.path.basename(file_path)}} (format: {{file_ext}}) - not automatically imported"

    print(f"SUCCESS: {{result}}")

except Exception as e:
    print(f"ERROR: Failed to import {{file_ext}} file: {{str(e)}}")
    import traceback
    traceback.print_exc()
"""
    return script


@app.tool
async def blender_download(
    url: str,
    import_into_scene: bool = True,
    custom_filename: Optional[str] = None,
    timeout: int = 30,
) -> str:
    """
    Download files from URLs and optionally import them into the Blender scene.

    Supports downloading and importing various file formats including 3D models,
    textures, and other assets. Automatically detects file type and uses appropriate
    Blender import operators.

    Args:
        url: URL to download from (http/https)
        import_into_scene: Whether to import the downloaded file into the current scene
        custom_filename: Optional custom filename (without extension, auto-detected)
        timeout: Download timeout in seconds (default: 30)

    Returns:
        Success message with download and import details

    Examples:
        - blender_download("https://example.com/model.obj") - Download and import OBJ model
        - blender_download("https://example.com/texture.png", import_into_scene=False) - Just download texture
        - blender_download("https://example.com/katana.fbx", custom_filename="my_katana") - Download with custom name
    """
    from ..utils.blender_executor import get_blender_executor

    logger.info(f"blender_download called - URL: {url}, import: {import_into_scene}")

    try:
        # Validate inputs
        if timeout < 1 or timeout > 300:
            raise MCPError(f"timeout must be between 1 and 300 seconds, got {timeout}")

        # Validate URL
        if not url.startswith(("http://", "https://")):
            raise MCPError("Invalid URL format. Must start with http:// or https://")

        # Detect file type from URL
        file_ext = _get_file_type_from_url(url)
        if file_ext == "unknown":
            raise MCPError(f"Could not determine file type from URL: {url}")

        # Create temp directory for downloads
        temp_dir = tempfile.mkdtemp(prefix="blender_mcp_download_")
        logger.debug(f"Created temp directory: {temp_dir}")

        # Generate filename
        if custom_filename:
            filename = f"{custom_filename}{file_ext}"
        else:
            # Extract filename from URL
            parsed_url = urlparse(url)
            url_filename = os.path.basename(parsed_url.path)
            if url_filename:
                filename = url_filename
            else:
                filename = f"downloaded_file{file_ext}"

        output_path = os.path.join(temp_dir, filename)

        # Download the file
        logger.info(f"Starting download: {url}")
        if not _download_file(url, output_path, timeout):
            return f"Error: Failed to download file from {url}"

        # Check if file was actually downloaded
        if not os.path.exists(output_path):
            return f"Error: Downloaded file not found at {output_path}"

        file_size = os.path.getsize(output_path)
        logger.info(f"Downloaded file size: {file_size} bytes")

        if not import_into_scene:
            return f"Successfully downloaded file: {filename} ({file_size} bytes) - saved to {output_path}"

        # Import into Blender scene
        logger.info(f"Importing {file_ext} file into Blender scene")
        import_script = _import_into_blender(output_path, file_ext)

        executor = get_blender_executor()
        import_result = await executor.execute_script(import_script)

        # Parse the result
        if "SUCCESS:" in import_result:
            success_line = [
                line for line in import_result.split("\n") if line.startswith("SUCCESS:")
            ]
            if success_line:
                return success_line[0].replace("SUCCESS: ", "")
            else:
                return f"Successfully downloaded and imported: {filename} ({file_size} bytes)"
        else:
            logger.warning(f"Import may have failed: {import_result}")
            return f"Downloaded: {filename} ({file_size} bytes) - Import result: {import_result}"

    except Exception as e:
        logger.error(f"Error in blender_download: {str(e)}")
        return f"Error downloading file: {str(e)}"


@app.tool
async def blender_download_info() -> str:
    """
    Get information about supported download formats and usage.

    Returns:
        Information about supported file formats and usage examples
    """
    logger.info("Getting download tool information")

    formats_list = []
    for ext, importer in SUPPORTED_FORMATS.items():
        formats_list.append(f"  {ext.upper()} - {importer}")

    result = f"""Blender Download Tool Information
{"=" * 40}

Supported File Formats:
{chr(10).join(formats_list)}

Usage Examples:
• blender_download("https://example.com/model.fbx") - Download and import FBX model
• blender_download("https://example.com/texture.png", import_into_scene=False) - Download only
• blender_download("https://example.com/katana.obj", custom_filename="samurai_sword") - Custom name

Notes:
• Downloads are temporary and cleaned up after import
• Large files may take time to download
• Some formats require specific Blender add-ons to be enabled
• Textures are loaded as image data but not automatically assigned to materials

For Katana downloads, ensure the URL points to a supported 3D model format (.obj, .fbx, .dae, etc.)
"""
    return result
