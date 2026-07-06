# AgentForge Core — TracePort
# Contrat pour l'émission de traces (télémétrie, observabilité).

from abc import ABC, abstractmethod

from ..types import Span


class TracePort(ABC):
    """Port pour le traçage — émission systématique d'une trace par run."""

    @abstractmethod
    async def record(self, run_id: str, spans: list[Span]) -> None:
        """Enregistre une trace complète pour un run.

        Args:
            run_id: Identifiant du run tracé.
            spans: Liste des spans représentant les phases d'exécution.
        """
        ...
