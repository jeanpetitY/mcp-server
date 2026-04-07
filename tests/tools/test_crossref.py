from server.tools.crossref import get_title_and_abstract


def test_get_title_and_abstract_returns_service_result(monkeypatch):
    expected = {"title": "Example", "abstract": "Example abstract"}

    def fake_get_title_and_abstract(doi):
        assert doi == "10.1000/test"
        return expected

    monkeypatch.setattr(
        "server.tools.crossref.crossref_service.get_title_and_abstract",
        fake_get_title_and_abstract,
    )

    result = get_title_and_abstract("10.1000/test")

    assert result == expected
