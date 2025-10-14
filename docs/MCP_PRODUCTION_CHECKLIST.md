# MCP Server Production Audit Checklist

Use this checklist to audit any MCP server repo before marking it production-ready.

## 🏗️ CORE MCP ARCHITECTURE

- [ ] **🔥 DUAL INTERFACE MANDATORY** - Both MCP and FastAPI interfaces implemented
- [ ] **FastMCP 2.12+ framework** implemented with:
  - [ ] `from fastmcp import FastMCP` import
  - [ ] Proper MCP and FastAPI app initialization
  - [ ] Unified tool registration system
- [ ] **FastMCP 2.12 Repository Structure:**
  - [ ] `src/mcp/` directory containing main MCP server code
  - [ ] `tools/` directory with organized tool modules (**CRITICAL: NO monster `server.py`**)
  - [ ] **Tool organization:** Each category in separate subdirectory (e.g., `tools/containers/`, `tools/images/`)
  - [ ] **Tool imports:** Main server imports from `tools/` directory, not inline implementations
  - [ ] **Separation of concerns:** Tools, utilities, config, models all separate
  - [ ] **Anti-pattern avoided:** Single massive file with all tool implementations
- [ ] stdio protocol for Claude Desktop connection
- [ ] **⚡ FastAPI Standard Conformance REQUIRED:**
  - [ ] `/api/docs` endpoint with OpenAPI documentation accessible
  - [ ] `/health` endpoint returning JSON status (200 OK)
  - [ ] `/api/v1/` versioned API endpoints structure
  - [ ] Proper HTTP status codes (200, 400, 404, 500)
  - [ ] JSON request/response format throughout
  - [ ] CORS properly configured for web access
- [ ] Proper tool registration with `@mcp.tool()` multiline decorators
- [ ] No `"""` inside `"""` delimited decorators
- [ ] Self-documenting tool descriptions present
- [ ] **Multilevel help tool** implemented
- [ ] **Status tool** implemented
- [ ] **Health check tool** implemented
- [ ] `prompts/` folder with example prompt templates

## ✨ CODE QUALITY

- [ ] **FastMCP 2.12+ Modular Architecture (ANTI-MONSTER SERVER.PY):**
  - [ ] **Thin server.py** < 150 lines (only FastMCP init + tool imports)
  - [ ] **NO monster server.py** with hundreds of tool implementations
  - [ ] **Proper tools/ directory structure:**
    ```
    src/mcp/
    ├── server.py          # THIN - only imports & registration
    └── tools/             # ALL LOGIC GOES HERE
        ├── __init__.py
        ├── category1/     # Tool categories (containers, images, etc.)
        │   ├── __init__.py
        │   ├── models.py  # Pydantic models
        │   └── tools.py   # Tool implementations
        ├── category2/
        └── shared/        # Common utilities
            ├── __init__.py
            ├── exceptions.py
            └── utils.py
    ```
  - [ ] **Category-based tool organization** (not all tools in one file)
  - [ ] **Clean tool registration pattern:** `mcp.add_tools(category_tools)`
  - [ ] **Model separation:** Pydantic models in separate `models.py` files
  - [ ] **Shared utilities** in `shared/` directory
  - [ ] Clear module boundaries and responsibilities
- [ ] ALL `print()` / `console.log()` replaced with structured logging
- [ ] Comprehensive error handling (try/catch everywhere)
- [ ] Graceful degradation on failures
- [ ] Type hints (Python) / TypeScript types throughout
- [ ] Input validation on ALL tool parameters
- [ ] Proper resource cleanup (connections, files, processes)
- [ ] No memory leaks (verified)

## 📦 PACKAGING & DISTRIBUTION

- [ ] **DXT/MCPB Workflow:**
  - [ ] Anthropic `mcpb validate` passes successfully (DO NOT use `mcpb init` or `mcpb publish`)
  - [ ] Anthropic `mcpb pack` creates valid package
  - [ ] Package validates in Claude Desktop Extensions directory
- [ ] **Dependencies properly declared** (Claude Desktop installs them automatically)
- [ ] `requirements.txt` / `package.json` with correct versions
- [ ] Claude Desktop config example in README
- [ ] Virtual environment setup script (`venv` for Python)
- [ ] Installation instructions tested and working

## 🧪 TESTING

- [ ] **🎯 DUAL INTERFACE TESTING MANDATORY:**
  - [ ] **Local test scripts in `tests/local/`** for both MCP and FastAPI
  - [ ] **Postman collection** with all API endpoints tested
  - [ ] **PowerShell test runner** for MCP stdio interface
  - [ ] **FastAPI test client** for HTTP endpoints  
- [ ] Unit tests in `tests/unit/` covering all tools
- [ ] Integration tests in `tests/integration/`
- [ ] **API endpoint testing:**
  - [ ] `/health` endpoint returns 200 OK with valid JSON
  - [ ] `/api/docs` endpoint accessible and shows OpenAPI schema
  - [ ] All `/api/v1/` endpoints return proper HTTP status codes
  - [ ] Error handling tested (400, 404, 500 responses)
- [ ] Test fixtures and mocks created
- [ ] Coverage reporting configured (target: >80%)
- [ ] **Postman environment setup** with base URLs and auth
- [ ] All tests passing locally before commit

## 📚 DOCUMENTATION

- [ ] README.md updated: features, installation, usage, troubleshooting
- [ ] PRD updated with current capabilities
- [ ] API documentation for all tools
- [ ] `CHANGELOG.md` following Keep a Changelog format
- [ ] Wiki pages: architecture, development guide, FAQ
- [ ] `CONTRIBUTING.md` with contribution guidelines
- [ ] `SECURITY.md` with security policy
- [ ] **Development Notes:**
  - [ ] Basic memory notes timestamped with format: "YYYY-MM-DD HH:MM CET"
  - [ ] Proper tagging: `["project-name", "technology", "status", "priority"]`
  - [ ] Mark outdated notes as "OBSOLETE"

## 🔧 GITHUB INFRASTRUCTURE

- [ ] **Repository Standards:**
  - [ ] Repository under `sandraschi` GitHub user
  - [ ] Repository name follows `project-name-mcp` convention
  - [ ] Repository description includes "MCP server for [functionality]"
  - [ ] Topics/tags include: `mcp-server`, `fastmcp`, `claude-desktop`
- [ ] CI/CD workflows in `.github/workflows/`: test, lint, build, release
- [ ] Dependabot configured for dependency updates
- [ ] Issue templates created
- [ ] PR templates created
- [ ] Release automation with semantic versioning
- [ ] Branch protection rules documented
- [ ] GitHub Actions all passing

## 💻 PLATFORM REQUIREMENTS (Windows/PowerShell)

- [ ] **PowerShell Reliability Rules:**
  - [ ] No Linux syntax (`&&`, `||`, etc.) - Use PowerShell operators
  - [ ] PowerShell cmdlets used (`New-Item` not `mkdir`, `Copy-Item` not `cp`)
  - [ ] File redirect + read back pattern: `Command > temp.txt; Get-Content temp.txt`
  - [ ] Always quote paths with spaces: `"C:\Program Files\"`
  - [ ] Use backslashes for Windows paths consistently
  - [ ] Include error handling: `-ErrorAction SilentlyContinue`
- [ ] Cross-platform path handling (`path.join` where needed)
- [ ] All PowerShell scripts tested on Windows
- [ ] **Temp file management:**
  - [ ] Use `d:\dev\repos\temp\` for redirected outputs
  - [ ] Unique temp filenames with timestamps
  - [ ] Cleanup temp files after use

## 🎁 EXTRAS

- [ ] Example configurations for common use cases
- [ ] Performance benchmarks (if applicable)
- [ ] Rate limiting/quota handling (where relevant)
- [ ] Secrets management documentation (env vars, config)
- [ ] Error messages are user-friendly
- [ ] Logging levels properly configured

## 🌐 API & INTERFACE VALIDATION

- [ ] **FastAPI Interface Validation:**
  - [ ] OpenAPI schema generated and accessible at `/api/docs`
  - [ ] All endpoints documented with proper descriptions
  - [ ] Request/response models defined with Pydantic
  - [ ] API versioning implemented (v1, v2, etc.)
  - [ ] Rate limiting configured where appropriate
- [ ] **MCP Interface Validation:**
  - [ ] All tools registered with proper metadata
  - [ ] Tool descriptions follow MCP specification
  - [ ] Error handling returns proper MCP error format
  - [ ] Resource cleanup on client disconnect
- [ ] **Cross-Interface Consistency:**
  - [ ] Same functionality available through both interfaces
  - [ ] Consistent error messages and codes
  - [ ] Matching parameter validation rules
  - [ ] Unified logging and monitoring

## 📋 FINAL REVIEW

- [ ] All dependencies up to date
- [ ] No security vulnerabilities (npm audit / pip-audit)
- [ ] License file present and correct
- [ ] Version number follows semantic versioning
- [ ] Git tags match releases
- [ ] Repository description and topics set on GitHub

---

**Total Items:** 95  
**Completed:** _____ / 95  
**Coverage:** _____%

**🔥 CRITICAL:** Dual interface (MCP + FastAPI) with `/api/docs` and `/health` endpoints is MANDATORY  
**🎯 TESTING:** Local test scripts + Postman collection required for production readiness  
**⚡ DXT:** Use only `mcpb validate` and `mcpb pack` - NO `mcpb init` or `mcpb publish`

**Auditor:** _____________  
**Date:** _____________  
**Repo:** _____________  
**Status:** ⬜ In Progress | ⬜ Ready for Review | ⬜ Production Ready
