"""Test agent state definition."""

from langchain_core.messages import AIMessage, HumanMessage

from asterism.agent.models import AgentResponse, EvaluationResult, LLMUsage, Plan, Task, TaskResult
from asterism.agent.state import AgentState


def test_agent_state_basic():
    """Test creating a basic AgentState."""
    state: AgentState = {
        "session_id": "test_session",
        "trace_id": "trace_123",
        "messages": [HumanMessage(content="Hello")],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    assert state["session_id"] == "test_session"
    assert state["trace_id"] == "trace_123"
    assert len(state["messages"]) == 1
    assert state["plan"] is None


def test_agent_state_with_plan():
    """Test AgentState with a plan."""
    plan = Plan(tasks=[Task(id="task_1", description="Test task")], reasoning="Test")

    state: AgentState = {
        "session_id": "test_session",
        "trace_id": "trace_123",
        "messages": [],
        "plan": plan,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    assert state["plan"] is not None
    assert len(state["plan"].tasks) == 1


def test_agent_state_with_execution_results():
    """Test AgentState with execution results."""
    result = TaskResult(task_id="task_1", success=True, result="output")

    state: AgentState = {
        "session_id": "test_session",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 1,
        "execution_results": [result],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    assert len(state["execution_results"]) == 1
    assert state["current_task_index"] == 1


def test_agent_state_with_evaluation():
    """Test AgentState with evaluation result."""
    evaluation = EvaluationResult(decision="continue", reasoning="Good progress")

    state: AgentState = {
        "session_id": "test_session",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": evaluation,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    assert state["evaluation_result"] is not None
    assert state["evaluation_result"].decision == "continue"


def test_agent_state_with_final_response():
    """Test AgentState with final response."""
    response = AgentResponse(
        message="Done!",
        execution_trace=[{"task_id": "t1", "success": True}],
    )

    state: AgentState = {
        "session_id": "test_session",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": response,
        "error": None,
        "llm_usage": [],
    }

    assert state["final_response"] is not None
    assert state["final_response"].message == "Done!"


def test_agent_state_with_error():
    """Test AgentState with error."""
    state: AgentState = {
        "session_id": "test_session",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": "Something went wrong",
        "llm_usage": [],
    }

    assert state["error"] == "Something went wrong"


def test_agent_state_with_llm_usage():
    """Test AgentState with LLM usage tracking."""
    usage = LLMUsage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        model="gpt-4",
        node_name="planner_node",
    )

    state: AgentState = {
        "session_id": "test_session",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [usage],
    }

    assert len(state["llm_usage"]) == 1
    assert state["llm_usage"][0].total_tokens == 150


def test_agent_state_mixed_messages():
    """Test AgentState with mixed message types."""
    state: AgentState = {
        "session_id": "test_session",
        "trace_id": "trace_123",
        "messages": [
            HumanMessage(content="User message"),
            AIMessage(content="AI response"),
        ],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    assert len(state["messages"]) == 2
    assert isinstance(state["messages"][0], HumanMessage)
    assert isinstance(state["messages"][1], AIMessage)


def test_agent_state_trace_id_optional():
    """Test that trace_id can be None."""
    state: AgentState = {
        "session_id": "test_session",
        "trace_id": None,
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    assert state["trace_id"] is None
