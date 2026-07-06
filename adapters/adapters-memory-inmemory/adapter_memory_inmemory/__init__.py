# AgentForge — Adapter Memory InMemory
# Implémentation embarquée de WorkingMemoryPort avec un simple dict en mémoire.

from ...agentforge_core.ports.working_memory_port import WorkingMemoryPort


class InMemoryWorkingMemory(WorkingMemoryPort):
    """Mémoire de travail en mémoire (dict) — aucune persistance.

    Stockage éphémère, perdu à l'arrêt du processus.
    Utilisation : développement local, tests, recette minimale.
    """

    def __init__(self) -> None:
        """Initialise le stockage en mémoire."""
        self._store: dict[str, dict] = {}

    async def get(self, run_id: str) -> dict:
        """Récupère le contexte d'un run.

        Args:
            run_id: Identifiant unique du run.

        Returns:
            dict: Contexte stocké, ou dict vide si inexistant.
        """
        return self._store.get(run_id, {})

    async def set(self, run_id: str, context: dict) -> None:
        """Stocke le contexte d'un run.

        Args:
            run_id: Identifiant unique du run.
            context: Contexte à stocker.
        """
        self._store[run_id] = context

    async def delete(self, run_id: str) -> None:
        """Supprime le contexte d'un run.

        Args:
            run_id: Identifiant unique du run à supprimer.
        """
        self._store.pop(run_id, None)
