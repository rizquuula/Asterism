"""Tests for server-side history reconstruction in AgentService."""

import asyncio
from types import SimpleNamespace

from asterism.api.models import ChatCompletionRequest, ChatMessage
from asterism.api.services.agent_service import AgentService
from asterism.api.services.session_history_store import SessionHistoryStore


class _FakeAgent:
    calls: list[dict] = []

    def __init__(self, llm, mcp_executor, db_path=None, workspace_root="."):
        self.llm = llm
        self.mcp_executor = mcp_executor
        self.db_path = db_path
        self.workspace_root = workspace_root

    def invoke(self, session_id, messages):
        self.__class__.calls.append(
            {
                "session_id": session_id,
                "message_count": len(messages),
            }
        )
        return {
            "message": "assistant reply",
            "execution_trace": [],
            "plan_used": None,
            "session_id": session_id,
            "total_usage": {},
        }

    def close(self):
        return None


def _build_config(db_path: str, use_server_side_history: bool):
    return SimpleNamespace(
        workspace_path=".",
        data=SimpleNamespace(
            api=SimpleNamespace(
                db_path=db_path,
                use_server_side_history=use_server_side_history,
            )
        ),
    )


def test_run_completion_reconstructs_history_when_enabled(monkeypatch, tmp_path):
    """Second single-message turn should include restored prior turns when enabled."""
    monkeypatch.setattr("asterism.api.services.agent_service.Agent", _FakeAgent)
    _FakeAgent.calls.clear()

    db_path = str(tmp_path / "history.db")
    service = AgentService(
        llm_router=object(),
        mcp_executor=object(),
        config=_build_config(db_path, use_server_side_history=True),
    )

    req1 = ChatCompletionRequest(
        model="llmgateway/psn/Nusa-Max",
        messages=[ChatMessage(role="user", content="Hello")],
        session_id="session-1",
    )
    asyncio.run(service.run_completion(req1, "session-1"))

    req2 = ChatCompletionRequest(
        model="llmgateway/psn/Nusa-Max",
        messages=[ChatMessage(role="user", content="Continue")],
        session_id="session-1",
    )
    asyncio.run(service.run_completion(req2, "session-1"))

    assert _FakeAgent.calls[0]["message_count"] == 1
    assert _FakeAgent.calls[1]["message_count"] == 3

    history_store = SessionHistoryStore(db_path)
    persisted = history_store.load_messages("session-1")
    assert len(persisted) == 4


def test_run_completion_stays_stateless_when_disabled(monkeypatch, tmp_path):
    """Single-message turns should remain single-message in stateless mode."""
    monkeypatch.setattr("asterism.api.services.agent_service.Agent", _FakeAgent)
    _FakeAgent.calls.clear()

    service = AgentService(
        llm_router=object(),
        mcp_executor=object(),
        config=_build_config(str(tmp_path / "history.db"), use_server_side_history=False),
    )

    req1 = ChatCompletionRequest(
        model="llmgateway/psn/Nusa-Max",
        messages=[ChatMessage(role="user", content="Hello")],
        session_id="session-1",
    )
    asyncio.run(service.run_completion(req1, "session-1"))

    req2 = ChatCompletionRequest(
        model="llmgateway/psn/Nusa-Max",
        messages=[ChatMessage(role="user", content="Continue")],
        session_id="session-1",
    )
    asyncio.run(service.run_completion(req2, "session-1"))

    assert _FakeAgent.calls[0]["message_count"] == 1
    assert _FakeAgent.calls[1]["message_count"] == 1
