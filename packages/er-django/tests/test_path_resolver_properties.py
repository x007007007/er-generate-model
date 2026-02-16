"""
Property-based tests for PathResolver.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.

Feature: field-db-column-and-path-separation
"""
import pytest
from pathlib import Path
from unittest.mock import Mock
from hypothesis import given, settings as hypothesis_settings, strategies as st, assume
from x007007007.er_django.path_configuration import PathConfiguration
from x007007007.er_django.path_resolver import PathResolver


# Custom strategies for generating paths and package names
safe_path_component = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
    lambda s: len(s) < 20 and s not in ['..', '.']
)

relative_path = st.lists(safe_path_component, min_size=1, max_size=3).map(
    lambda parts: '/'.join(parts)
)

# Strategy for generating Python package names (e.g., "django.contrib.auth")
package_name = st.lists(safe_path_component, min_size=1, max_size=4).map(
    lambda parts: '.'.join(parts)
)


class TestProperty6ThirdPartyPackagePrefixAddition:
    """
    Property 6: 三方包名前缀添加
    
    **Feature: field-db-column-and-path-separation, Property 6: 三方包名前缀添加**
    **Validates: Requirements 2.4**
    
    For any application marked as third-party,
    its resolved package name should start with third_party_package_prefix,
    in the format "{prefix}.{original_package}".
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        app_package_name=package_name,
        third_party_prefix=safe_path_component,
        working_dir=relative_path
    )
    def test_third_party_package_has_prefix(
        self, app_package_name, third_party_prefix, working_dir
    ):
        """Test that third-party packages get the configured prefix."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with custom prefix
        config = PathConfiguration.from_options(
            third_party_package_prefix=third_party_prefix,
            working_dir=working_dir_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.name = app_package_name
        app_config.label = app_package_name.split('.')[-1]
        
        # Resolve package name for third-party
        resolved_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Verify prefix is added
        expected_name = f"{third_party_prefix}.{app_package_name}"
        assert resolved_name == expected_name, \
            f"Expected package name '{expected_name}', got '{resolved_name}'"
        
        # Verify it starts with the prefix
        assert resolved_name.startswith(f"{third_party_prefix}."), \
            f"Package name should start with '{third_party_prefix}.'"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        app_package_name=package_name,
        third_party_prefix=safe_path_component,
        working_dir=relative_path
    )
    def test_non_third_party_package_has_no_prefix(
        self, app_package_name, third_party_prefix, working_dir
    ):
        """Test that non-third-party packages don't get a prefix."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with custom prefix
        config = PathConfiguration.from_options(
            third_party_package_prefix=third_party_prefix,
            working_dir=working_dir_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.name = app_package_name
        app_config.label = app_package_name.split('.')[-1]
        
        # Resolve package name for non-third-party
        resolved_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=False
        )
        
        # Verify no prefix is added - the resolved name should be exactly the original
        assert resolved_name == app_package_name, \
            f"Expected package name '{app_package_name}', got '{resolved_name}'"


class TestProperty7CustomPackagePrefixUsage:
    """
    Property 7: 自定义包名前缀使用
    
    **Feature: field-db-column-and-path-separation, Property 7: 自定义包名前缀使用**
    **Validates: Requirements 2.6**
    
    For any configuration with third_party_package_prefix specified,
    third-party packages should use the user-specified prefix value.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        app_package_name=package_name,
        custom_prefix=safe_path_component,
        working_dir=relative_path
    )
    def test_custom_prefix_is_used(
        self, app_package_name, custom_prefix, working_dir
    ):
        """Test that custom package prefix is used when specified."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with custom prefix
        config = PathConfiguration.from_options(
            third_party_package_prefix=custom_prefix,
            working_dir=working_dir_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.name = app_package_name
        app_config.label = app_package_name.split('.')[-1]
        
        # Resolve package name for third-party
        resolved_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Verify custom prefix is used
        expected_name = f"{custom_prefix}.{app_package_name}"
        assert resolved_name == expected_name, \
            f"Expected package name '{expected_name}', got '{resolved_name}'"
        
        # Verify the prefix matches exactly
        actual_prefix = resolved_name.split('.')[0]
        assert actual_prefix == custom_prefix, \
            f"Expected prefix '{custom_prefix}', got '{actual_prefix}'"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        app_package_name=package_name,
        prefix1=safe_path_component,
        prefix2=safe_path_component,
        working_dir=relative_path
    )
    def test_different_prefixes_produce_different_names(
        self, app_package_name, prefix1, prefix2, working_dir
    ):
        """Test that different prefixes produce different package names."""
        # Ensure prefixes are different
        assume(prefix1 != prefix2)
        
        working_dir_path = Path('/tmp') / working_dir
        
        # Create two configurations with different prefixes
        config1 = PathConfiguration.from_options(
            third_party_package_prefix=prefix1,
            working_dir=working_dir_path
        )
        resolver1 = PathResolver(config1)
        
        config2 = PathConfiguration.from_options(
            third_party_package_prefix=prefix2,
            working_dir=working_dir_path
        )
        resolver2 = PathResolver(config2)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.name = app_package_name
        app_config.label = app_package_name.split('.')[-1]
        
        # Resolve with both prefixes
        resolved_name1 = resolver1.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        resolved_name2 = resolver2.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Verify different prefixes produce different names
        assert resolved_name1 != resolved_name2, \
            f"Different prefixes should produce different names: '{resolved_name1}' vs '{resolved_name2}'"
        
        # Verify both have correct format
        assert resolved_name1 == f"{prefix1}.{app_package_name}"
        assert resolved_name2 == f"{prefix2}.{app_package_name}"


class TestProperty12PathSeparationCorrectness:
    """
    Property 12: 路径分离功能正确性
    
    **Feature: field-db-column-and-path-separation, Property 12: 路径分离功能正确性**
    **Validates: Requirements 3.6**
    
    For any configuration with different scan_path and output_path,
    the system should read source code from scan_path and output generated code to output_path.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=relative_path,
        output_path=relative_path,
        app_package_name=package_name,
        working_dir=relative_path
    )
    def test_output_path_independent_of_scan_path(
        self, scan_path, output_path, app_package_name, working_dir
    ):
        """Test that output path is independent of scan path."""
        # Ensure scan_path and output_path are different
        assume(scan_path != output_path)
        
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with different scan and output paths
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            working_dir=working_dir_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.name = app_package_name
        app_config.label = app_package_name.split('.')[-1]
        
        # Get scan path
        resolved_scan_path = resolver.get_scan_path()
        
        # Get output path
        resolved_output_path = resolver.resolve_output_path(
            app_config=app_config,
            format='toml',
            is_third_party=False
        )
        
        # Verify scan path is correct
        expected_scan_path = working_dir_path / scan_path
        assert resolved_scan_path == expected_scan_path, \
            f"Expected scan path '{expected_scan_path}', got '{resolved_scan_path}'"
        
        # Verify output path is based on output_path, not scan_path
        expected_output_base = working_dir_path / output_path
        assert str(resolved_output_path).startswith(str(expected_output_base)), \
            f"Output path '{resolved_output_path}' should start with '{expected_output_base}'"
        
        # The key property: scan_path and output_path are independent
        # The output path should be constructed from output_path + package_name
        # not from scan_path
        assert config.scan_path != config.output_path or scan_path == output_path, \
            "When scan_path and output_path are different in config, they should remain different"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=relative_path,
        output_path=relative_path,
        third_party_output_path=relative_path,
        app_package_name=package_name,
        working_dir=relative_path
    )
    def test_third_party_output_path_independent_of_scan_path(
        self, scan_path, output_path, third_party_output_path, app_package_name, working_dir
    ):
        """Test that third-party output path is independent of scan path."""
        # Ensure paths are different
        assume(scan_path != output_path)
        assume(third_party_output_path != scan_path)
        
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with all paths different
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            third_party_output_path=third_party_output_path,
            working_dir=working_dir_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.name = app_package_name
        app_config.label = app_package_name.split('.')[-1]
        
        # Get scan path
        resolved_scan_path = resolver.get_scan_path()
        
        # Get third-party output path
        resolved_output_path = resolver.resolve_output_path(
            app_config=app_config,
            format='toml',
            is_third_party=True
        )
        
        # Verify scan path is correct
        expected_scan_path = working_dir_path / scan_path
        assert resolved_scan_path == expected_scan_path, \
            f"Expected scan path '{expected_scan_path}', got '{resolved_scan_path}'"
        
        # Verify third-party output path is based on third_party_output_path
        expected_output_base = working_dir_path / output_path / third_party_output_path
        assert str(resolved_output_path).startswith(str(expected_output_base)), \
            f"Third-party output path '{resolved_output_path}' should start with '{expected_output_base}'"
        
        # The key property: third-party output uses third_party_output_path, not scan_path
        # Verify the base directory is from third_party_output_path
        assert config.third_party_output_path in resolved_output_path.parents or \
               config.third_party_output_path == resolved_output_path.parent, \
            f"Third-party output path should be under third_party_output_path"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=relative_path,
        output_path=relative_path,
        working_dir=relative_path
    )
    def test_scan_path_accessible_via_get_scan_path(
        self, scan_path, output_path, working_dir
    ):
        """Test that scan path is accessible via get_scan_path method."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            working_dir=working_dir_path
        )
        resolver = PathResolver(config)
        
        # Get scan path
        resolved_scan_path = resolver.get_scan_path()
        
        # Verify it matches the configured scan path
        expected_scan_path = working_dir_path / scan_path
        assert resolved_scan_path == expected_scan_path, \
            f"Expected scan path '{expected_scan_path}', got '{resolved_scan_path}'"
        
        # Verify it's different from output path (if they were configured differently)
        if scan_path != output_path:
            expected_output_path = working_dir_path / output_path
            assert resolved_scan_path != expected_output_path, \
                "Scan path should be different from output path"
