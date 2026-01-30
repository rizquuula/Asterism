"""Executor node: MCP tool execution loop."""

from agent.mcp.executor import execute_mcp_tool
from agent.state import AgentState


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
