from server.core import Settings


def build_run_kwargs(settings: Settings) -> dict:
    if settings.fastmcp_transport in {"streamable-http", "http", "sse"}:
        return {
            "host": settings.host,
            "port": settings.port,
        }
    return {}
