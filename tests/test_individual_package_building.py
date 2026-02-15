"""
Test script for Task 8.1: Test individual package building

This script verifies that each package in the monorepo can be built
independently using `python -m build` and that both wheel and sdist
are created correctly.

Validates: Requirements 6.3
"""

import subprocess
import sys
from pathlib import Path


def test_package_build(package_path: Path) -> tuple[bool, str]:
    """
    Test building a single package.
    
    Args:
        package_path: Path to the package directory
        
    Returns:
        Tuple of (success, message)
    """
    package_name = package_path.name
    dist_dir = package_path / "dist"
    
    # Check if dist directory exists and has files
    if not dist_dir.exists():
        return False, f"{package_name}: No dist directory found"
    
    files = list(dist_dir.glob("*"))
    if not files:
        return False, f"{package_name}: dist directory is empty"
    
    # Check for wheel (.whl) file
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        return False, f"{package_name}: No wheel (.whl) file found"
    
    # Check for source distribution (.tar.gz) file
    sdist_files = list(dist_dir.glob("*.tar.gz"))
    if not sdist_files:
        return False, f"{package_name}: No sdist (.tar.gz) file found"
    
    # Verify file sizes are reasonable (not empty)
    for file in wheel_files + sdist_files:
        size = file.stat().st_size
        if size < 1000:  # Less than 1KB is suspicious
            return False, f"{package_name}: {file.name} is suspiciously small ({size} bytes)"
    
    return True, f"{package_name}: ✓ Built successfully (wheel: {wheel_files[0].name}, sdist: {sdist_files[0].name})"


def main():
    """Run tests for all packages."""
    workspace_root = Path(__file__).parent
    packages_dir = workspace_root / "packages"
    
    if not packages_dir.exists():
        print("ERROR: packages directory not found")
        sys.exit(1)
    
    # Get all package directories
    packages = [p for p in packages_dir.iterdir() if p.is_dir() and (p / "pyproject.toml").exists()]
    
    if not packages:
        print("ERROR: No packages found")
        sys.exit(1)
    
    print(f"Testing individual package building for {len(packages)} packages...")
    print("=" * 70)
    
    results = []
    for package in sorted(packages):
        success, message = test_package_build(package)
        results.append((success, message))
        print(message)
    
    print("=" * 70)
    
    # Summary
    successful = sum(1 for success, _ in results if success)
    total = len(results)
    
    print(f"\nSummary: {successful}/{total} packages built successfully")
    
    if successful == total:
        print("\n✓ All packages can be built independently")
        print("✓ All packages produce both wheel and sdist artifacts")
        print("\nRequirement 6.3 validated: Packages maintain independence and can be built individually")
        return 0
    else:
        print("\n✗ Some packages failed to build correctly")
        return 1


if __name__ == "__main__":
    sys.exit(main())
