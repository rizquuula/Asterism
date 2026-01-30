"""Unit tests for SSETransport."""

import json
from unittest.mock import MagicMock, patch

import pytest

from agent.mcp.transport_executor.sse import SSETransport


def test_sse_transport_init():
    """Test SSETransport initialization."""
    transport = SSETransport()
    assert transport._session is None
    assert transport._base_url is None
    assert transport._timeout == 30
    assert transport._request_id == 0
    assert transport._initialized is False
    assert transport._message_endpoint is None


@patch("agent.mcp.transport_executor.sse.requests.Session")
@patch("agent.mcp.transport_executor.sse.threading.Thread")
def test_sse_start_success(mock_thread_class, mock_session_class):
    """Test successful start and initialization."""
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock thread
    mock_thread = MagicMock()
    mock_thread_class.return_value = mock_thread

    transport = SSETransport()
    # Set message endpoint manually (normally set by SSE listener)
    transport._message_endpoint = "http://localhost:3000/message"

    # Pre-populate response queue with init response
    transport._response_queue.put({
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"protocolVersion": "2024-11-05"},
    })

    # Mock time.sleep to avoid actual sleep
    with patch("time.sleep"):
        transport.start("http", ["http://localhost:3000"])

    assert transport._base_url == "http://localhost:3000"
    assert transport._session is not None
    assert transport._initialized is True


@patch("agent.mcp.transport_executor.sse.requests.Session")
def test_sse_start_without_args_raises(mock_session_class):
    """Test start raises ValueError when args is empty."""
    transport = SSETransport()
    with pytest.raises(ValueError, match="SSE transport requires server URL in args"):
        transport.start("http", [])


@patch("agent.mcp.transport_executor.sse.requests.Session")
def test_sse_execute_tool_success(mock_session_class):
    """Test successful tool execution."""
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock response
    mock_post_response = MagicMock()
    mock_post_response.ok = True
    mock_post_response.json.return_value = {"result": "posted"}
    mock_session.post.return_value = mock_post_response

    transport = SSETransport()
    transport._base_url = "http://localhost:3000"
    transport._session = mock_session
    transport._message_endpoint = "http://localhost:3000/message"
    transport._initialized = True
    transport._request_id = 1

    # Put response in queue
    response_data = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {"content": [{"type": "text", "text": json.dumps({"result": "success"})}]},
    }
    transport._response_queue.put(response_data)

    result = transport.execute_tool("test_tool", param1="value1")

    assert result["success"] is True
    assert result["result"] == {"result": "success"}


@patch("agent.mcp.transport_executor.sse.requests.Session")
def test_sse_list_tools_success(mock_session_class):
    """Test successful tools listing."""
    # Setup mock session
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    # Setup mock response
    mock_post_response = MagicMock()
    mock_post_response.ok = True
    mock_session.post.return_value = mock_post_response

    transport = SSETransport()
    transport._base_url = "http://localhost:3000"
    transport._session = mock_session
    transport._message_endpoint = "http://localhost:3000/message"
    transport._initialized = True
    transport._request_id = 1

    # Put response in queue
    response_data = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {"tools": [{"name": "tool1"}, {"name": "tool2"}]},
    }
    transport._response_queue.put(response_data)

    tools = transport.list_tools()

    assert "tool1" in tools
    assert "tool2" in tools


@patch("agent.mcp.transport_executor.sse.requests.Session")
def test_sse_is_alive(mock_session_class):
    """Test is_alive returns correct state."""
    transport = SSETransport()
    assert not transport.is_alive()

    transport._session = MagicMock()
    transport._base_url = "http://localhost:3000"
    assert transport.is_alive()

    transport._session = None
    assert not transport.is_alive()


@patch("agent.mcp.transport_executor.sse.requests.Session")
@patch("agent.mcp.transport_executor.sse.threading.Thread")
def test_sse_stop_closes_session(mock_thread_class, mock_session_class):
    """Test stop closes session and stops thread."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_thread = MagicMock()
    mock_thread_class.return_value = mock_thread
    mock_thread.is_alive.return_value = True

    transport = SSETransport()
    transport._base_url = "http://localhost:3000"
    transport._session = mock_session
    transport._sse_thread = mock_thread
    transport._message_endpoint = "http://localhost:3000/message"
    transport._initialized = True

    transport.stop()

    mock_session.close.assert_called_once()
    assert transport._session is None
    assert transport._base_url is None
    assert transport._initialized is False
    assert transport._message_endpoint is None


@patch("agent.mcp.transport_executor.sse.requests.Session")
def test_sse_execute_tool_non_json_response(mock_session_class):
    """Test tool execution with non-JSON response returns text."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_post_response = MagicMock()
    mock_post_response.ok = True
    mock_session.post.return_value = mock_post_response

    transport = SSETransport()
    transport._base_url = "http://localhost:3000"
    transport._session = mock_session
    transport._message_endpoint = "http://localhost:3000/message"
    transport._initialized = True
    transport._request_id = 1

    # Put response with non-JSON text in queue
    response_data = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {"content": [{"type": "text", "text": "plain text result"}]},
    }
    transport._response_queue.put(response_data)

    result = transport.execute_tool("test_tool")

    assert result["success"] is True
    assert result["result"] == {"text": "plain text result"}


@patch("agent.mcp.transport_executor.sse.requests.Session")
def test_sse_execute_tool_empty_content(mock_session_class):
    """Test tool execution with empty content."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_post_response = MagicMock()
    mock_post_response.ok = True
    mock_session.post.return_value = mock_post_response

    transport = SSETransport()
    transport._base_url = "http://localhost:3000"
    transport._session = mock_session
    transport._message_endpoint = "http://localhost:3000/message"
    transport._initialized = True
    transport._request_id = 1

    # Put response with empty content in queue
    response_data = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {"content": []},
    }
    transport._response_queue.put(response_data)

    result = transport.execute_tool("test_tool")

    assert result["success"] is True
    assert result["result"] == {}


@patch("agent.mcp.transport_executor.sse.requests.Session")
@patch("agent.mcp.transport_executor.sse.threading.Thread")
def test_sse_list_tools_not_initialized_returns_empty(mock_thread_class, mock_session_class):
    """Test list_tools returns empty list when not initialized."""
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session

    mock_thread = MagicMock()
    mock_thread_class.return_value = mock_thread

    transport = SSETransport()
    transport._base_url = "http://localhost:3000"
    transport._session = mock_session
    transport._initialized = False

    tools = transport.list_tools()
    assert tools == []


if __name__ == "__main__":
    pytest.main([__file__])
