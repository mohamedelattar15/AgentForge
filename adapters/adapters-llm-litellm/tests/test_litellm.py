# AgentForge — Adapter LLM LiteLLM (tests)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentforge_core.types import Message, ToolCall
from agentforge_litellm import LiteLLMAdapter


class TestLiteLLMAdapter:
    """Tests pour l'adapter LiteLLM (avec mock)."""

    @pytest.fixture
    def adapter(self):
        """Fixture retournant un adapter LiteLLM avec des valeurs de test."""
        return LiteLLMAdapter(
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=100,
        )

    @pytest.mark.asyncio
    async def test_complete_returns_message(self, adapter):
        """complete() doit retourner un Message."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Bonjour !",
                    tool_calls=None,
                )
            )
        ]

        with patch.object(adapter, "_build_completion_kwargs", return_value={}):
            with patch("litellm.acompletion", new=AsyncMock(return_value=mock_response)):
                messages = [Message(role="user", content="Dis bonjour")]
                response = await adapter.complete(messages)

        assert isinstance(response, Message)
        assert response.role == "assistant"
        assert response.content == "Bonjour !"

    @pytest.mark.asyncio
    async def test_complete_with_tools(self, adapter):
        """complete() doit accepter des outils."""
        mock_tc = MagicMock(spec=["id", "function"])
        mock_tc.id = "call_1"
        mock_tc.function.name = "get_time"
        mock_tc.function.arguments = "{}"

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=None,
                    tool_calls=[mock_tc],
                )
            )
        ]

        with patch.object(adapter, "_build_completion_kwargs", return_value={}):
            with patch("litellm.acompletion", new=AsyncMock(return_value=mock_response)):
                messages = [Message(role="user", content="Quelle heure ?")]
                tools = [{"type": "function", "function": {"name": "get_time"}}]
                response = await adapter.complete(messages, tools=tools)

        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "get_time"
        assert response.tool_calls[0].id == "call_1"

    @pytest.mark.asyncio
    async def test_stream_yields_deltas(self, adapter):
        """stream() doit yield des tokens."""
        chunks = []
        for token in ["Bon", "jour", " !"]:
            chunk = MagicMock()
            chunk.choices = [MagicMock(delta=MagicMock(content=token))]
            chunks.append(chunk)

        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = chunks  # type: ignore

        with patch.object(adapter, "_build_completion_kwargs", return_value={}):
            with patch("litellm.acompletion", new=AsyncMock(return_value=mock_stream)):
                messages = [Message(role="user", content="Dis bonjour")]
                deltas = []
                async for delta in adapter.stream(messages):
                    deltas.append(delta)

        assert len(deltas) == 3
        assert "".join(deltas) == "Bonjour !"

    def test_initialization_without_litellm(self):
        """L'initialisation doit fonctionner avec les valeurs par défaut."""
        adapter = LiteLLMAdapter(model="test-model")
        assert adapter._model == "test-model"
        assert adapter._temperature == 0.7

    @pytest.mark.asyncio
    async def test_complete_raises_on_error(self, adapter):
        """Une erreur API doit être convertie en RuntimeError."""
        with patch.object(adapter, "_build_completion_kwargs", return_value={}):
            with patch("litellm.acompletion", side_effect=Exception("API Error")):
                messages = [Message(role="user", content="Test")]
                with pytest.raises(RuntimeError, match="API Error"):
                    await adapter.complete(messages)

    def test_build_kwargs_includes_all_params(self, adapter):
        """Les kwargs doivent inclure tous les paramètres configurés."""
        messages = [Message(role="user", content="Test")]
        kwargs = adapter._build_completion_kwargs(messages)
        assert kwargs["model"] == "gpt-4o-mini"
        assert kwargs["temperature"] == 0.5
        assert kwargs["max_tokens"] == 100
        assert len(kwargs["messages"]) == 1
