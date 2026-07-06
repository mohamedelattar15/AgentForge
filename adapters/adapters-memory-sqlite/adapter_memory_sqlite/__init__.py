# AgentForge — Adapter Memory SQLite
# Implémentation embarquée de SemanticMemoryPort et EpisodicMemoryPort avec SQLite.

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from ...agentforge_core.ports.episodic_memory_port import EpisodicMemoryPort
from ...agentforge_core.ports.semantic_memory_port import SemanticMemoryPort
from ...agentforge_core.types import Message


class SQLiteSemanticMemory(SemanticMemoryPort):
    """Mémoire sémantique stockée dans SQLite.

    Stocke les faits avec embeddings vectoriels (via sqlite-vec si disponible,
    sinon recherche textuelle simple).
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        """Initialise la base de données SQLite.

        Args:
            db_path: Chemin vers le fichier DB (":memory:" pour temporaire).
        """
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Retourne une connexion SQLite (crée si nécessaire)."""
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        """Crée les tables si elles n'existent pas."""
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS semantic_facts (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    async def search(
        self, query: str, top_k: int = 5, filters: dict | None = None
    ) -> list[dict]:
        """Recherche des faits par similarité textuelle.

        Args:
            query: Texte de recherche.
            top_k: Nombre maximum de résultats.
            filters: Filtres metadata (non implémenté en SQLite simple).

        Returns:
            list[dict]: Faits pertinents.
        """
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT id, content, metadata, created_at
            FROM semantic_facts
            WHERE content LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (f"%{query}%", top_k),
        )
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "content": row["content"],
                "metadata": json.loads(row["metadata"]),
                "created_at": row["created_at"],
            })
        return results

    async def upsert(self, fact: dict) -> None:
        """Ajoute ou met à jour un fait.

        Args:
            fact: Dictionnaire avec clés 'id', 'content', et optionnellement 'metadata'.
        """
        conn = self._get_conn()
        conn.execute(
            """
            INSERT INTO semantic_facts (id, content, metadata, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                content = excluded.content,
                metadata = excluded.metadata,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                fact["id"],
                fact["content"],
                json.dumps(fact.get("metadata", {})),
            ),
        )
        conn.commit()

    async def delete(self, fact_id: str) -> None:
        """Supprime un fait.

        Args:
            fact_id: Identifiant du fait à supprimer.
        """
        conn = self._get_conn()
        conn.execute("DELETE FROM semantic_facts WHERE id = ?", (fact_id,))
        conn.commit()


class SQLiteEpisodicMemory(EpisodicMemoryPort):
    """Mémoire épisodique stockée dans SQLite.

    Stocke l'historique des conversations par session.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        """Initialise la base de données SQLite.

        Args:
            db_path: Chemin vers le fichier DB (":memory:" pour temporaire).
        """
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Retourne une connexion SQLite."""
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        """Crée les tables si elles n'existent pas."""
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS episodic_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_calls TEXT DEFAULT '[]',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_episodic_session
            ON episodic_messages(session_id)
        """)
        conn.commit()

    async def search_hybrid(
        self,
        query: str,
        since: datetime | None = None,
        top_k: int = 10,
    ) -> list[dict]:
        """Recherche dans l'historique par contenu textuel.

        Args:
            query: Texte de recherche.
            since: Date limite (optionnelle).
            top_k: Nombre maximum de résultats.

        Returns:
            list[dict]: Messages pertinents.
        """
        conn = self._get_conn()
        params: list[Any] = [f"%{query}%", top_k]
        sql = """
            SELECT id, session_id, role, content, tool_calls, timestamp
            FROM episodic_messages
            WHERE content LIKE ?
        """
        if since:
            sql += " AND timestamp >= ?"
            params.insert(1, since.isoformat())

        sql += " ORDER BY timestamp DESC LIMIT ?"
        params[-1] = top_k

        cursor = conn.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row["id"],
                "session_id": row["session_id"],
                "role": row["role"],
                "content": row["content"],
                "tool_calls": json.loads(row["tool_calls"]),
                "timestamp": row["timestamp"],
            })
        return results

    async def append(self, event: Message) -> None:
        """Ajoute un message à l'historique.

        Args:
            event: Message à ajouter.
        """
        conn = self._get_conn()
        from uuid import uuid4

        conn.execute(
            """
            INSERT INTO episodic_messages (id, session_id, role, content, tool_calls)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                uuid4().hex,
                event.tool_calls[0].id if event.tool_calls else "default",
                event.role,
                event.content,
                json.dumps([vars(tc) for tc in event.tool_calls]),
            ),
        )
        conn.commit()

    async def get_history(
        self, session_id: str, limit: int = 50
    ) -> list[Message]:
        """Récupère l'historique d'une session.

        Args:
            session_id: Identifiant de la session.
            limit: Nombre maximum de messages.

        Returns:
            list[Message]: Messages de l'historique.
        """
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT role, content, tool_calls, timestamp
            FROM episodic_messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
            """,
            (session_id, limit),
        )
        messages = []
        for row in cursor.fetchall():
            messages.append(Message(
                role=row["role"],
                content=row["content"],
                tool_calls=json.loads(row["tool_calls"]),
            ))
        return messages
