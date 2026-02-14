"""
ER Diagram Generator Tool - Main CLI Entry Point

This module provides the main CLI entry point for er-gen-tool with plugin discovery.
Plugins can be registered via the 'er_gen_tool.plugins' entry point group.
"""
import click
import logging
from importlib.metadata import entry_points, version, PackageNotFoundError

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_version():
    """Get the version of er-gen-tool package"""
    try:
        return version("x007007007-er-gen-tool")
    except PackageNotFoundError:
        return "0.3.0"


@click.group()
@click.version_option(version=get_version(), prog_name="er-gen-tool")
def main():
    """ER Diagram Generator Tool
    
    Unified CLI for ER diagram operations including conversion, migration,
    and optional AI-assisted modeling (when er-gen-tool-ai is installed).
    """
    pass


def load_plugins():
    """Automatically discover and load plugin commands via entry points.
    
    This function discovers plugins registered under the 'er_gen_tool.plugins'
    entry point group. Plugins are loaded dynamically, allowing extensions
    like ai-assist to be added when their packages are installed.
    
    Plugin loading errors are logged but do not interrupt the main CLI.
    """
    try:
        # Python 3.10+ uses entry_points().select()
        # Python 3.9 uses entry_points() with group parameter
        try:
            plugin_eps = entry_points(group='er_gen_tool.plugins')
        except TypeError:
            # Python 3.10+ API
            plugin_eps = entry_points().select(group='er_gen_tool.plugins')
        
        for ep in plugin_eps:
            try:
                plugin_cmd = ep.load()
                main.add_command(plugin_cmd, name=ep.name)
                logger.debug(f"Successfully loaded plugin: {ep.name}")
            except Exception as e:
                # Plugin loading failed, log but don't interrupt
                logger.warning(f"Failed to load plugin '{ep.name}': {e}")
    except Exception as e:
        # If entry_points fails entirely, continue without plugins
        logger.warning(f"Failed to discover plugins: {e}")


# Register core subcommands
from .convert import convert_cmd
from .migrate import makemigration_cmd, migrate_group

main.add_command(convert_cmd, name='convert')
main.add_command(makemigration_cmd, name='makemigration')
main.add_command(migrate_group, name='migrate')

# Load all plugins
load_plugins()


if __name__ == '__main__':
    main()
