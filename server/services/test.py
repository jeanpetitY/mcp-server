import os
from typing import Any, Optional

import requests


class COREService:
    """Starter for CORE Service."""

    _SEARCH_URL = "https://api.core.ac.uk/v3/search/works"
    _DEFAULT_TIMEOUT = 8

    def fetch_papers(
        self, author_name: str, paper_title: str, affiliation: Optional[str]
    ) -> list:
        """Search papers in CORE using author, title and optional affiliation."""
        query = self._build_query(author_name, paper_title, affiliation)
        print(query)
        if not query:
            print("True")
            return []

        headers = {"Accept": "application/json"}
        api_key = os.getenv("CORE_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.get(
                self._SEARCH_URL,
                params={"q": query, "limit": 100, "offset": 0},
                headers=headers,
                timeout=self._DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
            # print(payload)
        except (requests.RequestException, ValueError):
            return []

        return self._normalize_results(payload)

    def _build_query(
        self, author_name: str, paper_title: str, affiliation: Optional[str]
    ) -> str:
        query_parts = []
        if paper_title.strip():
            query_parts.append(f'title:"{paper_title.strip()}"')
        if author_name.strip():
            query_parts.append(f'authors:"{author_name.strip()}"')
        if affiliation and affiliation.strip():
            query_parts.append(f'authors.affiliation.name:"{affiliation.strip()}"')
        return " OR ".join(query_parts)

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
                    "doi": item.get("doi"),
                    "year": item.get("yearPublished") or item.get("year"),
                    "authors": item.get("authors", []),
                    "url": item.get("downloadUrl") or item.get("sourceFulltextUrls"),
                }
            )
        return papers