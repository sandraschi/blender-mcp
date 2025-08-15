# DXT Extension Building - Complete Guide for All MCP Servers

**Version:** 2.1  
**Date:** 2025-08-15  
**Applies to:** ALL MCP server repositories  
**AI Tools:** Windsurf, Cursor, Claude Code  
**Critical Update:** Claude Desktop Extension Path Bug Workarounds  

## 🎯 CRITICAL RULES - READ FIRST

### ❌ NEVER DO
1. **NO `dxt init`** - Primitive 1980s CLI prompting
2. **NO manual manifest editing** - Use AI to generate comprehensive configs
3. **NO custom build scripts** - Use official `dxt pack` only
4. **NO hardcoded external paths** - Use `user_config` for all dependencies
5. **NO shell variable substitution** - Claude Desktop doesn't resolve `${VAR}` literals
6. **NO fastmcp < 2.10.1** - CRITICAL: Use fastmcp>=2.10.1,<3.0.0 for stability
7. **NO incorrect Python paths** - DXT requires explicit `cwd` and `PYTHONPATH` setup

### ✅ ALWAYS DO
1. **AI-generate manifest.json** - Comprehensive, professional configurations
2. **Use `user_config`** - For ALL external dependencies (executables, directories, API keys)
3. **Template literals** - `${user_config.key}` for runtime substitution
4. **Official DXT toolchain** - `dxt validate`, `dxt pack`, `dxt sign`
5. **GitHub Actions automation** - Tag-based releases with CI/CD
6. **Exact fastmcp version** - `fastmcp>=2.10.1,<3.0.0` in requirements.txt
7. **Python path fixes** - Explicit `cwd` and `PYTHONPATH` in mcp_config
**Use `dxt validate`** - Always use `dxt validate` to validate the final extension packag
8. **Use `dxt pack`** - Always use `dxt pack` to create the final extension package. do not use a script to create the final extension package
9. **Use `dxt sign`** - Always use `dxt sign` to sign the final extension package
10. **Include everything** - Include all requirements and dependencies, not just sources


## 📋 DXT MANIFEST.JSON SPECIFICATION

### Required Fields
```json
{
  "dxt_version": "0.1",
  "name": "your-mcp-server",
  "version": "1.0.0",
  "description": "Brief description for extension store",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "server": {
    "type": "python",
    "entry_point": "src/your_mcp/server.py",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "your_mcp.server"],
      "cwd": "src",
      "env": {
        "PYTHONPATH": "src",
        "EXTERNAL_TOOL": "${user_config.external_tool}",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### 🚨 CRITICAL PYTHON PATH FIX

**Problem**: DXT extensions fail with `ModuleNotFoundError` because Python module path resolution is incorrect.

**Root Cause**: DXT runner executes from extension root, but Python modules are in `src/` subdirectory.

**Solution**: ALWAYS include these fields in Python-based DXT manifests. 

**IMPORTANT**: Do NOT use `cwd` in `mcp_config` as it will cause validation to fail. Instead, ensure your Python path is set correctly using `PYTHONPATH` environment variable.

```json
{
  "server": {
    "type": "python",
    "entry_point": "src/your_mcp/server.py",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "your_mcp.server"],
      "env": {
        "PYTHONPATH": "${PWD}",  // ⭐ CRITICAL: Use ${PWD} to reference the package root
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**File Structure that requires this fix:**
```
your-extension.dxt/
├── manifest.json
├── requirements.txt
├── src/                           // ⭐ Python modules here
│   └── your_mcp/
│       ├── __init__.py
│       ├── server.py              // Entry point
│       └── ...
└── lib/                           // Dependencies here
    ├── fastmcp/
    └── ...
```

## 📝 PROMPTS CONFIGURATION

### Prompt Files Structure

DXT supports three types of prompt files that should be placed in a `prompts/` directory:

```
your-extension.dxt/
├── prompts/
│   ├── system.md     # System prompt (required)
│   ├── user.md       # User prompt template (required)
│   └── examples.json # Example interactions (optional)
└── ...
```

### 1. System Prompt (`system.md`)
- Defines the AI's role and capabilities
- Should include:
  - Core functionality description
  - Available tools and their purposes
  - Response format guidelines
  - Safety and security constraints

### 2. User Prompt (`user.md`)
- Template for user interactions
- Can include placeholders for dynamic content
- Should be clear and concise

### 3. Examples (`examples.json`)
- Optional but highly recommended
- Provides example interactions
- Helps the AI understand expected behavior
- Format:
  ```json
  [
    {
      "input": "user query or command",
      "output": "expected AI response"
    }
  ]
  ```

### Referencing Prompts in manifest.json

Add a `prompts` section to your manifest.json:

```json
{
  "name": "your-mcp-server",
  "version": "1.0.0",
  "prompts": {
    "system": "prompts/system.md",
    "user": "prompts/user.md",
    "examples": "prompts/examples.json"
  },
  "server": {
    "type": "python",
    "entry_point": "src/your_mcp/server.py"
  }
}
```

### Best Practices for Prompts

1. **Be Specific**: Clearly define the AI's capabilities and limitations
2. **Use Markdown**: Format prompts with headers, lists, and code blocks
3. **Version Control**: Track prompt changes in version control
4. **Test Thoroughly**: Validate prompts with various inputs
5. **Keep Secure**: Don't include sensitive information in prompts
6. **Document Assumptions**: Note any assumptions about the environment or user knowledge

## 🔧 FASTMCP VERSION REQUIREMENT

**CRITICAL**: Must use fastmcp>=2.10.1,<3.0.0 for DXT compatibility.

**requirements.txt:**
```txt
# Core MCP dependencies - EXACT VERSION REQUIRED
fastmcp>=2.10.1,<3.0.0
fastapi>=0.95.0
uvicorn[standard]>=0.22.0
pydantic>=2.0.0,<3.0.0
python-dotenv>=1.0.0

# System utilities
psutil>=5.9.0
typing-extensions>=4.5.0
python-dateutil>=2.8.2
httpx>=0.24.0

# Development dependencies (optional)
# pytest>=7.4.0
# black>=23.7.0
# mypy>=1.4.0
```

**Why fastmcp 2.10.1?**
- Fixes critical DXT runtime compatibility issues
- Resolves async/await handling in DXT environments
- Proper error handling for extension context
- Stable API surface for production use

### User Config Patterns

#### External Executable
```json
"user_config": {
  "external_tool": {
    "type": "file",
    "title": "External Tool Executable",
    "description": "Select your tool installation (tool.exe on Windows, tool on macOS/Linux)",
    "required": true,
    "default": "C:\\Program Files\\Tool\\tool.exe",
    "filter": [".exe"],
    "validation": {
      "must_exist": true,
      "executable": true
    }
  }
}
```

#### Directory Selection
```json
"workspace_directory": {
  "type": "directory", 
  "title": "Workspace Directory",
  "description": "Directory for project files and outputs",
  "required": true,
  "default": "${HOME}/Documents/Workspace"
}
```

#### API Key/Secret
```json
"api_key": {
  "type": "string",
  "title": "API Key",
  "description": "Your service API key",
  "sensitive": true,
  "required": true
}
```

#### Boolean Flag
```json
"debug_mode": {
  "type": "boolean",
  "title": "Debug Mode", 
  "description": "Enable detailed logging for troubleshooting",
  "required": false,
  "default": false
}
```

#### Multiple Selection
```json
"allowed_directories": {
  "type": "directory",
  "title": "Allowed Directories",
  "description": "Directories this extension can access",
  "multiple": true,
  "required": true,
  "default": ["${HOME}/Documents", "${HOME}/Projects"]
}
```

### Template Literals

#### Supported Variables
- `${__dirname}` - Extension installation directory
- `${user_config.key}` - User-provided configuration value
- `${HOME}` - User home directory
- `${PROGRAM_FILES}` - Windows Program Files (platform-specific)

#### Usage in mcp_config
```json
"mcp_config": {
  "command": "python",
  "args": ["-m", "your_mcp.server"],
  "cwd": "src",
  "env": {
    "PYTHONPATH": "src",
    "TOOL_EXECUTABLE": "${user_config.tool_executable}",
    "WORKSPACE_DIR": "${user_config.workspace_directory}",
    "API_KEY": "${user_config.api_key}",
    "DEBUG": "${user_config.debug_mode}",
    "EXTENSION_DIR": "${__dirname}",
    "PYTHONUNBUFFERED": "1"
  }
}
```

### Complete Manifest Example (Production-Ready)
```json
{
  "dxt_version": "0.1",
  "name": "example-mcp",
  "version": "1.0.0",
  "description": "Example MCP server with external tool integration",
  "long_description": "Comprehensive MCP server that demonstrates proper external dependency handling, user configuration, and professional tool integration patterns using FastMCP 2.10.1+.",
  "author": {
    "name": "Sandra Schi",
    "email": "sandra@sandraschi.dev",
    "url": "https://github.com/sandraschi"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/sandraschi/example-mcp"
  },
  "homepage": "https://github.com/sandraschi/example-mcp",
  "documentation": "https://github.com/sandraschi/example-mcp/blob/main/README.md",
  "support": "https://github.com/sandraschi/example-mcp/issues",
  "license": "MIT",
  "keywords": ["mcp", "example", "external-tools", "automation", "fastmcp"],
  "icon": "assets/icon.png",
  "screenshots": [
    "assets/screenshots/main-interface.png",
    "assets/screenshots/configuration.png"
  ],
  "server": {
    "type": "python",
    "entry_point": "src/example_mcp/server.py",
    "mcp_config": {
      "command": "python", 
      "args": ["-m", "example_mcp.server"],
      "cwd": "src",
      "env": {
        "PYTHONPATH": "src",
        "TOOL_EXECUTABLE": "${user_config.tool_executable}",
        "WORKSPACE_DIR": "${user_config.workspace_directory}",
        "API_KEY": "${user_config.api_key}",
        "DEBUG_MODE": "${user_config.debug_mode}",
        "PYTHONUNBUFFERED": "1"
      }
    }
  },
  "user_config": {
    "tool_executable": {
      "type": "file",
      "title": "External Tool Executable",
      "description": "Select your external tool executable",
      "required": true,
      "default": "C:\\Program Files\\Tool\\tool.exe",
      "filter": [".exe"]
    },
    "workspace_directory": {
      "type": "directory",
      "title": "Workspace Directory",
      "description": "Directory for project files and outputs",
      "required": true,
      "default": "${HOME}/Documents/ExampleMCP"
    },
    "api_key": {
      "type": "string",
      "title": "API Key",
      "description": "Your service API key (stored securely)",
      "sensitive": true,
      "required": false
    },
    "debug_mode": {
      "type": "boolean",
      "title": "Debug Mode",
      "description": "Enable detailed logging",
      "required": false,
      "default": false
    }
  },
  "tools": [
    {
      "name": "process_file",
      "description": "Process files using external tool integration"
    },
    {
      "name": "analyze_data", 
      "description": "Analyze data with AI-powered insights"
    },
    {
      "name": "generate_report",
      "description": "Generate comprehensive reports"
    }
  ],
  "prompts": [
    {
      "name": "analyze_project",
      "description": "Analyze project structure and provide insights",
      "arguments": ["project_type", "analysis_depth"],
      "text": "Analyze the ${arguments.project_type} project with ${arguments.analysis_depth} level analysis. Provide comprehensive insights and recommendations."
    }
  ],
  "tools_generated": true,
  "prompts_generated": false,
  "compatibility": {
    "platforms": ["windows", "macos", "linux"],
    "python_version": ">=3.8"
  },
  "permissions": {
    "filesystem": {
      "read": true,
      "write": true,
      "directories": ["${user_config.workspace_directory}"]
    },
    "network": {
      "allowed": true,
      "domains": ["api.example.com"]
    },
    "system": {
      "execute_external": true,
      "processes": ["${user_config.tool_executable}"]
    }
  },
  "dependencies": [
    "fastmcp>=2.10.1,<3.0.0",
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
    "loguru>=0.7.0"
  ]
}
```

## 🚀 BUILD PROCESS

### Prerequisites
```bash
# Install DXT CLI (official toolchain)
npm install -g @anthropic-ai/dxt

# Install Python dependencies (EXACT VERSIONS)
pip install "fastmcp>=2.10.1,<3.0.0"
pip install -r requirements.txt
```

### Repository Structure (Updated)
```
your-mcp-server/
├── .github/
│   └── workflows/
│       └── build-dxt.yml          # GitHub Actions
├── dxt/
│   ├── manifest.json              # AI-generated manifest
│   └── assets/                    # Icons, screenshots
├── src/                           # ⭐ Python source code HERE
│   └── your_mcp/                  # Main Python package
│       ├── __init__.py
│       ├── server.py              # Main server entry point
│       └── handlers/              # Tool handlers
├── docs/
│   └── DXT_BUILDING_GUIDE.md      # This file
├── requirements.txt               # Python dependencies (fastmcp>=2.10.1)
├── build_github.py               # CI/CD build script
└── README.md
```

### Local Development
```bash
# 1. AI-generate manifest.json (place in dxt/manifest.json)
# ENSURE: fastmcp>=2.10.1 in requirements.txt
# ENSURE: cwd: "src" and PYTHONPATH: "src" in mcp_config

# 2. Validate manifest
cd dxt
dxt validate manifest.json

# 3. Build DXT package
dxt pack . ../dist/your-mcp-server-1.0.0.dxt

# 4. Test installation
# Drag dist/*.dxt to Claude Desktop
```

## 🚨 CLAUDE DESKTOP EXTENSION PATH BUGS

### Critical Bug: Incorrect Extension Path Resolution

**Symptoms:**
```
python.exe: can't open file 'C:\\Users\\user\\AppData\\Local\\AnthropicClaude\\app-{version}\\server\\main.py': [Errno 2] No such file or directory
[Extension Name] [error] Server disconnected
```

**Root Cause:**
Claude Desktop has a path resolution bug where it tries to execute extensions from the wrong directory:
- **Incorrect (what Claude Desktop tries):** `C:\Users\{user}\AppData\Local\AnthropicClaude\app-{version}\server\main.py`
- **Correct (actual location):** `C:\Users\{user}\AppData\Roaming\Claude\Claude Extensions\local.dxt.{publisher}.{name}\server\main.py`

### 🔧 WORKAROUND STRATEGIES

#### Strategy 1: Manual Configuration Entry (Immediate Fix)

When an extension fails with path errors, add a manual entry to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "your-extension-manual": {
      "command": "python",
      "args": ["C:/Users/{username}/AppData/Roaming/Claude/Claude Extensions/local.dxt.{publisher}.{extension-name}/server/main.py"],
      "cwd": "C:/Users/{username}/AppData/Roaming/Claude/Claude Extensions/local.dxt.{publisher}.{extension-name}",
      "env": {
        "PYTHONPATH": "C:/Users/{username}/AppData/Roaming/Claude/Claude Extensions/local.dxt.{publisher}.{extension-name}/server;C:/Users/{username}/AppData/Roaming/Claude/Claude Extensions/local.dxt.{publisher}.{extension-name}/server/lib",
        "PYTHONUNBUFFERED": "1",
        "EXTENSION_DEBUG": "1"
      }
    }
  }
}
```

**Steps:**
1. Backup your config: `Copy-Item "$env:APPDATA\Claude\claude_desktop_config.json" "C:\temp\claude_config_backup.json"`
2. Find your extension's actual path in: `%APPDATA%\Claude\Claude Extensions\`
3. Add manual entry with correct paths
4. Restart Claude Desktop
5. Disable the broken extension to avoid conflicts

#### Strategy 2: Prevention in DXT Manifest Design

Update your `manifest.json` to be more robust against path resolution bugs:

```json
{
  "server": {
    "type": "python",
    "entry_point": "server/main.py",
    "mcp_config": {
      "command": "python",
      "args": ["${__dirname}/server/main.py"],
      "cwd": "${__dirname}",
      "env": {
        "PYTHONPATH": "${__dirname}/server;${__dirname}/server/lib;${__dirname}",
        "PYTHONUNBUFFERED": "1",
        "EXTENSION_ROOT": "${__dirname}"
      }
    }
  }
}
```

**Key Prevention Elements:**
- Use `${__dirname}` template literals for all paths
- Include comprehensive PYTHONPATH with fallbacks
- Add extension root environment variable for runtime detection
- Use relative paths in entry_point when possible

#### Strategy 3: User Documentation Template

Include this troubleshooting section in your extension's README.md:

```markdown
## 🚨 Troubleshooting Installation

### Extension Fails to Start ("Server disconnected")

**Symptoms:** Extension shows as failed in Claude Desktop settings.

**Diagnosis:**
1. Check logs: `%APPDATA%\Claude\logs\mcp-server-{ExtensionName}.log`
2. Look for errors like: `can't open file 'C:\\Users\\...\\app-{version}\\server\\main.py'`
3. This indicates a Claude Desktop path resolution bug

**Fix:** Apply manual configuration workaround:

1. **Backup your config:**
   ```powershell
   Copy-Item "$env:APPDATA\Claude\claude_desktop_config.json" "$env:TEMP\claude_config_backup.json"
   ```

2. **Find your extension path:**
   ```powershell
   Get-ChildItem "$env:APPDATA\Claude\Claude Extensions" | Where-Object Name -like "*{your-extension-name}*"
   ```

3. **Add manual entry to `claude_desktop_config.json`:**
   ```json
   {
     "mcpServers": {
       "{your-extension-name}-manual": {
         "command": "python",
         "args": ["C:/Users/{YOUR_USERNAME}/AppData/Roaming/Claude/Claude Extensions/local.dxt.{publisher}.{extension-name}/server/main.py"],
         "cwd": "C:/Users/{YOUR_USERNAME}/AppData/Roaming/Claude/Claude Extensions/local.dxt.{publisher}.{extension-name}",
         "env": {
           "PYTHONPATH": "C:/Users/{YOUR_USERNAME}/AppData/Roaming/Claude/Claude Extensions/local.dxt.{publisher}.{extension-name}/server",
           "PYTHONUNBUFFERED": "1"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

5. **Disable the broken extension** to avoid conflicts

This workaround bypasses the Claude Desktop path resolution bug.
```

### 🔍 DEBUGGING EXTENSION PATH ISSUES

#### Log Analysis

**Primary log location:**
```
%APPDATA%\Claude\logs\mcp-server-{ExtensionName}.log
```

**Error patterns to look for:**
```
can't open file 'C:\\Users\\...\\app-{version}\\server\\main.py'
ModuleNotFoundError: No module named 'your_extension'
Server disconnected unexpectedly
```

#### PowerShell Diagnostic Script

```powershell
# Quick extension path diagnostic
$extensionName = "your-extension-name"
$username = $env:USERNAME
$appDataPath = $env:APPDATA

# Check if extension is installed
$extensionPath = Get-ChildItem "$appDataPath\Claude\Claude Extensions" | Where-Object Name -like "*$extensionName*"
if ($extensionPath) {
    Write-Host "✅ Extension found: $($extensionPath.FullName)"
    
    # Check for main.py
    $mainPy = Join-Path $extensionPath.FullName "server\main.py"
    if (Test-Path $mainPy) {
        Write-Host "✅ Main script found: $mainPy"
    } else {
        Write-Host "❌ Main script NOT found: $mainPy"
    }
    
    # Check logs
    $logPath = "$appDataPath\Claude\logs\mcp-server-$extensionName.log"
    if (Test-Path $logPath) {
        Write-Host "📋 Recent log entries:"
        Get-Content $logPath -Tail 10
    }
} else {
    Write-Host "❌ Extension not found in: $appDataPath\Claude\Claude Extensions"
}
```

## 🚧 TROUBLESHOOTING DXT EXTENSIONS

### Common Python Module Issues

#### Problem: ModuleNotFoundError
```
python.exe: Error while finding module specification for 'your_mcp.server' 
(ModuleNotFoundError: No module named 'your_mcp')
[your-mcp] [error] Server disconnected
```

#### Solution: Verify Python Path Configuration
Check manifest.json has correct paths:
```json
{
  "server": {
    "mcp_config": {
      "command": "python",
      "args": ["-m", "your_mcp.server"],
      "cwd": "src",                    // ⭐ Must point to module directory
      "env": {
        "PYTHONPATH": "src",           // ⭐ Must include module directory
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

#### Manual MCP Configuration Fallback
If DXT fails, configure manually in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "your-mcp-server": {
      "command": "python",
      "args": ["-m", "your_mcp.server"],
      "cwd": "C:/Users/{user}/AppData/Roaming/Claude/Claude Extensions/local.dxt.{publisher}.{name}/src",
      "env": {
        "PYTHONPATH": "C:/Users/{user}/AppData/Roaming/Claude/Claude Extensions/local.dxt.{publisher}.{name}/src",
        "PYTHONUNBUFFERED": "1",
        "YOUR_CONFIG": "your_value"
      }
    }
  }
}
```

### FastMCP Version Issues

#### Problem: Incompatible FastMCP Version
```
ImportError: cannot import name 'FastMCP' from 'fastmcp'
AttributeError: 'FastMCP' object has no attribute 'some_method'
```

#### Solution: Update to FastMCP 2.10.1+
```bash
# Uninstall old version
pip uninstall fastmcp

# Install exact version
pip install "fastmcp>=2.10.1,<3.0.0"

# Verify installation
python -c "import fastmcp; print(fastmcp.__version__)"
```

#### Update requirements.txt
```txt
# CRITICAL: Use exact version constraints
fastmcp>=2.10.1,<3.0.0
fastapi>=0.95.0
uvicorn[standard]>=0.22.0
pydantic>=2.0.0,<3.0.0
```

## 🚀 GITHUB CI/CD AUTOMATION

### Complete GitHub Actions Workflow
Create `.github/workflows/build-dxt.yml`:

```yaml
name: Build and Release DXT Extension

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to build (e.g., 1.0.0)'
        required: true
        default: '1.0.0'

jobs:
  build-dxt:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install DXT CLI
      run: npm install -g @anthropic-ai/dxt
      
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install "fastmcp>=2.10.1,<3.0.0"
        pip install -r requirements.txt
        
    - name: Create dist directory
      run: mkdir -p dist
        
    - name: Validate manifest.json
      run: dxt validate dxt/manifest.json
      
    - name: Build DXT extension
      run: |
        cd dxt
        dxt pack . ../dist/${{ github.event.repository.name }}-${{ github.event.inputs.version || github.ref_name }}.dxt
        
    - name: Sign DXT extension (optional)
      if: ${{ secrets.DXT_SIGNING_KEY }}
      run: |
        echo "${{ secrets.DXT_SIGNING_KEY }}" > signing.key
        dxt sign dist/*.dxt --key signing.key
        rm signing.key
        
    - name: Upload DXT artifact
      uses: actions/upload-artifact@v3
      with:
        name: dxt-extension
        path: dist/*.dxt
        retention-days: 30
        
    - name: Create GitHub Release
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: dist/*.dxt
        generate_release_notes: true
        draft: false
        prerelease: false
        body: |
          ## DXT Extension Release
          
          Download the `.dxt` file below and drag it to Claude Desktop for one-click installation.
          
          ### Installation
          1. Download the `.dxt` file from the assets below
          2. Drag the file to Claude Desktop
          3. Follow the configuration prompts
          4. Restart Claude Desktop
          
          ### Dependencies
          - FastMCP 2.10.1+ (bundled)
          - Python 3.8+ (built into Claude Desktop)
          
          ### What's New
          See the auto-generated release notes below.
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🔧 VALIDATION RULES

### Manifest Validation
```bash
# Always validate before building
dxt validate dxt/manifest.json

# Common issues:
# - Missing cwd and PYTHONPATH for Python servers
# - fastmcp version < 2.10.1 in dependencies
# - Invalid template literal syntax
# - Incorrect user_config types
```

### Python Environment Validation
```bash
# Test Python module import manually
cd src
python -c "import your_mcp.server; print('✅ Module imports successfully')"

# Test FastMCP version
python -c "import fastmcp; print(f'FastMCP version: {fastmcp.__version__}')"

# Verify >= 2.10.1
python -c "import fastmcp; assert fastmcp.__version__ >= '2.10.1', 'Update FastMCP!'"
```

### DXT Package Testing
```bash
# Build test package
cd dxt
dxt pack . ../test-package.dxt

# Install test package in Claude Desktop
# Verify configuration prompts work
# Test extension functionality
# Check logs for errors
```

## 🎯 COMMON PATTERNS BY MCP TYPE

### Tool Integration MCP (Blender, Docker, Git)
```json
{
  "user_config": {
    "tool_executable": {
      "type": "file",
      "title": "Tool Executable",
      "description": "Select your tool installation",
      "required": true,
      "default": "C:\\Program Files\\Tool\\tool.exe"
    }
  },
  "server": {
    "mcp_config": {
      "cwd": "src",
      "env": {
        "PYTHONPATH": "src",
        "TOOL_PATH": "${user_config.tool_executable}"
      }
    }
  }
}
```

### API Service MCP (OpenAI, Anthropic, etc.)
```json
{
  "user_config": {
    "api_key": {
      "type": "string", 
      "title": "API Key",
      "description": "Your service API key",
      "sensitive": true,
      "required": true
    }
  },
  "server": {
    "mcp_config": {
      "cwd": "src",
      "env": {
        "PYTHONPATH": "src",
        "API_KEY": "${user_config.api_key}"
      }
    }
  }
}
```

### File Processing MCP (Document, Media, etc.)
```json
{
  "user_config": {
    "input_directory": {
      "type": "directory",
      "title": "Input Directory",
      "description": "Directory containing files to process",
      "required": true,
      "default": "${HOME}/Documents/Input"
    }
  },
  "server": {
    "mcp_config": {
      "cwd": "src",
      "env": {
        "PYTHONPATH": "src",
        "INPUT_DIR": "${user_config.input_directory}"
      }
    }
  }
}
```

## 📝 CHECKLIST FOR NEW MCP SERVERS

### Pre-Development
- [ ] Plan Python package structure in `src/` directory
- [ ] Identify ALL external dependencies (tools, APIs, directories)
- [ ] Plan user_config structure for each dependency
- [ ] Choose appropriate types (file, directory, string, boolean)
- [ ] Design sensible defaults for common platforms
- [ ] **Plan manual config fallback strategy** for Claude Desktop path bugs

### Development
- [ ] Use fastmcp>=2.10.1,<3.0.0 in requirements.txt
- [ ] Structure Python modules in `src/your_mcp/` directory
- [ ] Create comprehensive manifest.json with AI
- [ ] Include `cwd: "src"` and `PYTHONPATH: "src"` in mcp_config
- [ ] Implement runtime detection fallbacks in Python
- [ ] Add proper error handling for missing dependencies

### Building
- [ ] Validate Python import: `cd src && python -c "import your_mcp.server"`
- [ ] Validate FastMCP version: `python -c "import fastmcp; print(fastmcp.__version__)"`
- [ ] Validate manifest: `dxt validate dxt/manifest.json`
- [ ] Build package: `dxt pack . ../dist/package.dxt`
- [ ] Test installation on clean Claude Desktop
- [ ] Verify user configuration prompts work correctly

### Release
- [ ] Setup GitHub Actions workflow with Python 3.11
- [ ] Include fastmcp>=2.10.1 installation step in CI
- [ ] Create release tag: `git tag v1.0.0`
- [ ] Verify automatic build and release
- [ ] Test downloaded .dxt package installation
- [ ] Document troubleshooting for manual MCP fallback

### Post-Release
- [ ] Monitor installation success rates
- [ ] Track user configuration completion
- [ ] Address issues and feature requests
- [ ] **Document manual config workaround** if extension path bugs occur
- [ ] Plan updates and improvements
- [ ] Keep FastMCP dependency current
- [ ] **Monitor Claude Desktop path resolution bug reports**

## 🎪 EXAMPLES

### Blender MCP (Updated)
```json
{
  "dependencies": ["fastmcp>=2.10.1,<3.0.0"],
  "server": {
    "type": "python",
    "entry_point": "src/blender_mcp/server.py",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "blender_mcp.server"],
      "cwd": "src",
      "env": {
        "PYTHONPATH": "src",
        "BLENDER_EXECUTABLE": "${user_config.blender_executable}"
      }
    }
  }
}
```

### Docker MCP (Updated)
```json
{
  "dependencies": ["fastmcp>=2.10.1,<3.0.0"],
  "server": {
    "type": "python", 
    "entry_point": "src/docker_mcp/server.py",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "docker_mcp.server"],
      "cwd": "src",
      "env": {
        "PYTHONPATH": "src",
        "DOCKER_EXECUTABLE": "${user_config.docker_path}"
      }
    }
  }
}
```

### Database MCP (Updated)
```json
{
  "dependencies": ["fastmcp>=2.10.1,<3.0.0"],
  "server": {
    "type": "python",
    "entry_point": "src/database_mcp/server.py", 
    "mcp_config": {
      "command": "python",
      "args": ["-m", "database_mcp.server"],
      "cwd": "src",
      "env": {
        "PYTHONPATH": "src",
        "DATABASE_URL": "${user_config.connection_string}"
      }
    }
  }
}
```

## 🆕 WHAT'S NEW IN VERSION 2.1

### Critical Bug Documentation
1. **Claude Desktop Extension Path Bug**: Comprehensive troubleshooting for path resolution failures
2. **Manual Config Workarounds**: Three strategies to bypass extension path bugs
3. **Prevention Techniques**: DXT manifest patterns to reduce bug impact
4. **User Documentation Templates**: Ready-to-use troubleshooting guides
5. **Diagnostic Tools**: PowerShell scripts for quick path issue detection

### Updated Checklists
- Added manual config fallback planning to pre-development
- Enhanced post-release monitoring for path resolution issues
- Integrated extension bug reporting into maintenance workflows

## 🆕 WHAT'S NEW IN VERSION 2.0

### Critical Updates
1. **FastMCP 2.10.1 Requirement**: Mandatory for DXT compatibility
2. **Python Path Fix**: Explicit `cwd` and `PYTHONPATH` configuration
3. **Updated Examples**: All examples include new requirements
4. **Enhanced Troubleshooting**: Manual MCP fallback procedures
5. **CI/CD Updates**: GitHub Actions with correct dependency installation

### Breaking Changes
- **FastMCP < 2.10.1 no longer supported** in DXT extensions
- **Python servers require explicit path configuration** in manifest
- **All existing DXT packages need rebuilding** with new requirements

### Migration Guide
1. Update `requirements.txt`: `fastmcp>=2.10.1,<3.0.0`
2. Add to manifest `mcp_config`: `"cwd": "src"` and `"PYTHONPATH": "src"`
3. Rebuild DXT package: `dxt pack . ../dist/updated-package.dxt`
4. Test installation and fallback to manual MCP if needed

This guide provides everything needed to build professional DXT extensions that work reliably across all platforms and installations with the latest FastMCP improvements and Python path fixes. Follow these patterns for consistent, high-quality MCP server packaging that actually works in production.
