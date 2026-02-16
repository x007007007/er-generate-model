"""
Property-based tests for PathConfiguration.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.

Feature: field-db-column-and-path-separation
"""
import pytest
from pathlib import Path
from hypothesis import given, settings as hypothesis_settings, strategies as st, assume
from x007007007.er_django.path_configuration import PathConfiguration


# Custom strategies for generating paths
safe_path_component = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(
    lambda s: len(s) < 20 and s not in ['..', '.']
)

relative_path = st.lists(safe_path_component, min_size=1, max_size=3).map(
    lambda parts: '/'.join(parts)
)

absolute_path = st.lists(safe_path_component, min_size=1, max_size=3).map(
    lambda parts: '/' + '/'.join(parts)
)

path_str = st.one_of(relative_path, absolute_path)


class TestProperty4DefaultThirdPartyOutputPathDerivation:
    """
    Property 4: 默认Third_Party_Output_Path推导
    
    **Feature: field-db-column-and-path-separation, Property 4: 默认Third_Party_Output_Path推导**
    **Validates: Requirements 2.2**
    
    For any configuration without third_party_output_path specified,
    the resolved third_party_output_path should equal output_path plus 'third' subdirectory.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=st.one_of(st.none(), relative_path),
        output_path=st.one_of(st.none(), relative_path),
        working_dir=relative_path
    )
    def test_default_third_party_output_path_is_output_path_plus_third(
        self, scan_path, output_path, working_dir
    ):
        """Test that default third_party_output_path is output_path/third."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration without third_party_output_path
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            third_party_output_path=None,  # Not specified
            working_dir=working_dir_path
        )
        
        # Verify third_party_output_path is output_path/third
        expected_third_path = config.output_path / 'third'
        assert config.third_party_output_path == expected_third_path, \
            f"Expected third_party_output_path to be '{expected_third_path}', got '{config.third_party_output_path}'"


class TestProperty5CustomThirdPartyOutputPathPriority:
    """
    Property 5: 自定义Third_Party_Output_Path优先级
    
    **Feature: field-db-column-and-path-separation, Property 5: 自定义Third_Party_Output_Path优先级**
    **Validates: Requirements 2.3**
    
    For any configuration with third_party_output_path specified,
    the resolved third_party_output_path should equal the user-specified value (after path resolution).
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=st.one_of(st.none(), relative_path),
        output_path=st.one_of(st.none(), relative_path),
        third_party_output_path=relative_path,
        working_dir=relative_path
    )
    def test_custom_third_party_output_path_is_used(
        self, scan_path, output_path, third_party_output_path, working_dir
    ):
        """Test that custom third_party_output_path is used when specified."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with custom third_party_output_path
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            third_party_output_path=third_party_output_path,
            working_dir=working_dir_path
        )
        
        # Calculate expected path (relative to output_path)
        expected_third_path = config.output_path / third_party_output_path
        
        # Verify third_party_output_path uses custom value
        assert config.third_party_output_path == expected_third_path, \
            f"Expected third_party_output_path to be '{expected_third_path}', got '{config.third_party_output_path}'"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=st.one_of(st.none(), relative_path),
        output_path=st.one_of(st.none(), relative_path),
        third_party_output_path=absolute_path,
        working_dir=relative_path
    )
    def test_absolute_third_party_output_path_is_preserved(
        self, scan_path, output_path, third_party_output_path, working_dir
    ):
        """Test that absolute third_party_output_path is preserved as-is."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with absolute third_party_output_path
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            third_party_output_path=third_party_output_path,
            working_dir=working_dir_path
        )
        
        # Verify absolute path is preserved
        expected_third_path = Path(third_party_output_path)
        assert config.third_party_output_path == expected_third_path, \
            f"Expected third_party_output_path to be '{expected_third_path}', got '{config.third_party_output_path}'"


class TestProperty8DefaultPackagePrefixDerivation:
    """
    Property 8: 默认包名前缀推导
    
    **Feature: field-db-column-and-path-separation, Property 8: 默认包名前缀推导**
    **Validates: Requirements 2.7**
    
    For any configuration without third_party_package_prefix specified,
    the prefix should equal the last directory name of third_party_output_path.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=st.one_of(st.none(), relative_path),
        output_path=st.one_of(st.none(), relative_path),
        third_party_output_path=st.one_of(st.none(), relative_path),
        working_dir=relative_path
    )
    def test_default_package_prefix_is_last_directory_name(
        self, scan_path, output_path, third_party_output_path, working_dir
    ):
        """Test that default package prefix is the last directory name of third_party_output_path."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration without package prefix
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            third_party_output_path=third_party_output_path,
            third_party_package_prefix=None,  # Not specified
            working_dir=working_dir_path
        )
        
        # Verify prefix is the last directory name
        expected_prefix = config.third_party_output_path.name
        assert config.third_party_package_prefix == expected_prefix, \
            f"Expected package prefix to be '{expected_prefix}', got '{config.third_party_package_prefix}'"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        third_party_output_path=relative_path,
        working_dir=relative_path
    )
    def test_package_prefix_matches_path_name(
        self, third_party_output_path, working_dir
    ):
        """Test that package prefix always matches the path's last component."""
        working_dir_path = Path('/tmp') / working_dir
        
        config = PathConfiguration.from_options(
            third_party_output_path=third_party_output_path,
            working_dir=working_dir_path
        )
        
        # Extract expected prefix from path
        path_parts = third_party_output_path.split('/')
        expected_prefix = path_parts[-1]
        
        assert config.third_party_package_prefix == expected_prefix, \
            f"Expected prefix '{expected_prefix}', got '{config.third_party_package_prefix}'"


class TestProperty10DefaultScanPathValue:
    """
    Property 10: 默认Scan_Path值
    
    **Feature: field-db-column-and-path-separation, Property 10: 默认Scan_Path值**
    **Validates: Requirements 3.3**
    
    For any configuration without scan_path specified,
    the resolved scan_path should equal 'src' directory (relative to working directory).
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(working_dir=relative_path)
    def test_default_scan_path_is_src(self, working_dir):
        """Test that default scan_path is 'src'."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration without scan_path
        config = PathConfiguration.from_options(
            scan_path=None,  # Not specified
            working_dir=working_dir_path
        )
        
        # Verify scan_path is working_dir/src
        expected_scan_path = working_dir_path / 'src'
        assert config.scan_path == expected_scan_path, \
            f"Expected scan_path to be '{expected_scan_path}', got '{config.scan_path}'"


class TestProperty11OutputPathInheritsScanPath:
    """
    Property 11: Output_Path继承Scan_Path
    
    **Feature: field-db-column-and-path-separation, Property 11: Output_Path继承Scan_Path**
    **Validates: Requirements 3.4**
    
    For any configuration with scan_path specified but output_path not specified,
    the resolved output_path should equal scan_path.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=relative_path,
        working_dir=relative_path
    )
    def test_output_path_inherits_scan_path(self, scan_path, working_dir):
        """Test that output_path inherits scan_path when not specified."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with scan_path but no output_path
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=None,  # Not specified
            working_dir=working_dir_path
        )
        
        # Verify output_path equals scan_path
        assert config.output_path == config.scan_path, \
            f"Expected output_path to equal scan_path '{config.scan_path}', got '{config.output_path}'"


class TestProperty13ScanPathOnlyInheritanceChain:
    """
    Property 13: 仅Scan_Path配置的继承链
    
    **Feature: field-db-column-and-path-separation, Property 13: 仅Scan_Path配置的继承链**
    **Validates: Requirements 4.1**
    
    For any configuration with only scan_path specified,
    output_path should equal scan_path, and
    third_party_output_path should equal scan_path plus 'third' subdirectory.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=relative_path,
        working_dir=relative_path
    )
    def test_scan_path_only_inheritance_chain(self, scan_path, working_dir):
        """Test complete inheritance chain when only scan_path is specified."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with only scan_path
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=None,
            third_party_output_path=None,
            working_dir=working_dir_path
        )
        
        # Verify output_path equals scan_path
        assert config.output_path == config.scan_path, \
            f"Expected output_path to equal scan_path '{config.scan_path}', got '{config.output_path}'"
        
        # Verify third_party_output_path equals scan_path/third
        expected_third_path = config.scan_path / 'third'
        assert config.third_party_output_path == expected_third_path, \
            f"Expected third_party_output_path to be '{expected_third_path}', got '{config.third_party_output_path}'"


class TestProperty14ScanPathAndOutputPathInheritanceChain:
    """
    Property 14: Scan_Path和Output_Path配置的继承链
    
    **Feature: field-db-column-and-path-separation, Property 14: Scan_Path和Output_Path配置的继承链**
    **Validates: Requirements 4.2**
    
    For any configuration with scan_path and output_path specified but not third_party_output_path,
    third_party_output_path should equal output_path plus 'third' subdirectory.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=relative_path,
        output_path=relative_path,
        working_dir=relative_path
    )
    def test_scan_and_output_path_inheritance_chain(self, scan_path, output_path, working_dir):
        """Test inheritance chain when scan_path and output_path are specified."""
        # Ensure scan_path and output_path are different
        assume(scan_path != output_path)
        
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with scan_path and output_path
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            third_party_output_path=None,
            working_dir=working_dir_path
        )
        
        # Verify third_party_output_path equals output_path/third
        expected_third_path = config.output_path / 'third'
        assert config.third_party_output_path == expected_third_path, \
            f"Expected third_party_output_path to be '{expected_third_path}', got '{config.third_party_output_path}'"


class TestProperty15CompleteConfigurationPriority:
    """
    Property 15: 完整配置优先级
    
    **Feature: field-db-column-and-path-separation, Property 15: 完整配置优先级**
    **Validates: Requirements 4.3**
    
    For any configuration with all path parameters specified,
    all resolved path values should equal user-specified values (after path resolution).
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=relative_path,
        output_path=relative_path,
        third_party_output_path=relative_path,
        third_party_package_prefix=safe_path_component,
        working_dir=relative_path
    )
    def test_all_specified_values_are_used(
        self, scan_path, output_path, third_party_output_path, 
        third_party_package_prefix, working_dir
    ):
        """Test that all user-specified values are used when provided."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with all parameters
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            third_party_output_path=third_party_output_path,
            third_party_package_prefix=third_party_package_prefix,
            working_dir=working_dir_path
        )
        
        # Verify all paths are resolved correctly
        expected_scan_path = working_dir_path / scan_path
        expected_output_path = working_dir_path / output_path
        expected_third_path = expected_output_path / third_party_output_path
        
        assert config.scan_path == expected_scan_path, \
            f"Expected scan_path '{expected_scan_path}', got '{config.scan_path}'"
        assert config.output_path == expected_output_path, \
            f"Expected output_path '{expected_output_path}', got '{config.output_path}'"
        assert config.third_party_output_path == expected_third_path, \
            f"Expected third_party_output_path '{expected_third_path}', got '{config.third_party_output_path}'"
        assert config.third_party_package_prefix == third_party_package_prefix, \
            f"Expected prefix '{third_party_package_prefix}', got '{config.third_party_package_prefix}'"


class TestProperty16RelativePathResolutionBase:
    """
    Property 16: 相对路径解析基准
    
    **Feature: field-db-column-and-path-separation, Property 16: 相对路径解析基准**
    **Validates: Requirements 4.4**
    
    For any configuration using relative paths for scan_path or output_path,
    the resolved absolute paths should be relative to the current working directory.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=relative_path,
        output_path=relative_path,
        working_dir=relative_path
    )
    def test_relative_paths_resolved_from_working_dir(
        self, scan_path, output_path, working_dir
    ):
        """Test that relative paths are resolved from working directory."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with relative paths
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            working_dir=working_dir_path
        )
        
        # Verify paths are resolved relative to working_dir
        expected_scan_path = working_dir_path / scan_path
        expected_output_path = working_dir_path / output_path
        
        assert config.scan_path == expected_scan_path, \
            f"Expected scan_path '{expected_scan_path}', got '{config.scan_path}'"
        assert config.output_path == expected_output_path, \
            f"Expected output_path '{expected_output_path}', got '{config.output_path}'"
        
        # Verify paths are absolute
        assert config.scan_path.is_absolute(), "scan_path should be absolute"
        assert config.output_path.is_absolute(), "output_path should be absolute"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        scan_path=absolute_path,
        output_path=absolute_path,
        working_dir=relative_path
    )
    def test_absolute_paths_preserved(self, scan_path, output_path, working_dir):
        """Test that absolute paths are preserved as-is."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with absolute paths
        config = PathConfiguration.from_options(
            scan_path=scan_path,
            output_path=output_path,
            working_dir=working_dir_path
        )
        
        # Verify absolute paths are preserved
        assert config.scan_path == Path(scan_path), \
            f"Expected scan_path '{scan_path}', got '{config.scan_path}'"
        assert config.output_path == Path(output_path), \
            f"Expected output_path '{output_path}', got '{config.output_path}'"


class TestProperty17ThirdPartyRelativePathResolutionBase:
    """
    Property 17: Third_Party相对路径解析基准
    
    **Feature: field-db-column-and-path-separation, Property 17: Third_Party相对路径解析基准**
    **Validates: Requirements 4.5**
    
    For any configuration using relative path for third_party_output_path,
    the resolved absolute path should be relative to output_path.
    """
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        output_path=relative_path,
        third_party_output_path=relative_path,
        working_dir=relative_path
    )
    def test_third_party_relative_path_resolved_from_output_path(
        self, output_path, third_party_output_path, working_dir
    ):
        """Test that third_party relative path is resolved from output_path."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with relative third_party_output_path
        config = PathConfiguration.from_options(
            output_path=output_path,
            third_party_output_path=third_party_output_path,
            working_dir=working_dir_path
        )
        
        # Verify third_party_output_path is resolved relative to output_path
        expected_output_path = working_dir_path / output_path
        expected_third_path = expected_output_path / third_party_output_path
        
        assert config.third_party_output_path == expected_third_path, \
            f"Expected third_party_output_path '{expected_third_path}', got '{config.third_party_output_path}'"
        
        # Verify path is absolute
        assert config.third_party_output_path.is_absolute(), \
            "third_party_output_path should be absolute"
    
    @hypothesis_settings(max_examples=100, deadline=None)
    @given(
        output_path=relative_path,
        third_party_output_path=absolute_path,
        working_dir=relative_path
    )
    def test_third_party_absolute_path_preserved(
        self, output_path, third_party_output_path, working_dir
    ):
        """Test that absolute third_party_output_path is preserved as-is."""
        working_dir_path = Path('/tmp') / working_dir
        
        # Create configuration with absolute third_party_output_path
        config = PathConfiguration.from_options(
            output_path=output_path,
            third_party_output_path=third_party_output_path,
            working_dir=working_dir_path
        )
        
        # Verify absolute path is preserved
        expected_third_path = Path(third_party_output_path)
        assert config.third_party_output_path == expected_third_path, \
            f"Expected third_party_output_path '{expected_third_path}', got '{config.third_party_output_path}'"
