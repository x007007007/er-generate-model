"""
Unit tests for task 9.4: Modify default output path to current working directory

Tests for:
- Default output directory is current working directory (os.getcwd())
- Support for relative paths (relative to current working directory)
- Support for absolute paths (used directly)
- ER_EXPORT_DIR setting is ignored

Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
"""
import pytest
import os
import tempfile
from pathlib import Path
from io import StringIO

# Skip all tests if Django is not available
pytest.importorskip("django")

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

from django.test import TestCase, override_settings
from django.core.management.base import CommandError


class TestErExportOutputDirectory(TestCase):
    """Test output directory handling - Task 9.4"""
    
    def test_default_output_dir_is_src(self):
        """
        Test that default output directory is ./src.
        
        Validates: Requirement 3.1
        """
        from x007007007.er_django.management.commands.er_export import Command
        from unittest.mock import Mock, patch, MagicMock
        
        cmd = Command()
        
        # Mock options with no output_dir specified
        options = {
            'apps': ['testapp'],  # Provide at least one app
            'format': 'toml',
            'output': None,
            'output_dir': None,  # Not specified
            'models': None,
            'exclude_apps': '',
            'include_django_apps': False,
            'name': None,
        }
        
        # Track what output_dir is used
        captured_output_dir = None
        
        def mock_ensure_directory_exists(path):
            nonlocal captured_output_dir
            captured_output_dir = path
        
        with patch('x007007007.er_django.management.commands.er_export.get_er_settings') as mock_settings:
            mock_settings.return_value = {
                'migrations_dir': '/tmp/migrations',
                'export_dir': '/tmp/export',  # This should be ignored
                'auto_create_dirs': True,
                'default_format': 'toml',
                'include_django_apps': False,
                'exclude_apps': [],
                'file_prefix': '',
                'file_suffix': '',
            }
            
            # Mock app config
            mock_app_config = MagicMock()
            mock_app_config.label = 'testapp'
            
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config', return_value=mock_app_config):
                with patch('x007007007.er_django.management.commands.er_export.ensure_directory_exists', side_effect=mock_ensure_directory_exists):
                    # Mock the parser to avoid actual parsing
                    with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser:
                        mock_parser_instance = MagicMock()
                        mock_parser_instance.parse.return_value = MagicMock(entities={})
                        mock_parser.return_value = mock_parser_instance
                        
                        out = StringIO()
                        cmd.stdout = out
                        
                        # Call handle
                        cmd.handle(**options)
                        
                        # Check that output_dir is ./src
                        expected_path = os.path.normpath(os.path.join(os.getcwd(), 'src'))
                        actual_path = os.path.normpath(captured_output_dir)
                        assert actual_path == expected_path, \
                            f"Output directory should be ./src, got {captured_output_dir}"
    
    def test_relative_path_resolved_to_cwd(self):
        """
        Test that relative paths are resolved relative to current working directory.
        
        Validates: Requirement 3.2, 3.4
        """
        from x007007007.er_django.management.commands.er_export import Command
        from unittest.mock import Mock, patch, MagicMock
        
        cmd = Command()
        
        # Mock options with relative output_dir
        options = {
            'apps': ['testapp'],
            'format': 'toml',
            'output': None,
            'output_dir': 'erexport',  # Relative path
            'models': None,
            'exclude_apps': '',
            'include_django_apps': False,
            'name': None,
        }
        
        captured_output_dir = None
        
        def mock_ensure_directory_exists(path):
            nonlocal captured_output_dir
            captured_output_dir = path
        
        with patch('x007007007.er_django.management.commands.er_export.get_er_settings') as mock_settings:
            mock_settings.return_value = {
                'migrations_dir': '/tmp/migrations',
                'export_dir': '/tmp/export',
                'auto_create_dirs': True,
                'default_format': 'toml',
                'include_django_apps': False,
                'exclude_apps': [],
                'file_prefix': '',
                'file_suffix': '',
            }
            
            mock_app_config = MagicMock()
            mock_app_config.label = 'testapp'
            
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config', return_value=mock_app_config):
                with patch('x007007007.er_django.management.commands.er_export.ensure_directory_exists', side_effect=mock_ensure_directory_exists):
                    with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser:
                        mock_parser_instance = MagicMock()
                        mock_parser_instance.parse.return_value = MagicMock(entities={})
                        mock_parser.return_value = mock_parser_instance
                        
                        out = StringIO()
                        cmd.stdout = out
                        
                        # Call handle
                        cmd.handle(**options)
                        
                        # Check that output_dir is resolved relative to cwd
                        expected_path = os.path.join(os.getcwd(), 'erexport')
                        assert captured_output_dir == expected_path, \
                            f"Output directory should be {expected_path}, got {captured_output_dir}"
    
    def test_absolute_path_used_directly(self):
        """
        Test that absolute paths are used directly without modification.
        
        Validates: Requirement 3.3
        """
        from x007007007.er_django.management.commands.er_export import Command
        from unittest.mock import Mock, patch, MagicMock
        
        cmd = Command()
        
        # Use a temporary directory as absolute path
        with tempfile.TemporaryDirectory() as tmpdir:
            absolute_path = tmpdir
            
            # Mock options with absolute output_dir
            options = {
                'apps': ['testapp'],
                'format': 'toml',
                'output': None,
                'output_dir': absolute_path,  # Absolute path
                'models': None,
                'exclude_apps': '',
                'include_django_apps': False,
                'name': None,
            }
            
            captured_output_dir = None
            
            def mock_ensure_directory_exists(path):
                nonlocal captured_output_dir
                captured_output_dir = path
            
            with patch('x007007007.er_django.management.commands.er_export.get_er_settings') as mock_settings:
                mock_settings.return_value = {
                    'migrations_dir': '/tmp/migrations',
                    'export_dir': '/tmp/export',
                    'auto_create_dirs': True,
                    'default_format': 'toml',
                    'include_django_apps': False,
                    'exclude_apps': [],
                    'file_prefix': '',
                    'file_suffix': '',
                }
                
                mock_app_config = MagicMock()
                mock_app_config.label = 'testapp'
                
                with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config', return_value=mock_app_config):
                    with patch('x007007007.er_django.management.commands.er_export.ensure_directory_exists', side_effect=mock_ensure_directory_exists):
                        with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser:
                            mock_parser_instance = MagicMock()
                            mock_parser_instance.parse.return_value = MagicMock(entities={})
                            mock_parser.return_value = mock_parser_instance
                            
                            out = StringIO()
                            cmd.stdout = out
                            
                            # Call handle
                            cmd.handle(**options)
                            
                            # Check that output_dir is the absolute path
                            assert captured_output_dir == absolute_path, \
                                f"Output directory should be {absolute_path}, got {captured_output_dir}"
    
    @override_settings(ER_EXPORT_DIR='/some/settings/path')
    def test_ignores_er_export_dir_setting(self):
        """
        Test that ER_EXPORT_DIR setting is ignored when output_dir is not specified.
        
        Validates: Requirement 3.5
        """
        from x007007007.er_django.management.commands.er_export import Command
        from unittest.mock import Mock, patch, MagicMock
        
        cmd = Command()
        
        # Mock options with no output_dir specified
        options = {
            'apps': ['testapp'],
            'format': 'toml',
            'output': None,
            'output_dir': None,  # Not specified
            'models': None,
            'exclude_apps': '',
            'include_django_apps': False,
            'name': None,
        }
        
        captured_output_dir = None
        
        def mock_ensure_directory_exists(path):
            nonlocal captured_output_dir
            captured_output_dir = path
        
        with patch('x007007007.er_django.management.commands.er_export.get_er_settings') as mock_settings:
            mock_settings.return_value = {
                'migrations_dir': '/tmp/migrations',
                'export_dir': '/some/settings/path',  # This should be ignored
                'auto_create_dirs': True,
                'default_format': 'toml',
                'include_django_apps': False,
                'exclude_apps': [],
                'file_prefix': '',
                'file_suffix': '',
            }
            
            mock_app_config = MagicMock()
            mock_app_config.label = 'testapp'
            
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config', return_value=mock_app_config):
                with patch('x007007007.er_django.management.commands.er_export.ensure_directory_exists', side_effect=mock_ensure_directory_exists):
                    with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser:
                        mock_parser_instance = MagicMock()
                        mock_parser_instance.parse.return_value = MagicMock(entities={})
                        mock_parser.return_value = mock_parser_instance
                        
                        out = StringIO()
                        cmd.stdout = out
                        
                        # Call handle
                        cmd.handle(**options)
                        
                        # Check that output_dir is ./src, not the settings path
                        expected_path = os.path.normpath(os.path.join(os.getcwd(), 'src'))
                        actual_path = os.path.normpath(captured_output_dir)
                        assert actual_path == expected_path, \
                            f"Output directory should be ./src, not settings path. Got {captured_output_dir}"
                        assert captured_output_dir != '/some/settings/path', \
                            "Output directory should not use ER_EXPORT_DIR setting"
    
    def test_relative_path_with_parent_directory(self):
        """
        Test that relative paths with parent directory references work correctly.
        
        Validates: Requirement 3.4
        """
        from x007007007.er_django.management.commands.er_export import Command
        from unittest.mock import Mock, patch, MagicMock
        
        cmd = Command()
        
        # Mock options with relative path containing ../
        options = {
            'apps': ['testapp'],
            'format': 'toml',
            'output': None,
            'output_dir': '../output',  # Relative path with parent reference
            'models': None,
            'exclude_apps': '',
            'include_django_apps': False,
            'name': None,
        }
        
        captured_output_dir = None
        
        def mock_ensure_directory_exists(path):
            nonlocal captured_output_dir
            captured_output_dir = path
        
        with patch('x007007007.er_django.management.commands.er_export.get_er_settings') as mock_settings:
            mock_settings.return_value = {
                'migrations_dir': '/tmp/migrations',
                'export_dir': '/tmp/export',
                'auto_create_dirs': True,
                'default_format': 'toml',
                'include_django_apps': False,
                'exclude_apps': [],
                'file_prefix': '',
                'file_suffix': '',
            }
            
            mock_app_config = MagicMock()
            mock_app_config.label = 'testapp'
            
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config', return_value=mock_app_config):
                with patch('x007007007.er_django.management.commands.er_export.ensure_directory_exists', side_effect=mock_ensure_directory_exists):
                    with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser:
                        mock_parser_instance = MagicMock()
                        mock_parser_instance.parse.return_value = MagicMock(entities={})
                        mock_parser.return_value = mock_parser_instance
                        
                        out = StringIO()
                        cmd.stdout = out
                        
                        # Call handle
                        cmd.handle(**options)
                        
                        # Check that output_dir is resolved relative to cwd
                        expected_path = os.path.join(os.getcwd(), '../output')
                        assert captured_output_dir == expected_path, \
                            f"Output directory should be {expected_path}, got {captured_output_dir}"


class TestErExportArgumentParser(TestCase):
    """Test argument parser for output-dir parameter"""
    
    def test_output_dir_default_is_src(self):
        """
        Test that --output-dir parameter defaults to 'src'.
        
        Validates: Requirement 2.1
        """
        from x007007007.er_django.management.commands.er_export import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_export')
        
        # Parse with no --output-dir argument
        options = parser.parse_args([])
        
        # Check that output_dir defaults to 'src'
        assert options.output_dir == 'src', "Default output_dir should be 'src'"
    
    def test_output_dir_accepts_value(self):
        """
        Test that --output-dir parameter accepts a value.
        """
        from x007007007.er_django.management.commands.er_export import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_export')
        
        # Parse with --output-dir argument
        options = parser.parse_args(['--output-dir', 'custom/path'])
        
        # Check that output_dir is set
        assert options.output_dir == 'custom/path', "output_dir should be 'custom/path'"
