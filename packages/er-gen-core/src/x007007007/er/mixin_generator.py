"""
Mixin generator module for creating SQLAlchemy mixin class files from templates.

This module provides the MixinGenerator class which handles:
- Converting export_path to file path (dots to slashes)
- Converting class name to snake_case for filename
- Creating directory structure
- Generating Python code with SQLAlchemy columns
- Marking class as abstract with __abstract__ = True
"""

from pathlib import Path
from typing import Dict
from jinja2 import Environment, PackageLoader, select_autoescape

from x007007007.er.models import TemplateInfo
from x007007007.er.renderers.python.utils import to_snake_case
from x007007007.er.type_mapper import TypeMapper


def sqlalchemy_column_type(col):
    """Jinja2 filter for SQLAlchemy column type."""
    column_type, params = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
    return column_type, params


class MixinGenerator:
    """
    Generate SQLAlchemy mixin class files from templates.
    
    The generator converts export_path to file path, converts class name to snake_case
    for filename, creates directory structure, and generates Python code with SQLAlchemy
    columns marked as abstract.
    
    Example:
        >>> generator = MixinGenerator()
        >>> file_path = generator.generate_mixin_file(
        ...     'KinkoTechModelBase',
        ...     template_info,
        ...     'output'
        ... )
    """
    
    def __init__(self):
        """Initialize the mixin generator with Jinja2 environment."""
        # Set up Jinja2 environment
        loader = PackageLoader("x007007007.er.renderers.python.sqlalchemy", "templates")
        self.env = Environment(
            loader=loader,
            autoescape=select_autoescape()
        )
        
        # Register filters
        self.env.filters['sqlalchemy_column_type'] = sqlalchemy_column_type
        self.env.filters['code_value'] = self._serialize_value
        
        # Load mixin template
        self.mixin_template = self.env.get_template("sqlalchemy_mixin.j2")
    
    def generate_mixin_file(
        self,
        template_name: str,
        template_info: TemplateInfo,
        output_dir: str
    ) -> str:
        """
        Generate mixin class file from template.
        
        Converts export_path to file path (dots to slashes), converts class name to
        snake_case for filename, creates directory structure, and generates Python
        code with SQLAlchemy columns marked as abstract.
        
        Args:
            template_name: Name of the template (used as class name)
            template_info: Template information including columns and export_path
            output_dir: Base output directory
            
        Returns:
            Path to generated mixin file (as string)
            
        Raises:
            ValueError: If template_info is invalid or output_dir is not writable
            PermissionError: If output directory is not writable
            
        Preconditions:
            - template_name is non-empty string
            - template_info.export_path is set (auto-derived or explicit)
            - template_info.columns is non-empty
            - output_dir is writable directory
            
        Postconditions:
            - Mixin file created at correct path
            - File contains valid SQLAlchemy mixin class
            - Class marked as __abstract__ = True
            - All columns properly defined
            - Directory structure created if needed
        """
        # Validate inputs
        if not template_name:
            raise ValueError("template_name cannot be empty")
        
        if not template_info.export_path:
            raise ValueError(
                f"Template '{template_name}' must have export_path set"
            )
        
        if not template_info.columns:
            raise ValueError(
                f"Template '{template_name}' has empty columns list"
            )
        
        # Step 1: Convert export_path to file path
        # e.g., "kinkotech.common.models.base_sqlalchemy" -> "kinkotech/common/models/base_sqlalchemy"
        package_path = template_info.export_path.replace('.', '/')
        
        # Step 2: Create file name from class name
        # e.g., "KinkoTechModelBase" -> "kinkotech_model_base.py"
        file_name = to_snake_case(template_name) + '.py'
        
        # Step 3: Construct full file path
        output_path = Path(output_dir)
        full_dir_path = output_path / package_path
        file_path = full_dir_path / file_name
        
        # Step 4: Create directory structure
        try:
            full_dir_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(
                f"Cannot create directory '{full_dir_path}': {e}"
            ) from e
        
        # Step 5: Collect column types needed for imports
        column_types = set()
        for col in template_info.columns:
            col_type, _ = TypeMapper.get_sqlalchemy_type(col.type, col.max_length)
            # Extract base type name (e.g., "String(255)" -> "String")
            base_type = col_type.split('(')[0] if '(' in col_type else col_type
            column_types.add(base_type)
        
        # Step 6: Generate Python code
        content = self.mixin_template.render(
            mixin_name=template_name,
            columns=template_info.columns,
            column_types=sorted(column_types),
            package=template_info.package
        )
        
        # Step 7: Write file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError as e:
            raise PermissionError(
                f"Cannot write to file '{file_path}': {e}"
            ) from e
        except OSError as e:
            raise OSError(
                f"Failed to write file '{file_path}': {e}"
            ) from e
        
        return str(file_path)
    
    def _serialize_value(self, value):
        """
        Serialize a Python value to its code representation.
        
        Args:
            value: Value to serialize
            
        Returns:
            String representation of the value for Python code
        """
        if value is None:
            return 'None'
        elif isinstance(value, bool):
            return 'True' if value else 'False'
        elif isinstance(value, str):
            # Escape quotes and return as string literal
            escaped = value.replace('\\', '\\\\').replace("'", "\\'")
            return f"'{escaped}'"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            # For other types, use repr
            return repr(value)
