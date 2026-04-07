from fastmcp import FastMCP
from server.tools.sum import server as sum_server
from server.tools.core import server as core_server
from server.tools.crossref import server as crossref_server
from server.tools.orcid import server as orcid_server
from server.tools.semantic_scholar import server as semantic_scholar_server


def register_tools(app: FastMCP) -> None:
    app.mount(sum_server, namespace="sum")
    app.mount(core_server, namespace="core")
    app.mount(crossref_server, namespace="crossref")
    app.mount(orcid_server, namespace="orcid")
    app.mount(semantic_scholar_server, namespace="semantic_scholar")


__all__ = ["register_tools"]
