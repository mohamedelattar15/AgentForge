# AgentForge — Tests Redis

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentforge_core.types import Message
from agentforge_redis import RedisWorkingMemory, RedisEpisodicMemory


class TestRedisWorkingMemory:
    """Tests pour RedisWorkingMemory (mocké)."""

    @pytest.fixture
    def mock_redis(self):
        """Fixture retournant un client Redis mocké."""
        client = MagicMock()
        client.get = AsyncMock()
        client.setex = AsyncMock()
        client.delete = AsyncMock()
        return client

    @pytest.fixture
    def adapter(self, mock_redis):
        """Fixture retournant un adapter avec Redis mocké."""
        with patch("agentforge_redis.aioredis.Redis", return_value=mock_redis):
            yield RedisWorkingMemory(host="localhost", port=6379)

    @pytest.mark.asyncio
    async def test_set_get(self, adapter, mock_redis):
        """set() puis get() doit retourner la même valeur."""
        mock_redis.get.return_value = json.dumps({"key": "value"})
        await adapter.set("run_1", {"key": "value"})
        result = await adapter.get("run_1")
        assert result == {"key": "value"}
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, adapter, mock_redis):
        """get() sur un run inexistant doit retourner {}."""
        mock_redis.get.return_value = None
        result = await adapter.get("run_inexistant")
        assert result == {}

    @pytest.mark.asyncio
    async def test_delete(self, adapter, mock_redis):
        """delete() doit appeler Redis."""
        await adapter.delete("run_1")
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_ttl_is_set(self, adapter, mock_redis):
        """set() doit utiliser setex avec TTL."""
        await adapter.set("run_1", {"data": "test"})
        args, kwargs = mock_redis.setex.call_args
        assert args[1] == 3600  # TTL par défaut

    def test_key_prefix(self):
        """Le préfixe de clé doit être configurable."""
        adapter = RedisWorkingMemory(host="x", port=1, key_prefix="custom:")
        assert adapter._key("test") == "custom:test"


class TestRedisEpisodicMemory:
    """Tests pour RedisEpisodicMemory (mocké)."""

    @pytest.fixture
    def mock_redis(self):
        """Fixture retournant un client Redis mocké."""
        client = MagicMock()
        client.lpush = AsyncMock()
        client.lrange = AsyncMock()
        client.ltrim = AsyncMock()
        client.scan = AsyncMock()
        return client

    @pytest.fixture
    def adapter(self, mock_redis):
        """Fixture retournant un adapter avec Redis mocké."""
        with patch("agentforge_redis.aioredis.Redis", return_value=mock_redis):
            yield RedisEpisodicMemory(host="localhost", port=6379)

    @pytest.mark.asyncio
    async def test_append(self, adapter, mock_redis):
        """append() doit ajouter un message à la liste Redis."""
        msg = Message(role="user", content="Bonjour")
        await adapter.append(msg)
        mock_redis.lpush.assert_called_once()
        mock_redis.ltrim.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_history(self, adapter, mock_redis):
        """get_history() doit retourner les messages."""
        mock_redis.lrange.return_value = [
            json.dumps({"role": "user", "content": "Hello", "tool_calls": []}),
        ]
        history = await adapter.get_history("session_1")
        assert len(history) == 1
        assert history[0].content == "Hello"

    @pytest.mark.asyncio
    async def test_search_hybrid(self, adapter, mock_redis):
        """search_hybrid() doit filtrer par contenu."""
        mock_redis.scan.return_value = (0, [b"key:session_1"])
        mock_redis.lrange.return_value = [
            json.dumps({"role": "user", "content": "Quel temps fait-il ?", "tool_calls": []}),
        ]
        results = await adapter.search_hybrid("temps")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_get_history_empty(self, adapter, mock_redis):
        """get_history() sur session vide doit retourner []."""
        mock_redis.lrange.return_value = []
        history = await adapter.get_history("session_vide")
        assert history == []
