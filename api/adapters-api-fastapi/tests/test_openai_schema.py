# AgentForge — Tests de l'adaptateur de schéma OpenAI

import pytest

from agentforge_api.openai_schema_adapter import OpenAISchemaAdapter
from agentforge_core.types import Message, ToolCall


class TestOpenAISchemaAdapter:
    """Tests pour la conversion bidirectionnelle OpenAI ↔ interne."""

    def test_to_run_context_basic(self):
        """Une requête OpenAI basique doit produire un RunContext valide."""
        request = {
            "messages": [
                {"role": "system", "content": "Assistant utile."},
                {"role": "user", "content": "Bonjour le monde"},
            ],
            "user": "session_1",
            "max_tokens": 100,
        }
        context = OpenAISchemaAdapter.to_run_context(request)
        assert context.user_query == "Bonjour le monde"
        assert context.session_id == "session_1"
        assert len(context.messages) == 2
        assert context.token_budget == 300  # 100 * 3

    def test_to_run_context_no_user(self):
        """Sans user ID, session_id doit être None."""
        request = {
            "messages": [{"role": "user", "content": "Test"}],
        }
        context = OpenAISchemaAdapter.to_run_context(request)
        assert context.session_id is None

    def test_to_openai_response_basic(self):
        """Un Message interne doit être converti en réponse OpenAI."""
        msg = Message(role="assistant", content="Ceci est une réponse.")
        response = OpenAISchemaAdapter.to_openai_response(msg)
        assert response["object"] == "chat.completion"
        assert response["choices"][0]["message"]["content"] == "Ceci est une réponse."
        assert response["choices"][0]["finish_reason"] == "stop"

    def test_to_openai_response_with_tools(self):
        """Un Message avec tool_calls doit inclure les appels d'outils."""
        msg = Message(
            role="assistant",
            content="",
            tool_calls=[
                ToolCall(id="call_1", name="get_weather", arguments='{"city": "Paris"}'),
            ],
        )
        response = OpenAISchemaAdapter.to_openai_response(msg)
        assert "tool_calls" in response["choices"][0]["message"]
        assert response["choices"][0]["message"]["tool_calls"][0]["function"]["name"] == "get_weather"

    def test_to_openai_stream(self):
        """Le streaming doit produire des chunks SSE."""
        deltas = ["Hello", " ", "World"]
        chunks = list(OpenAISchemaAdapter.to_openai_stream(deltas))
        assert len(chunks) == 4  # 3 tokens + 1 finish
        assert chunks[0]["choices"][0]["delta"]["content"] == "Hello"
        assert chunks[-1]["choices"][0]["finish_reason"] == "stop"

    def test_to_openai_response_has_usage(self):
        """La réponse doit inclure les métriques d'usage."""
        msg = Message(role="assistant", content="Test")
        response = OpenAISchemaAdapter.to_openai_response(msg)
        assert "usage" in response
        assert response["usage"]["total_tokens"] == 0
