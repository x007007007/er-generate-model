#!/usr/bin/env python3
"""
Verification script for er-gen-tool-ai package installation.
This script verifies that the package can be installed independently and the CLI plugin interface works.
"""

import sys
from importlib.metadata import entry_points


def verify_package_import():
    """Verify the package can be imported."""
    try:
        import x007007007.er_tool_ai
        print("✓ Package imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import package: {e}")
        return False


def verify_cli_plugin():
    """Verify the CLI plugin interface works."""
    try:
        from x007007007.er_tool_ai.cli_plugin import ai_assist_cmd
        print("✓ CLI plugin interface imported successfully")
        print(f"  - Command name: {ai_assist_cmd.name}")
        print(f"  - Command type: {type(ai_assist_cmd).__name__}")
        print(f"  - Subcommands: {list(ai_assist_cmd.commands.keys())}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import CLI plugin: {e}")
        return False


def verify_entry_point():
    """Verify the entry point is registered correctly."""
    try:
        eps = entry_points(group='er_gen_tool.plugins')
        found = False
        for ep in eps:
            if ep.name == 'ai-assist':
                found = True
                print("✓ Entry point registered successfully")
                print(f"  - Name: {ep.name}")
                print(f"  - Value: {ep.value}")
                
                # Try to load it
                try:
                    plugin_cmd = ep.load()
                    print("✓ Plugin loaded successfully")
                    print(f"  - Plugin type: {type(plugin_cmd).__name__}")
                    print(f"  - Plugin commands: {list(plugin_cmd.commands.keys())}")
                except Exception as e:
                    print(f"✗ Failed to load plugin: {e}")
                    return False
                
                break
        
        if not found:
            print("✗ Entry point 'ai-assist' not found")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to verify entry point: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Verifying er-gen-tool-ai package installation")
    print("=" * 60)
    print()
    
    checks = [
        ("Package Import", verify_package_import),
        ("CLI Plugin Interface", verify_cli_plugin),
        ("Entry Point Registration", verify_entry_point),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        result = check_func()
        results.append(result)
        print()
    
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for (name, _), result in zip(checks, results):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    
    if all(results):
        print("✓ All verification checks passed!")
        return 0
    else:
        print("✗ Some verification checks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
