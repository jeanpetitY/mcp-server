from fastmcp import FastMCP

from server.core import get_settings
from server.tools import register_tools


def create_app() -> FastMCP:
    settings = get_settings()
    mcp = FastMCP(settings.server_name)
    register_tools(mcp)
    return mcp


def get_application() -> FastMCP:
    return create_app()
