"""Test context extraction utilities."""

from langchain_core.messages import AIMessage, HumanMessage

from asterism.agent.models import Plan, Task, TaskResult
from asterism.agent.nodes.shared.context_extractors import (
    are_dependencies_satisfied,
    format_execution_history,
    format_execution_summary,
    get_completed_task_ids,
    get_current_task,
    get_failed_tasks,
    get_last_result,
    get_user_request,
    has_execution_history,
)
from asterism.agent.state import AgentState


def test_get_user_request_first_human_message():
    """Test extracting user request from first human message."""
    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [
            HumanMessage(content="Please help me with this task"),
            AIMessage(content="I'll help you"),
        ],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    request = get_user_request(state)
    assert request == "Please help me with this task"


def test_get_user_request_no_human_message():
    """Test extracting user request when no human message exists."""
    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [AIMessage(content="AI message")],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    request = get_user_request(state)
    assert request == "No user request found"


def test_get_user_request_empty_messages():
    """Test extracting user request with empty messages."""
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

    request = get_user_request(state)
    assert request == "No user request found"


def test_get_last_result_with_results():
    """Test getting last result when results exist."""
    result1 = TaskResult(task_id="task_1", success=True, result="output1")
    result2 = TaskResult(task_id="task_2", success=False, error="failed")

    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [result1, result2],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    last = get_last_result(state)
    assert last is not None
    assert last.task_id == "task_2"


def test_get_last_result_no_results():
    """Test getting last result when no results exist."""
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

    last = get_last_result(state)
    assert last is None


def test_get_current_task():
    """Test getting current task from plan."""
    plan = Plan(
        tasks=[
            Task(id="task_1", description="First"),
            Task(id="task_2", description="Second"),
        ],
        reasoning="Test",
    )

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

    current = get_current_task(state)
    assert current is not None
    assert current.id == "task_2"


def test_get_current_task_no_plan():
    """Test getting current task when no plan exists."""
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

    current = get_current_task(state)
    assert current is None


def test_get_current_task_all_completed():
    """Test getting current task when all tasks are completed."""
    plan = Plan(tasks=[Task(id="task_1", description="First")], reasoning="Test")

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

    current = get_current_task(state)
    assert current is None


def test_format_execution_history():
    """Test formatting execution history."""
    results = [
        TaskResult(task_id="task_1", success=True, result="output1"),
        TaskResult(task_id="task_2", success=False, error="Something went wrong"),
    ]

    history = format_execution_history(results)

    assert "✓ task_1" in history
    assert "✗ task_2" in history
    assert "output1" in history
    assert "ERROR" in history


def test_format_execution_history_empty():
    """Test formatting empty execution history."""
    history = format_execution_history([])
    assert history == "No tasks executed yet."


def test_format_execution_history_truncation():
    """Test that execution history is truncated."""
    results = [TaskResult(task_id=f"task_{i}", success=True, result="x" * 500) for i in range(15)]

    history = format_execution_history(results, max_results=5)

    # Should only show recent 5
    assert "task_14" in history
    assert "task_10" in history
    # Older ones should not be present
    assert "task_0" not in history


def test_format_execution_summary():
    """Test formatting execution summary."""
    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [
            TaskResult(task_id="t1", success=True, result="ok"),
            TaskResult(task_id="t2", success=True, result="ok"),
            TaskResult(task_id="t3", success=False, error="fail"),
        ],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    summary = format_execution_summary(state)
    assert "Completed: 2" in summary
    assert "Failed: 1" in summary
    assert "Total: 3" in summary


def test_format_execution_summary_empty():
    """Test formatting empty execution summary."""
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

    summary = format_execution_summary(state)
    assert summary == "No execution history."


def test_get_completed_task_ids():
    """Test getting completed task IDs."""
    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [
            TaskResult(task_id="task_1", success=True, result="ok"),
            TaskResult(task_id="task_2", success=False, error="fail"),
        ],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    completed = get_completed_task_ids(state)
    assert completed == {"task_1", "task_2"}


def test_get_completed_task_ids_empty():
    """Test getting completed task IDs when empty."""
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

    completed = get_completed_task_ids(state)
    assert completed == set()


def test_are_dependencies_satisfied_no_deps():
    """Test checking dependencies when task has none."""
    task = Task(id="task_1", description="No deps", depends_on=[])

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

    satisfied = are_dependencies_satisfied(task, state)
    assert satisfied is True


def test_are_dependencies_satisfied_all_met():
    """Test checking dependencies when all are satisfied."""
    task = Task(id="task_2", description="Has deps", depends_on=["task_1"])

    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [TaskResult(task_id="task_1", success=True, result="ok")],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    satisfied = are_dependencies_satisfied(task, state)
    assert satisfied is True


def test_are_dependencies_satisfied_not_met():
    """Test checking dependencies when not all are satisfied."""
    task = Task(id="task_3", description="Has deps", depends_on=["task_1", "task_2"])

    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [TaskResult(task_id="task_1", success=True, result="ok")],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    satisfied = are_dependencies_satisfied(task, state)
    assert satisfied is False


def test_get_failed_tasks():
    """Test getting failed tasks."""
    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [
            TaskResult(task_id="task_1", success=True, result="ok"),
            TaskResult(task_id="task_2", success=False, error="fail1"),
            TaskResult(task_id="task_3", success=False, error="fail2"),
        ],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    failed = get_failed_tasks(state)
    assert len(failed) == 2
    assert failed[0].task_id == "task_2"
    assert failed[1].task_id == "task_3"


def test_get_failed_tasks_none():
    """Test getting failed tasks when all succeeded."""
    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [
            TaskResult(task_id="task_1", success=True, result="ok"),
            TaskResult(task_id="task_2", success=True, result="ok"),
        ],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    failed = get_failed_tasks(state)
    assert failed == []


def test_has_execution_history_true():
    """Test checking execution history when it exists."""
    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [TaskResult(task_id="task_1", success=True, result="ok")],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    assert has_execution_history(state) is True


def test_has_execution_history_false():
    """Test checking execution history when it doesn't exist."""
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

    assert has_execution_history(state) is False
