"""Executor node: MCP tool execution loop."""

from pathlib import Path
from typing import Any

from agent.state import AgentState


def execute_mcp_tool(server_name: str, tool_name: str, **kwargs) -> dict[str, Any]:
    """Execute an MCP tool by calling the corresponding server."""
    try:
        # For now, we'll simulate MCP tool execution
        # In a real implementation, this would connect to MCP servers

        if server_name == "filesystem":
            return execute_filesystem_tool(tool_name, **kwargs)
        elif server_name == "code_parser":
            return execute_code_parser_tool(tool_name, **kwargs)
        else:
            return {"success": False, "error": f"Unknown MCP server: {server_name}", "result": None}

    except Exception as e:
        return {"success": False, "error": str(e), "result": None}


def execute_filesystem_tool(tool_name: str, **kwargs) -> dict[str, Any]:
    """Execute filesystem-related tools."""
    try:
        if tool_name == "list_files":
            pattern = kwargs.get("pattern", "*")
            # Simple file listing (in real implementation, use proper glob)
            path = Path.cwd()
            if pattern == "*.py":
                files = list(path.glob("*.py"))
            elif pattern == "**/*.py":
                files = list(path.rglob("*.py"))
            else:
                files = list(path.iterdir())

            file_names = [f.name for f in files if f.is_file()]
            return {"success": True, "result": file_names, "tool": "filesystem:list_files"}

        elif tool_name == "read_file":
            file_path = kwargs.get("path", "")
            if not file_path:
                return {"success": False, "error": "No file path provided", "result": None}

            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": f"File not found: {file_path}", "result": None}

            with open(path) as f:
                content = f.read()

            return {"success": True, "result": content, "tool": "filesystem:read_file", "file_path": file_path}

        elif tool_name == "write_file":
            file_path = kwargs.get("path", "")
            content = kwargs.get("content", "")

            if not file_path:
                return {"success": False, "error": "No file path provided", "result": None}

            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w") as f:
                f.write(content)

            return {
                "success": True,
                "result": f"File written: {file_path}",
                "tool": "filesystem:write_file",
                "file_path": file_path,
            }

        else:
            return {"success": False, "error": f"Unknown filesystem tool: {tool_name}", "result": None}

    except Exception as e:
        return {"success": False, "error": str(e), "result": None}


def execute_code_parser_tool(tool_name: str, **kwargs) -> dict[str, Any]:
    """Execute code parsing tools."""
    try:
        if tool_name == "analyze_complexity":
            functions = kwargs.get("functions", [])
            # Simple complexity analysis (in real implementation, use AST parsing)

            analysis = []
            for func in functions:
                # Mock complexity analysis
                complexity_score = len(func.get("code", "")) // 10  # Simple length-based metric
                issues = []

                if complexity_score > 20:
                    issues.append("High complexity - consider refactoring")
                if len(func.get("params", [])) > 5:
                    issues.append("Too many parameters")
                if len(func.get("code", "").split("\n")) > 50:
                    issues.append("Function too long")

                analysis.append(
                    {"function": func.get("name", "unknown"), "complexity_score": complexity_score, "issues": issues}
                )

            return {"success": True, "result": analysis, "tool": "code_parser:analyze_complexity"}

        else:
            return {"success": False, "error": f"Unknown code parser tool: {tool_name}", "result": None}

    except Exception as e:
        return {"success": False, "error": str(e), "result": None}


def node(state: AgentState) -> AgentState:
    """Executes MCP tools from the tactical plan."""
    tactical_plan = state["tactical_plan"]
    history = state.get("history", [])

    for tool_call in tactical_plan:
        try:
            # Parse tool call (format: "server:tool(param=value,...)")
            if ":" not in tool_call:
                result = {"success": False, "error": f"Invalid tool call format: {tool_call}", "tool_call": tool_call}
            else:
                server_name, tool_spec = tool_call.split(":", 1)

                # Simple parameter parsing (basic implementation)
                if "(" in tool_spec and ")" in tool_spec:
                    tool_name = tool_spec.split("(")[0]
                    params_str = tool_spec.split("(")[1].rstrip(")")
                    # Very basic parameter parsing - in real implementation, use proper parsing
                    kwargs = {}
                    if params_str and params_str != "pattern=*.py" and params_str != "pattern=**/*.py":
                        # For now, skip complex parameter parsing
                        pass
                else:
                    tool_name = tool_spec
                    kwargs = {}

                # Execute the tool
                result = execute_mcp_tool(server_name, tool_name, **kwargs)
                result["tool_call"] = tool_call

        except Exception as e:
            result = {"success": False, "error": str(e), "tool_call": tool_call, "result": None}

        history.append(result)

    return {**state, "history": history}
