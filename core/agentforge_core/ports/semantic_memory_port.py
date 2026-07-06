# AgentForge Core — SemanticMemoryPort
# Contrat pour la mémoire sémantique (faits durables, connaissances).

from abc import ABC, abstractmethod


class SemanticMemoryPort(ABC):
    """Port pour la mémoire sémantique — faits durables et profil utilisateur."""

    @abstractmethod
    async def search(
        self, query: str, top_k: int = 5, filters: dict | None = None
    ) -> list[dict]:
        """Recherche des faits pertinents par similarité sémantique.

        Args:
            query: Texte de recherche.
            top_k: Nombre maximum de résultats.
            filters: Filtres metadata optionnels.

        Returns:
            list[dict]: Liste de faits pertinents.
        """
        ...

    @abstractmethod
    async def upsert(self, fact: dict) -> None:
        """Ajoute ou met à jour un fait dans la mémoire sémantique.

        Args:
            fact: Dictionnaire représentant le fait (id, content, embedding, metadata).
        """
        ...

    @abstractmethod
    async def delete(self, fact_id: str) -> None:
        """Supprime un fait de la mémoire sémantique.

        Args:
            fact_id: Identifiant du fait à supprimer.
        """
        ...
