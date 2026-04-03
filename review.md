I reviewed the code, and it runs locally without issues. However, based on the provided template and Allard's issue description, I propose updating the scaffolding according to the points below.


## Blocking Findings
### 1) Missing architecture refactor (`core/services/utils`)
- **Expected**: Introduce `server/core/`, `server/services/`, and `server/utils/` to separate configuration, business logic, and runtime helpers.
- **Current in this commit**: These modules are not introduced.
- **Requested changes**:
  - Add `server/core/config.py` and `server/core/__init__.py`.
  - Add `server/services/sum.py` and `server/services/__init__.py`.
  - Add `server/utils/runtime.py` and `server/utils/__init__.py`.

### 2) Runtime bootstrap not aligned with target design
- **Files**: `main.py`, `server/main.py`, `server/app.py`
- **Expected**:
  - `server/main.py` should be the runtime source of truth (`TRANSPORT`, `HOST`, `PORT`, `LOG_LEVEL`, and `run()`).
  - `main.py` should delegate to `server.main.run()`.
  - `server/app.py` should build the app from `Settings` (including `MCP_SERVER_NAME`).
- **Current in this commit**: These updates are missing.
- **Requested changes**:
  - Align entrypoints and app factory with the target scaffolding.

### 3) `sum` tool not aligned with service layer
- **Files**: `server/tools/sum.py`, `server/services/sum.py`, `server/services/__init__.py`
- **Expected**: The tool should call a dedicated service (`SumService`) instead of keeping logic inline.
- **Current in this commit**: Service-based separation is not implemented.
- **Requested changes**:
  - Introduce `SumService` and wire it into `server/tools/sum.py`.
  - Export the service properly in `server/services/__init__.py`.

### 4) Incomplete environment/config updates
I suggest adding the MCP_SERVER_NAME as an environment variable, since the project is open source and users should not need to modify the source code to update the server name.

### 5) Incomplete usage documentation
- **File**: `README.md`
- **Expected**:
  - Updated architecture section,
  - "Adding a New Tool" section aligned with service + sub-server + mount + tests,
  - Mention of `@modelcontextprotocol/inspector`.
- **Current in this commit**: These additions are not present.
- **Requested changes**:
  - Update the README to match the intended scaffolding.

## Validation Required After Changes

```bash
uv run pytest
uv run pre-commit run --all-files
```

### 6) Proposed Project Structure (Target Architecture)
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
├── LICENSE
└── README.md
```

## Answer to Yaser MR comment
Thanks for addressing the comments and for the clarification, that makes sense.

I noticed one remaining issue. When a user clones the repository and installs dependencies using uv sync, then copies the content of .env.example into a .env file, the server raises the following error:

``TypeError: TransportMixin.run_stdio_async() got an unexpected keyword argument 'host'``

In core/config.py, the default transport is already set to streamable-http, but in the .env file it is still set to stdio. We should align this by updating the environment variable to streamable-http in .env.example.

Additionally, this error indicates that the runtime configuration does not properly handle transport-specific arguments. The logic in runtime.py should ensure that host (and similar parameters) are only passed when using transports like streamable-http or sse, and not when using stdio.

Fixing both the environment configuration and the transport handling logic should resolve the issue.

Regarding the reasoning behind points 1, 2, and 3:

- The introduction of core, services, and utils aims to enforce a clear separation of concerns: configuration (core), business logic (services), and runtime/helpers (utils). This improves maintainability and scalability as the project grows.
- Aligning server/main.py as the runtime source of truth ensures a single, consistent entry point for configuration and execution, avoiding duplication and making the application easier to reason about.
- Moving the logic into a dedicated SumService follows a service-oriented approach, which keeps tools thin and reusable, and makes testing and future extensions easier.

That was the main intention behind these suggestions.