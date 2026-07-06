# AgentForge — Tests OpenTelemetry Trace

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from agentforge_core.types import Span
from agentforge_otel import OTelTrace


class TestOTelTrace:
    """Tests pour OTelTrace (mocké)."""

    @pytest.fixture
    def mock_tracer(self):
        """Fixture retournant un tracer mocké."""
        tracer = MagicMock()
        tracer.start_as_current_span = MagicMock()
        return tracer

    @pytest.fixture
    def adapter(self, mock_tracer):
        """Fixture retournant un adapter OTel mocké."""
        with patch("agentforge_otel.otel_trace.get_tracer", return_value=mock_tracer):
            with patch("agentforge_otel.OTelTrace._to_nano", return_value=0):
                yield OTelTrace(
                    service_name="test-agent",
                    endpoint="http://localhost:4317",
                )

    @pytest.mark.asyncio
    async def test_record_creates_root_span(self, adapter, mock_tracer):
        """record() doit créer une span racine."""
        mock_span = MagicMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_span)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_tracer.start_as_current_span.return_value = mock_cm

        now = datetime.now(timezone.utc)
        spans = [Span(name="test", start_time=now, end_time=now, attributes={"key": "val"})]

        await adapter.record("run_test", spans)

        assert mock_tracer.start_as_current_span.called

    @pytest.mark.asyncio
    async def test_record_empty_spans(self, adapter, mock_tracer):
        """record() avec spans vides doit créer la span racine uniquement."""
        mock_cm = MagicMock()
        mock_cm.__enter__ = MagicMock(return_value=MagicMock())
        mock_cm.__exit__ = MagicMock(return_value=None)
        mock_tracer.start_as_current_span.return_value = mock_cm

        await adapter.record("run_empty", [])
        mock_tracer.start_as_current_span.assert_called_once()

    def test_to_nano(self):
        """_to_nano() doit convertir correctement."""
        dt = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        nano = OTelTrace._to_nano(dt)
        assert nano == 1704067200000000000
