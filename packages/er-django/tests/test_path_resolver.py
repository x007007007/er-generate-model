"""Unit tests for PathResolver."""

import os
from pathlib import Path
from unittest.mock import Mock

import pytest

from x007007007.er_django.path_configuration import PathConfiguration
from x007007007.er_django.path_resolver import PathResolver


class TestPathResolverResolveOutputPath:
    """Tests for PathResolver.resolve_output_path() method."""

    def test_simple_package_name(self, tmp_path):
        """Test path resolution for simple package name."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve output path
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml"
        )
        
        # Should output to src/myapp/models.toml
        expected = tmp_path / "src" / "myapp" / "models.toml"
        assert output_path == expected

    def test_nested_package_path(self, tmp_path):
        """Test path resolution for nested package path."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig with nested package
        app_config = Mock()
        app_config.label = "account"
        app_config.name = "kinkotech.common.domains.account"
        
        # Resolve output path
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml"
        )
        
        # Should output to src/kinkotech/common/domains/account/models.toml
        expected = tmp_path / "src" / "kinkotech" / "common" / "domains" / "account" / "models.toml"
        assert output_path == expected

    def test_django_contrib_app(self, tmp_path):
        """Test path resolution for Django contrib app."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "output"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig for django.contrib.auth
        app_config = Mock()
        app_config.label = "auth"
        app_config.name = "django.contrib.auth"
        
        # Resolve output path
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml"
        )
        
        # Should output to output/django/contrib/auth/models.toml
        expected = tmp_path / "output" / "django" / "contrib" / "auth" / "models.toml"
        assert output_path == expected

    def test_absolute_base_dir(self, tmp_path):
        """Test path resolution with absolute base_dir."""
        # Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Create configuration with absolute path
        config = PathConfiguration.from_options(
            output_path=str(output_dir),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve with absolute base_dir
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml"
        )
        
        # Should output to output_dir/myapp/models.toml
        expected = output_dir / "myapp" / "models.toml"
        assert output_path == expected

    def test_relative_base_dir(self, tmp_path):
        """Test path resolution with relative base_dir."""
        # Create configuration with relative path
        config = PathConfiguration.from_options(
            output_path="output",
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve with relative base_dir
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml"
        )
        
        # Should output to working_dir/output/myapp/models.toml
        expected = tmp_path / "output" / "myapp" / "models.toml"
        assert output_path == expected

    def test_different_formats(self, tmp_path):
        """Test path resolution with different output formats."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Test TOML format
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml"
        )
        assert output_path == tmp_path / "src" / "myapp" / "models.toml"
        
        # Test Mermaid format
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="mermaid"
        )
        assert output_path == tmp_path / "src" / "myapp" / "models.mermaid"
        
        # Test PlantUML format
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="plantuml"
        )
        assert output_path == tmp_path / "src" / "myapp" / "models.plantuml"

    def test_deeply_nested_package(self, tmp_path):
        """Test path resolution for deeply nested package structure."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig with deeply nested package
        app_config = Mock()
        app_config.label = "ccc"
        app_config.name = "aaa.bbb.ccc"
        
        # Resolve output path
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml"
        )
        
        # Should maintain full nested structure
        expected = tmp_path / "src" / "aaa" / "bbb" / "ccc" / "models.toml"
        assert output_path == expected

    def test_error_when_package_name_empty(self, tmp_path):
        """Test fail-fast when package name is empty."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig with empty name
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = ""
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            resolver.resolve_output_path(
                app_config=app_config,
                format="toml"
            )
        
        # Error message should be clear
        assert "Cannot determine package path" in str(exc_info.value)
        assert "myapp" in str(exc_info.value)

    def test_path_object_as_base_dir(self, tmp_path):
        """Test that base_dir can be a Path object."""
        # Create configuration with Path object
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Pass Path object as base_dir
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml"
        )
        
        assert output_path == tmp_path / "src" / "myapp" / "models.toml"

    def test_output_independent_of_filesystem_location(self, tmp_path):
        """Test that output path is independent of app's filesystem location."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Create two apps with same package name but different filesystem locations
        
        # App 1: located at /some/path/myapp
        app_config_1 = Mock()
        app_config_1.label = "myapp"
        app_config_1.name = "myapp"
        app_config_1.path = "/some/path/myapp"
        
        # App 2: located at /different/location/myapp
        app_config_2 = Mock()
        app_config_2.label = "myapp"
        app_config_2.name = "myapp"
        app_config_2.path = "/different/location/myapp"
        
        # Both should produce the same output path
        output_path_1 = resolver.resolve_output_path(
            app_config=app_config_1,
            format="toml"
        )
        
        output_path_2 = resolver.resolve_output_path(
            app_config=app_config_2,
            format="toml"
        )
        
        # Paths should be identical
        assert output_path_1 == output_path_2
        assert output_path_1 == tmp_path / "src" / "myapp" / "models.toml"

    def test_complex_nested_package_independent_of_location(self, tmp_path):
        """Test complex nested package produces same output regardless of filesystem location."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # App located outside project
        app_config_1 = Mock()
        app_config_1.label = "account"
        app_config_1.name = "kinkotech.common.domains.account"
        app_config_1.path = "/usr/lib/python/site-packages/kinkotech/common/domains/account"
        
        # App located inside project
        app_config_2 = Mock()
        app_config_2.label = "account"
        app_config_2.name = "kinkotech.common.domains.account"
        app_config_2.path = "/home/user/project/src/kinkotech/common/domains/account"
        
        # Both should produce the same output path
        output_path_1 = resolver.resolve_output_path(
            app_config=app_config_1,
            format="toml"
        )
        
        output_path_2 = resolver.resolve_output_path(
            app_config=app_config_2,
            format="toml"
        )
        
        # Paths should be identical
        assert output_path_1 == output_path_2
        expected = tmp_path / "src" / "kinkotech" / "common" / "domains" / "account" / "models.toml"
        assert output_path_1 == expected

    def test_third_party_output_path(self, tmp_path):
        """Test that third-party packages use third_party_output_path."""
        # Create configuration with third-party output path
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_output_path=str(tmp_path / "third"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig for third-party package
        app_config = Mock()
        app_config.label = "auth"
        app_config.name = "django.contrib.auth"
        
        # Resolve output path for third-party package
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml",
            is_third_party=True
        )
        
        # Should output to third/django/contrib/auth/models.toml
        expected = tmp_path / "third" / "django" / "contrib" / "auth" / "models.toml"
        assert output_path == expected

    def test_non_third_party_uses_output_path(self, tmp_path):
        """Test that non-third-party packages use output_path."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_output_path=str(tmp_path / "third"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig for regular package
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve output path for regular package
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml",
            is_third_party=False
        )
        
        # Should output to src/myapp/models.toml
        expected = tmp_path / "src" / "myapp" / "models.toml"
        assert output_path == expected


class TestPathResolverResolvePackageName:
    """Tests for PathResolver.resolve_package_name() method."""

    def test_regular_package_name(self, tmp_path):
        """Test package name resolution for regular packages."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve package name
        package_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=False
        )
        
        # Should return package name as-is
        assert package_name == "myapp"

    def test_third_party_package_with_prefix(self, tmp_path):
        """Test package name resolution for third-party packages with prefix."""
        # Create configuration with third-party prefix
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_package_prefix="third",
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig for third-party package
        app_config = Mock()
        app_config.label = "auth"
        app_config.name = "django.contrib.auth"
        
        # Resolve package name for third-party
        package_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Should add prefix
        assert package_name == "third.django.contrib.auth"

    def test_third_party_package_without_prefix(self, tmp_path):
        """Test third-party package when prefix is None."""
        # Create configuration without prefix
        config = PathConfiguration(
            scan_path=tmp_path / "src",
            output_path=tmp_path / "src",
            third_party_output_path=tmp_path / "third",
            third_party_package_prefix=None
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "auth"
        app_config.name = "django.contrib.auth"
        
        # Resolve package name
        package_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Should return package name as-is when prefix is None
        assert package_name == "django.contrib.auth"

    def test_nested_package_name(self, tmp_path):
        """Test package name resolution for nested packages."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_package_prefix="external",
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig with nested package
        app_config = Mock()
        app_config.label = "account"
        app_config.name = "kinkotech.common.domains.account"
        
        # Resolve as third-party
        package_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Should add prefix to full package name
        assert package_name == "external.kinkotech.common.domains.account"

    def test_error_when_package_name_empty(self, tmp_path):
        """Test error handling when package name is empty."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig with empty name
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = ""
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            resolver.resolve_package_name(
                app_config=app_config,
                is_third_party=False
            )
        
        # Error message should be clear
        assert "Cannot determine package path" in str(exc_info.value)
        assert "myapp" in str(exc_info.value)


class TestPathResolverGetScanPath:
    """Tests for PathResolver.get_scan_path() method."""

    def test_get_scan_path(self, tmp_path):
        """Test getting scan path from configuration."""
        # Create configuration with specific scan path
        scan_dir = tmp_path / "source"
        scan_dir.mkdir()
        
        config = PathConfiguration.from_options(
            scan_path=str(scan_dir),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Get scan path
        scan_path = resolver.get_scan_path()
        
        # Should return the configured scan path
        assert scan_path == scan_dir

    def test_get_default_scan_path(self, tmp_path):
        """Test getting default scan path."""
        # Create default src directory
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        # Create configuration without explicit scan path
        config = PathConfiguration.from_options(
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Get scan path
        scan_path = resolver.get_scan_path()
        
        # Should return default 'src' directory
        assert scan_path == src_dir
    """Tests for PathResolver.get_package_path() method."""

    def test_simple_app_name(self):
        """Test package path for simple app name."""
        # Mock AppConfig with simple name
        app_config = Mock()
        app_config.name = "blog"
        app_config.path = "/path/to/blog"
        
        # Get package path
        package_path = PathResolver.get_package_path(app_config)
        
        # Should be app_name.models
        assert package_path == "blog.models"

    def test_nested_package_path(self):
        """Test package path for deeply nested app."""
        # Mock AppConfig with nested package
        app_config = Mock()
        app_config.name = "kinkotech.common.domains.account"
        app_config.path = "/path/to/kinkotech/common/domains/account"
        
        # Get package path
        package_path = PathResolver.get_package_path(app_config)
        
        # Should append .models to the full package path
        assert package_path == "kinkotech.common.domains.account.models"

    def test_django_contrib_app(self):
        """Test package path for Django contrib app."""
        # Mock AppConfig for django.contrib.auth
        app_config = Mock()
        app_config.name = "django.contrib.auth"
        app_config.path = "/path/to/django/contrib/auth"
        
        # Get package path
        package_path = PathResolver.get_package_path(app_config)
        
        # Should be django.contrib.auth.models
        assert package_path == "django.contrib.auth.models"

    def test_error_when_package_name_empty(self):
        """Test fail-fast when package name is empty."""
        # Mock AppConfig with empty name
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = ""
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            PathResolver.get_package_path(app_config)
        
        # Error message should be clear
        assert "Cannot determine package path" in str(exc_info.value)
        assert "myapp" in str(exc_info.value)

    def test_package_path_independent_of_filesystem(self):
        """Test that package path is independent of filesystem location."""
        # Two apps with same package name but different filesystem locations
        app_config_1 = Mock()
        app_config_1.name = "myapp"
        app_config_1.path = "/some/path/myapp"
        
        app_config_2 = Mock()
        app_config_2.name = "myapp"
        app_config_2.path = "/different/location/myapp"
        
        # Both should produce the same package path
        package_path_1 = PathResolver.get_package_path(app_config_1)
        package_path_2 = PathResolver.get_package_path(app_config_2)
        
        assert package_path_1 == package_path_2
        assert package_path_1 == "myapp.models"


class TestPathResolverBasicFunctionality:
    """
    Unit tests for PathResolver basic functionality.
    
    Tests Requirements 2.4 (third-party package prefix) and 3.6 (path separation).
    """
    
    def test_third_party_package_output_path(self, tmp_path):
        """Test that third-party packages use third_party_output_path."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_output_path=str(tmp_path / "external"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig for third-party package
        app_config = Mock()
        app_config.label = "auth"
        app_config.name = "django.contrib.auth"
        
        # Resolve output path for third-party
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml",
            is_third_party=True
        )
        
        # Should use third_party_output_path
        expected = tmp_path / "external" / "django" / "contrib" / "auth" / "models.toml"
        assert output_path == expected
    
    def test_non_third_party_package_output_path(self, tmp_path):
        """Test that non-third-party packages use output_path."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_output_path=str(tmp_path / "external"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig for regular package
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve output path for non-third-party
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml",
            is_third_party=False
        )
        
        # Should use output_path
        expected = tmp_path / "src" / "myapp" / "models.toml"
        assert output_path == expected
    
    def test_third_party_package_name_with_prefix(self, tmp_path):
        """Test that third-party packages get prefix added to package name."""
        # Create configuration with custom prefix
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_package_prefix="external",
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "auth"
        app_config.name = "django.contrib.auth"
        
        # Resolve package name for third-party
        package_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Should have prefix
        assert package_name == "external.django.contrib.auth"
    
    def test_non_third_party_package_name_without_prefix(self, tmp_path):
        """Test that non-third-party packages don't get prefix."""
        # Create configuration with custom prefix
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_package_prefix="external",
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve package name for non-third-party
        package_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=False
        )
        
        # Should not have prefix
        assert package_name == "myapp"
    
    def test_path_separation_scan_vs_output(self, tmp_path):
        """Test that scan_path and output_path are properly separated."""
        # Create directories
        scan_dir = tmp_path / "source"
        output_dir = tmp_path / "build"
        scan_dir.mkdir()
        output_dir.mkdir()
        
        # Create configuration with different scan and output paths
        config = PathConfiguration.from_options(
            scan_path=str(scan_dir),
            output_path=str(output_dir),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Get scan path
        resolved_scan_path = resolver.get_scan_path()
        assert resolved_scan_path == scan_dir
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Get output path
        output_path = resolver.resolve_output_path(
            app_config=app_config,
            format="toml",
            is_third_party=False
        )
        
        # Output should be under output_dir, not scan_dir
        assert output_path.parent.parent == output_dir
        assert output_path == output_dir / "myapp" / "models.toml"
    
    def test_default_third_party_prefix_from_path(self, tmp_path):
        """Test that default prefix is derived from third_party_output_path."""
        # Create configuration without explicit prefix
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_output_path=str(tmp_path / "src" / "external_libs"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "auth"
        app_config.name = "django.contrib.auth"
        
        # Resolve package name for third-party
        package_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Prefix should be the last directory name
        assert package_name == "external_libs.django.contrib.auth"
    
    def test_custom_prefix_overrides_default(self, tmp_path):
        """Test that custom prefix overrides the default derived from path."""
        # Create configuration with explicit prefix
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_output_path=str(tmp_path / "src" / "external_libs"),
            third_party_package_prefix="vendor",
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "auth"
        app_config.name = "django.contrib.auth"
        
        # Resolve package name for third-party
        package_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Should use custom prefix, not path-derived one
        assert package_name == "vendor.django.contrib.auth"
    
    def test_nested_package_with_third_party_prefix(self, tmp_path):
        """Test prefix addition for deeply nested packages."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            third_party_package_prefix="third",
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig with deeply nested package
        app_config = Mock()
        app_config.label = "models"
        app_config.name = "company.product.module.submodule.models"
        
        # Resolve package name for third-party
        package_name = resolver.resolve_package_name(
            app_config=app_config,
            is_third_party=True
        )
        
        # Prefix should be added to the full package name
        assert package_name == "third.company.product.module.submodule.models"
    
    def test_output_path_with_different_formats(self, tmp_path):
        """Test that format parameter affects file extension."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "src"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Test different formats
        toml_path = resolver.resolve_output_path(app_config, "toml", False)
        assert toml_path.suffix == ".toml"
        
        mermaid_path = resolver.resolve_output_path(app_config, "mermaid", False)
        assert mermaid_path.suffix == ".mermaid"
        
        plantuml_path = resolver.resolve_output_path(app_config, "plantuml", False)
        assert plantuml_path.suffix == ".plantuml"
    
    def test_third_party_flag_determines_base_directory(self, tmp_path):
        """Test that is_third_party flag correctly selects base directory."""
        # Create configuration
        config = PathConfiguration.from_options(
            output_path=str(tmp_path / "project"),
            third_party_output_path=str(tmp_path / "vendor"),
            working_dir=tmp_path
        )
        resolver = PathResolver(config)
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Non-third-party should use output_path
        regular_path = resolver.resolve_output_path(app_config, "toml", False)
        assert str(regular_path).startswith(str(tmp_path / "project"))
        
        # Third-party should use third_party_output_path
        third_party_path = resolver.resolve_output_path(app_config, "toml", True)
        assert str(third_party_path).startswith(str(tmp_path / "vendor"))
