"""Architect node: High-level milestone planner."""

import uuid

from agent.state import AgentState, SubGoal


def node(state: AgentState) -> AgentState:
    """Creates high-level milestones for the code repository analysis task."""
    # objective = state["objective"]

    # For code repository analysis, create standardized milestones
    milestones = [
        SubGoal(
            id=str(uuid.uuid4()),
            description="List all Python files in the project",
            assigned_skill="filesystem",
            status="pending",
        ),
        SubGoal(
            id=str(uuid.uuid4()),
            description="Read each Python file and extract function definitions",
            assigned_skill="code_reader",
            status="pending",
        ),
        SubGoal(
            id=str(uuid.uuid4()),
            description="Analyze functions for complexity issues (long functions, too many parameters, etc.)",
            assigned_skill="code_analyzer",
            status="pending",
        ),
        SubGoal(
            id=str(uuid.uuid4()),
            description="Generate a summary report of findings",
            assigned_skill="report_writer",
            status="pending",
        ),
    ]

    return {
        **state,
        "milestones": milestones,
        "current_idx": 0,  # Start with first milestone
        "tactical_plan": [],  # Reset tactical plan
        "active_skill_context": "",  # Reset skill context
        "last_verification_status": "",  # Reset validation status
    }
