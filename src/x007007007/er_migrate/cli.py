"""
CLI命令行接口
"""
import click
from pathlib import Path
from x007007007.er.parser.antlr.mermaid_antlr_parser import MermaidAntlrParser
from .generator import MigrationGenerator
from .file_manager import FileManager
from ..er.version import get_version


@click.group()
@click.version_option(version=get_version(), prog_name="er-migrate")
def cli():
    """ER Migrations - Database migration system based on ER diagrams"""
    pass


@cli.command()
@click.option('--namespace', '-n', required=True, help='Migration namespace')
@click.option('--er-file', '-e', required=True, type=click.Path(exists=True), help='ER diagram file (Mermaid format)')
@click.option('--migrations-dir', '-d', default='.migrations', help='Migrations directory')
@click.option('--name', help='Custom migration name (optional)')
def makemigrations(namespace: str, er_file: str, migrations_dir: str, name: str):
    """
    Generate migration from ER diagram
    
    Example:
        er-migrate makemigrations -n blog -e schema.mmd
    """
    try:
        # 1. 解析ER图
        click.echo(f"Parsing ER diagram from {er_file}...")
        parser = MermaidAntlrParser()
        
        with open(er_file, 'r', encoding='utf-8') as f:
            er_content = f.read()
        
        er_model = parser.parse(er_content)
        
        # 2. 生成迁移
        click.echo(f"Generating migration for namespace '{namespace}'...")
        generator = MigrationGenerator(migrations_dir)
        migration = generator.generate(namespace, er_model, name=name)
        
        # 3. 保存迁移
        if migration is None:
            click.echo(click.style("No changes detected.", fg='yellow'))
            return
        
        file_manager = FileManager(migrations_dir)
        file_path = file_manager.save_migration(migration)
        
        # 4. 显示结果
        click.echo(click.style(f"\nMigrations for '{namespace}':", fg='green', bold=True))
        click.echo(f"  {file_path.name}")
        click.echo(f"\nMigration saved to: {file_path}")
        
    except FileNotFoundError as e:
        click.echo(click.style(f"Error: File does not exist: {er_file}", fg='red'), err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.Abort()


@cli.command()
@click.option('--namespace', '-n', help='Show migrations for specific namespace')
@click.option('--migrations-dir', '-d', default='.migrations', help='Migrations directory')
def showmigrations(namespace: str, migrations_dir: str):
    """
    Show migration status
    
    Example:
        er-migrate showmigrations -n blog
        er-migrate showmigrations  # Show all namespaces
    """
    try:
        file_manager = FileManager(migrations_dir)
        migrations_path = Path(migrations_dir)
        
        # 如果指定了命名空间
        if namespace:
            migrations = file_manager.load_namespace_migrations(namespace)
            
            if not migrations:
                click.echo(f"No migrations found for namespace '{namespace}'")
                return
            
            click.echo(click.style(f"\n{namespace}:", fg='cyan', bold=True))
            for migration in migrations:
                # 获取文件名
                files = file_manager.list_migration_files(namespace)
                for file in files:
                    if migration.name in file:
                        click.echo(f"  [X] {file.replace('.yaml', '').replace('.yml', '')}")
                        break
        
        # 显示所有命名空间
        else:
            if not migrations_path.exists():
                click.echo("No migrations directory found")
                return
            
            # 列出所有命名空间
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


if __name__ == '__main__':
    cli()
