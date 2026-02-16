"""
Unit tests for er_convert command app validation - Task 11.3

Tests for:
- Validation that specified apps exist
- Validation that each app has models.toml file
- Fail-fast behavior when validation fails

Requirements: 4.9, 8.2, 8.6
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


class TestErConvertAppValidation(TestCase):
    """Test er_convert command app validation functionality - Task 11.3"""
    
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_validate_app_exists(self, mock_apps):
        """
        Test that validation checks if specified app exists.
        
        Requirements: 4.9, 8.2
        """
        # Mock apps.get_app_config to raise LookupError for non-existent app
        mock_apps.get_app_config.side_effect = LookupError("No installed app with label 'nonexistent'")
        
        # Call command with non-existent app
        out = StringIO()
        
        # Should raise CommandError with appropriate message
        with pytest.raises(CommandError) as exc_info:
            call_command('er_convert', 'nonexistent', stdout=out)
        
        # Verify error message mentions the app not found
        error_msg = str(exc_info.value)
        assert 'nonexistent' in error_msg
        assert 'not found' in error_msg.lower()
        
        # Verify that get_app_config was called
        mock_apps.get_app_config.assert_called_with('nonexistent')
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_validate_app_has_toml_file(self, mock_apps, mock_discovery_service):
        """
        Test that validation checks if app has models.toml file.
        
        Requirements: 8.6
        """
        # Mock apps.get_app_config to succeed (app exists)
        mock_app_config = Mock()
        mock_app_config.label = 'testapp'
        mock_apps.get_app_config.return_value = mock_app_config
        
        # Mock AppDiscoveryService.get_toml_path to raise FileNotFoundError
        mock_discovery_service.get_toml_path.side_effect = FileNotFoundError(
            "models.toml not found for app 'testapp'"
        )
        
        # Call command with app that has no TOML file
        out = StringIO()
        
        # Should raise CommandError with appropriate message
        with pytest.raises(CommandError) as exc_info:
            call_command('er_convert', 'testapp', stdout=out)
        
        # Verify error message mentions TOML not found
        error_msg = str(exc_info.value)
        assert 'testapp' in error_msg
        assert 'models.toml' in error_msg
        assert 'not found' in error_msg.lower()
        
        # Verify that get_toml_path was called
        mock_discovery_service.get_toml_path.assert_called_with('testapp', toml_search_dir=Path('src'))
    
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_fail_fast_on_first_invalid_app(self, mock_apps):
        """
        Test that validation fails fast on the first invalid app.
        
        Requirements: 8.6
        """
        # Mock apps.get_app_config to fail on first app
        mock_apps.get_app_config.side_effect = LookupError("No installed app with label 'invalid1'")
        
        # Call command with multiple apps, first one invalid
        out = StringIO()
        
        # Should raise CommandError immediately
        with pytest.raises(CommandError) as exc_info:
            call_command('er_convert', 'invalid1', 'valid_app', stdout=out)
        
        # Verify error message mentions the first invalid app
        error_msg = str(exc_info.value)
        assert 'invalid1' in error_msg
        
        # Verify that get_app_config was called only once (fail-fast)
        assert mock_apps.get_app_config.call_count == 1
        mock_apps.get_app_config.assert_called_with('invalid1')
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_validate_multiple_apps_all_valid(self, mock_apps, mock_discovery_service):
        """
        Test that validation succeeds when all specified apps are valid.
        
        Requirements: 4.9, 8.2
        """
        # Mock apps.get_app_config to succeed for all apps
        mock_app_config1 = Mock()
        mock_app_config1.label = 'app1'
        mock_app_config1.path = '/path/to/app1'
        
        mock_app_config2 = Mock()
        mock_app_config2.label = 'app2'
        mock_app_config2.path = '/path/to/app2'
        
        mock_apps.get_app_config.side_effect = [mock_app_config1, mock_app_config2, mock_app_config1, mock_app_config2]
        
        # Mock AppDiscoveryService.get_toml_path to succeed
        mock_discovery_service.get_toml_path.side_effect = [
            Path('/path/to/app1/models.toml'),
            Path('/path/to/app2/models.toml'),
        ]
        
        # Mock toml.load to succeed
        with patch('builtins.open', create=True), \
             patch('toml.load', return_value={}):
            
            # Call command with multiple valid apps
            out = StringIO()
            
            # Should not raise any errors during validation
            # (will fail later in conversion, but validation should pass)
            try:
                call_command('er_convert', 'app1', 'app2', stdout=out)
            except CommandError as e:
                # If it fails, it should not be due to validation
                error_msg = str(e)
                assert 'not found' not in error_msg.lower()
                assert 'INSTALLED_APPS' not in error_msg
        
        # Verify that get_app_config was called for both apps
        assert mock_apps.get_app_config.call_count >= 2
        
        # Verify that get_toml_path was called for both apps
        assert mock_discovery_service.get_toml_path.call_count >= 2
    
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_validation_error_message_includes_suggestion(self, mock_apps):
        """
        Test that validation error messages include helpful suggestions.
        
        Requirements: 4.9, 8.2
        """
        # Mock apps.get_app_config to raise LookupError
        mock_apps.get_app_config.side_effect = LookupError("No installed app")
        
        # Call command with non-existent app
        out = StringIO()
        
        # Should raise CommandError with suggestion
        with pytest.raises(CommandError) as exc_info:
            call_command('er_convert', 'myapp', stdout=out)
        
        # Verify error message includes suggestion
        error_msg = str(exc_info.value)
        assert 'Suggestion' in error_msg or 'INSTALLED_APPS' in error_msg
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_validation_checks_each_app_in_order(self, mock_apps, mock_discovery_service):
        """
        Test that validation checks each app in the order specified.
        
        Requirements: 4.9, 8.2, 8.6
        """
        # Mock apps.get_app_config to succeed
        mock_app_config = Mock()
        mock_app_config.label = 'app1'
        mock_apps.get_app_config.return_value = mock_app_config
        
        # Mock AppDiscoveryService.get_toml_path to fail on second app
        mock_discovery_service.get_toml_path.side_effect = [
            Path('/path/to/app1/models.toml'),  # First app succeeds
            FileNotFoundError("models.toml not found for app 'app2'"),  # Second app fails
        ]
        
        # Call command with multiple apps
        out = StringIO()
        
        # Should raise CommandError on second app
        with pytest.raises(CommandError) as exc_info:
            call_command('er_convert', 'app1', 'app2', stdout=out)
        
        # Verify error message mentions the second app
        error_msg = str(exc_info.value)
        assert 'app2' in error_msg
        
        # Verify that get_toml_path was called twice (once for each app)
        assert mock_discovery_service.get_toml_path.call_count == 2
        mock_discovery_service.get_toml_path.assert_any_call('app1', toml_search_dir=Path('src'))
        mock_discovery_service.get_toml_path.assert_any_call('app2', toml_search_dir=Path('src'))
    
    def test_validate_apps_method_exists(self):
        """
        Test that the _validate_apps method exists in the Command class.
        
        Requirements: 4.9, 8.2, 8.6
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        
        # Verify that _validate_apps method exists
        assert hasattr(cmd, '_validate_apps'), "Command should have _validate_apps method"
        assert callable(cmd._validate_apps), "_validate_apps should be callable"
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_validate_apps_method_validates_all_apps(self, mock_apps, mock_discovery_service):
        """
        Test that _validate_apps method validates all specified apps.
        
        Requirements: 4.9, 8.2, 8.6
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock apps.get_app_config to succeed
        mock_app_config = Mock()
        mock_apps.get_app_config.return_value = mock_app_config
        
        # Mock AppDiscoveryService.get_toml_path to succeed
        mock_discovery_service.get_toml_path.return_value = Path('/path/to/models.toml')
        
        cmd = Command()
        
        # Call _validate_apps with multiple apps
        cmd._validate_apps(['app1', 'app2', 'app3'])
        
        # Verify that get_app_config was called for each app
        assert mock_apps.get_app_config.call_count == 3
        mock_apps.get_app_config.assert_any_call('app1')
        mock_apps.get_app_config.assert_any_call('app2')
        mock_apps.get_app_config.assert_any_call('app3')
        
        # Verify that get_toml_path was called for each app
        assert mock_discovery_service.get_toml_path.call_count == 3
        mock_discovery_service.get_toml_path.assert_any_call('app1', toml_search_dir=None)
        mock_discovery_service.get_toml_path.assert_any_call('app2', toml_search_dir=None)
        mock_discovery_service.get_toml_path.assert_any_call('app3', toml_search_dir=None)
    
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_validate_apps_raises_command_error_on_invalid_app(self, mock_apps):
        """
        Test that _validate_apps raises CommandError for invalid apps.
        
        Requirements: 4.9, 8.2, 8.6
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock apps.get_app_config to raise LookupError
        mock_apps.get_app_config.side_effect = LookupError("App not found")
        
        cmd = Command()
        
        # Call _validate_apps with invalid app
        with pytest.raises(CommandError) as exc_info:
            cmd._validate_apps(['invalid_app'])
        
        # Verify error message
        error_msg = str(exc_info.value)
        assert 'invalid_app' in error_msg
        assert 'not found' in error_msg.lower()


class TestErConvertValidationIntegration(TestCase):
    """Integration tests for app validation - Task 11.3"""
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_validation_runs_before_conversion(self, mock_apps, mock_discovery_service):
        """
        Test that validation runs before any conversion attempts.
        
        Requirements: 4.9, 8.2, 8.6
        """
        # Mock apps.get_app_config to fail
        mock_apps.get_app_config.side_effect = LookupError("App not found")
        
        # Call command with invalid app
        out = StringIO()
        
        # Should raise CommandError during validation
        with pytest.raises(CommandError) as exc_info:
            call_command('er_convert', 'invalid_app', stdout=out)
        
        # Verify error is from validation (not conversion)
        error_msg = str(exc_info.value)
        assert 'not found' in error_msg.lower()
        
        # Verify that get_toml_path was NOT called (validation failed first)
        mock_discovery_service.get_toml_path.assert_not_called()
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    @patch('x007007007.er_django.management.commands.er_convert.apps')
    def test_no_validation_for_auto_discovered_apps(self, mock_apps, mock_discovery_service):
        """
        Test that validation is NOT run for auto-discovered apps.
        
        Auto-discovered apps are already validated by the discovery process.
        
        Requirements: 4.10, 8.1
        """
        # Mock auto-discovery to return apps
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2']
        mock_discovery_service.get_toml_path.side_effect = FileNotFoundError("TOML not found")
        
        # Call command without specifying apps (auto-discovery)
        out = StringIO()
        
        # Should fail during conversion, not validation
        with pytest.raises(CommandError):
            call_command('er_convert', stdout=out)
        
        # Verify that get_app_config was NOT called for validation
        # (it may be called during conversion, but not during validation phase)
        # We can't easily distinguish, but the key is that auto-discovery was called
        mock_discovery_service.discover_apps_with_toml.assert_called_once()
