# AgentForge Core — ProceduralMemoryPort
# Contrat pour la mémoire procédurale (compétences, instructions, skills).

from abc import ABC, abstractmethod


class ProceduralMemoryPort(ABC):
    """Port pour la mémoire procédurale — compétences et instructions (Skill.md)."""

    @abstractmethod
    async def load(self, skill_name: str) -> str:
        """Charge le contenu textuel d'une compétence.

        Args:
            skill_name: Nom de la compétence à charger.

        Returns:
            str: Contenu textuel de la compétence.
        """
        ...

    @abstractmethod
    async def list_skills(self) -> list[str]:
        """Liste toutes les compétences disponibles.

        Returns:
            list[str]: Noms des compétences disponibles.
        """
        ...
