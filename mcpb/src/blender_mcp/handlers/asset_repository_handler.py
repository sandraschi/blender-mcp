"""
Asset Repository Handler for Blender MCP

This module provides tools for downloading and importing assets from free Blender repositories.
Supports multiple repositories including BlenderKit, Kenney Assets, Quaternius, Open Game Art, and more.
"""

from ..compat import *

from typing import Optional, Dict, Any, List, Union, Tuple
import os
import tempfile
import urllib.request
import urllib.parse
from pathlib import Path
from enum import Enum
import logging
import zipfile
import tarfile

from fastmcp import FastMCP
from ..decorators import blender_operation
from ..utils.blender_executor import get_blender_executor

# Initialize logger
logger = logging.getLogger(__name__)

# Create FastMCP instance
app = FastMCP("blender-mcp-asset-repositories")

# Global executor instance
_executor = get_blender_executor()


class AssetRepository(str, Enum):
    """Supported asset repositories."""

    BLENDERKIT = "blenderkit"
    KENNEY = "kenney"
    QUATERNIUS = "quaternius"
    OPEN_GAME_ART = "opengameart"
    POLY_HAVEN = "polyhaven"
    SKETCHFAB = "sketchfab"


class AssetType(str, Enum):
    """Types of assets that can be imported."""

    MODEL = "model"
    MATERIAL = "material"
    TEXTURE = "texture"
    SCENE = "scene"
    ANIMATION = "animation"
    HDRI = "hdri"


class AssetFormat(str, Enum):
    """File formats supported for import."""

    BLEND = "blend"
    FBX = "fbx"
    OBJ = "obj"
    GLTF = "gltf"
    PNG = "png"
    JPG = "jpg"
    HDR = "hdr"
    ZIP = "zip"


class RepositoryManager:
    """Manages asset downloads from various repositories."""

    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "blender_mcp_assets"
        self.temp_dir.mkdir(exist_ok=True)

    def _download_file(self, url: str, filename: str) -> str:
        """Download a file from URL and return the local path."""
        local_path = self.temp_dir / filename

        try:
            logger.info(f"Downloading from {url} to {local_path}")
            with urllib.request.urlopen(url) as response:
                with open(local_path, "wb") as f:
                    f.write(response.read())

            logger.info(f"Successfully downloaded {filename}")
            return str(local_path)

        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")

    def _extract_archive(self, archive_path: str, extract_to: str) -> List[str]:
        """Extract archive and return list of extracted files."""
        extracted_files = []

        try:
            if archive_path.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(extract_to)
                    extracted_files = [os.path.join(extract_to, f) for f in zip_ref.namelist()]

            elif archive_path.endswith((".tar.gz", ".tar.bz2", ".tar.xz")):
                with tarfile.open(archive_path, "r:*") as tar_ref:
                    tar_ref.extractall(extract_to)
                    extracted_files = [
                        os.path.join(extract_to, m.name) for m in tar_ref.getmembers()
                    ]

            logger.info(f"Extracted {len(extracted_files)} files from {archive_path}")
            return extracted_files

        except Exception as e:
            logger.error(f"Failed to extract {archive_path}: {str(e)}")
            raise Exception(f"Extraction failed: {str(e)}")

    def get_kenney_asset(self, asset_name: str, asset_type: str = "3d") -> Tuple[str, List[str]]:
        """Download an asset from Kenney.nl."""
        # Kenney assets follow a predictable URL pattern
        base_url = f"https://kenney.nl/assets/{asset_name}"
        zip_url = f"{base_url}/{asset_name}.zip"

        try:
            # Download the zip file
            local_zip = self._download_file(zip_url, f"{asset_name}.zip")

            # Extract it
            extract_dir = str(self.temp_dir / asset_name)
            extracted_files = self._extract_archive(local_zip, extract_dir)

            # Find Blender files (.blend)
            blend_files = [f for f in extracted_files if f.endswith(".blend")]

            if blend_files:
                return blend_files[0], extracted_files
            else:
                # Look for other 3D formats
                supported_formats = [".fbx", ".obj", ".gltf", ".glb"]
                for fmt in supported_formats:
                    model_files = [f for f in extracted_files if f.endswith(fmt)]
                    if model_files:
                        return model_files[0], extracted_files

                raise Exception(f"No supported 3D files found in {asset_name}")

        except Exception as e:
            raise Exception(f"Failed to get Kenney asset {asset_name}: {str(e)}")

    def get_quaternius_asset(self, asset_name: str) -> Tuple[str, List[str]]:
        """Download an asset from Quaternius.com."""
        # Quaternius assets are typically in zip files
        base_url = f"https://quaternius.com/packs/{asset_name}"
        zip_url = f"{base_url}.zip"

        try:
            local_zip = self._download_file(zip_url, f"{asset_name}.zip")
            extract_dir = str(self.temp_dir / asset_name)
            extracted_files = self._extract_archive(local_zip, extract_dir)

            # Find Blender files
            blend_files = [f for f in extracted_files if f.endswith(".blend")]
            if blend_files:
                return blend_files[0], extracted_files

            # Look for FBX files (common format for Quaternius)
            fbx_files = [f for f in extracted_files if f.endswith(".fbx")]
            if fbx_files:
                return fbx_files[0], extracted_files

            raise Exception(f"No supported files found in {asset_name}")

        except Exception as e:
            raise Exception(f"Failed to get Quaternius asset {asset_name}: {str(e)}")

    def get_opengameart_asset(self, asset_url: str) -> Tuple[str, List[str]]:
        """Download an asset from OpenGameArt.org."""
        try:
            # Extract filename from URL
            filename = asset_url.split("/")[-1]
            if not filename:
                filename = "opengameart_asset.zip"

            local_file = self._download_file(asset_url, filename)

            # If it's an archive, extract it
            if filename.endswith((".zip", ".tar.gz", ".tar.bz2")):
                extract_dir = str(self.temp_dir / filename.replace(".", "_"))
                extracted_files = self._extract_archive(local_file, extract_dir)
                return extracted_files[0] if extracted_files else local_file, extracted_files
            else:
                return local_file, [local_file]

        except Exception as e:
            raise Exception(f"Failed to get OpenGameArt asset from {asset_url}: {str(e)}")

    def get_polyhaven_asset(
        self, asset_name: str, asset_type: str = "hdris"
    ) -> Tuple[str, List[str]]:
        """Download an asset from Poly Haven."""
        base_url = f"https://dl.polyhaven.org/file/ph-assets/{asset_type}/{asset_name}"

        try:
            if asset_type == "hdris":
                # HDRIs are typically in HDR format
                hdr_url = f"{base_url}/hdri/4k/{asset_name}_4k.hdr"
                local_file = self._download_file(hdr_url, f"{asset_name}_4k.hdr")
                return local_file, [local_file]

            elif asset_type == "textures":
                # Textures are usually in ZIP format
                zip_url = f"{base_url}/blender/{asset_name}_blender.zip"
                local_zip = self._download_file(zip_url, f"{asset_name}_blender.zip")
                extract_dir = str(self.temp_dir / asset_name)
                extracted_files = self._extract_archive(local_zip, extract_dir)
                return extracted_files[0], extracted_files

            else:
                raise Exception(f"Unsupported Poly Haven asset type: {asset_type}")

        except Exception as e:
            raise Exception(f"Failed to get Poly Haven asset {asset_name}: {str(e)}")


# Global repository manager instance
repo_manager = RepositoryManager()


@blender_operation("download_and_import_asset", log_args=True)
async def download_and_import_asset(
    repository: Union[AssetRepository, str],
    asset_name: str,
    repository_specific_params: Optional[Dict[str, Any]] = None,
    import_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Download and import an asset from a free repository.

    Args:
        repository: Asset repository to download from
        asset_name: Name/ID of the asset to download
        repository_specific_params: Additional parameters for specific repositories
            - For Kenney: {"type": "3d|2d|music|sound"}
            - For Poly Haven: {"type": "hdris|textures|models"}
            - For OpenGameArt: {"url": "full_download_url"}
        import_options: Options for importing the downloaded asset
            - format: File format (blend, fbx, obj, gltf, etc.)
            - scale: Import scale factor
            - location: Import location as [x, y, z]
            - rotation: Import rotation as [x, y, z] degrees
        **kwargs: Additional options

    Returns:
        Dict containing import status and asset details
    """
    try:
        repository = AssetRepository(repository) if isinstance(repository, str) else repository
        repository_specific_params = repository_specific_params or {}
        import_options = import_options or {}

        logger.info(f"Downloading asset '{asset_name}' from {repository.value}")

        # Download the asset based on repository
        if repository == AssetRepository.KENNEY:
            asset_type = repository_specific_params.get("type", "3d")
            asset_file, all_files = repo_manager.get_kenney_asset(asset_name, asset_type)

        elif repository == AssetRepository.QUATERNIUS:
            asset_file, all_files = repo_manager.get_quaternius_asset(asset_name)

        elif repository == AssetRepository.OPEN_GAME_ART:
            asset_url = repository_specific_params.get("url")
            if not asset_url:
                return {
                    "status": "ERROR",
                    "error": "OpenGameArt requires 'url' parameter with download link",
                }
            asset_file, all_files = repo_manager.get_opengameart_asset(asset_url)

        elif repository == AssetRepository.POLY_HAVEN:
            asset_type = repository_specific_params.get("type", "hdris")
            asset_file, all_files = repo_manager.get_polyhaven_asset(asset_name, asset_type)

        elif repository == AssetRepository.BLENDERKIT:
            return {
                "status": "ERROR",
                "error": "BlenderKit integration requires API key and official add-on. Use BlenderKit add-on directly.",
            }

        elif repository == AssetRepository.SKETCHFAB:
            return {
                "status": "ERROR",
                "error": "Sketchfab integration not yet implemented. Download manually and use import_file tool.",
            }

        else:
            return {"status": "ERROR", "error": f"Unsupported repository: {repository}"}

        logger.info(f"Downloaded asset to: {asset_file}")

        # Determine file format for import
        file_ext = Path(asset_file).suffix.lower().lstrip(".")

        # Import the asset into Blender
        if file_ext == "blend":
            # For .blend files, use append/link
            import_result = await import_blend_asset(asset_file, import_options)
        else:
            # For other formats, use import_scene
            import_result = await import_scene_asset(asset_file, file_ext, import_options)

        # Add repository and download info
        import_result.update(
            {
                "repository": repository.value,
                "asset_name": asset_name,
                "downloaded_file": asset_file,
                "all_downloaded_files": all_files,
                "repository_params": repository_specific_params,
            }
        )

        return import_result

    except Exception as e:
        logger.error(f"Failed to download and import asset: {str(e)}")
        return {
            "status": "ERROR",
            "error": str(e),
            "repository": repository.value if "repository" in locals() else str(repository),
            "asset_name": asset_name,
        }


async def import_blend_asset(asset_file: str, import_options: Dict[str, Any]) -> Dict[str, Any]:
    """Import a .blend file using append/link."""
    from .import_handler import link_asset

    # Use default object directory for blend files
    directory = import_options.get("directory", "Object")
    asset_name = import_options.get("asset_name", "Asset")

    # For blend files, we link/append the main asset
    return await link_asset(
        filepath=asset_file,
        asset_name=asset_name,
        directory=directory,
        link=import_options.get("link", False),
    )


async def import_scene_asset(
    asset_file: str, file_format: str, import_options: Dict[str, Any]
) -> Dict[str, Any]:
    """Import a scene asset using import_scene operators."""
    from .import_handler import import_file

    # Map file extensions to import formats
    format_mapping = {
        "fbx": "FBX",
        "obj": "OBJ",
        "gltf": "GLTF",
        "glb": "GLTF",
        "dae": "COLLADA",
        "abc": "ABC",
        "ply": "PLY",
        "stl": "STL",
        "x3d": "X3D",
    }

    import_format = format_mapping.get(file_format.lower())
    if not import_format:
        return {"status": "ERROR", "error": f"Unsupported file format: {file_format}"}

    # Add import options
    import_kwargs = {}
    if "scale" in import_options:
        import_kwargs["global_scale"] = import_options["scale"]

    return await import_file(filepath=asset_file, file_format=import_format, **import_kwargs)


@blender_operation("list_available_assets", log_args=True)
async def list_available_assets(repository: Union[AssetRepository, str]) -> Dict[str, Any]:
    """
    List available assets from a repository.

    Note: This is a basic implementation. For comprehensive asset browsing,
    visit the repository websites directly.

    Args:
        repository: Repository to list assets from

    Returns:
        Dict containing available assets and information
    """
    repository = AssetRepository(repository) if isinstance(repository, str) else repository

    try:
        if repository == AssetRepository.KENNEY:
            return {
                "status": "SUCCESS",
                "repository": "Kenney Assets",
                "description": "Free game assets by Kenney",
                "website": "https://kenney.nl/assets",
                "sample_assets": [
                    "fantasy-town-kit",
                    "modular-dungeon-kit",
                    "city-kit-industrial",
                    "blocky-characters",
                    "blaster-kit",
                ],
                "usage": "Use asset name from URL, e.g., 'fantasy-town-kit'",
                "note": "Visit https://kenney.nl/assets to see all available assets",
            }

        elif repository == AssetRepository.QUATERNIUS:
            return {
                "status": "SUCCESS",
                "repository": "Quaternius",
                "description": "Free modular game assets",
                "website": "https://quaternius.com/",
                "sample_assets": [
                    "ultimate-space-kit",
                    "medieval-village-megakit",
                    "cyberpunk-game-kit",
                    "platformer-game-kit",
                    "toon-shooter-game-kit",
                ],
                "usage": "Use pack name from URL, e.g., 'ultimate-space-kit'",
                "note": "Visit https://quaternius.com/ to see all available packs",
            }

        elif repository == AssetRepository.OPEN_GAME_ART:
            return {
                "status": "SUCCESS",
                "repository": "Open Game Art",
                "description": "Community-contributed free game assets",
                "website": "https://opengameart.org/",
                "sample_assets": ["Various community assets"],
                "usage": "Provide direct download URL in repository_specific_params",
                "note": "Browse https://opengameart.org/ and copy download links",
            }

        elif repository == AssetRepository.POLY_HAVEN:
            return {
                "status": "SUCCESS",
                "repository": "Poly Haven",
                "description": "Free PBR textures and HDRIs",
                "website": "https://polyhaven.com/",
                "asset_types": ["hdris", "textures", "models"],
                "sample_assets": {
                    "hdris": ["studio_small_08", "lebombo_1k", "kloppenheim_06"],
                    "textures": ["wood_02", "fabric_01", "metal_01"],
                },
                "usage": "Specify asset_name and type in repository_specific_params",
            }

        elif repository == AssetRepository.BLENDERKIT:
            return {
                "status": "SUCCESS",
                "repository": "BlenderKit",
                "description": "Blender add-on required for downloads",
                "website": "https://www.blenderkit.com/",
                "note": "Install BlenderKit add-on in Blender for direct access",
                "integration_status": "Not implemented - use BlenderKit add-on",
            }

        else:
            return {
                "status": "ERROR",
                "error": f"Repository '{repository}' not supported for listing",
            }

    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


@blender_operation("search_assets", log_args=True)
async def search_assets(
    query: str,
    repository: Optional[Union[AssetRepository, str]] = None,
    asset_type: Optional[Union[AssetType, str]] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Search for assets across repositories.

    This is a basic search implementation. For comprehensive searching,
    visit repository websites directly.

    Args:
        query: Search query (keywords)
        repository: Specific repository to search (optional)
        asset_type: Type of assets to search for (optional)
        limit: Maximum number of results to return

    Returns:
        Dict containing search results
    """
    results = []

    # Basic keyword matching for demonstration
    if not repository:
        # Search all repositories
        repos_to_search = [
            AssetRepository.KENNEY,
            AssetRepository.QUATERNIUS,
            AssetRepository.POLY_HAVEN,
        ]
    else:
        repos_to_search = [
            AssetRepository(repository) if isinstance(repository, str) else repository
        ]

    query_lower = query.lower()

    for repo in repos_to_search:
        repo_results = await list_available_assets(repo)
        if repo_results["status"] == "SUCCESS":
            # Simple keyword matching
            assets = repo_results.get("sample_assets", [])
            if isinstance(assets, list):
                for asset in assets:
                    if query_lower in asset.lower():
                        results.append(
                            {
                                "repository": repo.value,
                                "asset_name": asset,
                                "match_score": 1.0,
                                "description": f"Asset from {repo_results.get('description', repo.value)}",
                            }
                        )

    return {
        "status": "SUCCESS",
        "query": query,
        "total_results": len(results),
        "results": results[:limit],
        "note": "This is a basic search. For comprehensive results, visit repository websites directly.",
    }
