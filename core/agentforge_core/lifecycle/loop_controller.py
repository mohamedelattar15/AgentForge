# AgentForge Core — LoopController
# Phase 2 : Boucle d'exécution — délègue à l'orchestrateur avec guardrails.

import asyncio

from ..ports.orchestration_port import OrchestrationPort
from ..types import Message
from .run_context import RunContext, RunStatus


class LoopController:
    """Contrôle la boucle d'exécution en appliquant les guardrails."""

    def __init__(self, orchestration: OrchestrationPort) -> None:
        """Initialise le contrôleur de boucle.

        Args:
            orchestration: Port d'orchestration à utiliser.
        """
        self._orchestration = orchestration

    async def execute(self, context: RunContext) -> Message:
        """Exécute la boucle via l'orchestrateur avec guardrails.

        Vérifie les guardrails (max itérations, budget tokens, timeout)
        avant, pendant et après l'exécution.

        Args:
            context: Contexte du run à exécuter.

        Returns:
            Message: Réponse finale après exécution.
        """
        context.status = RunStatus.RUNNING

        # Vérification initiale des guardrails
        if context.is_exhausted():
            context.status = RunStatus.BLOCKED
            return Message(
                role="system",
                content="Le run a été bloqué avant exécution : guardrails déjà atteints.",
            )

        try:
            # Exécution avec timeout
            response = await asyncio.wait_for(
                self._orchestration.run(context),
                timeout=context.timeout_seconds,
            )

            # Vérification post-exécution
            if context.is_exhausted():
                context.status = RunStatus.BLOCKED
                return Message(
                    role="system",
                    content="Le run a été interrompu : guardrail atteint.",
                )

            context.status = RunStatus.COMPLETED
            return response

        except asyncio.TimeoutError:
            context.status = RunStatus.FAILED
            return Message(
                role="system",
                content=f"Le run a expiré après {context.timeout_seconds} secondes.",
            )
        except Exception as e:
            context.status = RunStatus.FAILED
            return Message(
                role="system",
                content=f"Erreur lors de l'exécution : {e!s}",
            )
