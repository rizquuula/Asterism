"""Full graph builder - includes all nodes including finalizer."""

from typing import TYPE_CHECKING

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from asterism.agent.graph_builders.base import (
    _make_finalizer_node,
    add_common_edges,
    add_common_nodes,
    make_routing_function,
)
from asterism.agent.state import AgentState

if TYPE_CHECKING:
    from asterism.agent.agent import Agent


def _should_use_parallel_executor(state: AgentState) -> str:
    """Determine if parallel executor should be used.

    Returns "parallel_executor_node" if there are independent tasks that can
    run in parallel, otherwise returns "executor_node" for sequential execution.
    """
    from asterism.agent.nodes.shared.state_utils import get_independent_tasks

    plan = state.get("plan")
    if not plan:
        return "executor_node"

    # Get completed task IDs
    execution_results = state.get("execution_results", [])
    completed_task_ids = {r.task_id for r in execution_results}

    # Get remaining tasks
    remaining_tasks = plan.tasks[len(execution_results) :]

    # Find independent tasks that can run in parallel
    independent_tasks = get_independent_tasks(remaining_tasks, completed_task_ids)

    # Use parallel executor if there are 2+ independent tasks
    if len(independent_tasks) >= 2:
        return "parallel_executor_node"

    return "executor_node"


def build_full_graph(
    agent: "Agent",
    checkpointer: BaseCheckpointSaver | None = None,
) -> StateGraph:
    """Build the complete agent graph with all nodes.

    This graph includes: planner → executor → evaluator → finalizer → END
    Use this for standard invoke() operations.

    The executor node will automatically use parallel execution when there
    are independent tasks that can run in parallel.

    Args:
        agent: The Agent instance with dependencies.
        checkpointer: Optional checkpointer for state persistence.

    Returns:
        Compiled StateGraph ready for execution.
    """
    workflow = StateGraph(AgentState)

    # Add common nodes (planner, executor, evaluator, parallel executor)
    add_common_nodes(workflow, agent)

    # Add finalizer node
    workflow.add_node("finalizer_node", _make_finalizer_node(agent))

    # Add common edges (START → planner → executor → evaluator)
    add_common_edges(workflow)

    # Add conditional edge from planner to choose between sequential and parallel executor
    workflow.add_conditional_edges(
        "planner_node",
        _should_use_parallel_executor,
        {
            "executor_node": "executor_node",
            "parallel_executor_node": "parallel_executor_node",
        },
    )

    # Add parallel execution edges
    # parallel_executor_node uses Send API to dispatch tasks to parallel_execute_task
    # After parallel execution, aggregate results and go to evaluator
    workflow.add_edge("parallel_executor_node", "parallel_execute_task")
    workflow.add_edge("parallel_execute_task", "evaluator_node")

    # Add conditional edges from evaluator
    # Routes: planner_node | executor_node | finalizer_node
    workflow.add_conditional_edges(
        "evaluator_node",
        make_routing_function(agent),
        {
            "planner_node": "planner_node",
            "executor_node": "executor_node",
            "finalizer_node": "finalizer_node",
        },
    )

    # Finalizer → END
    workflow.add_edge("finalizer_node", END)

    # Compile with or without checkpointing
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()
