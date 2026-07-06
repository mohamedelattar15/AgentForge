# AgentForge Core — Planner
# Contrat de planification : décompose l'objectif en étapes.

from abc import ABC, abstractmethod

from ..lifecycle.run_context import RunContext


class Planner(ABC):
    """Planificateur — décompose l'objectif utilisateur en étapes."""

    @abstractmethod
    async def plan(self, context: RunContext) -> list[str]:
        """Décompose la requête utilisateur en une séquence d'étapes.

        Args:
            context: Contexte du run contenant la requête utilisateur.

        Returns:
            list[str]: Liste d'étapes à exécuter.
        """
        ...
