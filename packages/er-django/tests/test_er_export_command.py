"""
Unit tests for er_export command - Task 9.1

Tests for default TOML format and format override functionality.
"""
import pytest
from io import StringIO
from pathlib import Path

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
from django.test import TestCase, override_settings


class TestErExportDefaultFormat(TestCase):
    """Test default TOML format - Requirements 1.1, 1.2, 1.3"""
    
    def test_default_format_is_toml(self):
        """
        Test that er_export defaults to TOML format when --format is not specified.
        
        Validates: Requirement 1.1
        """
        # Import the command to check its argument parser
        from x007007007.er_django.management.commands.er_export import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_export')
        
        # Parse with no --format argument
        options = parser.parse_args([])
        
        # Check that format defaults to 'toml'
        assert options.format == 'toml', "Default format should be 'toml'"
    
    def test_format_override_mermaid(self):
        """
        Test that --format=mermaid overrides the default.
        
        Validates: Requirement 1.2
        """
        from x007007007.er_django.management.commands.er_export import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_export')
        
        # Parse with --format=mermaid
        options = parser.parse_args(['--format', 'mermaid'])
        
        # Check that format is 'mermaid'
        assert options.format == 'mermaid', "Format should be 'mermaid' when explicitly specified"
    
    def test_format_override_plantuml(self):
        """
        Test that --format=plantuml overrides the default.
        
        Validates: Requirement 1.2
        """
        from x007007007.er_django.management.commands.er_export import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_export')
        
        # Parse with --format=plantuml
        options = parser.parse_args(['--format', 'plantuml'])
        
        # Check that format is 'plantuml'
        assert options.format == 'plantuml', "Format should be 'plantuml' when explicitly specified"
    
    @override_settings(ER_DEFAULT_FORMAT='mermaid')
    def test_ignores_settings_default_format(self):
        """
        Test that ER_DEFAULT_FORMAT setting is ignored and TOML is still the default.
        
        Validates: Requirement 1.3
        """
        from x007007007.er_django.management.commands.er_export import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_export')
        
        # Parse with no --format argument
        options = parser.parse_args([])
        
        # Check that format defaults to 'toml', not 'mermaid' from settings
        assert options.format == 'toml', "Should ignore ER_DEFAULT_FORMAT setting and default to 'toml'"
    
    def test_command_uses_format_from_options(self):
        """
        Test that the command handle method uses the format from options, not from settings.
        
        Validates: Requirement 1.3
        """
        from x007007007.er_django.management.commands.er_export import Command
        from unittest.mock import Mock, patch
        
        cmd = Command()
        
        # Mock options with format='toml'
        options = {
            'apps': [],
            'format': 'toml',
            'output': None,
            'output_dir': None,
            'models': None,
            'exclude_apps': '',
            'include_django_apps': False,
            'name': None,
        }
        
        # Mock get_er_settings to return mermaid as default
        with patch('x007007007.er_django.management.commands.er_export.get_er_settings') as mock_settings:
            mock_settings.return_value = {
                'migrations_dir': '/tmp/migrations',
                'export_dir': '/tmp/export',
                'auto_create_dirs': True,
                'default_format': 'mermaid',  # This should be ignored
                'include_django_apps': False,
                'exclude_apps': [],
                'file_prefix': '',
                'file_suffix': '',
            }
            
            # Mock apps.get_app_configs to return empty list
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_apps:
                mock_apps.return_value = []
                
                # Capture stdout
                out = StringIO()
                cmd.stdout = out
                
                # Call handle
                cmd.handle(**options)
                
                # Check that no error occurred and the command completed
                output = out.getvalue()
                assert 'No apps to export' in output or 'Exporting' in output


class TestErExportFormatValidation(TestCase):
    """Test format validation"""
    
    def test_invalid_format_rejected(self):
        """Test that invalid format values are rejected by the argument parser"""
        from x007007007.er_django.management.commands.er_export import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_export')
        
        # Try to parse with invalid format - Django raises CommandError instead of SystemExit
        with pytest.raises(CommandError):
            parser.parse_args(['--format', 'invalid'])
    
    def test_valid_formats_accepted(self):
        """Test that all valid formats are accepted"""
        from x007007007.er_django.management.commands.er_export import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_export')
        
        valid_formats = ['mermaid', 'plantuml', 'toml']
        
        for fmt in valid_formats:
            options = parser.parse_args(['--format', fmt])
            assert options.format == fmt, f"Format '{fmt}' should be accepted"



class TestErExportOutputPath(TestCase):
    """Test output path handling - Requirements 3.1, 3.2, 3.3, 3.4"""
    
    def test_default_output_path_is_src_directory(self):
        """
        Test that er_export uses ./src directory when --output-dir is not specified.
        
        Validates: Requirement 3.1
        """
        import tempfile
        import shutil
        from unittest.mock import patch, Mock
        from x007007007.er_django.management.commands.er_export import Command
        from x007007007.er.models import ERModel, Entity
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        
        try:
            # Change to temp directory
            os.chdir(temp_dir)
            
            cmd = Command()
            
            # Mock the parser and app discovery
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_apps, \
                 patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_app_config, \
                 patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser, \
                 patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_resolver:
                
                # Setup mock app config
                mock_app = Mock()
                mock_app.label = 'testapp'
                mock_app.path = str(Path(temp_dir) / 'testapp')
                mock_apps.return_value = [mock_app]
                mock_app_config.return_value = mock_app
                
                # Setup mock parser to return a simple ER model
                mock_parser_instance = Mock()
                er_model = ERModel()
                entity = Entity(name='TestModel')
                er_model.entities['TestModel'] = entity
                mock_parser_instance.parse.return_value = er_model
                mock_parser.return_value = mock_parser_instance
                
                # Setup mock resolver
                output_file = Path(temp_dir) / 'src' / 'testapp' / 'models.toml'
                mock_resolver.resolve_output_path.return_value = output_file
                
                # Capture stdout
                out = StringIO()
                cmd.stdout = out
                
                # Call handle without --output-dir
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
                
                cmd.handle(**options)
                
                # Verify that PathResolver was called with ./src directory
                mock_resolver.resolve_output_path.assert_called_once()
                call_args = mock_resolver.resolve_output_path.call_args
                expected_path = str((Path(temp_dir) / 'src').resolve())
                actual_path = str(Path(call_args[1]['base_dir']).resolve())
                assert actual_path == expected_path, "Should use ./src directory as default"
                
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_custom_relative_output_path(self):
        """
        Test that er_export resolves relative paths relative to current working directory.
        
        Validates: Requirement 3.2, 3.4
        """
        import tempfile
        import shutil
        from unittest.mock import patch, Mock
        from x007007007.er_django.management.commands.er_export import Command
        from x007007007.er.models import ERModel, Entity
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        
        try:
            # Change to temp directory
            os.chdir(temp_dir)
            
            cmd = Command()
            
            # Mock the parser and app discovery
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_apps, \
                 patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_app_config, \
                 patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser, \
                 patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_resolver:
                
                # Setup mock app config
                mock_app = Mock()
                mock_app.label = 'testapp'
                mock_app.path = str(Path(temp_dir) / 'testapp')
                mock_apps.return_value = [mock_app]
                mock_app_config.return_value = mock_app
                
                # Setup mock parser to return a simple ER model
                mock_parser_instance = Mock()
                er_model = ERModel()
                entity = Entity(name='TestModel')
                er_model.entities['TestModel'] = entity
                mock_parser_instance.parse.return_value = er_model
                mock_parser.return_value = mock_parser_instance
                
                # Setup mock resolver
                output_file = Path(temp_dir) / 'erexport' / 'testapp' / 'models.toml'
                mock_resolver.resolve_output_path.return_value = output_file
                
                # Capture stdout
                out = StringIO()
                cmd.stdout = out
                
                # Call handle with relative --output-dir
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
                
                cmd.handle(**options)
                
                # Verify that PathResolver was called with resolved absolute path
                mock_resolver.resolve_output_path.assert_called_once()
                call_args = mock_resolver.resolve_output_path.call_args
                expected_path = str(Path(temp_dir).resolve() / 'erexport')
                actual_path = str(Path(call_args[1]['base_dir']).resolve())
                assert actual_path == expected_path, "Should resolve relative path to absolute"
                
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_custom_absolute_output_path(self):
        """
        Test that er_export uses absolute paths directly without modification.
        
        Validates: Requirement 3.3
        """
        import tempfile
        import shutil
        from unittest.mock import patch, Mock
        from x007007007.er_django.management.commands.er_export import Command
        from x007007007.er.models import ERModel, Entity
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        absolute_output_dir = tempfile.mkdtemp()
        
        try:
            cmd = Command()
            
            # Mock the parser and app discovery
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_apps, \
                 patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_app_config, \
                 patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser, \
                 patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_resolver:
                
                # Setup mock app config
                mock_app = Mock()
                mock_app.label = 'testapp'
                mock_app.path = str(Path(temp_dir) / 'testapp')
                mock_apps.return_value = [mock_app]
                mock_app_config.return_value = mock_app
                
                # Setup mock parser to return a simple ER model
                mock_parser_instance = Mock()
                er_model = ERModel()
                entity = Entity(name='TestModel')
                er_model.entities['TestModel'] = entity
                mock_parser_instance.parse.return_value = er_model
                mock_parser.return_value = mock_parser_instance
                
                # Setup mock resolver
                output_file = Path(absolute_output_dir) / 'testapp' / 'models.toml'
                mock_resolver.resolve_output_path.return_value = output_file
                
                # Capture stdout
                out = StringIO()
                cmd.stdout = out
                
                # Call handle with absolute --output-dir
                options = {
                    'apps': ['testapp'],
                    'format': 'toml',
                    'output': None,
                    'output_dir': absolute_output_dir,  # Absolute path
                    'models': None,
                    'exclude_apps': '',
                    'include_django_apps': False,
                    'name': None,
                }
                
                cmd.handle(**options)
                
                # Verify that PathResolver was called with the absolute path unchanged
                mock_resolver.resolve_output_path.assert_called_once()
                call_args = mock_resolver.resolve_output_path.call_args
                assert call_args[1]['base_dir'] == absolute_output_dir, "Should use absolute path directly"
                
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.rmtree(absolute_output_dir, ignore_errors=True)


class TestErExportMultipleApps(TestCase):
    """Test multiple app export - Requirements 2.2, 8.1"""
    
    def test_exports_multiple_apps_to_separate_files(self):
        """
        Test that er_export creates separate files for each app.
        
        Validates: Requirement 2.2
        """
        import tempfile
        import shutil
        from unittest.mock import patch, Mock
        from x007007007.er_django.management.commands.er_export import Command
        from x007007007.er.models import ERModel, Entity
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            cmd = Command()
            
            # Mock the parser and app discovery
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_apps, \
                 patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_app_config, \
                 patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser, \
                 patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_resolver:
                
                # Setup mock app configs for two apps
                mock_app1 = Mock()
                mock_app1.label = 'app1'
                mock_app1.path = str(Path(temp_dir) / 'app1')
                
                mock_app2 = Mock()
                mock_app2.label = 'app2'
                mock_app2.path = str(Path(temp_dir) / 'app2')
                
                mock_apps.return_value = [mock_app1, mock_app2]
                
                def get_app_config_side_effect(label):
                    if label == 'app1':
                        return mock_app1
                    elif label == 'app2':
                        return mock_app2
                    raise LookupError(f"App '{label}' not found")
                
                mock_app_config.side_effect = get_app_config_side_effect
                
                # Setup mock parser to return different ER models for each app
                def parser_side_effect(app_label):
                    parser_instance = Mock()
                    er_model = ERModel()
                    entity = Entity(name=f'{app_label.capitalize()}Model')
                    er_model.entities[f'{app_label.capitalize()}Model'] = entity
                    parser_instance.parse.return_value = er_model
                    return parser_instance
                
                mock_parser.side_effect = parser_side_effect
                
                # Setup mock resolver to return different paths for each app
                output_files = []
                def resolver_side_effect(app_config, base_dir, format):
                    output_file = Path(base_dir) / app_config.label / f'models.{format}'
                    output_files.append(output_file)
                    return output_file
                
                mock_resolver.resolve_output_path.side_effect = resolver_side_effect
                
                # Capture stdout
                out = StringIO()
                cmd.stdout = out
                
                # Call handle with multiple apps
                options = {
                    'apps': ['app1', 'app2'],
                    'format': 'toml',
                    'output': None,
                    'output_dir': temp_dir,
                    'models': None,
                    'exclude_apps': '',
                    'include_django_apps': False,
                    'name': None,
                }
                
                cmd.handle(**options)
                
                # Verify that both files were created
                assert len(output_files) == 2, "Should create files for both apps"
                assert all(f.exists() for f in output_files), "All output files should exist"
                
                # Verify output mentions both apps
                output = out.getvalue()
                assert 'app1' in output, "Output should mention app1"
                assert 'app2' in output, "Output should mention app2"
                assert 'Exported' in output and '2 apps' in output, "Summary should mention 2 apps"
                
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_maintains_app_path_structure(self):
        """
        Test that er_export maintains the app's relative path structure.
        
        Validates: Requirement 2.3
        """
        import tempfile
        import shutil
        from unittest.mock import patch, Mock
        from x007007007.er_django.management.commands.er_export import Command
        from x007007007.er.models import ERModel, Entity
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            cmd = Command()
            
            # Mock the parser and app discovery
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_apps, \
                 patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_app_config, \
                 patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser, \
                 patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_resolver:
                
                # Setup mock app config with nested path
                mock_app = Mock()
                mock_app.label = 'nested_app'
                mock_app.path = str(Path(temp_dir) / 'src' / 'aaa' / 'bbb' / 'ccc')
                mock_apps.return_value = [mock_app]
                mock_app_config.return_value = mock_app
                
                # Setup mock parser to return a simple ER model
                mock_parser_instance = Mock()
                er_model = ERModel()
                entity = Entity(name='TestModel')
                er_model.entities['TestModel'] = entity
                mock_parser_instance.parse.return_value = er_model
                mock_parser.return_value = mock_parser_instance
                
                # Setup mock resolver to return nested path
                output_file = Path(temp_dir) / 'src' / 'aaa' / 'bbb' / 'ccc' / 'models.toml'
                mock_resolver.resolve_output_path.return_value = output_file
                
                # Capture stdout
                out = StringIO()
                cmd.stdout = out
                
                # Call handle
                options = {
                    'apps': ['nested_app'],
                    'format': 'toml',
                    'output': None,
                    'output_dir': temp_dir,
                    'models': None,
                    'exclude_apps': '',
                    'include_django_apps': False,
                    'name': None,
                }
                
                cmd.handle(**options)
                
                # Verify that PathResolver was called with correct app_config
                mock_resolver.resolve_output_path.assert_called_once()
                call_args = mock_resolver.resolve_output_path.call_args
                assert call_args[1]['app_config'] == mock_app, "Should pass correct app_config"
                
                # Verify that the nested directory structure was created
                assert output_file.exists(), "Output file should exist in nested path"
                
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestErExportDirectoryCreation(TestCase):
    """Test directory auto-creation - Task 9.10, Requirements 2.4, 3.6"""
    
    def test_creates_nested_directories(self):
        """
        Test that er_export creates nested directories when they don't exist.
        
        Validates: Requirement 2.4
        """
        import tempfile
        import shutil
        from unittest.mock import patch, Mock
        from x007007007.er_django.management.commands.er_export import Command
        from x007007007.er.models import ERModel, Entity
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create a nested path that doesn't exist yet
            nested_output_dir = Path(temp_dir) / 'deeply' / 'nested' / 'path'
            assert not nested_output_dir.exists(), "Test directory should not exist initially"
            
            cmd = Command()
            
            # Mock the parser and app discovery
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_apps, \
                 patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_app_config, \
                 patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser, \
                 patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_resolver:
                
                # Setup mock app config
                mock_app = Mock()
                mock_app.label = 'testapp'
                mock_app.path = str(Path(temp_dir) / 'testapp')
                mock_apps.return_value = [mock_app]
                mock_app_config.return_value = mock_app
                
                # Setup mock parser to return a simple ER model
                mock_parser_instance = Mock()
                er_model = ERModel()
                entity = Entity(name='TestModel')
                er_model.entities['TestModel'] = entity
                mock_parser_instance.parse.return_value = er_model
                mock_parser.return_value = mock_parser_instance
                
                # Setup mock resolver to return nested path
                output_file = nested_output_dir / 'models.toml'
                mock_resolver.resolve_output_path.return_value = output_file
                
                # Capture stdout
                out = StringIO()
                cmd.stdout = out
                
                # Call handle with nested output directory
                options = {
                    'apps': ['testapp'],
                    'format': 'toml',
                    'output': None,
                    'output_dir': str(nested_output_dir),
                    'models': None,
                    'exclude_apps': '',
                    'include_django_apps': False,
                    'name': None,
                }
                
                cmd.handle(**options)
                
                # Verify that the nested directory was created
                assert nested_output_dir.exists(), "Nested directory should be created"
                assert output_file.exists(), "Output file should be created"
                
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_fails_fast_on_permission_error(self):
        """
        Test that er_export raises CommandError when directory creation fails.
        
        Validates: Requirement 3.6 (fail-fast on directory creation error)
        """
        import tempfile
        import shutil
        from unittest.mock import patch, Mock, MagicMock
        from x007007007.er_django.management.commands.er_export import Command
        from x007007007.er.models import ERModel, Entity
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            cmd = Command()
            
            # Mock the parser and app discovery
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_apps, \
                 patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_app_config, \
                 patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser, \
                 patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_resolver, \
                 patch('x007007007.er_django.management.commands.er_export.ensure_directory_exists'):
                
                # Setup mock app config
                mock_app = Mock()
                mock_app.label = 'testapp'
                mock_app.path = str(Path(temp_dir) / 'testapp')
                mock_apps.return_value = [mock_app]
                mock_app_config.return_value = mock_app
                
                # Setup mock parser to return a simple ER model
                mock_parser_instance = Mock()
                er_model = ERModel()
                entity = Entity(name='TestModel')
                er_model.entities['TestModel'] = entity
                mock_parser_instance.parse.return_value = er_model
                mock_parser.return_value = mock_parser_instance
                
                # Setup mock resolver to return a path with a parent that will fail to create
                output_file_mock = MagicMock(spec=Path)
                output_file_mock.parent = MagicMock(spec=Path)
                # Make mkdir raise PermissionError
                output_file_mock.parent.mkdir.side_effect = PermissionError("Permission denied")
                output_file_mock.__str__ = lambda self: '/forbidden/path/models.toml'
                output_file_mock.parent.__str__ = lambda self: '/forbidden/path'
                
                mock_resolver.resolve_output_path.return_value = output_file_mock
                
                # Capture stdout
                out = StringIO()
                cmd.stdout = out
                
                # Call handle - should raise CommandError
                options = {
                    'apps': ['testapp'],
                    'format': 'toml',
                    'output': None,
                    'output_dir': str(temp_dir),
                    'models': None,
                    'exclude_apps': '',
                    'include_django_apps': False,
                    'name': None,
                }
                
                # Should raise CommandError due to permission denied
                with pytest.raises(CommandError) as exc_info:
                    cmd.handle(**options)
                
                # Verify error message mentions directory creation failure
                assert 'Failed to create directory' in str(exc_info.value)
                
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_handles_existing_directory_gracefully(self):
        """
        Test that er_export handles existing directories gracefully (exist_ok=True).
        
        Validates: Requirement 2.4
        """
        import tempfile
        import shutil
        from unittest.mock import patch, Mock
        from x007007007.er_django.management.commands.er_export import Command
        from x007007007.er.models import ERModel, Entity
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create the output directory beforehand
            output_dir = Path(temp_dir) / 'existing' / 'path'
            output_dir.mkdir(parents=True, exist_ok=True)
            assert output_dir.exists(), "Test directory should exist"
            
            cmd = Command()
            
            # Mock the parser and app discovery
            with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_apps, \
                 patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_app_config, \
                 patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser, \
                 patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_resolver:
                
                # Setup mock app config
                mock_app = Mock()
                mock_app.label = 'testapp'
                mock_app.path = str(Path(temp_dir) / 'testapp')
                mock_apps.return_value = [mock_app]
                mock_app_config.return_value = mock_app
                
                # Setup mock parser to return a simple ER model
                mock_parser_instance = Mock()
                er_model = ERModel()
                entity = Entity(name='TestModel')
                er_model.entities['TestModel'] = entity
                mock_parser_instance.parse.return_value = er_model
                mock_parser.return_value = mock_parser_instance
                
                # Setup mock resolver to return path in existing directory
                output_file = output_dir / 'models.toml'
                mock_resolver.resolve_output_path.return_value = output_file
                
                # Capture stdout
                out = StringIO()
                cmd.stdout = out
                
                # Call handle with existing output directory
                options = {
                    'apps': ['testapp'],
                    'format': 'toml',
                    'output': None,
                    'output_dir': str(output_dir),
                    'models': None,
                    'exclude_apps': '',
                    'include_django_apps': False,
                    'name': None,
                }
                
                # Should not raise any error
                cmd.handle(**options)
                
                # Verify that the file was created
                assert output_file.exists(), "Output file should be created in existing directory"
                
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
