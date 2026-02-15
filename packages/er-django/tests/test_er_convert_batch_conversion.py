"""
Unit tests for er_convert command batch conversion - Task 11.4

Tests for:
- Batch conversion of multiple apps
- Fail-fast behavior when an app conversion fails
- Counting successfully converted apps
- Summary output
"""
import pytest
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

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


class TestErConvertBatchConversion(TestCase):
    """Test er_convert command batch conversion functionality - Task 11.4"""
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_batch_conversion_iterates_through_all_apps(self, mock_discovery_service):
        """
        Test that batch conversion iterates through each app in the list.
        
        Requirements: 4.7, 8.5
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2', 'app3']
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock _convert_app to track calls
        with patch.object(cmd, '_convert_app', return_value=2) as mock_convert:
            out = StringIO()
            cmd.stdout = out
            
            # Call handle with auto-discovery
            cmd.handle(apps=[], framework='django', output_subdir=None, base_model_import=None)
            
            # Verify _convert_app was called for each app
            assert mock_convert.call_count == 3, "Should call _convert_app for each app"
            
            # Verify the calls were made with correct app labels
            # Extract app_label from keyword arguments of each call
            app_labels = [call_args[1]['app_label'] for call_args in mock_convert.call_args_list]
            assert 'app1' in app_labels
            assert 'app2' in app_labels
            assert 'app3' in app_labels
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_batch_conversion_calls_convert_app_method(self, mock_discovery_service):
        """
        Test that batch conversion calls _convert_app() for each app.
        
        Requirements: 4.7
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2']
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock _convert_app
        with patch.object(cmd, '_convert_app', return_value=1) as mock_convert:
            out = StringIO()
            cmd.stdout = out
            
            # Call handle
            cmd.handle(apps=[], framework='sqlalchemy', output_subdir='custom', base_model_import='mybase.Base')
            
            # Verify _convert_app was called with correct parameters
            assert mock_convert.call_count == 2
            
            # Check first call
            first_call = mock_convert.call_args_list[0]
            assert first_call[1]['app_label'] == 'app1'
            assert first_call[1]['framework'] == 'sqlalchemy'
            assert first_call[1]['output_subdir'] == 'custom'
            assert first_call[1]['base_model_import'] == 'mybase.Base'
            
            # Check second call
            second_call = mock_convert.call_args_list[1]
            assert second_call[1]['app_label'] == 'app2'
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_fail_fast_on_conversion_error(self, mock_discovery_service):
        """
        Test that conversion stops immediately when an app fails (fail-fast).
        
        Requirements: 8.3
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2', 'app3']
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock _convert_app to fail on second app
        def convert_side_effect(app_label, **kwargs):
            if app_label == 'app2':
                raise ValueError("Conversion failed for app2")
            return 1
        
        with patch.object(cmd, '_convert_app', side_effect=convert_side_effect) as mock_convert:
            out = StringIO()
            cmd.stdout = out
            
            # Call handle - should raise CommandError
            with pytest.raises(CommandError) as exc_info:
                cmd.handle(apps=[], framework='django', output_subdir=None, base_model_import=None)
            
            # Verify error message mentions the failed app
            error_msg = str(exc_info.value)
            assert 'app2' in error_msg
            assert 'Failed to convert' in error_msg
            
            # Verify _convert_app was called only twice (app1 succeeded, app2 failed, app3 not attempted)
            assert mock_convert.call_count == 2, "Should stop after first failure"
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_records_successfully_converted_app_count(self, mock_discovery_service):
        """
        Test that the command records the number of successfully converted apps.
        
        Requirements: 4.7, 8.4
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2', 'app3']
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock _convert_app to return file counts
        with patch.object(cmd, '_convert_app', return_value=5) as mock_convert:
            out = StringIO()
            cmd.stdout = out
            
            # Call handle
            cmd.handle(apps=[], framework='django', output_subdir=None, base_model_import=None)
            
            # Verify output shows correct count
            output = out.getvalue()
            assert 'Successfully converted 3 apps' in output or '3 apps' in output
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_outputs_conversion_summary(self, mock_discovery_service):
        """
        Test that the command outputs a summary after successful conversion.
        
        Requirements: 8.4, 12.3
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2']
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock _convert_app to return different file counts
        def convert_side_effect(app_label, **kwargs):
            return 3 if app_label == 'app1' else 5
        
        with patch.object(cmd, '_convert_app', side_effect=convert_side_effect):
            out = StringIO()
            cmd.stdout = out
            
            # Call handle
            cmd.handle(apps=[], framework='sqlalchemy', output_subdir=None, base_model_import=None)
            
            # Verify output contains summary information
            output = out.getvalue()
            assert 'Successfully converted' in output
            assert '2 apps' in output
            assert 'sqlalchemy' in output
            assert 'Total files generated: 8' in output  # 3 + 5
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_batch_conversion_with_specified_apps(self, mock_discovery_service):
        """
        Test batch conversion when apps are explicitly specified.
        
        Requirements: 4.7, 8.2, 8.5
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service for validation
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock apps.get_app_config to avoid LookupError
        with patch('x007007007.er_django.management.commands.er_convert.apps') as mock_apps:
            mock_app_config = Mock()
            mock_apps.get_app_config.return_value = mock_app_config
            
            # Mock _convert_app
            with patch.object(cmd, '_convert_app', return_value=2) as mock_convert:
                out = StringIO()
                cmd.stdout = out
                
                # Call handle with specific apps
                cmd.handle(apps=['app1', 'app2'], framework='django', output_subdir=None, base_model_import=None)
                
                # Verify _convert_app was called for each specified app
                assert mock_convert.call_count == 2
                
                # Verify output shows correct count
                output = out.getvalue()
                assert 'Successfully converted 2 apps' in output or '2 apps' in output
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_fail_fast_preserves_error_context(self, mock_discovery_service):
        """
        Test that fail-fast preserves the original error context.
        
        Requirements: 8.3, 12.1
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1']
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock _convert_app to raise a specific error
        original_error = ValueError("Invalid TOML format: missing required field 'entities'")
        
        with patch.object(cmd, '_convert_app', side_effect=original_error):
            out = StringIO()
            cmd.stdout = out
            
            # Call handle - should raise CommandError with original error message
            with pytest.raises(CommandError) as exc_info:
                cmd.handle(apps=[], framework='django', output_subdir=None, base_model_import=None)
            
            # Verify error message includes original error
            error_msg = str(exc_info.value)
            assert 'app1' in error_msg
            assert 'Invalid TOML format' in error_msg or 'missing required field' in error_msg
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_batch_conversion_accumulates_file_counts(self, mock_discovery_service):
        """
        Test that batch conversion accumulates total file counts from all apps.
        
        Requirements: 8.4, 12.3
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2', 'app3']
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock _convert_app to return different file counts
        file_counts = {'app1': 3, 'app2': 5, 'app3': 2}
        
        def convert_side_effect(app_label, **kwargs):
            return file_counts[app_label]
        
        with patch.object(cmd, '_convert_app', side_effect=convert_side_effect):
            out = StringIO()
            cmd.stdout = out
            
            # Call handle
            cmd.handle(apps=[], framework='django', output_subdir=None, base_model_import=None)
            
            # Verify output shows total file count
            output = out.getvalue()
            assert 'Total files generated: 10' in output  # 3 + 5 + 2
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_batch_conversion_with_zero_files_generated(self, mock_discovery_service):
        """
        Test batch conversion when no files are generated (edge case).
        
        Requirements: 8.4
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1']
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock _convert_app to return 0 files
        with patch.object(cmd, '_convert_app', return_value=0):
            out = StringIO()
            cmd.stdout = out
            
            # Call handle
            cmd.handle(apps=[], framework='django', output_subdir=None, base_model_import=None)
            
            # Verify output shows conversion completed
            output = out.getvalue()
            assert 'Successfully converted 1 apps' in output or '1 apps' in output
            assert 'Total files generated: 0' in output


class TestErConvertBatchConversionIntegration(TestCase):
    """Integration tests for batch conversion - Task 11.4"""
    
    @patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService')
    def test_batch_conversion_full_workflow(self, mock_discovery_service):
        """
        Integration test: full batch conversion workflow.
        
        Requirements: 4.7, 8.3, 8.4, 8.5
        """
        from x007007007.er_django.management.commands.er_convert import Command
        
        # Mock the discovery service
        mock_discovery_service.discover_apps_with_toml.return_value = ['app1', 'app2']
        mock_discovery_service.get_toml_path.return_value = Path('/fake/path/models.toml')
        
        cmd = Command()
        
        # Mock _convert_app
        with patch.object(cmd, '_convert_app', return_value=3) as mock_convert:
            out = StringIO()
            cmd.stdout = out
            
            # Call handle
            cmd.handle(apps=[], framework='django', output_subdir=None, base_model_import=None)
            
            # Verify complete workflow
            output = out.getvalue()
            
            # Should show auto-discovery
            assert 'Auto-discovered' in output or 'auto-discovered' in output.lower()
            
            # Should show conversion for each app
            assert 'app1' in output
            assert 'app2' in output
            
            # Should show summary
            assert 'Successfully converted 2 apps' in output or '2 apps' in output
            assert 'Total files generated: 6' in output
            
            # Should call _convert_app for each app
            assert mock_convert.call_count == 2
