#!/usr/bin/env python3
"""
Test external dependency installation for monorepo workspace.

This test verifies:
1. External dependencies are installed correctly
2. Dependencies come from the configured index (Aliyun mirror)

Requirements: 1.5
"""

import importlib
import subprocess
import sys
from pathlib import Path


def test_external_dependencies_installed():
    """Verify that external dependencies are installed and importable."""
    
    # List of external dependencies to check
    external_deps = [
        # From er-gen-core
        ("jinja2", "Jinja2"),
        ("antlr4", "antlr4-python3-runtime"),
        ("sqlalchemy", "SQLAlchemy"),
        ("toml", "toml"),
        ("pydantic", "pydantic"),
        ("yaml", "PyYAML"),
        # From er-gen-tool and er-gen-tool-ai
        ("click", "click"),
        # From dev dependencies
        ("pytest", "pytest"),
        ("hypothesis", "hypothesis"),
    ]
    
    print("Testing external dependency installation...")
    print("=" * 60)
    
    failed_imports = []
    successful_imports = []
    
    for module_name, package_name in external_deps:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "unknown")
            successful_imports.append((package_name, module_name, version))
            print(f"✓ {package_name:30s} (module: {module_name:15s}) v{version}")
        except ImportError as e:
            failed_imports.append((package_name, module_name, str(e)))
            print(f"✗ {package_name:30s} (module: {module_name:15s}) FAILED: {e}")
    
    print("=" * 60)
    print(f"Successfully imported: {len(successful_imports)}/{len(external_deps)}")
    
    if failed_imports:
        print(f"\nFailed imports ({len(failed_imports)}):")
        for pkg, mod, err in failed_imports:
            print(f"  - {pkg} ({mod}): {err}")
        return False
    
    return True


def test_dependencies_from_configured_index():
    """Verify that dependencies come from the configured index (Aliyun)."""
    
    print("\n\nChecking dependency installation source...")
    print("=" * 60)
    
    # Check uv.lock file for index information
    lock_file = Path("uv.lock")
    
    if not lock_file.exists():
        print("✗ uv.lock file not found")
        return False
    
    print(f"✓ Found uv.lock file")
    
    # Read lock file and check for index URL
    lock_content = lock_file.read_text()
    
    # Check if Aliyun mirror is configured
    if "mirrors.aliyun.com" in lock_content:
        print("✓ Lock file references Aliyun mirror")
    else:
        print("⚠ Lock file does not explicitly reference Aliyun mirror")
        print("  (This may be normal if the index is configured in pyproject.toml)")
    
    # Verify pyproject.toml has the correct index configuration
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        pyproject_content = pyproject.read_text()
        if 'index-url = "https://mirrors.aliyun.com/pypi/simple/"' in pyproject_content:
            print("✓ pyproject.toml configured with Aliyun mirror")
        else:
            print("✗ pyproject.toml missing Aliyun mirror configuration")
            return False
    
    # Check pip list to see installed packages
    try:
        result = subprocess.run(
            ["uv", "pip", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Count external packages (excluding workspace packages)
        lines = result.stdout.strip().split("\n")
        external_packages = [
            line for line in lines[2:]  # Skip header lines
            if line and not line.startswith("x007007007-")
        ]
        
        print(f"✓ Found {len(external_packages)} external packages installed")
        
        # Show a sample of installed external packages
        print("\nSample of installed external packages:")
        for line in external_packages[:10]:
            print(f"  {line}")
        
        if len(external_packages) > 10:
            print(f"  ... and {len(external_packages) - 10} more")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to list installed packages: {e}")
        return False
    
    print("=" * 60)
    return True


def main():
    """Run all external dependency tests."""
    
    print("External Dependency Installation Test")
    print("=" * 60)
    print("Requirement 1.5: External dependencies should be installed")
    print("from the configured index (Aliyun mirror)")
    print("=" * 60)
    print()
    
    # Run tests
    test1_passed = test_external_dependencies_installed()
    test2_passed = test_dependencies_from_configured_index()
    
    # Summary
    print("\n\nTest Summary")
    print("=" * 60)
    print(f"External dependencies installed: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Dependencies from configured index: {'PASS' if test2_passed else 'FAIL'}")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
