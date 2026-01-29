"""Main application entry point for the AI Agent Boilerplate."""

from pathlib import Path

from dotenv import load_dotenv

from agent.graph import app


def main():
    """Run the AI agent with code repository analysis example."""
    print("AI Agent Boilerplate - Code Repository Analysis")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Use mock provider for demonstration (no API key needed)
    print("Using Mock LLM Provider (for demonstration)")
    print()

    # Example objective: Code repository analysis
    objective = "Analyze this Python project and identify all functions with complexity issues"

    print(f"Objective: {objective}")
    print()

    try:
        # Initialize agent state
        initial_state = {
            "objective": objective,
            "milestones": [],
            "current_idx": 0,
            "tactical_plan": [],
            "history": [],
            "active_skill_context": "",
            "last_verification_status": "",
        }

        print("Starting agent workflow...")
        print()

        # Run the agent
        result = None
        for output in app.stream(initial_state):
            for node_name, state in output.items():
                print(f"Executing node: {node_name}")

                # Show current milestone if available
                if state.get("milestones") and state.get("current_idx") < len(state["milestones"]):
                    current_milestone = state["milestones"][state["current_idx"]]
                    print(f"   Milestone: {current_milestone.description}")
                    print(f"   Skill: {current_milestone.assigned_skill}")

                # Show tactical plan if available
                if state.get("tactical_plan"):
                    print(f"   Tools: {', '.join(state['tactical_plan'])}")

                # Show verification status
                if state.get("last_verification_status"):
                    status = state["last_verification_status"]
                    icon = "PASS" if status == "passed" else "FAIL"
                    print(f"   Status: {icon} {status}")

                print()

            result = state

        print("Agent execution completed!")
        print()

        # Show final results
        if result and result.get("history"):
            print("Execution Summary:")
            print("-" * 30)

            successful_tools = [h for h in result["history"] if h.get("success")]
            failed_tools = [h for h in result["history"] if not h.get("success")]

            print(f"Successful tool calls: {len(successful_tools)}")
            print(f"Failed tool calls: {len(failed_tools)}")

            if successful_tools:
                print("\nTools executed successfully:")
                for tool in successful_tools:
                    tool_call = tool.get("tool_call", "unknown")
                    result_preview = str(tool.get("result", ""))[:100]
                    print(f"   * {tool_call}: {result_preview}...")

        # Check for generated report
        report_path = Path("analysis_report.md")
        if report_path.exists():
            print(f"\nReport generated: {report_path}")
            print("   You can view the analysis report in the file above.")

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        import traceback

        traceback.print_exc()

    print("\nDemo completed!")
    print("\nTo use with a real LLM provider:")
    print("1. Set OPENAI_API_KEY in your .env file")
    print("2. Update the code to use OpenAIProvider instead of MockProvider")


if __name__ == "__main__":
    main()
