"""
CLI entry point for MCP server.
"""

import sys
import click
from x007007007.er.version import get_version
from x007007007.er_mcp.server import main as server_main


@click.command()
@click.version_option(version=get_version(), prog_name="er-mcp")
def main():
    """ER Diagram Converter MCP Server."""
    server_main()


if __name__ == "__main__":
    main()

