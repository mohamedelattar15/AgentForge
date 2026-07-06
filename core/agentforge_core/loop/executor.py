# AgentForge Core — Executor
# Contrat d'exécution : réalise les tool calls planifiés.

from abc import ABC, abstractmethod

from ..lifecycle.run_context import RunContext
from ..types import Message, ToolResult


class Executor(ABC):
    """Exécuteur — réalise une étape (tool call ou réponse LLM)."""

    @abstractmethod
    async def execute(
        self, context: RunContext, step: str
    ) -> ToolResult | Message:
        """Exécute une étape planifiée.

        Args:
            context: Contexte du run.
            step: Description textuelle de l'étape à exécuter.

        Returns:
            ToolResult | Message: Résultat de l'outil ou réponse LLM.
        """
        ...
