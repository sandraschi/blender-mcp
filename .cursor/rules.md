# 🚀 Blender MCP Development Rules & Standards

## 📋 **Complete Rule Set - October 2025**

This document establishes the complete set of rules, standards, and best practices for Blender MCP development.

---

## 🎯 **Core Architecture Rules**

### **FastMCP 2.12 Compliance (MANDATORY)**

#### **✅ Tool Registration Standard**
```python
def get_app():
    from blender_mcp.app import app
    return app

def _register_tools():
    app = get_app()

    @app.tool  # ← FastMCP 2.12 standard decorator
    async def tool_name(params) -> str:
        """
        Comprehensive description.

        Args:
            param: Description

        Returns:
            Description of return value
        """
        return await handler.function(params)

_register_tools()
```

#### **✅ Parameter Validation (Pydantic)**
```python
class ToolParams(BaseModel):
    param: str = Field(..., description="Description")
    optional: int = Field(5, ge=1, le=10, description="Optional param")
```

#### **✅ Async/Await Pattern**
- All tool functions must be `async`
- All handler calls must use `await`
- No blocking operations in tool functions

#### **✅ Error Handling Standard**
```python
try:
    result = await handler.function(params)
    return result
except Exception as e:
    raise MCPError(f"Tool failed: {str(e)}")
```

### **MCPB Packaging Rules (MANDATORY)**

#### **✅ Package Structure**
```
src/blender_mcp/
├── handlers/           # Business logic
├── tools/              # MCP interface (organized by category)
├── utils/              # Utilities
└── *.py               # Main package files
```

#### **✅ Tool Organization**
- **Category-based subdirectories** in `tools/`
- **Each category** has `__init__.py` importing from tools file
- **Portmanteau tools** instead of 150+ separate tools
- **Operation parameter** for sub-operations

#### **✅ Import Standards**
- **Lazy app loading** to prevent circular imports
- **No circular dependencies**
- **Clean module structure**

---

## 💻 **PowerShell-Only Development (STRICTLY ENFORCED)**

### **🚫 PROHIBITED Linux Tools**
- ~~`ls`~~ → Use `Get-ChildItem`
- ~~`mkdir`~~ → Use `New-Item -ItemType Directory`
- ~~`rm`~~ → Use `Remove-Item`
- ~~`cp`~~ → Use `Copy-Item`
- ~~`mv`~~ → Use `Move-Item`
- ~~`cat`~~ → Use `Get-Content`
- ~~`head`~~ → Use `Get-Content -Head`
- ~~`tail`~~ → Use `Get-Content -Tail`
- ~~`grep`~~ → Use `Select-String`
- ~~`find`~~ → Use `Get-ChildItem -Recurse`
- ~~`chmod`~~ → Use file system ACLs
- ~~`&&`~~ → **NO CHAINING** - use separate commands
- ~~`|`~~ → **NO PIPES** - use intermediate variables

### **✅ REQUIRED PowerShell Commands**
```powershell
# Directory operations
New-Item -ItemType Directory -Path "path" -Force
Remove-Item "path" -Recurse -Force
Get-ChildItem -Path "path" -Recurse

# File operations
Set-Content -Path "file" -Value "content"
Get-Content -Path "file"
Copy-Item "source" "dest"
Move-Item "source" "dest"

# Text processing
Get-Content "file" | Where-Object { $_ -match "pattern" }
Select-String -Path "file" -Pattern "regex"
```

### **🚫 NEVER Use These Patterns**
- ❌ `ls -la && mkdir test`
- ❌ `cat file | grep pattern`
- ❌ `find . -name "*.py" | head -10`
- ❌ `cp file1 file2 && mv file3 file4`

### **✅ CORRECT PowerShell Patterns**
```powershell
# Correct approach
Get-ChildItem -Recurse -Name "*.py"
New-Item -ItemType Directory -Path "test" -Force
Get-Content "file.txt" | Select-String "pattern"
```

---

## 🏗️ **Portmanteau Tool Architecture (MANDATORY)**

### **✅ Tool Design Pattern**
```python
@app.tool
async def blender_category(
    operation: str = "default_operation",
    # ... operation-specific parameters
) -> str:
    """
    Comprehensive category management tool.

    Supports multiple operations through the operation parameter.

    Args:
        operation: Operation type ("create", "list", "modify", etc.)
        # ... operation-specific parameters

    Returns:
        Operation result
    """
    if operation == "create":
        return await handler_create_function(params)
    elif operation == "list":
        return await handler_list_function()
    # ... etc
```

### **✅ Tool Categories (19 total + 2 utility)**
1. **`blender_scene`** - Scene management (12 operations)
2. **`blender_materials`** - Material creation (7 operations)
3. **`blender_mesh`** - Geometry creation (1 operation)
4. **`blender_furniture`** - Furniture creation (1 operation)
5. **`blender_lighting`** - Lighting systems (1 operation)
6. **`blender_camera`** - Camera controls (1 operation)
7. **`blender_animation`** - Animation & rigging (1 operation)
8. **`blender_render`** - Rendering & output (1 operation)
9. **`blender_export`** - Export operations (1 operation)
10. **`blender_import`** - Import operations (1 operation)
11. **`blender_physics`** - Physics simulation (1 operation)
12. **`blender_modifiers`** - Modifiers & effects (1 operation)
13. **`blender_textures`** - Textures & UVs (1 operation)
14. **`blender_particles`** - Particles & effects (1 operation)
15. **`blender_rigging`** - Rigging operations (1 operation)
16. **`blender_selection`** - Object selection (1 operation)
17. **`blender_transform`** - Object transformation (1 operation)
18. **`blender_addons`** - Add-on management (1 operation)
19. **`blender_uv`** - UV mapping operations (1 operation)

**Utility Tools (13 total):**
- **`blender_help`** - Help system (5 operations)
- **`blender_status`** - System status (4 operations)
- **`blender_view_logs`** - Log viewing (1 operation)
- **`blender_log_stats`** - Log statistics (1 operation)
- **`blender_download`** - File download & import (1 operation)
- **`blender_download_info`** - Download format info (1 operation)

### **✅ Operation Parameter Standard**
- **Required `operation` parameter** for all portmanteau tools
- **Operation-specific parameters** that vary by operation type
- **Clear operation descriptions** in docstrings

---

## 📚 **Documentation Standards (MANDATORY)**

### **✅ Multiline Docstrings (NO """ inside)**
```python
@app.tool
async def tool_name(params) -> str:
    """
    Brief description of what the tool does.

    More detailed explanation of functionality,
    use cases, and behavior.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value
    """
```

### **✅ Self-Documenting Tools**
- **Comprehensive parameter descriptions**
- **Usage examples** in docstrings
- **Return value explanations**
- **Error condition documentation**

### **✅ Module Documentation**
- **Module-level docstrings** explaining purpose
- **Import statements** properly documented
- **Class and function documentation**

---

## 🧪 **Testing Standards (MANDATORY)**

### **✅ Test Categories**
1. **Unit Tests** - Pydantic validation (no Blender required)
2. **Integration Tests** - Real Blender execution
3. **End-to-End Tests** - Complete workflows
4. **Performance Tests** - Large scene handling

### **✅ Test Organization**
```
tests/
├── test_unit_utils.py      # Unit tests (no Blender)
├── test_integration_*.py   # Integration tests (real Blender)
├── test_e2e_*.py          # End-to-end workflows
├── test_performance.py     # Performance tests
└── conftest.py            # Pytest fixtures
```

### **✅ Test Execution**
```bash
# Unit tests only (CI/CD safe)
python tests/run_tests.py --no-blender

# Integration tests (requires Blender)
python tests/run_tests.py --integration

# All tests
python tests/run_tests.py --all
```

---

## 🚨 **Error Handling & Logging (MANDATORY)**

### **✅ Exception Hierarchy**
```python
class BlenderMCPError(Exception):
    """Base exception for Blender MCP operations."""
    pass

class BlenderNotFoundError(BlenderMCPError):
    """Blender executable not found."""
    pass

class BlenderScriptError(BlenderMCPError):
    """Error in Blender script execution."""
    pass
```

### **✅ Logging Standards (MANDATORY)**
```python
from loguru import logger

# Operation logging with emoji prefixes
logger.info(f"🎨 Starting Blender operation: {operation_name}")
logger.error(f"❌ Blender operation failed: {operation_name}")
logger.debug(f"📥 Operation parameters: {params}")
```

#### **🚫 STRICTLY PROHIBITED: Print & Console Statements**
- **❌ NO `print()` statements** in application code
- **❌ NO `console.log()` statements** (JavaScript style)
- **✅ ONLY structured logging** with loguru
- **✅ Appropriate `print()` only** in:
  - Blender script execution strings (remote output)
  - CLI interface display
  - Initialization warnings to stderr

#### **🛡️ Server Stability (CRITICAL)**
- **Errors must NEVER crash the server** under any circumstance
- **All exceptions must be caught** and handled gracefully
- **Comprehensive error handling** in all async operations
- **Proper exception chaining** with meaningful context
- **Graceful degradation** for missing optional features

### **✅ Error Recovery**
- **Informative error messages** for users with actionable guidance
- **Proper exception chaining** maintaining original error context
- **Resource cleanup** in error paths
- **Timeout handling** for long-running operations

---

## 🔧 **Development Workflow (MANDATORY)**

### **✅ Code Organization**
- **Handler Layer** (`handlers/`) - Business logic
- **Tool Layer** (`tools/`) - MCP interface
- **Utility Layer** (`utils/`) - Shared utilities

### **✅ Import Standards**
- **Lazy loading** for app and heavy dependencies
- **No circular imports**
- **Clean separation** of concerns

### **✅ File Naming**
- **snake_case** for functions and variables
- **PascalCase** for classes
- **descriptive names** that explain purpose

---

## 📦 **Distribution & Packaging (MANDATORY)**

### **✅ MCPB Package Requirements**
- **Single executable** with all dependencies
- **No external dependencies** for end users
- **Proper version management**
- **Installation automation**

### **✅ Package Metadata**
```toml
[project]
name = "blender-mcp"
version = "1.0.0"
description = "FastMCP 2.12 Blender automation server"
```

### **✅ Installation Methods**
- **DXT packaging** for one-click installation
- **PyPI distribution** for pip install
- **GitHub releases** for manual installation

---

## 🏆 **Quality Standards (MANDATORY)**

### **✅ Code Quality**
- **Type annotations** on all functions
- **Comprehensive error handling**
- **Performance optimization**
- **Memory leak prevention**

### **✅ Documentation Quality**
- **Complete README** with examples
- **API documentation** for all tools
- **Troubleshooting guides**
- **Contributing guidelines**

### **✅ Testing Quality**
- **100% test coverage** for critical paths
- **Real Blender integration** (no mocks)
- **Performance benchmarks**
- **Error scenario testing**

---

## 🚫 **PROHIBITED Practices (STRICTLY ENFORCED)**

### **❌ NEVER Use Linux Syntax**
- ~~`ls -la`~~ ❌
- ~~`mkdir test && cd test`~~ ❌
- ~~`cat file | grep pattern`~~ ❌
- ~~`find . -name "*.py"`~~ ❌

### **❌ NEVER Create Tool Explosions**
- ~~150+ separate tools~~ ❌
- ~~Single-purpose tools~~ ❌
- ~~Unmanageable tool counts~~ ❌

### **❌ NEVER Use Inadequate Documentation**
- ~~Single-line docstrings~~ ❌
- ~~Missing parameter descriptions~~ ❌
- ~~No usage examples~~ ❌

### **❌ NEVER Skip Error Handling**
- ~~Bare except clauses~~ ❌
- ~~Silent failures~~ ❌
- ~~No error logging~~ ❌

---

## ✅ **Development Commandments**

### **1. 🎯 FastMCP 2.12 First**
- Always use `@app.tool` decorators
- Follow async/await patterns
- Implement proper parameter validation

### **2. 💻 PowerShell Only**
- No Linux tools or syntax
- Proper PowerShell commands only
- No command chaining or pipes

### **3. 🏗️ Portmanteau Architecture**
- 15 manageable tools instead of 150+
- Each tool is a "tool suite"
- Operation parameter for sub-operations

### **4. 📚 Self-Documenting Code**
- Comprehensive docstrings
- Clear parameter descriptions
- Usage examples in documentation

### **5. 🧪 Real Blender Testing**
- No mocks for Blender operations
- Real Blender execution in tests
- Proper error scenario testing

### **6. 🚨 Proper Error Handling**
- Informative error messages
- Graceful degradation
- Comprehensive logging

### **7. 📦 Production Ready**
- No development artifacts in production
- Proper packaging and distribution
- Installation automation

---

## 🏆 **Enforcement & Compliance**

### **✅ Code Review Requirements**
- **All rules** must be followed in PRs
- **No exceptions** for "quick fixes"
- **Automated linting** for style consistency

### **✅ CI/CD Integration**
- **PowerShell-only** build scripts
- **Automated testing** with real Blender
- **Package validation** before release

### **✅ Quality Gates**
- **All tests pass** before merge
- **No Pydantic warnings** in production
- **Proper error handling** verified

---

## 📊 **Current Implementation Status**

### **✅ Completed**
- **FastMCP 2.12 compliance** ✅
- **Portmanteau tool architecture** ✅
- **PowerShell-only development** ✅
- **Comprehensive error handling** ✅
- **Real Blender integration** ✅

### **✅ Verified Working**
- **48 tools** across 19 categories ✅
- **Scene management** (12 tools) ✅
- **Materials & shaders** (7 tools) ✅
- **Geometry creation** (1 tool) ✅
- **Lighting systems** (1 tool) ✅
- **Camera controls** (1 tool) ✅
- **Animation & rigging** (1 tool) ✅
- **Rendering & output** (1 tool) ✅
- **Import/Export operations** (2 tools) ✅
- **Physics simulation** (1 tool) ✅
- **Modifiers & effects** (1 tool) ✅
- **Textures & UVs** (2 tools) ✅
- **Particles & effects** (1 tool) ✅
- **Rigging operations** (1 tool) ✅
- **Object selection** (1 tool) ✅
- **Transform operations** (1 tool) ✅
- **Add-on management** (1 tool) ✅
- **Furniture creation** (1 tool) ✅
- **Help & status utilities** (9 tools) ✅
- **Live Blender execution** ✅

### **✅ Complete Implementation**
- **All major Blender workflows** supported
- **Professional 3D automation** ready for production
- **MCPB packaging** and distribution
- **Advanced features**

---

## 🎯 **Success Metrics**

### **✅ Technical Success**
- **FastMCP 2.12 compliant** ✅
- **No Linux dependencies** ✅
- **Real Blender integration** ✅
- **Comprehensive testing** ✅

### **✅ User Experience**
- **Manageable tool count** (15 vs 150+) ✅
- **Self-documenting tools** ✅
- **Clear error messages** ✅
- **Easy installation** ✅

### **✅ Developer Experience**
- **Clear architecture** ✅
- **Consistent patterns** ✅
- **Comprehensive documentation** ✅
- **Automated workflows** ✅

---

## 📞 **Quick Reference**

### **I Need To...**
- **Create a tool** → Use `@app.tool` decorator + proper docstring
- **Add parameters** → Use Pydantic BaseModel with Field() constraints
- **Handle errors** → Use try/catch with informative messages
- **Test tools** → Use real Blender execution (no mocks)
- **Use PowerShell** → Only PowerShell commands, no Linux tools
- **Document tools** → Multiline docstrings with Args/Returns

### **I Must NOT...**
- **Use Linux syntax** → `ls`, `mkdir`, `&&`, `|` ❌
- **Create tool explosions** → 150+ separate tools ❌
- **Skip error handling** → Bare except clauses ❌
- **Use inadequate docs** → Single-line docstrings ❌

---

## 🏆 **Final Authority**

This document is the **single source of truth** for Blender MCP development. All code must comply with these rules. No exceptions.

**Last Updated**: October 2025
**Status**: ✅ Active and Enforced
**Compliance**: Mandatory for all development

---

*These rules ensure the Blender MCP Server is a professional, maintainable, and reliable FastMCP 2.12 implementation with proper PowerShell-only development practices.*
