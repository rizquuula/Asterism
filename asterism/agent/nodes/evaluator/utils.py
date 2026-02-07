"""Utility functions for the evaluator node."""

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from asterism.agent.models import EvaluationDecision, LLMUsage, Task, TaskInputResolverResult
from asterism.agent.state import AgentState
from asterism.llm.base import BaseLLMProvider


def get_user_request(state: AgentState) -> str:
    """Extract the original user request from state messages."""
    messages = state.get("messages", [])
    if messages:
        # Find the first human message
        for msg in messages:
            if isinstance(msg, HumanMessage):
                return msg.content
    return "No user request found"


def format_tasks(tasks: list, current_index: int) -> str:
    """Format tasks list with completion status."""
    lines = []
    for i, task in enumerate(tasks):
        status = "[✓]" if i < current_index else "[ ]"
        state_label = "COMPLETED" if i < current_index else ("NEXT" if i == current_index else "PENDING")
        tool_info = f" (tool: {task.tool_call})" if task.tool_call else " (LLM task)"
        lines.append(f"{status} {task.id}: {task.description}{tool_info} ({state_label})")
    return "\n".join(lines)


def format_execution_results(results: list) -> str:
    """Format execution results for the prompt."""
    if not results:
        return "No tasks executed yet."

    lines = []
    for result in results:
        status = "✓" if result.success else "✗"
        if result.success:
            # Truncate long results
            result_str = str(result.result)
            if len(result_str) > 200:
                result_str = result_str[:200] + "... [truncated]"
            lines.append(f"{status} {result.task_id}: {result_str}")
        else:
            lines.append(f"{status} {result.task_id}: ERROR - {result.error}")
    return "\n".join(lines)


def build_evaluator_prompt(state: AgentState) -> str:
    """Build the evaluation prompt from state."""
    plan = state.get("plan")
    execution_results = state.get("execution_results", [])
    current_index = state.get("current_task_index", 0)

    user_request = get_user_request(state)

    if not plan:
        return f"""=== USER REQUEST ===
{user_request}

=== CURRENT STATE ===
No plan exists. Replanning required.

=== DECISION ===
Decision: replan
Reasoning: No plan available to execute."""

    # Get last result info
    last_result = execution_results[-1] if execution_results else None

    return f"""=== USER REQUEST ===
{user_request}

=== CURRENT PLAN ===
Total tasks: {len(plan.tasks)}
Completed: {current_index}/{len(plan.tasks)}
Remaining: {len(plan.tasks) - current_index}

Plan reasoning: {plan.reasoning}

Tasks:
{format_tasks(plan.tasks, current_index)}

=== EXECUTION HISTORY ===
{format_execution_results(execution_results)}

=== CURRENT CONTEXT ===
Last task: {last_result.task_id if last_result else "N/A"}
Last result: {str(last_result.result)[:200] if last_result and last_result.result else "N/A"}
Last error: {last_result.error if last_result and last_result.error else "None"}

=== DECISION REQUIRED ===
Based on the execution so far, should we:
1. **continue** - Proceed to next task (execution on track)
2. **replan** - Current plan needs adjustment (unexpected results, failures, new information)
3. **finalize** - Goals achieved, can complete early (all critical tasks done, user satisfied)

Provide your evaluation with clear reasoning."""


def fallback_decision(state: AgentState) -> EvaluationDecision:
    """Fallback decision logic when LLM evaluation fails."""
    plan = state.get("plan")
    if not plan:
        return EvaluationDecision.REPLAN

    current_index = state.get("current_task_index", 0)
    if current_index >= len(plan.tasks):
        return EvaluationDecision.FINALIZE

    execution_results = state.get("execution_results", [])
    if execution_results and not execution_results[-1].success:
        return EvaluationDecision.REPLAN

    return EvaluationDecision.CONTINUE


def build_task_resolver_prompt(
    next_task: Task,
    execution_results: list,
    user_request: str,
) -> str:
    """Build prompt for resolving task inputs based on previous results."""
    # Format previous results
    results_context = ""
    for i, result in enumerate(execution_results):
        status = "✓" if result.success else "✗"
        result_str = str(result.result) if result.result else "None"
        if len(result_str) > 500:
            result_str = result_str[:500] + "... [truncated]"
        results_context += f"\nTask {i + 1} ({result.task_id}): {status}\nResult: {result_str}\n"

    current_input = next_task.tool_input or {}

    return f"""=== USER REQUEST ===
{user_request}

=== EXECUTION HISTORY ===
{results_context}

=== NEXT TASK TO RESOLVE ===
Task ID: {next_task.id}
Description: {next_task.description}
Tool: {next_task.tool_call}
Current tool_input: {current_input}

=== TASK ===
Analyze the execution history and update the tool_input for the next task.

The previous task results may contain information needed for this task (e.g., file paths, IDs, search results).

Instructions:
1. Review the execution history to find relevant information
2. Update the tool_input with actual values from previous results
3. Return ONLY a JSON object with the updated tool_input fields

Example:
If a search returned "/path/to/file.txt", and the next task needs to read it:
Current: {{"path": "file.txt"}}
Updated: {{"path": "/path/to/file.txt"}}

Return format:
{{"updated_tool_input": {{...}}}}

If no updates needed, return: {{"updated_tool_input": null}}"""


def resolve_next_task_inputs(
    llm: BaseLLMProvider,
    next_task: Task,
    state: AgentState,
) -> tuple[dict[str, Any] | None, LLMUsage | None]:
    """
    Resolve task inputs by analyzing previous execution results using LLM.

    Args:
        llm: The LLM provider for resolution.
        next_task: The task whose inputs need to be resolved.
        state: Current agent state with execution history.

    Returns:
        Tuple of (updated_tool_input or None, LLMUsage or None).
    """
    execution_results = state.get("execution_results", [])
    if not execution_results:
        return None, None

    user_request = get_user_request(state)

    # Build resolver prompt
    prompt = build_task_resolver_prompt(next_task, execution_results, user_request)

    try:
        # Use LLM to resolve inputs
        messages = [
            SystemMessage(
                content=(
                    "You are a task input resolver. "
                    "Extract information from previous results to update task inputs. "
                    "Return only valid JSON."
                )
            ),
            HumanMessage(content=prompt),
        ]

        response = llm.invoke_structured(
            messages,
            schema=TaskInputResolverResult,
        )

        # Track LLM usage
        usage = LLMUsage(
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            model=llm.model,
            node_name="evaluator_node_task_resolver",
        )

        # Parse response
        result = response.parsed
        if isinstance(result, TaskInputResolverResult):
            updated_input = result.updated_tool_input
            if updated_input is not None:
                return updated_input, usage

        return None, usage

    except Exception:
        # If resolution fails, return None to use original inputs
        return None, None
