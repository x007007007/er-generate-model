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


def transform_namespace_for_sqlalchemy(namespace: str) -> str:
    """
    Jinja2 filter to transform Django namespace to SQLAlchemy namespace.
    
    This filter appends '_sqlalchemy' suffix to the last module component
    of the namespace, excluding any class name at the end.
    
    Args:
        namespace: Original namespace (e.g., "kinkotech.common.models.base.MyModel")
        
    Returns:
        Transformed namespace (e.g., "kinkotech.common.models.base_sqlalchemy")
        
    Example:
        {{ "myapp.models.base"|transform_namespace_for_sqlalchemy }}
        # Output: myapp.models.base_sqlalchemy
        
        {{ "myapp.models.base.MyModel"|transform_namespace_for_sqlalchemy }}
        # Output: myapp.models.base_sqlalchemy
    """
    if not namespace:
        return namespace
    
    parts = namespace.split('.')
    
    if not parts:
        return namespace
    
    # Detect if the last part is a class name (PascalCase)
    last_part = parts[-1]
    is_class_name = (
        last_part and 
        last_part[0].isupper() and 
        (len(last_part) == 1 or  # Single letter
         sum(1 for c in last_part[1:] if c.isupper()) > 0 or  # Has more uppercase
         not any(c.islower() for c in last_part))  # All uppercase
    )
    
    # If last part is a class name, transform the second-to-last part
    # Otherwise, transform the last part
    if is_class_name and len(parts) > 1:
        # Transform the module part (second to last)
        parts[-2] = parts[-2] + '_sqlalchemy'
        # Remove the class name from the namespace
        return '.'.join(parts[:-1])
    else:
        # Transform the last part (it's a module)
        parts[-1] = parts[-1] + '_sqlalchemy'
        return '.'.join(parts)


class SQLAlchemyRenderer(PythonRenderer):
    """SQLAlchemy model code renderer."""
    
    def __init__(self, table_prefix: str = '', base_model_import: str = None, inheritance_mode: str = 'reference'):
        self.table_prefix = table_prefix
        self.base_model_import = base_model_import
        self.inheritance_mode = inheritance_mode
        
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
        self.env.filters['transform_namespace_for_sqlalchemy'] = transform_namespace_for_sqlalchemy
        
        self.template = self.env.get_template("sqlalchemy_model.j2")
        self.single_template = self.env.get_template("sqlalchemy_single_model.j2")
        self.mixin_template = self.env.get_template("sqlalchemy_mixin.j2")
    
    def render(self, model: ERModel) -> str:
        assert isinstance(model, ERModel), "Model must be an ERModel instance"
        return self.template.render(
            model=model,
            table_prefix=self.table_prefix,
            inheritance_mode=self.inheritance_mode
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
        
        # In reference mode, generate mixin files for templates without external export_path
        if self.inheritance_mode == 'reference' and model.templates:
            mixin_files = self._generate_mixin_files(model)
            files.update(mixin_files)
        
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
                base_model_import=self.base_model_import,
                inheritance_mode=self.inheritance_mode
            )
            
            files[filename] = content
        
        # Generate __init__.py
        init_content = self._generate_init_file(model)
        files['__init__.py'] = init_content
        
        return files
    
    def _generate_mixin_files(self, model: ERModel) -> Dict[str, str]:
        """
        Generate mixin class files for templates in reference mode.
        
        Templates are generated to directories based on their package attribute:
        - Third-party templates (package with 3+ parts) → third/{package_path}.py
        - Current project templates (auto-generated) → mixins/{module_name}.py
        
        This method also updates the export_path in model.templates to reflect the generated location.
        
        Args:
            model: ERModel instance
        
        Returns:
            Dictionary mapping mixin filename to file content
        """
        mixin_files = {}
        
        for template_name, template_info in model.templates.items():
            export_path = template_info.get('export_path')
            package = template_info.get('package')
            columns = template_info.get('columns', [])
            
            # Skip templates without columns (they're just markers for external classes)
            if not columns:
                continue
            
            # Determine if we should generate this template
            # We generate templates that:
            # 1. Have export_path starting with 'mixins.' (auto-generated by parser)
            # 2. Have export_path pointing to external packages (for stub generation)
            should_generate = False
            is_third_party = False
            
            if export_path:
                if export_path.startswith('mixins.'):
                    # Auto-generated internal mixin
                    should_generate = True
                    is_third_party = False
                elif package:
                    # Check if it's a third-party package (3+ parts)
                    package_parts = package.split('.')
                    if len(package_parts) >= 3:
                        # Third-party template - generate stub in third/ directory
                        should_generate = True
                        is_third_party = True
            
            if not should_generate:
                continue
            
            # Generate filename and update export_path based on package and third-party status
            if is_third_party and package:
                # Third-party templates: third/{package_path}.py
                # Convert package to path: kinkotech.common.infrastructure.models.base -> third/kinkotech/common/infrastructure/models/base.py
                package_path = package.replace('.', '/')
                filename = f'third/{package_path}.py'
                # Update export_path to reflect the generated location
                new_export_path = f'third.{package}'
                template_info['export_path'] = new_export_path
            else:
                # Current project templates: mixins/{module_name}.py
                if export_path and export_path.startswith('mixins.'):
                    # Extract module name from export_path
                    module_name = export_path.split('.', 1)[1]
                else:
                    # Use snake_case template name
                    module_name = to_snake_case(template_name)
                filename = f'mixins/{module_name}.py'
                # export_path is already correct (mixins.{module_name})
            
            # Check if we already have content for this file (multiple templates in same module)
            if filename in mixin_files:
                # Append to existing file
                # Collect column types needed for imports
                column_types = set()
                for col in columns:
                    col_type, _ = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
                    column_types.add(col_type)
                
                # Render just the class definition (without imports)
                class_content = self._render_mixin_class(template_name, columns, sorted(column_types))
                mixin_files[filename] += '\n\n' + class_content
            else:
                # Create new file
                # Collect column types needed for imports
                column_types = set()
                for col in columns:
                    col_type, _ = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
                    column_types.add(col_type)
                
                # Render the full mixin template
                content = self.mixin_template.render(
                    mixin_name=template_name,
                    columns=columns,
                    column_types=sorted(column_types),
                    package=package
                )
                
                mixin_files[filename] = content
        
        return mixin_files
    
    def _render_mixin_class(self, mixin_name: str, columns: list, column_types: list) -> str:
        """
        Render just the class definition for a mixin (without imports).
        
        Args:
            mixin_name: Name of the mixin class
            columns: List of Column objects
            column_types: List of SQLAlchemy column types needed
        
        Returns:
            String containing the class definition
        """
        lines = []
        lines.append(f'class {mixin_name}(Base):')
        lines.append('    __abstract__ = True')
        
        for col in columns:
            col_type, params = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
            col_def = f'    {col.name} = Column({col_type}'
            
            if params:
                col_def += f'({params})'
            
            if not col.nullable:
                col_def += ', nullable=False'
            
            col_def += ')'
            lines.append(col_def)
        
        return '\n'.join(lines)
    
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
