"""
Property-based tests for Django parser db_column extraction.

These tests use hypothesis to verify universal properties across many generated inputs.
Each test runs a minimum of 100 iterations.

Feature: field-db-column-and-path-separation
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

from hypothesis import given, settings as hypothesis_settings, strategies as st, HealthCheck
from django.db import models
from x007007007.er_django import DjangoModelParser


# Custom strategies for generating field definitions
safe_identifier = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30 and s not in ['id'])
safe_db_column = st.from_regex(r'[a-z][a-z0-9_]*', fullmatch=True).filter(lambda s: len(s) < 30)


@st.composite
def field_with_db_column(draw):
    """Generate a field name and db_column name pair."""
    field_name = draw(safe_identifier)
    # Sometimes use same name, sometimes different
    use_different = draw(st.booleans())
    if use_different:
        db_column_name = draw(safe_db_column.filter(lambda s: s != field_name))
    else:
        db_column_name = field_name
    
    return field_name, db_column_name


class TestProperty1DbColumnExtractionCorrectness:
    """
    Property 1: db_column参数提取正确性
    
    **Feature: field-db-column-and-path-separation, Property 1: db_column参数提取正确性**
    **Validates: Requirements 1.1, 1.3**
    
    For any Django field definition with db_column parameter, the parser should
    correctly extract the db_column value. When db_column is not specified,
    the parser should use field.column or field.name as fallback.
    """
    
    @hypothesis_settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(field_with_db_column())
    def test_parser_extracts_db_column_when_specified(self, field_data):
        """Test that parser correctly extracts db_column when specified."""
        field_name, db_column_name = field_data
        
        # Create a dynamic model with db_column specified
        class TestModel(models.Model):
            class Meta:
                app_label = 'test_app'
        
        # Add field with db_column
        field = models.CharField(max_length=100, db_column=db_column_name)
        field.name = field_name
        field.model = TestModel
        field.set_attributes_from_name(field_name)
        
        # Parse the field
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Verify db_column is extracted correctly
        assert column.db_column == db_column_name, \
            f"Expected db_column to be '{db_column_name}', got '{column.db_column}'"
        
        # Verify name is the field name
        assert column.name == field_name, \
            f"Expected name to be '{field_name}', got '{column.name}'"
    
    @hypothesis_settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(safe_identifier)
    def test_parser_uses_field_name_when_db_column_not_specified(self, field_name):
        """Test that parser uses field name when db_column is not specified."""
        # Create a field without db_column
        field = models.CharField(max_length=100)
        field.name = field_name
        field.set_attributes_from_name(field_name)
        
        # Parse the field
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Verify db_column falls back to field name
        assert column.db_column is not None, "db_column should never be None"
        assert column.db_column == field_name or column.db_column == field.column, \
            f"Expected db_column to be '{field_name}' or field.column, got '{column.db_column}'"
        
        # Verify name is the field name
        assert column.name == field_name, \
            f"Expected name to be '{field_name}', got '{column.name}'"
    
    @hypothesis_settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(field_with_db_column())
    def test_db_column_always_has_value(self, field_data):
        """Test that db_column field always has a non-empty value."""
        field_name, db_column_name = field_data
        
        # Create a field with db_column
        field = models.CharField(max_length=100, db_column=db_column_name)
        field.name = field_name
        field.set_attributes_from_name(field_name)
        
        # Parse the field
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Verify db_column is always present and non-empty
        assert column.db_column is not None, "db_column must not be None"
        assert isinstance(column.db_column, str), "db_column must be a string"
        assert len(column.db_column) > 0, "db_column must not be empty"
    
    @hypothesis_settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(field_with_db_column())
    def test_database_column_name_property_returns_db_column(self, field_data):
        """Test that database_column_name property returns db_column value."""
        field_name, db_column_name = field_data
        
        # Create a field with db_column
        field = models.CharField(max_length=100, db_column=db_column_name)
        field.name = field_name
        field.set_attributes_from_name(field_name)
        
        # Parse the field
        parser = DjangoModelParser()
        column = parser._convert_field_to_column(field)
        
        # Verify database_column_name property equals db_column
        assert column.database_column_name == column.db_column, \
            f"database_column_name should equal db_column"
        assert column.database_column_name == db_column_name, \
            f"Expected database_column_name to be '{db_column_name}', got '{column.database_column_name}'"
    
    @hypothesis_settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    @given(st.lists(field_with_db_column(), min_size=1, max_size=10))
    def test_multiple_fields_preserve_individual_db_columns(self, fields_data):
        """Test that multiple fields each preserve their own db_column values."""
        parser = DjangoModelParser()
        
        for field_name, db_column_name in fields_data:
            # Create a field with db_column
            field = models.CharField(max_length=100, db_column=db_column_name)
            field.name = field_name
            field.set_attributes_from_name(field_name)
            
            # Parse the field
            column = parser._convert_field_to_column(field)
            
            # Verify each field preserves its own db_column
            assert column.db_column == db_column_name, \
                f"Field '{field_name}' should have db_column '{db_column_name}', got '{column.db_column}'"
            assert column.name == field_name, \
                f"Field should have name '{field_name}', got '{column.name}'"
