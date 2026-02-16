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
        Resolve output path for an app's ER export based ONLY on Python package path.
        
        This method determines where to write the ER export file based EXCLUSIVELY on the app's
        Python package path (app_config.name), completely independent of file system location.
        
        The output path is constructed by:
        1. Taking the app's Python package name (e.g., 'kinkotech.common.domains.account')
        2. Converting dots to directory separators (e.g., 'kinkotech/common/domains/account')
        3. Appending 'models.{format}' to create the full path
        
        This ensures predictable, consistent output paths regardless of where the app
        is physically located on the file system.

        Args:
            app_config: Django AppConfig instance
            format: Output format extension (toml, mermaid, plantuml)
            is_third_party: Whether this is a third-party package (default: False)

        Returns:
            Path object for output file

        Raises:
            ValueError: If app package path cannot be determined
            
        Examples:
            app_config.name = 'kinkotech.common.domains.account'
            format = 'toml'
            is_third_party = False
            → '{output_path}/kinkotech/common/domains/account/models.toml'
            
            app_config.name = 'django.contrib.auth'
            format = 'toml'
            is_third_party = True
            → '{third_party_output_path}/django/contrib/auth/models.toml'
        """
        # Select base directory based on whether it's a third-party package
        base_dir = (
            self.config.third_party_output_path 
            if is_third_party 
            else self.config.output_path
        )
        
        # Get app's Python package path
        package_path = app_config.name
        
        if not package_path:
            raise ValueError(
                f"Cannot determine package path for app '{app_config.label}'. "
                f"AppConfig.name is empty."
            )
        
        # Convert package path to directory structure
        # e.g., 'kinkotech.common.domains.account' → 'kinkotech/common/domains/account'
        relative_path = Path(package_path.replace('.', os.sep))
        
        # Construct output path based ONLY on package path
        output_path = base_dir / relative_path / f'models.{format}'
        
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
