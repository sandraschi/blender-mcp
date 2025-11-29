# MCP Server Production Audit Checklist

Use this checklist to audit any MCP server repo before marking it production-ready.

## 🏗️ CORE MCP ARCHITECTURE

- [ ] FastMCP latest stable version implemented
- [ ] stdio protocol for Claude Desktop connection
- [ ] Proper tool registration with `@mcp.tool()` multiline decorators
- [ ] No nested triple quotes in tool decorators (use single quotes for inner strings)
- [ ] Self-documenting tool descriptions present
- [ ] **Multilevel help tool** implemented
- [ ] **Status tool** implemented
- [ ] **Health check tool** implemented
- [ ] **Resource management** - proper cleanup of connections, files, processes
- [ ] **Error response standardization** - consistent error format across all tools
- [ ] `prompts/` folder with comprehensive prompt templates

## 🔧 MODERN MCP REQUIREMENTS

- [ ] **Tool parameter validation** - all parameters validated with proper error messages
- [ ] **Async/await patterns** used correctly (no blocking operations)
- [ ] **Resource limits** - prevent memory/CPU exhaustion
- [ ] **Timeout handling** - all operations have reasonable timeouts
- [ ] **Concurrent request handling** - thread-safe operations
- [ ] **Configuration management** - proper config file handling
- [ ] **Environment variable support** - secure configuration via env vars

## ✨ CODE QUALITY

- [ ] ALL `print()` / `console.log()` replaced with structured logging (use logger, not print)
- [ ] Comprehensive error handling (try/catch everywhere with proper error responses)
- [ ] Graceful degradation on failures (return meaningful error messages, not crashes)
- [ ] Type hints (Python) / TypeScript types throughout
- [ ] Input validation on ALL tool parameters
- [ ] Proper resource cleanup (connections, files, processes)
- [ ] No memory leaks (verified with profiling tools)

## 📦 PACKAGING & DISTRIBUTION

- [ ] Anthropic `mcpb validate` passes successfully
- [ ] Anthropic `mcpb pack` creates valid package
- [ ] **NO dependencies in mcpb file** - dependencies installed by MCP client
- [ ] **Extensive prompt templates** in `prompts/` folder covering all use cases
- [ ] Claude Desktop config example in README
- [ ] Virtual environment setup script (`venv` for Python) - NOT included in mcpb package
- [ ] Installation instructions tested and working

## 🧪 TESTING

- [ ] Unit tests in `tests/unit/` covering all tools
- [ ] Integration tests in `tests/integration/`
- [ ] Test fixtures and mocks created
- [ ] Coverage reporting configured (target: >80%)
- [ ] PowerShell test runner scripts present (`.ps1` files for Windows)
- [ ] **ALTERNATING WORKFLOW**: Run `ruff check` and `pytest` iteratively until:
  - [ ] All pytest tests pass
  - [ ] Ruff finds no linting errors
  - [ ] Ruff has formatted all files (`ruff format`)
  - [ ] No remaining code quality issues
- [ ] All tests passing (verified with CI/CD)

## 📚 DOCUMENTATION

- [ ] README.md updated: features, installation, usage, troubleshooting
- [ ] PRD updated with current capabilities (Product Requirements Document)
- [ ] API documentation for all tools
- [ ] `CHANGELOG.md` following Keep a Changelog format
- [ ] Wiki pages: architecture, development guide, FAQ (or comprehensive docs folder)
- [ ] `CONTRIBUTING.md` with contribution guidelines
- [ ] `SECURITY.md` with security policy

## 🔧 GITHUB INFRASTRUCTURE

- [ ] CI/CD workflows in `.github/workflows/`: test, lint, build, release
- [ ] Dependabot configured for dependency updates
- [ ] Issue templates created
- [ ] PR templates created
- [ ] Release automation with semantic versioning
- [ ] Branch protection rules documented
- [ ] GitHub Actions all passing

## 📁 GIT & REPOSITORY MANAGEMENT

### **Local Repository Setup**
- [ ] **Clean git history** - meaningful commit messages, no merge commits
- [ ] **Proper .gitignore** - excludes build artifacts, logs, venv, __pycache__
- [ ] **Branch strategy** - main/develop branches, feature branches
- [ ] **Pre-commit hooks** - automated linting, formatting, testing
- [ ] **Commit message convention** - conventional commits (feat:, fix:, docs:, etc.)
- [ ] **Large file handling** - Git LFS for models/assets, no large files in history

### **State-of-the-Art CI/CD Pipeline**
- [ ] **Multi-stage pipeline** - test → lint → build → security scan → deploy
- [ ] **Matrix testing** - multiple Python versions, OS combinations
- [ ] **Caching strategy** - dependency cache, build cache, test cache
- [ ] **Parallel execution** - tests run in parallel for speed
- [ ] **Conditional workflows** - only run on relevant changes
- [ ] **Artifact management** - store build artifacts, test reports
- [ ] **Security scanning** - SAST, dependency scanning, secret detection
- [ ] **Performance testing** - automated performance benchmarks
- [ ] **Code coverage reporting** - integrated coverage reports
- [ ] **Quality gates** - fail pipeline on coverage/quality thresholds

### **Modern Release Mechanism**
- [ ] **Semantic versioning** - automated version bumping (major.minor.patch)
- [ ] **Release automation** - GitHub Releases with changelog generation
- [ ] **Package publishing** - automated PyPI/npm publishing
- [ ] **Draft releases** - manual approval before publishing
- [ ] **Release notes** - auto-generated from conventional commits
- [ ] **Rollback capability** - easy rollback to previous versions
- [ ] **Release channels** - alpha, beta, stable release tracks
- [ ] **Dependency updates** - automated dependency updates with testing
- [ ] **Release validation** - automated testing of release artifacts
- [ ] **Distribution** - multiple distribution channels (PyPI, GitHub, Docker)

## 💻 PLATFORM REQUIREMENTS (Windows/PowerShell)

- [ ] No Linux syntax (`&&`, `||`, etc.)
- [ ] PowerShell cmdlets used (`New-Item` not `mkdir`, `Copy-Item` not `cp`)
- [ ] File paths use backslashes
- [ ] Paths with spaces properly quoted
- [ ] Cross-platform path handling (`pathlib.Path` or `os.path.join` where needed)
- [ ] All PowerShell scripts tested on Windows

## 🎁 EXTRAS

- [ ] Example configurations for common use cases
- [ ] Performance benchmarks (if applicable) - response times, memory usage
- [ ] Rate limiting/quota handling (where relevant) - API limits, request throttling
- [ ] Secrets management documentation (env vars, config files, secure storage)
- [ ] Error messages are user-friendly (clear, actionable, not technical jargon)
- [ ] Logging levels properly configured (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## 📋 FINAL REVIEW

- [ ] All dependencies up to date
- [ ] No security vulnerabilities (npm audit / pip-audit / safety check)
- [ ] License file present and correct
- [ ] Version number follows semantic versioning
- [ ] Git tags match releases
- [ ] Repository description and topics set on GitHub

---

**Total Items:** 95  
**Completed:** _____ / 95  
**Coverage:** _____%

**Auditor:** _____________  
**Date:** _____________  
**Repo:** _____________  
**Status:** ⬜ In Progress | ⬜ Ready for Review | ⬜ Production Ready