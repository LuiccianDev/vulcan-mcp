"""Global pytest fixtures for vulcan-mcp."""

import pytest

import vulcan_mcp.server as mcp_server
from tests.harness.mock_vulcan import MockVulcanServer


@pytest.fixture
def mock_vulcan(monkeypatch):
    """Spin up an ephemeral Mock Vulcan server on a dynamic port and wire it to FastMCP."""
    server = MockVulcanServer(host="127.0.0.1", port=0)
    server.start()

    monkeypatch.setenv("VULCAN_MCP_HOST", "127.0.0.1")
    monkeypatch.setenv("VULCAN_MCP_PORT", str(server.port))
    monkeypatch.delenv("VULCAN_MCP_TOKEN", raising=False)

    # Point existing FastMCP client instance to the ephemeral port
    monkeypatch.setattr(mcp_server._client, "host", "127.0.0.1")
    monkeypatch.setattr(mcp_server._client, "port", server.port)

    try:
        yield server
    finally:
        server.stop()
