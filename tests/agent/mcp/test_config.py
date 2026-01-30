"""Test MCP configuration system."""


import pytest

from agent.mcp.config import MCPConfig


def test_load_config():
    """Test loading MCP configuration from file."""
    config = MCPConfig()
    loaded_config = config.load_config()

    assert "mcp_servers" in loaded_config
    assert "filesystem" in loaded_config["mcp_servers"]
    assert "code_parser" in loaded_config["mcp_servers"]


def test_get_server_config():
    """Test getting configuration for specific servers."""
    config = MCPConfig()
    config.load_config()

    # Test filesystem server
    fs_config = config.get_server_config("filesystem")
    assert fs_config is not None
    assert "list_files" in fs_config["tools"]
    assert "read_file" in fs_config["tools"]
    assert "write_file" in fs_config["tools"]
    assert "get_file_info" in fs_config["tools"]
    assert fs_config["enabled"] is True

    # Test code_parser server
    cp_config = config.get_server_config("code_parser")
    assert cp_config is not None
    assert "parse_functions" in cp_config["tools"]
    assert "get_function_details" in cp_config["tools"]
    assert "analyze_complexity" in cp_config["tools"]
    assert cp_config["enabled"] is True

    # Test non-existent server
    non_existent = config.get_server_config("non_existent")
    assert non_existent is None


def test_get_available_servers():
    """Test getting list of available servers."""
    config = MCPConfig()
    config.load_config()

    servers = config.get_available_servers()
    assert "filesystem" in servers
    assert "code_parser" in servers
    assert len(servers) == 2


def test_get_enabled_servers():
    """Test getting list of enabled servers."""
    config = MCPConfig()
    config.load_config()

    enabled_servers = config.get_enabled_servers()
    assert "filesystem" in enabled_servers
    assert "code_parser" in enabled_servers
    assert len(enabled_servers) == 2


def test_is_server_enabled():
    """Test checking if servers are enabled."""
    config = MCPConfig()
    config.load_config()

    assert config.is_server_enabled("filesystem") is True
    assert config.is_server_enabled("code_parser") is True
    assert config.is_server_enabled("non_existent") is False


def test_get_server_tools():
    """Test getting tools for specific servers."""
    config = MCPConfig()
    config.load_config()

    fs_tools = config.get_server_tools("filesystem")
    assert "list_files" in fs_tools
    assert "read_file" in fs_tools
    assert "write_file" in fs_tools
    assert "get_file_info" in fs_tools

    cp_tools = config.get_server_tools("code_parser")
    assert "parse_functions" in cp_tools
    assert "get_function_details" in cp_tools
    assert "analyze_complexity" in cp_tools

    non_existent_tools = config.get_server_tools("non_existent")
    assert non_existent_tools == []


def test_is_tool_available():
    """Test checking if specific tools are available."""
    config = MCPConfig()
    config.load_config()

    # Test valid tools
    assert config.is_tool_available("filesystem", "list_files") is True
    assert config.is_tool_available("filesystem", "read_file") is True
    assert config.is_tool_available("code_parser", "parse_functions") is True

    # Test invalid tools
    assert config.is_tool_available("filesystem", "non_existent") is False
    assert config.is_tool_available("non_existent", "list_files") is False


def test_get_connection_info():
    """Test getting connection information."""
    config = MCPConfig()
    config.load_config()

    fs_connection = config.get_connection_info("filesystem")
    assert fs_connection is not None
    assert fs_connection["type"] == "local"
    assert fs_connection["host"] == "localhost"
    assert fs_connection["port"] == 8080

    cp_connection = config.get_connection_info("code_parser")
    assert cp_connection is not None
    assert cp_connection["type"] == "local"
    assert cp_connection["host"] == "localhost"
    assert cp_connection["port"] == 8081

    non_existent_connection = config.get_connection_info("non_existent")
    assert non_existent_connection is None


def test_config_validation():
    """Test configuration validation."""
    config = MCPConfig()
    config.load_config()

    # Test that required fields are present
    fs_config = config.get_server_config("filesystem")
    assert "tools" in fs_config
    assert "enabled" in fs_config
    assert "connection" in fs_config

    # Test default values
    assert fs_config["tools"] == ["list_files", "read_file", "write_file", "get_file_info"]
    assert fs_config["enabled"] is True
    assert fs_config["connection"]["type"] == "local"


if __name__ == "__main__":
    pytest.main([__file__])