# AgentForge Core — WorkingMemoryPort
# Contrat pour la mémoire de travail (contexte éphémère du run).

from abc import ABC, abstractmethod


class WorkingMemoryPort(ABC):
    """Port pour la mémoire de travail — stockage temporaire du contexte du run."""

    @abstractmethod
    async def get(self, run_id: str) -> dict:
        """Récupère le contexte d'un run.

        Args:
            run_id: Identifiant unique du run.

        Returns:
            dict: Contexte stocké pour ce run.
        """
        ...

    @abstractmethod
    async def set(self, run_id: str, context: dict) -> None:
        """Stocke le contexte d'un run.

        Args:
            run_id: Identifiant unique du run.
            context: Contexte à stocker.
        """
        ...

    @abstractmethod
    async def delete(self, run_id: str) -> None:
        """Supprime le contexte d'un run (fin de vie du run).

        Args:
            run_id: Identifiant unique du run à supprimer.
        """
        ...
