#!/usr/bin/env python3
"""
Test runner for Blender MCP project.

This script provides a comprehensive test runner that works in both local development
environments (with Blender) and CI/CD environments (without Blender).

Usage:
    python tests/run_tests.py                    # Run all appropriate tests
    python tests/run_tests.py --unit-only        # Run only unit tests
    python tests/run_tests.py --integration-only # Run only integration tests (requires Blender)
    python tests/run_tests.py --ci               # Run tests for CI environment
    python tests/run_tests.py --coverage         # Run with coverage reporting
    python tests/run_tests.py --verbose          # Verbose output
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path


def is_blender_available():
    """Check if Blender is available on the system."""
    # Check common Blender installation paths
    blender_paths = [
        "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.3\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        "/opt/blender/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
    ]

    # Check environment variable
    env_path = os.environ.get("BLENDER_EXECUTABLE")
    if env_path and Path(env_path).exists():
        return True

    # Check common paths
    for path in blender_paths:
        if Path(path).exists():
            return True

    return False


def run_pytest(args, test_path="tests/", markers=None, extra_args=None):
    """Run pytest with specified arguments."""
    cmd = [sys.executable, "-m", "pytest"]

    if test_path:
        cmd.append(test_path)

    if markers:
        cmd.extend(["-m", markers])

    if extra_args:
        cmd.extend(extra_args)

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Blender MCP tests")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests (requires Blender)",
    )
    parser.add_argument("--ci", action="store_true", help="Run tests optimized for CI environment")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage reporting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-blender-skip",
        action="store_true",
        help="Don't skip Blender-dependent tests even if Blender unavailable",
    )

    args = parser.parse_args()

    # Check Blender availability
    blender_available = is_blender_available()
    print(f"Blender available: {blender_available}")

    if not blender_available and not args.no_blender_skip:
        print("⚠️  Blender not found. Integration tests will be skipped.")
        print("   Install Blender or set BLENDER_EXECUTABLE environment variable.")

    # Determine test strategy
    extra_args = []
    if args.verbose:
        extra_args.extend(["-v", "--tb=short"])
    else:
        extra_args.append("--tb=short")

    if args.coverage:
        extra_args.extend(
            ["--cov=src/blender_mcp", "--cov-report=html:htmlcov", "--cov-report=term-missing"]
        )

    # CI mode optimizations
    if args.ci:
        extra_args.extend(
            [
                "--strict-markers",
                "--disable-warnings",
                "-x",  # Stop on first failure
            ]
        )

    success = True

    try:
        if args.unit_only:
            # Run only unit tests
            print("🧪 Running unit tests...")
            result = run_pytest(args, "tests/unit/", "unit", extra_args)
            if result != 0:
                success = False

        elif args.integration_only:
            # Run only integration tests
            if not blender_available and not args.no_blender_skip:
                print("❌ Cannot run integration tests: Blender not available")
                success = False
            else:
                print("🔗 Running integration tests...")
                result = run_pytest(
                    args, "tests/integration/", "integration and requires_blender", extra_args
                )
                if result != 0:
                    success = False

        else:
            # Run appropriate tests based on environment
            if args.ci or not blender_available:
                # CI mode or no Blender: run only unit tests
                print("🤖 Running unit tests only (CI mode or no Blender)...")
                result = run_pytest(args, "tests/unit/", "unit", extra_args)
                if result != 0:
                    success = False
            else:
                # Local development with Blender: run all tests
                print("🏠 Running all tests (local development mode)...")

                # Unit tests first
                print("  📦 Running unit tests...")
                result = run_pytest(args, "tests/unit/", "unit", extra_args)
                if result != 0:
                    success = False

                # Then integration tests
                if success:
                    print("  🔗 Running integration tests...")
                    result = run_pytest(
                        args, "tests/integration/", "integration and requires_blender", extra_args
                    )
                    if result != 0:
                        success = False

    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        success = False
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        success = False

    # Print results
    print()
    if success:
        print("✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
