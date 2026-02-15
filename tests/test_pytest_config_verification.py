#!/usr/bin/env python3
"""
Verification script for Task 5.1: Verify pytest configuration
Tests Requirements 2.1, 2.2, 7.2
"""

import subprocess
import sys
import tomllib
from pathlib import Path


def test_testpaths_pattern():
    """Verify testpaths pattern matches all package test directories"""
    print("✓ Testing testpaths pattern...")
    
    # Read pyproject.toml
    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    
    testpaths = config["tool"]["pytest"]["ini_options"]["testpaths"]
    print(f"  Configured testpaths: {testpaths}")
    
    # Check that pattern is correct
    assert testpaths == ["packages/*/tests"], f"Expected ['packages/*/tests'], got {testpaths}"
    
    # Verify all packages have test directories
    packages_dir = Path("packages")
    expected_packages = ["er-django", "er-gen-core", "er-gen-mcp", "er-gen-tool", "er-gen-tool-ai"]
    
    for pkg in expected_packages:
        test_dir = packages_dir / pkg / "tests"
        assert test_dir.exists(), f"Test directory not found: {test_dir}"
        print(f"  ✓ Found test directory: {test_dir}")
    
    print("✓ testpaths pattern verification PASSED\n")


def test_addopts_coverage_flags():
    """Verify addopts includes coverage flags"""
    print("✓ Testing addopts coverage flags...")
    
    # Read pyproject.toml
    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    
    addopts = config["tool"]["pytest"]["ini_options"]["addopts"]
    print(f"  Configured addopts: {addopts}")
    
    # Check for coverage report flags
    assert "--cov-report=term-missing" in addopts, "Missing --cov-report=term-missing"
    assert "--cov-report=html" in addopts, "Missing --cov-report=html"
    
    print("  ✓ Found --cov-report=term-missing")
    print("  ✓ Found --cov-report=html")
    print("✓ addopts coverage flags verification PASSED\n")


def test_pytest_discovers_all_tests():
    """Test that `uv run pytest` discovers all tests"""
    print("✓ Testing pytest test discovery...")
    
    # Run pytest with --collect-only to see what tests are discovered
    result = subprocess.run(
        ["uv", "run", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )
    
    # Check that tests from all packages are discovered
    output = result.stdout + result.stderr
    
    expected_packages = ["er-django", "er-gen-core", "er-gen-mcp", "er-gen-tool", "er-gen-tool-ai"]
    
    for pkg in expected_packages:
        pattern = f"packages/{pkg}/tests/"
        assert pattern in output, f"No tests discovered from {pkg}"
        print(f"  ✓ Tests discovered from {pkg}")
    
    # Count collected tests (look for "X tests collected" or similar)
    if "tests collected" in output or "test collected" in output:
        # Extract number of tests
        import re
        match = re.search(r'(\d+) tests? collected', output)
        if match:
            num_tests = int(match.group(1))
            print(f"  ✓ Total tests discovered: {num_tests}")
            assert num_tests > 0, "No tests were collected"
    
    print("✓ pytest test discovery verification PASSED\n")


def main():
    """Run all verification tests"""
    print("=" * 70)
    print("Task 5.1: Verify pytest configuration")
    print("Requirements: 2.1, 2.2, 7.2")
    print("=" * 70)
    print()
    
    try:
        test_testpaths_pattern()
        test_addopts_coverage_flags()
        test_pytest_discovers_all_tests()
        
        print("=" * 70)
        print("✓ ALL VERIFICATIONS PASSED")
        print("=" * 70)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ VERIFICATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
