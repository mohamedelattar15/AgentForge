# AgentForge — Adapter Eval Ragas
# Implémente EvalPort via Ragas (metrics d'évaluation LLM).

from agentforge_core.ports.eval_port import EvalPort
from agentforge_core.types import EvalResult

try:
    from ragas import evaluate as ragas_evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
except ImportError:
    ragas_evaluate = None  # type: ignore
    faithfulness = None
    answer_relevancy = None
    context_precision = None
    context_recall = None


class RagasEval(EvalPort):
    """Évaluation Ragas — score la qualité des réponses avec des métriques LLM-as-Judge.

    Métriques disponibles : faithfulness, answer_relevancy, context_precision, context_recall.
    """

    # Mapping des noms de métriques vers les objets Ragas
    AVAILABLE_METRICS = {
        "faithfulness": faithfulness,
        "answer_relevancy": answer_relevancy,
        "context_precision": context_precision,
        "context_recall": context_recall,
    }

    def __init__(
        self,
        metrics: list[str] | None = None,
        threshold: float = 0.7,
    ) -> None:
        """Initialise l'évaluateur Ragas.

        Args:
            metrics: Liste des métriques à utiliser (ex: ["faithfulness", "answer_relevancy"]).
                     Par défaut : toutes les métriques disponibles.
            threshold: Seuil minimum pour considérer le test comme passé.
        """
        if ragas_evaluate is None:
            raise ImportError("ragas est requis. Installez : pip install ragas")

        metric_names = metrics or list(self.AVAILABLE_METRICS.keys())
        self._metrics = [
            self.AVAILABLE_METRICS[name]
            for name in metric_names
            if name in self.AVAILABLE_METRICS and self.AVAILABLE_METRICS[name] is not None
        ]
        self._threshold = threshold

    async def evaluate(self, run_trace: dict) -> EvalResult:
        """Évalue la qualité d'un run avec Ragas.

        Args:
            run_trace: Trace du run contenant les messages et le contexte.

        Returns:
            EvalResult: Score moyen, verdict et diagnostic.
        """
        if not self._metrics:
            return EvalResult(
                score=1.0,
                verdict="passed",
                diagnosis="Aucune métrique Ragas configurée.",
                passed=True,
            )

        try:
            # Extraire les données depuis la trace
            messages = run_trace.get("messages", [])
            question = run_trace.get("user_query", "")
            answer = self._extract_answer(messages)
            contexts = self._extract_contexts(run_trace)

            if not question or not answer:
                return EvalResult(
                    score=0.0,
                    verdict="failed",
                    diagnosis="Question ou réponse manquante dans la trace.",
                    passed=False,
                )

            # Construire le dataset Ragas
            from datasets import Dataset

            data = {
                "question": [question],
                "answer": [answer],
                "contexts": [contexts],
            }
            dataset = Dataset.from_dict(data)

            # Exécuter l'évaluation
            scores = ragas_evaluate(dataset, metrics=self._metrics)
            avg_score = self._compute_average(scores)

            passed = avg_score >= self._threshold
            return EvalResult(
                score=avg_score,
                verdict="passed" if passed else "needs_improvement",
                diagnosis=f"Score moyen Ragas : {avg_score:.3f} (seuil: {self._threshold})",
                passed=passed,
            )

        except Exception as e:
            return EvalResult(
                score=0.0,
                verdict="failed",
                diagnosis=f"Erreur d'évaluation Ragas : {e!s}",
                passed=False,
            )

    def _extract_answer(self, messages: list) -> str:
        """Extrait la dernière réponse assistant de la liste des messages.

        Args:
            messages: Liste des messages.

        Returns:
            str: Contenu de la dernière réponse assistant.
        """
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                return msg.get("content", "")
            if hasattr(msg, "role") and msg.role == "assistant":
                return msg.content
        return ""

    def _extract_contexts(self, run_trace: dict) -> list[str]:
        """Extrait les contextes (faits sémantiques) de la trace.

        Args:
            run_trace: Trace du run.

        Returns:
            list[str]: Liste de contextes textuels.
        """
        working_memory = run_trace.get("working_memory", {})
        semantic_facts = working_memory.get("semantic_facts", [])
        return [
            f.get("content", str(f)) for f in semantic_facts
        ]

    def _compute_average(self, scores) -> float:
        """Calcule la moyenne des scores Ragas.

        Args:
            scores: Résultat brut de ragas.evaluate().

        Returns:
            float: Score moyen entre 0 et 1.
        """
        try:
            import pandas as pd

            df = scores.to_pandas()
            numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
            if len(numeric_cols) > 0:
                return float(df[numeric_cols].mean().mean())
        except Exception:
            pass
        return 0.5
