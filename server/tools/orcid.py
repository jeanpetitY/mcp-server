from fastmcp import FastMCP

from server.services import ORCIDService

server = FastMCP("orcid")
orcid_service = ORCIDService()


@server.tool()
def get_titles(orcid: str) -> list[str]:
    """Look up an ORCID record and return the list of public work titles."""
    return orcid_service.get_titles(orcid)
