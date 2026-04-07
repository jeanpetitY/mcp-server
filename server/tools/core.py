from fastmcp import FastMCP
from server.services import COREService
from typing import Optional, List

server = FastMCP("core")
core_service = COREService()

@server.tool()
def fetch_papers(authors: Optional[List[str]] = None, paper_title: Optional[str] = None, doi: Optional[str] = None) -> list:
    """Search papers in CORE using authors, title, and/or DOI.

    At least one filter should be provided (`authors`, `paper_title`, or `doi`).
    The tool forwards your filters to the CORE Works Search API and returns a
    normalized list of papers with these fields:
    `id`, `title`, `abstract`, `doi`, `year`, `authors`, and `url`.

    Query behavior:
    - If `doi` is provided, it has priority and is used as the only criterion.
      In that case, `authors` and `paper_title` are ignored.
    - If `doi` is not provided:
      - `authors` is interpreted as an AND list. Each returned paper must match
        all author names provided in the input list.
      - If both `authors` and `paper_title` are provided, they are combined
        with AND. Returned papers must match both the author constraints and
        the title constraint.
      - If only `authors` or only `paper_title` is provided, only that filter
        is applied.
    - Title and author matching are partial text matches (not exact matches):
      - `paper_title="machine learning"` can match titles that contain
        "machine learning".
      - `authors=["Allard"]` can match author names that contain "Allard".

    Args:
        authors (Optional[List[str]]): Author names used as AND conditions.
        paper_title (Optional[str]): Paper title used as a title constraint.
        doi (Optional[str]): DOI value. If provided, overrides other filters.

    Returns:
        list: A list of papers matching the effective query rules above.

    Examples:
        Example 1 (authors list is AND):
        ```python
            fetch_papers(authors=["Allard Oelen", "Yaser"])
        ```
            -> [papers containing BOTH authors]
        

        Example 2 (authors + title is AND):
        ```python
            fetch_papers(
                authors=["Ashish Vaswani"],
                paper_title="Attention Is All You Need"
            )
        ```
            -> [papers matching BOTH the author and the title]

        Example 3 (non-exact text matching):
        ```python
            fetch_papers(authors=["Allard"], paper_title="machine learning")
        ```
            -> [papers where author/title contain these terms]

        Example 4 (DOI overrides authors/title):
        ```python
            fetch_papers(
                authors=["Any Author"],
                paper_title="Any Title",
                doi="10.1038/nphys1170"
            )
        ```
            -> [papers matched by DOI only]
    """
    return core_service.fetch_papers(authors, paper_title, doi)