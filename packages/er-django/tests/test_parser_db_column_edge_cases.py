"""
Unit tests for db_column parsing edge cases.

These tests verify specific edge cases for db_column extraction from Django fields.

Feature: field-db-column-and-path-separation
Task: 2.4
Requirements: 1.3
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
from x007007007.er_django import DjangoModelParser


class TestDbColumnParsingEdgeCases:
    """Unit tests for db_column parsing edge cases."""
    
    def test_field_with_db_column_attribute(self):
        """Test parsing a field that has db_column attribute specified."""
        # Create a field with explicit db_column
        field = models.CharField(max_length=100, db_column='user_name')
        field.name = 'username'
        field.set_attributes_from_name('username')
        
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Should use the db_column value
        assert column.db_column == 'user_name'
        assert column.name == 'username'
        assert column.database_column_name == 'user_name'
    
    def test_field_without_db_column_but_with_column_attribute(self):
        """Test parsing a field without db_column but with column attribute."""
        # Create a field without db_column
        field = models.CharField(max_length=100)
        field.name = 'email'
        field.set_attributes_from_name('email')
        
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Should use field.column (which Django sets automatically)
        assert column.db_column == field.column
        assert column.name == 'email'
        assert column.database_column_name == field.column
    
    def test_field_with_only_name(self):
        """Test parsing a field with only name (fallback case)."""
        # Create a minimal field
        field = models.IntegerField()
        field.name = 'age'
        field.set_attributes_from_name('age')
        
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Should fall back to field name
        assert column.db_column is not None
        assert column.name == 'age'
        # db_column should be either field.column or field.name
        assert column.db_column in ['age', field.column]
    
    def test_model_without_db_table_raises_error(self):
        """Test that parsing a model without _meta.db_table raises an error."""
        # Create a mock model without db_table
        class MockMeta:
            pass
        
        class InvalidModel:
            __name__ = 'InvalidModel'
            __module__ = 'test_module'
            _meta = MockMeta()
        
        parser = DjangoModelParser()
        
        # Should raise ValueError when db_table is missing
        with pytest.raises(ValueError, match="Cannot get db_table for model InvalidModel"):
            parser._convert_model_to_entity(InvalidModel)
    
    def test_model_with_empty_db_table_raises_error(self):
        """Test that parsing a model with empty db_table raises an error."""
        # Create a mock model with empty db_table
        class MockMeta:
            db_table = ''
        
        class InvalidModel:
            __name__ = 'InvalidModel'
            __module__ = 'test_module'
            _meta = MockMeta()
        
        parser = DjangoModelParser()
        
        # Should raise ValueError when db_table is empty
        with pytest.raises(ValueError, match="db_table is empty for model InvalidModel"):
            parser._convert_model_to_entity(InvalidModel)
    
    def test_field_with_empty_db_column_falls_back(self):
        """Test that a field with empty db_column string falls back to column or name."""
        # Create a field with empty db_column (edge case)
        field = models.CharField(max_length=100, db_column='')
        field.name = 'title'
        field.set_attributes_from_name('title')
        
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Should fall back to field.column since db_column is empty
        assert column.db_column == field.column
        assert column.name == 'title'
    
    def test_field_with_special_characters_in_db_column(self):
        """Test parsing a field with special characters in db_column."""
        # Some databases allow special characters in column names
        field = models.CharField(max_length=100, db_column='user$name')
        field.name = 'username'
        field.set_attributes_from_name('username')
        
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Should preserve the special characters
        assert column.db_column == 'user$name'
        assert column.name == 'username'
    
    def test_foreign_key_field_db_column(self):
        """Test parsing a ForeignKey field with db_column."""
        # ForeignKey fields have special handling
        field = models.ForeignKey(
            'auth.User',
            on_delete=models.CASCADE,
            db_column='author_id'
        )
        field.name = 'author'
        field.set_attributes_from_name('author')
        
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Should use the specified db_column
        assert column.db_column == 'author_id'
        assert column.name == 'author'
        assert column.is_fk is True
