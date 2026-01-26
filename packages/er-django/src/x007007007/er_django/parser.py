"""
Django Model Parser - Convert Django models to ER model format
"""
import logging
from typing import List, Dict, Type, Optional
from django.apps import apps
from django.db import models
from django.db.models import ForeignKey, OneToOneField, ManyToManyField

from x007007007.er.models import ERModel, Entity, Column, Relationship
from x007007007.er.base import Parser
from .introspector import DjangoModelIntrospector

logger = logging.getLogger(__name__)


class DjangoModelParser(Parser):
    """
    Parse Django models to ER model format.
    
    This parser can work with:
    - A specific Django app (namespace)
    - A list of model classes
    - All models in the project
    """
    
    def __init__(self, app_label: Optional[str] = None):
        """
        Initialize parser.
        
        Args:
            app_label: Django app label (namespace). If None, parse all apps.
        """
        self.app_label = app_label
        self.introspector = DjangoModelIntrospector()
    
    def parse(self, models_list: Optional[List[Type[models.Model]]] = None) -> ERModel:
        """
        Parse Django models to ERModel.
        
        Args:
            models_list: Optional list of model classes. If None, use app_label or all models.
            
        Returns:
            ERModel instance
        """
        er_model = ERModel()
        
        # Get models to parse
        if models_list:
            target_models = models_list
        elif self.app_label:
            target_models = self._get_app_models(self.app_label)
        else:
            target_models = self._get_all_models()
        
        logger.info(f"Parsing {len(target_models)} Django models...")
        
        # First pass: Create entities
        for model in target_models:
            entity = self._convert_model_to_entity(model)
            er_model.add_entity(entity)
            logger.debug(f"Added entity: {entity.name}")
        
        # Second pass: Create relationships
        for model in target_models:
            relationships = self._extract_relationships(model)
            for rel in relationships:
                # Only add if both entities exist
                if rel.left_entity in er_model.entities and rel.right_entity in er_model.entities:
                    er_model.add_relationship(rel)
                    logger.debug(f"Added relationship: {rel.left_entity} -> {rel.right_entity}")
        
        return er_model
    
    def _get_app_models(self, app_label: str) -> List[Type[models.Model]]:
        """Get all models from a specific app"""
        try:
            app_config = apps.get_app_config(app_label)
            return list(app_config.get_models())
        except LookupError:
            logger.error(f"App '{app_label}' not found")
            return []
    
    def _get_all_models(self) -> List[Type[models.Model]]:
        """Get all models from all apps"""
        return list(apps.get_models())
    
    def _convert_model_to_entity(self, model: Type[models.Model]) -> Entity:
        """
        Convert Django model to Entity.
        
        Args:
            model: Django model class
            
        Returns:
            Entity instance
        """
        entity = Entity(
            name=model.__name__,
            comment=self.introspector.get_model_comment(model)
        )
        
        # Get concrete fields (fields with database columns)
        concrete_fields = self.introspector.get_concrete_fields(model)
        
        for field in concrete_fields:
            # Skip reverse relations and auto-created fields
            if field.auto_created and not field.concrete:
                continue
            
            # Skip ManyToManyField (handled in relationships)
            if isinstance(field, ManyToManyField):
                continue
            
            column = self._convert_field_to_column(field)
            entity.columns.append(column)
        
        return entity
    
    def _convert_field_to_column(self, field) -> Column:
        """
        Convert Django field to Column.
        
        Args:
            field: Django field instance
            
        Returns:
            Column instance
        """
        # Get field metadata
        field_type = self.introspector.get_field_type(field)
        max_length = self.introspector.get_field_max_length(field)
        precision, scale = self.introspector.get_field_precision_scale(field)
        
        # Check if it's a foreign key
        is_fk = isinstance(field, (ForeignKey, OneToOneField))
        
        column = Column(
            name=field.column if hasattr(field, 'column') else field.name,
            type=field_type,
            is_pk=self.introspector.is_primary_key(field),
            is_fk=is_fk,
            nullable=self.introspector.is_nullable(field),
            unique=self.introspector.is_unique(field),
            indexed=self.introspector.has_db_index(field),
            default=self.introspector.get_default(field),
            comment=self.introspector.get_help_text(field),
            max_length=max_length,
            precision=precision,
            scale=scale
        )
        
        return column
    
    def _extract_relationships(self, model: Type[models.Model]) -> List[Relationship]:
        """
        Extract relationships from Django model.
        
        Args:
            model: Django model class
            
        Returns:
            List of Relationship instances
        """
        relationships = []
        
        # ForeignKey relationships (many-to-one)
        for field in self.introspector.get_foreign_keys(model):
            related_model_name = self.introspector.get_related_model(field)
            if not related_model_name:
                continue
            
            rel = Relationship(
                left_entity=related_model_name,  # Referenced model (one side)
                right_entity=model.__name__,      # Current model (many side)
                relation_type='one-to-many',
                left_column='id',  # Assume primary key is 'id'
                right_column=field.column,
                left_cardinality='1',
                right_cardinality='*'
            )
            relationships.append(rel)
        
        # OneToOneField relationships
        for field in self.introspector.get_one_to_one_fields(model):
            related_model_name = self.introspector.get_related_model(field)
            if not related_model_name:
                continue
            
            rel = Relationship(
                left_entity=model.__name__,
                right_entity=related_model_name,
                relation_type='one-to-one',
                left_column=field.column,
                right_column='id',  # Assume primary key is 'id'
                left_cardinality='1',
                right_cardinality='1'
            )
            relationships.append(rel)
        
        # ManyToManyField relationships
        for field in self.introspector.get_many_to_many_fields(model):
            related_model_name = self.introspector.get_m2m_related_model(field)
            if not related_model_name:
                continue
            
            rel = Relationship(
                left_entity=model.__name__,
                right_entity=related_model_name,
                relation_type='many-to-many',
                left_cardinality='*',
                right_cardinality='*'
            )
            relationships.append(rel)
        
        return relationships
