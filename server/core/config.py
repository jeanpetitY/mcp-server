import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_SERVER_NAME = "tib-mcp"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_TRANSPORT = "streamable-http"
DEFAULT_LOG_LEVEL = "INFO"

load_dotenv()


@dataclass(frozen=True)
class Settings:
    server_name: str
    host: str
    port: int
    transport: str
    log_level: str

    @property
    def fastmcp_transport(self) -> str:
        return normalize_transport(self.transport)


def get_settings() -> Settings:
    return Settings(
        server_name=os.getenv("MCP_SERVER_NAME", DEFAULT_SERVER_NAME),
        host=os.getenv("MCP_HOST", DEFAULT_HOST),
        port=int(os.getenv("MCP_PORT", str(DEFAULT_PORT))),
        transport=os.getenv("MCP_TRANSPORT", DEFAULT_TRANSPORT),
        log_level=os.getenv("MCP_LOG_LEVEL", DEFAULT_LOG_LEVEL),
    )


def normalize_transport(transport: str) -> str:
    value = transport.strip().lower()
    aliases = {
        "streamable_https": "streamable-http",
        "streamable_http": "streamable-http",
        "streamable-http": "streamable-http",
        "streamable-https": "streamable-http",
        "stdio": "stdio",
        "sse": "sse",
    }
    if value not in aliases:
        raise ValueError(
            "Unsupported MCP_TRANSPORT. Use one of: "
            "streamable_https, streamable_http, streamable-http, http, stdio, sse"
        )
    return aliases[value]
