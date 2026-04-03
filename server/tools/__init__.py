from fastmcp import FastMCP
from server.tools.sum import server as sum_server
from server.tools.core import server as core_server


def register_tools(app: FastMCP) -> None:
    app.mount(sum_server, namespace="sum")
    app.mount(core_server, namespace="core")


__all__ = ["register_tools"]
