# AgentForge — Tests Langfuse Trace

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from agentforge_core.types import Span
from agentforge_langfuse import LangfuseTrace


class TestLangfuseTrace:
    """Tests pour LangfuseTrace (mocké)."""

    @pytest.fixture
    def mock_langfuse(self):
        """Fixture retournant un client Langfuse mocké."""
        client = MagicMock()
        client.trace = MagicMock()
        client.flush = MagicMock()
        return client

    @pytest.fixture
    def adapter(self, mock_langfuse):
        """Fixture retournant un adapter Langfuse mocké."""
        with patch("agentforge_langfuse.Langfuse", return_value=mock_langfuse):
            yield LangfuseTrace(
                public_key="pk-test",
                secret_key="sk-test",
                host="https://cloud.langfuse.com",
            )

    @pytest.mark.asyncio
    async def test_record_creates_trace(self, adapter, mock_langfuse):
        """record() doit créer une trace Langfuse."""
        now = datetime.now(timezone.utc)
        spans = [
            Span(name="hydrate", start_time=now, end_time=now, attributes={"status": "ok"}),
            Span(name="loop", start_time=now, end_time=now, attributes={"iterations": 3}),
        ]

        await adapter.record("run_123", spans)

        mock_langfuse.trace.assert_called_once()
        mock_langfuse.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_adds_generations(self, adapter, mock_langfuse):
        """record() doit ajouter des générations pour chaque span."""
        mock_trace = MagicMock()
        mock_langfuse.trace.return_value = mock_trace

        now = datetime.now(timezone.utc)
        spans = [Span(name="test_span", start_time=now, end_time=now, attributes={})]

        await adapter.record("run_456", spans)

        mock_trace.generation.assert_called_once()
        args, kwargs = mock_trace.generation.call_args
        assert kwargs["name"] == "test_span"

    @pytest.mark.asyncio
    async def test_record_empty_spans(self, adapter, mock_langfuse):
        """record() avec spans vides doit créer la trace mais pas de générations."""
        mock_trace = MagicMock()
        mock_langfuse.trace.return_value = mock_trace

        await adapter.record("run_empty", [])

        mock_langfuse.trace.assert_called_once()
        mock_trace.generation.assert_not_called()
        mock_langfuse.flush.assert_called_once()
