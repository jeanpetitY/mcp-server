async def test_tool_count(mcp_client):
    tools = await mcp_client.list_tools()
    assert len(tools) == 1


async def test_sum_tool_metadata(mcp_client):
    tools = await mcp_client.list_tools()
    tool = next(t for t in tools if t.name == "sum_add")

    assert "Add two numbers" in tool.description

    schema = tool.inputSchema
    assert "a" in schema["properties"]
    assert "b" in schema["properties"]
    assert schema["properties"]["a"]["type"] == "number"
    assert schema["properties"]["b"]["type"] == "number"
    assert "a" in schema["required"]
    assert "b" in schema["required"]
