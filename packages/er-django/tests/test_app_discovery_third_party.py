"""
Tests for AppDiscoveryService third-party package discovery.

This test verifies that AppDiscoveryService can discover TOML files
in the third/ subdirectory for third-party packages.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from x007007007.er_django.app_discovery import AppDiscoveryService


class TestAppDiscoveryThirdParty:
    """Test third-party package discovery in AppDiscoveryService."""
    
    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_third_party_app_with_full_package_path(self, mock_apps, tmp_path):
        """
        Test discovering third-party app using full package path.
        
        Validates that TOML files in src/third/{full_package_path}/models.toml
        are correctly discovered.
        """
        # Setup mock app config
        mock_app_config = Mock()
        mock_app_config.label = 'auth'
        mock_app_config.name = 'django.contrib.auth'
        mock_app_config.path = '/usr/local/lib/python3.12/site-packages/django/contrib/auth'
        
        mock_apps.get_app_configs.return_value = [mock_app_config]
        
        # Create TOML file in third/ subdirectory with full package path
        toml_dir = tmp_path / 'third' / 'django' / 'contrib' / 'auth'
        toml_dir.mkdir(parents=True)
        toml_file = toml_dir / 'models.toml'
        toml_file.write_text('[entities.User]\ncolumns = []')
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml(tmp_path)
        
        # Verify the app was discovered
        assert 'auth' in apps_with_toml
    
    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_third_party_app_with_simple_name(self, mock_apps, tmp_path):
        """
        Test discovering third-party app using simple app name.
        
        Validates that TOML files in src/third/{app_name}/models.toml
        are correctly discovered.
        """
        # Setup mock app config
        mock_app_config = Mock()
        mock_app_config.label = 'constance'
        mock_app_config.name = 'constance'
        mock_app_config.path = '/usr/local/lib/python3.12/site-packages/constance'
        
        mock_apps.get_app_configs.return_value = [mock_app_config]
        
        # Create TOML file in third/ subdirectory with simple name
        toml_dir = tmp_path / 'third' / 'constance'
        toml_dir.mkdir(parents=True)
        toml_file = toml_dir / 'models.toml'
        toml_file.write_text('[entities.Config]\ncolumns = []')
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml(tmp_path)
        
        # Verify the app was discovered
        assert 'constance' in apps_with_toml
    
    @patch('x007007007.er_django.app_discovery.apps')
    def test_discover_mixed_local_and_third_party_apps(self, mock_apps, tmp_path):
        """
        Test discovering both local and third-party apps.
        
        Validates that both local apps (in src/) and third-party apps (in src/third/)
        are discovered correctly.
        """
        # Setup mock app configs
        local_app = Mock()
        local_app.label = 'myapp'
        local_app.name = 'myapp'
        local_app.path = str(tmp_path / 'myapp')
        
        third_party_app = Mock()
        third_party_app.label = 'rest_framework'
        third_party_app.name = 'rest_framework'
        third_party_app.path = '/usr/local/lib/python3.12/site-packages/rest_framework'
        
        mock_apps.get_app_configs.return_value = [local_app, third_party_app]
        
        # Create TOML file for local app
        local_toml_dir = tmp_path / 'myapp'
        local_toml_dir.mkdir(parents=True)
        (local_toml_dir / 'models.toml').write_text('[entities.MyModel]\ncolumns = []')
        
        # Create TOML file for third-party app
        third_toml_dir = tmp_path / 'third' / 'rest_framework'
        third_toml_dir.mkdir(parents=True)
        (third_toml_dir / 'models.toml').write_text('[entities.Token]\ncolumns = []')
        
        # Discover apps
        apps_with_toml = AppDiscoveryService.discover_apps_with_toml(tmp_path)
        
        # Verify both apps were discovered
        assert 'myapp' in apps_with_toml
        assert 'rest_framework' in apps_with_toml
        assert len(apps_with_toml) == 2
    
    @patch('x007007007.er_django.app_discovery.apps')
    def test_get_toml_path_for_third_party_app(self, mock_apps, tmp_path):
        """
        Test getting TOML path for third-party app.
        
        Validates that get_toml_path() correctly returns the path
        for TOML files in the third/ subdirectory.
        """
        # Setup mock app config
        mock_app_config = Mock()
        mock_app_config.label = 'django_filters'
        mock_app_config.name = 'django_filters'
        mock_app_config.path = '/usr/local/lib/python3.12/site-packages/django_filters'
        
        mock_apps.get_app_config.return_value = mock_app_config
        
        # Create TOML file in third/ subdirectory
        toml_dir = tmp_path / 'third' / 'django_filters'
        toml_dir.mkdir(parents=True)
        toml_file = toml_dir / 'models.toml'
        toml_file.write_text('[entities.Filter]\ncolumns = []')
        
        # Get TOML path
        result_path = AppDiscoveryService.get_toml_path('django_filters', tmp_path)
        
        # Verify the correct path was returned
        assert result_path == toml_file
        assert result_path.exists()
    
    @patch('x007007007.er_django.app_discovery.apps')
    def test_get_toml_path_prefers_local_over_third_party(self, mock_apps, tmp_path):
        """
        Test that get_toml_path() prefers local TOML over third-party.
        
        If a TOML file exists in both src/{app}/ and src/third/{app}/,
        the local one should be preferred.
        """
        # Setup mock app config
        mock_app_config = Mock()
        mock_app_config.label = 'myapp'
        mock_app_config.name = 'myapp'
        mock_app_config.path = str(tmp_path / 'myapp')
        
        mock_apps.get_app_config.return_value = mock_app_config
        
        # Create TOML file in local directory
        local_toml_dir = tmp_path / 'myapp'
        local_toml_dir.mkdir(parents=True)
        local_toml_file = local_toml_dir / 'models.toml'
        local_toml_file.write_text('[entities.LocalModel]\ncolumns = []')
        
        # Create TOML file in third/ subdirectory
        third_toml_dir = tmp_path / 'third' / 'myapp'
        third_toml_dir.mkdir(parents=True)
        third_toml_file = third_toml_dir / 'models.toml'
        third_toml_file.write_text('[entities.ThirdPartyModel]\ncolumns = []')
        
        # Get TOML path
        result_path = AppDiscoveryService.get_toml_path('myapp', tmp_path)
        
        # Verify the local path was returned (not the third-party one)
        assert result_path == local_toml_file
        assert result_path != third_toml_file
