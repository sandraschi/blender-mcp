# Dependency Management with UV

> **Single source of truth** - How to avoid "missing dependency" disasters

Based on fixing 5+ "command not found" failures in our workflows.

---

## 🎯 The Golden Rule

**Everything that CI needs must be in `pyproject.toml`**

```toml
[tool.uv]
dev-dependencies = [
    # If CI runs it, it MUST be here!
]
```

---

## 📦 Complete Dev Dependencies Template

### Copy This to Your `pyproject.toml`

```toml
[tool.uv]
dev-dependencies = [
    # === Testing ===
    "pytest>=8.3.4",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "pytest-asyncio>=0.24.0",
    "pytest-xdist>=3.0.0",  # Parallel testing
    
    # === Linting & Formatting ===
    "ruff>=0.1.6",  # Fast linter + formatter
    "black>=24.0.0",  # Alternative formatter
    "isort>=5.13.0",  # Import sorting
    
    # === Type Checking ===
    "pyright>=1.1.390",  # Microsoft's type checker
    "mypy>=1.8.0",  # Alternative type checker
    "types-setuptools>=69.0.0",  # Type stubs
    
    # === Security ===
    "bandit>=1.7.0",  # Code security scanner
    "safety>=3.0.0",  # Dependency vulnerability scanner
    
    # === Building & Publishing ===
    "build>=1.0.0",  # CRITICAL - for building packages
    "twine>=5.0.0",  # CRITICAL - for validating packages
    
    # === Pre-commit ===
    "pre-commit>=3.6.0",  # Git hooks
    
    # === Utilities ===
    "icecream>=2.1.3",  # Debugging
    "gevent>=24.11.1",  # Async support
]
```

---

## ⚠️ Critical Dependencies Often Forgotten

### 1. Build Tools (MUST HAVE)

```toml
"build>=1.0.0",   # For: uv build, python -m build
"twine>=5.0.0",   # For: twine check dist/*
```

**Without these**:
```bash
# In CI:
$ uv run twine check dist/*
ERROR: twine: command not found
# Workflow fails ❌
```

**With these**:
```bash
$ uv sync --dev  # Installs build + twine
$ uv build  # ✅ Works!
$ uv run twine check dist/*  # ✅ Works!
```

---

### 2. Security Tools (MUST HAVE for security scans)

```toml
"bandit>=1.7.0",   # For: bandit -r src/
"safety>=3.0.0",   # For: safety scan
```

**Without these**:
```bash
$ uv run bandit -r src/
ERROR: bandit: command not found
# Security scan fails ❌
```

---

### 3. Type Checking (HIGHLY RECOMMENDED)

```toml
"pyright>=1.1.390",  # Recommended - fast, accurate
"mypy>=1.8.0",       # Alternative - stricter
```

**Both is OK too!** Different tools catch different issues.

---

## 🔧 UV Commands Reference

### Essential Commands

```bash
# Install all dependencies from pyproject.toml
uv sync

# Install including dev dependencies
uv sync --dev

# Add new dependency
uv add "package-name>=1.0.0"

# Add dev dependency
uv add --dev "package-name>=1.0.0"

# Update lock file
uv lock

# Update all dependencies
uv lock --upgrade

# Build package
uv build

# Run command in venv
uv run command args

# Install package in editable mode
uv pip install -e .
```

---

## 📊 Dependency Categories Explained

### 1. Runtime Dependencies (`dependencies`)

**Goes in**: `[project] dependencies = [...]`

**Purpose**: Required for your package to work

**Examples**:
```toml
[project]
dependencies = [
    "fastapi>=0.115.0",      # Your web framework
    "sqlalchemy>=2.0.0",     # Your database ORM
    "pydantic>=2.0.0",       # Data validation
    "defusedxml>=0.7.1",     # Security (if you parse XML)
]
```

**Rule**: If your code imports it, it goes here!

---

### 2. Dev Dependencies (`dev-dependencies`)

**Goes in**: `[tool.uv] dev-dependencies = [...]`

**Purpose**: Required for development/testing/CI

**Examples**:
```toml
[tool.uv]
dev-dependencies = [
    "pytest>=8.3.4",       # Testing
    "ruff>=0.1.6",         # Linting
    "pyright>=1.1.390",    # Type checking
    "build>=1.0.0",        # Building
    "twine>=5.0.0",        # Publishing
]
```

**Rule**: If CI runs it, it goes here!

---

## 🚨 Common Mistakes

### Mistake #1: Using `uv pip install` in CI

**Wrong**:
```yaml
- run: uv pip install build twine  # ❌ Fragile!
```

**Why it fails**:
- Needs project context
- Doesn't use lock file
- Not reproducible

**Right**:
```toml
# In pyproject.toml
[tool.uv]
dev-dependencies = [
    "build>=1.0.0",
    "twine>=5.0.0",
]
```

```yaml
# In workflow
- run: uv sync --dev  # ✅ Installs from pyproject.toml
```

---

### Mistake #2: Forgetting to Lock

**Problem**:
```bash
# Add dependency but forget to lock
$ uv add "new-package"
$ git add pyproject.toml
$ git commit
# Push without uv.lock! ❌
```

**Result**: CI gets different versions!

**Solution**:
```bash
$ uv add "new-package"  # Automatically updates uv.lock
$ git add pyproject.toml uv.lock  # ✅ Commit both!
$ git commit -m "feat: add new-package"
```

---

### Mistake #3: Not Updating Vulnerable Deps

**Problem**:
```bash
$ uv run safety scan
-> Vulnerability found in package version 1.0.0
   Fix: Update to 1.1.0+

# But developer ignores it ❌
```

**Solution**:
```bash
# Update immediately
$ uv add "package>=1.1.0"

# Verify fix
$ uv run safety scan
# Should show: 0 vulnerabilities ✅
```

---

## 🎯 Workflow Integration

### Single Install Command

Your workflow should only need:

```yaml
- name: Install dependencies
  run: uv sync --dev
```

This installs:
- ✅ All runtime dependencies
- ✅ All dev dependencies
- ✅ Locked versions from uv.lock
- ✅ Build tools (build, twine)
- ✅ Security tools (bandit, safety)
- ✅ Test tools (pytest, pytest-cov)
- ✅ Lint tools (ruff, pyright)

**No other install commands needed!**

---

## 📋 Dependency Audit Checklist

### Before First Release:

- [ ] All imports have corresponding dependencies
- [ ] `build` in dev-dependencies
- [ ] `twine` in dev-dependencies
- [ ] `bandit` in dev-dependencies
- [ ] `safety` in dev-dependencies
- [ ] Security tools (`defusedxml` if using XML)
- [ ] Type checking tools (`pyright` or `mypy`)
- [ ] Testing tools (`pytest`, `pytest-cov`)
- [ ] `uv.lock` committed to git
- [ ] No `uv pip install` in workflows

### After Adding New Code:

- [ ] New imports → Add to dependencies
- [ ] New dev tools → Add to dev-dependencies
- [ ] Run `uv lock` to update lock file
- [ ] Commit both `pyproject.toml` and `uv.lock`
- [ ] Test that `uv sync --dev` installs everything

---

## 🔍 Debugging Dependency Issues

### "Command not found" in CI

**Symptom**:
```
$ uv run bandit -r src/
ERROR: bandit: command not found
```

**Diagnosis**:
```bash
# Check if it's in dev-dependencies
$ grep -i bandit pyproject.toml
# If not found → Add it!
```

**Fix**:
```bash
$ uv add --dev "bandit>=1.7.0"
$ git add pyproject.toml uv.lock
$ git commit -m "fix: add missing bandit dependency"
```

---

### "Module not found" at Runtime

**Symptom**:
```python
ModuleNotFoundError: No module named 'fastapi'
```

**Diagnosis**:
```bash
# Check if it's in runtime dependencies
$ grep -i fastapi pyproject.toml
# Should be in [project] dependencies, not [tool.uv] dev-dependencies!
```

**Fix**:
```bash
$ uv add "fastapi>=0.115.0"  # Adds to runtime dependencies
$ git add pyproject.toml uv.lock
$ git commit -m "fix: add missing fastapi dependency"
```

---

### Lock File Conflicts

**Symptom**:
```bash
$ git pull
CONFLICT (content): Merge conflict in uv.lock
```

**Fix**:
```bash
# Regenerate lock file
$ uv lock

# Commit resolved lock
$ git add uv.lock
$ git commit -m "fix: resolve lock file conflict"
```

---

## 🎯 Dependency Update Strategy

### Conservative (Stable Projects)

```toml
# Pin to minor versions
dependencies = [
    "fastapi>=0.115.0,<0.116",
    "sqlalchemy>=2.0.0,<2.1",
]
```

**Pros**: Predictable, few breaking changes  
**Cons**: Miss security patches

---

### Moderate (Recommended)

```toml
# Allow patch updates
dependencies = [
    "fastapi>=0.115.0,<1.0",
    "sqlalchemy>=2.0.0,<3.0",
]
```

**Pros**: Security patches, minor features  
**Cons**: Occasional breaking changes

---

### Aggressive (Edge)

```toml
# Latest versions
dependencies = [
    "fastapi>=0.115.0",  # No upper bound
    "sqlalchemy>=2.0.0",
]
```

**Pros**: Latest features and fixes  
**Cons**: More breaking changes

---

## 📊 Dependency Health Metrics

### Our Stats:

| Metric | Value |
|--------|-------|
| Total dependencies | 40 |
| Dev dependencies | 17 |
| Security vulnerabilities | 0 |
| Outdated packages | 0 |
| Lock file size | 150 packages (with transitive deps) |

### Check Your Stats:

```bash
# List all dependencies
uv pip list

# Check for updates
uv lock --upgrade --dry-run

# Check for vulnerabilities
uv run safety scan
```

---

## 🚀 Best Practices

### Do's ✅

1. **Always commit `uv.lock`** - Ensures reproducible builds
2. **Use `uv sync --dev` in CI** - Single source of truth
3. **Update regularly** - Weekly dependency updates
4. **Scan for vulnerabilities** - Weekly security scans
5. **Pin important deps** - Avoid breaking changes
6. **Document why** - Explain version constraints

### Don'ts ❌

1. **Don't use `uv pip install` in workflows** - Use `uv sync`
2. **Don't commit without lock** - Always commit `uv.lock`
3. **Don't ignore vulnerabilities** - Fix immediately
4. **Don't over-pin** - Allow security patches
5. **Don't forget dev deps** - CI will fail mysteriously
6. **Don't mix package managers** - Stick to `uv`

---

## 🔗 Related Documentation

- [Workflows Guide](./WORKFLOWS.md) - Where these dependencies are used
- [Security Hardening](./SECURITY_HARDENING.md) - Why security tools are critical
- [Troubleshooting](./TROUBLESHOOTING.md) - Fixing dependency issues

---

**Remember**: 15 minutes managing dependencies saves 3+ hours debugging CI failures! 📦

