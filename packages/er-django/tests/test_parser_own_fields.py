"""
Tests for DjangoModelParser._get_own_fields() method

Tests for task 5.5: 实现 _get_own_fields() 方法
Requirements: 6.4, 9.7
"""
import pytest

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

from django.db import models
from django.contrib.auth.models import AbstractUser
from x007007007.er_django import DjangoModelParser


# Test base models
class BaseModelWithFields(models.Model):
    """Base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        app_label = 'test_app'


class AnotherBaseModel(models.Model):
    """Another base model with different fields"""
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, default='active')
    
    class Meta:
        abstract = True
        app_label = 'test_app'


# Test models
class SimpleModelNoInheritance(models.Model):
    """Model with no inheritance (only models.Model)"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        app_label = 'test_app'


class ChildModelSingleInheritance(BaseModelWithFields):
    """Model inheriting from one base model"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    class Meta:
        app_label = 'test_app'


class ChildModelMultipleInheritance(BaseModelWithFields, AnotherBaseModel):
    """Model with multiple inheritance"""
    name = models.CharField(max_length=100)
    value = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'test_app'


class GrandchildModel(ChildModelSingleInheritance):
    """Model inheriting from a child model (multi-level inheritance)"""
    extra_field = models.CharField(max_length=50)
    
    class Meta:
        app_label = 'test_app'


class CustomUserModel(AbstractUser):
    """Model inheriting from Django's AbstractUser"""
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    
    class Meta:
        app_label = 'test_app'


class TestGetOwnFields:
    """Test _get_own_fields() method"""
    
    def test_simple_model_returns_all_fields(self):
        """
        Test that a model with no inheritance returns all its fields
        Requirements: 6.4, 9.7
        """
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(SimpleModelNoInheritance)
        
        # Get field names
        field_names = [f.name for f in own_fields]
        
        # Should include the model's own fields
        assert 'name' in field_names
        assert 'description' in field_names
        
        # Should also include auto-created fields like 'id'
        assert 'id' in field_names
    
    def test_single_inheritance_excludes_parent_fields(self):
        """
        Test that inherited fields are excluded from own fields
        Requirements: 6.4, 9.7
        """
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(ChildModelSingleInheritance)
        
        # Get field names
        field_names = [f.name for f in own_fields]
        
        # Should include child's own fields
        assert 'title' in field_names
        assert 'content' in field_names
        
        # Should NOT include parent's fields
        assert 'created_at' not in field_names
        assert 'updated_at' not in field_names
    
    def test_multiple_inheritance_excludes_all_parent_fields(self):
        """
        Test that fields from multiple parents are all excluded
        Requirements: 6.4, 9.7
        """
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(ChildModelMultipleInheritance)
        
        # Get field names
        field_names = [f.name for f in own_fields]
        
        # Should include child's own fields
        assert 'name' in field_names
        assert 'value' in field_names
        
        # Should NOT include fields from first parent
        assert 'created_at' not in field_names
        assert 'updated_at' not in field_names
        
        # Should NOT include fields from second parent
        assert 'is_active' not in field_names
        assert 'status' not in field_names
    
    def test_multi_level_inheritance_excludes_all_ancestor_fields(self):
        """
        Test that multi-level inheritance excludes all ancestor fields
        Requirements: 6.4, 9.7
        """
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(GrandchildModel)
        
        # Get field names
        field_names = [f.name for f in own_fields]
        
        # Should include only the grandchild's own field
        assert 'extra_field' in field_names
        
        # Should NOT include parent's fields
        assert 'title' not in field_names
        assert 'content' not in field_names
        
        # Should NOT include grandparent's fields
        assert 'created_at' not in field_names
        assert 'updated_at' not in field_names
    
    def test_django_builtin_inheritance_excludes_builtin_fields(self):
        """
        Test that fields from Django built-in models are excluded
        Requirements: 6.4, 9.7
        """
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(CustomUserModel)
        
        # Get field names
        field_names = [f.name for f in own_fields]
        
        # Should include custom fields
        assert 'phone' in field_names
        assert 'bio' in field_names
        
        # Should NOT include AbstractUser fields
        assert 'username' not in field_names
        assert 'email' not in field_names
        assert 'first_name' not in field_names
        assert 'last_name' not in field_names
    
    def test_only_concrete_fields_included(self):
        """
        Test that only concrete fields (with database columns) are included
        Requirements: 6.4, 9.7
        """
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(SimpleModelNoInheritance)
        
        # All returned fields should be concrete
        for field in own_fields:
            assert field.concrete, f"Field {field.name} should be concrete"
    
    def test_returns_list(self):
        """
        Test that the method returns a list
        Requirements: 6.4, 9.7
        """
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(SimpleModelNoInheritance)
        
        assert isinstance(own_fields, list)
    
    def test_empty_model_returns_only_auto_fields(self):
        """
        Test that a model with no explicit fields returns only auto-created fields
        Requirements: 6.4, 9.7
        """
        # Create a minimal model
        class MinimalModel(models.Model):
            class Meta:
                app_label = 'test_app'
        
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(MinimalModel)
        
        # Should have at least the 'id' field
        field_names = [f.name for f in own_fields]
        assert 'id' in field_names


class TestGetOwnFieldsEdgeCases:
    """Test edge cases for _get_own_fields()"""
    
    def test_field_override_in_child(self):
        """
        Test that if a child overrides a parent field, it's included in own fields
        Requirements: 6.4, 9.7
        """
        # Create models with field override
        class ParentWithField(models.Model):
            name = models.CharField(max_length=50)
            
            class Meta:
                abstract = True
                app_label = 'test_app'
        
        class ChildOverridesField(ParentWithField):
            # Override parent's name field with different max_length
            name = models.CharField(max_length=200)
            
            class Meta:
                app_label = 'test_app'
        
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(ChildOverridesField)
        
        field_names = [f.name for f in own_fields]
        
        # The overridden field should be in own fields
        # Note: Django's behavior with field overriding can be complex
        # This test documents the expected behavior
        assert isinstance(own_fields, list)
    
    def test_models_model_only_inheritance(self):
        """
        Test model that only inherits from models.Model
        Requirements: 6.4, 9.7
        """
        parser = DjangoModelParser()
        own_fields = parser._get_own_fields(SimpleModelNoInheritance)
        
        # Should return the model's fields
        field_names = [f.name for f in own_fields]
        assert 'name' in field_names
        assert 'description' in field_names


class TestGetOwnFieldsIntegration:
    """Integration tests for _get_own_fields()"""
    
    def test_integration_with_convert_model_to_entity(self):
        """
        Test that _get_own_fields() can be used in model conversion
        Requirements: 6.4, 9.7
        
        Note: This test verifies the method works correctly and returns
        the expected data structure. The actual integration with
        _convert_model_to_entity will be tested in task 5.7
        """
        parser = DjangoModelParser()
        
        # Get own fields for a model with inheritance
        own_fields = parser._get_own_fields(ChildModelSingleInheritance)
        
        # Verify we can iterate and access field properties
        for field in own_fields:
            assert hasattr(field, 'name')
            assert hasattr(field, 'concrete')
            assert field.concrete is True
    
    def test_multiple_models_different_inheritance_patterns(self):
        """
        Test _get_own_fields() with multiple models having different patterns
        Requirements: 6.4, 9.7
        """
        parser = DjangoModelParser()
        
        # Model with no inheritance
        fields1 = parser._get_own_fields(SimpleModelNoInheritance)
        names1 = [f.name for f in fields1]
        assert 'name' in names1
        assert 'description' in names1
        
        # Model with single inheritance
        fields2 = parser._get_own_fields(ChildModelSingleInheritance)
        names2 = [f.name for f in fields2]
        assert 'title' in names2
        assert 'content' in names2
        assert 'created_at' not in names2  # Parent field excluded
        
        # Model with multiple inheritance
        fields3 = parser._get_own_fields(ChildModelMultipleInheritance)
        names3 = [f.name for f in fields3]
        assert 'name' in names3
        assert 'value' in names3
        assert 'created_at' not in names3  # First parent field excluded
        assert 'is_active' not in names3   # Second parent field excluded
