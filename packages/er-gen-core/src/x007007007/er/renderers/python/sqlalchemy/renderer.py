"""SQLAlchemy model code renderer."""
from typing import Dict
from jinja2 import PackageLoader
from x007007007.er.models import ERModel
from x007007007.er.type_mapper import TypeMapper
from x007007007.er.renderers.python.base import PythonRenderer
from x007007007.er.renderers.python.utils import to_snake_case


def sqlalchemy_column_type(col):
    """Jinja2 filter for SQLAlchemy column type."""
    column_type, params = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
    return column_type, params


class SQLAlchemyRenderer(PythonRenderer):
    """SQLAlchemy model code renderer."""
    
    def __init__(self, table_prefix: str = '', base_model_import: str = None):
        self.table_prefix = table_prefix
        self.base_model_import = base_model_import
        
        # Set up Jinja2 environment WITHOUT whitespace control for backward compatibility
        loader = PackageLoader("x007007007.er.renderers.python.sqlalchemy", "templates")
        from jinja2 import Environment, select_autoescape
        self.env = Environment(
            loader=loader,
            autoescape=select_autoescape()
        )
        
        # Register filters
        self.env.filters['sqlalchemy_column_type'] = sqlalchemy_column_type
        self.env.filters['code_value'] = self.serialize_value
        
        self.template = self.env.get_template("sqlalchemy_model.j2")
        self.single_template = self.env.get_template("sqlalchemy_single_model.j2")
    
    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(
            model=model,
            table_prefix=self.table_prefix
        )
    
    def render_multi_file(self, model: ERModel) -> Dict[str, str]:
        """
        Render ERModel as multiple files (one per entity).
        
        Args:
            model: ERModel instance
        
        Returns:
            Dictionary mapping filename to file content
            
        Raises:
            ValueError: If filename conflicts are detected
        """
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        
        files = {}
        filenames_seen = set()
        
        # Generate a file for each entity
        for entity_name, entity in model.entities.items():
            # Convert entity name to snake_case for filename
            filename = to_snake_case(entity_name) + '.py'
            
            # Check for filename conflicts (fail-fast)
            if filename in filenames_seen:
                raise ValueError(
                    f"Filename conflict detected: '{filename}' "
                    f"(entity: {entity_name}). "
                    f"Multiple entities map to the same filename."
                )
            filenames_seen.add(filename)
            
            # Get relationships for this entity
            entity_relationships = [
                rel for rel in model.relationships
                if rel.left_entity == entity_name or rel.right_entity == entity_name
            ]
            
            # Render the entity
            content = self.single_template.render(
                model=model,
                entity=entity,
                entity_relationships=entity_relationships,
                table_prefix=self.table_prefix,
                base_model_import=self.base_model_import
            )
            
            files[filename] = content
        
        # Generate __init__.py
        init_content = self._generate_init_file(model)
        files['__init__.py'] = init_content
        
        return files
    
    def _generate_init_file(self, model: ERModel) -> str:
        """
        Generate __init__.py file that imports all models.
        
        Args:
            model: ERModel instance
        
        Returns:
            Content of __init__.py file
        """
        lines = []
        lines.append('"""Auto-generated SQLAlchemy models."""')
        lines.append('')
        
        # Import all entities
        entity_names = []
        for entity_name in sorted(model.entities.keys()):
            filename = to_snake_case(entity_name)
            lines.append(f'from .{filename} import {entity_name}')
            entity_names.append(entity_name)
        
        lines.append('')
        lines.append('__all__ = [')
        for entity_name in entity_names:
            lines.append(f'    "{entity_name}",')
        lines.append(']')
        lines.append('')
        
        return '\n'.join(lines)
