"""
MCP Megatest - Universal Testing Framework for Blender MCP
==========================================================

Production-Safe, Multi-Level, Comprehensive Testing Framework

SAFETY GUARANTEES:
- NEVER touches production data
- Isolated test environment
- Multiple safety checks
- Automatic cleanup

USAGE:
    # Smoke test (2 min)
    pytest tests/megatest/ -m megatest_smoke

    # Standard test (10 min)
    pytest tests/megatest/ -m megatest_standard

    # Advanced test (20 min)
    pytest tests/megatest/ -m megatest_advanced

    # Integration test (45 min)
    pytest tests/megatest/ -m megatest_integration

    # Full blast (90 min)
    pytest tests/megatest/ -m megatest_full
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any, Optional
from contextlib import contextmanager


# ===============================================
# SAFETY CONSTANTS - NEVER MODIFY
# ===============================================

PRODUCTION_PATHS = [
    # User's actual Blender MCP data
    Path.home() / ".blender-mcp",
    Path.home() / "Documents" / "blender-mcp",
    Path.home() / "blender-mcp",

    # System paths that should never be touched
    Path("/usr/local/blender-mcp"),
    Path("/opt/blender-mcp"),
    Path("C:\\ProgramData\\blender-mcp"),
]

TEST_ALLOWED_PATHS = [
    Path("test_data"),
    Path("tests"),
    Path(tempfile.gettempdir()),
    Path.cwd() / "megatest_temp",
]


def is_production_path(path: Path) -> bool:
    """Check if a path is in production data directories."""
    path = path.resolve()

    for prod_path in PRODUCTION_PATHS:
        try:
            prod_path = prod_path.resolve()
            if path == prod_path or prod_path in path.parents:
                return True
        except (OSError, RuntimeError):
            continue
    return False


def validate_test_safety(test_base_path: Path) -> None:
    """Validate that test environment is safe (no production data access)."""
    if is_production_path(test_base_path):
        raise RuntimeError(
            f"FATAL SAFETY VIOLATION: Test path {test_base_path} "
            "is in production data directory! "
            "Megatest will NOT proceed."
        )

    # Ensure test path is in allowed locations
    allowed = False
    test_base_path = test_base_path.resolve()

    for allowed_path in TEST_ALLOWED_PATHS:
        try:
            allowed_path = allowed_path.resolve()
            if test_base_path == allowed_path or allowed_path in test_base_path.parents:
                allowed = True
                break
        except (OSError, RuntimeError):
            continue

    if not allowed:
        raise RuntimeError(
            f"FATAL SAFETY VIOLATION: Test path {test_base_path} "
            "is not in allowed test locations! "
            f"Allowed: {TEST_ALLOWED_PATHS}"
        )


# ===============================================
# TEST CONFIGURATION
# ===============================================

class MegatestConfig:
    """Megatest configuration with safety guarantees."""

    def __init__(self):
        # Get location from environment or use default
        location = os.getenv("MEGATEST_LOCATION", "local")

        if location == "local":
            self.base_path = Path.cwd() / "test_data" / "megatest"
        elif location == "temp":
            self.base_path = Path(tempfile.gettempdir()) / "blender_mcp_megatest"
        elif location == "hidden":
            self.base_path = Path(tempfile.gettempdir()) / ".blender_mcp_megatest"
        else:
            self.base_path = Path(location)

        # Validate safety BEFORE any operations
        validate_test_safety(self.base_path)

        # Get cleanup mode
        self.cleanup_mode = os.getenv("MEGATEST_CLEANUP", "on_success")

        # Create base directory
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Test run identifier
        import time
        self.run_id = f"run_{int(time.time())}"

        # Results directory for this run
        self.results_path = self.base_path / "results" / self.run_id
        self.results_path.mkdir(parents=True, exist_ok=True)

    @property
    def database_path(self) -> Path:
        """Get isolated database path."""
        return self.base_path / "db" / f"{self.run_id}.db"

    @property
    def temp_path(self) -> Path:
        """Get temporary files path."""
        return self.base_path / "temp" / self.run_id


# ===============================================
# PYTEST FIXTURES
# ===============================================

@pytest.fixture(scope="session")
def megatest_config() -> MegatestConfig:
    """Provide megatest configuration with safety validation."""
    return MegatestConfig()


@pytest.fixture(scope="session")
def megatest_base_path(megatest_config: MegatestConfig) -> Path:
    """Provide the base test path (validated as safe)."""
    return megatest_config.base_path


@pytest.fixture(scope="session")
def megatest_results_path(megatest_config: MegatestConfig) -> Path:
    """Provide the results path for this test run."""
    return megatest_config.results_path


@pytest.fixture
def safe_temp_dir(megatest_config: MegatestConfig, request) -> Generator[Path, None, None]:
    """Provide a safe temporary directory for individual tests."""
    test_name = getattr(request, 'node', None)
    if test_name:
        test_name = test_name.name
    else:
        test_name = "unknown"
    temp_path = megatest_config.temp_path / f"test_{test_name}"
    temp_path.mkdir(parents=True, exist_ok=True)

    yield temp_path

    # Cleanup based on configuration
    if megatest_config.cleanup_mode == "immediate":
        shutil.rmtree(temp_path, ignore_errors=True)
    # Note: on_success cleanup is handled in pytest_sessionfinish


# ===============================================
# TEST MARKERS
# ===============================================

def pytest_configure(config):
    """Configure pytest with megatest markers."""
    config.addinivalue_line("markers", "megatest_smoke: Quick sanity check (2 min)")
    config.addinivalue_line("markers", "megatest_standard: Core functionality (10 min)")
    config.addinivalue_line("markers", "megatest_advanced: Advanced features (20 min)")
    config.addinivalue_line("markers", "megatest_integration: Multi-tool workflows (45 min)")
    config.addinivalue_line("markers", "megatest_full: Complete validation (90 min)")


# ===============================================
# SAFETY HOOKS
# ===============================================

def pytest_sessionstart(session):
    """Validate safety before any tests run."""
    config = MegatestConfig()

    print("\n🧪 MEGATEST SESSION START")
    print(f"📍 Test Base Path: {config.base_path}")
    print(f"🗂️  Results Path: {config.results_path}")
    print(f"🧹 Cleanup Mode: {config.cleanup_mode}")
    print("✅ SAFETY: Production data protection active")
    # Create safety log
    safety_log = config.results_path / "safety_check.log"
    with open(safety_log, "w") as f:
        f.write("MEGATEST SAFETY CHECK PASSED\n")
        f.write(f"Test Path: {config.base_path}\n")
        f.write(f"Production Paths Checked: {len(PRODUCTION_PATHS)}\n")
        f.write("Status: SAFE TO PROCEED\n")


def pytest_sessionfinish(session, exitstatus):
    """Handle cleanup after tests complete."""
    config = MegatestConfig()

    if config.cleanup_mode == "immediate":
        print("🧹 Cleanup: Already performed during tests")
    elif config.cleanup_mode == "on_success" and exitstatus == 0:
        print("🧹 Cleanup: Removing test data (all tests passed)")
        shutil.rmtree(config.base_path, ignore_errors=True)
    else:
        print(f"🧹 Cleanup: Preserving test data at {config.base_path}")
        print("   (Use MEGATEST_CLEANUP=immediate to auto-clean)")


# ===============================================
# UTILITY FUNCTIONS
# ===============================================

def get_test_level() -> str:
    """Get the current test level from environment."""
    return os.getenv("MEGATEST_LEVEL", "smoke")


def should_skip_level(request, target_level: str) -> bool:
    """Check if test should be skipped based on level."""
    current_level = get_test_level()

    levels = ["smoke", "standard", "advanced", "integration", "full"]
    current_idx = levels.index(current_level)
    target_idx = levels.index(target_level)

    return target_idx > current_idx


@contextmanager
def megatest_isolation():
    """Context manager for isolated megatest operations."""
    config = MegatestConfig()
    original_cwd = os.getcwd()

    try:
        # Change to safe directory
        os.chdir(config.base_path)
        yield config
    finally:
        os.chdir(original_cwd)


# ===============================================
# TEST DATA HELPERS
# ===============================================

def create_test_blender_scene(name: str = "test_scene") -> Dict[str, Any]:
    """Create test Blender scene data."""
    return {
        "name": name,
        "objects": [],
        "materials": [],
        "lights": [],
        "cameras": [],
        "metadata": {
            "created_by": "megatest",
            "test_session": True
        }
    }


def create_test_blender_object(name: str, obj_type: str = "MESH") -> Dict[str, Any]:
    """Create test Blender object data."""
    return {
        "name": name,
        "type": obj_type,
        "location": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
        "metadata": {
            "created_by": "megatest",
            "test_object": True
        }
    }


def create_test_material(name: str, material_type: str = "PRINCIPLED") -> Dict[str, Any]:
    """Create test material data."""
    return {
        "name": name,
        "type": material_type,
        "base_color": [0.8, 0.8, 0.8, 1.0],
        "metallic": 0.0,
        "roughness": 0.5,
        "metadata": {
            "created_by": "megatest",
            "test_material": True
        }
    }
