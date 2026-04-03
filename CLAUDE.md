@AGENTS.md
## LangChain Clients (CLI + UI)

This repository includes two LangChain clients using OpenAI `gpt-4o-mini` and MCP tools:

- `client_langchain.py`: mcp client
- `app_streamlit.py`: graphical chat interface (Streamlit)

### Setup

Add your OpenAI key in `.env`:

```bash
OPENAI_API_KEY=your_key_here
```

Start the MCP server:

```bash
uv run python main.py
```

GUI:

```bash
uv run streamlit run app_streamlit.py
```

### Client Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | _(required)_ | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model used by LangChain clients |
| `MCP_CLIENT_TRANSPORT` | `streamable-http` | MCP transport (`streamable-http`, `sse`, `stdio`) |
| `MCP_CLIENT_URL` | `http://127.0.0.1:8000/mcp` | MCP URL for HTTP/SSE transports |
| `MCP_CLIENT_COMMAND` | `uv` | Command used in `stdio` mode |
