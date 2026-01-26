"""
Django Model Introspector - Extract metadata from Django models
"""
import logging
from typing import Dict, List, Optional, Any, Type
from django.db import models
from django.db.models import Field, ForeignKey, OneToOneField, ManyToManyField

logger = logging.getLogger(__name__)


class DjangoModelIntrospector:
    """Extract metadata from Django models for ER conversion"""
    
    @staticmethod
    def get_field_type(field: Field) -> str:
        """
        Get the ER type from Django field.
        
        Args:
            field: Django field instance
            
        Returns:
            ER type string
        """
        field_class = field.__class__.__name__
        
        # Map Django field types to ER types
        type_mapping = {
            'AutoField': 'int',
            'BigAutoField': 'bigint',
            'SmallAutoField': 'smallint',
            'IntegerField': 'int',
            'BigIntegerField': 'bigint',
            'SmallIntegerField': 'smallint',
            'PositiveIntegerField': 'int',
            'PositiveSmallIntegerField': 'smallint',
            'PositiveBigIntegerField': 'bigint',
            'CharField': 'string',
            'TextField': 'text',
            'EmailField': 'string',
            'URLField': 'string',
            'SlugField': 'string',
            'UUIDField': 'uuid',
            'BooleanField': 'boolean',
            'DateField': 'date',
            'DateTimeField': 'datetime',
            'TimeField': 'time',
            'DecimalField': 'decimal',
            'FloatField': 'float',
            'BinaryField': 'binary',
            'JSONField': 'json',
            'FileField': 'string',
            'ImageField': 'string',
            'FilePathField': 'string',
        }
        
        return type_mapping.get(field_class, 'string')
    
    @staticmethod
    def get_field_max_length(field: Field) -> Optional[int]:
        """Get max_length from Django field"""
        return getattr(field, 'max_length', None)
    
    @staticmethod
    def get_field_precision_scale(field: Field) -> tuple[Optional[int], Optional[int]]:
        """Get precision and scale from DecimalField"""
        if isinstance(field, models.DecimalField):
            return getattr(field, 'max_digits', None), getattr(field, 'decimal_places', None)
        return None, None
    
    @staticmethod
    def is_primary_key(field: Field) -> bool:
        """Check if field is primary key"""
        return field.primary_key
    
    @staticmethod
    def is_nullable(field: Field) -> bool:
        """Check if field is nullable"""
        return field.null
    
    @staticmethod
    def is_unique(field: Field) -> bool:
        """Check if field has unique constraint"""
        return field.unique
    
    @staticmethod
    def has_db_index(field: Field) -> bool:
        """Check if field has database index"""
        return field.db_index
    
    @staticmethod
    def get_default(field: Field) -> Optional[Any]:
        """Get default value from field"""
        if field.has_default():
            default = field.default
            # Handle callable defaults
            if callable(default):
                return None
            return default
        return None
    
    @staticmethod
    def get_help_text(field: Field) -> Optional[str]:
        """Get help text (comment) from field"""
        if field.help_text:
            # Convert lazy text to string
            return str(field.help_text)
        return None
    
    @staticmethod
    def get_related_model(field: Field) -> Optional[str]:
        """Get related model name from ForeignKey/OneToOneField"""
        if isinstance(field, (ForeignKey, OneToOneField)):
            related_model = field.related_model
            if isinstance(related_model, str):
                return related_model
            return related_model.__name__
        return None
    
    @staticmethod
    def get_on_delete(field: Field) -> str:
        """Get on_delete behavior from ForeignKey/OneToOneField"""
        if isinstance(field, (ForeignKey, OneToOneField)):
            on_delete = field.remote_field.on_delete
            # Map Django on_delete to SQL
            mapping = {
                models.CASCADE: 'CASCADE',
                models.SET_NULL: 'SET NULL',
                models.SET_DEFAULT: 'SET DEFAULT',
                models.PROTECT: 'RESTRICT',
                models.DO_NOTHING: 'NO ACTION',
            }
            return mapping.get(on_delete, 'CASCADE')
        return 'CASCADE'
    
    @staticmethod
    def get_m2m_related_model(field: ManyToManyField) -> Optional[str]:
        """Get related model name from ManyToManyField"""
        if isinstance(field, ManyToManyField):
            related_model = field.related_model
            if isinstance(related_model, str):
                return related_model
            return related_model.__name__
        return None
    
    @staticmethod
    def get_table_name(model: Type[models.Model]) -> str:
        """Get database table name from model"""
        return model._meta.db_table
    
    @staticmethod
    def get_model_comment(model: Type[models.Model]) -> Optional[str]:
        """Get model comment from verbose_name"""
        return model._meta.verbose_name if hasattr(model._meta, 'verbose_name') else None
    
    @staticmethod
    def get_all_fields(model: Type[models.Model]) -> List[Field]:
        """Get all fields from model (excluding auto-created reverse relations)"""
        return [
            field for field in model._meta.get_fields()
            if not field.auto_created or field.concrete
        ]
    
    @staticmethod
    def get_concrete_fields(model: Type[models.Model]) -> List[Field]:
        """Get concrete fields (fields that have database columns)"""
        return [
            field for field in model._meta.get_fields()
            if field.concrete and not isinstance(field, ManyToManyField)
        ]
    
    @staticmethod
    def get_foreign_keys(model: Type[models.Model]) -> List[ForeignKey]:
        """Get all ForeignKey fields"""
        return [
            field for field in model._meta.get_fields()
            if isinstance(field, ForeignKey)
        ]
    
    @staticmethod
    def get_one_to_one_fields(model: Type[models.Model]) -> List[OneToOneField]:
        """Get all OneToOneField fields"""
        return [
            field for field in model._meta.get_fields()
            if isinstance(field, OneToOneField)
        ]
    
    @staticmethod
    def get_many_to_many_fields(model: Type[models.Model]) -> List[ManyToManyField]:
        """Get all ManyToManyField fields"""
        return [
            field for field in model._meta.get_fields()
            if isinstance(field, ManyToManyField) and not field.auto_created
        ]
