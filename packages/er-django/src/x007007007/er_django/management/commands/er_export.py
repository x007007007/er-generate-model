"""
Django management command: er_export

Export Django models to ER diagram (Mermaid/PlantUML).
"""
import os
from collections import defaultdict
from typing import Any, Dict, List
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.template import Template, Context
from pathlib import Path

from x007007007.er_django.parser import DjangoModelParser
from x007007007.er_django.path_resolver import PathResolver
from x007007007.er_django.path_configuration import PathConfiguration
from x007007007.er_django.entity_name_extractor import EntityNameExtractor
from x007007007.er_django.settings import (
    get_er_settings, ensure_directory_exists, get_output_filename
)


class Command(BaseCommand):
    help = 'Export Django models to ER diagram (Mermaid/PlantUML)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'apps',
            nargs='*',
            help='Django app labels (if not specified, export all apps)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['mermaid', 'plantuml', 'toml'],
            default='toml',
            help='Output format (default: toml)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (default: auto-generated in export directory)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='src',
            help='Output directory (default: src)'
        )
        parser.add_argument(
            '--models',
            type=str,
            help='Comma-separated list of specific models to export (format: app.Model)'
        )
        parser.add_argument(
            '--exclude-apps',
            type=str,
            help='Comma-separated list of apps to exclude'
        )
        parser.add_argument(
            '--include-django-apps',
            action='store_true',
            help='Include Django built-in apps (auth, contenttypes, etc.)'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Custom base name for output file'
        )
        parser.add_argument(
            '--entity-name-pattern',
            type=str,
            default=EntityNameExtractor.DEFAULT_PATTERN,
            help='Regex pattern to extract business entity name from model name. '
                 'Must have one capture group. Default: "(.+)Model$" (removes "Model" suffix)'
        )
    
    def handle(self, *args, **options):
        # Get ER settings
        er_settings = get_er_settings()
        
        # Create entity name extractor with error handling
        entity_name_pattern = options.get('entity_name_pattern') or EntityNameExtractor.DEFAULT_PATTERN
        try:
            name_extractor = EntityNameExtractor(entity_name_pattern)
        except ValueError as e:
            raise CommandError(f"Invalid entity name pattern: {e}")
        
        apps_to_export = options.get('apps', [])
        output_format = options.get('format')  # Already has default value 'toml'
        output_path = options.get('output')
        
        # Determine output directory: use --output-dir (default is 'src')
        output_dir = options.get('output_dir') or 'src'
        
        # Create PathConfiguration
        path_config = PathConfiguration.from_options(
            scan_path=output_dir,
            output_path=output_dir,
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
        
        # Create PathResolver with configuration
        path_resolver = PathResolver(path_config)
        
        specific_models = options.get('models')
        exclude_apps = options.get('exclude_apps', '')
        include_django_apps = options.get('include_django_apps') or er_settings['include_django_apps']
        custom_name = options.get('name')
        
        # Parse excluded apps (combine from options and settings)
        excluded_apps = [app.strip() for app in exclude_apps.split(',')] if exclude_apps else []
        excluded_apps.extend(er_settings['exclude_apps'])
        excluded_apps = list(set(excluded_apps))  # Remove duplicates
        
        # Parse specific models
        specific_model_list = []
        if specific_models:
            for model_spec in specific_models.split(','):
                model_spec = model_spec.strip()
                if '.' in model_spec:
                    app_label, model_name = model_spec.split('.', 1)
                    specific_model_list.append((app_label, model_name))
                else:
                    raise CommandError(f"Invalid model specification: {model_spec}. Use format: app.Model")
        
        # Determine which apps to process
        if specific_model_list:
            # If specific models are specified, get their apps
            target_apps = list(set(app_label for app_label, _ in specific_model_list))
            self.stdout.write(f"Exporting specific models from apps: {', '.join(target_apps)}")
        elif apps_to_export:
            # Use specified apps
            target_apps = apps_to_export
            self.stdout.write(f"Exporting apps: {', '.join(target_apps)}")
        else:
            # Export all local apps (exclude Django built-in apps unless requested)
            all_apps = [app.label for app in apps.get_app_configs()]
            if include_django_apps:
                target_apps = [app for app in all_apps if app not in excluded_apps]
            else:
                # Exclude common Django built-in apps
                django_builtin_apps = {
                    'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
                    'staticfiles', 'sites', 'flatpages', 'redirects'
                }
                target_apps = [
                    app for app in all_apps 
                    if app not in django_builtin_apps and app not in excluded_apps
                ]
            self.stdout.write(f"Exporting all local apps: {', '.join(target_apps)}")
        
        # Validate apps exist
        for app_label in target_apps:
            try:
                apps.get_app_config(app_label)
            except LookupError:
                raise CommandError(f"App '{app_label}' not found")
        
        if not target_apps:
            self.stdout.write(self.style.WARNING("No apps to export"))
            return
        
        # Ensure output directory exists
        if er_settings['auto_create_dirs']:
            ensure_directory_exists(str(path_config.output_path))
        
        # Export each app to a separate file
        exported_files = []
        total_entities = 0
        all_templates: Dict[str, Dict[str, Any]] = {}

        for app_label in target_apps:
            # Get app config for path resolution
            app_config = apps.get_app_config(app_label)
            
            # Determine if this is a third-party package
            # A package is considered third-party if it's installed outside the scan_path
            is_third_party = self._is_third_party_app(app_config, path_config.scan_path)
            
            if is_third_party:
                self.stdout.write(f"  {app_label}: third-party package")
            
            # Parse models for this app
            parser = DjangoModelParser(app_label=app_label)
            
            if specific_model_list:
                # Filter models for this app
                app_models = [
                    model_name for app, model_name in specific_model_list 
                    if app == app_label
                ]
                if app_models:
                    # Get specific model classes
                    model_classes = []
                    for model_name in app_models:
                        try:
                            model_class = app_config.get_model(model_name)
                            model_classes.append(model_class)
                        except LookupError:
                            raise CommandError(f"Model '{model_name}' not found in app '{app_label}'")
                    
                    er_model = parser.parse(models_list=model_classes)
                else:
                    continue  # No models for this app
            else:
                # Parse all models in the app
                er_model = parser.parse()
            
            if not er_model.entities:
                self.stdout.write(self.style.WARNING(f"No models found in app '{app_label}'"))
                continue
            
            # Apply entity naming rules
            er_model = self._apply_entity_naming(er_model, name_extractor)
            
            er_model.namespace = app_config.module.__name__
            
            self.stdout.write(f"Found {len(er_model.entities)} models in app '{app_label}'")
            total_entities += len(er_model.entities)
            
            # Use PathResolver to determine output path and set export_path for each entity
            try:
                resolved_output_path = path_resolver.resolve_output_path(
                    app_config=app_config,
                    format=output_format,
                    is_third_party=is_third_party
                )
                
                # Set export_path for all entities in this app
                for entity in er_model.entities.values():
                    entity.export_path = str(resolved_output_path)
                    
            except ValueError as e:
                raise CommandError(f"Failed to resolve output path for app '{app_label}': {e}")
            
            # Render ER diagram
            if output_format == 'mermaid':
                from x007007007.er_django.renderers import MermaidRenderer
                renderer = MermaidRenderer()
            elif output_format == 'plantuml':
                from x007007007.er_django.renderers import PlantUMLRenderer
                renderer = PlantUMLRenderer()
            elif output_format == 'toml':
                from x007007007.er_django.renderers import TOMLRenderer
                renderer = TOMLRenderer()
            else:
                raise CommandError(f"Unsupported format: {output_format}")
            
            diagram = renderer.render(er_model)
            
            # Determine output file path
            if output_path and len(target_apps) == 1:
                # Use specified output path only for single app
                output_file = Path(output_path)
                if not output_file.is_absolute():
                    output_file = path_config.output_path / output_file
            else:
                # Use the resolved output path from PathResolver
                output_file = resolved_output_path
            
            # Ensure parent directory exists (fail-fast if cannot create)
            try:
                output_file.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise CommandError(f"Failed to create directory {output_file.parent}: {e}")
            
            # Write file (fail-fast if cannot write)
            try:
                output_file.write_text(diagram, encoding='utf-8')
            except Exception as e:
                raise CommandError(f"Failed to write {output_file}: {e}")
                
            exported_files.append((app_label, output_file))
            self.stdout.write(self.style.SUCCESS(f"  → {output_file}"))

            for tmpl_name, tmpl_data in er_model.templates.items():
                if tmpl_name not in all_templates:
                    all_templates[tmpl_name] = tmpl_data

        if output_format == 'toml' and all_templates:
            template_files = self._export_templates(
                all_templates, path_config, name_extractor
            )
            exported_files.extend(template_files)
            total_entities += len(all_templates)

        # Summary
        if exported_files:
            self.stdout.write(self.style.SUCCESS(f"\nExported {total_entities} models from {len(exported_files)} apps:"))
            for app_label, file_path in exported_files:
                self.stdout.write(f"  {app_label}: {file_path}")
            self.stdout.write(f"\nExport directory: {path_config.output_path}")
            self.stdout.write(f"Format: {output_format}")
            if excluded_apps:
                self.stdout.write(f"Excluded apps: {', '.join(excluded_apps)}")
        else:
            self.stdout.write(self.style.WARNING("No models found to export"))
    
    def _export_templates(
        self,
        all_templates: Dict[str, Dict[str, Any]],
        path_config: PathConfiguration,
        name_extractor,
    ) -> List:
        """
        Export abstract model templates grouped by their Python package.

        Templates are grouped by their package path. Each group is written
        to a separate TOML file named after the package namespace.

        Args:
            all_templates: Dict mapping template_name -> template_data
            path_config: PathConfiguration for output directory
            name_extractor: EntityNameExtractor for naming

        Returns:
            List of (label, Path) tuples for exported files
        """
        from x007007007.er.models import ERModel, Entity, Column
        from x007007007.er_django.renderers import TOMLRenderer

        package_groups: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        for tmpl_name, tmpl_data in all_templates.items():
            package = tmpl_data.get('package', '')
            package_groups[package][tmpl_name] = tmpl_data

        renderer = TOMLRenderer()
        exported = []

        for package, templates in package_groups.items():
            namespace = package if package else '_unknown'
            output_file = path_config.output_path / f'{namespace}.toml'

            er_model = ERModel()
            er_model.namespace = namespace
            er_model.templates = templates

            diagram = renderer.render(er_model)

            try:
                output_file.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise CommandError(f"Failed to create directory {output_file.parent}: {e}")

            try:
                output_file.write_text(diagram, encoding='utf-8')
            except Exception as e:
                raise CommandError(f"Failed to write {output_file}: {e}")

            exported.append((f'templates:{namespace}', output_file))
            self.stdout.write(f"Found {len(templates)} abstract models in package '{namespace}'")
            self.stdout.write(self.style.SUCCESS(f"  → {output_file}"))

        return exported

    def _apply_entity_naming(self, er_model, name_extractor):
        """
        Apply business entity naming rules to ERModel.

        This method renames entities in the ERModel according to the
        business naming pattern, and updates all references in relationships.

        Args:
            er_model: Original ERModel with model class names
            name_extractor: EntityNameExtractor instance

        Returns:
            New ERModel with renamed entities
        """
        from x007007007.er.models import ERModel, Relationship

        # Create name mapping: model name → business name
        name_mapping = {}
        for entity_name in er_model.entities.keys():
            business_name = name_extractor.extract(entity_name)
            name_mapping[entity_name] = business_name

        # Create new ERModel
        new_model = ERModel()

        # Rename entities
        for old_name, entity in er_model.entities.items():
            new_name = name_mapping[old_name]
            entity.name = new_name
            new_model.entities[new_name] = entity

        # Update relationships with new entity names
        for rel in er_model.relationships:
            new_rel = Relationship(
                left_entity=name_mapping.get(rel.left_entity, rel.left_entity),
                right_entity=name_mapping.get(rel.right_entity, rel.right_entity),
                relation_type=rel.relation_type,
                left_column=rel.left_column,
                right_column=rel.right_column,
                left_cardinality=rel.left_cardinality,
                right_cardinality=rel.right_cardinality,
                left_label=rel.left_label,
                right_label=rel.right_label
            )
            new_model.relationships.append(new_rel)

        # Copy templates if any
        new_model.templates = er_model.templates.copy()

        return new_model
    
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

