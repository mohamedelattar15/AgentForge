# AgentForge Core — Types partagés
# Dataclasses fondamentales utilisées par tous les ports et composants.

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


@dataclass
class Message:
    """Un message dans l'historique de la conversation.

    Attributes:
        role: Rôle de l'émetteur (system, user, assistant, tool).
        content: Contenu textuel du message.
        tool_calls: Liste des appels d'outils (pour les messages assistant).
        timestamp: Horodatage du message.
    """
    role: str
    content: str
    tool_calls: list["ToolCall"] = field(default_factory=list)
    timestamp: datetime | None = None


@dataclass
class ToolCall:
    """Appel d'outil émis par le LLM.

    Attributes:
        id: Identifiant unique de l'appel.
        name: Nom de l'outil à appeler.
        arguments: Arguments d'appel (dict).
    """
    id: str
    name: str
    arguments: dict


@dataclass
class ToolResult:
    """Résultat de l'exécution d'un outil.

    Attributes:
        tool_call_id: Identifiant du tool_call correspondant.
        content: Contenu du résultat.
        success: True si l'exécution a réussi.
    """
    tool_call_id: str
    content: str
    success: bool = True


class RunStatus(Enum):
    """Statuts possibles d'un run."""
    PENDING = "pending"
    HYDRATING = "hydrating"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Span:
    """Une span de tracing — représente une phase d'exécution.

    Attributes:
        name: Nom de la span (ex: "hydrate", "loop", "persist").
        start_time: Début de la span.
        end_time: Fin de la span.
        attributes: Métadonnées associées.
    """
    name: str
    start_time: datetime
    end_time: datetime
    attributes: dict = field(default_factory=dict)


@dataclass
class EvalResult:
    """Résultat de l'évaluation d'un run.

    Attributes:
        score: Score numérique (0.0 à 1.0).
        verdict: Verdict textuel ("passed", "needs_improvement", "failed").
        diagnosis: Diagnostic si le score est insuffisant.
        passed: True si le run est validé.
    """
    score: float
    verdict: str
    diagnosis: str = ""
    passed: bool = True


@dataclass
class AdapterDeclaration:
    """Déclaration d'un adapter pour le registre.

    Attributes:
        port: Nom du port implémenté.
        name: Nom de l'adapter.
        version: Version de l'adapter.
        class_ref: Chemin de classe complet (module.ClassName).
    """
    port: str
    name: str
    version: str
    class_ref: str
