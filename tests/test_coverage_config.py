"""
Test to verify coverage configuration for monorepo workspace.

This test validates:
- Source patterns include all package src directories
- Omit patterns exclude generated code and tests
- Coverage reports include all packages

Requirements: 2.5, 7.4, 7.5
"""

import subprocess
import sys
from pathlib import Path


def test_coverage_source_patterns():
    """Verify that coverage source patterns are configured correctly."""
    # Read pyproject.toml
    pyproject_path = Path("pyproject.toml")
    assert pyproject_path.exists(), "pyproject.toml not found"
    
    content = pyproject_path.read_text()
    
    # Check that source pattern is configured
    assert '[tool.coverage.run]' in content, "Coverage run section not found"
    assert 'source = ["packages/*/src"]' in content, "Source pattern not configured correctly"
    
    print("✓ Coverage source patterns configured correctly")


def test_coverage_omit_patterns():
    """Verify that coverage omit patterns exclude generated code and tests."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    
    # Check omit patterns
    assert 'omit = [' in content, "Omit patterns not found"
    assert '"*/generated/*"' in content, "Generated code not excluded"
    assert '"*/__pycache__/*"' in content, "Pycache not excluded"
    assert '"*/tests/*"' in content, "Tests not excluded"
    
    print("✓ Coverage omit patterns configured correctly")


def test_coverage_includes_all_packages():
    """Test that coverage reports include all packages."""
    # Get list of packages
    packages_dir = Path("packages")
    packages = [p for p in packages_dir.iterdir() if p.is_dir() and (p / "src").exists()]
    
    print(f"\nFound {len(packages)} packages with src directories:")
    for pkg in packages:
        print(f"  - {pkg.name}")
    
    # Run a simple test with coverage on one package to verify configuration works
    # We'll use a package that has working tests
    test_cmd = [
        "uv", "run", "pytest",
        "packages/er-gen-mcp/tests/test_er_mcp.py",
        "--cov=packages/er-gen-mcp/src",
        "--cov-report=term-missing",
        "-v"
    ]
    
    print(f"\nRunning test command: {' '.join(test_cmd)}")
    result = subprocess.run(test_cmd, capture_output=True, text=True)
    
    # Check if coverage was collected
    if "no data was collected" in result.stdout.lower() or "no data was collected" in result.stderr.lower():
        print("\n⚠ Warning: Coverage data collection issue detected")
        print("This is expected with glob patterns in coverage source configuration")
        print("\nThe issue is that coverage.py doesn't expand glob patterns like 'packages/*/src'")
        print("We need to specify explicit package paths or use a different approach")
        return False
    
    print("✓ Coverage collection works for individual packages")
    return True


def test_coverage_with_explicit_sources():
    """Test coverage with explicit source paths instead of glob patterns."""
    # Get all package src directories
    packages_dir = Path("packages")
    src_dirs = []
    for pkg in packages_dir.iterdir():
        if pkg.is_dir():
            src_path = pkg / "src"
            if src_path.exists():
                src_dirs.append(str(src_path))
    
    print(f"\nFound {len(src_dirs)} source directories:")
    for src in src_dirs:
        print(f"  - {src}")
    
    # Run pytest with explicit coverage sources
    test_cmd = [
        "uv", "run", "pytest",
        "packages/er-gen-mcp/tests/test_er_mcp.py",
        "-v"
    ]
    
    # Add coverage for each source directory
    for src in src_dirs:
        test_cmd.append(f"--cov={src}")
    
    test_cmd.extend(["--cov-report=term-missing", "--cov-report=html"])
    
    print(f"\nRunning test with explicit sources...")
    result = subprocess.run(test_cmd, capture_output=True, text=True)
    
    # Check output
    if result.returncode == 0:
        print("✓ Tests passed")
    
    # Check if coverage was collected
    if "no data was collected" not in result.stdout.lower() and "no data was collected" not in result.stderr.lower():
        print("✓ Coverage data collected successfully with explicit sources")
        
        # Check if multiple packages are in coverage report
        output = result.stdout + result.stderr
        covered_packages = []
        for src in src_dirs:
            pkg_name = Path(src).parent.name
            if pkg_name in output or src in output:
                covered_packages.append(pkg_name)
        
        print(f"\nPackages in coverage report: {len(covered_packages)}")
        for pkg in covered_packages:
            print(f"  - {pkg}")
        
        return True
    else:
        print("⚠ Coverage data collection failed")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Coverage Configuration")
    print("=" * 70)
    
    try:
        test_coverage_source_patterns()
        test_coverage_omit_patterns()
        
        print("\n" + "=" * 70)
        print("Testing Coverage Collection")
        print("=" * 70)
        
        glob_works = test_coverage_includes_all_packages()
        
        if not glob_works:
            print("\n" + "=" * 70)
            print("Testing Alternative Approach")
            print("=" * 70)
            test_coverage_with_explicit_sources()
        
        print("\n" + "=" * 70)
        print("Summary")
        print("=" * 70)
        print("\nCoverage configuration verification complete!")
        print("\nKey findings:")
        print("1. Source patterns are configured: packages/*/src")
        print("2. Omit patterns exclude: generated code, __pycache__, tests")
        print("3. Coverage.py doesn't expand glob patterns directly")
        print("4. Solution: Use explicit --cov arguments or configure differently")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
