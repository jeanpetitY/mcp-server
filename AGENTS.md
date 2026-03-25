# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the server
uv run python main.py

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/tools/test_sum.py

# Run a single test by name
uv run pytest tests/test_integration.py::test_call_sum_tool

# Lint and format (runs Ruff)
uv run pre-commit run --all-files

# Install pre-commit hooks (one-time setup)
uv run pre-commit install
```

## Architecture

This is a [FastMCP](https://gofastmcp.com/) server exposing scholarly tools via the Model Context Protocol. The entry point is `main.py`, which delegates to `server/main.py` for config and `server/app.py` for the app factory.

### Tool sub-server pattern

Each tool lives in its own file under `server/tools/` and creates its own `FastMCP` instance (a "sub-server"). Tools are registered via the `@server.tool()` decorator. The sub-server is then **mounted** onto the main app in `server/tools/__init__.py`'s `register_tools()` function with a namespace.

- Tool names exposed to MCP clients follow the pattern `{namespace}_{function_name}` (e.g., `sum_add` from namespace `"sum"` and function `add`).
- Type hints define the JSON input schema; docstrings become the tool description visible to clients.

### Adding a new tool

1. Create `server/tools/my_tool.py` with a `FastMCP("my_tool")` instance and decorated functions.
2. Mount it in `server/tools/__init__.py`: `app.mount(my_tool_server, namespace="my_tool")`.
3. Add unit tests in `tests/tools/test_my_tool.py`; update `tests/test_contract.py` (tool count, metadata) and `tests/test_integration.py`.

### Configuration

All runtime config comes from environment variables (loaded via `python-dotenv` from `.env`):

| Variable | Default | Purpose |
|---|---|---|
| `MCP_TRANSPORT` | `streamable-http` | `stdio`, `http`, `sse`, or `streamable-http` |
| `MCP_HOST` | `127.0.0.1` | Bind address |
| `MCP_PORT` | `8000` | Port |
| `MCP_LOG_LEVEL` | `INFO` | Log verbosity |

Use `stdio` transport for direct AI client integrations (Claude Desktop, VS Code); use `streamable-http` for networked/remote access (also the Docker default on `0.0.0.0:8000`).

### Test categories

- `tests/tools/` — unit tests (direct function calls)
- `tests/test_config.py` — env var defaults/overrides
- `tests/test_contract.py` — tool count, metadata, JSON schema shape
- `tests/test_integration.py` — end-to-end via `fastmcp.Client` against the live app

Shared fixtures (`mcp_app`, `mcp_client`) live in `tests/conftest.py`. All tests are async; `asyncio_mode = "auto"` is set in `pyproject.toml`.

## Developement standards
- If you want to add or delete a dependency, use `uv add <dependency>` or `uv remove <dependency>` to ensure `uv.lock` is updated correctly. Never edit `uv.lock` and `pyproject.toml` manually.
