# AgentForge Core — ToolRegistryPort
# Contrat pour le catalogue d'outils exécutables.

from abc import ABC, abstractmethod

from ..types import ToolResult


class ToolRegistryPort(ABC):
    """Port pour le registre d'outils — catalogue et exécution."""

    @abstractmethod
    async def list_tools(self) -> list[dict]:
        """Liste tous les outils disponibles avec leurs schémas (format OpenAI).

        Returns:
            list[dict]: Schémas des outils au format OpenAI tool calling.
        """
        ...

    @abstractmethod
    async def execute(self, name: str, args: dict) -> ToolResult:
        """Exécute un outil par son nom avec les arguments donnés.

        Args:
            name: Nom de l'outil à exécuter.
            args: Arguments d'appel de l'outil.

        Returns:
            ToolResult: Résultat de l'exécution (succès ou échec).
        """
        ...
