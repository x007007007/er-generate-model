"""
Migration subcommands - Database migration management
"""
import click
from pathlib import Path
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from .migration_core.generator import MigrationGenerator
from .migration_core.file_manager import FileManager


@click.command()
@click.option('--namespace', '-n', required=True, help='Migration namespace')
@click.option('--er-file', '-e', required=True, type=click.Path(exists=True), help='ER diagram file (Mermaid format)')
@click.option('--migrations-dir', '-d', default='.migrations', help='Migrations directory')
@click.option('--name', help='Custom migration name (optional)')
def makemigration_cmd(namespace: str, er_file: str, migrations_dir: str, name: str):
    """
    Generate migration from ER diagram
    
    Example:
        er-gen-tool makemigration -n blog -e schema.mmd
    """
    try:
        # 1. Parse ER diagram
        click.echo(f"Parsing ER diagram from {er_file}...")
        parser = MermaidAntlrParser()
        
        with open(er_file, 'r', encoding='utf-8') as f:
            er_content = f.read()
        
        er_model = parser.parse(er_content)
        
        # 2. Generate migration
        click.echo(f"Generating migration for namespace '{namespace}'...")
        generator = MigrationGenerator(migrations_dir)
        migration = generator.generate(namespace, er_model, name=name)
        
        # 3. Save migration
        if migration is None:
            click.echo(click.style("No changes detected.", fg='yellow'))
            return
        
        file_manager = FileManager(migrations_dir)
        file_path = file_manager.save_migration(migration)
        
        # 4. Display result
        click.echo(click.style(f"\nMigrations for '{namespace}':", fg='green', bold=True))
        click.echo(f"  {file_path.name}")
        click.echo(f"\nMigration saved to: {file_path}")
        
    except FileNotFoundError as e:
        click.echo(click.style(f"Error: File does not exist: {er_file}", fg='red'), err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.Abort()


@click.group()
def migrate_group():
    """Database migration management"""
    pass


@migrate_group.command(name='showmigrations')
@click.option('--namespace', '-n', help='Show migrations for specific namespace')
@click.option('--migrations-dir', '-d', default='.migrations', help='Migrations directory')
def showmigrations_cmd(namespace: str, migrations_dir: str):
    """
    Show migration status
    
    Example:
        er-gen-tool migrate showmigrations -n blog
        er-gen-tool migrate showmigrations  # Show all namespaces
    """
    try:
        file_manager = FileManager(migrations_dir)
        migrations_path = Path(migrations_dir)
        
        # If namespace is specified
        if namespace:
            migrations = file_manager.load_namespace_migrations(namespace)
            
            if not migrations:
                click.echo(f"No migrations found for namespace '{namespace}'")
                return
            
            click.echo(click.style(f"\n{namespace}:", fg='cyan', bold=True))
            for migration in migrations:
                # Get file name
                files = file_manager.list_migration_files(namespace)
                for file in files:
                    if migration.name in file:
                        click.echo(f"  [X] {file.replace('.yaml', '').replace('.yml', '')}")
                        break
        
        # Show all namespaces
        else:
            if not migrations_path.exists():
                click.echo("No migrations directory found")
                return
            
            # List all namespaces
            namespaces = [d.name for d in migrations_path.iterdir() if d.is_dir()]
            
            if not namespaces:
                click.echo("No migrations found")
                return
            
            for ns in sorted(namespaces):
                migrations = file_manager.load_namespace_migrations(ns)
                if migrations:
                    click.echo(click.style(f"\n{ns}:", fg='cyan', bold=True))
                    files = file_manager.list_migration_files(ns)
                    for file in files:
                        migration_id = file.replace('.yaml', '').replace('.yml', '')
                        click.echo(f"  [X] {migration_id}")
    
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.Abort()
