from fastmcp import FastMCP

from server.tools import register_tools


def create_app() -> FastMCP:
    app = FastMCP("tib-mcp")
    register_tools(app)
    return app
