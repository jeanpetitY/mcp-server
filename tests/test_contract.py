async def test_tool_count(mcp_client):
    tools = await mcp_client.list_tools()
    assert len(tools) == 5


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

    assert "authors" in schema["properties"]
    assert "paper_title" in schema["properties"]
    assert "doi" in schema["properties"]
    assert schema["properties"]["authors"]["anyOf"][0]["type"] == "array"
    assert schema["properties"]["paper_title"]["anyOf"][0]["type"] == "string"
    assert schema["properties"]["doi"]["anyOf"][0]["type"] == "string"
    assert schema.get("required", []) == []


async def test_crossref_tool_metadata(mcp_client):
    tools = await mcp_client.list_tools()
    tool = next(t for t in tools if t.name == "crossref_get_title_and_abstract")

    assert "Crossref work by DOI" in tool.description
    schema = tool.inputSchema

    assert "doi" in schema["properties"]
    assert schema["properties"]["doi"]["type"] == "string"
    assert "doi" in schema["required"]


async def test_orcid_tool_metadata(mcp_client):
    tools = await mcp_client.list_tools()
    tool = next(t for t in tools if t.name == "orcid_get_titles")

    assert "ORCID record" in tool.description
    schema = tool.inputSchema

    assert "orcid" in schema["properties"]
    assert schema["properties"]["orcid"]["type"] == "string"
    assert "orcid" in schema["required"]


async def test_semantic_scholar_tool_metadata(mcp_client):
    tools = await mcp_client.list_tools()
    tool = next(t for t in tools if t.name == "semantic_scholar_search_papers")

    assert "Semantic Scholar" in tool.description
    schema = tool.inputSchema

    assert "keywords" in schema["properties"]
    assert schema["properties"]["keywords"]["type"] == "string"
    assert "keywords" in schema["required"]
