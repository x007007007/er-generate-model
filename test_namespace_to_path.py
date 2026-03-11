#!/usr/bin/env python3
"""Quick test to verify _namespace_to_path implementation"""

import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages/er-gen-core/src'))

from x007007007.er.namespace_resolver import NamespaceResolver

def test_namespace_to_path():
    """Test the _namespace_to_path method"""
    resolver = NamespaceResolver(search_paths=["src/", "src/third/"])
    
    # Test case 1: Simple namespace
    result = resolver._namespace_to_path("myapp.models")
    expected = "myapp/models.toml"
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"✓ Test 1 passed: 'myapp.models' -> '{result}'")
    
    # Test case 2: Multi-level namespace
    result = resolver._namespace_to_path("kinkotech.common.models.base")
    expected = "kinkotech/common/models/base.toml"
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"✓ Test 2 passed: 'kinkotech.common.models.base' -> '{result}'")
    
    # Test case 3: Django-style namespace
    result = resolver._namespace_to_path("django.contrib.auth.models")
    expected = "django/contrib/auth/models.toml"
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"✓ Test 3 passed: 'django.contrib.auth.models' -> '{result}'")
    
    # Test case 4: Empty namespace (should raise ValueError)
    try:
        resolver._namespace_to_path("")
        print("✗ Test 4 failed: Empty namespace should raise ValueError")
        sys.exit(1)
    except ValueError as e:
        print(f"✓ Test 4 passed: Empty namespace raises ValueError: {e}")
    
    # Test case 5: Path traversal attempt (should raise ValueError)
    try:
        resolver._namespace_to_path("../etc/passwd")
        print("✗ Test 5 failed: Path traversal should raise ValueError")
        sys.exit(1)
    except ValueError as e:
        print(f"✓ Test 5 passed: Path traversal raises ValueError: {e}")
    
    # Test case 6: Absolute path attempt (should raise ValueError)
    try:
        resolver._namespace_to_path("/etc/passwd")
        print("✗ Test 6 failed: Absolute path should raise ValueError")
        sys.exit(1)
    except ValueError as e:
        print(f"✓ Test 6 passed: Absolute path raises ValueError: {e}")
    
    # Test case 7: Windows path separator (should raise ValueError)
    try:
        resolver._namespace_to_path("myapp\\models")
        print("✗ Test 7 failed: Windows path separator should raise ValueError")
        sys.exit(1)
    except ValueError as e:
        print(f"✓ Test 7 passed: Windows path separator raises ValueError: {e}")
    
    # Test case 8: Forward slash (should raise ValueError)
    try:
        resolver._namespace_to_path("myapp/models")
        print("✗ Test 8 failed: Forward slash should raise ValueError")
        sys.exit(1)
    except ValueError as e:
        print(f"✓ Test 8 passed: Forward slash raises ValueError: {e}")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_namespace_to_path()


def test_resolve_batch():
    """Test the resolve_batch method"""
    import tempfile
    import shutil
    
    # Create a temporary directory structure for testing
    temp_dir = tempfile.mkdtemp()
    try:
        # Create test TOML files
        src_dir = os.path.join(temp_dir, "src")
        third_dir = os.path.join(temp_dir, "src", "third")
        os.makedirs(os.path.join(src_dir, "myapp", "models"), exist_ok=True)
        os.makedirs(os.path.join(third_dir, "django", "contrib", "auth"), exist_ok=True)
        
        # Create test files
        with open(os.path.join(src_dir, "myapp", "models", "user.toml"), "w") as f:
            f.write("[entity.User]\n")
        with open(os.path.join(third_dir, "django", "contrib", "auth", "models.toml"), "w") as f:
            f.write("[entity.AbstractUser]\n")
        
        # Initialize resolver with temp directory
        resolver = NamespaceResolver(
            search_paths=[
                os.path.join(temp_dir, "src") + os.sep,
                os.path.join(temp_dir, "src", "third") + os.sep
            ]
        )
        
        # Test batch resolution
        namespaces = [
            "myapp.models.user",
            "django.contrib.auth.models",
            "nonexistent.module"
        ]
        results = resolver.resolve_batch(namespaces)
        
        # Verify results
        assert "myapp.models.user" in results, "myapp.models.user should be in results"
        assert results["myapp.models.user"] is not None, "myapp.models.user should resolve successfully"
        assert results["myapp.models.user"].location_type == "project", "myapp.models.user should be project type"
        print(f"✓ Test 1 passed: myapp.models.user resolved as project")
        
        assert "django.contrib.auth.models" in results, "django.contrib.auth.models should be in results"
        assert results["django.contrib.auth.models"] is not None, "django.contrib.auth.models should resolve successfully"
        assert results["django.contrib.auth.models"].location_type == "third-party", "django.contrib.auth.models should be third-party type"
        print(f"✓ Test 2 passed: django.contrib.auth.models resolved as third-party")
        
        assert "nonexistent.module" in results, "nonexistent.module should be in results"
        assert results["nonexistent.module"] is None, "nonexistent.module should return None"
        print(f"✓ Test 3 passed: nonexistent.module returned None")
        
        print("\n✅ All resolve_batch tests passed!")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_cache_invalidation():
    """Test cache invalidation methods"""
    import tempfile
    import shutil
    
    # Create a temporary directory structure for testing
    temp_dir = tempfile.mkdtemp()
    try:
        # Create test TOML file
        src_dir = os.path.join(temp_dir, "src")
        os.makedirs(os.path.join(src_dir, "myapp", "models"), exist_ok=True)
        
        test_file = os.path.join(src_dir, "myapp", "models", "user.toml")
        with open(test_file, "w") as f:
            f.write("[entity.User]\n")
        
        # Initialize resolver
        resolver = NamespaceResolver(
            search_paths=[os.path.join(temp_dir, "src") + os.sep]
        )
        
        # Test 1: Verify caching works
        result1 = resolver.resolve("myapp.models.user")
        assert result1 is not None, "First resolve should succeed"
        assert "myapp.models.user" in resolver._cache, "Result should be cached"
        print(f"✓ Test 1 passed: Result cached after first resolve")
        
        # Test 2: Verify cache is used
        result2 = resolver.resolve("myapp.models.user")
        assert result2 is result1, "Second resolve should return cached result"
        print(f"✓ Test 2 passed: Cache is used on second resolve")
        
        # Test 3: Test invalidate() method
        resolver.invalidate("myapp.models.user")
        assert "myapp.models.user" not in resolver._cache, "Cache should be invalidated"
        print(f"✓ Test 3 passed: invalidate() removes specific namespace from cache")
        
        # Test 4: Verify resolve works after invalidation
        result3 = resolver.resolve("myapp.models.user")
        assert result3 is not None, "Resolve should work after invalidation"
        assert "myapp.models.user" in resolver._cache, "Result should be cached again"
        print(f"✓ Test 4 passed: Resolve works after invalidation and re-caches")
        
        # Test 5: Test clear_cache() method
        resolver.clear_cache()
        assert len(resolver._cache) == 0, "Cache should be empty after clear_cache()"
        print(f"✓ Test 5 passed: clear_cache() removes all cached results")
        
        # Test 6: Verify resolve works after clear
        result4 = resolver.resolve("myapp.models.user")
        assert result4 is not None, "Resolve should work after clear_cache()"
        assert "myapp.models.user" in resolver._cache, "Result should be cached again"
        print(f"✓ Test 6 passed: Resolve works after clear_cache() and re-caches")
        
        # Test 7: Test invalidate on non-existent namespace (should not raise error)
        resolver.invalidate("nonexistent.module")
        print(f"✓ Test 7 passed: invalidate() on non-existent namespace doesn't raise error")
        
        print("\n✅ All cache invalidation tests passed!")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing _namespace_to_path method")
    print("=" * 60)
    test_namespace_to_path()
    
    print("\n" + "=" * 60)
    print("Testing resolve_batch method")
    print("=" * 60)
    test_resolve_batch()
    
    print("\n" + "=" * 60)
    print("Testing cache invalidation methods")
    print("=" * 60)
    test_cache_invalidation()
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! 🎉")
    print("=" * 60)


if __name__ == "__main__":
    # Check if we should run all tests or just the original test
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all_tests()
    else:
        test_namespace_to_path()
