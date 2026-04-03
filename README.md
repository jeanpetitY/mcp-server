# TIB MCP

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for scholarly tools, built with [FastMCP](https://gofastmcp.com/). MCP is an open standard that lets AI assistants interact with external tools and data sources through a unified protocol. This server exposes scholarly tools that any MCP-compatible client can discover and invoke.

## Prerequisites

- **Python 3.14+** — the project includes a `.python-version` file for tool compatibility
- **[uv](https://docs.astral.sh/uv/)** — used as the package manager, build system, and script runner

## Quick Start

```bash
# Clone the repository
git clone https://gitlab.com/TIBHannover/orkg/tib-aissistant/tib-mcp.git
cd tib-mcp

# Create your local environment file
cp .env.example .env

# Install all dependencies (including dev tools)
uv sync

# Start the server
uv run python main.py
```

By default the server starts in **streamable-http** mode, which is suitable for networked or remote access. For local MCP client integrations (e.g. Claude Desktop, VS Code with Copilot), you can switch to **stdio** mode.

## Architecture

The runtime is split into small layers:

- `main.py` and `server/main.py` are entry points that start the FastMCP server.
- `server/app.py` builds the application instance (`create_app`) and registers tools.
- `server/core/` contains environment-based configuration (`Settings`, transport normalization).
- `server/tools/` exposes MCP tools and mounts them by namespace.
- `server/services/` contains business logic used by tools.
- `server/utils/` contains runtime helpers (for example transport-specific run kwargs).

## Configuration

All configuration is done through environment variables. A `.env` file in the project root is automatically loaded on startup via [python-dotenv](https://pypi.org/project/python-dotenv/). See `.env.example` for a documented template.

| Variable | Description | Default | Valid Values |
|---|---|---|---|
| `MCP_SERVER_NAME` | Server Name     | `TIB MCP Server` | any name |
| `MCP_TRANSPORT`   | Transport protocol | `streamable-http` | `stdio`, `http`, `sse`, `streamable-http` |
| `MCP_HOST`        | Bind address (non-stdio transports) | `127.0.0.1` | Any valid host/IP |
| `MCP_PORT`        | Port number (non-stdio transports) | `8000` | Any valid port |
| `MCP_LOG_LEVEL`   | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

## Running the Server

### stdio Mode

Designed for direct integration with AI clients. The client launches the server as a subprocess and communicates over stdin/stdout:

```bash
uv run python main.py
```

For example, to configure this server in an MCP client, point it at:

```json
{
  "mcpServers": {
    "tib-mcp": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/path/to/tib-mcp"
    }
  }
}
```

### HTTP Mode

For networked or remote access, use the `streamable-http` transport:

```bash
# Via .env file
MCP_TRANSPORT=streamable-http

# Or inline
MCP_TRANSPORT=streamable-http uv run python main.py
```

The server will be available at `http://127.0.0.1:8000/mcp`.

## Try It with MCP Inspector

You can play around with the server using [`@modelcontextprotocol/inspector`](https://www.npmjs.com/package/@modelcontextprotocol/inspector):

```bash
# Inspect via stdio (launches this server as a subprocess)
npx @modelcontextprotocol/inspector uv run python main.py
```

If your server is already running in `streamable-http` mode:

```bash
npx @modelcontextprotocol/inspector
```

Then connect to `http://127.0.0.1:8000/mcp` from the Inspector UI.

## Docker

The project includes a production-ready Dockerfile that defaults to `streamable-http` transport on `0.0.0.0:8000`:

```bash
# Build the image
docker build -t tib-mcp .

# Run the container
docker run -p 8000:8000 tib-mcp
```

Override configuration with environment variables:

```bash
docker run -e MCP_LOG_LEVEL=DEBUG -p 8000:8000 tib-mcp
```

## Running Tests

```bash
uv run pytest
```

The test suite is organized into four categories:

| Category | Location | Description |
|---|---|---|
| **Unit** | `tests/tools/test_sum.py` | Direct function-level tests for each tool |
| **Config** | `tests/test_config.py` | Validates environment variable defaults and overrides |
| **Contract** | `tests/test_contract.py` | Verifies tool metadata, descriptions, and JSON schemas |
| **Integration** | `tests/test_integration.py` | End-to-end MCP client/server communication tests |

For verbose output:

```bash
uv run pytest -v
```

## Project Structure

```
tib-mcp/
├── main.py                   # Root entry point for running the MCP server
├── server/
│   ├── __init__.py
│   ├── app.py                # App factory (create_app / get_application)
│   ├── main.py               # Server module entry point + exported runtime constants
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py         # Environment config + transport normalization
│   ├── services/
│   │   ├── __init__.py
│   │   └── sum.py            # Sum service logic
│   ├── tools/
│   │   ├── __init__.py       # Tool mounting (register_tools)
│   │   └── sum.py            # Sum MCP sub-server and tool definition
│   └── utils/
│       ├── __init__.py
│       └── runtime.py        # Runtime helpers (run kwargs per transport)
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures (mcp_app, mcp_client)
│   ├── test_config.py        # Configuration behavior tests
│   ├── test_contract.py      # Tool metadata/schema contract tests
│   ├── test_integration.py   # MCP client/server integration tests
│   └── tools/
│       ├── __init__.py
│       └── test_sum.py       # Unit tests for sum behavior
├── pyproject.toml            # Dependencies + tool configuration
├── uv.lock                   # Dependency lock file
├── Dockerfile                # Container image definition
├── .dockerignore
├── .env.example              # Environment variable template
├── .pre-commit-config.yaml   # Pre-commit hooks (Ruff + checks)
├── AGENTS.md                 # Repository instructions for coding agents
├── CLAUDE.md
├── LICENSE
└── README.md
```

## Development

### Pre-commit Hooks

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting, configured via pre-commit:

```bash
uv run pre-commit install
```

This runs automatically on every commit, or manually with:

```bash
uv run pre-commit run --all-files
```

### Adding a New Tool

Tools in this project follow the same pattern as `sum`: a service layer for logic, and a FastMCP sub-server for exposure.

1. **Create the service** in `server/services/my_tool.py`:

```python
class MyToolService:
    def do_something(self, param: str) -> str:
        return param.strip().upper()
```

2. **Export the service** in `server/services/__init__.py`:

```python
from server.services.my_tool import MyToolService

__all__ = ["SumService", "MyToolService"]
```

3. **Create the MCP tool sub-server** in `server/tools/my_tool.py`:

```python
from fastmcp import FastMCP

from server.services import MyToolService

server = FastMCP("my_tool")
my_tool_service = MyToolService()


@server.tool()
def do_something(param: str) -> str:
    """Short description of what this tool does.

    Args:
        param: Description of the parameter.

    Returns:
        Description of the return value.
    """
    return my_tool_service.do_something(param)

```

Type hints define the input schema, and the docstring is exposed to MCP clients as tool description.

4. **Mount the tool** in `server/tools/__init__.py`:

```python
from fastmcp import FastMCP

from server.tools.my_tool import server as my_tool_server
from server.tools.sum import server as sum_server


def register_tools(app: FastMCP) -> None:
    app.mount(sum_server, namespace="sum")
    app.mount(my_tool_server, namespace="my_tool")
```

With namespace mounting, this tool is discoverable as `my_tool_do_something`.

5. **Add/update tests**:
- Unit test in `tests/tools/test_my_tool.py` (direct function/service behavior).
- Contract test in `tests/test_contract.py` (tool name, description, schema, tool count).
- Integration test in `tests/test_integration.py` (call the tool via MCP client).

Then run:

```bash
uv run pytest
uv run pre-commit run --all-files
```

## License

This project is licensed under the [MIT License](LICENSE). © 2026 ORKG/TIB Team
