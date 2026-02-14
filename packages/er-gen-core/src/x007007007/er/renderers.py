import logging
import re
from pathlib import Path
from typing import Dict
from jinja2 import Environment, PackageLoader, select_autoescape
from x007007007.er.base import Renderer
from x007007007.er.models import ERModel
from x007007007.er.type_mapper import TypeMapper

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


def sqlalchemy_column_type(col):
    """Jinja2 filter for SQLAlchemy column type."""
    column_type, params = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
    return column_type, params


class JinjaRenderer(Renderer):
    def __init__(self, template_name: str, table_prefix: str = ''):
        self.env = Environment(
            loader=PackageLoader("x007007007.er", "templates"),
            autoescape=select_autoescape()
        )
        # Register custom filters
        self.env.filters['django_field_type'] = django_field_type
        self.env.filters['sqlalchemy_column_type'] = sqlalchemy_column_type
        self.template = self.env.get_template(template_name)
        self.table_prefix = table_prefix

    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(model=model, table_prefix=self.table_prefix)

class DjangoRenderer(JinjaRenderer):
    def __init__(self, app_label: str = 'app', table_prefix: str = ''):
        super().__init__("django_model.j2", table_prefix=table_prefix)
        self.app_label = app_label

    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(model=model, app_label=self.app_label, table_prefix=self.table_prefix)

class SQLAlchemyRenderer(JinjaRenderer):
    def __init__(self, table_prefix: str = ''):
        super().__init__("sqlalchemy_model.j2", table_prefix=table_prefix)


class DjangoPackageRenderer(Renderer):
    """Renderer that generates Django models as a package (one file per model)."""
    
    def __init__(self, app_label: str = 'app', table_prefix: str = ''):
        self.env = Environment(
            loader=PackageLoader("x007007007.er", "templates"),
            autoescape=select_autoescape()
        )
        # Register custom filters
        self.env.filters['django_field_type'] = django_field_type
        self.env.filters['sqlalchemy_column_type'] = sqlalchemy_column_type
        
        self.single_template = self.env.get_template("django_model_single.j2")
        self.init_template = self.env.get_template("django_init.j2")
        self.app_label = app_label
        self.table_prefix = table_prefix
    
    def render(self, model: ERModel) -> Dict[str, str]:
        """
        Render Django models as multiple files.
        
        Returns:
            Dict[str, str]: Dictionary mapping file paths to content
                - '__init__.py': Package init file
                - '<model_name>.py': Individual model files (in snake_case)
        """
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        
        files = {}
        entity_names = list(model.entities.keys())
        
        # Generate __init__.py with snake_case imports
        entity_info = [
            {'name': name, 'filename': to_snake_case(name)}
            for name in entity_names
        ]
        files['__init__.py'] = self.init_template.render(
            entity_names=entity_names,
            entity_info=entity_info
        )
        
        # Generate individual model files with snake_case filenames
        for entity_name, entity in model.entities.items():
            filename = f"{to_snake_case(entity_name)}.py"
            content = self.single_template.render(
                entity=entity,
                model=model,
                app_label=self.app_label,
                table_prefix=self.table_prefix
            )
            files[filename] = content
        
        return files
    
    def write_to_directory(self, model: ERModel, output_dir: str) -> None:
        """
        Write rendered models to a directory.
        
        Args:
            model: ERModel instance
            output_dir: Output directory path
        """
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

