"""Factory for creating LLM provider instances."""

import logging

from asterism.config import ModelProvider

from .providers import BaseLLMProvider, OpenAIProvider

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM provider instances from configuration."""

    @staticmethod
    def create_provider(provider_config: ModelProvider) -> BaseLLMProvider:
        """Create a single provider instance from configuration.

        Currently supports:
        - openai-compatible: OpenAI-compatible APIs (OpenRouter, LocalAI, etc.)

        Args:
            provider_config: Provider configuration from config file

        Returns:
            BaseLLMProvider: Configured provider instance

        Raises:
            ValueError: If provider type is not supported
        """
        if provider_config.type == "openai-compatible":
            # For OpenAI-compatible APIs, the model name will be set per-request
            # based on the model parameter passed to invoke()
            api_key = provider_config.api_key
            if not api_key:
                raise ValueError(f"API key is required for provider: {provider_config.name}")

            return OpenAIProvider(
                provider_name=provider_config.name,
                model="placeholder",  # Will be overridden per-request
                base_url=provider_config.base_url,
                api_key=api_key,
                prompt_loader=None,  # API mode doesn't use SOUL/AGENT prompts
            )

        raise ValueError(f"Unsupported provider type: {provider_config.type}")
