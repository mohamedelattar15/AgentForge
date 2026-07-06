# AgentForge — Tests LangGraph

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentforge_core.lifecycle.run_context import RunContext
from agentforge_core.types import Message, ToolResult
from agentforge_langgraph import LangGraphOrchestrator


class TestLangGraphOrchestrator:
    """Tests pour LangGraphOrchestrator (mocké)."""

    @pytest.fixture
    def mock_graph(self):
        """Fixture retournant un graphe mocké."""
        graph = MagicMock()
        graph.ainvoke = AsyncMock(return_value={
            "step_results": ["Réponse finale"],
            "final_response": "Réponse finale",
            "steps": ["répondre"],
            "current_step": 1,
            "retry_count": 0,
        })
        return graph

    @pytest.mark.asyncio
    async def test_run_returns_message(self, mock_graph):
        """run() doit retourner un Message."""
        adapter = LangGraphOrchestrator()
        adapter._graph = mock_graph

        context = RunContext(user_query="Bonjour")
        result = await adapter.run(context)

        assert isinstance(result, Message)
        assert result.content == "Réponse finale"

    @pytest.mark.asyncio
    async def test_run_empty_result(self, mock_graph):
        """run() avec résultat vide doit retourner un message par défaut."""
        mock_graph.ainvoke = AsyncMock(return_value={"step_results": [], "steps": []})
        adapter = LangGraphOrchestrator()
        adapter._graph = mock_graph

        context = RunContext(user_query="Test")
        result = await adapter.run(context)
        assert isinstance(result, Message)

    @pytest.mark.asyncio
    async def test_should_stop(self):
        """should_stop() avec retry_count >= max_retries doit retourner True."""
        adapter = LangGraphOrchestrator(max_retries=3)
        assert await adapter.should_stop({"retry_count": 3}) is True
        assert await adapter.should_stop({"retry_count": 2}) is False

    def test_route_after_reflector(self):
        """_route_after_reflector() doit router correctement."""
        adapter = LangGraphOrchestrator()
        assert adapter._route_after_reflector({"current_step": 0, "steps": ["a", "b"]}) == "executor"
        assert adapter._route_after_reflector({"current_step": 2, "steps": ["a", "b"]}) == "verifier"
