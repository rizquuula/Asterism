"""Test MCP HTTP stream transport."""

from unittest.mock import MagicMock, patch

import pytest

from agent.mcp.transport_executor.http_stream import HTTPStreamTransport


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_start_success(mock_session_class):
    """Test successful start of HTTP stream transport."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.ok = True
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])

    assert transport._base_url == "http://localhost:8080"
    assert transport._session == mock_session
    mock_session.get.assert_called_once_with(
        "http://localhost:8080/health",
        timeout=30,
    )


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_start_no_url(mock_session_class):
    """Test start without URL raises error."""
    transport = HTTPStreamTransport()

    with pytest.raises(ValueError, match="HTTP transport requires server URL"):
        transport.start("test", [])


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_start_health_check_fails(mock_session_class):
    """Test start when health check fails."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.text = "Server Error"
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()

    with pytest.raises(RuntimeError, match="Server health check failed"):
        transport.start("test", ["http://localhost:8080"])


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_start_connection_error(mock_session_class):
    """Test start when connection fails."""
    import requests

    mock_session = MagicMock()
    mock_session.get.side_effect = requests.RequestException("Connection refused")
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()

    with pytest.raises(RuntimeError, match="HTTP connection failed"):
        transport.start("test", ["http://localhost:8080"])


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_stop(mock_session_class):
    """Test stopping HTTP stream transport."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.ok = True
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])
    transport.stop()

    mock_session.close.assert_called_once()
    assert transport._session is None
    assert transport._base_url is None


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_stop_no_session(mock_session_class):
    """Test stopping HTTP stream transport when no session exists."""
    transport = HTTPStreamTransport()
    transport.stop()

    # Should not raise any errors
    assert transport._session is None
    assert transport._base_url is None


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_is_alive_true(mock_session_class):
    """Test is_alive returns True when connected."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.ok = True
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])

    assert transport.is_alive() is True


def test_http_stream_transport_is_alive_false():
    """Test is_alive returns False when not connected."""
    transport = HTTPStreamTransport()
    assert transport.is_alive() is False


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_is_alive_no_session(mock_session_class):
    """Test is_alive returns False when session is None."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.ok = True
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])
    transport._session = None

    assert transport.is_alive() is False


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_is_alive_no_base_url(mock_session_class):
    """Test is_alive returns False when base_url is None."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.ok = True
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])
    transport._base_url = None

    assert transport.is_alive() is False


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_execute_tool_success(mock_session_class):
    """Test successful tool execution."""
    mock_session = MagicMock()
    mock_health_response = MagicMock()
    mock_health_response.ok = True
    mock_session.get.return_value = mock_health_response

    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.iter_lines.return_value = [
        b'{"result": "chunk1"}',
        b'{"result": "chunk2"}',
    ]
    mock_post_response.__enter__ = MagicMock(return_value=mock_post_response)
    mock_post_response.__exit__ = MagicMock(return_value=False)
    mock_session.post.return_value = mock_post_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])
    result = transport.execute_tool("test_tool", arg1="value1")

    assert result["success"] is True


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_execute_tool_not_connected(mock_session_class):
    """Test tool execution when not connected."""
    transport = HTTPStreamTransport()

    with pytest.raises(RuntimeError, match="HTTP transport is not connected"):
        transport.execute_tool("test_tool")


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_execute_tool_http_error(mock_session_class):
    """Test tool execution with HTTP error."""
    mock_session = MagicMock()
    mock_health_response = MagicMock()
    mock_health_response.ok = True
    mock_session.get.return_value = mock_health_response

    mock_post_response = MagicMock()
    mock_post_response.status_code = 500
    mock_post_response.text = "Internal Server Error"
    mock_post_response.__enter__ = MagicMock(return_value=mock_post_response)
    mock_post_response.__exit__ = MagicMock(return_value=False)
    mock_session.post.return_value = mock_post_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])
    result = transport.execute_tool("test_tool")

    assert result["success"] is False
    assert "HTTP error 500" in result["error"]


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_execute_tool_request_exception(mock_session_class):
    """Test tool execution with request exception."""
    import requests

    mock_session = MagicMock()
    mock_health_response = MagicMock()
    mock_health_response.ok = True
    mock_session.get.return_value = mock_health_response
    mock_session.post.side_effect = requests.RequestException("Network error")
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])
    result = transport.execute_tool("test_tool")

    assert result["success"] is False
    assert "HTTP request failed" in result["error"]


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_list_tools_success(mock_session_class):
    """Test listing tools successfully."""
    mock_session = MagicMock()
    mock_health_response = MagicMock()
    mock_health_response.ok = True
    mock_session.get.return_value = mock_health_response

    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.iter_lines.return_value = [b'{"tools": ["tool1", "tool2"]}']
    mock_post_response.__enter__ = MagicMock(return_value=mock_post_response)
    mock_post_response.__exit__ = MagicMock(return_value=False)
    mock_session.post.return_value = mock_post_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])
    tools = transport.list_tools()

    assert "tool1" in tools
    assert "tool2" in tools


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_list_tools_failure(mock_session_class):
    """Test listing tools when execution fails."""
    mock_session = MagicMock()
    mock_health_response = MagicMock()
    mock_health_response.ok = True
    mock_session.get.return_value = mock_health_response

    mock_post_response = MagicMock()
    mock_post_response.status_code = 500
    mock_post_response.text = "Error"
    mock_post_response.__enter__ = MagicMock(return_value=mock_post_response)
    mock_post_response.__exit__ = MagicMock(return_value=False)
    mock_session.post.return_value = mock_post_response
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])
    tools = transport.list_tools()

    assert tools == []


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_list_tools_not_connected(mock_session_class):
    """Test listing tools when not connected."""
    transport = HTTPStreamTransport()
    tools = transport.list_tools()

    assert tools == []


@patch("agent.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_transport_list_tools_exception(mock_session_class):
    """Test listing tools when exception occurs."""
    mock_session = MagicMock()
    mock_health_response = MagicMock()
    mock_health_response.ok = True
    mock_session.get.return_value = mock_health_response
    mock_session.post.side_effect = Exception("Unexpected error")
    mock_session_class.return_value = mock_session

    transport = HTTPStreamTransport()
    transport.start("test", ["http://localhost:8080"])
    tools = transport.list_tools()

    assert tools == []


if __name__ == "__main__":
    pytest.main([__file__])
