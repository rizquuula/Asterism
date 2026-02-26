"""Agent lifecycle management service."""

import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from asterism.agent import Agent
from asterism.config import Config
from asterism.llm import LLMProviderRouter
from asterism.mcp.executor import MCPExecutor

from ..models import ChatCompletionRequest, ChatMessage
from .session_history_store import SessionHistoryStore

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing Agent lifecycle per request.

    Design: Stateless - creates fresh Agent for each request.
    No session persistence, no SQLite checkpointing for API mode.
    """

    def __init__(
        self,
        llm_router: LLMProviderRouter,
        mcp_executor: MCPExecutor,
        config: Config,
    ):
        """Initialize the agent service.

        Args:
            llm_router: LLM provider router for fallback support
            mcp_executor: MCP executor for tool calls
            config: Configuration instance
        """
        self.llm_router = llm_router
        self.mcp_executor = mcp_executor
        self.config = config
        self._history_store = self._build_history_store()

    def _build_history_store(self) -> SessionHistoryStore | None:
        """Create history store when enabled and supported by config."""
        if not self.config.data.api.use_server_side_history:
            return None

        db_path = self.config.data.api.db_path
        if not db_path:
            logger.warning(
                "[agent_service] Server-side history enabled but api.db_path is empty; skipping history store"
            )
            return None

        return SessionHistoryStore(db_path)

    async def run_completion(
        self,
        request: ChatCompletionRequest,
        request_id: str,
    ) -> dict[str, Any]:
        """Run a single completion (non-streaming).

        Args:
            request: The chat completion request
            request_id: Unique request identifier

        Returns:
            Dictionary containing the agent response and metadata
        """
        # Create fresh agent for this request
        agent = Agent(
            llm=self.llm_router,
            mcp_executor=self.mcp_executor,
            db_path=self.config.data.api.db_path,
            workspace_root=self.config.workspace_path,
        )

        try:
            # Merge with server-side history if enabled
            effective_messages = self._build_effective_messages(request.messages, request_id)

            # Convert OpenAI format messages to LangChain messages
            messages = self._convert_messages(effective_messages)

            # Set model if specified in request
            if request.model:
                # The router will handle model resolution
                pass

            # Run agent with full conversation context
            result = agent.invoke(
                session_id=request_id,
                messages=messages,
            )

            self._persist_assistant_response(request_id, effective_messages, result.get("message", ""))

            return result

        finally:
            agent.close()

    async def run_streaming(
        self,
        request: ChatCompletionRequest,
        request_id: str,
    ) -> Any:
        """Run streaming completion.

        Args:
            request: The chat completion request
            request_id: Unique request identifier

        Yields:
            Tuples of (token, metadata) from the agent's streaming response
        """
        # Create fresh agent for this request
        agent = Agent(
            llm=self.llm_router,
            mcp_executor=self.mcp_executor,
            db_path=self.config.data.api.db_path,
            workspace_root=self.config.workspace_path,
        )

        try:
            # Merge with server-side history if enabled
            effective_messages = self._build_effective_messages(request.messages, request_id)

            # Convert OpenAI format messages to LangChain messages
            messages = self._convert_messages(effective_messages)

            # Stream agent response with full conversation context
            async for token, metadata in agent.astream(
                session_id=request_id,
                messages=messages,
            ):
                if metadata is not None:
                    final_message = metadata.get("message", "") if isinstance(metadata, dict) else ""
                    self._persist_assistant_response(request_id, effective_messages, final_message)
                yield token, metadata

        finally:
            agent.close()

    def _convert_messages(self, messages: list) -> list:
        """Convert OpenAI format messages to LangChain messages.

        Args:
            messages: List of ChatMessage objects with role and content

        Returns:
            List of LangChain BaseMessage objects
        """
        converted = []
        for msg in messages:
            if msg.role == "system":
                converted.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                converted.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                converted.append(AIMessage(content=msg.content))
            elif msg.role == "tool":
                # Tool messages require tool_call_id to link to the assistant's tool call
                converted.append(
                    ToolMessage(
                        content=msg.content,
                        tool_call_id=msg.tool_call_id or "",
                        name=msg.name or "tool",
                    )
                )
        return converted

    def _build_effective_messages(self, incoming_messages: list, session_id: str) -> list:
        """Build effective conversation by merging restored history with incoming messages."""
        incoming_count = len(incoming_messages)

        if self._history_store is None:
            logger.info(
                "[agent_service] History mode disabled or unavailable: "
                f"incoming_messages_count={incoming_count}, restored_history_count=0, "
                f"effective_messages_count={incoming_count}"
            )
            return incoming_messages

        restored_messages = self._history_store.load_messages(session_id)
        overlap = self._compute_overlap(restored_messages, incoming_messages)
        effective_messages = restored_messages + incoming_messages[overlap:]

        logger.info(
            "[agent_service] Built effective history: "
            f"incoming_messages_count={incoming_count}, restored_history_count={len(restored_messages)}, "
            f"effective_messages_count={len(effective_messages)}, overlap_count={overlap}"
        )
        return effective_messages

    def _persist_assistant_response(self, session_id: str, effective_messages: list, assistant_message: str) -> None:
        """Persist updated session history including assistant response."""
        if self._history_store is None:
            return

        new_history = [*effective_messages]
        if assistant_message:
            new_history.append(
                ChatMessage(
                    role="assistant",
                    content=assistant_message,
                )
            )
        self._history_store.replace_messages(session_id, new_history)

    def _compute_overlap(self, restored_messages: list, incoming_messages: list) -> int:
        """Compute longest suffix/prefix overlap between restored and incoming message lists."""
        max_overlap = min(len(restored_messages), len(incoming_messages))
        for overlap in range(max_overlap, 0, -1):
            if self._messages_equal(restored_messages[-overlap:], incoming_messages[:overlap]):
                return overlap
        return 0

    def _messages_equal(self, left: list, right: list) -> bool:
        if len(left) != len(right):
            return False

        for lmsg, rmsg in zip(left, right, strict=False):
            if not self._message_key_equal(lmsg, rmsg):
                return False
        return True

    def _message_key_equal(self, left, right) -> bool:
        return (
            left.role,
            left.content,
            left.name,
            left.tool_call_id,
        ) == (
            right.role,
            right.content,
            right.name,
            right.tool_call_id,
        )

    def _extract_last_user_message(self, messages: list) -> str:
        """Extract the last user message from the conversation.

        Args:
            messages: List of chat messages

        Returns:
            The content of the last user message
        """
        for msg in reversed(messages):
            if msg.role == "user":
                return msg.content
        return ""

    def _format_conversation_history(self, messages: list) -> str:
        """Format full conversation history for context.

        Args:
            messages: List of chat messages

        Returns:
            Formatted conversation history string
        """
        lines = []
        for msg in messages:
            lines.append(f"[{msg.role}]: {msg.content}")
        return "\n".join(lines)
