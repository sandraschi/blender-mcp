# Blender MCP Test Suite

This directory contains a comprehensive **two-tier test suite** for the Blender MCP server:

## 🧪 Two-Tier Testing Strategy

### **Tier 1: CI-Ready Unit Tests** (No Blender Required)
- ✅ Runs in GitHub Actions automatically
- ✅ Tests configuration, validation, utilities
- ✅ Fast feedback (< 2 seconds)
- ✅ No external dependencies

### **Tier 2: Integration Tests** (Real Blender Execution)
- 🎨 Tests actual 3D operations with running Blender
- 🎨 Validates scene creation, materials, exports
- 🎨 Runs locally or in specialized CI environments
- 🎨 Requires Blender installation

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_utils.py            # Test utilities and helpers
├── test_unit_utils.py       # Unit tests for utilities
├── test_unit_blender_executor.py  # Unit tests for BlenderExecutor
├── test_integration_blender_executor.py  # Integration tests for BlenderExecutor
├── test_integration_handlers.py  # Integration tests for handlers
├── test_e2e_workflows.py     # End-to-end workflow tests
├── test_performance.py      # Performance and stress tests
├── test_blender_mcp.py      # Main test suite (updated)
├── run_tests.py             # Test runner script
├── README.md                # This file
└── resources/               # Test resources (created as needed)
```

## Test Categories

### Unit Tests (`--unit`)
- Test individual components without Blender
- Mock external dependencies
- Fast execution, no Blender required
- Files: `test_unit_*.py`

### Integration Tests (`--integration`)
- Test components with real Blender execution
- Test individual handlers and utilities
- Require Blender installation
- Files: `test_integration_*.py`

### End-to-End Tests (`--e2e`)
- Test complete workflows from start to finish
- Test real user scenarios
- Require Blender installation
- Files: `test_e2e_*.py`

### Performance Tests (`--performance`)
- Test performance characteristics
- Stress test with large scenes/objects
- Require Blender installation
- Files: `test_performance.py`

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided `run_tests.py` script:

```bash
# Run unit tests only (no Blender required)
python tests/run_tests.py --unit

# Run integration tests (requires Blender)
python tests/run_tests.py --integration

# Run end-to-end tests (requires Blender)
python tests/run_tests.py --e2e

# Run performance tests (requires Blender)
python tests/run_tests.py --performance

# Run all tests that don't require Blender
python tests/run_tests.py --no-blender

# Run all tests (requires Blender for integration/e2e/performance)
python tests/run_tests.py --all
```

### Using Pytest Directly

You can also run tests directly with pytest:

```bash
# Run unit tests
pytest tests/ -m "not (integration or e2e or performance)"

# Run integration tests
pytest tests/ -m integration

# Run end-to-end tests
pytest tests/ -m e2e

# Run performance tests
pytest tests/ -m performance

# Run specific test file
pytest tests/test_unit_utils.py -v

# Run specific test class
pytest tests/test_integration_handlers.py::TestSceneHandlerIntegration -v

# Run specific test function
pytest tests/test_integration_handlers.py::TestSceneHandlerIntegration::test_create_scene -v
```

### Blender Setup

For tests that require Blender:

1. **Install Blender** (version 4.0+ recommended)
2. **Set environment variable**:
   ```bash
   export BLENDER_EXECUTABLE=/path/to/blender
   ```
   Or use the `--blender-path` option:
   ```bash
   python tests/run_tests.py --integration --blender-path /path/to/blender
   ```

The test suite will automatically detect Blender in common locations:
- Windows: `C:\Program Files\Blender Foundation\Blender X.X\blender.exe`
- Linux: `/usr/bin/blender`, `/usr/local/bin/blender`
- macOS: `/Applications/Blender.app/Contents/MacOS/Blender`

## Test Configuration

### Pytest Configuration

Tests use markers to control execution:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.requires_blender` - Tests requiring Blender

### Test Fixtures

Common fixtures available:
- `blender_executable` - Path to Blender executable
- `temp_dir` - Temporary directory for test files
- `temp_file` - Temporary file for test data
- `test_config` - Test configuration dictionary
- `blender_test_helper` - Helper class for Blender operations

## Writing Tests

### Unit Tests

```python
import pytest

def test_some_utility():
    """Test utility function without Blender."""
    from blender_mcp.utils.some_module import some_function

    result = some_function(input_data)
    assert result == expected_output
```

### Integration Tests

```python
import pytest

@pytest.mark.integration
@pytest.mark.requires_blender
class TestSomeHandler:
    @pytest.mark.asyncio
    async def test_handler_function(self, blender_executable):
        from blender_mcp.handlers.some_handler import SomeHandler

        handler = SomeHandler(blender_executable)
        result = await handler.some_method()

        assert "expected output" in result
```

### Performance Tests

```python
import pytest
import time

@pytest.mark.performance
@pytest.mark.requires_blender
class TestPerformance:
    @pytest.mark.asyncio
    async def test_operation_performance(self, blender_executable):
        from tests.test_utils import PerformanceTimer

        timer = PerformanceTimer()
        timer.start()

        # Perform operation
        result = await some_async_operation()

        duration = await timer.stop()
        assert duration < 30.0  # Should complete within 30 seconds
```

## Test Utilities

The `test_utils.py` module provides helpful utilities:

- `TestBlenderHelper` - Helper for Blender operations
- `TestDataBuilder` - Builder for creating test scenes
- `PerformanceTimer` - Timer for performance measurements
- `temp_directory()` - Context manager for temporary directories
- `find_blender_executable()` - Utility to find Blender

## Coverage and Reporting

Generate coverage reports:

```bash
python tests/run_tests.py --unit --coverage
```

Generate HTML test reports:

```bash
python tests/run_tests.py --all --html-report
```

## CI/CD Integration

The test suite is designed for **two-tier testing** to work in CI/CD environments:

### **Tier 1: Fast CI Tests (No Blender Required)**
These run automatically in GitHub Actions and provide quick feedback:

```bash
# Run all tests that don't require Blender
python tests/run_tests.py --no-blender --coverage

# Or with pytest markers
pytest tests/ -m "not (integration or e2e or performance or requires_blender)"
```

**What's tested:**
- Unit tests for utilities, validation, configuration
- Mock-free testing of core logic
- Fast execution (< 2 seconds)
- No external dependencies

### **Tier 2: Full Integration Tests (Blender Required)**
These run locally or in specialized CI environments with Blender installed:

```bash
# Run integration tests with real Blender
python tests/run_tests.py --integration

# Run end-to-end workflow tests
python tests/run_tests.py --e2e

# Run performance tests
python tests/run_tests.py --performance
```

**What's tested:**
- Real Blender script execution
- 3D scene creation and manipulation
- Export/import functionality
- Performance under load

### **GitHub Actions Setup**

The repository includes `.github/workflows/ci.yml` that:

1. **Always runs:** Unit tests (no Blender needed)
2. **Optionally runs:** Integration tests on main branch (with Blender)

```yaml
# Example from .github/workflows/ci.yml
- name: Run unit tests (no Blender required)
  run: python tests/run_tests.py --no-blender --coverage

# Only on main branch with Blender installed
- name: Run integration tests (with Blender)
  run: python tests/run_tests.py --integration --e2e
```

### **Local Development**

For local development with Blender installed:

```bash
# Quick unit test feedback
python tests/run_tests.py --unit

# Full test suite with Blender
python tests/run_tests.py --all

# Run specific test categories
python tests/run_tests.py --integration --performance
```

## Troubleshooting

### Common Issues

1. **Blender not found**: Set `BLENDER_EXECUTABLE` environment variable or use `--blender-path`
2. **Import errors**: Ensure the project is properly installed or run from project root
3. **Permission errors**: Ensure Blender executable has proper permissions
4. **Timeout errors**: Increase timeout values in test configuration

### Debug Mode

Run tests with verbose output:

```bash
python tests/run_tests.py --all --verbose
```

Check Blender output in test failures for debugging script issues.

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Add appropriate pytest markers
3. Include docstrings for all test methods
4. Use fixtures for common setup/teardown
5. Handle missing dependencies gracefully with `pytest.skip()`
6. Add performance assertions for performance tests

## Test Data

Test resources are stored in the `resources/` directory (created as needed). This includes:
- Sample blend files
- Test textures
- Configuration files
- Expected output files
