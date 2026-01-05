"""
MCP Server for ER Diagram Converter.

This module provides a Model Context Protocol (MCP) server implementation
that exposes ER diagram conversion capabilities to MCP-compatible clients like Cursor.
"""

from x007007007.er_mcp.server import create_mcp_server

__all__ = ['create_mcp_server']

