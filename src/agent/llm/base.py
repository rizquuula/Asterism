"""Base LLM provider interface for the agent framework."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def invoke(self, prompt: str, **kwargs) -> str:
        """
        Invoke the LLM with a text prompt.

        Args:
            prompt: The text prompt to send to the LLM
            **kwargs: Additional provider-specific parameters

        Returns:
            The LLM's text response
        """
        pass

    @abstractmethod
    def invoke_structured(self, prompt: str, schema: type, **kwargs) -> Any:
        """
        Invoke the LLM with a structured output request.

        Args:
            prompt: The text prompt to send to the LLM
            schema: Pydantic model or type for structured output
            **kwargs: Additional provider-specific parameters

        Returns:
            Parsed structured output matching the schema
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the LLM provider."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Model name/version being used."""
        pass
