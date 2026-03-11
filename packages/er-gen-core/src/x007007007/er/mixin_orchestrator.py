"""
Mixin orchestrator module for coordinating template discovery and mixin generation.

This module provides the MixinOrchestrator class which coordinates:
- Template discovery across multiple TOML files using TemplateRegistry
- Mixin file generation for all templates using MixinGenerator
- Providing templates to the entity renderer
- Handling inheritance mode selection (reference vs flatten)
"""

from typing import Dict, List
from pathlib import Path

from x007007007.er.models import TemplateInfo
from x007007007.er.template_registry import TemplateRegistry
from x007007007.er.mixin_generator import MixinGenerator


class MixinOrchestrator:
    """
    Orchestrate the complete workflow for template discovery and mixin generation.
    
    The orchestrator coordinates:
    1. Discovers templates from multiple TOML files using TemplateRegistry
    2. Generates mixin files for all templates using MixinGenerator
    3. Provides templates to the entity renderer
    4. Handles inheritance mode selection
    
    Example:
        >>> orchestrator = MixinOrchestrator()
        >>> templates = orchestrator.process_templates(
        ...     toml_files=['models1.toml', 'models2.toml'],
        ...     output_dir='output',
        ...     inheritance_mode='reference'
        ... )
    """
    
    def __init__(self):
        """Initialize the orchestrator with registry and generator."""
        self._registry = TemplateRegistry()
        self._generator = MixinGenerator()
    
    def process_templates(
        self,
        toml_files: List[str],
        output_dir: str,
        inheritance_mode: str = 'reference'
    ) -> Dict[str, TemplateInfo]:
        """
        Process templates from multiple TOML files.
        
        Discovers templates from all TOML files, generates mixin files for each
        template, and returns the template registry for use by entity renderer.
        
        Args:
            toml_files: List of TOML file paths to process
            output_dir: Base output directory for generated mixin files
            inheritance_mode: 'reference' or 'flatten' (default: 'reference')
            
        Returns:
            Dictionary mapping template names to TemplateInfo objects
            
        Raises:
            ValueError: If inheritance_mode is invalid or inputs are invalid
            ConflictError: If duplicate template names are found
            ValidationError: If template configuration is invalid
            FileNotFoundError: If a TOML file doesn't exist
            PermissionError: If output directory is not writable
            
        Preconditions:
            - toml_files is non-null list of valid file paths
            - output_dir is writable directory path
            - inheritance_mode is either 'reference' or 'flatten'
            
        Postconditions:
            - All templates from all files are discovered
            - In reference mode: mixin files are generated for all templates
            - In flatten mode: no mixin files are generated
            - Returns complete template registry
        """
        # Validate inputs
        if not isinstance(toml_files, list):
            raise ValueError("toml_files must be a list")
        
        if not toml_files:
            raise ValueError("toml_files cannot be empty")
        
        if not output_dir:
            raise ValueError("output_dir cannot be empty")
        
        if inheritance_mode not in ('reference', 'flatten'):
            raise ValueError(
                f"inheritance_mode must be 'reference' or 'flatten', "
                f"got '{inheritance_mode}'"
            )
        
        # Step 1: Discover templates from all TOML files
        templates = self._registry.discover_templates(toml_files)
        
        # Step 2: Generate mixin files (only in reference mode)
        if inheritance_mode == 'reference':
            # Validate output directory
            output_path = Path(output_dir)
            if output_path.exists() and not output_path.is_dir():
                raise ValueError(f"output_dir '{output_dir}' exists but is not a directory")
            
            # Create output directory if it doesn't exist
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise PermissionError(
                    f"Cannot create output directory '{output_dir}': {e}"
                ) from e
            
            # Generate mixin file for each template
            for template_name, template_info in templates.items():
                self._generator.generate_mixin_file(
                    template_name,
                    template_info,
                    output_dir
                )
        
        # Step 3: Return templates for use by entity renderer
        return templates
    
    def get_template(self, template_name: str) -> TemplateInfo:
        """
        Get a specific template by name.
        
        Args:
            template_name: Name of template to retrieve
            
        Returns:
            TemplateInfo object for the template
            
        Raises:
            TemplateNotFoundError: If template doesn't exist
            
        Preconditions:
            - template_name is non-empty string
            - process_templates() has been called
            
        Postconditions:
            - Returns valid TemplateInfo if template exists
        """
        template = self._registry.resolve_template(template_name)
        if template is None:
            from x007007007.er.template_registry import TemplateNotFoundError
            raise TemplateNotFoundError(
                f"Template '{template_name}' not found in registry"
            )
        return template
