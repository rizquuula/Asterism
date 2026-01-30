"""Test MCP transport factory function."""

import pytest

from agent.mcp.transport_executor import create_transport
from agent.mcp.transport_executor.http_stream import HTTPStreamTransport
from agent.mcp.transport_executor.sse import SSETransport
from agent.mcp.transport_executor.stdio import StdioTransport


def test_create_transport_stdio():
    """Test creating stdio transport."""
    transport = create_transport("stdio")
    assert isinstance(transport, StdioTransport)


def test_create_transport_sse():
    """Test creating SSE transport."""
    transport = create_transport("sse")
    assert isinstance(transport, SSETransport)


def test_create_transport_http_stream():
    """Test creating HTTP stream transport."""
    transport = create_transport("http_stream")
    assert isinstance(transport, HTTPStreamTransport)


def test_create_transport_invalid_type():
    """Test creating transport with invalid type raises error."""
    with pytest.raises(ValueError, match="Unsupported transport type: invalid"):
        create_transport("invalid")


def test_create_transport_unknown_type():
    """Test creating transport with unknown type raises error."""
    with pytest.raises(ValueError, match="Unsupported transport type: unknown"):
        create_transport("unknown")


def test_create_transport_case_sensitive():
    """Test that transport type is case sensitive."""
    with pytest.raises(ValueError, match="Unsupported transport type: STDIO"):
        create_transport("STDIO")

    with pytest.raises(ValueError, match="Unsupported transport type: SSE"):
        create_transport("SSE")


def test_create_transport_empty_string():
    """Test creating transport with empty string raises error."""
    with pytest.raises(ValueError, match="Unsupported transport type: "):
        create_transport("")


def test_create_transport_whitespace():
    """Test creating transport with whitespace string raises error."""
    with pytest.raises(ValueError, match="Unsupported transport type:   "):
        create_transport("  ")


if __name__ == "__main__":
    pytest.main([__file__])
