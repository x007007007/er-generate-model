"""
Basic unit tests for er_convert command - Task 11.1

Tests for command structure, arguments, and help text.
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
from django.test import TestCase


class TestErConvertCommandStructure(TestCase):
    """Test er_convert command structure - Task 11.1"""
    
    def test_command_can_be_imported(self):
        """Test that the er_convert command can be imported successfully."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        assert cmd is not None, "Command should be instantiable"
    
    def test_command_has_help_text(self):
        """Test that the command has appropriate help text."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        assert cmd.help, "Command should have help text"
        assert 'TOML' in cmd.help or 'toml' in cmd.help, "Help text should mention TOML"
        assert 'convert' in cmd.help.lower(), "Help text should mention conversion"
    
    def test_command_has_apps_argument(self):
        """Test that the command accepts apps as positional arguments."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with app names
        options = parser.parse_args(['app1', 'app2'])
        
        assert options.apps == ['app1', 'app2'], "Should accept multiple app names"
    
    def test_command_has_framework_argument(self):
        """Test that the command has --framework argument with correct default."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with no --framework argument
        options = parser.parse_args([])
        
        assert options.framework == 'django', "Default framework should be 'django'"
    
    def test_framework_argument_accepts_django(self):
        """Test that --framework accepts 'django' value."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with --framework=django
        options = parser.parse_args(['--framework', 'django'])
        
        assert options.framework == 'django', "Should accept 'django' framework"
    
    def test_framework_argument_accepts_sqlalchemy(self):
        """Test that --framework accepts 'sqlalchemy' value."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with --framework=sqlalchemy
        options = parser.parse_args(['--framework', 'sqlalchemy'])
        
        assert options.framework == 'sqlalchemy', "Should accept 'sqlalchemy' framework"
    
    def test_command_has_output_subdir_argument(self):
        """Test that the command has --output-subdir argument."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with --output-subdir
        options = parser.parse_args(['--output-subdir', 'custom'])
        
        assert options.output_subdir == 'custom', "Should accept custom output subdirectory"
    
    def test_output_subdir_defaults_to_none(self):
        """Test that --output-subdir defaults to None."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with no --output-subdir argument
        options = parser.parse_args([])
        
        assert options.output_subdir is None, "Default output_subdir should be None"
    
    def test_command_has_base_model_import_argument(self):
        """Test that the command has --base-model-import argument."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with --base-model-import
        options = parser.parse_args(['--base-model-import', 'myproject.database.Base'])
        
        assert options.base_model_import == 'myproject.database.Base', \
            "Should accept custom base model import path"
    
    def test_base_model_import_defaults_to_none(self):
        """Test that --base-model-import defaults to None."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with no --base-model-import argument
        options = parser.parse_args([])
        
        assert options.base_model_import is None, "Default base_model_import should be None"
    
    def test_apps_argument_is_optional(self):
        """Test that apps argument is optional (for auto-discovery)."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with no apps
        options = parser.parse_args([])
        
        assert options.apps == [], "Apps should be empty list when not specified"
    
    def test_all_arguments_together(self):
        """Test that all arguments can be used together."""
        from x007007007.er_django.management.commands.er_convert import Command
        
        cmd = Command()
        parser = cmd.create_parser('manage.py', 'er_convert')
        
        # Parse with all arguments
        options = parser.parse_args([
            'app1', 'app2',
            '--framework', 'sqlalchemy',
            '--output-subdir', 'generated',
            '--base-model-import', 'myproject.db.Base'
        ])
        
        assert options.apps == ['app1', 'app2']
        assert options.framework == 'sqlalchemy'
        assert options.output_subdir == 'generated'
        assert options.base_model_import == 'myproject.db.Base'
