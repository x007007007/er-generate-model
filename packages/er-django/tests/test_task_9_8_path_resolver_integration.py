"""
Unit tests for Task 9.8: PathResolver Integration in er_export command

Tests that er_export command properly integrates PathResolver to:
- Determine output paths for each app
- Set Entity.export_path for each entity
- Set Entity.package for each entity

Requirements: 2.1, 2.2, 2.3, 2.7, 7.1, 7.7
"""
import pytest
from pathlib import Path
import tempfile
import shutil

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

from django.test import TestCase
from django.apps import apps
from unittest.mock import Mock, patch, MagicMock
from x007007007.er_django.management.commands.er_export import Command
from x007007007.er.models import Entity, ERModel


class TestPathResolverIntegration(TestCase):
    """Test PathResolver integration in er_export command"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cmd = Command()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_path_resolver_called_for_each_app(self):
        """
        Test that PathResolver.resolve_output_path is called for each app.
        
        Validates: Requirements 2.1, 2.2, 2.3, 2.7
        """
        # Create mock app config
        mock_app_config = Mock()
        mock_app_config.label = 'testapp'
        mock_app_config.name = 'testproject.testapp'
        mock_app_config.path = str(Path(self.temp_dir) / 'testproject' / 'testapp')
        
        # Create mock ER model with entities
        mock_entity = Entity(name='TestModel', package='testproject.testapp.models')
        mock_er_model = ERModel()
        mock_er_model.entities = {'TestModel': mock_entity}
        
        # Mock the parser
        with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.return_value = mock_er_model
            mock_parser_class.return_value = mock_parser
            
            # Mock PathResolver
            with patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_path_resolver:
                mock_path_resolver.resolve_output_path.return_value = Path(self.temp_dir) / 'output.toml'
                
                # Mock apps.get_app_config
                with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_get_app:
                    mock_get_app.return_value = mock_app_config
                    
                    # Mock renderer
                    with patch('x007007007.er_django.renderers.TOMLRenderer') as mock_renderer_class:
                        mock_renderer = Mock()
                        mock_renderer.render.return_value = '[entities]'
                        mock_renderer_class.return_value = mock_renderer
                        
                        # Mock apps.get_app_configs for the initial app discovery
                        with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_get_configs:
                            mock_get_configs.return_value = []
                            
                            # Call the command
                            options = {
                                'apps': ['testapp'],
                                'format': 'toml',
                                'output': None,
                                'output_dir': self.temp_dir,
                                'models': None,
                                'exclude_apps': '',
                                'include_django_apps': False,
                                'name': None,
                            }
                            
                            self.cmd.handle(**options)
                            
                            # Verify PathResolver.resolve_output_path was called
                            mock_path_resolver.resolve_output_path.assert_called_once()
                            call_args = mock_path_resolver.resolve_output_path.call_args
                            
                            # Check arguments
                            assert call_args[1]['app_config'] == mock_app_config
                            assert call_args[1]['base_dir'] == self.temp_dir
                            assert call_args[1]['format'] == 'toml'
    
    def test_entity_export_path_set_from_path_resolver(self):
        """
        Test that Entity.export_path is set from PathResolver.resolve_output_path().
        
        Validates: Requirements 2.1, 2.7
        """
        # Create mock app config
        mock_app_config = Mock()
        mock_app_config.label = 'testapp'
        mock_app_config.name = 'testproject.testapp'
        mock_app_config.path = str(Path(self.temp_dir) / 'testproject' / 'testapp')
        
        # Create mock ER model with entities
        mock_entity1 = Entity(name='Model1', package='testproject.testapp.models')
        mock_entity2 = Entity(name='Model2', package='testproject.testapp.models')
        mock_er_model = ERModel()
        mock_er_model.entities = {'Model1': mock_entity1, 'Model2': mock_entity2}
        
        expected_path = Path(self.temp_dir) / 'testproject' / 'testapp' / 'models.toml'
        
        # Mock the parser
        with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.return_value = mock_er_model
            mock_parser_class.return_value = mock_parser
            
            # Mock PathResolver
            with patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_path_resolver:
                mock_path_resolver.resolve_output_path.return_value = expected_path
                
                # Mock apps.get_app_config
                with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_get_app:
                    mock_get_app.return_value = mock_app_config
                    
                    # Mock renderer
                    with patch('x007007007.er_django.renderers.TOMLRenderer') as mock_renderer_class:
                        mock_renderer = Mock()
                        mock_renderer.render.return_value = '[entities]'
                        mock_renderer_class.return_value = mock_renderer
                        
                        # Mock apps.get_app_configs
                        with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_get_configs:
                            mock_get_configs.return_value = []
                            
                            # Call the command
                            options = {
                                'apps': ['testapp'],
                                'format': 'toml',
                                'output': None,
                                'output_dir': self.temp_dir,
                                'models': None,
                                'exclude_apps': '',
                                'include_django_apps': False,
                                'name': None,
                            }
                            
                            self.cmd.handle(**options)
                            
                            # Verify that export_path was set for all entities
                            assert mock_entity1.export_path == str(expected_path)
                            assert mock_entity2.export_path == str(expected_path)
    
    def test_entity_package_preserved_from_parser(self):
        """
        Test that Entity.package is preserved from DjangoModelParser.
        
        Validates: Requirements 7.1, 7.7
        """
        # Create mock app config
        mock_app_config = Mock()
        mock_app_config.label = 'testapp'
        mock_app_config.name = 'testproject.testapp'
        mock_app_config.path = str(Path(self.temp_dir) / 'testproject' / 'testapp')
        
        # Create mock ER model with entities that have package set
        expected_package = 'testproject.testapp.models'
        mock_entity = Entity(name='TestModel', package=expected_package)
        mock_er_model = ERModel()
        mock_er_model.entities = {'TestModel': mock_entity}
        
        # Mock the parser
        with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.return_value = mock_er_model
            mock_parser_class.return_value = mock_parser
            
            # Mock PathResolver
            with patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_path_resolver:
                mock_path_resolver.resolve_output_path.return_value = Path(self.temp_dir) / 'output.toml'
                
                # Mock apps.get_app_config
                with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_get_app:
                    mock_get_app.return_value = mock_app_config
                    
                    # Mock renderer
                    with patch('x007007007.er_django.renderers.TOMLRenderer') as mock_renderer_class:
                        mock_renderer = Mock()
                        mock_renderer.render.return_value = '[entities]'
                        mock_renderer_class.return_value = mock_renderer
                        
                        # Mock apps.get_app_configs
                        with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_get_configs:
                            mock_get_configs.return_value = []
                            
                            # Call the command
                            options = {
                                'apps': ['testapp'],
                                'format': 'toml',
                                'output': None,
                                'output_dir': self.temp_dir,
                                'models': None,
                                'exclude_apps': '',
                                'include_django_apps': False,
                                'name': None,
                            }
                            
                            self.cmd.handle(**options)
                            
                            # Verify that package was preserved
                            assert mock_entity.package == expected_package
    
    def test_path_resolver_error_raises_command_error(self):
        """
        Test that PathResolver errors are caught and converted to CommandError (fail-fast).
        
        Validates: Requirements 2.6
        """
        from django.core.management.base import CommandError
        
        # Create mock app config
        mock_app_config = Mock()
        mock_app_config.label = 'testapp'
        mock_app_config.name = 'testproject.testapp'
        mock_app_config.path = str(Path(self.temp_dir) / 'testproject' / 'testapp')
        
        # Create mock ER model with entities
        mock_entity = Entity(name='TestModel', package='testproject.testapp.models')
        mock_er_model = ERModel()
        mock_er_model.entities = {'TestModel': mock_entity}
        
        # Mock the parser
        with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.return_value = mock_er_model
            mock_parser_class.return_value = mock_parser
            
            # Mock PathResolver to raise ValueError
            with patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_path_resolver:
                mock_path_resolver.resolve_output_path.side_effect = ValueError("Cannot determine models location")
                
                # Mock apps.get_app_config
                with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_get_app:
                    mock_get_app.return_value = mock_app_config
                    
                    # Mock apps.get_app_configs
                    with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_get_configs:
                        mock_get_configs.return_value = []
                        
                        # Call the command and expect CommandError
                        options = {
                            'apps': ['testapp'],
                            'format': 'toml',
                            'output': None,
                            'output_dir': self.temp_dir,
                            'models': None,
                            'exclude_apps': '',
                            'include_django_apps': False,
                            'name': None,
                        }
                        
                        with pytest.raises(CommandError) as exc_info:
                            self.cmd.handle(**options)
                        
                        # Verify error message contains app label and original error
                        assert 'testapp' in str(exc_info.value)
                        assert 'Cannot determine models location' in str(exc_info.value)
    
    def test_directory_creation_on_write(self):
        """
        Test that parent directories are created when writing output file.
        
        Validates: Requirements 2.4
        """
        # Create mock app config
        mock_app_config = Mock()
        mock_app_config.label = 'testapp'
        mock_app_config.name = 'testproject.testapp'
        mock_app_config.path = str(Path(self.temp_dir) / 'testproject' / 'testapp')
        
        # Create mock ER model with entities
        mock_entity = Entity(name='TestModel', package='testproject.testapp.models')
        mock_er_model = ERModel()
        mock_er_model.entities = {'TestModel': mock_entity}
        
        # Create a nested path that doesn't exist
        nested_path = Path(self.temp_dir) / 'deep' / 'nested' / 'path' / 'models.toml'
        
        # Mock the parser
        with patch('x007007007.er_django.management.commands.er_export.DjangoModelParser') as mock_parser_class:
            mock_parser = Mock()
            mock_parser.parse.return_value = mock_er_model
            mock_parser_class.return_value = mock_parser
            
            # Mock PathResolver
            with patch('x007007007.er_django.management.commands.er_export.PathResolver') as mock_path_resolver:
                mock_path_resolver.resolve_output_path.return_value = nested_path
                
                # Mock apps.get_app_config
                with patch('x007007007.er_django.management.commands.er_export.apps.get_app_config') as mock_get_app:
                    mock_get_app.return_value = mock_app_config
                    
                    # Mock renderer
                    with patch('x007007007.er_django.renderers.TOMLRenderer') as mock_renderer_class:
                        mock_renderer = Mock()
                        mock_renderer.render.return_value = '[entities]'
                        mock_renderer_class.return_value = mock_renderer
                        
                        # Mock apps.get_app_configs
                        with patch('x007007007.er_django.management.commands.er_export.apps.get_app_configs') as mock_get_configs:
                            mock_get_configs.return_value = []
                            
                            # Call the command
                            options = {
                                'apps': ['testapp'],
                                'format': 'toml',
                                'output': None,
                                'output_dir': self.temp_dir,
                                'models': None,
                                'exclude_apps': '',
                                'include_django_apps': False,
                                'name': None,
                            }
                            
                            self.cmd.handle(**options)
                            
                            # Verify that the nested directory was created
                            assert nested_path.parent.exists()
                            # Verify that the file was written
                            assert nested_path.exists()
