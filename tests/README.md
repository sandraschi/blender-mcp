# Blender MCP Test Suite

Comprehensive test suite for the Blender MCP server with unit and integration tests that work in both local development and CI/CD environments.

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
Pure unit tests that don't require external dependencies:
- Configuration validation
- Exception handling
- Utility functions
- App initialization
- Data validation and sanitization

### Integration Tests (`tests/integration/`)
Full workflow tests that require Blender:
- Blender executor functionality
- Server startup and communication
- Complex scene operations
- File I/O operations
- Error handling with real Blender

## 🚀 Quick Start

### Local Development (with Blender)
```bash
# Run all tests
python tests/run_tests.py

# Run only unit tests
python tests/run_tests.py --unit-only

# Run with coverage
python tests/run_tests.py --coverage

# Verbose output
python tests/run_tests.py --verbose
```

### CI/CD Environment (without Blender)
```bash
# Run unit tests only (automatic detection)
python tests/run_tests.py --ci

# Or explicitly
python tests/run_tests.py --unit-only
```

## 📋 Test Markers

| Marker | Description | Environment |
|--------|-------------|-------------|
| `unit` | Pure unit tests, no dependencies | All |
| `integration` | Full workflow tests | Requires Blender |
| `requires_blender` | Tests needing Blender | Local only |
| `slow` | Tests taking >5 seconds | May be skipped |
| `performance` | Performance benchmarks | Optional |
| `ci_skip` | Skip in CI environment | Local only |
| `local_only` | Local development only | Local only |

## 🛠️ Manual Testing

### Using pytest directly
```bash
# All unit tests
pytest tests/unit/ -m "unit"

# All integration tests (requires Blender)
pytest tests/integration/ -m "integration and requires_blender"

# Specific test file
pytest tests/unit/test_config.py -v

# With coverage
pytest --cov=src/blender_mcp --cov-report=html
```

### Custom test runs
```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Run only fast unit tests
pytest tests/unit/ -m "unit and not slow"

# Run performance tests
pytest tests/ -m "performance"
```

## 🔧 Configuration

### Environment Variables
- `BLENDER_EXECUTABLE`: Path to Blender executable
- `CI`: Set to `true` in CI environments to skip Blender-dependent tests

### Blender Detection
The test suite automatically detects Blender in these locations:
- `BLENDER_EXECUTABLE` environment variable
- `C:\Program Files\Blender Foundation\Blender*\blender.exe` (Windows)
- `/usr/bin/blender`, `/usr/local/bin/blender` (Linux)
- `/Applications/Blender.app/Contents/MacOS/Blender` (macOS)

## 📊 Coverage Reporting

### Generate Coverage Report
```bash
python tests/run_tests.py --coverage
# Opens htmlcov/index.html in browser
```

### Coverage Configuration
- Source: `src/blender_mcp/`
- Excluded: Tests, venv, setup.py
- Report: HTML and terminal output

## 🐛 Debugging Failed Tests

### Common Issues

#### Blender Not Found
```bash
# Set Blender path explicitly
export BLENDER_EXECUTABLE="/path/to/blender"

# Or install Blender and restart terminal
```

#### Import Errors
```bash
# Ensure you're in the project root
cd /path/to/blender-mcp

# Install dependencies
pip install -r requirements.txt
```

#### Permission Errors
```bash
# On Windows, run as administrator or check file permissions
# On Linux/Mac, check executable permissions on Blender
```

### Debug Output
```bash
# Verbose pytest output
pytest tests/ -v -s

# Debug specific test
pytest tests/unit/test_config.py::TestBlenderValidation::test_validate_blender_executable_success -v -s
```

## 📈 Performance Testing

### Run Performance Benchmarks
```bash
pytest tests/ -m "performance" -v
```

### Profile Slow Tests
```bash
# Time individual tests
pytest tests/ --durations=10

# Profile specific test
pytest tests/unit/test_config.py --profile
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python tests/run_tests.py --ci
```

### Local CI Simulation
```bash
# Simulate CI environment
CI=true python tests/run_tests.py
```

## 🏗️ Test Structure

```
tests/
├── __init__.py              # Test package
├── conftest.py              # Pytest configuration and fixtures
├── pytest.ini              # Pytest settings
├── run_tests.py            # Custom test runner
├── README.md               # This file
├── unit/                   # Unit tests
│   ├── __init__.py
│   ├── test_config.py      # Configuration tests
│   ├── test_exceptions.py  # Exception tests
│   ├── test_utils.py       # Utility tests
│   └── test_app.py         # App/server tests
└── integration/            # Integration tests
    ├── __init__.py
    ├── test_blender_executor.py  # Blender execution tests
    └── test_server_startup.py   # Server startup tests
```

## 🎯 Best Practices

### Writing Unit Tests
1. **Mock external dependencies** - Don't rely on Blender being available
2. **Test one thing per test** - Keep tests focused and simple
3. **Use descriptive names** - `test_validate_blender_executable_success`
4. **Test edge cases** - Invalid inputs, error conditions
5. **Use fixtures** - Reuse common test setup

### Writing Integration Tests
1. **Mark with `@pytest.mark.requires_blender`** - Skip when Blender unavailable
2. **Use realistic test data** - Test with actual Blender operations
3. **Clean up after tests** - Don't leave test files/artifacts
4. **Test error conditions** - Network failures, invalid scripts
5. **Time-sensitive operations** - Use appropriate timeouts

### General Guidelines
1. **Fast feedback** - Unit tests should be <100ms each
2. **Independent tests** - Tests shouldn't depend on each other
3. **Clear assertions** - Use descriptive assertion messages
4. **Document complex tests** - Explain what and why you're testing
5. **Regular maintenance** - Update tests when code changes

## 🐛 Troubleshooting

### Test Discovery Issues
```bash
# Check pytest can find tests
pytest --collect-only tests/

# Debug import issues
python -c "import sys; sys.path.insert(0, 'src'); import blender_mcp"
```

### Blender-Specific Issues
```bash
# Test Blender manually
/path/to/blender --version

# Test script execution
/path/to/blender --python script.py
```

### Coverage Issues
```bash
# Check coverage configuration
pytest --cov=src/blender_mcp --cov-report=term-missing tests/unit/

# Debug coverage collection
COVERAGE_DEBUG=trace pytest --cov=src/blender_mcp tests/unit/test_config.py
```

## 📝 Contributing

### Adding New Tests
1. **Choose appropriate category** - Unit vs integration
2. **Follow naming conventions** - `test_*`, `Test*`
3. **Add proper markers** - `@pytest.mark.unit`, etc.
4. **Update documentation** - Add to this README if needed
5. **Test locally** - Ensure tests pass in your environment

### Test Maintenance
1. **Regular review** - Check for flaky or outdated tests
2. **Performance monitoring** - Watch for slow tests
3. **Coverage goals** - Maintain >90% coverage
4. **CI health** - Keep CI pipeline green

---

**Blender MCP Test Suite** - Comprehensive testing for reliable 3D automation
