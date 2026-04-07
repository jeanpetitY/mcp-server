from fastmcp import FastMCP

from server.services import CrossrefService

server = FastMCP("crossref")
crossref_service = CrossrefService()


@server.tool()
def get_title_and_abstract(doi: str) -> dict[str, str | None]:
    """Look up a Crossref work by DOI and return its title and abstract."""
    return crossref_service.get_title_and_abstract(doi)
