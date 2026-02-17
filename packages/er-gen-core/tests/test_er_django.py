"""
Tests for Django integration module

Note: These tests require Django to be installed and configured.
They are designed to be run in a Django project context.
"""
import pytest

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

from django.db import models
from x007007007.er_django import DjangoModelParser, DjangoModelIntrospector


# Test models - using CoreTest prefix to avoid conflicts with er-django tests
class CoreTestUser(models.Model):
    """Test user model"""
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'core_test_app'
        db_table = 'core_test_user'


class CoreTestPost(models.Model):
    """Test post model"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(CoreTestUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'core_test_app'
        db_table = 'core_test_post'


class CoreTestProfile(models.Model):
    """Test profile model with OneToOne"""
    user = models.OneToOneField(CoreTestUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    
    class Meta:
        app_label = 'core_test_app'
        db_table = 'core_test_profile'


class CoreTestTag(models.Model):
    """Test tag model"""
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        app_label = 'core_test_app'
        db_table = 'core_test_tag'


class CoreTestPostTag(models.Model):
    """Test many-to-many through model"""
    post = models.ForeignKey(CoreTestPost, on_delete=models.CASCADE)
    tag = models.ForeignKey(CoreTestTag, on_delete=models.CASCADE)
    
    class Meta:
        app_label = 'core_test_app'
        db_table = 'core_test_post_tag'


class TestIntrospector:
    """Test DjangoModelIntrospector"""
    
    def test_get_field_type(self):
        """Test field type extraction"""
        introspector = DjangoModelIntrospector()
        
        # CharField -> string
        field = CoreTestUser._meta.get_field('username')
        assert introspector.get_field_type(field) == 'string'
        
        # EmailField -> string
        field = CoreTestUser._meta.get_field('email')
        assert introspector.get_field_type(field) == 'string'
        
        # DateTimeField -> datetime
        field = CoreTestUser._meta.get_field('created_at')
        assert introspector.get_field_type(field) == 'datetime'
        
        # TextField -> text
        field = CoreTestPost._meta.get_field('content')
        assert introspector.get_field_type(field) == 'text'
        
        # BooleanField -> boolean
        field = CoreTestPost._meta.get_field('published')
        assert introspector.get_field_type(field) == 'boolean'
    
    def test_get_field_max_length(self):
        """Test max_length extraction"""
        introspector = DjangoModelIntrospector()
        
        field = CoreTestUser._meta.get_field('username')
        assert introspector.get_field_max_length(field) == 100
        
        field = CoreTestPost._meta.get_field('title')
        assert introspector.get_field_max_length(field) == 200
    
    def test_is_primary_key(self):
        """Test primary key detection"""
        introspector = DjangoModelIntrospector()
        
        # Auto-created id field
        field = CoreTestUser._meta.get_field('id')
        assert introspector.is_primary_key(field) is True
        
        # Regular field
        field = CoreTestUser._meta.get_field('username')
        assert introspector.is_primary_key(field) is False
    
    def test_is_unique(self):
        """Test unique constraint detection"""
        introspector = DjangoModelIntrospector()
        
        field = CoreTestUser._meta.get_field('username')
        assert introspector.is_unique(field) is True
        
        field = CoreTestPost._meta.get_field('title')
        assert introspector.is_unique(field) is False
    
    def test_get_related_model(self):
        """Test related model extraction"""
        introspector = DjangoModelIntrospector()
        
        field = CoreTestPost._meta.get_field('author')
        related_model = introspector.get_related_model(field)
        assert related_model == 'CoreTestUser'


class TestDjangoModelParser:
    """Test DjangoModelParser"""
    
    def test_parse_single_model(self):
        """Test parsing a single model"""
        parser = DjangoModelParser()
        er_model = parser.parse(models_list=[CoreTestUser])
        
        assert len(er_model.entities) == 1
        assert 'CoreTestUser' in er_model.entities
        
        entity = er_model.entities['CoreTestUser']
        assert entity.name == 'CoreTestUser'
        
        # Check columns
        column_names = [col.name for col in entity.columns]
        assert 'id' in column_names
        assert 'username' in column_names
        assert 'email' in column_names
        assert 'created_at' in column_names
    
    def test_parse_with_foreign_key(self):
        """Test parsing models with ForeignKey"""
        parser = DjangoModelParser()
        er_model = parser.parse(models_list=[CoreTestUser, CoreTestPost])
        
        assert len(er_model.entities) == 2
        assert 'CoreTestUser' in er_model.entities
        assert 'CoreTestPost' in er_model.entities
        
        # Check relationships
        assert len(er_model.relationships) > 0
        
        # Find the ForeignKey relationship
        fk_rels = [rel for rel in er_model.relationships if rel.relation_type == 'one-to-many']
        assert len(fk_rels) > 0
        
        # Check relationship details
        rel = fk_rels[0]
        assert rel.left_entity == 'CoreTestUser'
        assert rel.right_entity == 'CoreTestPost'
    
    def test_parse_with_one_to_one(self):
        """Test parsing models with OneToOneField"""
        parser = DjangoModelParser()
        er_model = parser.parse(models_list=[CoreTestUser, CoreTestProfile])
        
        # Check relationships
        one_to_one_rels = [rel for rel in er_model.relationships if rel.relation_type == 'one-to-one']
        assert len(one_to_one_rels) > 0
        
        rel = one_to_one_rels[0]
        assert rel.left_entity == 'CoreTestProfile'
        assert rel.right_entity == 'CoreTestUser'
    
    def test_column_attributes(self):
        """Test column attribute extraction"""
        parser = DjangoModelParser()
        er_model = parser.parse(models_list=[CoreTestUser])
        
        entity = er_model.entities['CoreTestUser']
        
        # Find username column
        username_col = next(col for col in entity.columns if col.name == 'username')
        assert username_col.type == 'string'
        assert username_col.max_length == 100
        assert username_col.unique is True
        assert username_col.nullable is False  # CharField has blank=False by default
        
        # Find id column
        id_col = next(col for col in entity.columns if col.name == 'id')
        assert id_col.is_pk is True
    
    def test_parse_multiple_models(self):
        """Test parsing multiple models"""
        parser = DjangoModelParser()
        er_model = parser.parse(models_list=[CoreTestUser, CoreTestPost, CoreTestProfile, CoreTestTag])
        
        assert len(er_model.entities) == 4
        assert 'CoreTestUser' in er_model.entities
        assert 'CoreTestPost' in er_model.entities
        assert 'CoreTestProfile' in er_model.entities
        assert 'CoreTestTag' in er_model.entities


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.skip(reason="ERConverter not available in current codebase")
    def test_full_workflow(self):
        """Test complete workflow: Django models -> ER model -> Migration format"""
        from x007007007.er_tool.migrate.converter import ERConverter
        
        # Parse Django models
        parser = DjangoModelParser()
        er_model = parser.parse(models_list=[CoreTestUser, CoreTestPost])
        
        # Convert to migration format
        converter = ERConverter()
        migration_data = converter.convert_model(er_model)
        
        # Check tables
        assert 'tables' in migration_data
        assert len(migration_data['tables']) == 2
        
        # Check foreign keys
        assert 'foreign_keys' in migration_data
        assert len(migration_data['foreign_keys']) > 0
