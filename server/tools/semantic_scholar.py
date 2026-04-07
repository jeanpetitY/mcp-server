from typing import Any

from fastmcp import FastMCP

from server.services import SemanticScholarService

server = FastMCP("semantic_scholar")
semantic_scholar_service = SemanticScholarService()


@server.tool()
def search_papers(keywords: str) -> list[dict[str, Any]]:
    """Search Semantic Scholar by keywords and return normalized article metadata."""
    return semantic_scholar_service.search_papers(keywords)
