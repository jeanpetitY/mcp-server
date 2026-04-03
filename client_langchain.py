from __future__ import annotations

import os
import warnings
from collections.abc import AsyncIterator, Sequence

warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.",
    category=UserWarning,
)

from langchain.agents import create_agent  # noqa: E402
from langchain_mcp_adapters.client import MultiServerMCPClient  # noqa: E402
from langchain_openai import ChatOpenAI  # noqa: E402

DEFAULT_MCP_URL = "http://127.0.0.1:8000/mcp"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_STDIO_ARGS = ["run", "python", "main.py"]
SYSTEM_PROMPT = (
    "You are an assistant connected to MCP tools. "
    "Prefer using tools when they are relevant, then answer clearly in user query language."
)


def _normalize_transport(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_")
    aliases = {
        "streamablehttps": "streamable_http",
        "streamable_https": "streamable_http",
        "streamable_http": "streamable_http",
        "stdio": "stdio",
        "sse": "sse",
    }
    if normalized not in aliases:
        supported = ", ".join(sorted(aliases))
        msg = f"Unsupported MCP_CLIENT_TRANSPORT '{value}'. Use one of: {supported}"
        raise ValueError(msg)
    return aliases[normalized]


def _build_connections() -> dict[str, dict[str, object]]:
    transport = _normalize_transport(
        os.getenv("MCP_CLIENT_TRANSPORT", "streamable-http")
    )

    if transport == "stdio":
        command = os.getenv("MCP_CLIENT_COMMAND", "uv")
        return {
            "tib": {
                "transport": "stdio",
                "command": command,
                "args": DEFAULT_STDIO_ARGS,
                "cwd": os.getenv("MCP_CLIENT_CWD", os.getcwd()),
            }
        }

    if transport == "sse":
        url = os.getenv("MCP_CLIENT_URL", DEFAULT_MCP_URL)
        return {
            "tib": {
                "transport": "sse",
                "url": url,
            }
        }

    url = os.getenv("MCP_CLIENT_URL", DEFAULT_MCP_URL)
    return {
        "tib": {
            "transport": "streamable_http",
            "url": url,
        }
    }


def _extract_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, Sequence):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text")
                if text:
                    parts.append(str(text))
        if parts:
            return "\n".join(parts)
    return str(content)


async def _run_agent(user_prompt: str, model: str, temperature: float, list_tools: bool) -> str:
    client = MultiServerMCPClient(_build_connections())
    tools = await client.get_tools()

    if list_tools:
        return _format_tools_with_descriptions(tools)

    llm = ChatOpenAI(model=model, temperature=temperature)
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)

    result = await agent.ainvoke({"messages": [("user", user_prompt)]})
    return _extract_text(result["messages"][-1].content)


async def _stream_agent_response(
    user_prompt: str, model: str, temperature: float
) -> AsyncIterator[str]:
    client = MultiServerMCPClient(_build_connections())
    tools = await client.get_tools()

    llm = ChatOpenAI(model=model, temperature=temperature, streaming=True)
    agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)

    async for event in agent.astream_events(
        {"messages": [("user", user_prompt)]},
        version="v2",
    ):
        if event.get("event") != "on_chat_model_stream":
            continue
        chunk = event.get("data", {}).get("chunk")
        text = _extract_text(getattr(chunk, "content", ""))
        if text:
            yield text


def _format_tools_with_descriptions(tools: Sequence[object]) -> str:
    if not tools:
        return "No MCP tools found."
    lines = []
    for tool in tools:
        name = str(getattr(tool, "name", "unknown_tool"))
        description = str(getattr(tool, "description", "") or "").strip()
        if not description:
            description = "No description."
        # lines.append(f"- {name}: {description}")
        lines.append(f"{name}")
    return "\n".join(lines)
