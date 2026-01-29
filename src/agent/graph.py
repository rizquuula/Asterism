from typing import Literal
from langgraph.graph import StateGraph, END, START
from .state import AgentState
from .nodes import architect, router, refiner, executor, auditor


# 1. Define the Logic for Conditional Edges
def should_continue(state: AgentState) -> Literal["route_skill", "end"]:
    """Determines if there are more milestones or if we are finished."""
    if state["current_idx"] >= len(state["milestones"]):
        return "end"
    return "route_skill"


def check_validation(state: AgentState) -> Literal["next_milestone", "retry"]:
    """Decides if the sub-goal was met or needs a re-plan."""
    if state["last_verification_status"] == "passed":
        return "next_milestone"
    return "retry"


def next_milestone(state: AgentState) -> AgentState:
    """Advance to the next milestone."""
    return {
        **state,
        "current_idx": state["current_idx"] + 1,
        "last_verification_status": ""  # Reset for next milestone
    }


# 2. Build the Graph
def create_agent_graph():
    workflow = StateGraph(AgentState)

    # Add our Hierarchical Nodes
    workflow.add_node("architect", architect.node)      # Global Planner
    workflow.add_node("router", router.node)            # Skill/MCP Loader
    workflow.add_node("refiner", refiner.node)          # Tactical Planner
    workflow.add_node("executor", executor.node)        # Tool Executor
    workflow.add_node("auditor", auditor.node)          # Quality Control

    # Add helper node for milestone advancement
    workflow.add_node("next_milestone", next_milestone)

    # 3. Define the Flow
    workflow.add_edge(START, "architect")

    # After planning, we check if we have milestones to process
    workflow.add_conditional_edges(
        "architect",
        should_continue,
        {
            "route_skill": "router",
            "end": END
        }
    )

    # The Skill Loop: Routing -> Refining -> Executing
    workflow.add_edge("router", "refiner")
    workflow.add_edge("refiner", "executor")
    workflow.add_edge("executor", "auditor")

    # The Validation Loop (Self-Healing)
    workflow.add_conditional_edges(
        "auditor",
        check_validation,
        {
            "next_milestone": "next_milestone",
            "retry": "router"  # Try the same milestone again with context
        }
    )

    # After advancing milestone, check if we continue or end
    workflow.add_conditional_edges(
        "next_milestone",
        should_continue,
        {
            "route_skill": "router",
            "end": END
        }
    )

    return workflow.compile()


# Export the compiled graph
app = create_agent_graph()