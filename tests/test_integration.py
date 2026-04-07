async def test_list_tools_includes_sum(mcp_client):
    tools = await mcp_client.list_tools()
    tool_names = [t.name for t in tools]
    assert "sum_add" in tool_names


async def test_call_sum_tool(mcp_client):
    result = await mcp_client.call_tool("sum_add", {"a": 2, "b": 3})
    assert not result.is_error
    assert result.data == 5


async def test_call_sum_tool_missing_args(mcp_client):
    result = await mcp_client.call_tool(
        "sum_add",
        {},
        raise_on_error=False,
    )
    assert result.is_error


async def test_list_tools_includes_core(mcp_client):
    tools = await mcp_client.list_tools()
    tool_names = [t.name for t in tools]
    assert "core_fetch_papers" in tool_names


async def test_call_core_tool(mcp_client):
    result = await mcp_client.call_tool(
        "core_fetch_papers",
        {"paper_title": "machine learning"},
    )
    assert not result.is_error
    assert isinstance(result.data, list)


async def test_call_core_tool_missing_args(mcp_client):
    result = await mcp_client.call_tool(
        "core_fetch_papers",
        {},
        raise_on_error=False,
    )

    assert result.is_error


async def test_list_tools_include_new_scholarly_tools(mcp_client):
    tools = await mcp_client.list_tools()
    tool_names = {t.name for t in tools}

    assert "crossref_get_title_and_abstract" in tool_names
    assert "orcid_get_titles" in tool_names
    assert "semantic_scholar_search_papers" in tool_names


async def test_call_crossref_tool(mcp_client, monkeypatch):
    expected = {"title": "Example Title", "abstract": "Example abstract"}

    monkeypatch.setattr(
        "server.tools.crossref.crossref_service.get_title_and_abstract",
        lambda doi: expected if doi == "10.1000/test" else {},
    )

    result = await mcp_client.call_tool(
        "crossref_get_title_and_abstract",
        {"doi": "10.1000/test"},
    )
    assert not result.is_error
    assert result.data == expected


async def test_call_orcid_tool(mcp_client, monkeypatch):
    expected = ["Paper A", "Paper B"]

    monkeypatch.setattr(
        "server.tools.orcid.orcid_service.get_titles",
        lambda orcid: expected if orcid == "0000-0002-1825-0097" else [],
    )

    result = await mcp_client.call_tool(
        "orcid_get_titles",
        {"orcid": "0000-0002-1825-0097"},
    )
    assert not result.is_error
    assert result.data == expected


async def test_call_semantic_scholar_tool(mcp_client, monkeypatch):
    expected = [{"id": "p1", "title": "Paper"}]

    monkeypatch.setattr(
        "server.tools.semantic_scholar.semantic_scholar_service.search_papers",
        lambda keywords: expected if keywords == "transformers" else [],
    )

    result = await mcp_client.call_tool(
        "semantic_scholar_search_papers",
        {"keywords": "transformers"},
    )
    assert not result.is_error
    assert result.structured_content == {"result": expected}
