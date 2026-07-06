# AgentForge Core — Contract Tests : Memory Ports
# Tests partagés que tout adapter mémoire doit passer.

from typing import TYPE_CHECKING

import pytest

from agentforge_core.types import Message

if TYPE_CHECKING:
    from agentforge_core.ports.working_memory_port import WorkingMemoryPort
    from agentforge_core.ports.semantic_memory_port import SemanticMemoryPort
    from agentforge_core.ports.episodic_memory_port import EpisodicMemoryPort


class WorkingMemoryContractTests:
    """Tests de conformité pour tout adapter WorkingMemoryPort."""

    @pytest.mark.asyncio
    async def test_set_get(self, adapter: "WorkingMemoryPort"):
        """set() puis get() doit retourner la même valeur."""
        await adapter.set("run_1", {"key": "value"})
        result = await adapter.get("run_1")
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, adapter: "WorkingMemoryPort"):
        """get() sur un run inexistant doit retourner un dict vide."""
        result = await adapter.get("run_inexistant")
        assert result == {}

    @pytest.mark.asyncio
    async def test_delete(self, adapter: "WorkingMemoryPort"):
        """delete() doit supprimer le contexte."""
        await adapter.set("run_2", {"data": "test"})
        await adapter.delete("run_2")
        result = await adapter.get("run_2")
        assert result == {}


class SemanticMemoryContractTests:
    """Tests de conformité pour tout adapter SemanticMemoryPort."""

    @pytest.mark.asyncio
    async def test_upsert_and_search(self, adapter: "SemanticMemoryPort"):
        """upsert() puis search() doit retrouver le fait."""
        fact = {"id": "fact_1", "content": "L'utilisateur aime Python"}
        await adapter.upsert(fact)
        results = await adapter.search("Python")
        assert len(results) >= 1
        assert any("Python" in r["content"] for r in results)

    @pytest.mark.asyncio
    async def test_delete_fact(self, adapter: "SemanticMemoryPort"):
        """delete() doit supprimer un fait."""
        fact = {"id": "fact_2", "content": "Test à supprimer"}
        await adapter.upsert(fact)
        await adapter.delete("fact_2")
        results = await adapter.search("supprimer")
        assert not any(r["id"] == "fact_2" for r in results)


class EpisodicMemoryContractTests:
    """Tests de conformité pour tout adapter EpisodicMemoryPort."""

    @pytest.mark.asyncio
    async def test_append_and_get_history(self, adapter: "EpisodicMemoryPort"):
        """append() puis get_history() doit retourner les messages."""
        msg = Message(role="user", content="Bonjour")
        await adapter.append(msg)
        history = await adapter.get_history("default", limit=10)
        assert len(history) >= 1

    @pytest.mark.asyncio
    async def test_search_hybrid(self, adapter: "EpisodicMemoryPort"):
        """search_hybrid() doit trouver des messages par contenu."""
        msg = Message(role="user", content="Quel est le sens de la vie ?")
        await adapter.append(msg)
        results = await adapter.search_hybrid("sens de la vie")
        assert len(results) >= 1
