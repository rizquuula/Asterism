"""State manipulation utilities with immutable-style updates.

All functions return new state objects rather than modifying in place,
making state transitions explicit and testable.
"""

from langchain_core.messages import AIMessage, HumanMessage

from asterism.agent.models import (
    AgentResponse,
    EvaluationResult,
    LLMUsage,
    Plan,
    TaskResult,
)
from asterism.agent.state import AgentState


def create_error_state(state: AgentState, error: str) -> AgentState:
    """Create new state with error set.

    Also adds error message to conversation for context in replanning.
    """
    new_state = state.copy()
    new_state["error"] = error
    new_state["messages"] = state.get("messages", []) + [HumanMessage(content=f"[Error] {error}")]
    return new_state


def clear_error(state: AgentState) -> AgentState:
    """Create new state with error cleared."""
    new_state = state.copy()
    new_state["error"] = None
    return new_state


def append_llm_usage(state: AgentState, usage: LLMUsage) -> AgentState:
    """Create new state with LLM usage appended."""
    new_state = state.copy()
    new_state["llm_usage"] = state.get("llm_usage", []) + [usage]
    return new_state


def set_plan(state: AgentState, plan: Plan, usage: LLMUsage) -> AgentState:
    """Create new state with plan set and usage tracked."""
    new_state = state.copy()
    new_state["plan"] = plan
    new_state["current_task_index"] = 0
    new_state["error"] = None
    new_state["llm_usage"] = state.get("llm_usage", []) + [usage]
    return new_state


def advance_task(state: AgentState, result: TaskResult) -> AgentState:
    """Create new state with task result recorded and index advanced."""
    new_state = state.copy()
    new_state["execution_results"] = state.get("execution_results", []) + [result]
    new_state["current_task_index"] = state.get("current_task_index", 0) + 1
    new_state["error"] = None if result.success else result.error

    # Track LLM usage if task used LLM
    if result.llm_usage:
        new_state["llm_usage"] = new_state.get("llm_usage", []) + [result.llm_usage]

    return new_state


def set_evaluation_result(
    state: AgentState,
    evaluation: EvaluationResult,
    usage: LLMUsage,
) -> AgentState:
    """Create new state with evaluation result set."""
    new_state = state.copy()
    new_state["evaluation_result"] = evaluation
    new_state["llm_usage"] = state.get("llm_usage", []) + [usage]
    return new_state


def prepare_replan_state(
    state: AgentState,
    evaluation: EvaluationResult,
) -> AgentState:
    """Create new state prepared for replanning based on evaluation."""
    error_parts = [f"Replanning needed: {evaluation.reasoning}"]

    execution_results = state.get("execution_results", [])
    if execution_results:
        last_result = execution_results[-1]
        if not last_result.success:
            error_parts.append(f"Last task '{last_result.task_id}' failed: {last_result.error}")

    if evaluation.suggested_changes:
        error_parts.append(f"Suggested changes: {evaluation.suggested_changes}")

    new_state = state.copy()
    new_state["error"] = "\n".join(error_parts)

    # Add detailed context for planner
    replan_context = f"""[Evaluator] Replanning required.
Decision: {evaluation.decision}
Reasoning: {evaluation.reasoning}
Suggested changes: {evaluation.suggested_changes or "None provided"}"""
    new_state["messages"] = state.get("messages", []) + [AIMessage(content=replan_context)]

    return new_state


def set_final_response(
    state: AgentState,
    response: AgentResponse,
    usage: LLMUsage | None = None,
) -> AgentState:
    """Create new state with final response set."""
    new_state = state.copy()
    new_state["final_response"] = response
    new_state["error"] = None

    if usage:
        new_state["llm_usage"] = state.get("llm_usage", []) + [usage]

    return new_state


def get_parallelizable_tasks(plan) -> list:
    """Get tasks that can be executed in parallel (no inter-dependencies).

    This function identifies tasks from the current task index onward that
    have no dependencies on each other. These tasks can be executed in parallel
    using LangGraph's Send API.

    Args:
        plan: The Plan object with tasks.

    Returns:
        List of tasks that can be executed in parallel.
    """
    if not plan or not plan.tasks:
        return []

    tasks = plan.tasks

    # Find the starting index for parallel tasks
    # We look for tasks that can run in parallel from current position
    parallel_tasks = []

    for task in tasks:
        # Check if this task depends on any task in our parallel list
        depends_on_parallel = any(dep in [t.id for t in parallel_tasks] for dep in task.depends_on)

        # If task has no dependencies on already-collected parallel tasks, add it
        if not depends_on_parallel:
            parallel_tasks.append(task)

    return parallel_tasks


def get_independent_tasks(tasks: list, completed_task_ids: set) -> list:
    """Get tasks that have all their dependencies satisfied and are not completed.

    Args:
        tasks: List of Task objects.
        completed_task_ids: Set of task IDs that have been completed.

    Returns:
        List of tasks whose dependencies are all satisfied and are not yet completed.
    """
    independent = []
    for task in tasks:
        # Skip already completed tasks
        if task.id in completed_task_ids:
            continue

        # Check if all dependencies are satisfied
        deps_satisfied = all(dep_id in completed_task_ids for dep_id in task.depends_on)
        if deps_satisfied:
            independent.append(task)
    return independent
