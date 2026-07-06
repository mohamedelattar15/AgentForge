# AgentForge Core — Configuration des tests pytest

import pytest

from agentforge_core.ports.llm_port import LLMPort
from agentforge_core.ports.working_memory_port import WorkingMemoryPort
from agentforge_core.ports.semantic_memory_port import SemanticMemoryPort
from agentforge_core.ports.episodic_memory_port import EpisodicMemoryPort
from agentforge_core.ports.tool_registry_port import ToolRegistryPort
from agentforge_core.types import Message, ToolResult


# ─── LLM Port Mock ────────────────────────────────────────────────────────────

class MockLLMAdapter(LLMPort):
    """Adapter LLM mocké pour les tests."""

    async def complete(self, messages, tools=None):
        return Message(role="assistant", content="Ceci est une réponse mockée.")

    async def stream(self, messages, tools=None):
        yield "Ceci "
        yield "est "
        yield "un "
        yield "stream "
        yield "mocké."


@pytest.fixture
def llm_adapter():
    """Fixture retournant un adapter LLM mocké."""
    return MockLLMAdapter()


# ─── Working Memory Port Mock ─────────────────────────────────────────────────

class MockWorkingMemory(WorkingMemoryPort):
    """Mémoire de travail mockée."""

    def __init__(self):
        self._store = {}

    async def get(self, run_id):
        return self._store.get(run_id, {})

    async def set(self, run_id, context):
        self._store[run_id] = context

    async def delete(self, run_id):
        self._store.pop(run_id, None)


@pytest.fixture
def working_memory_adapter():
    """Fixture retournant une mémoire de travail mockée."""
    return MockWorkingMemory()


# ─── Semantic Memory Port Mock ────────────────────────────────────────────────

class MockSemanticMemory(SemanticMemoryPort):
    """Mémoire sémantique mockée."""

    def __init__(self):
        self._facts = {}

    async def search(self, query, top_k=5, filters=None):
        return [
            {"id": k, "content": v["content"], "metadata": v.get("metadata", {})}
            for k, v in self._facts.items()
            if query.lower() in v["content"].lower()
        ][:top_k]

    async def upsert(self, fact):
        self._facts[fact["id"]] = fact

    async def delete(self, fact_id):
        self._facts.pop(fact_id, None)


@pytest.fixture
def semantic_memory_adapter():
    """Fixture retournant une mémoire sémantique mockée."""
    return MockSemanticMemory()


# ─── Episodic Memory Port Mock ────────────────────────────────────────────────

class MockEpisodicMemory(EpisodicMemoryPort):
    """Mémoire épisodique mockée."""

    def __init__(self):
        self._messages = []

    async def search_hybrid(self, query, since=None, top_k=10):
        results = [
            {"content": m.content, "role": m.role}
            for m in self._messages
            if query.lower() in m.content.lower()
        ]
        return results[:top_k]

    async def append(self, event):
        self._messages.append(event)

    async def get_history(self, session_id, limit=50):
        return self._messages[:limit]


@pytest.fixture
def episodic_memory_adapter():
    """Fixture retournant une mémoire épisodique mockée."""
    return MockEpisodicMemory()


# ─── Tool Registry Port Mock ──────────────────────────────────────────────────

class MockToolRegistry(ToolRegistryPort):
    """Registre d'outils mocké."""

    def __init__(self):
        self._tools = [
            {
                "type": "function",
                "function": {
                    "name": "mock_tool",
                    "description": "Outil mocké pour les tests",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ]

    async def list_tools(self):
        return self._tools

    async def execute(self, name, args):
        if name == "mock_tool":
            return ToolResult(
                tool_call_id="call_mock",
                content="Résultat mocké",
                success=True,
            )
        return ToolResult(
            tool_call_id="",
            content=f"Outil '{name}' inconnu",
            success=False,
        )


@pytest.fixture
def tool_registry_adapter():
    """Fixture retournant un registre d'outils mocké."""
    return MockToolRegistry()
