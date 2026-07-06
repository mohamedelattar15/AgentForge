# AgentForge Core — PersistStage
# Phase 3 : Persistance — sauvegarde des messages et consolidation.

from ..ports.episodic_memory_port import EpisodicMemoryPort
from ..ports.semantic_memory_port import SemanticMemoryPort
from .run_context import RunContext


class PersistStage:
    """Sauvegarde les messages et déclenche la consolidation mémoire."""

    # Seuil de nouveaux échanges pour déclencher la consolidation
    CONSOLIDATION_THRESHOLD: int = 10

    def __init__(
        self,
        episodic_memory: EpisodicMemoryPort,
        semantic_memory: SemanticMemoryPort,
    ) -> None:
        """Initialise le stage de persistance.

        Args:
            episodic_memory: Port de mémoire épisodique.
            semantic_memory: Port de mémoire sémantique.
        """
        self._episodic = episodic_memory
        self._semantic = semantic_memory

    async def persist(self, context: RunContext) -> None:
        """Sauvegarde les messages et déclenche la consolidation si nécessaire.

        Args:
            context: Contexte du run à persister.
        """
        # 1. Sauvegarder tous les messages dans la mémoire épisodique
        for msg in context.messages:
            await self._episodic.append(msg)

        # 2. Compter les nouveaux échanges et déclencher consolidation si seuil atteint
        new_exchanges = len(context.messages) // 2
        if new_exchanges >= self.CONSOLIDATION_THRESHOLD:
            await self._consolidate(context)

    async def _consolidate(self, context: RunContext) -> None:
        """Consolide les échanges récents vers la mémoire sémantique.

        Extrait les faits des échanges et les stocke dans la mémoire sémantique.
        """
        # Extraire un résumé simple des échanges
        exchange_text = "\n".join(
            f"{m.role}: {m.content}" for m in context.messages[-10:]
        )

        fact = {
            "id": f"consolidated-{context.run_id}",
            "content": f"Résumé de la session {context.session_id or context.run_id}:\n{exchange_text}",
            "metadata": {
                "source": "consolidation",
                "session_id": context.session_id,
                "run_id": context.run_id,
            },
        }
        await self._semantic.upsert(fact)
