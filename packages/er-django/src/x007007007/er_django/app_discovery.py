"""App discovery utilities for Django ER export."""

from pathlib import Path
from typing import List, Optional

from django.apps import apps


class AppDiscoveryService:
    """Discover Django apps with TOML files."""

    @staticmethod
    def discover_apps_with_toml(toml_search_dir: Optional[Path] = None) -> List[str]:
        """
        Discover all Django apps that have models.toml files.

        This method scans all installed Django apps and checks for the presence
        of models.toml files. If toml_search_dir is provided, it searches for
        TOML files in that directory instead of the app's installation directory.

        Args:
            toml_search_dir: Optional directory to search for TOML files.
                           If provided, searches for models.toml relative to this directory.
                           If None, searches in the app's installation directory.

        Returns:
            List of app labels (strings) that have models.toml files

        Example:
            >>> # Search in app directories
            >>> apps_with_toml = AppDiscoveryService.discover_apps_with_toml()
            >>> print(apps_with_toml)
            ['account', 'profile', 'blog']
            
            >>> # Search in custom directory (e.g., src/)
            >>> apps_with_toml = AppDiscoveryService.discover_apps_with_toml(Path('src'))
            >>> print(apps_with_toml)
            ['account', 'profile', 'blog', 'constance', 'django_celery_beat']
        """
        apps_with_toml = []

        for app_config in apps.get_app_configs():
            if toml_search_dir:
                # Search in custom directory
                # Try to find TOML file by converting app path to relative path under toml_search_dir
                app_path = Path(app_config.path)
                
                # Strategy 1: Use app's full package name (e.g., kinkotech/common/domains/account)
                app_package_path = app_config.name.replace('.', '/')
                toml_path = toml_search_dir / app_package_path / 'models.toml'
                
                if toml_path.exists():
                    apps_with_toml.append(app_config.label)
                    continue
                
                # Strategy 2: Check in third/ subdirectory for third-party packages
                # (e.g., src/third/django/contrib/auth/models.toml)
                toml_path = toml_search_dir / 'third' / app_package_path / 'models.toml'
                
                if toml_path.exists():
                    apps_with_toml.append(app_config.label)
                    continue
                
                # Strategy 3: Use just the last part of package name (e.g., constance)
                app_name = app_config.name.split('.')[-1]
                toml_path = toml_search_dir / app_name / 'models.toml'
                
                if toml_path.exists():
                    apps_with_toml.append(app_config.label)
                    continue
                
                # Strategy 4: Check in third/ subdirectory with just app name
                toml_path = toml_search_dir / 'third' / app_name / 'models.toml'
                
                if toml_path.exists():
                    apps_with_toml.append(app_config.label)
            else:
                # Search in app's installation directory
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
    def get_toml_path(app_label: str, toml_search_dir: Optional[Path] = None) -> Path:
        """
        Get the TOML file path for a specific app.

        Args:
            app_label: Django app label
            toml_search_dir: Optional directory to search for TOML files.
                           If provided, searches for models.toml relative to this directory.
                           If None, searches in the app's installation directory.

        Returns:
            Path to models.toml file

        Raises:
            FileNotFoundError: If TOML file not found for the specified app

        Example:
            >>> # Search in app directory
            >>> toml_path = AppDiscoveryService.get_toml_path('account')
            >>> print(toml_path)
            /path/to/account/models.toml
            
            >>> # Search in custom directory
            >>> toml_path = AppDiscoveryService.get_toml_path('constance', Path('src'))
            >>> print(toml_path)
            /path/to/src/constance/models.toml
        """
        app_config = apps.get_app_config(app_label)
        
        if toml_search_dir:
            # Search in custom directory
            # Strategy 1: Use app's full package name (e.g., kinkotech/common/domains/account)
            app_package_path = app_config.name.replace('.', '/')
            toml_path = toml_search_dir / app_package_path / 'models.toml'
            
            if toml_path.exists():
                return toml_path
            
            # Strategy 2: Check in third/ subdirectory for third-party packages
            # (e.g., src/third/django/contrib/auth/models.toml)
            toml_path = toml_search_dir / 'third' / app_package_path / 'models.toml'
            
            if toml_path.exists():
                return toml_path
            
            # Strategy 3: Use just the last part of package name (e.g., constance)
            app_name = app_config.name.split('.')[-1]
            toml_path = toml_search_dir / app_name / 'models.toml'
            
            if toml_path.exists():
                return toml_path
            
            # Strategy 4: Check in third/ subdirectory with just app name
            toml_path = toml_search_dir / 'third' / app_name / 'models.toml'
            
            if toml_path.exists():
                return toml_path
            
            # TOML file not found - fail fast
            raise FileNotFoundError(
                f"models.toml not found for app '{app_label}' in custom search directory\n"
                f"Tried locations:\n"
                f"  - {toml_search_dir / app_package_path / 'models.toml'}\n"
                f"  - {toml_search_dir / 'third' / app_package_path / 'models.toml'}\n"
                f"  - {toml_search_dir / app_name / 'models.toml'}\n"
                f"  - {toml_search_dir / 'third' / app_name / 'models.toml'}\n"
                f"Suggestion: Check that the TOML file exists in the specified search directory"
            )
        else:
            # Search in app's installation directory
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
