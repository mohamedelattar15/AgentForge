# AgentForge Core — Verifier
# Contrat de vérification : valide la réponse finale.

from abc import ABC, abstractmethod

from ..lifecycle.run_context import RunContext
from ..types import Message


class Verifier(ABC):
    """Vérificateur — valide que la réponse répond à la requête."""

    @abstractmethod
    async def verify(
        self, context: RunContext, final_response: Message
    ) -> bool:
        """Vérifie que la réponse finale est valide et complète.

        Args:
            context: Contexte du run (requête originale, historique).
            final_response: Réponse générée à vérifier.

        Returns:
            bool: True si la réponse est valide, False sinon.
        """
        ...
