"""App discovery utilities for Django ER export."""

from pathlib import Path
from typing import List

from django.apps import apps


class AppDiscoveryService:
    """Discover Django apps with TOML files."""

    @staticmethod
    def discover_apps_with_toml() -> List[str]:
        """
        Discover all Django apps that have models.toml files.

        This method scans all installed Django apps and checks for the presence
        of models.toml files in two possible locations:
        1. {app_path}/models.toml
        2. {app_path}/models/models.toml

        Returns:
            List of app labels (strings) that have models.toml files

        Example:
            >>> apps_with_toml = AppDiscoveryService.discover_apps_with_toml()
            >>> print(apps_with_toml)
            ['account', 'profile', 'blog']
        """
        apps_with_toml = []

        for app_config in apps.get_app_configs():
            app_path = Path(app_config.path)

            # Check possible TOML file locations
            toml_locations = [
                app_path / 'models.toml',
                app_path / 'models' / 'models.toml',
            ]

            for toml_path in toml_locations:
                if toml_path.exists():
                    apps_with_toml.append(app_config.label)
                    break  # Found TOML file, no need to check other locations

        return apps_with_toml

    @staticmethod
    def get_toml_path(app_label: str) -> Path:
        """
        Get the TOML file path for a specific app.

        Args:
            app_label: Django app label

        Returns:
            Path to models.toml file

        Raises:
            FileNotFoundError: If TOML file not found for the specified app

        Example:
            >>> toml_path = AppDiscoveryService.get_toml_path('account')
            >>> print(toml_path)
            /path/to/account/models.toml
        """
        app_config = apps.get_app_config(app_label)
        app_path = Path(app_config.path)

        # Check possible TOML file locations
        toml_locations = [
            app_path / 'models.toml',
            app_path / 'models' / 'models.toml',
        ]

        for toml_path in toml_locations:
            if toml_path.exists():
                return toml_path

        # TOML file not found - fail fast
        raise FileNotFoundError(
            f"models.toml not found for app '{app_label}'\n"
            f"Expected locations:\n"
            f"  - {toml_locations[0]}\n"
            f"  - {toml_locations[1]}\n"
            f"Suggestion: Run 'python manage.py er_export {app_label}' first to generate TOML files"
        )
