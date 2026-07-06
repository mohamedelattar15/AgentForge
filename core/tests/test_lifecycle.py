# AgentForge Core — Tests du lifecycle

import pytest

from agentforge_core.lifecycle.run_context import RunContext, RunStatus
from agentforge_core.types import Message, ToolResult


class TestRunContext:
    """Tests pour le contexte d'exécution (RunContext)."""

    def test_default_initialization(self):
        """Un RunContext doit s'initialiser avec des valeurs par défaut."""
        ctx = RunContext(user_query="Bonjour")
        assert ctx.run_id is not None
        assert ctx.user_query == "Bonjour"
        assert ctx.status == RunStatus.PENDING
        assert ctx.messages == []
        assert ctx.tool_results == []
        assert ctx.max_iterations == 20
        assert ctx.token_budget == 100_000
        assert ctx.timeout_seconds == 120
        assert "started_at" in ctx.metadata

    def test_add_message(self):
        """Ajouter un message doit mettre à jour le compteur de tokens."""
        ctx = RunContext()
        msg = Message(role="user", content="Bonjour le monde")
        ctx.add_message(msg)
        assert len(ctx.messages) == 1
        assert ctx.metadata["token_count"] == 3  # "Bonjour" + "le" + "monde" = 3 mots

    def test_add_tool_result(self):
        """Ajouter un résultat d'outil doit l'ajouter à la liste."""
        ctx = RunContext()
        result = ToolResult(tool_call_id="call_1", content="Résultat", success=True)
        ctx.add_tool_result(result)
        assert len(ctx.tool_results) == 1
        assert ctx.tool_results[0].content == "Résultat"

    def test_is_exhausted_max_iterations(self):
        """Le guardrail max_iterations doit fonctionner."""
        ctx = RunContext(max_iterations=5)
        ctx.metadata["iteration_count"] = 5
        assert ctx.is_exhausted() is True

    def test_is_exhausted_token_budget(self):
        """Le guardrail token_budget doit fonctionner."""
        ctx = RunContext(token_budget=100)
        ctx.metadata["token_count"] = 150
        assert ctx.is_exhausted() is True

    def test_is_not_exhausted(self):
        """Aucun guardrail atteint."""
        ctx = RunContext(max_iterations=20, token_budget=100_000)
        assert ctx.is_exhausted() is False

    def test_to_dict(self):
        """La sérialisation en dict doit contenir les champs clés."""
        ctx = RunContext(user_query="Test", session_id="session_1")
        data = ctx.to_dict()
        assert data["user_query"] == "Test"
        assert data["session_id"] == "session_1"
        assert data["status"] == "pending"
        assert "run_id" in data
