import os
from typing import Any, Optional, List
import requests

class COREService:
    "Starter fro Core Service"
    search_url = "https://api.core.ac.uk/v3/search/works"
    _DEFAULT_TIMEOUT = 8
    
    def _build_query(
        self, authors: Optional[List[str]], paper_title: str, doi: Optional[str]
    ) -> str:
        
        if not any([authors, paper_title, doi]):
            return ""
        
        query_parts = []
        
        # DOI has priority and overrides other filters
        if doi and doi.strip():
            return f'doi:"{doi.strip()}"'
        # If DOI is not provided, build query based on authors and paper title
        if authors:
            query_parts.append(self._parse_authors(authors))
        if paper_title and paper_title.strip():
            query_parts.append(f'title:"{paper_title.strip()}"')
        return " AND ".join(query_parts)
    
    def _parse_authors(self, authors_data: Any) -> List[str]:
        # Authors are treated as an AND list. Each author is matched with a partial text match.
        if isinstance(authors_data, list):
            return " AND ".join([f'(author:"{author.strip()}")' for author in authors_data if isinstance(author, str) and author.strip()])
        return []
    
    def fetch_papers(
        self, authors: Optional[List[str]], paper_title: Optional[str], doi: Optional[str]
    ) -> list:
        query = self._build_query(authors, paper_title, doi)
        if not query:
            return []
        params = {
            "q": query,
            "limit": 100,
            "offset": 0
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
                timeout=self._DEFAULT_TIMEOUT
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