"""Refiner node: Tactical planner that breaks milestones into tool calls."""

from agent.state import AgentState


def node(state: AgentState) -> AgentState:
    """Breaks the current milestone into specific MCP tool invocations."""
    current_milestone = state["milestones"][state["current_idx"]]
    skill_name = current_milestone.assigned_skill
    description = current_milestone.description

    # Create tactical plan based on skill and milestone
    tactical_plan = []

    if skill_name == "filesystem":
        if "list all python files" in description.lower():
            tactical_plan = ["filesystem:list_files(pattern=*.py)", "filesystem:list_files(pattern=**/*.py)"]
        else:
            tactical_plan = ["filesystem:list_files()"]

    elif skill_name == "code_reader":
        if "extract function definitions" in description.lower():
            tactical_plan = ["filesystem:read_file(path={file})" for file in state.get("python_files", [])]
            if not tactical_plan:
                tactical_plan = ["filesystem:read_file(path=example.py)"]
        else:
            tactical_plan = ["filesystem:read_file(path=main.py)"]

    elif skill_name == "code_analyzer":
        if "complexity issues" in description.lower():
            tactical_plan = ["code_parser:analyze_complexity(functions={functions})"]
        else:
            tactical_plan = ["code_parser:analyze_complexity()"]

    elif skill_name == "report_writer":
        if "summary report" in description.lower():
            tactical_plan = ["filesystem:write_file(path=analysis_report.md,content={report})"]
        else:
            tactical_plan = ["filesystem:write_file(path=report.md,content=Analysis complete)"]

    else:
        # Default tactical plan for unknown skills
        tactical_plan = [f"unknown:execute_task(description={description})"]

    return {**state, "tactical_plan": tactical_plan}
