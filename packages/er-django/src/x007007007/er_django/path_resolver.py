"""Path resolution utilities for Django ER export."""

import os
from pathlib import Path
from typing import Union

from django.apps import AppConfig


class PathResolver:
    """Resolve file paths for Django apps based on Python package paths."""

    @staticmethod
    def resolve_output_path(
        app_config: AppConfig,
        base_dir: Union[str, Path],
        format: str
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
            base_dir: Base output directory (default: './src')
            format: Output format extension (toml, mermaid, plantuml)

        Returns:
            Path object for output file

        Raises:
            ValueError: If app package path cannot be determined
            
        Examples:
            app_config.name = 'kinkotech.common.domains.account'
            base_dir = './src'
            format = 'toml'
            → './src/kinkotech/common/domains/account/models.toml'
            
            app_config.name = 'django.contrib.auth'
            base_dir = './output'
            format = 'toml'
            → './output/django/contrib/auth/models.toml'
            
            app_config.name = 'myapp'
            base_dir = './src'
            format = 'toml'
            → './src/myapp/models.toml'
        """
        # Convert base_dir to Path object
        base_dir = Path(base_dir)
        
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
