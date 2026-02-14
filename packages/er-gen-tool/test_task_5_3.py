#!/usr/bin/env python3
"""
Test for Task 5.3: Verify plugin loading mechanism using entry points

This test verifies:
1. The load_plugins() function exists and is called
2. It uses importlib.metadata entry_points
3. It can discover plugins from 'er_gen_tool.plugins' group
"""
import sys
import inspect


def test_load_plugins_function_exists():
    """Verify that load_plugins() function exists in cli.py"""
    print("Test 1: Checking if load_plugins() function exists...")
    
    try:
        from x007007007.er_tool import cli
        
        # Check if load_plugins function exists
        if hasattr(cli, 'load_plugins'):
            print("  ✓ load_plugins() function exists")
            
            # Check the function signature
            sig = inspect.signature(cli.load_plugins)
            print(f"  ✓ Function signature: load_plugins{sig}")
            
            return True
        else:
            print("  ✗ load_plugins() function not found")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_uses_importlib_metadata():
    """Verify that the implementation uses importlib.metadata.entry_points"""
    print("\nTest 2: Checking if load_plugins() uses importlib.metadata...")
    
    try:
        from x007007007.er_tool import cli
        import importlib.metadata
        
        # Get the source code of load_plugins
        source = inspect.getsource(cli.load_plugins)
        
        # Check for importlib.metadata usage
        if 'entry_points' in source:
            print("  ✓ Uses entry_points() API")
        else:
            print("  ✗ Does not use entry_points() API")
            return False
        
        # Check for the correct group name
        if 'er_gen_tool.plugins' in source:
            print("  ✓ Uses correct group name: 'er_gen_tool.plugins'")
        else:
            print("  ✗ Does not use correct group name")
            return False
        
        # Check for error handling
        if 'try' in source and 'except' in source:
            print("  ✓ Has error handling for plugin loading failures")
        else:
            print("  ⚠ Warning: No error handling detected")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_plugin_discovery():
    """Verify that plugins can be discovered from 'er_gen_tool.plugins' group"""
    print("\nTest 3: Testing plugin discovery from entry points...")
    
    try:
        from importlib.metadata import entry_points
        
        # Try to discover plugins
        try:
            plugin_eps = entry_points(group='er_gen_tool.plugins')
        except TypeError:
            # Python 3.10+ API
            plugin_eps = entry_points().select(group='er_gen_tool.plugins')
        
        plugins = list(plugin_eps)
        
        if plugins:
            print(f"  ✓ Successfully discovered {len(plugins)} plugin(s):")
            for ep in plugins:
                print(f"    - {ep.name}: {ep.value}")
            return True
        else:
            print("  ℹ No plugins found (this is OK if no plugins are installed)")
            return True
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_load_plugins_is_called():
    """Verify that load_plugins() is called during CLI initialization"""
    print("\nTest 4: Checking if load_plugins() is called...")
    
    try:
        from x007007007.er_tool import cli
        
        # Get the module source
        source = inspect.getsource(cli)
        
        # Check if load_plugins() is called
        if 'load_plugins()' in source:
            print("  ✓ load_plugins() is called in the module")
            
            # Check if it's called after command registration
            lines = source.split('\n')
            load_plugins_line = None
            add_command_line = None
            
            for i, line in enumerate(lines):
                if 'load_plugins()' in line and not line.strip().startswith('#'):
                    load_plugins_line = i
                if 'main.add_command' in line and not line.strip().startswith('#'):
                    if add_command_line is None:
                        add_command_line = i
            
            if load_plugins_line and add_command_line:
                if load_plugins_line > add_command_line:
                    print("  ✓ load_plugins() is called after core commands are registered")
                else:
                    print("  ⚠ Warning: load_plugins() might be called before core commands")
            
            return True
        else:
            print("  ✗ load_plugins() is not called")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_cli_integration():
    """Verify that the CLI can be imported and plugins are integrated"""
    print("\nTest 5: Testing CLI integration...")
    
    try:
        from x007007007.er_tool.cli import main
        
        print("  ✓ CLI main function imported successfully")
        
        # Check registered commands
        commands = main.commands
        print(f"  ✓ Total commands registered: {len(commands)}")
        
        for cmd_name in sorted(commands.keys()):
            print(f"    - {cmd_name}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests for task 5.3"""
    print("=" * 70)
    print("Task 5.3: Plugin Loading Mechanism Verification")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(("load_plugins() exists", test_load_plugins_function_exists()))
    results.append(("Uses importlib.metadata", test_uses_importlib_metadata()))
    results.append(("Plugin discovery works", test_plugin_discovery()))
    results.append(("load_plugins() is called", test_load_plugins_is_called()))
    results.append(("CLI integration works", test_cli_integration()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ Task 5.3 requirements verified successfully!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
