# Megatest Location and Cleanup Strategies
## Flexible Test Environment Placement and Artifact Management

## 🎯 Overview

Megatest supports **flexible test location** and **configurable cleanup** strategies to balance:
- **Transparency** vs **Cleanliness**
- **Debugging** vs **Disk space**
- **Visibility** vs **Hidden**
- **Ephemeral** vs **Archival**

## 📍 Test Location Strategies

### Strategy 1: Hidden (AppData/Temp) - DEFAULT

**Location**: System temp or AppData (tucked away)

**Paths by OS**:
- **Windows**: `C:\Users\{user}\AppData\Local\Temp\megatest_*\`
- **macOS**: `/var/folders/.../T/megatest_*/`
- **Linux**: `/tmp/megatest_*/`

**Pros**:
- ✅ Automatically cleaned by OS (eventually)
- ✅ Doesn't clutter visible directories
- ✅ Standard practice for tests
- ✅ Fast (temp drives are often fast)

**Cons**:
- ⚠️ Hard to find for debugging
- ⚠️ May be deleted unexpectedly
- ⚠️ Not visible to user

**Use when**:
- CI/CD environments
- Automated testing
- Quick validations
- Disposable results

**Configuration**:
```python
# pytest.ini or environment variable
MEGATEST_LOCATION = "hidden"  # or "temp"

# Implementation
if config.location == "hidden":
    test_base = Path(tempfile.gettempdir()) / f"megatest_{timestamp}"
```

---

### Strategy 2: Visible (Documents) - DEBUGGING

**Location**: Documents folder (out and proud)

**Paths by OS**:
- **Windows**: `C:\Users\{user}\Documents\megatest-results\{timestamp}\`
- **macOS**: `~/Documents/megatest-results/{timestamp}/`
- **Linux**: `~/Documents/megatest-results/{timestamp}/`

**Pros**:
- ✅ Easy to find and inspect
- ✅ Persistent across sessions
- ✅ User can browse results
- ✅ Great for debugging

**Cons**:
- ⚠️ Clutters Documents folder
- ⚠️ Manual cleanup required
- ⚠️ Uses visible disk space

**Use when**:
- Debugging test failures
- Inspecting generated artifacts
- Analyzing performance
- Demo/presentation mode

**Configuration**:
```python
# pytest.ini or environment variable
MEGATEST_LOCATION = "visible"  # or "documents"

# Implementation
if config.location == "visible":
    test_base = Path.home() / "Documents" / "megatest-results" / timestamp
```

---

### Strategy 3: Project-Local (Repo) - DEVELOPMENT

**Location**: Within repository (gitignored)

**Paths**:
- `{repo}/test-results/megatest/{timestamp}/`
- Example: `advanced-memory-mcp/test-results/megatest/2025-10-15_14-30-45/`

**Pros**:
- ✅ Easy to find (same directory as code)
- ✅ Gitignored (won't be committed)
- ✅ Project-specific isolation
- ✅ Easy cleanup (delete test-results/)

**Cons**:
- ⚠️ Repo gets large with artifacts
- ⚠️ Need to remember to clean up

**Use when**:
- Local development
- Iterative debugging
- Artifact inspection needed
- CI artifacts (uploaded separately)

**Configuration**:
```python
# pytest.ini or environment variable
MEGATEST_LOCATION = "local"  # or "repo"

# Implementation
if config.location == "local":
    test_base = Path.cwd() / "test-results" / "megatest" / timestamp
```

---

### Strategy 4: Custom Path - ADVANCED

**Location**: User-specified path

**Pros**:
- ✅ Complete control
- ✅ Can use fast drives (SSD)
- ✅ Can use network shares
- ✅ Can use dedicated test volumes

**Use when**:
- Performance critical (use SSD)
- Network testing (use shared storage)
- Custom workflow requirements

**Configuration**:
```python
# Environment variable or CLI arg
MEGATEST_LOCATION = "/mnt/fast-ssd/megatest"

# pytest command
pytest tests/megatest/ -m megatest_smoke --megatest-dir="/custom/path"
```

---

## 🗑️ Cleanup Strategies

### Strategy A: Immediate Teardown - DEFAULT

**Behavior**: Delete all test data immediately after test completes

**When it happens**:
- Success: Delete after test passes
- Failure: Delete after test fails (unless configured otherwise)

**Pros**:
- ✅ No disk clutter
- ✅ Clean environment every run
- ✅ No manual cleanup needed
- ✅ CI-friendly

**Cons**:
- ⚠️ Can't inspect artifacts after success
- ⚠️ Debugging requires re-run

**Configuration**:
```python
# pytest.ini
MEGATEST_CLEANUP = "immediate"  # or "always"


# Implementation
@pytest.fixture(scope="module")
def isolated_test_env():
    test_dir = create_test_dir()
    yield {"test_dir": test_dir}

    # ALWAYS cleanup
    shutil.rmtree(test_dir)
    print(f"✅ Cleaned up: {test_dir}")
```

**Use when**:
- CI/CD runs
- Quick validations
- Disk space limited
- Standard testing

---

### Strategy B: Keep on Failure - DEBUGGING

**Behavior**: Delete on success, **keep on failure**

**When it happens**:
- Success: Delete (clean)
- Failure: **Keep for inspection**

**Pros**:
- ✅ Clean on success (no clutter)
- ✅ Artifacts preserved on failure (debugging)
- ✅ Automatic (smart decision)
- ✅ Best of both worlds

**Cons**:
- ⚠️ Disk space grows with failures
- ⚠️ Manual cleanup eventually needed

**Configuration**:
```python
# pytest.ini
MEGATEST_CLEANUP = "on-success"  # or "keep-on-failure"


# Implementation
@pytest.fixture(scope="module")
def isolated_test_env(request):
    test_dir = create_test_dir()
    yield {"test_dir": test_dir}

    # Cleanup only if test passed
    if request.session.testsfailed == 0:
        shutil.rmtree(test_dir)
        print(f"✅ Test passed - cleaned up: {test_dir}")
    else:
        print(f"⚠️  Test failed - kept for debugging: {test_dir}")
```

**Use when**:
- Development
- Debugging test failures
- Iterative testing
- Need to inspect failures

---

### Strategy C: Archive with Timestamps - HISTORICAL

**Behavior**: Keep all test runs with timestamps for historical analysis

**Directory structure**:
```
~/Documents/megatest-results/
├── 2025-10-15_09-30-45_smoke_PASS/
│   ├── test_data/
│   ├── artifacts/
│   └── report.html
├── 2025-10-15_10-15-22_standard_PASS/
│   ├── test_data/
│   ├── artifacts/
│   └── report.html
├── 2025-10-15_14-45-10_full_FAIL/
│   ├── test_data/
│   ├── artifacts/
│   ├── report.html
│   └── error.log
└── archive_manifest.json
```

**Pros**:
- ✅ Complete history of all runs
- ✅ Compare results over time
- ✅ Trend analysis possible
- ✅ Debugging historical issues
- ✅ Audit trail

**Cons**:
- ⚠️ Disk space grows continuously
- ⚠️ Manual cleanup needed eventually
- ⚠️ Can accumulate gigabytes

**Configuration**:
```python
# pytest.ini
MEGATEST_CLEANUP = "archive"  # or "never"


# Implementation
@pytest.fixture(scope="module")
def isolated_test_env(request):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    test_level = get_test_level(request)  # smoke, standard, etc.

    # Create timestamped directory
    archive_base = Path.home() / "Documents" / "megatest-results"
    archive_base.mkdir(parents=True, exist_ok=True)

    # Will be renamed with status after test
    test_dir = archive_base / f"{timestamp}_{test_level}_RUNNING"
    test_dir.mkdir()

    yield {"test_dir": test_dir, "timestamp": timestamp, "level": test_level}

    # Rename with final status
    if request.session.testsfailed == 0:
        final_dir = archive_base / f"{timestamp}_{test_level}_PASS"
    else:
        final_dir = archive_base / f"{timestamp}_{test_level}_FAIL"

    test_dir.rename(final_dir)
    print(f"📦 Archived: {final_dir}")

    # Update manifest
    update_archive_manifest(
        archive_base,
        {
            "timestamp": timestamp,
            "level": test_level,
            "status": "PASS" if request.session.testsfailed == 0 else "FAIL",
            "path": str(final_dir),
        },
    )
```

**Use when**:
- Performance trend analysis
- Historical debugging
- Quality metrics collection
- Compliance/audit requirements

---

### Strategy D: Smart Archive - RECOMMENDED

**Behavior**: Keep recent and important runs, auto-delete old ones

**Rules**:
- ✅ Keep last 5 runs of each level
- ✅ Keep all failures (for debugging)
- ✅ Keep all Level 5 (full blast) runs
- ✅ Delete old Level 1-2 runs after 7 days
- ✅ Keep monthly snapshots (first run each month)

**Directory structure**:
```
~/Documents/megatest-results/
├── 2025-10-15_smoke_PASS/          (kept: recent)
├── 2025-10-14_smoke_PASS/          (kept: recent)
├── 2025-10-13_standard_FAIL/       (kept: failure)
├── 2025-10-10_full_PASS/           (kept: level 5)
├── 2025-10-01_full_PASS/           (kept: monthly snapshot)
└── archive_manifest.json

Deleted automatically:
- 2025-10-01_smoke_PASS/  (old, level 1)
- 2025-09-28_standard_PASS/  (old, level 2)
```

**Configuration**:
```python
# pytest.ini
MEGATEST_CLEANUP = "smart-archive"
MEGATEST_KEEP_RECENT = 5
MEGATEST_KEEP_FAILURES = "all"
MEGATEST_KEEP_FULL_BLAST = "all"
MEGATEST_AUTO_DELETE_DAYS = 7


# Implementation (automatic pruning)
def prune_old_archives(archive_dir, config):
    """Smart cleanup of old test runs."""
    manifest = load_archive_manifest(archive_dir)

    # Keep all failures
    # Keep last N runs of each level
    # Keep all Level 5 runs
    # Delete old Level 1-2 runs after X days

    for entry in manifest:
        if should_delete(entry, config):
            shutil.rmtree(entry["path"])
            print(f"🗑️  Pruned old archive: {entry['path']}")
```

**Use when**:
- Production environments
- Long-term testing
- Performance tracking
- Balance disk space vs history

---

## 🔧 Configuration Options

### Environment Variables
```bash
# Location
export MEGATEST_LOCATION="hidden"      # temp directory
export MEGATEST_LOCATION="visible"     # Documents folder
export MEGATEST_LOCATION="local"       # repo/test-results/
export MEGATEST_LOCATION="/custom/path"  # custom location

# Cleanup
export MEGATEST_CLEANUP="immediate"    # delete after run
export MEGATEST_CLEANUP="on-success"   # keep on failure
export MEGATEST_CLEANUP="archive"      # keep all with timestamps
export MEGATEST_CLEANUP="smart-archive"  # intelligent pruning
```

### pytest.ini Configuration
```ini
[pytest]
env =
    MEGATEST_LOCATION=hidden
    MEGATEST_CLEANUP=on-success
    MEGATEST_KEEP_RECENT=5
    MEGATEST_KEEP_FAILURES=all
    MEGATEST_AUTO_DELETE_DAYS=7
```

### Command-Line Override
```bash
# Override location for one run
pytest tests/megatest/ -m megatest_smoke --megatest-location=visible

# Override cleanup for debugging
pytest tests/megatest/ -m megatest_full --megatest-cleanup=archive

# Custom path for fast SSD
pytest tests/megatest/ -m megatest_full --megatest-dir="/mnt/ssd/megatest"
```

---

## 📊 Location Comparison Matrix

| Strategy | Path | Visibility | Auto-Cleanup | Best For |
|----------|------|------------|--------------|----------|
| **Hidden** | AppData/Temp | Hidden | OS-managed | CI/CD, Quick tests |
| **Visible** | Documents | Visible | Manual | Debugging, Demos |
| **Local** | Repo/test-results | Visible | Manual | Development |
| **Custom** | User-specified | Varies | Varies | Performance, Special needs |

## 🗑️ Cleanup Comparison Matrix

| Strategy | On Success | On Failure | Disk Usage | Best For |
|----------|------------|------------|------------|----------|
| **Immediate** | Delete | Delete | Minimal | CI/CD, Production |
| **On-Success** | Delete | Keep | Low | Development, Debugging |
| **Archive** | Keep | Keep | High | Analysis, Compliance |
| **Smart Archive** | Prune old | Keep recent | Medium | Long-term, Production |

---

## 🎯 Recommended Configurations

### For CI/CD
```python
location = "hidden"  # Use temp directory
cleanup = "immediate"  # Always clean up
artifacts_upload = True  # Upload to GitHub Actions
```

**Result**: Fast, clean, artifacts preserved in CI

---

### For Local Development
```python
location = "local"  # Repo/test-results/
cleanup = "on-success"  # Keep failures for debugging
artifacts_upload = False  # Local inspection only
```

**Result**: Easy debugging, minimal clutter

---

### For Release Validation
```python
location = "visible"  # Documents/megatest-results/
cleanup = "archive"  # Keep all runs
artifacts_upload = True  # Upload for record
generate_report = True  # HTML report with screenshots
```

**Result**: Complete historical record, full transparency

---

### For Performance Benchmarking
```python
location = "custom"  # /mnt/ssd/megatest
cleanup = "smart-archive"  # Keep trends, prune old
collect_metrics = True  # Performance tracking
retention_days = 30  # Keep last 30 days
```

**Result**: Performance trends tracked, manageable disk usage

---

## 🛠️ Implementation

### Enhanced conftest.py
```python
# tests/megatest/conftest.py
import os
from datetime import datetime
from pathlib import Path
import tempfile


def get_test_location() -> Path:
    """Determine test location based on configuration."""
    location = os.environ.get("MEGATEST_LOCATION", "hidden")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if location == "hidden" or location == "temp":
        # Hidden: System temp directory
        return Path(tempfile.gettempdir()) / f"megatest_{timestamp}"

    elif location == "visible" or location == "documents":
        # Visible: Documents folder
        base = Path.home() / "Documents" / "megatest-results"
        base.mkdir(parents=True, exist_ok=True)
        return base / timestamp

    elif location == "local" or location == "repo":
        # Local: Repository test-results
        base = Path.cwd() / "test-results" / "megatest"
        base.mkdir(parents=True, exist_ok=True)
        return base / timestamp

    else:
        # Custom: User-specified path
        base = Path(location)
        if not base.is_absolute():
            base = Path.cwd() / base
        base.mkdir(parents=True, exist_ok=True)
        return base / timestamp


def get_cleanup_strategy() -> str:
    """Get cleanup strategy from config."""
    return os.environ.get("MEGATEST_CLEANUP", "on-success")


@pytest.fixture(scope="module")
def isolated_test_env(request):
    """Create test environment with configurable location and cleanup."""
    # Determine location
    test_base = get_test_location()
    test_dir = test_base / "test_data"
    test_db = test_base / "test.db"

    # Create directories
    test_dir.mkdir(parents=True, exist_ok=True)

    # CRITICAL: Safety checks (always enforced)
    assert is_safe_test_path(test_base)
    assert not is_production_path(test_base)

    # Display environment
    location_type = os.environ.get("MEGATEST_LOCATION", "hidden")
    cleanup_type = get_cleanup_strategy()

    print(f"""
╔══════════════════════════════════════════════════════════╗
║          MEGATEST ENVIRONMENT - ISOLATED                 ║
╠══════════════════════════════════════════════════════════╣
║ Location: {location_type.upper():<45} ║
║ Cleanup:  {cleanup_type.upper():<45} ║
║                                                          ║
║ Test Dir: {str(test_base):<45} ║
║                                                          ║
║ Status: ✅ ISOLATED - Safe to proceed                    ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Store checksum of production data (if exists)
    prod_checksum = store_production_checksum()

    # Yield test environment
    yield {
        "test_dir": test_dir,
        "test_db": test_db,
        "test_base": test_base,
        "timestamp": test_base.name,
    }

    # Determine cleanup action
    cleanup_strategy = get_cleanup_strategy()
    test_failed = request.session.testsfailed > 0

    if cleanup_strategy == "immediate":
        # Always delete
        shutil.rmtree(test_base)
        print(f"✅ Cleaned up: {test_base}")

    elif cleanup_strategy == "on-success":
        # Delete on success, keep on failure
        if not test_failed:
            shutil.rmtree(test_base)
            print(f"✅ Test passed - cleaned up: {test_base}")
        else:
            print(f"⚠️  Test failed - kept for debugging: {test_base}")

    elif cleanup_strategy == "archive":
        # Keep all runs
        # Rename with status
        status = "PASS" if not test_failed else "FAIL"
        final_name = f"{test_base.name}_{status}"
        final_path = test_base.parent / final_name
        test_base.rename(final_path)
        print(f"📦 Archived: {final_path}")

    elif cleanup_strategy == "smart-archive":
        # Keep with smart pruning
        archive_with_pruning(test_base, test_failed)

    # CRITICAL: Verify production untouched
    verify_production_checksum(prod_checksum)
    print("✅ Production data verified: UNTOUCHED")
```

---

## 📁 Directory Structure Examples

### Hidden (Temp) - After Run
```
# Nothing visible! Cleaned up automatically
# (or managed by OS temp cleanup)
```

### Visible (Documents) - After Runs
```
~/Documents/megatest-results/
├── 2025-10-15_09-30-45_smoke_PASS/
│   ├── test_data/
│   │   ├── test_personal/
│   │   │   ├── note1.md
│   │   │   └── note2.md
│   │   └── test.db
│   ├── artifacts/
│   │   ├── docsify_export/
│   │   ├── html_export/
│   │   └── screenshots/
│   └── megatest_report.html
│
├── 2025-10-15_14-30-00_full_PASS/
│   ├── test_data/ (100+ notes)
│   ├── artifacts/
│   │   ├── docsify_export/ (working site)
│   │   ├── html_export/ (working site)
│   │   ├── screenshots/
│   │   │   ├── docsify_homepage.png
│   │   │   ├── docsify_search.png
│   │   │   ├── html_index.png
│   │   │   └── html_navigation.png
│   │   └── performance_metrics.json
│   └── megatest_report.html
│
└── archive_manifest.json
```

**Manifest**:
```json
{
  "runs": [
    {
      "timestamp": "2025-10-15_09-30-45",
      "level": "smoke",
      "status": "PASS",
      "duration_seconds": 125,
      "tests_run": 10,
      "tests_passed": 10,
      "artifacts_size_mb": 2.3
    },
    {
      "timestamp": "2025-10-15_14-30-00",
      "level": "full",
      "status": "PASS",
      "duration_seconds": 5420,
      "tests_run": 150,
      "tests_passed": 150,
      "artifacts_size_mb": 145.7
    }
  ]
}
```

### Local (Repo) - Gitignored
```
advanced-memory-mcp/
├── .gitignore  (includes test-results/)
├── test-results/
│   └── megatest/
│       ├── 2025-10-15_09-30-45/
│       └── 2025-10-15_14-30-00/
└── (rest of repo)

# .gitignore
test-results/
megatest-results/
```

---

## 🎯 Usage Examples

### Quick Development Check (Hidden + Immediate)
```bash
# Fast, clean, disposable
export MEGATEST_LOCATION=hidden
export MEGATEST_CLEANUP=immediate
pytest tests/megatest/ -m megatest_smoke

# Result: Test runs, completes, disappears
# Time: 2 min total
```

### Debugging Failed Test (Visible + Keep on Failure)
```bash
# Debug-friendly
export MEGATEST_LOCATION=visible
export MEGATEST_CLEANUP=on-success
pytest tests/megatest/ -m megatest_standard

# If test fails:
# → Check ~/Documents/megatest-results/{timestamp}/
# → Inspect artifacts, logs, generated files
```

### Release Validation (Visible + Archive)
```bash
# Complete record
export MEGATEST_LOCATION=visible
export MEGATEST_CLEANUP=archive
pytest tests/megatest/ -m megatest_full

# Result:
# → ~/Documents/megatest-results/2025-10-15_14-30-00_full_PASS/
# → Contains all artifacts, screenshots, reports
# → Permanent record of release validation
```

### CI/CD (Hidden + Immediate + Upload)
```yaml
# .github/workflows/megatest.yml
- name: Run Megatest
  env:
    MEGATEST_LOCATION: hidden
    MEGATEST_CLEANUP: immediate
  run: pytest tests/megatest/ -m megatest_standard

- name: Upload Artifacts (if configured)
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: megatest-results
    path: artifacts/  # Copied before cleanup
```

---

## 📊 Artifact Management

### What to Save (Level 5 Only)

**Always save**:
- ✅ HTML report (megatest_report.html)
- ✅ Performance metrics (metrics.json)
- ✅ Error logs (if any)

**Level 5 specific**:
- ✅ Screenshots (docsify_*.png, html_*.png)
- ✅ Generated exports (docsify_export/, html_export/)
- ✅ Test database (for analysis)

**Optional**:
- Test markdown files (100+ notes)
- Import test data
- Raw logs

### Artifact Compression
```python
# For archive mode, compress old runs
def compress_old_archives(archive_dir, days_old=30):
    """Compress archives older than N days."""
    for run_dir in archive_dir.iterdir():
        age = datetime.now() - get_dir_timestamp(run_dir)
        if age.days > days_old and not run_dir.suffix == ".tar.gz":
            # Compress to tar.gz
            compress_directory(run_dir)
            print(f"📦 Compressed: {run_dir} → {run_dir}.tar.gz")
```

---

## 🎯 Best Practices

### For Quick Development
```python
location = "hidden"  # Tucked away
cleanup = "immediate"  # Clean slate every run
level = "smoke"  # Just 2 minutes
```

### For Iterative Debugging
```python
location = "visible"  # Easy to find
cleanup = "on-success"  # Keep failures
level = "standard"  # Good coverage
```

### For Release Validation
```python
location = "visible"  # Full transparency
cleanup = "archive"  # Permanent record
level = "full"  # Complete validation
generate_screenshots = True  # Visual proof
```

### For Long-Term Monitoring
```python
location = "visible"  # Trackable
cleanup = "smart-archive"  # Intelligent retention
level = "full"  # Weekly/monthly runs
track_trends = True  # Performance over time
```

---

## 📋 Configuration File Example

### megatest.config.json (Optional)
```json
{
  "location": {
    "default": "hidden",
    "ci": "hidden",
    "development": "local",
    "release": "visible"
  },
  "cleanup": {
    "default": "on-success",
    "ci": "immediate",
    "development": "on-success",
    "release": "archive"
  },
  "retention": {
    "keep_recent": 5,
    "keep_failures": "all",
    "keep_full_blast": "all",
    "auto_delete_days": 7,
    "compress_after_days": 30
  },
  "artifacts": {
    "save_screenshots": true,
    "save_exports": true,
    "save_test_data": false,
    "save_logs": true,
    "compress": true
  }
}
```

### Load in conftest.py
```python
def load_megatest_config():
    """Load megatest configuration."""
    config_path = Path("tests/megatest/megatest.config.json")
    if config_path.exists():
        return json.loads(config_path.read_text())
    return DEFAULT_CONFIG
```

---

## 🎉 Summary

### Location Options
1. **Hidden** (AppData/Temp) - Clean, automatic, CI-friendly
2. **Visible** (Documents) - Transparent, debuggable, demo-friendly
3. **Local** (Repo) - Convenient, gitignored, dev-friendly
4. **Custom** - Flexible, performance-optimized, special-use

### Cleanup Options
1. **Immediate** - Always delete, minimal disk, CI-friendly
2. **On-Success** - Smart, keeps failures, debug-friendly
3. **Archive** - Keep all, historical, compliance-friendly
4. **Smart Archive** - Best of both, auto-prune, production-friendly

### Recommended Defaults
```python
# For most users
MEGATEST_LOCATION = "local"  # Repo/test-results/
MEGATEST_CLEANUP = "on-success"  # Keep failures
MEGATEST_KEEP_RECENT = 5  # Last 5 runs
MEGATEST_AUTO_DELETE_DAYS = 7  # Prune after week
```

### Quick Reference
```bash
# Quick & clean (default)
pytest tests/megatest/ -m megatest_smoke

# Debug mode (keep artifacts)
MEGATEST_LOCATION=visible MEGATEST_CLEANUP=archive pytest tests/megatest/ -m megatest_full

# CI mode (fast & clean)
MEGATEST_LOCATION=hidden MEGATEST_CLEANUP=immediate pytest tests/megatest/ -m megatest_standard
```

**Choose your strategy based on needs - flexibility is built in!** 🎯

---

*Location and cleanup guide created: October 15, 2025*
*Flexible by design, safe by default*
*Your testing ground, your choice!*
