# AgentForge — Tests Temporal

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentforge_core.lifecycle.run_context import RunContext
from agentforge_core.types import Message
from agentforge_temporal import TemporalOrchestrator


class TestTemporalOrchestrator:
    """Tests pour TemporalOrchestrator (mocké)."""

    @pytest.fixture
    def mock_client(self):
        """Fixture retournant un client Temporal mocké."""
        client = MagicMock()
        mock_handle = MagicMock()
        mock_handle.result = AsyncMock(return_value={"response": "Résultat Temporal"})
        client.execute_workflow = AsyncMock(return_value=mock_handle)
        return client

    @pytest.mark.asyncio
    async def test_run_returns_message(self, mock_client):
        """run() doit retourner un Message."""
        with patch("agentforge_temporal.TemporalClient.connect", new=AsyncMock(return_value=mock_client)):
            adapter = TemporalOrchestrator(host="localhost:7233")
            context = RunContext(user_query="Test Temporal")
            result = await adapter.run(context)

        assert isinstance(result, Message)
        assert result.content == "Résultat Temporal"

    @pytest.mark.asyncio
    async def test_should_stop(self):
        """should_stop() doit retourner False (Temporal gère lui-même)."""
        adapter = TemporalOrchestrator()
        assert await adapter.should_stop({}) is False

    def test_initialization(self):
        """L'initialisation doit stocker la config."""
        adapter = TemporalOrchestrator(
            host="temporal:7233",
            namespace="agentforge",
            task_queue="agent-tasks",
            workflow_timeout=600,
        )
        assert adapter._host == "temporal:7233"
        assert adapter._namespace == "agentforge"
        assert adapter._task_queue == "agent-tasks"
        assert adapter._workflow_timeout == 600
