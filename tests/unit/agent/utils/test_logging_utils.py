"""Test logging utilities."""

from unittest.mock import MagicMock, patch

from asterism.agent.models import Plan, Task, TaskResult
from asterism.agent.state import AgentState
from asterism.agent.utils.logging_utils import (
    get_logger_context,
    log_evaluation_decision,
    log_llm_call,
    log_llm_call_start,
    log_mcp_tool_call,
    log_node_execution,
    log_plan_created,
    log_task_execution,
)


def test_get_logger_context_basic():
    """Test basic logger context building."""
    state: AgentState = {
        "session_id": "session_123",
        "trace_id": "trace_456",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    context = get_logger_context(state, "test_node")

    assert context["node"] == "test_node"
    assert context["session_id"] == "session_123"
    assert context["trace_id"] == "trace_456"


def test_get_logger_context_with_plan():
    """Test logger context with plan."""
    plan = Plan(tasks=[Task(id="t1", description="Task 1"), Task(id="t2", description="Task 2")], reasoning="Test")

    state: AgentState = {
        "session_id": "session_123",
        "trace_id": "trace_456",
        "messages": [],
        "plan": plan,
        "current_task_index": 1,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    context = get_logger_context(state, "executor_node")

    assert context["plan_task_count"] == 2
    assert context["current_task_index"] == 1


def test_get_logger_context_with_execution_results():
    """Test logger context with execution results."""
    result = TaskResult(task_id="task_1", success=True, result="output")

    state: AgentState = {
        "session_id": "session_123",
        "trace_id": "trace_456",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [result],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    context = get_logger_context(state, "evaluator_node")

    assert context["completed_tasks"] == 1
    assert context["last_task_id"] == "task_1"
    assert context["last_task_success"] is True


def test_get_logger_context_with_error():
    """Test logger context with error."""
    state: AgentState = {
        "session_id": "session_123",
        "trace_id": "trace_456",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": "Something went wrong",
        "llm_usage": [],
    }

    context = get_logger_context(state, "planner_node")

    assert context["has_error"] is True
    assert "error_preview" in context


def test_get_logger_context_no_trace_id():
    """Test logger context without trace_id."""
    state: AgentState = {
        "session_id": "session_123",
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

    context = get_logger_context(state, "test_node")

    # The actual implementation returns None when trace_id is None, not "unknown"
    assert context["trace_id"] is None


def test_log_llm_call_success():
    """Test successful LLM call logging."""
    mock_logger = MagicMock()

    log_llm_call(
        logger=mock_logger,
        node_name="planner_node",
        model="gpt-4",
        prompt_tokens=100,
        completion_tokens=50,
        duration_ms=500.0,
        prompt_preview="Test prompt",
        response_preview="Test response",
        success=True,
    )

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    assert "planner_node" in call_args[0][0]
    assert call_args[1]["extra"]["agent_context"]["success"] is True


def test_log_llm_call_failure():
    """Test failed LLM call logging."""
    mock_logger = MagicMock()

    log_llm_call(
        logger=mock_logger,
        node_name="executor_node",
        model="gpt-4",
        prompt_tokens=0,
        completion_tokens=0,
        duration_ms=100.0,
        success=False,
        error="Connection timeout",
    )

    mock_logger.error.assert_called_once()
    call_args = mock_logger.error.call_args
    assert call_args[1]["extra"]["agent_context"]["success"] is False


def test_log_llm_call_start():
    """Test LLM call start logging."""
    mock_logger = MagicMock()

    log_llm_call_start(
        logger=mock_logger,
        node_name="evaluator_node",
        model="gpt-4",
        action="evaluating execution",
        prompt_preview="Test prompt content",
    )

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    context = call_args[1]["extra"]["agent_context"]
    assert context["node"] == "evaluator_node"
    assert context["action"] == "evaluating execution"


def test_log_task_execution_success():
    """Test successful task execution logging."""
    mock_logger = MagicMock()

    log_task_execution(
        logger=mock_logger,
        task_id="task_1",
        task_type="tool",
        success=True,
        duration_ms=250.0,
        tool_call="filesystem:list_files",
        result_preview="Files listed successfully",
    )

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    context = call_args[1]["extra"]["agent_context"]
    assert context["task_id"] == "task_1"
    assert context["success"] is True


def test_log_task_execution_failure():
    """Test failed task execution logging."""
    mock_logger = MagicMock()

    log_task_execution(
        logger=mock_logger,
        task_id="task_2",
        task_type="llm",
        success=False,
        duration_ms=1000.0,
        error="Model failed to respond",
    )

    mock_logger.warning.assert_called_once()
    call_args = mock_logger.warning.call_args
    context = call_args[1]["extra"]["agent_context"]
    assert context["success"] is False


def test_log_plan_created():
    """Test plan creation logging."""
    mock_logger = MagicMock()

    log_plan_created(
        logger=mock_logger,
        task_count=5,
        task_ids=["t1", "t2", "t3", "t4", "t5"],
        has_dependencies=True,
        reasoning_preview="Plan to solve the problem",
    )

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    context = call_args[1]["extra"]["agent_context"]
    assert context["task_count"] == 5
    assert context["has_dependencies"] is True


def test_log_evaluation_decision():
    """Test evaluation decision logging."""
    mock_logger = MagicMock()

    log_evaluation_decision(
        logger=mock_logger,
        decision="continue",
        reasoning_preview="Progress is good",
        suggested_changes=None,
    )

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    context = call_args[1]["extra"]["agent_context"]
    assert context["decision"] == "continue"


def test_log_evaluation_decision_with_suggestions():
    """Test evaluation decision logging with suggestions."""
    mock_logger = MagicMock()

    log_evaluation_decision(
        logger=mock_logger,
        decision="replan",
        reasoning_preview="Need to adjust approach",
        suggested_changes="Add error handling",
    )

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    context = call_args[1]["extra"]["agent_context"]
    assert context["suggested_changes"] == "Add error handling"


def test_log_mcp_tool_call_success():
    """Test successful MCP tool call logging."""
    mock_logger = MagicMock()

    log_mcp_tool_call(
        logger=mock_logger,
        server_name="filesystem",
        tool_name="list_files",
        input_keys=["directory"],
        success=True,
        duration_ms=100.0,
        result_preview="file1.txt, file2.txt",
    )

    mock_logger.info.assert_called_once()
    call_args = mock_logger.info.call_args
    context = call_args[1]["extra"]["agent_context"]
    assert context["server"] == "filesystem"
    assert context["tool"] == "list_files"


def test_log_mcp_tool_call_failure():
    """Test failed MCP tool call logging."""
    mock_logger = MagicMock()

    log_mcp_tool_call(
        logger=mock_logger,
        server_name="code_parser",
        tool_name="parse_file",
        input_keys=["path"],
        success=False,
        duration_ms=50.0,
        error="File not found",
    )

    mock_logger.warning.assert_called_once()
    call_args = mock_logger.warning.call_args
    context = call_args[1]["extra"]["agent_context"]
    assert context["success"] is False


@patch("asterism.agent.utils.logging_utils.get_logger_context")
@patch("time.perf_counter")
def test_log_node_execution_decorator(mock_perf_counter, mock_get_context):
    """Test node execution decorator."""
    mock_perf_counter.side_effect = [0.0, 0.1]  # Start and end times
    mock_get_context.return_value = {"node": "test_node", "session_id": "123"}

    @log_node_execution("test_node")
    def dummy_node_func(llm, mcp, state):
        return {"error": None, "evaluation_result": None}

    mock_llm = MagicMock()
    mock_mcp = MagicMock()
    mock_state: AgentState = {
        "session_id": "123",
        "trace_id": "456",
        "messages": [],
        "plan": None,
        "current_task_index": 0,
        "execution_results": [],
        "evaluation_result": None,
        "final_response": None,
        "error": None,
        "llm_usage": [],
    }

    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        result = dummy_node_func(mock_llm, mock_mcp, mock_state)

        assert result is not None
        mock_logger.info.assert_called()
