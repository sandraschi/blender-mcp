# MCP Extension Development Standards

## CRITICAL: DXT Packaging Requirements for Claude Desktop Extensions

**This document prevents 4-hour debugging sessions.** Follow these standards religiously for GIMP, VRChat, and all future MCP extensions.

## 🚨 MANDATORY FIXES (Based on Blender-MCP disasters)

### 1. UNICODE ENCODING - WINDOWS KILLER
**Problem:** Windows cp1252 codec crashes on Unicode emojis in output

```python
# ❌ BROKEN - Causes UnicodeEncodeError
print(f"⚠️ Warning: {message}")
print(f"✅ Success: {message}")

# ✅ FIXED - ASCII only with stderr
print(f"WARNING: {message}", file=sys.stderr)
print(f"SUCCESS: {message}", file=sys.stderr)
```

**RULE:** Zero Unicode in any MCP server output. ASCII text only.

### 2. FUNCTION DEFAULT PARAMETERS
**Problem:** Hardcoded defaults ignore configuration

```python
# ❌ BROKEN - Ignores config
def get_executor(executable: str = "app"):
    return Executor(executable)

# ✅ FIXED - Uses config when no param
def get_executor(executable: str = None):
    return Executor(executable or CONFIG_EXECUTABLE)
```

**RULE:** Default to config values, never hardcoded strings.

### 3. FASTMCP BANNER CONTAMINATION  
**Problem:** Banner text breaks Claude Desktop JSON parsing

```python
# ❌ BROKEN - Shows banner
mcp = FastMCP("server-name")

# ✅ FIXED - Clean output
mcp = FastMCP("server-name", banner=False)
```

**RULE:** Always `banner=False` in FastMCP constructor.

## 📋 PRE-BUILD TESTING CHECKLIST

Before running `dxt build`, verify these tests pass:

### 1. Manual Server Test
```bash
cd /path/to/extension
python -m extension_name.server
```
- Must start without errors
- No banner text in output
- No Unicode characters
- Clean JSON-only stdout

### 2. Path Resolution Test
```python
# Test with default path
extension.validate_executable()

# Test with environment variable
os.environ['APP_EXECUTABLE'] = '/custom/path'
extension.validate_executable()
```

### 3. Unicode Safety Test
```bash
# Run on Windows with cp1252 
chcp 1252
python -m extension_name.server
```
- No UnicodeEncodeError crashes
- All output in ASCII

### 4. Claude Desktop Integration Test
- Install extension via DXT drag-drop
- Check connection status immediately
- No "Unable to connect to extension server" errors

## 🎯 CONFIGURATION STANDARDS

### Required Environment Variables
Every extension must support:
```
{APP}_EXECUTABLE=path/to/executable
```

### Config File Template
```python
"""Configuration for {APP} MCP server."""
import os
import sys
from pathlib import Path

def find_executable():
    """Auto-detect application executable."""
    possible_paths = [
        # Add version-specific paths
        "C:\\Program Files\\{App}\\{app}.exe",
        # Add common installation locations
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    # Try PATH
    import shutil
    if shutil.which("{app}"):
        return shutil.which("{app}")
    
    return None

# Environment variable or auto-detect
EXECUTABLE = os.environ.get("{APP}_EXECUTABLE") or find_executable()

def validate_executable():
    """Validate executable exists."""
    if not EXECUTABLE or not Path(EXECUTABLE).exists():
        print(f"ERROR: {APP} executable not found", file=sys.stderr)
        return False
    return True
```

## 🚀 EXTENSION REBUILD PROCESS

When fixing broken extensions:

1. **Fix code issues** (Unicode, paths, banner)
2. **Test manually** with checklist above
3. **Uninstall extension** in Claude Desktop
4. **Rebuild DXT:** `dxt build`
5. **Install new DXT** via drag-drop
6. **Verify connection** immediately

## 📝 FUTURE EXTENSION TARGETS

Apply these standards to:
- **GIMP-MCP:** Image editing automation
- **VRChat-MCP:** Avatar/world management  
- **OBS-MCP:** Streaming control
- **Audacity-MCP:** Audio processing

## ⚡ CRITICAL SUCCESS FACTORS

1. **No Unicode anywhere** - ASCII text only
2. **Banner disabled** - `FastMCP(name, banner=False)`
3. **Config-based paths** - No hardcoded defaults
4. **Stderr for logs** - Keep stdout clean for JSON
5. **Test before build** - Manual verification required
6. **Environment variables** - Support custom paths

## 🔗 DEPENDENCY MANAGEMENT - CRITICAL

### ALL Dependencies Must Be Explicit
**Problem:** Windsurf doesn't auto-detect indirect dependencies

```toml
# ❌ INCOMPLETE - Missing transitive deps
[dependencies]
fastmcp = "2.10.1"

# ✅ COMPLETE - All deps explicit
[dependencies]
fastmcp = "2.10.1"
loguru = "^0.7.0"  # Used by FastMCP but not auto-detected
psutil = "^5.9.0"  # Process monitoring
pydantic = "^2.0.0"  # Data validation
typing-extensions = "^4.0.0"  # Type hints
```

**RULE:** Every import must have explicit dependency in pyproject.toml

### pyproject.toml Template
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{extension-name}"
version = "1.0.0"
description = "{App} MCP Server for Claude Desktop"
authors = [{name = "sandraschi", email = "sandra@example.com"}]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "fastmcp>=2.10.1,<3.0.0",
    "loguru>=0.7.0",
    "psutil>=5.9.0", 
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0",
    # Add ALL imports here
]

[project.scripts]
{extension-name} = "{extension_name}.server:main"
```

## 📚 REFERENCE EXTENSION: windows-mcp (DXT Extension)

**Use the `windows-mcp` DXT EXTENSION as the PERFECT template for all future extensions.**

**Why this is the ideal reference:**
- ✅ **Working DXT extension** installed via drag-drop in Claude Desktop
- ✅ **Modular tool design** - PowerShell tool disabled, others work fine
- ✅ **Proper FastMCP 2.10.1** implementation  
- ✅ **No Unicode issues** - production tested
- ✅ **Individual tool control** - broken tools can be disabled while keeping good ones

**CRITICAL:** This is a DXT EXTENSION, not a config-based MCP server!

Find the source repo for windows-mcp DXT extension and copy its structure:
- Individual tool modules that can be enabled/disabled
- Clean FastMCP server setup with `banner=False`
- Proper dependency management in pyproject.toml
- ASCII-only output (no Unicode crashes)

**Tool Modularity Success:**
- File operations: ✅ Working
- System info: ✅ Working
- Process management: ✅ Working
- PowerShell integration: ❌ Disabled (broken)

**This proves the modular design works perfectly for DXT extensions!**

## 🎛️ TOOL MODULARITY STANDARDS

### Each Tool = Separate Handler
**Rule:** Every MCP tool must be independently enable/disable-able

```python
# ❌ MONOLITHIC - All tools coupled
class AppServer:
    def __init__(self):
        self.register_all_tools()  # Can't disable individual tools

# ✅ MODULAR - Tools can be disabled
class AppServer:
    def __init__(self):
        self.handlers = {
            'scene': SceneHandler(),
            'render': RenderHandler(), 
            'export': ExportHandler()
        }
        
    def register_tools(self, enabled_tools=None):
        enabled = enabled_tools or list(self.handlers.keys())
        for name, handler in self.handlers.items():
            if name in enabled:
                handler.register(self.mcp)
```

### Environment-Based Tool Control
```python
# Allow selective tool enabling
ENABLED_TOOLS = os.environ.get('{APP}_ENABLED_TOOLS', 'all').split(',')
if ENABLED_TOOLS == ['all']:
    ENABLED_TOOLS = list(server.handlers.keys())

server.register_tools(ENABLED_TOOLS)
```

**Follow this doc religiously or waste another 4 hours debugging the same Unicode/path/banner/dependency shit.**

## 🚀 DXT EXTENSION BUILD & INSTALL PROCESS

### CRITICAL: Source Code Changes Don't Auto-Update Extensions
**Problem:** Fixing bugs in repo source doesn't update installed DXT extensions

```powershell
# ❌ WRONG - Just fixing source code
git commit -m "Fixed Unicode bug"
# Extension still broken - old version cached!

# ✅ CORRECT - Full rebuild cycle
# 1. Uninstall extension in Claude Desktop UI
# 2. Rebuild DXT package
dxt build
# 3. Drag-drop new .dxt file to Claude Desktop
```

### MANDATORY Workflow After Source Fixes
```powershell
# 1. Test source works
cd D:/Dev/repos/{extension-name}
python -m {extension_name}.server  # Must start without errors

# 2. Uninstall old extension
# Claude Desktop > Extensions > {name} > Disable/Remove

# 3. Build new DXT
dxt build

# 4. Install new DXT  
# Drag dist/{name}.dxt onto Claude Desktop
```

**RULE:** DXT extensions are separate copies. Source changes require full rebuild + reinstall cycle.