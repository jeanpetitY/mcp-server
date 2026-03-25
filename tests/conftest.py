import pytest
from fastmcp import Client

from server.app import create_app


@pytest.fixture
def mcp_app():
    return create_app()


@pytest.fixture
async def mcp_client(mcp_app):
    async with Client(mcp_app) as client:
        yield client
