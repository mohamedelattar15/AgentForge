# AgentForge Core — EvalStage
# Phase 5 : Évaluation asynchrone — scoring, gate, diagnose, release.

from ..ports.eval_port import EvalPort
from ..types import EvalResult
from .run_context import RunContext


class EvalStage:
    """Évalue la qualité du run en tâche de fond."""

    # Seuil de score pour le gate (en dessous = diagnostic)
    GATE_THRESHOLD: float = 0.7

    def __init__(self, eval_port: EvalPort) -> None:
        """Initialise le stage d'évaluation.

        Args:
            eval_port: Port d'évaluation à utiliser.
        """
        self._eval = eval_port

    async def evaluate(self, context: RunContext) -> EvalResult:
        """Évalue la qualité du run et applique le mécanisme Gate.

        1. Construit la trace d'évaluation.
        2. Appelle eval_port.evaluate().
        3. Gate : si score < seuil → Diagnose.
        4. Si fix trouvé → Release.

        Args:
            context: Contexte du run à évaluer.

        Returns:
            EvalResult: Résultat de l'évaluation.
        """
        run_trace = context.to_dict()
        result = await self._eval.evaluate(run_trace)

        # Gate : vérifier si le score est suffisant
        if result.score < self.GATE_THRESHOLD:
            # Diagnose : analyser les causes du score faible
            result = EvalResult(
                score=result.score,
                verdict="needs_improvement",
                diagnosis=result.diagnosis or "Score sous le seuil — diagnostic requis.",
                passed=False,
            )
        else:
            # Release : le run est validé
            result = EvalResult(
                score=result.score,
                verdict="passed",
                diagnosis=result.diagnosis,
                passed=True,
            )

        return result
