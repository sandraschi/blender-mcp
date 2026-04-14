"""
Download tools for Blender MCP.

Provides tools to download files from URLs and import them into Blender scenes.
Supports models, textures, and other assets with automatic format detection.
"""

import logging
import os
import tempfile
from urllib.parse import urlparse

import httpx

from ..app import app

logger = logging.getLogger(__name__)
from ..compat import *
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


async def _download_file(url: str, output_path: str, timeout: int = 30) -> bool:
    """Download file from URL to specified path with async httpx."""
    try:
        logger.info(f"Downloading from: {url}")
        logger.debug(f"Saving to: {output_path}")

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0
                with open(output_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            logger.debug(f"Download progress: {downloaded / total_size * 100:.1f}%")

        file_size = os.path.getsize(output_path)
        logger.info(f"Download completed: {file_size} bytes")
        return True

    except httpx.HTTPStatusError as e:
        logger.error(f"Download HTTP error {e.response.status_code}: {url}")
        return False
    except Exception as e:
        logger.error(f"Download failed: {e!s}")
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
    operation: str = "download",
    url: str = "",
    import_into_scene: bool = True,
    custom_filename: str | None = None,
    timeout: int = 30,
) -> str:
    """
    Download from URL and import, or get supported formats info (portmanteau).

    Operations:
    - download: Download from url and optionally import into scene (requires url)
    - info: Supported file formats and usage examples

    Args:
        operation: One of download, info
        url: For download - URL to download from (http/https)
        import_into_scene: For download - import into current scene
        custom_filename: For download - custom filename without extension
        timeout: For download - timeout in seconds (1-300)

    Returns:
        Success message or info string
    """
    if operation == "info":
        logger.info("Getting download tool information")
        formats_list = [f"  {ext.upper()} - {importer}" for ext, importer in SUPPORTED_FORMATS.items()]
        return f"""Blender Download Tool Information
{"=" * 40}

Supported File Formats:
{chr(10).join(formats_list)}

Usage: blender_download(operation="download", url="https://...", import_into_scene=True)
Use operation="info" for this message.
"""
    if not url or not url.strip():
        return "url is required for operation='download'. Use operation='info' for supported formats."
    from ..utils.blender_executor import get_blender_executor

    logger.info(f"blender_download called - URL: {url}, import: {import_into_scene}")

    try:
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
        if not await _download_file(url, output_path, timeout):
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
            success_line = [line for line in import_result.split("\n") if line.startswith("SUCCESS:")]
            if success_line:
                return success_line[0].replace("SUCCESS: ", "")
            else:
                return f"Successfully downloaded and imported: {filename} ({file_size} bytes)"
        else:
            logger.warning(f"Import may have failed: {import_result}")
            return f"Downloaded: {filename} ({file_size} bytes) - Import result: {import_result}"

    except Exception as e:
        logger.error(f"Error in blender_download: {e!s}")
        return f"Error downloading file: {e!s}"
