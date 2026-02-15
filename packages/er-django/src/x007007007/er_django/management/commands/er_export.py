"""
Django management command: er_export

Export Django models to ER diagram (Mermaid/PlantUML).
"""
import os
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.template import Template, Context
from pathlib import Path

from x007007007.er_django.parser import DjangoModelParser
from x007007007.er_django.path_resolver import PathResolver
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
            default=None,
            help='Output directory (default: ./src)'
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
    
    def handle(self, *args, **options):
        # Get ER settings
        er_settings = get_er_settings()
        
        apps_to_export = options.get('apps', [])
        output_format = options.get('format')  # Already has default value 'toml'
        output_path = options.get('output')
        
        # Determine output directory: use --output-dir if specified, otherwise use ./src
        output_dir = options.get('output_dir')
        if output_dir is None:
            # Use ./src as default output directory
            output_dir = './src'
        
        # Handle relative and absolute paths
        if not os.path.isabs(output_dir):
            # Relative path: resolve relative to current working directory
            output_dir = os.path.join(os.getcwd(), output_dir)
        
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
            ensure_directory_exists(output_dir)
        
        # Export each app to a separate file
        exported_files = []
        total_entities = 0
        
        for app_label in target_apps:
            # Get app config for path resolution
            app_config = apps.get_app_config(app_label)
            
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
            
            self.stdout.write(f"Found {len(er_model.entities)} models in app '{app_label}'")
            total_entities += len(er_model.entities)
            
            # Use PathResolver to determine output path and set export_path for each entity
            try:
                resolved_output_path = PathResolver.resolve_output_path(
                    app_config=app_config,
                    base_dir=output_dir,
                    format=output_format
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
                    output_file = Path(output_dir) / output_file
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
        
        # Summary
        if exported_files:
            self.stdout.write(self.style.SUCCESS(f"\nExported {total_entities} models from {len(exported_files)} apps:"))
            for app_label, file_path in exported_files:
                self.stdout.write(f"  {app_label}: {file_path}")
            self.stdout.write(f"\nExport directory: {output_dir}")
            self.stdout.write(f"Format: {output_format}")
            if excluded_apps:
                self.stdout.write(f"Excluded apps: {', '.join(excluded_apps)}")
        else:
            self.stdout.write(self.style.WARNING("No models found to export"))
