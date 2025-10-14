# MCP Server Production Audit Checklist

Use this checklist to audit any MCP server repo before marking it production-ready.

## 🏗️ CORE MCP ARCHITECTURE

- [ ] FastMCP 2.12+ framework implemented
- [ ] stdio protocol for Claude Desktop connection
- [ ] Proper tool registration with `@mcp.tool()` multiline decorators
- [ ] No `"""` inside `"""` delimited decorators
- [ ] Self-documenting tool descriptions present
- [ ] **Multilevel help tool** implemented
- [ ] **Status tool** implemented
- [ ] **Health check tool** implemented
- [ ] `prompts/` folder with example prompt templates

## ✨ CODE QUALITY

- [ ] ALL `print()` / `console.log()` replaced with structured logging
- [ ] Comprehensive error handling (try/catch everywhere)
- [ ] Graceful degradation on failures
- [ ] Type hints (Python) / TypeScript types throughout
- [ ] Input validation on ALL tool parameters
- [ ] Proper resource cleanup (connections, files, processes)
- [ ] No memory leaks (verified)

## 📦 PACKAGING & DISTRIBUTION

- [ ] Anthropic `mcpb validate` passes successfully
- [ ] Anthropic `mcpb pack` creates valid package
- [ ] Package includes ALL dependencies (not just code)
- [ ] Claude Desktop config example in README
- [ ] Virtual environment setup script (`venv` for Python)
- [ ] Installation instructions tested and working

## 🧪 TESTING

- [ ] Unit tests in `tests/unit/` covering all tools
- [ ] Integration tests in `tests/integration/`
- [ ] Test fixtures and mocks created
- [ ] Coverage reporting configured (target: >80%)
- [ ] PowerShell test runner scripts present
- [ ] All tests passing

## 📚 DOCUMENTATION

- [ ] README.md updated: features, installation, usage, troubleshooting
- [ ] PRD updated with current capabilities
- [ ] API documentation for all tools
- [ ] `CHANGELOG.md` following Keep a Changelog format
- [ ] Wiki pages: architecture, development guide, FAQ
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

## 💻 PLATFORM REQUIREMENTS (Windows/PowerShell)

- [ ] No Linux syntax (`&&`, `||`, etc.)
- [ ] PowerShell cmdlets used (`New-Item` not `mkdir`, `Copy-Item` not `cp`)
- [ ] File paths use backslashes
- [ ] Paths with spaces properly quoted
- [ ] Cross-platform path handling (`path.join` where needed)
- [ ] All PowerShell scripts tested on Windows

## 🎁 EXTRAS

- [ ] Example configurations for common use cases
- [ ] Performance benchmarks (if applicable)
- [ ] Rate limiting/quota handling (where relevant)
- [ ] Secrets management documentation (env vars, config)
- [ ] Error messages are user-friendly
- [ ] Logging levels properly configured

## 📋 FINAL REVIEW

- [ ] All dependencies up to date
- [ ] No security vulnerabilities (npm audit / pip-audit)
- [ ] License file present and correct
- [ ] Version number follows semantic versioning
- [ ] Git tags match releases
- [ ] Repository description and topics set on GitHub

---

**Total Items:** 60  
**Completed:** _____ / 60  
**Coverage:** _____%

**Auditor:** _____________  
**Date:** _____________  
**Repo:** _____________  
**Status:** ⬜ In Progress | ⬜ Ready for Review | ⬜ Production Ready
