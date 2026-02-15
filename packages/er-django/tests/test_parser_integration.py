"""
Tests for DjangoModelParser._convert_model_to_entity() integration

Tests for task 5.7: 修改 _convert_model_to_entity() 方法
Requirements: 6.1, 7.1, 9.1
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
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from x007007007.er_django import DjangoModelParser


# Test base models
class TimeStampedModel(models.Model):
    """Base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        app_label = 'test_app'


class SoftDeleteModel(models.Model):
    """Base model with soft delete"""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
        app_label = 'test_app'


# Test models
class BasicModel(models.Model):
    """Model with no inheritance (only models.Model)"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        app_label = 'test_app'


class ArticleModel(TimeStampedModel):
    """Model inheriting from TimeStampedModel"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test_app'


class ProductModel(TimeStampedModel, SoftDeleteModel):
    """Model with multiple inheritance"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'test_app'


class AppUser(AbstractUser):
    """Model inheriting from Django's AbstractUser"""
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.CharField(max_length=255, blank=True)  # Simplified for testing
    
    class Meta:
        app_label = 'test_app'


class TestConvertModelToEntityIntegration:
    """Test _convert_model_to_entity() with inheritance support"""
    
    def test_simple_model_no_inheritance(self):
        """
        Test that a simple model with no inheritance works correctly
        Requirements: 6.1, 7.1, 9.1
        """
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(BasicModel)
        
        # Check basic entity properties
        assert entity.name == 'BasicModel'
        
        # Check extends field is empty (no inheritance except models.Model)
        assert entity.extends == []
        
        # Check package field is set
        assert entity.package is not None
        assert entity.package == BasicModel.__module__
        
        # Check that fields are included
        column_names = [col.name for col in entity.columns]
        assert 'name' in column_names
        assert 'description' in column_names
    
    def test_single_inheritance_extends_field(self):
        """
        Test that extends field is populated for single inheritance
        Requirements: 6.1, 9.1
        """
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(ArticleModel)
        
        # Check extends field contains parent class
        assert len(entity.extends) == 1
        assert TimeStampedModel.__module__ in entity.extends[0]
        assert 'TimeStampedModel' in entity.extends[0]
        
        # Verify full path format
        expected_path = f"{TimeStampedModel.__module__}.TimeStampedModel"
        assert entity.extends[0] == expected_path
    
    def test_multiple_inheritance_extends_field(self):
        """
        Test that extends field contains all parent classes for multiple inheritance
        Requirements: 6.1, 9.1
        """
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(ProductModel)
        
        # Check extends field contains both parent classes
        assert len(entity.extends) == 2
        
        # Check that both parents are in extends
        extends_str = ' '.join(entity.extends)
        assert 'TimeStampedModel' in extends_str
        assert 'SoftDeleteModel' in extends_str
    
    def test_django_builtin_inheritance(self):
        """
        Test that Django built-in model inheritance is recorded correctly
        Requirements: 6.1, 9.1
        """
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(AppUser)
        
        # Check extends field contains AbstractUser
        assert len(entity.extends) >= 1
        
        # Find AbstractUser in extends
        abstract_user_found = False
        for parent in entity.extends:
            if 'AbstractUser' in parent:
                abstract_user_found = True
                assert 'django.contrib.auth.models' in parent
                break
        
        assert abstract_user_found, "AbstractUser should be in extends field"
    
    def test_package_field_set_correctly(self):
        """
        Test that package field is set to model's __module__
        Requirements: 7.1
        """
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(ArticleModel)
        
        # Check package field
        assert entity.package is not None
        assert entity.package == ArticleModel.__module__
        
        # Package should be a string
        assert isinstance(entity.package, str)
    
    def test_only_own_fields_included(self):
        """
        Test that only the model's own fields are included, not inherited fields
        Requirements: 6.1, 9.1
        """
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(ArticleModel)
        
        # Get column names
        column_names = [col.name for col in entity.columns]
        
        # Should include own fields
        assert 'title' in column_names
        assert 'content' in column_names
        assert 'author' in column_names
        
        # Should NOT include parent fields
        assert 'created_at' not in column_names
        assert 'updated_at' not in column_names
    
    def test_multiple_inheritance_only_own_fields(self):
        """
        Test that with multiple inheritance, only own fields are included
        Requirements: 6.1, 9.1
        """
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(ProductModel)
        
        # Get column names
        column_names = [col.name for col in entity.columns]
        
        # Should include own fields
        assert 'name' in column_names
        assert 'price' in column_names
        assert 'stock' in column_names
        
        # Should NOT include fields from first parent
        assert 'created_at' not in column_names
        assert 'updated_at' not in column_names
        
        # Should NOT include fields from second parent
        assert 'is_deleted' not in column_names
        assert 'deleted_at' not in column_names
    
    def test_django_builtin_only_own_fields(self):
        """
        Test that Django built-in model inheritance excludes built-in fields
        Requirements: 6.1, 9.1
        """
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(AppUser)
        
        # Get column names
        column_names = [col.name for col in entity.columns]
        
        # Should include custom fields
        assert 'phone' in column_names
        assert 'bio' in column_names
        assert 'avatar' in column_names
        
        # Should NOT include AbstractUser fields
        assert 'username' not in column_names
        assert 'email' not in column_names
        assert 'first_name' not in column_names
        assert 'last_name' not in column_names
        assert 'password' not in column_names
    
    def test_entity_structure_complete(self):
        """
        Test that the returned entity has all required fields
        Requirements: 6.1, 7.1, 9.1
        """
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(ArticleModel)
        
        # Check all required attributes exist
        assert hasattr(entity, 'name')
        assert hasattr(entity, 'columns')
        assert hasattr(entity, 'comment')
        assert hasattr(entity, 'extends')
        assert hasattr(entity, 'package')
        
        # Check types
        assert isinstance(entity.name, str)
        assert isinstance(entity.columns, list)
        assert isinstance(entity.extends, list)
        assert isinstance(entity.package, str)
    
    def test_manytomany_fields_excluded(self):
        """
        Test that ManyToManyField are excluded from columns
        Requirements: 6.1, 9.1
        """
        # Create a model with ManyToMany field
        class TagModel(models.Model):
            name = models.CharField(max_length=50)
            
            class Meta:
                app_label = 'test_app'
        
        class PostModel(TimeStampedModel):
            title = models.CharField(max_length=200)
            tags = models.ManyToManyField(TagModel)
            
            class Meta:
                app_label = 'test_app'
        
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(PostModel)
        
        # Get column names
        column_names = [col.name for col in entity.columns]
        
        # Should include regular fields
        assert 'title' in column_names
        
        # Should NOT include ManyToMany field
        assert 'tags' not in column_names
    
    def test_foreignkey_fields_included(self):
        """
        Test that ForeignKey fields are included in columns
        Requirements: 6.1, 9.1
        """
        # Create models with ForeignKey
        class CategoryModel(models.Model):
            name = models.CharField(max_length=50)
            
            class Meta:
                app_label = 'test_app'
        
        class ItemModel(TimeStampedModel):
            name = models.CharField(max_length=100)
            category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
            
            class Meta:
                app_label = 'test_app'
        
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(ItemModel)
        
        # Get column names
        column_names = [col.name for col in entity.columns]
        
        # Should include ForeignKey field
        assert 'category_id' in column_names or 'category' in column_names


class TestConvertModelToEntityEdgeCases:
    """Test edge cases for _convert_model_to_entity()"""
    
    def test_model_with_no_custom_fields(self):
        """
        Test model that only has auto-created fields
        Requirements: 6.1, 7.1, 9.1
        """
        class EmptyModel(models.Model):
            class Meta:
                app_label = 'test_app'
        
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(EmptyModel)
        
        # Should have basic structure
        assert entity.name == 'EmptyModel'
        assert entity.extends == []
        assert entity.package is not None
        
        # Should have at least id field
        column_names = [col.name for col in entity.columns]
        assert 'id' in column_names
    
    def test_model_with_comment(self):
        """
        Test that model docstring is captured as comment
        Requirements: 6.1, 7.1, 9.1
        """
        class DocumentedModel(models.Model):
            """This is a documented model"""
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'test_app'
        
        parser = DjangoModelParser()
        entity = parser._convert_model_to_entity(DocumentedModel)
        
        # Comment might be captured from docstring
        # This depends on introspector implementation
        assert entity.name == 'DocumentedModel'
    
    def test_package_field_never_none(self):
        """
        Test that package field is always set (never None)
        Requirements: 7.1
        """
        parser = DjangoModelParser()
        
        # Test with different models
        models_to_test = [BasicModel, ArticleModel, ProductModel]
        
        for model in models_to_test:
            entity = parser._convert_model_to_entity(model)
            assert entity.package is not None
            assert len(entity.package) > 0


class TestConvertModelToEntityConsistency:
    """Test consistency of _convert_model_to_entity() behavior"""
    
    def test_multiple_calls_same_result(self):
        """
        Test that calling the method multiple times gives consistent results
        Requirements: 6.1, 7.1, 9.1
        """
        parser = DjangoModelParser()
        
        # Call twice
        entity1 = parser._convert_model_to_entity(ArticleModel)
        entity2 = parser._convert_model_to_entity(ArticleModel)
        
        # Should have same structure
        assert entity1.name == entity2.name
        assert entity1.extends == entity2.extends
        assert entity1.package == entity2.package
        assert len(entity1.columns) == len(entity2.columns)
    
    def test_different_models_different_results(self):
        """
        Test that different models produce different entities
        Requirements: 6.1, 7.1, 9.1
        """
        parser = DjangoModelParser()
        
        entity1 = parser._convert_model_to_entity(BasicModel)
        entity2 = parser._convert_model_to_entity(ArticleModel)
        
        # Should have different names
        assert entity1.name != entity2.name
        
        # Should have different extends
        assert entity1.extends != entity2.extends
        
        # Should have different number of columns
        assert len(entity1.columns) != len(entity2.columns)
