"""
Django management command: er_showmigrations

Show ER migration status for Django apps.
"""
from django.core.management.base import BaseCommand
from django.apps import apps
from pathlib import Path

from x007007007.er_migrate.file_manager import FileManager
from x007007007.er_django.settings import get_er_migrations_dir


class Command(BaseCommand):
    help = 'Show ER migration status for Django apps'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'apps',
            nargs='*',
            help='Django app labels (show all if not specified)'
        )
        parser.add_argument(
            '--migrations-dir',
            type=str,
            help='Migrations directory (default: from settings)'
        )
    
    def handle(self, *args, **options):
        apps_to_show = options.get('apps', [])
        migrations_dir = options.get('migrations_dir') or get_er_migrations_dir()
        
        self.stdout.write(f"Migrations directory: {migrations_dir}")
        
        file_manager = FileManager(migrations_dir)
        
        if apps_to_show:
            # Show migrations for specific apps
            for app_label in apps_to_show:
                self._show_app_migrations(file_manager, app_label)
                if len(apps_to_show) > 1:
                    self.stdout.write("")  # Empty line between apps
        else:
            # Show migrations for all apps
            migrations_dir_path = Path(migrations_dir)
            if not migrations_dir_path.exists():
                self.stdout.write("No migrations found")
                return
            
            # Get all subdirectories as namespaces
            namespaces = [
                d.name for d in migrations_dir_path.iterdir() 
                if d.is_dir() and not d.name.startswith('.')
            ]
            
            if not namespaces:
                self.stdout.write("No migrations found")
                return
            
            for namespace in sorted(namespaces):
                self._show_app_migrations(file_manager, namespace)
                self.stdout.write("")  # Empty line between apps
    
    def _show_app_migrations(self, file_manager, app_label):
        """Show migrations for a specific app"""
        migrations = file_manager.load_namespace_migrations(app_label)
        
        if not migrations:
            self.stdout.write(f"{app_label}:")
            self.stdout.write("  (no migrations)")
            return
        
        self.stdout.write(f"{app_label}:")
        for migration in migrations:
            # All migrations are considered applied in this simple version
            # In a real implementation, you'd check against a database table
            status = self.style.SUCCESS("[X]")
            self.stdout.write(f"  {status} {migration.name}")
