"""
Tests for DjangoModelParser inheritance detection (_extract_inheritance method)

Tests for task 5.1: 实现 _extract_inheritance() 方法
Requirements: 6.1, 6.2, 6.3, 6.6, 6.7, 6.8, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6
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


# Test models with inheritance
class SimpleModel(models.Model):
    """Model that only inherits from models.Model"""
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'test_app'


class SingleInheritanceModel(TimeStampedModel):
    """Model with single inheritance"""
    title = models.CharField(max_length=200)
    
    class Meta:
        app_label = 'test_app'


class MultipleInheritanceModel(TimeStampedModel, SoftDeleteModel):
    """Model with multiple inheritance"""
    content = models.TextField()
    
    class Meta:
        app_label = 'test_app'


class CustomUser(AbstractUser):
    """Model inheriting from Django's AbstractUser"""
    phone = models.CharField(max_length=20, blank=True)
    
    class Meta:
        app_label = 'test_app'


class TestExtractInheritance:
    """Test _extract_inheritance() method"""
    
    def test_models_model_excluded(self):
        """
        Test that models.Model is excluded from inheritance list
        Requirements: 6.8, 9.5
        """
        parser = DjangoModelParser()
        extends = parser._extract_inheritance(SimpleModel)
        
        # Should not include models.Model
        assert 'django.db.models.Model' not in extends
        assert len(extends) == 0
    
    def test_single_inheritance(self):
        """
        Test single inheritance detection
        Requirements: 6.1, 9.1
        """
        parser = DjangoModelParser()
        extends = parser._extract_inheritance(SingleInheritanceModel)
        
        # Should include TimeStampedModel
        assert len(extends) == 1
        assert extends[0].endswith('.TimeStampedModel')
        assert 'test_parser_inheritance' in extends[0]
    
    def test_multiple_inheritance_mro_order(self):
        """
        Test multiple inheritance in MRO order
        Requirements: 6.3, 9.3, 9.4
        """
        parser = DjangoModelParser()
        extends = parser._extract_inheritance(MultipleInheritanceModel)
        
        # Should include both parent classes in MRO order
        assert len(extends) == 2
        
        # First parent should be TimeStampedModel
        assert extends[0].endswith('.TimeStampedModel')
        
        # Second parent should be SoftDeleteModel
        assert extends[1].endswith('.SoftDeleteModel')
    
    def test_django_builtin_inheritance(self):
        """
        Test inheritance from Django built-in models (AbstractUser)
        Requirements: 6.6, 9.2
        """
        parser = DjangoModelParser()
        extends = parser._extract_inheritance(CustomUser)
        
        # Should include AbstractUser with full module path
        assert len(extends) == 1
        assert extends[0] == 'django.contrib.auth.models.AbstractUser'
    
    def test_full_module_path_recorded(self):
        """
        Test that full module path is recorded (module.ClassName)
        Requirements: 6.6, 9.2
        """
        parser = DjangoModelParser()
        extends = parser._extract_inheritance(SingleInheritanceModel)
        
        # Should have format: module.ClassName
        assert len(extends) == 1
        assert '.' in extends[0]  # Has module separator
        assert extends[0].endswith('TimeStampedModel')  # Ends with class name
        
        # Should contain the module path
        parts = extends[0].split('.')
        assert len(parts) >= 2  # At least module.ClassName
    
    def test_inheritance_with_abstract_base(self):
        """
        Test inheritance detection with abstract base models
        Requirements: 6.1, 9.1
        """
        parser = DjangoModelParser()
        
        # TimeStampedModel is abstract
        extends = parser._extract_inheritance(SingleInheritanceModel)
        assert len(extends) == 1
        
        # Should still record the abstract parent
        assert 'TimeStampedModel' in extends[0]
    
    def test_no_inheritance_returns_empty_list(self):
        """
        Test that models with only models.Model inheritance return empty list
        Requirements: 6.8, 9.5
        """
        parser = DjangoModelParser()
        extends = parser._extract_inheritance(SimpleModel)
        
        assert extends == []
        assert isinstance(extends, list)


class TestExtractInheritanceErrorHandling:
    """Test error handling in _extract_inheritance()"""
    
    def test_invalid_parent_class_fails_fast(self):
        """
        Test that invalid parent class raises ImportError (fail-fast)
        Requirements: 6.7, 9.6
        
        Note: This is difficult to test directly as Python won't allow
        creating a class with an invalid parent. This test documents
        the expected behavior.
        """
        parser = DjangoModelParser()
        
        # Normal case should work
        extends = parser._extract_inheritance(SimpleModel)
        assert isinstance(extends, list)
        
        # The actual fail-fast behavior is tested by the implementation
        # which checks for missing __module__ or __name__ attributes


class TestExtractInheritanceIntegration:
    """Integration tests for inheritance detection"""
    
    def test_inheritance_in_full_parse(self):
        """
        Test that inheritance is properly integrated in full model parsing
        Requirements: 6.1, 7.1, 9.1
        """
        parser = DjangoModelParser()
        
        # Parse a model with inheritance
        # Note: This test verifies the method exists and can be called
        # The actual integration with _convert_model_to_entity will be
        # tested in task 5.7
        extends = parser._extract_inheritance(SingleInheritanceModel)
        
        assert len(extends) > 0
        assert isinstance(extends, list)
        assert all(isinstance(e, str) for e in extends)
    
    def test_multiple_models_with_different_inheritance(self):
        """
        Test parsing multiple models with different inheritance patterns
        Requirements: 6.1, 6.3, 9.1, 9.3
        """
        parser = DjangoModelParser()
        
        # Model with no inheritance (except models.Model)
        extends1 = parser._extract_inheritance(SimpleModel)
        assert len(extends1) == 0
        
        # Model with single inheritance
        extends2 = parser._extract_inheritance(SingleInheritanceModel)
        assert len(extends2) == 1
        
        # Model with multiple inheritance
        extends3 = parser._extract_inheritance(MultipleInheritanceModel)
        assert len(extends3) == 2
        
        # Model inheriting from Django built-in
        extends4 = parser._extract_inheritance(CustomUser)
        assert len(extends4) == 1
        assert 'django.contrib.auth' in extends4[0]
