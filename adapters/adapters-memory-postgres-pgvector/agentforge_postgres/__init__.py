# AgentForge — Adapter mémoire PostgreSQL/pgvector
# Implémente SemanticMemoryPort et EpisodicMemoryPort via PostgreSQL.

import json
from datetime import datetime
from typing import Any

from agentforge_core.ports.episodic_memory_port import EpisodicMemoryPort
from agentforge_core.ports.semantic_memory_port import SemanticMemoryPort
from agentforge_core.types import Message

try:
    import psycopg
    from psycopg import AsyncConnection
    from psycopg_pool import AsyncConnectionPool
    from psycopg.rows import dict_row
except ImportError:
    psycopg = None  # type: ignore
    AsyncConnection = None
    AsyncConnectionPool = None
    dict_row = None


class PostgresConnectionPool:
    """Gestionnaire de pool de connexions PostgreSQL.

    Utilise psycopg.AsyncConnectionPool pour gérer les connexions.
    """

    def __init__(
        self,
        dsn: str = "postgresql://user:pass@localhost:5432/agentforge",
        min_size: int = 2,
        max_size: int = 10,
    ) -> None:
        """Initialise la configuration du pool.

        Args:
            dsn: Chaîne de connexion PostgreSQL.
            min_size: Taille minimale du pool.
            max_size: Taille maximale du pool.
        """
        if psycopg is None:
            raise ImportError("psycopg est requis. Installez : pip install psycopg[binary]")

        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: AsyncConnectionPool | None = None

    async def get_connection(self) -> AsyncConnection:
        """Obtient une connexion du pool.

        Returns:
            AsyncConnection: Connexion PostgreSQL asynchrone.
        """
        if self._pool is None:
            self._pool = AsyncConnectionPool(
                self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
                open=True,
            )
        return await self._pool.getconn()

    async def put_connection(self, conn: AsyncConnection) -> None:
        """Remet une connexion dans le pool.

        Args:
            conn: Connexion à libérer.
        """
        if self._pool:
            await self._pool.putconn(conn)

    async def close(self) -> None:
        """Ferme le pool de connexions."""
        if self._pool:
            await self._pool.close()
            self._pool = None


class PostgresSemanticMemory(SemanticMemoryPort):
    """Mémoire sémantique PostgreSQL avec pgvector.

    Stocke les faits avec des vecteurs d'embedding pour la recherche
    par similarité. Utilise l'extension pgvector.
    """

    def __init__(
        self,
        dsn: str = "postgresql://user:pass@localhost:5432/agentforge",
        embedding_size: int = 1536,
        pool_min: int = 2,
        pool_max: int = 10,
    ) -> None:
        """Initialise la mémoire sémantique PostgreSQL.

        Args:
            dsn: Chaîne de connexion.
            embedding_size: Taille des vecteurs d'embedding.
            pool_min: Taille min du pool.
            pool_max: Taille max du pool.
        """
        self._embedding_size = embedding_size
        self._pool_mgr = PostgresConnectionPool(dsn, pool_min, pool_max)

    async def _init_schema(self, conn: AsyncConnection) -> None:
        """Crée les tables et l'extension si nécessaire."""
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS semantic_facts (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                embedding vector({self._embedding_size}),
                metadata JSONB DEFAULT '{{}}',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_semantic_embedding
            ON semantic_facts
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
        await conn.commit()

    def _simple_embed(self, text: str) -> list[float]:
        """Génère un embedding simple (fallback développement).

        NOTE: Remplacez par un vrai modèle d'embedding en production.
        """
        import hashlib

        vector = [0.0] * self._embedding_size
        words = text.split()
        for i, word in enumerate(words[:self._embedding_size]):
            h = hashlib.md5(word.encode()).hexdigest()
            vector[i] = (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1
        return vector

    async def search(
        self, query: str, top_k: int = 5, filters: dict | None = None
    ) -> list[dict]:
        """Recherche des faits par similarité cosinus.

        Args:
            query: Texte de recherche.
            top_k: Nombre maximum de résultats.
            filters: Filtres metadata (clé/valeur).

        Returns:
            list[dict]: Faits pertinents.
        """
        conn = await self._pool_mgr.get_connection()
        try:
            await self._init_schema(conn)
            query_vector = self._simple_embed(query)

            sql = """
                SELECT id, content, metadata, created_at,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM semantic_facts
            """
            params: list[Any] = [query_vector]

            if filters:
                conditions = []
                for k, v in filters.items():
                    conditions.append(f"metadata->>'{k}' = %s")
                    params.append(str(v))
                sql += " WHERE " + " AND ".join(conditions)

            sql += " ORDER BY similarity DESC LIMIT %s"
            params.append(top_k)

            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(sql, params)
                rows = await cur.fetchall()

            return [
                {
                    "id": row["id"],
                    "content": row["content"],
                    "metadata": row["metadata"],
                    "score": float(row["similarity"]),
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                }
                for row in rows
            ]
        finally:
            await self._pool_mgr.put_connection(conn)

    async def upsert(self, fact: dict) -> None:
        """Ajoute ou met à jour un fait.

        Args:
            fact: Dictionnaire avec 'id', 'content', optionnellement 'metadata'.
        """
        conn = await self._pool_mgr.get_connection()
        try:
            await self._init_schema(conn)
            fact_id = fact.get("id", "")
            content = fact.get("content", "")
            metadata = json.dumps(fact.get("metadata", {}))
            vector = self._simple_embed(content)

            await conn.execute("""
                INSERT INTO semantic_facts (id, content, embedding, metadata, updated_at)
                VALUES (%s, %s, %s::vector, %s::jsonb, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
            """, (fact_id, content, vector, metadata))
            await conn.commit()
        finally:
            await self._pool_mgr.put_connection(conn)

    async def delete(self, fact_id: str) -> None:
        """Supprime un fait.

        Args:
            fact_id: Identifiant du fait.
        """
        conn = await self._pool_mgr.get_connection()
        try:
            await self._init_schema(conn)
            await conn.execute("DELETE FROM semantic_facts WHERE id = %s", (fact_id,))
            await conn.commit()
        finally:
            await self._pool_mgr.put_connection(conn)


class PostgresEpisodicMemory(EpisodicMemoryPort):
    """Mémoire épisodique PostgreSQL.

    Stocke l'historique des conversations dans une table JSONB.
    """

    def __init__(
        self,
        dsn: str = "postgresql://user:pass@localhost:5432/agentforge",
        pool_min: int = 2,
        pool_max: int = 10,
    ) -> None:
        """Initialise la mémoire épisodique PostgreSQL.

        Args:
            dsn: Chaîne de connexion.
            pool_min: Taille min du pool.
            pool_max: Taille max du pool.
        """
        self._pool_mgr = PostgresConnectionPool(dsn, pool_min, pool_max)

    async def _init_schema(self, conn: AsyncConnection) -> None:
        """Crée la table si nécessaire."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS episodic_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_calls JSONB DEFAULT '[]',
                timestamp TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_episodic_session
            ON episodic_messages(session_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_episodic_timestamp
            ON episodic_messages(timestamp DESC)
        """)
        await conn.commit()

    async def search_hybrid(
        self,
        query: str,
        since: datetime | None = None,
        top_k: int = 10,
    ) -> list[dict]:
        """Recherche textuelle dans l'historique.

        Args:
            query: Texte de recherche.
            since: Date limite.
            top_k: Nombre maximum de résultats.

        Returns:
            list[dict]: Messages pertinents.
        """
        conn = await self._pool_mgr.get_connection()
        try:
            await self._init_schema(conn)

            sql = """
                SELECT id, session_id, role, content, tool_calls, timestamp
                FROM episodic_messages
                WHERE content ILIKE %s
            """
            params: list[Any] = [f"%{query}%"]

            if since:
                sql += " AND timestamp >= %s"
                params.append(since)

            sql += " ORDER BY timestamp DESC LIMIT %s"
            params.append(top_k)

            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(sql, params)
                rows = await cur.fetchall()

            return [
                {
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "tool_calls": row["tool_calls"],
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                }
                for row in rows
            ]
        finally:
            await self._pool_mgr.put_connection(conn)

    async def append(self, event: Message) -> None:
        """Ajoute un message à l'historique.

        Args:
            event: Message à ajouter.
        """
        from uuid import uuid4

        conn = await self._pool_mgr.get_connection()
        try:
            await self._init_schema(conn)
            session_id = event.tool_calls[0].id if event.tool_calls else "default"

            await conn.execute("""
                INSERT INTO episodic_messages (id, session_id, role, content, tool_calls)
                VALUES (%s, %s, %s, %s, %s::jsonb)
            """, (
                uuid4().hex,
                session_id,
                event.role,
                event.content,
                json.dumps([vars(tc) for tc in event.tool_calls]),
            ))
            await conn.commit()
        finally:
            await self._pool_mgr.put_connection(conn)

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
        conn = await self._pool_mgr.get_connection()
        try:
            await self._init_schema(conn)

            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute("""
                    SELECT role, content, tool_calls
                    FROM episodic_messages
                    WHERE session_id = %s
                    ORDER BY timestamp ASC
                    LIMIT %s
                """, (session_id, limit))
                rows = await cur.fetchall()

            return [
                Message(
                    role=row["role"],
                    content=row["content"],
                    tool_calls=[],
                )
                for row in rows
            ]
        finally:
            await self._pool_mgr.put_connection(conn)
