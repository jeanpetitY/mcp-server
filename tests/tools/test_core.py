from server.tools.core import fetch_papers


def test_fetch_papers_returns_service_result(monkeypatch):
    expected = [{"id": 1, "title": "Test Paper"}]

    def fake_fetch_papers(author_name, paper_title, affiliation):
        assert author_name == "Ada Lovelace"
        assert paper_title == "Analytical Engine"
        assert affiliation == "Babbage Lab"
        return expected

    monkeypatch.setattr(
        "server.tools.core.core_service.fetch_papers",
        fake_fetch_papers,
    )

    result = fetch_papers(
        author_name="Ada Lovelace",
        paper_title="Analytical Engine",
        affiliation="Babbage Lab",
    )

    assert result == expected


def test_fetch_papers_default_affiliation_is_none(monkeypatch):
    expected = []

    def fake_fetch_papers(author_name, paper_title, affiliation):
        assert author_name == "Alan Turing"
        assert paper_title == "Computing Machinery and Intelligence"
        assert affiliation is None
        return expected

    monkeypatch.setattr(
        "server.tools.core.core_service.fetch_papers",
        fake_fetch_papers,
    )

    result = fetch_papers(
        author_name="Alan Turing",
        paper_title="Computing Machinery and Intelligence",
    )

    assert result == expected
