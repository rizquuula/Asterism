"""Unit tests for HTTPStreamTransport."""

from unittest.mock import MagicMock, patch

import pytest

from asterism.mcp.transport_executor.http_stream import HTTPStreamTransport


def test_http_stream_transport_init():
    """Test HTTPStreamTransport initialization."""
    transport = HTTPStreamTransport()
    assert transport._session is None
    assert transport._base_url is None
    assert transport._timeout == 30
    assert transport._request_id == 0
    assert transport._initialized is False
    assert transport._session_id is None


@patch("asterism.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_start_success(mock_session_class):
    """Test successful start and initialization."""
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock response for initialization
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"mcp-session-id": "test-session-123"}
    mock_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}}'
    ]
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_session.post.return_value = mock_response

    transport = HTTPStreamTransport()
    transport.start("http", ["http://localhost:3000"])

    assert transport._base_url == "http://localhost:3000"
    assert transport._session is not None
    assert transport._initialized is True
    assert transport._session_id == "test-session-123"


@patch("asterism.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_start_without_args_raises(mock_session_class):
    """Test start raises ValueError when args is empty."""
    transport = HTTPStreamTransport()
    with pytest.raises(ValueError, match="HTTP transport requires server URL in args"):
        transport.start("http", [])


@patch("asterism.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_execute_tool_success(mock_session_class):
    """Test successful tool execution."""
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock responses (init + notification + tool execution)
    mock_init_response = MagicMock()
    mock_init_response.ok = True
    mock_init_response.headers = {"mcp-session-id": "test-session-123"}
    mock_init_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}}'
    ]
    mock_init_response.__enter__ = MagicMock(return_value=mock_init_response)
    mock_init_response.__exit__ = MagicMock(return_value=False)

    mock_notification_response = MagicMock()
    mock_notification_response.ok = True
    mock_notification_response.iter_lines.return_value = []
    mock_notification_response.__enter__ = MagicMock(return_value=mock_notification_response)
    mock_notification_response.__exit__ = MagicMock(return_value=False)

    mock_tool_response = MagicMock()
    mock_tool_response.ok = True
    mock_tool_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "{\\"result\\": \\"success\\"}"}]}}'  # noqa: E501
    ]
    mock_tool_response.__enter__ = MagicMock(return_value=mock_tool_response)
    mock_tool_response.__exit__ = MagicMock(return_value=False)

    mock_session.post.side_effect = [mock_init_response, mock_notification_response, mock_tool_response]

    transport = HTTPStreamTransport()
    transport.start("http", ["http://localhost:3000"])

    result = transport.execute_tool("test_tool", param1="value1")

    assert result["success"] is True
    assert result["result"] == {"result": "success"}


@patch("asterism.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_list_tools_success(mock_session_class):
    """Test successful tools listing."""
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock responses (init + notification + list tools)
    mock_init_response = MagicMock()
    mock_init_response.ok = True
    mock_init_response.headers = {"mcp-session-id": "test-session-123"}
    mock_init_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}}'
    ]
    mock_init_response.__enter__ = MagicMock(return_value=mock_init_response)
    mock_init_response.__exit__ = MagicMock(return_value=False)

    mock_notification_response = MagicMock()
    mock_notification_response.ok = True
    mock_notification_response.iter_lines.return_value = []
    mock_notification_response.__enter__ = MagicMock(return_value=mock_notification_response)
    mock_notification_response.__exit__ = MagicMock(return_value=False)

    mock_list_response = MagicMock()
    mock_list_response.ok = True
    mock_list_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 3, "result": {"tools": [{"name": "tool1"}, {"name": "tool2"}]}}'
    ]
    mock_list_response.__enter__ = MagicMock(return_value=mock_list_response)
    mock_list_response.__exit__ = MagicMock(return_value=False)

    mock_session.post.side_effect = [mock_init_response, mock_notification_response, mock_list_response]

    transport = HTTPStreamTransport()
    transport.start("http", ["http://localhost:3000"])

    tools = transport.list_tools()

    assert "tool1" in tools
    assert "tool2" in tools


@patch("asterism.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_is_alive(mock_session_class):
    """Test is_alive returns correct state."""
    transport = HTTPStreamTransport()
    assert not transport.is_alive()

    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock response for initialization
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"mcp-session-id": "test-session-123"}
    mock_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}}'
    ]
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_session.post.return_value = mock_response

    transport.start("http", ["http://localhost:3000"])
    assert transport.is_alive()

    transport.stop()
    assert not transport.is_alive()


@patch("asterism.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_stop_closes_session(mock_session_class):
    """Test stop closes the session."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock response for initialization
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"mcp-session-id": "test-session-123"}
    mock_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}}'
    ]
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_session.post.return_value = mock_response

    transport = HTTPStreamTransport()
    transport.start("http", ["http://localhost:3000"])
    transport.stop()

    mock_session.close.assert_called_once()
    assert transport._session is None
    assert transport._base_url is None
    assert transport._initialized is False


@patch("asterism.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_execute_tool_non_json_response(mock_session_class):
    """Test tool execution with non-JSON response returns text."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock responses (init + notification + tool execution)
    mock_init_response = MagicMock()
    mock_init_response.ok = True
    mock_init_response.headers = {"mcp-session-id": "test-session-123"}
    mock_init_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}}'
    ]
    mock_init_response.__enter__ = MagicMock(return_value=mock_init_response)
    mock_init_response.__exit__ = MagicMock(return_value=False)

    mock_notification_response = MagicMock()
    mock_notification_response.ok = True
    mock_notification_response.iter_lines.return_value = []
    mock_notification_response.__enter__ = MagicMock(return_value=mock_notification_response)
    mock_notification_response.__exit__ = MagicMock(return_value=False)

    mock_tool_response = MagicMock()
    mock_tool_response.ok = True
    mock_tool_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "plain text result"}]}}'
    ]
    mock_tool_response.__enter__ = MagicMock(return_value=mock_tool_response)
    mock_tool_response.__exit__ = MagicMock(return_value=False)

    mock_session.post.side_effect = [mock_init_response, mock_notification_response, mock_tool_response]

    transport = HTTPStreamTransport()
    transport.start("http", ["http://localhost:3000"])

    result = transport.execute_tool("test_tool")

    assert result["success"] is True
    assert result["result"] == {"text": "plain text result"}


@patch("asterism.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_execute_tool_empty_content(mock_session_class):
    """Test tool execution with empty content."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock responses (init + notification + tool execution)
    mock_init_response = MagicMock()
    mock_init_response.ok = True
    mock_init_response.headers = {"mcp-session-id": "test-session-123"}
    mock_init_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}}'
    ]
    mock_init_response.__enter__ = MagicMock(return_value=mock_init_response)
    mock_init_response.__exit__ = MagicMock(return_value=False)

    mock_notification_response = MagicMock()
    mock_notification_response.ok = True
    mock_notification_response.iter_lines.return_value = []
    mock_notification_response.__enter__ = MagicMock(return_value=mock_notification_response)
    mock_notification_response.__exit__ = MagicMock(return_value=False)

    mock_tool_response = MagicMock()
    mock_tool_response.ok = True
    mock_tool_response.iter_lines.return_value = [b'data: {"jsonrpc": "2.0", "id": 3, "result": {"content": []}}']
    mock_tool_response.__enter__ = MagicMock(return_value=mock_tool_response)
    mock_tool_response.__exit__ = MagicMock(return_value=False)

    mock_session.post.side_effect = [mock_init_response, mock_notification_response, mock_tool_response]

    transport = HTTPStreamTransport()
    transport.start("http", ["http://localhost:3000"])

    result = transport.execute_tool("test_tool")

    assert result["success"] is True
    assert result["result"] == {}


@patch("asterism.mcp.transport_executor.http_stream.requests.Session")
def test_http_stream_list_tools_not_initialized_returns_empty(mock_session_class):
    """Test list_tools returns empty list when not initialized."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock response for initialization
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"mcp-session-id": "test-session-123"}
    mock_response.iter_lines.return_value = [
        b'data: {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}}'
    ]
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_session.post.return_value = mock_response

    transport = HTTPStreamTransport()
    transport.start("http", ["http://localhost:3000"])
    transport._initialized = False

    tools = transport.list_tools()
    assert tools == []


if __name__ == "__main__":
    pytest.main([__file__])
