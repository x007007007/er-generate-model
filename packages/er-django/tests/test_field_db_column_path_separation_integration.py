"""
End-to-end integration tests for field-db-column-and-path-separation spec.

This test verifies the complete workflow of:
1. db_column parameter support in Django models
2. Path separation (scan_path vs output_path)
3. Third-party package output with prefixes

Requirements tested: 1.1, 1.2, 1.3, 1.4, 2.2, 2.3, 2.4, 3.3, 3.4, 3.6
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
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()

from django.db import models
from django.test import TestCase
from x007007007.er_django.parser import DjangoModelParser
from x007007007.er_django.path_configuration import PathConfiguration
from x007007007.er_django.path_resolver import PathResolver
from x007007007.er_django.renderers import TOMLRenderer
from x007007007.er.renderers.python.django import DjangoPackageRenderer
import toml


class TestDbColumnIntegration(TestCase):
    """Test db_column functionality end-to-end"""
    
    def test_db_column_parsing_and_toml_output(self):
        """
        Test that db_column is correctly parsed from Django models and output to TOML.
        
        Requirements: 1.1, 1.3, 1.4
        """
        # Create a test model with db_column
        class TestModel(models.Model):
            # Field with db_column different from name
            username = models.CharField(max_length=100, db_column='user_name')
            # Field without db_column (should use field name)
            email = models.EmailField()
            
            class Meta:
                app_label = 'test'
                db_table = 'test_user'
        
        # Parse the model
        parser = DjangoModelParser(app_label='test')
        er_model = parser.parse(models_list=[TestModel])
        
        # Verify Column objects have db_column
        entity = er_model.entities['TestModel']
        username_col = next(c for c in entity.columns if c.name == 'username')
        email_col = next(c for c in entity.columns if c.name == 'email')
        
        assert username_col.db_column == 'user_name', "db_column should be 'user_name'"
        assert email_col.db_column == 'email', "db_column should default to field name"
        
        # Verify database_column_name property
        assert username_col.database_column_name == 'user_name'
        assert email_col.database_column_name == 'email'
        
        # Render to TOML
        renderer = TOMLRenderer()
        toml_output = renderer.render(er_model)
        data = toml.loads(toml_output)
        
        # Verify TOML output
        user_entity = data['entities']['TestModel']
        username_toml = next(c for c in user_entity['columns'] if c['name'] == 'username')
        email_toml = next(c for c in user_entity['columns'] if c['name'] == 'email')
        
        # db_column should be in TOML when different from name
        assert 'db_column' in username_toml, "db_column should be in TOML"
        assert username_toml['db_column'] == 'user_name'
        
        # db_column should NOT be in TOML when same as name
        assert 'db_column' not in email_toml, "db_column should not be in TOML when same as name"
        
        # table_name should always be in TOML
        assert user_entity['table_name'] == 'test_user'
    
    def test_db_column_in_generated_django_code(self):
        """
        Test that generated Django code includes db_column parameter when needed.
        
        Requirements: 1.4
        """
        # Create a test model
        class TestModel(models.Model):
            username = models.CharField(max_length=100, db_column='user_name')
            email = models.EmailField()
            
            class Meta:
                app_label = 'test'
                db_table = 'test_user'
        
        # Parse the model
        parser = DjangoModelParser(app_label='test')
        er_model = parser.parse(models_list=[TestModel])
        
        # Generate Django code
        renderer = DjangoPackageRenderer(app_label='test')
        files = renderer.render(er_model)
        
        # Check the model file
        model_file = files['test_model.py']
        
        # Should include db_column for username
        assert "db_column='user_name'" in model_file, "Generated code should include db_column"
        
        # Should NOT include db_column for email (same as field name)
        # Count occurrences of db_column in the email field definition
        email_field_start = model_file.find('email = models.EmailField')
        if email_field_start != -1:
            email_field_end = model_file.find('\n', email_field_start)
            email_field_def = model_file[email_field_start:email_field_end]
            assert 'db_column' not in email_field_def, "Should not include db_column when same as name"
        
        # Should always include db_table in Meta
        assert "db_table = 'test_user'" in model_file, "Generated code should include db_table"


class TestPathSeparationIntegration(TestCase):
    """Test path separation functionality end-to-end"""
    
    def setUp(self):
        """Create temporary directories for testing"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.scan_dir = self.temp_dir / 'src'
        self.output_dir = self.temp_dir / 'output'
        self.scan_dir.mkdir(parents=True)
        self.output_dir.mkdir(parents=True)
    
    def tearDown(self):
        """Clean up temporary directories"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_path_configuration_defaults(self):
        """
        Test default path configuration values.
        
        Requirements: 3.3, 3.4
        """
        # Test default scan_path
        config = PathConfiguration.from_options(working_dir=self.temp_dir)
        assert config.scan_path == self.temp_dir / 'src', "Default scan_path should be 'src'"
        
        # Test output_path inherits scan_path
        assert config.output_path == config.scan_path, "output_path should inherit scan_path"
        
        # Test third_party_output_path defaults to output_path/third
        assert config.third_party_output_path == config.output_path / 'third'
    
    def test_path_configuration_inheritance(self):
        """
        Test path configuration inheritance chain.
        
        Requirements: 2.2, 2.3
        """
        # Test with only scan_path
        config1 = PathConfiguration.from_options(
            scan_path='custom_src',
            working_dir=self.temp_dir
        )
        assert config1.output_path == self.temp_dir / 'custom_src'
        assert config1.third_party_output_path == self.temp_dir / 'custom_src' / 'third'
        
        # Test with scan_path and output_path
        config2 = PathConfiguration.from_options(
            scan_path='src',
            output_path='output',
            working_dir=self.temp_dir
        )
        assert config2.scan_path == self.temp_dir / 'src'
        assert config2.output_path == self.temp_dir / 'output'
        assert config2.third_party_output_path == self.temp_dir / 'output' / 'third'
        
        # Test with all paths specified (relative third_party path is relative to output_path)
        config3 = PathConfiguration.from_options(
            scan_path='src',
            output_path='output',
            third_party_output_path='external',  # Relative to output_path
            working_dir=self.temp_dir
        )
        assert config3.third_party_output_path == self.temp_dir / 'output' / 'external'
    
    def test_path_resolver_with_configuration(self):
        """
        Test PathResolver uses configuration correctly.
        
        Requirements: 3.6
        """
        from unittest.mock import Mock
        
        # Create configuration
        config = PathConfiguration.from_options(
            scan_path=str(self.scan_dir),
            output_path=str(self.output_dir),
            working_dir=self.temp_dir
        )
        
        # Create resolver
        resolver = PathResolver(config)
        
        # Mock app config
        mock_app = Mock()
        mock_app.name = 'myapp'
        
        # Test output path resolution
        output_path = resolver.resolve_output_path(mock_app, 'toml', is_third_party=False)
        assert output_path.parent.parent == self.output_dir, "Should use output_path"
        
        # Test third-party output path
        third_party_path = resolver.resolve_output_path(mock_app, 'toml', is_third_party=True)
        assert third_party_path.parent.parent.parent == self.output_dir, "Should use third_party_output_path"
        
        # Test scan path
        assert resolver.get_scan_path() == self.scan_dir


class TestThirdPartyPackageIntegration(TestCase):
    """Test third-party package output functionality end-to-end"""
    
    def test_third_party_package_prefix(self):
        """
        Test that third-party packages get correct prefix.
        
        Requirements: 2.4
        """
        from unittest.mock import Mock
        
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Create configuration with custom prefix
            config = PathConfiguration.from_options(
                output_path='output',
                third_party_output_path='output/external',
                third_party_package_prefix='external',
                working_dir=temp_dir
            )
            
            resolver = PathResolver(config)
            
            # Mock third-party app
            mock_app = Mock()
            mock_app.name = 'django.contrib.auth'
            
            # Test package name resolution
            package_name = resolver.resolve_package_name(mock_app, is_third_party=True)
            assert package_name == 'external.django.contrib.auth', "Should add prefix to third-party package"
            
            # Test non-third-party package
            mock_local_app = Mock()
            mock_local_app.name = 'myapp'
            local_package = resolver.resolve_package_name(mock_local_app, is_third_party=False)
            assert local_package == 'myapp', "Should not add prefix to local package"
        finally:
            shutil.rmtree(temp_dir)
    
    def test_default_package_prefix_from_path(self):
        """
        Test that package prefix defaults to last directory name.
        
        Requirements: 2.7
        """
        from unittest.mock import Mock
        
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Create configuration without explicit prefix
            config = PathConfiguration.from_options(
                output_path='output',
                third_party_output_path='output/vendor',
                working_dir=temp_dir
            )
            
            # Prefix should be 'vendor' (last directory name)
            assert config.third_party_package_prefix == 'vendor'
            
            resolver = PathResolver(config)
            mock_app = Mock()
            mock_app.name = 'external.package'
            
            package_name = resolver.resolve_package_name(mock_app, is_third_party=True)
            assert package_name == 'vendor.external.package'
        finally:
            shutil.rmtree(temp_dir)


class TestCompleteWorkflow(TestCase):
    """Test complete workflow from parsing to code generation"""
    
    def test_end_to_end_workflow(self):
        """
        Test complete workflow: parse model with db_column, configure paths, generate code.
        
        Requirements: 1.1, 1.2, 1.3, 1.4, 2.2, 2.3, 2.4, 3.3, 3.4, 3.6
        """
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Step 1: Create test model with db_column
            class UserModel(models.Model):
                username = models.CharField(max_length=100, db_column='user_name')
                email_address = models.EmailField(db_column='email')
                
                class Meta:
                    app_label = 'testapp'
                    db_table = 'app_user'
            
            # Step 2: Parse model
            parser = DjangoModelParser(app_label='testapp')
            er_model = parser.parse(models_list=[UserModel])
            
            # Verify parsing
            entity = er_model.entities['UserModel']
            assert entity.table_name == 'app_user'
            username_col = next(c for c in entity.columns if c.name == 'username')
            assert username_col.db_column == 'user_name'
            
            # Step 3: Configure paths
            config = PathConfiguration.from_options(
                scan_path='src',
                output_path='output',
                third_party_output_path='third',  # Relative to output_path
                third_party_package_prefix='third',
                working_dir=temp_dir
            )
            
            # Verify configuration
            assert config.scan_path == temp_dir / 'src'
            assert config.output_path == temp_dir / 'output'
            assert config.third_party_output_path == temp_dir / 'output' / 'third'
            assert config.third_party_package_prefix == 'third'
            
            # Step 4: Create resolver
            resolver = PathResolver(config)
            
            # Step 5: Render to TOML
            toml_renderer = TOMLRenderer()
            toml_output = toml_renderer.render(er_model)
            
            # Verify TOML contains db_column
            data = toml.loads(toml_output)
            user_entity = data['entities']['UserModel']
            assert user_entity['table_name'] == 'app_user'
            username_toml = next(c for c in user_entity['columns'] if c['name'] == 'username')
            assert username_toml['db_column'] == 'user_name'
            
            # Step 6: Generate Django code
            django_renderer = DjangoPackageRenderer(app_label='testapp')
            files = django_renderer.render(er_model)
            
            # Verify generated code
            model_file = files['user_model.py']
            assert "db_column='user_name'" in model_file
            assert "db_table = 'app_user'" in model_file
            
            # Success!
            assert True, "Complete workflow executed successfully"
        finally:
            shutil.rmtree(temp_dir)
