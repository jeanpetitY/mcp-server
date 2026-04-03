from server.app import create_app
from server.core import get_settings
from server.utils import build_run_kwargs

_settings = get_settings()
TRANSPORT = _settings.fastmcp_transport
HOST = _settings.host
PORT = _settings.port
LOG_LEVEL = _settings.log_level

mcp = create_app()


def run() -> None:
    mcp.run(transport=TRANSPORT, **build_run_kwargs(_settings))
