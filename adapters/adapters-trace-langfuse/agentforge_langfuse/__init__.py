# AgentForge — Adapter Trace Langfuse
# Implémente TracePort via Langfuse (observabilité LLM).

from datetime import datetime, timezone

from agentforge_core.ports.trace_port import TracePort
from agentforge_core.types import Span

try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None  # type: ignore


class LangfuseTrace(TracePort):
    """Trace Langfuse — envoie les traces d'exécution à Langfuse.

    Crée une trace par run avec des spans pour chaque phase
    (hydrate, loop, persist, trace, eval).
    """

    def __init__(
        self,
        public_key: str | None = None,
        secret_key: str | None = None,
        host: str = "https://cloud.langfuse.com",
        release: str = "0.4.0",
    ) -> None:
        """Initialise le client Langfuse.

        Args:
            public_key: Clé publique Langfuse (ou env LANGFUSE_PUBLIC_KEY).
            secret_key: Clé secrète Langfuse (ou env LANGFUSE_SECRET_KEY).
            host: Hôte Langfuse (cloud ou auto-hébergé).
            release: Version du release tag.
        """
        if Langfuse is None:
            raise ImportError("langfuse est requis. Installez : pip install langfuse")

        self._client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            release=release,
        )

    async def record(self, run_id: str, spans: list[Span]) -> None:
        """Enregistre une trace complète dans Langfuse.

        Args:
            run_id: Identifiant du run (devient l'ID de trace Langfuse).
            spans: Liste des spans représentant les phases d'exécution.
        """
        # Créer la trace Langfuse
        trace = self._client.trace(
            id=run_id,
            name=f"run-{run_id[:8]}",
            input={"run_id": run_id},
            timestamp=datetime.now(timezone.utc),
        )

        # Ajouter chaque span comme génération
        for span in spans:
            trace.generation(
                name=span.name,
                start_time=span.start_time,
                end_time=span.end_time,
                metadata=span.attributes,
                level="DEFAULT",
            )

        # Finaliser et envoyer
        self._client.flush()
