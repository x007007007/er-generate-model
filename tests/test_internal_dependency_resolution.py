#!/usr/bin/env python3
"""
Test internal dependency resolution for monorepo workspace.

This test verifies:
1. er-gen-tool can import from er-gen-core
2. er-gen-tool-ai can import from er-gen-core
3. Workspace versions are used, not external versions

Requirements: 1.2, 3.4, 4.2
"""

import sys
import importlib.util
from pathlib import Path


def test_er_gen_tool_imports_core():
    """Verify er-gen-tool can import from er-gen-core."""
    print("Testing: er-gen-tool can import from er-gen-core...")
    
    try:
        # Import er-gen-tool module
        import x007007007.er_tool
        print(f"  ✓ Successfully imported x007007007.er_tool")
        
        # Try to import er-gen-core modules (er-gen-core provides x007007007.er)
        import x007007007.er.models
        print(f"  ✓ Successfully imported x007007007.er.models (from er-gen-core)")
        
        import x007007007.er.parser.antlr.mermaid_antlr_parser
        print(f"  ✓ Successfully imported x007007007.er.parser (from er-gen-core)")
        
        # Verify it's the workspace version by checking the file location
        core_file = x007007007.er.models.__file__
        print(f"  ✓ er-gen-core location: {core_file}")
        
        # Check that it's from the workspace (should contain 'packages/er-gen-core')
        if 'packages/er-gen-core' in core_file or 'packages\\er-gen-core' in core_file:
            print(f"  ✓ Using workspace version (not external)")
            return True
        else:
            print(f"  ✗ NOT using workspace version!")
            return False
            
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_er_gen_tool_ai_imports_core():
    """Verify er-gen-tool-ai can import from er-gen-core."""
    print("\nTesting: er-gen-tool-ai can import from er-gen-core...")
    
    try:
        # Import er-gen-tool-ai module
        import x007007007.er_tool_ai
        print(f"  ✓ Successfully imported x007007007.er_tool_ai")
        
        # Try to import er-gen-core modules (er-gen-core provides x007007007.er)
        import x007007007.er.version
        print(f"  ✓ Successfully imported x007007007.er.version (from er-gen-core)")
        
        import x007007007.er.parser.toml_parser
        print(f"  ✓ Successfully imported x007007007.er.parser (from er-gen-core)")
        
        # Verify it's the workspace version by checking the file location
        core_file = x007007007.er.version.__file__
        print(f"  ✓ er-gen-core location: {core_file}")
        
        # Check that it's from the workspace
        if 'packages/er-gen-core' in core_file or 'packages\\er-gen-core' in core_file:
            print(f"  ✓ Using workspace version (not external)")
            return True
        else:
            print(f"  ✗ NOT using workspace version!")
            return False
            
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_workspace_version_consistency():
    """Verify that both packages use the same workspace version of er-gen-core."""
    print("\nTesting: Workspace version consistency...")
    
    try:
        # Import the er module from er-gen-core
        import x007007007.er.version
        
        # Get the version from the package
        version = x007007007.er.version.get_version()
        print(f"  ✓ er-gen-core version: {version}")
        
        # Verify the file location is in the workspace
        core_file = x007007007.er.version.__file__
        workspace_root = Path(__file__).parent
        
        # Check if the core package is within our workspace
        if str(workspace_root) in core_file:
            print(f"  ✓ er-gen-core is from workspace: {core_file}")
            return True
        else:
            print(f"  ✗ er-gen-core is NOT from workspace: {core_file}")
            return False
            
    except Exception as e:
        print(f"  ✗ Version check failed: {e}")
        return False


def main():
    """Run all internal dependency resolution tests."""
    print("=" * 70)
    print("Internal Dependency Resolution Test")
    print("=" * 70)
    
    results = []
    
    # Test 1: er-gen-tool imports core
    results.append(("er-gen-tool → er-gen-core", test_er_gen_tool_imports_core()))
    
    # Test 2: er-gen-tool-ai imports core
    results.append(("er-gen-tool-ai → er-gen-core", test_er_gen_tool_ai_imports_core()))
    
    # Test 3: Workspace version consistency
    results.append(("Workspace version consistency", test_workspace_version_consistency()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ All internal dependency resolution tests PASSED")
        print("=" * 70)
        return 0
    else:
        print("✗ Some internal dependency resolution tests FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
