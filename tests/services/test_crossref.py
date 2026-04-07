from server.services.crossref import CrossrefService


def test_get_title_and_abstract_normalizes_crossref_payload(monkeypatch):
    expected_payload = {
        "message": {
            "title": [" Test Title "],
            "abstract": "<jats:p>Hello <b>world</b>.</jats:p>",
        }
    }

    def fake_request_json(url, *, params, headers):
        assert url.endswith("/10.1000%2Fxyz")
        assert isinstance(params, dict)
        assert headers["Accept"] == "application/json"
        return expected_payload

    monkeypatch.setattr("server.services.crossref.request_json", fake_request_json)

    result = CrossrefService().get_title_and_abstract("doi:10.1000/xyz")

    assert result == {"title": "Test Title", "abstract": "Hello world."}


def test_get_title_and_abstract_rejects_empty_doi():
    service = CrossrefService()

    try:
        service.get_title_and_abstract(" ")
    except ValueError as exc:
        assert "doi must not be empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty DOI")
