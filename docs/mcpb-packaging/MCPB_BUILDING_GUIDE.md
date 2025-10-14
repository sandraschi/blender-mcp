# MCPB Extension Building - Complete Guide for MCP Servers

**Version:** 3.1.0  
**Date:** 2025-01-15  
**Applies to:** ALL MCP server repositories  
**AI Tools:** Windsurf, Cursor, Claude Code  

## 🚨 IMPORTANT: DXT is now MCPB

**BREAKING CHANGE:** As of January 2025, DXT (Deployment eXtension Toolkit) has been renamed to **MCPB (MCP Bundle)**. This is more than just a name change - it reflects the evolution of the toolkit into a more comprehensive MCP packaging solution.

### Migration Summary

| Old (DXT) | New (MCPB) | Notes |
|-----------|------------|-------|
| `dxt` CLI commands | `mcpb` CLI commands | All commands now use `mcpb` prefix |
| `dxt.json` | `mcpb.json` | Configuration file renamed |
| `dxt_manifest.json` | `mcpb_manifest.json` | Manifest file renamed |
| `.dxt` packages | `.mcpb` packages | Package extension changed |
| `@anthropic-ai/dxt` | `@anthropic-ai/mcpb` | NPM package renamed |

### Quick Migration Steps

1. **Update CLI Installation:**
   ```bash
   npm uninstall -g @anthropic-ai/dxt
   npm install -g @anthropic-ai/mcpb
   ```

2. **Rename Configuration Files:**
   ```bash
   # Rename dxt.json to mcpb.json
   mv dxt.json mcpb.json
   
   # Rename manifest file
   mv dxt_manifest.json mcpb_manifest.json
   ```

3. **Update Commands:**
   ```bash
   # Old DXT commands
   dxt validate
   dxt pack
   dxt sign
   
   # New MCPB commands
   mcpb validate
   mcpb pack
   mcpb sign
   ```

4. **Update Package Extensions:**
   - Build outputs now use `.mcpb` extension instead of `.dxt`
   - All references to `.dxt` files should be updated to `.mcpb`

## 🌟 What is MCPB?

MCPB (MCP Bundle) is a powerful framework developed by Anthropic specifically for packaging and distributing MCP (Model Control Protocol) servers. It provides a standardized way to package, version, and deploy MCP server implementations with all their dependencies.

### Key Components of MCPB

1. **MCPB CLI**: Command-line interface for managing the MCPB packaging and deployment lifecycle
2. **MCPB Runtime**: Execution environment for MCP servers
3. **MCPB Registry**: Central repository for versioned MCP server packages
4. **MCPB SDK**: Tools and libraries for MCP server development

## 🏗️ MCPB Manifest (mcpb_manifest.json)

The `mcpb_manifest.json` file is the heart of any MCP server package. It defines the server's metadata, configuration, dependencies, and runtime requirements.

### Manifest Creation Methods

#### 1. Manual Creation (Not Recommended)

```bash
mcpb init  # Creates a basic manifest (not recommended for production)
```

This method creates a minimal `mcpb_manifest.json` that requires manual updates. It's only suitable for quick testing.

#### 2. AI-Powered Generation (Recommended)

The preferred method is to use AI-powered tools that analyze your repository and generate a comprehensive manifest:

```bash
# Using Windsurf AI (recommended)
windsurf mcpb analyze --path ./src --output mcpb_manifest.json

# Or using the MCPB CLI with AI enhancement
mcpb analyze --ai --output mcpb_manifest.json
```

These tools will:
- Analyze your codebase structure
- Detect entry points and dependencies
- Generate appropriate configuration
- Create proper API bindings
- Set up required permissions

### Key Manifest Sections

```json
{
  "name": "your-extension",
  "version": "1.0.0",
  "description": "Your extension description",
  "main": "dist/main.js",
  "docker": {
    "image": "your-org/your-image:tag",
    "ports": ["8080"]
  },
  "ui": {
    "dashboard-tab": "./ui/dashboard.html"
  },
  "permissions": [
    "containers:read",
    "images:list"
  ]
}
```

## 🤖 Prompt Templates in MCPB

Prompt templates are JSON files that define how AI models should interact with your extension. They're crucial for creating consistent and effective AI-driven features.

### Template Structure

```json
{
  "name": "container-inspection",
  "description": "Inspects a container and provides detailed analysis",
  "parameters": {
    "container_id": {
      "type": "string",
      "description": "ID of the container to inspect"
    }
  },
  "prompt": "Analyze the container with ID {{container_id}}. Check its status, resources, and potential issues.",
  "examples": [
    {
      "input": {"container_id": "abc123"},
      "output": "Container abc123 is running with 2 CPUs and 4GB memory..."
    }
  ]
}
```

### Automatic Template Generation

MCPB can generate prompt templates by analyzing your code and documentation:

```bash
# Generate prompt templates from code analysis
mcpb generate-prompts --source ./src --output ./prompts

# Or use AI to enhance existing prompts
mcpb enhance-prompts --input ./prompts --output ./enhanced-prompts
```

### Prompt Template Features

1. **Variables**: Use `{{variable}}` syntax for dynamic content
2. **Validation**: Automatic parameter validation
3. **Versioning**: Track changes to prompts over time
4. **Localization**: Support for multiple languages
5. **Testing**: Built-in testing framework for prompts

## 🏭 MCPB Standards and Governance

MCPB is developed and maintained by Anthropic with contributions from the open-source community. The project follows semantic versioning and has a well-defined RFC process for major changes.

### Key Standards

1. **Extension Packaging**: OCI-compliant containers
2. **API Design**: RESTful principles with OpenAPI specifications
3. **Security**: OAuth 2.0 and mTLS for authentication
4. **UI/UX**: Follows Docker Design System
5. **Logging**: Structured logging in JSON format

### Versioning

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes and improvements

## 🎯 CRITICAL RULES - READ FIRST

### ❌ NEVER DO

1. **NO `mcpb init`** - Outdated and creates minimal configurations
2. **NO manual configuration** - Use proper `mcpb.json` with all required fields
3. **NO custom build scripts** - Use standard MCPB tooling only
4. **NO hardcoded paths** - Use relative paths in configuration
5. **NO direct server execution** - Always use MCPB CLI tools

### ✅ ALWAYS DO

1. **Use `mcpb.json`** - Central configuration file for all MCPB settings
2. **Follow semantic versioning** - For both package and MCP versions
3. **Use stdio transport** - Required for reliable communication
4. **Specify exact versions** - For all dependencies
5. **Validate before building** - Always run `mcpb validate` first
6. **Verify after building** - Always run `mcpb verify` after packaging
7. **Sign production packages** - Use `mcpb sign` for production releases
8. **Use the build script** - For consistent builds across environments

## 🖥️ MCPB CLI COMMAND SYNTAX

### Core Commands

#### 1. Package Creation

```bash
# Basic package creation
mcpb pack . dist/

# Sign the package (required for production)
mcpb sign --key your-key.pem dist/package.mcpb

# Verify package integrity
mcpb verify --key your-key.pem dist/package.mcpb

# Publish to a MCPB registry (if configured)
mcpb publish --registry your-registry dist/package.mcpb
```

#### 2. MCPB Registries

MCPB registries are package repositories that store and distribute MCPB packages. Here's what you need to know:

##### Official Registries

- **Anthropic's Public Registry**: The primary public registry for production MCPB packages
  - URL: `https://registry.mcpb.anthropic.com` (requires authentication)
  - Managed by Anthropic
  - Requires review and approval for public packages

##### Self-hosted Registries

- **Enterprise/Private Registries**: Some organizations run private MCPB registries
  - Configure via environment variable: `MCPB_REGISTRY_URL`
  - Authentication typically required via API keys or tokens

##### Key Points

- **Authentication**: Always required for publishing

  ```bash
  export MCPB_API_TOKEN='your-token-here'
  ```

- **Scoped Packages**: Use `@scope/package-name` for organization-specific packages
- **Rate Limits**: Public registry has rate limits for downloads/uploads
- **Verification**: All packages are cryptographically signed

#### 3. Build Script (Recommended)

For consistent builds, use the provided PowerShell build script:

```powershell
# Show help and available options
.\scripts\build-mcp-package.ps1 -Help

# Build and sign the package (default behavior)
.\scripts\build-mcp-package.ps1

# Build without signing (for development/testing)
.\scripts\build-mcp-package.ps1 -NoSign

# Specify custom output directory
.\scripts\build-mcp-package.ps1 -OutputDir "C:\builds"
```

## 🎯 CRITICAL RULES - READ FIRST

### ❌ NEVER DO

1. **NO `mcpb init`** - Outdated and creates minimal configurations
2. **NO manual configuration** - Use proper `mcpb.json` with all required fields
3. **NO custom build scripts** - Use standard MCPB tooling only
4. **NO hardcoded paths** - Use relative paths in configuration
5. **NO direct server execution** - Always use MCPB CLI tools

### ✅ ALWAYS DO

1. **Use `mcpb.json`** - Central configuration file for all MCPB settings
2. **Follow semantic versioning** - For both package and MCP versions
3. **Use stdio transport** - Required for reliable communication
4. **Specify exact versions** - For all dependencies
5. **Validate before building** - Always run `mcpb validate` first
6. **Verify after building** - Always run `mcpb verify` after packaging
7. **Sign production packages** - Use `mcpb sign` for production releases
8. **Use the build script** - For consistent builds across environments

## 🖥️ MCPB CLI COMMAND SYNTAX

### Core Commands

#### 1. Package Creation

```bash
# Basic package creation
mcpb pack . dist/

# Sign the package (required for production)
mcpb sign --key your-key.pem dist/package.mcpb

# Verify package integrity
mcpb verify --key your-key.pem dist/package.mcpb

# Publish to a MCPB registry (if configured)
mcpb publish --registry your-registry dist/package.mcpb
```

#### 2. MCPB Registries

MCPB registries are package repositories that store and distribute MCPB packages. Here's what you need to know:

##### Official Registries

- **Anthropic's Public Registry**: The primary public registry for production MCPB packages
  - URL: `https://registry.mcpb.anthropic.com` (requires authentication)
  - Managed by Anthropic
  - Requires review and approval for public packages

##### Self-hosted Registries

- **Enterprise/Private Registries**: Some organizations run private MCPB registries
  - Configure via environment variable: `MCPB_REGISTRY_URL`
  - Authentication typically required via API keys or tokens

##### Key Points

- **Authentication**: Always required for publishing

  ```bash
  export MCPB_API_TOKEN='your-token-here'
  ```

- **Scoped Packages**: Use `@scope/package-name` for organization-specific packages
- **Rate Limits**: Public registry has rate limits for downloads/uploads
- **Verification**: All packages are cryptographically signed

#### 3. Build Script (Recommended)

For consistent builds, use the provided PowerShell build script:

```powershell
# Show help and available options
.\scripts\build-mcp-package.ps1 -Help

# Build and sign the package (default behavior)
.\scripts\build-mcp-package.ps1

# Build without signing (for development/testing)
.\scripts\build-mcp-package.ps1 -NoSign

# Specify custom output directory
.\scripts\build-mcp-package.ps1 -OutputDir "C:\builds"
```

#### 3. Package Validation

```bash
# Validate manifest file
mcpb validate

# Validate built package
mcpb validate package.mcpb
```

#### 3. Package Signing

```bash
# Sign a package
mcpb sign package.mcpb

# Sign with specific key
mcpb sign --key my-key.pem package.mcpb
```

### Common Options

- `--verbose` or `-v`: Enable verbose output
- `--help` or `-h`: Show help message
- `--version` or `-V`: Show version information

### Environment Variables

- `MCPB_DEBUG=1`: Enable debug mode
- `MCPB_LOG_LEVEL=debug`: Set log level (debug, info, warn, error)

### Important Notes

1. Always run from the project root directory
2. The `mcpb init` command is deprecated - do not use it
3. For production builds, always validate before packaging
4. Sign packages for distribution when sharing with others

## 📋 MCPB.JSON VS MANIFEST.JSON

### Key Differences

| File | Purpose | When Used | Example Use Case |
|------|---------|-----------|------------------|
| `mcpb.json` | Development/build configuration | During development and build process | Configure build output directory, development server settings |
| `manifest.json` | Runtime configuration | When the extension is running | Define server entry points, capabilities, and extension metadata |

### mcpb.json (Build Configuration)

Used by the MCPB CLI tools during development and build. Defines how to build and package your extension.

### manifest.json (Runtime Configuration)

Packaged with your extension and used by the MCPB runtime. Defines how your extension should be loaded and executed.

## 📋 MCPB.JSON CONFIGURATION

### Required Fields

```json
{
  "name": "your-mcp-server",
  "version": "1.0.0",
  "description": "Brief description of your MCP server",
  "author": "Your Name",
  "license": "MIT",
  "outputDir": "dist",
  "mcp": {
    "version": "2.12.0",
    "server": {
      "command": "python",
      "args": ["-m", "your.package.module"],
      "transport": "stdio"
    },
    "capabilities": {
      "tools": true,
      "resources": true,
      "prompts": true
    }
  },
  "dependencies": {
    "python": ">=3.9.0"
  }
}
```

## 🛠️ BUILDING THE PACKAGE

### 1. Validate Configuration

```bash
mcpb validate
```

### 2. Build the Package

```bash
mcpb pack
```

This will create the package in the `dist` directory.

### 3. Package Signing (Not Currently Used)

```bash
mcpb sign package.mcpb
```

Package signing is used to verify the authenticity and integrity of MCPB packages. However, we currently do not use package signing in our workflow. If needed in the future, signing can be enabled by:

1. Generating a signing key pair
2. Configuring the build process to sign packages
3. Distributing the public key to all clients

For now, you can safely ignore any signing-related steps in the MCPB documentation.

## 📜 MANIFEST.JSON - CORE CONFIGURATION

### Purpose

`manifest.json` is the primary configuration file that defines your MCPB extension's behavior, dependencies, and capabilities. It's crucial for the MCPB runtime to understand how to load and execute your extension.

### Required Fields

```json
{
  "mcpb_version": "0.1",
  "name": "your-extension-name",
  "version": "1.0.0",
  "description": "Brief description of your extension",
  "author": "Your Name <email@example.com>",
  "license": "MIT",
  "server": {
    "type": "python",
    "entry_point": "src/your_package/server.py"
  },
  "capabilities": {
    "tools": true,
    "resources": true,
    "prompts": true
  }
}
```

### Key Sections Explained

1. **Server Configuration**
   - `type`: Must be "python" for Python-based extensions
   - `entry_point`: Path to your main server file

2. **Capabilities**
   - `tools`: Enable/disable tool support
   - `resources`: Enable/disable resource handling
   - `prompts`: Enable/disable prompt templates

### Best Practices

- Keep `manifest.json` in the root of your project
- Use semantic versioning for the `version` field
- Include all required fields
- Validate using `mcpb validate` before building

## 🏗️ PROJECT STRUCTURE

```text
your-mcp/
   ├── mcpb.json           # MCPB configuration
   ├── pyproject.toml     # Python project metadata
   ├── src/               # Source code
   │   └── your_package/  # Your Python package
   ├── tests/             # Test files
   └── dist/              # Output directory for packages
```

## ⚙️ SERVER CONFIGURATION

### FastMCP Server Best Practices

- Use FastMCP 2.12.0 or later
- Implement proper signal handling
- Use structured logging
- Handle all exceptions gracefully

### Dependency Management

- List all dependencies in `pyproject.toml`
- Pin exact versions for production
- Use virtual environments

## 📦 PACKAGE MANIFEST

### Manifest Fields

```json
{
  "mcpb_version": "0.1",
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
your-extension.mcpb/
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
your-extension.mcpb/
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

## 🚀 GITHUB RELEASES & CI/CD

### PyPI & TestPyPI Publishing

#### Prerequisites

1. **PyPI Account**
   - Create at [pypi.org/account/register/](https://pypi.org/account/register/)
   - Verify your email address

2. **API Tokens**
   - **PyPI Token**:
     1. Go to [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
     2. Create token with "Entire account" scope
     3. Add to GitHub secrets as `PYPI_API_TOKEN`
   - **TestPyPI Token** (optional):
     1. Create account at [test.pypi.org](https://test.pypi.org/)
     2. Create token at [test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)
     3. Add to GitHub secrets as `TEST_PYPI_API_TOKEN`

### Automated Release Process

1. **Version Tagging**
   - Update version in `pyproject.toml`
   - Create and push tag:

     ```bash
     # Update version in pyproject.toml first
     git add pyproject.toml
     git commit -m "bump version to 1.0.0"
     git tag -a v1.0.0 -m "Release v1.0.0"
     git push origin v1.0.0
     ```

2. **CI/CD Pipeline**
   - **On tag push**:
     1. Build Python package (wheel and source)
     2. Create MCPB package (`.mcpb` file)
     3. Publish to TestPyPI (for testing)
     4. Publish to PyPI (production)
     5. Create GitHub release with all artifacts
   - **On `main` branch push**:
     1. Build packages
     2. Publish to PyPI
   - **On `develop` branch push**:
     1. Build packages
     2. Publish to TestPyPI

3. **Verification**
   - Check PyPI: [pypi.org/project/database-operations-mcp/](https://pypi.org/project/database-operations-mcp/)
   - Check TestPyPI: [test.pypi.org/project/database-operations-mcp/](https://test.pypi.org/project/database-operations-mcp/)

### Release Artifacts

1. **GitHub Release**
   - Source distribution (`.tar.gz`)
   - Python wheel (`.whl`)
   - MCPB package (`.mcpb`)
   - Auto-generated release notes

2. **PyPI**
   - Source distribution
   - Python wheel
   - Package metadata and documentation

3. **TestPyPI** (for testing)
   - Same as PyPI, but in a testing environment

### Manual Release (if needed)

1. **Create Release on GitHub**

   ```bash
   # Build packages locally first
   python -m build
   mcpb pack . dist/package.mcpb
   
   # Create and push tag
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

2. **Manual PyPI Upload (if needed)**

   ```bash
   # Install twine
   pip install twine
   
   # Upload to TestPyPI
   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   
   # Upload to PyPI (after testing)
   twine upload dist/*
   ```

### CI/CD Pipeline Details

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    tags: ['v*']  # Trigger on version tags
  pull_request:
    branches: [main, develop]

jobs:
  # ... (test and lint jobs remain the same) ...
  
  build:
    name: Build and Publish
    needs: [test, lint]
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/'))
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build mcpb
    
    - name: Build Python package
      run: python -m build
    
    - name: Build MCPB package
      run: |
        mkdir -p dist
        mcpb pack . dist/package.mcpb
    
    - name: Publish to PyPI
      if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/')
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        user: __token__
        password: ${{ secrets.PYPI_API_TOKEN }}
    
    - name: Create GitHub Release
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/*.whl
          dist/*.tar.gz
          dist/*.mcpb
        generate_release_notes: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Required Secrets

1. `PYPI_API_TOKEN`: Token for PyPI uploads
   - Create at PyPI account settings → API tokens
   - Add to GitHub repository secrets

2. `GITHUB_TOKEN` (automatically provided by GitHub Actions)

## 🔧 FASTMCP VERSION REQUIREMENT

**CRITICAL**: Must use fastmcp>=2.12.0 for DXT compatibility.

**requirements.txt:**

```txt
# Core MCP dependencies - VERSION REQUIREMENT
fastmcp>=2.12.0,<3.0.0
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

**Why fastmcp 2.12.0?**

- Includes all critical MCPB runtime compatibility fixes
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
  "mcpb_version": "0.1",
  "name": "example-mcp",
  "version": "1.0.0",
  "description": "Example MCP server with external tool integration",
  "long_description": "Comprehensive MCP server that demonstrates proper external dependency handling, user configuration, and professional tool integration patterns using FastMCP 2.12.0+.",
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
    "fastmcp>=2.12.0,<3.0.0",
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
    "loguru>=0.7.0"
  ]
}
```

## 🚀 BUILD PROCESS

### Prerequisites

```bash
# Install MCPB CLI (official toolchain)
npm install -g @anthropic-ai/mcpb

# Install Python dependencies (EXACT VERSIONS)
pip install "fastmcp>=2.12.0,<3.0.0"
pip install -r requirements.txt
```

### Repository Structure (Updated)

```
your-mcp-server/
├── .github/
│   └── workflows/
│       └── build-dxt.yml          # GitHub Actions
├── mcpb/
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
# 1. AI-generate manifest.json (place in mcpb/manifest.json)
# ENSURE: fastmcp>=2.10.1 in requirements.txt
# ENSURE: cwd: "src" and PYTHONPATH: "src" in mcp_config

# 2. Validate manifest
cd mcpb
mcpb validate

# 3. Build DXT package
mcpb pack . ../dist/package.mcpb

# 4. Test installation
# Drag dist/*.mcpb to Claude Desktop
```

## 🚨 CLAUDE DESKTOP MCPB EXTENSION PATH BUGS

### Critical Bug: Incorrect Extension Path Resolution

**Symptoms:**

```
python.exe: can't open file 'C:\\Users\\user\\AppData\\Local\\AnthropicClaude\\app-{version}\\server\\main.py': [Errno 2] No such file or directory
[Extension Name] [error] Server disconnected
```

**Root Cause:**
Claude Desktop has a path resolution bug where it tries to execute extensions from the wrong directory:

- **Incorrect (what Claude Desktop tries):** `C:\Users\{user}\AppData\Local\AnthropicClaude\app-{version}\server\main.py`
- **Correct (actual location):** `C:\Users\{user}\AppData\Roaming\Claude\Claude Extensions\local.mcpb.{publisher}.{name}\server\main.py`

### 🔧 WORKAROUND STRATEGIES

#### Strategy 1: Manual Configuration Entry (Immediate Fix)

When an extension fails with path errors, add a manual entry to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "your-extension-manual": {
      "command": "python",
      "args": ["C:/Users/{username}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.{publisher}.{extension-name}/server/main.py"],
      "cwd": "C:/Users/{username}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.{publisher}.{extension-name}",
      "env": {
        "PYTHONPATH": "C:/Users/{username}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.{publisher}.{extension-name}/server;C:/Users/{username}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.{publisher}.{extension-name}/server/lib",
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
         "args": ["C:/Users/{YOUR_USERNAME}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.{publisher}.{extension-name}/server/main.py"],
         "cwd": "C:/Users/{YOUR_USERNAME}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.{publisher}.{extension-name}",
         "env": {
           "PYTHONPATH": "C:/Users/{YOUR_USERNAME}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.{publisher}.{extension-name}/server",
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

## 🚧 TROUBLESHOOTING MCPB EXTENSIONS

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
      "cwd": "C:/Users/{user}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.{publisher}.{name}/src",
      "env": {
        "PYTHONPATH": "C:/Users/{user}/AppData/Roaming/Claude/Claude Extensions/local.mcpb.{publisher}.{name}/src",
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

#### Solution: Update to FastMCP 2.12.0+

```bash
# Uninstall old version
pip uninstall fastmcp

# Install exact version
pip install "fastmcp>=2.12.0,<3.0.0"

# Verify installation
python -c "import fastmcp; print(fastmcp.__version__)"
```

#### Update requirements.txt

```txt
# CRITICAL: Use exact version constraints
fastmcp>=2.12.0,<3.0.0
fastapi>=0.95.0
uvicorn[standard]>=0.22.0
pydantic>=2.0.0,<3.0.0
```

## 🚀 GITHUB CI/CD AUTOMATION

### Complete GitHub Actions Workflow

Create `.github/workflows/build-mcpb.yml`:

```yaml
name: Build and Release MCPB Extension

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
  build-mcpb:
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
        
    - name: Install MCPB CLI
      run: npm install -g @anthropic-ai/mcpb
      
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install "fastmcp>=2.12.0,<3.0.0"
        pip install -r requirements.txt
        
    - name: Create dist directory
      run: mkdir -p dist
        
    - name: Validate manifest.json
      run: mcpb validate mcpb/manifest.json
      
    - name: Build MCPB extension
      run: |
        cd mcpb
        mcpb pack . ../dist/package.mcpb
        
    - name: Sign MCPB extension (optional)
      if: ${{ secrets.MCPB_SIGNING_KEY }}
      run: |
        echo "${{ secrets.MCPB_SIGNING_KEY }}" > signing.key
        mcpb sign --key signing.key dist/*.mcpb
        rm signing.key
        
    - name: Upload MCPB artifact
      uses: actions/upload-artifact@v3
      with:
        name: mcpb-extension
        path: dist/*.mcpb
        retention-days: 30
        
    - name: Create GitHub Release
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: dist/*.mcpb
        generate_release_notes: true
        draft: false
        prerelease: false
        body: |
          ## MCPB Extension Release
          
          Download the `.mcpb` file below and drag it to Claude Desktop for one-click installation.
          
          ### Installation
          1. Download the `.mcpb` file from the assets below
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
mcpb validate mcpb/manifest.json

# Common issues:
# - Missing cwd and PYTHONPATH for Python servers
# - fastmcp version < 2.12.0 in dependencies
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

# Verify >= 2.12.0
python -c "import fastmcp; assert fastmcp.__version__ >= '2.12.0', 'Update FastMCP!'"
```

### MCPB Package Testing

```bash
# Build test package
cd mcpb
mcpb pack . ../package.mcpb

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

- [ ] Use fastmcp>=2.12.0,<3.0.0 in requirements.txt
- [ ] Structure Python modules in `src/your_mcp/` directory
- [ ] Create comprehensive manifest.json with AI
- [ ] Include `cwd: "src"` and `PYTHONPATH: "src"` in mcp_config
- [ ] Implement runtime detection fallbacks in Python
- [ ] Add proper error handling for missing dependencies

### Building

- [ ] Validate Python import: `cd src && python -c "import your_mcp.server"`
- [ ] Validate FastMCP version: `python -c "import fastmcp; print(fastmcp.__version__)"`
- [ ] Validate manifest: `mcpb validate mcpb/manifest.json`
- [ ] Build package: `mcpb pack . dist/`
- [ ] Test installation on clean Claude Desktop
- [ ] Verify user configuration prompts work correctly

### Release

- [ ] Setup GitHub Actions workflow with Python 3.11
- [ ] Include fastmcp>=2.12.0 installation step in CI
- [ ] Create release tag: `git tag v1.0.0`
- [ ] Verify automatic build and release
- [ ] Test downloaded .mcpb package installation
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
  "dependencies": ["fastmcp>=2.12.0,<3.0.0"],
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
  "dependencies": ["fastmcp>=2.12.0,<3.0.0"],
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
  "dependencies": ["fastmcp>=2.12.0,<3.0.0"],
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

## 🆕 WHAT'S NEW IN VERSION 3.1

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

## 🆕 WHAT'S NEW IN VERSION 3.0

### Critical Updates

1. **FastMCP 2.12.0 Requirement**: Mandatory for MCPB compatibility
2. **Python Path Fix**: Explicit `cwd` and `PYTHONPATH` configuration
3. **Updated Examples**: All examples include new requirements
4. **Enhanced Troubleshooting**: Manual MCP fallback procedures
5. **CI/CD Updates**: GitHub Actions with correct dependency installation

### Breaking Changes

- **FastMCP < 2.12.0 no longer supported** in MCPB extensions
- **Python servers require explicit path configuration** in manifest
- **All existing MCPB packages need rebuilding** with new requirements

### Migration Guide

1. Update `requirements.txt`: `fastmcp>=2.12.0,<3.0.0`
2. Add to manifest `mcp_config`: `"cwd": "src"` and `"PYTHONPATH": "src"`
3. Rebuild MCPB package: `mcpb pack . ../dist/updated-package.mcpb`
4. Test installation and fallback to manual MCP if needed

This guide provides everything needed to build professional MCPB extensions that work reliably across all platforms and installations with the latest FastMCP improvements and Python path fixes. Follow these patterns for consistent, high-quality MCP server packaging that actually works in production.

## 🔄 MIGRATION FROM DXT TO MCPB

### Overview

As of January 2025, DXT (Deployment eXtension Toolkit) has been renamed to MCPB (MCP Bundle). This is a comprehensive migration that affects all aspects of the toolkit.

### What Changed

1. **Tool Name**: `dxt` → `mcpb`
2. **Configuration Files**: `dxt.json` → `mcpb.json`
3. **Manifest Files**: `dxt_manifest.json` → `mcpb_manifest.json`
4. **Package Extensions**: `.dxt` → `.mcpb`
5. **NPM Package**: `@anthropic-ai/dxt` → `@anthropic-ai/mcpb`
6. **Registry URLs**: `registry.dxt.anthropic.com` → `registry.mcpb.anthropic.com`

### Migration Checklist

#### 1. Update Development Environment

```bash
# Uninstall old DXT CLI
npm uninstall -g @anthropic-ai/dxt

# Install new MCPB CLI
npm install -g @anthropic-ai/mcpb
```

#### 2. Update Project Files

```bash
# Rename configuration files
mv dxt.json mcpb.json
mv dxt_manifest.json mcpb_manifest.json

# Update any scripts or CI/CD configurations
# Replace all references to 'dxt' with 'mcpb'
```

#### 3. Update Commands

```bash
# Old DXT commands → New MCPB commands
dxt validate     → mcpb validate
dxt pack        → mcpb pack
dxt sign        → mcpb sign
dxt verify      → mcpb verify
mcpb publish     → mcpb publish
```

#### 4. Update Environment Variables

```bash
# Old environment variables → New environment variables
DXT_REGISTRY_URL → MCPB_REGISTRY_URL
DXT_API_TOKEN   → MCPB_API_TOKEN
DXT_DEBUG       → MCPB_DEBUG
```

#### 5. Update CI/CD Pipelines

- Change workflow file names from `build-dxt.yml` to `build-mcpb.yml`
- Update all `dxt` commands to `mcpb`
- Update package extensions from `.dxt` to `.mcpb`
- Update artifact names and paths

#### 6. Update Documentation

- Update all references from DXT to MCPB
- Update file extensions in examples
- Update command examples
- Update URLs and registry references

### Backward Compatibility

**Important**: MCPB is **not** backward compatible with DXT packages. All existing DXT packages must be rebuilt using the new MCPB toolchain.

### Migration Timeline

- **January 2025**: MCPB officially released
- **February 2025**: DXT CLI deprecated (still functional)
- **March 2025**: DXT CLI removed from NPM
- **April 2025**: DXT registry sunset

### Getting Help

If you encounter issues during migration:

1. Check the official MCPB documentation
2. Review this updated guide
3. Search for migration-related issues in the Anthropic community forums
4. Contact Anthropic support for enterprise migration assistance

### Common Migration Issues

1. **Command Not Found**: Ensure MCPB CLI is properly installed
2. **Package Import Errors**: Rebuild packages with new MCPB toolchain
3. **Registry Access**: Update to new MCPB registry URLs
4. **CI/CD Failures**: Update all pipeline configurations

Remember: This migration improves the toolkit's functionality and provides better integration with the broader MCP ecosystem.
