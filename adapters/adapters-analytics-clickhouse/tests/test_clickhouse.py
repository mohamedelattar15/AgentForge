# AgentForge — Tests ClickHouse Analytics

import pytest
from unittest.mock import MagicMock, patch

from agentforge_clickhouse import ClickHouseAnalytics


class TestClickHouseAnalytics:
    """Tests pour ClickHouseAnalytics (mocké)."""

    @pytest.fixture
    def mock_client(self):
        """Fixture retournant un client ClickHouse mocké."""
        client = MagicMock()
        client.execute = MagicMock(return_value=[])
        return client

    @pytest.mark.asyncio
    async def test_ingest(self, mock_client):
        """ingest() doit exécuter une requête INSERT."""
        with patch("agentforge_clickhouse.CHClient", return_value=mock_client):
            adapter = ClickHouseAnalytics(host="localhost", port=9000)
            await adapter.ingest({
                "run_id": "run_123",
                "latency_ms": 1500,
                "token_count": 500,
                "status": "completed",
            })

        assert mock_client.execute.called

    @pytest.mark.asyncio
    async def test_query(self, mock_client):
        """query() doit retourner des résultats."""
        mock_client.execute = MagicMock(return_value=[(10, 100.0, 500.0, 0.85, 25)])

        with patch("agentforge_clickhouse.CHClient", return_value=mock_client):
            adapter = ClickHouseAnalytics(host="localhost", port=9000)
            results = await adapter.query({"period": "24h"})

        assert len(results) == 1
        assert results[0]["total_runs"] == 10
        assert results[0]["avg_latency_ms"] == 100.0
        assert results[0]["avg_eval_score"] == 0.85

    @pytest.mark.asyncio
    async def test_query_with_filters(self, mock_client):
        """query() avec filtres doit les passer à la requête."""
        mock_client.execute = MagicMock(return_value=[(5, 200.0, 300.0, 0.9, 10)])

        with patch("agentforge_clickhouse.CHClient", return_value=mock_client):
            adapter = ClickHouseAnalytics(host="localhost", port=9000)
            results = await adapter.query({
                "period": "7d",
                "status": "completed",
                "model": "gpt-4o",
            })

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_query_empty(self, mock_client):
        """query() sans données doit retourner []."""
        mock_client.execute = MagicMock(return_value=[])

        with patch("agentforge_clickhouse.CHClient", return_value=mock_client):
            adapter = ClickHouseAnalytics(host="localhost", port=9000)
            results = await adapter.query({})

        assert results == []

    def test_init_database(self, mock_client):
        """_init_database() doit créer la base et la table."""
        with patch("agentforge_clickhouse.CHClient", return_value=mock_client):
            adapter = ClickHouseAnalytics(host="localhost", port=9000, database="test_db", table="test_metrics")
            client = adapter._get_client()

        # Vérifier que CREATE DATABASE et CREATE TABLE ont été appelés
        create_calls = [c for c in mock_client.execute.call_args_list if "CREATE" in str(c)]
        assert len(create_calls) >= 2
