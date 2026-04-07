from server.services.semantic_scholar import SemanticScholarService


def test_search_papers_normalizes_results(monkeypatch):
    calls = []

    def fake_request_json(url, **kwargs):
        calls.append((url, kwargs))
        if url.endswith("/paper/search/bulk"):
            return {
                "data": [
                    {"paperId": "p1", "title": "One", "url": "https://example.org/one"},
                    {"paperId": "p2", "title": "Two"},
                ]
            }

        return [
            {
                "paperId": "p1",
                "title": "One",
                "url": "https://example.org/one",
                "externalIds": {"DOI": "10.1000/one"},
                "authors": [{"name": "Ada"}],
                "abstract": "Abstract One",
            },
            {
                "paperId": "p2",
                "title": "Two",
                "authors": [{"name": "Alan"}],
                "abstract": "Abstract Two",
            },
        ]

    monkeypatch.setattr(
        "server.services.semantic_scholar.request_json",
        fake_request_json,
    )

    result = SemanticScholarService().search_papers("transformers")

    assert len(calls) == 2
    assert result == [
        {
            "id": "p1",
            "title": "One",
            "url": "https://example.org/one",
            "doi": "10.1000/one",
            "authors": ["Ada"],
            "abstract": "Abstract One",
        },
        {
            "id": "p2",
            "title": "Two",
            "url": "https://www.semanticscholar.org/paper/p2",
            "doi": None,
            "authors": ["Alan"],
            "abstract": "Abstract Two",
        },
    ]


def test_search_papers_rejects_empty_keywords():
    service = SemanticScholarService()

    try:
        service.search_papers(" ")
    except ValueError as exc:
        assert "keywords must not be empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty keywords")
