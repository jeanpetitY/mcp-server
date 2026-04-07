from server.services.orcid import ORCIDService


def test_get_titles_returns_unique_titles(monkeypatch):
    payload = {
        "group": [
            {
                "work-summary": [
                    {"display-index": "0", "title": {"title": {"value": "Ignore me"}}},
                    {"display-index": "1", "title": {"title": {"value": "Paper A"}}},
                ]
            },
            {
                "work-summary": [
                    {"display-index": "3", "title": {"title": {"value": "Paper B"}}}
                ]
            },
            {
                "work-summary": [
                    {"display-index": "2", "title": {"title": {"value": "Paper A"}}}
                ]
            },
        ]
    }

    def fake_request_json(url, *, headers):
        assert url.endswith("/0000-0002-1825-0097/works")
        assert headers["Accept"] == "application/json"
        return payload

    monkeypatch.setattr("server.services.orcid.request_json", fake_request_json)

    result = ORCIDService().get_titles("https://orcid.org/0000-0002-1825-0097")

    assert result == ["Paper A", "Paper B"]


def test_get_titles_rejects_empty_orcid():
    service = ORCIDService()

    try:
        service.get_titles(" ")
    except ValueError as exc:
        assert "orcid must not be empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty ORCID")
