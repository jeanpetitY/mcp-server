from __future__ import annotations

from html import unescape
import os
import re
from urllib.parse import quote

from server.utils import build_headers, request_json

WORKS_URL = "https://api.crossref.org/works"
TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")
SPACE_BEFORE_PUNCTUATION_PATTERN = re.compile(r"\s+([.,;:!?])")


class CrossrefService:
    """Business logic for querying Crossref metadata."""

    def get_title_and_abstract(self, doi: str) -> dict[str, str | None]:
        normalized_doi = self._normalize_doi(doi)
        payload = request_json(
            f"{WORKS_URL}/{quote(normalized_doi, safe='')}",
            params=self._crossref_params(),
            headers=build_headers(),
        )
        message = payload.get("message", {})
        title_values = message.get("title") or []

        return {
            "title": title_values[0].strip() if title_values else None,
            "abstract": self._strip_jats_markup(message.get("abstract")),
        }

    def _normalize_doi(self, doi: str) -> str:
        cleaned_doi = doi.strip()
        if not cleaned_doi:
            raise ValueError("doi must not be empty.")

        prefixes = ("https://doi.org/", "http://doi.org/", "doi:")
        lower_value = cleaned_doi.lower()
        for prefix in prefixes:
            if lower_value.startswith(prefix):
                return cleaned_doi[len(prefix) :].strip()
        return cleaned_doi

    def _crossref_params(self) -> dict[str, str]:
        mailto = os.getenv("CROSSREF_MAILTO")
        return {"mailto": mailto} if mailto else {}

    def _strip_jats_markup(self, abstract: str | None) -> str | None:
        if not abstract:
            return None

        text = TAG_PATTERN.sub(" ", abstract)
        text = WHITESPACE_PATTERN.sub(" ", unescape(text)).strip()
        return SPACE_BEFORE_PUNCTUATION_PATTERN.sub(r"\1", text)
