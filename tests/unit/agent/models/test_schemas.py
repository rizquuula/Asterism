"""Test agent models/schemas."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from asterism.agent.models import (
    AgentResponse,
    EvaluationDecision,
    EvaluationResult,
    LLMUsage,
    Plan,
    Task,
    TaskInputResolverResult,
    TaskResult,
    UsageSummary,
)


def test_evaluation_decision_enum():
    """Test EvaluationDecision enum values."""
    assert EvaluationDecision.CONTINUE == "continue"
    assert EvaluationDecision.REPLAN == "replan"
    assert EvaluationDecision.FINALIZE == "finalize"


def test_task_creation():
    """Test Task model creation."""
    task = Task(
        id="task_1",
        description="Test task",
        tool_call="server:tool",
        tool_input={"key": "value"},
        depends_on=["task_0"],
    )

    assert task.id == "task_1"
    assert task.description == "Test task"
    assert task.tool_call == "server:tool"
    assert task.tool_input == {"key": "value"}
    assert task.depends_on == ["task_0"]


def test_task_defaults():
    """Test Task model with default values."""
    task = Task(id="task_1", description="Test task")

    assert task.tool_call is None
    assert task.tool_input is None
    assert task.depends_on == []


def test_task_validation_required():
    """Test Task model validation for required fields."""
    with pytest.raises(ValidationError):
        Task()  # Missing required fields

    with pytest.raises(ValidationError):
        Task(id="task_1")  # Missing description


def test_plan_creation():
    """Test Plan model creation."""
    tasks = [
        Task(id="task_1", description="First task"),
        Task(id="task_2", description="Second task"),
    ]
    plan = Plan(tasks=tasks, reasoning="Test plan reasoning")

    assert len(plan.tasks) == 2
    assert plan.reasoning == "Test plan reasoning"


def test_plan_validation():
    """Test Plan model validation."""
    with pytest.raises(ValidationError):
        Plan()  # Missing required fields


def test_llm_usage_creation():
    """Test LLMUsage model creation."""
    usage = LLMUsage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        model="gpt-4",
        node_name="planner_node",
    )

    assert usage.prompt_tokens == 100
    assert usage.completion_tokens == 50
    assert usage.total_tokens == 150
    assert usage.model == "gpt-4"
    assert usage.node_name == "planner_node"


def test_usage_summary_creation():
    """Test UsageSummary model creation."""
    summary = UsageSummary(
        total_prompt_tokens=100,
        total_completion_tokens=50,
        total_tokens=150,
        calls_by_node={"planner_node": 1, "executor_node": 2},
    )

    assert summary.total_prompt_tokens == 100
    assert summary.total_completion_tokens == 50
    assert summary.total_tokens == 150
    assert summary.calls_by_node == {"planner_node": 1, "executor_node": 2}


def test_usage_summary_defaults():
    """Test UsageSummary model with default values."""
    summary = UsageSummary()

    assert summary.total_prompt_tokens == 0
    assert summary.total_completion_tokens == 0
    assert summary.total_tokens == 0
    assert summary.calls_by_node == {}


def test_task_result_creation():
    """Test TaskResult model creation."""
    result = TaskResult(
        task_id="task_1",
        success=True,
        result={"data": "value"},
        error=None,
    )

    assert result.task_id == "task_1"
    assert result.success is True
    assert result.result == {"data": "value"}
    assert result.error is None
    assert isinstance(result.timestamp, datetime)


def test_task_result_with_llm_usage():
    """Test TaskResult with LLM usage."""
    usage = LLMUsage(
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        model="gpt-4",
        node_name="executor_node",
    )
    result = TaskResult(
        task_id="task_1",
        success=True,
        result="output",
        llm_usage=usage,
    )

    assert result.llm_usage is not None
    assert result.llm_usage.prompt_tokens == 10


def test_evaluation_result_creation():
    """Test EvaluationResult model creation."""
    result = EvaluationResult(
        decision=EvaluationDecision.CONTINUE,
        reasoning="Continue execution",
        context_updates={"key": "value"},
        suggested_changes=None,
    )

    assert result.decision == EvaluationDecision.CONTINUE
    assert result.reasoning == "Continue execution"
    assert result.context_updates == {"key": "value"}
    assert result.suggested_changes is None


def test_evaluation_result_defaults():
    """Test EvaluationResult model with default values."""
    result = EvaluationResult(
        decision=EvaluationDecision.FINALIZE,
        reasoning="Complete",
    )

    assert result.context_updates == {}
    assert result.suggested_changes is None


def test_agent_response_creation():
    """Test AgentResponse model creation."""
    tasks = [Task(id="task_1", description="Test task")]
    plan = Plan(tasks=tasks, reasoning="Test plan")
    response = AgentResponse(
        message="Test response",
        execution_trace=[{"task_id": "task_1", "success": True}],
        plan_used=plan,
    )

    assert response.message == "Test response"
    assert len(response.execution_trace) == 1
    assert response.plan_used is not None


def test_agent_response_defaults():
    """Test AgentResponse model with default values."""
    response = AgentResponse(
        message="Test",
        execution_trace=[],
    )

    assert response.plan_used is None
    assert response.total_usage.total_tokens == 0


def test_task_input_resolver_result():
    """Test TaskInputResolverResult model."""
    result = TaskInputResolverResult(updated_tool_input={"key": "value"})

    assert result.updated_tool_input == {"key": "value"}


def test_task_input_resolver_result_defaults():
    """Test TaskInputResolverResult with default values."""
    result = TaskInputResolverResult()

    assert result.updated_tool_input is None


def test_task_model_dump():
    """Test Task model_dump method."""
    task = Task(id="task_1", description="Test", tool_call="server:tool")
    data = task.model_dump()

    assert data["id"] == "task_1"
    assert data["description"] == "Test"
    assert data["tool_call"] == "server:tool"


def test_plan_model_dump():
    """Test Plan model_dump method."""
    plan = Plan(tasks=[Task(id="t1", description="Task 1")], reasoning="Test")
    data = plan.model_dump()

    assert "tasks" in data
    assert len(data["tasks"]) == 1
    assert data["reasoning"] == "Test"
