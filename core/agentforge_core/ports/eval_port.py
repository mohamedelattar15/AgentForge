# AgentForge Core — EvalPort
# Contrat pour l'évaluation de la qualité des runs.

from abc import ABC, abstractmethod

from ..types import EvalResult


class EvalPort(ABC):
    """Port pour l'évaluation — scoring et jugement de qualité."""

    @abstractmethod
    async def evaluate(self, run_trace: dict) -> EvalResult:
        """Évalue la qualité d'un run à partir de sa trace.

        Args:
            run_trace: Trace complète du run (messages, tool calls, timing).

        Returns:
            EvalResult: Score, verdict et diagnostic de l'évaluation.
        """
        ...
