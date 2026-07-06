# AgentForge — Adapter LLM OpenAI-compatible (tests)

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from openai import AsyncOpenAI

from agentforge_core.types import Message, ToolCall
from agentforge_openai import OpenAICompatibleAdapter


class TestOpenAICompatibleAdapter:
    """Tests pour l'adapter OpenAI-compatible (avec mock)."""

    @pytest.fixture
    def adapter(self):
        """Fixture retournant un adapter OpenAI de test."""
        return OpenAICompatibleAdapter(
            model="gpt-4o-mini",
            api_key="test-key",
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
                    content="Réponse test",
                    tool_calls=None,
                )
            )
        ]

        with patch.object(adapter._client.chat.completions, "create", new=AsyncMock(return_value=mock_response)):
            messages = [Message(role="user", content="Test")]
            response = await adapter.complete(messages)

        assert isinstance(response, Message)
        assert response.content == "Réponse test"
        assert response.role == "assistant"

    @pytest.mark.asyncio
    async def test_complete_with_tools(self, adapter):
        """complete() avec outils doit retourner des ToolCall."""
        mock_tc = MagicMock()
        mock_tc.id = "call_1"
        mock_tc.function.name = "get_weather"
        mock_tc.function.arguments = '{"city": "Paris"}'

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=None,
                    tool_calls=[mock_tc],
                )
            )
        ]

        with patch.object(adapter._client.chat.completions, "create", new=AsyncMock(return_value=mock_response)):
            messages = [Message(role="user", content="Météo à Paris ?")]
            tools = [{"type": "function", "function": {"name": "get_weather"}}]
            response = await adapter.complete(messages, tools=tools)

        assert len(response.tool_calls) == 1
        assert response.tool_calls[0].name == "get_weather"
        assert response.tool_calls[0].id == "call_1"

    @pytest.mark.asyncio
    async def test_stream_yields_deltas(self, adapter):
        """stream() doit yield des tokens."""
        chunks = []
        for token in ["Hello", " ", "World"]:
            chunk = MagicMock()
            chunk.choices = [MagicMock(delta=MagicMock(content=token))]
            chunks.append(chunk)

        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = chunks  # type: ignore

        with patch.object(adapter._client.chat.completions, "create", new=AsyncMock(return_value=mock_stream)):
            messages = [Message(role="user", content="Say hi")]
            deltas = []
            async for delta in adapter.stream(messages):
                deltas.append(delta)

        assert "".join(deltas) == "Hello World"

    def test_initialization_without_openai(self):
        """L'initialisation doit fonctionner avec les valeurs par défaut."""
        adapter = OpenAICompatibleAdapter(model="test-model", api_key="test-key")
        assert adapter._model == "test-model"
        assert isinstance(adapter._client, AsyncOpenAI)

    @pytest.mark.asyncio
    async def test_complete_raises_on_error(self, adapter):
        """Une erreur API doit être convertie en RuntimeError."""
        with patch.object(
            adapter._client.chat.completions, "create",
            side_effect=Exception("Rate limit"),
        ):
            messages = [Message(role="user", content="Test")]
            with pytest.raises(RuntimeError, match="Rate limit"):
                await adapter.complete(messages)

    def test_format_messages_with_tool_calls(self, adapter):
        """Le formatage des messages doit inclure les tool_calls."""
        msg = Message(
            role="assistant",
            content="",
            tool_calls=[ToolCall(id="c1", name="test", arguments="{}")],
        )
        formatted = adapter._format_messages([msg])
        assert "tool_calls" in formatted[0]
        assert formatted[0]["tool_calls"][0]["function"]["name"] == "test"
