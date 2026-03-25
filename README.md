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

## Configuration

All configuration is done through environment variables. A `.env` file in the project root is automatically loaded on startup via [python-dotenv](https://pypi.org/project/python-dotenv/). See `.env.example` for a documented template.

| Variable | Description | Default | Valid Values |
|---|---|---|---|
| `MCP_TRANSPORT` | Transport protocol | `streamable-http` | `stdio`, `http`, `sse`, `streamable-http` |
| `MCP_HOST` | Bind address (non-stdio transports) | `127.0.0.1` | Any valid host/IP |
| `MCP_PORT` | Port number (non-stdio transports) | `8000` | Any valid port |
| `MCP_LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

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
├── main.py                  # Entry point — starts the MCP server
├── pyproject.toml            # Project metadata, dependencies, and tool config
├── uv.lock                  # Deterministic dependency lock file
├── Dockerfile               # Production container build
├── .env.example             # Documented environment variable template
├── .pre-commit-config.yaml  # Pre-commit hooks (Ruff linter & formatter)
├── server/
│   ├── main.py              # Loads config from environment, creates app instance
│   ├── app.py               # App factory — creates FastMCP and registers tools
│   └── tools/
│       ├── __init__.py      # Tool registration — mounts sub-servers onto the app
│       └── sum.py           # Example tool: adds two numbers
└── tests/
    ├── conftest.py          # Shared fixtures (mcp_app, mcp_client)
    ├── test_config.py       # Configuration tests
    ├── test_contract.py     # Tool schema/contract tests
    ├── test_integration.py  # Integration tests
    └── tools/
        └── test_sum.py      # Unit tests for the sum tool
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

Tools follow a sub-server pattern. Use `server/tools/sum.py` as a reference:

**1. Create a new tool file** in `server/tools/`:

```python
# server/tools/my_tool.py
from fastmcp import FastMCP

server = FastMCP("my_tool")


@server.tool()
def do_something(param: str) -> str:
    """Short description of what this tool does.

    Args:
        param: Description of the parameter.

    Returns:
        Description of the return value.
    """
    return f"Result: {param}"
```

Type hints define the tool's input schema and docstrings become the tool description — both are exposed to MCP clients.

**2. Register it** in `server/tools/__init__.py`:

```python
from server.tools.my_tool import server as my_tool_server


def register_tools(app: FastMCP) -> None:
    app.mount(sum_server, namespace="sum")
    app.mount(my_tool_server, namespace="my_tool")
```

The tool will be discoverable as `my_tool_do_something` (namespace + function name).

**3. Add tests** in `tests/tools/test_my_tool.py` for unit tests, and update `tests/test_contract.py` and `tests/test_integration.py` as needed.

## License

This project is licensed under the [MIT License](LICENSE). © 2026 ORKG/TIB Team
