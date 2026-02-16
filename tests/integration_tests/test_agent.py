"""Integration test for the complete agent workflow."""

import os
import tempfile

import pytest
import yaml
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from asterism.agent.agent import Agent
from asterism.config import Config
from asterism.llm.provider_router import LLMProviderRouter
from asterism.mcp.executor import MCPExecutor

load_dotenv()


def agent_invoke(message: dict):
    """Test agent invocation with real LLM."""

    if not os.getenv("TEST_OPENAI_PROVIDER_NAME"):
        pytest.skip("TEST_OPENAI_PROVIDER_NAME not set")

    if not os.getenv("TEST_OPENAI_BASE_URL"):
        pytest.skip("TEST_OPENAI_BASE_URL not set")

    if not os.getenv("TEST_OPENAI_API_KEY"):
        pytest.skip("TEST_OPENAI_API_KEY not set")

    if not os.getenv("TEST_OPENAI_MODEL"):
        pytest.skip("TEST_OPENAI_MODEL not set")

    # Define the target directory
    target_dir = "./workspace"

    # Change the directory if it exists
    if os.path.exists(target_dir):
        os.chdir(target_dir)
        print(f"CWD changed to: {os.getcwd()}")
    else:
        print(f"Warning: {target_dir} not found. Staying in current directory.")

    # Create temporary workspace with config.yaml
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create config.yaml for LLMProviderRouter
        config_data = {
            "agent": {
                "name": "TestAgent",
                "version": "1.0.0",
                "description": "Test agent",
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": True,
                "cors_origins": ["*"],
            },
            "models": {
                "provider": [
                    {
                        "type": "openai-compatible",
                        "name": "env.TEST_OPENAI_PROVIDER_NAME",
                        "base_url": "env.TEST_OPENAI_BASE_URL",
                        "api_key": "env.TEST_OPENAI_API_KEY",
                    }
                ],
                "default": "env.TEST_OPENAI_MODEL",
                "fallback": [],
            },
            "mcp": {
                "servers_file": "mcp_servers/mcp_servers.json",
                "timeout": 30,
            },
        }

        config_path = os.path.join(tmp_dir, "config.yaml")
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Reset Config singleton and create new instance with temp workspace
        Config.reset_instance()
        config = Config(workspace_path=tmp_dir)

        # Create LLM provider router with fallback support
        llm = LLMProviderRouter(config=config)

        mcp_executor = MCPExecutor(
            config_path=config.get_mcp_servers_file(),
        )

        agent = Agent(
            llm=llm,
            mcp_executor=mcp_executor,
            db_path=":memory:",
        )

        response = agent.invoke(
            session_id="test-session",
            messages=[message],
        )

        agent.close()

        assert response["session_id"] == "test-session"
        assert "message" in response
        assert response.get("error") is None


@pytest.mark.parametrize(
    "message",
    (
        "What time is it now?",
        # "Can you read your SOUL.md and tell me what inside?",
        # "Can you change your name in personality.md from Asteri to Yui? I want a cute name",
    ),
)
def test_agent_invoke(message: str):
    user_message = HumanMessage(content=message)
    agent_invoke(user_message)
