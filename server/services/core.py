import os
from typing import Any

import requests


class COREService:
    """Business logic for querying the CORE works API."""

    search_url = "https://api.core.ac.uk/v3/search/works"
    _DEFAULT_TIMEOUT = 8

    def _build_query(
        self,
        authors: list[str] | None,
        paper_title: str | None,
        doi: str | None,
    ) -> str:
        if doi and doi.strip():
            return f'doi:"{doi.strip()}"'

        query_parts: list[str] = []
        authors_query = self._parse_authors(authors)
        if authors_query:
            query_parts.append(authors_query)
        if paper_title and paper_title.strip():
            query_parts.append(f'title:"{paper_title.strip()}"')
        return " AND ".join(query_parts)

    def _parse_authors(self, authors_data: Any) -> str:
        if not isinstance(authors_data, list):
            return ""

        authors = [
            f'(author:"{author.strip()}")'
            for author in authors_data
            if isinstance(author, str) and author.strip()
        ]
        return " AND ".join(authors)

    def fetch_papers(
        self,
        authors: list[str] | None = None,
        paper_title: str | None = None,
        doi: str | None = None,
    ) -> list[dict[str, Any]]:
        query = self._build_query(authors, paper_title, doi)
        if not query:
            raise ValueError(
                "At least one filter must be provided: authors, paper_title, or doi."
            )

        params = {
            "q": query,
            "limit": 100,
            "offset": 0,
        }
        headers = {"Accept": "application/json"}
        api_key = os.getenv("CORE_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.get(
                self.search_url,
                params=params,
                headers=headers,
                timeout=self._DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            return []

        return self._normalize_results(payload)

    def _normalize_results(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        raw_results = payload.get("results", [])
        if not isinstance(raw_results, list):
            return []

        papers: list[dict[str, Any]] = []
        for item in raw_results:
            if not isinstance(item, dict):
                continue
            papers.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "abstract": item.get("abstract"),
                    "doi": item.get("doi"),
                    "year": item.get("yearPublished") or item.get("year"),
                    "authors": item.get("authors", []),
                    "url": item.get("downloadUrl") or item.get("sourceFulltextUrls"),
                }
            )
        return papers
