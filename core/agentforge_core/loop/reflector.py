# AgentForge Core — Reflector
# Contrat de réflexion : analyse le résultat avant de continuer.

from abc import ABC, abstractmethod

from ..lifecycle.run_context import RunContext
from ..types import ToolResult


class Reflector(ABC):
    """Réflecteur — analyse le résultat d'une étape et décide de la suite."""

    @abstractmethod
    async def reflect(
        self, context: RunContext, result: ToolResult
    ) -> str | None:
        """Analyse le résultat d'une étape et suggère la prochaine action.

        Args:
            context: Contexte du run.
            result: Résultat de l'étape exécutée.

        Returns:
            str | None: Suggestion de correction ou None si l'étape est valide.
        """
        ...
