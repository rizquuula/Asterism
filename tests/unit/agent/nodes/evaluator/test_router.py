"""Test evaluator routing logic."""

from asterism.agent.models import EvaluationDecision, EvaluationResult, Plan, Task, TaskResult
from asterism.agent.nodes.evaluator.router import (
    RouteTarget,
    _determine_fallback_route,
    _route_from_decision,
    determine_route,
    should_continue,
)
from asterism.agent.state import AgentState


def test_route_target_enum():
    """Test RouteTarget enum values."""
    assert RouteTarget.PLANNER == "planner_node"
    assert RouteTarget.EXECUTOR == "executor_node"
    assert RouteTarget.FINALIZER == "finalizer_node"


def test_route_from_decision_replan():
    """Test routing from REPLAN decision."""
    target = _route_from_decision(EvaluationDecision.REPLAN)
    assert target == RouteTarget.PLANNER


def test_route_from_decision_continue():
    """Test routing from CONTINUE decision."""
    target = _route_from_decision(EvaluationDecision.CONTINUE)
    assert target == RouteTarget.EXECUTOR


def test_route_from_decision_finalize():
    """Test routing from FINALIZE decision."""
    target = _route_from_decision(EvaluationDecision.FINALIZE)
    assert target == RouteTarget.FINALIZER


def test_route_from_decision_invalid():
    """Test routing from invalid decision defaults to executor."""

    # Create a mock decision value
    class MockDecision:
        value = "unknown"

    target = _route_from_decision(MockDecision())
    assert target == RouteTarget.EXECUTOR


def test_determine_route_with_error():
    """Test routing when state has error."""
    state: AgentState = {
        "session_id": "test",
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

    target = determine_route(state)
    assert target == RouteTarget.PLANNER


def test_determine_route_with_evaluation_replan():
    """Test routing with REPLAN evaluation."""
    evaluation = EvaluationResult(
        decision=EvaluationDecision.REPLAN,
        reasoning="Need to replan",
    )

    state: AgentState = {
        "session_id": "test",
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

    target = determine_route(state)
    assert target == RouteTarget.PLANNER


def test_determine_route_with_evaluation_continue():
    """Test routing with CONTINUE evaluation."""
    evaluation = EvaluationResult(
        decision=EvaluationDecision.CONTINUE,
        reasoning="Continue execution",
    )

    state: AgentState = {
        "session_id": "test",
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

    target = determine_route(state)
    assert target == RouteTarget.EXECUTOR


def test_determine_route_with_evaluation_finalize():
    """Test routing with FINALIZE evaluation."""
    evaluation = EvaluationResult(
        decision=EvaluationDecision.FINALIZE,
        reasoning="All done",
    )

    state: AgentState = {
        "session_id": "test",
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

    target = determine_route(state)
    assert target == RouteTarget.FINALIZER


def test_determine_route_fallback_no_plan():
    """Test fallback routing when no plan exists."""
    state: AgentState = {
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

    target = determine_route(state)
    assert target == RouteTarget.PLANNER


def test_determine_route_fallback_all_tasks_done():
    """Test fallback routing when all tasks are done."""
    plan = Plan(tasks=[Task(id="t1", description="Task 1")], reasoning="Test")

    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": plan,
        "current_task_index": 1,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    target = determine_route(state)
    assert target == RouteTarget.FINALIZER


def test_determine_route_fallback_last_task_failed():
    """Test fallback routing when last task failed."""
    plan = Plan(
        tasks=[Task(id="t1", description="Task 1"), Task(id="t2", description="Task 2")],
        reasoning="Test",
    )

    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": plan,
        "current_task_index": 1,
        "execution_results": [TaskResult(task_id="t1", success=False, error="Failed")],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    target = determine_route(state)
    assert target == RouteTarget.PLANNER


def test_determine_route_fallback_continue():
    """Test fallback routing to continue execution."""
    plan = Plan(
        tasks=[Task(id="t1", description="Task 1"), Task(id="t2", description="Task 2")],
        reasoning="Test",
    )

    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": plan,
        "current_task_index": 1,
        "execution_results": [TaskResult(task_id="t1", success=True, result="ok")],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    target = determine_route(state)
    assert target == RouteTarget.EXECUTOR


def test_determine_fallback_route_no_plan():
    """Test fallback route with no plan."""
    state: AgentState = {
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

    target = _determine_fallback_route(state)
    assert target == RouteTarget.PLANNER


def test_determine_fallback_route_tasks_remaining():
    """Test fallback route with tasks remaining."""
    plan = Plan(
        tasks=[Task(id="t1", description="Task 1"), Task(id="t2", description="Task 2")],
        reasoning="Test",
    )

    state: AgentState = {
        "session_id": "test",
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

    target = _determine_fallback_route(state)
    assert target == RouteTarget.EXECUTOR


def test_should_continue_returns_string():
    """Test that should_continue returns a string."""
    state: AgentState = {
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

    result = should_continue(state)
    assert isinstance(result, str)
    assert result in ["planner_node", "executor_node", "finalizer_node"]


def test_should_continue_with_evaluation():
    """Test should_continue with evaluation result."""
    evaluation = EvaluationResult(
        decision=EvaluationDecision.FINALIZE,
        reasoning="Complete",
    )

    state: AgentState = {
        "session_id": "test",
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

    result = should_continue(state)
    assert result == "finalizer_node"
