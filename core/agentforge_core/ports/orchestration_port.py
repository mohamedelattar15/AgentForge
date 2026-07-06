# AgentForge Core — OrchestrationPort
# Contrat pour la boucle d'exécution (orchestrateur).

from abc import ABC, abstractmethod

from ..types import Message, RunContext


class OrchestrationPort(ABC):
    """Port pour l'orchestration de la boucle d'exécution."""

    @abstractmethod
    async def run(self, context: RunContext) -> Message:
        """Exécute la boucle de raisonnement complète.

        Args:
            context: Contexte complet du run (état, mémoires, outils).

        Returns:
            Message: La réponse finale après exécution de la boucle.
        """
        ...

    @abstractmethod
    async def should_stop(self, state: dict) -> bool:
        """Vérifie si la boucle doit s'arrêter.

        Args:
            state: État courant de la boucle (itération, tokens, etc.).

        Returns:
            bool: True si la boucle doit s'arrêter, False sinon.
        """
        ...
