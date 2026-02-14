#!/usr/bin/env python3
"""
Verification script for er-gen-mcp package installation.

This script verifies that:
1. The package can be imported
2. The CLI entry point is available
3. Dependencies (er-gen-core) are accessible
"""

import sys
import subprocess


def verify_import():
    """Verify the package can be imported."""
    try:
        import x007007007.er_mcp
        print("✓ Package x007007007.er_mcp imported successfully")
        print(f"  Location: {x007007007.er_mcp.__file__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import package: {e}")
        return False


def verify_cli():
    """Verify the CLI entry point works."""
    import shutil
    
    # Try to find er-gen-mcp in PATH or .venv/bin
    cli_path = shutil.which("er-gen-mcp")
    if not cli_path:
        # Try .venv/bin/er-gen-mcp
        import os
        venv_cli = os.path.join(os.getcwd(), ".venv", "bin", "er-gen-mcp")
        if os.path.exists(venv_cli):
            cli_path = venv_cli
    
    if not cli_path:
        print("✗ CLI entry point 'er-gen-mcp' not found in PATH or .venv/bin")
        return False
    
    try:
        result = subprocess.run(
            [cli_path, "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ CLI entry point 'er-gen-mcp' is available")
        print(f"  Location: {cli_path}")
        print(f"  Version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"✗ Failed to run CLI: {e}")
        return False


def verify_dependencies():
    """Verify dependencies are accessible."""
    try:
        from x007007007.er import models
        from x007007007.er_mcp import cli
        print("✓ All dependencies accessible")
        print("  - x007007007.er (er-gen-core)")
        print("  - x007007007.er_mcp.cli")
        return True
    except ImportError as e:
        print(f"✗ Failed to import dependencies: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("er-gen-mcp Installation Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Package Import", verify_import),
        ("CLI Entry Point", verify_cli),
        ("Dependencies", verify_dependencies),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"Checking: {name}")
        result = check_func()
        results.append(result)
        print()
    
    print("=" * 60)
    if all(results):
        print("✓ All verification checks passed!")
        print("er-gen-mcp is correctly installed and ready to use.")
        return 0
    else:
        print("✗ Some verification checks failed.")
        print("Please check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
