import os

from dotenv import load_dotenv

from server.app import create_app

load_dotenv()

mcp = create_app()

TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")
HOST = os.getenv("MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_PORT", "8000"))
LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO")
