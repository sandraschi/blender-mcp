# Megatest Quick Reference
## Run the Right Test Level for Your Needs

## ⚡ Quick Decision Matrix

| Scenario | Level | Time | Command |
|----------|-------|------|---------|
| **Pre-commit check** | Smoke | 2 min | `pytest tests/megatest/ -m megatest_smoke` |
| **Before PR** | Standard | 10 min | `pytest tests/megatest/ -m megatest_standard` |
| **Weekly validation** | Advanced | 20 min | `pytest tests/megatest/ -m megatest_advanced` |
| **Before minor release** | Integration | 45 min | `pytest tests/megatest/ -m megatest_integration` |
| **Before stable release** | Full Blast | 90 min | `pytest tests/megatest/ -m megatest_full` |

## 📋 Test Levels Explained

### Level 1: Smoke Test (2 minutes) ⚡

**Quick & Dirty - Just the essentials!**

```bash
pytest tests/megatest/ -v -m megatest_smoke
```

**What it tests**:
- ✅ System initializes (cold start)
- ✅ Create 10 simple notes
- ✅ Read notes back
- ✅ Search works (5 queries)
- ✅ Delete works
- ✅ No crashes

**What it SKIPS**:
- ❌ No exports
- ❌ No imports
- ❌ No multi-project
- ❌ No edge cases
- ❌ No stress testing

**Use when**:
- Quick sanity check
- Pre-commit validation
- Rapid development cycle
- CI fast path

**Output**:
```
🟢 SMOKE TEST: PASSED (2m 15s)
✅ Basic CRUD works
✅ Search works
✅ No crashes
✅ Production data: SAFE
```

---

### Level 2: Standard Test (10 minutes) 🔧

**Covers core functionality**

```bash
pytest tests/megatest/ -v -m megatest_standard
```

**What it tests**:
- ✅ All Level 1 operations
- ✅ Create 30 notes (simple + complex)
- ✅ Multi-project operations (3 projects)
- ✅ All CRUD operations
- ✅ Tag operations (add, remove, search)
- ✅ Basic search (20 queries)
- ✅ Basic edge cases (malformed files)

**What it SKIPS**:
- ❌ No exports
- ❌ No imports
- ❌ No stress testing
- ❌ Limited edge cases

**Use when**:
- Before creating PR
- Feature development
- Daily validation
- Regression check

**Output**:
```
🟢 STANDARD TEST: PASSED (10m 32s)
✅ Multi-project: 3 projects OK
✅ CRUD: 100/100 operations
✅ Search: 20/20 queries
✅ Tags: All operations OK
✅ Production data: SAFE
```

---

### Level 3: Advanced Test (20 minutes) 🚀

**Advanced features and performance**

```bash
pytest tests/megatest/ -v -m megatest_advanced
```

**What it tests**:
- ✅ All Level 2 operations
- ✅ Create 60 notes (varied complexity)
- ✅ Advanced search (50 queries: boolean, phrases, filters)
- ✅ Knowledge graph traversal
- ✅ Relationship navigation (depth=3)
- ✅ Context building (memory:// URLs)
- ✅ Performance metrics (response times)
- ✅ Extended edge cases (large files, special chars)

**What it SKIPS**:
- ❌ No exports (yet)
- ❌ No imports (yet)
- ❌ No stress testing

**Use when**:
- Weekly validation
- Performance benchmarking
- Advanced feature development
- Pre-minor-release

**Output**:
```
🟢 ADVANCED TEST: PASSED (20m 18s)
✅ Advanced search: 50/50 queries (avg 42ms)
✅ Knowledge graph: 30 traversals OK
✅ Performance: All within limits
✅ Edge cases: 20/20 handled
✅ Production data: SAFE
```

---

### Level 4: Integration Test (45 minutes) 📦

**Import/Export ecosystem validation**

```bash
pytest tests/megatest/ -v -m megatest_integration
```

**What it tests**:
- ✅ All Level 3 operations
- ✅ Create 80 notes
- ✅ **Export Testing**:
  - Docsify basic (validate structure)
  - Docsify enhanced (validate plugins)
  - HTML export (validate standalone)
  - Joplin export (validate metadata)
  - Pandoc PDF export
  - Pandoc DOCX export
  - Archive export (full backup)
- ✅ **Import Testing**:
  - Obsidian vault import
  - Joplin export import
  - Notion HTML import
  - Evernote ENEX import
  - Archive restore
- ✅ **Round-trip Testing**:
  - Export → Import → Verify integrity

**What it SKIPS**:
- ❌ No Docsify site validation (files only)
- ❌ No HTML browsing validation
- ❌ No stress testing

**Use when**:
- Before major releases
- Integration validation
- Data portability testing
- Monthly comprehensive check

**Output**:
```
🟢 INTEGRATION TEST: PASSED (45m 12s)
✅ Exports: 7/7 formats working
   • Docsify basic: 80 notes exported
   • Docsify enhanced: Plugins verified
   • HTML: Standalone site created
   • Joplin: Metadata preserved
   • Pandoc PDF: 80 notes → 45 pages
   • Pandoc DOCX: All formatting OK
   • Archive: 2.3MB backup created
✅ Imports: 5/5 sources working
   • Obsidian: 50 notes imported
   • Joplin: 40 notes imported
   • Notion: 30 notes imported
   • Evernote: 25 notes imported
   • Archive: 80 notes restored
✅ Round-trip: 100% data integrity
✅ Production data: SAFE
```

---

### Level 5: Full Blast (90 minutes) 💥

**Complete system certification**

```bash
pytest tests/megatest/ -v -m megatest_full
```

**What it tests**:
- ✅ All Level 4 operations
- ✅ Create 100+ notes (all types)
- ✅ All edge cases (30 scenarios)
- ✅ Stress testing (1000+ operations)
- ✅ **Working Docsify Site**:
  - Export Docsify enhanced
  - Validate index.html structure
  - Validate _sidebar.md navigation
  - Validate README.md content
  - **Start local server (npx docsify serve)**
  - **Validate site loads in browser**
  - **Validate navigation works**
  - **Validate search plugin works**
  - **Validate theme toggle works**
  - Screenshot success
- ✅ **Working HTML Site**:
  - Export HTML notes
  - Validate index.html
  - **Open in browser**
  - **Validate all links work**
  - **Validate images display**
  - **Validate tables render**
  - Screenshot success
- ✅ Long-running operations
- ✅ Resource exhaustion
- ✅ Concurrent operations
- ✅ Complete analysis

**Use when**:
- Before stable releases
- Monthly certification
- Pre-production deployment
- Complete system validation

**Output**:
```
🟢 FULL BLAST: PASSED (90m 45s)

📊 Comprehensive Results:
✅ Notes: 100+ created, all types
✅ Operations: 1500+ total
✅ Success rate: 98.7%
✅ Crashes: 0
✅ Hangs: 0

✅ Exports: 7/7 formats
   • Docsify Enhanced: ✅ WORKING SITE
     - index.html: Valid HTML5
     - Sidebar: 100 entries
     - Plugins: 6 active (pagination, TOC, theme, etc.)
     - Local server: Started on port 3000
     - Browser test: ✅ PASSED
     - Navigation: ✅ WORKING
     - Search: ✅ WORKING
     - Theme toggle: ✅ WORKING
     - Screenshot: saved to artifacts/
   
   • HTML Site: ✅ WORKING SITE
     - index.html: Valid
     - 100 note pages generated
     - Browser test: ✅ PASSED
     - All links: ✅ WORKING
     - Images: ✅ DISPLAYED
     - Tables: ✅ RENDERED
     - Screenshot: saved to artifacts/

   • Other exports: All validated

✅ Imports: 5/5 sources
✅ Round-trip: 100% integrity
✅ Stress test: 1000 ops/min
✅ Edge cases: 30/30 handled
✅ Performance: All within limits

✅ Production data: VERIFIED SAFE
   • DB checksum: UNCHANGED
   • MD folder: UNCHANGED
   • File count: UNCHANGED

📈 Grade: A+ (System is PRODUCTION READY)
```

---

## 🎯 Level Selection Guide

### When to Run Each Level

#### Daily Development
```bash
# After code changes
pytest tests/megatest/ -m megatest_smoke  # 2 min
```

#### Before PR
```bash
# Comprehensive pre-PR check
pytest tests/megatest/ -m megatest_standard  # 10 min
```

#### Weekly
```bash
# Weekly validation
pytest tests/megatest/ -m megatest_advanced  # 20 min
```

#### Before Releases
```bash
# Minor release (v0.x.1)
pytest tests/megatest/ -m megatest_integration  # 45 min

# Major release (v1.0.0)
pytest tests/megatest/ -m megatest_full  # 90 min
```

---

## 🏗️ Test Organization

### Directory Structure
```
tests/megatest/
├── __init__.py                    # Level documentation
├── conftest.py                    # Safety fixtures (ALL levels)
│
├── level1_smoke/                  # 2 minutes ⚡
│   ├── test_smoke_crud.py         # Basic operations
│   └── test_smoke_search.py       # Basic search
│
├── level2_standard/               # 10 minutes 🔧
│   ├── test_standard_crud.py      # All CRUD
│   ├── test_standard_projects.py  # Multi-project
│   ├── test_standard_tags.py      # Tag operations
│   └── test_standard_search.py    # Standard search
│
├── level3_advanced/               # 20 minutes 🚀
│   ├── test_advanced_search.py    # Advanced queries
│   ├── test_advanced_graph.py     # Knowledge graph
│   ├── test_advanced_context.py   # Context building
│   ├── test_advanced_performance.py # Metrics
│   └── test_advanced_edge_cases.py  # Edge cases
│
├── level4_integration/            # 45 minutes 📦
│   ├── test_export_docsify.py     # Docsify exports
│   ├── test_export_html.py        # HTML exports
│   ├── test_export_joplin.py      # Joplin exports
│   ├── test_export_pandoc.py      # Pandoc exports
│   ├── test_export_archive.py     # Archive exports
│   ├── test_import_obsidian.py    # Obsidian import
│   ├── test_import_joplin.py      # Joplin import
│   ├── test_import_notion.py      # Notion import
│   ├── test_import_evernote.py    # Evernote import
│   ├── test_import_archive.py     # Archive restore
│   └── test_roundtrip.py          # Export → Import integrity
│
├── level5_full/                   # 90 minutes 💥
│   ├── test_full_stress.py        # High volume
│   ├── test_full_edge_cases.py    # All edge cases
│   ├── test_full_concurrent.py    # Concurrent ops
│   ├── test_full_docsify_site.py  # ✨ Working Docsify validation
│   ├── test_full_html_site.py     # ✨ Working HTML validation
│   └── test_full_analysis.py      # Final report
│
├── shared/                        # Shared utilities
│   ├── generators.py              # Synthetic data
│   ├── validators.py              # Integrity checks
│   ├── metrics.py                 # Performance tracking
│   └── reporters.py               # Report generation
│
└── artifacts/                     # Test outputs (gitignored)
    ├── screenshots/               # Site screenshots
    ├── exports/                   # Export test outputs
    └── reports/                   # HTML/JSON reports
```

---

## 🚀 Example: Level 5 Docsify Site Validation

```python
@pytest.mark.megatest_full
@pytest.mark.timeout(600)  # 10 min max
async def test_working_docsify_site(megatest_context, assert_production_safe):
    """
    Level 5: Validate a fully functional Docsify site.
    
    Tests that exported Docsify site:
    - Has valid HTML structure
    - Can be served locally
    - Loads in browser
    - Navigation works
    - Search works
    - Plugins active
    """
    # SAFETY: Verify test environment
    assert_production_safe(megatest_context.test_dir)
    
    # Create test notes
    notes = await megatest_context.create_notes(count=50, complexity="varied")
    
    # Export to Docsify (enhanced)
    export_path = megatest_context.test_dir / "docsify_export"
    result = await megatest_context.export_docsify_enhanced(
        export_path=str(export_path),
        enable_all_plugins=True
    )
    
    # Validate file structure
    assert (export_path / "index.html").exists()
    assert (export_path / "_sidebar.md").exists()
    assert (export_path / "README.md").exists()
    
    # Validate HTML structure
    html_content = (export_path / "index.html").read_text()
    assert "<!DOCTYPE html>" in html_content
    assert "docsify" in html_content.lower()
    assert "search" in html_content.lower()
    
    # Validate plugins configured
    assert "docsify-pagination" in html_content
    assert "docsify-themeable" in html_content
    assert "docsify-copy-code" in html_content
    
    # Start local Docsify server
    import subprocess
    server = subprocess.Popen(
        ["npx", "-y", "docsify-cli", "serve", str(export_path), "-p", "3000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for server to start
        import time
        time.sleep(5)
        
        # Test site loads
        import requests
        response = requests.get("http://localhost:3000")
        assert response.status_code == 200
        assert "Docsify" in response.text
        
        # Test navigation works (check sidebar)
        assert "sidebar" in response.text.lower()
        
        # Test search endpoint exists
        search_response = requests.get("http://localhost:3000/#/?id=search")
        assert search_response.status_code == 200
        
        # Take screenshot (if running in headless browser mode)
        screenshot_path = take_screenshot("http://localhost:3000", 
                                         megatest_context.artifacts_dir / "docsify_working.png")
        
        print(f"✅ Docsify site WORKING: http://localhost:3000")
        print(f"✅ Screenshot saved: {screenshot_path}")
        
    finally:
        # Stop server
        server.terminate()
        server.wait(timeout=5)
    
    # FINAL VALIDATION
    assert result.success == True
    assert result.notes_exported == 50
    print("✅ Full Docsify site validation: PASSED")
```

---

## 🎯 CI Integration

### Fast CI (Every Push)
```yaml
# .github/workflows/ci.yml
- name: Smoke Test
  run: pytest tests/megatest/ -v -m megatest_smoke
  timeout-minutes: 5
```

### Nightly CI
```yaml
# .github/workflows/nightly.yml
- name: Standard Test
  run: pytest tests/megatest/ -v -m megatest_standard
  timeout-minutes: 15
```

### Weekly CI
```yaml
# .github/workflows/weekly.yml
- name: Full Blast Test
  run: pytest tests/megatest/ -v -m megatest_full
  timeout-minutes: 120
```

### Pre-Release CI
```yaml
# .github/workflows/release.yml
- name: Integration Test
  run: pytest tests/megatest/ -v -m megatest_integration
  timeout-minutes: 60
```

---

## 📊 Feature Coverage by Level

| Feature | L1 | L2 | L3 | L4 | L5 |
|---------|----|----|----|----|-----|
| **Basic CRUD** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Multi-project** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Tag operations** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Advanced search** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Knowledge graph** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Export formats** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Import formats** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Working sites** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Stress testing** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Edge cases** | 5 | 10 | 20 | 25 | 30 |
| **Time** | 2m | 10m | 20m | 45m | 90m |
| **Coverage** | 20% | 40% | 60% | 80% | 100% |

---

## 💡 Tips for Efficient Testing

### During Development
```bash
# Run only what you changed
pytest tests/megatest/level1_smoke/test_smoke_crud.py -v

# Quick feedback loop
pytest tests/megatest/ -m megatest_smoke --maxfail=1
```

### Before Committing
```bash
# Standard validation (10 min)
pytest tests/megatest/ -m megatest_standard
```

### Before Releasing
```bash
# Full validation (90 min)
# Run this on Friday afternoon, review Monday morning
pytest tests/megatest/ -m megatest_full --tb=short --durations=20
```

---

## 🔒 Safety Reminder

**ALL LEVELS USE ISOLATED TEST ENVIRONMENT**

No matter which level you run:
- ✅ Test data in `/tmp/megatest_*/`
- ✅ Separate test database
- ✅ Production data PROTECTED
- ✅ Checksum verified
- ✅ Auto-cleanup after test

**Your production data is safe at EVERY level!** 🛡️

---

## 🎉 Summary

### Choose Your Level

**Need speed?** → Level 1 (2 min)
**Need confidence?** → Level 2 (10 min)
**Need performance data?** → Level 3 (20 min)
**Need export/import validation?** → Level 4 (45 min)
**Need complete certification?** → Level 5 (90 min)

### Progressive Enhancement
```
L1 → L2 → L3 → L4 → L5
 ↓     ↓     ↓     ↓     ↓
Quick Core Advanced I/O  Full
```

Each level builds on the previous, adding more features and coverage.

**Run the level that matches your timeline and needs!** ⚡🚀💥

---

*Quick reference created: October 15, 2025*
*All levels: ISOLATED and SAFE*
*Choose wisely, test confidently!*

