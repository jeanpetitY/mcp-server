async def test_tool_count(mcp_client):
    tools = await mcp_client.list_tools()
    assert len(tools) == 2


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


async def test_core_tool_metadata(mcp_client):
    tools = await mcp_client.list_tools()
    tool = next(t for t in tools if t.name == "core_fetch_papers")

    assert "Search papers in CORE" in tool.description
    schema = tool.inputSchema

    assert "author_name" in schema["properties"]
    assert "paper_title" in schema["properties"]
    assert "affiliation" in schema["properties"]
    assert schema["properties"]["author_name"]["type"] == "string"
    assert schema["properties"]["paper_title"]["type"] == "string"
    assert "author_name" in schema["required"]
    assert "paper_title" in schema["required"]
    assert "affiliation" not in schema["required"]
