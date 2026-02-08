"""Test state manipulation utilities."""

from langchain_core.messages import AIMessage, HumanMessage

from asterism.agent.models import (
    AgentResponse,
    EvaluationDecision,
    EvaluationResult,
    LLMUsage,
    Plan,
    Task,
    TaskResult,
)
from asterism.agent.nodes.shared.state_utils import (
    advance_task,
    append_llm_usage,
    clear_error,
    create_error_state,
    prepare_replan_state,
    set_evaluation_result,
    set_final_response,
    set_plan,
)
from asterism.agent.state import AgentState


def test_create_error_state():
    """Test creating error state."""
    initial_state: AgentState = {
        "session_id": "test",
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

    new_state = create_error_state(initial_state, "Something went wrong")

    assert new_state["error"] == "Something went wrong"
    assert len(new_state["messages"]) == 2
    assert "[Error] Something went wrong" in new_state["messages"][-1].content


def test_clear_error():
    """Test clearing error from state."""
    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": "Previous error",
        "llm_usage": [],
    }

    new_state = clear_error(initial_state)

    assert new_state["error"] is None


def test_append_llm_usage():
    """Test appending LLM usage to state."""
    usage1 = LLMUsage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        model="gpt-4",
        node_name="planner_node",
    )
    usage2 = LLMUsage(
        prompt_tokens=200,
        completion_tokens=100,
        total_tokens=300,
        model="gpt-4",
        node_name="executor_node",
    )

    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [usage1],
    }

    new_state = append_llm_usage(initial_state, usage2)

    assert len(new_state["llm_usage"]) == 2
    assert new_state["llm_usage"][0].node_name == "planner_node"
    assert new_state["llm_usage"][1].node_name == "executor_node"


def test_set_plan():
    """Test setting plan in state."""
    plan = Plan(tasks=[Task(id="t1", description="Task 1")], reasoning="Test")
    usage = LLMUsage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        model="gpt-4",
        node_name="planner_node",
    )

    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 5,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": "Previous error",
        "llm_usage": [],
    }

    new_state = set_plan(initial_state, plan, usage)

    assert new_state["plan"] == plan
    assert new_state["current_task_index"] == 0
    assert new_state["error"] is None
    assert len(new_state["llm_usage"]) == 1


def test_advance_task_success():
    """Test advancing task with successful result."""
    result = TaskResult(task_id="task_1", success=True, result="output")

    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    new_state = advance_task(initial_state, result)

    assert len(new_state["execution_results"]) == 1
    assert new_state["current_task_index"] == 1
    assert new_state["error"] is None


def test_advance_task_failure():
    """Test advancing task with failed result."""
    result = TaskResult(task_id="task_1", success=False, error="Task failed")

    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    new_state = advance_task(initial_state, result)

    assert len(new_state["execution_results"]) == 1
    assert new_state["current_task_index"] == 1
    assert new_state["error"] == "Task failed"


def test_advance_task_with_llm_usage():
    """Test advancing task that used LLM."""
    usage = LLMUsage(
        prompt_tokens=50,
        completion_tokens=25,
        total_tokens=75,
        model="gpt-4",
        node_name="executor_node",
    )
    result = TaskResult(task_id="task_1", success=True, result="output", llm_usage=usage)

    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    new_state = advance_task(initial_state, result)

    assert len(new_state["llm_usage"]) == 1
    assert new_state["llm_usage"][0].total_tokens == 75


def test_set_evaluation_result():
    """Test setting evaluation result in state."""
    evaluation = EvaluationResult(
        decision=EvaluationDecision.CONTINUE,
        reasoning="Good progress",
    )
    usage = LLMUsage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        model="gpt-4",
        node_name="evaluator_node",
    )

    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    new_state = set_evaluation_result(initial_state, evaluation, usage)

    assert new_state["evaluation_result"] == evaluation
    assert len(new_state["llm_usage"]) == 1


def test_prepare_replan_state():
    """Test preparing state for replanning."""
    evaluation = EvaluationResult(
        decision=EvaluationDecision.REPLAN,
        reasoning="Need different approach",
        suggested_changes="Try alternative method",
    )

    failed_result = TaskResult(task_id="task_2", success=False, error="Execution failed")

    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 1,
        "execution_results": [failed_result],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    new_state = prepare_replan_state(initial_state, evaluation)

    assert "Replanning needed" in new_state["error"]
    assert "Need different approach" in new_state["error"]
    assert "task_2" in new_state["error"]
    assert "Try alternative method" in new_state["error"]
    assert len(new_state["messages"]) == 1
    assert isinstance(new_state["messages"][0], AIMessage)


def test_set_final_response_without_usage():
    """Test setting final response without LLM usage."""
    response = AgentResponse(
        message="Task completed!",
        execution_trace=[{"task_id": "t1", "success": True}],
    )

    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": "Previous error",
        "llm_usage": [],
    }

    new_state = set_final_response(initial_state, response)

    assert new_state["final_response"] == response
    assert new_state["error"] is None
    assert len(new_state["llm_usage"]) == 0


def test_set_final_response_with_usage():
    """Test setting final response with LLM usage."""
    response = AgentResponse(
        message="Task completed!",
        execution_trace=[{"task_id": "t1", "success": True}],
    )
    usage = LLMUsage(
        prompt_tokens=200,
        completion_tokens=100,
        total_tokens=300,
        model="gpt-4",
        node_name="finalizer_node",
    )

    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    new_state = set_final_response(initial_state, response, usage)

    assert new_state["final_response"] == response
    assert len(new_state["llm_usage"]) == 1


def test_state_immutability():
    """Test that state functions return new state objects."""
    initial_state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    result = TaskResult(task_id="task_1", success=True, result="output")
    new_state = advance_task(initial_state, result)

    # Original state should be unchanged
    assert len(initial_state["execution_results"]) == 0
    assert initial_state["current_task_index"] == 0

    # New state should have the updates
    assert len(new_state["execution_results"]) == 1
    assert new_state["current_task_index"] == 1
