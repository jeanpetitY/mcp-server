from fastmcp import FastMCP

from server.tools.sum import server as sum_server


def register_tools(app: FastMCP) -> None:
    app.mount(sum_server, namespace="sum")
