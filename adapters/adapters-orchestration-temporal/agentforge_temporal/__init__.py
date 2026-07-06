# AgentForge — Adapter Orchestration Temporal
# Implémente OrchestrationPort via Temporal (workflow durable).

from agentforge_core.lifecycle.run_context import RunContext
from agentforge_core.ports.orchestration_port import OrchestrationPort
from agentforge_core.types import Message

try:
    from temporalio.client import Client as TemporalClient
except ImportError:
    TemporalClient = None  # type: ignore


class TemporalOrchestrator(OrchestrationPort):
    """Orchestrateur basé sur Temporal.

    Délègue l'exécution du run à un workflow Temporal durable,
    avec gestion des timeouts, retries, et reprise sur erreur.
    """

    def __init__(
        self,
        host: str = "localhost:7233",
        namespace: str = "default",
        task_queue: str = "agent-tasks",
        workflow_timeout: int = 600,
    ) -> None:
        """Initialise l'orchestrateur Temporal.

        Args:
            host: Hôte du serveur Temporal.
            namespace: Namespace Temporal.
            task_queue: File d'attente des tâches.
            workflow_timeout: Timeout du workflow en secondes.
        """
        if TemporalClient is None:
            raise ImportError("temporalio est requis. Installez : pip install temporalio")

        self._host = host
        self._namespace = namespace
        self._task_queue = task_queue
        self._workflow_timeout = workflow_timeout
        self._client: TemporalClient | None = None

    async def _get_client(self) -> TemporalClient:
        """Retourne le client Temporal (connecte si nécessaire).

        Returns:
            TemporalClient: Client connecté.
        """
        if self._client is None:
            self._client = await TemporalClient.connect(
                self._host,
                namespace=self._namespace,
            )
        return self._client

    async def run(self, context: RunContext) -> Message:
        """Exécute le run via un workflow Temporal.

        Args:
            context: Contexte du run.

        Returns:
            Message: Réponse finale.
        """
        client = await self._get_client()

        # Note: Dans une implémentation réelle, le workflow et les activités
        # seraient définis dans des fichiers séparés et déployés.
        # Ici on utilise une exécution simplifiée pour l'interface.

        handle = await client.execute_workflow(
            "agent-workflow",
            {
                "run_id": context.run_id,
                "user_query": context.user_query,
                "messages": [{"role": m.role, "content": m.content} for m in context.messages],
            },
            id=f"agent-run-{context.run_id}",
            task_queue=self._task_queue,
            execution_timeout=self._workflow_timeout,
        )

        result = await handle.result()
        return Message(
            role="assistant",
            content=result.get("response", "Workflow exécuté avec succès."),
        )

    async def should_stop(self, state: dict) -> bool:
        """Vérifie si la boucle doit s'arrêter (délégue à Temporal).

        Args:
            state: État courant.

        Returns:
            bool: True si le workflow doit s'arrêter.
        """
        return False  # Temporal gère lui-même les conditions d'arrêt
