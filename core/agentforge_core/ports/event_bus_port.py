# AgentForge Core — EventBusPort
# Contrat pour la communication asynchrone interne.

from abc import ABC, abstractmethod
from collections.abc import Callable


class EventBusPort(ABC):
    """Port pour le bus d'événements — communication asynchrone entre composants."""

    @abstractmethod
    async def publish(self, topic: str, event: dict) -> None:
        """Publie un événement sur un topic.

        Args:
            topic: Nom du topic (ex: "agent.run.completed").
            event: Données de l'événement.
        """
        ...

    @abstractmethod
    async def subscribe(self, topic: str, handler: Callable) -> None:
        """Souscrit un handler à un topic.

        Args:
            topic: Nom du topic à écouter.
            handler: Fonction appelée lors de la réception d'un événement.
        """
        ...
