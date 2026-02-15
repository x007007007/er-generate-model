"""
Django management command: er_convert

Convert TOML ER models to target framework code (Django or SQLAlchemy).
"""
import os
from pathlib import Path
from typing import List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from x007007007.er_django.app_discovery import AppDiscoveryService


class Command(BaseCommand):
    help = 'Convert TOML ER models to target framework code (Django or SQLAlchemy)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'apps',
            nargs='*',
            help='Django app labels to convert (if not specified, auto-discover all apps with models.toml)'
        )
        
        parser.add_argument(
            '--framework',
            type=str,
            choices=['django', 'sqlalchemy'],
            default='django',
            help='Target framework for code generation (default: django)'
        )
        
        parser.add_argument(
            '--output-subdir',
            type=str,
            default=None,
            help='Custom output subdirectory name (default: "models" for Django, "sqlalchemy" for SQLAlchemy)'
        )
        
        parser.add_argument(
            '--base-model-import',
            type=str,
            default=None,
            help='Custom BaseModel import path for SQLAlchemy (e.g., "myproject.database.Base")'
        )
    
    def handle(self, *args, **options):
        apps_to_convert = options.get('apps', [])
        framework = options.get('framework')
        output_subdir = options.get('output_subdir')
        base_model_import = options.get('base_model_import')
        
        # Auto-discover or validate apps
        if not apps_to_convert:
            # Auto-discover all apps with models.toml
            apps_to_convert = AppDiscoveryService.discover_apps_with_toml()
            
            if not apps_to_convert:
                raise CommandError("No apps with models.toml found")
            
            self.stdout.write(f"Auto-discovered {len(apps_to_convert)} apps with models.toml:")
            for app_label in apps_to_convert:
                self.stdout.write(f"  - {app_label}")
        else:
            # Print message before validation
            self.stdout.write(f"Converting specified apps: {', '.join(apps_to_convert)}")
            # Validate specified apps (fail-fast)
            self._validate_apps(apps_to_convert)
        
        # Convert each app (fail-fast)
        converted_count = 0
        total_files = 0
        
        for app_label in apps_to_convert:
            try:
                files_generated = self._convert_app(
                    app_label=app_label,
                    framework=framework,
                    output_subdir=output_subdir,
                    base_model_import=base_model_import
                )
                converted_count += 1
                total_files += files_generated
                
            except Exception as e:
                raise CommandError(f"Failed to convert app '{app_label}': {e}")
        
        # Output summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully converted {converted_count} apps to {framework}"
            )
        )
        self.stdout.write(f"Total files generated: {total_files}")
    
    def _validate_apps(self, app_labels: List[str]) -> None:
        """
        Validate that specified apps exist and have models.toml files.
        
        This method performs fail-fast validation:
        1. Checks that each app exists in Django's installed apps
        2. Checks that each app has a models.toml file
        
        Args:
            app_labels: List of app labels to validate
        
        Raises:
            CommandError: If any app doesn't exist or doesn't have models.toml
        
        Requirements: 4.9, 8.2, 8.6
        """
        for app_label in app_labels:
            # Validate app exists
            try:
                apps.get_app_config(app_label)
            except LookupError:
                raise CommandError(
                    f"App '{app_label}' not found\n"
                    f"Suggestion: Check that '{app_label}' is in INSTALLED_APPS"
                )
            
            # Validate app has models.toml file
            try:
                AppDiscoveryService.get_toml_path(app_label)
            except FileNotFoundError as e:
                raise CommandError(str(e))
    
    def _convert_app(
        self,
        app_label: str,
        framework: str,
        output_subdir: Optional[str],
        base_model_import: Optional[str]
    ) -> int:
        """
        Convert a single app's TOML file to target framework code.
        
        This method implements the core conversion logic:
        1. Gets the TOML file path for the app
        2. Reads and parses the TOML file
        3. Determines the output directory based on framework and output-subdir
        4. Calls the appropriate code generator to generate target framework code
        5. Handles errors with fail-fast strategy
        
        Args:
            app_label: Django app label
            framework: Target framework ('django' or 'sqlalchemy')
            output_subdir: Custom output subdirectory name
            base_model_import: Custom BaseModel import path for SQLAlchemy
        
        Returns:
            Number of files generated
        
        Raises:
            CommandError: If conversion fails (fail-fast)
        
        Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.8
        """
        self.stdout.write(f"\nConverting app '{app_label}' to {framework}...")
        
        # Get TOML file path (fail-fast if not found)
        try:
            toml_path = AppDiscoveryService.get_toml_path(app_label)
        except FileNotFoundError as e:
            raise CommandError(str(e))
        
        self.stdout.write(f"  Reading TOML from: {toml_path}")
        
        # Read and parse TOML file (fail-fast on format errors)
        try:
            import toml
            with open(toml_path, 'r', encoding='utf-8') as f:
                toml_content = f.read()
        except Exception as e:
            raise CommandError(f"Failed to read TOML file {toml_path}: {e}")
        
        # Parse TOML content into ERModel
        try:
            from x007007007.er.parser.toml_parser import TomlERParser
            parser = TomlERParser()
            er_model = parser.parse(toml_content)
        except Exception as e:
            raise CommandError(f"Failed to parse TOML file {toml_path}: {e}")
        
        # Determine output directory
        app_config = apps.get_app_config(app_label)
        app_path = Path(app_config.path)
        
        # Use custom subdir if specified, otherwise use framework-specific default
        if output_subdir:
            subdir_name = output_subdir
        else:
            subdir_name = 'models' if framework == 'django' else 'sqlalchemy'
        
        output_dir = app_path / subdir_name
        
        self.stdout.write(f"  Output directory: {output_dir}")
        
        # Create output directory (fail-fast on error)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise CommandError(f"Failed to create output directory {output_dir}: {e}")
        
        # Generate code based on target framework
        try:
            if framework == 'django':
                files_generated = self._generate_django_code(
                    er_model=er_model,
                    output_dir=output_dir,
                    app_label=app_label
                )
            elif framework == 'sqlalchemy':
                files_generated = self._generate_sqlalchemy_code(
                    er_model=er_model,
                    output_dir=output_dir,
                    base_model_import=base_model_import
                )
            else:
                raise CommandError(f"Unsupported framework: {framework}")
        except Exception as e:
            raise CommandError(f"Failed to generate {framework} code: {e}")
        
        self.stdout.write(self.style.SUCCESS(f"  Generated {files_generated} files in {output_dir}/"))
        
        return files_generated
    
    def _generate_django_code(
        self,
        er_model,
        output_dir: Path,
        app_label: str
    ) -> int:
        """
        Generate Django model code from ERModel.
        
        Args:
            er_model: Parsed ERModel instance
            output_dir: Output directory for generated files
            app_label: Django app label
        
        Returns:
            Number of files generated
        
        Raises:
            Exception: If code generation fails
        """
        from x007007007.er.renderers import DjangoPackageRenderer
        
        # Use DjangoPackageRenderer for multi-file output
        renderer = DjangoPackageRenderer(app_label=app_label, table_prefix='')
        
        # Generate files
        result = renderer.render(er_model)
        
        # Write files to output directory
        files_generated = 0
        for filename, content in result.items():
            file_path = output_dir / filename
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path.write_text(content, encoding='utf-8')
            files_generated += 1
        
        return files_generated
    
    def _generate_sqlalchemy_code(
        self,
        er_model,
        output_dir: Path,
        base_model_import: Optional[str]
    ) -> int:
        """
        Generate SQLAlchemy model code from ERModel.
        
        Args:
            er_model: Parsed ERModel instance
            output_dir: Output directory for generated files
            base_model_import: Custom BaseModel import path
        
        Returns:
            Number of files generated
        
        Raises:
            Exception: If code generation fails
        """
        from x007007007.er.renderers import SQLAlchemyRenderer
        
        # Use SQLAlchemyRenderer with custom base model import if provided
        renderer_kwargs = {'table_prefix': ''}
        if base_model_import:
            renderer_kwargs['base_model_import'] = base_model_import
        
        renderer = SQLAlchemyRenderer(**renderer_kwargs)
        
        # Generate multi-file output (one file per model class)
        try:
            files = renderer.render_multi_file(er_model)
        except ValueError as e:
            # Fail-fast on filename conflicts
            raise CommandError(f"Failed to generate SQLAlchemy code: {e}")
        
        # Write each file to the output directory
        file_count = 0
        for filename, content in files.items():
            output_file = output_dir / filename
            try:
                output_file.write_text(content, encoding='utf-8')
                file_count += 1
            except Exception as e:
                # Fail-fast on write errors
                raise CommandError(
                    f"Failed to write file '{output_file}': {e}"
                )
        
        return file_count
