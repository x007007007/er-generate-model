"""
Django management command: er_makemigrations

Generate ER-based migrations from Django models.
"""
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from pathlib import Path

from x007007007.er_django.parser import DjangoModelParser
from x007007007.er_migrate.converter import ERConverter
from x007007007.er_migrate.file_manager import FileManager
from x007007007.er_migrate.differ import ERDiffer
from x007007007.er_migrate.generator import MigrationGenerator
from x007007007.er_django.settings import get_er_settings, get_er_migrations_dir, ensure_directory_exists


class Command(BaseCommand):
    help = 'Generate ER-based migrations from Django models'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'apps',
            nargs='*',
            help='Django app labels (if not specified, generate for all apps)'
        )
        parser.add_argument(
            '--migrations-dir',
            type=str,
            help='Migrations directory (default: from settings)'
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Custom migration name'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without creating files'
        )
        parser.add_argument(
            '--exclude-apps',
            type=str,
            help='Comma-separated list of apps to exclude'
        )
    
    def handle(self, *args, **options):
        # Get ER settings
        er_settings = get_er_settings()
        
        apps_to_migrate = options.get('apps', [])
        migrations_dir = options.get('migrations_dir') or get_er_migrations_dir()
        custom_name = options.get('name')
        dry_run = options.get('dry_run', False)
        exclude_apps = options.get('exclude_apps', '')
        
        # Parse excluded apps (combine from options and settings)
        excluded_apps = [app.strip() for app in exclude_apps.split(',')] if exclude_apps else []
        excluded_apps.extend(er_settings['exclude_apps'])
        excluded_apps = list(set(excluded_apps))  # Remove duplicates
        
        # Determine which apps to process
        if apps_to_migrate:
            target_apps = apps_to_migrate
        else:
            # Get all local apps (exclude Django built-in apps)
            all_apps = [app.label for app in apps.get_app_configs()]
            django_builtin_apps = {
                'admin', 'auth', 'contenttypes', 'sessions', 'messages', 
                'staticfiles', 'sites', 'flatpages', 'redirects'
            }
            target_apps = [
                app for app in all_apps 
                if app not in django_builtin_apps and app not in excluded_apps
            ]
        
        # Validate apps exist
        for app_label in target_apps:
            try:
                apps.get_app_config(app_label)
            except LookupError:
                raise CommandError(f"App '{app_label}' not found")
        
        if not target_apps:
            self.stdout.write(self.style.WARNING("No apps to process"))
            return
        
        self.stdout.write(f"Processing apps: {', '.join(target_apps)}")
        self.stdout.write(f"Migrations directory: {migrations_dir}")
        
        # Ensure migrations directory exists
        if er_settings['auto_create_dirs']:
            ensure_directory_exists(migrations_dir)
        
        # Process each app
        generated_migrations = []
        for app_label in target_apps:
            migration = self._process_app(app_label, migrations_dir, custom_name, dry_run)
            if migration:
                generated_migrations.append((app_label, migration))
        
        # Summary
        if generated_migrations:
            self.stdout.write(self.style.SUCCESS(f"\nGenerated {len(generated_migrations)} migrations:"))
            for app_label, migration in generated_migrations:
                self.stdout.write(f"  {app_label}: {migration.name}.yaml")
        else:
            self.stdout.write(self.style.SUCCESS("No changes detected in any app"))
    
    def _process_app(self, app_label: str, migrations_dir: str, custom_name: str, dry_run: bool):
        """Process a single app and generate migration if needed"""
        self.stdout.write(f"\n--- Processing app '{app_label}' ---")
        
        self.stdout.write(f"Parsing Django models from app '{app_label}'...")
        
        # Parse Django models to ER model
        parser = DjangoModelParser(app_label=app_label)
        er_model = parser.parse()
        
        if not er_model.entities:
            self.stdout.write(self.style.WARNING(f"No models found in app '{app_label}'"))
            return None
        
        self.stdout.write(f"Found {len(er_model.entities)} models")
        
        # Convert ER model to migration format (for future use)
        converter = ERConverter()
        current_state = converter.convert_model(er_model)
        
        # Initialize file manager and differ
        file_manager = FileManager(migrations_dir)
        differ = ERDiffer()
        
        # Get previous state
        previous_migrations = file_manager.load_namespace_migrations(app_label)
        if previous_migrations:
            last_migration = previous_migrations[-1]
            self.stdout.write(f"Last migration: {last_migration.name}")
            
            # For now, create an empty previous model since we don't have state reconstruction
            # TODO: Implement proper state reconstruction from migrations
            from x007007007.er.models import ERModel
            previous_model = ERModel()
        else:
            self.stdout.write("No previous migrations found")
            from x007007007.er.models import ERModel
            previous_model = ERModel()
        
        # Generate diff
        operations = differ.diff(previous_model, er_model)
        
        if not operations:
            self.stdout.write(self.style.SUCCESS("No changes detected"))
            return None
        
        self.stdout.write(f"Detected {len(operations)} operations:")
        for op in operations:
            self.stdout.write(f"  - {op.type}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run - no files created"))
            return None
        
        # Generate migration
        generator = MigrationGenerator(migrations_dir)
        
        migration = generator.generate(
            namespace=app_label,
            current_er=er_model,
            name=custom_name
        )
        
        if migration:
            # Save the migration to disk
            migration_path = generator.file_manager.save_migration(migration)
            self.stdout.write(f"Migration saved to: {migration_path}")
            return migration
        else:
            self.stdout.write("No migration generated")
            return None
    
    def _rebuild_state(self, migrations):
        """Rebuild database state from migrations"""
        state = {"tables": {}, "foreign_keys": []}
        
        for migration in migrations:
            for operation in migration.operations:
                op_type = operation.type
                
                if op_type == "CreateTable":
                    state["tables"][operation.table_name] = {
                        "columns": operation.columns,
                        "indexes": []
                    }
                elif op_type == "DropTable":
                    state["tables"].pop(operation.table_name, None)
                elif op_type == "AddColumn":
                    if operation.table_name in state["tables"]:
                        state["tables"][operation.table_name]["columns"].append(operation.column)
                elif op_type == "RemoveColumn":
                    if operation.table_name in state["tables"]:
                        state["tables"][operation.table_name]["columns"] = [
                            col for col in state["tables"][operation.table_name]["columns"]
                            if col.name != operation.column_name
                        ]
                elif op_type == "AddForeignKey":
                    state["foreign_keys"].append(operation.foreign_key)
                elif op_type == "RemoveForeignKey":
                    state["foreign_keys"] = [
                        fk for fk in state["foreign_keys"]
                        if not (fk.column_name == operation.constraint_name)
                    ]
        
        return state
