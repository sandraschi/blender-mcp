# DXT Extension Building Standards - Definitive Guide

**Author:** Sandra Schi  
**Date:** 2025-08-13  
**Status:** DEFINITIVE - ALL MCP Extensions Must Follow These Rules

## 🎯 FUNDAMENTAL PRINCIPLES

### ❌ NEVER DO IN DXT EXTENSIONS

1. **NO Shell-Style Variable Substitution in Build Scripts**
   - ❌ `"${BLENDER_EXECUTABLE}"` in build_dxt.py
   - ❌ `"${DOCKER_PATH}"` hardcoded in packaging
   - Claude Desktop does NOT resolve shell variables in manifest

2. **NO Hardcoded External Paths**
   - ❌ `C:\Program Files\Blender\blender.exe`
   - ❌ `/usr/bin/docker`
   - ❌ Assuming PATH contains executables

3. **NO `dxt init` Command Line Prompting**
   - ❌ Primitive 1980s-style CLI questionnaires
   - ❌ Manual typing of manifest fields
   - Use AI to generate comprehensive manifest.json files

### ✅ CORRECT DXT PATTERNS

## 🚀 AI-FIRST MANIFEST GENERATION

**Our Approach:**
- Generate manifest.json with AI prompts
- Create dozens of optimized sample configurations
- Iterate with natural language refinement
- Generate comprehensive tool/prompt libraries

**Example AI Prompt:**
```
Generate a DXT manifest.json for a Blender MCP extension with:
- User config for Blender executable path detection
- 10 professional 3D modeling tools
- Japanese architecture and boudoir photography presets
- Comprehensive permissions and compatibility
```

## 📋 USER CONFIG PATTERNS

### External Executable Detection
```json
"user_config": {
  "blender_executable": {
    "type": "file",
    "title": "Blender Executable",
    "description": "Select your Blender installation",
    "required": true,
    "default": "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
    "filter": [".exe"],
    "validation": {
      "must_exist": true,
      "executable": true
    }
  }
}
```

### Directory Configuration
```json
"workspace_directory": {
  "type": "directory",
  "title": "Workspace Directory",
  "description": "Directory for project files",
  "required": true,
  "default": "${HOME}/Documents/Projects"
}
```

### API Key Configuration
```json
"api_key": {
  "type": "string",
  "title": "API Key",
  "description": "Service API key",
  "sensitive": true,
  "required": true
}
```

## 🔧 TEMPLATE LITERALS

### Supported by Claude Desktop
- `${__dirname}` - Extension installation directory
- `${user_config.key}` - User-provided configuration
- `${HOME}` - User home directory
- `${PROGRAM_FILES}` - Windows Program Files (platform-specific)

### Usage in mcp_config
```json
"mcp_config": {
  "command": "python",
  "args": ["-m", "my_extension.server"],
  "env": {
    "EXTERNAL_TOOL": "${user_config.tool_executable}",
    "WORKSPACE_DIR": "${user_config.workspace_directory}",
    "API_KEY": "${user_config.api_key}"
  }
}
```

## 📦 PACKAGING WORKFLOW

### 1. AI-Generated Manifest
- Use AI to create comprehensive manifest.json
- Include all user_config requirements
- Define proper permissions and compatibility

### 2. Remove Build Script Hardcoding
```python
# ❌ WRONG - hardcoded in build script
"env": {
    "TOOL_PATH": "${EXTERNAL_TOOL}"  # This becomes literal!
}

# ✅ CORRECT - use user_config
"env": {
    "TOOL_PATH": "${user_config.tool_executable}"
}
```

### 3. Runtime Detection Fallback
```python
def detect_external_tool():
    """Runtime detection of external dependencies"""
    # Check user config first
    configured_path = os.environ.get('TOOL_EXECUTABLE')
    if configured_path and os.path.exists(configured_path):
        return configured_path
    
    # Check common installation paths
    common_paths = [
        "C:\\Program Files\\Tool\\tool.exe",
        "/usr/bin/tool",
        "/Applications/Tool.app/Contents/MacOS/Tool"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # Check PATH
    return shutil.which("tool")
```

### 4. Use DXT Pack Only
```bash
# Only use the packaging part of DXT toolchain
dxt pack . my-extension.dxt

# Skip the primitive dxt init questionnaire
# Generate manifest.json with AI instead
```

## 🎯 VALIDATION CHECKLIST

### Pre-Build
- [ ] No literal `${VAR}` strings in build scripts
- [ ] No hardcoded absolute paths to external tools
- [ ] All external dependencies in user_config
- [ ] AI-generated manifest.json with comprehensive metadata

### Manifest Requirements
- [ ] user_config section for ALL external dependencies
- [ ] Proper template literals (`${user_config.key}`)
- [ ] Sensible defaults for common installation paths
- [ ] Clear descriptions and validation rules

### Testing
- [ ] Test on clean machine without external tools
- [ ] Test user config flow in Claude Desktop
- [ ] Test with different tool versions/paths
- [ ] Test error scenarios and validation

## 🔄 MIGRATION FOR EXISTING EXTENSIONS

For all our MCP servers (local-llm-mcp, fastsearch, vboxmcp, etc.):

1. **Audit External Dependencies**
   - Identify all hardcoded paths
   - Find shell variable assumptions
   - List required external tools

2. **Add User Config**
   - Convert hardcoded paths to user_config
   - Add proper defaults and validation
   - Include clear descriptions

3. **Update Build Scripts**
   - Remove literal template strings
   - Use AI-generated manifests
   - Test packaging workflow

4. **Implement Runtime Detection**
   - Add fallback detection code
   - Provide clear error messages
   - Handle missing dependencies gracefully

## 🎪 EXAMPLES

### Blender MCP Extension
- user_config for blender_executable
- Runtime detection with common paths
- Clear error messages for missing Blender

### Docker MCP Extension
- user_config for docker_executable
- Detection of Docker Desktop vs Docker CLI
- Platform-specific defaults

### Git MCP Extension
- user_config for git_executable
- Repository directory configuration
- SSH key and credential handling

## 📝 KEY TAKEAWAYS

1. **AI-First Development:** Generate manifest.json with AI, not CLI tools
2. **User Config Everything:** Any external dependency needs user_config
3. **Template Literals:** Use `${user_config.key}` for runtime substitution
4. **No Hardcoding:** Never assume installation paths or PATH contents
5. **Comprehensive Testing:** Test on clean machines with missing dependencies

**This prevents 4-hour debugging sessions and ensures extensions work everywhere!**
