#!/usr/bin/env python3
"""Test runner script for Blender MCP tests.

This script provides an easy way to run different types of tests with proper
configuration and filtering.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def find_blender_executable():
    """Find Blender executable for testing."""
    # Check environment variable
    env_path = os.environ.get('BLENDER_EXECUTABLE')
    if env_path and Path(env_path).exists():
        return env_path

    # Common Blender installation paths
    common_paths = [
        "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        "/opt/blender/blender",
        "blender"
    ]

    for path in common_paths:
        if Path(path).exists():
            return path

    return None


def run_pytest(args, extra_args=None):
    """Run pytest with given arguments."""
    cmd = [sys.executable, "-m", "pytest"] + args
    if extra_args:
        cmd.extend(extra_args)

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run Blender MCP tests - Two-tier testing for CI/CD and local development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Two-Tier Testing Strategy:

TIER 1 - CI/CD Tests (No Blender Required):
  --unit              Unit tests for utilities, validation, configuration
  --no-blender        All tests that don't require Blender (CI-safe)

TIER 2 - Integration Tests (Blender Required):
  --integration       Real Blender script execution tests
  --e2e              End-to-end workflow tests
  --performance       Performance and stress tests

Examples:
  # CI/CD: Fast tests without Blender
  python tests/run_tests.py --no-blender --coverage

  # Local development: Full test suite with Blender
  python tests/run_tests.py --all

  # Specific test categories
  python tests/run_tests.py --unit
  python tests/run_tests.py --integration --e2e

  # Development workflow
  python tests/run_tests.py --unit --verbose  # Quick feedback
  python tests/run_tests.py --integration     # Test real functionality
        """
    )

    # Test type options
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument('--unit', action='store_true',
                           help='Run unit tests only (no Blender required)')
    test_group.add_argument('--integration', action='store_true',
                           help='Run integration tests (requires Blender)')
    test_group.add_argument('--e2e', action='store_true',
                           help='Run end-to-end tests (requires Blender)')
    test_group.add_argument('--performance', action='store_true',
                           help='Run performance tests (requires Blender)')
    test_group.add_argument('--no-blender', action='store_true',
                           help='Run tests that do not require Blender')
    test_group.add_argument('--all', action='store_true',
                           help='Run all tests')

    # Specific test options
    parser.add_argument('--file', type=str,
                       help='Run specific test file')
    parser.add_argument('--test-class', type=str,
                       help='Run specific test class')
    parser.add_argument('--function', type=str,
                       help='Run specific test function')

    # Output options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Quiet output')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--html-report', action='store_true',
                       help='Generate HTML test report')

    # Blender options
    parser.add_argument('--blender-path', type=str,
                       help='Path to Blender executable')

    args = parser.parse_args()

    # Check for Blender
    blender_path = args.blender_path or find_blender_executable()
    if blender_path:
        os.environ['BLENDER_EXECUTABLE'] = blender_path
        print(f"Using Blender: {blender_path}")
    else:
        print("Warning: Blender executable not found. Some tests will be skipped.")

    # Build pytest arguments
    pytest_args = []

    # Handle test selection
    if args.file:
        pytest_args.append(f"tests/{args.file}")
    elif args.unit:
        pytest_args.extend(["-m", "not (integration or e2e or performance)"])
    elif args.integration:
        pytest_args.extend(["-m", "integration"])
    elif args.e2e:
        pytest_args.extend(["-m", "e2e"])
    elif args.performance:
        pytest_args.extend(["-m", "performance"])
    elif args.no_blender:
        pytest_args.extend(["-m", "not (integration or e2e or performance or requires_blender)"])
    elif args.all:
        pass  # Run all tests
    else:
        # Default: run unit tests only
        pytest_args.extend(["-m", "not (integration or e2e or performance)"])

    # Handle specific test selection
    if args.test_class:
        pytest_args.extend(["-k", args.test_class])
    if args.function:
        if args.test_class:
            pytest_args.extend([f"{args.test_class} and {args.function}"])
        else:
            pytest_args.extend(["-k", args.function])

    # Output options
    if args.verbose:
        pytest_args.append("-v")
    elif args.quiet:
        pytest_args.append("-q")

    if args.coverage:
        pytest_args.extend([
            "--cov=blender_mcp",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])

    if args.html_report:
        pytest_args.extend([
            "--html=test_report.html",
            "--self-contained-html"
        ])

    # Default test path if not specified
    if not any(arg.startswith("tests/") for arg in pytest_args):
        pytest_args.insert(0, "tests/")

    # Run the tests
    exit_code = run_pytest(pytest_args)

    # Print summary
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")

    # Print helpful information
    if not blender_path:
        print("\nNote: Some tests were skipped because Blender was not found.")
        print("To run all tests, install Blender and set BLENDER_EXECUTABLE environment variable")
        print("or use --blender-path option.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
