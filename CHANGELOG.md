# Changelog

All notable changes to **Blender MCP** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-01-15

### Added
- **8 New Advanced VR Tools** for professional avatar workflows:
  - `blender_validation`: Pre-flight checks for VRChat/Resonite compatibility
  - `blender_splatting`: Gaussian Splatting (3DGS) import with proxy objects
  - `blender_materials_baking`: Shader conversion (toon→PBR) and material atlasing
  - `blender_vrm_metadata`: VRM-specific data (first person, visemes, spring bones)
  - `blender_atlasing`: Material/texture merging for mobile VR optimization
  - `blender_shapekeys`: Facial animation (visemes A/I/U/E/O, blink, expressions)
  - Extended `blender_rigging`: Weight transfer and humanoid bone mapping
  - `blender_export_presets`: Platform-specific exports (VRChat, Resonite, Unity)
- **Project AG Integration**: Complete VR avatar creation pipeline
- **Cross-Platform VR Support**: VRChat, Resonite, Unity, and VRM compatibility
- **Advanced Material System**: PBR conversion and draw call optimization
- **Professional Rigging Tools**: Weight painting automation and bone mapping
- **Gaussian Splatting Support**: Hybrid environment creation with collision meshes

### Features
- **VR Avatar Optimization Pipeline**:
  - Automatic polycount validation (VRChat: 70k, Resonite: 100k)
  - Bone count limits and naming conventions (256 max for VRChat)
  - Material atlasing for reduced draw calls
  - Unapplied transform detection and correction
- **Advanced Facial Animation**:
  - VRM-compliant viseme creation (A, I, U, E, O)
  - Blink animation setup with customizable intensity
  - Facial expression blending and weight management
  - Lip sync automation for voice acting
- **Cross-Platform Export System**:
  - VRChat presets (Unity scale 1.0, FBX format)
  - Resonite presets (GLTF format with collision support)
  - Legacy VRChat support (0.01 scale for old workflows)
  - Pre-export validation against platform limits
- **Gaussian Splatting Integration**:
  - Import `.ply`/`.spz` files with performance proxy objects
  - Collision mesh generation for walkable environments
  - Hybrid avatar + environment workflows
  - Resonite export with splat collision data
- **Professional Material Workflow**:
  - Cel-shaded to PBR texture baking
  - Material consolidation into atlas textures
  - VRM shader conversion to standard materials
  - Mobile VR optimization (reduce draw calls)

### Technical
- **FastMCP 2.13+ Portmanteau Pattern**: All tools use consolidated interfaces
- **Advanced Blender API Integration**: Direct access to rigging, materials, and animation
- **Cross-Platform File Handling**: Pathlib-based operations for Windows/Linux/Mac
- **Comprehensive Error Recovery**: Custom exceptions for each tool category
- **Async/Await Architecture**: All operations properly async for FastMCP compatibility
- **Pydantic Validation**: Type-safe parameter validation for all operations
- **Logging Integration**: Detailed operation logging with loguru

---

## [0.1.0] - 2025-12-24

### Added
- Initial alpha release
- Basic Blender connectivity
- Core MCP server implementation
- Development infrastructure (CI/CD, testing, documentation)

### Changed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- Basic security scanning implementation
- Input validation for MCP commands

---

## Release Process

### For Contributors
1. Update version in `src/blender_mcp/__init__.py`
2. Update `CHANGELOG.md` with changes
3. Create pull request
4. CI/CD will handle the rest

### Automated Release
- Push to `main` triggers CI/CD pipeline
- Automatic version bumping available
- MCPB packages built and signed
- GitHub releases created with assets

### Version Types
- **PATCH** (`0.0.X`): Bug fixes, small improvements
- **MINOR** (`0.X.0`): New features, backwards compatible
- **MAJOR** (`X.0.0`): Breaking changes

---

## Types of Changes
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

---

*This changelog follows the principles of [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).*