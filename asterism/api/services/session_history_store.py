"""SQLite-backed chat history storage for API sessions."""

import sqlite3
from pathlib import Path

from ..models import ChatMessage


class SessionHistoryStore:
    """Persist and load chat message history by session ID."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _ensure_schema(self) -> None:
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    name TEXT,
                    tool_call_id TEXT,
                    position INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_session_messages_session_position
                ON session_messages (session_id, position)
                """
            )

    def load_messages(self, session_id: str) -> list[ChatMessage]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content, name, tool_call_id
                FROM session_messages
                WHERE session_id = ?
                ORDER BY position ASC, id ASC
                """,
                (session_id,),
            ).fetchall()

        return [
            ChatMessage(role=row[0], content=row[1], name=row[2], tool_call_id=row[3])
            for row in rows
        ]

    def replace_messages(self, session_id: str, messages: list[ChatMessage]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM session_messages WHERE session_id = ?", (session_id,))
            conn.executemany(
                """
                INSERT INTO session_messages (session_id, role, content, name, tool_call_id, position)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (session_id, msg.role, msg.content, msg.name, msg.tool_call_id, idx)
                    for idx, msg in enumerate(messages)
                ],
            )
