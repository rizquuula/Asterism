"""Integration tests for StdioTransport using localtime MCP server."""

from asterism.mcp.transport_executor.stdio import StdioTransport


def test_list_tools_success(localtime_mcp_path):
    """Test successfully listing tools from the localtime MCP server."""
    transport = StdioTransport()

    try:
        transport.start("uvx", [localtime_mcp_path])
        tools = transport.list_tools()

        assert isinstance(tools, list)
        assert "get_current_time" in tools
    finally:
        transport.stop()


def test_get_current_time_success(localtime_mcp_path):
    """Test successfully getting current time from the localtime MCP server."""
    transport = StdioTransport()

    try:
        transport.start("uvx", [localtime_mcp_path])
        time_data = transport.execute_tool("get_current_time")

        assert "iso_datetime" in time_data
        assert "unix_timestamp" in time_data
        assert "timezone" in time_data
        assert isinstance(time_data["unix_timestamp"], int)
    finally:
        transport.stop()
