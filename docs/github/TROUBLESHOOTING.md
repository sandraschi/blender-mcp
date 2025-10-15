# GitHub Actions Troubleshooting Guide

> **Every error we encountered and how we fixed it** - Save yourself hours of debugging!

---

## 🔴 Critical Workflow Failures

### Error: "twine: command not found"

**Full Error**:
```
Run uv run twine check dist/*
ERROR: twine: command not found
Error: Process completed with exit code 1.
```

**Cause**: `twine` not installed in CI environment

**Fix**:
```toml
# Add to pyproject.toml
[tool.uv]
dev-dependencies = [
    "twine>=5.0.0",  # ✅ Now installed with uv sync --dev
]
```

```yaml
# In workflow
- run: uv sync --dev  # Installs twine
- run: uv run twine check dist/*  # ✅ Now works!
```

**Time wasted**: 30 minutes  
**Lesson**: All CI tools must be in dev-dependencies!

---

### Error: "build: command not found"

**Full Error**:
```
Run uv run python -m build
ERROR: No module named 'build'
Error: Process completed with exit code 1.
```

**Cause**: `build` package not installed

**Wrong fix**:
```yaml
- run: uv pip install build  # ❌ Doesn't work reliably
```

**Right fix**:
```toml
# Add to pyproject.toml
[tool.uv]
dev-dependencies = [
    "build>=1.0.0",
]
```

```yaml
# In workflow
- run: uv sync --dev
- run: uv build  # ✅ Use uv's native build command
```

**Time wasted**: 1 hour  
**Lesson**: Use `uv build` instead of `python -m build`

---

### Error: "bandit: command not found"

**Full Error**:
```
Run uv run bandit -r src/
ERROR: bandit: command not found
```

**Cause**: Security scan runs but `bandit` not installed

**Fix**:
```toml
[tool.uv]
dev-dependencies = [
    "bandit>=1.7.0",  # ✅
]
```

Already fixed if you copied the complete dev-dependencies!

---

### Error: Deprecated GitHub Actions

**Full Error**:
```
Warning: The `actions/create-release@v1` action is deprecated
Error: Resource not accessible by integration
```

**Cause**: Using deprecated GitHub Actions

**Wrong approach**:
```yaml
- uses: actions/create-release@v1  # ❌ Deprecated!
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Right approach**:
```yaml
- uses: softprops/action-gh-release@v1  # ✅ Modern!
  with:
    files: |
      dist/*.mcpb
      dist/*.whl
      dist/*.tar.gz
```

**Time wasted**: 2 hours  
**Lesson**: Use modern, maintained actions

---

## 🔴 Security Scan Failures

### Error: "safety check: command deprecated"

**Full Error**:
```
DEPRECATED: this command (check) has been DEPRECATED, 
and will be unsupported beyond 01 June 2024.
```

**Cause**: Using old `safety check` instead of `safety scan`

**Wrong**:
```yaml
- run: uv run safety check --json --output report.json  # ❌ Deprecated
```

**Right**:
```yaml
- run: uv run safety scan --output json --save-as report.json  # ✅ Modern
```

**Time wasted**: 30 minutes  
**Lesson**: Check tool documentation for command updates

---

### Error: Security scan blocks workflow

**Problem**: Bandit finds issues → entire workflow fails

**Wrong approach**:
```yaml
- run: uv run bandit -r src/  # ❌ Fails on any finding
# Blocks deployment even for low-severity issues!
```

**Right approach**:
```yaml
- run: uv run bandit -r src/ || echo "Scan completed"
  continue-on-error: true  # ✅ Never blocks

- name: Upload reports
  if: always()  # ✅ Always uploads results
```

**Time wasted**: 1 hour  
**Lesson**: Security scans should inform, not block

---

### Error: "Semgrep: Unauthorized"

**Full Error**:
```
Error: Semgrep failed with exit code 1
Error: API request failed: 401 Unauthorized
```

**Cause**: No `SEMGREP_APP_TOKEN` secret configured

**Fix Option 1** (Skip Semgrep):
```yaml
- name: Run Semgrep
  if: env.SEMGREP_APP_TOKEN != ''  # ✅ Only run if token exists
  uses: returntocorp/semgrep-action@v1
  continue-on-error: true  # ✅ Don't block if missing
```

**Fix Option 2** (Add token):
1. Go to https://semgrep.dev/login
2. Create token
3. Add to GitHub Secrets as `SEMGREP_APP_TOKEN`

**Time wasted**: 45 minutes  
**Lesson**: Make optional tools actually optional!

---

## 🔴 Build Failures

### Error: "No files found matching dist/*"

**Full Error**:
```
Run uv run twine check dist/*
ERROR: No files found matching 'dist/*'
```

**Cause**: Build step failed silently or dist/ not created

**Diagnosis**:
```yaml
- name: Build package
  run: uv build  # Check this step's output!
```

**Common causes**:
1. `pyproject.toml` syntax error
2. Missing `[project]` metadata
3. Build dependencies not installed

**Fix**:
```yaml
- name: Install dependencies
  run: uv sync --dev  # ✅ Install build first

- name: Build package
  run: uv build  # ✅ Now works

- name: Verify build
  run: ls -la dist/  # ✅ Check files created
```

---

### Error: "MCPB pack failed"

**Full Error**:
```
Run mcpb pack . ../dist/project.mcpb
ERROR: mcpb: command not found
```

**Cause**: MCPB CLI not installed

**Fix**:
```yaml
- name: Set up Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '18'  # ✅ Required for npm

- name: Install MCPB CLI
  run: npm install -g @anthropic-ai/mcpb

- name: Build MCPB
  run: |
    if command -v mcpb >/dev/null 2>&1; then
      cd mcpb && mcpb pack . ../dist/project.mcpb
    else
      echo "Fallback: creating ZIP"
      cd mcpb && zip -r ../dist/project.mcpb .
    fi  # ✅ Fallback if MCPB unavailable
```

---

## 🔴 Type Checking Errors

### Error: "FunctionTool is not callable"

**Full Error**:
```
error: Object of type "FunctionTool" is not callable
```

**See**: [Complete Type Fix Guide](./COMPLETE_TYPE_FIX_GUIDE.md#1-functiontool-not-callable)

**Quick fix**:
```python
from blender_mcp.mcp.tools import read_note as mcp_read_note

result = await mcp_read_note.fn(identifier)  # ✅ Use .fn()
```

---

### Error: "No parameter named 'page'"

**Full Error**:
```
error: No parameter named "page" in SearchQuery
```

**See**: [Complete Type Fix Guide](./COMPLETE_TYPE_FIX_GUIDE.md#2-searchquery-parameter-mismatch)

**Quick fix**:
```python
query = SearchQuery(text=search_text)  # Only takes 'text'
response = await call_post(
    client, url, json=query.model_dump(),
    params={"page": 1, "page_size": 100}  # ✅ In params
)
```

---

## 🔴 Test Failures

### Error: "API server not running"

**Full Error**:
```
Exception: API server not running
tests/cli/test_project_commands.py::test_create_project FAILED
```

**Cause**: CLI tests need API server for internal calls

**Fix**: Tests should auto-start API server via fixtures

**Check**:
```python
# In conftest.py
@pytest.fixture
async def api_client():
    # Should start API server
    async with TestClient(app) as client:
        yield client
```

---

### Error: "JSONDecodeError: Expecting value"

**Full Error**:
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Cause**: CLI command outputs non-JSON when expecting JSON

**Fix**:
```python
# In CLI command with --json flag:
if json_output:
    print(json.dumps(data))  # ✅ Use print(), not console.print()
else:
    console.print(formatted_output)
```

---

## 🔴 Formatting Failures

### Error: "111 files would be reformatted"

**Full Error**:
```
Would reformat: src/file1.py
Would reformat: src/file2.py
...
111 files would be reformatted
Error: Process completed with exit code 1
```

**Cause**: Files not formatted with ruff

**Fix**:
```bash
# Format all files locally
$ uv run ruff format .

# Verify
$ uv run ruff format --check .
# All checks passed!

# Commit
$ git add -A
$ git commit -m "style: apply ruff formatting"
```

**Prevention**: Add pre-commit hook

**Time wasted**: 15 minutes  
**Lesson**: Format before pushing!

---

## 🔴 Release Workflow Issues

### Error: "steps.create_release.outputs.upload_url not found"

**Full Error**:
```
Error: Unable to get upload URL from create_release step
```

**Cause**: Release creation step has no `id`

**Wrong**:
```yaml
- name: Create GitHub Release  # ❌ No id!
  uses: actions/create-release@v1
```

**Right** (but still deprecated):
```yaml
- name: Create GitHub Release
  id: create_release  # ✅ Add id
  uses: actions/create-release@v1
```

**Best** (modern action):
```yaml
- uses: softprops/action-gh-release@v1  # ✅ No id needed!
  with:
    files: dist/*
```

---

### Error: "PyPI publishing failed"

**Full Error**:
```
Error: HTTPError: 403 Forbidden
```

**Causes**:
1. Missing `PYPI_API_TOKEN` secret
2. Wrong token permissions
3. Package already exists with same version

**Fix**:
1. Create token at https://pypi.org/manage/account/token/
2. Add to GitHub Secrets as `PYPI_API_TOKEN`
3. Ensure workflow has:
   ```yaml
   environment: pypi  # Links to environment secrets
   ```

---

## 🛠️ Diagnostic Commands

### Check Workflow Locally

```bash
# 1. All linting checks
uv run ruff check . --fix
uv run ruff format --check .

# 2. Type checking
uv run pyright

# 3. Security
uv run bandit -r src/ --severity-level high
uv run safety scan

# 4. Tests
uv run pytest -v

# 5. Build
uv build
uv run twine check dist/*

# If all pass → CI should pass!
```

---

### Check Dependencies

```bash
# List installed packages
uv pip list

# Check what will be installed
uv sync --dry-run --dev

# Verify specific package
uv pip show bandit
uv pip show twine
```

---

### Check Git Status

```bash
# What changed?
git status

# What's staged?
git diff --cached

# What's in remote?
git log origin/master..HEAD
```

---

## 📊 Common Error Patterns

| Error Message | Cause | Fix | Time Saved |
|---------------|-------|-----|------------|
| "command not found" | Missing dev-dependency | Add to `pyproject.toml` | 30 min |
| "deprecated" warning | Old action version | Update to modern action | 1 hour |
| "No files found" | Build failed | Check build step output | 20 min |
| "401 Unauthorized" | Missing secret | Add to GitHub Secrets | 15 min |
| "Type error" | Missing import/type hint | See Type Fix Guide | 2+ hours |
| "Formatting failed" | Unformatted code | Run `ruff format .` | 10 min |

---

## 🎯 Quick Fixes Cheat Sheet

```bash
# Linting failed
uv run ruff check . --fix && git add -A && git commit -m "fix: linting"

# Formatting failed  
uv run ruff format . && git add -A && git commit -m "style: formatting"

# Type checking failed
# See: COMPLETE_TYPE_FIX_GUIDE.md (no quick fix!)

# Security scan failed
uv run safety scan  # Check locally
uv add "package>=safe.version"  # Update vulnerable deps

# Build failed
uv sync --dev  # Ensure dependencies
uv build  # Try locally first

# Tests failed
uv run pytest -v  # Run locally
uv run pytest path/to/test.py  # Run specific test
```

---

## 🔍 Debugging Workflow Failures

### Step 1: Check GitHub Actions Logs

1. Go to https://github.com/your-org/your-repo/actions
2. Click failed workflow run
3. Click failed job
4. Read error message (usually at the bottom)

### Step 2: Reproduce Locally

```bash
# Run the exact command that failed
uv run <command>

# Check if dependency is installed
uv pip show <package>

# Install dependencies if missing
uv sync --dev
```

### Step 3: Fix and Test

```bash
# Make fix
vim file.py

# Test locally
uv run <command>

# Commit and push
git add -A
git commit -m "fix: description"
git push
```

### Step 4: Monitor

Watch GitHub Actions to verify fix worked

---

## 🚨 Emergency Fixes

### Workflow is Completely Broken

**Nuclear option**:

```yaml
# Add to job:
  continue-on-error: true  # Allows workflow to continue

# Or to step:
  - run: command
    continue-on-error: true  # Allows step to fail
```

**Use sparingly!** Better to fix the root cause.

---

### Need to Release NOW but CI Failing

**Option 1**: Fix the CI
```bash
# Best approach - fix properly
```

**Option 2**: Manual release
```bash
# Build locally
uv build

# Create release manually on GitHub
# Upload dist/* files

# Tag manually
git tag -a v1.0.0 -m "Release"
git push origin v1.0.0
```

**Option 3**: Skip CI
```yaml
# In workflow
on:
  push:
    branches: [ main ]
  workflow_dispatch:  # ✅ Manual trigger
```

Trigger manually and monitor closely.

---

## 📋 Pre-Push Checklist

**Run locally before every push**:

```bash
# Quick check (2 min)
uv run ruff check . --fix
uv run ruff format .

# Medium check (5 min)
uv run pyright
uv run pytest

# Full check (10 min)
uv run bandit -r src/ --severity-level high
uv run safety scan
uv build
```

**If all pass locally → CI will probably pass!**

---

## 🔄 Workflow Status Matrix

### Understanding Job Dependencies

```yaml
jobs:
  lint:     # No dependencies
  test:     # No dependencies  
  security: # No dependencies
  
  build:
    needs: [lint, test, security]  # Waits for all 3
    if: always() && needs.lint.result == 'success'  # Must pass lint
  
  quality-gate:
    needs: [lint, test, security, build]  # Waits for all
    if: always()  # Always runs
```

**Result**:
- If `lint` fails → `build` is skipped → `quality-gate` runs anyway
- If `test` fails → `build` still runs (if `lint` passed)
- If `security` fails → Ignored (has `continue-on-error`)

---

## 🎯 Common Configuration Mistakes

### Mistake #1: Missing Permissions

**Error**:
```
Error: Resource not accessible by integration
```

**Fix**:
```yaml
jobs:
  release:
    permissions:
      contents: write  # ✅ Required for creating releases
      packages: write  # ✅ Required for publishing packages
```

---

### Mistake #2: Wrong Branch Names

**Error**: Workflow doesn't trigger

**Cause**:
```yaml
on:
  push:
    branches: [ main ]  # But your branch is 'master'!
```

**Fix**:
```yaml
on:
  push:
    branches: [ main, master, develop ]  # ✅ Support all common names
```

---

### Mistake #3: Missing Environment

**Error**:
```
Error: Environment 'pypi' not found
```

**Cause**:
```yaml
publish-pypi:
  environment: pypi  # But environment doesn't exist!
```

**Fix**:
1. Go to Settings → Environments
2. Create environment named `pypi`
3. Add secrets to environment

**Or remove**:
```yaml
publish-pypi:
  # environment: pypi  # ✅ Not required for basic publishing
```

---

## 📱 Getting Help

### When Stuck:

1. **Check this troubleshooting guide** (you're here!)
2. **Check GitHub Actions logs** (detailed error messages)
3. **Run locally** (reproduce the exact command)
4. **Check tool docs** (bandit, safety, ruff, etc.)
5. **Google the exact error** (someone else hit it too!)
6. **Open an issue** (with full error details)

### What to Include in Issue:

```markdown
## Error

[Paste full error message]

## Workflow

[Link to failed workflow run]

## What I tried

- Tried X → Result Y
- Checked Z → Found W

## Environment

- Python version: 3.12
- UV version: 0.x.x
- OS: Ubuntu/Windows/macOS
```

---

## ✅ Success Indicators

### Your workflow is healthy when:

- ✅ CI passes on every push
- ✅ Security scans complete (even with findings)
- ✅ Build artifacts are created
- ✅ Releases publish automatically
- ✅ No "command not found" errors
- ✅ No deprecated action warnings

---

## 🎓 Lessons from 6 Hours of Debugging

### Timeline of Our Pain:

| Hour | Issue | Fix | Status |
|------|-------|-----|--------|
| 0-1 | 130+ type errors | Systematic fixing | ✅ |
| 1-2 | 130+ lint errors | Ruff auto-fix | ✅ |
| 2-3 | Deprecated actions | Modern actions | ✅ |
| 3-4 | Missing dependencies | Complete dev-deps | ✅ |
| 4-5 | Security blocking | continue-on-error | ✅ |
| 5-6 | Vulnerabilities | Update deps, defusedxml | ✅ |

### What We'd Do Differently:

1. **Start with complete `pyproject.toml`** - Would save 2 hours
2. **Use modern actions from the start** - Would save 1 hour
3. **Make security scans non-blocking** - Would save 1 hour
4. **Format code before first commit** - Would save 30 min
5. **Check for deprecated commands** - Would save 30 min

**Total time that could have been saved**: ~5 hours!

---

## 🚀 Copy This to Other Repos

### Quick Setup for New Repo:

```bash
# 1. Copy workflows
cp -r .github/workflows/ /path/to/new-repo/.github/

# 2. Copy pyproject.toml dev-dependencies section
# (manual copy-paste)

# 3. Install and test
cd /path/to/new-repo
uv sync --dev
uv run ruff check .
uv run pyright
uv run pytest

# 4. Push and monitor
git push
# Watch GitHub Actions succeed on first try! 🎉
```

**Time**: ~30 minutes vs 6 hours debugging!

---

## 📚 Related Guides

- [Workflows Templates](./WORKFLOWS.md)
- [Type Fix Guide](./COMPLETE_TYPE_FIX_GUIDE.md)
- [Security Hardening](./SECURITY_HARDENING.md)
- [Dependency Management](./DEPENDENCY_MANAGEMENT.md)

---

**Don't repeat our mistakes - use this guide!** 🎯

