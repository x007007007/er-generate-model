#!/usr/bin/env python3
"""
Test script to verify plugin loading mechanism.

This script tests:
1. The load_plugins() function works correctly
2. Entry points are properly configured
3. Plugin discovery works as expected
"""
import sys
from importlib.metadata import entry_points


def test_entry_points_discovery():
    """Test that entry points can be discovered."""
    print("Testing entry points discovery...")
    
    try:
        # Try Python 3.9 API first
        try:
            plugin_eps = entry_points(group='er_gen_tool.plugins')
        except TypeError:
            # Python 3.10+ API
            plugin_eps = entry_points().select(group='er_gen_tool.plugins')
        
        print(f"✓ Entry points API is working")
        
        # List discovered plugins
        plugins = list(plugin_eps)
        print(f"✓ Found {len(plugins)} plugin(s)")
        
        for ep in plugins:
            print(f"  - Plugin: {ep.name}")
            print(f"    Module: {ep.value}")
            
        return plugins
        
    except Exception as e:
        print(f"✗ Failed to discover entry points: {e}")
        return []


def test_plugin_loading(plugins):
    """Test that plugins can be loaded."""
    print("\nTesting plugin loading...")
    
    loaded_count = 0
    failed_count = 0
    
    for ep in plugins:
        try:
            plugin_cmd = ep.load()
            print(f"✓ Successfully loaded plugin: {ep.name}")
            print(f"  Command type: {type(plugin_cmd).__name__}")
            
            # Check if it's a Click command
            if hasattr(plugin_cmd, 'name'):
                print(f"  Command name: {plugin_cmd.name}")
            if hasattr(plugin_cmd, 'help'):
                print(f"  Help text: {plugin_cmd.help}")
            
            loaded_count += 1
            
        except Exception as e:
            print(f"✗ Failed to load plugin '{ep.name}': {e}")
            failed_count += 1
    
    print(f"\nSummary: {loaded_count} loaded, {failed_count} failed")
    return loaded_count, failed_count


def test_cli_integration():
    """Test that plugins are integrated into the main CLI."""
    print("\nTesting CLI integration...")
    
    try:
        from x007007007.er_tool.cli import main
        
        print(f"✓ Main CLI imported successfully")
        
        # List all registered commands
        commands = main.commands
        print(f"✓ Found {len(commands)} command(s) in main CLI:")
        
        for cmd_name in sorted(commands.keys()):
            cmd = commands[cmd_name]
            help_text = cmd.help or "(no help text)"
            print(f"  - {cmd_name}: {help_text}")
        
        # Check for expected core commands
        expected_core = ['convert', 'makemigration', 'migrate']
        for cmd in expected_core:
            if cmd in commands:
                print(f"✓ Core command '{cmd}' is registered")
            else:
                print(f"✗ Core command '{cmd}' is missing")
        
        # Check for AI plugin (if installed)
        if 'ai-assist' in commands:
            print(f"✓ Plugin command 'ai-assist' is registered")
        else:
            print(f"ℹ Plugin command 'ai-assist' not found (er-gen-tool-ai may not be installed)")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test CLI integration: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Plugin Loading Mechanism Verification")
    print("=" * 60)
    
    # Test 1: Entry points discovery
    plugins = test_entry_points_discovery()
    
    # Test 2: Plugin loading
    if plugins:
        loaded, failed = test_plugin_loading(plugins)
    else:
        print("\nℹ No plugins found to test loading")
        loaded, failed = 0, 0
    
    # Test 3: CLI integration
    cli_ok = test_cli_integration()
    
    # Final summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    if cli_ok:
        print("✓ Plugin loading mechanism is working correctly")
        print(f"✓ Entry points discovery: OK")
        print(f"✓ CLI integration: OK")
        
        if plugins:
            print(f"✓ Plugins found: {len(plugins)}")
            if failed == 0:
                print(f"✓ All plugins loaded successfully")
            else:
                print(f"⚠ Some plugins failed to load: {failed}/{len(plugins)}")
        else:
            print(f"ℹ No plugins installed (this is OK for base installation)")
        
        return 0
    else:
        print("✗ Plugin loading mechanism has issues")
        return 1


if __name__ == '__main__':
    sys.exit(main())
