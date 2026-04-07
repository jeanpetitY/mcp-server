from server.tools.orcid import get_titles


def test_get_titles_returns_service_result(monkeypatch):
    expected = ["Paper A", "Paper B"]

    def fake_get_titles(orcid):
        assert orcid == "0000-0002-1825-0097"
        return expected

    monkeypatch.setattr(
        "server.tools.orcid.orcid_service.get_titles",
        fake_get_titles,
    )

    result = get_titles("0000-0002-1825-0097")

    assert result == expected
