"""Unit tests for AppDiscoveryService."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from x007007007.er_django.app_discovery import AppDiscoveryService


class TestAppDiscoveryServiceDiscoverAppsWithToml:
    """Tests for AppDiscoveryService.discover_apps_with_toml() method."""

    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_single_app_with_models_toml(self, mock_apps, tmp_path):
        """Test discovering a single app with models.toml in root."""
        # Create app structure: myapp/models.toml
        app_dir = tmp_path / "myapp"
        app_dir.mkdir()
        toml_file = app_dir / "models.toml"
        toml_file.touch()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_configs.return_value = [app_config]
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml()
        
        # Should find the app
        assert apps_with_toml == ["myapp"]

    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_single_app_with_models_models_toml(self, mock_apps, tmp_path):
        """Test discovering a single app with models/models.toml."""
        # Create app structure: myapp/models/models.toml
        app_dir = tmp_path / "myapp"
        models_dir = app_dir / "models"
        models_dir.mkdir(parents=True)
        toml_file = models_dir / "models.toml"
        toml_file.touch()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_configs.return_value = [app_config]
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml()
        
        # Should find the app
        assert apps_with_toml == ["myapp"]

    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_multiple_apps(self, mock_apps, tmp_path):
        """Test discovering multiple apps with TOML files."""
        # Create multiple app structures
        app1_dir = tmp_path / "app1"
        app1_dir.mkdir()
        (app1_dir / "models.toml").touch()
        
        app2_dir = tmp_path / "app2"
        models2_dir = app2_dir / "models"
        models2_dir.mkdir(parents=True)
        (models2_dir / "models.toml").touch()
        
        app3_dir = tmp_path / "app3"
        app3_dir.mkdir()
        (app3_dir / "models.toml").touch()
        
        # Mock AppConfigs
        app_config1 = Mock()
        app_config1.label = "app1"
        app_config1.path = str(app1_dir)
        
        app_config2 = Mock()
        app_config2.label = "app2"
        app_config2.path = str(app2_dir)
        
        app_config3 = Mock()
        app_config3.label = "app3"
        app_config3.path = str(app3_dir)
        
        mock_apps.get_app_configs.return_value = [app_config1, app_config2, app_config3]
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml()
        
        # Should find all three apps
        assert set(apps_with_toml) == {"app1", "app2", "app3"}
        assert len(apps_with_toml) == 3

    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_no_apps_with_toml(self, mock_apps, tmp_path):
        """Test discovering when no apps have TOML files."""
        # Create app without TOML
        app_dir = tmp_path / "myapp"
        app_dir.mkdir()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_configs.return_value = [app_config]
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml()
        
        # Should return empty list
        assert apps_with_toml == []

    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_mixed_apps(self, mock_apps, tmp_path):
        """Test discovering when some apps have TOML and some don't."""
        # Create apps with and without TOML
        app1_dir = tmp_path / "app1"
        app1_dir.mkdir()
        (app1_dir / "models.toml").touch()
        
        app2_dir = tmp_path / "app2"
        app2_dir.mkdir()
        # No TOML file for app2
        
        app3_dir = tmp_path / "app3"
        models3_dir = app3_dir / "models"
        models3_dir.mkdir(parents=True)
        (models3_dir / "models.toml").touch()
        
        # Mock AppConfigs
        app_config1 = Mock()
        app_config1.label = "app1"
        app_config1.path = str(app1_dir)
        
        app_config2 = Mock()
        app_config2.label = "app2"
        app_config2.path = str(app2_dir)
        
        app_config3 = Mock()
        app_config3.label = "app3"
        app_config3.path = str(app3_dir)
        
        mock_apps.get_app_configs.return_value = [app_config1, app_config2, app_config3]
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml()
        
        # Should find only app1 and app3
        assert set(apps_with_toml) == {"app1", "app3"}
        assert len(apps_with_toml) == 2

    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_prefers_root_toml_over_models_toml(self, mock_apps, tmp_path):
        """Test that when both TOML locations exist, app is only listed once."""
        # Create app with TOML in both locations
        app_dir = tmp_path / "myapp"
        app_dir.mkdir()
        (app_dir / "models.toml").touch()
        
        models_dir = app_dir / "models"
        models_dir.mkdir()
        (models_dir / "models.toml").touch()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_configs.return_value = [app_config]
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml()
        
        # Should find the app only once (break after first match)
        assert apps_with_toml == ["myapp"]
        assert len(apps_with_toml) == 1

    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_nested_app_structure(self, mock_apps, tmp_path):
        """Test discovering apps with nested package structure."""
        # Create nested app: src/kinkotech/common/account/models.toml
        app_dir = tmp_path / "src" / "kinkotech" / "common" / "account"
        app_dir.mkdir(parents=True)
        (app_dir / "models.toml").touch()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "account"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_configs.return_value = [app_config]
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml()
        
        # Should find the nested app
        assert apps_with_toml == ["account"]


class TestAppDiscoveryServiceGetTomlPath:
    """Tests for AppDiscoveryService.get_toml_path() method."""

    @patch('x007007007.er_django.app_discovery.apps')
    def test_get_toml_path_from_root(self, mock_apps, tmp_path):
        """Test getting TOML path when it's in app root."""
        # Create app structure: myapp/models.toml
        app_dir = tmp_path / "myapp"
        app_dir.mkdir()
        toml_file = app_dir / "models.toml"
        toml_file.touch()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_config.return_value = app_config
        
        # Get TOML path
        toml_path = AppDiscoveryService.get_toml_path("myapp")
        
        # Should return the root TOML path
        assert toml_path == toml_file

    @patch('x007007007.er_django.app_discovery.apps')
    def test_get_toml_path_from_models_dir(self, mock_apps, tmp_path):
        """Test getting TOML path when it's in models/ directory."""
        # Create app structure: myapp/models/models.toml
        app_dir = tmp_path / "myapp"
        models_dir = app_dir / "models"
        models_dir.mkdir(parents=True)
        toml_file = models_dir / "models.toml"
        toml_file.touch()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_config.return_value = app_config
        
        # Get TOML path
        toml_path = AppDiscoveryService.get_toml_path("myapp")
        
        # Should return the models/ TOML path
        assert toml_path == toml_file

    @patch('x007007007.er_django.app_discovery.apps')
    def test_get_toml_path_prefers_root_location(self, mock_apps, tmp_path):
        """Test that root TOML is preferred when both locations exist."""
        # Create app with TOML in both locations
        app_dir = tmp_path / "myapp"
        app_dir.mkdir()
        root_toml = app_dir / "models.toml"
        root_toml.touch()
        
        models_dir = app_dir / "models"
        models_dir.mkdir()
        models_toml = models_dir / "models.toml"
        models_toml.touch()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_config.return_value = app_config
        
        # Get TOML path
        toml_path = AppDiscoveryService.get_toml_path("myapp")
        
        # Should return the root TOML (checked first)
        assert toml_path == root_toml

    @patch('x007007007.er_django.app_discovery.apps')
    def test_get_toml_path_not_found_fail_fast(self, mock_apps, tmp_path):
        """Test fail-fast when TOML file not found."""
        # Create app without TOML
        app_dir = tmp_path / "myapp"
        app_dir.mkdir()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "myapp"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_config.return_value = app_config
        
        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            AppDiscoveryService.get_toml_path("myapp")
        
        # Error message should be clear and helpful
        error_msg = str(exc_info.value)
        assert "models.toml not found for app 'myapp'" in error_msg
        assert "Expected locations:" in error_msg
        assert "models.toml" in error_msg
        assert "models/models.toml" in error_msg
        assert "Suggestion:" in error_msg
        assert "er_export" in error_msg

    @patch('x007007007.er_django.app_discovery.apps')
    def test_get_toml_path_nested_app(self, mock_apps, tmp_path):
        """Test getting TOML path for nested app structure."""
        # Create nested app: src/kinkotech/common/account/models.toml
        app_dir = tmp_path / "src" / "kinkotech" / "common" / "account"
        app_dir.mkdir(parents=True)
        toml_file = app_dir / "models.toml"
        toml_file.touch()
        
        # Mock AppConfig
        app_config = Mock()
        app_config.label = "account"
        app_config.path = str(app_dir)
        
        mock_apps.get_app_config.return_value = app_config
        
        # Get TOML path
        toml_path = AppDiscoveryService.get_toml_path("account")
        
        # Should return the correct nested path
        assert toml_path == toml_file
