# Glama.ai Integration Guide for blender-mcp

## 🎉 Platform Discovery

Our **blender-mcp** repository has been discovered and indexed by the Glama.ai platform!

### Repository Listing
- **URL**: https://glama.ai/mcp/servers/%40sandraschi/blender-mcp
- **Status**: ✅ Indexed and Discoverable
- **Discovery Method**: `glama.json` file in repository root (now added)

### glama.json Configuration

**Important**: Glama.ai uses `glama.json` for discovery (not naming conventions). Our `glama.json` clearly indicates:
- Production-ready status
- Detailed feature matrix
- Transport support (stdio + http)

See `glama.json` in repository root for full configuration.

## 📊 Project Statistics

### Quality Indicators
- ✅ **FastMCP 2.14.3+**: Latest framework version
- ✅ **Comprehensive Testing**: Unit + integration tests
- ✅ **Code Quality**: Black, ruff, mypy configured
- ✅ **Documentation**: Extensive docs in `docs/` folder
- ✅ **Dual Transport**: stdio (MCP) + HTTP (FastAPI)

## 🔧 Repository Configuration

### glama.json

Repository metadata for Glama.ai indexing (located in repository root):
```json
{
  "$schema": "https://glama.ai/mcp/schemas/server.json",
  "maintainers": ["sandraschi"],
  "name": "blender-mcp",
  "description": "FastMCP 2.14.3+ server for Blender automation - programmatic control over 3D creation, manipulation, and rendering.",
  "type": "mcp_server",
  "status": "production",
  "framework": "FastMCP 2.14.3+",
  "transport": ["stdio", "http"]
}
```

---

*Last Updated: 2026-01-25*
