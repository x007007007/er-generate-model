"""
Template registry module for discovering and managing templates across multiple TOML files.

This module provides the TemplateRegistry class which handles:
- Discovery of templates from multiple TOML files
- Auto-derivation of export_path from package using NamespaceTransformer
- Template resolution by name across all loaded files
- Detection and reporting of duplicate template names
"""

import toml
from typing import Dict, List, Optional
from pathlib import Path

from x007007007.er.models import TemplateInfo, Column
from x007007007.er.namespace import NamespaceTransformer


class ConflictError(Exception):
    """Raised when duplicate template names are detected across TOML files."""
    pass


class TemplateNotFoundError(Exception):
    """Raised when a referenced template cannot be found in the registry."""
    pass


class ValidationError(Exception):
    """Raised when template configuration is invalid."""
    pass


class TemplateRegistry:
    """
    Discovers and manages templates across multiple TOML files.
    
    The registry scans multiple TOML files for template definitions, auto-derives
    export_path from package using NamespaceTransformer when not explicitly specified,
    builds a unified template registry, and provides template lookup by name.
    
    Example:
        >>> registry = TemplateRegistry()
        >>> templates = registry.discover_templates(['models1.toml', 'models2.toml'])
        >>> template = registry.resolve_template('KinkoTechModelBase')
    """
    
    def __init__(self):
        """Initialize the template registry."""
        self._templates: Dict[str, TemplateInfo] = {}
        self._namespace_transformer = NamespaceTransformer()
    
    def discover_templates(self, toml_files: List[str]) -> Dict[str, TemplateInfo]:
        """
        Discover templates from multiple TOML files.
        
        Scans all provided TOML files for template definitions, auto-derives export_path
        from package when not explicitly specified, and builds a unified registry.
        
        Args:
            toml_files: List of TOML file paths to scan
            
        Returns:
            Dictionary mapping template names to TemplateInfo objects
            
        Raises:
            ConflictError: If duplicate template names are found across files
            ValidationError: If template configuration is invalid
            FileNotFoundError: If a TOML file doesn't exist
            toml.TomlDecodeError: If a TOML file is malformed
            
        Preconditions:
            - toml_files is non-null list
            - All files in toml_files exist and are readable
            - TOML files are well-formed
            
        Postconditions:
            - All templates from all files are discovered
            - Each template has valid export_path (auto-derived or explicit)
            - No duplicate template names
            - All templates have parsed columns
        """
        if not isinstance(toml_files, list):
            raise ValueError("toml_files must be a list")
        
        self._templates = {}
        
        for file_path in toml_files:
            # Validate file exists
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"TOML file not found: {file_path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            # Parse TOML file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = toml.load(f)
            except toml.TomlDecodeError as e:
                # Re-raise with additional context in the message
                raise
            
            # Extract templates section
            templates_section = data.get('templates', {})
            if not isinstance(templates_section, dict):
                raise ValidationError(
                    f"'templates' section in '{file_path}' must be a dictionary"
                )
            
            # Process each template
            for template_name, template_data in templates_section.items():
                # Check for conflicts
                if template_name in self._templates:
                    existing_template = self._templates[template_name]
                    raise ConflictError(
                        f"Duplicate template name '{template_name}' found in files: "
                        f"'{existing_template.source_file}' and '{file_path}'"
                    )
                
                # Validate template data
                if not isinstance(template_data, dict):
                    raise ValidationError(
                        f"Template '{template_name}' in '{file_path}' must be a dictionary"
                    )
                
                # Extract package and export_path
                package = template_data.get('package')
                export_path = template_data.get('export_path')
                
                # Validate that at least one is specified
                if not package and not export_path:
                    raise ValidationError(
                        f"Template '{template_name}' in '{file_path}' must have either "
                        f"'package' or 'export_path' field"
                    )
                
                # Auto-derive export_path if only package specified
                if package and not export_path:
                    try:
                        export_path = self._namespace_transformer.transform_package_to_export_path(
                            package, 'sqlalchemy'
                        )
                    except ValueError as e:
                        raise ValidationError(
                            f"Failed to transform package '{package}' for template "
                            f"'{template_name}' in '{file_path}': {e}"
                        ) from e
                
                # Validate export_path
                if export_path:
                    self._validate_export_path(export_path, template_name, file_path)
                
                # Parse columns
                columns_data = template_data.get('columns', [])
                if not isinstance(columns_data, list):
                    raise ValidationError(
                        f"Template '{template_name}.columns' in '{file_path}' must be a list"
                    )
                
                if not columns_data:
                    raise ValidationError(
                        f"Template '{template_name}' in '{file_path}' has empty columns list"
                    )
                
                columns = self._parse_columns(columns_data, template_name, file_path)
                
                # Validate template name is valid Python identifier
                if not template_name.isidentifier():
                    raise ValidationError(
                        f"Template name '{template_name}' in '{file_path}' is not a "
                        f"valid Python identifier"
                    )
                
                # Create TemplateInfo
                template_info = TemplateInfo(
                    name=template_name,
                    package=package,
                    export_path=export_path,
                    columns=columns,
                    source_file=str(path.absolute())
                )
                
                self._templates[template_name] = template_info
        
        return self._templates
    
    def resolve_template(self, template_name: str) -> Optional[TemplateInfo]:
        """
        Resolve template by name across all loaded TOML files.
        
        Args:
            template_name: Name of template to resolve
            
        Returns:
            TemplateInfo if found, None otherwise
            
        Preconditions:
            - template_name is non-empty string
            
        Postconditions:
            - Returns TemplateInfo if template exists in registry
            - Returns None if template doesn't exist
        """
        if not isinstance(template_name, str):
            raise ValueError("template_name must be a string")
        
        if not template_name:
            raise ValueError("template_name cannot be empty")
        
        return self._templates.get(template_name)
    
    def _validate_export_path(self, export_path: str, template_name: str, file_path: str) -> None:
        """
        Validate that export_path is a valid Python package path.
        
        Args:
            export_path: Export path to validate
            template_name: Name of template (for error messages)
            file_path: Source file path (for error messages)
            
        Raises:
            ValidationError: If export_path is invalid
        """
        if not export_path:
            raise ValidationError(
                f"Template '{template_name}' in '{file_path}' has empty export_path"
            )
        
        # Split into components and validate each
        components = export_path.split('.')
        for component in components:
            if not component:
                raise ValidationError(
                    f"Template '{template_name}' in '{file_path}' has invalid export_path "
                    f"'{export_path}': contains empty component"
                )
            
            if not component.isidentifier():
                raise ValidationError(
                    f"Template '{template_name}' in '{file_path}' has invalid export_path "
                    f"'{export_path}': component '{component}' is not a valid Python identifier"
                )
    
    def _parse_columns(
        self, 
        columns_data: List[dict], 
        template_name: str, 
        file_path: str
    ) -> List[Column]:
        """
        Parse column definitions from template data.
        
        Args:
            columns_data: List of column dictionaries
            template_name: Name of template (for error messages)
            file_path: Source file path (for error messages)
            
        Returns:
            List of Column objects
            
        Raises:
            ValidationError: If column data is invalid
        """
        columns = []
        
        for i, col_data in enumerate(columns_data):
            if not isinstance(col_data, dict):
                raise ValidationError(
                    f"Column {i} in template '{template_name}' in '{file_path}' must be a dictionary"
                )
            
            # Validate required fields
            if 'name' not in col_data:
                raise ValidationError(
                    f"Column {i} in template '{template_name}' in '{file_path}' "
                    f"must have 'name' field"
                )
            
            if 'type' not in col_data:
                raise ValidationError(
                    f"Column {i} in template '{template_name}' in '{file_path}' "
                    f"must have 'type' field"
                )
            
            # Get db_column (use name as default for backward compatibility)
            db_column = col_data.get('db_column', col_data['name'])
            
            # Create Column object
            column = Column(
                name=str(col_data['name']),
                type=str(col_data['type']),
                db_column=str(db_column),
                is_pk=col_data.get('primary_key', col_data.get('is_pk', False)),
                is_fk=col_data.get('is_fk', False),
                nullable=col_data.get('nullable', True),
                comment=col_data.get('comment'),
                default=col_data.get('default'),
                max_length=col_data.get('max_length'),
                precision=col_data.get('precision'),
                scale=col_data.get('scale'),
                unique=col_data.get('unique', False),
                indexed=col_data.get('indexed', False)
            )
            
            columns.append(column)
        
        return columns
