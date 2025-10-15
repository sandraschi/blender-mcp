# Pre-Release Validation Checklist

> **Don't ship broken code!** - Complete pre-release validation from our beta release experience.

Use this checklist before **every** release to ensure quality.

---

## 📋 Complete Release Checklist

### Phase 1: Code Quality (Required)

- [ ] **Type checking passes**
  ```bash
  uv run pyright
  # Expected: 0 errors found
  ```

- [ ] **Linting passes**
  ```bash
  uv run ruff check .
  # Expected: All checks passed!
  ```

- [ ] **Formatting passes**
  ```bash
  uv run ruff format --check .
  # Expected: All checks passed!
  ```

- [ ] **All tests pass**
  ```bash
  uv run pytest -v
  # Expected: >95% pass rate
  ```

**If any fail → STOP. Fix before continuing.**

---

### Phase 2: Security Validation (Required)

- [ ] **No HIGH severity security issues**
  ```bash
  uv run bandit -r src/ --severity-level high
  # Expected: No issues identified
  ```

- [ ] **No dependency vulnerabilities**
  ```bash
  uv run safety scan
  # Expected: 0 vulnerabilities reported
  ```

- [ ] **Dependencies up to date**
  ```bash
  uv lock --upgrade --dry-run
  # Review: Any critical updates?
  ```

- [ ] **No secrets in code**
  ```bash
  git grep -i "password\|secret\|token\|api[_-]key" src/
  # Expected: No hardcoded secrets
  ```

**If vulnerabilities found → Update dependencies first**

---

### Phase 3: Build Validation (Required)

- [ ] **Package builds successfully**
  ```bash
  uv build
  # Check: dist/*.whl and dist/*.tar.gz created
  ```

- [ ] **Package validation passes**
  ```bash
  uv run twine check dist/*
  # Expected: Passed all checks
  ```

- [ ] **MCPB package builds** (if applicable)
  ```bash
  cd mcpb
  mcpb pack . ../dist/project.mcpb
  # Check: .mcpb file created
  ```

- [ ] **Can install from wheel**
  ```bash
  uv pip install dist/*.whl
  # Expected: Installation successful
  ```

**If builds fail → Fix configuration**

---

### Phase 4: Documentation (Required)

- [ ] **Version numbers updated**
  - [ ] `pyproject.toml` → `version = "1.0.0b2"`
  - [ ] `src/your_package/__init__.py` → `__version__ = "1.0.0b2"`
  - [ ] `mcpb/manifest.json` → `"version": "1.0.0b2"`

- [ ] **CHANGELOG.md updated**
  - [ ] New version section added
  - [ ] All changes documented
  - [ ] Breaking changes highlighted
  - [ ] Migration notes (if needed)

- [ ] **README.md reviewed**
  - [ ] Installation instructions current
  - [ ] Features list accurate
  - [ ] Examples work
  - [ ] Links not broken

- [ ] **Documentation builds** (if applicable)
  ```bash
  mkdocs build  # or your doc tool
  ```

**If docs incomplete → Update before releasing**

---

### Phase 5: Functional Testing (Beta: Required, Stable: CRITICAL)

#### For Beta Releases:

- [ ] **Smoke test** - Basic functionality works
  - [ ] Can import package
  - [ ] Core features work
  - [ ] No obvious breakage

#### For Stable Releases:

- [ ] **Complete functional testing**
  - [ ] All core features tested
  - [ ] All MCP tools tested
  - [ ] Integration scenarios tested
  - [ ] Performance acceptable
  - [ ] Error handling works

- [ ] **Megatest suite passes** (if available)
  ```bash
  pytest tests/megatest/ -v -m megatest_full
  ```

- [ ] **Integration tests pass**
  ```bash
  pytest tests/integration/ -v
  ```

- [ ] **Manual testing complete**
  - [ ] Install in real environment
  - [ ] Test common workflows
  - [ ] Verify documentation examples

**For stable releases: NO SHORTCUTS on testing!**

---

### Phase 6: GitHub Actions (Required)

- [ ] **All workflows passing on master/main**
  - Check: https://github.com/your-org/your-repo/actions
  - Expected: All green checkmarks ✅

- [ ] **Latest commit has passing CI**
  ```bash
  git log -1 --oneline
  # Check this commit in GitHub Actions
  ```

- [ ] **No pending security alerts**
  - Check: GitHub Security tab
  - Expected: No unresolved alerts

**If CI failing → Fix before tagging**

---

### Phase 7: Git Preparation (Required)

- [ ] **All changes committed**
  ```bash
  git status
  # Expected: nothing to commit, working tree clean
  ```

- [ ] **On correct branch**
  ```bash
  git branch --show-current
  # Expected: master or main
  ```

- [ ] **Synced with remote**
  ```bash
  git pull origin master
  # Expected: Already up to date
  ```

- [ ] **No local commits ahead**
  ```bash
  git log origin/master..HEAD
  # Expected: empty (or ready to push)
  ```

**If behind/ahead → Sync first**

---

## 🚀 Release Execution

### For Beta Releases (v1.0.0b2):

1. **Update versions** (if not done)
   ```bash
   # Update pyproject.toml, __init__.py, mcpb/manifest.json
   git add -A
   git commit -m "chore: bump version to 1.0.0b2"
   ```

2. **Push to remote**
   ```bash
   git push origin master
   ```

3. **Wait for CI to pass**
   - Monitor GitHub Actions
   - All workflows must be green ✅

4. **Create and push tag**
   ```bash
   git tag -a v1.0.0b2 -m "Beta release v1.0.0b2

   Production-ready beta for testing.
   
   - All code quality checks pass
   - Security scans clean
   - Ready for user testing"
   
   git push origin v1.0.0b2
   ```

5. **Monitor release workflow**
   - Check GitHub Actions
   - Verify release created
   - Download and test MCPB package

6. **Announce** (optional for beta)
   - GitHub Discussions
   - Discord/Slack
   - Beta tester group

---

### For Stable Releases (v1.0.0):

**Additional requirements**:

- [ ] **Beta testing complete**
  - Minimum 1 week of beta testing
  - All critical bugs fixed
  - No known blockers

- [ ] **Megatest suite passed**
  - All 5 levels complete
  - No failures in critical tests

- [ ] **Performance validated**
  - Load testing complete
  - No regressions
  - Acceptable response times

- [ ] **Migration guide** (if breaking changes)
  - Upgrade path documented
  - Deprecation warnings in place
  - Migration scripts (if needed)

**Follow same steps as beta, but**:
- Tag as `v1.0.0` (no suffix)
- Will publish to PyPI automatically
- Requires more thorough announcement

---

## 🎯 Post-Release Validation

### Immediately After Release:

- [ ] **GitHub Release created**
  - Check: https://github.com/your-org/your-repo/releases
  - Verify: Assets uploaded (wheel, tar.gz, .mcpb)

- [ ] **Release notes complete**
  - Changelog included
  - Installation instructions
  - Known issues documented

- [ ] **Assets downloadable**
  - Download each asset
  - Verify file sizes reasonable
  - Test installation from assets

---

### For Stable Releases Only:

- [ ] **PyPI package published**
  - Check: https://pypi.org/project/your-package/
  - Verify: Correct version listed
  - Test: `pip install your-package==1.0.0`

- [ ] **Installation works**
  ```bash
  # Fresh environment
  pip install your-package==1.0.0
  your-command --version
  # Expected: 1.0.0
  ```

- [ ] **MCPB package works in Claude Desktop**
  - Install .mcpb file
  - Verify tools appear
  - Test basic functionality

---

## 🔴 Emergency Rollback

### If Release is Broken:

1. **Delete GitHub Release**
   - Go to Releases
   - Click Edit
   - Delete release

2. **Delete tag**
   ```bash
   git tag -d v1.0.0b2
   git push origin :refs/tags/v1.0.0b2
   ```

3. **Yank from PyPI** (if published)
   ```bash
   # Login to PyPI
   # Go to package → Manage → Yank release
   ```

4. **Fix issues**
   ```bash
   # Fix the problem
   # Re-run all checklists
   ```

5. **Create new release**
   ```bash
   git tag -a v1.0.0b3 -m "Fixed release"
   git push origin v1.0.0b3
   ```

---

## 📊 Release Quality Metrics

### Our Beta Release (v1.0.0b2):

| Metric | Target | Achieved |
|--------|--------|----------|
| Type errors | 0 | ✅ 0 |
| Lint errors | 0 | ✅ 0 |
| Format issues | 0 | ✅ 0 |
| Test pass rate | >95% | ✅ 98% |
| Security HIGH | 0 | ✅ 0 |
| Vulnerabilities | 0 | ✅ 0 |
| CI passing | ✅ | ✅ All green |
| Docs updated | ✅ | ✅ Complete |

**Result**: Ready for release! ✅

---

## 🎯 Quality Gates

### Minimum for Beta Release:

```
✅ 0 type errors
✅ 0 lint errors  
✅ 0 format issues
✅ >90% tests passing
✅ 0 HIGH security issues
✅ 0 dependency vulnerabilities
✅ CI workflows passing
✅ Docs updated
```

### Minimum for Stable Release:

**All beta requirements PLUS**:

```
✅ >95% tests passing
✅ Megatest suite complete
✅ Integration tests passing
✅ Performance validated
✅ Beta testing complete (min 1 week)
✅ No known critical bugs
✅ Migration guide (if breaking)
✅ Manual testing complete
```

---

## 🔄 Release Cadence

### Recommended Schedule:

- **Beta releases**: When ready (after fixes)
- **Stable releases**: Monthly or quarterly
- **Patch releases**: As needed (security fixes)
- **Hot fixes**: Within 24h (critical bugs)

### Version Numbering:

```
v1.0.0      - Stable release
v1.0.0rc1   - Release candidate
v1.0.0b2    - Beta release
v1.0.0a1    - Alpha release
v1.0.1      - Patch release
v1.1.0      - Minor release (new features)
v2.0.0      - Major release (breaking changes)
```

---

## 📞 Pre-Release Review

### Questions to Ask:

1. **Would I use this version in production?**
   - Beta: Maybe not, but for testing yes
   - Stable: Yes, confidently

2. **Are there any known critical bugs?**
   - If yes → Don't release stable
   - Document in release notes

3. **Is documentation complete?**
   - Users should be able to install and use
   - No missing instructions

4. **Have we tested enough?**
   - Beta: Basic functionality
   - Stable: Comprehensive testing

5. **Are we proud of this release?**
   - Quality reflects on the project
   - Don't rush!

---

## ✅ Sign-Off

**Release Manager**: [Your Name]  
**Date**: [Release Date]  
**Version**: [Version Number]  
**Status**: [Ready/Not Ready]

**Notes**:
- [ ] All checklists complete
- [ ] No blockers identified  
- [ ] Team reviewed (if applicable)
- [ ] Ready to tag and release

---

**Better to delay a release than to ship broken code!** 🛡️

Use this checklist for **every** release - no exceptions!

