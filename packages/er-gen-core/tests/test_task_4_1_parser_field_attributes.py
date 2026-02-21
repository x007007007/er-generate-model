"""
Test task 4.1: Verify DjangoModelParser correctly extracts unique, db_index, and null attributes

This test verifies that the DjangoModelParser correctly extracts:
- unique attribute from Django fields
- db_index attribute (converted to indexed)
- null attribute (converted to nullable)

Requirements: 4.1, 4.2, 4.3
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
        ],
        SECRET_KEY='test-secret-key',
    )
    django.setup()

from django.db import models
from x007007007.er_django.parser import DjangoModelParser


def test_parser_extracts_unique_attribute():
    """Test that parser correctly extracts unique=True attribute"""
    
    class TestModel(models.Model):
        unique_field = models.CharField(max_length=100, unique=True)
        non_unique_field = models.CharField(max_length=100, unique=False)
        
        class Meta:
            app_label = 'test_app'
    
    parser = DjangoModelParser()
    er_model = parser.parse([TestModel])
    
    # Get the entity from the dictionary
    entity = er_model.entities['TestModel']
    
    # Find the unique field
    unique_col = next(col for col in entity.columns if col.name == 'unique_field')
    assert unique_col.unique is True, "unique=True should be extracted"
    
    # Find the non-unique field
    non_unique_col = next(col for col in entity.columns if col.name == 'non_unique_field')
    assert non_unique_col.unique is False, "unique=False should be extracted"


def test_parser_extracts_db_index_attribute():
    """Test that parser correctly extracts db_index=True and converts to indexed=True"""
    
    class TestModel(models.Model):
        indexed_field = models.CharField(max_length=100, db_index=True)
        non_indexed_field = models.CharField(max_length=100, db_index=False)
        
        class Meta:
            app_label = 'test_app'
    
    parser = DjangoModelParser()
    er_model = parser.parse([TestModel])
    
    # Get the entity from the dictionary
    entity = er_model.entities['TestModel']
    
    # Find the indexed field
    indexed_col = next(col for col in entity.columns if col.name == 'indexed_field')
    assert indexed_col.indexed is True, "db_index=True should be converted to indexed=True"
    
    # Find the non-indexed field
    non_indexed_col = next(col for col in entity.columns if col.name == 'non_indexed_field')
    assert non_indexed_col.indexed is False, "db_index=False should be converted to indexed=False"


def test_parser_extracts_null_attribute():
    """Test that parser correctly extracts null attribute and converts to nullable"""
    
    class TestModel(models.Model):
        nullable_field = models.CharField(max_length=100, null=True)
        non_nullable_field = models.CharField(max_length=100, null=False)
        
        class Meta:
            app_label = 'test_app'
    
    parser = DjangoModelParser()
    er_model = parser.parse([TestModel])
    
    # Get the entity from the dictionary
    entity = er_model.entities['TestModel']
    
    # Find the nullable field
    nullable_col = next(col for col in entity.columns if col.name == 'nullable_field')
    assert nullable_col.nullable is True, "null=True should be converted to nullable=True"
    
    # Find the non-nullable field
    non_nullable_col = next(col for col in entity.columns if col.name == 'non_nullable_field')
    assert non_nullable_col.nullable is False, "null=False should be converted to nullable=False"


def test_parser_extracts_combined_attributes():
    """Test that parser correctly extracts multiple attributes together"""
    
    class TestModel(models.Model):
        combined_field = models.CharField(
            max_length=100,
            unique=True,
            db_index=True,
            null=False
        )
        
        class Meta:
            app_label = 'test_app'
    
    parser = DjangoModelParser()
    er_model = parser.parse([TestModel])
    
    # Get the entity from the dictionary
    entity = er_model.entities['TestModel']
    
    # Find the combined field
    combined_col = next(col for col in entity.columns if col.name == 'combined_field')
    assert combined_col.unique is True, "unique=True should be extracted"
    assert combined_col.indexed is True, "db_index=True should be converted to indexed=True"
    assert combined_col.nullable is False, "null=False should be converted to nullable=False"


def test_introspector_methods():
    """Test that introspector methods return correct values"""
    from x007007007.er_django.introspector import DjangoModelIntrospector
    
    class TestModel(models.Model):
        test_field = models.CharField(
            max_length=100,
            unique=True,
            db_index=True,
            null=False
        )
        
        class Meta:
            app_label = 'test_app'
    
    # Get the field
    field = TestModel._meta.get_field('test_field')
    
    introspector = DjangoModelIntrospector()
    
    # Test introspector methods
    assert introspector.is_unique(field) is True, "is_unique should return True"
    assert introspector.has_db_index(field) is True, "has_db_index should return True"
    assert introspector.is_nullable(field) is False, "is_nullable should return False"


if __name__ == '__main__':
    test_parser_extracts_unique_attribute()
    test_parser_extracts_db_index_attribute()
    test_parser_extracts_null_attribute()
    test_parser_extracts_combined_attributes()
    test_introspector_methods()
    print("All tests passed!")
