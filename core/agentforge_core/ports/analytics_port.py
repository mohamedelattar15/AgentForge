# AgentForge Core — AnalyticsPort
# Contrat pour l'agrégation de métriques à grande échelle.

from abc import ABC, abstractmethod


class AnalyticsPort(ABC):
    """Port pour l'analytique — agrégation et interrogation de métriques."""

    @abstractmethod
    async def ingest(self, metrics: dict) -> None:
        """Ingère des métriques dans le système d'analytique.

        Args:
            metrics: Dictionnaire de métriques (latence, tokens, scores...).
        """
        ...

    @abstractmethod
    async def query(self, filters: dict) -> list[dict]:
        """Interroge les métriques agrégées avec des filtres.

        Args:
            filters: Filtres de recherche (période, port, adapter...).

        Returns:
            list[dict]: Résultats agrégés.
        """
        ...
