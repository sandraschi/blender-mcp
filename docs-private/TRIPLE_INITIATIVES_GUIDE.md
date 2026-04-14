# Triple Initiatives - Improvement Plan for blender-mcp

**Part of:** Great Doc Bash + GitHub Dash + Release Flash  
**Started:** 2025-10-21  
**Status:** Tier 1 batch work complete, Tier 2 pending  
**Priority:** MEDIUM

---

## 🎯 What Are The Triple Initiatives?

**Three parallel improvement initiatives running across 15 high-priority repos:**

**1. Great Doc Bash** (Documentation Quality)
- Goal: World-class documentation (9.0+/10 average)
- Current baseline: 8.1/10 average
- Your repo: 8/10

**2. GitHub Dash** (CI/CD Modernization)
- Goal: Modern, spam-free CI/CD (8.0+/10 average)
- Current baseline: 5.9/10 average
- Your repo: 8/10

**3. Release Flash** (Successful Releases)
- Goal: All repos successfully releasing with zero errors
- Your repo: 7/10

---

## 📋 Improvement Plan for blender-mcp

### ✅ TIER 1 - Batch Work (Already Done or In Progress)

**These improvements can be done WITHOUT opening this repo in Cursor:**

- [x] docs-private/ folder created
- [x] .gitignore updated
- [x] CHANGELOG.md created (if missing)
- [x] Dependabot disabled (if present)
- [ ] ci.yml template applied (if simple)
- [ ] Standard .gitignore additions

**Status:** Mostly complete (Day 1)

---

### ⚠️ TIER 2 - Deep Work (REQUIRES Opening This Repo)

**These improvements NEED full context - must open this repo in Cursor:**

- [ ] FastMCP 2.10 → 2.12 upgrade
- [ ] Review PyPI necessity
- [ ] Specialized blender docs

**Why full context needed:**
- Need <project_layout> tag to see full structure
- Need to understand import relationships
- Need real-time linter/type checker feedback
- Need to trace through code for complex fixes
- Need comprehensive understanding before refactoring

**Status:** Waiting for dedicated Cursor instance

---

## 🚀 How To Work on This Repo

### Option 1: Quick Batch Improvements (Any Time)

**From any Cursor workspace:**
```powershell
cd D:\Dev\repos\blender-mcp
# Run simple operations
# Commit changes
```

**Suitable for:**
- Simple file updates
- Template application
- Mechanical operations

---

### Option 2: Deep Improvements (RECOMMENDED)

**Open this repo in its own Cursor instance:**

1. **File → Open Folder** → `D:\Dev\repos\blender-mcp`
2. Wait for project layout to load
3. Execute ALL THREE initiatives in one session:
   - **Doc Bash:** Upgrade docs, fix issues
   - **GitHub Dash:** Modernize CI/CD
   - **Release Flash:** Fix errors, test, release
4. Test thoroughly (ruff, pytest, workflows)
5. Commit all changes
6. Create release tag if ready
7. Close folder

**Time estimate:** 2-4 hours for complete improvement

---

## 🎯 CRITICAL Priority Actions

- FastMCP 2.12 upgrade
- Specialized docs

---

## 📝 Notes

**Cursor Instance Management:**
- You can have ~5 Cursor instances open simultaneously 😄
- Recommend: 1-2 for deep work, keep one for batch operations
- Close instances when done to free resources

**Session Strategy:**
- Morning: Batch work across repos (stay in current workspace)
- Afternoon: Deep work on 1-2 priority repos (open dedicated instances)
- Evening: Track progress, plan next session

**Tracking:**
- All progress tracked in: `D:\Dev\repos\mcp-central-docs`
- Advanced Memory notes for each initiative
- Per-repo STATUS.md files in central docs

---

## 🔗 References

- mcp-central-docs/great-doc-bash/DOC_BASH_PLAN.md
- mcp-central-docs/great-doc-bash/GITHUB_DASH_PLAN.md
- mcp-central-docs/great-doc-bash/RELEASE_FLASH_PLAN.md
- mcp-central-docs/great-doc-bash/COMBINED_PROGRESS.md
- mcp-central-docs/docs-private/CURSOR_WORKFLOW_STRATEGY.md
- Advanced Memory: "Great Doc Bash - Multi-Repo Documentation Improvement Initiative"
- Advanced Memory: "GitHub Dash - CI/CD Modernization Initiative"
- Advanced Memory: "Release Flash - Successful Releases Initiative"

---

**Last Updated:** 2025-10-21 (Day 1)  
**Next Review:** After completing Tier 2 improvements
