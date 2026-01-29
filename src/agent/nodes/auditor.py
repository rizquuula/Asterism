"""Auditor node: Success validation and replanning."""

from agent.state import AgentState


def node(state: AgentState) -> AgentState:
    """Validates if the current milestone was completed successfully."""
    current_milestone = state["milestones"][state["current_idx"]]
    history = state.get("history", [])

    # Analyze the history to determine if the milestone was completed
    verification_status = "failed"  # Default to failed

    if not history:
        # No tools were executed
        verification_status = "failed"
    else:
        # Check the results of the executed tools
        successful_tools = [h for h in history if h.get("success", False)]
        # failed_tools = [h for h in history if not h.get("success", True)]

        skill_name = current_milestone.assigned_skill
        description = current_milestone.description.lower()

        # Milestone-specific validation logic
        if skill_name == "filesystem" and "list all python files" in description:
            # Check if we successfully listed Python files
            python_files_found = any(
                h.get("tool") == "filesystem:list_files" and h.get("success") and
                any(f.endswith('.py') for f in h.get("result", []))
                for h in successful_tools
            )
            if python_files_found:
                verification_status = "passed"

        elif skill_name == "code_reader" and "extract function definitions" in description:
            # Check if we successfully read some Python files
            files_read = any(
                h.get("tool") == "filesystem:read_file" and h.get("success")
                for h in successful_tools
            )
            if files_read:
                verification_status = "passed"

        elif skill_name == "code_analyzer" and "complexity issues" in description:
            # Check if we performed complexity analysis
            analysis_done = any(
                h.get("tool") == "code_parser:analyze_complexity" and h.get("success")
                for h in successful_tools
            )
            if analysis_done:
                verification_status = "passed"

        elif skill_name == "report_writer" and "summary report" in description:
            # Check if we wrote a report file
            report_written = any(
                h.get("tool") == "filesystem:write_file" and h.get("success")
                for h in successful_tools
            )
            if report_written:
                verification_status = "passed"

        else:
            # Generic validation: if any tools succeeded, consider it passed
            if successful_tools:
                verification_status = "passed"

    return {
        **state,
        "last_verification_status": verification_status
    }