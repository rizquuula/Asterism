"""MCP Tool Execution Interface.

This module provides a dynamic interface for executing MCP tools based on
configuration, replacing the hardcoded implementations in the executor node.
"""

from typing import Any

from .config import get_mcp_config


class MCPExecutor:
    """Dynamic MCP tool executor that uses configuration-based tool routing."""

    def __init__(self, config_path: str | None = None):
        """
        Initialize the MCP executor.

        Args:
            config_path: Path to the MCP configuration file. If None, uses default location.
        """
        self.config = get_mcp_config()
        if config_path:
            self.config = self.config.load_config(config_path)

    def execute_tool(self, server_name: str, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Execute an MCP tool dynamically based on configuration.

        Args:
            server_name: Name of the MCP server.
            tool_name: Name of the tool to execute.
            **kwargs: Additional arguments for the tool.

        Returns:
            Dictionary containing execution result with keys:
                - success: Boolean indicating if execution succeeded
                - result: The tool result or None if failed
                - error: Error message if failed, None if succeeded
                - tool: The tool identifier used
                - tool_call: The original tool call string
        """
        try:
            # Validate server and tool availability
            if not self.config.is_server_enabled(server_name):
                return {
                    "success": False,
                    "error": f"MCP server '{server_name}' is not enabled",
                    "result": None,
                    "tool": f"{server_name}:{tool_name}",
                    "tool_call": f"{server_name}:{tool_name}",
                }

            if not self.config.is_tool_available(server_name, tool_name):
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' is not available on server '{server_name}'",
                    "result": None,
                    "tool": f"{server_name}:{tool_name}",
                    "tool_call": f"{server_name}:{tool_name}",
                }

            # Get connection information
            connection_info = self.config.get_connection_info(server_name)

            # Execute the tool based on server type
            if connection_info.get("type") == "local":
                return self._execute_local_tool(server_name, tool_name, **kwargs)
            else:
                return self._execute_remote_tool(server_name, tool_name, connection_info, **kwargs)

        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing tool: {str(e)}",
                "result": None,
                "tool": f"{server_name}:{tool_name}",
                "tool_call": f"{server_name}:{tool_name}",
            }

    def _execute_local_tool(self, server_name: str, tool_name: str, **kwargs) -> dict[str, Any]:
        """
        Execute a local MCP tool.

        Args:
            server_name: Name of the local MCP server.
            tool_name: Name of the tool to execute.
            **kwargs: Additional arguments for the tool.

        Returns:
            Dictionary containing execution result.
        """
        ## TODO: Implement local MCP tool execution logic

        return {
            "success": False,
            "error": f"Local MCP server '{server_name}' not yet implemented",
            "result": None,
            "tool": f"{server_name}:{tool_name}",
            "tool_call": f"{server_name}:{tool_name}",
        }

    def _execute_remote_tool(
        self, server_name: str, tool_name: str, connection_info: dict[str, Any], **kwargs
    ) -> dict[str, Any]:
        """
        Execute a remote MCP tool.

        Args:
            server_name: Name of the remote MCP server.
            tool_name: Name of the tool to execute.
            connection_info: Connection information for the remote server.
            **kwargs: Additional arguments for the tool.

        Returns:
            Dictionary containing execution result.
        """
        # TODO: Implement remote MCP server communication
        # This would typically involve:
        # 1. Establishing connection to remote MCP server
        # 2. Authenticating if required
        # 3. Sending tool execution request
        # 4. Handling response and errors

        return {
            "success": False,
            "error": f"Remote MCP server '{server_name}' not yet implemented",
            "result": None,
            "tool": f"{server_name}:{tool_name}",
            "tool_call": f"{server_name}:{tool_name}",
        }

    def get_available_tools(self) -> dict[str, list]:
        """
        Get all available tools organized by server.

        Returns:
            Dictionary mapping server names to lists of available tool names.
        """
        available_tools = {}
        enabled_servers = self.config.get_enabled_servers()

        for server_name in enabled_servers:
            tools = self.config.get_server_tools(server_name)
            available_tools[server_name] = tools

        return available_tools

    def validate_tool_call(self, server_name: str, tool_name: str) -> bool:
        """
        Validate if a tool call is valid.

        Args:
            server_name: Name of the MCP server.
            tool_name: Name of the tool.

        Returns:
            True if the tool call is valid, False otherwise.
        """
        return self.config.is_tool_available(server_name, tool_name)


# Global MCP executor instance
_mcp_executor: MCPExecutor | None = None


def get_mcp_executor() -> MCPExecutor:
    """
    Get the global MCP executor instance.

    Returns:
        MCPExecutor instance.
    """
    global _mcp_executor
    if _mcp_executor is None:
        _mcp_executor = MCPExecutor()
    return _mcp_executor


def execute_mcp_tool(server_name: str, tool_name: str, **kwargs) -> dict[str, Any]:
    """
    Execute an MCP tool using the global executor instance.

    This function provides a simple interface for executing MCP tools that
    can be used as a drop-in replacement for the hardcoded implementations.

    Args:
        server_name: Name of the MCP server.
        tool_name: Name of the tool to execute.
        **kwargs: Additional arguments for the tool.

    Returns:
        Dictionary containing execution result.
    """
    executor = get_mcp_executor()
    return executor.execute_tool(server_name, tool_name, **kwargs)