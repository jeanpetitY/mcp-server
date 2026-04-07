from server.tools.core import fetch_papers


def test_fetch_papers_returns_service_result(monkeypatch):
    expected = [{"id": 1, "title": "Test Paper"}]

    def fake_fetch_papers(authors, paper_title, doi):
        assert authors == ["Ada Lovelace"]
        assert paper_title == "Analytical Engine"
        assert doi is None
        return expected

    monkeypatch.setattr(
        "server.tools.core.core_service.fetch_papers",
        fake_fetch_papers,
    )

    result = fetch_papers(
        authors=["Ada Lovelace"],
        paper_title="Analytical Engine",
    )

    assert result == expected


def test_fetch_papers_doi_is_forwarded(monkeypatch):
    expected = []

    def fake_fetch_papers(authors, paper_title, doi):
        assert authors is None
        assert paper_title is None
        assert doi == "10.1000/test"
        return expected

    monkeypatch.setattr(
        "server.tools.core.core_service.fetch_papers",
        fake_fetch_papers,
    )

    result = fetch_papers(doi="10.1000/test")

    assert result == expected
