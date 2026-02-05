"""OpenAI LLM provider implementation."""

import os
from typing import Any

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from asterism.core.prompt_loader import SystemPromptLoader

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider using LangChain.

    This provider supports both simple string prompts and full message-based
    conversations. When a SystemPromptLoader is configured, SOUL.md and
    AGENT.md content will be automatically prepended to all LLM calls.
    """

    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        prompt_loader: SystemPromptLoader | None = None,
        **kwargs,
    ):
        """
        Initialize OpenAI provider.

        Args:
            model: OpenAI model name/version
            base_url: OpenAI base URL (if None, uses default OpenAI URL)
            api_key: OpenAI API key (if None, uses OPENAI_API_KEY env var)
            prompt_loader: Optional SystemPromptLoader for loading SOUL.md and AGENT.md.
                          If provided, these files' content will be prepended to all LLM calls.
            **kwargs: Additional LangChain ChatOpenAI parameters
        """
        super().__init__(prompt_loader=prompt_loader)
        self._model = model
        self._base_url = base_url
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self._api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

        # Initialize LangChain OpenAI client
        self.client = ChatOpenAI(model=model, base_url=self._base_url, api_key=self._api_key, **kwargs)

    def invoke(
        self,
        prompt: str | list[BaseMessage],
        **kwargs,
    ) -> str:
        """
        Invoke OpenAI LLM with a text prompt or message list.

        If a string is provided, it will be converted to a HumanMessage.
        If a prompt_loader is configured, SOUL.md and AGENT.md content
        will be prepended as a SystemMessage.

        Args:
            prompt: Either a text prompt (str) or a list of messages.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The LLM's text response.
        """
        # Build full message list with system prompts
        messages = self._build_messages(prompt, **kwargs)

        try:
            response = self.client.invoke(messages, **kwargs)
            return response.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    def invoke_structured(
        self,
        prompt: str | list[BaseMessage],
        schema: type,
        **kwargs,
    ) -> Any:
        """
        Invoke OpenAI LLM with structured output.

        If a string is provided, it will be converted to a HumanMessage.
        If a prompt_loader is configured, SOUL.md and AGENT.md content
        will be prepended as a SystemMessage.

        Args:
            prompt: Either a text prompt (str) or a list of messages.
            schema: Pydantic model or type for structured output.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Parsed structured output matching the schema.
        """
        try:
            # Build full message list with system prompts (SOUL + AGENT)
            full_messages = self._build_messages(prompt, **kwargs)

            # Convert messages to text for the template
            prompt_text = self._messages_to_text(full_messages)

            # Create output parser
            parser = PydanticOutputParser(pydantic_object=schema)

            template = PromptTemplate(
                template="{prompt}\n\n{format_instructions}",
                input_variables=["prompt"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )

            # Create chain
            chain = template | self.client | parser

            # Invoke and parse
            result = chain.invoke({"prompt": prompt_text}, **kwargs)
            return result

        except Exception as e:
            raise RuntimeError(f"OpenAI structured output error: {str(e)}")

    def _messages_to_text(self, messages: list[BaseMessage]) -> str:
        """
        Convert a list of messages to a text representation.

        This is used for structured output where we need a single
        text prompt for the template.

        Args:
            messages: List of messages to convert.

        Returns:
            A text representation of the messages.
        """
        text_parts = []
        for msg in messages:
            role = type(msg).__name__.replace("Message", "").lower()
            content = getattr(msg, "content", str(msg))
            text_parts.append(f"[{role}]: {content}")
        return "\n".join(text_parts)

    @property
    def name(self) -> str:
        """Name of the LLM provider."""
        return "OpenAI"

    @property
    def model(self) -> str:
        """Model name/version being used."""
        return self._model
