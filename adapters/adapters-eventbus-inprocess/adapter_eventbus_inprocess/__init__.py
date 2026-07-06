# AgentForge — Adapter Event Bus InProcess
# Implémentation embarquée de EventBusPort avec un dispatcher in-process.

from collections.abc import Callable

from ...agentforge_core.ports.event_bus_port import EventBusPort


class InProcessEventBus(EventBusPort):
    """Bus d'événements in-process — publication et souscription en mémoire.

    Simple dispatcher synchrone, adapté pour les recettes minimales.
    Les handlers sont appelés dans le même thread que le publisher.
    """

    def __init__(self) -> None:
        """Initialise le bus avec un dictionnaire de souscripteurs."""
        self._subscribers: dict[str, list[Callable]] = {}

    async def publish(self, topic: str, event: dict) -> None:
        """Publie un événement sur un topic.

        Appelle tous les handlers souscrits à ce topic de façon synchrone.

        Args:
            topic: Nom du topic.
            event: Données de l'événement.
        """
        handlers = self._subscribers.get(topic, [])
        for handler in handlers:
            await handler(event)

    async def subscribe(self, topic: str, handler: Callable) -> None:
        """Souscrit un handler à un topic.

        Args:
            topic: Nom du topic.
            handler: Fonction asynchrone appelée sur réception d'événement.
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
