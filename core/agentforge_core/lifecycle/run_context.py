# AgentForge Core — RunContext
# Objet représentant l'état complet d'un run.

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from ..types import Message, ToolResult


class RunStatus(Enum):
    """Statut possible d'un run."""
    PENDING = "pending"
    HYDRATING = "hydrating"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class RunContext:
    """Contexte complet d'un run — état, messages, mémoires, guardrails.

    Attributes:
        run_id: Identifiant unique du run (UUID).
        user_query: Prompt original de l'utilisateur.
        messages: Messages échangés durant le run.
        working_memory: Contexte assemblé (phase d'hydratation).
        tool_results: Résultats des appels d'outils.
        status: Statut actuel du run.
        metadata: Métadonnées diverses (timestamps, tokens...).
        session_id: Identifiant de session pour la mémoire épisodique.
        max_iterations: Nombre maximum d'itérations de la boucle.
        token_budget: Budget maximum de tokens.
        timeout_seconds: Timeout maximum en secondes.
    """

    run_id: str = field(default_factory=lambda: uuid4().hex)
    user_query: str = ""
    messages: list[Message] = field(default_factory=list)
    working_memory: dict = field(default_factory=dict)
    tool_results: list[ToolResult] = field(default_factory=list)
    status: RunStatus = RunStatus.PENDING
    metadata: dict = field(default_factory=dict)
    session_id: str | None = None
    max_iterations: int = 20
    token_budget: int = 100_000
    timeout_seconds: int = 120

    def __post_init__(self) -> None:
        """Initialise les métadonnées de timestamp."""
        if "started_at" not in self.metadata:
            self.metadata["started_at"] = datetime.now(timezone.utc).isoformat()
        self.metadata.setdefault("token_count", 0)
        self.metadata.setdefault("iteration_count", 0)

    def add_message(self, msg: Message) -> None:
        """Ajoute un message et met à jour le compteur de tokens.

        Args:
            msg: Message à ajouter.
        """
        self.messages.append(msg)
        if msg.content:
            self.metadata["token_count"] += len(msg.content.split())

    def add_tool_result(self, result: ToolResult) -> None:
        """Ajoute un résultat d'outil.

        Args:
            result: Résultat d'exécution d'outil.
        """
        self.tool_results.append(result)

    def is_exhausted(self) -> bool:
        """Vérifie si un guardrail est atteint (doit arrêter le run).

        Returns:
            bool: True si un guardrail est violé.
        """
        if self.metadata.get("iteration_count", 0) >= self.max_iterations:
            return True
        if self.metadata.get("token_count", 0) >= self.token_budget:
            return True
        return False

    def to_dict(self) -> dict:
        """Sérialise le contexte en dictionnaire (pour tracing).

        Returns:
            dict: Représentation sérialisée du contexte.
        """
        return {
            "run_id": self.run_id,
            "user_query": self.user_query,
            "messages": [vars(m) for m in self.messages],
            "status": self.status.value,
            "metadata": self.metadata,
            "session_id": self.session_id,
        }
