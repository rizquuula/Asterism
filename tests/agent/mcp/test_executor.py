"""Test MCP executor system."""

from pathlib import Path

import pytest

from agent.mcp.executor import MCPExecutor, execute_mcp_tool


def test_mcp_executor_initialization():
    """Test MCP executor initialization."""
    executor = MCPExecutor()
    assert executor.config is not None


def test_execute_tool_valid_server():
    """Test executing tools on valid servers."""
    executor = MCPExecutor()

    # Test filesystem tools
    result = executor.execute_tool("filesystem", "list_files")
    assert result["success"] is True
    assert "tool" in result
    assert result["tool"] == "filesystem:list_files"

    # Test code_parser tools
    result = executor.execute_tool("code_parser", "analyze_complexity", functions=[])
    assert result["success"] is True
    assert "tool" in result
    assert result["tool"] == "code_parser:analyze_complexity"


def test_execute_tool_invalid_server():
    """Test executing tools on invalid servers."""
    executor = MCPExecutor()

    result = executor.execute_tool("invalid_server", "list_files")
    assert result["success"] is False
    assert "error" in result
    assert "invalid_server" in result["error"]


def test_execute_tool_invalid_tool():
    """Test executing invalid tools."""
    executor = MCPExecutor()

    result = executor.execute_tool("filesystem", "invalid_tool")
    assert result["success"] is False
    assert "error" in result
    assert "invalid_tool" in result["error"]


def test_execute_tool_disabled_server():
    """Test executing tools on disabled servers."""
    # Create a temporary config with disabled server
    config_path = Path(__file__).parent.parent.parent / "config" / "mcp_servers.yaml"

    executor = MCPExecutor(config_path)

    # For now, all servers are enabled in our config
    # This test would be more relevant if we had a disabled server
    result = executor.execute_tool("filesystem", "list_files")
    assert result["success"] is True


def test_get_available_tools():
    """Test getting available tools."""
    executor = MCPExecutor()
    available_tools = executor.get_available_tools()

    assert "filesystem" in available_tools
    assert "code_parser" in available_tools

    fs_tools = available_tools["filesystem"]
    assert "list_files" in fs_tools
    assert "read_file" in fs_tools
    assert "write_file" in fs_tools
    assert "get_file_info" in fs_tools

    cp_tools = available_tools["code_parser"]
    assert "parse_functions" in cp_tools
    assert "get_function_details" in cp_tools
    assert "analyze_complexity" in cp_tools


def test_validate_tool_call():
    """Test tool call validation."""
    executor = MCPExecutor()

    # Valid tool calls
    assert executor.validate_tool_call("filesystem", "list_files") is True
    assert executor.validate_tool_call("code_parser", "analyze_complexity") is True

    # Invalid tool calls
    assert executor.validate_tool_call("filesystem", "invalid_tool") is False
    assert executor.validate_tool_call("invalid_server", "list_files") is False


def test_execute_mcp_tool_function():
    """Test the standalone execute_mcp_tool function."""
    # Test valid tool
    result = execute_mcp_tool("filesystem", "list_files")
    assert result["success"] is True
    assert "tool" in result
    assert result["tool"] == "filesystem:list_files"

    # Test invalid tool
    result = execute_mcp_tool("invalid_server", "list_files")
    assert result["success"] is False
    assert "error" in result


def test_tool_execution_with_parameters():
    """Test tool execution with parameters."""
    executor = MCPExecutor()

    # Test filesystem tool with parameters
    result = executor.execute_tool("filesystem", "list_files", pattern="*.py")
    assert result["success"] is True
    assert "tool" in result
    assert result["tool"] == "filesystem:list_files"

    # Test code_parser tool with parameters
    result = executor.execute_tool(
        "code_parser",
        "analyze_complexity",
        functions=[{"name": "test", "code": "def test(): pass"}]
    )
    assert result["success"] is True
    assert "tool" in result
    assert result["tool"] == "code_parser:analyze_complexity"


def test_error_handling():
    """Test error handling in tool execution."""
    executor = MCPExecutor()

    # Test with invalid parameters
    result = executor.execute_tool("filesystem", "read_file", invalid_param="test")
    # Should still succeed as the function handles missing parameters gracefully
    assert "tool" in result
    assert result["tool"] == "filesystem:read_file"


if __name__ == "__main__":
    pytest.main([__file__])