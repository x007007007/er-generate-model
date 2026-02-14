"""Type mapping utilities for converting database types to ORM types."""
import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class TypeMapper:
    """Maps database types to Django and SQLAlchemy field types."""
    
    # Type patterns and their mappings
    TYPE_PATTERNS = {
        'int': {
            'django': 'IntegerField',
            'sqlalchemy': 'Integer',
            'patterns': [r'int', r'integer', r'bigint', r'smallint', r'tinyint']
        },
        'float': {
            'django': 'FloatField',
            'sqlalchemy': 'Float',
            'patterns': [r'float', r'real', r'double']
        },
        'decimal': {
            'django': 'DecimalField',
            'sqlalchemy': 'Numeric',
            'patterns': [r'decimal', r'numeric']
        },
        'boolean': {
            'django': 'BooleanField',
            'sqlalchemy': 'Boolean',
            'patterns': [r'bool', r'boolean']
        },
        'date': {
            'django': 'DateField',
            'sqlalchemy': 'Date',
            'patterns': [r'date']
        },
        'time': {
            'django': 'TimeField',
            'sqlalchemy': 'Time',
            'patterns': [r'time']
        },
        'datetime': {
            'django': 'DateTimeField',
            'sqlalchemy': 'DateTime',
            'patterns': [r'datetime', r'timestamp']
        },
        'text': {
            'django': 'TextField',
            'sqlalchemy': 'Text',
            'patterns': [r'text', r'longtext', r'clob']
        },
        'string': {
            'django': 'CharField',
            'sqlalchemy': 'String',
            'patterns': [r'string', r'varchar', r'char', r'nvarchar']
        },
        'json': {
            'django': 'JSONField',
            'sqlalchemy': 'JSON',
            'patterns': [r'json', r'jsonb']
        },
        'uuid': {
            'django': 'UUIDField',
            'sqlalchemy': 'UUID',
            'patterns': [r'uuid', r'guid']
        },
        'file': {
            'django': 'FileField',
            'sqlalchemy': 'String',
            'patterns': [r'file', r'upload']
        },
    }
    
    @classmethod
    def _normalize_type(cls, type_str: str) -> str:
        """Normalize type string for matching."""
        return type_str.lower().strip()
    
    @classmethod
    def _match_type(cls, type_str: str) -> Optional[str]:
        """Match type string to a known type category."""
        normalized = cls._normalize_type(type_str)
        
        for type_category, config in cls.TYPE_PATTERNS.items():
            for pattern in config['patterns']:
                if re.search(pattern, normalized):
                    return type_category
        
        return None
    
    @classmethod
    def get_django_type(cls, col_type: str, max_length: Optional[int] = None) -> Tuple[str, dict]:
        """
        Get Django field type and parameters.
        Returns (field_type, params_dict)
        """
        assert isinstance(col_type, str), "col_type must be a string"
        
        type_category = cls._match_type(col_type)
        if not type_category:
            logger.warning(f"Unknown type '{col_type}', defaulting to CharField")
            type_category = 'string'
        
        field_type = cls.TYPE_PATTERNS[type_category]['django']
        params = {}
        
        # Add max_length for string types
        if type_category == 'string':
            params['max_length'] = max_length or 255
        
        # Add max_digits and decimal_places for decimal types
        if type_category == 'decimal':
            # Try to extract precision and scale from type string
            match = re.search(r'decimal\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', col_type.lower())
            if match:
                params['max_digits'] = int(match.group(1))
                params['decimal_places'] = int(match.group(2))
            else:
                params['max_digits'] = 10
                params['decimal_places'] = 2
        
        return field_type, params
    
    @classmethod
    def get_sqlalchemy_type(cls, col_type: str, max_length: Optional[int] = None) -> Tuple[str, dict]:
        """
        Get SQLAlchemy column type and parameters.
        Returns (column_type, params_dict)
        """
        assert isinstance(col_type, str), "col_type must be a string"
        
        type_category = cls._match_type(col_type)
        if not type_category:
            logger.warning(f"Unknown type '{col_type}', defaulting to String")
            type_category = 'string'
        
        column_type = cls.TYPE_PATTERNS[type_category]['sqlalchemy']
        params = {}
        
        # Add length for string types
        if type_category == 'string':
            if max_length:
                column_type = f"String({max_length})"
            else:
                column_type = "String(255)"
        
        # Add precision and scale for decimal types
        if type_category == 'decimal':
            match = re.search(r'decimal\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', col_type.lower())
            if match:
                precision = int(match.group(1))
                scale = int(match.group(2))
                column_type = f"Numeric({precision}, {scale})"
            else:
                column_type = "Numeric(10, 2)"
        
        return column_type, params

