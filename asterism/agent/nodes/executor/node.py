"""Executor node implementation - executes tasks in the plan."""

import logging
from typing import Any

from langgraph.types import Send

from asterism.agent.nodes.executor.task_runner import create_task_runner
from asterism.agent.nodes.shared import (
    advance_task,
    are_dependencies_satisfied,
    create_error_state,
    get_current_task,
    get_independent_tasks,
    is_linear_plan,
)
from asterism.agent.state import AgentState
from asterism.llm.providers import BaseLLMProvider
from asterism.mcp.executor import MCPExecutor

logger = logging.getLogger(__name__)


def executor_node(
    llm: BaseLLMProvider,
    mcp_executor: MCPExecutor,
    state: AgentState,
) -> AgentState:
    """Execute the current task in the plan.

    For linear plans (sequential tasks with simple dependencies), this will
    batch execute all remaining tasks in a single pass, reducing the number
    of evaluator calls needed.

    If the plan has no tasks (empty tasks array), skip execution entirely
    and return state as-is. This handles simple queries that don't need tools.

    Args:
        llm: The LLM provider for LLM-only tasks.
        mcp_executor: The MCP executor for tool calls.
        state: Current agent state.

    Returns:
        Updated state with execution result(s).
    """
    plan = state.get("plan")

    # Skip execution if plan has no tasks (simple query - no tools needed)
    if not plan or not plan.tasks:
        logger.info("[executor] No tasks to execute (empty plan), skipping executor")
        return state

    # Check if this is a linear plan that can be batch executed
    if is_linear_plan(plan):
        return _execute_linear_plan(llm, mcp_executor, state)

    # Standard single-task execution for non-linear plans
    return _execute_single_task(llm, mcp_executor, state)


def _execute_linear_plan(
    llm: BaseLLMProvider,
    mcp_executor: MCPExecutor,
    state: AgentState,
) -> AgentState:
    """Execute tasks in a linear plan sequentially without intermediate evaluations.

    This optimization executes all remaining tasks in a linear plan in one pass,
    only stopping if a task fails. This eliminates unnecessary evaluator calls
    between tasks in a simple sequential workflow.

    Args:
        llm: The LLM provider for LLM-only tasks.
        mcp_executor: The MCP executor for tool calls.
        state: Current agent state.

    Returns:
        Updated state with all execution results.
    """
    # plan = state.get("plan")
    current_state = state
    executed_count = 0

    while True:
        task = get_current_task(current_state)

        if not task:
            # No more tasks to execute
            break

        if not are_dependencies_satisfied(task, current_state):
            deps = [d for d in task.depends_on]
            return create_error_state(current_state, f"Dependencies not satisfied: {deps}")

        logger.info(f"[executor] Starting task {task.id}: {task.description[:80]}")

        runner = create_task_runner(task, llm, mcp_executor)
        result = runner.execute(task, current_state)

        log_task_completion(task.id, result.success)
        executed_count += 1

        # Advance to next task
        current_state = advance_task(current_state, result)

        # Stop batch execution if task failed
        if not result.success:
            logger.info("[executor] Stopping batch execution due to task failure")
            break

    if executed_count > 1:
        logger.info(f"[executor] Batch executed {executed_count} tasks in linear plan")

    return current_state


def _execute_single_task(
    llm: BaseLLMProvider,
    mcp_executor: MCPExecutor,
    state: AgentState,
) -> AgentState:
    """Execute a single task (standard mode for non-linear plans).

    Args:
        llm: The LLM provider for LLM-only tasks.
        mcp_executor: The MCP executor for tool calls.
        state: Current agent state.

    Returns:
        Updated state with execution result.
    """
    task = get_current_task(state)

    if not task:
        return create_error_state(state, "No task to execute")

    if not are_dependencies_satisfied(task, state):
        deps = [d for d in task.depends_on]
        return create_error_state(state, f"Dependencies not satisfied: {deps}")

    logger.info(f"[executor] Starting task {task.id}: {task.description[:80]}")

    runner = create_task_runner(task, llm, mcp_executor)
    result = runner.execute(task, state)

    log_task_completion(task.id, result.success)

    return advance_task(state, result)


def log_task_completion(task_id: str, success: bool) -> None:
    """Log task completion status."""
    if success:
        logger.info(f"[executor] Task {task_id} completed successfully")
    else:
        logger.warning(f"[executor] Task {task_id} failed")


# Parallel execution functions using LangGraph Send API


def executor_node_with_parallel(
    llm: BaseLLMProvider,
    mcp_executor: MCPExecutor,
    state: AgentState,
) -> list[Send]:
    """Entry point for executor that supports parallel execution.

    This function uses LangGraph's Send API to dispatch independent tasks
    to be executed in parallel. It returns a list of Send objects, each
    targeting the parallel_execute_task node with the task data.

    If the plan has no tasks (empty tasks array), skip execution entirely
    and return state as-is. This handles simple queries that don't need tools.

    Args:
        llm: The LLM provider for LLM-only tasks.
        mcp_executor: The MCP executor for tool calls.
        state: Current agent state.

    Returns:
        List of Send objects for parallel execution, or single task update.
    """
    plan = state.get("plan")

    # Skip execution if plan has no tasks (simple query - no tools needed)
    if not plan or not plan.tasks:
        logger.info("[executor] No tasks to execute (empty plan), skipping parallel executor")
        return state

    # Get completed task IDs
    execution_results = state.get("execution_results", [])
    completed_task_ids = {r.task_id for r in execution_results}

    # Get remaining tasks
    remaining_tasks = plan.tasks[len(execution_results) :]

    # Find independent tasks that can run in parallel
    independent_tasks = get_independent_tasks(remaining_tasks, completed_task_ids)

    if len(independent_tasks) <= 1:
        # No parallelization possible, use standard execution
        return _execute_single_task(llm, mcp_executor, state)

    # Create Send objects for parallel execution
    logger.info(f"[executor] Executing {len(independent_tasks)} tasks in parallel")
    sends = []
    for task in independent_tasks:
        sends.append(
            Send(
                "parallel_execute_task",
                {
                    "task": task,
                    "parent_state": state,
                },
            )
        )

    return sends


def parallel_execute_task(
    llm: BaseLLMProvider,
    mcp_executor: MCPExecutor,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Execute a single task in parallel.

    This node receives task data via Send and executes it, returning
    the result to be aggregated by the reducer.

    Args:
        llm: The LLM provider for LLM-only tasks.
        mcp_executor: The MCP executor for tool calls.
        data: Dictionary containing task and parent_state.

    Returns:
        Dictionary with execution result to be merged into state.
    """
    task = data.get("task")
    parent_state = data.get("parent_state", {})

    if not task:
        return {"parallel_results": []}

    logger.info(f"[executor] Parallel executing task {task.id}: {task.description[:80]}")

    runner = create_task_runner(task, llm, mcp_executor)
    result = runner.execute(task, parent_state)

    log_task_completion(task.id, result.success)

    return {
        "parallel_results": [result],
    }
