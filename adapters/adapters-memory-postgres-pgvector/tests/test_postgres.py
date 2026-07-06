# AgentForge — Tests PostgreSQL/pgvector

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentforge_core.types import Message
from agentforge_postgres import (
    PostgresSemanticMemory,
    PostgresEpisodicMemory,
    PostgresConnectionPool,
)


class TestPostgresConnectionPool:
    """Tests pour le pool de connexions PostgreSQL."""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """L'initialisation doit stocker la config."""
        pool = PostgresConnectionPool("test_dsn", min_size=1, max_size=5)
        assert pool._dsn == "test_dsn"
        assert pool._min_size == 1
        assert pool._max_size == 5

    @pytest.mark.asyncio
    async def test_get_connection_no_pool(self):
        """get_connection() sans pool doit en créer un."""
        pool = PostgresConnectionPool("test_dsn", min_size=1, max_size=1)
        with patch("agentforge_postgres.AsyncConnectionPool") as mock_pool_cls:
            mock_instance = MagicMock()
            mock_pool_cls.return_value = mock_instance
            mock_instance.getconn = AsyncMock(return_value="conn")
            conn = await pool.get_connection()
            assert conn == "conn"


class TestPostgresSemanticMemory:
    """Tests pour PostgresSemanticMemory (mocké)."""

    @pytest.fixture
    def mock_pool_mgr(self):
        """Fixture retournant un pool manager mocké."""
        mgr = MagicMock()
        mgr.get_connection = AsyncMock()
        mgr.put_connection = AsyncMock()
        return mgr

    @pytest.mark.asyncio
    async def test_upsert(self, mock_pool_mgr):
        """upsert() doit appeler le pool."""
        adapter = PostgresSemanticMemory(dsn="test_dsn", embedding_size=4)
        adapter._pool_mgr = mock_pool_mgr

        mock_conn = AsyncMock()
        mock_pool_mgr.get_connection.return_value = mock_conn

        await adapter.upsert({"id": "fact_1", "content": "Test content"})
        assert mock_conn.execute.called
        assert mock_conn.commit.called

    @pytest.mark.asyncio
    async def test_search(self, mock_pool_mgr):
        """search() doit retourner des résultats."""
        adapter = PostgresSemanticMemory(dsn="test_dsn", embedding_size=4)
        adapter._pool_mgr = mock_pool_mgr

        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        # Simuler cursor() comme gestionnaire de contexte asynchrone
        mock_cur = AsyncMock()
        mock_cur.fetchall = AsyncMock(return_value=[])
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_cur)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_conn.cursor = MagicMock(return_value=mock_cm)
        mock_pool_mgr.get_connection.return_value = mock_conn

        results = await adapter.search("test")
        assert results == []

    @pytest.mark.asyncio
    async def test_delete(self, mock_pool_mgr):
        """delete() doit exécuter une requête DELETE."""
        adapter = PostgresSemanticMemory(dsn="test_dsn", embedding_size=4)
        adapter._pool_mgr = mock_pool_mgr

        mock_conn = AsyncMock()
        mock_pool_mgr.get_connection.return_value = mock_conn

        await adapter.delete("fact_1")
        assert mock_conn.execute.called

    def test_embedding_size(self):
        """L'embedding doit avoir la taille configurée."""
        adapter = PostgresSemanticMemory(dsn="test_dsn", embedding_size=4)
        vector = adapter._simple_embed("test")
        assert len(vector) == 4

    def test_embedding_deterministic(self):
        """Le même texte doit produire le même embedding."""
        adapter = PostgresSemanticMemory(dsn="test_dsn", embedding_size=4)
        v1 = adapter._simple_embed("Bonjour le monde")
        v2 = adapter._simple_embed("Bonjour le monde")
        assert v1 == v2


class TestPostgresEpisodicMemory:
    """Tests pour PostgresEpisodicMemory (mocké)."""

    @pytest.fixture
    def mock_pool_mgr(self):
        """Fixture retournant un pool manager mocké."""
        mgr = MagicMock()
        mgr.get_connection = AsyncMock()
        mgr.put_connection = AsyncMock()
        return mgr

    @pytest.mark.asyncio
    async def test_append(self, mock_pool_mgr):
        """append() doit insérer un message."""
        adapter = PostgresEpisodicMemory(dsn="test_dsn")
        adapter._pool_mgr = mock_pool_mgr

        mock_conn = AsyncMock()
        mock_pool_mgr.get_connection.return_value = mock_conn

        msg = Message(role="user", content="Bonjour")
        await adapter.append(msg)
        assert mock_conn.execute.called
        assert mock_conn.commit.called

    @pytest.mark.asyncio
    async def test_get_history(self, mock_pool_mgr):
        """get_history() doit retourner une liste."""
        adapter = PostgresEpisodicMemory(dsn="test_dsn")
        adapter._pool_mgr = mock_pool_mgr

        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_cur = AsyncMock()
        mock_cur.fetchall = AsyncMock(return_value=[])
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_cur)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_conn.cursor = MagicMock(return_value=mock_cm)
        mock_pool_mgr.get_connection.return_value = mock_conn

        history = await adapter.get_history("session_1")
        assert history == []

    @pytest.mark.asyncio
    async def test_search_hybrid(self, mock_pool_mgr):
        """search_hybrid() doit retourner des résultats."""
        adapter = PostgresEpisodicMemory(dsn="test_dsn")
        adapter._pool_mgr = mock_pool_mgr

        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_cur = AsyncMock()
        mock_cur.fetchall = AsyncMock(return_value=[])
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_cur)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_conn.cursor = MagicMock(return_value=mock_cm)
        mock_pool_mgr.get_connection.return_value = mock_conn

        results = await adapter.search_hybrid("test")
        assert results == []
