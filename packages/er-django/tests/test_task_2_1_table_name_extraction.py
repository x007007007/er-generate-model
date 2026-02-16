"""
Tests for Task 2.1: table_name extraction in _convert_model_to_entity

Requirements: 2.2, 3.2
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
from x007007007.er_django.parser import DjangoModelParser


class TableNameTestModel(models.Model):
    """Simple model without custom db_table"""
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test_app'


class CustomTableNameTestModel(models.Model):
    """Model with custom db_table"""
    title = models.CharField(max_length=200)
    
    class Meta:
        app_label = 'test_app'
        db_table = 'custom_table_name'


class TestTableNameExtraction:
    """Test that _convert_model_to_entity extracts table_name correctly"""
    
    def test_default_table_name(self):
        """Test extraction of default Django table name"""
        parser = DjangoModelParser(app_label='test_app')
        entity = parser._convert_model_to_entity(TableNameTestModel)
        
        # Django default: {app_label}_{model_name_lower}
        assert entity.table_name == 'test_app_tablenametestmodel'
    
    def test_custom_table_name(self):
        """Test extraction of custom db_table"""
        parser = DjangoModelParser(app_label='test_app')
        entity = parser._convert_model_to_entity(CustomTableNameTestModel)
        
        assert entity.table_name == 'custom_table_name'
    
    def test_table_name_not_none(self):
        """Test that table_name is always set (never None)"""
        parser = DjangoModelParser(app_label='test_app')
        entity = parser._convert_model_to_entity(TableNameTestModel)
        
        assert entity.table_name is not None
        assert isinstance(entity.table_name, str)
        assert len(entity.table_name) > 0
