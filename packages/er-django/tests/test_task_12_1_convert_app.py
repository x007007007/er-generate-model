"""
Integration test for Task 12.1: _convert_app() method implementation

This test verifies that the _convert_app() method:
- Reads and parses TOML files correctly
- Determines output directory based on framework and output-subdir
- Calls code generators to generate target framework code
- Handles TOML format errors with fail-fast strategy

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.8
"""
import pytest
from pathlib import Path
from io import StringIO

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

from django.core.management.base import CommandError
from django.test import TestCase
from x007007007.er_django.management.commands.er_convert import Command


class TestTask12_1ConvertApp(TestCase):
    """Test Task 12.1: _convert_app() method implementation"""
    
    def test_convert_app_reads_and_parses_toml(self, tmp_path=None):
        """
        Test that _convert_app reads and parses TOML file correctly.
        
        Requirements: 4.1, 4.8
        """
        if tmp_path is None:
            import tempfile
            tmp_path = Path(tempfile.mkdtemp())
        
        # Create a test TOML file
        toml_content = """
[entities.User]
[[entities.User.columns]]
name = "username"
type = "CharField"
max_length = 100

[[entities.User.columns]]
name = "email"
type = "EmailField"
"""
        
        # Create test app directory structure
        app_dir = tmp_path / "testapp"
        app_dir.mkdir(parents=True)
        toml_file = app_dir / "models.toml"
        toml_file.write_text(toml_content)
        
        # Mock AppConfig
        from unittest.mock import Mock, patch
        mock_app_config = Mock()
        mock_app_config.path = str(app_dir)
        mock_app_config.label = 'testapp'
        
        # Mock AppDiscoveryService
        with patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService') as mock_discovery:
            with patch('x007007007.er_django.management.commands.er_convert.apps') as mock_apps:
                mock_discovery.get_toml_path.return_value = toml_file
                mock_apps.get_app_config.return_value = mock_app_config
                
                cmd = Command()
                cmd.stdout = StringIO()
                
                # Call _convert_app
                files_generated = cmd._convert_app(
                    app_label='testapp',
                    framework='django',
                    output_subdir=None,
                    base_model_import=None
                )
                
                # Verify files were generated
                assert files_generated > 0, "Should generate at least one file"
                
                # Verify output directory was created
                output_dir = app_dir / "models"
                assert output_dir.exists(), "Output directory should be created"
    
    def test_convert_app_determines_output_dir_for_django(self, tmp_path=None):
        """
        Test that _convert_app determines correct output directory for Django framework.
        
        Requirements: 4.2
        """
        if tmp_path is None:
            import tempfile
            tmp_path = Path(tempfile.mkdtemp())
        
        toml_content = """
[entities.User]
[[entities.User.columns]]
name = "id"
type = "AutoField"
primary_key = true
"""
        
        app_dir = tmp_path / "testapp"
        app_dir.mkdir(parents=True)
        toml_file = app_dir / "models.toml"
        toml_file.write_text(toml_content)
        
        from unittest.mock import Mock, patch
        mock_app_config = Mock()
        mock_app_config.path = str(app_dir)
        mock_app_config.label = 'testapp'
        
        with patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService') as mock_discovery:
            with patch('x007007007.er_django.management.commands.er_convert.apps') as mock_apps:
                mock_discovery.get_toml_path.return_value = toml_file
                mock_apps.get_app_config.return_value = mock_app_config
                
                cmd = Command()
                cmd.stdout = StringIO()
                
                cmd._convert_app(
                    app_label='testapp',
                    framework='django',
                    output_subdir=None,
                    base_model_import=None
                )
                
                # Verify Django output directory
                django_output_dir = app_dir / "models"
                assert django_output_dir.exists(), "Django output directory should be 'models'"
    
    def test_convert_app_determines_output_dir_for_sqlalchemy(self, tmp_path=None):
        """
        Test that _convert_app determines correct output directory for SQLAlchemy framework.
        
        Requirements: 4.3
        """
        if tmp_path is None:
            import tempfile
            tmp_path = Path(tempfile.mkdtemp())
        
        toml_content = """
[entities.User]
[[entities.User.columns]]
name = "id"
type = "Integer"
primary_key = true
"""
        
        app_dir = tmp_path / "testapp"
        app_dir.mkdir(parents=True)
        toml_file = app_dir / "models.toml"
        toml_file.write_text(toml_content)
        
        from unittest.mock import Mock, patch
        mock_app_config = Mock()
        mock_app_config.path = str(app_dir)
        mock_app_config.label = 'testapp'
        
        with patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService') as mock_discovery:
            with patch('x007007007.er_django.management.commands.er_convert.apps') as mock_apps:
                mock_discovery.get_toml_path.return_value = toml_file
                mock_apps.get_app_config.return_value = mock_app_config
                
                cmd = Command()
                cmd.stdout = StringIO()
                
                cmd._convert_app(
                    app_label='testapp',
                    framework='sqlalchemy',
                    output_subdir=None,
                    base_model_import=None
                )
                
                # Verify SQLAlchemy output directory
                sqlalchemy_output_dir = app_dir / "sqlalchemy"
                assert sqlalchemy_output_dir.exists(), "SQLAlchemy output directory should be 'sqlalchemy'"
    
    def test_convert_app_uses_custom_output_subdir(self, tmp_path=None):
        """
        Test that _convert_app uses custom output subdirectory when specified.
        
        Requirements: 4.5
        """
        if tmp_path is None:
            import tempfile
            tmp_path = Path(tempfile.mkdtemp())
        
        toml_content = """
[entities.User]
[[entities.User.columns]]
name = "id"
type = "AutoField"
primary_key = true
"""
        
        app_dir = tmp_path / "testapp"
        app_dir.mkdir(parents=True)
        toml_file = app_dir / "models.toml"
        toml_file.write_text(toml_content)
        
        from unittest.mock import Mock, patch
        mock_app_config = Mock()
        mock_app_config.path = str(app_dir)
        mock_app_config.label = 'testapp'
        
        with patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService') as mock_discovery:
            with patch('x007007007.er_django.management.commands.er_convert.apps') as mock_apps:
                mock_discovery.get_toml_path.return_value = toml_file
                mock_apps.get_app_config.return_value = mock_app_config
                
                cmd = Command()
                cmd.stdout = StringIO()
                
                cmd._convert_app(
                    app_label='testapp',
                    framework='django',
                    output_subdir='custom_models',
                    base_model_import=None
                )
                
                # Verify custom output directory
                custom_output_dir = app_dir / "custom_models"
                assert custom_output_dir.exists(), "Custom output directory should be used"
    
    def test_convert_app_fails_fast_on_invalid_toml(self, tmp_path=None):
        """
        Test that _convert_app fails fast when TOML file has format errors.
        
        Requirements: 4.8
        """
        if tmp_path is None:
            import tempfile
            tmp_path = Path(tempfile.mkdtemp())
        
        # Create invalid TOML content
        invalid_toml = """
[entities.User
this is not valid TOML
"""
        
        app_dir = tmp_path / "testapp"
        app_dir.mkdir(parents=True)
        toml_file = app_dir / "models.toml"
        toml_file.write_text(invalid_toml)
        
        from unittest.mock import Mock, patch
        mock_app_config = Mock()
        mock_app_config.path = str(app_dir)
        mock_app_config.label = 'testapp'
        
        with patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService') as mock_discovery:
            with patch('x007007007.er_django.management.commands.er_convert.apps') as mock_apps:
                mock_discovery.get_toml_path.return_value = toml_file
                mock_apps.get_app_config.return_value = mock_app_config
                
                cmd = Command()
                cmd.stdout = StringIO()
                
                # Should raise CommandError on invalid TOML
                with pytest.raises(CommandError) as exc_info:
                    cmd._convert_app(
                        app_label='testapp',
                        framework='django',
                        output_subdir=None,
                        base_model_import=None
                    )
                
                # Verify error message mentions TOML parsing
                assert 'parse' in str(exc_info.value).lower() or 'toml' in str(exc_info.value).lower()
    
    def test_convert_app_generates_django_code(self, tmp_path=None):
        """
        Test that _convert_app generates Django model code correctly.
        
        Requirements: 4.1, 4.2
        """
        if tmp_path is None:
            import tempfile
            tmp_path = Path(tempfile.mkdtemp())
        
        toml_content = """
[entities.User]
[[entities.User.columns]]
name = "username"
type = "CharField"
max_length = 100

[[entities.User.columns]]
name = "email"
type = "EmailField"
"""
        
        app_dir = tmp_path / "testapp"
        app_dir.mkdir(parents=True)
        toml_file = app_dir / "models.toml"
        toml_file.write_text(toml_content)
        
        from unittest.mock import Mock, patch
        mock_app_config = Mock()
        mock_app_config.path = str(app_dir)
        mock_app_config.label = 'testapp'
        
        with patch('x007007007.er_django.management.commands.er_convert.AppDiscoveryService') as mock_discovery:
            with patch('x007007007.er_django.management.commands.er_convert.apps') as mock_apps:
                mock_discovery.get_toml_path.return_value = toml_file
                mock_apps.get_app_config.return_value = mock_app_config
                
                cmd = Command()
                cmd.stdout = StringIO()
                
                files_generated = cmd._convert_app(
                    app_label='testapp',
                    framework='django',
                    output_subdir=None,
                    base_model_import=None
                )
                
                # Verify files were generated
                assert files_generated > 0
                
                # Verify output directory contains Python files
                output_dir = app_dir / "models"
                python_files = list(output_dir.glob("*.py"))
                assert len(python_files) > 0, "Should generate Python files"
                
                # Verify __init__.py exists
                init_file = output_dir / "__init__.py"
                assert init_file.exists(), "Should generate __init__.py"
