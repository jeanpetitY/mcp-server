from __future__ import annotations

from server.utils import build_headers, request_json

PUBLIC_API_BASE_URL = "https://pub.orcid.org/v3.0"


class ORCIDService:
    """Business logic for querying public ORCID records."""

    def get_titles(self, orcid: str) -> list[str]:
        normalized_orcid = self._normalize_orcid(orcid)
        payload = request_json(
            f"{PUBLIC_API_BASE_URL}/{normalized_orcid}/works",
            headers=build_headers(),
        )

        titles: list[str] = []
        seen_titles: set[str] = set()

        for group in payload.get("group", []):
            work_summary = self._select_preferred_work_summary(
                group.get("work-summary", [])
            )
            title = self._extract_title(work_summary)
            if not title or title in seen_titles:
                continue

            seen_titles.add(title)
            titles.append(title)

        return titles

    def _normalize_orcid(self, orcid: str) -> str:
        cleaned_orcid = orcid.strip()
        if not cleaned_orcid:
            raise ValueError("orcid must not be empty.")

        prefixes = ("https://orcid.org/", "http://orcid.org/", "orcid:")
        lower_value = cleaned_orcid.lower()
        for prefix in prefixes:
            if lower_value.startswith(prefix):
                return cleaned_orcid[len(prefix) :].strip()
        return cleaned_orcid

    def _select_preferred_work_summary(
        self, work_summaries: list[dict[str, object]]
    ) -> dict[str, object]:
        if not work_summaries:
            return {}

        return max(
            work_summaries,
            key=lambda summary: int(summary.get("display-index", "0") or 0),
        )

    def _extract_title(self, work_summary: dict[str, object]) -> str | None:
        title = work_summary.get("title", {})
        if not isinstance(title, dict):
            return None

        nested_title = title.get("title", {})
        if not isinstance(nested_title, dict):
            return None

        title_value = nested_title.get("value")
        return title_value.strip() if isinstance(title_value, str) else None
