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
