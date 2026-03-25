import importlib

from fastmcp import FastMCP

from server.app import create_app


def test_create_app_returns_fastmcp():
    app = create_app()
    assert isinstance(app, FastMCP)
    assert app.name == "tib-mcp"


def test_default_env_values(monkeypatch):
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)
    monkeypatch.delenv("MCP_HOST", raising=False)
    monkeypatch.delenv("MCP_PORT", raising=False)
    monkeypatch.delenv("MCP_LOG_LEVEL", raising=False)

    import server.main

    importlib.reload(server.main)

    assert server.main.TRANSPORT == "streamable-http"
    assert server.main.HOST == "127.0.0.1"
    assert server.main.PORT == 8000
    assert server.main.LOG_LEVEL == "INFO"


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "sse")
    monkeypatch.setenv("MCP_HOST", "0.0.0.0")
    monkeypatch.setenv("MCP_PORT", "9090")
    monkeypatch.setenv("MCP_LOG_LEVEL", "DEBUG")

    import server.main

    importlib.reload(server.main)

    assert server.main.TRANSPORT == "sse"
    assert server.main.HOST == "0.0.0.0"
    assert server.main.PORT == 9090
    assert server.main.LOG_LEVEL == "DEBUG"
