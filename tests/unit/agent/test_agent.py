"""Unit tests for Agent class."""

import pytest

from asterism.agent.agent import Agent, _initialize_state
from asterism.agent.models import Plan, Task


def test_initialize_state():
    """Test _initialize_state creates correct state."""
    session_id = "test-session"
    user_message = "Hello agent"

    state = _initialize_state(session_id, user_message)

    assert state["session_id"] == session_id
    assert len(state["messages"]) == 1
    assert state["messages"][0].content == user_message
    assert state["plan"] is None
    assert state["current_task_index"] == 0
    assert state["execution_results"] == []
    assert state["final_response"] is None
    assert state["error"] is None


def test_agent_builds_graph(mock_llm, mock_mcp_executor):
    """Test that Agent.build() creates a compiled graph."""
    agent = Agent(llm=mock_llm, mcp_executor=mock_mcp_executor)
    graph = agent.build()

    assert graph is not None


def test_agent_invoke_success(mock_llm, mock_mcp_executor):
    """Test Agent.invoke() with successful execution."""
    # Mock the LLM to return a simple plan
    mock_llm.invoke_structured.return_value = Plan(
        tasks=[
            Task(
                id="task_1",
                description="Test task",
                tool_call="test:tool",
                tool_input={},
                depends_on=[],
            )
        ],
        reasoning="Test plan",
    )

    agent = Agent(llm=mock_llm, mcp_executor=mock_mcp_executor)
    result = agent.invoke("test-session", "Do something")

    assert "message" in result
    assert "execution_trace" in result
    assert "session_id" in result
    assert result["session_id"] == "test-session"
    # The finalizer should have generated a response
    assert result["message"] is not None


def test_agent_invoke_with_llm_failure(mock_llm, mock_mcp_executor):
    """Test Agent.invoke() when LLM fails during planning."""
    mock_llm.invoke_structured.side_effect = Exception("LLM error")

    agent = Agent(llm=mock_llm, mcp_executor=mock_mcp_executor)
    result = agent.invoke("test-session", "Do something")

    assert "error" in result
    assert "Agent execution failed" in result["message"]


def test_agent_clear_session(mock_llm, mock_mcp_executor):
    """Test Agent.clear_session() calls session manager."""
    agent = Agent(llm=mock_llm, mcp_executor=mock_mcp_executor)

    # This should not raise an error even if checkpointer not initialized
    # We're just testing that it doesn't crash
    try:
        agent.clear_session("test-session")
    except Exception as e:
        pytest.fail(f"clear_session raised unexpected exception: {e}")


def test_agent_custom_db_path(mock_llm, mock_mcp_executor):
    """Test Agent with custom db_path."""
    custom_path = "/tmp/test_agent.db"
    agent = Agent(llm=mock_llm, mcp_executor=mock_mcp_executor, db_path=custom_path)

    assert agent.db_path == custom_path
