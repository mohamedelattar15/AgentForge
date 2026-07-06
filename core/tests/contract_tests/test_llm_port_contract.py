# AgentForge Core — Contract Tests : LLMPort
# Tests partagés que tout adapter LLM doit passer.

from typing import TYPE_CHECKING

import pytest

from agentforge_core.types import Message

if TYPE_CHECKING:
    from agentforge_core.ports.llm_port import LLMPort


class LLMPortContractTests:
    """Tests de conformité pour tout adapter implémentant LLMPort.

    Tout adapter LLM doit hériter de cette classe et définir
    une fixture 'adapter' retournant une instance de LLMPort.
    """

    @pytest.mark.asyncio
    async def test_complete_returns_message(self, adapter: "LLMPort"):
        """complete() doit retourner un Message."""
        messages = [Message(role="user", content="Dis bonjour")]
        response = await adapter.complete(messages)
        assert isinstance(response, Message)
        assert response.role == "assistant"
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_complete_accepts_tools(self, adapter: "LLMPort"):
        """complete() doit accepter une liste d'outils optionnelle."""
        messages = [Message(role="user", content="Quelle heure est-il ?")]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_time",
                    "description": "Retourne l'heure actuelle",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            }
        ]
        response = await adapter.complete(messages, tools=tools)
        assert isinstance(response, Message)

    @pytest.mark.asyncio
    async def test_stream_yields_deltas(self, adapter: "LLMPort"):
        """stream() doit yield des chaînes de caractères."""
        messages = [Message(role="user", content="Compte jusqu'à 3")]
        deltas = []
        async for delta in adapter.stream(messages):
            deltas.append(delta)
        assert len(deltas) > 0
        assert all(isinstance(d, str) for d in deltas)
