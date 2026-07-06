# AgentForge — Adapter Event Bus NATS JetStream
# Implémente EventBusPort via NATS (messaging asynchrone).

from collections.abc import Callable

from agentforge_core.ports.event_bus_port import EventBusPort

try:
    import nats
    from nats.js import JetStreamContext
except ImportError:
    nats = None  # type: ignore
    JetStreamContext = None  # type: ignore


class NATSEventBus(EventBusPort):
    """Bus d'événements via NATS JetStream.

    Publie et souscrit à des événements de façon durable.
    Topics : agent.run.{run_id}, agent.eval.{run_id}, agent.analytics
    """

    def __init__(
        self,
        servers: list[str] | None = None,
        stream: str = "agentforge",
        consumer_prefix: str = "agent-worker",
    ) -> None:
        """Initialise le bus NATS.

        Args:
            servers: Liste des serveurs NATS (ex: ["nats://localhost:4222"]).
            stream: Nom du stream JetStream.
            consumer_prefix: Préfixe pour les noms de consumers.
        """
        if nats is None:
            raise ImportError("nats-py est requis. Installez : pip install nats-py")

        self._servers = servers or ["nats://localhost:4222"]
        self._stream = stream
        self._consumer_prefix = consumer_prefix
        self._nc = None
        self._js = None
        self._subscriptions: dict[str, Callable] = {}

    async def _connect(self) -> None:
        """Connecte au serveur NATS et crée le stream JetStream."""
        if self._nc is not None:
            return

        self._nc = await nats.connect(servers=self._servers)

        # Tentative de création du stream JetStream
        try:
            js = self._nc.jetstream()
            if js and hasattr(js, "add_stream"):
                await js.add_stream(name=self._stream, subjects=[f"agent.>"])
                self._js = js
        except Exception:
            self._js = None  # JetStream non disponible, fallback sur NATS core

    async def publish(self, topic: str, event: dict) -> None:
        """Publie un événement sur un topic NATS.

        Args:
            topic: Nom du topic (ex: "agent.run.completed").
            event: Données de l'événement (sérialisées en JSON).
        """
        await self._connect()

        import json
        data = json.dumps(event, default=str).encode()

        if self._js:
            await self._js.publish(f"agent.{topic}", data)
        elif self._nc:
            await self._nc.publish(f"agent.{topic}", data)

    async def subscribe(self, topic: str, handler: Callable) -> None:
        """Souscrit à un topic NATS.

        Args:
            topic: Nom du topic à écouter.
            handler: Fonction asynchrone appelée sur réception d'événement.
        """
        await self._connect()

        subject = f"agent.{topic}"

        async def message_handler(msg) -> None:
            import json
            data = json.loads(msg.data.decode())
            await handler(data)

        if self._js:
            # Subscription durable via JetStream
            consumer_name = f"{self._consumer_prefix}-{topic.replace('.', '-')}"
            await self._js.subscribe(
                subject=subject,
                durable=consumer_name,
                cb=message_handler,
                stream=self._stream,
            )
        elif self._nc:
            sub = await self._nc.subscribe(subject, cb=message_handler)
            self._subscriptions[topic] = sub
