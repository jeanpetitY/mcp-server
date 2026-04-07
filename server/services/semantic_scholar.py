from __future__ import annotations

import os
from typing import Any

from server.utils import build_headers, request_json

BULK_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
PAPER_BATCH_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
SEARCH_FIELDS = "paperId,title,url"
DETAIL_FIELDS = "paperId,title,url,externalIds,authors,abstract"
DEFAULT_RESULT_COUNT = 10


class SemanticScholarService:
    """Business logic for Semantic Scholar paper search."""

    def search_papers(self, keywords: str) -> list[dict[str, Any]]:
        cleaned_keywords = keywords.strip()
        if not cleaned_keywords:
            raise ValueError("keywords must not be empty.")

        headers = self._semantic_scholar_headers()
        search_payload = request_json(
            BULK_SEARCH_URL,
            params={
                "query": cleaned_keywords,
                "fields": SEARCH_FIELDS,
            },
            headers=headers,
        )

        candidate_papers = search_payload.get("data", [])[:DEFAULT_RESULT_COUNT]
        paper_ids = [
            paper.get("paperId")
            for paper in candidate_papers
            if isinstance(paper, dict) and paper.get("paperId")
        ]
        if not paper_ids:
            return []

        details_payload = request_json(
            PAPER_BATCH_URL,
            method="POST",
            params={"fields": DETAIL_FIELDS},
            json_body={"ids": paper_ids},
            headers=headers,
        )

        return [
            self._normalize_paper(paper)
            for paper in details_payload
            if isinstance(paper, dict) and paper.get("paperId")
        ]

    def _semantic_scholar_headers(self) -> dict[str, str]:
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        return build_headers({"x-api-key": api_key} if api_key else None)

    def _normalize_paper(self, paper: dict[str, Any]) -> dict[str, Any]:
        paper_id = paper.get("paperId")
        url = paper.get("url") or (
            f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else None
        )

        return {
            "id": paper_id,
            "title": paper.get("title"),
            "url": url,
            "doi": self._extract_doi(paper),
            "authors": [
                author.get("name")
                for author in paper.get("authors", [])
                if isinstance(author, dict) and author.get("name")
            ],
            "abstract": paper.get("abstract"),
        }

    def _extract_doi(self, paper: dict[str, Any]) -> str | None:
        external_ids = paper.get("externalIds", {})
        if isinstance(external_ids, dict):
            doi = external_ids.get("DOI")
            if doi:
                return str(doi)
        return None
