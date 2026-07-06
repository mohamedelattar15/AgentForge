# AgentForge — Tests Qdrant

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentforge_qdrant import QdrantSemanticMemory


class TestQdrantSemanticMemory:
    """Tests pour QdrantSemanticMemory (mocké)."""

    @pytest.fixture
    def mock_client(self):
        """Fixture retournant un client Qdrant mocké."""
        client = MagicMock()
        client.get_collections = AsyncMock()
        client.create_collection = AsyncMock()
        client.search = AsyncMock()
        client.upsert = AsyncMock()
        client.delete = AsyncMock()

        # Mock get_collections return
        mock_response = MagicMock()
        mock_response.collections = []
        client.get_collections.return_value = mock_response

        return client

    @pytest.fixture
    def adapter(self, mock_client):
        """Fixture retournant un adapter Qdrant mocké."""
        with patch("agentforge_qdrant.AsyncQdrantClient", return_value=mock_client):
            yield QdrantSemanticMemory(
                host="localhost",
                port=6333,
                collection="test_collection",
                embedding_size=4,
            )

    @pytest.mark.asyncio
    async def test_upsert_and_search(self, adapter, mock_client):
        """upsert() puis search() doit retourner des résultats."""
        # Mock search results
        mock_hit = MagicMock()
        mock_hit.id = "fact_1"
        mock_hit.payload = {
            "content": "L'utilisateur aime Python",
            "metadata": "{}",
        }
        mock_hit.score = 0.95
        mock_client.search.return_value = [mock_hit]

        await adapter.upsert({"id": "fact_1", "content": "L'utilisateur aime Python"})
        results = await adapter.search("Python")

        assert len(results) >= 1
        assert results[0]["id"] == "fact_1"
        assert results[0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_delete(self, adapter, mock_client):
        """delete() doit appeler le client Qdrant."""
        await adapter.delete("fact_1")
        mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_filters(self, adapter, mock_client):
        """search() avec filtres doit les passer à Qdrant."""
        mock_client.search.return_value = []
        results = await adapter.search("test", filters={"source": "web"})
        assert results == []

    @pytest.mark.asyncio
    async def test_empty_search(self, adapter, mock_client):
        """search() sans résultat doit retourner []."""
        mock_client.search.return_value = []
        results = await adapter.search("rien")
        assert results == []

    def test_embedding_size(self, adapter):
        """L'embedding doit avoir la taille configurée."""
        vector = adapter._simple_embed("test")
        assert len(vector) == 4

    def test_embedding_deterministic(self, adapter):
        """Le même texte doit produire le même embedding."""
        v1 = adapter._simple_embed("Bonjour le monde")
        v2 = adapter._simple_embed("Bonjour le monde")
        assert v1 == v2
