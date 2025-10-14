# 🎨 Blender MCP - Asset Repositories

## Overview

Blender MCP can automatically download and import assets from popular free repositories, eliminating the need to manually search, download, and import 3D models, textures, materials, and other assets.

## Supported Repositories

### ✅ **Kenney Assets** (`kenney`)
- **Website**: https://kenney.nl/assets
- **Description**: High-quality free game assets by Kenney
- **Asset Types**: 3D models, 2D sprites, textures, UI elements
- **Formats**: Blend, FBX, PNG, JPG
- **Usage**: Direct download links, no API required

### ✅ **Quaternius** (`quaternius`)
- **Website**: https://quaternius.com/
- **Description**: Modular game assets, characters, environments
- **Asset Types**: 3D models, animations, modular kits
- **Formats**: FBX, Blend
- **Usage**: Direct download links from asset packs

### ✅ **Open Game Art** (`opengameart`)
- **Website**: https://opengameart.org/
- **Description**: Community-contributed free game assets
- **Asset Types**: 2D/3D art, music, sound effects, textures
- **Formats**: PNG, JPG, WAV, MP3, Blend, FBX, OBJ
- **Usage**: Direct download URLs (copy from website)

### ✅ **Poly Haven** (`polyhaven`)
- **Website**: https://polyhaven.com/
- **Description**: Free PBR textures and HDRIs
- **Asset Types**: HDRIs, textures, models
- **Formats**: HDR, PNG, JPG, EXR, Blend
- **Usage**: Direct download links

### ❌ **BlenderKit** (`blenderkit`) - Not Implemented
- **Status**: Requires API key and official Blender add-on
- **Alternative**: Install BlenderKit add-on directly in Blender

### ❌ **Sketchfab** (`sketchfab`) - Not Implemented
- **Status**: Limited free assets, complex API
- **Alternative**: Download manually and use `import_file` tool

## Basic Usage

### Download and Import Asset

```python
from blender_mcp.handlers.asset_repository_handler import download_and_import_asset
from blender_mcp.handlers.asset_repository_handler import AssetRepository

# Download a Kenney asset
result = await download_and_import_asset(
    repository=AssetRepository.KENNEY,
    asset_name="fantasy-town-kit",
    import_options={
        "scale": 1.0,
        "location": [0, 0, 0]
    }
)

if result['status'] == 'SUCCESS':
    print(f"✅ Imported {result['asset_name']}")
else:
    print(f"❌ Error: {result['error']}")
```

### List Available Assets

```python
from blender_mcp.handlers.asset_repository_handler import list_available_assets

# List Kenney assets
assets = await list_available_assets(AssetRepository.KENNEY)
print(f"Available: {assets['sample_assets']}")
```

### Search Across Repositories

```python
from blender_mcp.handlers.asset_repository_handler import search_assets

# Search for fantasy assets
results = await search_assets("fantasy", limit=5)
for asset in results['results']:
    print(f"Found: {asset['asset_name']} in {asset['repository']}")
```

## Repository-Specific Examples

### Kenney Assets

```python
# Download 3D assets (default)
await download_and_import_asset(
    repository="kenney",
    asset_name="fantasy-town-kit",
    repository_specific_params={"type": "3d"}
)

# Download 2D assets
await download_and_import_asset(
    repository="kenney",
    asset_name="ui-pack",
    repository_specific_params={"type": "2d"}
)
```

### Quaternius Assets

```python
# Download a game kit
await download_and_import_asset(
    repository="quaternius",
    asset_name="ultimate-space-kit",
    import_options={
        "scale": 0.5,
        "location": [10, 0, 0]
    }
)
```

### Open Game Art

```python
# Download using direct URL (copy from website)
await download_and_import_asset(
    repository="opengameart",
    asset_name="community_asset",
    repository_specific_params={
        "url": "https://opengameart.org/sites/default/files/asset.zip"
    }
)
```

### Poly Haven HDRIs

```python
# Download HDRI environment
await download_and_import_asset(
    repository="polyhaven",
    asset_name="lebombo",
    repository_specific_params={"type": "hdris"}
)
```

### Poly Haven Textures

```python
# Download PBR texture pack
await download_and_import_asset(
    repository="polyhaven",
    asset_name="wood_02",
    repository_specific_params={"type": "textures"}
)
```

## Import Options

### Common Options
```python
import_options = {
    "scale": 1.0,           # Import scale factor
    "location": [0, 0, 0],  # Import location [x, y, z]
    "rotation": [0, 0, 0],  # Import rotation [x, y, z] degrees
    "format": "blend"       # File format (auto-detected)
}
```

### Blend File Options
```python
import_options = {
    "directory": "Object",   # Directory in blend file (Object/, Material/, etc.)
    "asset_name": "Asset",   # Name of asset to import
    "link": False           # True = link, False = append
}
```

### Scene Import Options
```python
import_options = {
    "global_scale": 1.0,    # Scale factor for FBX/OBJ imports
    "use_split_objects": True,  # Split objects (OBJ)
    "import_pack_images": True,  # Pack images (GLTF)
    "merge_vertices": False     # Merge vertices (GLTF)
}
```

## Error Handling

### Common Issues

**1. Asset Not Found**
```
Error: Download failed: HTTP Error 404
Solution: Check asset name spelling and availability
```

**2. Unsupported Format**
```
Error: Unsupported file format: xyz
Solution: Asset may not contain Blender-compatible files
```

**3. Network Issues**
```
Error: Download failed: Connection timeout
Solution: Check internet connection, try again later
```

**4. Import Failures**
```
Error: Import failed with result: {'CANCELLED'}
Solution: Check file format and import options
```

## Popular Assets by Category

### Characters & Animation
- **Kenney**: `blocky-characters`, `toon-characters-1`
- **Quaternius**: `ultimate-animated-character-pack`, `rpg-character-pack`
- **Mixamo**: Free animated characters (download manually)

### Environments
- **Kenney**: `fantasy-town-kit`, `city-kit-industrial`, `modular-dungeon-kit`
- **Quaternius**: `medieval-village-megakit`, `ultimate-modular-ruins-pack`
- **Poly Haven**: HDRIs for lighting (`lebombo`, `studio_small_08`)

### Props & Furniture
- **Kenney**: `furniture-pack`, `household-pack`
- **Quaternius**: `ultimate-house-interior-pack`, `fantasy-props-megakit`

### Textures & Materials
- **Poly Haven**: `wood_02`, `fabric_01`, `metal_01`, `stone_01`
- **Kenney**: Various texture packs in 2D assets

## Performance Tips

### 1. Use Appropriate Scale
```python
# Large environments - scale down
import_options = {"scale": 0.1}

# Small props - use default scale
import_options = {"scale": 1.0}
```

### 2. Position Assets Properly
```python
# Place assets in scene
import_options = {
    "location": [x, y, z],
    "rotation": [0, 0, 0]
}
```

### 3. Batch Import Multiple Assets
```python
assets_to_import = [
    ("kenney", "fantasy-town-kit"),
    ("quaternius", "ultimate-space-kit"),
    ("polyhaven", "lebombo")
]

for repo, asset in assets_to_import:
    # Import with different positions
    pass
```

## File Management

### Temporary Files
- Downloaded files are stored in: `C:\Users\<user>\AppData\Local\Temp\blender_mcp_assets\`
- Files are automatically cleaned up on restart
- Large downloads may require disk space

### Import Locations
- Assets are imported at the specified location
- Use different locations to avoid overlap
- Consider scene scale when positioning

## Integration with Blender MCP

### Combine with Other Tools

```python
# Download asset
result = await download_and_import_asset("kenney", "fantasy-town-kit")

# Then apply materials
from blender_mcp.handlers.material_handler import create_material
await create_material(name="wood_material", color=[0.4, 0.3, 0.2])

# Add lighting
from blender_mcp.handlers.scene_handler import setup_lighting
await setup_lighting()
```

### GUI Mode for Preview

```python
from blender_mcp.utils.blender_executor import get_blender_executor

# Enable GUI mode to see downloaded assets
executor = get_blender_executor(headless=False)
await download_and_import_asset("kenney", "fantasy-town-kit")
# Blender window opens - you can see the imported assets!
```

## Contributing

### Adding New Repositories

To add support for a new repository:

1. **Research the repository**:
   - Download URLs or API endpoints
   - Available asset formats
   - Licensing terms

2. **Add to AssetRepository enum**:
```python
class AssetRepository(str, Enum):
    NEW_REPO = "new_repo"
```

3. **Implement download method**:
```python
def get_new_repo_asset(self, asset_name: str) -> Tuple[str, List[str]]:
    # Download logic here
    pass
```

4. **Add to download_and_import_asset**:
```python
elif repository == AssetRepository.NEW_REPO:
    asset_file, all_files = repo_manager.get_new_repo_asset(asset_name)
```

## License Information

### Repository Licenses
- **Kenney Assets**: CC0 (Public Domain)
- **Quaternius**: Free for personal/commercial use
- **Open Game Art**: Various (check individual assets)
- **Poly Haven**: CC0 (Public Domain)

**Always verify license terms before commercial use!**

## See Also

- [Main README](../README.md)
- [Examples](../examples/asset_repositories_example.py)
- [Tool Reference](TOOL_REFERENCE.md)
- [Import Handler](import_handler.md)
