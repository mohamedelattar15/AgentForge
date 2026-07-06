# AgentForge — Tests NATS EventBus

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentforge_nats import NATSEventBus


class TestNATSEventBus:
    """Tests pour NATSEventBus (mocké)."""

    @pytest.mark.asyncio
    async def test_publish(self):
        """publish() doit envoyer un message NATS."""
        mock_nc = MagicMock()
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        mock_nc.jetstream = MagicMock(side_effect=ImportError("no js"))

        with patch("agentforge_nats.nats.connect", new=AsyncMock(return_value=mock_nc)):
            bus = NATSEventBus(servers=["nats://localhost:4222"])
            await bus.publish("test.topic", {"key": "value"})

        mock_nc.publish.assert_called_once()
        args, _ = mock_nc.publish.call_args
        assert args[0] == "agent.test.topic"

    @pytest.mark.asyncio
    async def test_publish_with_js(self):
        """publish() avec JetStream doit utiliser js.publish."""
        mock_nc = AsyncMock()
        mock_js = MagicMock()
        mock_js.add_stream = AsyncMock()
        mock_js.publish = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=mock_js)

        with patch("agentforge_nats.nats.connect", new=AsyncMock(return_value=mock_nc)):
            bus = NATSEventBus(servers=["nats://localhost:4222"])
            await bus.publish("run.started", {"run_id": "123"})

        mock_js.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe(self):
        """subscribe() doit créer une souscription NATS."""
        mock_nc = AsyncMock()
        mock_nc.subscribe = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=MagicMock(add_stream=AsyncMock(side_effect=Exception("no js"))))

        with patch("agentforge_nats.nats.connect", new=AsyncMock(return_value=mock_nc)):
            bus = NATSEventBus(servers=["nats://localhost:4222"])

            async def handler(event):
                pass

            await bus.subscribe("run.completed", handler)

        mock_nc.subscribe.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_creates_stream(self):
        """La connexion doit créer le stream JetStream."""
        mock_nc = AsyncMock()
        mock_js = MagicMock()
        mock_js.add_stream = AsyncMock()
        mock_js.publish = AsyncMock()
        mock_nc.jetstream = MagicMock(return_value=mock_js)

        with patch("agentforge_nats.nats.connect", new=AsyncMock(return_value=mock_nc)):
            bus = NATSEventBus(servers=["nats://localhost:4222"], stream="test-stream")
            await bus.publish("test", {})

        mock_js.add_stream.assert_called_once()
