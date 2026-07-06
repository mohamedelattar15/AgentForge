# AgentForge Core — TraceStage
# Phase 4 : Traçage — émission systématique d'une trace par run.

from datetime import datetime, timezone

from ..ports.trace_port import TracePort
from ..types import Span
from .run_context import RunContext


class TraceStage:
    """Émet une trace complète du run de façon asynchrone."""

    def __init__(self, trace_port: TracePort) -> None:
        """Initialise le stage de traçage.

        Args:
            trace_port: Port de traçage à utiliser.
        """
        self._trace = trace_port

    async def trace(self, context: RunContext) -> None:
        """Émet une trace du run (ne bloque jamais la réponse utilisateur).

        Args:
            context: Contexte du run à tracer.
        """
        spans = [
            Span(
                name="run",
                start_time=datetime.fromisoformat(
                    context.metadata.get("started_at", datetime.now(timezone.utc).isoformat())
                ),
                end_time=datetime.now(timezone.utc),
                attributes={
                    "status": context.status.value,
                    "message_count": len(context.messages),
                    "tool_call_count": len(context.tool_results),
                    "token_count": context.metadata.get("token_count", 0),
                    "iteration_count": context.metadata.get("iteration_count", 0),
                },
            )
        ]
        await self._trace.record(context.run_id, spans)
