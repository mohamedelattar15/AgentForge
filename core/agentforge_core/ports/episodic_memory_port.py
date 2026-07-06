# AgentForge Core — EpisodicMemoryPort
# Contrat pour la mémoire épisodique (historique des conversations).

from abc import ABC, abstractmethod
from datetime import datetime

from ..types import Message


class EpisodicMemoryPort(ABC):
    """Port pour la mémoire épisodique — historique daté des conversations."""

    @abstractmethod
    async def search_hybrid(
        self,
        query: str,
        since: datetime | None = None,
        top_k: int = 10,
    ) -> list[dict]:
        """Recherche hybride (texte + metadata) dans l'historique.

        Args:
            query: Texte de recherche.
            since: Date limite (ne chercher que les événements après cette date).
            top_k: Nombre maximum de résultats.

        Returns:
            list[dict]: Événements pertinents de l'historique.
        """
        ...

    @abstractmethod
    async def append(self, event: Message) -> None:
        """Ajoute un message à l'historique de la session.

        Args:
            event: Message à ajouter à l'historique.
        """
        ...

    @abstractmethod
    async def get_history(
        self, session_id: str, limit: int = 50
    ) -> list[Message]:
        """Récupère l'historique complet d'une session.

        Args:
            session_id: Identifiant de la session.
            limit: Nombre maximum de messages à retourner.

        Returns:
            list[Message]: Messages de l'historique triés par date.
        """
        ...
