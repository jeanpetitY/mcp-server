from server.tools.semantic_scholar import search_papers


def test_search_papers_returns_service_result(monkeypatch):
    expected = [{"id": "p1", "title": "Test Paper"}]

    def fake_search_papers(keywords):
        assert keywords == "language models"
        return expected

    monkeypatch.setattr(
        "server.tools.semantic_scholar.semantic_scholar_service.search_papers",
        fake_search_papers,
    )

    result = search_papers("language models")

    assert result == expected
