# 📥 Download Tools Documentation

Download files from URLs and automatically import them into Blender scenes with format detection and error handling.

## Overview

Blender MCP provides powerful download tools that can fetch assets from the internet and automatically import them into your Blender scenes. Supports various 3D formats, textures, and other assets with intelligent format detection.

## Available Download Tools

### `blender_download`
Download files from URLs and optionally import them into the current Blender scene.

#### Parameters
- `url` (str): URL to download from (http/https)
- `import_into_scene` (bool): Whether to import the file into the scene (default: true)
- `custom_filename` (Optional[str]): Custom filename without extension
- `timeout` (int): Download timeout in seconds (1-300, default: 30)

#### Supported Formats
- **3D Models**: OBJ, FBX, DAE, 3DS, PLY, STL, X3D, glTF/GLB, Alembic, USD
- **Images**: PNG, JPG, JPEG, TIFF, BMP, EXR, HDR
- **Archives**: ZIP (automatic extraction)
- **Blender Files**: .blend (for linking/appending)

#### Examples
```python
# Download and import OBJ model
blender_download("https://example.com/model.obj")

# Download texture without importing
blender_download("https://example.com/texture.png", import_into_scene=False)

# Custom filename
blender_download("https://example.com/asset.fbx", custom_filename="my_asset")

# Long timeout for large files
blender_download("https://example.com/large_model.obj", timeout=120)
```

### `blender_download_info`
Get information about supported download formats and capabilities.

#### Returns
- List of supported file formats
- Format categories and extensions
- Import capabilities for each format
- Usage examples

#### Example
```python
blender_download_info()
# Output: Supported formats include:
# 3D Models: .obj, .fbx, .dae, .3ds, .ply, .stl, .x3d, .gltf, .glb, .abc, .usd, .usda, .usdc, .usdz
# Images: .png, .jpg, .jpeg, .tiff, .tif, .bmp, .exr, .hdr
# Archives: .zip
# Blender: .blend
```

## Download Process

### Step-by-Step Workflow
1. **URL Validation**: Check URL format and accessibility
2. **Format Detection**: Analyze file extension and MIME type
3. **Download**: Stream file with progress monitoring
4. **Validation**: Verify download integrity
5. **Import**: Automatically import based on format
6. **Cleanup**: Remove temporary files

### Automatic Format Detection
```python
# Extension-based detection
".obj" → Wavefront OBJ import
".fbx" → FBX import
".png" → Image texture load
".blend" → Blend file link/append
```

### Import Methods by Format

#### 3D Models
- **OBJ**: `bpy.ops.import_scene.obj()`
- **FBX**: `bpy.ops.import_scene.fbx()`
- **DAE**: `bpy.ops.wm.collada_import()`
- **glTF/GLB**: `bpy.ops.import_scene.gltf()`
- **STL**: `bpy.ops.import_mesh.stl()`

#### Images/Textures
- **All formats**: `bpy.data.images.load()`
- Automatic texture setup
- UV mapping preparation

#### Blender Files
- Link or append objects/materials
- Scene merging capabilities
- Library linking support

## Error Handling

### Network Errors
```python
# Automatic retry logic
# Timeout handling
# Connection error recovery
# SSL certificate validation
```

### Format Errors
```python
# Unsupported format detection
# Corrupted file handling
# Import failure recovery
# Partial download cleanup
```

### Permission Errors
```python
# File system access checks
# Directory creation
# Write permission validation
# Temporary file cleanup
```

## Performance Optimization

### Download Optimization
- **Streaming**: Large files downloaded in chunks
- **Progress Monitoring**: Real-time download progress
- **Resume Support**: Partial download continuation
- **Compression**: Automatic decompression for archives

### Memory Management
- **Chunked Reading**: Controlled memory usage
- **Temporary Files**: Disk-based processing for large files
- **Cleanup**: Automatic temp file removal
- **Resource Limits**: Configurable timeouts and size limits

### Concurrent Downloads
- **Queue Management**: Sequential download processing
- **Resource Pooling**: Connection reuse
- **Rate Limiting**: Respectful download behavior
- **Error Isolation**: Individual download failure handling

## Asset Sources

### Recommended Free Sources

#### Poly Haven
```python
# High-quality PBR assets
blender_download("https://dl.polyhaven.com/file/ph-assets/Textures/png/512/concrete/concrete_01_diff_512.png")
blender_download("https://dl.polyhaven.com/file/ph-assets/HDRIs/hdr/4k/forest_path_4k.hdr")
```

#### AmbientCG
```python
# Material and texture library
blender_download("https://ambientcg.com/download/DownloadFile?file=AmbientCG%2FMetal032%2F2K-Metal032.zip")
```

#### Free3D
```python
# 3D model library
blender_download("https://free3d.com/dl.php?file=some-model.zip")
```

#### Sketchfab (Free Section)
```python
# Community models (check licenses)
blender_download("https://sketchfab.com/download-model-url")
```

### Commercial Sources
- **BlenderKit**: Premium assets via add-on
- **TurboSquid**: Professional models
- **CGTrader**: Artist marketplace
- **ArtStation**: Portfolio downloads

## Integration with BlenderKit

### Hybrid Workflow
```python
# Use BlenderKit add-on for browsing
# Download URLs from BlenderKit
# Use blender_download for automation

blender_download("https://www.blenderkit.com/asset-url")
```

### Batch Downloads
```python
# Download multiple assets
urls = [
    "https://example.com/model1.obj",
    "https://example.com/texture1.png",
    "https://example.com/model2.fbx"
]

for url in urls:
    blender_download(url)
```

## File Management

### Download Locations
- **Default**: System temp directory
- **Custom**: Configurable via environment variables
- **Cache**: Optional persistent caching
- **Organization**: Automatic subdirectories by type

### Naming Conventions
- **Auto-generated**: Based on URL filename
- **Custom**: User-specified prefixes
- **Collisions**: Automatic numbering (file_001.obj)
- **Sanitization**: Safe filename generation

## Security Considerations

### URL Validation
- **Protocol Check**: HTTP/HTTPS only
- **Domain Filtering**: Configurable allowed domains
- **Path Sanitization**: Prevent directory traversal
- **Size Limits**: Maximum download size enforcement

### Content Validation
- **MIME Type Check**: Server response validation
- **File Signature**: Content-based format detection
- **Malware Scanning**: Optional virus checking
- **Quarantine**: Suspicious file isolation

## Troubleshooting

### Common Issues

#### Download Failures
```python
# Check URL accessibility
curl -I "https://example.com/file.obj"

# Verify internet connection
ping example.com

# Check firewall settings
# Try different timeout values
```

#### Import Errors
```python
# Verify Blender version compatibility
blender --version

# Check file corruption
file downloaded_file.obj

# Try manual import in Blender
# Check Blender console for errors
```

#### Permission Errors
```python
# Check write permissions
ls -la /tmp/

# Verify temp directory access
mkdir /tmp/test_blender_download

# Check disk space
df -h
```

#### Format Not Supported
```python
# Check supported formats
blender_download_info()

# Convert file format
# Use different source
# Request format support
```

### Debug Information
```python
# Enable detailed logging
export LOG_LEVEL=DEBUG

# Check download logs
blender_view_logs(module_filter="download", since_minutes=5)

# Monitor file system
watch -n 1 'ls -la /tmp/blender_mcp_*'
```

## Advanced Usage

### Custom Import Scripts
```python
# Post-download processing
# Custom material assignment
# Scene integration logic
# Batch processing pipelines
```

### Integration APIs
```python
# REST API endpoints
# Webhook notifications
# Progress callbacks
# Error event handling
```

### Custom Format Support
```python
# Plugin architecture
# Custom import handlers
# Format converter integration
# Third-party tool integration
```

## Performance Benchmarks

### Download Speeds
- **Small files (<1MB)**: Instantaneous
- **Medium files (1-10MB)**: 10-60 seconds
- **Large files (10-100MB)**: 1-5 minutes
- **Archives**: Additional extraction time

### Import Times
- **Simple models**: <5 seconds
- **Complex scenes**: 30-120 seconds
- **High-poly models**: 5-30 minutes
- **Textures**: <1 second each

## Best Practices

### Workflow Optimization
1. **Batch Downloads**: Group similar assets
2. **Format Selection**: Choose optimal formats
3. **Quality Settings**: Balance quality vs. speed
4. **Caching Strategy**: Reuse downloaded assets

### Error Prevention
1. **URL Validation**: Check links before downloading
2. **Size Estimation**: Verify file sizes
3. **Format Compatibility**: Confirm Blender support
4. **License Checking**: Verify usage rights

### Maintenance
1. **Regular Cleanup**: Remove unused downloads
2. **Cache Management**: Monitor disk usage
3. **Update Checks**: Verify asset freshness
4. **Backup Strategy**: Preserve important assets

---

**Download and import assets with ease! Transform your workflow with automated asset management.** 📥🎨

*For BlenderKit integration, see the [complete guide](../blender/BLENDERKIT_GUIDE.md).* 🚀
