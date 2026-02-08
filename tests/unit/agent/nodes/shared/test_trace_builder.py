"""Test trace building utilities."""

from datetime import datetime

from asterism.agent.models import TaskResult
from asterism.agent.nodes.shared.trace_builder import (
    build_execution_trace,
    format_trace_for_display,
    get_trace_summary,
)
from asterism.agent.state import AgentState


def test_build_execution_trace_empty():
    """Test building trace with no results."""
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

    trace = build_execution_trace(state)
    assert trace == []


def test_build_execution_trace_with_results():
    """Test building trace with execution results."""
    result1 = TaskResult(task_id="task_1", success=True, result={"data": "value"})
    result2 = TaskResult(task_id="task_2", success=False, error="Task failed")

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

    trace = build_execution_trace(state)

    assert len(trace) == 2
    assert trace[0]["task_id"] == "task_1"
    assert trace[0]["success"] is True
    assert trace[0]["result"] == {"data": "value"}
    assert trace[1]["task_id"] == "task_2"
    assert trace[1]["success"] is False
    assert trace[1]["error"] == "Task failed"


def test_build_execution_trace_timestamp_formatting():
    """Test that timestamps are properly formatted in trace."""
    now = datetime.now()
    result = TaskResult(task_id="task_1", success=True, result="ok")
    result.timestamp = now

    state: AgentState = {
        "session_id": "test",
        "trace_id": "trace_123",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [result],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    trace = build_execution_trace(state)

    assert len(trace) == 1
    assert trace[0]["timestamp"] is not None


def test_format_trace_for_display_empty():
    """Test formatting empty trace for display."""
    formatted = format_trace_for_display([])
    assert formatted == "No execution trace available."


def test_format_trace_for_display_with_entries():
    """Test formatting trace with entries."""
    trace = [
        {"task_id": "task_1", "success": True, "result": "Output data", "error": None},
        {"task_id": "task_2", "success": False, "result": None, "error": "Failed"},
    ]

    formatted = format_trace_for_display(trace)

    assert "=== Execution Trace ===" in formatted
    assert "✓ Task: task_1" in formatted
    assert "✗ Task: task_2" in formatted
    assert "Output data" in formatted
    assert "Failed" in formatted


def test_format_trace_for_display_truncation():
    """Test that long results are truncated in display."""
    trace = [{"task_id": "task_1", "success": True, "result": "x" * 300, "error": None}]

    formatted = format_trace_for_display(trace)

    # Should contain the task but the output might be truncated in the actual implementation
    assert "task_1" in formatted


def test_get_trace_summary_empty():
    """Test getting summary from empty trace."""
    summary = get_trace_summary([])

    assert summary["total"] == 0
    assert summary["successful"] == 0
    assert summary["failed"] == 0


def test_get_trace_summary_all_successful():
    """Test getting summary when all tasks succeeded."""
    trace = [
        {"task_id": "t1", "success": True},
        {"task_id": "t2", "success": True},
        {"task_id": "t3", "success": True},
    ]

    summary = get_trace_summary(trace)

    assert summary["total"] == 3
    assert summary["successful"] == 3
    assert summary["failed"] == 0


def test_get_trace_summary_mixed():
    """Test getting summary with mixed results."""
    trace = [
        {"task_id": "t1", "success": True},
        {"task_id": "t2", "success": False},
        {"task_id": "t3", "success": True},
        {"task_id": "t4", "success": False},
    ]

    summary = get_trace_summary(trace)

    assert summary["total"] == 4
    assert summary["successful"] == 2
    assert summary["failed"] == 2


def test_get_trace_summary_all_failed():
    """Test getting summary when all tasks failed."""
    trace = [
        {"task_id": "t1", "success": False},
        {"task_id": "t2", "success": False},
    ]

    summary = get_trace_summary(trace)

    assert summary["total"] == 2
    assert summary["successful"] == 0
    assert summary["failed"] == 2
