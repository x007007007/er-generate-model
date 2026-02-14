"""Django model code renderers."""
import logging
import re
from pathlib import Path
from typing import Dict
from jinja2 import PackageLoader
from x007007007.er.models import ERModel
from x007007007.er.type_mapper import TypeMapper
from x007007007.er.renderers.python.base import PythonRenderer

logger = logging.getLogger(__name__)


def to_snake_case(name: str) -> str:
    """
    Convert CamelCase or PascalCase to snake_case.
    
    Examples:
        User -> user
        ConversationSessionModel -> conversation_session_model
        FileTypeModel -> file_type_model
    """
    # Insert underscore before uppercase letters (except at start)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insert underscore before uppercase letters preceded by lowercase
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def django_field_type(col):
    """Jinja2 filter for Django field type."""
    field_type, params = TypeMapper.get_django_type(col.type, col.max_length)
    return field_type, params


class DjangoRenderer(PythonRenderer):
    """Django model code renderer (single file output)."""
    
    def __init__(self, app_label: str = 'app', table_prefix: str = ''):
        self.app_label = app_label
        self.table_prefix = table_prefix
        
        # Set up Jinja2 environment WITHOUT whitespace control for backward compatibility
        loader = PackageLoader("x007007007.er.renderers.python.django", "templates")
        from jinja2 import Environment, select_autoescape
        self.env = Environment(
            loader=loader,
            autoescape=select_autoescape()
        )
        
        # Register filters
        self.env.filters['django_field_type'] = django_field_type
        self.env.filters['code_value'] = self.serialize_value
        
        self.template = self.env.get_template("django_model.j2")
    
    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(
            model=model,
            app_label=self.app_label,
            table_prefix=self.table_prefix
        )


class DjangoPackageRenderer(PythonRenderer):
    """
    Django model code renderer (package output with three files per entity).
    Django 模型代码渲染器（包输出，每个实体三个文件）。
    """
    
    def __init__(self, app_label: str = 'app', table_prefix: str = ''):
        self.app_label = app_label
        self.table_prefix = table_prefix
        
        # Set up Jinja2 environment WITHOUT whitespace control for backward compatibility
        loader = PackageLoader("x007007007.er.renderers.python.django", "templates")
        from jinja2 import Environment, select_autoescape
        self.env = Environment(
            loader=loader,
            autoescape=select_autoescape()
        )
        
        # Register filters
        self.env.filters['django_field_type'] = django_field_type
        self.env.filters['code_value'] = self.serialize_value
        
        # Load templates for each component
        self.model_template = self.env.get_template("django_model_only.j2")
        self.manager_template = self.env.get_template("django_manager_only.j2")
        self.queryset_template = self.env.get_template("django_queryset_only.j2")
        self.init_template = self.env.get_template("django_init.j2")
    
    def render(self, model: ERModel) -> Dict[str, str]:
        """
        Render Django models as multiple files (3 files per entity).
        
        Returns:
            Dict[str, str]: Dictionary mapping file paths to content
        """
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        
        files = {}
        entity_names = list(model.entities.keys())
        
        # Generate __init__.py
        entity_info = [
            {'name': name, 'filename': to_snake_case(name)}
            for name in entity_names
        ]
        files['__init__.py'] = self.init_template.render(
            entity_names=entity_names,
            entity_info=entity_info
        )
        
        # Generate three files for each entity
        for entity_name, entity in model.entities.items():
            base_filename = to_snake_case(entity_name)
            
            # 1. QuerySet file
            queryset_filename = f"{base_filename}_queryset.py"
            files[queryset_filename] = self.queryset_template.render(
                entity=entity,
                model=model
            )
            
            # 2. Manager file
            manager_filename = f"{base_filename}_manager.py"
            files[manager_filename] = self.manager_template.render(
                entity=entity,
                model=model,
                base_filename=base_filename
            )
            
            # 3. Model file
            model_filename = f"{base_filename}_model.py"
            files[model_filename] = self.model_template.render(
                entity=entity,
                model=model,
                app_label=self.app_label,
                table_prefix=self.table_prefix,
                base_filename=base_filename
            )
        
        return files
    
    def write_to_directory(self, model: ERModel, output_dir: str) -> None:
        """Write rendered models to a directory."""
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        assert isinstance(output_dir, str), "output_dir must be a string"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files = self.render(model)
        
        for filename, content in files.items():
            file_path = output_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Generated: {file_path}")
