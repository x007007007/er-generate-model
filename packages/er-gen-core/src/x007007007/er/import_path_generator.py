"""
Import Path Generator for namespace-driven model export/import system.

This module provides the ImportPathGenerator class which generates Python import
statements based on model location type (project vs third-party).
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ImportSpec:
    """Import statement specification."""
    
    namespace: str
    """Model's namespace"""
    
    model_name: str
    """Model class name"""
    
    location_type: str
    """Location type: 'project' or 'third-party'"""
    
    alias: Optional[str] = None
    """Optional alias"""


class ImportPathGenerator:
    """
    Generate Python import statements based on model location.
    
    This class generates correct import statements for models based on whether
    they are project models or third-party models. Project models use direct
    namespace imports, while third-party models are prefixed with the configured
    third-party directory.
    
    It also supports framework-specific namespace transformations. For example,
    when generating SQLAlchemy imports from Django namespaces, it can append
    '_sqlalchemy' suffix to the module path.
    
    Examples:
        >>> generator = ImportPathGenerator(third_party_dir="third")
        >>> generator.generate("myapp.models.base", "project", "BaseModel")
        'from myapp.models.base import BaseModel'
        
        >>> generator.generate("django.contrib.auth.models", "third-party", "AbstractUser")
        'from third.django.contrib.auth.models import AbstractUser'
        
        >>> generator = ImportPathGenerator(target_framework="sqlalchemy")
        >>> generator.generate("myapp.models.base", "project", "BaseModel")
        'from myapp.models.base_sqlalchemy import BaseModel'
    """
    
    def __init__(self, third_party_dir: str = "third", target_framework: Optional[str] = None):
        """
        Initialize the import path generator.
        
        Args:
            third_party_dir: Third-party directory name, defaults to "third"
            target_framework: Target framework for namespace transformation.
                            Supported values: "sqlalchemy", None (no transformation)
        """
        self.third_party_dir = third_party_dir
        self.target_framework = target_framework
    
    def _transform_namespace(self, namespace: str) -> str:
        """
        Transform namespace based on target framework.
        
        This method applies framework-specific transformations to the namespace.
        For example, when target_framework is "sqlalchemy", it appends "_sqlalchemy"
        suffix to the last component of the module path.
        
        The method intelligently detects if the namespace includes a class name
        (PascalCase identifier) and only transforms the module path portion.
        
        Args:
            namespace: Original namespace (e.g., "kinkotech.common.models.base")
            
        Returns:
            Transformed namespace (e.g., "kinkotech.common.models.base_sqlalchemy")
            
        Example:
            >>> generator = ImportPathGenerator(target_framework="sqlalchemy")
            >>> generator._transform_namespace("myapp.models.base")
            'myapp.models.base_sqlalchemy'
            
            >>> generator._transform_namespace("myapp.models.base.MyModel")
            'myapp.models.base_sqlalchemy'
        """
        if not self.target_framework:
            return namespace
        
        if self.target_framework == "sqlalchemy":
            # Split namespace to separate module path from class name (if present)
            parts = namespace.split('.')
            
            if not parts:
                return namespace
            
            # Detect if the last part is a class name (PascalCase)
            # A class name typically:
            # 1. Starts with an uppercase letter
            # 2. Contains at least one more uppercase letter (PascalCase pattern)
            # 3. Or is a single uppercase word
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
        
        return namespace
    
    def generate(self, namespace: str, location_type: str, model_name: str) -> str:
        """
        Generate import statement.
        
        Args:
            namespace: Model's namespace (will be transformed based on target_framework)
            location_type: Location type, "project" or "third-party"
            model_name: Model class name
            
        Returns:
            Complete import statement string
            
        Example:
            generate("kinkotech.common.models.base", "project", "BaseModel")
            # Returns: "from kinkotech.common.models.base import BaseModel"
            # Or with target_framework="sqlalchemy":
            # Returns: "from kinkotech.common.models.base_sqlalchemy import BaseModel"
            
            generate("django.contrib.auth.models", "third-party", "AbstractUser")
            # Returns: "from third.django.contrib.auth.models import AbstractUser"
            # Or with target_framework="sqlalchemy":
            # Returns: "from third.django.contrib.auth.models_sqlalchemy import AbstractUser"
        """
        # Apply framework-specific transformation
        transformed_namespace = self._transform_namespace(namespace)
        
        if location_type == "project":
            return f"from {transformed_namespace} import {model_name}"
        elif location_type == "third-party":
            return f"from {self.third_party_dir}.{transformed_namespace} import {model_name}"
        else:
            raise ValueError(f"Invalid location_type: {location_type}. Must be 'project' or 'third-party'")
    
    def generate_batch(self, imports: List[ImportSpec]) -> List[str]:
        """
        Batch generate import statements.
        
        Args:
            imports: List of ImportSpec objects
            
        Returns:
            List of import statements
        """
        return [
            self.generate(spec.namespace, spec.location_type, spec.model_name)
            for spec in imports
        ]
