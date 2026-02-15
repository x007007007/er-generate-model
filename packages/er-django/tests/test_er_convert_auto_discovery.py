"""
Unit tests for er_convert command auto-discovery - Task 11.2

Tests for:
- Auto-discovery when apps parameter is empty
- Fail-fast when no apps with models.toml are found
"""
import pytest
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Skip all tests if Django is not available
pytest.importorskip("django")

import os
import django
from django.conf import settings

# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'x007007007.er_django',
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class TestErConvertAutoDiscovery(TestCase):
    """Test er_convert command auto-discovery functionality - Task 11.2"""
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_auto_discovery_when_no_apps_specified(self, mock_discovery_service):
        """
        Test that auto-discovery is triggered when apps parameter is empty.
        
        Requirements: 4.10, 8.1
        """
        # Mock the discovery service to return some apps
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2']
        mock_discovery_service.get_toml_path.side_effect = FileNotFoundError("TOML not found")
        
        # Call command without specifying apps
        out = StringIO()
        
        # Should fail when trying to convert (since we're mocking), but auto-discovery should be called
        with pytest.raises(CommandError):
            call_command('er_convert', stdout=out)
        
        # Verify that discover_apps_with_toml was called
        mock_discovery_service.discover_apps_with_toml.assert_called_once()
        
        # Verify output mentions auto-discovery
        output = out.getvalue()
        assert 'Auto-discovered' in output or 'auto-discovered' in output.lower()
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_fail_fast_when_no_apps_discovered(self, mock_discovery_service):
        """
        Test that CommandError is raised when no apps with models.toml are found.
        
        Requirements: 8.7
        """
        # Mock the discovery service to return empty list
        mock_discovery_service.discover_apps_with_toml.return_value = []
        
        # Call command without specifying apps
        out = StringIO()
        
        # Should raise CommandError with appropriate message
        with pytest.raises(CommandError) as exc_info:
            call_command('er_convert', stdout=out)
        
        # Verify error message
        error_msg = str(exc_info.value)
        assert 'No apps with models.toml found' in error_msg
        
        # Verify that discover_apps_with_toml was called
        mock_discovery_service.discover_apps_with_toml.assert_called_once()
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_no_auto_discovery_when_apps_specified(self, mock_discovery_service):
        """
        Test that auto-discovery is NOT triggered when apps are explicitly specified.
        
        Requirements: 4.9, 8.2
        """
        # Mock the discovery service
        mock_discovery_service.get_toml_path.side_effect = FileNotFoundError("TOML not found")
        
        # Call command with specific apps
        out = StringIO()
        
        # Should fail when trying to get TOML path, but auto-discovery should NOT be called
        with pytest.raises(CommandError):
            call_command('er_convert', 'app1', 'app2', stdout=out)
        
        # Verify that discover_apps_with_toml was NOT called
        mock_discovery_service.discover_apps_with_toml.assert_not_called()
        
        # Verify output mentions the specified apps
        output = out.getvalue()
        assert 'app1' in output or 'Converting specified apps' in output
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_auto_discovery_lists_found_apps(self, mock_apps, mock_discovery_service):
        """
        Test that auto-discovered apps are listed in the output.
        
        Requirements: 4.10, 8.1
        """
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2']
        mock_discovery_service.get_toml_path.side_effect = FileNotFoundError("TOML not found")
        
        # Call command without specifying apps
        out = StringIO()
        
        # Should fail when trying to convert, but we're testing discovery output
        with pytest.raises(CommandError):
            call_command('er_convert', stdout=out)
        
        # Verify output lists the discovered apps
        output = out.getvalue()
        assert 'app1' in output
        assert 'app2' in output
        assert 'Auto-discovered' in output or '2 apps' in output
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_checks_apps_parameter_is_empty(self, mock_discovery_service):
        """
        Test that the command correctly checks if apps parameter is empty.
        
        Requirements: 4.10, 8.1
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1']
        mock_discovery_service.get_toml_path.side_effect = FileNotFoundError("TOML not found")
        
        cmd = Command()
        
        # Test with empty apps list
        with pytest.raises(CommandError):
            cmd.handle(apps=[], framework='django', output_subdir=None, base_model_import=None)
        
        # Should have called discover_apps_with_toml
        mock_discovery_service.discover_apps_with_toml.assert_called()
        
        # Reset mock
        mock_discovery_service.reset_mock()
        
        # Test with non-empty apps list
        with pytest.raises(CommandError):
            cmd.handle(apps=['app1'], framework='django', output_subdir=None, base_model_import=None)
        
        # Should NOT have called discover_apps_with_toml
        mock_discovery_service.discover_apps_with_toml.assert_not_called()


class TestErConvertAutoDiscoveryIntegration(TestCase):
    """Integration tests for auto-discovery functionality - Task 11.2"""
    
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_auto_discovery_integration_with_real_discovery_service(self, mock_discovery_service, mock_apps):
        """
        Integration test: auto-discovery with mocked AppDiscoveryService.
        
        Requirements: 4.10, 8.1, 8.7
        """
        # Mock the discovery service to return apps
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2']
        mock_discovery_service.get_toml_path.side_effect = FileNotFoundError("TOML not found")
        
        # Call command without specifying apps
        out = StringIO()
        
        # Should fail when trying to get TOML path, but we're testing discovery
        with pytest.raises(CommandError):
            call_command('er_convert', stdout=out)
        
        # Verify output shows auto-discovery worked
        output = out.getvalue()
        assert 'app1' in output
        assert 'app2' in output
        assert 'Auto-discovered' in output or '2 apps' in output
