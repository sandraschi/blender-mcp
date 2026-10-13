# Free 3D Assets Guide for Blender MCP

## Overview

This guide helps you find and download legitimate free 3D assets, models, textures, and materials for use with Blender MCP's download tools. All recommendations focus on legal, high-quality resources with proper licensing.

## 🏆 Top Recommended Sites

### 1. **Poly Haven** (polyhaven.com)
**Best for:** HDRI environments, textures, models
- ✅ **100% Free** - No account required
- ✅ **High Quality** - Professional-grade assets
- ✅ **Multiple Formats** - EXR, PNG, JPG, GLTF, OBJ
- ✅ **CC0 License** - Use commercially without restrictions
- ✅ **Regular Updates** - New assets added frequently

**Popular Downloads:**
- HDRI environments for lighting
- PBR textures (wood, metal, fabric)
- 3D models (furniture, props)
- Material presets

**Blender MCP Usage:**
```python
# Download HDRI for environment lighting
await blender_download("https://dl.polyhaven.org/file/ph_assets/HDRIs/hdr/4k/studio_small_09_4k.hdr")

# Download PBR texture set
await blender_download("https://dl.polyhaven.org/file/ph_assets/Textures/jpg/4k/wooden_planks_diff_4k.jpg")
```

### 2. **AmbientCG** (ambientcg.com)
**Best for:** PBR textures and materials
- ✅ **Free Downloads** - Direct links, no signup
- ✅ **PBR Materials** - Albedo, Normal, Roughness, Displacement
- ✅ **High Resolution** - Up to 8K textures
- ✅ **CC0 License** - Commercial use allowed
- ✅ **Fast Downloads** - Direct file links

**Popular Categories:**
- Wood, Metal, Fabric, Stone, Ground
- Seamless tiling textures
- Material variations (weathered, painted, etc.)

**Blender MCP Usage:**
```python
# Download complete PBR material set
await blender_download("https://ambientcg.com/download/download.php?file=Wood054_4K-PNG.zip")
```

### 3. **Quixel Megascans** (megascans.se)
**Best for:** High-end PBR surfaces
- ✅ **Free Library** - Large selection without account
- ✅ **Photogrammetry** - Real-world scanned surfaces
- ✅ **Multiple Formats** - EXR, PNG, TIFF, UDIM
- ✅ **CC0 License** - Commercial use allowed
- ✅ **Industry Standard** - Used in AAA games/movies

**Asset Types:**
- Surface materials (rocks, wood, metal)
- 3D scans of real objects
- Environment assets

### 4. **Textures.com** (textures.com)
**Best for:** Professional textures
- ✅ **Free Downloads** - Large library without signup
- ✅ **High Quality** - 1K to 8K resolutions
- ✅ **Organized Categories** - Easy to find specific materials
- ✅ **Various Formats** - JPG, PNG, PSD, TIFF
- ✅ **Regular Updates** - New textures added weekly

**Categories:**
- Architecture, Nature, Urban, Industrial
- Seamless patterns, tileable textures

### 5. **Free3D** (free3d.com)
**Best for:** 3D models and scenes
- ✅ **Free Models** - OBJ, FBX, 3DS formats
- ✅ **User Submissions** - Community contributed
- ✅ **Various Categories** - Characters, Vehicles, Props
- ✅ **Preview Images** - See before downloading
- ✅ **Multiple Formats** - Often includes multiple export formats

**Popular Categories:**
- Game assets, Architectural models
- Vehicles, Characters, Props

### 6. **CGAxis** (cgaxis.com)
**Best for:** 3D models and textures
- ✅ **Free Section** - Large library of free assets
- ✅ **Professional Quality** - Production-ready models
- ✅ **Multiple Formats** - OBJ, FBX, 3DS, MAX
- ✅ **Organized Collections** - Easy browsing
- ✅ **Regular Free Releases**

**Asset Types:**
- Furniture, Architecture, Vehicles
- Plants, Props, Materials

### 7. **Blend Swap** (blendswap.com)
**Best for:** Blender-specific assets
- ✅ **Free Blender Files** - .blend format
- ✅ **Blender Community** - User-created content
- ✅ **Materials & Textures** - Blender-compatible
- ✅ **Node Setups** - Ready-to-use materials
- ✅ **Tutorials** - Learning resources

**Perfect for Blender MCP:**
- Direct .blend file downloads
- Pre-configured materials
- Scene setups

## 🔍 How to Find Assets

### Search Strategies

#### 1. **Specific Keywords**
```
"katana model free" - Direct search for what you need
"samurai sword obj" - Be specific about format
"japanese sword fbx" - Include desired format
"katana texture seamless" - For materials
```

#### 2. **Format-Specific Searches**
```
"katana.obj" - OBJ format
"katana.fbx" - FBX format
"katana.gltf" - glTF format
"katana.blend" - Blender native
```

#### 3. **Quality Indicators**
```
"PBR" - Physically Based Rendering materials
"4K" - High resolution textures
"game ready" - Optimized for real-time use
"low poly" - Reduced polygon count
```

### Advanced Search Techniques

#### 1. **Google Advanced Search**
```
site:polyhaven.com katana - Search specific sites
filetype:obj katana free - Find specific file types
"katana" -obj -fbx site:cgaxis.com - Exclude formats
```

#### 2. **Asset Aggregation Sites**
- **OpenGameArt.org** - Game assets, CC0 license
- **Sketchfab.com** - Free downloads section
- **Thingiverse.com** - 3D printable models (STL)
- **GrabCAD.com** - Engineering/Industrial models

## 📥 Download Best Practices

### 1. **Check Licenses**
```python
# Always verify licensing before commercial use
# Look for: CC0, CC-BY, Public Domain
# Avoid: All Rights Reserved, Copyright
```

### 2. **File Format Selection**
```python
# For 3D models (Blender MCP supports all these):
".obj"  # Universal, simple

".fbx"  # Game engines, preserves materials
".dae"  # COLLADA, good material support
".gltf"  # Modern web format
".blend"  # Blender native (best compatibility)

# For textures:
".png"  # Universal, lossless
".jpg"  # Smaller files, lossy
".exr"  # HDR, floating point
".tiff"  # High quality, large files
```

### 3. **Batch Downloads**
```python
# Download multiple related assets
assets = [
    "https://polyhaven.com/model/katana",
    "https://ambientcg.com/metal_textures",
    "https://textures.com/wood_grain",
]

for url in assets:
    await blender_download(url)
```

## 🎯 Katana-Specific Resources

### Recommended Katana Asset Sources

#### 1. **Game Asset Sites**
- **OpenGameArt** - Search "katana", "sword", "japanese weapon"
- **Itch.io** - Free asset packs, search "katana"
- **Kenney Assets** - Free game assets including weapons

#### 2. **3D Model Marketplaces**
- **Sketchfab** - Free download section, search "katana model"
- **TurboSquid** - Free models section
- **CGTrader** - Free downloads

#### 3. **Educational Resources**
- **BlenderKit** - Free assets for learning
- **Poly Haven** - Japanese-themed textures/materials

### Katana Model Examples
```python
# Download a katana model
await blender_download("https://example.com/katana.obj")

# Download katana textures
await blender_download("https://polyhaven.com/texture/metal_plate")
await blender_download("https://ambientcg.com/metal_sword")

# Download traditional Japanese patterns
await blender_download("https://textures.com/japanese_pattern")
```

## ⚖️ Legal & Ethical Considerations

### ✅ **Do's**
- Check license terms before use
- Give credit when required (CC-BY)
- Use CC0 assets commercially
- Verify file integrity after download
- Respect content creator rights

### ❌ **Don'ts**
- Don't download from pirate sites
- Don't use copyrighted assets commercially without permission
- Don't redistribute paid assets for free
- Don't remove watermarks without permission

### License Types to Look For
```
CC0        - Public Domain, use anywhere
CC-BY      - Attribution required
CC-BY-SA   - Attribution + ShareAlike
Public Domain - No restrictions
```

## 🛠️ Troubleshooting Downloads

### Common Issues

#### 1. **File Not Found**
```python
# Check URL is still valid
# Some free sites remove old files
# Try alternative sources
```

#### 2. **Import Errors**
```python
# Verify file format matches extension
# Check for corrupted downloads
# Try alternative formats
```

#### 3. **Large File Timeouts**
```python
# Use longer timeout for big files
await blender_download(url, timeout=120)
```

#### 4. **Unsupported Formats**
```python
# Convert files using online converters
# Find alternative sources with better formats
```

### Quality Checks
```python
# Always preview assets before full download
# Check polygon count for performance
# Verify texture resolutions
# Test material assignments
```

## 📚 Learning Resources

### Free Asset Creation
- **Blender Guru** - Learn to model your own assets
- **CG Cookie** - Free Blender tutorials
- **YouTube Channels** - Search "blender modeling katana"

### Asset Optimization
- **Learn PBR** - Understand physically based materials
- **UV Mapping** - Proper texture coordinates
- **LOD Creation** - Level of detail for performance

## 🚀 Pro Tips

### 1. **Build Asset Libraries**
```python
# Create organized folders
# Tag assets by type/license
# Document sources and licenses
```

### 2. **Asset Management**
```python
# Use Blender's asset browser
# Create material libraries
# Organize by project/category
```

### 3. **Community Resources**
- **Blender Artists Forum** - Free asset requests
- **Reddit r/blender** - Asset sharing
- **Discord Communities** - Asset exchange

### 4. **Automation**
```python
# Create scripts to batch download
# Auto-organize downloaded assets
# Generate material libraries
```

## 🔗 Quick Reference

### Top Sites Summary
| Site | Best For | Formats | License |
|------|----------|---------|---------|
| Poly Haven | HDRI/Textures | EXR, PNG, GLTF | CC0 |
| AmbientCG | PBR Materials | PNG, ZIP | CC0 |
| Free3D | 3D Models | OBJ, FBX, 3DS | Varies |
| Blend Swap | Blender Files | .blend | Varies |
| Textures.com | Textures | JPG, PNG | Free |

### Search Commands
```bash
# Google search operators
"katana model free" filetype:obj
"samurai sword" site:free3d.com
"japanese weapon" -paid -buy
```

**Happy asset hunting! Find those perfect katana models and textures for your Blender projects!** ⚔️🎨
