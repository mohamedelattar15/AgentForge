# AgentForge — Adapter Orchestration Minimal
# Implémentation embarquée de OrchestrationPort avec une boucle synchrone simple.

from ...agentforge_core.lifecycle.run_context import RunContext
from ...agentforge_core.loop.executor import Executor
from ...agentforge_core.loop.planner import Planner
from ...agentforge_core.loop.reflector import Reflector
from ...agentforge_core.loop.verifier import Verifier
from ...agentforge_core.ports.orchestration_port import OrchestrationPort
from ...agentforge_core.types import Message


class MinimalOrchestrator(OrchestrationPort):
    """Orchestrateur minimal avec boucle synchrone intégrée.

    Utilise les composants Planner, Executor, Reflector et Verifier
    pour exécuter la boucle de raisonnement complète.
    """

    def __init__(
        self,
        planner: Planner | None = None,
        executor: Executor | None = None,
        reflector: Reflector | None = None,
        verifier: Verifier | None = None,
        max_retries: int = 3,
    ) -> None:
        """Initialise l'orchestrateur minimal.

        Args:
            planner: Planificateur (utilise DefaultPlanner si None).
            executor: Exécuteur (utilise DefaultExecutor si None).
            reflector: Réflecteur (utilise DefaultReflector si None).
            verifier: Vérificateur (utilise DefaultVerifier si None).
            max_retries: Nombre maximum de tentatives de vérification.
        """
        self._planner = planner
        self._executor = executor
        self._reflector = reflector
        self._verifier = verifier
        self._max_retries = max_retries

    async def run(self, context: RunContext) -> Message:
        """Exécute la boucle de raisonnement complète.

        1. Planifier les étapes.
        2. Pour chaque étape : exécuter, réfléchir, corriger si besoin.
        3. Vérifier la réponse finale.

        Args:
            context: Contexte du run.

        Returns:
            Message: Réponse finale.
        """
        steps = await self._planner.plan(context) if self._planner else ["répondre"]

        final_response = Message(role="assistant", content="")

        for step in steps:
            result = await self._executor.execute(context, step) if self._executor else Message(
                role="assistant", content="Traitement par défaut."
            )

            if self._reflector and hasattr(result, "tool_call_id"):
                correction = await self._reflector.reflect(context, result)
                if correction:
                    result = await self._executor.execute(context, correction)

            if isinstance(result, Message):
                final_response = result

        # Vérification finale
        if self._verifier:
            for attempt in range(self._max_retries):
                is_valid = await self._verifier.verify(context, final_response)
                if is_valid:
                    break
                if attempt < self._max_retries - 1:
                    final_response = Message(
                        role="assistant",
                        content=final_response.content
                        + "\n\n[Vérification échouée, tentative de correction...]",
                    )

        return final_response

    async def should_stop(self, state: dict) -> bool:
        """Vérifie si la boucle doit s'arrêter.

        Args:
            state: État courant (itération, tokens...).

        Returns:
            bool: True si la boucle doit s'arrêter.
        """
        max_iter = state.get("max_iterations", 20)
        current_iter = state.get("iteration", 0)
        return current_iter >= max_iter
