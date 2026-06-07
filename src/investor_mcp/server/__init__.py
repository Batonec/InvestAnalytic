"""MCP server surface (FastMCP): registers the investor tools and resources."""

from .app import mcp, service, main
from . import resources, tools, prompts  # noqa: F401
