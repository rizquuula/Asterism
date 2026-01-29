"""Router node: Skill and MCP tool selector."""

from pathlib import Path

import yaml

from agent.state import AgentState


def load_skill_data(skill_name: str) -> dict:
    """Load skill configuration from filesystem."""
    skill_dir = Path(__file__).parent.parent.parent / "skills" / skill_name

    # Load prompt
    prompt_file = skill_dir / "prompt.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Skill prompt file not found: {prompt_file}")

    with open(prompt_file) as f:
        system_prompt = f.read().strip()

    # Load tools configuration
    tools_file = skill_dir / "tools.yaml"
    if not tools_file.exists():
        raise FileNotFoundError(f"Skill tools file not found: {tools_file}")

    with open(tools_file) as f:
        tools_config = yaml.safe_load(f)

    return {
        "system_prompt": system_prompt,
        "mcp_servers": tools_config.get("mcp_servers", []),
        "allowed_tools": tools_config.get("allowed_tools", []),
    }


def node(state: AgentState) -> AgentState:
    """Loads the assigned skill's configuration and sets up the active context."""
    current_milestone = state["milestones"][state["current_idx"]]
    skill_name = current_milestone.assigned_skill

    try:
        skill_config = load_skill_data(skill_name)

        # Create the active skill context
        skill_context = f"""
You are operating with the "{skill_name}" skill.

{skill_config["system_prompt"]}

Current milestone: {current_milestone.description}

Available MCP servers: {", ".join(skill_config["mcp_servers"])}
Allowed tools: {", ".join(skill_config["allowed_tools"])}

Focus on completing this milestone using the available tools and your expertise.
"""

        return {**state, "active_skill_context": skill_context.strip()}

    except FileNotFoundError:
        # If skill configuration is missing, create a basic context
        skill_context = f"""
You are operating with the "{skill_name}" skill.

Current milestone: {current_milestone.description}

Note: Skill configuration files not found. Using basic capabilities.
"""

        return {**state, "active_skill_context": skill_context.strip()}
