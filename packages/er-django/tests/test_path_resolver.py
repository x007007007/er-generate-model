"""Unit tests for PathResolver."""

import os
from pathlib import Path
from unittest.mock import Mock

import pytest

from x007007007.er_django.path_resolver import PathResolver


class TestPathResolverResolveOutputPath:
    """Tests for PathResolver.resolve_output_path() method."""

    def test_simple_package_name(self, tmp_path):
        """Test path resolution for simple package name."""
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve output path
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir="./src",
            format="toml"
        )
        
        # Should output to src/myapp/models.toml
        expected = Path("src/myapp/models.toml")
        assert output_path == expected

    def test_nested_package_path(self, tmp_path):
        """Test path resolution for nested package path."""
        # Mock AppConfig with nested package
        app_config = Mock()
        app_config.label = "account"
        app_config.name = "kinkotech.common.domains.account"
        
        # Resolve output path
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir="./src",
            format="toml"
        )
        
        # Should output to src/kinkotech/common/domains/account/models.toml
        expected = Path("src/kinkotech/common/domains/account/models.toml")
        assert output_path == expected

    def test_django_contrib_app(self, tmp_path):
        """Test path resolution for Django contrib app."""
        # Mock AppConfig for django.contrib.auth
        app_config = Mock()
        app_config.label = "auth"
        app_config.name = "django.contrib.auth"
        
        # Resolve output path
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir="./output",
            format="toml"
        )
        
        # Should output to output/django/contrib/auth/models.toml
        expected = Path("output/django/contrib/auth/models.toml")
        assert output_path == expected

    def test_absolute_base_dir(self, tmp_path):
        """Test path resolution with absolute base_dir."""
        # Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve with absolute base_dir
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir=str(output_dir),
            format="toml"
        )
        
        # Should output to output_dir/myapp/models.toml
        expected = output_dir / "myapp" / "models.toml"
        assert output_path == expected

    def test_relative_base_dir(self, tmp_path):
        """Test path resolution with relative base_dir."""
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Resolve with relative base_dir
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir="./output",
            format="toml"
        )
        
        # Should output to output/myapp/models.toml
        expected = Path("output/myapp/models.toml")
        assert output_path == expected

    def test_different_formats(self, tmp_path):
        """Test path resolution with different output formats."""
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Test TOML format
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir="./src",
            format="toml"
        )
        assert output_path == Path("src/myapp/models.toml")
        
        # Test Mermaid format
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir="./src",
            format="mermaid"
        )
        assert output_path == Path("src/myapp/models.mermaid")
        
        # Test PlantUML format
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir="./src",
            format="plantuml"
        )
        assert output_path == Path("src/myapp/models.plantuml")

    def test_deeply_nested_package(self, tmp_path):
        """Test path resolution for deeply nested package structure."""
        # Mock AppConfig with deeply nested package
        app_config = Mock()
        app_config.label = "ccc"
        app_config.name = "aaa.bbb.ccc"
        
        # Resolve output path
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir="./src",
            format="toml"
        )
        
        # Should maintain full nested structure
        expected = Path("src/aaa/bbb/ccc/models.toml")
        assert output_path == expected

    def test_error_when_package_name_empty(self, tmp_path):
        """Test fail-fast when package name is empty."""
        # Mock AppConfig with empty name
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = ""
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            PathResolver.resolve_output_path(
                app_config=app_config,
                base_dir="./src",
                format="toml"
            )
        
        # Error message should be clear
        assert "Cannot determine package path" in str(exc_info.value)
        assert "myapp" in str(exc_info.value)

    def test_path_object_as_base_dir(self, tmp_path):
        """Test that base_dir can be a Path object."""
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.name = "myapp"
        
        # Pass Path object as base_dir
        output_path = PathResolver.resolve_output_path(
            app_config=app_config,
            base_dir=Path("./src"),
            format="toml"
        )
        
        assert output_path == Path("src/myapp/models.toml")

    def test_output_independent_of_filesystem_location(self, tmp_path):
        """Test that output path is independent of app's filesystem location."""
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
        output_path_1 = PathResolver.resolve_output_path(
            app_config=app_config_1,
            base_dir="./src",
            format="toml"
        )
        
        output_path_2 = PathResolver.resolve_output_path(
            app_config=app_config_2,
            base_dir="./src",
            format="toml"
        )
        
        # Paths should be identical
        assert output_path_1 == output_path_2
        assert output_path_1 == Path("src/myapp/models.toml")

    def test_complex_nested_package_independent_of_location(self, tmp_path):
        """Test complex nested package produces same output regardless of filesystem location."""
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
        output_path_1 = PathResolver.resolve_output_path(
            app_config=app_config_1,
            base_dir="./src",
            format="toml"
        )
        
        output_path_2 = PathResolver.resolve_output_path(
            app_config=app_config_2,
            base_dir="./src",
            format="toml"
        )
        
        # Paths should be identical
        assert output_path_1 == output_path_2
        expected = Path("src/kinkotech/common/domains/account/models.toml")
        assert output_path_1 == expected


class TestPathResolverGetPackagePath:
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
