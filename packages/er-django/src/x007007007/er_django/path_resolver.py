"""Path resolution utilities for Django ER export."""

import os
from pathlib import Path
from typing import Union

from django.apps import AppConfig

from .path_configuration import PathConfiguration


class PathResolver:
    """Resolve file paths for Django apps based on Python package paths."""

    def __init__(self, config: PathConfiguration):
        """Initialize PathResolver with configuration.
        
        Args:
            config: PathConfiguration instance containing path settings
        """
        self.config = config

    def resolve_output_path(
        self,
        app_config: AppConfig,
        format: str,
        is_third_party: bool = False
    ) -> Path:
        """
        Resolve output path for an app's ER export based on namespace.

        The output file is named directly after the app's Python package path
        (namespace), placed flat in the output directory.

        Args:
            app_config: Django AppConfig instance
            format: Output format extension (toml, mermaid, plantuml)
            is_third_party: Unused, kept for interface compatibility

        Returns:
            Path object for output file

        Examples:
            app_config.name = 'kinkotech.common.domains.account'
            format = 'toml'
            → '{output_path}/kinkotech.common.domains.account.toml'
        """
        base_dir = self.config.output_path

        package_path = app_config.name

        if not package_path:
            raise ValueError(
                f"Cannot determine package path for app '{app_config.label}'. "
                f"AppConfig.name is empty."
            )

        output_path = base_dir / f'{package_path}.{format}'

        return output_path

    def resolve_package_name(
        self,
        app_config: AppConfig,
        is_third_party: bool = False
    ) -> str:
        """
        Resolve the package name for an app.
        
        For third-party packages, adds the configured prefix to the package name.
        For regular packages, returns the package name as-is.
        
        Args:
            app_config: Django AppConfig instance
            is_third_party: Whether this is a third-party package (default: False)
            
        Returns:
            Complete package name (with prefix for third-party packages)
            
        Examples:
            app_config.name = 'django.contrib.auth'
            is_third_party = True
            config.third_party_package_prefix = 'third'
            → 'third.django.contrib.auth'
            
            app_config.name = 'myapp'
            is_third_party = False
            → 'myapp'
        """
        base_package = app_config.name
        
        if not base_package:
            raise ValueError(
                f"Cannot determine package path for app '{app_config.label}'. "
                f"AppConfig.name is empty."
            )
        
        if is_third_party and self.config.third_party_package_prefix:
            return f"{self.config.third_party_package_prefix}.{base_package}"
        
        return base_package

    def get_scan_path(self) -> Path:
        """
        Get the scan path from configuration.
        
        Returns:
            Path object for the scan directory
        """
        return self.config.scan_path

    @staticmethod
    def get_package_path(app_config: AppConfig) -> str:
        """
        Get the Python package path for an app's models.

        Args:
            app_config: Django AppConfig instance

        Returns:
            Package path string (e.g., 'kinkotech.common.domains.account.models')

        Raises:
            ValueError: If package path cannot be determined
        """
        # Use app_config.name as the base package
        # e.g., 'kinkotech.common.domains.account'
        base_package = app_config.name
        
        if not base_package:
            raise ValueError(
                f"Cannot determine package path for app '{app_config.label}'. "
                f"AppConfig.name is empty."
            )
        
        # Always append .models to the base package
        # This works for both models.py and models/__init__.py structures
        return f"{base_package}.models"
