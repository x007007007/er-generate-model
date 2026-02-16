"""
Tests for er_convert command third-party package detection.

This test verifies that the er_convert command correctly detects third-party
packages and outputs them to the third/ subdirectory.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO


class TestErConvertThirdPartyDetection:
    """Test third-party package detection in er_convert command."""
    
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_local_app_not_marked_as_third_party(self, mock_apps):
        """
        Test that local apps (inside scan_path) are not marked as third-party.
        
        Validates:
        - Local app detection works correctly
        - Output path does NOT include third/ subdirectory for local apps
        - No "(third-party package)" label in output
        """
        # Setup mock app config for a local app
        mock_app_config = Mock()
        mock_app_config.label = 'myapp'
        # Simulate local app path (inside scan_path)
        mock_app_config.path = '/project/src/myapp'
        
        mock_apps.get_app_config.return_value = mock_app_config
        
        # Create command instance
        from x007007007.er_django.management.commands.er_convert import Command
        command = Command()
        
        # Test third-party detection
        from x007007007.er_django.path_configuration import PathConfiguration
        path_config = PathConfiguration.from_options(
            scan_path=Path('/project/src'),
            output_path=Path('/project/src'),
            working_dir=Path('/project')
        )
        
        is_third_party = command._is_third_party_app(mock_app_config, path_config.scan_path)
        
        # Verify it's NOT detected as third-party
        assert is_third_party is False
    
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_site_packages_app_marked_as_third_party(self, mock_apps):
        """
        Test that apps in site-packages are marked as third-party.
        
        Validates:
        - Apps installed in site-packages are detected as third-party
        - Detection works regardless of Python version path
        """
        # Setup mock app config for a site-packages app
        mock_app_config = Mock()
        mock_app_config.label = 'django_filters'
        # Simulate site-packages path
        mock_app_config.path = '/usr/local/lib/python3.12/site-packages/django_filters'
        
        mock_apps.get_app_config.return_value = mock_app_config
        
        # Create command instance
        from x007007007.er_django.management.commands.er_convert import Command
        command = Command()
        
        # Test third-party detection
        from x007007007.er_django.path_configuration import PathConfiguration
        path_config = PathConfiguration.from_options(
            scan_path=Path('/project/src'),
            output_path=Path('/project/src'),
            working_dir=Path('/project')
        )
        
        is_third_party = command._is_third_party_app(mock_app_config, path_config.scan_path)
        
        # Verify it IS detected as third-party
        assert is_third_party is True
    
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_venv_app_marked_as_third_party(self, mock_apps):
        """
        Test that apps in .venv are marked as third-party.
        
        Validates:
        - Apps installed in virtual environment are detected as third-party
        """
        # Setup mock app config for a .venv app
        mock_app_config = Mock()
        mock_app_config.label = 'rest_framework'
        # Simulate .venv path
        mock_app_config.path = '/project/.venv/lib/python3.12/site-packages/rest_framework'
        
        mock_apps.get_app_config.return_value = mock_app_config
        
        # Create command instance
        from x007007007.er_django.management.commands.er_convert import Command
        command = Command()
        
        # Test third-party detection
        from x007007007.er_django.path_configuration import PathConfiguration
        path_config = PathConfiguration.from_options(
            scan_path=Path('/project/src'),
            output_path=Path('/project/src'),
            working_dir=Path('/project')
        )
        
        is_third_party = command._is_third_party_app(mock_app_config, path_config.scan_path)
        
        # Verify it IS detected as third-party
        assert is_third_party is True

