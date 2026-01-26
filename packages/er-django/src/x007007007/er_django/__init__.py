"""
Django integration for ER diagram and migration system.

This module provides Django-specific functionality:
- Parse Django models to ER diagrams
- Generate ER-based migrations from Django models
- Export Django models to Mermaid/PlantUML diagrams
"""

from .parser import DjangoModelParser
from .introspector import DjangoModelIntrospector

__all__ = [
    'DjangoModelParser',
    'DjangoModelIntrospector',
]
