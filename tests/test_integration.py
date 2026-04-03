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
        {"author_name": "", "paper_title": "machine learning", "affiliation": ""},
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
