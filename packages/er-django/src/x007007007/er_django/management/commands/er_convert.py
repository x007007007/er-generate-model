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
from x007007007.er_django.path_configuration import PathConfiguration
from x007007007.er_django.path_resolver import PathResolver


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
        
        parser.add_argument(
            '--output-dir',
            type=str,
            default='src',
            help='Root directory for TOML search and code output (default: src)'
        )
        
        parser.add_argument(
            '--inheritance-mode',
            '-i',
            type=str,
            choices=['reference', 'flatten'],
            default='reference',
            help='Inheritance handling mode: reference (generate mixin files, use Python inheritance) or flatten (expand all inherited fields directly into entity classes)'
        )
    
    def handle(self, *args, **options):
        apps_to_convert = options.get('apps', [])
        framework = options.get('framework')
        output_subdir = options.get('output_subdir')
        base_model_import = options.get('base_model_import')
        output_dir = options.get('output_dir')
        inheritance_mode = options.get('inheritance_mode', 'reference')
        
        # Convert output_dir to Path
        output_path = Path(output_dir) if output_dir else Path('src')
        
        # Create PathConfiguration for third-party detection
        path_config = PathConfiguration.from_options(
            scan_path=output_path,
            output_path=output_path,
            working_dir=Path.cwd()
        )
        
        # Validate configuration
        config_errors = path_config.validate()
        if config_errors:
            # If scan_path doesn't exist, try to create it
            if not path_config.scan_path.exists():
                try:
                    path_config.scan_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    raise CommandError(f"Failed to create output directory: {e}")
            else:
                raise CommandError(f"Configuration errors: {', '.join(config_errors)}")
        
        # Auto-discover or validate apps
        if not apps_to_convert:
            # Auto-discover all apps with models.toml
            apps_to_convert = AppDiscoveryService.discover_apps_with_toml(
                toml_search_dir=output_path
            )
            
            if not apps_to_convert:
                raise CommandError("No apps with models.toml found")
            
            self.stdout.write(f"Auto-discovered {len(apps_to_convert)} apps with models.toml:")
            for app_label in apps_to_convert:
                self.stdout.write(f"  - {app_label}")
        else:
            # Print message before validation
            self.stdout.write(f"Converting specified apps: {', '.join(apps_to_convert)}")
            # Validate specified apps (fail-fast)
            self._validate_apps(apps_to_convert, output_path)
        
        # Convert each app (fail-fast)
        converted_count = 0
        total_files = 0
        
        for app_label in apps_to_convert:
            try:
                files_generated = self._convert_app(
                    app_label=app_label,
                    framework=framework,
                    output_subdir=output_subdir,
                    base_model_import=base_model_import,
                    output_dir=output_path,
                    path_config=path_config,
                    inheritance_mode=inheritance_mode
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
    
    def _validate_apps(self, app_labels: List[str], output_dir: Optional[Path] = None) -> None:
        """
        Validate that specified apps exist and have models.toml files.
        
        This method performs fail-fast validation:
        1. Checks that each app exists in Django's installed apps
        2. Checks that each app has a models.toml file
        
        Args:
            app_labels: List of app labels to validate
            output_dir: Optional directory to search for TOML files
        
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
                AppDiscoveryService.get_toml_path(app_label, toml_search_dir=output_dir)
            except FileNotFoundError as e:
                raise CommandError(str(e))
    
    def _convert_app(
        self,
        app_label: str,
        framework: str,
        output_subdir: Optional[str],
        base_model_import: Optional[str],
        output_dir: Optional[Path] = None,
        path_config: Optional[PathConfiguration] = None,
        inheritance_mode: str = 'reference'
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
            output_dir: Optional directory to search for TOML files
            path_config: Optional PathConfiguration for third-party detection
        
        Returns:
            Number of files generated
        
        Raises:
            CommandError: If conversion fails (fail-fast)
        
        Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.8
        """
        # Get app config for third-party detection
        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            raise CommandError(f"App '{app_label}' not found")
        
        # Determine if this is a third-party package
        is_third_party = False
        if path_config:
            is_third_party = self._is_third_party_app(app_config, path_config.scan_path)
        
        if is_third_party:
            self.stdout.write(f"\nConverting app '{app_label}' to {framework} (third-party package)...")
        else:
            self.stdout.write(f"\nConverting app '{app_label}' to {framework}...")
        
        # Get TOML file path (fail-fast if not found)
        try:
            toml_path = AppDiscoveryService.get_toml_path(app_label, toml_search_dir=output_dir)
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
            parser = TomlERParser(inheritance_mode=inheritance_mode)
            er_model = parser.parse(toml_content)
        except Exception as e:
            raise CommandError(f"Failed to parse TOML file {toml_path}: {e}")
        
        # Determine output directory
        # For third-party packages, use third/ subdirectory
        toml_dir = toml_path.parent
        
        if is_third_party and path_config:
            # Third-party packages go to third/ subdirectory
            base_output_dir = path_config.output_path / 'third' / app_label
        else:
            # Local apps stay in their original location
            base_output_dir = toml_dir
        
        # Use custom subdir if specified
        if output_subdir:
            final_output_dir = base_output_dir / output_subdir
        else:
            # Default behavior depends on framework:
            # - Django: output to models/ subdirectory
            # - SQLAlchemy: output to sqlalchemy/ subdirectory
            if framework == 'django':
                final_output_dir = base_output_dir / 'models'
            elif framework == 'sqlalchemy':
                final_output_dir = base_output_dir / 'sqlalchemy'
            else:
                final_output_dir = base_output_dir
        
        self.stdout.write(f"  Output directory: {final_output_dir}")
        
        # Create output directory (fail-fast on error)
        try:
            final_output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise CommandError(f"Failed to create output directory {final_output_dir}: {e}")
        
        # Generate code based on target framework
        try:
            if framework == 'django':
                files_generated = self._generate_django_code(
                    er_model=er_model,
                    output_dir=final_output_dir,
                    app_label=app_label,
                    inheritance_mode=inheritance_mode
                )
            elif framework == 'sqlalchemy':
                files_generated = self._generate_sqlalchemy_code(
                    er_model=er_model,
                    output_dir=final_output_dir,
                    base_model_import=base_model_import,
                    inheritance_mode=inheritance_mode,
                    toml_path=toml_path,
                    output_root=output_dir if output_dir else Path('src')
                )
            else:
                raise CommandError(f"Unsupported framework: {framework}")
        except Exception as e:
            raise CommandError(f"Failed to generate {framework} code: {e}")
        
        self.stdout.write(self.style.SUCCESS(f"  Generated {files_generated} files in {final_output_dir}/"))
        
        return files_generated
    
    def _generate_django_code(
        self,
        er_model,
        output_dir: Path,
        app_label: str,
        inheritance_mode: str = 'reference'
    ) -> int:
        """
        Generate Django model code from ERModel.
        
        Args:
            er_model: Parsed ERModel instance
            output_dir: Output directory for generated files
            app_label: Django app label
            inheritance_mode: Inheritance handling mode ('reference' or 'flatten')
        
        Returns:
            Number of files generated
        
        Raises:
            Exception: If code generation fails
        """
        from x007007007.er.renderers import DjangoPackageRenderer
        
        # Use DjangoPackageRenderer for multi-file output
        renderer = DjangoPackageRenderer(
            app_label=app_label,
            table_prefix='',
            inheritance_mode=inheritance_mode
        )
        
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
        base_model_import: Optional[str],
        inheritance_mode: str = 'reference',
        toml_path: Optional[Path] = None,
        output_root: Optional[Path] = None
    ) -> int:
        """
        Generate SQLAlchemy model code from ERModel.
        
        Args:
            er_model: Parsed ERModel instance
            output_dir: Output directory for generated files
            base_model_import: Custom BaseModel import path
            inheritance_mode: Inheritance handling mode ('reference' or 'flatten')
            toml_path: Path to the main TOML file (for discovering dependencies)
            output_root: Root output directory (for MixinOrchestrator)
        
        Returns:
            Number of files generated
        
        Raises:
            Exception: If code generation fails
        """
        from x007007007.er.renderers import SQLAlchemyRenderer
        
        # Process templates if in reference mode
        # We need to discover dependent TOML files even if er_model.templates is empty
        # because the templates might be defined in other TOML files (referenced via extends)
        self.stdout.write(f"  DEBUG: inheritance_mode={inheritance_mode}, has_templates={bool(er_model.templates)}, toml_path={toml_path}, output_root={output_root}")
        if inheritance_mode == 'reference' and toml_path and output_root:
            from x007007007.er.mixin_orchestrator import MixinOrchestrator
            from x007007007.er.renderers.python.utils import to_snake_case
            
            # Discover all dependent TOML files by resolving extends references
            all_toml_files = self._discover_dependent_toml_files(er_model, toml_path)
            
            self.stdout.write(f"  Discovered {len(all_toml_files)} TOML file(s) (including dependencies)")
            for toml_file in all_toml_files:
                self.stdout.write(f"    - {toml_file}")
            
            # Use MixinOrchestrator to process templates from all discovered files
            orchestrator = MixinOrchestrator()
            try:
                templates = orchestrator.process_templates(
                    toml_files=all_toml_files,
                    output_dir=str(output_root),
                    inheritance_mode=inheritance_mode
                )
                # Convert TemplateInfo objects back to dictionary format for renderer compatibility
                # Update export_path to include the module name for correct imports
                er_model.templates = {
                    name: {
                        'columns': [],  # Empty columns so renderer skips mixin generation
                        'export_path': f"{info.export_path}.{to_snake_case(name)}",  # Add module name
                        'package': info.package
                    }
                    for name, info in templates.items()
                }
                self.stdout.write(f"  Processed {len(templates)} template(s)")
            except Exception as e:
                raise CommandError(f"Failed to process templates: {e}")
        
        # Use SQLAlchemyRenderer with custom base model import if provided
        renderer_kwargs = {
            'table_prefix': '',
            'inheritance_mode': inheritance_mode
        }
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
        # IMPORTANT: third-party files should be written to global src/third/ directory
        # while entity files should be written to the module-specific output_dir
        file_count = 0
        for filename, content in files.items():
            if filename.startswith('third/'):
                # Third-party files go to global src/third/ directory
                # Find the src/ root by going up from output_dir
                # output_dir might be like: src/kinkotech/rfc_backend/domains/rfc_login/sqlalchemy
                # We need to find the 'src' part and use it as the base
                current = output_dir
                src_root = None
                while current.parent != current:  # Stop at filesystem root
                    if current.name == 'src':
                        src_root = current
                        break
                    current = current.parent
                
                if src_root is None:
                    # Fallback: assume output_dir is relative to current directory
                    # and try to find src/ in the path
                    if 'src' in output_dir.parts:
                        src_index = output_dir.parts.index('src')
                        src_root = Path(*output_dir.parts[:src_index+1])
                    else:
                        # Last resort: use output_dir's parent as src root
                        src_root = output_dir.parent
                
                output_file = src_root / filename
            else:
                # Entity and mixin files go to module-specific output_dir
                output_file = output_dir / filename
            
            # Create parent directories if needed (for mixin files in subdirectories)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                output_file.write_text(content, encoding='utf-8')
                file_count += 1
            except Exception as e:
                # Fail-fast on write errors
                raise CommandError(
                    f"Failed to write file '{output_file}': {e}"
                )
        
        return file_count
    
    def _discover_dependent_toml_files(self, er_model, main_toml_path: Path) -> List[str]:
        """
        Discover all TOML files that the main TOML file depends on.
        
        This method analyzes the extends references in the ERModel and uses
        NamespaceResolver to find the corresponding TOML files.
        
        Args:
            er_model: Parsed ERModel instance
            main_toml_path: Path to the main TOML file
        
        Returns:
            List of TOML file paths (including the main file)
        """
        from x007007007.er.namespace_resolver import NamespaceResolver
        
        # Start with the main TOML file
        toml_files = [str(main_toml_path)]
        discovered_files = {str(main_toml_path)}
        
        # Get the root directory for namespace resolution (typically 'src')
        # Assume TOML files are under src/ directory
        root_dir = main_toml_path
        while root_dir.parent != root_dir:
            if root_dir.name == 'src':
                break
            root_dir = root_dir.parent
        
        if root_dir.name != 'src':
            # If we didn't find 'src', use the parent of the TOML file's directory
            root_dir = main_toml_path.parent.parent
        
        # Create NamespaceResolver with search paths
        search_paths = [str(root_dir), str(root_dir / 'third')]
        resolver = NamespaceResolver(search_paths=search_paths)
        
        # Collect all extends references from entities
        extends_namespaces = set()
        for entity in er_model.entities.values():
            if hasattr(entity, 'extends') and entity.extends:
                for extend_ref in entity.extends:
                    # Extract namespace from extend reference
                    # Format: "namespace.path.to.ClassName"
                    # We need to resolve the namespace part (without the class name)
                    if '.' in extend_ref:
                        # Remove the class name (last part)
                        namespace_parts = extend_ref.rsplit('.', 1)
                        if len(namespace_parts) == 2:
                            namespace = namespace_parts[0]
                            extends_namespaces.add(namespace)
        
        # Resolve each namespace to a TOML file
        for namespace in extends_namespaces:
            try:
                result = resolver.resolve(namespace)
                if result.exists and result.file_path not in discovered_files:
                    toml_files.append(result.file_path)
                    discovered_files.add(result.file_path)
            except Exception as e:
                # Log warning but continue (the template might be defined elsewhere)
                self.stdout.write(
                    self.style.WARNING(
                        f"  Warning: Could not resolve namespace '{namespace}': {e}"
                    )
                )
        
        return toml_files
    
    def _is_third_party_app(self, app_config, scan_path: Path) -> bool:
        """
        Determine if an app is a third-party package.
        
        An app is considered third-party if its path is outside the scan_path directory.
        This typically means it's installed in site-packages or another external location.
        
        Args:
            app_config: Django AppConfig instance
            scan_path: Path to the project's source code directory
            
        Returns:
            True if the app is third-party, False otherwise
        """
        try:
            app_path = Path(app_config.path).resolve()
            scan_path_resolved = scan_path.resolve()
            
            # Check if app_path is under scan_path
            # If app is inside scan_path, it's a local app
            # If app is outside scan_path, it's a third-party app
            try:
                app_path.relative_to(scan_path_resolved)
                return False  # Local app
            except ValueError:
                # app_path is not relative to scan_path, so it's third-party
                return True
        except Exception:
            # If we can't determine, assume it's third-party to be safe
            return True
