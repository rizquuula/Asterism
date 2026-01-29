from typing import Literal, TypedDict

from pydantic import BaseModel


class SubGoal(BaseModel):
    """Represents a high-level milestone in the task execution."""

    id: str
    description: str
    assigned_skill: str
    status: Literal["pending", "active", "completed", "failed"]


class AgentState(TypedDict):
    """Global state for the hierarchical agent workflow."""

    objective: str  # The original user request
    milestones: list[SubGoal]  # The high-level plan
    current_idx: int  # Index of the active milestone
    tactical_plan: list[str]  # Atomic steps for the current skill
    history: list[dict]  # Tool results & observations
    active_skill_context: str  # Current system prompt injection
    last_verification_status: str  # "passed" or "failed" for validation


# Type aliases for clarity
Milestones = list[SubGoal]
TacticalPlan = list[str]
History = list[dict]
