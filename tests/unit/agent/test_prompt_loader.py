"""Test prompt loader module."""

from asterism.agent.prompt_loader import SystemPromptLoader


def test_prompt_loader_re_export():
    """Test that SystemPromptLoader is properly re-exported from core."""
    from asterism.core.prompt_loader import SystemPromptLoader as CoreLoader

    assert SystemPromptLoader is CoreLoader


def test_prompt_loader_all_exports():
    """Test that __all__ contains expected exports."""
    from asterism.agent import prompt_loader

    assert hasattr(prompt_loader, "__all__")
    assert "SystemPromptLoader" in prompt_loader.__all__
