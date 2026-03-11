"""
Namespace transformation module for converting Django package paths to SQLAlchemy equivalents.

This module provides the NamespaceTransformer class which handles the transformation
of Django package namespaces to SQLAlchemy export paths by appending framework-specific
suffixes to the last component of the package path.
"""

from typing import Optional


class NamespaceTransformer:
    """
    Transforms Django package namespaces to SQLAlchemy equivalents.
    
    The transformer appends a framework-specific suffix (e.g., '_sqlalchemy') to the
    last component of a package path. The transformation is idempotent, meaning applying
    it multiple times produces the same result.
    
    Example:
        >>> transformer = NamespaceTransformer()
        >>> transformer.transform_package_to_export_path("kinkotech.common.models.base")
        'kinkotech.common.models.base_sqlalchemy'
        >>> transformer.transform_package_to_export_path("kinkotech.common.models.base_sqlalchemy")
        'kinkotech.common.models.base_sqlalchemy'
    """
    
    # Framework suffix mapping
    FRAMEWORK_SUFFIXES = {
        'sqlalchemy': '_sqlalchemy',
        'django': '_django',
    }
    
    def transform_package_to_export_path(
        self, 
        package: str, 
        output_framework: str = 'sqlalchemy'
    ) -> str:
        """
        Transform Django package to SQLAlchemy export path.
        
        Appends a framework-specific suffix to the last component of the package path.
        The transformation is idempotent - if the suffix is already present, the package
        is returned unchanged.
        
        Args:
            package: Django package path (e.g., "kinkotech.common.infrastructure.models.base")
            output_framework: Target framework (default: "sqlalchemy")
            
        Returns:
            SQLAlchemy export path (e.g., "kinkotech.common.infrastructure.models.base_sqlalchemy")
            
        Raises:
            ValueError: If package is empty, None, or contains invalid components
            ValueError: If output_framework is not supported
            
        Preconditions:
            - package is non-null and non-empty string
            - package contains valid Python identifiers separated by dots
            - output_framework is a supported framework name
            
        Postconditions:
            - Returns valid Python package path
            - Last component has framework suffix appended
            - Idempotent: f(f(x)) = f(x)
            - Preserves all components except last
        """
        # Validate input
        if not package:
            raise ValueError("Package path cannot be empty or None")
        
        if not isinstance(package, str):
            raise ValueError(f"Package must be a string, got {type(package).__name__}")
        
        # Validate framework
        if output_framework not in self.FRAMEWORK_SUFFIXES:
            raise ValueError(
                f"Unsupported framework: {output_framework}. "
                f"Supported frameworks: {', '.join(self.FRAMEWORK_SUFFIXES.keys())}"
            )
        
        # Get the suffix for the framework
        suffix = self.FRAMEWORK_SUFFIXES[output_framework]
        
        # Split package into components
        components = package.split('.')
        
        # Validate components
        if not components or any(not comp for comp in components):
            raise ValueError(f"Package path contains empty components: {package}")
        
        # Validate that components are valid Python identifiers
        for comp in components:
            if not self._is_valid_identifier(comp):
                raise ValueError(
                    f"Invalid Python identifier in package path: '{comp}' in '{package}'"
                )
        
        # Get the last component
        last_component = components[-1]
        
        # Check if already transformed (idempotence)
        if last_component.endswith(suffix):
            return package
        
        # Apply transformation
        transformed_component = last_component + suffix
        components[-1] = transformed_component
        
        # Reconstruct package path
        export_path = '.'.join(components)
        
        return export_path
    
    def _is_valid_identifier(self, identifier: str) -> bool:
        """
        Check if a string is a valid Python identifier.
        
        Args:
            identifier: String to validate
            
        Returns:
            True if valid Python identifier, False otherwise
        """
        if not identifier:
            return False
        
        # Check if it's a valid Python identifier
        # Must start with letter or underscore, followed by letters, digits, or underscores
        if not identifier.isidentifier():
            return False
        
        # Additional check: should not be a Python keyword
        import keyword
        if keyword.iskeyword(identifier):
            return False
        
        return True
