# AgentForge Core — LLMPort
# Contrat pour l'appel à n'importe quel LLM.

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from ..types import Message


class LLMPort(ABC):
    """Port pour l'appel à un modèle de langage (LLM)."""

    @abstractmethod
    async def complete(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> Message:
        """Appelle le LLM et retourne une réponse complète.

        Args:
            messages: Liste des messages échangés (contexte + historique).
            tools: Schémas d'outils disponibles au format OpenAI (optionnel).

        Returns:
            Message: La réponse générée par le LLM.
        """
        ...

    @abstractmethod
    async def stream(
        self, messages: list[Message], tools: list[dict] | None = None
    ) -> AsyncGenerator[str, None]:
        """Appelle le LLM en streaming et yield des tokens un par un.

        Args:
            messages: Liste des messages échangés.
            tools: Schémas d'outils disponibles (optionnel).

        Yields:
            str: Tokens de la réponse au fur et à mesure.
        """
        ...
        yield  # pragma: no cover
