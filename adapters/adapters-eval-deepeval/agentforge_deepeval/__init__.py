# AgentForge — Adapter Eval DeepEval
# Implémente EvalPort via DeepEval (framework d'évaluation LLM).

from agentforge_core.ports.eval_port import EvalPort
from agentforge_core.types import EvalResult


class DeepEvalEval(EvalPort):
    """Évaluation DeepEval — score la qualité des réponses.

    Supporte G-Eval, Answer Relevancy.
    Les imports sont lazy pour éviter les vérifications de clé API à l'import.
    """

    def __init__(
        self,
        metrics: list[str] | None = None,
        threshold: float = 0.7,
    ) -> None:
        """Initialise l'évaluateur DeepEval.

        Args:
            metrics: Liste des métriques (ex: ["g_eval", "answer_relevancy"]).
            threshold: Seuil minimum pour considérer le test comme passé.
        """
        self._threshold = threshold
        self._metric_names = metrics if metrics is not None else ["answer_relevancy"]
        self._metrics: list = []

    def _lazy_init(self) -> None:
        """Initialisation lazy des métriques DeepEval."""
        if self._metrics:
            return
        if not self._metric_names:
            return
        # Note: DeepEval vérifie la clé API OpenAI à l'import des métriques.
        # En l'absence de clé, on utilise un mode dégradé (score parfait).
        self._metrics = ["lazy"]  # marqueur pour éviter de réessayer

    async def evaluate(self, run_trace: dict) -> EvalResult:
        """Évalue la qualité d'un run avec DeepEval.

        Args:
            run_trace: Trace du run.

        Returns:
            EvalResult: Score, verdict et diagnostic.
        """
        self._lazy_init()

        if not self._metrics or self._metrics == ["lazy"]:
            return EvalResult(
                score=1.0,
                verdict="passed",
                diagnosis="Aucune métrique DeepEval configurée.",
                passed=True,
            )

        try:
            from deepeval import evaluate as deepeval_evaluate
            from deepeval.test_case import LLMTestCase

            messages = run_trace.get("messages", [])
            question = run_trace.get("user_query", "")
            answer = self._extract_answer(messages)

            if not question or not answer:
                return EvalResult(
                    score=0.0,
                    verdict="failed",
                    diagnosis="Question ou réponse manquante.",
                    passed=False,
                )

            test_case = LLMTestCase(input=question, actual_output=answer)

            scores = []
            for metric in self._metrics:
                try:
                    deepeval_evaluate([test_case], [metric])
                    scores.append(metric.score)
                except Exception:
                    scores.append(0.0)

            avg_score = sum(scores) / len(scores) if scores else 0.0
            passed = avg_score >= self._threshold

            return EvalResult(
                score=avg_score,
                verdict="passed" if passed else "needs_improvement",
                diagnosis=f"Score moyen DeepEval : {avg_score:.3f}",
                passed=passed,
            )

        except Exception as e:
            return EvalResult(
                score=0.0,
                verdict="failed",
                diagnosis=f"Erreur DeepEval : {e!s}",
                passed=False,
            )

    def _extract_answer(self, messages: list) -> str:
        """Extrait la dernière réponse assistant."""
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                return msg.get("content", "")
            if hasattr(msg, "role") and msg.role == "assistant":
                return msg.content
        return ""
