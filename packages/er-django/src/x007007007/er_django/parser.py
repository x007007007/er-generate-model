"""
Django Model Parser - Convert Django models to ER model format
"""
import logging
from typing import Any, List, Dict, Type, Optional
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
        
        abstract_bases: Dict[str, Type[models.Model]] = {}
        
        # First pass: Create entities and collect abstract base classes
        for model in target_models:
            entity = self._convert_model_to_entity(model)
            er_model.add_entity(entity)
            logger.debug(f"Added entity: {entity.name}")
            
            for ext_ref in entity.extends:
                base = self._resolve_extends_to_model(ext_ref)
                if base is not None and self._is_abstract_model(base):
                    abstract_bases[ext_ref] = base
        
        # Second pass: Create relationships
        for model in target_models:
            relationships = self._extract_relationships(model)
            for rel in relationships:
                # Only add if both entities exist
                if rel.left_entity in er_model.entities and rel.right_entity in er_model.entities:
                    er_model.add_relationship(rel)
                    logger.debug(f"Added relationship: {rel.left_entity} -> {rel.right_entity}")
        
        # Third pass: Add abstract base classes as templates
        for ext_ref, base_model in abstract_bases.items():
            template_key = base_model.__name__
            if template_key not in er_model.templates:
                template_data = self._convert_abstract_to_template(base_model)
                er_model.templates[template_key] = template_data
                logger.debug(f"Added template: {template_key} (from {ext_ref})")
        
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
            Convert Django model to Entity with inheritance support and table_name.

            Args:
                model: Django model class

            Returns:
                Entity instance with inheritance, package information, and table_name

            Requirements: 6.1, 7.1, 9.1, 2.2, 3.2
            """
            # Extract inheritance information
            extends = self._extract_inheritance(model)

            # Get package path
            package_path = model.__module__

            # Get database table name (required)
            try:
                table_name = model._meta.db_table
            except AttributeError as e:
                raise ValueError(
                    f"Cannot get db_table for model {model.__name__}. "
                    f"Model must have _meta.db_table attribute."
                ) from e
            
            if not table_name:
                raise ValueError(
                    f"db_table is empty for model {model.__name__}. "
                    f"Model must have a valid table name."
                )

            # Create entity with inheritance, package information, and table_name
            entity = Entity(
                name=model.__name__,
                comment=self.introspector.get_model_comment(model),
                extends=extends,
                package=package_path,
                table_name=table_name
            )

            # Get only the model's own fields (not inherited)
            own_fields = self._get_own_fields(model)

            for field in own_fields:
                # Skip reverse relations and auto-created fields
                if field.auto_created and not field.concrete:
                    continue

                # Skip ManyToManyField (handled in relationships)
                if isinstance(field, ManyToManyField):
                    continue

                column = self._convert_field_to_column(field)
                entity.columns.append(column)

            return entity
    def _extract_inheritance(self, model: Type[models.Model]) -> List[str]:
        """
        Extract inheritance information from Django model.

        Traverses the model's __bases__ to get all parent classes,
        skipping models.Model (default behavior). Records the full
        module path (module.ClassName) for each parent class in MRO order.

        Args:
            model: Django model class

        Returns:
            List of parent class paths (excluding models.Model)

        Raises:
            ImportError: If unable to resolve parent class module path (fail-fast)
        """
        extends = []

        # Get all base classes (MRO order)
        for base in model.__bases__:
            # Skip models.Model (default behavior)
            if base is models.Model:
                continue

            # Get full module path
            try:
                module = base.__module__
                class_name = base.__name__

                # Validate that we can construct a valid path
                if not module or not class_name:
                    raise ImportError(
                        f"Cannot resolve parent class for model '{model.__name__}': "
                        f"Invalid module ({module}) or class name ({class_name})"
                    )

                full_path = f"{module}.{class_name}"
                extends.append(full_path)

            except AttributeError as e:
                raise ImportError(
                    f"Cannot import parent class '{base}' for model '{model.__name__}': "
                    f"Missing __module__ or __name__ attribute. Error: {e}"
                ) from e

        return extends
    def _get_own_fields(self, model: Type[models.Model]) -> List:
        """
        Get fields defined in the model itself (not inherited).

        This method filters out fields that are inherited from parent classes,
        returning only the fields that are directly defined in the model.
        Only concrete fields (fields with database columns) are included.

        Args:
            model: Django model class

        Returns:
            List of field instances that are defined in the model itself

        Requirements: 6.4, 9.7
        """
        own_fields = []

        # Get all fields from the model
        all_fields = model._meta.get_fields()

        # Collect field names from all parent classes
        parent_field_names = set()
        for base in model.__bases__:
            # Skip models.Model
            if base is models.Model:
                continue

            # Check if base has _meta (is a Django model)
            if hasattr(base, '_meta'):
                for field in base._meta.get_fields():
                    parent_field_names.add(field.name)

        # Filter to only include own fields that are concrete
        for field in all_fields:
            # Skip if field is inherited from parent
            if field.name in parent_field_names:
                continue

            # Only include concrete fields (fields with database columns)
            if field.concrete:
                own_fields.append(field)

        return own_fields


    
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
        
        # Get database column name (required field)
        # Priority: db_column attribute > column attribute > field name
        if hasattr(field, 'db_column') and field.db_column:
            db_column = field.db_column
        elif hasattr(field, 'column'):
            db_column = field.column
        else:
            db_column = field.name
        
        column = Column(
            name=field.name,
            type=field_type,
            db_column=db_column,
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

    def _resolve_extends_to_model(self, extends_ref: str) -> Optional[Type[models.Model]]:
        """
        Resolve an extends reference string (module.ClassName) to the actual model class.

        Args:
            extends_ref: Full dotted path like 'kinkotech.common.infrastructure.models.base.KinkoTechModelBase'

        Returns:
            The model class if found, None otherwise
        """
        try:
            module_path, class_name = extends_ref.rsplit('.', 1)
            import importlib
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name, None)
            if cls is not None and isinstance(cls, type) and issubclass(cls, models.Model):
                return cls
        except (ImportError, AttributeError, ValueError):
            logger.debug(f"Could not resolve extends reference: {extends_ref}")
        return None

    def _is_abstract_model(self, model: Type[models.Model]) -> bool:
        """
        Check if a Django model is abstract.

        Args:
            model: Django model class

        Returns:
            True if the model has Meta.abstract = True
        """
        return getattr(model._meta, 'abstract', False)

    def _convert_abstract_to_template(self, model: Type[models.Model]) -> Dict[str, Any]:
        """
        Convert a Django abstract model to a template dict for ERModel.templates.

        Args:
            model: Django abstract model class

        Returns:
            Dict with 'package', 'columns', and optional 'comment' keys
        """
        columns = []
        for f in model._meta.get_fields():
            if not f.concrete:
                continue
            if isinstance(f, ManyToManyField):
                continue

            col = self._convert_field_to_column(f)
            columns.append({
                'name': col.name,
                'type': col.type,
            })
            if col.db_column != col.name:
                columns[-1]['db_column'] = col.db_column
            if col.is_pk:
                columns[-1]['primary_key'] = True
            if not col.nullable:
                columns[-1]['nullable'] = False
            if col.unique:
                columns[-1]['unique'] = True
            if col.default is not None:
                columns[-1]['default'] = col.default
            if col.max_length is not None:
                columns[-1]['max_length'] = col.max_length
            if col.precision is not None:
                columns[-1]['precision'] = col.precision
            if col.scale is not None:
                columns[-1]['scale'] = col.scale
            if col.comment:
                columns[-1]['comment'] = col.comment

        template_data: Dict[str, Any] = {
            'package': model.__module__,
            'columns': columns,
        }

        verbose_name = getattr(model._meta, 'verbose_name', None)
        if verbose_name:
            template_data['comment'] = str(verbose_name)

        return template_data
